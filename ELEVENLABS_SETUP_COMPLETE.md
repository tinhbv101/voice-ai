# ✅ ElevenLabs TTS Integration Complete!

Đã thêm **ElevenLabs** và **OpenAI TTS** vào dự án. Bây giờ bạn có 3 TTS providers:

## 🎯 Providers Có Sẵn

### 1. Edge-TTS (Mặc định)
- **Free**, không cần API key
- Giọng hơi đơ, không tự nhiên lắm
- Setup: Không cần config gì

### 2. OpenAI TTS ⭐ (Khuyên dùng)
- Giọng **rất tự nhiên**, giá rẻ ($15/1M chars)
- Giọng `nova` và `shimmer` phù hợp anime vibe
- Không có tiếng Việt nhưng English rất hay
- Setup: Cần `OPENAI_API_KEY`

### 3. ElevenLabs ⭐⭐ (Tốt nhất)
- Giọng **TỰ NHIÊN NHẤT**, hỗ trợ tiếng Việt tốt
- Voice cloning, emotion control
- Đắt ($300/1M chars)
- Setup: Cần `ELEVENLABS_API_KEY`

## 📁 Files Đã Tạo

```
src/
├── elevenlabs_tts_client.py   # ElevenLabs client (NEW)
├── openai_tts_client.py       # OpenAI client (UPDATED)
└── config.py                  # Config updated với TTS providers

TTS_SETUP.md                   # Hướng dẫn chi tiết
```

## 🚀 Quick Start

### 1. Cài dependencies (Đã xong ✅)

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Config trong `.env`

**Để dùng ElevenLabs:**
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE=rachel           # rachel, bella, elli (xem TTS_SETUP.md)
ELEVENLABS_MODEL=eleven_multilingual_v2
```

**Để dùng OpenAI:**
```bash
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_VOICE=nova                 # nova, shimmer (anime vibe)
OPENAI_MODEL=tts-1
```

**Để dùng Edge-TTS (default):**
```bash
TTS_PROVIDER=edge
# Không cần API key
```

### 3. Run Server

```bash
source venv/bin/activate
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ tự động load TTS provider từ `.env`.

## 🎤 ElevenLabs Voice Presets

Đã config sẵn các giọng hay:

- `rachel` - Calm, natural female (⭐ Default)
- `bella` - Soft, gentle female
- `elli` - Young, energetic female (⭐ Anime vibe)
- `domi` - Strong, confident female
- `adam` - Deep male
- `antoni` - Warm male

Hoặc dùng voice ID trực tiếp từ ElevenLabs Voice Library.

## 📖 Full Documentation

Xem `TTS_SETUP.md` để biết:
- Chi tiết về từng provider
- Pricing comparison
- Troubleshooting
- Advanced config

## ✅ Test Thử

```bash
# Test OpenAI TTS
source venv/bin/activate
export OPENAI_API_KEY=sk-xxx
python src/openai_tts_client.py

# Test ElevenLabs TTS
export ELEVENLABS_API_KEY=xxx
python src/elevenlabs_tts_client.py
```

## 🎯 Gợi Ý

**Cho Hackathon/Demo:**
→ Dùng **OpenAI TTS** (balance tốt)

**Cho Production (Tiếng Việt):**
→ Dùng **ElevenLabs** (tự nhiên nhất)

**Cho Development:**
→ Dùng **Edge-TTS** (free)

---

Enjoy! 🎉
