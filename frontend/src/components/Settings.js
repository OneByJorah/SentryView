import React, { useState, useEffect } from 'react';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [config, setConfig] = useState({
    audioThreshold: 70,
    retentionDays: 7,
    username: '',
    password: '',
    mesh-vpnApiKey: '',
    mesh-vpnMeshId: ''
  });
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(false);

  // ===== LOAD SETTINGS =====
  const loadSettings = async () => {
    try {
      // Load from environment
      const audioThreshold = parseFloat(process.env.REACT_APP_AUDIO_THRESHOLD_DB) || 70;
      const retentionDays = parseInt(process.env.REACT_APP_RETENTION_DAYS) || 7;
      
      setConfig(prev => ({ ...prev, audioThreshold, retentionDays }));
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  useEffect(() => {
    loadSettings();
    fetchStreams();
  }, []);

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

  // ===== SAVE SETTINGS =====
  const saveSettings = async () => {
    setLoading(true);
    try {
      // Save to environment file (requires restart)
      const fs = require('fs');
      const path = require('path');
      
      const envPath = path.resolve(__dirname, '../../../.env');
      const envContent = `
AUDIO_THRESHOLD_DB=${config.audioThreshold}
RETENTION_DAYS=${config.retentionDays}
MESH_VPN_API_KEY=${config.mesh-vpnApiKey}
MESH_VPN_MESH_ID=${config.mesh-vpnMeshId}
      `;
      
      fs.writeFileSync(envPath, envContent);
      
      alert('Settings saved! Please restart the backend for changes to take effect.');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings. Please edit .env file manually.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings">
      <h2>⚙️ Settings</h2>

      {/* ===== TABS ===== */}
      <div className="settings-tabs">
        <button 
          className={`tab ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          General
        </button>
        <button 
          className={`tab ${activeTab === 'recording' ? 'active' : ''}`}
          onClick={() => setActiveTab('recording')}
        >
          Recording
        </button>
        <button 
          className={`tab ${activeTab === 'mesh-vpn' ? 'active' : ''}`}
          onClick={() => setActiveTab('mesh-vpn')}
        >
          Mesh-VPN
        </button>
        <button 
          className={`tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          Security
        </button>
      </div>

      {/* ===== GENERAL TAB ===== */}
      {activeTab === 'general' && (
        <div className="settings-panel">
          <h3>General Settings</h3>
          <div className="form-group">
            <label>System Name</label>
            <input type="text" defaultValue="RTSP NVR Dashboard" />
          </div>
          <div className="form-group">
            <label>Default Language</label>
            <select>
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
            </select>
          </div>
        </div>
      )}

      {/* ===== RECORDING TAB ===== */}
      {activeTab === 'recording' && (
        <div className="settings-panel">
          <h3>Recording Settings</h3>
          
          <div className="form-group">
            <label>Audio Threshold (dB)</label>
            <input
              type="number"
              value={config.audioThreshold}
              onChange={(e) => setConfig(prev => ({ ...prev, audioThreshold: e.target.value }))}
              min="0"
              max="150"
            />
            <p>Recording starts when audio exceeds {config.audioThreshold}dB</p>
          </div>

          <div className="form-group">
            <label>Retention Days</label>
            <input
              type="number"
              value={config.retentionDays}
              onChange={(e) => setConfig(prev => ({ ...prev, retentionDays: e.target.value }))}
              min="1"
              max="365"
            />
            <p>Keep recordings for {config.retentionDays} days</p>
          </div>

          <div className="form-group">
            <label>Auto-Cleanup</label>
            <select>
              <option value="daily">Daily at 2 AM</option>
              <option value="weekly">Weekly on Sunday</option>
              <option value="never">Never</option>
            </select>
          </div>
        </div>
      )}

      {/* ===== MESH_VPN TAB ===== */}
      {activeTab === 'mesh-vpn' && (
        <div className="settings-panel">
          <h3>Mesh-VPN Configuration</h3>
          <p>Use Mesh-VPN for secure remote access to your dashboard.</p>
          
          <div className="form-group">
            <label>Mesh-VPN API Key</label>
            <textarea
              value={config.mesh-vpnApiKey}
              onChange={(e) => setConfig(prev => ({ ...prev, mesh-vpnApiKey: e.target.value }))}
              placeholder="tskey-..."
              rows="3"
            />
            <p className="help-text">
              Get your API key from: <a href="https://mesh-vpn.com/admin/cloudapi" target="_blank">Mesh-VPN Admin Console</a>
            </p>
          </div>

          <div className="form-group">
            <label>Mesh ID</label>
            <input
              type="text"
              value={config.mesh-vpnMeshId}
              onChange={(e) => setConfig(prev => ({ ...prev, mesh-vpnMeshId: e.target.value }))}
              placeholder="example.mesh"
            />
          </div>

          <div className="form-group">
            <label>Enable Mesh-VPN Access</label>
            <select>
              <option value="true">Enable</option>
              <option value="false">Disable</option>
            </select>
          </div>

          <button onClick={saveSettings} className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Save Mesh-VPN Config'}
          </button>
        </div>
      )}

      {/* ===== SECURITY TAB ===== */}
      {activeTab === 'security' && (
        <div className="settings-panel">
          <h3>Security Settings</h3>
          
          <div className="form-group">
            <label>Change Password</label>
            <input
              type="password"
              placeholder="New password"
              value={config.password}
              onChange={(e) => setConfig(prev => ({ ...prev, password: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={config.username}
              onChange={(e) => setConfig(prev => ({ ...prev, username: e.target.value }))}
            />
          </div>

          <button onClick={saveSettings} className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Update Credentials'}
          </button>
        </div>
      )}

      {/* ===== SAVE BUTTON ===== */}
      <div className="settings-footer">
        <button onClick={saveSettings} className="btn btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Save All Settings'}
        </button>
      </div>
    </div>
  );
};

export default Settings;
