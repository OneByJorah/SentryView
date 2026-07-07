# Changelog

All notable changes to this project will be documented in this file.

## [2.1.1] - 2026-07-07

### Added
- Dockerfile improvements (backend, frontend, ffmpeg)
- docker-compose.yml with healthchecks
- .env.example with placeholder values

### Fixed

- **CRITICAL:** Initialized `Limiter` and `SocketIO` instances in `app.py` — all rate-limited routes and WebSocket handlers were crashing
- **CRITICAL:** Implemented `get_db()` connection factory in `app.py` — every API route was failing with `NameError`
- **CRITICAL:** Fixed `install.sh` password generation (broken `$()` syntax was writing literal `***` instead of random values)
- **CRITICAL:** Fixed `cleanup_old_events()` global variable shadowing in `ffmpeg/processor.py` — added `global events` keyword
- Removed hardcoded `admin`/`admin` default credentials from `init-db.sql` — first user must register via API
- Fixed all hardcoded default credentials in `backend/config.py` — defaults are now empty (must be set via env)
- Added `psycopg2.extras` import with `RealDictCursor` for proper dict-like row access

### Security

- Removed default `admin`/`admin` seed user from `init-db.sql`
- Replaced all weak default passwords with empty-env-required defaults
- Changed `SECRET_KEY` and `JWT_SECRET_KEY` defaults to use `os.urandom()`

### Added

- `.dockerignore` to prevent build context leaks
- `j1.yaml` for pipeline registry metadata
- `.github/CODEOWNERS` for PR routing
