import React, { useState } from 'react';
import { RoleSwitcher } from './RoleSwitcher';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import {
  Shield,
  Layers,
  Bell,
  Check,
  ChevronDown,
  Building2,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

interface NavbarProps {
  onRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh }) => {
  const { user, brands, activeBrand, switchBrand, notifications, unreadNotificationCount, refreshNotifications } = useAuth();
  const [showBrandDropdown, setShowBrandDropdown] = useState(false);
  const [showNotificationDropdown, setShowNotificationDropdown] = useState(false);

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      await refreshNotifications();
    } catch (e) {
      console.error('Failed to mark all notifications read', e);
    }
  };

  const handleNotificationClick = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      await refreshNotifications();
    } catch (e) {
      console.error('Failed to mark notification read', e);
    }
  };

  return (
    <header className="h-16 bg-navy-950/95 border-b border-navy-800 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Workspace Switcher */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-teal-600 flex items-center justify-center shadow-lg shadow-teal-500/20 text-slate-950 font-black text-sm tracking-wider">
            PL
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-white text-base tracking-tight">Proofline</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-teal-950 text-teal-300 border border-teal-700/60 font-semibold">
                ENTERPRISE
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              Brand Governance Platform
            </div>
          </div>
        </div>

        {/* Brand Workspace Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowBrandDropdown(!showBrandDropdown)}
            className="flex items-center space-x-2 bg-navy-900 hover:bg-navy-850 border border-navy-800 hover:border-navy-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 transition-colors"
          >
            <Building2 className="w-3.5 h-3.5 text-teal-400" />
            <span className="font-semibold">{activeBrand?.name || 'NovusBio Health'}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showBrandDropdown && (
            <div className="absolute left-0 mt-2 w-56 bg-navy-950 border border-navy-700 rounded-xl shadow-2xl p-2 z-50">
              <div className="text-[10px] font-bold text-slate-500 uppercase px-2 py-1">
                Switch Brand Workspace
              </div>
              <div className="space-y-1">
                {brands.length > 0 ? (
                  brands.map((b) => (
                    <button
                      key={b.id}
                      onClick={() => {
                        switchBrand(b.id);
                        setShowBrandDropdown(false);
                      }}
                      className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center justify-between transition-colors ${
                        activeBrand?.id === b.id
                          ? 'bg-teal-500/20 text-teal-300 font-semibold'
                          : 'text-slate-300 hover:bg-navy-900 hover:text-white'
                      }`}
                    >
                      <span className="truncate">{b.name}</span>
                      {activeBrand?.id === b.id && <Check className="w-3.5 h-3.5 text-teal-400 shrink-0" />}
                    </button>
                  ))
                ) : (
                  <div className="text-xs text-slate-500 px-2 py-1">NovusBio Health (Active)</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Middle Role Switcher */}
      <div className="hidden md:flex items-center space-x-3">
        <RoleSwitcher />
      </div>

      {/* Right Controls: Notifications & User Profile */}
      <div className="flex items-center space-x-3">
        {/* Notifications Popover */}
        <div className="relative">
          <button
            onClick={() => setShowNotificationDropdown(!showNotificationDropdown)}
            className="relative p-2 rounded-xl bg-navy-900 hover:bg-navy-800 text-slate-300 hover:text-white border border-navy-800 transition-colors"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadNotificationCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-teal-500 text-slate-950 font-black text-[9px] rounded-full flex items-center justify-center animate-pulse">
                {unreadNotificationCount}
              </span>
            )}
          </button>

          {showNotificationDropdown && (
            <div className="absolute right-0 mt-2 w-80 bg-navy-950 border border-navy-700 rounded-2xl shadow-2xl p-4 z-50">
              <div className="flex items-center justify-between pb-3 border-b border-navy-800 mb-2">
                <span className="text-xs font-bold text-white">Notifications</span>
                {unreadNotificationCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-[11px] text-teal-400 hover:text-teal-300"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto">
                {notifications.length > 0 ? (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => handleNotificationClick(n.id)}
                      className={`p-2.5 rounded-xl text-xs cursor-pointer transition-colors ${
                        n.is_read
                          ? 'bg-navy-900/40 text-slate-400'
                          : 'bg-navy-900 text-slate-200 border border-navy-750'
                      }`}
                    >
                      <div className="flex items-center justify-between font-semibold mb-0.5">
                        <span className="text-white text-xs">{n.title}</span>
                        {!n.is_read && <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-snug">{n.message}</p>
                      <div className="text-[9px] text-slate-500 mt-1 font-mono">
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-slate-500 py-6 text-center">
                    No new notifications
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill */}
        <div className="flex items-center space-x-2.5 px-3 py-1.5 rounded-xl bg-navy-900 border border-navy-800 text-xs">
          <div className="w-6 h-6 rounded-lg bg-teal-500/20 text-teal-400 border border-teal-500/40 flex items-center justify-center font-bold text-xs">
            {user?.full_name ? user.full_name.slice(0, 1).toUpperCase() : 'U'}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-white font-semibold text-xs leading-none">{user?.full_name || 'Sarah Chen'}</div>
            <div className="text-[10px] text-teal-400 font-mono capitalize leading-none mt-0.5">{user?.role || 'creator'}</div>
          </div>
        </div>
      </div>
    </header>
  );
};
