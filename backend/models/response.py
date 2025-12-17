"""
Response model for the RAG Chatbot
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .document_chunk import DocumentChunk


class SourceReference(BaseModel):
    """
    Model representing a source used in the response
    """
    document_id: str = Field(..., description="Reference to document chunk")
    relative_path: str = Field(..., description="Path to source document")
    score: float = Field(..., description="Relevance score", ge=0.0, le=1.0)
    content_preview: str = Field(..., description="Preview of source content")


class Response(BaseModel):
    """
    Model representing a response to a user query
    """
    id: str = Field(..., description="Unique identifier for the response")
    query_id: str = Field(..., description="Reference to related query")
    content: str = Field(..., description="Generated response text")
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used to generate the response"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When response was generated"
    )

    class Config:
        extra = "allow"

    def validate_content(self):
        """
        Validate that content is not empty
        """
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Content must not be empty")

    def validate_sources(self, is_error_response: bool = False):
        """
        Validate sources array - must contain at least one source for non-error responses
        """
        if not is_error_response and len(self.sources) == 0:
            raise ValueError("Sources array must contain at least one source for non-error responses")

        for source in self.sources:
            if source.score < 0 or source.score > 1:
                raise ValueError(f"Each source must have a score between 0 and 1, got {source.score}")