import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import type { User } from '../services/types';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('lanaspau_token'));
  const [user, setUser] = useState<User | null>(JSON.parse(localStorage.getItem('lanaspau_user') || 'null'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem('lanaspau_token', token);
    } else {
      localStorage.removeItem('lanaspau_token');
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem('lanaspau_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('lanaspau_user');
    }
  }, [user]);

  async function login(email: string, password: string) {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      setToken(response.data.access_token);
      setUser(response.data.user);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  const value = useMemo(() => ({ user, token, loading, login, logout, isAuthenticated: Boolean(token) }), [user, token, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}
