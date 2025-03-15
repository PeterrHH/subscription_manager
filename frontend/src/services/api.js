import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication API
export const authAPI = {
  login: (username, password) => 
    apiClient.post('/auth/login/', { username, password }),
  
  register: (username, email, password) => 
    apiClient.post('/auth/register/', { username, email, password }),
  
  refreshToken: (refresh) => 
    apiClient.post('/auth/refresh/', { refresh }),
};

// Subscriptions API
export const subscriptionsAPI = {
  getAll: () => 
    apiClient.get('/subscriptions/'),
  
  getActive: () => 
    apiClient.get('/subscriptions/active/'),
  
  getCanceled: () => 
    apiClient.get('/subscriptions/canceled/'),
  
  create: (subscriptionData) => 
    apiClient.post('/subscriptions/', subscriptionData),
  
  update: (id, subscriptionData) => 
    apiClient.put(`/subscriptions/${id}/`, subscriptionData),
  
  cancel: (id) => 
    apiClient.post(`/subscriptions/${id}/cancel/`),
  
  delete: (id) => 
    apiClient.delete(`/subscriptions/${id}/`),
};

export default {
  auth: authAPI,
  subscriptions: subscriptionsAPI,
}; 