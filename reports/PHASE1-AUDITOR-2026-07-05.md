# Phase 1 AUDITOR — SentryView

**Date:** 2026-07-05
**Analyst:** J1-PIPELINE AUDITOR

---

## 1. Lint & Formatting

### Python (backend/app.py)

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| F821 | **CRITICAL** | `app.py:72,102,152,186,204,227,265,287,325,353,377,410,436,449,478,512,530,557,581` | `limiter` is used in route decorators (`@limiter.limit(...)`) but never imported or instantiated. Flask-Limiter is in `requirements.txt` but the `Limiter` object is never created. This causes a `NameError` at runtime on any route decorated with `@limiter.limit()`. |
| F821 | **CRITICAL** | `app.py:345,367,427,612,616,622,629,632,679` | `socketio` is used throughout the file (emit, run, on decorators) but never imported or instantiated. Flask-SocketIO is in `requirements.txt` but the `SocketIO` object is never created. This causes a `NameError` at runtime. |
| F821 | **CRITICAL** | `app.py:80,114,134,163,189,215,236,271,290,312,333,357,381,397,422,441,465,486,517,535,596` | `get_db()` is called but never defined. The function `close_db` is defined (line 52) but `get_db` is missing. This causes a `NameError` at runtime on any database operation. |
| Missing import | **HIGH** | `app.py` | `Flask-JWT-Extended` imports only `create_access_token`, `get_jwt_identity`, `jwt_required` — missing `JWTManager` initialization. Without `JWTManager(app)`, JWT features won't work. |
| Unused import | LOW | `app.py:13` | `Path` from `pathlib` is imported but only used once (line 672) — acceptable. |
| Unused import | LOW | `app.py:19` | `psycopg2` imported at module level but only used in the scheduler callback (line 640). |

### JavaScript (frontend/src/)

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| Hardcoded secret | **CRITICAL** | `Settings.js:6` | `tailscaleApiKey: ***` — contains literal `***` as a default value in source code. This is a template redaction artifact that was never cleaned up. |
| Unused variable | LOW | `App.js:147` | `events` state variable is set but never read in the App component (passed to Timeline as prop). |
| Unused import | LOW | `Dashboard.js:1` | `useEffect` imported but `useState` also used — both are used. No issue. |

### Shell Scripts

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| Syntax error | **CRITICAL** | `install.sh:82-84` | Lines use `***` as a command prefix: `SECRET=*** rand -hex 32` — `***` is not a valid command. The shell will fail with `***: command not found`. |
| Syntax error | **CRITICAL** | `install.sh:82-84` | Missing opening parenthesis on subshell: `head -c 64 /dev/urandom \| xxd -p \| head -1)` has a closing `)` but no opening `$(`. |
| Skeletal file | LOW | `proxmox/install-ct.sh` | Only 2 lines: `#!/bin/bash` and `echo Proxmox CT installer`. This is a placeholder. |

---

## 2. Dead Code

| Item | Severity | Location | Description |
|------|----------|----------|-------------|
| `Dockerfile.backend` | LOW | Root | Legacy Dockerfile at root level. The compose file uses `backend/Dockerfile` instead. This file is unused and may confuse users. |
| `config.py` | MEDIUM | `backend/config.py` | This file defines 91 lines of configuration constants, but `app.py` does NOT import it. `app.py` reads config directly from `os.getenv()` and `app.config[]`. The `config.py` file is dead code — none of its constants are used by the running application. |

---

## 3. Dependency Review

### Python (backend/requirements.txt)

| Package | Version | Notes |
|---------|---------|-------|
| flask | 3.1.1 | Latest stable |
| flask-cors | 5.0.1 | Latest |
| flask-jwt-extended | 4.7.1 | Latest |
| flask-socketio | 5.5.1 | Latest |
| flask-limiter | 3.10.1 | Latest |
| bcrypt | 4.3.0 | **Unused** — app uses PBKDF2-SHA256, not bcrypt |
| python-dotenv | 1.1.0 | Latest |
| requests | 2.32.3 | Latest |
| python-multipart | 0.0.31 | Latest |
| werkzeug | 3.1.3 | Latest |
| gunicorn | 23.0.0 | Latest |
| psycopg2-binary | 2.9.10 | Latest |
| redis | 5.2.1 | Latest |
| apscheduler | 3.11.0 | Latest |
| eventlet | 0.39.1 | Latest |

**Issues:**
- `bcrypt==4.3.0` is listed but never used — the app uses `hashlib.pbkdf2_hmac` instead. This is a dead dependency.
- `python-multipart==0.0.31` is listed but never imported in `app.py`. May be needed by Flask for form parsing.

