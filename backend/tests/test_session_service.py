"""
Unit tests for the Session Service
"""
import unittest
from datetime import datetime, timedelta
from ..services.session_service import SessionService
from ..models.session import Session, Message


class TestSessionService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.session_service = SessionService()

    def test_create_session(self):
        """Test creating a new session."""
        session = self.session_service.create_session(user_id="test_user", metadata={"test": "value"})

        # Check that session was created with correct properties
        self.assertIsInstance(session, Session)
        self.assertIsNotNone(session.id)
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.metadata, {"test": "value"})
        self.assertTrue(session.is_active)
        self.assertEqual(len(session.messages), 0)

    def test_get_session(self):
        """Test getting an existing session."""
        # Create a session first
        session = self.session_service.create_session()
        session_id = session.id

        # Retrieve the session
        retrieved_session = self.session_service.get_session(session_id)

        # Should return the same session
        self.assertEqual(retrieved_session.id, session_id)
        self.assertEqual(retrieved_session.user_id, session.user_id)

        # Test getting non-existent session
        non_existent = self.session_service.get_session("non-existent-id")
        self.assertIsNone(non_existent)

    def test_add_message_to_session(self):
        """Test adding a message to a session."""
        session = self.session_service.create_session()
        session_id = session.id

        # Add a message
        message = self.session_service.add_message_to_session(session_id, "user", "Hello, world!")

        # Check that message was added
        self.assertIsNotNone(message)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello, world!")

        # Check that session now has the message
        updated_session = self.session_service.get_session(session_id)
        self.assertEqual(len(updated_session.messages), 1)
        self.assertEqual(updated_session.messages[0].content, "Hello, world!")

    def test_get_session_messages(self):
        """Test getting messages from a session."""
        session = self.session_service.create_session()
        session_id = session.id

        # Add multiple messages
        self.session_service.add_message_to_session(session_id, "user", "Message 1")
        self.session_service.add_message_to_session(session_id, "assistant", "Message 2")
        self.session_service.add_message_to_session(session_id, "user", "Message 3")

        # Get all messages
        messages = self.session_service.get_session_messages(session_id)
        self.assertEqual(len(messages), 3)

        # Get limited messages
        limited_messages = self.session_service.get_session_messages(session_id, limit=2)
        self.assertEqual(len(limited_messages), 2)

    def test_delete_session(self):
        """Test deleting a session."""
        session = self.session_service.create_session()
        session_id = session.id

        # Verify session exists
        self.assertIsNotNone(self.session_service.get_session(session_id))

        # Delete the session
        result = self.session_service.delete_session(session_id)

        # Should return True for successful deletion
        self.assertTrue(result)

        # Session should no longer exist
        self.assertIsNone(self.session_service.get_session(session_id))

        # Deleting non-existent session should return False
        result = self.session_service.delete_session("non-existent-id")
        self.assertFalse(result)

    def test_session_expiration(self):
        """Test that expired sessions are handled correctly."""
        session = self.session_service.create_session()
        session_id = session.id

        # Manually set the session to be expired by changing its updated_at time
        session = self.session_service.get_session(session_id)
        session.updated_at = datetime.now() - timedelta(hours=25)  # More than 24 hours ago
        self.session_service.update_session(session)

        # Try to get the expired session - should return None
        retrieved_session = self.session_service.get_session(session_id)
        self.assertIsNone(retrieved_session)

    def test_clear_session_messages(self):
        """Test clearing messages from a session."""
        session = self.session_service.create_session()
        session_id = session.id

        # Add some messages
        self.session_service.add_message_to_session(session_id, "user", "Message 1")
        self.session_service.add_message_to_session(session_id, "assistant", "Message 2")

        # Verify messages exist
        messages = self.session_service.get_session_messages(session_id)
        self.assertEqual(len(messages), 2)

        # Clear messages
        result = self.session_service.clear_session_messages(session_id)
        self.assertTrue(result)

        # Verify messages are cleared
        messages = self.session_service.get_session_messages(session_id)
        self.assertEqual(len(messages), 0)

        # Clearing messages from non-existent session should return False
        result = self.session_service.clear_session_messages("non-existent-id")
        self.assertFalse(result)

    def test_get_active_sessions_count(self):
        """Test getting count of active sessions."""
        # Initially should be 0
        count = self.session_service.get_active_sessions_count()
        self.assertEqual(count, 0)

        # Create a session
        self.session_service.create_session()
        count = self.session_service.get_active_sessions_count()
        self.assertEqual(count, 1)

        # Create another session
        self.session_service.create_session()
        count = self.session_service.get_active_sessions_count()
        self.assertEqual(count, 2)

    def test_get_user_sessions(self):
        """Test getting all sessions for a specific user."""
        # Create sessions for different users
        user1_session1 = self.session_service.create_session(user_id="user1")
        user1_session2 = self.session_service.create_session(user_id="user1")
        user2_session = self.session_service.create_session(user_id="user2")

        # Get sessions for user1
        user1_sessions = self.session_service.get_user_sessions("user1")
        self.assertEqual(len(user1_sessions), 2)

        # Get sessions for user2
        user2_sessions = self.session_service.get_user_sessions("user2")
        self.assertEqual(len(user2_sessions), 1)

        # Get sessions for non-existent user
        no_sessions = self.session_service.get_user_sessions("non-existent")
        self.assertEqual(len(no_sessions), 0)

    def test_end_session(self):
        """Test ending a session."""
        session = self.session_service.create_session()
        session_id = session.id

        # Verify session is active
        session = self.session_service.get_session(session_id)
        self.assertTrue(session.is_active)

        # End the session
        result = self.session_service.end_session(session_id)
        self.assertTrue(result)

        # Verify session is no longer active
        session = self.session_service.get_session(session_id)
        self.assertFalse(session.is_active)

        # Ending non-existent session should return False
        result = self.session_service.end_session("non-existent-id")
        self.assertFalse(result)

    def test_get_session_summary(self):
        """Test getting session summary."""
        session = self.session_service.create_session(
            user_id="test_user",
            metadata={"source": "web", "version": "1.0"}
        )
        session_id = session.id

        # Add a message to change message count
        self.session_service.add_message_to_session(session_id, "user", "Test message")

        # Get summary
        summary = self.session_service.get_session_summary(session_id)

        # Check that summary has all required fields
        self.assertIsNotNone(summary)
        self.assertEqual(summary["id"], session_id)
        self.assertEqual(summary["user_id"], "test_user")
        self.assertEqual(summary["message_count"], 1)
        self.assertTrue(summary["is_active"])
        self.assertEqual(summary["metadata"], {"source": "web", "version": "1.0"})

        # Summary for non-existent session should return None
        summary = self.session_service.get_session_summary("non-existent-id")
        self.assertIsNone(summary)


if __name__ == '__main__':
    unittest.main()