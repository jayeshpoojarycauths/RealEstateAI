import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { logger } from "../utils/logger";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

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
    "Content-Type": "application/json",
  },
});

let refreshPromise: Promise<string | null> | null = null;

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers = config.headers || {};
      Object.assign(config.headers, {
        Authorization: `Bearer ${token}`,
      });
    }
    return config;
  },
  (error) => {
    logger.error("API request error", error);
    return Promise.reject(error);
  },
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomInternalAxiosRequestConfig;
    const isRefreshEndpoint = originalRequest.url?.includes(
      "/api/v1/auth/refresh",
    );

    // Exclude refresh endpoint from retry logic
    if (isRefreshEndpoint) {
      return Promise.reject(error);
    }

    // Handle token refresh with shared refreshPromise
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      if (!refreshPromise) {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
          logger.error("No refresh token available");
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          window.location.href = "/login";
          return Promise.reject(error);
        }
        refreshPromise = axios
          .post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          .then((response) => {
            const { access_token } = response.data;
            localStorage.setItem("token", access_token);
            return access_token;
          })
          .catch((refreshError) => {
            logger.error("Token refresh failed", refreshError);
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            window.location.href = "/login";
            return null;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newToken = await refreshPromise;
      if (newToken && originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } else {
        return Promise.reject(error);
      }
    }

    // Log error details
    logger.error("API response error", error);

    return Promise.reject(error);
  },
);

export default api;
