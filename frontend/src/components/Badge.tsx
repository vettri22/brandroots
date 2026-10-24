import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'critical' | 'warning' | 'suggestion' | 'success' | 'info' | 'neutral' | 'teal';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  const variantClasses = {
    critical: 'bg-rose-950/70 text-rose-300 border border-rose-800/60',
    warning: 'bg-amber-950/70 text-amber-300 border border-amber-800/60',
    suggestion: 'bg-indigo-950/70 text-indigo-300 border border-indigo-800/60',
    success: 'bg-emerald-950/70 text-emerald-300 border border-emerald-800/60',
    info: 'bg-sky-950/70 text-sky-300 border border-sky-800/60',
    neutral: 'bg-slate-800 text-slate-300 border border-slate-700',
    teal: 'bg-teal-950/80 text-teal-300 border border-teal-700/60',
  }[variant];

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${sizeClasses} ${variantClasses}`}>
      {children}
    </span>
  );
};
