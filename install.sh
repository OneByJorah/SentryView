#!/bin/bash

# ============================================
# RTSP NVR Dashboard - Installer Script
# ============================================
# This script installs all dependencies and sets up the RTSP NVR Dashboard
# Supports Ubuntu 20.04/22.04, Debian 11+
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

SUCCESS() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

WARNING() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

ERROR() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check for sudo privileges
if [ "$EUID" -ne 0 ]; then
    ERROR "This script must be run as root"
    exit 1
fi

LOG "Starting RTSP NVR Dashboard installation..."
LOG "=========================================="

# ===== STEP 1: Update system =====
LOG "Step 1/8: Updating system packages..."
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# ===== STEP 2: Install Docker =====
LOG "Step 2/8: Installing Docker..."
curl -fsSL https://get.docker.com -sS | sh
usermod -aG docker $USER
systemctl enable docker
systemctl start docker

# ===== STEP 3: Install Docker Compose =====
LOG "Step 3/8: Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# ===== STEP 4: Install FFmpeg =====
LOG "Step 4/8: Installing FFmpeg..."
apt-get install -y ffmpeg

# ===== STEP 5: Install Git =====
LOG "Step 5/8: Installing Git..."
apt-get install -y git

# ===== STEP 6: Clone repository =====
LOG "Step 6/8: Cloning repository..."
cd /opt
git clone https://github.com/OneByJorah/rtsp-nvr-dashboard.git
cd rtsp-nvr-dashboard

# ===== STEP 7: Setup environment =====
LOG "Step 7/8: Setting up environment..."

# Create .env from sample
cp .env.sample .env

# Edit .env with nano (or ask user to edit manually)
echo ""
echo -e "${YELLOW}Please configure your RTSP stream URL and other settings:${NC}"
echo -e "${YELLOW}   nano /opt/rtsp-nvr-dashboard/.env${NC}"
echo ""
read -p "Press Enter when done editing, or skip to continue..."

# ===== STEP 8: Build and start =====
LOG "Step 8/8: Building and starting services..."

# Build images
docker compose build

# Start services
docker compose up -d

# Check status
sleep 5
docker compose ps

echo ""
SUCCESS "Installation complete!"
echo ""
echo -e "${GREEN}Services:${NC}"
echo -e "  Frontend:  http://localhost:3000"
echo -e "  Backend:   http://localhost:5000"
echo -e "  FFmpeg:    localhost:8889"
echo ""
echo -e "${YELLOW}Default credentials:${NC}"
echo -e "  Username: admin"
echo -e "  Password: admin"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Configure /opt/rtsp-nvr-dashboard/.env with your RTSP URL"
echo -e "  2. View logs: docker compose logs -f"
echo -e "  3. Stop services: docker compose down"
echo ""

# ===== OPTIONAL: Tailscale Setup =====
if command -v docker &> /dev/null; then
    LOG "Tailscale setup (optional):"
    LOG "  1. Install Tailscale: sudo apt install tailscale"
    LOG "  2. Login: sudo tailscale up"
    LOG "  3. Access dashboard via Tailscale IP: http://<tailscale-ip>:3000"
    echo ""
fi

# ===== ADD USER TO DOCKER GROUP =====
echo -e "${YELLOW}Adding user to docker group for local access:${NC}"
read -p "Username? " username
usermod -aG docker $username
echo -e "${GREEN}Done!${NC}"

echo ""
SUCCESS "RTSP NVR Dashboard is now running!"
echo ""
