import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { logger } from '../utils/logger';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Extend the InternalAxiosRequestConfig type to include _retry
interface CustomInternalAxiosRequestConfig extends InternalAxiosRequestConfig {
    _retry?: boolean;
}

// const api = axios.create({
//     baseURL: config.apiUrl,
//     withCredentials: true, // Enable sending cookies
//     headers: {
//         'Content-Type': 'application/json',
//     },
// });

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        logger.error('API request error', error);
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error: AxiosError) => {
        const originalRequest = error.config as CustomInternalAxiosRequestConfig;

        // Handle token refresh
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                    refresh_token: refreshToken,
                });

                const { access_token } = response.data;
                localStorage.setItem('token', access_token);

                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                return api(originalRequest);
            } catch (refreshError) {
                logger.error('Token refresh failed', refreshError as Error);
                // Clear auth data and redirect to login
                localStorage.removeItem('token');
                localStorage.removeItem('refreshToken');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        // Log error details
        logger.error('API response error', error, {
            url: originalRequest?.url,
            method: originalRequest?.method,
            status: error.response?.status,
            data: error.response?.data,
        });

        return Promise.reject(error);
    }
);

export default api; 