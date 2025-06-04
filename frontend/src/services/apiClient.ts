import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import {
  API_ENDPOINTS,
  ApiResponse,
  PaginatedResponse,
} from "../config/api";
import { logger } from "../utils/logger";

// Define ApiError as a class for use as a value
export class ApiError extends Error {
  status: number;
  errors?: Record<string, string[]>;
  constructor(status: number, message: string, errors?: Record<string, string[]>) {
    super(message);
    this.status = status;
    this.errors = errors;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

class ApiClient {
  private static instance: ApiClient;
  private client: AxiosInstance;

  private constructor() {
    // Validate required environment variables
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    if (!baseUrl) {
      throw new Error('VITE_API_BASE_URL environment variable is not defined');
    }

    // Validate timeout if provided
    const timeout = import.meta.env.VITE_API_TIMEOUT;
    let timeoutValue = 30000; // Default timeout
    if (timeout) {
      const parsedTimeout = Number(timeout);
      if (isNaN(parsedTimeout) || parsedTimeout <= 0) {
        throw new Error('VITE_API_TIMEOUT must be a positive number');
      }
      timeoutValue = parsedTimeout;
    }

    this.client = axios.create({
      baseURL: baseUrl,
      timeout: timeoutValue,
      headers: {
        "Content-Type": "application/json",
      },
    });
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
        const token = localStorage.getItem("token");
        if (token) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        logger.error("Request interceptor error:", error);
        return Promise.reject(error);
      },
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem("refreshToken");
            if (!refreshToken) {
              throw new Error("No refresh token available");
            }

            const response = await this.client.post("/api/auth/refresh", {
              refresh_token: refreshToken,
            });

            const { access_token } = response.data;
            localStorage.setItem("token", access_token);

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            logger.error("Token refresh failed:", refreshError);
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            window.location.href = "/login";
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        let message = "An unexpected error occurred";
        let errors: Record<string, string[]> | undefined = undefined;
        if (error.response?.data && typeof error.response.data === "object") {
          if ("message" in error.response.data) {
            message = (error.response.data as any).message;
          }
          if ("errors" in error.response.data) {
            errors = (error.response.data as any).errors;
          }
        }
        const apiError = new ApiError(
          error.response?.status || 500,
          message,
          errors,
        );

        logger.error("API error:", apiError);
        return Promise.reject(apiError);
      },
    );
  }

  public async get<T>(url: string, options?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, options);
    return response.data;
  }

  public async post<T>(
    url: string,
    data?: any,
    options?: AxiosRequestConfig,
  ): Promise<T> {
    const response = await this.client.post<T>(url, data, options);
    return response.data;
  }

  public async put<T>(
    url: string,
    data?: any,
    options?: AxiosRequestConfig,
  ): Promise<T> {
    const response = await this.client.put<T>(url, data, options);
    return response.data;
  }

  public async patch<T>(
    url: string,
    data?: any,
    options?: AxiosRequestConfig,
  ): Promise<T> {
    const response = await this.client.patch<T>(url, data, options);
    return response.data;
  }

  public async delete<T>(url: string, options?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, options);
    return response.data;
  }

  public async upload<T>(
    url: string,
    formData: FormData,
    options?: AxiosRequestConfig,
  ): Promise<T> {
    const response = await this.client.post<T>(url, formData, {
      ...options,
      headers: {
        ...options?.headers,
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }
}

export const apiClient = ApiClient.getInstance();
 