// API Client for RTSP NVR Dashboard
const api = {
  async request(path, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
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

export default api;
export { api };
