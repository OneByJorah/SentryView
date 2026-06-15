import React, { useState, useEffect } from 'react';
import { api } from '../api';

const Dashboard = ({ socket }) => {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [recording, setRecording] = useState(null);
  const [selectedStream, setSelectedStream] = useState(null);
  const [streamUrl, setStreamUrl] = useState('');
  const [isAddingStream, setIsAddingStream] = useState(false);
  const [newStreamName, setNewStreamName] = useState('');

  useEffect(() => {
    fetchStreams();
    fetchAnalytics();
  }, []);

  const fetchStreams = async () => {
    try {
      const data = await api.get('/api/streams');
      if (data) setStreams(data.streams || []);
    } catch (e) {
      console.error('Failed to fetch streams:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const data = await api.get('/api/analytics/overview');
      if (data) setAnalytics(data);
    } catch (e) { console.error('Failed to fetch analytics:', e); }
  };

  const addStream = async () => {
    if (!streamUrl.trim() || !newStreamName.trim()) return;
    try {
      await api.post('/api/streams', { name: newStreamName.trim(), url: streamUrl.trim() });
      fetchStreams();
      setStreamUrl('');
      setNewStreamName('');
      setIsAddingStream(false);
    } catch (e) { alert(e.message); }
  };

  const deleteStream = async (id) => {
    if (!window.confirm('Delete this stream?')) return;
    try {
      await api.del('/api/streams/' + id);
      fetchStreams();
    } catch (e) { alert(e.message); }
  };

  const startRecording = async (streamId) => {
    try {
      const data = await api.post('/api/recordings', { stream_id: streamId });
      if (data) setRecording(streamId);
    } catch (e) { alert(e.message); }
  };

  const stopRecording = async () => {
    try {
      // Find active recording for this stream
      const recData = await api.get('/api/recordings?active=true&stream_id=' + recording);
      if (recData && recData.recordings && recData.recordings.length > 0) {
        await api.del('/api/recordings/' + recData.recordings[0].id);
      }
      setRecording(null);
      fetchAnalytics();
    } catch (e) { alert(e.message); }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /><p>Loading dashboard...</p></div>;

  return (
    <div className="dashboard">
      <div className="streams-grid">
        {streams.map((stream) => (
          <div key={stream.id} className="stream-card">
            <div className="stream-header">
              <h3>{stream.name}</h3>
              <div className="stream-status">
                <span className={'status-indicator ' + (stream.is_active ? 'online' : 'offline')} />
                {stream.is_active ? 'Active' : 'Inactive'}
              </div>
              <div className="stream-actions">
                <button onClick={() => setSelectedStream(selectedStream === stream.id ? null : stream.id)} className="btn btn-small">
                  {selectedStream === stream.id ? 'Close' : 'View'}
                </button>
                <button onClick={() => deleteStream(stream.id)} className="btn btn-danger btn-small">Delete</button>
              </div>
            </div>

            {selectedStream === stream.id && (
              <div className="stream-player">
                <div className="stream-placeholder">
                  <p>RTSP streams require browser plugin or HLS transcoding</p>
                  <p className="stream-url">{stream.url}</p>
                </div>
              </div>
            )}

            <div className="stream-controls">
              {!recording || recording === stream.id ? (
                <button onClick={() => startRecording(stream.id)} className="btn btn-record" disabled={!!recording}>
                  Start Record
                </button>
              ) : null}
              {recording === stream.id && (
                <button onClick={stopRecording} className="btn btn-stop">Stop Record</button>
              )}
            </div>
          </div>
        ))}

        {isAddingStream ? (
          <div className="stream-card add-stream-card">
            <h3>Add New Stream</h3>
            <input type="text" placeholder="Stream Name" value={newStreamName} onChange={(e) => setNewStreamName(e.target.value)} className="stream-input" />
            <input type="text" placeholder="RTSP URL (rtsp://...)" value={streamUrl} onChange={(e) => setStreamUrl(e.target.value)} className="stream-input" />
            <div className="stream-actions">
              <button onClick={addStream} className="btn btn-primary">Add Stream</button>
              <button onClick={() => { setIsAddingStream(false); setStreamUrl(''); setNewStreamName(''); }} className="btn">Cancel</button>
            </div>
          </div>
        ) : (
          <button onClick={() => setIsAddingStream(true)} className="btn btn-add">+ Add Stream</button>
        )}
      </div>

      {analytics && (
        <div className="analytics-panel">
          <h2>Analytics</h2>
          <div className="analytics-grid">
            <div className="analytics-card"><h3>Streams</h3><p>Total: {analytics.streams.total}</p><p>Active: {analytics.streams.active}</p></div>
            <div className="analytics-card"><h3>Recordings</h3><p>Total: {analytics.recordings.total}</p><p>Time: {(analytics.recordings.total_seconds / 3600).toFixed(1)}h</p></div>
            <div className="analytics-card"><h3>Events</h3>{analytics.events.map((e, i) => <p key={i}>{e.type}: {e.count}</p>)}</div>
          </div>
          {analytics.daily_recordings && analytics.daily_recordings.length > 0 && (
            <div className="daily-chart">
              <h3>Recordings (Last 7 Days)</h3>
              <div className="bar-chart">
                {analytics.daily_recordings.map((d, i) => (
                  <div key={i} className="bar-item">
                    <div className="bar" style={{ height: Math.max(10, d.count * 20) + 'px' }} />
                    <span className="bar-label">{d.day}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
