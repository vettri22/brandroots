import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  role: UserRole;
  loading: boolean;
  switchRole: (role: UserRole) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  role: 'creator',
  loading: true,
  switchRole: async () => {},
  refreshUser: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>('creator');
  const [loading, setLoading] = useState<boolean>(true);

  const initAuth = async () => {
    try {
      const me = await api.getMe();
      setUser(me);
      setRole(me.role as UserRole);
    } catch (e) {
      // Default to demo creator login
      try {
        const res = await api.switchRole('creator');
        setUser(res.user);
        setRole('creator');
      } catch (err) {
        console.error('Failed to initialize default user', err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initAuth();
  }, []);

  const switchRole = async (newRole: UserRole) => {
    setLoading(true);
    try {
      const res = await api.switchRole(newRole);
      setUser(res.user);
      setRole(newRole);
    } catch (e) {
      console.error('Error switching role', e);
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      const me = await api.getMe();
      setUser(me);
      setRole(me.role as UserRole);
    } catch (e) {
      console.error('Error refreshing user', e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, role, loading, switchRole, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
