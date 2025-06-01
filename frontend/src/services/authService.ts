import { apiClient } from "./apiClient";
import { API_CONFIG } from "../config/api";
import { LoginDto, RegisterDto, AuthResponse, User } from "../types/auth";

export const authService = {
  async login(credentials: LoginDto): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(
      API_CONFIG.endpoints.auth.login,
      credentials,
    );
  },

  async register(userData: RegisterDto): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(
      API_CONFIG.endpoints.auth.register,
      userData,
    );
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(API_CONFIG.endpoints.auth.refresh, {
      refresh_token: refreshToken,
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>(API_CONFIG.endpoints.auth.me);
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post(API_CONFIG.endpoints.auth.logout);
    } finally {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
    }
  },

  async forgotPassword(email: string): Promise<void> {
    return apiClient.post(API_CONFIG.endpoints.auth.forgotPassword, { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    return apiClient.post(API_CONFIG.endpoints.auth.resetPassword, {
      token,
      password,
    });
  },

  async verifyEmail(token: string): Promise<void> {
    return apiClient.post(API_CONFIG.endpoints.auth.verifyEmail, { token });
  },

  async resendVerificationEmail(email: string): Promise<void> {
    return apiClient.post(API_CONFIG.endpoints.auth.resendVerification, {
      email,
    });
  },
};