### Python (ffmpeg/requirements.txt)

| Package | Version | Notes |
|---------|---------|-------|
| requests | 2.33.0 | Latest |
| python-dotenv | 1.1.0 | Latest |

**Issues:**
- `requests` is imported in `processor.py` but never actually called — the processor uses `subprocess` for FFmpeg operations. Dead dependency.

### JavaScript (frontend/package.json)

| Package | Version | Notes |
|---------|---------|-------|
| react | ^18.3.1 | Latest |
| react-dom | ^18.3.1 | Latest |
| react-scripts | 5.0.1 | Latest |
| react-router-dom | ^6.28.0 | Latest |
| socket.io-client | ^4.7.5 | Latest |
| axios | ^1.7.7 | **Unused** — the app uses `fetch()` directly, not axios |
| recharts | ^2.13.3 | Latest |
| hls.js | ^1.5.15 | Latest |
| react-hot-toast | ^2.4.1 | Latest |

**Issues:**
- `axios` is listed as a dependency but never imported or used anywhere in the frontend code. The app uses the native `fetch()` API and a custom `api.js` wrapper. Dead dependency.

---

## 4. CVEs / Known Vulnerabilities

No automated CVE scan was run (no tool available in this environment). Manual review of dependency versions shows all packages are recent (2024-2025 releases). Recommend running `pip-audit` or `safety` in CI.

---

## 5. Secrets Detection

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| Hardcoded default credentials | **CRITICAL** | `init-db.sql:121-131` | Default admin user created with password "admin" and a placeholder hash. The comment says "CHANGE THIS IN PRODUCTION!" but the hash is a placeholder (`b2d1c348...`), not a real hash of "admin". |
| Hardcoded RTSP credentials | **HIGH** | `ffmpeg/processor.py:16` | Default RTSP URL contains hardcoded credentials: `rtsp://admin:admin@192.168.1.10:554/stream` |
| Hardcoded DB password in compose | **HIGH** | `docker-compose.yml:32,62,118` | Database URL contains `***` placeholder and `POSTGRES_PASSWORD` has default `secure_password_change_me` |
| Hardcoded JWT secret | **HIGH** | `docker-compose.yml:35` | `JWT_SECRET_KEY` default: `change-this-jwt-secret` |
| Hardcoded secret key | **HIGH** | `docker-compose.yml:34` | `SECRET_KEY` default: `change-this-to-a-random-secret` |
| Template redaction artifact | **CRITICAL** | `Settings.js:6` | `tailscaleApiKey: ***` — literal `***` in source code |
| Template redaction artifact | **CRITICAL** | `install.sh:82-84` | `***` used as shell command prefix |
| Email address in SECURITY.md | LOW | `SECURITY.md:15` | `j1admin@onebyjorah.com` — legitimate contact, but exposed in public repo |

---

## 6. README Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| System purpose | ✅ | Clear: "Web-Based RTSP NVR Dashboard" |
| Quick start | ✅ | Both Docker and install.sh methods documented |
| Architecture diagram | ⚠️ | Present but incomplete — omits `backup`, `redis`, `scripts/` |
| Tech stack badges | ❌ | Claims "FastAPI" but code is Flask — **misleading** |
| Service table | ❌ | Missing — no port/service/role table |
| Configuration | ❌ | No `.env` reference or configuration guide |
| License | ✅ | MIT, correctly referenced |
| Contributing | ✅ | Separate CONTRIBUTING.md exists |
| Security | ✅ | Separate SECURITY.md exists |
| Screenshots | ✅ | Assets directory has screenshots |

**Critical README bug:** Badge and description claim "FastAPI Backend" but the actual code is Flask. This is a documentation error that will confuse developers.

---

## 7. Tests

| Item | Status | Notes |
|------|--------|-------|
| Python tests | ❌ | No test files exist anywhere in the repo |
| JavaScript tests | ❌ | No test files exist; `package.json` has `"test": "react-scripts test"` but no test files |
| Shell tests | ❌ | No shell-based tests |
| Smoke tests | ❌ | No smoke test script |
| CI test runner | ❌ | CodeQL workflow does not run tests |

**No tests exist in the repository.** This is a significant gap for a Production-classified system.

---

## 8. Docker Review

