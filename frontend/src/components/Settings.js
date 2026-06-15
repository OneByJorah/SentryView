import React, { useState, useEffect } from 'react';
import { api } from '../api';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [config, setConfig] = useState({ audioThreshold: 70, retentionDays: 7, username: '', password: '', tailscaleApiKey: '' });
  const [loading, setLoading] = useState(false);
  const [streams, setStreams] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [newSchedule, setNewSchedule] = useState({ name: '', stream_id: '', recording_type: 'video', cron_expression: '' });

  useEffect(() => { fetchStreams(); fetchSchedules(); }, []);

  const fetchStreams = async () => {
    try { const data = await api.get('/api/streams'); if (data) setStreams(data.streams || []); } catch (e) {}
  };
  const fetchSchedules = async () => {
    try { const data = await api.get('/api/schedules'); if (data) setSchedules(data.schedules || []); } catch (e) {}
  };

  const createSchedule = async () => {
    if (!newSchedule.name || !newSchedule.stream_id || !newSchedule.cron_expression) {
      alert('Please fill all fields'); return;
    }
    try {
      await api.post('/api/schedules', newSchedule);
      setNewSchedule({ name: '', stream_id: '', recording_type: 'video', cron_expression: '' });
      fetchSchedules();
    } catch (e) { alert(e.message); }
  };

  const deleteSchedule = async (id) => {
    if (!window.confirm('Delete this schedule?')) return;
    try { await api.del('/api/schedules/' + id); fetchSchedules(); } catch (e) { alert(e.message); }
  };

  const changePassword = async () => {
    const current = prompt('Current password:');
    if (!current) return;
    const newPass = prompt('New password (min 8 chars):');
    if (!newPass || newPass.length < 8) { alert('Password must be 8+ chars'); return; }
    try {
      await api.put('/api/auth/password', { current_password: current, new_password: newPass });
      alert('Password changed successfully');
    } catch (e) { alert(e.message); }
  };

  const createBackup = async () => {
    try {
      setLoading(true);
      const data = await api.post('/api/backup', {});
      alert('Backup created: ' + (data.size ? (data.size / 1024).toFixed(0) + ' KB' : 'OK'));
    } catch (e) { alert(e.message); } finally { setLoading(false); }
  };

  return (
    <div className="settings">
      <h2>Settings</h2>
      <div className="settings-tabs">
        {['general', 'recording', 'schedules', 'backup', 'security'].map(tab => (
          <button key={tab} className={'tab' + (activeTab === tab ? ' active' : '')} onClick={() => setActiveTab(tab)}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'general' && (
        <div className="settings-panel">
          <h3>General Settings</h3>
          <div className="form-group"><label>System Name</label><input type="text" defaultValue="RTSP NVR Dashboard" /></div>
          <div className="form-group"><label>Audio Threshold (dB)</label>
            <input type="number" value={config.audioThreshold} onChange={(e) => setConfig(p => ({ ...p, audioThreshold: e.target.value }))} min="0" max="150" />
          </div>
          <div className="form-group"><label>Retention Days</label>
            <input type="number" value={config.retentionDays} onChange={(e) => setConfig(p => ({ ...p, retentionDays: e.target.value }))} min="1" max="365" />
          </div>
        </div>
      )}

      {activeTab === 'schedules' && (
        <div className="settings-panel">
          <h3>Recording Schedules</h3>
          <div className="schedule-list">
            {schedules.length === 0 ? <p>No schedules configured</p> : schedules.map(s => (
              <div key={s.id} className="schedule-item">
                <div><strong>{s.name}</strong> - {s.stream_name || 'Unknown'}</div>
                <div>Type: {s.recording_type} | Cron: {s.cron_expression} | {s.is_active ? 'Active' : 'Inactive'}</div>
                <button onClick={() => deleteSchedule(s.id)} className="btn btn-danger btn-small">Delete</button>
              </div>
            ))}
          </div>
          <h4>Add Schedule</h4>
          <div className="form-group"><input placeholder="Name" value={newSchedule.name} onChange={(e) => setNewSchedule(p => ({ ...p, name: e.target.value }))} /></div>
          <div className="form-group">
            <select value={newSchedule.stream_id} onChange={(e) => setNewSchedule(p => ({ ...p, stream_id: e.target.value }))}>
              <option value="">Select Stream</option>
              {streams.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <select value={newSchedule.recording_type} onChange={(e) => setNewSchedule(p => ({ ...p, recording_type: e.target.value }))}>
              <option value="video">Video</option><option value="audio">Audio</option><option value="both">Both</option>
            </select>
          </div>
          <div className="form-group"><input placeholder="Cron expression (e.g., 0 9 * * *)" value={newSchedule.cron_expression} onChange={(e) => setNewSchedule(p => ({ ...p, cron_expression: e.target.value }))} /></div>
          <button onClick={createSchedule} className="btn btn-primary">Create Schedule</button>
        </div>
      )}

      {activeTab === 'backup' && (
        <div className="settings-panel">
          <h3>Backup & Restore</h3>
          <button onClick={createBackup} className="btn btn-primary" disabled={loading}>{loading ? 'Creating...' : 'Create Backup'}</button>
          <p className="help-text">Backups use pg_dump format and are stored in Docker volume.</p>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="settings-panel">
          <h3>Security</h3>
          <button onClick={changePassword} className="btn btn-primary">Change Password</button>
        </div>
      )}
    </div>
  );
};

export default Settings;
