import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
  const [cameras, setCameras] = useState([]);
  const [recording, setRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [streamStatus, setStreamStatus] = useState({});
  const [alert, setAlert] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const fetchCameras = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stream/status`);
      const data = await response.json();
      setStreamStatus(data);
    } catch (error) {
      console.error('Failed to fetch stream status:', error);
    }
  };

  const startRecording = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/recordings`, {
        trigger: 'manual'
      });
      setAlert({ type: 'success', message: 'Recording started!' });
      setTimeout(() => setAlert(null), 3000);
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to start recording' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  const stopRecording = async () => {
    try {
      const response = await axios.delete(`${API_URL}/api/recordings/${recording.id}`);
      setRecording(false);
      setAlert({ type: 'success', message: 'Recording stopped!' });
      setTimeout(() => setAlert(null), 3000);
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to stop recording' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      {alert && (
        <div className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <h1>📹 Live Dashboard</h1>
        <button
          className="cyber-button"
          onClick={recording ? stopRecording : startRecording}
        >
          {recording ? '⏹ Stop Recording' : '🔴 Start Recording'}
        </button>
      </div>

      <div className="camera-grid">
        <div className="camera-card">
          <div className="camera-video">
            <video
              autoPlay
              playsInline
              muted
              style={{ width: '100%', height: '100%' }}
              src={streamStatus.url}
            />
          </div>
          <div className="camera-info">
            <h3>Camera 1 - Main Feed</h3>
            <div style={{ marginTop: '1rem' }}>
              <span className={`status-indicator ${recording ? 'status-connected' : 'status-disconnected'}`}></span>
              {recording ? '🔴 RECORDING' : '● LIVE'}
            </div>
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#888' }}>
              {streamStatus.latency_ms > 0 ? `${streamStatus.latency_ms}ms latency` : 'Connected'}
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>📊 Stream Health</h2>
        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <h4>Connection Status</h4>
              <p>{streamStatus.connected || 'Unknown'}</p>
            </div>
            <div>
              <h4>Audio Level</h4>
              <p>{audioLevel > 0 ? `${audioLevel} dB` : 'Not monitoring'}</p>
            </div>
            <div>
              <h4>FFmpeg Active</h4>
              <p>{streamStatus.fps > 0 ? `${streamStatus.fps} FPS` : 'Inactive'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
