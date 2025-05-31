import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '../config';
import { useApi } from './useApi';

interface AuthState {
  token: string | null;
  requiresMFA: boolean;
  error: string | null;
}

interface MFASetupResponse {
  secret_key: string;
  qr_code_url: string;
  backup_codes: string[];
}

export const useAuth = () => {
  const [state, setState] = useState<AuthState>({
    token: localStorage.getItem('token'),
    requiresMFA: false,
    error: null,
  });

  const { post } = useApi();

  const login = useCallback(async (email: string, password: string, rememberMe: boolean) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await post(
        '/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const { access_token, requires_mfa } = response.data;

      if (config.ENABLE_MFA && requires_mfa) {
        setState(prev => ({ ...prev, requiresMFA: true }));
        return;
      }

      if (access_token) {
        localStorage.setItem('token', access_token);
        setState({
          token: access_token,
          requiresMFA: false,
          error: null,
        });
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.response?.data?.detail || 'An error occurred during login',
      }));
      throw error;
    }
  }, [post]);

  const verifyMFA = useCallback(async (code: string) => {
    try {
      const response = await post('/auth/mfa/verify', { code });
      const { access_token } = response.data;

      if (access_token) {
        localStorage.setItem('token', access_token);
        setState({
          token: access_token,
          requiresMFA: false,
          error: null,
        });
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.response?.data?.detail || 'Invalid MFA code',
      }));
      throw error;
    }
  }, [post]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setState({
      token: null,
      requiresMFA: false,
      error: null,
    });
  }, []);

  const setupMFA = async () => {
    try {
      const response = await axios.post<MFASetupResponse>(
        `${config.apiUrl}/auth/setup-mfa`,
        {},
        { withCredentials: true }
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const enableMFA = async (code: string) => {
    try {
      await axios.post(
        `${config.apiUrl}/auth/enable-mfa`,
        { code },
        { withCredentials: true }
      );
    } catch (error) {
      throw error;
    }
  };

  const requestPasswordReset = async (email: string) => {
    try {
      await axios.post(
        `${config.apiUrl}/auth/request-password-reset`,
        { email }
      );
    } catch (error) {
      throw error;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      await axios.post(
        `${config.apiUrl}/auth/reset-password`,
        { token, new_password: newPassword }
      );
    } catch (error) {
      throw error;
    }
  };

  const getAuthHeaders = () => {
    return {
      'X-CSRF-Token': axios.defaults.headers.common['X-CSRF-Token'],
    };
  };

  return {
    token: state.token,
    requiresMFA: state.requiresMFA,
    error: state.error,
    login,
    logout,
    verifyMFA,
    setupMFA,
    enableMFA,
    requestPasswordReset,
    resetPassword,
    getAuthHeaders,
  };
}; 