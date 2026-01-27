"""Tests for STT client using Faster-Whisper."""

import pytest
import asyncio
from pathlib import Path
import tempfile
import wave

from src.stt_client import FasterWhisperClient, STTError


# Create a simple test audio file (silence)
def create_test_audio_file(duration_seconds=1) -> Path:
    """Create a temporary WAV file with silence for testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = Path(temp_file.name)
    
    # Create a simple WAV file (silence)
    sample_rate = 16000
    num_channels = 1
    sample_width = 2  # 16-bit
    
    with wave.open(str(temp_path), 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        # Write silence
        num_frames = sample_rate * duration_seconds
        silence = b'\x00' * (num_frames * num_channels * sample_width)
        wav_file.writeframes(silence)
    
    return temp_path


class TestFasterWhisperClient:
    """Test suite for FasterWhisperClient."""

    def test_client_initialization(self):
        """Test that client initializes successfully."""
        client = FasterWhisperClient(model_size="tiny")
        assert client.model_size == "tiny"
        assert client.device == "cpu"
        assert client.compute_type == "int8"
        client.close()

    def test_client_initialization_with_params(self):
        """Test client initialization with custom parameters."""
        client = FasterWhisperClient(
            model_size="base",
            device="cpu",
            compute_type="int8"
        )
        assert client.model_size == "base"
        assert client.device == "cpu"
        assert client.compute_type == "int8"
        client.close()

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio(self):
        """Test transcription of empty/silence audio."""
        client = FasterWhisperClient(model_size="tiny")
        
        try:
            # Create test audio file
            audio_path = create_test_audio_file(duration_seconds=1)
            
            # Transcribe
            result = await client.transcribe(
                audio_path,
                language="en",
                vad_filter=False  # Disable VAD for silence test
            )
            
            # Check result structure
            assert isinstance(result, dict)
            assert "text" in result
            assert "segments" in result
            assert "language" in result
            assert "duration" in result
            
            # Silence should produce empty or minimal transcription
            assert isinstance(result["text"], str)
            assert isinstance(result["segments"], list)
            assert result["language"] == "en"
            assert result["duration"] > 0
            
        finally:
            client.close()
            # Cleanup
            if audio_path.exists():
                audio_path.unlink()

    @pytest.mark.asyncio
    async def test_transcribe_with_vad(self):
        """Test transcription with VAD enabled."""
        client = FasterWhisperClient(model_size="tiny")
        
        try:
            audio_path = create_test_audio_file(duration_seconds=1)
            
            result = await client.transcribe(
                audio_path,
                vad_filter=True
            )
            
            assert isinstance(result, dict)
            assert "text" in result
            
        finally:
            client.close()
            if audio_path.exists():
                audio_path.unlink()

    @pytest.mark.asyncio
    async def test_transcribe_audio_bytes(self):
        """Test transcription from audio bytes."""
        client = FasterWhisperClient(model_size="tiny")
        
        try:
            # Create test audio file and read bytes
            audio_path = create_test_audio_file(duration_seconds=1)
            audio_bytes = audio_path.read_bytes()
            
            # Transcribe from bytes
            result = await client.transcribe_audio_bytes(
                audio_bytes,
                language="en"
            )
            
            assert isinstance(result, dict)
            assert "text" in result
            assert "segments" in result
            
        finally:
            client.close()
            if audio_path.exists():
                audio_path.unlink()

    def test_transcribe_sync(self):
        """Test synchronous transcription."""
        client = FasterWhisperClient(model_size="tiny")
        
        try:
            audio_path = create_test_audio_file(duration_seconds=1)
            
            result = client.transcribe_sync(
                audio_path,
                language="en"
            )
            
            assert isinstance(result, dict)
            assert "text" in result
            
        finally:
            client.close()
            if audio_path.exists():
                audio_path.unlink()

    def test_transcribe_invalid_file(self):
        """Test transcription with invalid file."""
        client = FasterWhisperClient(model_size="tiny")
        
        try:
            with pytest.raises(STTError):
                client.transcribe_sync("nonexistent_file.wav")
        finally:
            client.close()

    def test_client_close(self):
        """Test client cleanup."""
        client = FasterWhisperClient(model_size="tiny")
        client.close()
        # Should not raise any errors


@pytest.mark.asyncio
async def test_multiple_concurrent_transcriptions():
    """Test multiple concurrent transcriptions."""
    client = FasterWhisperClient(model_size="tiny")
    
    try:
        # Create multiple test files
        audio_paths = [
            create_test_audio_file(duration_seconds=1),
            create_test_audio_file(duration_seconds=1),
            create_test_audio_file(duration_seconds=1)
        ]
        
        # Transcribe concurrently
        tasks = [
            client.transcribe(path, language="en")
            for path in audio_paths
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)
            assert "text" in result
            
    finally:
        client.close()
        # Cleanup
        for path in audio_paths:
            if path.exists():
                path.unlink()
