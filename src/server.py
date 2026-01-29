"""FastAPI WebSocket server for real-time voice AI assistant."""

import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import Config
from src.websocket_manager import ConnectionManager
from src.websocket_protocol import (
    WebSocketMessage,
    MessageType,
    MessageValidator,
    ProtocolError,
    create_text_response,
    create_error_message,
    create_status_message,
    create_transcript_message,
    create_audio_response_message
)
from src.audio_streaming import AudioStreamManager
from src.gemini_client import GeminiClient, GeminiError
from src.openai_llm_client import OpenAILLMClient, OpenAIError
from src.memory import ConversationMemory
from src.persona import get_system_instruction
from src.stt_client import FasterWhisperClient, STTError
from src.tts_client import EdgeTTSClient, TTSError
from src.elevenlabs_tts_client import ElevenLabsTTSClient
from src.openai_tts_client import OpenAI_TTSClient
from src.audio_pipeline import AudioPipeline
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VoiceAI WebSocket Server",
    description="Real-time AI Voice Assistant with WebSocket support",
    version="0.4.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize managers
connection_manager = ConnectionManager()
audio_stream_manager = AudioStreamManager()

# Initialize STT client (singleton)
stt_client: Optional[FasterWhisperClient] = None

def get_stt_client() -> FasterWhisperClient:
    """Get or create STT client."""
    global stt_client
    if stt_client is None:
        logger.info("Initializing STT client...")
        stt_client = FasterWhisperClient(
            model_size="tiny",  # Fastest model for Hackathon
            device="cpu",
            compute_type="int8"
        )
    return stt_client

# Initialize TTS client (singleton)
tts_client = None
tts_fallback_client = None  # Fallback to Edge-TTS

def get_tts_client():
    """Get or create TTS client based on config."""
    global tts_client
    if tts_client is None:
        logger.info("Initializing TTS client...")
        config = Config()
        
        if config.tts_provider == "elevenlabs":
            logger.info("Using ElevenLabs TTS")
            tts_client = ElevenLabsTTSClient(
                api_key=config.elevenlabs_api_key,
                voice=config.elevenlabs_voice,
                model=config.elevenlabs_model
            )
        elif config.tts_provider == "openai":
            logger.info("Using OpenAI TTS")
            tts_client = OpenAI_TTSClient(
                api_key=config.openai_api_key,
                voice=config.openai_voice,
                model=config.openai_model
            )
        else:  # edge (default)
            logger.info("Using Edge TTS")
            tts_client = EdgeTTSClient(
                voice="vi-VN-HoaiMyNeural",
                rate="+20%",
                pitch="+25Hz"
            )
    return tts_client

def get_fallback_tts_client():
    """Get fallback TTS client (always Edge-TTS)."""
    global tts_fallback_client
    if tts_fallback_client is None:
        logger.info("Initializing fallback TTS client (Edge-TTS)...")
        tts_fallback_client = EdgeTTSClient(
            voice="vi-VN-HoaiMyNeural",
            rate="+20%",
            pitch="+25Hz"
        )
    return tts_fallback_client

# Session storage: session_id -> (memory, llm_client)
session_storage: dict[str, tuple[ConversationMemory, Any]] = {}


def get_or_create_session(session_id: str) -> tuple[ConversationMemory, Any]:
    """
    Get or create session components.

    Args:
        session_id: Session identifier

    Returns:
        Tuple of (memory, llm_client) - client can be GeminiClient or OpenAILLMClient
    """
    if session_id not in session_storage:
        # Load configuration
        config = Config()

        # Create memory
        memory = ConversationMemory(max_messages=config.max_memory_messages)

        # Create LLM client based on provider
        system_instruction = get_system_instruction()
        
        if config.llm_provider == "openai":
            logger.info("Creating OpenAI LLM client")
            llm_client = OpenAILLMClient(
                api_key=config.openai_api_key,
                model_name=config.openai_llm_model,
                system_instruction=system_instruction,
                temperature=config.temperature
            )
        else:  # gemini (default)
            logger.info("Creating Gemini client")
            llm_client = GeminiClient(
                api_key=config.google_api_key,
                model_name=config.gemini_model,
                system_instruction=system_instruction,
                temperature=config.temperature
            )

        session_storage[session_id] = (memory, llm_client)
        logger.info(f"Created new session: {session_id} with {config.llm_provider}")

    return session_storage[session_id]


