# AnimeVoice AI - Phase 3: WebSocket Server

Real-time AI Voice Assistant with Character Persona. A complete voice interaction system with WebSocket server, text chat, text-to-speech, and character voice conversion capabilities.

## Features

### Phase 1: Text Chat ✅
✨ **Streaming Responses** - Real-time token-by-token display for low-latency feel
🧠 **Conversation Memory** - Maintains context with 10-message circular buffer
🎭 **Character Persona** - Casual Vietnamese personality with playful, friendly tone
🎨 **Rich CLI** - Colorful, formatted output using Rich library
⚡ **Fast & Free** - Uses Gemini 1.5 Flash (free tier available)

### Phase 2: Voice Output ✅
🎵 **Text-to-Speech** - Edge-TTS integration for natural Vietnamese voice
🔊 **Voice Conversion** - Extensible pipeline for character voice transformation
📁 **Audio Files** - Saves responses as MP3 files with timestamps
⚙️ **Configurable** - Support for multiple voices, rate, and pitch adjustment

### Phase 3: WebSocket Server ✅
🌐 **Real-time Communication** - WebSocket server with FastAPI
🔌 **Multiple Clients** - Support for concurrent connections
📨 **Message Protocol** - Structured message types (text, audio, status, error)
💾 **Session Management** - Per-session memory and state
🎙️ **Audio Streaming** - Buffer and process audio chunks (ready for Phase 4)
📊 **Health Monitoring** - Health check and status endpoints

## Prerequisites

- Python 3.10 or higher
- Poetry (recommended) or pip
- Google API Key for Gemini

## Installation

### Method 1: Using Poetry (Recommended)

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

### Method 2: Using pip

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or manually:
   ```bash
   pip install google-generativeai python-dotenv rich edge-tts pydub aiofiles pytest pytest-asyncio
   ```

## Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Add your Google API key** to `.env`:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Get API key** from: https://makersuite.google.com/app/apikey

## Usage

### Running the Chat

**Text-only mode** (default):

```bash
# With Poetry
poetry run voiceai

# With pip (in virtual environment)
python -m src.cli
```

**Voice mode** (with TTS output):

```bash
# With Poetry
poetry run voiceai --voice

# With pip
python -m src.cli --voice
```

Voice mode will:
- Generate audio files for AI responses
- Save them in `audio_output/` directory
- Use Vietnamese TTS voice (vi-VN-HoaiMyNeural)

**WebSocket Server** (Phase 3):

```bash
# Run WebSocket server
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000

# Or with Python
python -m src.server
```

Server will run at:
- **Web Client**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Commands

- `/clear` - Clear conversation history
- `/exit` or `/quit` - Exit the program
- `Ctrl+C` - Graceful exit

### Example Session

```
🎭 VoiceAI - Phase 1: CLI Chat with Gemini

Chào mày! Tao là AI assistant của mày đây 😄
Cứ thoải mái nói chuyện với tao nhé!

Bạn > Chào mày!
🤖 Ủa chào mày! Có chuyện gì vui không? 😄

Bạn > Giải thích cho tao về AI được không?
🤖 Okay để tao giải thích cho! AI là trí tuệ nhân tạo...
```

## Testing

Run tests with pytest:

**With Poetry**:
```bash
poetry run pytest
```

**With pip**:
```bash
pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=src tests/
```

## Project Structure

```
voiceai/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Environment variables and configuration
│   ├── persona.py          # Character persona and system prompts
│   ├── memory.py           # Conversation memory management
│   ├── gemini_client.py    # Gemini API wrapper with streaming
│   ├── tts_client.py       # Edge-TTS client (Phase 2)
│   ├── voice_converter.py  # Voice conversion module (Phase 2)
│   ├── audio_pipeline.py   # Audio processing pipeline (Phase 2)
│   └── cli.py              # Main CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_persona.py
│   ├── test_memory.py
│   └── test_gemini_client.py
├── .env.example            # Environment template
├── .gitignore
├── pyproject.toml          # Poetry dependencies
├── README.md
└── CLAUDE.md
```

## Configuration Options

Environment variables (optional, with defaults):

```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional (defaults shown)
MODEL_NAME=gemini-1.5-flash
MAX_MEMORY_MESSAGES=10
TEMPERATURE=0.7
```

## Architecture

### Streaming Pipeline

```
User Input → Gemini API (streaming) → Token-by-token display → Memory
```

### Memory Management

- **Circular Buffer**: Maintains last 10 messages (5 exchanges)
- **Immutable Pattern**: All operations return new instances
- **Gemini Format**: Messages formatted for API compatibility

### Character Persona

- **Language**: Casual Vietnamese with mày-tao pronouns
- **Personality**: Playful, friendly, teasing but kind
- **Style**: Conversational, expressive, uses slang

## Phase 2: Voice Output

### Audio Pipeline

```
Text Response → Edge-TTS → Base Audio → Voice Converter → Character Audio (MP3)
```

**Components**:
1. **TTS Client** (`src/tts_client.py`): Edge-TTS integration for Vietnamese text-to-speech
2. **Voice Converter** (`src/voice_converter.py`): Extensible voice conversion system
   - `PassthroughConverter`: Direct audio output (no conversion)
   - `RVCConverter`: Placeholder for RVC model integration (future)
