#!/bin/bash
# Quick diagnostic script for VoiceAI server

echo "🔍 VoiceAI Server Diagnostics"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

# 1. Check Python version
echo "1. Python Version:"
python3 --version
check_status "Python installed"
echo ""

# 2. Check venv
echo "2. Virtual Environment:"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} venv exists"
else
    echo -e "${YELLOW}!${NC} venv not found. Run: python3 -m venv venv"
fi
echo ""

# 3. Check .env
echo "3. Environment Variables:"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env exists"
    echo "   API Keys configured:"
    grep -E "API_KEY|PROVIDER" .env | sed 's/=.*/=***/' | sed 's/^/   /'
else
    echo -e "${RED}✗${NC} .env not found. Run: cp env.example .env"
fi
echo ""

# 4. Check FFmpeg
echo "4. FFmpeg:"
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg installed"
    ffmpeg -version | head -n 1 | sed 's/^/   /'
else
    echo -e "${RED}✗${NC} FFmpeg not found. Run: sudo apt install ffmpeg"
fi
echo ""

# 5. Check port 8000
echo "5. Port 8000:"
if netstat -tulpn 2>/dev/null | grep -q ":8000"; then
    echo -e "${GREEN}✓${NC} Port 8000 is in use (server running)"
    netstat -tulpn | grep ":8000" | sed 's/^/   /'
else
    echo -e "${YELLOW}!${NC} Port 8000 is free (server not running)"
fi
echo ""

# 6. Check service
echo "6. Systemd Service:"
if systemctl list-units --type=service --all | grep -q voiceai; then
    echo -e "${GREEN}✓${NC} Service exists"
    systemctl is-active voiceai &>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Service is running"
    else
        echo -e "${YELLOW}!${NC} Service is stopped"
    fi
else
    echo -e "${YELLOW}!${NC} Service not installed"
fi
echo ""

# 7. Check Python packages (if venv exists)
if [ -d "venv" ]; then
    echo "7. Python Packages:"
    source venv/bin/activate
    
    packages=("fastapi" "uvicorn" "openai" "elevenlabs" "faster-whisper" "edge-tts")
    for pkg in "${packages[@]}"; do
        if pip show "$pkg" &>/dev/null; then
            version=$(pip show "$pkg" | grep Version | cut -d' ' -f2)
            echo -e "${GREEN}✓${NC} $pkg ($version)"
        else
            echo -e "${RED}✗${NC} $pkg not installed"
        fi
    done
    deactivate
    echo ""
fi

# 8. Test health endpoint
echo "8. Health Check:"
if curl -s http://localhost:8000/health &>/dev/null; then
    response=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}✓${NC} Server is responding"
    echo "$response" | python3 -m json.tool 2>/dev/null | sed 's/^/   /'
else
    echo -e "${RED}✗${NC} Server not responding on http://localhost:8000"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Summary:"
echo ""

if [ -d "venv" ] && [ -f ".env" ] && command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓ Basic setup complete${NC}"
    echo ""
    echo "🚀 To start server:"
    echo "   source venv/bin/activate"
    echo "   uvicorn src.server:app --host 0.0.0.0 --port 8000"
else
    echo -e "${YELLOW}! Setup incomplete${NC}"
    echo ""
    echo "📝 Run these commands:"
    [ ! -d "venv" ] && echo "   python3 -m venv venv"
    [ ! -f ".env" ] && echo "   cp env.example .env && nano .env"
    ! command -v ffmpeg &> /dev/null && echo "   sudo apt install ffmpeg"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

echo ""
echo "📚 For more help, see:"
echo "   - DEPLOYMENT.md"
echo "   - TROUBLESHOOTING.md"
echo "   - PRODUCTION.md"
