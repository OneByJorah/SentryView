# INTENT.md — J1-PIPELINE Phase -1 (ORACLE)

**Repository:** `OneByJorah/SentryView`
**Analysis Date:** 2026-07-05
**Analyst:** J1-PIPELINE ORACLE (read-only)
**Status:** Intent Reconstructed

---

## What This System Does

**SentryView is a self-hosted, web-based Network Video Recorder (NVR) dashboard for IP camera surveillance.** It provides a complete lifecycle for RTSP video streams: live monitoring, automated recording, timeline-based playback review, event tracking, and analytics — all through a modern browser UI.

### Technical Architecture

The system is composed of six containerized services orchestrated via Docker Compose:

| Service | Role | Technology | Port |
|---------|------|------------|------|
| **frontend** | React SPA — live view, timeline, settings | React 18, Socket.IO Client, recharts, hls.js, Nginx (Alpine) | 3000 → 80 |
| **backend** | REST API + WebSocket server — auth, CRUD, scheduling, analytics | Flask, Flask-JWT-Extended, Flask-SocketIO, Flask-Limiter, APScheduler, Gunicorn + Eventlet | 5000 |
| **db** | Primary data store — users, streams, recordings, events, schedules | PostgreSQL 15 (Alpine) | 5432 |
| **redis** | In-memory cache + Socket.IO pub/sub | Redis 7 (Alpine) with append-only persistence | 6379 |
| **ffmpeg** | Stream processor — RTSP ingestion, transcoding, recording, cleanup | FFmpeg + Python wrapper | — |
| **backup** | Scheduled pg_dump backups | PostgreSQL client + cron | — |

### Key Capabilities

- **Live Monitoring** — Real-time RTSP stream viewing from any IP camera (H.264/H.265)
- **Timeline Playback** — Review recorded footage with event-type filtering and JSON export
- **Automated Recording** — On-demand or cron-scheduled recording (video, audio, or both)
- **Event System** — 8 event types: `recording_started`, `recording_stopped`, `motion_detected`, `audio_exceeded`, `stream_connected`, `stream_disconnected`, `system_alert`, `manual_event`
- **Multi-User Auth** — JWT-based authentication with role-based access (admin/user/viewer), rate-limited endpoints
- **Analytics Dashboard** — Stream counts, recording hours, event breakdowns, 7-day recording bar chart
- **Scheduled Cleanup** — Automatic purging of recordings (30 days) and events (7 days) via APScheduler
- **Backup & Restore** — On-demand and daily cron pg_dump backups with 30-day retention
- **Health Checks** — Every service has Docker health checks; a dedicated healthcheck script validates the full stack
- **Tailscale Support** — Optional Tailscale integration for secure remote access without port forwarding
- **Proxmox Support** — Container template installer for Proxmox VE environments

### Operational Role

SentryView operates as a **self-hosted surveillance infrastructure** component. It replaces or augments commercial NVR appliances (e.g., Hikvision DVRs, Blue Iris, Synology Surveillance Station) with an open-source, containerized alternative that runs on commodity hardware — a Raspberry Pi, a home server, or a Proxmox cluster. It is designed to be deployed with a single `docker compose up -d` command and immediately start ingesting RTSP streams.

---

## Why This Was Built

### Real Problem

IP camera surveillance has a fragmented tooling landscape with no single solution that is simultaneously **lightweight, self-hosted, privacy-preserving, and production-grade**:

1. **Commercial NVRs** (Hikvision, Dahua, Synology) are expensive, vendor-locked, and often require proprietary hardware or per-camera licensing.
2. **Open-source NVRs** (ZoneMinder, Shinobi, Frigate) exist but carry significant complexity — ZoneMinder's Perl-based architecture is hard to extend, Shinobi requires Node.js expertise, and Frigate is heavily optimized for AI-based object detection (overkill for basic recording).
3. **Cloud solutions** (Ring, Nest, Arlo) require monthly subscriptions and send video off-site, which is unacceptable for privacy-conscious users or air-gapped environments.
4. **DIY approaches** (raw ffmpeg scripts, custom Python) lack a unified UI, user management, scheduling, and event tracking.