3. **Audio Pipeline** (`src/audio_pipeline.py`): Orchestrates TTS → Conversion → Output

### Voice Configuration

Current default voice: `vi-VN-HoaiMyNeural` (Female, warm, natural)

Available Vietnamese voices:
- `vi-VN-HoaiMyNeural` - Female, gentle and warm
- `vi-VN-NamMinhNeural` - Male, clear and natural

To use a different voice, modify `src/cli.py`:
```python
tts_client = EdgeTTSClient(voice="vi-VN-NamMinhNeural")
```

### Audio Output

- **Location**: `audio_output/` directory (created automatically)
- **Format**: MP3
- **Naming**: `response_YYYYMMDD_HHMMSS.mp3`
- **Example**: `response_20260127_143052.mp3`

### Future: RVC Integration

RVC (Retrieval-based Voice Conversion) integration is planned for character-specific voices:
- Place `.pth` model files in `models/` directory
- Update voice converter configuration to use RVC
- Convert base TTS voice to anime/idol character voice

## Phase 3: WebSocket Server

### Server Architecture

**FastAPI WebSocket Server** with real-time bidirectional communication:

```
Client (Browser/App) ←→ WebSocket ←→ Server ←→ Gemini API
                                    ↓
                              Session Manager
                              Memory & State
```

### WebSocket Protocol

**Message Format:**
```json
{
  "type": "message_type",
  "data": {...},
  "session_id": "uuid",
  "timestamp": 1234567890.123
}
```

**Message Types:**

**Client → Server:**
- `text_input` - Send text message
- `audio_chunk` - Send audio data chunk
- `start_recording` - Start audio recording
- `stop_recording` - Stop audio recording
- `ping` - Keepalive ping

**Server → Client:**
- `text_response` - AI text response (streaming)
- `audio_response` - AI audio response (Phase 4)
- `transcript` - STT transcript (Phase 4)
- `status` - Status update
- `error` - Error message
- `pong` - Keepalive pong

### Example WebSocket Messages

**Send text input:**
```json
{
  "type": "text_input",
  "data": {"text": "Chào mày!"},
  "session_id": null
}
```

**Receive text response (streaming):**
```json
{
  "type": "text_response",
  "data": {"text": "Ủa "},
  "session_id": "abc-123"
}
```

**Receive status:**
```json
{
  "type": "status",
  "data": {"status": "Connected to VoiceAI server"},
  "session_id": "abc-123"
}
```

### API Endpoints

- `GET /` - Web client UI
- `GET /api` - API information
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)
- `WS /ws` - WebSocket endpoint

### Testing WebSocket

**Using HTML Client:**
1. Open http://localhost:8000
2. Click "Connect"
3. Send messages in the chat interface

**Using Python:**
```python
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # Receive welcome
        print(await ws.recv())

        # Send text
        await ws.send(json.dumps({
            "type": "text_input",
            "data": {"text": "Hello!"}
        }))

        # Receive response
        while True:
            print(await ws.recv())

asyncio.run(test())
```

**Using wscat (Node.js):**
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

### Session Management

Each WebSocket connection gets:
- **Unique session ID** - UUID generated on connect
- **Conversation memory** - 10 message buffer per session
- **Gemini client** - Dedicated AI client instance
- **Audio stream** - Optional audio buffer for recording

Sessions are isolated - each client has independent state.

### Features Implemented

✅ **Real-time Text Chat** - Streaming responses
✅ **Connection Management** - Multiple concurrent clients
✅ **Session Isolation** - Independent memory per client
✅ **Message Validation** - Protocol error handling
✅ **Audio Buffering** - Ready for STT integration (Phase 4)
✅ **Health Monitoring** - Status and metrics endpoints
✅ **CORS Support** - Cross-origin requests enabled

## Troubleshooting

### API Key Error

```
❌ Lỗi cấu hình: GOOGLE_API_KEY environment variable is required
```

**Solution**: Add your API key to `.env` file

### Poetry Not Found

```
command not found: poetry
```

**Solution**: Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or use pip installation method instead.

### Import Errors

**Solution**: Make sure you're in the virtual environment:
```bash
# With Poetry
poetry shell

# With pip
source venv/bin/activate
```

## Development

### Code Style

- **Immutability**: All data structures use immutable patterns
- **Small Files**: Each module < 400 lines
- **Error Handling**: Comprehensive try-catch blocks
- **Type Hints**: Full type annotations

### Adding Features

1. Write tests first (TDD approach)
2. Implement minimal code to pass tests
3. Refactor for clarity
4. Verify 80%+ test coverage

## Next Phases

- **Phase 2**: Edge-TTS & RVC integration (voice conversion)
- **Phase 3**: WebSocket server (FastAPI)
- **Phase 4**: Web frontend with audio capture and VAD

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please follow:
1. TDD approach (tests first)
2. Immutable patterns
3. Comprehensive error handling
4. Vietnamese comments/docs welcome

## Support

For issues or questions:
- Open an issue on GitHub
- Check troubleshooting section above
- Review CLAUDE.md for technical details
