"""WebSocket protocol definitions and message handling."""

import json
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


class MessageType(str, Enum):
    """WebSocket message types."""

    # Client to Server
    TEXT_INPUT = "text_input"          # User text message
    AUDIO_CHUNK = "audio_chunk"        # Audio data chunk
    START_RECORDING = "start_recording"  # Start audio recording
    STOP_RECORDING = "stop_recording"    # Stop audio recording
    VAD_AUDIO = "vad_audio"            # Complete audio from VAD (Voice Activity Detection)

    # Server to Client
    TEXT_RESPONSE = "text_response"    # AI text response (streaming)
    AUDIO_RESPONSE = "audio_response"  # AI audio response
    TRANSCRIPT = "transcript"          # STT transcript
    STATUS = "status"                  # Status update
    ERROR = "error"                    # Error message

    # Control
    PING = "ping"
    PONG = "pong"


@dataclass
class WebSocketMessage:
    """Base WebSocket message structure."""

    type: MessageType
    data: Any
    session_id: Optional[str] = None
    timestamp: Optional[float] = None

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "session_id": self.session_id,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            data=data["data"],
            session_id=data.get("session_id"),
            timestamp=data.get("timestamp")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "type": self.type.value,
            "data": self.data,
            "session_id": self.session_id,
            "timestamp": self.timestamp
        }


class ProtocolError(Exception):
    """Raised when protocol validation fails."""
    pass


class MessageValidator:
    """Validates WebSocket messages."""

    @staticmethod
    def validate_text_input(data: Any) -> bool:
        """Validate text input message."""
        if not isinstance(data, dict):
            raise ProtocolError("Text input data must be a dictionary")

        if "text" not in data:
            raise ProtocolError("Text input must contain 'text' field")

        if not isinstance(data["text"], str):
            raise ProtocolError("Text must be a string")

        if not data["text"].strip():
            raise ProtocolError("Text cannot be empty")

        return True

    @staticmethod
    def validate_audio_chunk(data: Any) -> bool:
        """Validate audio chunk message."""
        if not isinstance(data, dict):
            raise ProtocolError("Audio chunk data must be a dictionary")

        if "audio" not in data:
            raise ProtocolError("Audio chunk must contain 'audio' field")

        # Audio should be base64 encoded string or bytes
        if not isinstance(data["audio"], (str, bytes)):
            raise ProtocolError("Audio must be string or bytes")

        return True

    @staticmethod
    def validate_message(message: WebSocketMessage) -> bool:
        """
        Validate message based on type.

        Args:
            message: Message to validate

        Returns:
            True if valid

        Raises:
            ProtocolError: If validation fails
        """
        if message.type == MessageType.TEXT_INPUT:
            return MessageValidator.validate_text_input(message.data)

        if message.type == MessageType.AUDIO_CHUNK:
            return MessageValidator.validate_audio_chunk(message.data)

        # Other message types have minimal validation
        return True


def create_text_response(text: str, session_id: Optional[str] = None) -> WebSocketMessage:
    """Create a text response message."""
    return WebSocketMessage(
        type=MessageType.TEXT_RESPONSE,
        data={"text": text},
        session_id=session_id
    )


def create_error_message(error: str, session_id: Optional[str] = None) -> WebSocketMessage:
    """Create an error message."""
    return WebSocketMessage(
        type=MessageType.ERROR,
        data={"error": error},
        session_id=session_id
    )


def create_status_message(status: str, session_id: Optional[str] = None) -> WebSocketMessage:
    """Create a status message."""
    return WebSocketMessage(
        type=MessageType.STATUS,
        data={"status": status},
        session_id=session_id
    )


def create_transcript_message(
    transcript: str,
    is_final: bool = False,
    session_id: Optional[str] = None
) -> WebSocketMessage:
    """Create a transcript message."""
    return WebSocketMessage(
        type=MessageType.TRANSCRIPT,
        data={
            "transcript": transcript,
            "is_final": is_final
        },
        session_id=session_id
    )


def create_audio_response_message(
    audio_base64: str,
    session_id: Optional[str] = None
) -> WebSocketMessage:
    """Create an audio response message."""
    return WebSocketMessage(
        type=MessageType.AUDIO_RESPONSE,
        data={"audio": audio_base64},
        session_id=session_id
    )