The core gap: **a lightweight, modern, fully self-contained NVR that "just works" with any RTSP camera, deployable in minutes, with a clean web UI and no external dependencies beyond Docker.**

### Why Existing Tools Were Insufficient

| Tool | Gap |
|------|-----|
| **ZoneMinder** | Heavy, Perl-based, dated UI, complex setup, requires Apache/MySQL |
| **Shinobi** | Node.js dependency, less mature, smaller community |
| **Frigate** | Optimized for Coral TPU + AI detection; overkill and resource-heavy for basic recording |
| **Blue Iris** | Windows-only, paid license, no containerization |
| **Scrypted / Homebridge** | Focused on HomeKit integration, not standalone NVR |
| **Commercial DVRs** | Hardware lock-in, limited API access, no customization |
| **Motion / MotionEye** | Limited to motion detection, no timeline/playback UI, dated interface |

None of these provide a **container-native, Docker Compose-first, Flask+React NVR** with real-time WebSocket updates, JWT auth, scheduled recording, and a modern UI — all in a single `docker compose up -d` command.

### What Triggered Development

The git history reveals the project was initially developed externally and uploaded as a bulk commit (`0245300 — "Add files via upload"`, 2026-02-08). The initial upload already contained a complete Flask+React NVR with FFmpeg processing, indicating it was built as a **greenfield project** to fill the gap described above.

Key milestones in the evolution:

- **`0245300`** — Initial bulk upload of the complete NVR system
- **`4fce8cf`** — `v2.1.0: Full upgrade - backend security, frontend Socket.IO, init-db, docker-compose v5, modernized README` — major iteration adding real-time WebSocket support, proper database initialization, and production-grade Docker Compose
- **`15bfebb`** — `feat: production-ready healthcheck` — production hardening
- **`3289c84`** — `Apply ruff auto-fixes and portfolio standardization` — J1 pipeline standardization pass
- **`6fec234`** — `audit(SentryView): sanitize email references` — security audit
- **Repo rename** — Multiple commits (`3bed4ac`, `7fef4bb`, `481b41a`) show the repo was renamed to SentryView from a previous name, aligning it with the JorahOne portfolio naming convention

The project was built iteratively, starting as a minimal Flask+React dashboard and evolving into a full-featured NVR with real-time updates, scheduled recording, analytics, and production deployment patterns.

### Ecosystem Fit

SentryView fills the **Security / Observability** slot in the JorahOne portfolio:

```
JorahOne Ecosystem
├── Infrastructure & Deployment
│   ├── [JorahOne/EdgeRouter]     ← Network edge / routing
│   └── [JorahOne/SentryView]     ← Security surveillance / NVR
├── AI & Automation
│   ├── [JorahOne/Hermes]         ← AI agent orchestration
│   └── [JorahOne/...]            ← Other AI tools
├── Developer Tools
│   └── [JorahOne/...]            ← Dev tooling
└── Security & Observability
    └── [JorahOne/SentryView]     ← ← THIS REPO
```

SentryView is:
- **Self-hosted and privacy-first** — no cloud dependency, no telemetry
- **Vendor-agnostic** — works with any RTSP-compatible camera
- **Container-native** — designed for Docker Compose from day one
- **J1 pipeline-compliant** — has gone through audit, brand-align, dependabot, and standardization phases

---

## Operational Classification

**Classification: PRODUCTION**

**Sub-classification: Security / Observability**

