/**
 * API Service
 * Handles all HTTP requests to the Flask backend
 */

import axios from 'axios';

const DEFAULT_API_URL = 'http://localhost:5000';
const DEFAULT_AI_URL = 'http://localhost:11434';

const envApiUrl = import.meta.env.VITE_API_URL?.trim();
const envAiUrl = import.meta.env.VITE_AI_API_URL?.trim();

// Use the configured backend first, then fall back to local port detection.
let API_BASE_URL = envApiUrl || DEFAULT_API_URL;
const AI_API_URL = envAiUrl || DEFAULT_AI_URL; // Ollama API

// Function to detect which port backend is on
const detectBackendPort = async () => {
  if (envApiUrl) {
    API_BASE_URL = envApiUrl;
    return;
  }

  const ports = [5005, 5006, 5004, 5003, 5000, 5001, 5002, 5007, 5008, 5009, 5010];
  for (const port of ports) {
    try {
      await axios.get(`http://localhost:${port}/`, { timeout: 1000 });
      API_BASE_URL = `http://localhost:${port}`;
      console.log(`✓ Backend found on port ${port}`);
      return;
    } catch {
      // Try next port
    }
  }
  console.warn('Backend not found on any port, using default 5000');
};

// Create axios instance for backend
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 15 second timeout for API calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for AI service
const aiApi = axios.create({
  baseURL: AI_API_URL,
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

// Detect backend port on first API call
let portDetected = false;
api.interceptors.request.use(async (config) => {
  if (!portDetected) {
    portDetected = true;
    await detectBackendPort().catch(() => {
      // Silently fail, use default port
    });
    // Update baseURL after detection
    api.defaults.baseURL = API_BASE_URL;
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
    }
    return Promise.reject(error);
  }
);

// Export API base URL for image construction and other uses
export const getAPIBaseURL = () => API_BASE_URL;

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getMe: () => api.get('/auth/me'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  uploadProfilePicture: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/auth/profile/picture', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Chat API - with AI integration
export const chatAPI = {
  sendMessage: (message, sessionId, cvText = null, masked = false, userEmail = null, language = 'en', history = []) => api.post('/chat', {
    message,
    session_id: sessionId || `session_${Date.now()}`,
    user_email: userEmail,
    cv_text: cvText,
    masked,
    language,
    history: history, // Include conversation history for context
  }),

  getHistory: (sessionId) => api.get(`/session/${sessionId}`),

  clearHistory: (sessionId) => api.delete(`/session/${sessionId}`),
  uploadCV: (file, sessionId, masked = false, userEmail = null, language = 'en') => {
    const fd = new FormData();
    fd.append('cv_file', file);
    fd.append('session_id', sessionId || `session_${Date.now()}`);
    fd.append('user_email', userEmail);
    fd.append('masked', masked ? 'true' : 'false');
    fd.append('language', language);
    return api.post('/upload_cv', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    });
  },
};

// Jobs API - Kagel dataset
export const jobsAPI = {
  getAll: (params = {}) => api.get('/jobs', { params }),
  
  getById: (jobId) => api.get(`/jobs/${jobId}`),
  
  search: (searchParams) => api.get('/jobs', { params: searchParams }),
  
  create: (data) => api.post('/jobs', data),
};

// Applications API
export const applicationsAPI = {
  apply: (jobId, candidateId, data = {}) => api.post('/apply', { 
    jobId, 
    candidateId,
    ...data 
  }),
  
  getMyApplications: (candidateId) => api.get('/apply', { params: { candidateId } }),
  
  getById: (id) => api.get(`/apply/${id}`),
};

// AI Service API - Ollama local LLM
export const aiServiceAPI = {
  // Generate response using local Ollama
  generateResponse: async (prompt, model = 'mistral') => {
    try {
      const response = await aiApi.post('/api/generate', {
        model,
        prompt,
        stream: false,
      });
      return response;
    } catch (error) {
      console.error('AI Service error:', error);
      throw error;
    }
  },

  // Check if AI service is available
  healthCheck: () => aiApi.get('/api/tags').catch(() => ({ data: null })),
};

// 🧠 NLP API - Local NLP Service (spaCy, NLTK, scikit-learn)
export const nlpAPI = {
  // Check NLP service health
  health: () => api.get('/nlp/health'),

  // Detect user intent (job_search, salary_query, skill_match, etc.)
  detectIntent: (message) => api.post('/nlp/detect-intent', { message }),

  // Extract entities (organizations, locations, money, dates, persons)
  extractEntities: (message) => api.post('/nlp/extract-entities', { message }),

  // Extract skills (technical, soft, languages)
  extractSkills: (message) => api.post('/nlp/extract-skills', { message }),

  // Extract keywords using TF-IDF
  extractKeywords: (message, topN = 10) => api.post('/nlp/extract-keywords', { 
    message,
    top_n: topN 
  }),

  // Parse user profile from text
  parseProfile: (message) => api.post('/nlp/parse-profile', { message }),

  // Parse job requirements from job description
  parseJob: (message) => api.post('/nlp/parse-job', { message }),

  // Summarize text
  summarize: (message, numSentences = 3) => api.post('/nlp/summarize', { 
    message,
    num_sentences: numSentences 
  }),

  // Calculate text similarity between two strings
  similarity: (userSkills, jobSkills) => api.post('/nlp/similarity', { 
    user_skills: userSkills,
    job_skills: jobSkills 
  }),
};

export { api, aiApi };
export default api;

