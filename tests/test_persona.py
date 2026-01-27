"""Tests for persona module."""

import pytest
from src.persona import get_system_instruction


class TestPersona:
    """Test persona and system instruction generation."""

    def test_get_system_instruction_returns_string(self):
        """Test that system instruction is returned as a string."""
        instruction = get_system_instruction()
        assert isinstance(instruction, str)
        assert len(instruction) > 0

    def test_system_instruction_includes_character_traits(self):
        """Test that system instruction includes key character traits."""
        instruction = get_system_instruction()

        # Should include personality traits
        assert "playful" in instruction.lower() or "vui vẻ" in instruction.lower()
        assert "casual" in instruction.lower() or "thân thiện" in instruction.lower()

    def test_system_instruction_mentions_vietnamese(self):
        """Test that system instruction specifies Vietnamese language."""
        instruction = get_system_instruction()
        assert "vietnamese" in instruction.lower() or "tiếng việt" in instruction.lower()

    def test_system_instruction_mentions_informal_speech(self):
        """Test that system instruction mentions informal speech style."""
        instruction = get_system_instruction()
        assert "mày" in instruction.lower() or "tao" in instruction.lower() or "informal" in instruction.lower()

    def test_get_character_name_returns_string(self):
        """Test that character name is returned as a string."""
        from src.persona import get_character_name
        name = get_character_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_welcome_message_includes_commands(self):
        """Test that welcome message includes command instructions."""
        from src.persona import get_welcome_message
        message = get_welcome_message()
        assert isinstance(message, str)
        assert "/clear" in message
        assert "/exit" in message or "/quit" in message
        assert "Ctrl+C" in message or "ctrl+c" in message.lower()
