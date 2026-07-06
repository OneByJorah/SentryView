<!-- j1-brand:v2 -->
<div align="center">

# SentryView

A modern, web-based RTSP NVR dashboard for Linux with audio + video streaming, event-based recording, timeline playback, and volume-triggered audio capture.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2FSentryView-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/SentryView)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/Python-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://python.org)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

Commercial NVRs lock you into expensive hardware and proprietary ecosystems. SentryView is a vendor-agnostic, self-hosted alternative that works with any RTSP camera. Built with a React frontend, async FastAPI backend, and FFmpeg for stream processing — all containerized for one-command deployment on any Linux machine.

## Key Features

| Feature | Why It Matters |
|---|---|
| Live RTSP streaming | Watch any IP camera in your browser in real time |
| Timeline playback | Scrub through recorded footage with frame-level precision |
| Event-based recording | Saves clips on motion or schedule — not 24/7 garbage |
| Audio + video capture | Volume-triggered audio recording alongside video streams |
| H.264/H.265 transcoding | FFmpeg handles any codec your cameras throw at it |
| Fully containerized | `docker compose up` on any Linux host — no manual dependency wrangling |

## Quick Start

```bash
git clone https://github.com/OneByJorah/SentryView.git
cd SentryView
./install.sh           # automated setup
# — or —
docker compose up -d   # containerized deployment
```

## Architecture

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│  Camera    │────▶│  FFmpeg   │────▶│  Backend   │
│  (RTSP)    │     │  transcoder │    │  FastAPI   │
└───────────┘     └───────────┘     └─────┬─────┘
                                          │
                                   ┌──────▼──────┐
                                   │  React       │
                                   │  Frontend    │
                                   └─────────────┘
```

## Documentation

| Doc | Description |
|---|---|
| [Installation Guide](docs/install.md) | System requirements and deployment options |
| [Camera Configuration](docs/cameras.md) | Adding and tuning RTSP camera sources |
| [Proxmox Integration](docs/proxmox.md) | Running SentryView on Proxmox LXC |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
