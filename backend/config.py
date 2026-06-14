"""
Configuration management for RTSP NVR Dashboard.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# ===== DATABASE =====
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/rtsp_nvr")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ===== AUTHENTICATION =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = os.getenv("JWT_EXPIRY_HOURS", "24")
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "password-salt-change-in-production")

# ===== NETWORKING =====
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Tailscale Support
TAILSCALE_ENABLED = os.getenv("TAILSCALE_ENABLED", "false").lower() == "true"
TAILSCALE_API_KEY = os.getenv("TAILSCALE_API_KEY", "")
TAILSCALE_GROUP = os.getenv("TAILSCALE_GROUP", "rtsp-nvr")
TAILSCALE_SUBNET_Routes = os.getenv("TAILSCALE_SUBNET_ROUTES", "")

# ===== CORS =====
CORS_ORIGINS = os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")

# ===== SECURITY =====
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_MINUTES = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "15"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

# ===== STORAGE =====
VIDEO_STORAGE_PATH = os.getenv("VIDEO_STORAGE_PATH", "/data/videos")
EVENT_STORAGE_PATH = os.getenv("EVENT_STORAGE_PATH", "/data/events")
RECORDING_STORAGE_PATH = os.getenv("RECORDING_STORAGE_PATH", "/data/recordings")
BACKUP_STORAGE_PATH = os.getenv("BACKUP_STORAGE_PATH", "/data/backups")

# ===== MEDIA SERVER =====
RTSP_PORT = int(os.getenv("RTSP_PORT", "8554"))
RTSP_USERNAME = os.getenv("RTSP_USERNAME", "admin")
RTSP_PASSWORD = os.getenv("RTSP_PASSWORD", "admin")

# ===== STREAM SETTINGS =====
MAX_STREAMS = int(os.getenv("MAX_STREAMS", "10"))
STREAM_TIMEOUT_SECONDS = int(os.getenv("STREAM_TIMEOUT_SECONDS", "300"))
RECONNECT_INTERVAL_SECONDS = int(os.getenv("RECONNECT_INTERVAL_SECONDS", "30"))

# ===== RECORDING SETTINGS =====
AUDIO_THRESHOLD_DB = float(os.getenv("AUDIO_THRESHOLD_DB", "70.0"))
MOTION_SENSITIVITY = float(os.getenv("MOTION_SENSITIVITY", "0.5"))
RECORDING_RETENTION_DAYS = int(os.getenv("RECORDING_RETENTION_DAYS", "7"))
EVENT_RETENTION_DAYS = int(os.getenv("EVENT_RETENTION_DAYS", "30"))
MAX_RECORDING_SIZE_MB = int(os.getenv("MAX_RECORDING_SIZE_MB", "1000"))

# ===== NOTIFICATIONS =====
NOTIFICATION_ENABLED = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
NOTIFICATION_EMAIL_PASSWORD = os.getenv("NOTIFICATION_EMAIL_PASSWORD", "")
NOTIFICATION_EMAIL_FROM = os.getenv("NOTIFICATION_EMAIL_FROM", "NVR Dashboard <noreply@example.com>")

# ===== WEBSOCKET =====
WEBSOCKET_ENABLED = os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true"
WEBSOCKET_HEARTBEAT_INTERVAL = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
WEBSOCKET_MAX_SIZE = int(os.getenv("WEBSOCKET_MAX_SIZE", "10485760"))  # 10MB

# ===== ANALYTICS =====
ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "7"))

# ===== LOGGING =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "/var/log/rtsp-nvr/app.log")
AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"

# ===== BACKUP =====
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
BACKUP_SCHEDULE = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

# ===== CACHE =====
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
