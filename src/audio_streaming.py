"""Audio streaming handler for WebSocket audio data."""

import base64
import asyncio
from typing import Optional, Callable
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class AudioStreamingError(Exception):
    """Raised when audio streaming encounters an error."""
    pass


class AudioBuffer:
    """Buffer for accumulating audio chunks."""

    def __init__(self, max_size: int = 1024 * 1024):  # 1MB default
        """
        Initialize audio buffer.

        Args:
            max_size: Maximum buffer size in bytes
        """
        self.buffer = BytesIO()
        self.max_size = max_size
        self._lock = asyncio.Lock()

    async def add_chunk(self, chunk: bytes) -> None:
        """
        Add audio chunk to buffer.

        Args:
            chunk: Audio data bytes

        Raises:
            AudioStreamingError: If buffer exceeds max size
        """
        async with self._lock:
            current_size = self.buffer.tell()

            if current_size + len(chunk) > self.max_size:
                raise AudioStreamingError(
                    f"Buffer overflow: {current_size + len(chunk)} > {self.max_size}"
                )

            self.buffer.write(chunk)

    async def get_data(self) -> bytes:
        """
        Get all buffered audio data.

        Returns:
            Audio data bytes
        """
        async with self._lock:
            self.buffer.seek(0)
            data = self.buffer.read()
            return data

    async def clear(self) -> None:
        """Clear buffer."""
        async with self._lock:
            self.buffer = BytesIO()

    async def size(self) -> int:
        """
        Get current buffer size.

        Returns:
            Size in bytes
        """
        async with self._lock:
            return self.buffer.tell()


class AudioStreamHandler:
    """Handles audio streaming for a single session."""

    def __init__(
        self,
        session_id: str,
        on_audio_complete: Optional[Callable] = None
    ):
        """
        Initialize audio stream handler.

        Args:
            session_id: Session identifier
            on_audio_complete: Callback when audio recording completes
        """
        self.session_id = session_id
        self.buffer = AudioBuffer()
        self.is_recording = False
        self.on_audio_complete = on_audio_complete

    async def start_recording(self) -> None:
        """Start audio recording."""
        if self.is_recording:
            logger.warning(f"Session {self.session_id} already recording")
            return

        self.is_recording = True
        await self.buffer.clear()
        logger.info(f"Started recording for session {self.session_id}")

    async def stop_recording(self) -> bytes:
        """
        Stop audio recording and return buffered data.

        Returns:
            Audio data bytes
        """
        if not self.is_recording:
            logger.warning(f"Session {self.session_id} not recording")
            return b""

        self.is_recording = False
        audio_data = await self.buffer.get_data()
        logger.info(
            f"Stopped recording for session {self.session_id}, "
            f"collected {len(audio_data)} bytes"
        )

        # Call completion callback if provided
        if self.on_audio_complete:
            await self.on_audio_complete(audio_data)

        return audio_data

    async def add_audio_chunk(self, chunk_data: str) -> None:
        """
        Add audio chunk from WebSocket message.

        Args:
            chunk_data: Base64 encoded audio data or raw bytes

        Raises:
            AudioStreamingError: If not recording or invalid data
        """
        if not self.is_recording:
            raise AudioStreamingError("Not recording audio")

        try:
            # Decode base64 if string
            if isinstance(chunk_data, str):
                audio_bytes = base64.b64decode(chunk_data)
            else:
                audio_bytes = chunk_data

            await self.buffer.add_chunk(audio_bytes)

        except Exception as e:
            raise AudioStreamingError(f"Failed to add audio chunk: {str(e)}") from e

    async def get_buffer_size(self) -> int:
        """
        Get current buffer size.

        Returns:
            Size in bytes
        """
        return await self.buffer.size()


class AudioStreamManager:
    """Manages audio streams for multiple sessions."""

    def __init__(self):
        """Initialize audio stream manager."""
        self.streams: dict[str, AudioStreamHandler] = {}

    def create_stream(
        self,
        session_id: str,
        on_audio_complete: Optional[Callable] = None
    ) -> AudioStreamHandler:
        """
        Create audio stream for session.

        Args:
            session_id: Session identifier
            on_audio_complete: Callback when audio completes

        Returns:
            Audio stream handler
        """
        if session_id in self.streams:
            logger.warning(f"Stream already exists for session {session_id}")
            return self.streams[session_id]

        stream = AudioStreamHandler(session_id, on_audio_complete)
        self.streams[session_id] = stream
        logger.info(f"Created audio stream for session {session_id}")

        return stream

    def get_stream(self, session_id: str) -> Optional[AudioStreamHandler]:
        """
        Get audio stream for session.

        Args:
            session_id: Session identifier

        Returns:
            Audio stream handler or None
        """
        return self.streams.get(session_id)

    def remove_stream(self, session_id: str) -> None:
        """
        Remove audio stream for session.

        Args:
            session_id: Session identifier
        """
        if session_id in self.streams:
            del self.streams[session_id]
            logger.info(f"Removed audio stream for session {session_id}")

    def get_active_count(self) -> int:
        """
        Get number of active streams.

        Returns:
            Number of active streams
        """
        return len(self.streams)