Evidence:
- **Version labels**: v2.1.0 tagged in git history (`4fce8cf`); `package.json` declares version 2.1.0
- **Health checks**: Every Docker service has a health check defined; dedicated `scripts/healthcheck.sh` validates the full stack
- **CI/CD**: CodeQL analysis workflow (Python, JavaScript, TypeScript) on push/PR to main; Dependabot configured for pip, npm, docker, and GitHub Actions
- **Security posture**: `SECURITY.md` with 90-day disclosure timeline; security audit commit (`6fec234`); JWT auth with rate limiting on all endpoints; password hashing via PBKDF2-SHA256
- **Monitoring**: Health endpoint (`/health`) checks both PostgreSQL and Redis connectivity
- **Backup**: Automated daily pg_dump backups with 30-day retention; on-demand backup via API
- **Data retention**: Scheduled cleanup of recordings (30 days) and events (7 days) via APScheduler
- **Production web server**: Gunicorn + Eventlet (not Flask dev server) in production; Nginx reverse proxy for frontend
- **Community readiness**: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE` (MIT), issue/PR templates, `ROADWAY.md`
- **Multi-environment support**: Bare metal (install.sh), Docker Compose, Proxmox CT
- **Tailscale integration**: Optional secure remote access without port forwarding

---

## Key Architectural Decisions

1. **Flask over FastAPI** — Despite the README claiming "FastAPI Backend," the actual implementation uses Flask with Flask-SocketIO, Flask-JWT-Extended, and Flask-Limiter. This was likely chosen for Flask's mature ecosystem of extensions (SocketIO, JWT, rate limiting) and simpler async model via Eventlet. The README discrepancy is a documentation bug.

2. **Separate FFmpeg container** — Rather than embedding FFmpeg in the backend container, it runs as a standalone service. This allows independent scaling, resource allocation, and restart policies for the stream processing pipeline without affecting the API server.

3. **PostgreSQL over SQLite** — Chosen for concurrent access, JSONB support for event metadata, and production-grade backup/restore via pg_dump. SQLite would be simpler but cannot handle concurrent writes from multiple services.

4. **Redis for Socket.IO pub/sub** — Redis provides a cross-process pub/sub bus for Socket.IO, enabling real-time event broadcasting across multiple backend instances if scaled horizontally. Also used for caching.

5. **Nginx reverse proxy** — The frontend Nginx container proxies `/api/` and `/socket.io/` to the backend, providing a single entry point, WebSocket upgrade handling, and static asset caching with immutable cache headers.

6. **Eventlet worker for Gunicorn** — Flask-SocketIO requires an async worker. Eventlet was chosen over Gevent for its simpler monkey-patching and compatibility with the Flask ecosystem.

7. **PBKDF2-SHA256 for password hashing** — Uses the Flask app's SECRET_KEY as a salt with 100,000 iterations. This is a reasonable choice for a self-hosted system but would benefit from bcrypt/argon2 for stronger password storage.

8. **APScheduler for background tasks** — In-process scheduler handles cleanup of old recordings and events. This avoids an external cron dependency but means cleanup runs inside the backend container process.

---

## Repository Structure

```
SentryView/
├── docker-compose.yml           # Full deployment (6 services)
├── Dockerfile.backend           # Legacy backend Dockerfile (not used by compose)
├── .env.sample                  # Environment template with all config vars
├── install.sh                   # Bare-metal installer (Ubuntu/Debian)
├── init-db.sql                  # PostgreSQL schema + default admin user
├── README.md                    # Project documentation
├── CHANGELOG.md                 # Release notes (minimal)
├── ROADMAP.md                   # Future plans (generic)
├── CONTRIBUTING.md              # Contribution guidelines
├── CODE_OF_CONDUCT.md           # Contributor Covenant v2.1
├── SECURITY.md                  # Security policy (90-day disclosure)
├── LICENSE                      # MIT License
├── .gitignore                   # Python/IDE/OS ignores
│
├── backend/                     # Flask API server
│   ├── Dockerfile               # Production container (Gunicorn)
│   ├── requirements.txt         # Python dependencies (15 packages)
│   ├── app.py                   # Main application (679 lines)
│   └── config.py                # Configuration management (91 lines)
│
├── frontend/                    # React SPA
│   ├── Dockerfile               # Multi-stage build (Node → Nginx)
│   ├── nginx.conf               # Nginx config with API proxy + WebSocket
│   ├── package.json             # React 18, Socket.IO, recharts, hls.js
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js               # Main app with auth, routing, socket
│       ├── App.css              # Styling
│       ├── index.js             # Entry point
│       ├── index.css            # Global styles
│       ├── api.js               # API client with JWT handling
│       └── components/
│           ├── Login.js         # Login form
│           ├── Dashboard.js     # Stream grid + analytics
│           ├── Timeline.js      # Event timeline with filtering/export
│           └── Settings.js      # Settings tabs (general, schedules, backup, security)
│
├── ffmpeg/                      # Stream processor
│   ├── Dockerfile               # Python + FFmpeg container
│   ├── requirements.txt         # requests, python-dotenv
│   └── processor.py             # RTSP ingestion + recording loop (165 lines)
│
├── scripts/
│   └── healthcheck.sh           # Full-stack health check script
│
├── proxmox/
│   └── install-ct.sh            # Proxmox CT installer (skeletal — 2 lines)
│
├── assets/
│   ├── banner.svg               # Project banner
│   ├── logo.svg                 # Project logo
│   ├── screenshot-stream.png    # Live stream screenshot
│   ├── screenshot-timeline.png  # Timeline screenshot
│   ├── screenshot-dashboard.png # Dashboard screenshot
│   └── screenshot-settings.png # Settings screenshot
│
└── .github/
    ├── dependabot.yml           # Dependabot config (pip, npm, docker, actions)
    ├── workflows/
    │   └── codeql.yml           # CodeQL analysis (Python, JS, TS)
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        ├── feature_request.md
        └── PULL_REQUEST_TEMPLATE.md
