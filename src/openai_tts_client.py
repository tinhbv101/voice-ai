"""OpenAI TTS client for high-quality speech synthesis."""

from openai import OpenAI
from pathlib import Path
from typing import Optional

class OpenAI_TTSClient:
    """Client for OpenAI Text-to-Speech API."""

    def __init__(self, api_key: str, voice: str = "nova", model: str = "tts-1"):
        """
        Initialize OpenAI TTS client.
        
        Voices: alloy, echo, fable, onyx, nova, shimmer
        Nova and Shimmer are best for 'waifu/anime' vibe.
        """
        self.client = OpenAI(api_key=api_key)
        self.voice = voice
        self.model = model

    async def synthesize(self, text: str, output_path: str) -> None:
        """Synthesize speech and save to file."""
        try:
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            # OpenAI's SDK provides a way to stream to file
            response.stream_to_file(output_path)
        except Exception as e:
            raise Exception(f"OpenAI TTS failed: {str(e)}")
