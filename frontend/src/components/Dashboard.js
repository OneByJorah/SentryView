import React, { useState, useEffect } from 'react';

const Dashboard = ({ onStatusUpdate }) => {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [audioLevels, setAudioLevels] = useState({});
  const [recording, setRecording] = useState(null);
  const [selectedStream, setSelectedStream] = useState(null);
  const [streamUrl, setStreamUrl] = useState('');
  const [isAddingStream, setIsAddingStream] = useState(false);

  // ===== FETCH STREAMS =====
  useEffect(() => {
    fetchStreams();
    fetchAnalytics();
  }, []);

  const fetchStreams = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/streams', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setStreams(data.streams);
    } catch (error) {
      console.error('Failed to fetch streams:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/analytics/overview', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  // ===== ADD STREAM =====
  const addStream = async () => {
    if (!streamUrl.trim()) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/streams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name: 'New Stream', url: streamUrl })
      });

      if (response.ok) {
        fetchStreams();
        setStreamUrl('');
        setIsAddingStream(false);
      }
    } catch (error) {
      console.error('Failed to add stream:', error);
    }
  };

  // ===== DELETE STREAM =====
  const deleteStream = async (id) => {
    if (!confirm('Delete this stream?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/streams/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        fetchStreams();
      }
    } catch (error) {
      console.error('Failed to delete stream:', error);
    }
  };

  // ===== START RECORDING =====
  const startRecording = async (streamId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/recordings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ stream_id: streamId })
      });

      if (response.ok) {
        setRecording(streamId);
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  // ===== STOP RECORDING =====
  const stopRecording = async (recordingId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/recordings/${recordingId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        setRecording(null);
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  };

  // ===== CONNECT TO STREAM =====
  const connectStream = (streamId, url) => {
    try {
      const socket = new WebSocket(`ws://${window.location.host}`);
      
      socket.onopen = () => {
        console.log('Connected to stream');
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'stream_update') {
          setAudioLevels(prev => ({ ...prev, [streamId]: data.audioLevel }));
          if (onStatusUpdate) {
            onStatusUpdate({ stream_id: streamId, status: data.status });
          }
        }
      };
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  // ===== RENDER =====
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* ===== STREAMS GRID ===== */}
      <div className="streams-grid">
        {streams.map((stream) => (
          <div key={stream.id} className="stream-card">
            <div className="stream-header">
              <h3>{stream.name}</h3>
              <div className="stream-actions">
                <button 
                  onClick={() => connectStream(stream.id, stream.url)}
                  className="btn btn-small"
                >
                  ▶ Connect
                </button>
                <button 
                  onClick={() => deleteStream(stream.id)}
                  className="btn btn-danger btn-small"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>

            <div className="stream-player">
              {selectedStream === stream.id ? (
                <video 
                  ref={(video) => {
                    if (video) {
                      video.srcObject = new MediaStream([
                        ...new MediaStream().getTracks()
                      ]);
                      video.src = stream.url;
                      video.play();
                    }
                  }}
                  autoPlay
                  controls
                  muted
                  className="video-player"
                />
              ) : (
                <div className="stream-placeholder">
                  <span>📺</span>
                  <p>Click Connect to view stream</p>
                </div>
              )}
            </div>

            <div className="stream-controls">
              <button 
                onClick={() => startRecording(stream.id)}
                className="btn btn-record"
                disabled={!!recording && recording !== stream.id}
              >
                🎥 Start Record
              </button>
              {recording === stream.id && (
                <button 
                  onClick={() => stopRecording(recording)}
                  className="btn btn-stop"
                >
                  ⏹️ Stop Record
                </button>
              )}
            </div>
          </div>
        ))}

        {/* ===== ADD STREAM FORM ===== */}
        {isAddingStream ? (
          <div className="stream-card add-stream-card">
            <h3>Add New Stream</h3>
            <input
              type="text"
              placeholder="RTSP URL (e.g., rtsp://user:pass@ip:554/stream)"
              value={streamUrl}
              onChange={(e) => setStreamUrl(e.target.value)}
              className="stream-input"
            />
            <div className="stream-actions">
              <button onClick={addStream} className="btn btn-primary">
                ➕ Add Stream
              </button>
              <button onClick={() => setIsAddingStream(false)} className="btn">
                ✖️ Cancel
              </button>
            </div>
          </div>
        ) : (
          <button onClick={() => setIsAddingStream(true)} className="btn btn-add">
            ➕ Add Stream
          </button>
        )}
      </div>

      {/* ===== ANALYTICS PANEL ===== */}
      {analytics && (
        <div className="analytics-panel">
          <h2>📊 Analytics</h2>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>Streams</h3>
              <p>Total: {analytics.streams.total}</p>
              <p>Active: {analytics.streams.active}</p>
            </div>
            <div className="analytics-card">
              <h3>Recordings</h3>
              <p>Total: {analytics.recordings.total}</p>
              <p>Total Time: {(analytics.recordings.total_seconds / 3600).toFixed(2)}h</p>
            </div>
            <div className="analytics-card">
              <h3>Events</h3>
              {analytics.events.map((event, index) => (
                <p key={index}>{event.type}: {event.count}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ===== AUDIO LEVELS ===== */}
      <div className="audio-levels">
        <h3>🔊 Audio Levels</h3>
        {Object.entries(audioLevels).map(([streamId, level]) => (
          <div key={streamId} className="audio-bar">
            <span>{streams.find(s => s.id === streamId)?.name}</span>
            <div className="bar-container">
              <div 
                className="bar" 
                style={{ width: `${level}%` }}
              />
            </div>
            <span>{level.toFixed(1)}dB</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
