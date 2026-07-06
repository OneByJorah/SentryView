# Phase 2 ARCHITECT — SentryView

**Date:** 2026-07-05
**Analyst:** J1-PIPELINE ARCHITECT

---

## Architecture Overview

SentryView is a **6-service Docker Compose stack** implementing a self-hosted NVR (Network Video Recorder) with a React SPA frontend and Flask REST API backend.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│   Nginx      │────▶│   Backend   │
│  (React SPA)│     │  (frontend)  │     │  (Flask)    │
└─────────────┘     │  port:3000   │     │  port:5000  │
                    └──────────────┘     └──────┬───────┘
                           │                    │
                           │  /socket.io/       │
                           │  (WebSocket)       │
                           ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │    Redis     │     │ PostgreSQL  │
                    │  (pub/sub)   │     │   (data)    │
                    └──────────────┘     └─────────────┘
                                                    │
                    ┌──────────────┐     ┌─────────────┐
                    │   FFmpeg     │     │   Backup    │
                    │ (processor)  │     │  (pg_dump)  │
                    └──────────────┘     └─────────────┘
```

---

## Service Architecture

### 1. Frontend (React SPA)
- **Role:** User interface for live monitoring, timeline review, settings
- **Tech:** React 18, Socket.IO Client, recharts, hls.js
- **Deployment:** Multi-stage Docker build (Node → Nginx Alpine)
- **Nginx config:** Reverse proxies `/api/` and `/socket.io/` to backend
- **Key design decisions:**
  - SPA with client-side routing (react-router-dom)
  - JWT token stored in `localStorage` (not httpOnly cookies — security concern)
  - Socket.IO for real-time updates (stream status, events, recordings)
  - Dark/light theme toggle
  - No CSS framework — custom CSS in App.css

### 2. Backend (Flask API)
- **Role:** REST API + WebSocket server for auth, CRUD, scheduling, analytics
- **Tech:** Flask, Flask-JWT-Extended, Flask-SocketIO, Flask-Limiter, APScheduler, Gunicorn + Eventlet
- **Key design decisions:**
  - **Flask over FastAPI** despite README claiming FastAPI. Flask was chosen for its mature extension ecosystem (SocketIO, JWT, rate limiting) and simpler async model via Eventlet.
  - **Gunicorn + Eventlet** for production — Eventlet provides the async worker needed by Flask-SocketIO
  - **APScheduler** for in-process background tasks (cleanup of old recordings/events at 2 AM daily)
  - **PBKDF2-SHA256** for password hashing (100,000 iterations, using SECRET_KEY as salt)
  - **Rate limiting** on all endpoints via Flask-Limiter
  - **Health endpoint** at `/health` checks both PostgreSQL and Redis connectivity
  - **Catch-all route** serves the React SPA for client-side routing

### 3. Database (PostgreSQL 15 Alpine)
- **Role:** Primary data store — users, streams, recordings, events, schedules
- **Schema:** 5 tables (users, streams, events, recordings, schedules) + analytics_cache
- **Key design decisions:**
  - JSONB for event metadata (flexible schema)
  - CHECK constraints for event_type and recording_type validation
  - Indexes on user_id, stream_id, event_type, created_at for query performance
  - Partial index on recordings.is_active for active recording lookups
  - Auto-update triggers for updated_at columns
  - Stored procedure `cleanup_expired_records()` for database-level cleanup
  - Default admin user seeded in init-db.sql

### 4. Redis (Redis 7 Alpine)
- **Role:** In-memory cache + Socket.IO pub/sub bus
- **Configuration:** Append-only persistence, 128MB maxmemory, allkeys-lru eviction
- **Key design decisions:**
  - Enables horizontal scaling of backend (multiple instances share Redis pub/sub)
  - AOF persistence ensures events survive restarts
  - LRU eviction prevents memory exhaustion

### 5. FFmpeg Processor (Python + FFmpeg)
- **Role:** RTSP stream ingestion, transcoding, recording, cleanup
- **Tech:** Python 3.11, FFmpeg, subprocess
- **Key design decisions:**
  - **Separate container** from backend — allows independent scaling and resource allocation
  - **Subprocess-based FFmpeg calls** — launches FFmpeg as a child process for stream handling
  - **In-memory event tracking** — events stored in a Python list and persisted to `/events/events.json`
  - **Cleanup loop** — runs every 60 seconds, removes old recordings and events
  - **No health check** — the container has no health endpoint

### 6. Backup (PostgreSQL 15 Alpine)
- **Role:** Scheduled pg_dump backups with 30-day retention
- **Deployment:** Uses the same postgres:15-alpine image with a cron entrypoint
- **Key design decisions:**
  - **Cron-based** — uses BusyBox crond inside the container
  - **pg_dump custom format** — compressed, restore-friendly
  - **30-day retention** — old backups auto-pruned
  - **Separate volume** — backups stored in dedicated Docker volume

---

## Data Flow

### Authentication Flow
```
Browser → POST /api/auth/login → Backend validates credentials → Returns JWT
Browser stores JWT in localStorage → Sends JWT in Authorization header
Backend validates JWT via flask-jwt-extended → Returns user data
```

### Live Stream Flow
```
IP Camera (RTSP) → FFmpeg container → Transcodes to HLS/FLV
Browser connects via Socket.IO → Receives stream status updates
Browser plays HLS stream via hls.js
```

### Recording Flow
```
Browser → POST /api/recordings → Backend creates recording record
Backend emits Socket.IO event → FFmpeg starts recording
FFmpeg writes to /recordings/ volume
Browser → DELETE /api/recordings/:id → Backend stops recording
Backend emits Socket.IO event → FFmpeg stops recording
```

### Event Flow
```
FFmpeg detects motion/audio → Saves event to events.json
Browser creates manual event → POST /api/events
Backend emits Socket.IO "new_event" → All connected browsers receive it
```

---

## Architectural Strengths

1. **Clean separation of concerns** — Each service has a single responsibility (frontend, API, DB, cache, processing, backup)
2. **Container-native design** — Everything runs in Docker with health checks, restart policies, and named volumes
3. **Real-time architecture** — Socket.IO + Redis pub/sub enables live updates without polling
4. **Defense in depth** — JWT auth + rate limiting + input validation on all endpoints
5. **Production web server** — Gunicorn + Eventlet (not Flask dev server)
6. **Database schema quality** — Proper foreign keys, CHECK constraints, indexes, triggers
7. **Health monitoring** — Every core service has health checks; dedicated healthcheck script validates the full stack
8. **Backup strategy** — Automated daily pg_dump with retention policy

---

## Architectural Concerns

### CRITICAL

| # | Concern | Impact |
|---|---------|--------|
| A1 | **Missing imports/initializations** — `limiter`, `socketio`, `get_db()`, `JWTManager` are all used but never defined in `app.py` | The application will crash on first request. This is not an architectural design issue but a code-completeness issue — the architecture was designed for these components but they were never wired up. |

### HIGH

| # | Concern | Impact |
|---|---------|--------|
| A2 | **JWT in localStorage** — The frontend stores JWT tokens in `localStorage` instead of httpOnly cookies | Vulnerable to XSS attacks. If an attacker injects JavaScript, they can steal the token. |
| A3 | **No database migration system** — Schema is defined in `init-db.sql` which runs once on first container start | Schema changes require manual SQL or container rebuild. No Alembic/Flyway-style migrations. |
| A4 | **FFmpeg processor has no health check** — The container runs silently with no way to detect failure | If FFmpeg crashes, the container stays up but no streams are processed. |
| A5 | **Backup container has no health check** — If cron fails, backups silently stop | No monitoring of backup success/failure. |
| A6 | **config.py is dead code** — 91 lines of configuration constants that are never imported by app.py | Configuration is duplicated between config.py and app.py's inline os.getenv() calls. Maintenance risk. |

### MEDIUM

| # | Concern | Impact |
|---|---------|--------|
| A7 | **Single backend instance** — Gunicorn is configured with `-w 1` (1 worker) | No horizontal scaling within the container. Multiple requests block on the single Eventlet worker. |
| A8 | **FFmpeg processor uses in-memory event list** — Events are stored in a Python list and persisted to a JSON file | Events are lost if the container restarts before the file is written. No synchronization with the database. |
| A9 | **No message queue** — FFmpeg communicates with backend only via HTTP | Tight coupling. If backend is down, FFmpeg cannot report events. |
| A10 | **Backup container uses BusyBox crond** — No monitoring, no alerting | Backup failures are silent. |
| A11 | **No rate limiting on /health endpoint** — The health endpoint is publicly accessible with no rate limit | Minor — health endpoints are typically left open, but could be abused for DoS. |

### LOW

| # | Concern | Impact |
|---|---------|--------|
| A12 | **No API versioning** — All routes are under `/api/` with no version prefix | Future API changes will break existing clients. |
| A13 | **No OpenAPI/Swagger docs** — No API documentation endpoint | Developers must read the source code to understand the API. |
| A14 | **Frontend uses `window.location.href` for navigation** — Instead of react-router's `useNavigate` | Causes full page reloads instead of SPA-style navigation. |
| A15 | **No pagination on analytics endpoint** — Returns all data at once | Could be slow with many events/recordings. |

---

## Architecture Score

**Score: 65/100** (DEGRADED)

**Deductions:**
- -20: Missing imports/initializations make the app non-functional (A1)
- -5: JWT in localStorage (A2)
- -5: No database migrations (A3)
- -3: Missing health checks on 2 services (A4, A5)
- -2: Dead config.py (A6)

**The architecture design is sound** — the concerns are primarily about incomplete implementation and operational gaps, not fundamental design flaws. The service decomposition, data flow, and technology choices are appropriate for a self-hosted NVR system.
