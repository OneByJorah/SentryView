import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import { io } from 'socket.io-client';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Timeline from './components/Timeline';
import Settings from './components/Settings';
import './App.css';

const api = {
  async request(path, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const response = await fetch(path, { ...options, headers });
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || 'Request failed');
    }
    return response.json();
  },
  get: (path) => api.request(path),
  post: (path, body) => api.request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => api.request(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => api.request(path, { method: 'DELETE' }),
};

const AuthContext = React.createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const data = await api.get('/api/auth/me');
          if (data) setUser(data);
        }
      } catch (error) {
        localStorage.removeItem('access_token');
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      const data = await response.json();
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        setUser(data.user);
        toast.success('Welcome, ' + data.user.username + '!');
        return { success: true };
      }
      return { success: false, error: data.error || 'Login failed' };
    } catch (err) {
      return { success: false, error: 'Network error' };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  if (loading) return <div className="loading-screen"><div className="spinner" /><p>Loading...</p></div>;

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => React.useContext(AuthContext);

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

const useSocket = () => {
  const [connected, setConnected] = useState(false);
  const socket = useMemo(() => {
    const s = io('/', { path: '/socket.io/', transports: ['websocket', 'polling'] });
    s.on('connect', () => setConnected(true));
    s.on('disconnect', () => setConnected(false));
    return s;
  }, []);
  useEffect(() => () => { socket.disconnect(); }, [socket]);
  return { socket, connected };
};

const Sidebar = ({ socketConnected }) => {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/timeline', label: 'Timeline' },
    { path: '/settings', label: 'Settings' },
  ];
  return (
    <aside className={'sidebar' + (location.pathname === '/login' ? ' hidden' : '')}>
      <div className="sidebar-header">
        <h2 className="cyber-text glow">NVR</h2>
        <div className={'status-dot ' + (socketConnected ? 'online' : 'offline')} title={socketConnected ? 'Connected' : 'Disconnected'} />
      </div>
      <nav className="nav-menu">
        {navItems.map(item => (
          <div key={item.path} className={'nav-item' + (location.pathname === item.path ? ' active' : '')} onClick={() => window.location.href = item.path}>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="user-info">
          <span className="user-role">{user?.role || 'user'}</span>
          <span className="user-name">{user?.username || 'Guest'}</span>
        </div>
        <button onClick={logout} className="btn btn-small btn-danger">Logout</button>
      </div>
    </aside>
  );
};

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { socket, connected } = useSocket();
  const [streams, setStreams] = useState([]);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    socket.on('stream_update', (data) => {
      setStreams(prev => prev.map(s => s.id === data.stream_id ? { ...s, status: data.status } : s));
    });
    socket.on('new_event', (data) => {
      setEvents(prev => [data, ...prev]);
      toast.success('New event: ' + data.event_type);
    });
    socket.on('recording_update', (data) => {
      toast('Recording ' + data.type);
    });
    return () => { socket.off('stream_update'); socket.off('new_event'); socket.off('recording_update'); };
  }, [socket]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    document.documentElement.classList.toggle('light', !darkMode);
  }, [darkMode]);

  return (
    <AuthProvider>
      <Router>
        <div className={'app ' + (darkMode ? 'dark' : 'light')}>
          <Toaster position="top-right" toastOptions={{ duration: 3000, style: { background: darkMode ? '#1a1a2e' : '#fff', color: darkMode ? '#e0e0e0' : '#333' } }} />
          <header className="header">
            <div className="header-left">
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="menu-btn">Menu</button>
              <h1 className="cyber-text">RTSP NVR Dashboard</h1>
            </div>
            <div className="header-right">
              <button onClick={() => setDarkMode(!darkMode)} className="theme-btn">
                {darkMode ? 'Light' : 'Dark'}
              </button>
            </div>
          </header>
          <div className="main-container">
            <Sidebar socketConnected={connected} />
            <main className={'content' + (sidebarOpen ? '' : ' sidebar-closed')}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={<ProtectedRoute><Dashboard socket={socket} /></ProtectedRoute>} />
                <Route path="/timeline" element={<ProtectedRoute><Timeline events={events} /></ProtectedRoute>} />
                <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
