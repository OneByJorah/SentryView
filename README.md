# SentryView

Self-hosted RTSP NVR dashboard — live monitoring, recording, and timeline review for IP cameras (Flask + React).

![status](https://img.shields.io/badge/status-active-FFB300?style=flat-square)
![language](https://img.shields.io/badge/python+react-0d0d0c?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)

## Overview

SentryView is a self-hosted Network Video Recorder dashboard for IP cameras. It provides live RTSP stream monitoring, automated recording, and timeline-based playback through a modern React frontend backed by a FastAPI async Python server. Works with any RTSP-compatible camera — no vendor lock-in.

## Features

- Live RTSP stream viewing from multiple IP cameras simultaneously
- Timeline playback with scrubber for reviewing recorded footage
- Automated recording of RTSP streams to local storage
- Vendor-agnostic — works with any RTSP-compatible IP camera
- React SPA frontend with responsive design
- FastAPI async Python backend for high-performance stream handling
- FFmpeg-based stream processing (industry standard)
- Docker Compose deployment with health checks
- Proxmox LXC deployment scripts included

## Architecture / Tech Stack

- **Frontend**: React SPA, video players
- **Backend**: FastAPI (Python async)
- **Stream Processing**: FFmpeg
- **Database**: SQLite (init-db.sql)
- **Deployment**: Docker Compose, Proxmox LXC
- **Network**: Isolated Docker network for camera traffic

## Installation

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView

# Option 1: Automated install
./install.sh

# Option 2: Docker Compose
docker compose up -d
```

## Usage

1. Add your RTSP camera streams via the dashboard or API
2. Open the web UI at `http://localhost:3000`
3. Monitor live feeds, record, and review timeline footage

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_PORT` | `3000` | Web UI port |
| `BACKEND_PORT` | `5000` | API server port |
| `BACKEND_URL` | `http://backend:5000` | Internal API URL |

See `.env.example` for full options.

## License

MIT — see [LICENSE](LICENSE).

---
Part of the JorahOne / J1 ecosystem — self-hosted surveillance for VIDE OIT infrastructure.
