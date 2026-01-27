# ✅ ElevenLabs Default Config - DONE!

## 🎯 Changes Made

### 1. Default Provider
- ✅ Changed from `edge` → `elevenlabs`
- ✅ Server will use ElevenLabs by default

### 2. Default Voice
- ✅ Voice: `elli` (Young, energetic - anime vibe)
- ✅ Was: `rachel` → Now: `elli`

### 3. Default Model
- ✅ Model: `eleven_turbo_v2` (Fast & good quality)
- ✅ Was: `eleven_multilingual_v2` → Now: `eleven_turbo_v2`

### 4. Updated Files
- ✅ `src/config.py` - Default provider = elevenlabs
- ✅ `.env.example` - Updated template
- ✅ `QUICKSTART.md` - Updated docs
- ✅ `ELEVENLABS_DEFAULT.md` - New guide (NEW)

## 🚀 Quick Setup

### 1. Get API Key
https://elevenlabs.io/app/settings/api-keys

### 2. Create .env
```bash
cp .env.example .env
```

### 3. Add API Key
```bash
GOOGLE_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 4. Run Server
```bash
source venv/bin/activate
uvicorn src.server:app --reload
```

→ **ElevenLabs will be used automatically!**

## 🎤 Default Settings

```bash
TTS_PROVIDER=elevenlabs              # Auto-selected
ELEVENLABS_VOICE=elli                # Young anime vibe
ELEVENLABS_MODEL=eleven_turbo_v2     # Fast model
```

## 🔄 Override Options

Nếu muốn đổi trong `.env`:

```bash
# Đổi giọng
ELEVENLABS_VOICE=rachel  # Calm
ELEVENLABS_VOICE=bella   # Soft waifu

# Đổi model (quality vs speed)
ELEVENLABS_MODEL=eleven_multilingual_v2  # Better quality, slower

# Đổi provider
TTS_PROVIDER=openai  # Use OpenAI instead
TTS_PROVIDER=edge    # Use free Edge-TTS
```

## 📊 Why ElevenLabs Default?

| Feature | ElevenLabs | OpenAI | Edge-TTS |
|---------|------------|--------|----------|
| **Tự nhiên** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Tiếng Việt** | ✅ Xuất sắc | ❌ Không có | ✅ OK |
| **Emotion** | ✅ Tốt | ⭐⭐⭐ | ❌ |
| **Latency** | 2-3s | 1-2s | 1-2s |

→ ElevenLabs tốt nhất cho tiếng Việt tự nhiên!

## ✅ Testing

```bash
# Test config
source venv/bin/activate
python3 -c "
import os
os.environ['GOOGLE_API_KEY']='test'
os.environ['ELEVENLABS_API_KEY']='test'
from src.config import Config
c = Config()
print(f'Provider: {c.tts_provider}')
print(f'Voice: {c.elevenlabs_voice}')
print(f'Model: {c.elevenlabs_model}')
"

# Expected output:
# Provider: elevenlabs
# Voice: elli
# Model: eleven_turbo_v2
```

---

**Status**: ✅ ElevenLabs is now the default TTS provider!

Just add your API key and you're ready to go! 🎉
