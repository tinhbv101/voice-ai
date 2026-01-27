"""Tests for audio pipeline."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from src.audio_pipeline import AudioPipeline, PipelineError


class TestAudioPipeline:
    """Test audio pipeline orchestration."""

    @pytest.mark.asyncio
    async def test_pipeline_initializes_with_clients(self):
        """Test that pipeline initializes with TTS and converter."""
        mock_tts = Mock()
        mock_converter = Mock()

        pipeline = AudioPipeline(
            tts_client=mock_tts,
            voice_converter=mock_converter
        )

        assert pipeline.tts_client == mock_tts
        assert pipeline.voice_converter == mock_converter

    @pytest.mark.asyncio
    async def test_process_validates_empty_text(self):
        """Test that process validates empty text."""
        mock_tts = Mock()
        mock_converter = Mock()
        pipeline = AudioPipeline(mock_tts, mock_converter)

        with pytest.raises(PipelineError, match="Text cannot be empty"):
            await pipeline.process("", "/tmp/output.mp3")

    @pytest.mark.asyncio
    async def test_process_validates_output_path(self):
        """Test that process validates output path."""
        mock_tts = Mock()
        mock_converter = Mock()
        pipeline = AudioPipeline(mock_tts, mock_converter)

        with pytest.raises(PipelineError, match="Output path cannot be empty"):
            await pipeline.process("Hello", "")

    @pytest.mark.asyncio
    async def test_process_calls_tts_then_converter(self, tmp_path):
        """Test that process calls TTS then converter in sequence."""
        mock_tts = AsyncMock()
        mock_converter = Mock()

        pipeline = AudioPipeline(mock_tts, mock_converter)
        output_path = str(tmp_path / "output.mp3")

        await pipeline.process("Hello world", output_path)

        # Should call TTS synthesize
        assert mock_tts.synthesize.called
        tts_call_args = mock_tts.synthesize.call_args
        assert tts_call_args[0][0] == "Hello world"

        # Should call converter
        assert mock_converter.convert.called

    @pytest.mark.asyncio
    async def test_process_uses_temp_file_for_conversion(self, tmp_path):
        """Test that process uses temp file between TTS and conversion."""
        mock_tts = AsyncMock()
        mock_converter = Mock()

        pipeline = AudioPipeline(mock_tts, mock_converter)
        output_path = str(tmp_path / "output.mp3")

        await pipeline.process("Test", output_path)

        # TTS should save to temp file (not final output)
        tts_output = mock_tts.synthesize.call_args[0][1]
        assert "temp_" in tts_output or ".tmp" in tts_output

        # Converter should convert from temp to final output
        converter_call = mock_converter.convert.call_args
        assert converter_call[0][1] == output_path

    @pytest.mark.asyncio
    async def test_process_cleans_up_temp_file(self, tmp_path):
        """Test that process cleans up temporary file."""
        mock_tts = AsyncMock()

        # Create a real temp file
        def create_temp_file(text, path):
            Path(path).write_text("audio")

        mock_tts.synthesize.side_effect = create_temp_file
        mock_converter = Mock()

        pipeline = AudioPipeline(mock_tts, mock_converter)
        output_path = str(tmp_path / "output.mp3")

        await pipeline.process("Test", output_path)

        # Temp file should be cleaned up
        temp_files = list(tmp_path.glob("temp_*.mp3"))
        assert len(temp_files) == 0

    @pytest.mark.asyncio
    async def test_process_handles_tts_error(self):
        """Test that process handles TTS errors gracefully."""
        mock_tts = AsyncMock()
        mock_tts.synthesize.side_effect = Exception("TTS failed")
        mock_converter = Mock()

        pipeline = AudioPipeline(mock_tts, mock_converter)

        with pytest.raises(PipelineError, match="TTS synthesis failed"):
            await pipeline.process("Test", "/tmp/output.mp3")

    @pytest.mark.asyncio
    async def test_process_handles_converter_error(self, tmp_path):
        """Test that process handles converter errors gracefully."""
        mock_tts = AsyncMock()

        # TTS succeeds but creates temp file
        def create_temp(text, path):
            Path(path).write_text("audio")

        mock_tts.synthesize.side_effect = create_temp

        mock_converter = Mock()
        mock_converter.convert.side_effect = Exception("Conversion failed")

        pipeline = AudioPipeline(mock_tts, mock_converter)

        with pytest.raises(PipelineError, match="Voice conversion failed"):
            await pipeline.process("Test", str(tmp_path / "output.mp3"))

    @pytest.mark.asyncio
    async def test_process_without_converter(self, tmp_path):
        """Test that process works without voice converter."""
        mock_tts = AsyncMock()

        # TTS writes directly to output
        def write_output(text, path):
            Path(path).write_text("audio")

        mock_tts.synthesize.side_effect = write_output

        pipeline = AudioPipeline(mock_tts, voice_converter=None)
        output_path = str(tmp_path / "output.mp3")

        await pipeline.process("Test", output_path)

        # Should only call TTS, not converter
        assert mock_tts.synthesize.called
        # Output file should exist
        assert Path(output_path).exists()
