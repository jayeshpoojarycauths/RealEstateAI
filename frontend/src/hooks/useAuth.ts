import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../config/api";
import {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  User,
} from "../types/auth";
import { useToast } from "../components/common/Toast";
import { logger } from "../utils/logger";

// Re-use the keys that the Axios interceptors expect so that both layers share the same source of truth
const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY ?? "auth_token";
const REFRESH_TOKEN_KEY =
  import.meta.env.VITE_AUTH_REFRESH_TOKEN_KEY ?? "auth_refresh_token";
const USER_KEY = "auth_user";

export const useAuth = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem(USER_KEY);
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.post("/auth/login", credentials);
        const { user, token } = response.data;
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        setUser(user);
        showToast("success", "Login successful");
        navigate("/dashboard");
        logger.info("User logged in successfully", { userId: user.id });
      } catch (err) {
        const error = err as Error;
        setError(error.message);
        showToast("error", "Login failed: " + error.message);
        logger.error("Login failed:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, showToast],
  );

  const register = useCallback(
    async (data: RegisterData) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.post("/auth/register", data);
        const { user, token } = response.data;
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        setUser(user);
        showToast("success", "Registration successful. Please login.");
        navigate("/login");
        logger.info("User registered successfully", { userId: user.id });
      } catch (err) {
        const error = err as Error;
        setError(error.message);
        showToast("error", "Registration failed: " + error.message);
        logger.error("Registration failed:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, showToast],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    showToast("success", "Logged out successfully");
    navigate("/login");
    logger.info("User logged out");
  }, [navigate, showToast]);

  const refreshToken = useCallback(async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      const response = await api.post("/auth/refresh");
      const { user, token: newToken } = response.data;
      localStorage.setItem(TOKEN_KEY, newToken);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      setUser(user);
      logger.info("Token refreshed successfully", { userId: user.id });
    } catch (err) {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
      logger.error("Token refresh failed", err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const requestPasswordReset = async (email: string) => {
    try {
      setError(null);
      await api.post("/auth/forgot-password", { email });
      logger.info("Password reset requested", { email });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Password reset request failed";
      setError(message);
      logger.error("Password reset request failed", err as Error);
      throw err;
    }
  };

  const requestUsernameReminder = async (email: string) => {
    try {
      setError(null);
      await api.post("/auth/forgot-username", { email });
      logger.info("Username reminder requested", { email });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Username reminder request failed";
      setError(message);
      logger.error("Username reminder request failed", err as Error);
      throw err;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      setError(null);
      await api.post("/auth/reset-password", { token, new_password: newPassword });
      logger.info("Password reset successful");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Password reset failed";
      setError(message);
      logger.error("Password reset failed", err as Error);
      throw err;
    }
  };

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      refreshToken();
    }
  }, [refreshToken]);

  return {
    user,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshToken,
    requestPasswordReset,
    requestUsernameReminder,
    resetPassword,
  };
};
