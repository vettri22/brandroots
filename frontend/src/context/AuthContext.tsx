import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole, Brand, NotificationItem } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  role: UserRole;
  loading: boolean;
  activeBrand: Brand | null;
  brands: Brand[];
  notifications: NotificationItem[];
  unreadNotificationCount: number;
  switchRole: (role: UserRole) => Promise<void>;
  switchBrand: (brandId: string) => void;
  refreshUser: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  role: 'creator',
  loading: true,
  activeBrand: null,
  brands: [],
  notifications: [],
  unreadNotificationCount: 0,
  switchRole: async () => {},
  switchBrand: () => {},
  refreshUser: async () => {},
  refreshNotifications: async () => {},
  logout: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>('creator');
  const [loading, setLoading] = useState<boolean>(true);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [activeBrand, setActiveBrand] = useState<Brand | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const initData = async () => {
    try {
      // 1. Fetch user profile
      let me: User;
      try {
        me = await api.getMe();
      } catch {
        // Fallback to demo creator for instant local accessibility
        const res = await api.switchRole('creator');
        me = res.user;
      }
      setUser(me);
      setRole(me.role as UserRole);

      // 2. Fetch brands
      const brandList = await api.listBrands().catch(() => []);
      setBrands(brandList);
      if (brandList.length > 0) {
        setActiveBrand(brandList[0]);
      }

      // 3. Fetch notifications
      const notifs = await api.listNotifications().catch(() => []);
      setNotifications(notifs);
    } catch (err) {
      console.error('Initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initData();
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

  const switchBrand = (brandId: string) => {
    const found = brands.find((b) => b.id === brandId);
    if (found) {
      setActiveBrand(found);
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

  const refreshNotifications = async () => {
    try {
      const notifs = await api.listNotifications();
      setNotifications(notifs);
    } catch (e) {
      console.error('Error refreshing notifications', e);
    }
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
  };

  const unreadNotificationCount = notifications.filter((n) => !n.is_read).length;

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        loading,
        activeBrand,
        brands,
        notifications,
        unreadNotificationCount,
        switchRole,
        switchBrand,
        refreshUser,
        refreshNotifications,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
