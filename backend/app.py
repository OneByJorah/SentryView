"""
RTSP NVR Dashboard - Production Backend
Flask + JWT + Socket.IO + PostgreSQL + Redis
"""
import os
import sys
import logging
import hashlib
import hmac
import json
import subprocess
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import psycopg2
from psycopg2.extras import RealDictCursor
import redis

from apscheduler.schedulers.background import BackgroundScheduler

# ===== LOGGING =====
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/rtsp-nvr/backend/app.log') if os.path.exists('/var/log/rtsp-nvr/backend') else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ===== APP SETUP =====
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-to-a-random-secret')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://admin:***@localhost:5432/rtsp_nvr')
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:***@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_redis():
    if 'redis' not in g:
        g.redis = redis.Redis.from_url(app.config['REDIS_URL'], decode_responses=True)
    return g.redis

# ===== AUTH HELPERS =====
def hash_password(password):
    salt = app.config['SECRET_KEY'].encode()
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

def verify_password(password, hashed):
    return hmac.compare_digest(hash_password(password), hashed)

# ===== AUTH ROUTES =====
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, username, role, is_active, password_hash FROM users WHERE username = %s",
                (username,)
            )
            user = cur.fetchone()
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        if not user['is_active']:
            return jsonify({'error': 'Account inactive'}), 403
        token = create_access_token(identity=str(user['id']))
        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        if len(username) < 3 or len(username) > 80:
            return jsonify({'error': 'Username must be 3-80 characters'}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return jsonify({'error': 'Username already exists'}), 409
            password_hash = hash_password(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, role, is_active, created_at) VALUES (%s, %s, %s, %s, %s)",
                (username, password_hash, 'user', True, datetime.now())
            )
            db.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id, username, role, is_active, created_at FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'id': user['id'], 'username': user['username'], 'role': user['role'],
            'is_active': user['is_active'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None
        })
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@app.route('/api/auth/password', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per minute")
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
        if not user or not verify_password(current_password, user['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        new_hash = hash_password(new_password)
        with db.cursor() as cur:
            cur.execute("UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s", (new_hash, datetime.now(), user_id))
            db.commit()
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'error': 'Failed to change password'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully'})

# ===== STREAMS ROUTES =====
@app.route('/api/streams', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_streams():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT s.id, s.name, s.url, s.is_active, s.created_at, s.user_id, u.username as owner FROM streams s JOIN users u ON s.user_id = u.id WHERE s.user_id = %s ORDER BY s.created_at DESC",
                (user_id,)
            )
            streams = cur.fetchall()
        return jsonify({'streams': [{'id': s['id'], 'name': s['name'], 'url': s['url'], 'is_active': s['is_active'], 'created_at': s['created_at'].isoformat() if s['created_at'] else None, 'owner': s['owner']} for s in streams]})
    except Exception as e:
        logger.error(f"Get streams error: {e}")
        return jsonify({'error': 'Failed to get streams'}), 500

@app.route('/api/streams', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def add_stream():
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        if not name or not url:
            return jsonify({'error': 'Name and URL required'}), 400
        if not url.startswith('rtsp://'):
            return jsonify({'error': 'URL must start with rtsp://'}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute("INSERT INTO streams (user_id, name, url, is_active, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING id", (user_id, name, url, True, datetime.now()))
            stream_id = cur.fetchone()['id']
            db.commit()
        return jsonify({'message': 'Stream created', 'id': stream_id}), 201
    except Exception as e:
        logger.error(f"Add stream error: {e}")
        return jsonify({'error': 'Failed to create stream'}), 500

@app.route('/api/streams/<int:stream_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_stream(stream_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        is_active = data.get('is_active')
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT user_id FROM streams WHERE id = %s", (stream_id,))
            stream = cur.fetchone()
            if not stream:
                return jsonify({'error': 'Stream not found'}), 404
            updates = []
            params = []
            if name:
                updates.append("name = %s")
                params.append(name)
            if url:
                if not url.startswith('rtsp://'):
                    return jsonify({'error': 'URL must start with rtsp://'}), 400
                updates.append("url = %s")
                params.append(url)
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(bool(is_active))
            if updates:
                updates.append("updated_at = %s")
                params.append(datetime.now())
                params.append(stream_id)
                cur.execute("UPDATE streams SET " + ", ".join(updates) + " WHERE id = %s", params)
                db.commit()
        return jsonify({'message': 'Stream updated'})
    except Exception as e:
        logger.error(f"Update stream error: {e}")
        return jsonify({'error': 'Failed to update stream'}), 500

@app.route('/api/streams/<int:stream_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_stream(stream_id):
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT user_id FROM streams WHERE id = %s", (stream_id,))
            stream = cur.fetchone()
            if not stream:
                return jsonify({'error': 'Stream not found'}), 404
            cur.execute("DELETE FROM streams WHERE id = %s", (stream_id,))
            db.commit()
        return jsonify({'message': 'Stream deleted'})
    except Exception as e:
        logger.error(f"Delete stream error: {e}")
        return jsonify({'error': 'Failed to delete stream'}), 500

# ===== RECORDINGS ROUTES =====
@app.route('/api/recordings', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_recordings():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            query = "SELECT r.id, r.stream_id, r.event_id, r.started_at, r.stopped_at, r.duration, r.file_path, r.file_size, r.is_active, s.name as stream_name FROM recordings r JOIN streams s ON r.stream_id = s.id WHERE r.user_id = %s"
            params = [user_id]
            if 'type' in request.args:
                event_type = request.args.get('type')
                query += " AND r.event_id IN (SELECT id FROM events WHERE event_type = %s AND user_id = %s)"
                params.extend([event_type, user_id])
            if 'stream_id' in request.args:
                query += " AND r.stream_id = %s"
                params.append(int(request.args.get('stream_id')))
            if 'active' in request.args:
                query += " AND r.is_active = %s"
                params.append(request.args.get('active').lower() == 'true')
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)
            offset = (page - 1) * per_page
            query += " ORDER BY r.started_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            cur.execute(query, params)
            recordings = cur.fetchall()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM recordings WHERE user_id = %s", (user_id,))
            count = cur.fetchone()['cnt']
        return jsonify({
            'recordings': [{'id': r['id'], 'stream_id': r['stream_id'], 'stream_name': r['stream_name'], 'event_id': r['event_id'], 'started_at': r['started_at'].isoformat() if r['started_at'] else None, 'stopped_at': r['stopped_at'].isoformat() if r['stopped_at'] else None, 'duration': r['duration'].total_seconds() if r['duration'] else 0, 'file_path': r['file_path'], 'file_size': r['file_size'], 'is_active': r['is_active']} for r in recordings],
            'pagination': {'page': page, 'per_page': per_page, 'total': count, 'pages': (count + per_page - 1) // per_page}
        })
    except Exception as e:
        logger.error(f"Get recordings error: {e}")
        return jsonify({'error': 'Failed to get recordings'}), 500

@app.route('/api/recordings', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def start_recording():
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        stream_id = data.get('stream_id')
        if not stream_id:
            return jsonify({'error': 'stream_id required'}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id FROM streams WHERE id = %s", (stream_id,))
            if not cur.fetchone():
                return jsonify({'error': 'Stream not found'}), 404
            cur.execute("SELECT id FROM recordings WHERE stream_id = %s AND is_active = TRUE", (stream_id,))
            if cur.fetchone():
                return jsonify({'error': 'Recording already active for this stream'}), 409
            cur.execute("INSERT INTO recordings (user_id, stream_id, started_at, is_active) VALUES (%s, %s, %s, %s) RETURNING id", (user_id, stream_id, datetime.now(), True))
            recording_id = cur.fetchone()['id']
            cur.execute("INSERT INTO events (user_id, stream_id, event_type, description, created_at) VALUES (%s, %s, %s, %s, %s)", (user_id, stream_id, 'recording_started', 'Recording ' + str(recording_id) + ' started', datetime.now()))
            db.commit()
        socketio.emit('recording_update', {'type': 'recording_started', 'recording_id': recording_id, 'stream_id': stream_id, 'timestamp': datetime.now().isoformat()})
        return jsonify({'message': 'Recording started', 'id': recording_id})
    except Exception as e:
        logger.error(f"Start recording error: {e}")
        return jsonify({'error': 'Failed to start recording'}), 500

@app.route('/api/recordings/<int:recording_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per minute")
def stop_recording(recording_id):
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT stream_id, started_at FROM recordings WHERE id = %s AND is_active = TRUE", (recording_id,))
            recording = cur.fetchone()
            if not recording:
                return jsonify({'error': 'Recording not found or already stopped'}), 404
            duration = datetime.now() - recording['started_at']
            cur.execute("UPDATE recordings SET stopped_at = %s, duration = %s, is_active = FALSE WHERE id = %s", (datetime.now(), duration, recording_id))
            cur.execute("INSERT INTO events (user_id, stream_id, event_type, description, created_at) VALUES (%s, %s, %s, %s, %s)", (user_id, recording['stream_id'], 'recording_stopped', 'Recording ' + str(recording_id) + ' stopped', datetime.now()))
            db.commit()
        socketio.emit('recording_update', {'type': 'recording_stopped', 'recording_id': recording_id, 'duration': duration.total_seconds(), 'timestamp': datetime.now().isoformat()})
        return jsonify({'message': 'Recording stopped', 'duration': duration.total_seconds()})
    except Exception as e:
        logger.error(f"Stop recording error: {e}")
        return jsonify({'error': 'Failed to stop recording'}), 500

# ===== EVENTS ROUTES =====
@app.route('/api/events', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_events():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            query = "SELECT e.id, e.event_type, e.description, e.created_at, e.stream_id, e.metadata, s.name as stream_name FROM events e LEFT JOIN streams s ON e.stream_id = s.id WHERE e.user_id = %s"
            params = [user_id]
            if 'type' in request.args:
                query += " AND e.event_type = %s"
                params.append(request.args.get('type'))
            if 'stream_id' in request.args:
                query += " AND e.stream_id = %s"
                params.append(int(request.args.get('stream_id')))
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)
            offset = (page - 1) * per_page
            query += " ORDER BY e.created_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            cur.execute(query, params)
            events = cur.fetchall()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM events WHERE user_id = %s", (user_id,))
            count = cur.fetchone()['cnt']
        return jsonify({
            'events': [{'id': e['id'], 'event_type': e['event_type'], 'description': e['description'], 'created_at': e['created_at'].isoformat() if e['created_at'] else None, 'stream_id': e['stream_id'], 'stream_name': e['stream_name'], 'metadata': e['metadata']} for e in events],
            'pagination': {'page': page, 'per_page': per_page, 'total': count, 'pages': (count + per_page - 1) // per_page}
        })
    except Exception as e:
        logger.error(f"Get events error: {e}")
        return jsonify({'error': 'Failed to get events'}), 500

@app.route('/api/events', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_event():
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        event_type = data.get('event_type', '').strip()
        description = data.get('description', '').strip()
        stream_id = data.get('stream_id')
        metadata = data.get('metadata', {})
        valid_types = ['recording_started', 'recording_stopped', 'motion_detected', 'audio_exceeded', 'stream_connected', 'stream_disconnected', 'system_alert', 'manual_event']
        if event_type not in valid_types:
            return jsonify({'error': 'Invalid event_type'}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute("INSERT INTO events (user_id, stream_id, event_type, description, metadata, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (user_id, stream_id, event_type, description, json.dumps(metadata), datetime.now()))
            event_id = cur.fetchone()['id']
            db.commit()
        socketio.emit('new_event', {'id': event_id, 'event_type': event_type, 'description': description, 'stream_id': stream_id, 'timestamp': datetime.now().isoformat()})
        return jsonify({'message': 'Event created', 'id': event_id}), 201
    except Exception as e:
        logger.error(f"Create event error: {e}")
        return jsonify({'error': 'Failed to create event'}), 500

# ===== SCHEDULES ROUTES =====
@app.route('/api/schedules', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_schedules():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT s.id, s.name, s.stream_id, s.recording_type, s.cron_expression, s.start_time, s.end_time, s.is_active, s.created_at, st.name as stream_name FROM schedules s LEFT JOIN streams st ON s.stream_id = st.id WHERE s.user_id = %s ORDER BY s.created_at DESC", (user_id,))
            schedules = cur.fetchall()
        return jsonify({'schedules': [{'id': s['id'], 'name': s['name'], 'stream_id': s['stream_id'], 'stream_name': s['stream_name'], 'recording_type': s['recording_type'], 'cron_expression': s['cron_expression'], 'start_time': str(s['start_time']) if s['start_time'] else None, 'end_time': str(s['end_time']) if s['end_time'] else None, 'is_active': s['is_active'], 'created_at': s['created_at'].isoformat() if s['created_at'] else None} for s in schedules]})
    except Exception as e:
        logger.error(f"Get schedules error: {e}")
        return jsonify({'error': 'Failed to get schedules'}), 500

@app.route('/api/schedules', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_schedule():
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        stream_id = data.get('stream_id')
        recording_type = data.get('recording_type', 'video')
        cron_expression = data.get('cron_expression', '').strip()
        if not name or not stream_id or not cron_expression:
            return jsonify({'error': 'name, stream_id, and cron_expression required'}), 400
        valid_types = ['video', 'audio', 'both']
        if recording_type not in valid_types:
            return jsonify({'error': 'recording_type must be one of: ' + str(valid_types)}), 400
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id FROM streams WHERE id = %s", (stream_id,))
            if not cur.fetchone():
                return jsonify({'error': 'Stream not found'}), 404
            cur.execute("INSERT INTO schedules (user_id, stream_id, name, recording_type, cron_expression, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id", (user_id, stream_id, name, recording_type, cron_expression, True, datetime.now()))
            schedule_id = cur.fetchone()['id']
            db.commit()
        return jsonify({'message': 'Schedule created', 'id': schedule_id}), 201
    except Exception as e:
        logger.error(f"Create schedule error: {e}")
        return jsonify({'error': 'Failed to create schedule'}), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_schedule(schedule_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT user_id FROM schedules WHERE id = %s", (schedule_id,))
            if not cur.fetchone():
                return jsonify({'error': 'Schedule not found'}), 404
            updates = []
            params = []
            for field in ['name', 'recording_type', 'cron_expression']:
                if field in data:
                    updates.append(field + " = %s")
                    params.append(data[field])
            if 'is_active' in data:
                updates.append("is_active = %s")
                params.append(bool(data['is_active']))
            if updates:
                updates.append("updated_at = %s")
                params.append(datetime.now())
                params.append(schedule_id)
                cur.execute("UPDATE schedules SET " + ", ".join(updates) + " WHERE id = %s", params)
                db.commit()
        return jsonify({'message': 'Schedule updated'})
    except Exception as e:
        logger.error(f"Update schedule error: {e}")
        return jsonify({'error': 'Failed to update schedule'}), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_schedule(schedule_id):
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM schedules WHERE id = %s", (schedule_id,))
            if cur.rowcount == 0:
                return jsonify({'error': 'Schedule not found'}), 404
            db.commit()
        return jsonify({'message': 'Schedule deleted'})
    except Exception as e:
        logger.error(f"Delete schedule error: {e}")
        return jsonify({'error': 'Failed to delete schedule'}), 500

# ===== ANALYTICS ROUTES =====
@app.route('/api/analytics/overview', methods=['GET'])
@jwt_required()
@limiter.limit("10 per minute")
def get_analytics_overview():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total, COALESCE(SUM(is_active::int), 0) as active FROM streams WHERE user_id = %s", (user_id,))
            stream_stats = cur.fetchone()
            cur.execute("SELECT COUNT(*) as total, COALESCE(EXTRACT(EPOCH FROM SUM(duration)), 0) as total_seconds FROM recordings WHERE user_id = %s", (user_id,))
            recording_stats = cur.fetchone()
            cur.execute("SELECT event_type, COUNT(*) as count FROM events WHERE user_id = %s GROUP BY event_type", (user_id,))
            event_counts = cur.fetchall()
            cur.execute("SELECT DATE(started_at) as day, COUNT(*) as count FROM recordings WHERE user_id = %s AND started_at > NOW() - INTERVAL '7 days' GROUP BY DATE(started_at) ORDER BY day", (user_id,))
            daily_recordings = cur.fetchall()
        return jsonify({
            'streams': {'total': stream_stats['total'], 'active': int(stream_stats['active'])},
            'recordings': {'total': recording_stats['total'], 'total_seconds': float(recording_stats['total_seconds'] or 0)},
            'events': [{'type': e['event_type'], 'count': e['count']} for e in event_counts],
            'daily_recordings': [{'day': str(d['day']), 'count': d['count']} for d in daily_recordings]
        })
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        return jsonify({'error': 'Failed to get analytics'}), 500

# ===== BACKUP ROUTES =====
@app.route('/api/backup', methods=['POST'])
@jwt_required()
@limiter.limit("2 per hour")
def create_backup():
    backup_dir = Path('/var/backups/rtsp-nvr')
    backup_dir.mkdir(parents=True, exist_ok=True)
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / ('backup_' + timestamp + '.dump')
        db_url = app.config['DATABASE_URL']
        result = subprocess.run(['pg_dump', '--format=custom', '--file', str(backup_file), db_url], capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error("pg_dump failed: " + result.stderr)
            return jsonify({'error': 'Backup failed'}), 500
        backups = sorted(backup_dir.glob('backup_*.dump'), key=lambda p: p.stat().st_mtime)
        for old_backup in backups[:-30]:
            old_backup.unlink()
        file_size = backup_file.stat().st_size
        return jsonify({'message': 'Backup created', 'path': str(backup_file), 'size': file_size, 'timestamp': timestamp})
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Backup timed out'}), 504
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'error': 'Backup failed'}), 500

@app.route('/api/backup', methods=['GET'])
@jwt_required()
def list_backups():
    backup_dir = Path('/var/backups/rtsp-nvr')
    if not backup_dir.exists():
        return jsonify({'backups': []})
    backups = []
    for f in sorted(backup_dir.glob('backup_*.dump'), key=lambda p: p.stat().st_mtime, reverse=True):
        backups.append({'filename': f.name, 'size': f.stat().st_size, 'created': datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    return jsonify({'backups': backups})

# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health_check():
    status = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT 1")
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = 'error: ' + str(e)
        status['status'] = 'unhealthy'
    try:
        r = get_redis()
        r.ping()
        status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = 'error: ' + str(e)
    status_code = 200 if status['status'] == 'healthy' else 503
    return jsonify(status), status_code

# ===== WEBSOCKET HANDLERS =====
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('stream_status')
def handle_stream_status(data):
    stream_id = data.get('stream_id')
    status = data.get('status')
    join_room('stream_' + str(stream_id))
    emit('stream_update', {'stream_id': stream_id, 'status': status, 'timestamp': datetime.now().isoformat()})

@socketio.on('event_update')
def handle_event_update(data):
    event = data.get('event')
    emit('new_event', event, broadcast=True)

# ===== BACKGROUND TASKS =====
scheduler = BackgroundScheduler()

@scheduler.job(id='cleanup_old_records', trigger='cron', hour=2, minute=0)
def cleanup_old_records():
    try:
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        with conn.cursor() as cur:
            cur.execute("DELETE FROM recordings WHERE is_active = FALSE AND stopped_at < NOW() - INTERVAL '30 days'")
            deleted_r = cur.rowcount
            cur.execute("DELETE FROM events WHERE created_at < NOW() - INTERVAL '7 days'")
            deleted_e = cur.rowcount
            conn.commit()
        conn.close()
        logger.info("Cleanup: removed %d recordings, %d events", deleted_r, deleted_e)
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

scheduler.start()

# ===== ERROR HANDLERS =====
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# ===== SERVE FRONTEND =====
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and Path(app.static_folder + '/' + path).exists():
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
