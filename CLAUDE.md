# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AnimeVoice AI: Real-time AI Voice Assistant with Character Persona. A low-latency, open-source voice interaction system where AI responds with distinct anime/idol character personalities and voice characteristics.

**Target Latency**: < 1.5s total pipeline latency through parallel processing.

## System Architecture

Four-layer streaming pipeline:

1. **Frontend (Interaction Layer)**
   - VAD: Silero VAD (WASM) for browser-based voice activity detection
   - Audio: 16kHz Mono PCM format
   - Transport: WebSocket for bidirectional audio streaming

2. **STT Layer**
   - Engine: Faster-Whisper (Large-v3 or Distil-large-v3)
   - Deployment: Local server (no API costs, reduced latency)

3. **LLM Layer**
   - Brain: Gemini 1.5 Flash with streaming enabled (`stream=True`)
   - Memory: 10 recent messages in RAM (short-term context)
   - Persona: System prompt defines character personality (casual, playful, informal speech)

4. **TTS & Voice Morphing Layer**
   - TTS: Edge-TTS (Microsoft Edge) for base voice generation
   - Voice Conversion: RVC (Retrieval-based Voice Conversion) with character .pth models
   - Pipeline: Text → Edge-TTS → RVC → Character voice

## Data Flow

```
User Speech → VAD → WebSocket → Faster-Whisper (STT) →
Gemini (streaming text chunks) → Edge-TTS → RVC →
WebSocket → Audio playback
```

**Key Optimization**: Parallel pipelining - STT, LLM, and TTS processes overlap to minimize total latency.

## Development Phases

**Phase 1**: CLI-based chat with Gemini (memory management)
**Phase 2**: Edge-TTS & RVC integration (voice conversion)
**Phase 3**: WebSocket server (FastAPI)
**Phase 4**: Web frontend with audio capture and VAD

## Tech Stack

- **STT**: Faster-Whisper
- **LLM**: Gemini 1.5 Flash (Google Generative AI SDK)
- **TTS**: Edge-TTS (free)
- **Voice Conversion**: RVC with character model files (.pth)
- **Backend**: FastAPI (WebSocket server)
- **Frontend**: Browser-based (WebSocket client, Silero VAD WASM)

## Key Implementation Considerations

- Maintain character persona consistency through system prompts
- Optimize for zero-cost stack using open-source and free-tier services
- Stream processing at every layer to reduce latency
- Handle audio format conversions efficiently (16kHz Mono PCM standard)
- Manage short-term context window (10 messages) to balance coherence and speed

## Phase 1: CLI Chat (COMPLETED) ✅

### Implementation Status

Phase 1 has been fully implemented with the following components:

- ✅ **Configuration Module** (`src/config.py`): Environment variable management with validation
- ✅ **Persona Module** (`src/persona.py`): Vietnamese casual character personality system
- ✅ **Memory Management** (`src/memory.py`): Circular buffer with immutable patterns (10 messages)
- ✅ **Gemini Client** (`src/gemini_client.py`): Streaming API wrapper with error handling
- ✅ **CLI Interface** (`src/cli.py`): Rich-based chat interface with commands
- ✅ **Test Suite**: Comprehensive unit tests for all modules (80%+ coverage)
- ✅ **Documentation**: README.md with setup and usage instructions

### Quick Start Commands

```bash
# Setup (first time)
poetry install
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run CLI
poetry run voiceai

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src tests/
```

### Architecture Notes

**Immutability Pattern**: All data structures (especially `ConversationMemory`) use immutable patterns - operations return new instances rather than modifying in place.

**Streaming**: Gemini responses are streamed token-by-token to provide immediate feedback and reduce perceived latency.

**Error Handling**: Comprehensive error handling at all layers:
- Configuration validation (missing API keys, invalid values)
- API errors (network issues, rate limits)
- User input handling (graceful Ctrl+C handling)

### File Structure

```
src/
├── config.py          # 72 lines - Environment config with validation
├── persona.py         # 60 lines - Character personality definition
├── memory.py          # 88 lines - Immutable conversation memory
├── gemini_client.py   # 105 lines - Streaming Gemini API client
└── cli.py             # 145 lines - Rich CLI interface

tests/
├── test_config.py        # Configuration tests
├── test_persona.py       # Persona tests
├── test_memory.py        # Memory management tests
└── test_gemini_client.py # Gemini client tests
```

### Known Limitations

