import React from 'react';
import { RoleSwitcher } from './RoleSwitcher';
import { api } from '../services/api';
import { Sparkles, RotateCcw, Shield, Layers } from 'lucide-react';

interface NavbarProps {
  onRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh }) => {
  const [resetting, setResetting] = React.useState(false);

  const handleResetDemo = async () => {
    if (confirm('Reset all demo data back to initial Hackathon Round 2 baseline?')) {
      setResetting(true);
      try {
        await api.resetDemoData();
        if (onRefresh) onRefresh();
        window.location.reload();
      } catch (err) {
        alert('Failed to reset demo data');
      } finally {
        setResetting(false);
      }
    }
  };

  return (
    <header className="h-16 bg-navy-950/90 border-b border-navy-800 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand & Workspace */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center shadow-lg shadow-teal-500/20 text-slate-950 font-black text-lg tracking-tight">
            BR
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white text-base tracking-tight">BrandRoots</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-teal-950 text-teal-300 border border-teal-700/60 font-semibold">
                v2.0
              </span>
            </div>
            <div className="text-xs text-slate-400 flex items-center space-x-1.5">
              <span>NovusBio Health</span>
              <span className="text-slate-600">•</span>
              <span className="text-teal-400/90">Inkloom Round 2</span>
            </div>
          </div>
        </div>
      </div>

      {/* Middle Persona Switcher */}
      <div className="hidden md:flex items-center space-x-3">
        <RoleSwitcher />
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-3">
        <button
          onClick={handleResetDemo}
          disabled={resetting}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white bg-navy-900 hover:bg-navy-800 border border-navy-700/80 px-3 py-1.5 rounded-lg transition-colors"
          title="Reset demonstration data"
        >
          <RotateCcw className={`w-3.5 h-3.5 text-teal-400 ${resetting ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Reset Demo</span>
        </button>

        <div className="hidden lg:flex items-center space-x-1 px-2.5 py-1 rounded-full bg-navy-900 border border-navy-700 text-[11px] text-slate-400">
          <Shield className="w-3.5 h-3.5 text-teal-400" />
          <span>Team: <strong className="text-slate-200">vettriselvam190</strong></span>
        </div>
      </div>
    </header>
  );
};
