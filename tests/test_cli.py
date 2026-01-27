"""Tests for CLI interface."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.cli import ChatCLI, main
from src.config import Config, ConfigError
from src.gemini_client import GeminiError


class TestChatCLI:
    """Test CLI interface."""

    @pytest.fixture
    def mock_config(self, monkeypatch):
        """Create mock configuration."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        return Config()

    @patch("src.cli.GeminiClient")
    def test_cli_initializes_with_config(self, mock_client_class, mock_config):
        """Test that CLI initializes with configuration."""
        cli = ChatCLI(mock_config)

        assert cli.config == mock_config
        assert cli.memory.is_empty()
        mock_client_class.assert_called_once()

    @patch("src.cli.GeminiClient")
    def test_handle_command_exit_returns_false(self, mock_client_class, mock_config):
        """Test that /exit and /quit commands return False."""
        cli = ChatCLI(mock_config)

        assert cli.handle_command("/exit") is False
        assert cli.handle_command("/quit") is False
        assert cli.handle_command("/EXIT") is False  # Case insensitive

    @patch("src.cli.GeminiClient")
    def test_handle_command_clear_clears_memory(self, mock_client_class, mock_config):
        """Test that /clear command clears conversation memory."""
        cli = ChatCLI(mock_config)

        # Add some messages
        cli.memory = cli.memory.add_message("user", "Hello")
        cli.memory = cli.memory.add_message("model", "Hi!")

        assert not cli.memory.is_empty()

        # Clear memory
        result = cli.handle_command("/clear")

        assert result is True
        assert cli.memory.is_empty()

    @patch("src.cli.GeminiClient")
    def test_handle_command_unknown_continues(self, mock_client_class, mock_config):
        """Test that unknown commands return True (continue)."""
        cli = ChatCLI(mock_config)

        assert cli.handle_command("/unknown") is True
        assert cli.handle_command("/help") is True

    @patch("src.cli.GeminiClient")
    def test_process_message_adds_to_memory(self, mock_client_class, mock_config):
        """Test that process_message adds messages to memory."""
        mock_client = Mock()
        mock_client.chat_stream.return_value = iter(["Test ", "response"])
        mock_client_class.return_value = mock_client

        cli = ChatCLI(mock_config)
        cli.process_message("Hello")

        # Should have user message and model response
        assert cli.memory.message_count() == 2
        history = cli.memory.get_history()
        assert history[0]["role"] == "user"
        assert history[0]["parts"][0]["text"] == "Hello"
        assert history[1]["role"] == "model"
        assert history[1]["parts"][0]["text"] == "Test response"

    @patch("src.cli.GeminiClient")
    def test_process_message_calls_client_stream(self, mock_client_class, mock_config):
        """Test that process_message calls client chat_stream."""
        mock_client = Mock()
        mock_client.chat_stream.return_value = iter(["Response"])
        mock_client_class.return_value = mock_client

        cli = ChatCLI(mock_config)
        cli.process_message("Test message")

        # Should call chat_stream with message and empty history
        mock_client.chat_stream.assert_called_once()
        call_args = mock_client.chat_stream.call_args
        assert call_args[0][0] == "Test message"
        assert call_args[0][1] == []  # Empty history

    @patch("src.cli.GeminiClient")
    def test_process_message_handles_api_error(self, mock_client_class, mock_config):
        """Test that process_message handles API errors gracefully."""
        mock_client = Mock()
        mock_client.chat_stream.side_effect = GeminiError("API failed")
        mock_client_class.return_value = mock_client

        cli = ChatCLI(mock_config)

        # Should not raise exception
        cli.process_message("Test")

        # Memory should only have user message (no response)
        assert cli.memory.message_count() == 1

    @patch("src.cli.GeminiClient")
    def test_process_message_with_history(self, mock_client_class, mock_config):
        """Test that process_message sends conversation history."""
        mock_client = Mock()
        mock_client.chat_stream.return_value = iter(["Response"])
        mock_client_class.return_value = mock_client

        cli = ChatCLI(mock_config)

        # Add initial message
        cli.memory = cli.memory.add_message("user", "First message")
        cli.memory = cli.memory.add_message("model", "First response")

        # Send second message
        cli.process_message("Second message")

        # Should send history (2 previous messages)
        call_args = mock_client.chat_stream.call_args
        history = call_args[0][1]
        assert len(history) == 2

    @patch("src.cli.GeminiClient")
    def test_show_welcome_displays_message(self, mock_client_class, mock_config):
        """Test that show_welcome displays welcome message."""
        cli = ChatCLI(mock_config)

        # Should not raise exception
        cli.show_welcome()


class TestMainFunction:
    """Test main entry point."""

    @patch("sys.argv", ["voiceai"])
    @patch("src.cli.ChatCLI")
    @patch("src.cli.Config")
    def test_main_creates_cli_and_runs(self, mock_config_class, mock_cli_class):
        """Test that main creates CLI and runs it."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        main()

        mock_config_class.assert_called_once()
        mock_cli_class.assert_called_once_with(mock_config, enable_voice=False)
        mock_cli.run.assert_called_once()

    @patch("sys.argv", ["voiceai"])
    @patch("src.cli.Config")
    def test_main_handles_config_error(self, mock_config_class):
        """Test that main handles configuration errors."""
        mock_config_class.side_effect = ConfigError("Missing API key")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch("sys.argv", ["voiceai"])
    @patch("src.cli.ChatCLI")
    @patch("src.cli.Config")
    def test_main_handles_unexpected_error(self, mock_config_class, mock_cli_class):
        """Test that main handles unexpected errors."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        mock_cli = Mock()
        mock_cli.run.side_effect = Exception("Unexpected error")
        mock_cli_class.return_value = mock_cli

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
