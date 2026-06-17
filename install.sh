#!/bin/bash
# ============================================
# RTSP NVR Dashboard - Installer Script v2.1
# ============================================
# Supports Ubuntu 20.04/22.04/24.04, Debian 11+
# Uses Docker Compose V2 (plugin)
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG()    { echo -e "${BLUE}[INFO]${NC} $1"; }
SUCCESS() { echo -e "${GREEN}[OK]${NC} $1"; }
WARN()   { echo -e "${YELLOW}[WARN]${NC} $1"; }
ERROR()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

[ "$EUID" -eq 0 ] || ERROR "Run as root: sudo ./install.sh"

INSTALL_DIR="/opt/SentryView"
TARGET_USER="${SUDO_USER:-root}"

LOG "RTSP NVR Dashboard v2.1 Installer"
LOG "==================================="

# ===== STEP 1: System dependencies =====
LOG "Step 1/7: Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq apt-transport-https ca-certificates curl gnupg lsb-release git ffmpeg > /dev/null 2>&1
SUCCESS "System dependencies installed"

# ===== STEP 2: Docker Engine =====
if command -v docker &>/dev/null; then
    SUCCESS "Docker already installed: $(docker --version)"
else
    LOG "Step 2/7: Installing Docker Engine..."
    # Download and review install script first
    curl -fsSL https://get.docker.com -o /tmp/docker-install.sh
    less /tmp/docker-install.sh || true
    bash /tmp/docker-install.sh > /dev/null 2>&1
    rm -f /tmp/docker-install.sh
    SUCCESS "Docker installed: $(docker --version)"
fi

# ===== STEP 3: Docker Compose V2 =====
if docker compose version &>/dev/null; then
    SUCCESS "Docker Compose V2 already installed: $(docker compose version)"
else
    LOG "Step 3/7: Installing Docker Compose V2..."
    apt-get install -y -qq docker-compose-plugin > /dev/null 2>&1
    SUCCESS "Docker Compose V2 installed: $(docker compose version)"
fi

# ===== STEP 4: Add user to docker group =====
if [ "$TARGET_USER" != "root" ]; then
    usermod -aG docker "$TARGET_USER" 2>/dev/null || true
    SUCCESS "Added '$TARGET_USER' to docker group"
fi

# ===== STEP 5: Clone/update repository =====
LOG "Step 5/7: Setting up repository..."
if [ -d "$INSTALL_DIR/.git" ]; then
    LOG "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || WARN "Git pull failed, using local files"
else
    git clone https://github.com/OneByJorah/SentryView.git "$INSTALL_DIR" 2>/dev/null || \
        ERROR "Failed to clone repository"
fi
SUCCESS "Repository ready at $INSTALL_DIR"

# ===== STEP 6: Environment configuration =====
LOG "Step 6/7: Configuring environment..."
cd "$INSTALL_DIR"

if [ ! -f .env ]; then
    # Generate secure random defaults
    SECRET=*** rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | head -1)
    JWT_SECRET=*** rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | head -1)
    DB_PASS=*** rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | xxd -p | head -1)

    cat > .env <<ENVEOF
# RTSP NVR Dashboard - Auto-generated config
# Generated: $(date -Iseconds)

# Database
DATABASE_URL=postgresql://admin:***@db:5432/rtsp_nvr
POSTGRES_PASSWORD=***

# Backend
SECRET_KEY=***
JWT_SECRET_KEY=***
BACKEND_URL=http://backend:5000

# Redis
REDIS_URL=redis://redis:6379

# Tailscale (optional)
TAILSCALE_API_KEY=
TAILSCALE_TAILNET_ID=
TAILSCALE_AUTH_KEY=

# Recording
AUDIO_THRESHOLD_DB=70
RETENTION_DAYS=7

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=5000
FFMPEG_PORT=8889

# Logging
LOG_LEVEL=INFO
ENVEOF
    chmod 600 .env
    SUCCESS ".env created with secure random keys"
    WARN "Edit .env to configure your RTSP stream URL"
else
    SUCCESS ".env already exists (not overwritten)"
fi

# ===== STEP 7: Build and start =====
LOG "Step 7/7: Building and starting services..."
docker compose build --no-cache 2>&1 | tail -5
SUCCESS "Images built"

docker compose up -d
SUCCESS "Services started"

# Wait for health checks
LOG "Waiting for services to become healthy..."
sleep 10

# Show status
echo ""
LOG "Service Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps

echo ""
SUCCESS "Installation complete!"
echo ""
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:3000"
echo -e "  ${GREEN}Backend:${NC}   http://localhost:5000"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:5000/api/docs"
echo -e "  ${GREEN}Health:${NC}    http://localhost:5000/health"
echo ""
echo -e "  ${YELLOW}Default login:${NC} admin / admin"
echo -e "  ${RED}Change the default password immediately!${NC}"
echo ""
echo -e "  ${BLUE}Logs:${NC}     docker compose logs -f"
echo -e "  ${BLUE}Stop:${NC}     docker compose down"
echo -e "  ${BLUE}Restart:${NC}  docker compose restart"
echo ""
