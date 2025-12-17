"""
Unit tests for the Citation Service
"""
import unittest
from ..services.citation_service import CitationService
from ..models.response import SourceReference


class TestCitationService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.citation_service = CitationService()

    def test_create_source_references(self):
        """Test creating source references from retrieved documents."""
        # Create test documents
        retrieved_docs = [
            {
                'id': 'doc1',
                'content': 'Test content 1',
                'metadata': {'relative_path': 'test/path1.md'},
                'score': 0.85
            },
            {
                'id': 'doc2',
                'content': 'Test content 2',
                'metadata': {'relative_path': 'test/path2.md'},
                'score': 0.72
            }
        ]

        source_refs = self.citation_service.create_source_references(retrieved_docs)

        # Check that correct number of source references were created
        self.assertEqual(len(source_refs), 2)
        self.assertIsInstance(source_refs[0], SourceReference)
        self.assertEqual(source_refs[0].document_id, 'doc1')
        self.assertEqual(source_refs[0].relative_path, 'test/path1.md')
        self.assertEqual(source_refs[0].score, 0.85)

    def test_truncate_content(self):
        """Test content truncation."""
        long_content = "A" * 300  # 300 characters
        truncated = self.citation_service._truncate_content(long_content, max_length=100)

        # Should be truncated to 100 chars + "..."
        self.assertEqual(len(truncated), 103)  # 100 + 3 for "..."
        self.assertTrue(truncated.endswith("..."))

        # Test with content shorter than max length
        short_content = "Short content"
        not_truncated = self.citation_service._truncate_content(short_content, max_length=100)
        self.assertEqual(not_truncated, "Short content")

    def test_format_citation_text(self):
        """Test formatting citation text."""
        source_ref = SourceReference(
            document_id='doc1',
            relative_path='test/path.md',
            score=0.85,
            content_preview='Test content preview'
        )

        citation_text = self.citation_service.format_citation_text(source_ref)

        # Should contain path and formatted score
        self.assertIn('test/path.md', citation_text)
        self.assertIn('0.85', citation_text)

    def test_format_multiple_citations(self):
        """Test formatting multiple citation texts."""
        source_refs = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path1.md',
                score=0.85,
                content_preview='Test content 1'
            ),
            SourceReference(
                document_id='doc2',
                relative_path='test/path2.md',
                score=0.72,
                content_preview='Test content 2'
            )
        ]

        citation_texts = self.citation_service.format_multiple_citations(source_refs)

        # Should return list of formatted citation texts
        self.assertEqual(len(citation_texts), 2)
        self.assertIsInstance(citation_texts[0], str)
        self.assertIn('test/path1.md', citation_texts[0])

    def test_validate_source_references(self):
        """Test validating source references."""
        # Valid source references
        valid_sources = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path.md',
                score=0.85,
                content_preview='Test content'
            )
        ]

        is_valid = self.citation_service.validate_source_references(valid_sources)
        self.assertTrue(is_valid)

        # Invalid source reference with bad score
        invalid_sources = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path.md',
                score=1.5,  # Score > 1.0
                content_preview='Test content'
            )
        ]

        is_valid = self.citation_service.validate_source_references(invalid_sources)
        self.assertFalse(is_valid)

        # Empty list should be invalid
        is_valid = self.citation_service.validate_source_references([])
        self.assertFalse(is_valid)

    def test_filter_by_relevance_threshold(self):
        """Test filtering sources by relevance threshold."""
        sources = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path1.md',
                score=0.9,
                content_preview='Test content 1'
            ),
            SourceReference(
                document_id='doc2',
                relative_path='test/path2.md',
                score=0.3,
                content_preview='Test content 2'
            ),
            SourceReference(
                document_id='doc3',
                relative_path='test/path3.md',
                score=0.7,
                content_preview='Test content 3'
            )
        ]

        # Filter with threshold of 0.5
        filtered_sources = self.citation_service.filter_by_relevance_threshold(sources, min_score=0.5)

        # Should only include sources with score >= 0.5
        self.assertEqual(len(filtered_sources), 2)
        for source in filtered_sources:
            self.assertGreaterEqual(source.score, 0.5)

    def test_sort_sources_by_relevance(self):
        """Test sorting sources by relevance."""
        sources = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path1.md',
                score=0.3,
                content_preview='Test content 1'
            ),
            SourceReference(
                document_id='doc2',
                relative_path='test/path2.md',
                score=0.9,
                content_preview='Test content 2'
            ),
            SourceReference(
                document_id='doc3',
                relative_path='test/path3.md',
                score=0.7,
                content_preview='Test content 3'
            )
        ]

        sorted_sources = self.citation_service.sort_sources_by_relevance(sources)

        # Should be sorted in descending order of score
        self.assertEqual(sorted_sources[0].score, 0.9)
        self.assertEqual(sorted_sources[1].score, 0.7)
        self.assertEqual(sorted_sources[2].score, 0.3)

    def test_get_top_k_sources(self):
        """Test getting top k sources."""
        sources = [
            SourceReference(
                document_id='doc1',
                relative_path='test/path1.md',
                score=0.3,
                content_preview='Test content 1'
            ),
            SourceReference(
                document_id='doc2',
                relative_path='test/path2.md',
                score=0.9,
                content_preview='Test content 2'
            ),
            SourceReference(
                document_id='doc3',
                relative_path='test/path3.md',
                score=0.7,
                content_preview='Test content 3'
            )
        ]

        top_2_sources = self.citation_service.get_top_k_sources(sources, k=2)

        # Should return top 2 sources sorted by score
        self.assertEqual(len(top_2_sources), 2)
        self.assertEqual(top_2_sources[0].score, 0.9)  # Highest score first
        self.assertEqual(top_2_sources[1].score, 0.7)  # Second highest

    def test_create_context_preview(self):
        """Test creating context preview."""
        content = "This is a long content with multiple sentences. " * 20  # Repeat to make it long
        query = "long content"

        preview = self.citation_service.create_context_preview(content, query, snippet_size=50)

        # Should return a preview string
        self.assertIsInstance(preview, str)
        self.assertLessEqual(len(preview), 100)  # 2 * snippet_size

        # Test without query (should return beginning of content)
        preview_no_query = self.citation_service.create_context_preview(content, query=None)
        self.assertIsInstance(preview_no_query, str)

    def test_create_source_preview(self):
        """Test creating detailed source preview."""
        source_ref = SourceReference(
            document_id='doc1',
            relative_path='test/path.md',
            score=0.85,
            content_preview='Test content preview'
        )

        preview = self.citation_service.create_source_preview(source_ref)

        # Should return a dictionary with all required fields
        self.assertIsInstance(preview, dict)
        self.assertIn('document_id', preview)
        self.assertIn('relative_path', preview)
        self.assertIn('score', preview)
        self.assertIn('preview', preview)
        self.assertIn('relevance_indicator', preview)
        self.assertIn('content_length', preview)

        # Check that values are correct
        self.assertEqual(preview['document_id'], 'doc1')
        self.assertEqual(preview['score'], 0.85)
        self.assertEqual(preview['preview'], 'Test content preview')

    def test_get_relevance_indicator(self):
        """Test getting relevance indicator text."""
        # Test different score ranges
        self.assertEqual(self.citation_service._get_relevance_indicator(0.9), "Highly Relevant")
        self.assertEqual(self.citation_service._get_relevance_indicator(0.7), "Relevant")
        self.assertEqual(self.citation_service._get_relevance_indicator(0.5), "Moderately Relevant")
        self.assertEqual(self.citation_service._get_relevance_indicator(0.3), "Slightly Relevant")
        self.assertEqual(self.citation_service._get_relevance_indicator(0.1), "Minimally Relevant")


if __name__ == '__main__':
    unittest.main()