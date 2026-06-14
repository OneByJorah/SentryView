import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Settings() {
  const [threshold, setThreshold] = useState(30);
  const [retentionDays, setRetentionDays] = useState(7);
  const [maxRecordings, setMaxRecordings] = useState(10);
  const [alert, setAlert] = useState(null);
  const [scheduledRecordings, setScheduledRecordings] = useState([]);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const updateThreshold = async () => {
    try {
      await axios.put(`${API_URL}/api/audio/threshold`, { threshold });
      setAlert({ type: 'success', message: 'Threshold updated!' });
      setTimeout(() => setAlert(null), 3000);
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to update threshold' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  useEffect(() => {
    fetchSettings();
    fetchScheduledRecordings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/audio/threshold`);
      const data = await response.json();
      setThreshold(data.threshold_db);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  const fetchScheduledRecordings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/schedule`);
      const data = await response.json();
      setScheduledRecordings(data.schedule);
    } catch (error) {
      console.error('Failed to fetch schedule:', error);
    }
  };

  const addScheduledRecording = async () => {
    const date = prompt('Enter date (YYYY-MM-DD HH:MM):');
    if (!date) return;

    const time = prompt('Enter time (HH:MM):');
    if (!time) return;

    try {
      const response = await axios.post(`${API_URL}/api/schedule`, {
        date,
        time,
        description: 'Scheduled recording'
      });
      setAlert({ type: 'success', message: 'Scheduled recording added!' });
      setTimeout(() => setAlert(null), 3000);
      fetchScheduledRecordings();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to add scheduled recording' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  const deleteScheduledRecording = async (id) => {
    try {
      await axios.delete(`${API_URL}/api/schedule`, { data: { id } });
      setAlert({ type: 'success', message: 'Scheduled recording deleted!' });
      setTimeout(() => setAlert(null), 3000);
      fetchScheduledRecordings();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to delete scheduled recording' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  return (
    <div className="container">
      {alert && (
        <div className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      )}

      <h1>⚙️ Settings</h1>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Audio Detection</h3>
        <div className="form-group">
          <label className="form-label">
            Volume Threshold (dB): {threshold}
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            style={{ width: '100%' }}
          />
          <p style={{ fontSize: '0.8rem', color: '#888', marginTop: '0.5rem' }}>
            Events will trigger when volume exceeds {threshold} dB
          </p>
        </div>
        <button className="cyber-button" onClick={updateThreshold}>
          Save Changes
        </button>
      </div>

      <div className="card">
        <h3>Recording Retention</h3>
        <div className="form-group">
          <label className="form-label">
            Days to retain recordings: {retentionDays}
          </label>
          <input
            type="number"
            min="1"
            max="365"
            value={retentionDays}
            onChange={(e) => setRetentionDays(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label className="form-label">
            Maximum recordings to keep: {maxRecordings}
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={maxRecordings}
            onChange={(e) => setMaxRecordings(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="card">
        <h3>Scheduled Recordings</h3>
        <button className="cyber-button" onClick={addScheduledRecording}>
          ➕ Add Scheduled Recording
        </button>
        <table style={{ width: '100%', marginTop: '1rem', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '2px solid var(--primary)' }}>
              <th style={{ padding: '1rem' }}>Date/Time</th>
              <th style={{ padding: '1rem' }}>Description</th>
              <th style={{ padding: '1rem' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {scheduledRecordings.map((rec) => (
              <tr key={rec.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '1rem' }}>
                  {rec.date} {rec.time}
                </td>
                <td style={{ padding: '1rem' }}>{rec.description}</td>
                <td style={{ padding: '1rem' }}>
                  <button
                    className="cyber-button"
                    onClick={() => deleteScheduledRecording(rec.id)}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                  >
                    🗑 Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Settings;
