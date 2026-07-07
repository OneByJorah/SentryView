# =============================================================================
# SentryView Backend — Flask + Gunicorn + Eventlet
# Tag convention: jorahone/sentryview-backend:latest
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Production stage ────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directories and non-root user
RUN mkdir -p /recordings /events /var/backups/rtsp-nvr /var/log/rtsp-nvr/backend && \
    addgroup --system --gid 1001 sentryview && \
    adduser --system --uid 1001 --ingroup sentryview --no-create-home sentryview && \
    chown -R sentryview:sentryview /app /recordings /events /var/backups/rtsp-nvr /var/log/rtsp-nvr

USER sentryview

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=30s \
    CMD wget --spider -q http://localhost:5000/health || exit 1

LABEL org.opencontainers.image.title="SentryView Backend" \
      org.opencontainers.image.description="Flask backend for SentryView RTSP NVR" \
      org.opencontainers.image.vendor="JorahOne" \
      org.opencontainers.image.version="2.1.0"

# Run with gunicorn in production, flask dev server in debug mode
CMD ["sh", "-c", "if [ \"${FLASK_DEBUG:-false}\" = \"true\" ]; then python app.py; else gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - app:app; fi"]
