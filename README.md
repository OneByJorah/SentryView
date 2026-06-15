# 📡 RTSP NVR Dashboard

[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintained by OneByJorah](https://img.shields.io/badge/Maintained%20by-OneByJorah-1E90FF?logo=github)](https://github.com/OneByJorah)

---

## 📋 Overview

**RTSP NVR Dashboard** is a modern, cyber-themed Network Video Recorder dashboard for monitoring and managing RTSP camera streams. Features real-time video monitoring, audio-triggered recording, event scheduling, and a responsive web interface — all containerized with Docker for easy deployment.

> **Built with ❤️ by [OneByJorah](https://github.com/OneByJorah)**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎥 **Live Stream Dashboard** | Monitor multiple RTSP camera feeds in real-time |
| 🔊 **Audio-Triggered Recording** | Auto-record when audio exceeds configurable dB threshold |
| 📅 **Event Timeline** | View and filter recordings by type (motion, audio, scheduled) |
| ⏰ **Scheduled Recordings** | Create and manage recording schedules |
| 🎨 **Cyber Theme UI** | Futuristic CRT scanline effects and dark interface |
| 🔐 **Authentication** | Secure access with admin/user roles |
| 🧹 **Auto-Cleanup** | Automatic removal of old recordings per retention policy |
| 📊 **System Stats** | Monitor CPU, memory, and disk usage |
| 🛠️ **FFmpeg Integration** | Stream transcoding and processing |

---

## 🖼️ Screenshots

| Dashboard | Stream Player | Timeline | Settings |
|-----------|--------------|----------|----------|
| ![Dashboard](assets/screenshot-dashboard.png) | ![Stream](assets/screenshot-stream.png) | ![Timeline](assets/screenshot-timeline.png) | ![Settings](assets/screenshot-settings.png) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │    FFmpeg    │  │
│  │   (React)    │──│   (Flask)    │──│  Processor   │  │
│  │   Port 3000  │  │   Port 5000  │  │   Port 8889  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                     RTSP Camera Streams                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
rtsp-nvr-dashboard/
├── docker-compose.yml        # Service orchestration
├── install.sh                # Ubuntu installer script
├── .env.sample               # Configuration template
├── .gitignore                # Git ignore rules
├── Dockerfile.backend        # Backend container definition
├── frontend/                 # React frontend
│   ├── Dockerfile           # Frontend container
│   ├── nginx.conf           # Nginx reverse proxy config
│   ├── package.json         # Node.js dependencies
│   ├── public/              # Static assets
│   └── src/                 # React components
├── backend/                  # Flask backend
│   ├── Dockerfile           # Backend container
│   ├── app.py               # Main application
│   └── requirements.txt     # Python dependencies
├── ffmpeg/                   # FFmpeg processor
│   ├── Dockerfile           # FFmpeg container
│   ├── processor.py         # Stream processing logic
│   └── requirements.txt     # Python dependencies
└── assets/                   # Screenshots and banners
```

---

## 📋 Prerequisites

| Requirement | Details |
|-------------|---------|
| **OS** | Ubuntu 20.04/22.04, Debian 11+, or any Docker-capable Linux |
| **Docker** | Docker Engine 20.10+ and Docker Compose V2 |
| **RAM** | Minimum 2GB (4GB recommended) |
| **Network** | Access to RTSP camera streams |
| **Ports** | 3000 (frontend), 5000 (backend), 8889 (FFmpeg) |

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/OneByJorah/rtsp-nvr-dashboard.git
cd rtsp-nvr-dashboard
```

### 2. Run the Installer

```bash
# Installs Docker, dependencies, and builds images
chmod +x install.sh
./install.sh
```

### 3. Configure RTSP Streams

```bash
cp .env.sample .env
nano .env
```

### 4. Start All Services

```bash
docker compose up -d
```

### 5. Access the Dashboard

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:5000 |
| **API Docs** | http://localhost:5000/docs |

### Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin` |

> ⚠️ **Change the default credentials immediately after first login!**

---

## 🔧 Configuration

Edit the `.env` file to customize:

```bash
# RTSP Stream Configuration
RTSP_URL=rtsp://username:password@192.168.1.100:554/stream

# Recording Settings
AUDIO_THRESHOLD_DB=70        # dB threshold for audio-triggered recording
RETENTION_DAYS=7             # Days to keep recordings/events

# System Settings
FRONTEND_PORT=3000
BACKEND_PORT=5000
FFMPEG_PORT=8889
```

### Multiple Cameras

Add multiple RTSP URLs separated by commas:

```bash
RTSP_URL=rtsp://user:pass@192.168.1.100:554/stream,rtsp://user:pass@192.168.1.101:554/stream
```

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login and receive session token |
| `POST` | `/api/auth/logout` | Logout and invalidate session |
| `GET` | `/api/auth/me` | Get current user info |

### Streams

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/streams` | List all configured streams |
| `POST` | `/api/streams` | Add a new RTSP stream |
| `DELETE` | `/api/streams/<id>` | Remove a stream |

### Recordings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recordings` | List all recordings |
| `POST` | `/api/recordings` | Start a recording |
| `DELETE` | `/api/recordings/<id>` | Stop a recording |

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events` | List all events |
| `GET` | `/api/events?type=audio` | Filter events by type |
| `POST` | `/api/events` | Create a manual event |

### Schedules

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/schedules` | List all schedules |
| `POST` | `/api/schedules` | Create a new schedule |
| `DELETE` | `/api/schedules/<id>` | Delete a schedule |

---

## 🐳 Docker Commands

```bash
# Build all images
docker compose build

# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend

# Restart a service
docker compose restart backend

# Check service status
docker compose ps
```

---

## 🛠️ Development

### Frontend

```bash
cd frontend
npm install
npm start          # Development server at http://localhost:3000
npm run build      # Production build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5000
```

### FFmpeg Processor

```bash
cd ffmpeg
pip install -r requirements.txt
python processor.py
```

---

## 🔒 Security

- Password authentication required for all dashboard access
- Session management with configurable timeout
- Secure RTSP stream access (credentials in `.env`, not hardcoded)
- CORS protection on API endpoints
- Input validation on all API routes
- **Change default credentials immediately**

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No video stream | Verify RTSP URL and camera accessibility |
| High CPU usage | Reduce stream resolution or frame rate |
| Disk filling up | Lower `RETENTION_DAYS` or increase threshold |
| Port conflict | Change ports in `.env` and `docker-compose.yml` |
| Container won't start | Check logs: `docker compose logs <service>` |
| Audio trigger not working | Verify microphone/audio input on camera |

---

## 🔄 Updates

```bash
cd /path/to/rtsp-nvr-dashboard
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 📞 Support

For issues or questions, please open an issue on GitHub:

https://github.com/OneByJorah/rtsp-nvr-dashboard/issues

---

**Made with ❤️ by [OneByJorah](https://github.com/OneByJorah)**
