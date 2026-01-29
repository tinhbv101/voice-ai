# 🚀 Quick Start - Production Server

## One-Command Setup

```bash
sudo bash setup.sh
```

This will:
- Install system dependencies (Python, FFmpeg)
- Create virtual environment
- Install Python packages
- Setup systemd service
- Create .env template

## Manual Setup

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3-full python3-venv ffmpeg

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Setup environment
cp env.example .env
nano .env  # Add your API keys

# 5. Run server
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

## Required API Keys

### Option A: OpenAI (Recommended)
- Get key: https://platform.openai.com/api-keys
- Cost: ~$0.15/1M tokens (very cheap)
- Set in `.env`:
  ```bash
  LLM_PROVIDER=openai
  OPENAI_API_KEY=sk-...
  ```

### Option B: Gemini (Free)
- Get key: https://aistudio.google.com/app/apikey
- Free tier: 15 req/min, 1500 req/day
- Set in `.env`:
  ```bash
  LLM_PROVIDER=gemini
  GOOGLE_API_KEY=AIza...
  ```

### TTS (Optional for better voice)
- ElevenLabs: https://elevenlabs.io
- Free tier: 10k chars/month
- Set in `.env`:
  ```bash
  TTS_PROVIDER=elevenlabs
  ELEVENLABS_API_KEY=...
  ```

## Run Server

```bash
# Activate venv
source venv/bin/activate

# Run server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Or with auto-reload (development)
uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

## Access

- Web UI: http://your-server-ip:8000
- Health check: http://your-server-ip:8000/health
- API docs: http://your-server-ip:8000/docs

## Systemd Service (Auto-start on boot)

```bash
# Enable service
sudo systemctl enable voiceai

# Start service
sudo systemctl start voiceai

# Check status
sudo systemctl status voiceai

# View logs
sudo journalctl -u voiceai -f

# Restart after config changes
sudo systemctl restart voiceai
```

## Troubleshooting

### "externally-managed-environment" error
```bash
# Always use venv!
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Port 8000 already in use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### FFmpeg not found
```bash
sudo apt install -y ffmpeg
```

### Model download slow
```bash
# Pre-download STT model
source venv/bin/activate
python3 -c "from faster_whisper import WhisperModel; WhisperModel('tiny')"
```

## Firewall Rules

```bash
# Allow port 8000
sudo ufw allow 8000/tcp

# Check firewall status
sudo ufw status
```

## Performance Tips

1. **Use tiny STT model** for faster transcription (~1-2s)
2. **Use eleven_turbo_v2** for faster TTS
3. **Enable GPU** if available (set `device="cuda"` in server.py)
4. **Use reverse proxy** (Nginx) for production
5. **Enable gzip** compression for WebSocket

## Security Notes

- Change default ports in production
- Add authentication (JWT tokens)
- Use HTTPS (SSL certificate)
- Restrict CORS origins
- Add rate limiting
- Monitor API usage

## Minimum Requirements

- Ubuntu 20.04+ or Debian 11+
- Python 3.10+
- 2GB RAM (4GB recommended)
- 2 CPU cores
- 5GB disk space
