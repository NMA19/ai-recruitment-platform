/**
 * API Service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Don't redirect, let the app handle it
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  getMe: () => api.get('/auth/me'),
};

// Chat API
export const chatAPI = {
  sendMessage: (message) => api.post('/chat', { message }),
  sendMessageGuest: (message) => api.post('/chat/guest', { message }),
  getHistory: (limit = 50) => api.get(`/chat/history?limit=${limit}`),
};

// Jobs API
export const jobsAPI = {
  getAll: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return api.get(`/jobs${queryParams ? '?' + queryParams : ''}`);
  },
  getById: (id) => api.get(`/jobs/${id}`),
  create: (data) => api.post('/jobs', data),
  update: (id, data) => api.put(`/jobs/${id}`, data),
  delete: (id) => api.delete(`/jobs/${id}`),
};

// Applications API
export const applicationsAPI = {
  apply: (jobId, data = {}) => api.post('/apply', { job_id: jobId, ...data }),
  getMyApplications: () => api.get('/apply'),
  getById: (id) => api.get(`/apply/${id}`),
  updateStatus: (id, status) => api.put(`/apply/${id}/status`, { status }),
};

export default api;
