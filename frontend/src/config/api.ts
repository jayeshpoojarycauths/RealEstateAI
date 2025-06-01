import { z } from 'zod';
import axios from 'axios';

// Environment variable validation
const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
  VITE_API_TIMEOUT: z.number().default(30000),
});

const env = envSchema.parse({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  VITE_API_TIMEOUT: Number(import.meta.env.VITE_API_TIMEOUT),
});

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    REGISTER: '/auth/register',
    VERIFY_EMAIL: '/auth/verify-email',
    RESEND_VERIFICATION: '/auth/resend-verification',
    RESET_PASSWORD: '/auth/reset-password',
  },
  USERS: {
    BASE: '/users',
    BY_ID: (id: string) => `/users/${id}`,
    ME: '/users/me',
    PASSWORD: '/users/me/password',
  },
  PROPERTIES: {
    BASE: '/properties',
    BY_ID: (id: string) => `/properties/${id}`,
    STATS: '/properties/stats',
  },
  CUSTOMERS: {
    BASE: '/customers',
    BY_ID: (id: string) => `/customers/${id}`,
  },
  ANALYTICS: {
    BASE: '/analytics',
    LEAD_SCORES: '/analytics/lead-scores',
    CONVERSION_FUNNEL: '/analytics/conversion-funnel',
    PRICE_TRENDS: '/analytics/price-trends',
  },
  PLATFORM: {
    TENANTS: '/platform/tenants',
    SETTINGS: '/platform/settings',
  },
  AUDIT: {
    LOGS: '/audit/logs',
  },
} as const;

// Create axios instance with default config
export const api = axios.create({
  baseURL: env.VITE_API_BASE_URL,
  timeout: env.VITE_API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(import.meta.env.VITE_AUTH_REFRESH_TOKEN_KEY);
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(
          `${env.VITE_API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
          { refreshToken }
        );

        const { token } = response.data;
        localStorage.setItem(import.meta.env.VITE_AUTH_TOKEN_KEY, token);

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, clear auth state and redirect to login
        localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY);
        localStorage.removeItem(import.meta.env.VITE_AUTH_REFRESH_TOKEN_KEY);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Type definitions
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
} 