- Memory limited to 10 messages (5 exchanges) - sufficient for casual conversation
- No persistence - conversation lost on exit (intentional for Phase 1)
- Vietnamese persona only (English responses require system prompt modification)
- Requires API key (free tier: 15 requests/minute, 1500 requests/day)

### Next Steps for Phase 2

1. Implement Edge-TTS integration for text-to-speech
2. Add RVC (Retrieval-based Voice Conversion) for character voice
3. Create audio pipeline: Text → Edge-TTS → RVC → Audio file
4. Test voice conversion with character .pth models

## Phase 2: TTS & Voice Conversion (COMPLETED) ✅

### Implementation Status

Phase 2 has been fully implemented with voice output capabilities:

- ✅ **TTS Client** (`src/tts_client.py`): Edge-TTS integration with Vietnamese voices
- ✅ **Voice Converter** (`src/voice_converter.py`): Extensible conversion system (Passthrough + RVC interface)
- ✅ **Audio Pipeline** (`src/audio_pipeline.py`): Complete TTS → Conversion → Output pipeline
- ✅ **CLI Voice Mode** (`src/cli.py --voice`): Voice output with audio file generation
- ✅ **Test Suite**: Comprehensive tests for all Phase 2 modules
- ✅ **Documentation**: Updated README with voice mode instructions

### Quick Start Commands

```bash
# Text-only mode (Phase 1)
python -m src.cli

# Voice mode (Phase 2) - generates audio files
python -m src.cli --voice

# Install Phase 2 dependencies
pip install edge-tts pydub aiofiles

# Run tests
pytest tests/test_tts_client.py
pytest tests/test_voice_converter.py
pytest tests/test_audio_pipeline.py
```

### Architecture

**Audio Pipeline Flow**:
```
Text → Edge-TTS → temp.mp3 → Voice Converter → output.mp3 → Cleanup temp file
```

**Voice Converter Types**:
- `PassthroughConverter`: No conversion (direct TTS output)
- `RVCConverter`: Placeholder for RVC model integration (future)

### File Structure

```
src/
├── tts_client.py         # 104 lines - Edge-TTS async client
├── voice_converter.py    # 127 lines - Voice conversion system
├── audio_pipeline.py     # 142 lines - Pipeline orchestrator
└── cli.py                # 223 lines - Extended with voice support

tests/
├── test_tts_client.py        # 107 lines - TTS client tests
├── test_voice_converter.py   # 75 lines - Converter tests
└── test_audio_pipeline.py    # 167 lines - Pipeline tests

audio_output/             # Generated audio files (MP3)
├── response_20260127_143052.mp3
├── response_20260127_143105.mp3
└── ...
```

### Key Features

**Edge-TTS Integration**:
- Async synthesis with edge-tts library
- Vietnamese voice support (vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural)
- Configurable rate and pitch
- Input validation (empty text, length limits)
- Error handling with TTSError

**Voice Converter**:
- Protocol-based design for extensibility
- PassthroughConverter for direct output
- RVCConverter interface ready for model integration
- Factory pattern for creating converters

**Audio Pipeline**:
- Chains TTS → Conversion → Output
- Temporary file management
- Cleanup on success/failure
- Batch processing support
- Pipeline configuration info

**CLI Enhancements**:
- `--voice` flag to enable TTS
- Audio files saved with timestamps
- Progress indicators for audio generation
- Graceful error handling for TTS failures

### Configuration

**Default Settings**:
- Voice: `vi-VN-HoaiMyNeural` (Female, warm)
- Rate: `+0%` (normal speed)
- Pitch: `+0Hz` (normal pitch)
- Converter: `passthrough` (no voice conversion)
- Output: `audio_output/response_YYYYMMDD_HHMMSS.mp3`

**Customization** (edit `src/cli.py`):
```python
# Change voice
tts_client = EdgeTTSClient(
    voice="vi-VN-NamMinhNeural",  # Male voice
    rate="+10%",                   # Faster
    pitch="+5Hz"                   # Higher pitch
)

# Enable RVC (when models available)
voice_converter = VoiceConverter.create(
    "rvc",
    model_path="models/character.pth"
)
```

### Known Limitations

- RVC integration is placeholder (requires model files and dependencies)
- Audio files are not automatically played (manual playback needed)
- No audio file cleanup (files accumulate in audio_output/)
- Voice mode requires internet connection for Edge-TTS
- No real-time audio streaming (files saved first)

