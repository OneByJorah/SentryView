#!/usr/bin/env bash
#=====================================================================
#  RTSP NVR Dashboard - Complete Installer for Ubuntu
#  Builds and deploys the complete dashboard stack
#=====================================================================
#  What the script does
#   1️⃣  Install APT prerequisites
#   2️⃣  Install Docker and Docker Compose
#   3️⃣  Clone/update the dashboard repo
#   4️⃣  Create .env configuration
#   5️⃣  Build all Docker images
#   6️⃣  Start the complete stack
#=====================================================================

set -euo pipefail
IFS=$'\n\t'

# ---------- Helper output ----------
log()   { echo -e "\033[1;33m📦\033[0m  $*"; }
ok()    { echo -e "\033[1;32m✅\033[0m  $*"; }
warn()  { echo -e "\033[1;31m⚠️\033[0m  $*"; }
info()  { echo -e "\033[1;34mℹ️\033[0m  $*"; }

# ---------- 1 – Detect Ubuntu / Debian codename ----------
log "Detecting distribution..."
if command -v lsb_release >/dev/null 2>&1; then
    UBUNTU_CODENAME=$(lsb_release -cs)
else
    . /etc/os-release
    UBUNTU_CODENAME=$VERSION_CODENAME
fi

if [[ "$UBUNTU_CODENAME" == "noble" ]]; then
    warn "Running on Ubuntu 'noble' (development). Switching apt sources to jammy."
    UBUNTU_CODENAME="jammy"
fi
log "Using apt codename: $UBUNTU_CODENAME"

# ---------- 2 – Install APT prerequisites ----------
log "Updating APT index..."
apt-get -o Acquire::ForceIPv4=true update -y

log "Installing required packages..."
apt-get -o Acquire::ForceIPv4=true install -y \
    ca-certificates curl gnupg lsb-release software-properties-common git build-essential

# ---------- 3 – Docker Engine ----------
log "Setting up Docker repository..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

log "Installing Docker Engine..."
apt-get -o Acquire::ForceIPv4=true update -y
apt-get -o Acquire::ForceIPv4=true install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

# ---------- 4 – Clone / update the dashboard ----------
TARGET_DIR="/opt/rtsp-nvr-dashboard"
log "Preparing $TARGET_DIR"

if [[ -d "$TARGET_DIR/.git" ]]; then
    ok "Repository already exists → pulling the latest"
    pushd "$TARGET_DIR" > /dev/null
    git fetch --all
    git reset --hard origin/main
    popd > /dev/null
else
    ok "Cloning fresh copy of the dashboard"
    git clone https://github.com/OneByJorah/rtsp-nvr-dashboard.git "$TARGET_DIR"
fi

# ---------- 5 – Create .env ----------
cd "$TARGET_DIR"

if [[ -f .env ]]; then
    ok ".env already exists – leaving untouched."
elif [[ -f .env.sample ]]; then
    cp .env.sample .env
    ok "Copied .env.sample → .env"
else
    info "Creating minimal .env..."
    cat > .env <<EOF
# RTSP NVR Dashboard Configuration
HOST_IP=0.0.0.0
NVR_URL=rtsp://admin:admin@192.168.1.10:554/stream
ADMIN_USER=admin
ADMIN_PASSWORD=your_password_here
AUDIO_THRESHOLD_DB=30
RECORDING_RETENTION_DAYS=7
MAX_RECORDINGS=10
EOF
    ok ".env file created."
fi

info "Please edit .env with your RTSP URL and settings (Ctrl+X to keep)"
if command -v nano >/dev/null 2>&1; then
    nano .env
else
    ${EDITOR:-vi} .env
fi

# ---------- 6 – Build Docker images ----------
log "Building Docker images..."

# Build backend
log "Building backend image..."
docker compose -f docker-compose.yml build backend

# Build frontend
log "Building frontend image..."
docker compose -f docker-compose.yml build frontend

# Build FFmpeg
log "Building FFmpeg processor image..."
docker compose -f docker-compose.yml build ffmpeg

ok "All images built successfully."

# ---------- 7 – Start the stack ----------
log "Starting the RTSP NVR Dashboard..."
docker compose -f docker-compose.yml up -d

# ---------- 8 – Final status ----------
log "Waiting for containers to initialize..."
sleep 5

log "Current container status:"
docker compose -f docker-compose.yml ps

# ---------- 9 – Summary ----------
ok "=============================================================="
ok "✅  RTSP NVR Dashboard installation complete!"
ok "=============================================================="
ok ""
ok "🌐 Access the dashboard at:   http://0.0.0.0:3000"
ok "🔑 Default credentials:      admin / (set in .env)"
ok ""
ok "📋 Useful commands:"
ok "   View logs:   docker compose -f docker-compose.yml logs -f"
ok "   Stop:        docker compose -f docker-compose.yml down"
ok "   Restart:     docker compose -f docker-compose.yml restart"
ok "=============================================================="
