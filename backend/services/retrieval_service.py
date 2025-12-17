"""
Document retrieval service for the RAG Chatbot
"""
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
import os

from ..models.document_chunk import DocumentChunk
from ..utils import get_logger
from ..config import settings

logger = get_logger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant documents based on query similarity
    """
    def __init__(self):
        # Load embeddings from local file
        self.embedded_docs = self.load_embeddings()
        logger.info(f"Retrieval service loaded {len(self.embedded_docs)} documents")

    def load_embeddings(self):
        """
        Load embeddings from the local JSON file
        """
        if not os.path.exists(settings.embedded_docs_path):
            raise FileNotFoundError(f"{settings.embedded_docs_path} not found. Please run the embedding pipeline first.")

        with open(settings.embedded_docs_path, 'r', encoding='utf-8') as f:
            embedded_docs = json.load(f)

        # Convert embedding lists back to numpy arrays for similarity calculations
        for doc in embedded_docs:
            doc['embedding'] = np.array(doc['embedding'])

        return embedded_docs

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def find_similar_documents(self, query_embedding: np.ndarray, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Find documents most similar to the query embedding

        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of similar documents with scores
        """
        if not self.embedded_docs:
            return []

        # Stack all document embeddings into a single numpy array for vectorized computation
        doc_embeddings = np.stack([doc['embedding'] for doc in self.embedded_docs])

        # Compute cosine similarities in a vectorized manner
        # Normalize embeddings
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(doc_embeddings, axis=1)

        # Handle zero vectors
        query_norm = query_norm if query_norm != 0 else 1e-10
        doc_norms = np.where(doc_norms == 0, 1e-10, doc_norms)

        # Compute dot products
        dot_products = np.dot(doc_embeddings, query_embedding)

        # Compute cosine similarities
        similarities = dot_products / (query_norm * doc_norms)

        # Apply minimum score threshold
        valid_indices = np.where(similarities >= min_score)[0]

        if len(valid_indices) == 0:
            return []

        # Get the top_k indices
        if len(valid_indices) <= top_k:
            top_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
        else:
            # Use argpartition for better performance when we only need top-k
            top_k_indices = np.argpartition(similarities[valid_indices], -top_k)[-top_k:]
            # Sort only the top-k results
            top_indices = valid_indices[top_k_indices[np.argsort(similarities[top_k_indices])[::-1]]]

        # Build result list
        top_docs = []
        for idx in top_indices:
            doc = self.embedded_docs[idx].copy()
            doc['score'] = float(similarities[idx])  # Convert to Python float for JSON serialization
            top_docs.append(doc)

        return top_docs

    def retrieve_by_content_similarity(self, query: str, embedding_service, top_k: int = 5, min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve documents based on content similarity to the query

        Args:
            query: Query text
            embedding_service: EmbeddingService instance to generate query embedding
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of similar documents with scores
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

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID

        Args:
            doc_id: Document ID to retrieve

        Returns:
            Document if found, None otherwise
        """
        for doc in self.embedded_docs:
            if doc.get('id') == doc_id:
                return doc
        return None

    def filter_by_metadata(self, metadata_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter documents by metadata fields

        Args:
            metadata_filters: Dictionary of metadata field-value pairs to filter by

        Returns:
            List of documents matching the filters
        """
        filtered_docs = []
        for doc in self.embedded_docs:
            match = True
            for key, value in metadata_filters.items():
                if doc['metadata'].get(key) != value:
                    match = False
                    break
            if match:
                filtered_docs.append(doc)
        return filtered_docs

    def validate_retrieval_results(self, results: List[Dict[str, Any]], top_k: int) -> bool:
        """
        Validate retrieval results meet quality criteria

        Args:
            results: List of retrieved documents
            top_k: Expected number of results

        Returns:
            True if results are valid, False otherwise
        """
        # Check that we have results
        if not results:
            logger.warning("No documents retrieved")
            return False

        # Check that scores are within expected range
        for doc in results:
            if not (0.0 <= doc.get('score', 0.0) <= 1.0):
                logger.warning(f"Document has invalid score: {doc.get('score')}")
                return False

        return True

    def calculate_relevance_score(self, query_embedding: np.ndarray, doc_embedding: np.ndarray,
                                 metadata: Dict[str, Any] = None) -> float:
        """
        Calculate comprehensive relevance score combining multiple factors

        Args:
            query_embedding: Embedding vector for the query
            doc_embedding: Embedding vector for the document
            metadata: Additional metadata to consider in scoring

        Returns:
            Relevance score between 0 and 1
        """
        # Base cosine similarity score
        base_score = self.cosine_similarity(query_embedding, doc_embedding)

        # Apply metadata-based adjustments if available
        adjusted_score = base_score
        if metadata:
            # Boost score for more recent documents if date information is available
            if 'last_modified' in metadata or 'created_date' in metadata:
                # This is a placeholder - in a real implementation you'd calculate recency boost
                pass

            # Adjust based on document quality metrics if available
            if 'quality_score' in metadata:
                quality_factor = metadata['quality_score']
                adjusted_score = base_score * 0.7 + quality_factor * 0.3  # weighted combination

        # Ensure the score is within bounds
        return max(0.0, min(1.0, adjusted_score))

    def rerank_documents(self, query_embedding: np.ndarray, documents: List[Dict[str, Any]],
                        rerank_top_k: int = None) -> List[Dict[str, Any]]:
        """
        Rerank documents using more sophisticated relevance scoring

        Args:
            query_embedding: Embedding vector for the query
            documents: List of documents to rerank
            rerank_top_k: Number of top documents to rerank (if None, rerank all)

        Returns:
            Reranked list of documents with updated scores
        """
        if not documents:
            return documents

        # Limit to top_k if specified
        docs_to_rerank = documents[:rerank_top_k] if rerank_top_k else documents

        # Calculate enhanced relevance scores
        reranked_docs = []
        for doc in docs_to_rerank:
            enhanced_score = self.calculate_relevance_score(
                query_embedding,
                doc['embedding'],
                doc.get('metadata', {})
            )

            # Update the document's score
            updated_doc = doc.copy()
            updated_doc['score'] = enhanced_score
            reranked_docs.append(updated_doc)

        # Sort by the enhanced scores
        reranked_docs.sort(key=lambda x: x['score'], reverse=True)

        # Combine with the rest of the documents if we only reranked a subset
        if rerank_top_k and len(documents) > rerank_top_k:
            reranked_docs.extend(documents[rerank_top_k:])

        logger.info(f"Reranked {len(docs_to_rerank)} documents using enhanced relevance scoring")
        return reranked_docs

    def get_relevance_statistics(self, documents: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate relevance statistics for a set of documents

        Args:
            documents: List of documents with scores

        Returns:
            Dictionary containing relevance statistics
        """
        if not documents:
            return {
                'mean_score': 0.0,
                'median_score': 0.0,
                'std_deviation': 0.0,
                'min_score': 0.0,
                'max_score': 0.0,
                'score_range': 0.0
            }

        scores = [doc.get('score', 0.0) for doc in documents]
        scores.sort()

        mean_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        # Calculate median
        n = len(scores)
        if n % 2 == 0:
            median_score = (scores[n//2 - 1] + scores[n//2]) / 2
        else:
            median_score = scores[n//2]

        # Calculate standard deviation
        variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
        std_deviation = variance ** 0.5

        return {
            'mean_score': mean_score,
            'median_score': median_score,
            'std_deviation': std_deviation,
            'min_score': min_score,
            'max_score': max_score,
            'score_range': max_score - min_score
        }

    def apply_diversity_filter(self, documents: List[Dict[str, Any]],
                              threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Filter documents to ensure diversity in retrieved results

        Args:
            documents: List of documents to filter
            threshold: Similarity threshold above which documents are considered too similar

        Returns:
            Filtered list of diverse documents
        """
        if len(documents) <= 1:
            return documents

        selected_docs = [documents[0]]  # Always include the top document

        for doc in documents[1:]:
            # Check similarity with already selected documents
            is_diverse = True
            for selected_doc in selected_docs:
                similarity = self.cosine_similarity(doc['embedding'], selected_doc['embedding'])
                if similarity > threshold:
                    is_diverse = False
                    break

            if is_diverse:
                selected_docs.append(doc)
            else:
                logger.debug(f"Filtered out document due to low diversity: similarity={similarity:.3f}")

        logger.info(f"Applied diversity filter: {len(documents)} -> {len(selected_docs)} documents")
        return selected_docs