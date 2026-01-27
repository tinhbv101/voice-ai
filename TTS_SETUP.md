# TTS Provider Setup Guide

Dự án hỗ trợ 3 TTS providers: **Edge-TTS** (free), **OpenAI TTS**, và **ElevenLabs**.

## 1. Edge-TTS (Mặc định - Miễn phí)

**Ưu điểm**: Free, không cần API key
**Nhược điểm**: Giọng hơi đơ, không tự nhiên lắm

```bash
# Không cần config gì, chạy luôn
TTS_PROVIDER=edge
```

## 2. OpenAI TTS (Khuyên dùng - Cân bằng)

**Ưu điểm**: Giọng rất tự nhiên, giá rẻ ($15/1M chars)
**Nhược điểm**: Không có tiếng Việt (nhưng giọng English vẫn ok)

### Setup

1. Lấy API key tại: https://platform.openai.com/api-keys

2. Thêm vào `.env`:
```bash
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_VOICE=nova        # Giọng cho anime vibe: nova, shimmer
OPENAI_MODEL=tts-1       # tts-1 (rẻ hơn) hoặc tts-1-hd (chất lượng cao hơn)
```

### Giọng có sẵn:
- `alloy` - Neutral
- `echo` - Male
- `fable` - British accent
- `onyx` - Deep male
- `nova` - Warm female (⭐ Khuyên dùng cho anime)
- `shimmer` - Soft female (⭐ Khuyên dùng cho waifu)

### Giá:
- `tts-1`: $0.015/1K characters (~$15/1M chars)
- `tts-1-hd`: $0.030/1K characters (~$30/1M chars)

## 3. ElevenLabs (Tốt nhất - Đắt)

**Ưu điểm**: Giọng TỰ NHIÊN NHẤT, hỗ trợ tiếng Việt tốt, voice cloning
**Nhược điểm**: Đắt ($300/1M chars), cần API key

### Setup

1. Tạo tài khoản tại: https://elevenlabs.io

2. Lấy API key tại: https://elevenlabs.io/app/settings/api-keys

3. Thêm vào `.env`:
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=xxxxxxxxxxxxxx
ELEVENLABS_VOICE=rachel           # Tên preset hoặc voice ID
ELEVENLABS_MODEL=eleven_multilingual_v2  # Model
```

### Voice Presets:
- `rachel` - Calm, natural female (⭐ Khuyên dùng)
- `bella` - Soft, gentle female
- `elli` - Young, energetic female (⭐ Cho anime)
- `domi` - Strong, confident female
- `adam` - Deep male
- `antoni` - Warm male

Hoặc dùng voice ID trực tiếp từ ElevenLabs Voice Library.

### Models:
- `eleven_monolingual_v1` - English only, nhanh nhất
- `eleven_multilingual_v1` - 25+ ngôn ngữ
- `eleven_multilingual_v2` - Mới nhất, chất lượng tốt nhất (⭐ Khuyên dùng)
- `eleven_turbo_v2` - Nhanh nhất, chất lượng vẫn tốt

### Giá:
- Free tier: 10,000 chars/month
- Starter: $5/month - 30,000 chars
- Creator: $22/month - 100,000 chars
- Pro: $99/month - 500,000 chars
- API pricing: ~$0.30/1K chars

## So Sánh

| Provider | Tự Nhiên | Tiếng Việt | Giá (1M chars) | Latency | Khuyên dùng |
|----------|----------|------------|----------------|---------|-------------|
| Edge-TTS | ⭐⭐ | ✅ | Free | ~1-2s | Để test |
| OpenAI | ⭐⭐⭐⭐⭐ | ❌ | $15 | ~1-2s | ⭐ Production |
| ElevenLabs | ⭐⭐⭐⭐⭐ | ✅ | $300 | ~2-3s | Premium |

## Cài đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Hoặc install riêng lẻ
pip install openai>=1.0.0
pip install elevenlabs>=1.0.0
```

## Test TTS

```bash
# Test OpenAI TTS
python src/openai_tts_client.py

# Test ElevenLabs TTS
python src/elevenlabs_tts_client.py
```

## Chạy Server

```bash
# Đảm bảo .env đã config đúng
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ tự động load TTS provider dựa trên `TTS_PROVIDER` trong `.env`.

## Gợi Ý

### Cho Hackathon/Demo:
- Dùng **OpenAI TTS** (giọng nova/shimmer)
- Nhanh, rẻ, chất lượng tốt

### Cho Production (Tiếng Việt):
- Dùng **ElevenLabs** với model `eleven_turbo_v2`
- Giọng tự nhiên nhất, hỗ trợ tiếng Việt

### Cho Development:
- Dùng **Edge-TTS**
- Free, không cần API key

## Troubleshooting

### Error: "ELEVENLABS_API_KEY is required"
- Đảm bảo đã thêm `ELEVENLABS_API_KEY` vào `.env`
- Kiểm tra TTS_PROVIDER đã set đúng

### Error: "OPENAI_API_KEY is required"
- Đảm bảo đã thêm `OPENAI_API_KEY` vào `.env`
- Kiểm tra API key còn credits

### Giọng không tự nhiên:
- Edge-TTS: Đây là limitation, chuyển sang OpenAI/ElevenLabs
- OpenAI: Thử voice khác (nova, shimmer)
- ElevenLabs: Thử model `eleven_turbo_v2` hoặc voice khác

### Latency cao:
- OpenAI: Dùng model `tts-1` thay vì `tts-1-hd`
- ElevenLabs: Dùng model `eleven_turbo_v2` thay vì `eleven_multilingual_v2`
- Edge-TTS: Đã nhanh nhất rồi
