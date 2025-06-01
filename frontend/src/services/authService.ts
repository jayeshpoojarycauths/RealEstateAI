import { apiClient } from "./apiClient";
import { API_ENDPOINTS } from "../config/api";
import { LoginDto, RegisterDto, AuthResponse, User } from "../types/auth";

export const authService = {
  async login(credentials: LoginDto): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials,
    );
  },

  async register(userData: RegisterDto): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      userData,
    );
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>(API_ENDPOINTS.AUTH.REFRESH, {
      refresh_token: refreshToken,
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>(API_ENDPOINTS.AUTH.ME);
  },

  async logout(): Promise<void> {
    try {
      // If you have a logout endpoint, use it here. Otherwise, just clear tokens.
      // await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } finally {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
    }
  },

  async forgotPassword(email: string): Promise<void> {
    // If you have a forgot password endpoint, use it here.
    // return apiClient.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    return apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
      token,
      password,
    });
  },

  async verifyEmail(token: string): Promise<void> {
    return apiClient.post(API_ENDPOINTS.AUTH.VERIFY_EMAIL, { token });
  },

  async resendVerificationEmail(email: string): Promise<void> {
    return apiClient.post(API_ENDPOINTS.AUTH.RESEND_VERIFICATION, {
      email,
    });
  },
};
