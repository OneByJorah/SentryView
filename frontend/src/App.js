import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Timeline from './components/Timeline';
import Settings from './components/Settings';
import './App.css';

// ===== AUTH CONTEXT =====
const AuthContext = React.createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const response = await fetch('/api/auth/me', {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            setUser(data);
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      setUser(data.user);
      return { success: true };
    }
    return { success: false, error: 'Invalid credentials' };
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// ===== PROTECTED ROUTE =====
const ProtectedRoute = ({ children }) => {
  const { user, login, logout } = React.useContext(AuthContext);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          localStorage.removeItem('access_token');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return user ? children : <Navigate to="/login" />;
};

// ===== MAIN APP =====
function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [streamStatus, setStreamStatus] = useState({});
  const [events, setEvents] = useState([]);

  // ===== WEBSOCKET CONNECTION =====
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5001');

    socket.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'stream_update') {
        setStreamStatus(prev => ({ ...prev, [data.stream_id]: data.status }));
      } else if (data.type === 'new_event') {
        setEvents(prev => [...prev, data.event]);
      } else if (data.type === 'recording_update') {
        console.log('Recording update:', data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      socket.close();
    };
  }, []);

  // ===== THEME TOGGLE =====
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [darkMode]);

  // ===== NAVIGATION =====
  const navigate = () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      window.location.href = '/dashboard';
    } else {
      window.location.href = '/login';
    }
  };

  return (
    <AuthProvider>
      <Router>
        <div className={`app ${darkMode ? 'dark' : 'light'}`}>
          <header className="header">
            <div className="header-left">
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="menu-btn">
                ☰
              </button>
              <h1>📡 RTSP NVR Dashboard</h1>
            </div>
            <div className="header-right">
              <button onClick={() => setDarkMode(!darkMode)} className="theme-btn">
                {darkMode ? '☀️ Light' : '🌙 Dark'}
              </button>
              <button onClick={navigate} className="nav-btn">
                🏠 Dashboard
              </button>
            </div>
          </header>

          <div className="main-container">
            <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
              <nav className="nav-menu">
                <div className="nav-item" onClick={() => window.location.href = '/dashboard'}>
                  📺 <span>Dashboard</span>
                </div>
                <div className="nav-item" onClick={() => window.location.href = '/timeline'}>
                  📅 <span>Timeline</span>
                </div>
                <div className="nav-item" onClick={() => window.location.href = '/settings'}>
                  ⚙️ <span>Settings</span>
                </div>
                <div className="nav-item" onClick={() => window.location.href = '/analytics'}>
                  📊 <span>Analytics</span>
                </div>
                <div className="nav-item" onClick={() => window.location.href = '/tailscale'}>
                  🔗 <span>Tailscale</span>
                </div>
              </nav>
            </aside>

            <main className="content">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Dashboard onStatusUpdate={setStreamStatus} />
                  </ProtectedRoute>
                } />
                <Route path="/timeline" element={
                  <ProtectedRoute>
                    <Timeline events={events} />
                  </ProtectedRoute>
                } />
                <Route path="/settings" element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                } />
                <Route path="/analytics" element={
                  <ProtectedRoute>
                    <Dashboard analyticsMode />
                  </ProtectedRoute>
                } />
                <Route path="/tailscale" element={
                  <ProtectedRoute>
                    <div className="tailscale-panel">
                      <h2>🔗 Tailscale Network</h2>
                      <p>Access your dashboard securely via Tailscale mesh network.</p>
                      <pre>{JSON.stringify(window.location, null, 2)}</pre>
                    </div>
                  </ProtectedRoute>
                } />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