```

---

## Notes

### Documentation Discrepancies

1. **README says "FastAPI Backend" but the code is Flask.** The README badge and description claim FastAPI, but `backend/app.py` imports Flask, Flask-JWT-Extended, Flask-SocketIO, Flask-Limiter, and runs via Gunicorn+Eventlet. This is a documentation bug that should be corrected.

2. **README architecture diagram is incomplete** — It omits the `backup` service, `redis` service, and the `scripts/` directory contents.

### Dependabot Config-Drift

3. **Dependabot pip ecosystem points to `/` instead of `/backend` and `/ffmpeg`.** The `dependabot.yml` has `directory: "/"` for the pip ecosystem, but there are two `requirements.txt` files at `/backend/requirements.txt` and `/ffmpeg/requirements.txt`, not at the repo root. Dependabot will scan the root for a `requirements.txt` that doesn't exist, producing no results. This is a template vestige — the npm and docker entries have the same issue (no `package.json` or `Dockerfile` at root level, though the root-level `Dockerfile.backend` exists).

### Git History Observations

4. **Initial commit is a bulk upload** (`0245300 — "Add files via upload"`), not a git-based initial build. The project was developed externally and uploaded as a complete snapshot, then iterated in-repo.

5. **Repo was renamed** — Multiple commits (`3bed4ac`, `7fef4bb`, `481b41a`) reference "rename to SentryView" and "migrate references after rename," indicating the repo had a different name earlier in its lifecycle.

6. **Security audit present** — Commit `6fec234` (`audit(SentryView): sanitize email references`) shows a security audit was performed, a positive maturity signal.

### Empty / Skeletal Directories

7. **`proxmox/install-ct.sh` is skeletal** — Only 2 lines (`echo Proxmox CT installer`). This appears to be a placeholder for future Proxmox container template support.

### Code Observations

8. **`backend/app.py` references `@limiter.limit()` before `limiter` is defined** — The `limiter` object is used in route decorators (lines 72, 102, 152, etc.) but is never imported or instantiated in the visible code. This would cause a `NameError` at runtime. The Flask-Limiter extension is in `requirements.txt` but the `Limiter` initialization is missing from `app.py`.

9. **`ffmpeg/processor.py` has a scoping bug** — The `cleanup_old_events()` function references `events` (line 75: `if len(events) > MAX_RECORDINGS`) but `events` is a global list that `cleanup_old_events` cannot reassign without a `global events` declaration. The assignment `events = events[-MAX_RECORDINGS:]` creates a local variable instead of modifying the global.

10. **`install.sh` has shell syntax errors** — Lines 82-84 use `***` as a command prefix (likely a redaction artifact from template processing): `SECRET=*** rand -hex 32` would fail because `***` is not a valid command.

### Classification Summary

Despite the above issues, SentryView is a **Production**-classified system. It has health checks, JWT auth, rate limiting, automated backups, retention policies, a security policy, CI/CD, and community documentation. The code issues noted above are bugs that should be addressed in a maintenance pass, but they do not change the overall production classification.
