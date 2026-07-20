<div align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</div>

<br>

<div align="center">
  <h1>📹 SentryView</h1>
  <p><strong>Web-Based RTSP NVR Dashboard</strong></p>
  <p>Self-hosted surveillance — live monitoring, playback, and timeline review for IP cameras</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-stream-processing">Stream Processing</a>
  </p>
</div>

---

## 📸 Screenshot

This is a CLI/backend-only tool. No screenshots available.

## ✨ Features

- **Live Monitoring** — Real-time RTSP stream viewing from IP cameras
- **Timeline Playback** — Review recorded footage with timeline scrubber
- **Recording** — Automated recording of RTSP streams
- **Vendor Agnostic** — Works with any RTSP-compatible IP camera
- **React Frontend** — Modern reactive UI with video players
- **FastAPI Backend** — High-performance async Python backend
- **FFmpeg Processing** — Industry-standard stream handling
- **Docker Deploy** — Complete containerized solution

## 🚀 Quick Start

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView
./install.sh
```

Or with Docker:
```bash
docker-compose up -d
```

## 🏗️ Architecture

```
SentryView/
├── frontend/                  # React SPA
├── backend/                   # FastAPI server
├── ffmpeg/                    # FFmpeg stream processing
├── assets/                    # Static assets
├── scripts/                   # Utility scripts
├── proxmox/                   # Proxmox integration
├── init-db.sql                # Database initialization
├── Dockerfile.backend         # Backend container
├── docker-compose.yml         # Full deployment
└── install.sh                 # Installation script
```

## 🔧 Stream Processing

SentryView uses FFmpeg to:
- Transcode RTSP streams for browser playback
- Record segments for timeline review
- Generate thumbnails and preview clips
- Support multiple codec formats (H.264, H.265)

## 📄 License

MIT © Jhonattan L. Jimenez / JorahOne LLC

---

<div align="center">
  <p>📹 Your cameras, self-hosted</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
