import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('accessToken', access_token);

          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Product API
export const productAPI = {
  getAll: () => apiClient.get('/products'),
  getById: (id) => apiClient.get(`/products/${id}`),
  create: (data) => apiClient.post('/products', data),
  update: (id, data) => apiClient.put(`/products/${id}`, data),
  delete: (id) => apiClient.delete(`/products/${id}`),
};

// Pricing API
export const pricingAPI = {
  getRules: () => apiClient.get('/pricing/rules'),
  createRule: (data) => apiClient.post('/pricing/rules', data),
  updateRule: (id, data) => apiClient.put(`/pricing/rules/${id}`, data),
  deleteRule: (id) => apiClient.delete(`/pricing/rules/${id}`),
  getRecommendations: (productId) => apiClient.get(`/pricing/recommendations/${productId}`),
};

// Competitor API
export const competitorAPI = {
  getAll: () => apiClient.get('/competitors'),
  getById: (id) => apiClient.get(`/competitors/${id}`),
  create: (data) => apiClient.post('/competitors', data),
  update: (id, data) => apiClient.put(`/competitors/${id}`, data),
  delete: (id) => apiClient.delete(`/competitors/${id}`),
  getProducts: (id) => apiClient.get(`/competitors/${id}/products`),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => apiClient.get('/analytics/dashboard'),
  getPriceHistory: (productId, days = 30) => apiClient.get(`/analytics/price-history/${productId}?days=${days}`),
  getMarketTrends: () => apiClient.get('/analytics/market-trends'),
  getPerformanceMetrics: () => apiClient.get('/analytics/performance'),
};

// Scraper API
export const scraperAPI = {
  getJobs: () => apiClient.get('/scraper/jobs'),
  triggerScrape: (data) => apiClient.post('/scraper/trigger', data),
  getJobStatus: (jobId) => apiClient.get(`/scraper/jobs/${jobId}`),
};
