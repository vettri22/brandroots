import React from 'react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';
import { UserCheck, ShieldCheck, Award } from 'lucide-react';

export const RoleSwitcher: React.FC = () => {
  const { role, switchRole, user } = useAuth();

  const roles: Array<{ id: UserRole; label: string; icon: React.ReactNode; desc: string }> = [
    {
      id: 'creator',
      label: 'Creator',
      icon: <UserCheck className="w-3.5 h-3.5" />,
      desc: 'Submits drafts, accepts suggested edits',
    },
    {
      id: 'reviewer',
      label: 'Reviewer',
      icon: <ShieldCheck className="w-3.5 h-3.5" />,
      desc: 'Inspects drafts, requests revisions, approves/rejects',
    },
    {
      id: 'brand_owner',
      label: 'Brand Owner',
      icon: <Award className="w-3.5 h-3.5" />,
      desc: 'Manages guidelines, facts, approves Guideline Debugger fixes',
    },
  ];

  return (
    <div className="flex items-center space-x-2 bg-navy-900 border border-navy-700/80 p-1 rounded-lg">
      <span className="text-xs font-semibold text-slate-400 pl-2 pr-1 hidden sm:inline">Active Persona:</span>
      <div className="flex space-x-1">
        {roles.map((r) => {
          const isActive = role === r.id;
          return (
            <button
              key={r.id}
              onClick={() => switchRole(r.id)}
              title={r.desc}
              className={`flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
                isActive
                  ? 'bg-teal-500 text-slate-950 font-semibold shadow-sm shadow-teal-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-navy-800'
              }`}
            >
              {r.icon}
              <span>{r.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
