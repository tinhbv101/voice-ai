"""Tests for conversation memory management."""

import pytest
from src.memory import ConversationMemory


class TestConversationMemory:
    """Test conversation memory management."""

    def test_memory_initializes_empty(self):
        """Test that memory starts with no messages."""
        memory = ConversationMemory(max_messages=10)
        assert memory.get_history() == []
        assert memory.message_count() == 0

    def test_add_user_message(self):
        """Test adding a user message."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Hello")

        history = memory.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["parts"][0]["text"] == "Hello"

    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("model", "Hi there!")

        history = memory.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "model"
        assert history[0]["parts"][0]["text"] == "Hi there!"

    def test_add_multiple_messages(self):
        """Test adding multiple messages in sequence."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Hello")
        memory = memory.add_message("model", "Hi!")
        memory = memory.add_message("user", "How are you?")

        assert memory.message_count() == 3
        history = memory.get_history()
        assert history[0]["parts"][0]["text"] == "Hello"
        assert history[1]["parts"][0]["text"] == "Hi!"
        assert history[2]["parts"][0]["text"] == "How are you?"

    def test_memory_maintains_limit(self):
        """Test that memory maintains max message limit."""
        memory = ConversationMemory(max_messages=3)

        # Add 5 messages
        memory = memory.add_message("user", "Message 1")
        memory = memory.add_message("model", "Response 1")
        memory = memory.add_message("user", "Message 2")
        memory = memory.add_message("model", "Response 2")
        memory = memory.add_message("user", "Message 3")

        # Should only keep the last 3
        assert memory.message_count() == 3
        history = memory.get_history()
        assert history[0]["parts"][0]["text"] == "Message 2"
        assert history[1]["parts"][0]["text"] == "Response 2"
        assert history[2]["parts"][0]["text"] == "Message 3"

    def test_clear_removes_all_messages(self):
        """Test that clear removes all messages."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Hello")
        memory = memory.add_message("model", "Hi!")

        memory = memory.clear()

        assert memory.message_count() == 0
        assert memory.get_history() == []

    def test_memory_is_immutable(self):
        """Test that add_message returns new instance (immutability)."""
        memory1 = ConversationMemory(max_messages=10)
        memory2 = memory1.add_message("user", "Hello")

        # Original should be unchanged
        assert memory1.message_count() == 0
        # New instance should have the message
        assert memory2.message_count() == 1

    def test_get_history_returns_copy(self):
        """Test that get_history returns a copy (immutability)."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Hello")

        history1 = memory.get_history()
        history2 = memory.get_history()

        # Should be equal but not the same object
        assert history1 == history2
        assert history1 is not history2

    def test_message_format_is_correct(self):
        """Test that messages are formatted correctly for Gemini API."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Test message")

        history = memory.get_history()
        message = history[0]

        # Check structure
        assert "role" in message
        assert "parts" in message
        assert isinstance(message["parts"], list)
        assert len(message["parts"]) == 1
        assert "text" in message["parts"][0]

    def test_add_message_invalid_role_raises_error(self):
        """Test that invalid role raises ValueError."""
        memory = ConversationMemory(max_messages=10)

        with pytest.raises(ValueError, match="Invalid role"):
            memory.add_message("invalid_role", "Test content")

    def test_add_message_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        memory = ConversationMemory(max_messages=10)

        with pytest.raises(ValueError, match="Content cannot be empty"):
            memory.add_message("user", "")

        with pytest.raises(ValueError, match="Content cannot be empty"):
            memory.add_message("user", "   ")

    def test_is_empty_returns_true_for_new_memory(self):
        """Test that is_empty returns True for new memory."""
        memory = ConversationMemory(max_messages=10)
        assert memory.is_empty() is True

    def test_is_empty_returns_false_after_add(self):
        """Test that is_empty returns False after adding message."""
        memory = ConversationMemory(max_messages=10)
        memory = memory.add_message("user", "Hello")
        assert memory.is_empty() is False
