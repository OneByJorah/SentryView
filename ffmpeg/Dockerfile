# =============================================================================
# SentryView FFmpeg Processor — Python + FFmpeg
# Tag convention: jorahone/sentryview-ffmpeg:latest
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories and non-root user
RUN mkdir -p /recordings /output && \
    addgroup --system --gid 1001 sentryview && \
    adduser --system --uid 1001 --ingroup sentryview --no-create-home sentryview && \
    chown -R sentryview:sentryview /app /recordings /output

USER sentryview

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" || exit 1

LABEL org.opencontainers.image.title="SentryView FFmpeg Processor" \
      org.opencontainers.image.description="FFmpeg processing container for SentryView" \
      org.opencontainers.image.vendor="JorahOne" \
      org.opencontainers.image.version="2.1.0"

CMD ["python", "processor.py"]
