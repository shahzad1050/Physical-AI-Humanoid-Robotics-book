"""
RAG Agent service for the RAG Chatbot
"""
import os
# import json # Removed as no longer loading from local JSON
import numpy as np
import psycopg2
from psycopg2.extras import DictCursor
from pgvector.psycopg2 import register_vector # NEW import
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import cohere

from ..models.document_chunk import DocumentChunk
from ..models.response import Response, SourceReference
from ..utils import get_logger
from ..config import settings

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class RAGAgent:
    """
    RAG Agent that combines OpenAI GPT with local embeddings
    Bypasses Qdrant compatibility issues by using local embeddings
    """
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

        # Initialize Cohere client for query embedding
        self.cohere_client = cohere.Client(settings.cohere_api_key)

        # Initialize Postgres connection
        self.conn = psycopg2.connect(settings.neon_connection_string)
        register_vector(self.conn)
        self.table_name = "documents"

        # Ensure table exists
        self._check_and_create_table()
        logger.info("RAG Agent initialized with Neon Postgres backend.")

        # Set up system prompt
        self.system_prompt = """You are an AI assistant specialized in Physical AI & Humanoid Robotics.
        Use the provided documentation context to answer questions accurately.
        If the context doesn't contain relevant information, acknowledge this and provide a general response.
        Always cite relevant sources from the documentation when possible."""

    def _check_and_create_table(self):
        """
        Create a table in the Postgres database for storing document embeddings if it doesn't exist.
        """
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB NOT NULL,
                embedding VECTOR(1024),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            self.conn.commit()
            logger.info("Table 'documents' is ready.")

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed the query using Cohere
        """
        response = self.cohere_client.embed(
            texts=[query],
            model=settings.embedding_model,
            input_type=settings.embedding_input_type
        )
        return np.array(response.embeddings[0])

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using Postgres (similarity search)
        """
        query_embedding = self.embed_query(query)

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
                "metadata": dict(row["metadata"]), # Ensure metadata is a dict
                "score": row["score"]
            })
        return results

    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate response using OpenAI GPT with context
        """
        # Combine context documents into a single context string
        context_parts = []
        for doc in context_docs:
            source = doc['metadata'].get('relative_path', 'Unknown')
            context_parts.append(f"Source: {source}\nContent: {doc['content']}")

        context = "\n\n".join(context_parts)

        # Create the full prompt with context
        full_prompt = f"""
        Context information:
        {context}

        User query: {query}

        Please provide an answer based on the context information provided above.
        If the context doesn't contain relevant information, please say so and provide a general response.
        Always cite relevant sources from the documentation when possible.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using the same model as specified in your system
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"

    def chat(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Complete RAG chat function: retrieve context and generate response
        """
        logger.info(f"Processing query: {query}")

        # Retrieve relevant context
        context_docs = self.retrieve_context(query, top_k)
        logger.info(f"Retrieved {len(context_docs)} relevant documents")

        # Generate response
        response_text = self.generate_response(query, context_docs)

        # Create source references
        sources = []
        for doc in context_docs:
            source_ref = SourceReference(
                document_id=str(doc.get('id', 'unknown')),
                relative_path=doc['metadata'].get('relative_path', 'Unknown'),
                score=doc['score'],
                content_preview=doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            )
            sources.append(source_ref)

        # Create response object
        response = Response(
            id="temp_id",  # Will be replaced with actual ID in API endpoint
            query_id="temp_query_id",  # Will be replaced with actual query ID in API endpoint
            content=response_text,
            sources=sources
        )

        result = {
            "response": response.content,
            "context_used": context_docs,
            "query": query
        }

        return result

    def chat_with_context(self, query: str, conversation_context: List[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Complete RAG chat function with conversation context: retrieve context and generate response
        considering previous conversation history

        Args:
            query: User's current query
            conversation_context: List of previous conversation messages
            top_k: Number of top documents to retrieve

        Returns:
            Dictionary containing response, context used, and query
        """
        logger.info(f"Processing query with conversation context: {query}")

        # Prepare the full prompt with conversation history
        full_query = query
        if conversation_context:
            # Combine conversation history with current query
            context_str = "\n".join(conversation_context[-5:])  # Use last 5 conversation turns
            full_query = f"Previous conversation:\n{context_str}\n\nCurrent question: {query}"
            logger.debug(f"Included {len(conversation_context)} conversation turns in context")
        else:
            logger.debug("No conversation context provided")

        # Retrieve relevant context based on the full query (including conversation history)
        context_docs = self.retrieve_context(full_query, top_k)
        logger.info(f"Retrieved {len(context_docs)} relevant documents with conversation context")

        # Generate response using both the documentation context and conversation history
        response_text = self.generate_response_with_context(query, context_docs, conversation_context)

        # Create source references
        sources = []
        for doc in context_docs:
            source_ref = SourceReference(
                document_id=str(doc.get('id', 'unknown')),
                relative_path=doc['metadata'].get('relative_path', 'Unknown'),
                score=doc['score'],
                content_preview=doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            )
            sources.append(source_ref)

        result = {
            "response": response_text,
            "context_used": context_docs,
            "query": query
        }

        return result

    def generate_response_with_context(self, query: str, context_docs: List[Dict[str, Any]],
                                     conversation_context: List[str] = None) -> str:
        """
        Generate response using OpenAI GPT with both documentation context and conversation history

        Args:
            query: User's current query
            context_docs: Retrieved documentation context
            conversation_context: List of previous conversation messages

        Returns:
            Generated response text
        """
        # Combine context documents into a single context string
        context_parts = []
        for doc in context_docs:
            source = doc['metadata'].get('relative_path', 'Unknown')
            context_parts.append(f"Source: {source}\nContent: {doc['content']}")

        documentation_context = "\n\n".join(context_parts)

        # Prepare the full prompt with both documentation context and conversation history
        full_prompt_parts = []

        # Add system context
        full_prompt_parts.append(self.system_prompt)

        # Add conversation history if available
        if conversation_context:
            full_prompt_parts.append(f"Previous conversation context:\n{'\n'.join(conversation_context[-3:])}")  # Use last 3 exchanges

        # Add current documentation context
        full_prompt_parts.append(f"Documentation context:\n{documentation_context}")

        # Add the current query
        full_prompt_parts.append(f"Current question: {query}")

        # Add response instructions
        full_prompt_parts.append(
            "Please provide an answer based on the context information provided above. "
            "If the context doesn't contain relevant information, please say so and provide a general response. "
            "Always cite relevant sources from the documentation when possible. "
            "Maintain the conversational context from previous exchanges when relevant."
        )

        full_prompt = "\n\n".join(full_prompt_parts)

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using the same model as specified in your system
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response with conversation context: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"