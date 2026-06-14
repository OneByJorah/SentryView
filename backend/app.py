"""
RTSP NVR Dashboard - Enhanced Backend with Tailscale, WebSocket, Analytics, Backup & More
"""
import os
import sys
import logging
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Flask imports
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database & Redis
import psycopg2
from psycopg2.extras import RealDictCursor
import redis

# Background tasks
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-in-production')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://admin:***@localhost:5432/rtsp_nvr')
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize extensions
jwt = JWTManager(app)
limiter = Limiter(key_func=get_remote_address, app=app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ===== LOGGING =====
log_dir = Path('/var/log/rtsp-nvr')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== DATABASE FUNCTIONS =====
def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(app.config['DATABASE_URL'])
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ===== AUTHENTICATION =====
def hash_password(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'secret_salt', 100000).hex()

def verify_password(password, hashed):
    return hmac.compare_digest(hash_password(password), hashed)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login with username/password."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, username, role, is_active, password_hash FROM users WHERE username = %s",
                (username,)
            )
            user = cur.fetchone()
        
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Account inactive'}), 403
        
        token = create_access_token(identity=user['id'])
        
        return jsonify({
            'access_token': token,
            'token_type': 'JWT',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register new user."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return jsonify({'error': 'Username already exists'}), 409
            
            password_hash = hash_password(password)
            cur.execute(
                """INSERT INTO users (username, password_hash, role, is_active, created_at)
                   VALUES (%s, %s, %s, %s, %s)""",
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
    """Get current user info."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, username, role, is_active, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            user = cur.fetchone()
        
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'is_active': user['is_active'],
            'created_at': user['created_at'].isoformat()
        })
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout."""
    return jsonify({'message': 'Logged out successfully'})

# ===== TAILSCALE NETWORKING =====
class TailscaleManager:
    """Manage Tailscale networking for secure remote access."""
    
    def __init__(self):
        self.tailnet_id = os.getenv('TAILSCALE_TAILNET_ID')
        self.api_key = os.getenv('TAILSCALE_API_KEY')
        self.api_url = "https://api.tailscale.com/api/v2"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def is_tailscale_network(self):
        """Check if request is from Tailscale network."""
        x_tailnet_key = request.headers.get('X-Tailscale-Key')
        return bool(x_tailnet_key)
    
    def get_network_info(self):
        """Get Tailscale network information."""
        try:
            import requests
            response = requests.get(
                f"{self.api_url}/client/self",
                headers=self.headers,
                timeout=5
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Tailscale info error: {e}")
            return None

tailscale = TailscaleManager()

@app.route('/api/tailscale/info', methods=['GET'])
@jwt_required()
def get_tailscale_info():
    """Get Tailscale network information."""
    info = tailscale.get_network_info()
    if info:
        return jsonify(info)
    return jsonify({'error': 'Tailscale unavailable'}), 503

# ===== STREAMS ROUTES =====
@app.route('/api/streams', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_streams():
    """Get all streams for current user."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT s.id, s.name, s.url, s.is_active, s.created_at,
                          u.username as owner
                 FROM streams s
                 JOIN users u ON s.user_id = u.id
                 WHERE s.user_id = %s
                 ORDER BY s.created_at DESC""",
                (user_id,)
            )
            streams = cur.fetchall()
        
        return jsonify({
            'streams': [
                {
                    'id': s['id'],
                    'name': s['name'],
                    'url': s['url'],
                    'is_active': s['is_active'],
                    'created_at': s['created_at'].isoformat(),
                    'owner': s['owner']
                }
                for s in streams
            ]
        })
    except Exception as e:
        logger.error(f"Get streams error: {e}")
        return jsonify({'error': 'Failed to get streams'}), 500

@app.route('/api/streams', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def add_stream():
    """Add new stream."""
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        if not name or not url:
            return jsonify({'error': 'Name and URL required'}), 400
        
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO streams (user_id, name, url, is_active, created_at)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING id""",
                (user_id, name, url, True, datetime.now())
            )
            stream_id = cur.fetchone()['id']
            db.commit()
        
        return jsonify({'message': 'Stream created', 'id': stream_id}), 201
    except Exception as e:
        logger.error(f"Add stream error: {e}")
        return jsonify({'error': 'Failed to create stream'}), 500

@app.route('/api/streams/<int:stream_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
def delete_stream(stream_id):
    """Delete stream."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT user_id FROM streams WHERE id = %s AND user_id = %s",
                (stream_id, user_id)
            )
            if not cur.fetchone():
                return jsonify({'error': 'Not authorized'}), 403
            
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
    """Get recordings with filtering."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT r.id, r.stream_id, r.event_id, r.started_at, r.stopped_at,
                       r.duration, r.file_path, s.name as stream_name
                FROM recordings r
                JOIN streams s ON r.stream_id = s.id
                WHERE r.user_id = %s
            """
            params = [user_id]
            
            if 'type' in request.args:
                event_type = request.args.get('type')
                query += " AND r.event_id = (SELECT id FROM events WHERE type = %s AND user_id = %s)"
                params.extend([event_type, user_id])
            
            if 'stream_id' in request.args:
                query += " AND r.stream_id = %s"
                params.append(int(request.args.get('stream_id')))
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            offset = (page - 1) * per_page
            
            query += " ORDER BY r.started_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cur.execute(query, params)
            recordings = cur.fetchall()
        
        count_query = "SELECT COUNT(*) FROM recordings WHERE user_id = %s"
        count = cur.fetchone()[0]
        
        return jsonify({
            'recordings': [
                {
                    'id': r['id'],
                    'stream_id': r['stream_id'],
                    'stream_name': r['stream_name'],
                    'event_id': r['event_id'],
                    'started_at': r['started_at'].isoformat(),
                    'stopped_at': r['stopped_at'].isoformat() if r['stopped_at'] else None,
                    'duration': r['duration'].total_seconds() if r['duration'] else 0,
                    'file_path': r['file_path']
                }
                for r in recordings
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': count,
                'pages': (count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Get recordings error: {e}")
        return jsonify({'error': 'Failed to get recordings'}), 500

@app.route('/api/recordings', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def start_recording():
    """Start recording."""
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
        stream_id = data.get('stream_id')
        
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM streams WHERE id = %s AND user_id = %s",
                (stream_id, user_id)
            )
            if not cur.fetchone():
                return jsonify({'error': 'Not authorized'}), 403
            
            cur.execute(
                """INSERT INTO recordings (user_id, stream_id, started_at, is_active)
                   VALUES (%s, %s, %s, %s)
                   RETURNING id""",
                (user_id, stream_id, datetime.now(), True)
            )
            recording_id = cur.fetchone()['id']
            db.commit()
        
        return jsonify({'message': 'Recording started', 'id': recording_id})
    except Exception as e:
        logger.error(f"Start recording error: {e}")
        return jsonify({'error': 'Failed to start recording'}), 500

@app.route('/api/recordings/<int:recording_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per minute")
def stop_recording(recording_id):
    """Stop recording."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT user_id, stream_id FROM recordings WHERE id = %s AND user_id = %s AND is_active = %s",
                (recording_id, user_id, True)
            )
            recording = cur.fetchone()
            if not recording:
                return jsonify({'error': 'Not authorized'}), 404
            
            duration = datetime.now() - recording['started_at']
            
            cur.execute(
                """UPDATE recordings 
                   SET stopped_at = %s, duration = %s, is_active = %s
                   WHERE id = %s""",
                (datetime.now(), duration, False, recording_id)
            )
            db.commit()
        
        return jsonify({'message': 'Recording stopped', 'duration': duration.total_seconds()})
    except Exception as e:
        logger.error(f"Stop recording error: {e}")
        return jsonify({'error': 'Failed to stop recording'}), 500

# ===== EVENTS ROUTES =====
@app.route('/api/events', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_events():
    """Get events with filtering."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT e.id, e.event_type, e.description, e.created_at,
                       e.stream_id, s.name as stream_name
                FROM events e
                LEFT JOIN streams s ON e.stream_id = s.id
                WHERE e.user_id = %s
            """
            params = [user_id]
            
            if 'type' in request.args:
                query += " AND e.event_type = %s"
                params.append(request.args.get('type'))
            
            if 'stream_id' in request.args:
                query += " AND e.stream_id = %s"
                params.append(int(request.args.get('stream_id')))
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            offset = (page - 1) * per_page
            
            query += " ORDER BY e.created_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cur.execute(query, params)
            events = cur.fetchall()
        
        count_query = "SELECT COUNT(*) FROM events WHERE user_id = %s"
        count = cur.fetchone()[0]
        
        return jsonify({
            'events': [
                {
                    'id': e['id'],
                    'event_type': e['event_type'],
                    'description': e['description'],
                    'created_at': e['created_at'].isoformat(),
                    'stream_id': e['stream_id'],
                    'stream_name': e['stream_name']
                }
                for e in events
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': count,
                'pages': (count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Get events error: {e}")
        return jsonify({'error': 'Failed to get events'}), 500

# ===== SCHEDULES ROUTES =====
@app.route('/api/schedules', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_schedules():
    """Get recording schedules."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT s.id, s.name, s.stream_id, s.recording_type,
                          s.start_time, s.end_time, s.is_active, s.created_at
                 FROM schedules s
                 WHERE s.user_id = %s
                 ORDER BY s.created_at DESC""",
                (user_id,)
            )
            schedules = cur.fetchall()
        
        return jsonify({
            'schedules': [
                {
                    'id': s['id'],
                    'name': s['name'],
                    'stream_id': s['stream_id'],
                    'recording_type': s['recording_type'],
                    'start_time': s['start_time'].isoformat() if s['start_time'] else None,
                    'end_time': s['end_time'].isoformat() if s['end_time'] else None,
                    'is_active': s['is_active'],
                    'created_at': s['created_at'].isoformat()
                }
                for s in schedules
            ]
        })
    except Exception as e:
        logger.error(f"Get schedules error: {e}")
        return jsonify({'error': 'Failed to get schedules'}), 500

# ===== ANALYTICS ROUTES =====
@app.route('/api/analytics/overview', methods=['GET'])
@jwt_required()
@limiter.limit("10 per minute")
def get_analytics_overview():
    """Get analytics overview."""
    user_id = get_jwt_identity()
    db = get_db()
    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*) as total, SUM(is_active) as active FROM streams WHERE user_id = %s",
                (user_id,)
            )
            stream_stats = cur.fetchone()
            
            cur.execute(
                "SELECT COUNT(*) as total, COALESCE(SUM(duration), 0) as total_seconds FROM recordings WHERE user_id = %s",
                (user_id,)
            )
            recording_stats = cur.fetchone()
            
            cur.execute(
                "SELECT event_type, COUNT(*) as count FROM events WHERE user_id = %s GROUP BY event_type",
                (user_id,)
            )
            event_counts = cur.fetchall()
        
        return jsonify({
            'streams': {
                'total': stream_stats['total'],
                'active': stream_stats['active']
            },
            'recordings': {
                'total': recording_stats['total'],
                'total_seconds': recording_stats['total_seconds']
            },
            'events': [
                {'type': e['event_type'], 'count': e['count']}
                for e in event_counts
            ]
        })
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        return jsonify({'error': 'Failed to get analytics'}), 500

# ===== BACKUP ROUTES =====
@app.route('/api/backup', methods=['POST'])
@jwt_required()
def create_backup():
    """Create backup of database."""
    backup_dir = Path('/var/backups/rtsp-nvr')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.sql'
        
        with open(backup_file, 'w') as f:
            with psycopg2.connect(app.config['DATABASE_URL']) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    for table in ['users', 'streams', 'events', 'recordings', 'schedules']:
                        cur.execute(f"SELECT * FROM {table}")
                        rows = cur.fetchall()
                        f.write(f"-- Table: {table}\n")
                        if rows:
                            columns = ', '.join([str(k) for k in rows[0].keys()])
                            f.write(f"CREATE TABLE {table} ({columns})\n\n")
                            f.write(f"-- Data:\n\n")
                            for row in rows:
                                values = ', '.join([str(v) for v in row])
                                f.write(f"INSERT INTO {table} VALUES ({values});\n")
        
        return jsonify({'message': 'Backup created', 'path': str(backup_file)})
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'error': 'Backup failed'}), 500

# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    status = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    
    try:
        with psycopg2.connect(app.config['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    try:
        r = redis.Redis.from_url(app.config['REDIS_URL'])
        r.ping()
        status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
    
    return jsonify(status)

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
    
    join_room(f'stream_{stream_id}')
    emit('stream_update', {
        'stream_id': stream_id,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('event_update')
def handle_event_update(data):
    event = data.get('event')
    emit('new_event', event, broadcast=True)

# ===== BACKGROUND TASKS =====
scheduler = BackgroundScheduler()

@scheduler.job(id='cleanup_old_records', trigger='cron', hour=2, minute=0)
def cleanup_old_records():
    """Clean up old recordings and events."""
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM recordings WHERE is_active = %s AND stopped_at < %s",
                (False, datetime.now() - timedelta(days=30))
            )
            
            cur.execute(
                "DELETE FROM events WHERE created_at < %s",
                (datetime.now() - timedelta(days=7),)
            )
            
            db.commit()
        logger.info("Cleanup completed")
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

# ===== API DOCS =====
@app.route('/api/docs')
def api_docs():
    """Return API documentation."""
    return '''
# RTSP NVR Dashboard API

## Authentication
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/me
- POST /api/auth/logout

## Streams
- GET /api/streams
- POST /api/streams
- DELETE /api/streams/<id>

## Recordings
- GET /api/recordings
- POST /api/recordings
- DELETE /api/recordings/<id>

## Events
- GET /api/events

## Schedules
- GET /api/schedules
- POST /api/schedules

## Analytics
- GET /api/analytics/overview

## Tailscale
- GET /api/tailscale/info

## Health
- GET /health
    ''', 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
