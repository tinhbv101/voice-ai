"""Tests for WebSocket protocol."""

import pytest
import json
from src.websocket_protocol import (
    MessageType,
    WebSocketMessage,
    MessageValidator,
    ProtocolError,
    create_text_response,
    create_error_message,
    create_status_message,
    create_transcript_message
)


class TestMessageType:
    """Test message type enum."""

    def test_message_types_exist(self):
        """Test that all message types are defined."""
        assert MessageType.TEXT_INPUT == "text_input"
        assert MessageType.TEXT_RESPONSE == "text_response"
        assert MessageType.AUDIO_CHUNK == "audio_chunk"
        assert MessageType.STATUS == "status"
        assert MessageType.ERROR == "error"


class TestWebSocketMessage:
    """Test WebSocket message class."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = WebSocketMessage(
            type=MessageType.TEXT_INPUT,
            data={"text": "Hello"},
            session_id="test-123"
        )

        assert msg.type == MessageType.TEXT_INPUT
        assert msg.data == {"text": "Hello"}
        assert msg.session_id == "test-123"

    def test_message_to_json(self):
        """Test converting message to JSON."""
        msg = WebSocketMessage(
            type=MessageType.TEXT_INPUT,
            data={"text": "Hello"},
            session_id="test-123"
        )

        json_str = msg.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "text_input"
        assert parsed["data"]["text"] == "Hello"
        assert parsed["session_id"] == "test-123"

    def test_message_from_json(self):
        """Test creating message from JSON."""
        json_str = json.dumps({
            "type": "text_input",
            "data": {"text": "Hello"},
            "session_id": "test-123",
            "timestamp": 12345.67
        })

        msg = WebSocketMessage.from_json(json_str)

        assert msg.type == MessageType.TEXT_INPUT
        assert msg.data["text"] == "Hello"
        assert msg.session_id == "test-123"
        assert msg.timestamp == 12345.67

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = WebSocketMessage(
            type=MessageType.STATUS,
            data={"status": "connected"},
            session_id="test-123"
        )

        msg_dict = msg.to_dict()

        assert msg_dict["type"] == "status"
        assert msg_dict["data"]["status"] == "connected"
        assert msg_dict["session_id"] == "test-123"


class TestMessageValidator:
    """Test message validation."""

    def test_validate_text_input_success(self):
        """Test validating valid text input."""
        data = {"text": "Hello world"}
        assert MessageValidator.validate_text_input(data) is True

    def test_validate_text_input_not_dict(self):
        """Test validating text input that is not a dict."""
        with pytest.raises(ProtocolError, match="must be a dictionary"):
            MessageValidator.validate_text_input("not a dict")

    def test_validate_text_input_missing_text(self):
        """Test validating text input missing text field."""
        with pytest.raises(ProtocolError, match="must contain 'text' field"):
            MessageValidator.validate_text_input({"other": "field"})

    def test_validate_text_input_text_not_string(self):
        """Test validating text input where text is not string."""
        with pytest.raises(ProtocolError, match="Text must be a string"):
            MessageValidator.validate_text_input({"text": 123})

    def test_validate_text_input_empty_text(self):
        """Test validating text input with empty text."""
        with pytest.raises(ProtocolError, match="Text cannot be empty"):
            MessageValidator.validate_text_input({"text": "   "})

    def test_validate_audio_chunk_success(self):
        """Test validating valid audio chunk."""
        data = {"audio": "base64encodeddata"}
        assert MessageValidator.validate_audio_chunk(data) is True

    def test_validate_audio_chunk_not_dict(self):
        """Test validating audio chunk that is not a dict."""
        with pytest.raises(ProtocolError, match="must be a dictionary"):
            MessageValidator.validate_audio_chunk("not a dict")

    def test_validate_audio_chunk_missing_audio(self):
        """Test validating audio chunk missing audio field."""
        with pytest.raises(ProtocolError, match="must contain 'audio' field"):
            MessageValidator.validate_audio_chunk({"other": "field"})

    def test_validate_audio_chunk_invalid_type(self):
        """Test validating audio chunk with invalid audio type."""
        with pytest.raises(ProtocolError, match="Audio must be string or bytes"):
            MessageValidator.validate_audio_chunk({"audio": 123})

    def test_validate_message_text_input(self):
        """Test validating text input message."""
        msg = WebSocketMessage(
            type=MessageType.TEXT_INPUT,
            data={"text": "Hello"},
            session_id="test"
        )

        assert MessageValidator.validate_message(msg) is True

    def test_validate_message_audio_chunk(self):
        """Test validating audio chunk message."""
        msg = WebSocketMessage(
            type=MessageType.AUDIO_CHUNK,
            data={"audio": b"audio_data"},
            session_id="test"
        )

        assert MessageValidator.validate_message(msg) is True


class TestMessageHelpers:
    """Test message helper functions."""

    def test_create_text_response(self):
        """Test creating text response message."""
        msg = create_text_response("Hello", "session-123")

        assert msg.type == MessageType.TEXT_RESPONSE
        assert msg.data["text"] == "Hello"
        assert msg.session_id == "session-123"

    def test_create_error_message(self):
        """Test creating error message."""
        msg = create_error_message("Something went wrong", "session-123")

        assert msg.type == MessageType.ERROR
        assert msg.data["error"] == "Something went wrong"
        assert msg.session_id == "session-123"

    def test_create_status_message(self):
        """Test creating status message."""
        msg = create_status_message("Connected", "session-123")

        assert msg.type == MessageType.STATUS
        assert msg.data["status"] == "Connected"
        assert msg.session_id == "session-123"

    def test_create_transcript_message(self):
        """Test creating transcript message."""
        msg = create_transcript_message("Hello world", is_final=True, session_id="session-123")

        assert msg.type == MessageType.TRANSCRIPT
        assert msg.data["transcript"] == "Hello world"
        assert msg.data["is_final"] is True
        assert msg.session_id == "session-123"