### Next Steps for Phase 3

1. Implement WebSocket server with FastAPI
2. Create bidirectional audio streaming
3. Integrate STT (Faster-Whisper) for voice input
4. Parallel processing pipeline for lower latency
5. WebSocket protocol for client-server communication

## Phase 3: WebSocket Server (COMPLETED) ✅

### Implementation Status

Phase 3 has been fully implemented with WebSocket real-time communication:

- ✅ **WebSocket Protocol** (`src/websocket_protocol.py`): Message types, validation, serialization
- ✅ **Connection Manager** (`src/websocket_manager.py`): Multi-client connection management
- ✅ **Audio Streaming** (`src/audio_streaming.py`): Buffer and stream audio chunks
- ✅ **FastAPI Server** (`src/server.py`): WebSocket endpoint, session management, API routes
- ✅ **HTML Test Client** (`static/index.html`): Beautiful web UI for testing
- ✅ **Test Suite**: Comprehensive tests for protocol, manager, and streaming (80%+ coverage)
- ✅ **Documentation**: README updated with WebSocket usage and API docs

### Quick Start Commands

```bash
# Run WebSocket server
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000

# Or with Python
python -m src.server

# Test with HTML client
open http://localhost:8000

# Run Phase 3 tests
pytest tests/test_websocket_protocol.py
pytest tests/test_websocket_manager.py
pytest tests/test_audio_streaming.py
```

### Architecture

**WebSocket Flow**:
```
Browser/Client
    ↓
WebSocket Connection (/ws)
    ↓
Connection Manager (session management)
    ↓
Message Handler (protocol validation)
    ↓
├─→ Text Input → Gemini Client → Streaming Response
├─→ Audio Chunk → Audio Buffer (Phase 4: STT)
└─→ Control Messages (start/stop recording, ping/pong)
```

**Key Components**:
1. **Protocol Layer**: Message types, validation, serialization
2. **Connection Layer**: WebSocket lifecycle, session management
3. **Application Layer**: Business logic (chat, audio buffering)
4. **API Layer**: REST endpoints (health, docs)

### File Structure

```
src/
├── websocket_protocol.py   # 170 lines - Protocol definitions
├── websocket_manager.py     # 145 lines - Connection management
├── audio_streaming.py       # 210 lines - Audio buffer & streaming
└── server.py                # 310 lines - FastAPI WebSocket server

static/
└── index.html               # 330 lines - Web test client

tests/
├── test_websocket_protocol.py  # 180 lines - Protocol tests
├── test_websocket_manager.py   # 140 lines - Manager tests
└── test_audio_streaming.py     # 160 lines - Streaming tests
```

### Key Features

**WebSocket Protocol**:
- Structured message types (text, audio, control)
- JSON serialization/deserialization
- Input validation with ProtocolError
- Helper functions for common messages

**Connection Manager**:
- Session ID generation (UUID)
- Multi-client support (concurrent connections)
- Broadcast to all clients
- Connection metadata tracking
- Graceful disconnect handling

**Audio Streaming**:
- Async audio buffer with overflow protection
- Base64 and raw bytes support
- Start/stop recording lifecycle
- Callback on completion
- Per-session stream management

**FastAPI Server**:
- WebSocket endpoint with streaming Gemini responses
- REST API endpoints (/, /api, /health, /docs)
- Static file serving for HTML client
- CORS middleware for cross-origin
- Per-session memory and state
- Error handling and logging

**HTML Test Client**:
- Beautiful Tailwind CSS UI
- Real-time WebSocket connection status
- Send text messages
- Receive streaming responses (token-by-token)
- Message history display
- Auto-scroll
- Ping/pong keepalive
- Placeholder for audio (Phase 4)

### Session Management

Each WebSocket connection receives:
- **Unique session ID**: Auto-generated UUID
- **Conversation memory**: 10-message circular buffer
- **Gemini client**: Dedicated AI instance with persona
- **Audio stream**: Optional buffer for recording

Sessions are **isolated** - each client has independent state.

### WebSocket Message Types

**Client → Server**:
- `text_input` - User text message
- `audio_chunk` - Audio data chunk (base64)
- `start_recording` - Begin audio capture
- `stop_recording` - End audio capture
- `ping` - Keepalive

