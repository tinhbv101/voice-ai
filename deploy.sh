#!/bin/bash

# VoiceAI Deployment Script

set -e

echo "🚀 VoiceAI Deployment Script"
echo "=============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy env.example to .env and configure your API keys"
    echo "  cp env.example .env"
    exit 1
fi

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
}

# Function to check Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
}

# Parse arguments
MODE=${1:-dev}

echo ""
echo "Deployment mode: $MODE"
echo ""

# Check requirements
check_docker
check_docker_compose

# Build and deploy based on mode
if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
    echo -e "${YELLOW}Deploying in PRODUCTION mode...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
elif [ "$MODE" = "dev" ] || [ "$MODE" = "development" ]; then
    echo -e "${YELLOW}Deploying in DEVELOPMENT mode...${NC}"
    docker-compose build
    docker-compose up -d
else
    echo -e "${RED}Invalid mode: $MODE${NC}"
    echo "Usage: ./deploy.sh [dev|prod]"
    exit 1
fi

# Wait for service to be ready
echo ""
echo -e "${YELLOW}Waiting for service to be ready...${NC}"
sleep 5

# Check health
if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✓ Service is healthy!${NC}"
else
    echo -e "${RED}✗ Service health check failed${NC}"
    echo "Check logs: docker-compose logs -f"
    exit 1
fi

echo ""
echo -e "${GREEN}=============================="
echo "✓ Deployment successful!"
echo "=============================="
echo ""
echo "Access the application at: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f    - View logs"
echo "  docker-compose ps         - Check status"
echo "  docker-compose down       - Stop services"
echo "  docker-compose restart    - Restart services"
echo ""
