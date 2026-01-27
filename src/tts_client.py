"""Edge-TTS client for text-to-speech synthesis."""

import edge_tts
from pathlib import Path
from typing import Optional


class TTSError(Exception):
    """Raised when TTS operation fails."""
    pass


class EdgeTTSClient:
    """Client for Microsoft Edge Text-to-Speech."""

    # Default Vietnamese voices
    DEFAULT_VOICE = "vi-VN-HoaiMyNeural"  # Female voice

    # Common Vietnamese voices
    VIETNAMESE_VOICES = [
        "vi-VN-HoaiMyNeural",  # Female
        "vi-VN-NamMinhNeural",  # Male
    ]

    def __init__(
        self,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ):
        """
        Initialize Edge-TTS client.

        Args:
            voice: Voice name (e.g., "vi-VN-HoaiMyNeural")
            rate: Speech rate (e.g., "+10%" for faster, "-10%" for slower)
            pitch: Voice pitch (e.g., "+5Hz" for higher, "-5Hz" for lower)
        """
        self.voice = voice or self.DEFAULT_VOICE
        self.rate = rate
        self.pitch = pitch

    async def synthesize(self, text: str, output_path: str) -> None:
        """
        Synthesize speech from text and save to file.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file (MP3 format)

        Raises:
            TTSError: If synthesis fails or validation fails
        """
        # Validate inputs
        if not text or not text.strip():
            raise TTSError("Text cannot be empty")

        if not output_path:
            raise TTSError("Output path cannot be empty")

        try:
            # Create output directory if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Create communicate object with voice settings
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )

            # Save to file
            await communicate.save(output_path)

        except Exception as e:
            raise TTSError(f"Failed to synthesize speech: {str(e)}") from e

    @staticmethod
    def get_available_voices() -> list[str]:
        """
        Get list of available Vietnamese voices.

        Returns:
            List of voice names
        """
        # Return common Vietnamese voices
        # In production, could use edge_tts.list_voices() to get all voices
        return [
            "vi-VN-HoaiMyNeural",   # Female - gentle, warm
            "vi-VN-NamMinhNeural",  # Male - clear, natural
        ]

    def get_voice_info(self) -> dict:
        """
        Get information about current voice settings.

        Returns:
            Dictionary with voice configuration
        """
        return {
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "language": "Vietnamese" if self.voice.startswith("vi-") else "Other"
        }
