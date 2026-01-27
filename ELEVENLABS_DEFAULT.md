# ✅ ElevenLabs Set as Default!

## 🎯 Default Configuration

**TTS Provider**: ElevenLabs (giọng tốt nhất)
**Voice**: `elli` (Young, energetic - anime vibe)
**Model**: `eleven_turbo_v2` (Fast, good quality)

## 🚀 Setup Nhanh

### 1. Get ElevenLabs API Key

1. Tạo tài khoản: https://elevenlabs.io
2. Lấy API key: https://elevenlabs.io/app/settings/api-keys
3. Copy API key

### 2. Config .env

```bash
# Copy template
cp .env.example .env

# Edit và add API key
nano .env
```

**Add vào `.env`:**
```bash
GOOGLE_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 3. Run Server

```bash
source venv/bin/activate
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

→ Server sẽ tự động dùng ElevenLabs!

## 🎤 Voice Options

Nếu muốn đổi giọng, edit trong `.env`:

```bash
# Anime vibe (default)
ELEVENLABS_VOICE=elli

# Calm, natural
ELEVENLABS_VOICE=rachel

# Soft waifu vibe
ELEVENLABS_VOICE=bella
```

## ⚡ Model Options

```bash
# Fastest (default)
ELEVENLABS_MODEL=eleven_turbo_v2

# Best quality
ELEVENLABS_MODEL=eleven_multilingual_v2
```

## 🔄 Fallback Options

Nếu chưa có ElevenLabs API key, đổi sang:

```bash
# Free Edge-TTS (fallback)
TTS_PROVIDER=edge

# Hoặc OpenAI
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
```

## 📊 Pricing

ElevenLabs pricing:
- **Free tier**: 10,000 chars/month
- **Starter**: $5/month - 30,000 chars
- **Creator**: $22/month - 100,000 chars
- **Pro**: $99/month - 500,000 chars

→ Free tier đủ để test!

## ✅ Default Settings Summary

```bash
TTS_PROVIDER=elevenlabs              # Default provider
ELEVENLABS_VOICE=elli                # Young anime vibe
ELEVENLABS_MODEL=eleven_turbo_v2     # Fast & good quality
```

**Ready to go with the best TTS!** 🎉
