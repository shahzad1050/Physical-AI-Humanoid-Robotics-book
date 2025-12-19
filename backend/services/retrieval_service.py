"""
Document retrieval service for the RAG Chatbot
"""
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
import os
import psycopg2
from pgvector.psycopg2 import register_vector

from ..models.document_chunk import DocumentChunk
from ..utils import get_logger
from ..config import settings

logger = get_logger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant documents based on query similarity
    """
    def __init__(self):
        self.conn = psycopg2.connect(settings.neon_connection_string)
        register_vector(self.conn)
        logger.info("Retrieval service connected to the database.")

    def find_similar_documents(self, query_embedding: np.ndarray, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Find documents most similar to the query embedding using pgvector.

        Args:
            query_embedding: Embedding vector for the query.
            top_k: Number of top results to return.
            min_score: Minimum similarity score threshold (1 - cosine distance).

        Returns:
            List of similar documents with scores.
        """
        with self.conn.cursor() as cur:
            # The <=> operator in pgvector calculates the cosine distance (1 - cosine similarity)
            # So, a smaller distance is better.
            # We filter by distance <= (1 - min_score)
            cur.execute(
                "SELECT id, content, metadata, 1 - (embedding <=> %s) AS score FROM documents WHERE 1 - (embedding <=> %s) >= %s ORDER BY score DESC LIMIT %s",
                (query_embedding, query_embedding, min_score, top_k)
            )
            results = cur.fetchall()

        similar_docs = []
        for row in results:
            similar_docs.append({
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "score": row[3]
            })

        return similar_docs

    def retrieve_by_content_similarity(self, query: str, embedding_service, top_k: int = 5, min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve documents based on content similarity to the query.

        Args:
            query: Query text.
            embedding_service: EmbeddingService instance to generate query embedding.
            top_k: Number of top results to return.
            min_score: Minimum similarity score threshold.

        Returns:
            List of similar documents with scores.
        """
        try:
            # Generate embedding for the query
            query_embedding = np.array(embedding_service.embed_text(query))

            # Find similar documents
            similar_docs = self.find_similar_documents(
                query_embedding,
                top_k=top_k,
                min_score=min_score
            )

            logger.info(f"Retrieved {len(similar_docs)} documents for query: {query[:50]}...")
            return similar_docs
        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query[:50]}...': {str(e)}")
            raise e

    def __del__(self):
        """
        Destructor to close the database connection.
        """
        if self.conn:
            self.conn.close()