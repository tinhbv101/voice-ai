# 🎯 Quick Start - TTS Integration

## ✅ Đã Setup Xong

Dự án đã có **3 TTS providers**:
- ✅ **ElevenLabs** (DEFAULT, cần API key, giọng tốt nhất)
- ✅ **OpenAI TTS** (cần API key, giọng tự nhiên)
- ✅ **Edge-TTS** (fallback, free)

## 🚀 Bắt Đầu Ngay

### 1. Activate Virtual Environment

```bash
cd /root/voice-ai
source venv/bin/activate
```

### 2. Test TTS Demo

```bash
# Test Edge-TTS (free, không cần API key)
python3 demo_tts.py
# → Tạo file demo_edge.mp3
```

### 3. Setup API Keys (Optional)

**Để dùng OpenAI TTS:**
```bash
export OPENAI_API_KEY=sk-proj-xxxxx
python3 demo_tts.py  # Test OpenAI
```

**Để dùng ElevenLabs:**
```bash
export ELEVENLABS_API_KEY=your_key
python3 demo_tts.py  # Test ElevenLabs
```

### 4. Config Server

Tạo file `.env` (copy từ `.env.example`):

```bash
cp .env.example .env
nano .env  # Hoặc editor bất kỳ
```

**Add ElevenLabs API key trong `.env`:**

```bash
# Default: ElevenLabs (giọng tốt nhất)
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE=elli              # Young anime vibe
ELEVENLABS_MODEL=eleven_turbo_v2   # Fast model

# Hoặc dùng OpenAI
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-xxx

# Hoặc dùng Edge-TTS (free, fallback)
TTS_PROVIDER=edge
```

### 5. Run Server

```bash
source venv/bin/activate
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

Mở browser: http://localhost:8000

## 📁 Files

```
/root/voice-ai/
├── src/
│   ├── elevenlabs_tts_client.py    # ElevenLabs (NEW)
│   ├── openai_tts_client.py        # OpenAI (NEW)
│   ├── tts_client.py               # Edge-TTS
│   ├── config.py                   # Config updated
│   └── server.py                   # Server updated
├── demo_tts.py                     # Test script (NEW)
├── .env.example                    # Config template (NEW)
├── TTS_SETUP.md                    # Chi tiết setup
└── INTEGRATION_COMPLETE.md         # Summary
```

## 🎤 Giọng Khuyên Dùng

### ElevenLabs (DEFAULT - Tự nhiên nhất)
```bash
ELEVENLABS_VOICE=elli     # Young anime vibe (⭐ Default)
ELEVENLABS_VOICE=rachel   # Calm female
ELEVENLABS_VOICE=bella    # Soft waifu vibe
```

### OpenAI (Balance tốt)
```bash
OPENAI_VOICE=nova      # Warm female
OPENAI_VOICE=shimmer   # Soft female
```

## 📚 Docs

- **TTS_SETUP.md** - Chi tiết về từng provider, pricing, setup
- **INTEGRATION_COMPLETE.md** - Full summary của integration
- **demo_tts.py** - Script test nhanh

## 💡 Tips

1. **Development**: Dùng Edge-TTS (free)
2. **Hackathon**: Dùng OpenAI (balance tốt)
3. **Production**: Dùng ElevenLabs (tốt nhất)

## 🐛 Issues?

```bash
# Imports không work?
source venv/bin/activate
pip install -r requirements.txt

# Server không start?
python3 -c "from src.server import app; print('OK')"

# TTS không hoạt động?
python3 demo_tts.py  # Test từng provider
```

---

**Ready to go!** 🎉
