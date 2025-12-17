"""
Unit tests for the Retrieval Service
"""
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from ..services.retrieval_service import RetrievalService


class TestRetrievalService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        with patch('..services.retrieval_service.settings') as mock_settings:
            # Configure mock settings
            mock_settings.openai_api_key = 'test-key'
            mock_settings.cohere_api_key = 'test-key'
            mock_settings.embedding_model = 'test-model'
            mock_settings.embedding_input_type = 'search_query'
            mock_settings.embedding_dimensions = 1024
            mock_settings.embedded_docs_path = 'test/path.json'

            # Mock the file reading
            with patch('builtins.open', unittest.mock.mock_open(read_data='[]')):
                self.retrieval_service = RetrievalService()

            # Manually set embedded_docs for testing
            self.retrieval_service.embedded_docs = [
                {
                    'id': 'doc1',
                    'content': 'Test document content 1',
                    'metadata': {'relative_path': 'test/path1.md'},
                    'embedding': np.array([0.1, 0.2, 0.3])
                },
                {
                    'id': 'doc2',
                    'content': 'Test document content 2',
                    'metadata': {'relative_path': 'test/path2.md'},
                    'embedding': np.array([0.4, 0.5, 0.6])
                },
                {
                    'id': 'doc3',
                    'content': 'Test document content 3',
                    'metadata': {'relative_path': 'test/path3.md'},
                    'embedding': np.array([0.7, 0.8, 0.9])
                }
            ]

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation between two vectors."""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])

        similarity = self.retrieval_service.cosine_similarity(vec1, vec2)

        # Orthogonal vectors should have 0 similarity
        self.assertAlmostEqual(similarity, 0.0, places=5)

        # Same vectors should have 1.0 similarity
        similarity_same = self.retrieval_service.cosine_similarity(vec1, vec1)
        self.assertAlmostEqual(similarity_same, 1.0, places=5)

        # Test with zero vectors
        zero_vec = np.array([0, 0, 0])
        similarity_zero = self.retrieval_service.cosine_similarity(vec1, zero_vec)
        self.assertAlmostEqual(similarity_zero, 0.0, places=5)

    def test_find_similar_documents_returns_correct_count(self):
        """Test that find_similar_documents returns correct number of documents."""
        query_embedding = np.array([0.1, 0.2, 0.3])

        # Request top 2 documents
        result = self.retrieval_service.find_similar_documents(query_embedding, top_k=2)

        # Should return 2 documents (or fewer if there aren't enough)
        self.assertLessEqual(len(result), 2)
        self.assertIsInstance(result, list)

        # Each result should have required fields
        for doc in result:
            self.assertIn('id', doc)
            self.assertIn('content', doc)
            self.assertIn('metadata', doc)
            self.assertIn('score', doc)

    def test_find_similar_documents_with_min_score(self):
        """Test that find_similar_documents respects minimum score threshold."""
        query_embedding = np.array([0.1, 0.2, 0.3])

        # Use a high min_score to filter out low-scoring documents
        result = self.retrieval_service.find_similar_documents(
            query_embedding,
            top_k=5,
            min_score=1.0  # Very high threshold
        )

        # With high threshold, should return empty list or very few results
        self.assertLessEqual(len(result), 1)

    def test_find_similar_documents_empty_docs(self):
        """Test that find_similar_documents handles empty documents list."""
        # Temporarily clear the embedded docs
        original_docs = self.retrieval_service.embedded_docs
        self.retrieval_service.embedded_docs = []

        query_embedding = np.array([0.1, 0.2, 0.3])
        result = self.retrieval_service.find_similar_documents(query_embedding)

        # Should return empty list
        self.assertEqual(result, [])

        # Restore original docs
        self.retrieval_service.embedded_docs = original_docs

    def test_rerank_documents(self):
        """Test the rerank_documents functionality."""
        query_embedding = np.array([0.1, 0.2, 0.3])

        # Create test documents with initial scores
        documents = [
            {
                'id': 'doc1',
                'content': 'Test content 1',
                'metadata': {'relative_path': 'test/path1.md'},
                'embedding': np.array([0.1, 0.2, 0.3]),
                'score': 0.5
            },
            {
                'id': 'doc2',
                'content': 'Test content 2',
                'metadata': {'relative_path': 'test/path2.md'},
                'embedding': np.array([0.4, 0.5, 0.6]),
                'score': 0.3
            }
        ]

        reranked_docs = self.retrieval_service.rerank_documents(query_embedding, documents)

        # Should return same number of documents
        self.assertEqual(len(reranked_docs), 2)

        # Scores should be updated
        for doc in reranked_docs:
            self.assertIn('score', doc)
            self.assertGreaterEqual(doc['score'], 0.0)
            self.assertLessEqual(doc['score'], 1.0)

    def test_get_relevance_statistics(self):
        """Test the get_relevance_statistics functionality."""
        # Create test documents with different scores
        documents = [
            {'score': 0.9},
            {'score': 0.7},
            {'score': 0.5},
            {'score': 0.3},
            {'score': 0.1}
        ]

        stats = self.retrieval_service.get_relevance_statistics(documents)

        # Check that all required statistics are present
        self.assertIn('mean_score', stats)
        self.assertIn('median_score', stats)
        self.assertIn('std_deviation', stats)
        self.assertIn('min_score', stats)
        self.assertIn('max_score', stats)
        self.assertIn('score_range', stats)

        # Check that values are reasonable
        self.assertGreaterEqual(stats['mean_score'], 0.0)
        self.assertLessEqual(stats['mean_score'], 1.0)
        self.assertGreaterEqual(stats['max_score'], stats['min_score'])

    def test_apply_diversity_filter(self):
        """Test the apply_diversity_filter functionality."""
        # Create test documents with embeddings
        documents = [
            {
                'id': 'doc1',
                'content': 'Test content 1',
                'metadata': {'relative_path': 'test/path1.md'},
                'embedding': np.array([0.1, 0.2, 0.3]),
                'score': 0.9
            },
            {
                'id': 'doc2',
                'content': 'Test content 2',
                'metadata': {'relative_path': 'test/path2.md'},
                'embedding': np.array([0.11, 0.21, 0.31]),  # Very similar to doc1
                'score': 0.8
            },
            {
                'id': 'doc3',
                'content': 'Test content 3',
                'metadata': {'relative_path': 'test/path3.md'},
                'embedding': np.array([0.8, 0.9, 1.0]),  # Different from others
                'score': 0.7
            }
        ]

        filtered_docs = self.retrieval_service.apply_diversity_filter(documents, threshold=0.9)

        # Should return fewer documents if there are similar ones
        self.assertLessEqual(len(filtered_docs), len(documents))
        self.assertGreaterEqual(len(filtered_docs), 1)  # At least one should remain


if __name__ == '__main__':
    unittest.main()