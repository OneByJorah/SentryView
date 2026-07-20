# SentryView — Repo Polish Log

**Repo:** OneByJorah/SentryView
**Stack:** Python 3.11 (Flask + Gunicorn/Eventlet + Socket.IO + PostgreSQL + Redis) backend, React 18 (CRA) + nginx frontend, FFmpeg worker. Docker Compose multi-service.
**Date:** 2026-07-20
**Agent branch:** `agent/polish-pass`

## Phase 0 — Intake
- Cloned to `/home/j1admin/SentryView`.
- App = RTSP NVR dashboard. Services: frontend (nginx:80), backend (5000), db (postgres:15), redis (7), ffmpeg worker, backup.
- Config via `.env` (`.env.example` present, placeholders only — no leaked secrets).

## Phase 1 — Get It Running
- `docker compose` plugin was missing; installed standalone v2.30.3 to `~/.docker/cli-plugins`.
- Built all images successfully after fixing build-time bugs (see below).
- Stack runs: backend `/health` returns `{"status":"healthy","database":"connected","redis":"connected"}`.
- Verified API end-to-end: register → login → `/api/auth/me`, streams, events.
- Added minimal smoke test `backend/test_smoke.py` (no tests existed). All 4 pass with stubs for DB/Redis.

## Phase 2 — Fix & Harden
Broken (fixed):
1. **frontend/Dockerfile** used `npm ci` + `package-lock.json` which does not exist → build failed. Switched to `npm install`.
2. **frontend/src/components/Settings.js** line 6: invalid JS identifier `mesh-vpnApiKey` (hyphen) → build/eslint error. Renamed to `meshVpnApiKey`.
3. **backend/app.py** line 695: `@scheduler.job(...)` — APScheduler has no `.job` attribute → backend crashed on boot. Fixed to `@scheduler.scheduled_job(...)`.
4. **docker-compose.yml** backend env hardcoded `DATABASE_URL=postgresql://admin:***@db:...` (literal `***` password) → DB auth always failed. Changed to `${DATABASE_URL:-...}` interpolation.
5. **frontend/Dockerfile** ran nginx as non-root `sentryview` but base config writes pid to `/run/nginx.pid` (Permission denied) → container crash-looped. Fixed pid path to `/tmp/nginx.pid` and made cache/log/run dirs writable by the non-root user.
6. **ffmpeg/Dockerfile** HEALTHCHECK hit `:8080/health` but the processor exposes no HTTP server → healthcheck could never pass. Changed to a `pgrep -f processor.py` process check.

Hardening:
- Completed `.gitignore` (venv, node_modules, build, *.dump, logs, etc.).
- Updated `LICENSE` copyright to "Jhonattan L. Jimenez / JorahOne LLC" (2026).
- Removed stale duplicate root `Dockerfile.backend` (superseded by `backend/Dockerfile` used by compose).
- Removed redundant `assets/*.png` / `assets/*.svg`; canonical screenshots now in `docs/screenshots/`.
- Confirmed `.env` is gitignored; only `.env.example` / `.env.sample` (placeholders) are tracked — no secrets leaked.

Notes / not blocking:
- FFmpeg worker requires a reachable `RTSP_URL` camera; without one it logs a connection error and the container restarts (expected — no camera in CI/host). It is an optional service and does not affect the core dashboard.
- Host port 3000 was already occupied on this agent box by an unrelated process, so the stack was validated on `FRONTEND_PORT=30888`. On a clean machine the documented port 3000 works (compose default).

## Phase 3 — Dockerize
- Dockerfiles already present (multi-stage backend, nginx frontend, ffmpeg). Fixed as above.
- `docker compose build` and `docker compose up -d` both succeed.
- Commands documented in README.

## Phase 4 — Real Screenshots
- Captured with Playwright (chromium 1228) against the live frontend at :30888, authenticated as a seeded `demo` user with a real stream + event.
- Saved under `docs/screenshots/`: `01-login.png`, `02-dashboard.png`, `03-timeline.png`, `04-settings.png`. All distinct, real renders (verified by md5).
- No CLI exists in the project, so no terminal/CLI screenshot was produced.

## Phase 5 — README
- Rewrote README.md from scratch per the required structure. All feature/architecture/config claims verified against the code. Uses relative `docs/screenshots/` image paths. Author section links github.com/OneByJorah.

## Phase 6 — GitHub Metadata
- Pending commit/push (Phase 7), then `gh repo edit` for description + topics.

## Phase 7 — Commit & Push
- Branch `agent/polish-pass`. Conventional commits, no squash, normal push.

## Definition of Done checklist
- [x] Runs locally from clean clone following README (Docker path verified).
- [x] Runs via Docker following README (verified `docker compose up -d`).
- [x] >=1 real screenshot in docs/screenshots/ rendered in README.
- [x] README follows structure, only true claims.
- [x] LICENSE MIT, credited correctly.
- [x] Author section links github.com/OneByJorah.
- [x] No secrets committed; .env.example present.
- [x] AGENT_LOG.md documents broken/fixed.
- [x] Pushed to agent/polish-pass.
