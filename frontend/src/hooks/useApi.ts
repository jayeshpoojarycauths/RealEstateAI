import { useCallback } from "react";
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import config from "../config"; // ✅ Uses env-based config

const api = axios.create({
  baseURL: config.apiUrl, // ✅ Dynamically set via .env
  headers: {
    "Content-Type": "application/json",
  },
});

console.log("API Base URL (from config):", config.apiUrl);

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for 401 handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// Custom API hook
export const useApi = () => {
  const get = useCallback(
    async <T = any>(
      url: string,
      config?: AxiosRequestConfig,
    ): Promise<AxiosResponse<T>> => {
      return api.get<T>(url, config);
    },
    [],
  );

  const post = useCallback(
    async <T = any>(
      url: string,
      data?: any,
      config?: AxiosRequestConfig,
    ): Promise<AxiosResponse<T>> => {
      return api.post<T>(url, data, config);
    },
    [],
  );

  const put = useCallback(
    async <T = any>(
      url: string,
      data?: any,
      config?: AxiosRequestConfig,
    ): Promise<AxiosResponse<T>> => {
      return api.put<T>(url, data, config);
    },
    [],
  );

  const del = useCallback(
    async <T = any>(
      url: string,
      config?: AxiosRequestConfig,
    ): Promise<AxiosResponse<T>> => {
      return api.delete<T>(url, config);
    },
    [],
  );

  return {
    get,
    post,
    put,
    delete: del,
  };
};
