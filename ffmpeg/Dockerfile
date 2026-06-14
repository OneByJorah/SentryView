# FFmpeg Container for RTSP Processing
FROM python:3.11-slim

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /recordings

# Expose port for health checks
EXPOSE 8080

# Run the FFmpeg processor
CMD ["python", "processor.py"]