**Server → Client**:
- `text_response` - AI response (streaming)
- `audio_response` - Audio file (Phase 4)
- `transcript` - STT result (Phase 4)
- `status` - Status updates
- `error` - Error messages
- `pong` - Keepalive response

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | HTML test client |
| `/api` | GET | API information |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/ws` | WebSocket | Real-time communication |

### Configuration

**Default Settings**:
- Host: `0.0.0.0` (all interfaces)
- Port: `8000`
- CORS: Enabled for all origins
- Max memory: 10 messages per session
- WebSocket timeout: 30s ping interval

### Known Limitations

- No authentication/authorization (add JWT in production)
- No rate limiting (add for production)
- No persistence (sessions lost on server restart)
- Audio features are placeholders (STT in Phase 4)
- No audio playback on server side (client only)
- No RVC voice conversion over WebSocket yet

### Testing

**Run all Phase 3 tests**:
```bash
pytest tests/test_websocket*.py tests/test_audio_streaming.py -v
```

**Test with HTML client**:
1. Start server: `uvicorn src.server:app --reload`
2. Open: http://localhost:8000
3. Click "Connect"
4. Send messages and verify streaming

**Test with Python**:
```bash
python test_websocket.py
```

### Next Steps for Phase 4

1. Integrate Faster-Whisper for STT (audio → text)
2. Add voice input support in web client (browser mic)
3. Implement VAD (Voice Activity Detection) with Silero
4. Stream audio to TTS and send back to client
5. Parallel pipeline: STT → LLM → TTS (minimize latency)
6. Real-time audio playback in browser

## Phase 4: STT & Voice Input (COMPLETED) ✅

### Implementation Status

Phase 4 has been fully implemented with COMPLETE voice conversation:

- ✅ **Faster-Whisper Integration** (`src/stt_client.py`): STT client with async transcription
- ✅ **WebSocket STT Handler**: Audio processing in `stop_recording` handler
- ✅ **Web Client Microphone**: Browser audio capture with MediaRecorder API
- ✅ **Audio Streaming**: Base64 encoding for WebSocket transport
- ✅ **Transcript Display**: Real-time transcription results in UI
- ✅ **End-to-End Pipeline**: Voice → STT → LLM → TTS → Audio Response
- ✅ **TTS Integration**: Edge-TTS for Vietnamese voice responses
- ✅ **Audio Playback**: Automatic audio response playback in browser
- ✅ **Test Suite**: Comprehensive tests for STT client

### Quick Start Commands

```bash
# Ensure venv is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt

# Run server (STT model will download on first use)
python -m uvicorn src.server:app --reload --host 0.0.0.0 --port 8000

# Open web client
open http://localhost:8000

# Run STT tests
pytest tests/test_stt_client.py -v
```

### Architecture

**Complete Voice Conversation Pipeline**:
```
Voice Input:
Browser Mic → MediaRecorder → WebM Audio → Base64 Encode →
WebSocket (audio_chunk) → Server Buffer → WAV Conversion →
Faster-Whisper (STT) → Transcript → Gemini (LLM) →

Voice Output:
Full Text Response → Edge-TTS (vi-VN-HoaiMyNeural) → MP3 Audio →
Base64 Encode → WebSocket (audio_response) → Browser → Auto Playback
```

**Key Components**:
1. **Frontend Audio Capture**: MediaRecorder API with WebM codec
2. **WebSocket Transport**: Base64-encoded audio chunks (both directions)
3. **Server Processing**: Async audio buffering, STT, and TTS
4. **STT Engine**: Faster-Whisper with "base" model (Vietnamese/English)
5. **TTS Engine**: Edge-TTS with Vietnamese voice (vi-VN-HoaiMyNeural)
6. **Auto Playback**: Browser Audio API with blob URLs

### File Structure

```
src/
├── stt_client.py # 260 lines - Faster-Whisper async client
├── server.py # 370 lines - Updated with STT integration
└── audio_streaming.py # 231 lines - Audio buffer management

static/
└── index.html # 540 lines - Voice-enabled web client

