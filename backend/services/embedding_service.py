"""
Embedding generation service for the RAG Chatbot
"""
from typing import List, Dict, Any
import numpy as np
from cohere import Client
from dotenv import load_dotenv
import logging

from ..utils import get_logger
from ..config import settings

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using Cohere API
    """
    def __init__(self):
        self.client = Client(settings.cohere_api_key)
        self.model = settings.embedding_model
        self.input_type = settings.embedding_input_type
        self.dimensions = settings.embedding_dimensions

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as a list of floats
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type=self.input_type
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            raise e

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=self.input_type
            )
            return [embedding for embedding in response.embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings for texts: {str(e)}")
            raise e

    def embed_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks

        Args:
            chunks: List of document chunks with content and metadata

        Returns:
            List of document chunks with embeddings added
        """
        if not chunks:
            return []

        # Extract just the content for embedding
        texts = [chunk['content'] for chunk in chunks]

        try:
            embeddings = self.embed_texts(texts)

            # Add embeddings back to the chunks
            for i, chunk in enumerate(chunks):
                chunk['embedding'] = embeddings[i]

            return chunks
        except Exception as e:
            logger.error(f"Error embedding document chunks: {str(e)}")
            raise e

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding has the correct dimensions

        Args:
            embedding: Embedding vector to validate

        Returns:
            True if valid, False otherwise
        """
        if len(embedding) != self.dimensions:
            logger.warning(f"Embedding has {len(embedding)} dimensions, expected {self.dimensions}")
            return False
        return True

    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize an embedding vector to unit length

        Args:
            embedding: Embedding vector to normalize

        Returns:
            Normalized embedding vector
        """
        arr = np.array(embedding)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return embedding
        return (arr / norm).tolist()