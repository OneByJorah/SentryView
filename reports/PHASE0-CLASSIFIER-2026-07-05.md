# Phase 0 CLASSIFIER — SentryView

**Date:** 2026-07-05
**Analyst:** J1-PIPELINE CLASSIFIER

## Classification

**Primary Class:** `Web`
**Secondary Classes:** `Docker`, `Python`, `Security`

## Rationale

| Criterion | Evidence | Classification |
|-----------|----------|---------------|
| Tech stack | React 18 SPA (frontend) + Flask REST API (backend) | **Web** |
| Deployment | Docker Compose with 6 services, Nginx reverse proxy | **Docker** |
| Backend language | Python 3.11, Flask, Gunicorn, Eventlet | **Python** |
| Domain | IP camera surveillance, RTSP stream processing, JWT auth | **Security** |
| Frontend | React SPA with Socket.IO, recharts, hls.js | **Web** |
| Infrastructure | PostgreSQL, Redis, FFmpeg processing | **Docker** |

## Gating

- **Docker hardening checklist:** APPLIES
- **Security checklist:** APPLIES
- **Web security checklist:** APPLIES
- **Python lint/formatting:** APPLIES
- **JavaScript lint/formatting:** APPLIES
