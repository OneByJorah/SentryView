# Backend API Server - Production
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /recordings /events /var/backups/rtsp-nvr /var/log/rtsp-nvr/backend

# Expose backend port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=30s \
    CMD wget --spider -q http://localhost:5000/health || exit 1

# Run with gunicorn in production, flask dev server in debug mode
CMD ["sh", "-c", "if [ \"${FLASK_DEBUG:-false}\" = \"true\" ]; then python app.py; else gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - app:app; fi"]
