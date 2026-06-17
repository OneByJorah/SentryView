# RTSP NVR Dashboard

[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-blue.svg)](https://github.com/OneByJorah/SentryView)
[![Maintained by OneByJorah](https://img.shields.io/badge/Maintained%20by-OneByJorah-1E90FF?logo=github)](https://github.com/OneByJorah)

![RTSP NVR Dashboard Architecture](https://v3b.fal.media/files/b/0a9e59a6/3Cq6QvN0Qw5qZ7H7vJ0uK4yD9c0g8a.png)

> **RTSP NVR Dashboard**: Modern web-based RTSP NVR dashboard for Linux with **audio + video streaming**, **event-based recording**, **timeline playback**, and **volume-triggered audio capture**. Built for **home labs, MSPs, security engineers, and Proxmox users** who want full control without vendor lock-in.

---

## 📋 Overview

**RTSP NVR Dashboard** is a modern, cyber-themed Network Video Recorder dashboard for monitoring and managing RTSP camera streams. Features real-time video monitoring, audio-triggered recording, event scheduling, and a responsive web interface - all containerized with Docker for easy deployment.

> Built with love by [OneByJorah](https://github.com/OneByJorah)

---

## 🏗️ Architecture

### High-Level System Architecture

```mermaid
flowchart TB
    subgraph Frontend["Web UI / API"]
        WEB[Web Interface<br/>Flask + HTML/CSS/JS]
        API[REST API<br/>Flask Blueprint]
    end

    subgraph Services["Core Services"]
        VIDEO[Video Streaming<br/>RTSP + HLS + WebRTC]
        AUDIO[Audio Capture<br/>Real-time Audio Analysis]
        REC[Recording Engine<br/>Event-based Recording]
        PLAY[Playback Engine<br/>Timeline Navigation]
        ALERT[Alert System<br/>Motion + Sound Detection]
    end

    subgraph Storage["Storage Layer"]
        DB[(SQLite<br/>Config + Metadata)]
        CACHE[(Redis<br/>Real-time Status)]
        STORAGE[(Local Storage<br/>Recordings + Archives)]
    end

    subgraph Integration["Integrations"]
        AI[AI Analytics<br/>Object Detection + Recognition]
        MSG[Telegram Bot<br/>Alert Notifications]
        SLACK[Slack Alerts<br/>Incident Mgmt]
    end

    subgraph Security["Security"]
        AUTH[Authentication<br/>JWT + Session]
        SSL[SSL/TLS<br/>Let's Encrypt]
    end

    WEB <--> API
    API <--> VIDEO
    API <--> AUDIO
    API <--> REC
    API <--> PLAY
    API <--> ALERT
    VIDEO <--> STORAGE
    AUDIO <--> STORAGE
    REC <--> STORAGE
    PLAY <--> STORAGE
    ALERT <--> STORAGE
    ALERT <--> AI
    MSG <--> API
    SLACK <--> API
    AUTH <--> DB

    style Frontend fill:#1a237e,stroke:#3f51b5,stroke-width:2px,color:#ffffff
    style Services fill:#2e7d32,stroke:#4caf50,stroke-width:2px,color:#ffffff
    style Storage fill:#e65100,stroke:#ff9800,stroke-width:2px,color:#ffffff
    style Integration fill:#4a148c,stroke:#9c27b0,stroke-width:2px,color:#ffffff
    style Security fill:#c62828,stroke:#e53935,stroke-width:2px,color:#ffffff
```

---

## 🖼️ Screenshots

<div align="center">

### Dashboard Overview
![Dashboard](docs/dashboard.png)
*Main dashboard showing all camera feeds, system status, and quick actions*

---

### Live Camera Feed
![Camera Feed](docs/camera-feed.png)
*Real-time RTSP video stream with overlay controls and audio visualization*

---

### Timeline Playback
![Timeline](docs/timeline.png)
*Timeline-based playback with event markers, recording segments, and search*

---

### Audio Analysis
![Audio](docs/audio.png)
*Real-time audio analysis with volume-triggered detection and event capture*

---

### Event Log
![Event Log](docs/events.png)
*Event log with motion detection, sound alerts, and recording triggers*

---

### Camera Configuration
![Config](docs/config.png)
*Camera configuration with RTSP settings, recording rules, and audio thresholds*

</div>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎥 **RTSP Video Streaming** | Full-featured RTSP video streaming with HLS fallback, WebRTC support, and adaptive bitrate |
| 🎙️ **Real-time Audio Capture** | Simultaneous audio capture with real-time analysis, volume triggering, and audio event logging |
| 📋 **Event-based Recording** | Automated recording triggered by motion detection, sound alerts, or time schedules |
| 🎞️ **Timeline Playback** | Professional timeline-based playback with event markers, search, and annotation support |
| 🔊 **Volume Triggered Detection** | Audio analytics with configurable volume thresholds, event capture, and audio clipping |
| 🔔 **Alert System** | Multi-channel alerting with Telegram bot, Slack integration, email notifications, and push alerts |
| 🎮 **Playback Controls** | Advanced playback controls with variable speed, frame-by-frame navigation, and bookmarking |
| 📊 **System Monitoring** | Real-time system monitoring with disk usage, network traffic, and recording status |

---

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView

# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Initialize admin user
python manage.py init-admin
```

### Configuration

Edit `config/settings.py`:

```python
# Server
SERVER_NAME = 'rtsp-nvr.local'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database
DATABASE_URL = 'sqlite:///nvr.db'

# Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:***@192.168.1.100:554/stream'},
    {'id': 2, 'name': 'Backyard', 'rtsp': 'rtsp://camera2:password@192.168.1.101:554/stream'},
    {'id': 3, 'name': 'Parking Lot', 'rtsp': 'rtsp://camera3:password@192.168.1.102:554/stream'},
]

# Recording
RECORDING_ENABLED = True
RECORDING_SCHEDULE = '0 0 * * *'  # Daily at midnight
AUDIO_THRESHOLD = 5000  # Volume threshold in dB
AUDIO_EVENT_DURATION = 3  # Event duration in seconds
```

### Running the Application

```bash
# Development
flask run --host=0.0.0.0 --port=5000

# Production
gunicorn --workers=4 --bind=0.0.0.0:5000 --timeout=120 app:create_app()
```

### Accessing the Web UI

```
http://localhost:5000
```

---

## 🔍 API Reference

### Base URL

```
http://localhost:5000/api/v1
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cameras` | GET | List all cameras |
| `/api/v1/cameras/<id>` | GET | Get camera details |
| `/api/v1/cameras/<id>` | PUT | Update camera settings |
| `/api/v1/cameras/<id>` | DELETE | Delete camera |
| `/api/v1/cameras/<id>/stream` | GET | Get camera stream URL |
| `/api/v1/audio/threshold` | GET | Get audio threshold |
| `/api/v1/audio/threshold` | PUT | Update audio threshold |
| `/api/v1/audio/events` | GET | List audio events |
| `/api/v1/recordings` | GET | List recordings |
| `/api/v1/recordings/<id>` | GET | Get recording details |
| `/api/v1/recordings/<id>` | DELETE | Delete recording |
| `/api/v1/playback` | POST | Start playback |
| `/api/v1/playback/stop` | POST | Stop playback |
| `/api/v1/events` | GET | List events |
| `/api/v1/events/<id>` | GET | Get event details |
| `/api/v1/health` | GET | System health check |

---

## 📊 Monitoring

### System Health

```bash
# Check service status
sudo systemctl status nvr

# Check database connection
sqlite3 /var/lib/nvr/nvr.db "SELECT 1"

# Check Redis
redis-cli ping
```

### Logs

```bash
# Application logs
sudo tail -f /var/log/nvr/app.log

# Recording logs
sudo tail -f /var/log/nvr/recording.log
```

---

## 🔒 Security

### Network Security

- RTSP over TLS (RTSPS) with certificate verification
- Session-based authentication with JWT tokens
- Rate limiting on API endpoints

### Authentication

- Session-based authentication with Flask-Login
- JWT tokens for API access
- Role-based access control (RBAC)

---

## 📚 Dependencies

### Python

```
Flask>=3.0.0
Flask-SQLAlchemy>=3.0.0
Flask-Migrate>=3.1.0
Flask-CORS>=4.0.0
Flask-Login>=0.6.0
PyYAML>=6.0
opencv-python>=4.5.0
numpy>=1.21.0
pillow>=9.0.0
redis>=4.5.0
```

### System Dependencies

```
ffmpeg>=5.0
librtsp>=1.0
libavcodec>=5.0
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

https://github.com/OneByJorah/SentryView/issues

---

## 🙏 Acknowledgments

- **Flask**: Web framework by Armin Ronacher
- **OpenCV**: Computer vision library by Intel

---

**Made with ❤️ by [OneByJorah](https://github.com/OneByJorah)**
