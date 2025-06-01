import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../config/api';
import { AuthResponse, LoginCredentials, RegisterData, User } from '../types/auth';
import { useToast } from '../components/common/Toast';
import { logger } from '../utils/logger';

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';
const USER_KEY = 'auth_user';

export const useAuth = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem(USER_KEY);
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      setError(null);
      const { data } = await api.post<AuthResponse>('/auth/login', credentials);
      localStorage.setItem(TOKEN_KEY, data.token);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
      showToast('success', 'Login successful');
      navigate('/dashboard');
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      showToast('error', 'Login failed: ' + error.message);
      logger.error('Login failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [navigate, showToast]);

  const register = useCallback(async (data: RegisterData) => {
    try {
      setIsLoading(true);
      setError(null);
      await api.post('/auth/register', data);
      showToast('success', 'Registration successful. Please login.');
      navigate('/login');
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      showToast('error', 'Registration failed: ' + error.message);
      logger.error('Registration failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [navigate, showToast]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    showToast('success', 'Logged out successfully');
    navigate('/login');
  }, [navigate, showToast]);

  const refreshToken = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        throw new Error('No refresh token found');
      }

      const { data } = await api.post<AuthResponse>('/auth/refresh', {
        refreshToken,
      });

      localStorage.setItem(TOKEN_KEY, data.token);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setUser(data.user);
    } catch (err) {
      const error = err as Error;
      logger.error('Token refresh failed:', error);
      logout();
    }
  }, [logout]);

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
  };
}; 