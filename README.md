<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black">
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</div>

<br>

<div align="center">
  <h1>SentryView</h1>
  <p><strong>Self-Hosted RTSP NVR Dashboard</strong></p>
  <p>Live monitoring, recording, and timeline review for IP cameras.</p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## Screenshot

![SentryView Dashboard](docs/screenshot.png)
*RTSP NVR dashboard with live camera feeds and timeline playback.*

## Features

- **Live Monitoring** — Real-time RTSP stream viewing with low-latency playback.
- **Recording** — Automated and on-demand camera recording with FFmpeg.
- **Timeline Review** — Scrub through recorded footage with timeline navigation.
- **Multi-Camera** — Support for unlimited IP cameras via RTSP.
- **Motion Detection** — Configurable motion detection zones and alerts.
- **Storage Management** — Disk usage monitoring and retention policies.
- **React Dashboard** — Modern, responsive web interface.
- **FastAPI Backend** — Async Python backend with WebSocket updates.

## Quick Start

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView

cp .env.example .env  # Configure camera streams
docker compose up -d
```

Open **http://localhost:8000** in your browser.

### Adding Cameras

1. Navigate to **Settings → Cameras**
2. Click **Add Camera**
3. Enter RTSP URL: `rtsp://username:password@camera-ip:554/stream`
4. Configure recording settings
5. Save and view live feed

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Backend API port |
| `DATABASE_URL` | `sqlite:///sentryview.db` | Database connection string |
| `RECORDINGS_DIR` | `./recordings` | Storage directory for recordings |
| `MAX_STORAGE_GB` | `100` | Maximum storage allocation |
| `RETENTION_DAYS` | `30` | Days to keep recordings |
| `MOTION_THRESHOLD` | `30` | Motion detection sensitivity |

## Architecture

```
Browser (React) ──API/WebSocket──▶ FastAPI Backend ──▶ SQLite
                                        │
                                        ├──▶ FFmpeg ──▶ RTSP Cameras
                                        ├──▶ Recording Engine
                                        ├──▶ Motion Detection
                                        └──▶ Storage Manager
```

## Tech Stack

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy
- **Frontend**: React 18 (TypeScript)
- **Video**: FFmpeg for RTSP stream processing
- **Database**: SQLite (default), PostgreSQL (production)
- **Deployment**: Docker Compose

## Supported Camera Types

| Protocol | Compatibility |
|----------|---------------|
| **RTSP** | All ONVIF-compatible cameras |
| **RTMP** | Most IP cameras and DVRs |
| **HLS** | Streaming services |

## Project Structure

```
SentryView/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── routers/
│   │   ├── cameras.py       # Camera management
│   │   ├── streams.py       # Live stream endpoints
│   │   ├── recordings.py    # Recording management
│   │   └── timeline.py      # Timeline navigation
│   ├── services/
│   │   ├── ffmpeg_service.py    # FFmpeg wrapper
│   │   ├── motion_detect.py     # Motion detection
│   │   └── storage_manager.py   # Disk management
│   └── models.py            # Database models
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── pages/           # Dashboard pages
│   └── package.json
├── recordings/              # Video storage (gitignored)
├── docker-compose.yml       # Docker deployment
└── .env.example             # Configuration template
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cameras` | GET/POST | Manage cameras |
| `/api/cameras/{id}/stream` | GET | Get live RTSP stream |
| `/api/recordings` | GET | List recordings |
| `/api/recordings/{id}/download` | GET | Download recording |
| `/api/timeline/{camera_id}` | GET | Get timeline data |
| `/api/storage` | GET | Storage usage stats |

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## Security

For security concerns, see [SECURITY.md](SECURITY.md). Please report vulnerabilities to **info@jorahone.com** — do not use public issues.

## License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>Self-hosted NVR for IP camera monitoring.</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
