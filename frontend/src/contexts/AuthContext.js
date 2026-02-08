import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

async function loadCurrentUser() {
  const response = await authAPI.me();
  return response.data;
}

function toErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const parts = detail
      .map((item) => {
        if (!item || typeof item !== 'object') return null;
        if (typeof item.msg === 'string' && item.msg.trim()) return item.msg;
        if (typeof item.message === 'string' && item.message.trim()) return item.message;
        return null;
      })
      .filter(Boolean);
    if (parts.length > 0) {
      return parts.join('; ');
    }
  }

  if (detail && typeof detail === 'object') {
    const maybeMessage = detail.message || detail.error;
    if (typeof maybeMessage === 'string' && maybeMessage.trim()) {
      return maybeMessage;
    }
  }

  return fallbackMessage;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const bootstrap = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        if (mounted) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const currentUser = await loadCurrentUser();
        if (mounted) {
          setUser(currentUser);
        }
      } catch {
        localStorage.removeItem('accessToken');
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    bootstrap();

    return () => {
      mounted = false;
    };
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.loginJson({ email, password });
      localStorage.setItem('accessToken', response.data.access_token);
      const currentUser = await loadCurrentUser();
      setUser(currentUser);
      return { success: true };
    } catch (error) {
      return { success: false, error: toErrorMessage(error, 'Login failed') };
    }
  };

  const register = async (payload) => {
    try {
      const response = await authAPI.register(payload);
      return { success: true, user: response.data };
    } catch (error) {
      return { success: false, error: toErrorMessage(error, 'Registration failed') };
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
