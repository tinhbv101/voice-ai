"""Quick WebSocket test."""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection."""
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print("✅ Connected to WebSocket!")

            # Receive welcome message
            welcome = await websocket.recv()
            print(f"📥 Received: {welcome}")

            # Send test message
            message = {
                "type": "text_input",
                "data": {"text": "Chào mày!"},
                "session_id": None
            }

            await websocket.send(json.dumps(message))
            print(f"📤 Sent: {message}")

            # Receive responses
            for i in range(10):  # Receive up to 10 chunks
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print(f"📥 Response {i+1}: {response}")
                except asyncio.TimeoutError:
                    print("⏱️  Timeout - no more messages")
                    break

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
