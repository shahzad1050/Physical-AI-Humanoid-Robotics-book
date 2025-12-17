"""
Unit tests for the RAG Agent service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from typing import List, Dict, Any

from ..services.rag_agent import RAGAgent


class TestRAGAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the dependencies to avoid actual API calls
        with patch('..services.rag_agent.OpenAI'), \
             patch('..services.rag_agent.cohere'), \
             patch('..services.rag_agent.settings') as mock_settings:

            # Configure mock settings
            mock_settings.openai_api_key = 'test-key'
            mock_settings.cohere_api_key = 'test-key'
            mock_settings.embedding_model = 'test-model'
            mock_settings.embedding_input_type = 'search_query'
            mock_settings.embedding_dimensions = 1024
            mock_settings.embedded_docs_path = 'test/path.json'

            # Mock the file reading
            with patch('builtins.open', unittest.mock.mock_open(read_data='[]')):
                self.rag_agent = RAGAgent()

            # Manually set embedded_docs for testing
            self.rag_agent.embedded_docs = [
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
                }
            ]

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation between two vectors."""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])

        similarity = self.rag_agent.cosine_similarity(vec1, vec2)

        # Orthogonal vectors should have 0 similarity
        self.assertAlmostEqual(similarity, 0.0, places=5)

        # Same vectors should have 1.0 similarity
        similarity_same = self.rag_agent.cosine_similarity(vec1, vec1)
        self.assertAlmostEqual(similarity_same, 1.0, places=5)

    def test_retrieve_context_returns_documents(self):
        """Test that retrieve_context returns documents."""
        # Mock embed_query to return a simple vector
        with patch.object(self.rag_agent, 'embed_query') as mock_embed:
            mock_embed.return_value = np.array([0.1, 0.2, 0.3])

            result = self.rag_agent.retrieve_context('test query', top_k=2)

            # Should return 2 documents (or fewer if there aren't enough)
            self.assertIsInstance(result, list)
            self.assertLessEqual(len(result), 2)

    def test_chat_method_returns_proper_structure(self):
        """Test that chat method returns proper structure."""
        # Mock the methods to avoid actual API calls
        with patch.object(self.rag_agent, 'retrieve_context') as mock_retrieve, \
             patch.object(self.rag_agent, 'generate_response') as mock_generate:

            mock_retrieve.return_value = [
                {
                    'id': 'doc1',
                    'content': 'Test content',
                    'metadata': {'relative_path': 'test.md'},
                    'score': 0.8
                }
            ]
            mock_generate.return_value = 'Test response'

            result = self.rag_agent.chat('test query', top_k=1)

            # Check structure of result
            self.assertIn('response', result)
            self.assertIn('context_used', result)
            self.assertIn('query', result)
            self.assertEqual(result['response'], 'Test response')
            self.assertEqual(result['query'], 'test query')

    def test_chat_with_context_method(self):
        """Test that chat_with_context method works properly."""
        # Mock the methods to avoid actual API calls
        with patch.object(self.rag_agent, 'retrieve_context') as mock_retrieve, \
             patch.object(self.rag_agent, 'generate_response_with_context') as mock_generate:

            mock_retrieve.return_value = [
                {
                    'id': 'doc1',
                    'content': 'Test content',
                    'metadata': {'relative_path': 'test.md'},
                    'score': 0.8
                }
            ]
            mock_generate.return_value = 'Test response with context'

            result = self.rag_agent.chat_with_context('test query', ['User: Hello', 'Assistant: Hi'], top_k=1)

            # Check structure of result
            self.assertIn('response', result)
            self.assertIn('context_used', result)
            self.assertIn('query', result)
            self.assertEqual(result['response'], 'Test response with context')
            self.assertEqual(result['query'], 'test query')

    def test_generate_response_with_context(self):
        """Test the generate_response_with_context method."""
        # This method involves OpenAI API call, so we'll mock it
        context_docs = [
            {
                'id': 'doc1',
                'content': 'Test content',
                'metadata': {'relative_path': 'test.md'},
                'score': 0.8
            }
        ]
        conversation_context = ['User: Hello', 'Assistant: Hi there']
        query = 'How are you?'

        with patch.object(self.rag_agent, 'openai_client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'Fine, thank you!'
            mock_client.chat.completions.create.return_value = mock_response

            result = self.rag_agent.generate_response_with_context(query, context_docs, conversation_context)

            self.assertEqual(result, 'Fine, thank you!')
            # Verify that the API was called
            mock_client.chat.completions.create.assert_called_once()


if __name__ == '__main__':
    unittest.main()