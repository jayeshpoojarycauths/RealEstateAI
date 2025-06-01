import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CLIENT_CONFIG, ApiError, RequestOptions } from '../config/api';
import { logger } from '../utils/logger';

class ApiClient {
  private static instance: ApiClient;
  private client: AxiosInstance;

  private constructor() {
    this.client = axios.create(API_CLIENT_CONFIG);
    this.setupInterceptors();
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        logger.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            const response = await this.client.post('/api/auth/refresh', {
              refresh_token: refreshToken,
            });

            const { access_token } = response.data;
            localStorage.setItem('token', access_token);

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            logger.error('Token refresh failed:', refreshError);
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        const apiError = new ApiError(
          error.response?.status || 500,
          error.response?.data?.message || 'An unexpected error occurred',
          error.response?.data
        );

        logger.error('API error:', apiError);
        return Promise.reject(apiError);
      }
    );
  }

  public async get<T>(url: string, options?: RequestOptions): Promise<T> {
    const response = await this.client.get<T>(url, options);
    return response.data;
  }

  public async post<T>(url: string, data?: any, options?: RequestOptions): Promise<T> {
    const response = await this.client.post<T>(url, data, options);
    return response.data;
  }

  public async put<T>(url: string, data?: any, options?: RequestOptions): Promise<T> {
    const response = await this.client.put<T>(url, data, options);
    return response.data;
  }

  public async patch<T>(url: string, data?: any, options?: RequestOptions): Promise<T> {
    const response = await this.client.patch<T>(url, data, options);
    return response.data;
  }

  public async delete<T>(url: string, options?: RequestOptions): Promise<T> {
    const response = await this.client.delete<T>(url, options);
    return response.data;
  }

  public async upload<T>(url: string, formData: FormData, options?: RequestOptions): Promise<T> {
    const response = await this.client.post<T>(url, formData, {
      ...options,
      headers: {
        ...options?.headers,
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export const apiClient = ApiClient.getInstance(); 