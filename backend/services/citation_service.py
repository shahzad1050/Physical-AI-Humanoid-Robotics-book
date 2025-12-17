"""
Source citation service for the RAG Chatbot
"""
from typing import List, Dict, Any
import logging
from pydantic import BaseModel

from ..models.response import SourceReference
from ..utils import get_logger

logger = get_logger(__name__)


class CitationService:
    """
    Service for generating and formatting source citations
    """
    def __init__(self):
        self.logger = get_logger(__name__)

    def create_source_references(self, retrieved_docs: List[Dict[str, Any]]) -> List[SourceReference]:
        """
        Create source references from retrieved documents

        Args:
            retrieved_docs: List of retrieved documents with scores and metadata

        Returns:
            List of SourceReference objects
        """
        sources = []
        for doc in retrieved_docs:
            source_ref = SourceReference(
                document_id=str(doc.get('id', 'unknown')),
                relative_path=doc['metadata'].get('relative_path', 'Unknown'),
                score=doc.get('score', 0.0),
                content_preview=self._truncate_content(doc['content'], 200)
            )
            sources.append(source_ref)
        return sources

    def _truncate_content(self, content: str, max_length: int = 200) -> str:
        """
        Truncate content to specified length with ellipsis

        Args:
            content: Content to truncate
            max_length: Maximum length for content preview

        Returns:
            Truncated content with ellipsis if needed
        """
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def create_context_preview(self, content: str, query: str = None, snippet_size: int = 150) -> str:
        """
        Create a context preview highlighting relevant snippets based on query

        Args:
            content: Full content to create preview from
            query: Query to match against for relevant snippets (optional)
            snippet_size: Size of each snippet to extract

        Returns:
            Context preview with relevant snippets
        """
        if not query:
            # If no query provided, return the beginning of the content
            return self._truncate_content(content, snippet_size)

        # Find query terms in the content
        query_words = query.lower().split()
        content_lower = content.lower()

        # Find locations of query terms in the content
        term_positions = []
        for word in query_words:
            start = 0
            while True:
                pos = content_lower.find(word, start)
                if pos == -1:
                    break
                term_positions.append(pos)
                start = pos + 1

        if not term_positions:
            # If no query terms found, return the beginning of the content
            return self._truncate_content(content, snippet_size)

        # Sort positions and get snippets around them
        term_positions = sorted(set(term_positions))  # Remove duplicates
        snippets = []
        processed_end = -1

        for pos in term_positions:
            # Skip if this position is already covered by a previous snippet
            if pos < processed_end:
                continue

            # Calculate snippet start and end positions
            start = max(0, pos - snippet_size // 2)
            end = min(len(content), start + snippet_size)

            # Adjust start if we're at the end of the content
            if end - start < snippet_size:
                start = max(0, end - snippet_size)

            snippet = content[start:end]
            snippets.append(snippet.strip())
            processed_end = end

            # Limit to 2 snippets to keep preview manageable
            if len(snippets) >= 2:
                break

        if snippets:
            preview = " ... ".join(snippets)
            if len(preview) > snippet_size * 2:
                preview = self._truncate_content(preview, snippet_size * 2)
            return preview
        else:
            return self._truncate_content(content, snippet_size)

    def create_source_preview(self, source_ref: SourceReference, full_content: str = None) -> Dict[str, Any]:
        """
        Create a detailed preview of a source reference

        Args:
            source_ref: Source reference to create preview for
            full_content: Full content to use for more detailed preview (optional)

        Returns:
            Dictionary containing detailed source preview information
        """
        preview_content = full_content if full_content else source_ref.content_preview

        return {
            "document_id": source_ref.document_id,
            "relative_path": source_ref.relative_path,
            "score": source_ref.score,
            "preview": preview_content,
            "relevance_indicator": self._get_relevance_indicator(source_ref.score),
            "content_length": len(preview_content) if preview_content else 0
        }

    def _get_relevance_indicator(self, score: float) -> str:
        """
        Get a text indicator for the relevance score

        Args:
            score: Relevance score between 0 and 1

        Returns:
            Text indicator for the score
        """
        if score >= 0.8:
            return "Highly Relevant"
        elif score >= 0.6:
            return "Relevant"
        elif score >= 0.4:
            return "Moderately Relevant"
        elif score >= 0.2:
            return "Slightly Relevant"
        else:
            return "Minimally Relevant"

    def format_citation_text(self, source: SourceReference) -> str:
        """
        Format a source reference as human-readable citation text

        Args:
            source: Source reference to format

        Returns:
            Formatted citation text
        """
        return f"[{source.relative_path}] (Relevance: {source.score:.2f})"

    def format_multiple_citations(self, sources: List[SourceReference]) -> List[str]:
        """
        Format multiple source references as human-readable citation texts

        Args:
            sources: List of source references to format

        Returns:
            List of formatted citation texts
        """
        return [self.format_citation_text(source) for source in sources]

    def validate_source_references(self, sources: List[SourceReference]) -> bool:
        """
        Validate source references meet quality criteria

        Args:
            sources: List of source references to validate

        Returns:
            True if all sources are valid, False otherwise
        """
        if not sources:
            self.logger.warning("No source references provided")
            return False

        for i, source in enumerate(sources):
            # Validate score range
            if not (0.0 <= source.score <= 1.0):
                self.logger.warning(f"Source {i} has invalid score: {source.score}")
                return False

            # Validate required fields
            if not source.document_id:
                self.logger.warning(f"Source {i} has empty document_id")
                return False

            if not source.relative_path:
                self.logger.warning(f"Source {i} has empty relative_path")
                return False

        return True

    def filter_by_relevance_threshold(self, sources: List[SourceReference], min_score: float = 0.3) -> List[SourceReference]:
        """
        Filter sources based on minimum relevance score threshold

        Args:
            sources: List of source references to filter
            min_score: Minimum score threshold for inclusion

        Returns:
            Filtered list of source references
        """
        filtered_sources = []
        for source in sources:
            if source.score >= min_score:
                filtered_sources.append(source)
            else:
                self.logger.debug(f"Filtering out source with low score: {source.score} < {min_score}")

        self.logger.info(f"Filtered {len(sources)} sources to {len(filtered_sources)} based on threshold {min_score}")
        return filtered_sources

    def sort_sources_by_relevance(self, sources: List[SourceReference]) -> List[SourceReference]:
        """
        Sort sources by relevance score in descending order

        Args:
            sources: List of source references to sort

        Returns:
            Sorted list of source references
        """
        return sorted(sources, key=lambda x: x.score, reverse=True)

    def get_top_k_sources(self, sources: List[SourceReference], k: int) -> List[SourceReference]:
        """
        Get top k most relevant sources

        Args:
            sources: List of source references to select from
            k: Number of top sources to return

        Returns:
            Top k source references
        """
        sorted_sources = self.sort_sources_by_relevance(sources)
        return sorted_sources[:k]