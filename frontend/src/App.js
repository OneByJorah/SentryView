import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Timeline from './components/Timeline';
import Settings from './components/Settings';
import Login from './components/Login';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check auth status on mount
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        setIsLoggedIn(data.authenticated);
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        {isLoggedIn && (
          <nav className="navbar cyber-border">
            <div className="nav-brand">
              <span className="cyber-text glow">🎥 RTSP NVR Dashboard</span>
            </div>
            <div className="nav-links">
              <Link to="/dashboard" className="nav-link">📹 Dashboard</Link>
              <Link to="/timeline" className="nav-link">📅 Timeline</Link>
              <Link to="/settings" className="nav-link">⚙️ Settings</Link>
              <button onClick={() => setIsLoggedIn(false)} className="nav-link">
                🔒 Logout
              </button>
            </div>
          </nav>
        )}

        <Routes>
          <Route
            path="/login"
            element={
              <Login
                onSuccess={() => {
                  setIsLoggedIn(true);
                  window.location.pathname = '/dashboard';
                }}
              />
            }
          />
          <Route
            path="/dashboard"
            element={
              isLoggedIn ? <Dashboard /> : <Link to="/login">Login</Link>
            }
          />
          <Route
            path="/timeline"
            element={
              isLoggedIn ? <Timeline /> : <Link to="/login">Login</Link>
            }
          />
          <Route
            path="/settings"
            element={
              isLoggedIn ? <Settings /> : <Link to="/login">Login</Link>
            }
          />
          <Route path="/" element={<Link to="/login">Login</Link>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
