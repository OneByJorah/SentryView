import React, { useState, useEffect } from 'react';

const Timeline = ({ events: initialEvents = [] }) => {
  const [events, setEvents] = useState(initialEvents);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [filterStream, setFilterStream] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage] = useState(50);
  const [streams, setStreams] = useState([]);

  // ===== FETCH EVENTS =====
  const fetchEvents = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage
      });

      if (filterType) params.append('type', filterType);
      if (filterStream) params.append('stream_id', filterStream);

      const response = await fetch(`/api/events?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setEvents(data.events);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    } finally {
      setLoading(false);
    }
  };

  // ===== FETCH STREAMS =====
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
    }
  };

  useEffect(() => {
    fetchEvents();
    fetchStreams();
  }, [currentPage, filterType, filterStream]);

  // ===== EVENT TYPES =====
  const eventTypes = ['recording_started', 'recording_stopped', 'motion_detected', 'audio_exceeded'];

  // ===== EXPORT EVENTS =====
  const exportEvents = () => {
    const blob = new Blob([JSON.stringify(events, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `events_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ===== PAGINATION =====
  const totalPages = Math.ceil(events.length / perPage);
  const startIndex = (currentPage - 1) * perPage;
  const endIndex = startIndex + perPage;
  const currentEvents = events.slice(startIndex, endIndex);

  return (
    <div className="timeline">
      <div className="timeline-header">
        <h2>📅 Event Timeline</h2>
        <button onClick={exportEvents} className="btn btn-secondary">
          📤 Export Events
        </button>
      </div>

      {/* ===== FILTERS ===== */}
      <div className="timeline-filters">
        <div className="filter-group">
          <label>Event Type:</label>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="">All Types</option>
            {eventTypes.map((type) => (
              <option key={type} value={type}>{type.replace('_', ' ').toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Stream:</label>
          <select value={filterStream} onChange={(e) => setFilterStream(e.target.value)}>
            <option value="">All Streams</option>
            {streams.map((stream) => (
              <option key={stream.id} value={stream.id}>{stream.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ===== EVENTS LIST ===== */}
      <div className="timeline-list">
        {loading ? (
          <div className="loading">Loading events...</div>
        ) : currentEvents.length === 0 ? (
          <div className="empty-state">No events found</div>
        ) : (
          currentEvents.map((event) => (
            <div key={event.id} className={`event-item ${event.event_type}`}>
              <div className="event-icon">
                {event.event_type === 'recording_started' && '🟢'}
                {event.event_type === 'recording_stopped' && '🔴'}
                {event.event_type === 'motion_detected' && '🟡'}
                {event.event_type === 'audio_exceeded' && '🔊'}
              </div>
              <div className="event-details">
                <div className="event-header">
                  <span className="event-type">{event.event_type.replace('_', ' ')}</span>
                  <span className="event-time">
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                {event.description && (
                  <p className="event-description">{event.description}</p>
                )}
                {event.stream_name && (
                  <p className="event-stream">📺 {event.stream_name}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* ===== PAGINATION ===== */}
      {totalPages > 1 && (
        <div className="timeline-pagination">
          <button 
            disabled={currentPage === 1} 
            onClick={() => setCurrentPage(prev => prev - 1)}
          >
            ← Previous
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button 
            disabled={currentPage === totalPages} 
            onClick={() => setCurrentPage(prev => prev + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default Timeline;
