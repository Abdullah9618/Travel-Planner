import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Destination API calls
export const destinationService = {
  getAll: (params) => api.get('/destinations', { params }),
  getById: (id) => api.get(`/destinations/${id}`),
  search: (query) => api.post('/search', { query }),
  getRecommendations: (preferences, history) => 
    api.post('/recommendations', { preferences, history }),
  getTravelSuggestions: () => api.get('/travel-suggestions'),
  getHomeInsights: () => api.get('/home/insights'),
  getWeatherHighlights: (region) => api.get('/weather/highlights', { params: region ? { region } : {} }),
  getPlaces: (query, category = 'attractions') =>
    api.get('/explore/places', { params: { query, category, limit: 5 } }),
  generateItinerary: (payload) => api.post('/itinerary/generate', payload),
  submitFeedback: (payload) => api.post('/feedback', payload),
  getSharedTrip: (shareToken) => api.get(`/shared-trip/${shareToken}`)
};

// Budget API calls
export const budgetService = {
  estimate: (destination, days) => 
    api.post('/budget/estimate', { destination, days })
};

// Admin API calls
export const adminService = {
  getDestinations: () => api.get('/admin/destinations'),
  addDestination: (data) => api.post('/admin/destinations', data),
  updateDestination: (id, data) => api.put(`/admin/destinations/${id}`, data),
  deleteDestination: (id) => api.delete(`/admin/destinations/${id}`),
  getStats: () => api.get('/admin/stats'),
  getActivityStats: () => api.get('/admin/activity'),
  getFeedback: () => api.get('/admin/feedback'),
  updateFeedback: (id, status) => api.patch(`/admin/feedback/${id}`, { status }),
  getModels: () => api.get('/admin/models'),
  updateModel: (id, data) => api.patch(`/admin/models/${id}`, data),
  getCostRates: () => api.get('/admin/cost-rates'),
  updateCostRates: (data) => api.put('/admin/cost-rates', data)
};

export const tripService = {
  updateSavedTrip: (id, data) => api.put(`/auth/saved-trips/${id}`, data),
  deleteSavedTrip: (id) => api.delete(`/auth/saved-trips/${id}`),
  shareSavedTrip: (id) => api.post(`/auth/saved-trips/${id}/share`)
};

export default api;
