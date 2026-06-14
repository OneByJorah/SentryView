#!/usr/bin/env python3
"""
RTSP NVR Dashboard - Backend API Server
Provides authentication, stream management, and event handling
"""

import os
import json
import bcrypt
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
config = {
    'HOST': os.environ.get('HOST_IP', '0.0.0.0'),
    'PORT': 5000,
    'ADMIN_USER': os.environ.get('ADMIN_USER', 'admin'),
    'ADMIN_PASSWORD': os.environ.get('ADMIN_PASSWORD', 'admin')
}

# Ensure directories exist
RECORDINGS_DIR = Path('/recordings')
EVENTS_DIR = Path('/events')
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_DIR.mkdir(parents=True, exist_ok=True)

# Hash password for demo (replace with bcrypt hash in production)
ADMIN_PASSWORD_HASH = bcrypt.hashpw(
    config['ADMIN_PASSWORD'].encode(),
    bcrypt.gensalt()
).decode()

# Store active recording session
recording_session = {
    'active': False,
    'id': None,
    'start_time': None,
    'trigger': None  # 'audio' or 'scheduled'
}

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if username != config['ADMIN_USER']:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not verify_password(password, ADMIN_PASSWORD_HASH):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': username,
        'token': f"Bearer {datetime.now().isoformat()}"
    }), 200

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated (protected route)"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user': config['ADMIN_USER']
    }), 200

@app.route('/api/stream/status', methods=['GET'])
def stream_status():
    """Get RTSP stream status"""
    return jsonify({
        'url': os.environ.get('NVR_URL', 'N/A'),
        'connected': 'unknown',
        'latency_ms': 0,
        'fps': 0,
        'audio_active': False,
        'volume_db': 0
    })

@app.route('/api/stream/controls', methods=['POST'])
def stream_controls():
    """Control stream (pause, resume, etc.)"""
    data = request.get_json() or {}
    action = data.get('action', '')
    
    actions = ['pause', 'resume', 'seek']
    if action not in actions:
        return jsonify({'error': f'Unknown action: {action}'}), 400
    
    return jsonify({
        'action': action,
        'status': 'queued',
        'message': f'{action.capitalize()} request received'
    }), 202

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recordings"""
    recordings = []
    
    if RECORDINGS_DIR.exists():
        for f in RECORDINGS_DIR.glob('*.mp4'):
            recordings.append({
                'id': f.stem,
                'filename': f.name,
                'size_bytes': f.stat().st_size,
                'created': f.stat().st_ctime,
                'modified': f.stat().st_mtime,
                'duration': 0  # Would calculate from file metadata
            })
    
    return jsonify({
        'recordings': recordings,
        'total': len(recordings)
    }), 200

@app.route('/api/recordings', methods=['POST'])
def start_recording():
    """Start a new recording session"""
    data = request.get_json() or {}
    trigger = data.get('trigger', 'manual')
    
    recording_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    recording_path = RECORDINGS_DIR / f'{recording_id}.mp4'
    
    # Initialize empty recording file
    if not recording_path.exists():
        recording_path.touch()
    
    recording_session = {
        'active': True,
        'id': recording_id,
        'start_time': datetime.now().isoformat(),
        'trigger': trigger,
        'path': str(recording_path)
    }
    
    return jsonify({
        'status': 'recording',
        'id': recording_id,
        'path': recording_path,
        'start_time': recording_session['start_time']
    }), 201

@app.route('/api/recordings/<recording_id>', methods=['DELETE'])
def stop_recording(recording_id):
    """Stop recording and finalize file"""
    if not recording_session['active']:
        return jsonify({'error': 'No active recording'}), 404
    
    recording_path = Path(recording_session['path'])
    if recording_path.exists():
        # Here you would run FFmpeg to finalize the recording
        # For now, just log
        pass
    
    recording_session['active'] = False
    recording_session['end_time'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'stopped',
        'id': recording_id
    }), 200

@app.route('/api/events', methods=['GET'])
def list_events():
    """List all events"""
    events = []
    
    event_file = EVENTS_DIR / 'events.json'
    if event_file.exists():
        try:
            with open(event_file, 'r') as f:
                events = json.load(f)
        except:
            events = []
    
    return jsonify({
        'events': events,
        'total': len(events)
    }), 200

@app.route('/api/events', methods=['POST'])
def add_event():
    """Add a new event"""
    data = request.get_json() or {}
    event_type = data.get('type', 'unknown')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    description = data.get('description', '')
    metadata = data.get('metadata', {})
    
    event_file = EVENTS_DIR / 'events.json'
    
    try:
        events = []
        if event_file.exists():
            with open(event_file, 'r') as f:
                events = json.load(f)
    except:
        events = []
    
    new_event = {
        'id': len(events) + 1,
        'type': event_type,
        'timestamp': timestamp,
        'description': description,
        'metadata': metadata
    }
    
    events.append(new_event)
    
    with open(event_file, 'w') as f:
        json.dump(events, f, indent=2)
    
    return jsonify({
        'event': new_event,
        'total': len(events)
    }), 201

@app.route('/api/audio/threshold', methods=['GET', 'PUT'])
def audio_threshold():
    """Get/set audio volume threshold"""
    threshold_db = float(os.environ.get('AUDIO_THRESHOLD_DB', 30))
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        new_threshold = float(data.get('threshold', threshold_db))
        os.environ['AUDIO_THRESHOLD_DB'] = str(new_threshold)
        threshold_db = new_threshold
    
    return jsonify({
        'threshold_db': threshold_db
    }), 200

@app.route('/api/schedule', methods=['GET', 'POST', 'DELETE'])
def schedule():
    """Manage scheduled recordings"""
    schedule_file = Path('/schedule.json')
    
    if request.method == 'POST':
        data = request.get_json() or {}
        schedule = {
            'id': len(data) + 1 if isinstance(data, list) else 1,
            **data
        }
        
        if not schedule_file.exists():
            data = []
        
        data.append(schedule)
        with open(schedule_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'schedule': schedule}), 201
    
    elif request.method == 'DELETE':
        if not schedule_file.exists():
            return jsonify({'error': 'No schedule found'}), 404
        
        with open(schedule_file, 'r') as f:
            schedule_list = json.load(f)
        
        data = request.get_json() or {}
        schedule_id = data.get('id')
        
        schedule_list = [s for s in schedule_list if s.get('id') != schedule_id]
        
        with open(schedule_file, 'w') as f:
            json.dump(schedule_list, f, indent=2)
        
        return jsonify({'status': 'deleted'}), 200
    
    elif request.method == 'GET':
        if not schedule_file.exists():
            return jsonify({'schedule': []}), 200
        
        with open(schedule_file, 'r') as f:
            schedule_list = json.load(f)
        
        return jsonify({'schedule': schedule_list}), 200
    
    return jsonify({'error': 'Invalid method'}), 405

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'recording_active': recording_session['active']
    }), 200

if __name__ == '__main__':
    print(f"Starting RTSP NVR Dashboard Backend")
    print(f"Host: {config['HOST']}:{config['PORT']}")
    print(f"Recording directory: {RECORDINGS_DIR}")
    print(f"Event directory: {EVENTS_DIR}")
    
    app.run(host=config['HOST'], port=config['PORT'], debug=False)
