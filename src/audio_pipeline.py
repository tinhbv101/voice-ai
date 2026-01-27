"""Audio processing pipeline: Text → TTS → Voice Conversion → Audio."""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from src.tts_client import EdgeTTSClient, TTSError
from src.voice_converter import VoiceConverterProtocol, VoiceConversionError


class PipelineError(Exception):
    """Raised when audio pipeline processing fails."""
    pass


class AudioPipeline:
    """
    Audio processing pipeline that chains TTS and voice conversion.

    Pipeline flow:
    1. Text → Edge-TTS → Base audio (temp file)
    2. Base audio → Voice Converter → Character audio (output file)
    3. Cleanup temp files
    """

    def __init__(
        self,
        tts_client: EdgeTTSClient,
        voice_converter: Optional[VoiceConverterProtocol] = None
    ):
        """
        Initialize audio pipeline.

        Args:
            tts_client: Text-to-speech client
            voice_converter: Optional voice converter (if None, skip conversion)
        """
        self.tts_client = tts_client
        self.voice_converter = voice_converter

    async def process(self, text: str, output_path: str) -> None:
        """
        Process text through the full audio pipeline.

        Args:
            text: Text to convert to speech
            output_path: Path to save final audio file

        Raises:
            PipelineError: If any step in the pipeline fails
        """
        # Validate inputs
        if not text or not text.strip():
            raise PipelineError("Text cannot be empty")

        if not output_path:
            raise PipelineError("Output path cannot be empty")

        # Create output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        temp_file_path = None

        try:
            # If voice converter is enabled, use temp file
            if self.voice_converter:
                # Step 1: TTS → Temp file
                with tempfile.NamedTemporaryFile(
                    suffix=".mp3",
                    prefix="temp_tts_",
                    delete=False
                ) as temp_file:
                    temp_file_path = temp_file.name

                try:
                    await self.tts_client.synthesize(text, temp_file_path)
                except (TTSError, Exception) as e:
                    raise PipelineError(
                        f"TTS synthesis failed: {str(e)}"
                    ) from e

                # Step 2: Temp file → Voice Converter → Output
                try:
                    self.voice_converter.convert(temp_file_path, output_path)
                except (VoiceConversionError, Exception) as e:
                    raise PipelineError(
                        f"Voice conversion failed: {str(e)}"
                    ) from e

            else:
                # No voice conversion, TTS directly to output
                try:
                    await self.tts_client.synthesize(text, output_path)
                except (TTSError, Exception) as e:
                    raise PipelineError(
                        f"TTS synthesis failed: {str(e)}"
                    ) from e

        finally:
            # Cleanup: Remove temp file if it exists
            if temp_file_path and Path(temp_file_path).exists():
                try:
                    Path(temp_file_path).unlink()
                except Exception:
                    # Ignore cleanup errors
                    pass

    async def process_batch(
        self,
        texts: list[str],
        output_dir: str,
        prefix: str = "audio"
    ) -> list[str]:
        """
        Process multiple texts in batch.

        Args:
            texts: List of texts to convert
            output_dir: Directory to save audio files
            prefix: Prefix for output filenames

        Returns:
            List of output file paths

        Raises:
            PipelineError: If batch processing fails
        """
        output_paths = []
        output_path_obj = Path(output_dir)
        output_path_obj.mkdir(parents=True, exist_ok=True)

        for i, text in enumerate(texts):
            output_file = output_path_obj / f"{prefix}_{i:03d}.mp3"
            await self.process(text, str(output_file))
            output_paths.append(str(output_file))

        return output_paths

    def get_pipeline_info(self) -> dict:
        """
        Get information about pipeline configuration.

        Returns:
            Dictionary with pipeline settings
        """
        return {
            "tts_voice": self.tts_client.voice,
            "tts_rate": self.tts_client.rate,
            "tts_pitch": self.tts_client.pitch,
            "voice_conversion_enabled": self.voice_converter is not None,
            "converter_type": (
                type(self.voice_converter).__name__
                if self.voice_converter
                else None
            )
        }
