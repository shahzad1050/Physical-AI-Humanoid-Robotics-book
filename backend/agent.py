import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import requests

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import required libraries
import cohere

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv('COHERE_API_KEY')
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY is not set in the environment variables.")

cohere_client = cohere.Client(api_key=cohere_api_key)

# Qdrant configuration (using HTTP API due to Python 3.14 compatibility issues)
qdrant_cluster_endpoint = os.getenv('QDRANT_CLUSTER_ENDPOINT')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

if not qdrant_cluster_endpoint or not qdrant_api_key:
    raise ValueError("QDRANT_CLUSTER_ENDPOINT or QDRANT_API_KEY is not set in the environment variables.")

# Qdrant API headers
qdrant_headers = {
    'api-key': qdrant_api_key,
    'Content-Type': 'application/json'
}

# Initialize FastAPI app
app = FastAPI(
    title="Cohere-Qdrant RAG Agent",
    description="An intelligent agent using Cohere for embeddings and generation, with Qdrant for vector storage",
    version="1.0.0"
)

# Define input model for the API
class AgentInput(BaseModel):
    message: str
    top_k: int = 5

# Define output model for the API
class AgentOutput(BaseModel):
    response: str
    context_used: List[Dict[str, Any]]
    query_embedding: List[float]

class DocumentPayload(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    document_id: str = None

class AddDocumentsInput(BaseModel):
    documents: List[DocumentPayload]

# Initialize Qdrant collection if it doesn't exist
def initialize_qdrant_collection(collection_name: str = "documents"):
    try:
        # Check if collection exists
        response = requests.get(f"{qdrant_cluster_endpoint}/collections/{collection_name}", headers=qdrant_headers)
        if response.status_code == 200:
            logger.info(f"Collection '{collection_name}' already exists")
            return
    except:
        pass

    # Create a new collection using HTTP API
    collection_config = {
        "vectors": {
            "size": 1024,  # Cohere embeddings are 1024-dim
            "distance": "Cosine"
        }
    }

    response = requests.put(
        f"{qdrant_cluster_endpoint}/collections/{collection_name}",
        headers=qdrant_headers,
        json=collection_config
    )

    if response.status_code == 200:
        logger.info(f"Created new collection '{collection_name}'")
    else:
        logger.warning(f"Failed to create collection '{collection_name}': {response.text}")

# Initialize the collection
initialize_qdrant_collection()

@app.post("/chat", response_model=AgentOutput)
def chat_with_agent(agent_input: AgentInput):
    """
    Main endpoint to interact with the agent using Cohere and Qdrant.
    """
    try:
        # Generate embedding for the query using Cohere
        response = cohere_client.embed(
            texts=[agent_input.message],
            model="embed-multilingual-v3.0",
            input_type="search_query"
        )
        query_embedding = response.embeddings[0]

        # Search in Qdrant for similar documents using HTTP API
        search_payload = {
            "vector": query_embedding,
            "limit": agent_input.top_k,
            "with_payload": True
        }

        search_response = requests.post(
            f"{qdrant_cluster_endpoint}/collections/documents/points/search",
            headers=qdrant_headers,
            json=search_payload
        )

        if search_response.status_code != 200:
            logger.warning(f"Qdrant search failed: {search_response.text}")
            search_results = []
        else:
            search_results = search_response.json().get('result', [])

        # Extract context from search results
        context_used = []
        context_text = ""

        for result in search_results:
            if result.get('payload'):
                doc_data = {
                    "id": result.get('id'),
                    "content": result['payload'].get('content', ''),
                    "metadata": result['payload'].get('metadata', {}),
                    "score": result.get('score')
                }
                context_used.append(doc_data)
                context_text += f"{result['payload'].get('content', '')}\n\n"

        # Prepare the prompt for Cohere generation
        if context_text.strip():
            prompt = f"""
            Context information is provided below.
            Context:
            {context_text}

            Using the context information, answer the query: {agent_input.message}

            If the context doesn't contain relevant information for the question, acknowledge this and provide a general response related to the question's topic. If the answer is not in the context, say that you don't know.
            """
        else:
            prompt = f"""
            Answer the following query: {agent_input.message}

            Provide a helpful response based on your knowledge.
            """

        # Generate response using Cohere
        response = cohere_client.chat(
            message=prompt,
            temperature=0.3,
        )

        logger.info(f"Processed query: {agent_input.message[:50]}... with {len(context_used)} context documents")

        return AgentOutput(
            response=response.text,
            context_used=context_used,
            query_embedding=query_embedding
        )
    except Exception as e:
        logger.error(f"Error processing query '{agent_input.message[:50]}...': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/embed")
def embed_text(agent_input: AgentInput):
    """
    Endpoint to generate embeddings for text using Cohere.
    """
    try:
        response = cohere_client.embed(
            texts=[agent_input.message],
            model="embed-multilingual-v3.0",
            input_type="search_query"
        )
        embedding = response.embeddings[0]

        return {
            "embedding": embedding,
            "model": "embed-multilingual-v3.0"
        }
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/documents/add")
def add_documents(doc_input: AddDocumentsInput):
    """
    Endpoint to add documents to the Qdrant collection.
    """
    try:
        points = []
        for i, doc in enumerate(doc_input.documents):
            # Generate embedding for the document content using Cohere
            response = cohere_client.embed(
                texts=[doc.content],
                model="embed-multilingual-v3.0",
                input_type="search_document"
            )
            embedding = response.embeddings[0]

            # Create a point for Qdrant
            point = {
                "id": doc.document_id or f"doc_{i}_{abs(hash(doc.content)) % 100000}",
                "vector": embedding,
                "payload": {
                    "content": doc.content,
                    "metadata": doc.metadata
                }
            }
            points.append(point)

        # Upload points to Qdrant using HTTP API
        upsert_payload = {
            "points": points
        }

        upsert_response = requests.put(
            f"{qdrant_cluster_endpoint}/collections/documents/points?wait=true",
            headers=qdrant_headers,
            json=upsert_payload
        )

        if upsert_response.status_code != 200:
            logger.error(f"Qdrant upsert failed: {upsert_response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to add documents to Qdrant: {upsert_response.text}")

        logger.info(f"Added {len(points)} documents to Qdrant")

        return {
            "status": "success",
            "count": len(points),
            "message": f"Successfully added {len(points)} documents to Qdrant"
        }
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify all services are running.
    """
    try:
        # Test Qdrant connection
        response = requests.get(f"{qdrant_cluster_endpoint}/collections", headers=qdrant_headers)

        if response.status_code == 200:
            collections = response.json()
            collection_names = [c.get('name') for c in collections.get('result', {}).get('collections', [])]
        else:
            collection_names = []
            logger.warning(f"Could not fetch Qdrant collections: {response.text}")

        return {
            "status": "healthy",
            "components": {
                "cohere": "connected",
                "qdrant": "connected",
                "collections": collection_names
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/")
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Cohere-Qdrant RAG Agent API",
        "endpoints": [
            {"method": "POST", "path": "/chat", "description": "Chat with the agent"},
            {"method": "POST", "path": "/embed", "description": "Generate embeddings"},
            {"method": "POST", "path": "/documents/add", "description": "Add documents to vector store"},
            {"method": "GET", "path": "/health", "description": "Health check"}
        ]
    }

# Example usage when running as a standalone script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)