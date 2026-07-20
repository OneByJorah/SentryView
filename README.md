# 🔧 SentryView
### Self-hosted RTSP NVR dashboard — live monitoring, recording, and timeline review for IP cameras

SentryView is a Flask + React application for managing RTSP IP cameras. It provides JWT-authenticated REST APIs for streams, recordings, events, and schedules, a Socket.IO realtime channel, analytics, and an optional FFmpeg worker that transcodes RTSP sources for browser playback and recording.

![Dashboard screenshot](docs/screenshots/02-dashboard.png)

## ✨ Features

- **Stream management** — register RTSP camera sources, list/update/delete them per user.
- **Recording control** — start/stop recordings and browse them with pagination and filtering.
- **Event log** — motion, audio, connection, and system events with filtering by type and stream.
- **Schedules** — cron-based recording schedules (video / audio / both).
- **Analytics** — stream/recording/event summary statistics.
- **Realtime** — Socket.IO pushes stream, recording, and event updates to the UI.
- **Auth** — JWT login/register, password change, rate limiting (Flask-Limiter + Redis).
- **Backup** — `pg_dump` snapshots of the PostgreSQL database via the API.
- **React frontend** — Dashboard, Timeline, and Settings views served by nginx.
- **Containerized** — multi-service Docker Compose (frontend, backend, Postgres, Redis, FFmpeg worker).

## 🚀 Quick Start

### Docker (recommended)

Requires Docker Engine 29+ with the Compose plugin.

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView
cp .env.example .env          # edit secrets before deploying
docker compose build
docker compose up -d
```

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:5000/health

Create your first user, then promote it to admin in the database:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"change-me-please-123"}'
# Promote to admin:
docker compose exec db psql -U admin -d rtsp_nvr \
  -c "UPDATE users SET role='admin' WHERE username='admin';"
```

### Manual / from source

```bash
# Backend (Python 3.11+)
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
export DATABASE_URL=postgresql://admin:pass@localhost:5432/rtsp_nvr
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
# load schema: psql $DATABASE_URL -f init-db.sql
python backend/app.py                 # serves API on :5000 (also serves the built UI)

# Frontend (Node 20+)
cd frontend && npm install && npm run build
# serve frontend/build with any static server, or rely on the backend's static serving
```

The backend serves the compiled frontend from `frontend/build` when present, so a single `python backend/app.py` can host both API and UI in a simple deployment.

## 📸 Screenshots

- Login — `docs/screenshots/01-login.png`
- Dashboard (streams, analytics, realtime) — `docs/screenshots/02-dashboard.png`
- Timeline (event history) — `docs/screenshots/03-timeline.png`
- Settings (schedules, backup, security) — `docs/screenshots/04-settings.png`

## 🏗️ Architecture / How It Works

```
Browser (React SPA)
   │  REST + Socket.IO
   ▼
Flask backend (Gunicorn + Eventlet)
   ├── PostgreSQL  — users, streams, recordings, events, schedules
   ├── Redis       — rate-limit storage + cache
   └── pg_dump     — database backups
FFmpeg worker (optional)
   └── connects to an RTSP source, transcodes for playback / recording
```

The React frontend is built with Create React App and served by nginx in production; in single-host mode the Flask backend can also serve the static build. The FFmpeg container is only useful when a reachable RTSP camera URL is provided via `RTSP_URL` — without one it will log a connection error and exit.

## ⚙️ Configuration

All configuration is via environment variables (see `.env.example`). Key values:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | — | PostgreSQL connection string (required) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for rate limiting / cache |
| `SECRET_KEY` | random | Flask session signing key |
| `JWT_SECRET_KEY` | random | JWT signing key |
| `FRONTEND_PORT` | `3000` | Host port for the frontend container |
| `BACKEND_PORT` | `5000` | Host port for the backend container |
| `CORS_ENABLED` | `true` | Enable CORS on the backend |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `RETENTION_DAYS` | `7` | Recording/event retention window |
| `AUDIO_THRESHOLD_DB` | `70` | Audio-triggered recording threshold |
| `MESH_VPN_API_KEY` | — | Optional mesh-VPN integration key |
| `RTSP_URL` | — | RTSP source for the FFmpeg worker |

## 🧪 Testing

A minimal smoke test validates app import, route registration, the `/health` endpoint, and input validation:

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt pytest
PYTHONPATH=. python -m pytest test_smoke.py -v
```

The suite stubs database/Redis access so it runs without external services.

## 🗺️ Roadmap

- Native HLS/WebRTC in-browser playback pipeline.
- Per-camera retention policies and object-detection events.
- Helm chart / single-binary distribution.

## 🤝 Contributing

Fork, branch, and open a PR against `main`. Run the smoke test and `docker compose build` before submitting. Please follow the existing code style and keep secrets out of the repo (use `.env.example` only).

## 📄 License

MIT — see [LICENSE](LICENSE)

## 👤 Author

Built by **Jhonattan L. Jimenez** ([@OneByJorah](https://github.com/OneByJorah)) under **JorahOne LLC**. More projects: [github.com/OneByJorah](https://github.com/OneByJorah)
