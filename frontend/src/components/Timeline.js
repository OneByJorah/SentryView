import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Timeline() {
  const [events, setEvents] = useState([]);
  const [recording, setRecording] = useState(null);
  const [alert, setAlert] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/events`);
      const data = await response.json();
      setEvents(data.events);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const addEvent = async (eventType, description = '', metadata = {}) => {
    try {
      await axios.post(`${API_URL}/api/events`, {
        type: eventType,
        description,
        timestamp: new Date().toISOString(),
        metadata
      });
      setAlert({ type: 'success', message: 'Event recorded!' });
      setTimeout(() => setAlert(null), 3000);
      fetchEvents();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to record event' });
      setTimeout(() => setAlert(null), 3000);
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, []);

  const sortedEvents = [...events].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  );

  return (
    <div className="container">
      {alert && (
        <div className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      )}

      <h1>📅 Event Timeline</h1>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Recent Events</h3>
        
        {sortedEvents.length === 0 ? (
          <p>No events recorded yet.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '2px solid var(--primary)' }}>
                  <th style={{ padding: '1rem' }}>Time</th>
                  <th style={{ padding: '1rem' }}>Type</th>
                  <th style={{ padding: '1rem' }}>Description</th>
                  <th style={{ padding: '1rem' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {sortedEvents.map((event) => (
                  <tr key={event.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '1rem' }}>
                      {new Date(event.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        backgroundColor: event.type === 'audio' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(0, 200, 255, 0.2)',
                        color: event.type === 'audio' ? 'var(--success)' : 'var(--secondary)'
                      }}>
                        {event.type.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>{event.description}</td>
                    <td style={{ padding: '1rem' }}>
                      <details>
                        <summary style={{ cursor: 'pointer', color: 'var(--primary)' }}>View Details</summary>
                        <pre style={{ backgroundColor: '#000', padding: '0.5rem', borderRadius: '4px', marginTop: '0.5rem' }}>
                          {JSON.stringify(event.metadata, null, 2)}
                        </pre>
                      </details>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button
            className="cyber-button"
            onClick={() => addEvent('manual', 'Manual event logged by user')}
          >
            ➕ Manual Event
          </button>
          <button
            className="cyber-button"
            onClick={() => addEvent('audio', 'Audio threshold exceeded')}
          >
            🔊 Audio Alert
          </button>
          <button
            className="cyber-button"
            onClick={() => addEvent('video', 'Video motion detected')}
          >
            📹 Video Motion
          </button>
        </div>
      </div>
    </div>
  );
}

export default Timeline;
