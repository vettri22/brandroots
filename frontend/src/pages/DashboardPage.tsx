import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardMetrics, AuditEvent } from '../types';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  AlertCircle,
  CheckCircle,
  Radar,
  TrendingUp,
  ShieldAlert,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Scale,
  FileCheck2,
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { user, activeBrand } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentLogs, setRecentLogs] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [activeBrand]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [m, logs] = await Promise.all([
        api.getDashboardMetrics(activeBrand?.id),
        api.getAuditLogs(10)
      ]);
      setMetrics(m);
      setRecentLogs(logs);
    } catch (e) {
      console.error('Failed to load dashboard data', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-teal-400">
          <div className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Loading Governance Hub...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="bg-navy-950 border border-navy-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-2xl font-black text-white tracking-tight">Proofline Governance Hub</h1>
            <Badge variant="teal">ENTERPRISE PLATFORM</Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
            Active brand: <strong className="text-slate-200">{activeBrand?.name || 'NovusBio Health'}</strong> • Hybrid Compliance Engine • Traceable Evidence Ledger • Version-Bound Sign-offs
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('queue')}
            className="flex items-center space-x-2 px-4 py-2 bg-navy-900 hover:bg-navy-800 text-slate-200 rounded-xl text-xs font-semibold border border-navy-700 transition-colors"
          >
            <FileCheck2 className="w-4 h-4 text-teal-400" />
            <span>Review Queue</span>
          </button>
          <button
            onClick={() => onNavigate('evidence')}
            className="flex items-center space-x-2 px-4 py-2 bg-navy-900 hover:bg-navy-800 text-slate-200 rounded-xl text-xs font-semibold border border-navy-700 transition-colors"
          >
            <Scale className="w-4 h-4 text-cyan-400" />
            <span>Evidence Ledger</span>
          </button>
          <button
            onClick={() => onNavigate('radar')}
            className="flex items-center space-x-2 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 rounded-xl text-xs font-bold shadow-lg shadow-teal-500/20 transition-all"
          >
            <Radar className="w-4 h-4" />
            <span>Clarity Radar</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Pending Reviews */}
        <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
            <span>Pending Reviews</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-white tracking-tight">
            {metrics?.pending_reviews ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-2 flex items-center space-x-1">
            <span>Across</span>
            <strong className="text-slate-400">{metrics?.total_documents ?? 0}</strong>
            <span>total drafts</span>
          </div>
        </div>

        {/* Card 2: Approved Documents */}
        <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
            <span>Approved & Published</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-black text-white tracking-tight">
            {metrics?.approved_documents ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            Exact version-bound sign-offs
          </div>
        </div>

        {/* Card 3: Guideline Ambiguity Signals */}
        <div className="bg-navy-950 p-5 rounded-2xl border border-teal-800/40 shadow-md bg-gradient-to-br from-navy-950 to-teal-950/20">
          <div className="flex items-center justify-between text-teal-400 text-xs font-medium mb-3">
            <span>Clarity Radar Signals</span>
            <Radar className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-3xl font-black text-teal-300 tracking-tight">
            {metrics?.guideline_ambiguity_candidates ?? 0}
          </div>
          <div className="text-[11px] text-teal-400/70 mt-2 flex items-center space-x-1">
            <span>Recurring friction clusters</span>
          </div>
        </div>

        {/* Card 4: Active Knowledge Base */}
        <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
            <span>Evidence & Rule Base</span>
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-black text-white tracking-tight">
            {(metrics?.active_guidelines_count ?? 0) + (metrics?.active_facts_count ?? 0)}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            {metrics?.active_guidelines_count} Rules • {metrics?.active_facts_count} Verified Evidence
          </div>
        </div>
      </div>

      {/* Middle Section: Findings Breakdown & Top Recurring Violations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Findings by Severity */}
        <div className="bg-navy-950 p-6 rounded-2xl border border-navy-800 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-white tracking-tight">Compliance Findings by Severity</h2>
            <span className="text-xs text-slate-500">Live database audit</span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-rose-300 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Critical Violations (Unsupported claims / Pricing errors)</span>
                </span>
                <span className="font-mono text-white font-bold">{metrics?.findings_by_severity.critical ?? 0}</span>
              </div>
              <div className="w-full bg-navy-900 rounded-full h-2">
                <div
                  className="bg-rose-500 h-2 rounded-full"
                  style={{ width: `${Math.min(100, ((metrics?.findings_by_severity.critical ?? 0) / 10) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-amber-300 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  <span>Warnings (Tone, formatting & mandatory disclaimers)</span>
                </span>
                <span className="font-mono text-white font-bold">{metrics?.findings_by_severity.warning ?? 0}</span>
              </div>
              <div className="w-full bg-navy-900 rounded-full h-2">
                <div
                  className="bg-amber-500 h-2 rounded-full"
                  style={{ width: `${Math.min(100, ((metrics?.findings_by_severity.warning ?? 0) / 10) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-indigo-300 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span>Suggestions (Terminology & style polish)</span>
                </span>
                <span className="font-mono text-white font-bold">{metrics?.findings_by_severity.suggestion ?? 0}</span>
              </div>
              <div className="w-full bg-navy-900 rounded-full h-2">
                <div
                  className="bg-indigo-500 h-2 rounded-full"
                  style={{ width: `${Math.min(100, ((metrics?.findings_by_severity.suggestion ?? 0) / 10) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Top Recurring Violations */}
        <div className="bg-navy-950 p-6 rounded-2xl border border-navy-800 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-teal-400" />
              <span>Top Recurring Violations (Radar Telemetry)</span>
            </h2>
            <button
              onClick={() => onNavigate('radar')}
              className="text-xs text-teal-400 hover:text-teal-300 flex items-center space-x-1 font-semibold"
            >
              <span>View Radar</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-navy-800">
            {metrics?.top_recurring_violations && metrics.top_recurring_violations.length > 0 ? (
              metrics.top_recurring_violations.map((v, i) => (
                <div key={i} className="py-3 flex items-center justify-between text-xs">
                  <div>
                    <div className="font-mono text-teal-300 font-semibold">{v.rule_id}</div>
                    <div className="text-[11px] text-slate-400">
                      {v.rule_id === 'RULE-CLAIM-01'
                        ? 'Promotional Claim Boundaries & Outcome Guarantees'
                        : v.rule_id === 'FACT-PRICE-PRO'
                        ? 'Outdated Commercial Pricing ($29/mo citations)'
                        : 'Brand Terminology Compliance'}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60">
                      {v.count} occurrences
                    </span>
                    <button
                      onClick={() => onNavigate('radar')}
                      className="text-[11px] px-2 py-1 bg-navy-800 hover:bg-navy-700 text-slate-300 rounded transition-colors"
                    >
                      Investigate
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-500 py-4 text-center">No recurring violations recorded yet.</div>
            )}
          </div>
        </div>
      </div>

      {/* Live Audit Log Stream */}
      <div className="bg-navy-950 p-6 rounded-2xl border border-navy-800 shadow-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-teal-400" />
            <h2 className="text-sm font-bold text-white tracking-tight">Recent Governance Audit Trail</h2>
          </div>
          <button
            onClick={() => onNavigate('audit')}
            className="text-xs text-slate-400 hover:text-white"
          >
            Full Audit Log
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-navy-800 text-slate-400 font-semibold">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Event</th>
                <th className="py-2.5 px-3">Actor</th>
                <th className="py-2.5 px-3">Role</th>
                <th className="py-2.5 px-3">Action Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-900 font-mono text-[11px]">
              {recentLogs.map((log) => (
                <tr key={log.id} className="hover:bg-navy-900/50 transition-colors">
                  <td className="py-2.5 px-3 text-slate-500">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="font-semibold text-teal-300">{log.event_type}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 font-sans">{log.actor_name}</td>
                  <td className="py-2.5 px-3">
                    <Badge variant={log.actor_role === 'brand_owner' ? 'teal' : 'neutral'}>
                      {log.actor_role}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 font-sans truncate max-w-[360px]" title={log.summary}>
                    {log.summary}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
