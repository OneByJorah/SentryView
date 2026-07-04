# SentryView

> Modern web-based RTSP NVR dashboard for Linux with audio/video streaming.

![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-%23FFB300?style=for-the-badge)
![Language](https://img.shields.io/badge/language-Python-informational?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-linux-informational?style=for-the-badge)

SentryView is an enterprise-grade, ops-precise platform built for VIDE and SMB operations. Run it solo. Deliver results.

- **Live monitoring**: multiple RTSP camera streams in one dashboard.
- **Playback + timeline**: review recorded segments by time.
- **Settings management**: stream and recording configuration UI.
- **FFmpeg pipeline**: hardware-friendly transcoding and processing container.
- **Proxmox-ready**: dedicated install script for container deployment.
- **Docker Compose**: multi-service deploy with backend, frontend, and ffmpeg.

---

## Architecture

Client browser → React frontend (`frontend/`) → Nginx → FastAPI backend (`backend/app.py`) → FFmpeg processor (`ffmpeg/processor.py`) → RTSP streams.

Additional capabilities:
- Proxmox container bootstrap (`proxmox/install-ct.sh`)
- Database init via `init-db.sql`
- Config via `backend/config.py`

---

| Layer | Stack |
|---|---|
| Runtime | Linux (Ubuntu 22.04+, Docker, Proxmox) |
| Frontend | React |
| Backend | Python / FastAPI |
| Media | FFmpeg (RTSP capture + processing) |
| Reverse Proxy | Nginx (`frontend/nginx.conf`) |
| Database | SQL (via `init-db.sql`) |
| VCS | Git + GitHub (`github.com/OneByJorah/SentryView`) |

---

## Quickstart

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView
docker compose up -d
```
Verify at `http://<host-ip>`.

## Configuration

Environment variables are documented in-repo. See [Environment Variables](#environment-variables) for the full table.

## Roadmap

- Feature parity with production requirements
- Observability and alerting expansions
- Community feedback integration

## License

MIT — Copyright JorahOne, LLC. See [LICENSE](LICENSE) for details.

---

[OneByJorah](https://github.com/OneByJorah) · [JorahOne-Services](https://github.com/JorahOne-Services)
