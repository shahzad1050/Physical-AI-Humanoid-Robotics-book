"""
Query model for the RAG Chatbot
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class Query(BaseModel):
    """
    Model representing a user query
    """
    id: str = Field(..., description="Unique identifier for the query")
    content: str = Field(..., description="User's question/query")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When query was made"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Optional user identifier for tracking purposes"
    )

    class Config:
        extra = "allow"

    @validator('content')
    def validate_content(cls, v):
        """
        Validate that content is not empty and not too long
        """
        if not v or len(v.strip()) == 0:
            raise ValueError('Content must not be empty')

        if len(v) > 1000:
            raise ValueError('Content must be less than 1000 characters')

        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """
        Validate that timestamp is current or past
        """
        if v > datetime.now():
            raise ValueError('Timestamp must be current or past')
        return v