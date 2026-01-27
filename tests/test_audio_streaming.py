"""Tests for audio streaming handler."""

import pytest
import base64
from src.audio_streaming import (
    AudioBuffer,
    AudioStreamHandler,
    AudioStreamManager,
    AudioStreamingError
)


class TestAudioBuffer:
    """Test audio buffer."""

    @pytest.mark.asyncio
    async def test_buffer_initializes_empty(self):
        """Test that buffer initializes empty."""
        buffer = AudioBuffer()
        size = await buffer.size()
        assert size == 0

    @pytest.mark.asyncio
    async def test_add_chunk(self):
        """Test adding audio chunk."""
        buffer = AudioBuffer()
        await buffer.add_chunk(b"audio_data")

        size = await buffer.size()
        assert size == len(b"audio_data")

    @pytest.mark.asyncio
    async def test_add_multiple_chunks(self):
        """Test adding multiple chunks."""
        buffer = AudioBuffer()
        await buffer.add_chunk(b"chunk1")
        await buffer.add_chunk(b"chunk2")
        await buffer.add_chunk(b"chunk3")

        data = await buffer.get_data()
        assert data == b"chunk1chunk2chunk3"

    @pytest.mark.asyncio
    async def test_buffer_overflow(self):
        """Test buffer overflow protection."""
        buffer = AudioBuffer(max_size=10)

        await buffer.add_chunk(b"12345")

        with pytest.raises(AudioStreamingError, match="Buffer overflow"):
            await buffer.add_chunk(b"67890_overflow")

    @pytest.mark.asyncio
    async def test_clear_buffer(self):
        """Test clearing buffer."""
        buffer = AudioBuffer()
        await buffer.add_chunk(b"audio_data")
        await buffer.clear()

        size = await buffer.size()
        assert size == 0

    @pytest.mark.asyncio
    async def test_get_data_returns_all(self):
        """Test getting all buffered data."""
        buffer = AudioBuffer()
        await buffer.add_chunk(b"part1")
        await buffer.add_chunk(b"part2")

        data = await buffer.get_data()
        assert data == b"part1part2"


class TestAudioStreamHandler:
    """Test audio stream handler."""

    @pytest.mark.asyncio
    async def test_handler_initializes(self):
        """Test handler initialization."""
        handler = AudioStreamHandler("session-123")

        assert handler.session_id == "session-123"
        assert handler.is_recording is False

    @pytest.mark.asyncio
    async def test_start_recording(self):
        """Test starting recording."""
        handler = AudioStreamHandler("session-123")

        await handler.start_recording()

        assert handler.is_recording is True

    @pytest.mark.asyncio
    async def test_stop_recording(self):
        """Test stopping recording."""
        handler = AudioStreamHandler("session-123")

        await handler.start_recording()
        await handler.add_audio_chunk(base64.b64encode(b"audio"))

        audio_data = await handler.stop_recording()

        assert handler.is_recording is False
        assert len(audio_data) > 0

    @pytest.mark.asyncio
    async def test_add_chunk_while_recording(self):
        """Test adding chunks while recording."""
        handler = AudioStreamHandler("session-123")

        await handler.start_recording()
        
        # Add base64-encoded chunks as strings (like from WebSocket JSON)
        chunk1_b64 = base64.b64encode(b"chunk1").decode('utf-8')
        chunk2_b64 = base64.b64encode(b"chunk2").decode('utf-8')
        
        await handler.add_audio_chunk(chunk1_b64)
        await handler.add_audio_chunk(chunk2_b64)

        buffer_size = await handler.get_buffer_size()
        # Buffer contains decoded data, not base64
        assert buffer_size == len(b"chunk1") + len(b"chunk2")

    @pytest.mark.asyncio
    async def test_add_chunk_not_recording(self):
        """Test adding chunk when not recording."""
        handler = AudioStreamHandler("session-123")

        with pytest.raises(AudioStreamingError, match="Not recording"):
            await handler.add_audio_chunk(base64.b64encode(b"audio"))

    @pytest.mark.asyncio
    async def test_add_chunk_raw_bytes(self):
        """Test adding raw bytes instead of base64."""
        handler = AudioStreamHandler("session-123")

        await handler.start_recording()
        await handler.add_audio_chunk(b"raw_audio")

        buffer_size = await handler.get_buffer_size()
        assert buffer_size == len(b"raw_audio")

    @pytest.mark.asyncio
    async def test_callback_on_complete(self):
        """Test callback when recording completes."""
        callback_data = []

        async def on_complete(data):
            callback_data.append(data)

        handler = AudioStreamHandler("session-123", on_audio_complete=on_complete)

        await handler.start_recording()
        await handler.add_audio_chunk(b"audio")
        await handler.stop_recording()

        assert len(callback_data) == 1
        assert callback_data[0] == b"audio"


class TestAudioStreamManager:
    """Test audio stream manager."""

    def test_manager_initializes(self):
        """Test manager initialization."""
        manager = AudioStreamManager()
        assert manager.get_active_count() == 0

    def test_create_stream(self):
        """Test creating stream."""
        manager = AudioStreamManager()
        stream = manager.create_stream("session-123")

        assert stream is not None
        assert stream.session_id == "session-123"
        assert manager.get_active_count() == 1

    def test_create_stream_duplicate(self):
        """Test creating duplicate stream."""
        manager = AudioStreamManager()

        stream1 = manager.create_stream("session-123")
        stream2 = manager.create_stream("session-123")

        assert stream1 is stream2
        assert manager.get_active_count() == 1

    def test_get_stream(self):
        """Test getting stream."""
        manager = AudioStreamManager()
        created = manager.create_stream("session-123")

        retrieved = manager.get_stream("session-123")

        assert retrieved is created

    def test_get_stream_not_exists(self):
        """Test getting non-existent stream."""
        manager = AudioStreamManager()

        stream = manager.get_stream("non-existent")

        assert stream is None

    def test_remove_stream(self):
        """Test removing stream."""
        manager = AudioStreamManager()
        manager.create_stream("session-123")

        manager.remove_stream("session-123")

        assert manager.get_active_count() == 0
        assert manager.get_stream("session-123") is None

    def test_multiple_streams(self):
        """Test managing multiple streams."""
        manager = AudioStreamManager()

        stream1 = manager.create_stream("session-1")
        stream2 = manager.create_stream("session-2")
        stream3 = manager.create_stream("session-3")

        assert manager.get_active_count() == 3

        manager.remove_stream("session-2")

        assert manager.get_active_count() == 2
        assert manager.get_stream("session-1") is not None
        assert manager.get_stream("session-2") is None
        assert manager.get_stream("session-3") is not None
