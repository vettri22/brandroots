import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { GuidelineInsight, ProposedClarification } from '../types';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import {
  BugPlay,
  RotateCw,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowRight,
  BookOpen,
  Sparkles,
  ShieldCheck,
  Edit,
  Award,
  Layers,
  Clock
} from 'lucide-react';

export const GuidelineDebuggerPage: React.FC = () => {
  const { user, role } = useAuth();
  const [insights, setInsights] = useState<GuidelineInsight[]>([]);
  const [clarifications, setClarifications] = useState<ProposedClarification[]>([]);
  const [loading, setLoading] = useState(true);
  const [clustering, setClustering] = useState(false);

  // Proposal Edit State
  const [editingProposalId, setEditingProposalId] = useState<string | null>(null);
  const [editedText, setEditedText] = useState('');
  const [decisionNotes, setDecisionNotes] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    loadDebuggerData();
  }, []);

  const loadDebuggerData = async () => {
    try {
      setLoading(true);
      const [ins, props] = await Promise.all([
        api.getDebuggerInsights(),
        api.getProposedClarifications(),
      ]);
      setInsights(ins);
      setClarifications(props);
    } catch (e) {
      console.error('Failed to load debugger data', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunClustering = async () => {
    setClustering(true);
    setActionSuccess(null);
    setActionError(null);
    try {
      const ins = await api.clusterDebugger();
      setInsights(ins);
      const props = await api.getProposedClarifications();
      setClarifications(props);
      setActionSuccess(`Clustering complete: Analyzed historical reviews and clustered ${ins.length} recurring error pattern(s).`);
    } catch (err: any) {
      setActionError(err.message || 'Clustering failed');
    } finally {
      setClustering(false);
    }
  };

  const handleEvaluateHypothesis = async (insightId: string, action: 'confirm' | 'dismiss') => {
    try {
      const updated = await api.evaluateHypothesis(insightId, action, `Evaluated by ${user?.full_name} (${role})`);
      setInsights(insights.map((ins) => (ins.id === insightId ? updated : ins)));
      setActionSuccess(`Hypothesis for insight #${insightId} was marked as '${updated.hypothesis_status}'.`);
    } catch (err: any) {
      setActionError(err.message || 'Failed to update hypothesis');
    }
  };

  const handleDecideClarification = async (proposalId: string, decision: 'approve' | 'reject') => {
    setActionSuccess(null);
    setActionError(null);
    try {
      const res = await api.decideClarification(
        proposalId,
        decision,
        editingProposalId === proposalId ? editedText : undefined,
        decisionNotes || `Decided by ${user?.full_name}`
      );

      setActionSuccess(res.message);
      setEditingProposalId(null);
      setDecisionNotes('');
      // Reload debugger & guidelines
      await loadDebuggerData();
    } catch (err: any) {
      setActionError(err.message || 'Approval failed. Only Brand Owner is authorized.');
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-teal-400">
          <div className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Clustering review history & evaluating ambiguity...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Signature Feature Banner */}
      <div className="bg-gradient-to-r from-navy-950 via-navy-900 to-teal-950/40 p-6 rounded-2xl border border-teal-500/40 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5 mb-1">
            <span className="p-2 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400">
              <BugPlay className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-bold text-white tracking-tight">Guideline Debugger</h1>
            <Badge variant="teal">Signature Feature</Badge>
          </div>
          <p className="text-xs text-slate-300 max-w-3xl leading-relaxed mt-2">
            A normal checker flags a mistake. <strong>BrandRoots investigates whether repeated mistakes are caused by unclear, contradictory, missing, or outdated brand guidelines.</strong>
            Review history is clustered to detect root causes, surface evidence, propose clarifications as drafts, and require explicit Brand Owner approval.
          </p>
        </div>

        <button
          onClick={handleRunClustering}
          disabled={clustering}
          className="flex items-center space-x-2 px-4 py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-950 rounded-xl text-xs font-bold shadow-lg shadow-teal-500/20 transition-all shrink-0"
        >
          <RotateCw className={`w-4 h-4 ${clustering ? 'animate-spin' : ''}`} />
          <span>{clustering ? 'Clustering Drafts...' : 'Re-Run Clustering Engine'}</span>
        </button>
      </div>

      {/* Notifications */}
      {actionSuccess && (
        <div className="p-4 bg-emerald-950/70 border border-emerald-800 rounded-xl text-xs text-emerald-200 flex items-center justify-between shadow-md">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{actionSuccess}</span>
          </div>
          <button onClick={() => setActionSuccess(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {actionError && (
        <div className="p-4 bg-rose-950/70 border border-rose-800 rounded-xl text-xs text-rose-200 flex items-center justify-between shadow-md">
          <div className="flex items-center space-x-2">
            <XCircle className="w-4 h-4 text-rose-400" />
            <span>{actionError}</span>
          </div>
          <button onClick={() => setActionError(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Insights List */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-bold text-white tracking-tight">Active Guideline Ambiguity Signals</h2>
            <span className="text-xs text-slate-500 font-mono">({insights.length} clusters found)</span>
          </div>
          <div className="text-xs text-slate-400">
            Current Persona: <strong className="text-teal-400 capitalize">{role.replace('_', ' ')}</strong>
          </div>
        </div>

        {insights.map((insight) => {
          // Find matching proposal
          const prop = clarifications.find((c) => c.insight_id === insight.id);

          return (
            <div
              key={insight.id}
              className="bg-navy-950 rounded-2xl border border-navy-800 p-6 shadow-md space-y-6 hover:border-teal-500/40 transition-all"
            >
              {/* Insight Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-navy-850">
                <div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={insight.pattern_type === 'vague_guideline' ? 'critical' : 'warning'}>
                      {insight.pattern_type.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <span className="font-mono text-xs font-bold text-teal-300 bg-navy-900 px-2 py-0.5 rounded border border-navy-800">
                      Rule: {insight.rule_id || 'Cross-cutting'}
                    </span>
                    <span className="text-xs font-mono text-slate-500">#{insight.id}</span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-1.5">{insight.title}</h3>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-400">Observed:</span>
                  <span className="font-mono font-bold text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded-lg border border-amber-800/60 text-xs">
                    {insight.occurrence_count} recurring violations
                  </span>
                </div>
              </div>

              {/* Suspected Root Cause & Evidence */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Root Cause Analysis */}
                <div className="bg-navy-900/60 p-4 rounded-xl border border-navy-800 space-y-2">
                  <div className="text-xs font-bold text-teal-400 flex items-center space-x-1.5">
                    <Sparkles className="w-4 h-4 text-teal-400" />
                    <span>Suspected Root Cause:</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed">
                    {insight.suspected_root_cause}
                  </p>
                  <div className="pt-2 text-[11px] text-slate-400">
                    <strong>Suggested Action:</strong> {insight.suggested_action}
                  </div>
                </div>

                {/* Evidence Panel */}
                <div className="bg-navy-900/60 p-4 rounded-xl border border-navy-800 space-y-2">
                  <div className="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-teal-400" />
                    <span>Supporting Evidence from Stored Reviews:</span>
                  </div>
                  <p className="text-xs text-slate-300 font-mono bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                    {insight.evidence_summary}
                  </p>
                  <div className="text-[10px] text-slate-500 flex items-center space-x-2">
                    <span>Evidence Finding IDs:</span>
                    <span className="font-mono text-slate-400">{insight.supporting_finding_ids.slice(0, 4).join(', ')}...</span>
                  </div>
                </div>
              </div>

              {/* Hypothesis Evaluation Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-navy-900/40 rounded-xl border border-navy-800 text-xs">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-400 font-medium">Hypothesis Status:</span>
                  <Badge variant={insight.hypothesis_status === 'confirmed' ? 'teal' : insight.hypothesis_status === 'dismissed' ? 'neutral' : 'warning'}>
                    {insight.hypothesis_status.toUpperCase()}
                  </Badge>
                  {insight.reviewed_by && (
                    <span className="text-slate-400 text-[11px]">
                      (Evaluated by {insight.reviewed_by})
                    </span>
                  )}
                </div>

                {insight.hypothesis_status === 'hypothesis' && (
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400">Does evidence confirm ambiguity?</span>
                    <button
                      onClick={() => handleEvaluateHypothesis(insight.id, 'confirm')}
                      className="px-2.5 py-1 bg-teal-500/20 hover:bg-teal-500 hover:text-slate-950 text-teal-300 border border-teal-500/40 rounded-lg font-semibold transition-colors"
                    >
                      Confirm Hypothesis
                    </button>
                    <button
                      onClick={() => handleEvaluateHypothesis(insight.id, 'dismiss')}
                      className="px-2.5 py-1 bg-navy-800 hover:bg-navy-700 text-slate-400 hover:text-white rounded-lg transition-colors"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>

              {/* Proposed Guideline Clarification Draft Card */}
              {prop && (
                <div className="bg-gradient-to-br from-navy-900 via-navy-900 to-teal-950/30 p-5 rounded-xl border border-teal-800/40 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <BookOpen className="w-4 h-4 text-teal-400" />
                      <span className="text-xs font-bold text-white uppercase tracking-wider">
                        Proposed Guideline Clarification Draft
                      </span>
                      <Badge variant="teal">v{prop.current_rule_version} → v{prop.proposed_version}</Badge>
                      <Badge variant={prop.approval_status === 'approved' ? 'success' : prop.approval_status === 'rejected' ? 'critical' : 'warning'}>
                        {prop.approval_status.toUpperCase()}
                      </Badge>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      Generated by: {prop.proposing_actor}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 italic">
                    "{prop.clarification_summary}"
                  </p>

                  {/* Before / After Diff */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                    {/* Before (Original) */}
                    <div className="bg-navy-950 p-3 rounded-lg border border-navy-800">
                      <div className="text-[11px] font-sans font-semibold text-slate-400 mb-1 flex items-center justify-between">
                        <span>Original Rule (v{prop.current_rule_version})</span>
                        <span className="text-rose-400">Ambiguous</span>
                      </div>
                      <div className="text-slate-300 leading-relaxed">
                        {prop.original_rule_text}
                      </div>
                    </div>

                    {/* After (Proposed) */}
                    <div className="bg-teal-950/20 p-3 rounded-lg border border-teal-700/50">
                      <div className="text-[11px] font-sans font-semibold text-teal-300 mb-1 flex items-center justify-between">
                        <span>Proposed Clarification (v{prop.proposed_version})</span>
                        <span className="text-teal-400 font-bold">Explicit Boundary Added</span>
                      </div>
                      {editingProposalId === prop.id ? (
                        <textarea
                          rows={4}
                          value={editedText}
                          onChange={(e) => setEditedText(e.target.value)}
                          className="w-full bg-navy-950 border border-teal-500 rounded p-2 text-xs font-mono text-teal-200 focus:outline-none"
                        />
                      ) : (
                        <div className="text-teal-200 leading-relaxed font-sans">
                          {prop.proposed_rule_text}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Brand Owner Approval Control */}
                  {prop.approval_status === 'pending' && (
                    <div className="pt-3 border-t border-navy-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="text-xs text-slate-400 flex items-center space-x-1.5">
                        <Award className="w-4 h-4 text-teal-400" />
                        <span>
                          {role === 'brand_owner' ? (
                            <strong className="text-teal-300">You are authorized as Brand Owner to approve this guideline version.</strong>
                          ) : (
                            <span>Approval requires <strong>Brand Owner</strong> role (Switch in top bar).</span>
                          )}
                        </span>
                      </div>

                      {role === 'brand_owner' ? (
                        <div className="flex items-center space-x-2">
                          {editingProposalId !== prop.id ? (
                            <button
                              onClick={() => {
                                setEditingProposalId(prop.id);
                                setEditedText(prop.proposed_rule_text);
                              }}
                              className="px-3 py-1.5 bg-navy-800 hover:bg-navy-700 text-slate-300 rounded-lg text-xs transition-colors"
                            >
                              Edit Text Before Approval
                            </button>
                          ) : (
                            <button
                              onClick={() => setEditingProposalId(null)}
                              className="px-2 py-1.5 text-xs text-slate-400 hover:text-white"
                            >
                              Cancel Edit
                            </button>
                          )}
                          <button
                            onClick={() => handleDecideClarification(prop.id, 'reject')}
                            className="px-3 py-1.5 bg-navy-800 hover:bg-rose-950 hover:text-rose-300 text-slate-400 rounded-lg text-xs font-semibold transition-colors"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleDecideClarification(prop.id, 'approve')}
                            className="px-4 py-1.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all flex items-center space-x-1.5"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve & Publish Guideline (v{prop.proposed_version})</span>
                          </button>
                        </div>
                      ) : (
                        <div className="text-xs text-slate-500 italic">
                          Read-only for {role}. Switch to Brand Owner in header to publish.
                        </div>
                      )}
                    </div>
                  )}

                  {/* Already Approved Notice */}
                  {prop.approval_status === 'approved' && (
                    <div className="pt-2 text-xs text-emerald-400 flex items-center space-x-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>
                        Approved by {prop.reviewed_by} on {new Date(prop.reviewed_at || prop.created_at).toLocaleDateString()}.
                        Active guideline incremented to <strong>v{prop.proposed_version}</strong>. Historical reviews retain v{prop.current_rule_version}.
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