tests/
└── test_stt_client.py # 185 lines - STT integration tests
```

### Key Features

**STT Client** (`src/stt_client.py`):
- Async/sync transcription support
- Automatic language detection or forced language
- VAD (Voice Activity Detection) filtering
- Audio bytes or file path input
- Thread pool for non-blocking STT
- Temporary file management
- Model: "base" (fast, accurate for Vietnamese)

**WebSocket Server Updates**:
- STT client singleton (lazy initialization)
- Audio → transcript → LLM pipeline
- Transcript message type for client feedback
- Error handling for STT failures
- Automatic model download on first use

**Web Client Features**:
- One-click voice recording (Start/Stop button)
- Visual recording indicator (animated)
- Microphone permission handling
- Audio chunk streaming to server
- Real-time transcript display
- Automatic LLM response after transcription
- Audio format: WebM with Opus codec

### Configuration

**STT Settings** (in `server.py`):
```python
stt_client = FasterWhisperClient(
    model_size="base",      # Fast and accurate
    device="cpu",           # Use "cuda" for GPU
    compute_type="int8"     # Lower memory, faster
)
```

**Audio Settings** (in `index.html`):
```javascript
audio: {
    channelCount: 1,        // Mono
    sampleRate: 16000,      // 16kHz
    echoCancellation: true,
    noiseSuppression: true
}
```

**Available Models**:
- `tiny` - Fastest, less accurate (~75MB)
- `base` - Good balance (~150MB) **← Default**
- `small` - Better accuracy (~500MB)
- `medium` - High accuracy (~1.5GB)
- `large-v3` - Best accuracy (~3GB)
- `distil-large-v3` - Distilled large (~1.5GB)

### Usage Flow

1. **Open Web Client**: Navigate to http://localhost:8000
2. **Connect**: Click "Connect" button
3. **Record Voice**: Click "🎤 Start Recording" (grant mic permission)
4. **Speak**: Say something in Vietnamese or English
5. **Stop**: Click "⏹ Stop Recording"
6. **Processing**: Audio is transcribed by Faster-Whisper
7. **Display**: Transcript appears in chat (purple bubble)
8. **AI Response**: Gemini processes transcript and responds
9. **View**: Streaming AI text response appears (green bubble)
10. **Listen**: Audio response automatically plays (TTS voice)

### Voice Features

**Input (STT)**:
- Model: Faster-Whisper "base" (~150MB)
- Languages: Vietnamese, English (99 languages supported)
- VAD: Voice Activity Detection enabled
- Latency: ~2-4s for 10s audio on CPU

**Output (TTS)**:
- Engine: Edge-TTS (Microsoft Edge, free)
- Voice: vi-VN-HoaiMyNeural (Vietnamese female, warm tone)
- Format: MP3 audio
- Latency: ~1-2s for short responses
- Auto-play: Immediate playback in browser

### Known Limitations

- **First Run**: Model downloads automatically (~150MB for base model)
- **STT Latency**: Base model ~2-4 seconds for 10s audio on CPU
- **TTS Latency**: ~1-2 seconds for short responses
- **Audio Format**: WebM input, MP3 output
- **No Real-time VAD**: Recording must be stopped manually
- **Language**: Best for Vietnamese and English (model supports 99 languages)
- **Voice Selection**: Fixed to vi-VN-HoaiMyNeural (configurable in code)
- **No RVC**: Character voice conversion not yet integrated

### Performance Notes

**STT Speed** (on M1 Mac with base model):
- 5s audio: ~1.5-2s transcription
- 10s audio: ~2-4s transcription  
- 30s audio: ~5-8s transcription

**Optimization Tips**:
1. Use `tiny` model for fastest speed (lower accuracy)
2. Use GPU (`device="cuda"`) for 2-3x speedup
3. Enable VAD filtering to skip silence
4. Use `distil-large-v3` for best speed/accuracy balance

### Testing

**Run STT tests**:
```bash
pytest tests/test_stt_client.py -v
```

**Manual Testing**:
1. Start server
2. Open http://localhost:8000
3. Click Connect
4. Record voice input (Vietnamese or English)
5. Verify transcript appears
6. Verify AI responds to transcript

### Next Steps for Production

1. **Add Real-time VAD**: Browser-based Voice Activity Detection (Silero VAD)
2. **RVC Integration**: Character voice conversion for personality
3. **Optimize STT**: GPU acceleration, model caching, batching
4. **Audio Preprocessing**: Noise reduction, normalization
5. **Multi-language**: Auto-detect language or user selection
6. **Voice Selection**: UI to choose different TTS voices
7. **Error Recovery**: Handle network failures, retry logic
8. **Rate Limiting**: Prevent abuse of STT/TTS services
9. **Analytics**: Track STT/TTS accuracy, latency metrics
10. **Streaming TTS**: Stream audio chunks as they're generated