| Service | Dockerfile | Health Check | Restart Policy | Volumes | Networks |
|---------|-----------|-------------|----------------|---------|----------|
| frontend | ✅ Multi-stage | ✅ wget | unless-stopped | None | rtsp-nvr-network |
| backend | ✅ Slim | ✅ wget | unless-stopped | backend-logs | rtsp-nvr-network |
| db | ✅ postgres:15-alpine | ✅ pg_isready | unless-stopped | rtsp-nvr-data + init-db.sql | rtsp-nvr-network |
| redis | ✅ redis:7-alpine | ✅ redis-cli ping | unless-stopped | rtsp-nvr-redis | rtsp-nvr-network |
| ffmpeg | ✅ Slim | ❌ No health check | unless-stopped | rtsp-nvr-ffmpeg | rtsp-nvr-network |
| backup | ✅ postgres:15-alpine | ❌ No health check | unless-stopped | rtsp-nvr-backup | rtsp-nvr-network |

**Issues:**
- `ffmpeg` service has no health check
- `backup` service has no health check
- `ffmpeg` depends on `backend` but uses `depends_on` without `condition: service_healthy` (just `- backend`)
- `Dockerfile.backend` at root is unused (dead file)
- No `.dockerignore` files exist

---

## 9. Folder Structure

```
SentryView/
├── backend/          ✅ Flask API
├── frontend/         ✅ React SPA
├── ffmpeg/           ✅ Stream processor
├── scripts/          ✅ Health check script
├── proxmox/          ⚠️ Skeletal (1 placeholder file)
├── assets/           ✅ Screenshots, logos
├── .github/          ✅ CI/CD, templates, dependabot
├── reports/          ✅ Created by this audit
├── docker-compose.yml ✅
├── .env.sample       ✅
├── .gitignore        ✅
├── INTENT.md         ✅
├── README.md         ⚠️ Has inaccuracies
├── CHANGELOG.md      ⚠️ Minimal (only v1.0.0 entry, actual version is 2.1.0)
├── ROADMAP.md        ✅
├── CONTRIBUTING.md   ✅
├── CODE_OF_CONDUCT.md ✅
├── SECURITY.md       ✅
├── LICENSE           ✅
├── Dockerfile.backend ❌ Dead file
└── j1.yaml           ✅ Created by this pipeline
```

---

## 10. Summary

### CRITICAL Items (blocking)

| # | Item | Location |
|---|------|----------|
| C1 | `limiter` not imported/instantiated — all rate-limited routes will crash | `backend/app.py` |
| C2 | `socketio` not imported/instantiated — all WebSocket features will crash | `backend/app.py` |
| C3 | `get_db()` not defined — all database operations will crash | `backend/app.py` |
| C4 | `JWTManager` not initialized — JWT auth won't work | `backend/app.py` |
| C5 | Shell syntax errors in `install.sh` — `***` command prefix | `install.sh:82-84` |
| C6 | Hardcoded `***` in Settings.js source code | `frontend/src/components/Settings.js:6` |

### HIGH Items

| # | Item | Location |
|---|------|----------|
| H1 | `config.py` is dead code — not imported by `app.py` | `backend/config.py` |
| H2 | `bcrypt` in requirements.txt but never used | `backend/requirements.txt` |
| H3 | `axios` in package.json but never used | `frontend/package.json` |
| H4 | No tests anywhere in the repository | Entire repo |
| H5 | README claims FastAPI but code is Flask | `README.md` |
| H6 | Default admin credentials in init-db.sql | `init-db.sql:121-131` |
| H7 | Hardcoded RTSP credentials in processor.py | `ffmpeg/processor.py:16` |
| H8 | Dependabot pip/npm/docker directories point to `/` instead of actual paths | `.github/dependabot.yml` |
| H9 | CHANGELOG only lists v1.0.0 but actual version is 2.1.0 | `CHANGELOG.md` |
| H10 | ffmpeg and backup services lack health checks | `docker-compose.yml` |

### MEDIUM Items

| # | Item | Location |
|---|------|----------|
| M1 | `Dockerfile.backend` is dead/unused | Root |
| M2 | `proxmox/install-ct.sh` is a placeholder | `proxmox/install-ct.sh` |
| M3 | No `.dockerignore` files | Root, backend/, frontend/ |
| M4 | `ffmpeg/processor.py` has scoping bug in `cleanup_old_events` (line 75-76) | `ffmpeg/processor.py` |
| M5 | `requests` in ffmpeg/requirements.txt is unused | `ffmpeg/requirements.txt` |

### LOW Items

| # | Item | Location |
|---|------|----------|
| L1 | Architecture diagram in README is incomplete | `README.md` |
| L2 | No `.env` configuration guide in README | `README.md` |
| L3 | No service table in README | `README.md` |
