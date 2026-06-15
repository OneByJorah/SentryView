import React, { useState, useEffect } from 'react';
import { api } from '../api';

const Timeline = ({ events: liveEvents = [] }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const perPage = 50;

  const fetchEvents = async () => {
    setLoading(true);
    try {
      let url = '/api/events?page=' + currentPage + '&per_page=' + perPage;
      if (filterType) url += '&type=' + filterType;
      const data = await api.get(url);
      if (data) setEvents(data.events || []);
    } catch (e) { console.error('Failed to fetch events:', e); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchEvents(); }, [currentPage, filterType]);

  const allEvents = [...liveEvents, ...events].slice(0, 100);
  const eventTypes = ['recording_started', 'recording_stopped', 'motion_detected', 'audio_exceeded', 'stream_connected', 'stream_disconnected', 'system_alert', 'manual_event'];

  const exportEvents = () => {
    const blob = new Blob([JSON.stringify(allEvents, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'events_' + new Date().toISOString().split('T')[0] + '.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const getEventIcon = (type) => {
    const icons = { recording_started: 'REC+', recording_stopped: 'REC-', motion_detected: 'MOTION', audio_exceeded: 'AUDIO', stream_connected: 'ON', stream_disconnected: 'OFF', system_alert: 'ALERT', manual_event: 'MANUAL' };
    return icons[type] || type;
  };

  return (
    <div className="timeline">
      <div className="timeline-header">
        <h2>Event Timeline</h2>
        <button onClick={exportEvents} className="btn btn-secondary">Export Events</button>
      </div>
      <div className="timeline-filters">
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
          <option value="">All Types</option>
          {eventTypes.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ').toUpperCase()}</option>)}
        </select>
      </div>
      <div className="timeline-list">
        {loading ? <div className="loading">Loading events...</div> :
         allEvents.length === 0 ? <div className="empty-state">No events found</div> :
         allEvents.map((event, idx) => (
          <div key={event.id || idx} className="event-item">
            <div className="event-icon">{getEventIcon(event.event_type)}</div>
            <div className="event-details">
              <div className="event-header">
                <span className="event-type">{event.event_type ? event.event_type.replace(/_/g, ' ') : 'Unknown'}</span>
                <span className="event-time">{event.created_at ? new Date(event.created_at).toLocaleString() : 'Live'}</span>
              </div>
              {event.description && <p className="event-description">{event.description}</p>}
              {event.stream_name && <p className="event-stream">{event.stream_name}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline;
