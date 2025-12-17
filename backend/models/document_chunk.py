"""
DocumentChunk model for the RAG Chatbot
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class DocumentChunk(BaseModel):
    """
    Model representing a chunk of a document with its embedding
    """
    id: str = Field(..., description="Unique identifier for the document chunk")
    content: str = Field(..., description="Text content of the document chunk")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the source document"
    )
    embedding: Optional[list] = Field(
        default=None,
        description="Vector representation of the content (optional for storage)"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of creation"
    )

    class Config:
        # Allow extra fields for flexibility with metadata
        extra = "allow"

    def validate_content(self):
        """
        Validate that content is not empty
        """
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Content must not be empty")

    def validate_embedding(self):
        """
        Validate embedding dimensions (1024 for Cohere multilingual model)
        """
        if self.embedding:
            if len(self.embedding) != 1024:  # Standard size for Cohere embeddings
                raise ValueError(f"Embedding must have 1024 dimensions, got {len(self.embedding)}")

    def validate_metadata(self):
        """
        Validate metadata structure
        """
        if "relative_path" not in self.metadata:
            raise ValueError("metadata.relative_path must be a valid path reference")