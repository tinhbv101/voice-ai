# 🔧 Troubleshooting Guide

## WebSocket Connection Issues

### Issue: `WebSocket connection to 'ws://localhost:8000/ws' failed`

**Cause**: Browser trying to connect to localhost on remote server

**Solution**: 
✅ Already fixed! Frontend now auto-detects server URL:
```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.host;
const wsUrl = `${protocol}//${host}/ws`;
```

### Issue: Connection refused

**Check server is running**:
```bash
sudo systemctl status voiceai
# Or
ps aux | grep uvicorn
```

**Check port is open**:
```bash
netstat -tulpn | grep 8000
```

**Check firewall**:
```bash
sudo ufw status
sudo ufw allow 8000/tcp
```

### Issue: WebSocket closes immediately

**Check logs**:
```bash
sudo journalctl -u voiceai -f
```

**Common causes**:
1. Missing API keys in `.env`
2. Wrong Python version (need 3.10+)
3. Missing dependencies
4. Port conflict

## ElevenLabs API Issues

### Issue: `unsupported_model` or `optimize_streaming_latency not supported`

**Cause**: Model eleven_v3 has limited parameter support

**Solution**: Use eleven_multilingual_v2 or eleven_turbo_v2
```bash
# In .env
ELEVENLABS_MODEL=eleven_multilingual_v2
```

Or code will auto-detect and skip unsupported params.

### Issue: ElevenLabs API quota exceeded

**Check quota**: https://elevenlabs.io/app/usage

**Fallback**: Server auto-falls back to Edge-TTS (free)

## STT (Speech-to-Text) Issues

### Issue: Model download fails

**Pre-download manually**:
```bash
source venv/bin/activate
python3 -c "from faster_whisper import WhisperModel; WhisperModel('tiny')"
```

### Issue: STT very slow

**Solutions**:
1. Use tiny model (fastest):
   ```python
   # In src/server.py
   model_size="tiny"  # ~75MB, 1-2s for 10s audio
   ```

2. Use GPU (if available):
   ```python
   device="cuda"
   ```

3. Lower compute type:
   ```python
   compute_type="int8"  # Faster than float16
   ```

## Audio Issues

### Issue: No audio output

**Check browser permissions**:
- Allow microphone access
- Check browser audio settings
- Try in Chrome/Edge (best support)

**Check audio format**:
- Input: WebM with Opus codec
- Output: MP3

### Issue: Audio choppy or delayed

**Solutions**:
1. Reduce latency:
   ```bash
   # In .env
   ELEVENLABS_MODEL=eleven_turbo_v2
   ```

2. Use faster STT model:
   ```python
   model_size="tiny"
   ```

3. Check network:
   ```bash
   ping your-server-ip
   ```

## Memory Issues

### Issue: Out of memory (OOM)

**Check memory**:
```bash
free -h
htop
```

**Solutions**:
1. Use smaller STT model:
   ```python
   model_size="tiny"  # ~75MB vs base=150MB
   ```

2. Limit max connections:
   ```python
   # In src/websocket_manager.py
   MAX_CONNECTIONS = 10
   ```

3. Add memory limits:
   ```bash
   # In systemd service
   MemoryLimit=2G
   ```

## API Key Issues

### Issue: `OPENAI_API_KEY is required`

**Check .env file**:
```bash
cat .env | grep OPENAI_API_KEY
```

**Fix**:
```bash
nano .env
# Add: OPENAI_API_KEY=sk-...
```

**Restart**:
```bash
sudo systemctl restart voiceai
```

### Issue: `Invalid API key`

**Verify key**:
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api
- Gemini: https://aistudio.google.com/app/apikey

## Python Environment Issues

### Issue: `externally-managed-environment`

**Always use venv**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Module not found

**Reinstall dependencies**:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Import errors

**Check Python version**:
```bash
python3 --version  # Need 3.10+
```

## Network Issues

### Issue: Can't access from external IP

**Check server binding**:
```bash
# Should bind to 0.0.0.0, not 127.0.0.1
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

**Check firewall**:
```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

**Check cloud provider security group**:
- AWS: Add inbound rule for port 8000
- GCP: Add firewall rule
- Azure: Add NSG rule

### Issue: CORS errors

**Already handled** in FastAPI:
```python
allow_origins=["*"]  # Change in production
```

## Performance Monitoring

### Check CPU usage:
```bash
htop
top -p $(pgrep -f uvicorn)
```

### Check memory usage:
```bash
free -h
ps aux | grep uvicorn
```

### Check disk usage:
```bash
df -h
du -sh audio_output/
```

### Check logs:
```bash
sudo journalctl -u voiceai -f --since "10 minutes ago"
```

## Quick Diagnostics

Run this on server:

```bash
# Check Python
python3 --version

# Check pip in venv
source venv/bin/activate
pip list | grep -E "fastapi|uvicorn|openai|elevenlabs|faster-whisper"

# Check .env
cat .env | grep -E "API_KEY|PROVIDER|MODEL"

# Check ports
netstat -tulpn | grep 8000

# Check service
sudo systemctl status voiceai

# Test WebSocket locally
curl -I http://localhost:8000/health

# Check audio dependencies
which ffmpeg
ffmpeg -version
```

## Emergency Reset

If all else fails:

```bash
# Stop everything
sudo systemctl stop voiceai
pkill -f uvicorn

# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify .env
nano .env

# Test manually
uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload

# If works, enable service
sudo systemctl start voiceai
```

## Get Help

Check logs for specific error:
```bash
sudo journalctl -u voiceai -n 100 --no-pager
```

Share error message for specific help!
