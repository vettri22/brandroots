import React from 'react';
import {
  LayoutDashboard,
  FileCheck2,
  BugPlay,
  BookOpenCheck,
  History,
  Compass,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const navItems = [
    {
      id: 'dashboard',
      label: 'Governance Hub',
      icon: <LayoutDashboard className="w-4 h-4" />,
    },
    {
      id: 'workbench',
      label: 'Review Workbench',
      icon: <FileCheck2 className="w-4 h-4" />,
    },
    {
      id: 'debugger',
      label: 'Guideline Debugger',
      icon: <BugPlay className="w-4 h-4 text-teal-400" />,
      badge: 'SIGNATURE',
    },
    {
      id: 'brand',
      label: 'Brand Knowledge',
      icon: <BookOpenCheck className="w-4 h-4" />,
    },
    {
      id: 'audit',
      label: 'Audit Trail',
      icon: <History className="w-4 h-4" />,
    },
    {
      id: 'demo',
      label: 'Judge Walkthrough',
      icon: <Compass className="w-4 h-4 text-amber-400" />,
      badge: '9-STEP DEMO',
      badgeColor: 'amber',
    },
  ];

  return (
    <aside className="w-64 bg-navy-950 border-r border-navy-800 flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
            Governance Workflows
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/10 text-teal-300 border border-teal-500/30 font-semibold shadow-sm shadow-teal-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-navy-900 border border-transparent'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className={isActive ? 'text-teal-400' : 'text-slate-400'}>
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] font-bold font-mono px-1.5 py-0.5 rounded ${
                        item.badgeColor === 'amber'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-teal-950 text-teal-300 border border-teal-800'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info Box */}
      <div className="p-3 bg-navy-900/60 rounded-xl border border-navy-800/80 text-xs">
        <div className="flex items-center space-x-2 text-teal-400 font-semibold mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Hybrid Engine</span>
        </div>
        <p className="text-slate-400 text-[11px] leading-relaxed">
          Combines deterministic rules, verified facts, and AI contextual claim checks with explainable sources.
        </p>
      </div>
    </aside>
  );
};
