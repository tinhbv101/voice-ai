# Deployment Guide - Ubuntu/Debian Server

## Quick Setup (Production Server)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-full python3-pip python3-venv ffmpeg

# 2. Clone repository
git clone https://github.com/tinhbv101/voice-ai.git
cd voice-ai

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate venv
source venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Setup environment variables
cp env.example .env
nano .env  # Edit with your API keys

# 7. Run server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Or with systemd service (production)
sudo nano /etc/systemd/system/voiceai.service
```

## Environment Variables (.env)

```bash
# LLM Provider (choose one)
LLM_PROVIDER=openai  # or gemini

# OpenAI (Recommended)
OPENAI_API_KEY=sk-...
OPENAI_LLM_MODEL=gpt-4o-mini

# Gemini (Alternative)
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash

# TTS Provider
TTS_PROVIDER=elevenlabs  # or edge (free), openai

# ElevenLabs TTS (Best Quality)
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE=rachel
ELEVENLABS_MODEL=eleven_multilingual_v2

# General Settings
TEMPERATURE=0.7
MAX_MEMORY_MESSAGES=10
```

## Systemd Service (Auto-restart on boot)

Create `/etc/systemd/system/voiceai.service`:

```ini
[Unit]
Description=VoiceAI WebSocket Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/voice-ai
Environment="PATH=/root/voice-ai/venv/bin"
ExecStart=/root/voice-ai/venv/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable voiceai
sudo systemctl start voiceai
sudo systemctl status voiceai
```

## Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

## Firewall Setup

```bash
# Allow port 8000
sudo ufw allow 8000/tcp

# Or if using Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Resource Requirements

- **RAM**: 2GB minimum (4GB recommended for STT)
- **CPU**: 2 cores minimum (STT is CPU intensive)
- **Disk**: 5GB (for models and audio cache)
- **Bandwidth**: 1Mbps minimum for real-time audio

## Performance Optimization

### For faster STT:
```python
# In src/server.py, change to tiny model
stt_client = FasterWhisperClient(
    model_size="tiny",  # ~75MB, fastest
    device="cpu",
    compute_type="int8"
)
```

### For faster TTS:
```bash
# In .env
ELEVENLABS_MODEL=eleven_turbo_v2  # Fastest with good quality
```

## Monitoring

```bash
# Check logs
sudo journalctl -u voiceai -f

# Check service status
sudo systemctl status voiceai

# Check port
netstat -tulpn | grep 8000

# Check processes
ps aux | grep uvicorn
```

## Troubleshooting

### Port already in use:
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Permission denied:
```bash
sudo chown -R $USER:$USER /root/voice-ai
```

### FFmpeg not found:
```bash
sudo apt install -y ffmpeg
```

### Model download fails:
```bash
# Pre-download models
python3 -c "from faster_whisper import WhisperModel; WhisperModel('tiny')"
```
