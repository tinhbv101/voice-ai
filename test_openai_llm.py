"""Quick test for OpenAI LLM client."""

import asyncio
import os
from dotenv import load_dotenv
from src.openai_llm_client import OpenAILLMClient

async def test_openai_streaming():
    """Test OpenAI streaming with Vietnamese."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
    
    print("🚀 Testing OpenAI LLM streaming...")
    
    # Create client
    client = OpenAILLMClient(
        api_key=api_key,
        model_name="gpt-4o-mini",
        system_instruction="Bạn là một trợ lý AI thân thiện, nói tiếng Việt tự nhiên và vui vẻ.",
        temperature=0.7
    )
    
    # Test message
    message = "Xin chào! Bạn là ai?"
    print(f"\n👤 User: {message}\n🤖 Assistant: ", end="", flush=True)
    
    # Stream response
    full_response = ""
    for chunk in client.chat_stream(message, []):
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print("\n\n✅ Streaming completed!")
    print(f"📊 Total length: {len(full_response)} characters")
    
    # Test with history
    print("\n" + "="*50)
    history = [
        {"role": "user", "content": message},
        {"role": "assistant", "content": full_response}
    ]
    
    message2 = "Kể cho tôi một câu chuyện ngắn vui"
    print(f"\n👤 User: {message2}\n🤖 Assistant: ", end="", flush=True)
    
    full_response2 = ""
    for chunk in client.chat_stream(message2, history):
        print(chunk, end="", flush=True)
        full_response2 += chunk
    
    print("\n\n✅ Second message completed!")
    print(f"📊 Total length: {len(full_response2)} characters")

if __name__ == "__main__":
    asyncio.run(test_openai_streaming())
