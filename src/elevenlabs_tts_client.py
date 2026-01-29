"""ElevenLabs TTS client for high-quality, natural speech synthesis."""

from elevenlabs import ElevenLabs
from pathlib import Path
from typing import Optional


class ElevenLabsTTSClient:
    """Client for ElevenLabs Text-to-Speech API."""

    # Popular voices for different use cases
    VOICE_PRESETS = {
        # Female voices - good for waifu/anime vibe
        "rachel": "21m00Tcm4TlvDq8ikWAM",  # Calm, natural female
        "domi": "AZnzlk1XvdvUeBnXmlld",    # Strong, confident female
        "bella": "EXAVITQu4vr4xnSDxMaL",   # Soft, gentle female
        "elli": "MF3mGyEYCl7XYWbV9V6O",    # Young, energetic female
        
        # Male voices
        "adam": "pNInz6obpgDQGcFmaJgB",    # Deep, resonant male
        "antoni": "ErXwobaYiN019PkySvjV",  # Warm, friendly male
        
        # Multilingual (great for Vietnamese)
        "sarah": "EXAVITQu4vr4xnSDxMaL",   # Multilingual female
    }

    def __init__(
        self, 
        api_key: str, 
        voice: str = "rachel",
        model: str = "eleven_multilingual_v2"
    ):
        """
        Initialize ElevenLabs TTS client.
        
        Args:
            api_key: ElevenLabs API key
            voice: Voice ID or preset name (default: "rachel")
            model: Model ID (default: "eleven_multilingual_v2")
                   - "eleven_monolingual_v1": English only, fastest
                   - "eleven_multilingual_v1": 25+ languages
                   - "eleven_multilingual_v2": Latest, best quality (recommended)
                   - "eleven_turbo_v2": Fastest, good quality
        """
        self.client = ElevenLabs(api_key=api_key)
        
        # Resolve voice ID from preset or use directly
        if voice in self.VOICE_PRESETS:
            self.voice_id = self.VOICE_PRESETS[voice]
        else:
            self.voice_id = voice
            
        self.model = model

    async def synthesize(
        self, 
        text: str, 
        output_path: str, 
        optimize_latency: int = 3,
        previous_text: Optional[str] = None,
        next_text: Optional[str] = None,
        language_code: Optional[str] = "vi"
    ) -> None:
        """
        Synthesize speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file (MP3 format)
            optimize_latency: Latency optimization level (0-4)
                0 - default mode (no optimizations)
                1 - normal optimizations (~50% improvement)
                2 - strong optimizations (~75% improvement)
                3 - max optimizations (default)
                4 - max + text normalizer off (best latency)
            previous_text: Text that came before (for continuity)
            next_text: Text that comes after (for continuity)
            language_code: Language code (ISO 639-1) for better pronunciation (default: "vi" for Vietnamese)
        
        Raises:
            Exception: If synthesis fails
        """
        try:
            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Build request parameters
            kwargs = {
                "voice_id": self.voice_id,
                "text": text,
                "model_id": self.model,
                "output_format": "mp3_44100_128",
            }
            
            # Add language_code for better pronunciation (works with all models)
            if language_code:
                kwargs["language_code"] = language_code
            
            # eleven_v3 doesn't support optimize_streaming_latency, previous_text, next_text
            # Only add these for older models
            if not self.model.startswith("eleven_v3"):
                if optimize_latency > 0:
                    kwargs["optimize_streaming_latency"] = optimize_latency
                if previous_text:
                    kwargs["previous_text"] = previous_text
                if next_text:
                    kwargs["next_text"] = next_text
            
            # Use standard text-to-speech API
            audio_stream = self.client.text_to_speech.convert(**kwargs)
            
            # Write audio chunks to file
            with open(output_path, "wb") as f:
                for chunk in audio_stream:
                    f.write(chunk)
                    
        except Exception as e:
            raise Exception(f"ElevenLabs TTS failed: {str(e)}")

    def get_available_voices(self) -> list:
        """
        Get list of available voices from your account.
        
        Returns:
            List of voice objects with id, name, category
        """
        try:
            voices = self.client.voices.get_all()
            return voices.voices
        except Exception as e:
            raise Exception(f"Failed to get voices: {str(e)}")

    def get_voice_info(self) -> dict:
        """
        Get information about current voice settings.
        
        Returns:
            Dictionary with voice configuration
        """
        return {
            "voice_id": self.voice_id,
            "model": self.model,
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    
    async def test():
        # Get API key from environment
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("Please set ELEVENLABS_API_KEY environment variable")
            return
        
        # Create client with Rachel voice (good for anime vibe)
        client = ElevenLabsTTSClient(
            api_key=api_key,
            voice="rachel",  # or use direct voice ID
            model="eleven_multilingual_v2"
        )
        
        # Test Vietnamese text
        text = "Xin chào! Tôi là trợ lý AI của bạn. Rất vui được gặp bạn!"
        output_path = "test_elevenlabs.mp3"
        
        print(f"Synthesizing: {text}")
        await client.synthesize(text, output_path)
        print(f"Audio saved to: {output_path}")
    
    asyncio.run(test())
