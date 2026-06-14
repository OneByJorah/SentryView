# 📡 RTSP NVR Dashboard

A modern, cyber-themed Network Video Recorder dashboard for monitoring and managing RTSP camera streams.

![Cyber Theme Banner](assets/banner.svg)

## ✨ Features

- 🎥 **Live Stream Dashboard** - Monitor multiple RTSP camera feeds in real-time
- 🔊 **Audio-Triggered Recording** - Automatically record when audio exceeds configurable dB threshold
- 📅 **Event Timeline** - View and filter recordings by type (motion, audio, scheduled)
- ⏰ **Scheduled Recordings** - Create and manage recording schedules
- 🎨 **Cyber Theme UI** - Futuristic CRT scanline effects and dark interface
- 🔐 **Authentication** - Secure access with admin/user roles
- 🧹 **Auto-Cleanup** - Automatically removes old recordings and events based on retention policy
- 📊 **System Stats** - Monitor CPU, memory, and disk usage
- 🛠️ **FFmpeg Integration** - Stream transcoding and processing

## 🖼️ Screenshots

### Dashboard View
![Dashboard Screenshot](assets/screenshot-dashboard.png)

### Video Stream Player
![Stream Screenshot](assets/screenshot-stream.png)

### Event Timeline
![Timeline Screenshot](assets/screenshot-timeline.png)

### Settings Panel
![Settings Screenshot](assets/screenshot-settings.png)

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04/22.04 or Debian 11+
- Docker and Docker Compose
- At least 2GB RAM
- Network access to RTSP streams

### Installation

```bash
# Clone the repository
git clone https://github.com/OneByJorah/rtsp-nvr-dashboard.git
cd rtsp-nvr-dashboard

# Run the installer (installs Docker, dependencies, builds images)
./install.sh

# Configure your RTSP streams
nano .env

# Build and start all services
docker compose up -d

# Access the dashboard
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Default Credentials
- **Username**: admin
- **Password**: admin
- *(Change in Settings panel)*

## 🔧 Configuration

Edit the `.env` file to customize:

```bash
# RTSP Stream Configuration
RTSP_URL=http://username:password@192.168.1.100:554/stream

# Recording Settings
AUDIO_THRESHOLD_DB=70        # dB threshold for audio-triggered recording
RETENTION_DAYS=7            # Days to keep recordings/events

# System Settings
FRONTEND_PORT=3000
BACKEND_PORT=5000
FFMPEG_PORT=8889
```

## 📁 Project Structure

```
rtsp-nvr-dashboard/
├── docker-compose.yml    # Service orchestration
├── install.sh           # Ubuntu installer script
├── .env.sample          # Configuration template
├── .gitignore           # Git ignore rules
├── frontend/            # React frontend
│   ├── Dockerfile      # Frontend container
│   ├── nginx.conf      # Nginx reverse proxy config
│   ├── package.json    # Node.js dependencies
│   ├── public/         # Static assets
│   └── src/            # React components
├── backend/             # Flask backend
│   ├── Dockerfile      # Backend container
│   ├── app.py          # Main application
│   └── requirements.txt # Python dependencies
└── ffmpeg/              # FFmpeg processor
    ├── Dockerfile      # FFmpeg container
    ├── processor.py    # Stream processing logic
    └── requirements.txt
```

## 🎨 Features Detail

### Live Stream Dashboard
- Real-time video feed from RTSP streams
- Multiple camera support
- Stream quality control
- Connection status indicators

### Audio-Triggered Recording
- Configurable audio sensitivity (dB threshold)
- Automatic recording initiation
- Recording status indicators
- Event logging

### Event Timeline
- Chronological event list
- Filter by event type:
  - 🟢 **Recording Started**
  - 🔴 **Recording Stopped**
  - 🟡 **Motion Detected**
  - 🔊 **Audio Exceeded**
- Click events to view details
- Export functionality (planned)

### Scheduled Recordings
- Create recurring schedules
- Set time ranges
- Choose recording sources
- Manage existing schedules

### System Monitoring
- CPU usage graphs
- Memory usage charts
- Disk space monitoring
- Service health status

## 🔒 Security

- Password authentication required
- Session management
- Secure RTSP stream access
- CORS protection
- Input validation

## 🛠️ Development

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### FFmpeg Processor
```bash
cd ffmpeg
python processor.py
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Current user

### Streams
- `GET /api/streams` - List streams
- `POST /api/streams` - Add stream
- `DELETE /api/streams/<id>` - Remove stream

### Recordings
- `GET /api/recordings` - List recordings
- `POST /api/recordings` - Start recording
- `DELETE /api/recordings/<id>` - Stop recording

### Events
- `GET /api/events` - List events
- `GET /api/events?type=audio` - Filter events
- `POST /api/events` - Create event

### Schedules
- `GET /api/schedules` - List schedules
- `POST /api/schedules` - Create schedule
- `DELETE /api/schedules/<id>` - Delete schedule

## 🐳 Docker Commands

```bash
# Build all images
docker compose build

# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart backend
docker compose restart backend
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ by [OneByJorah](https://github.com/OneByJorah)**