async def handle_text_input(session_id: str, text: str):
    """
    Handle text input from client with streaming TTS.

    Args:
        session_id: Session identifier
        text: User text input
    """
    logger.info(f"handle_text_input called for session {session_id}")
    memory, llm_client = get_or_create_session(session_id)

    # Add user message to memory
    memory = memory.add_message("user", text)
    session_storage[session_id] = (memory, llm_client)

    # Get conversation history
    history = memory.get_history()
    history_without_current = history[:-1]

    try:
        # Stream response from LLM (Gemini or OpenAI)
        full_response = ""
        current_sentence = ""
        sentences_for_context = []  # Keep for continuity
        chunk_count = 0
        
        logger.info(f"Starting LLM stream for session {session_id}")
        
        # Helper to generate and send audio for a sentence
        async def stream_sentence_audio(sentence: str, previous_sentences: list):
            if not sentence.strip():
                return
                
            try:
                logger.info(f"Generating audio for sentence: {sentence[:50]}...")
                tts = get_tts_client()
                
                # Get previous text for continuity (last 2 sentences)
                previous_text = " ".join(previous_sentences[-2:]) if previous_sentences else None
                
                # Generate audio to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                # ElevenLabs supports previous_text param
                if hasattr(tts, 'synthesize') and 'previous_text' in tts.synthesize.__code__.co_varnames:
                    await tts.synthesize(
                        sentence, 
                        tmp_path,
                        optimize_latency=3,
                        previous_text=previous_text
                    )
                else:
                    # Fallback for other TTS (Edge, OpenAI)
                    await tts.synthesize(sentence, tmp_path)
                
                # Read and send audio
                audio_bytes = Path(tmp_path).read_bytes()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                audio_msg = create_audio_response_message(audio_base64, session_id)
                await connection_manager.send_message(session_id, audio_msg)
                logger.info(f"Sent audio ({len(audio_bytes)} bytes)")
                
                # Cleanup
                try:
                    Path(tmp_path).unlink()
                except: pass
                    
            except Exception as e:
                logger.error(f"TTS error: {e}")
                
                # Fallback to Edge-TTS
                try:
                    logger.warning("Falling back to Edge-TTS")
                    fallback_tts = get_fallback_tts_client()
                    
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    await fallback_tts.synthesize(sentence, tmp_path)
                    audio_bytes = Path(tmp_path).read_bytes()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                    
                    audio_msg = create_audio_response_message(audio_base64, session_id)
                    await connection_manager.send_message(session_id, audio_msg)
                    logger.info("Fallback TTS succeeded")
                    
                    try:
                        Path(tmp_path).unlink()
                    except: pass
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback TTS also failed: {fallback_error}")
        
        # Process LLM stream and split into sentences
        tts_tasks = []
        for chunk in llm_client.chat_stream(text, history_without_current):
            chunk_count += 1
            full_response += chunk
            current_sentence += chunk
            
            # Send text chunk to client
            response_msg = create_text_response(chunk, session_id)
            await connection_manager.send_message(session_id, response_msg)
            
            # Check for sentence boundaries
            if any(punct in chunk for punct in [".", "!", "?", "\n", "。", "！", "？"]):
                sentence_to_speak = current_sentence.strip()
                if sentence_to_speak:
                    # Create task for TTS (parallel processing)
                    task = asyncio.create_task(
                        stream_sentence_audio(sentence_to_speak, sentences_for_context.copy())
                    )
                    tts_tasks.append(task)
                    sentences_for_context.append(sentence_to_speak)
                current_sentence = ""
        
        # Handle last incomplete sentence
        if current_sentence.strip():
            task = asyncio.create_task(
                stream_sentence_audio(current_sentence.strip(), sentences_for_context.copy())
            )
            tts_tasks.append(task)
        
        # Wait for all TTS tasks to complete
        if tts_tasks:
            await asyncio.gather(*tts_tasks, return_exceptions=True)
        
        logger.info(f"LLM stream complete for session {session_id}")
        
        # Add assistant response to memory
        if full_response:
            memory = memory.add_message("model", full_response)
            session_storage[session_id] = (memory, llm_client)
            logger.info(f"Added response to memory for session {session_id}")
        else:
            logger.warning(f"Empty response from LLM for session {session_id}")

    except (GeminiError, OpenAIError) as e:
        logger.error(f"LLM error for session {session_id}: {e}")
        error_msg = create_error_message(str(e), session_id)
        await connection_manager.send_message(session_id, error_msg)
    except Exception as e:
        logger.error(f"Unexpected error in handle_text_input for session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        error_msg = create_error_message(f"Internal error: {str(e)}", session_id)
        await connection_manager.send_message(session_id, error_msg)


async def handle_audio_chunk(session_id: str, audio_data: str):
    """
    Handle audio chunk from client.

    Args:
        session_id: Session identifier
        audio_data: Base64 encoded audio data
    """
    stream = audio_stream_manager.get_stream(session_id)
    if not stream:
        logger.warning(f"No audio stream for session {session_id}")
        return

    try:
        await stream.add_audio_chunk(audio_data)

        # Send status update
        buffer_size = await stream.get_buffer_size()
        status_msg = create_status_message(
            f"Received audio chunk, buffer size: {buffer_size} bytes",
            session_id
        )
        await connection_manager.send_message(session_id, status_msg)

    except Exception as e:
        logger.error(f"Error handling audio chunk for session {session_id}: {e}")
        error_msg = create_error_message(str(e), session_id)
        await connection_manager.send_message(session_id, error_msg)


async def handle_start_recording(session_id: str):
    """
    Handle start recording request.

    Args:
        session_id: Session identifier
    """
    stream = audio_stream_manager.create_stream(session_id)
    await stream.start_recording()

    status_msg = create_status_message("Recording started", session_id)
    await connection_manager.send_message(session_id, status_msg)


async def handle_vad_audio(session_id: str, audio_base64: str):
    """
    Handle complete audio from VAD (Voice Activity Detection).

    Args:
        session_id: Session identifier
        audio_base64: Base64-encoded audio data
    """
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(audio_base64)
        logger.info(f"Received VAD audio: {len(audio_data)} bytes for session {session_id}")

        status_msg = create_status_message(
            f"Processing VAD audio: {len(audio_data)} bytes",
            session_id
        )
        await connection_manager.send_message(session_id, status_msg)

        # Process audio with STT
        if len(audio_data) > 0:
            try:
                # Get STT client
                stt = get_stt_client()

                # Transcribe audio
                result = await stt.transcribe_audio_bytes(
                    audio_data,
                    language="vi",  # Vietnamese
                    vad_filter=True
                )

                transcript_text = result["text"]
                logger.info(f"VAD Transcription: {transcript_text}")

                # Send transcript to client
                transcript_msg = create_transcript_message(transcript_text, session_id)
                await connection_manager.send_message(session_id, transcript_msg)

                # Process as text input (trigger LLM response)
                if transcript_text.strip():
                    await handle_text_input(session_id, transcript_text)

            except STTError as e:
                logger.error(f"STT error for VAD audio {session_id}: {e}")
                error_msg = create_error_message(f"STT error: {str(e)}", session_id)
                await connection_manager.send_message(session_id, error_msg)

    except Exception as e:
        logger.error(f"Error handling VAD audio for session {session_id}: {e}")
        error_msg = create_error_message(f"Failed to process VAD audio: {str(e)}", session_id)
        await connection_manager.send_message(session_id, error_msg)


async def handle_stop_recording(session_id: str):
    """
    Handle stop recording request.

    Args:
        session_id: Session identifier
    """
    stream = audio_stream_manager.get_stream(session_id)
    if not stream:
        logger.warning(f"No audio stream for session {session_id}")
        return

    audio_data = await stream.stop_recording()

    status_msg = create_status_message(
        f"Recording stopped, collected {len(audio_data)} bytes",
        session_id
    )
    await connection_manager.send_message(session_id, status_msg)

    # Process audio with STT
    if len(audio_data) > 0:
        logger.info(f"Processing {len(audio_data)} bytes of audio for session {session_id}")
        
        try:
            # Get STT client
            stt = get_stt_client()
            
            # Transcribe audio
            result = await stt.transcribe_audio_bytes(
                audio_data,
                language="vi",  # Vietnamese
                vad_filter=True
            )
            
            transcript_text = result["text"]
            logger.info(f"Transcription: {transcript_text}")
            
            # Send transcript to client
            transcript_msg = create_transcript_message(transcript_text, session_id)
            await connection_manager.send_message(session_id, transcript_msg)
            
            # Process as text input (trigger LLM response)
            if transcript_text.strip():
                await handle_text_input(session_id, transcript_text)
            
        except STTError as e:
            logger.error(f"STT error for session {session_id}: {e}")
            error_msg = create_error_message(f"STT error: {str(e)}", session_id)
            await connection_manager.send_message(session_id, error_msg)
        except Exception as e:
            logger.error(f"Unexpected error in STT for session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            error_msg = create_error_message(f"STT processing failed: {str(e)}", session_id)
            await connection_manager.send_message(session_id, error_msg)


@app.get("/")
async def root():
    """Serve the HTML test client."""
    static_dir = Path(__file__).parent.parent / "static"
    index_file = static_dir / "index.html"

    if index_file.exists():
        return FileResponse(str(index_file))

    # Fallback to JSON response
    return {
        "name": "VoiceAI WebSocket Server",
        "version": "0.3.0",
        "status": "running",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "docs": "/docs"
        },
        "active_connections": connection_manager.get_active_count(),
        "active_streams": audio_stream_manager.get_active_count()
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "VoiceAI WebSocket Server",
        "version": "0.3.0",
        "status": "running",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "docs": "/docs"
        },
        "active_connections": connection_manager.get_active_count(),
        "active_streams": audio_stream_manager.get_active_count()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_connections": connection_manager.get_active_count(),
        "active_streams": audio_stream_manager.get_active_count(),
        "active_sessions": len(session_storage)
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.

    Args:
        websocket: WebSocket connection
    """
    # Connect and get session ID
    session_id = await connection_manager.connect(websocket)

    try:
        # Send welcome message
        welcome_msg = create_status_message(
            "Connected to VoiceAI server",
            session_id
        )
        await connection_manager.send_message(session_id, welcome_msg)

        # Message loop
        while True:
            # Receive message
            data = await websocket.receive_text()
            logger.info(f"Received message from {session_id}: {data}")

            try:
                # Parse message
                message = WebSocketMessage.from_json(data)
                logger.info(f"Parsed message type: {message.type}")

                # Validate message
                MessageValidator.validate_message(message)
                logger.info(f"Message validated successfully")

                # Handle based on message type
                if message.type == MessageType.TEXT_INPUT:
                    text = message.data.get("text")
                    logger.info(f"Handling text input: {text}")
                    await handle_text_input(session_id, text)

                elif message.type == MessageType.AUDIO_CHUNK:
                    audio = message.data.get("audio")
                    await handle_audio_chunk(session_id, audio)

                elif message.type == MessageType.START_RECORDING:
                    await handle_start_recording(session_id)

                elif message.type == MessageType.STOP_RECORDING:
                    await handle_stop_recording(session_id)

                elif message.type == MessageType.VAD_AUDIO:
                    audio = message.data.get("audio")
                    await handle_vad_audio(session_id, audio)

                elif message.type == MessageType.PING:
                    pong_msg = WebSocketMessage(
                        type=MessageType.PONG,
                        data={},
                        session_id=session_id
                    )
                    await connection_manager.send_message(session_id, pong_msg)

                else:
                    logger.warning(f"Unknown message type: {message.type}")

            except ProtocolError as e:
                logger.error(f"Protocol error for session {session_id}: {e}")
                error_msg = create_error_message(str(e), session_id)
                await connection_manager.send_message(session_id, error_msg)

            except Exception as e:
                logger.error(f"Error processing message for session {session_id}: {e}")
                error_msg = create_error_message(
                    "Internal server error",
                    session_id
                )
                await connection_manager.send_message(session_id, error_msg)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")

    finally:
        # Cleanup
        connection_manager.disconnect(session_id)
        audio_stream_manager.remove_stream(session_id)

        # Remove session (optional: could keep for reconnection)
        if session_id in session_storage:
            del session_storage[session_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
