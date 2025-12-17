"""
Session model for the RAG Chatbot
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4


class Message(BaseModel):
    """
    Model representing a message in the conversation history
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique message identifier")
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Message timestamp"
    )
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata for the message")

    def validate_role(self):
        """
        Validate that role is either 'user' or 'assistant'
        """
        if self.role not in ['user', 'assistant']:
            raise ValueError(f"Role must be 'user' or 'assistant', got {self.role}")


class Session(BaseModel):
    """
    Model representing a user session with conversation history
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session identifier")
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Session start time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the session was last updated"
    )
    messages: List[Message] = Field(
        default_factory=list,
        description="Messages in the conversation"
    )
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata for the session")
    is_active: bool = Field(default=True, description="Whether the session is currently active")

    class Config:
        extra = "allow"

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a message to the session

        Args:
            role: Role of the message sender (user or assistant)
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            The created Message object
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get messages from the session, optionally limited to a number

        Args:
            limit: Maximum number of messages to return (from the end)

        Returns:
            List of messages
        """
        if limit is None:
            return self.messages
        return self.messages[-limit:] if len(self.messages) >= limit else self.messages

    def get_last_message(self) -> Optional[Message]:
        """
        Get the last message in the session

        Returns:
            Last message or None if no messages exist
        """
        if not self.messages:
            return None
        return self.messages[-1]

    def clear_messages(self):
        """
        Clear all messages from the session
        """
        self.messages = []
        self.updated_at = datetime.now()

    def get_message_count(self) -> int:
        """
        Get the total number of messages in the session

        Returns:
            Number of messages
        """
        return len(self.messages)

    def update_last_activity(self):
        """
        Update updated_at timestamp to current time
        """
        self.updated_at = datetime.now()

    def is_expired(self, hours: int = 24) -> bool:
        """
        Check if session has expired (after 24 hours of inactivity by default)
        """
        time_diff = datetime.now() - self.updated_at
        return time_diff > timedelta(hours=hours)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary representation

        Returns:
            Dictionary representation of the session
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.model_dump() for msg in self.messages],
            "metadata": self.metadata,
            "is_active": self.is_active
        }