#!/usr/bin/env python3
"""
FFmpeg RTSP Stream Processor
Handles live streaming, audio analysis, and recording
"""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
RTSP_URL = os.environ.get('RTSP_URL', 'rtsp://admin:admin@192.168.1.10:554/stream')
AUDIO_THRESHOLD_DB = float(os.environ.get('AUDIO_THRESHOLD_DB', 30))
RECORDING_RETENTION_DAYS = int(os.environ.get('RECORDING_RETENTION_DAYS', 7))
MAX_RECORDINGS = int(os.environ.get('MAX_RECORDINGS', 10))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
recording_session = {
    'active': False,
    'id': None,
    'start_time': None,
    'path': None,
    'ffmpeg': None
}

events = []
event_file = Path('/events/events.json')

def save_event(event_type, description='', metadata={}):
    """Save event to file"""
    event = {
        'id': len(events) + 1,
        'type': event_type,
        'timestamp': datetime.now().isoformat(),
        'description': description,
        'metadata': metadata
    }
    events.append(event)
    
    try:
        with open(event_file, 'w') as f:
            json.dump(events, f, indent=2)
    except Exception as e:
        logger.error(f'Failed to save event: {e}')

def cleanup_old_recordings():
    """Remove old recordings based on retention policy"""
    recordings_dir = Path('/recordings')
    if not recordings_dir.exists():
        return
    
    cutoff_time = time.time() - (RECORDING_RETENTION_DAYS * 86400)
    
    for f in recordings_dir.glob('*.mp4'):
        if f.stat().st_mtime < cutoff_time:
            try:
                f.unlink()
                logger.info(f'Cleaned up old recording: {f.name}')
            except Exception as e:
                logger.error(f'Failed to delete {f.name}: {e}')

def cleanup_old_events():
    """Remove old events based on max count"""
    if len(events) > MAX_RECORDINGS:
        events = events[-MAX_RECORDINGS:]
        
        try:
            with open(event_file, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.error(f'Failed to update events: {e}')

def stop_recording():
    """Stop current recording"""
    if recording_session['ffmpeg']:
        try:
            recording_session['ffmpeg'].terminate()
            recording_session['ffmpeg'].wait(timeout=5)
            recording_session['ffmpeg'] = None
            logger.info('Stopped recording')
        except Exception as e:
            logger.error(f'Error stopping recording: {e}')
    
    recording_session['active'] = False
    recording_session['id'] = None

def run_ffmpeg_stream():
    """Main FFmpeg loop for live streaming and recording"""
    logger.info(f'Starting FFmpeg processor for {RTSP_URL}')
    
    # Test connection first
    test_cmd = ['ffmpeg', '-stats', '-i', RTSP_URL, '-f', 'null', '-']
    try:
        result = subprocess.run(test_cmd, timeout=5, capture_output=True)
        if result.returncode != 0:
            logger.error(f'Failed to connect to RTSP: {result.stderr.decode()}')
            return
        logger.info('RTSP connection successful')
    except Exception as e:
        logger.error(f'Connection test failed: {e}')
        return
    
    # Start live streaming for dashboard
    nvr_url = os.environ.get('NVR_URL', RTSP_URL)
    stream_cmd = [
        'ffmpeg',
        '-i', nvr_url,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-c:a', 'aac',
        '-f', 'flv',
        'rtmp://127.0.0.1/live/stream'
    ]
    
    stream_process = subprocess.Popen(
        stream_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    logger.info('Live stream started')
    
    # Cleanup loop
    while True:
        try:
            cleanup_old_recordings()
            cleanup_old_events()
            time.sleep(60)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f'Cleanup error: {e}')
            time.sleep(10)

def main():
    """Main entry point"""
    logger.info('Starting FFmpeg RTSP Processor')
    logger.info(f'RTSP URL: {RTSP_URL}')
    logger.info(f'Audio threshold: {AUDIO_THRESHOLD_DB} dB')
    logger.info(f'Retention: {RECORDING_RETENTION_DAYS} days')
    logger.info(f'Max recordings: {MAX_RECORDINGS}')
    
    # Start the main loop
    try:
        run_ffmpeg_stream()
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        stop_recording()
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        stop_recording()

if __name__ == '__main__':
    main()
