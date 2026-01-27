"""Tests for Gemini client."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.gemini_client import GeminiClient, GeminiError


class TestGeminiClient:
    """Test Gemini API client."""

    @patch("src.gemini_client.genai")
    def test_client_initializes_with_api_key(self, mock_genai):
        """Test that client initializes with API key."""
        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test instruction"
        )

        # Should configure API
        mock_genai.configure.assert_called_once_with(api_key="test-key")

    @patch("src.gemini_client.genai")
    def test_client_creates_model_with_config(self, mock_genai):
        """Test that client creates model with correct configuration."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test instruction",
            temperature=0.8
        )

        # Should create model with system instruction
        mock_genai.GenerativeModel.assert_called_once()
        call_kwargs = mock_genai.GenerativeModel.call_args[1]
        assert call_kwargs["model_name"] == "gemini-1.5-flash"
        assert call_kwargs["system_instruction"] == "Test instruction"

    @patch("src.gemini_client.genai")
    def test_chat_stream_yields_text_chunks(self, mock_genai):
        """Test that chat_stream yields text chunks from API."""
        # Mock streaming response
        mock_chunk1 = Mock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = Mock()
        mock_chunk2.text = "world!"

        mock_model = Mock()
        mock_model.generate_content.return_value = [mock_chunk1, mock_chunk2]
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        # Stream chat
        chunks = list(client.chat_stream("Test message", []))

        assert chunks == ["Hello ", "world!"]

    @patch("src.gemini_client.genai")
    def test_chat_stream_sends_history(self, mock_genai):
        """Test that chat_stream sends conversation history."""
        mock_model = Mock()
        mock_model.generate_content.return_value = [Mock(text="Response")]
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        history = [
            {"role": "user", "parts": [{"text": "Hello"}]},
            {"role": "model", "parts": [{"text": "Hi!"}]}
        ]

        list(client.chat_stream("New message", history))

        # Should call generate_content with history + new message
        call_args = mock_model.generate_content.call_args
        # Check if called with keyword argument 'contents'
        if call_args[1]:  # kwargs exists
            contents = call_args[1].get('contents')
        else:  # positional args
            contents = call_args[0][0]
        assert len(contents) == 3  # 2 history + 1 new

    @patch("src.gemini_client.genai")
    def test_chat_stream_handles_api_errors(self, mock_genai):
        """Test that chat_stream handles API errors gracefully."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        with pytest.raises(GeminiError, match="API Error"):
            list(client.chat_stream("Test", []))

    @patch("src.gemini_client.genai")
    def test_chat_stream_skips_empty_chunks(self, mock_genai):
        """Test that chat_stream skips chunks without text."""
        mock_chunk1 = Mock()
        mock_chunk1.text = "Hello"
        mock_chunk2 = Mock()
        mock_chunk2.text = ""  # Empty chunk
        mock_chunk3 = Mock()
        mock_chunk3.text = "World"

        mock_model = Mock()
        mock_model.generate_content.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        chunks = list(client.chat_stream("Test", []))
        assert chunks == ["Hello", "World"]

    @patch("src.gemini_client.genai")
    def test_chat_stream_validates_empty_message(self, mock_genai):
        """Test that chat_stream rejects empty messages."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        with pytest.raises(GeminiError, match="Message cannot be empty"):
            list(client.chat_stream("", []))

        with pytest.raises(GeminiError, match="Message cannot be empty"):
            list(client.chat_stream("   ", []))

    @patch("src.gemini_client.genai")
    def test_chat_stream_validates_message_length(self, mock_genai):
        """Test that chat_stream rejects messages that are too long."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        # Create a message that's too long
        long_message = "x" * 30001

        with pytest.raises(GeminiError, match="exceeds maximum length"):
            list(client.chat_stream(long_message, []))

    @patch("src.gemini_client.genai")
    def test_chat_stream_validates_history_type(self, mock_genai):
        """Test that chat_stream validates history is a list."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            system_instruction="Test"
        )

        with pytest.raises(GeminiError, match="History must be a list"):
            list(client.chat_stream("Test", "not a list"))
