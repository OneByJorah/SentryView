# AUDIT_REPORT — SentryView

**Date:** 2026-07-05
**Status:** `CRITICAL` (Score: 45/100)

---

## 1. PROJECT CLASSIFICATION

| Field | Value |
|---|---|
| **Repo** | SentryView |
| **Class** | Web / Monitoring / Surveillance |
| **Primary Language** | Python (Flask), JavaScript (React) |
| **Deployment** | Docker Compose |
| **DB** | PostgreSQL 15 + Redis 7 |

---

## 2. CRITICAL BUGS (Runtime-breaking)

### 🔴 C1 — `app.py`: Missing `limiter` and `socketio` initialization

`@limiter.limit()` and `socketio.emit()` / `@socketio.on()` are used extensively but **neither `Limiter` nor `SocketIO` is ever instantiated**. The file imports `flask_limiter` and `flask_socketio` but never calls:

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: ...)

from flask_socketio import SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
```

**Impact:** All rate-limited routes and all WebSocket functionality will crash on first use.

### 🔴 C2 — `app.py`: Missing `get_db()` function

The code calls `db = get_db()` in nearly every route handler, but only `close_db(error)` is defined — there is no `get_db()` function that creates a database connection. `get_db()` is completely missing.

**Impact:** Every API route will crash with `NameError: name 'get_db' is not defined`.

### 🔴 C3 — `install.sh`: Broken password generation

The install script has mangled bash syntax:
```bash
SECRET=*** rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | head -1)
```
The `***` prefix and broken `$()` substitution means generated secrets will be wrong. The generated `.env` file also writes literal `***` placeholders instead of the actual random values.

**Impact:** Installer generates an unusable `.env` file with literal `***` strings as secrets.

### 🔴 C4 — `ffmpeg/processor.py`: Global variable shadowing

`cleanup_old_events()` does:
```python
events = events[-MAX_RECORDINGS:]
```
This creates a **local** variable instead of modifying the global `events` list. The cleanup has no effect.

**Impact:** Event list grows unbounded — memory leak over time.

---

## 3. SECURITY ISSUES

| # | Issue | Location | Severity |
|---|---|---|---|
| S1 | Default `admin`/`admin` credentials shipped | `init-db.sql` (seed data) | CRITICAL |
| S2 | Hardcoded default `admin:admin` in DATABASE_URL | `backend/config.py`, `docker-compose.yml` | CRITICAL |
| S3 | Weak default SECRET_KEY `"change-this-to-a-random-secret"` | `backend/app.py` | HIGH |
| S4 | Weak default JWT_SECRET_KEY `"jwt-secret-change-me"` | `backend/app.py` | HIGH |
| S5 | `RTSP_PASSWORD=admin` hardcoded default | `backend/config.py` | HIGH |
| S6 | CORS `supports_credentials=True` with no origin restriction | `backend/app.py` | MEDIUM |
| S7 | Installer runs as root, no drop-privileges | `install.sh` | MEDIUM |
| S8 | No HTTPS enforcement | `nginx.conf` (port 80 only) | MEDIUM |

---

## 4. README COMPLIANCE (README_STANDARD.md)

| Requirement | Status | Notes |
|---|---|---|
| One-line positioning | ✅ | "Web-Based RTSP NVR Dashboard" |
| Max 3 badges | ❌ | Has **4 badges** (React, FastAPI, FFmpeg, Docker) |
| 60-second quick start | ✅ | `./install.sh` and `docker compose up -d` |
| Features (3-5) | ✅ | 8 features listed |
| Architecture diagram | ✅ | Directory tree shown |
| Contributing | ✅ | Links to CONTRIBUTING.md |
| License | ✅ | MIT |

---

## 5. MISSING STANDARD FILES

| File | Purpose | Status |
|---|---|---|
| `.dockerignore` | Build context optimization | ❌ |
| `j1.yaml` | Pipeline registry metadata | ❌ |
| `INTENT.md` | Engineering intent | ❌ |
| `CODEOWNERS` | PR ownership routing | ❌ |
| `pyproject.toml` | Python package metadata | ❌ |

---

## 6. PRODUCTION SCORE

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Security | 20% | 30 | 6.0 |
| Architecture | 15% | 55 | 8.25 |
| Documentation | 15% | 75 | 11.25 |
| Testing | 15% | 30 | 4.5 |
| Deployment | 10% | 70 | 7.0 |
| Automation | 10% | 65 | 6.5 |
| GitHub Quality | 10% | 70 | 7.0 |
| Branding | 5% | 75 | 3.75 |

**Total Score: 45.25 / 100 — `CRITICAL`**

---

## 7. IMMEDIATE ACTIONS REQUIRED

1. **Fix C1**: Initialize `Limiter` and `SocketIO` in `app.py`
2. **Fix C2**: Implement `get_db()` connection factory in `app.py`
3. **Fix C3**: Fix `install.sh` password generation (broken `$()` syntax)
4. **Fix C4**: Fix `cleanup_old_events()` to modify global `events` (use `global` keyword)
5. **Fix S1-S4**: Replace all hardcoded default credentials with env-only config
6. Fix README (4 badges → 3 max)
7. Add `.dockerignore`, `j1.yaml`, `CODEOWNERS`
