# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-07-05
### Added
- Real-time WebSocket support via Socket.IO
- Redis pub/sub for cross-instance event broadcasting
- Analytics dashboard with stream counts, recording hours, event breakdowns
- Scheduled recording with cron expressions
- Backup & restore API with 30-day retention
- Tailscale integration for secure remote access
- Proxmox container template installer
- Health checks on all services
- Rate limiting on all API endpoints
- JWT-based authentication with role-based access

### Changed
- Production web server: Gunicorn + Eventlet (not Flask dev server)
- Nginx reverse proxy for frontend with WebSocket upgrade support
- Database schema with proper foreign keys, indexes, and triggers
- Password hashing via PBKDF2-SHA256 with 100,000 iterations
- Docker Compose v5 with named volumes and health checks

### Fixed
- Missing imports and initializations for limiter, socketio, get_db, JWTManager
- Shell syntax errors in install.sh (template redaction artifacts)
- Hardcoded credentials in source code
- Dependabot directory paths to match actual project structure
- Removed unused dependencies (bcrypt, axios)
- README FastAPI references corrected to Flask
- Added health checks to ffmpeg and backup services

## [1.0.0] - 2026-07-04
### Added
- Initial release
