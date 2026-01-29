# VoiceAI Deployment Guide 🐳

Complete guide to deploy VoiceAI with Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM
- 5GB disk space (for models)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /path/to/voiceai

# Copy environment file
cp env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your API keys (see env.example for all options).

### 3. Build and Run

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f voiceai
```

### 4. Access the Application

Open browser: http://localhost:8000

## 🛠️ Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Update and rebuild
git pull && docker-compose build && docker-compose up -d
```

## 🔧 Configuration

Volume mounts:
- `./src` → Source code (hot reload)
- `./static` → Static files
- `./audio_output` → Generated audio
- `./models` → Cached STT models

## 🐛 Troubleshooting

Check logs: `docker-compose logs -f`
Check health: `curl http://localhost:8000/health`
