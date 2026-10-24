import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AuditEvent } from '../types';
import { Badge } from '../components/Badge';
import { History, Shield, Clock, Search, Filter } from 'lucide-react';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (e) {
      console.error('Failed to load audit logs', e);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter((log) =>
    filterType === 'all' ? true : log.event_type.toLowerCase().includes(filterType.toLowerCase())
  );

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <History className="w-5 h-5 text-teal-400" />
            <span>Immutable Governance Audit Trail</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Every rule edit, clarification approval, content submission, review decision, and finding resolution is permanently recorded.
          </p>
        </div>
        <div className="text-xs text-slate-400 font-mono">
          Total Recorded Events: <strong className="text-teal-400">{logs.length}</strong>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center space-x-2 bg-navy-950 p-2.5 rounded-xl border border-navy-800 text-xs">
        <Filter className="w-3.5 h-3.5 text-slate-500" />
        <span className="text-slate-400 font-semibold">Filter Event:</span>
        {['all', 'CLARIFICATION_APPROVED', 'REVIEW_COMPLETED', 'DOCUMENT_STATUS_TRANSITION', 'FINDING_RESOLVED'].map((evt) => (
          <button
            key={evt}
            onClick={() => setFilterType(evt)}
            className={`px-2.5 py-1 rounded-md font-mono text-[11px] transition-colors ${
              filterType === evt
                ? 'bg-teal-500/20 text-teal-300 font-semibold border border-teal-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {evt === 'all' ? 'All Events' : evt}
          </button>
        ))}
      </div>

      {/* Audit Table */}
      <div className="bg-navy-950 rounded-2xl border border-navy-800 shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-navy-800 bg-navy-900/40 text-slate-400 font-semibold">
                <th className="py-3 px-4 font-sans">Timestamp (UTC)</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4 font-sans">Actor</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Target</th>
                <th className="py-3 px-4 font-sans">Audit Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-900 text-[11px]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500 font-sans">
                    Loading audit trail...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500 font-sans">
                    No matching audit events found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-navy-900/50 transition-colors">
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(log.timestamp).toISOString().replace('T', ' ').slice(0, 19)}
                    </td>
                    <td className="py-3 px-4 text-teal-300 font-bold">{log.event_type}</td>
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium">{log.actor_name}</td>
                    <td className="py-3 px-4">
                      <Badge variant={log.actor_role === 'brand_owner' ? 'teal' : 'neutral'}>
                        {log.actor_role}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {log.target_type}:{log.target_id}
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans leading-relaxed">
                      {log.summary}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
