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
            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            # OpenAI's SDK provides a way to stream to file
            response.stream_to_file(output_path)
        except Exception as e:
            raise Exception(f"OpenAI TTS failed: {str(e)}")

    def get_voice_info(self) -> dict:
        """
        Get information about current voice settings.
        
        Returns:
            Dictionary with voice configuration
        """
        return {
            "voice": self.voice,
            "model": self.model,
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    
    async def test():
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Please set OPENAI_API_KEY environment variable")
            return
        
        # Create client
        client = OpenAI_TTSClient(
            api_key=api_key,
            voice="nova",  # Warm female voice for anime vibe
            model="tts-1"
        )
        
        # Test text (OpenAI doesn't support Vietnamese, but English is very natural)
        text = "Hello! I'm your AI assistant. Nice to meet you!"
        output_path = "test_openai.mp3"
        
        print(f"Synthesizing: {text}")
        await client.synthesize(text, output_path)
        print(f"Audio saved to: {output_path}")
    
    asyncio.run(test())
