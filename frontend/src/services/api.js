import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

const v1 = (path) => `${API_V1_PREFIX}${path}`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => apiClient.post(v1('/auth/register'), data),
  loginJson: (data) => apiClient.post(v1('/auth/login/json'), data),
  me: () => apiClient.get(v1('/auth/me')),
};

export const productAPI = {
  getAll: (params = {}) => apiClient.get(v1('/products'), { params }),
  getById: (id) => apiClient.get(v1(`/products/${id}`)),
  create: (data) => apiClient.post(v1('/products'), data),
  update: (id, data) => apiClient.put(v1(`/products/${id}`), data),
  delete: (id) => apiClient.delete(v1(`/products/${id}`)),
};

export const competitorAPI = {
  getAll: (params = {}) => apiClient.get(v1('/competitors'), { params }),
  getById: (id) => apiClient.get(v1(`/competitors/${id}`)),
  create: (data, params = {}) => apiClient.post(v1('/competitors'), data, { params }),
  update: (id, data) => apiClient.put(v1(`/competitors/${id}`), data),
  delete: (id) => apiClient.delete(v1(`/competitors/${id}`)),
};

export const pricingAPI = {
  getRules: (params = {}) => apiClient.get(v1('/pricing/rules'), { params }),
  createRule: (data) => apiClient.post(v1('/pricing/rules'), data),
  updateRule: (id, data) => apiClient.put(v1(`/pricing/rules/${id}`), data),
  deleteRule: (id) => apiClient.delete(v1(`/pricing/rules/${id}`)),
  getRecommendation: (productId) => apiClient.get(v1(`/pricing/recommendations/${productId}`)),
};

export const analyticsAPI = {
  getDashboard: () => apiClient.get(v1('/analytics/dashboard')),
  getPriceTrends: () => apiClient.get(v1('/analytics/price-trends')),
  getCompetitorDistribution: () => apiClient.get(v1('/analytics/competitor-distribution')),
  getRecentActivity: () => apiClient.get(v1('/analytics/recent-activity')),
  getPriceHistory: (productId, days = 30) =>
    apiClient.get(v1(`/analytics/price-history/${productId}`), { params: { days } }),
  getMarketTrends: (days = 14) => apiClient.get(v1('/analytics/market-trends'), { params: { days } }),
  getPerformanceMetrics: () => apiClient.get(v1('/analytics/performance')),
};

export const scraperAPI = {
  fetch: (data) => apiClient.post(v1('/scraper/fetch'), data),
  enqueue: (data) => apiClient.post(v1('/scraper/enqueue'), data),
};

export const llmAPI = {
  ask: (data) => apiClient.post(v1('/llm/ask'), data),
};
