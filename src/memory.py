"""Conversation memory management with circular buffer."""

from typing import List, Dict, Any
from copy import deepcopy


# Valid message roles for Gemini API
VALID_ROLES = {"user", "model"}


class ConversationMemory:
    """
    Manages conversation history with a maximum message limit.

    Uses immutable pattern - all operations return new instances.
    """

    def __init__(self, max_messages: int = 10, messages: List[Dict[str, Any]] = None):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to store
            messages: Initial messages (for internal use)
        """
        self._max_messages = max_messages
        self._messages = messages if messages is not None else []

    def add_message(self, role: str, content: str) -> "ConversationMemory":
        """
        Add a message to the conversation history.

        Returns a new ConversationMemory instance (immutable pattern).

        Args:
            role: Message role ("user" or "model")
            content: Message content text

        Returns:
            New ConversationMemory instance with the added message

        Raises:
            ValueError: If role is invalid or content is empty
        """
        # Validate inputs
        if role not in VALID_ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Must be one of: {VALID_ROLES}"
            )

        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        # Create message in Gemini API format
        new_message = {
            "role": role,
            "parts": [{"text": content}]
        }

        # Create new message list (immutable)
        new_messages = self._messages + [new_message]

        # Maintain maximum message limit (FIFO)
        if len(new_messages) > self._max_messages:
            new_messages = new_messages[-self._max_messages:]

        return ConversationMemory(
            max_messages=self._max_messages,
            messages=new_messages
        )

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get conversation history in Gemini API format.

        Returns a deep copy to maintain immutability.

        Returns:
            List of message dictionaries
        """
        return deepcopy(self._messages)

    def clear(self) -> "ConversationMemory":
        """
        Clear all messages from memory.

        Returns a new ConversationMemory instance (immutable pattern).

        Returns:
            New empty ConversationMemory instance
        """
        return ConversationMemory(max_messages=self._max_messages)

    def message_count(self) -> int:
        """
        Get the number of messages in memory.

        Returns:
            Number of messages
        """
        return len(self._messages)

    def is_empty(self) -> bool:
        """
        Check if memory is empty.

        Returns:
            True if no messages in memory
        """
        return len(self._messages) == 0
