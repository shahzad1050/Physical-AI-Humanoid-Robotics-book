"""
Session management service for the RAG Chatbot
"""
from typing import Dict, Optional, List
import logging
from datetime import datetime
from uuid import uuid4

from ..models.session import Session, Message
from ..utils import get_logger

logger = get_logger(__name__)


class SessionService:
    """
    Service for managing conversation sessions
    """
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.logger = get_logger(__name__)

    def create_session(self, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Session:
        """
        Create a new conversation session

        Args:
            user_id: Optional user identifier
            metadata: Optional metadata for the session

        Returns:
            Created Session object
        """
        session_id = str(uuid4())
        session = Session(
            id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        self.sessions[session_id] = session
        self.logger.info(f"Created new session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID

        Args:
            session_id: Session identifier

        Returns:
            Session object if found, None otherwise
        """
        session = self.sessions.get(session_id)
        if session:
            # Check if session is expired
            if session.is_expired():
                self.logger.info(f"Session {session_id} has expired, removing it")
                del self.sessions[session_id]
                return None
        return session

    def update_session(self, session: Session) -> Session:
        """
        Update an existing session

        Args:
            session: Session object to update

        Returns:
            Updated Session object
        """
        session.update_last_activity()
        self.sessions[session.id] = session
        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session identifier to delete

        Returns:
            True if session was deleted, False if it didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def add_message_to_session(self, session_id: str, role: str, content: str,
                             metadata: Optional[Dict] = None) -> Optional[Message]:
        """
        Add a message to a session

        Args:
            session_id: Session identifier
            role: Role of the message sender (user or assistant)
            content: Content of the message
            metadata: Optional metadata for the message

        Returns:
            Created Message object if successful, None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            self.logger.warning(f"Cannot add message to non-existent session: {session_id}")
            return None

        message = session.add_message(role, content, metadata)
        self.update_session(session)
        self.logger.debug(f"Added message to session {session_id}, now has {session.get_message_count()} messages")
        return message

    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> Optional[List[Message]]:
        """
        Get messages from a session

        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return

        Returns:
            List of messages if session exists, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None
        return session.get_messages(limit)

    def clear_session_messages(self, session_id: str) -> bool:
        """
        Clear all messages from a session while keeping the session

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        session.clear_messages()
        self.update_session(session)
        self.logger.info(f"Cleared messages from session: {session_id}")
        return True

    def get_active_sessions_count(self) -> int:
        """
        Get the count of active sessions

        Returns:
            Number of active sessions
        """
        count = 0
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
            else:
                count += 1

        # Clean up expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return count

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions

        Returns:
            Number of sessions that were cleaned up
        """
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)

    def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all sessions for a specific user

        Args:
            user_id: User identifier

        Returns:
            List of sessions for the user
        """
        user_sessions = []
        for session in self.sessions.values():
            if session.user_id == user_id:
                # Check if session is expired
                if session.is_expired():
                    self.logger.info(f"Session {session.id} for user {user_id} has expired")
                    continue
                user_sessions.append(session)
        return user_sessions

    def end_session(self, session_id: str) -> bool:
        """
        Mark a session as inactive

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        session.is_active = False
        session.update_last_activity()
        self.update_session(session)
        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """
        Get a summary of a session

        Args:
            session_id: Session identifier

        Returns:
            Session summary dictionary if session exists, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "id": session.id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": session.get_message_count(),
            "is_active": session.is_active,
            "metadata": session.metadata
        }