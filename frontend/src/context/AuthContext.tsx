import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { User, Profile } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<Profile>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('jobguard_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async () => {
    try {
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }
      const response = await api.get<User>('/auth/me');
      setUser(response.data);
    } catch (err) {
      console.error('Failed to fetch user:', err);
      localStorage.removeItem('jobguard_token');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await api.post<{ access_token: string }>('/auth/login', {
      email,
      password,
    });
    const newToken = response.data.access_token;
    localStorage.setItem('jobguard_token', newToken);
    setToken(newToken);
    const meRes = await api.get<User>('/auth/me', {
      headers: { Authorization: `Bearer ${newToken}` },
    });
    setUser(meRes.data);
  };

  const register = async (name: string, email: string, password: string) => {
    await api.post('/auth/register', { name, email, password });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('jobguard_token');
    setToken(null);
    setUser(null);
  };

  const updateProfile = async (data: Partial<Profile>) => {
    await api.put('/profile', data);
    await fetchCurrentUser();
  };

  const refreshUser = async () => {
    await fetchCurrentUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

