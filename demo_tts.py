#!/usr/bin/env python3
"""Quick demo script to test all TTS providers."""

import asyncio
import os
import sys
from pathlib import Path


async def test_edge_tts():
    """Test Edge-TTS (free)."""
    print("\n" + "="*60)
    print("Testing Edge-TTS (Free)")
    print("="*60)
    
    try:
        from src.tts_client import EdgeTTSClient
        
        client = EdgeTTSClient(voice="vi-VN-HoaiMyNeural")
        text = "Xin chào! Tôi là trợ lý AI của bạn."
        output = "demo_edge.mp3"
        
        print(f"Synthesizing: {text}")
        await client.synthesize(text, output)
        print(f"✅ Success! Audio saved to: {output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_openai_tts():
    """Test OpenAI TTS."""
    print("\n" + "="*60)
    print("Testing OpenAI TTS")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set, skipping...")
        print("   Set it with: export OPENAI_API_KEY=sk-xxx")
        return
    
    try:
        from src.openai_tts_client import OpenAI_TTSClient
        
        client = OpenAI_TTSClient(api_key=api_key, voice="nova")
        text = "Hello! I'm your AI assistant. Nice to meet you!"
        output = "demo_openai.mp3"
        
        print(f"Synthesizing: {text}")
        await client.synthesize(text, output)
        print(f"✅ Success! Audio saved to: {output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_elevenlabs_tts():
    """Test ElevenLabs TTS."""
    print("\n" + "="*60)
    print("Testing ElevenLabs TTS")
    print("="*60)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️  ELEVENLABS_API_KEY not set, skipping...")
        print("   Set it with: export ELEVENLABS_API_KEY=xxx")
        return
    
    try:
        from src.elevenlabs_tts_client import ElevenLabsTTSClient
        
        client = ElevenLabsTTSClient(api_key=api_key, voice="rachel")
        text = "Xin chào! Tôi là trợ lý AI của bạn. Rất vui được gặp bạn!"
        output = "demo_elevenlabs.mp3"
        
        print(f"Synthesizing: {text}")
        await client.synthesize(text, output)
        print(f"✅ Success! Audio saved to: {output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all TTS tests."""
    print("\n" + "="*60)
    print("🎤 TTS PROVIDER DEMO")
    print("="*60)
    print("\nThis script will test all available TTS providers:")
    print("1. Edge-TTS (free) - Always works")
    print("2. OpenAI TTS - Requires OPENAI_API_KEY")
    print("3. ElevenLabs - Requires ELEVENLABS_API_KEY")
    print("\nAudio files will be saved in current directory.")
    
    # Test all providers
    await test_edge_tts()
    await test_openai_tts()
    await test_elevenlabs_tts()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nGenerated files:")
    for file in ["demo_edge.mp3", "demo_openai.mp3", "demo_elevenlabs.mp3"]:
        if Path(file).exists():
            print(f"  - {file}")


if __name__ == "__main__":
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Run demo
    asyncio.run(main())
