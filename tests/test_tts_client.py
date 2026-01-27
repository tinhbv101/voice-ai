"""Tests for Edge-TTS client."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from src.tts_client import EdgeTTSClient, TTSError


class TestEdgeTTSClient:
    """Test Edge-TTS client."""

    def test_client_initializes_with_voice(self):
        """Test that client initializes with voice setting."""
        client = EdgeTTSClient(voice="vi-VN-HoaiMyNeural")
        assert client.voice == "vi-VN-HoaiMyNeural"

    def test_client_uses_default_voice(self):
        """Test that client uses default voice if not specified."""
        client = EdgeTTSClient()
        assert client.voice is not None
        assert isinstance(client.voice, str)

    @pytest.mark.asyncio
    async def test_synthesize_validates_empty_text(self):
        """Test that synthesize rejects empty text."""
        client = EdgeTTSClient()

        with pytest.raises(TTSError, match="Text cannot be empty"):
            await client.synthesize("", "output.mp3")

        with pytest.raises(TTSError, match="Text cannot be empty"):
            await client.synthesize("   ", "output.mp3")

    @pytest.mark.asyncio
    async def test_synthesize_validates_output_path(self):
        """Test that synthesize validates output path."""
        client = EdgeTTSClient()

        with pytest.raises(TTSError, match="Output path cannot be empty"):
            await client.synthesize("Hello", "")

    @pytest.mark.asyncio
    @patch("src.tts_client.edge_tts.Communicate")
    async def test_synthesize_creates_audio_file(self, mock_communicate_class):
        """Test that synthesize creates audio file."""
        # Mock the edge-tts Communicate class
        mock_communicate = AsyncMock()
        mock_communicate.save = AsyncMock()
        mock_communicate_class.return_value = mock_communicate

        client = EdgeTTSClient(voice="vi-VN-HoaiMyNeural")
        output_path = "/tmp/test_output.mp3"

        await client.synthesize("Hello world", output_path)

        # Should create Communicate with text, voice, rate, and pitch
        mock_communicate_class.assert_called_once_with(
            text="Hello world",
            voice="vi-VN-HoaiMyNeural",
            rate="+0%",
            pitch="+0Hz"
        )

        # Should save to output path
        mock_communicate.save.assert_called_once_with(output_path)

    @pytest.mark.asyncio
    @patch("src.tts_client.edge_tts.Communicate")
    async def test_synthesize_handles_api_errors(self, mock_communicate_class):
        """Test that synthesize handles API errors gracefully."""
        mock_communicate = AsyncMock()
        mock_communicate.save.side_effect = Exception("TTS API failed")
        mock_communicate_class.return_value = mock_communicate

        client = EdgeTTSClient()

        with pytest.raises(TTSError, match="Failed to synthesize speech"):
            await client.synthesize("Test", "/tmp/output.mp3")

    @pytest.mark.asyncio
    @patch("src.tts_client.edge_tts.Communicate")
    async def test_synthesize_with_long_text(self, mock_communicate_class):
        """Test that synthesize handles long text."""
        mock_communicate = AsyncMock()
        mock_communicate.save = AsyncMock()
        mock_communicate_class.return_value = mock_communicate

        client = EdgeTTSClient()
        long_text = "Hello " * 1000  # Long text

        await client.synthesize(long_text, "/tmp/output.mp3")

        # Should still work
        mock_communicate.save.assert_called_once()

    def test_get_available_voices_returns_list(self):
        """Test that get_available_voices returns a list of voices."""
        voices = EdgeTTSClient.get_available_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0

        # Check Vietnamese voices are included
        vi_voices = [v for v in voices if v.startswith("vi-VN")]
        assert len(vi_voices) > 0

    def test_client_accepts_custom_rate_and_pitch(self):
        """Test that client accepts custom rate and pitch settings."""
        client = EdgeTTSClient(
            voice="vi-VN-HoaiMyNeural",
            rate="+10%",
            pitch="+5Hz"
        )
        assert client.rate == "+10%"
        assert client.pitch == "+5Hz"
