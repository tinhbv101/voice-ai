"""Speech-to-Text client using Faster-Whisper."""

import logging
from typing import Optional, Union
from pathlib import Path
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class STTError(Exception):
    """Raised when STT processing encounters an error."""
    pass


class FasterWhisperClient:
    """
    Faster-Whisper STT client for audio transcription.
    
    Uses CTranslate2 optimized inference for fast transcription.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        num_workers: int = 1
    ):
        """
        Initialize Faster-Whisper client.

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3, distil-large-v3)
            device: Device to use (cpu, cuda)
            compute_type: Computation type (int8, float16, float32)
            num_workers: Number of parallel workers for inference
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        logger.info(
            f"Initializing Faster-Whisper: model={model_size}, "
            f"device={device}, compute_type={compute_type}"
        )
        
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=num_workers
            )
            logger.info("Faster-Whisper model loaded successfully")
        except Exception as e:
            raise STTError(f"Failed to load Whisper model: {str(e)}") from e

        # Thread pool for running sync operations async
        self.executor = ThreadPoolExecutor(max_workers=2)

    def transcribe_sync(
        self,
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        task: str = "transcribe",
        vad_filter: bool = True,
        beam_size: int = 5
    ) -> dict:
        """
        Transcribe audio file synchronously.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "vi", "en"). Auto-detect if None
            task: Task type ("transcribe" or "translate")
            vad_filter: Enable Voice Activity Detection filter
            beam_size: Beam size for decoding

        Returns:
            Dictionary with transcription results:
            {
                "text": str,
                "segments": list,
                "language": str,
                "duration": float
            }

        Raises:
            STTError: If transcription fails
        """
        try:
            audio_path = str(audio_path)
            logger.info(f"Transcribing audio: {audio_path}")

            # Transcribe
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                vad_filter=vad_filter,
                beam_size=beam_size
            )

            # Collect segments
            segments_list = []
            full_text = []

            for segment in segments:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                segments_list.append(segment_data)
                full_text.append(segment.text.strip())

            result = {
                "text": " ".join(full_text),
                "segments": segments_list,
                "language": info.language,
                "duration": info.duration
            }

            logger.info(
                f"Transcription complete: language={info.language}, "
                f"duration={info.duration:.2f}s, text_length={len(result['text'])}"
            )

            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise STTError(f"Transcription failed: {str(e)}") from e

    async def transcribe(
        self,
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        task: str = "transcribe",
        vad_filter: bool = True,
        beam_size: int = 5
    ) -> dict:
        """
        Transcribe audio file asynchronously.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "vi", "en"). Auto-detect if None
            task: Task type ("transcribe" or "translate")
            vad_filter: Enable Voice Activity Detection filter
            beam_size: Beam size for decoding

        Returns:
            Dictionary with transcription results

        Raises:
            STTError: If transcription fails
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.transcribe_sync,
            audio_path,
            language,
            task,
            vad_filter,
            beam_size
        )

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        task: str = "transcribe",
        vad_filter: bool = True,
        beam_size: int = 5
    ) -> dict:
        """
        Transcribe audio from bytes asynchronously.

        Args:
            audio_bytes: Audio data as bytes
            language: Language code (e.g., "vi", "en"). Auto-detect if None
            task: Task type ("transcribe" or "translate")
            vad_filter: Enable Voice Activity Detection filter
            beam_size: Beam size for decoding

        Returns:
            Dictionary with transcription results

        Raises:
            STTError: If transcription fails
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            result = await self.transcribe(
                tmp_path,
                language=language,
                task=task,
                vad_filter=vad_filter,
                beam_size=beam_size
            )
            return result
        finally:
            # Cleanup temporary file
            try:
                Path(tmp_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_path}: {e}")

    def close(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)
        logger.info("Faster-Whisper client closed")
