# SentryView — RTSP NVR Dashboard

**Version:** v1.0  
**Status:** Active Development  
**Repository:** https://github.com/OneByJorah/SentryView

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [Service Management](#service-management)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

SentryView is a web-based RTSP NVR (Network Video Recorder) dashboard for live monitoring, playback, and timeline review of IP cameras. It combines a React frontend with a Python/FFmpeg backend, and includes Proxmox deployment support.

Designed for self-hosted surveillance setups where you want camera visibility without vendor lock-in.

---

## Architecture

Client browser → React frontend (`frontend/`) → Nginx → FastAPI backend (`backend/app.py`) → FFmpeg processor (`ffmpeg/processor.py`) → RTSP streams.

Additional capabilities:
- Proxmox container bootstrap (`proxmox/install-ct.sh`)
- Database init via `init-db.sql`
- Config via `backend/config.py`

---

## Technology Stack

| Layer | Stack |
|---|---|
| Runtime | Linux (Ubuntu 22.04+, Docker, Proxmox) |
| Frontend | React |
| Backend | Python / FastAPI |
| Media | FFmpeg (RTSP capture + processing) |
| Reverse Proxy | Nginx (`frontend/nginx.conf`) |
| Database | SQL (via `init-db.sql`) |
| VCS | Git + GitHub (`github.com/OneByJorah/SentryView`) |

---

## Features

- **Live monitoring**: multiple RTSP camera streams in one dashboard.
- **Playback + timeline**: review recorded segments by time.
- **Settings management**: stream and recording configuration UI.
- **FFmpeg pipeline**: hardware-friendly transcoding and processing container.
- **Proxmox-ready**: dedicated install script for container deployment.
- **Docker Compose**: multi-service deploy with backend, frontend, and ffmpeg.

---

## Getting Started

```bash
# 1. Clone
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView

# 2. Environment
cp .env.sample .env

# 3. Start with Docker Compose
docker compose up -d

# 4. Local frontend dev (optional)
cd frontend
npm install
npm start
```

---

## Service Management

```bash
# Start stack
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

---

## Project Structure

```
SentryView/
├── frontend/
│   ├── src/App.js, api.js, index.js
│   ├── public/index.html
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── ffmpeg/
│   ├── processor.py
│   └── requirements.txt
├── proxmox/
│   └── install-ct.sh
├── assets/
│   ├── banner.svg
│   ├── logo.svg
│   ├── screenshot-dashboard.png
│   ├── screenshot-settings.png
│   ├── screenshot-stream.png
│   └── screenshot-timeline.png
├── init-db.sql
├── docker-compose.yml
└── README.md
```

---

## Screenshots

### Dashboard
![Dashboard](assets/screenshot-dashboard.png)

### Stream
![Stream](assets/screenshot-stream.png)

### Timeline
![Timeline](assets/screenshot-timeline.png)

### Settings
![Settings](assets/screenshot-settings.png)

---

## Contributing

1. Create a feature branch off `main`.
2. Test RTSP playback end-to-end before submitting.
3. Submit a PR with description and screenshots for UI changes.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
