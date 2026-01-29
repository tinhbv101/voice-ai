#!/bin/bash
# Quick setup script for Ubuntu/Debian server

set -e  # Exit on error

echo "🚀 VoiceAI Server Setup"
echo "======================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root: sudo bash setup.sh"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update
apt install -y python3-full python3-pip python3-venv ffmpeg

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
echo "📚 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp env.example .env
    echo ""
    echo "🔑 Please edit .env and add your API keys:"
    echo "   nano .env"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Create systemd service
echo "🔧 Creating systemd service..."
CURRENT_DIR=$(pwd)
cat > /etc/systemd/system/voiceai.service <<EOF
[Unit]
Description=VoiceAI WebSocket Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env: nano .env"
echo "   2. Enable service: sudo systemctl enable voiceai"
echo "   3. Start service: sudo systemctl start voiceai"
echo "   4. Check status: sudo systemctl status voiceai"
echo "   5. View logs: sudo journalctl -u voiceai -f"
echo ""
echo "🌐 Server will be available at: http://your-ip:8000"
echo ""
echo "🔥 To start manually:"
echo "   source venv/bin/activate"
echo "   uvicorn src.server:app --host 0.0.0.0 --port 8000"
