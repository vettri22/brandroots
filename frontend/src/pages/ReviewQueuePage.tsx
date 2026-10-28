import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ContentDocument, ReviewJob, User } from '../types';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/Badge';
import {
  FileCheck2,
  Clock,
  UserCheck,
  AlertTriangle,
  ArrowRight,
  Filter,
  CheckCircle2,
  ShieldAlert,
  Search,
  RefreshCw,
} from 'lucide-react';

interface QueueItem {
  document: ContentDocument;
  latest_review_job: ReviewJob | null;
}

interface ReviewQueuePageProps {
  onOpenDocument: (documentId: string) => void;
}

export const ReviewQueuePage: React.FC<ReviewQueuePageProps> = ({ onOpenDocument }) => {
  const { user, role, activeBrand } = useAuth();
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [teamMembers, setTeamMembers] = useState<User[]>([]);
  const [assigningDocId, setAssigningDocId] = useState<string | null>(null);
  const [selectedReviewerId, setSelectedReviewerId] = useState<string>('');
  const [actionError, setActionError] = useState<string>('');

  const loadQueue = async () => {
    try {
      setLoading(true);
      const items = await api.getReviewQueue(activeBrand?.id);
      setQueueItems(items);
      const orgId = user?.organization_id || 'org-demo-001';
      const memberships = await api.listMembers(orgId).catch(() => []);
      const users: User[] = memberships.map((m: any) => ({
        id: m.user_id,
        email: m.user_email || 'user@proofline.internal',
        full_name: m.user_name || m.user_email || 'Team Reviewer',
        role: m.role as any,
        is_active: true,
        organization_id: m.organization_id,
        created_at: m.created_at,
      }));
      setTeamMembers(users);
    } catch (err: any) {
      console.error('Failed to load review queue:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [activeBrand]);

  const handleAssignReviewer = async (docId: string) => {
    if (!selectedReviewerId) return;
    setActionError('');
    try {
      await api.assignReviewer(docId, selectedReviewerId);
      setAssigningDocId(null);
      setSelectedReviewerId('');
      await loadQueue();
    } catch (err: any) {
      setActionError(err.message || 'Failed to assign reviewer');
    }
  };

  const filteredItems = queueItems.filter((item) => {
    const doc = item.document;
    if (statusFilter !== 'all' && doc.status !== statusFilter) return false;
    if (
      searchQuery &&
      !doc.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !doc.creator_name.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'submitted':
        return <Badge variant="warning">SUBMITTED</Badge>;
      case 'in_review':
        return <Badge variant="teal">IN REVIEW</Badge>;
      case 'changes_requested':
        return <Badge variant="critical">CHANGES REQUESTED</Badge>;
      case 'resubmitted':
        return <Badge variant="teal">RESUBMITTED</Badge>;
      default:
        return <Badge variant="neutral">{status.toUpperCase()}</Badge>;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">
            <FileCheck2 className="w-4 h-4" />
            <span>Governance Gate</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">Review & Approval Queue</h1>
          <p className="text-xs text-slate-400 mt-1">
            Pending content awaiting verification, rule enforcement, and version-bound sign-off.
          </p>
        </div>

        <button
          onClick={loadQueue}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3.5 py-2 bg-navy-900 hover:bg-navy-800 text-slate-300 text-xs font-medium rounded-xl border border-navy-700 transition-colors self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-teal-400 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {actionError && (
        <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-navy-950 p-4 rounded-2xl border border-navy-800 shadow-sm">
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-semibold text-slate-400">Filter Status:</span>
          {(['all', 'submitted', 'in_review', 'resubmitted'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === st
                  ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                  : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
              }`}
            >
              {st === 'all' ? 'All Pending' : st.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-navy-900 border border-navy-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-400"
          />
        </div>
      </div>

      {/* Queue Table */}
      <div className="bg-navy-950 rounded-2xl border border-navy-800 overflow-hidden shadow-lg">
        {loading ? (
          <div className="p-12 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin text-teal-400 mx-auto mb-2" />
            <p className="text-xs">Loading queue items...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3 opacity-80" />
            <h3 className="text-base font-bold text-white mb-1">Queue is clear!</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              There are no content drafts currently waiting for review matching the current criteria.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-navy-800/80">
            {filteredItems.map(({ document: doc, latest_review_job: job }) => {
              const score = job?.compliance_score ?? null;
              const findingsCount = job?.findings?.length ?? 0;
              const criticalCount = job?.findings?.filter((f) => f.severity === 'critical' || f.severity === 'high').length ?? 0;

              return (
                <div
                  key={doc.id}
                  className="p-5 hover:bg-navy-900/40 transition-colors flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center space-x-2.5">
                      {getStatusBadge(doc.status)}
                      <span className="text-xs font-mono text-slate-400 bg-navy-900 px-2 py-0.5 rounded border border-navy-800">
                        v{doc.current_version}
                      </span>
                      <h3
                        onClick={() => onOpenDocument(doc.id)}
                        className="text-sm font-bold text-white hover:text-teal-400 cursor-pointer transition-colors"
                      >
                        {doc.title}
                      </h3>
                    </div>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                      <span>
                        Author: <strong className="text-slate-300">{doc.creator_name}</strong>
                      </span>
                      <span>•</span>
                      <span>
                        Channel: <span className="uppercase font-mono text-slate-300">{doc.channel || 'Website'}</span>
                      </span>
                      <span>•</span>
                      <span>
                        Last updated: {new Date(doc.updated_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </span>
                      {doc.assigned_reviewer_name ? (
                        <>
                          <span>•</span>
                          <span className="text-teal-400 flex items-center space-x-1">
                            <UserCheck className="w-3 h-3" />
                            <span>Assigned: {doc.assigned_reviewer_name}</span>
                          </span>
                        </>
                      ) : (
                        <>
                          <span>•</span>
                          <span className="text-amber-400 flex items-center space-x-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Unassigned</span>
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Score & Findings summary */}
                  <div className="flex items-center space-x-4 self-stretch md:self-auto justify-between md:justify-end">
                    {score !== null ? (
                      <div className="text-right">
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">Compliance</div>
                        <div
                          className={`text-sm font-black font-mono ${
                            score >= 90
                              ? 'text-emerald-400'
                              : score >= 70
                              ? 'text-amber-400'
                              : 'text-rose-400'
                          }`}
                        >
                          {score}/100
                        </div>
                        <div className="text-[10px] text-slate-400">
                          {findingsCount} finding{findingsCount !== 1 ? 's' : ''} ({criticalCount} critical)
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500 italic">Not checked</div>
                    )}

                    {/* Assign Action */}
                    {assigningDocId === doc.id ? (
                      <div className="flex items-center space-x-1.5 bg-navy-900 p-1.5 rounded-xl border border-navy-700">
                        <select
                          value={selectedReviewerId}
                          onChange={(e) => setSelectedReviewerId(e.target.value)}
                          className="bg-navy-950 text-xs text-slate-200 border border-navy-700 rounded-lg px-2 py-1 focus:outline-none"
                        >
                          <option value="">Select reviewer...</option>
                          {teamMembers.map((m) => (
                            <option key={m.id} value={m.id}>
                              {m.full_name} ({m.role})
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleAssignReviewer(doc.id)}
                          className="px-2.5 py-1 bg-teal-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-teal-400"
                        >
                          Assign
                        </button>
                        <button
                          onClick={() => setAssigningDocId(null)}
                          className="px-2 py-1 text-slate-400 hover:text-white text-xs"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setAssigningDocId(doc.id);
                          setSelectedReviewerId(doc.assigned_reviewer_id || '');
                        }}
                        className="p-2 text-slate-400 hover:text-slate-200 hover:bg-navy-900 rounded-xl transition-colors border border-transparent hover:border-navy-800"
                        title="Assign Reviewer"
                      >
                        <UserCheck className="w-4 h-4" />
                      </button>
                    )}

                    {/* Open in Studio button */}
                    <button
                      onClick={() => onOpenDocument(doc.id)}
                      className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md"
                    >
                      <span>Open Studio</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
