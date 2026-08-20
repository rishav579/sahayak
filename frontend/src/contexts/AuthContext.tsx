import { createContext, ReactNode, useContext, useMemo, useState } from 'react';
import { api } from '../services/api';
import { AuthResponse, User } from '../types';

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('sahayak_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('sahayak_token'));

  const loginWithGoogle = async (credential: string) => {
    const { data } = await api.post<AuthResponse>('/auth/google', { credential });
    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('sahayak_user', JSON.stringify(data.user));
    localStorage.setItem('sahayak_token', data.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('sahayak_user');
    localStorage.removeItem('sahayak_token');
  };

  const value = useMemo(() => ({ user, token, loginWithGoogle, logout }), [user, token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
