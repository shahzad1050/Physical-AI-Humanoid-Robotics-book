from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv

from rag_engine import RAGEngine
from chatbot import ChatBot

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Add CORS middleware to allow requests from Docusaurus frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Docusaurus domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global RAG engine and chatbot instances
rag_engine = None
chatbot = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine and chatbot on startup"""
    global rag_engine, chatbot

    logger.info("Initializing RAG Engine and ChatBot...")

    # Check for required environment variables
    required_env_vars = ['OPENAI_API_KEY', 'COHERE_API_KEY', 'NEON_CONNECTION_STRING']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")

    # Initialize RAG Engine
    rag_engine = RAGEngine(table_name="docusaurus_content")

    # Initialize ChatBot
    chatbot = ChatBot(
        system_prompt="You are an AI assistant helping users with the content from the documentation. "
                     "Use the provided context to answer questions accurately. "
                     "If the context doesn't contain relevant information, acknowledge this and provide a general response."
    )

    logger.info("RAG Engine and ChatBot initialized successfully")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    top_k: Optional[int] = 3

class ChatResponse(BaseModel):
    response: str
    context_used: List[Dict[str, Any]]

class EmbedRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = "embed-multilingual-v3.0"

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

class Document(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class AddDocumentsRequest(BaseModel):
    documents: List[Document]

class AddDocumentsResponse(BaseModel):
    status: str
    count: int

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main RAG chat endpoint that retrieves context and generates response
    """
    global rag_engine, chatbot

    if not rag_engine or not chatbot:
        raise HTTPException(status_code=500, detail="RAG Engine or ChatBot not initialized")

    try:
        logger.info(f"Processing chat request: {request.message[:50]}...")

        # Use RAG to get response with context
        response = rag_engine.rag_chat(
            query=request.message,
            chatbot=chatbot,
            top_k=request.top_k
        )

        # Also get the context that was used for transparency
        context_results = rag_engine.search(request.message, top_k=request.top_k)
        context_used = [
            {
                "id": result["id"],
                "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],  # Truncate for response
                "score": result["score"]
            }
            for result in context_results
        ]

        logger.info("Chat request processed successfully")

        return ChatResponse(
            response=response,
            context_used=context_used
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/embed", response_model=EmbedResponse)
async def embed_endpoint(request: EmbedRequest):
    """
    Optional endpoint for generating embeddings
    """
    global rag_engine

    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG Engine not initialized")

    try:
        logger.info(f"Generating embeddings for {len(request.texts)} texts")

        # Use Cohere client from RAG engine to generate embeddings
        response = rag_engine.cohere_client.embed(
            texts=request.texts,
            model=request.model,
            input_type="search_query"
        )

        logger.info("Embeddings generated successfully")

        return EmbedResponse(embeddings=response.embeddings)

    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

@app.post("/documents/add", response_model=AddDocumentsResponse)
async def add_documents_endpoint(request: AddDocumentsRequest):
    """
    Endpoint to add documents to the RAG system
    """
    global rag_engine

    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG Engine not initialized")

    try:
        logger.info(f"Adding {len(request.documents)} documents to RAG system")

        # Extract content and metadata from request
        documents = [doc.content for doc in request.documents]
        metadata = [doc.metadata or {} for doc in request.documents]

        # Add documents to RAG engine
        rag_engine.add_documents(documents, metadata)

        logger.info(f"Successfully added {len(request.documents)} documents")

        return AddDocumentsResponse(
            status="success",
            count=len(request.documents)
        )

    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "components": {
            "rag_engine": "initialized" if rag_engine else "not initialized",
            "chatbot": "initialized" if chatbot else "not initialized"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)