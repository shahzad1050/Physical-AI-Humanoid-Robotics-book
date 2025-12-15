import os
import cohere
import psycopg2
from psycopg2.extras import DictCursor
from pgvector.psycopg2 import register_vector
from typing import List, Dict, Any
from chatbot import ChatBot
import numpy as np


class RAGEngine:
    """
    RAG Engine that integrates Cohere embeddings with a Neon Postgres database using pgvector.
    Implements the complete RAG pipeline: add_documents -> search -> retrieve_for_chat -> rag_chat
    """

    def __init__(self, table_name="documents"):
        # Initialize Cohere client
        self.cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))

        # Initialize Postgres connection
        self.conn = psycopg2.connect(os.getenv('NEON_CONNECTION_STRING'))
        register_vector(self.conn)
        self.table_name = table_name

        # Create table if it doesn't exist
        self._create_table()

    def _create_table(self):
        """
        Create a table in the Postgres database for storing document embeddings.
        """
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding VECTOR(1024)
            )
            """)
            self.conn.commit()
            print(f"Table '{self.table_name}' is ready.")

    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Add documents to the vector database with embeddings.
        """
        if metadata is None:
            metadata = [{}] * len(documents)

        # Generate embeddings using Cohere
        response = self.cohere_client.embed(
            texts=documents,
            model="embed-multilingual-v3.0",
            input_type="search_document"
        )

        embeddings = response.embeddings

        # Prepare data for insertion
        with self.conn.cursor() as cur:
            for doc, embedding, meta in zip(documents, embeddings, metadata):
                cur.execute(
                    f"INSERT INTO {self.table_name} (content, metadata, embedding) VALUES (%s, %s, %s)",
                    (doc, psycopg2.extras.Json(meta), np.array(embedding))
                )
            self.conn.commit()

        print(f"Added {len(documents)} documents to table '{self.table_name}'")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using the query.
        """
        # Generate embedding for the query
        response = self.cohere_client.embed(
            texts=[query],
            model="embed-multilingual-v3.0",
            input_type="search_query"
        )

        query_embedding = np.array(response.embeddings[0])

        # Search in Postgres using cosine similarity
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                f"SELECT id, content, metadata, 1 - (embedding <=> %s) AS score FROM {self.table_name} ORDER BY embedding <=> %s LIMIT %s",
                (query_embedding, query_embedding, top_k)
            )
            search_results = cur.fetchall()

        # Format results
        results = []
        for row in search_results:
            results.append({
                "id": row["id"],
                "content": row["content"],
                "metadata": row["metadata"],
                "score": row["score"]
            })

        return results

    def retrieve_for_chat(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant context for chat interaction.
        """
        search_results = self.search(query, top_k)

        # Combine retrieved documents into context
        context_parts = []
        for result in search_results:
            context_parts.append(result["content"])

        context = "\n\n".join(context_parts)
        return context

    def rag_chat(self, query: str, chatbot: ChatBot, top_k: int = 3) -> str:
        """
        Complete RAG chat function: retrieve context and generate response.
        """
        # Retrieve relevant context
        context = self.retrieve_for_chat(query, top_k)

        # Formulate prompt with context
        enhanced_prompt = f"""
        Context information:
        {context}

        User query: {query}

        Please provide an answer based on the context information provided above.
        If the context doesn't contain relevant information, please say so and provide a general response.
        """

        # Use the chatbot to generate a response
        response = chatbot.chat(enhanced_prompt)
        return response


def main():
    """
    Main function for testing the RAG Engine.
    """
    from dotenv import load_dotenv
    load_dotenv()

    print("Initializing RAG Engine...")

    # Initialize RAG Engine
    rag_engine = RAGEngine()

    # Initialize chatbot
    chatbot = ChatBot(system_prompt="You are an AI assistant with access to specific documents. Use the provided context to answer questions accurately.")

    # Example documents to add
    sample_docs = [
        "Docusaurus is a modern static website generator for building documentation websites.",
        "It is built with React and supports features like search, versioning, and internationalization.",
        "Neon is a serverless Postgres database that is highly scalable and efficient.",
        "Cohere provides state-of-the-art language models and embeddings for various NLP tasks.",
        "Retrieval-Augmented Generation (RAG) combines retrieval from a knowledge base with generative models."
    ]

    sample_metadata = [
        {"source": "docusaurus_intro", "page": 1},
        {"source": "docusaurus_features", "page": 1},
        {"source": "neon_info", "page": 1},
        {"source": "cohere_info", "page": 1},
        {"source": "rag_definition", "page": 1}
    ]

    print("Adding sample documents to the vector database...")
    rag_engine.add_documents(sample_docs, sample_metadata)

    print("\nRAG Engine ready! You can now ask questions based on the documents.")
    print("Type 'quit' to exit.\n")

    while True:
        user_query = input("Query: ")

        if user_query.lower() == 'quit':
            print("Goodbye!")
            break

        # Use RAG to answer the query
        response = rag_engine.rag_chat(user_query, chatbot)
        print(f"Response: {response}\n")


if __name__ == "__main__":
    main()