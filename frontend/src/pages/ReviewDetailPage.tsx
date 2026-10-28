import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ContentDocument, ReviewJob, Finding, ReviewComment, DocumentVersion, ApprovalRecord } from '../types';
import { FindingCard } from '../components/FindingCard';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Send,
  MessageSquare,
  History,
  ShieldCheck,
  Edit,
  Save,
  Clock,
  Sparkles,
  GitCompare,
  FileCheck2,
  Lock,
  CornerDownRight,
} from 'lucide-react';

interface ReviewDetailPageProps {
  documentId: string;
  onBack: () => void;
}

export const ReviewDetailPage: React.FC<ReviewDetailPageProps> = ({ documentId, onBack }) => {
  const { user, role } = useAuth();
  const [doc, setDoc] = useState<ContentDocument | null>(null);
  const [job, setJob] = useState<ReviewJob | null>(null);
  const [comments, setComments] = useState<ReviewComment[]>([]);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [rechecking, setRechecking] = useState(false);

  // Draft Editor State
  const [isEditingDraft, setIsEditingDraft] = useState(false);
  const [editText, setEditText] = useState('');
  const [changelogNote, setChangelogNote] = useState('');

  // Comment Modal / Action
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [pendingTransition, setPendingTransition] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');

  // Inline Comment Box
  const [newCommentInput, setNewCommentInput] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  // Version Diff Modal
  const [showDiffModal, setShowDiffModal] = useState(false);
  const [diffV1, setDiffV1] = useState<number>(1);
  const [diffV2, setDiffV2] = useState<number>(1);
  const [diffData, setDiffData] = useState<any>(null);
  const [loadingDiff, setLoadingDiff] = useState(false);

  // Tab
  const [activeTab, setActiveTab] = useState<'findings' | 'comments' | 'versions'>('findings');

  useEffect(() => {
    loadDocumentData();
  }, [documentId]);

  const loadDocumentData = async () => {
    try {
      setLoading(true);
      const [d, jobs, coms, vers, apps] = await Promise.all([
        api.getDocument(documentId),
        api.getDocumentReviews(documentId),
        api.getComments(documentId),
        api.getDocumentVersions(documentId),
        api.getDocumentApprovals(documentId).catch(() => []),
      ]);
      setDoc(d);
      setEditText(d.current_text);
      setComments(coms);
      setVersions(vers);
      setApprovals(apps);
      if (jobs.length > 0) {
        setJob(jobs[0]); // latest job
      } else {
        const newJob = await api.triggerReview(documentId);
        setJob(newJob);
      }
      if (vers.length >= 2) {
        setDiffV1(vers[vers.length - 2].version_number);
        setDiffV2(vers[vers.length - 1].version_number);
      } else if (vers.length === 1) {
        setDiffV1(vers[0].version_number);
        setDiffV2(vers[0].version_number);
      }
    } catch (e) {
      console.error('Failed to load review details', e);
    } finally {
      setLoading(false);
    }
  };

  const handleManualRecheck = async () => {
    setRechecking(true);
    try {
      const newJob = await api.triggerReview(documentId);
      setJob(newJob);
      const d = await api.getDocument(documentId);
      setDoc(d);
    } catch (err: any) {
      alert(err.message || 'Re-check failed');
    } finally {
      setRechecking(false);
    }
  };

  const handleSaveDraftEdits = async () => {
    if (!doc) return;
    try {
      const updated = await api.updateDocument(doc.id, editText, changelogNote || 'Manual editorial revision');
      setDoc(updated);
      setIsEditingDraft(false);
      setChangelogNote('');
      const newJob = await api.triggerReview(doc.id);
      setJob(newJob);
      const vers = await api.getDocumentVersions(doc.id);
      setVersions(vers);
    } catch (err: any) {
      alert(err.message || 'Failed to update draft');
    }
  };

  const handleResolveFinding = async (
    findingId: string,
    status: 'accepted' | 'edited' | 'dismissed' | 'escalated',
    notes?: string,
    customText?: string,
    reason?: string
  ) => {
    try {
      await api.resolveFinding(findingId, status, notes, customText, reason);
      const [d, jobs, vers] = await Promise.all([
        api.getDocument(documentId),
        api.getDocumentReviews(documentId),
        api.getDocumentVersions(documentId),
      ]);
      setDoc(d);
      setEditText(d.current_text);
      setVersions(vers);
      if (jobs.length > 0) setJob(jobs[0]);
    } catch (err: any) {
      alert(err.message || 'Failed to resolve finding');
    }
  };

  const handleOpenTransitionModal = (targetStatus: string) => {
    setPendingTransition(targetStatus);
    setActionError('');
    setShowCommentModal(true);
  };

  const handleExecuteTransition = async () => {
    if (!pendingTransition || !doc) return;
    setActionError('');
    try {
      await api.transitionStatus(doc.id, pendingTransition, commentText);
      setShowCommentModal(false);
      setCommentText('');
      setPendingTransition(null);
      const [d, coms, apps] = await Promise.all([
        api.getDocument(documentId),
        api.getComments(documentId),
        api.getDocumentApprovals(documentId).catch(() => []),
      ]);
      setDoc(d);
      setComments(coms);
      setApprovals(apps);
    } catch (err: any) {
      setActionError(err.message || 'Action denied by governance policy');
    }
  };

  const handleAddInlineComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCommentInput.trim() || !doc) return;
    setSubmittingComment(true);
    try {
      const added = await api.addComment(doc.id, newCommentInput.trim(), 'comment');
      setComments([...comments, added]);
      setNewCommentInput('');
    } catch (err: any) {
      alert(err.message || 'Failed to post comment');
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleFetchDiff = async () => {
    if (!doc) return;
    setLoadingDiff(true);
    try {
      const res = await api.getVersionDiff(doc.id, diffV1, diffV2);
      setDiffData(res);
      setShowDiffModal(true);
    } catch (err: any) {
      alert(err.message || 'Failed to generate version diff');
    } finally {
      setLoadingDiff(false);
    }
  };

  if (loading || !doc) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-teal-400">
          <div className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Loading Correction Studio...</span>
        </div>
      </div>
    );
  }

  const score = job?.compliance_score ?? 100;
  const scoreColor =
    score >= 90 ? 'text-emerald-400 border-emerald-800 bg-emerald-950/40' :
    score >= 70 ? 'text-amber-400 border-amber-800 bg-amber-950/40' :
    'text-rose-400 border-rose-800 bg-rose-950/40';

  const isApproved = doc.status === 'approved' && doc.approved_version !== null;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Version-Bound Approval Alert Banner */}
      {isApproved ? (
        <div className="p-4 bg-emerald-950/70 border border-emerald-500/50 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
            <div>
              <div className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Version-Bound Approval Active</span>
                <span className="bg-emerald-900/60 text-emerald-300 font-mono text-xs px-2 py-0.5 rounded border border-emerald-700">
                  v{doc.approved_version}
                </span>
              </div>
              <div className="text-xs text-emerald-300/90 mt-0.5">
                Approved by <strong>{doc.approved_by_name || 'Authorized Reviewer'}</strong> on{' '}
                {doc.approved_at ? new Date(doc.approved_at).toLocaleString() : 'Recent'}.
              </div>
            </div>
          </div>
          <div className="text-[11px] text-emerald-400/80 bg-emerald-900/40 px-3 py-1.5 rounded-xl border border-emerald-800">
            Editing will immediately invalidate this sign-off.
          </div>
        </div>
      ) : doc.status === 'draft' && doc.current_version > 1 ? (
        <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl flex items-center space-x-2 text-xs text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            Working draft at <strong>v{doc.current_version}</strong>. Previous versions are preserved permanently in version history.
          </span>
        </div>
      ) : null}

      {/* Top Header Bar */}
      <div className="bg-navy-950 p-4 rounded-2xl border border-navy-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-navy-900 hover:bg-navy-800 text-slate-400 hover:text-white border border-navy-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-tight">{doc.title}</h1>
              <Badge variant="teal">v{doc.current_version}</Badge>
              <Badge variant={doc.status === 'approved' ? 'teal' : doc.status === 'in_review' ? 'warning' : 'neutral'}>
                {doc.status.toUpperCase()}
              </Badge>
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Author: <strong className="text-slate-300">{doc.creator_name}</strong> • Channel:{' '}
              <span className="uppercase font-mono text-slate-300">{doc.channel || 'Website'}</span> • Market:{' '}
              <span className="font-mono text-slate-300">{doc.market || 'Global'}</span>
            </div>
          </div>
        </div>

        {/* Right Action Bar */}
        <div className="flex items-center space-x-2.5 flex-wrap gap-y-2">
          {/* Compliance Score Pill */}
          <div className={`px-3 py-1.5 rounded-xl border flex items-center space-x-2 font-mono text-xs font-bold ${scoreColor}`}>
            <span>COMPLIANCE:</span>
            <span className="text-sm">{score}/100</span>
          </div>

          <button
            onClick={handleManualRecheck}
            disabled={rechecking}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-navy-900 hover:bg-navy-800 text-slate-300 rounded-xl text-xs font-medium border border-navy-700 transition-colors"
            title="Re-run compliance engine"
          >
            <RotateCw className={`w-3.5 h-3.5 text-teal-400 ${rechecking ? 'animate-spin' : ''}`} />
            <span>Re-Check</span>
          </button>

          {versions.length >= 2 && (
            <button
              onClick={handleFetchDiff}
              disabled={loadingDiff}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-navy-900 hover:bg-navy-800 text-slate-300 rounded-xl text-xs font-medium border border-navy-700 transition-colors"
            >
              <GitCompare className="w-3.5 h-3.5 text-teal-400" />
              <span>Diff Versions</span>
            </button>
          )}

          {/* Workflow Action Buttons */}
          {doc.status === 'draft' && (
            <button
              onClick={() => handleOpenTransitionModal('submitted')}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Submit for Review</span>
            </button>
          )}

          {doc.status === 'submitted' && (
            <button
              onClick={() => handleOpenTransitionModal('in_review')}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Start Review</span>
            </button>
          )}

          {(doc.status === 'in_review' || doc.status === 'resubmitted') && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleOpenTransitionModal('changes_requested')}
                className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded-xl shadow-md transition-all"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Request Changes</span>
              </button>
              <button
                onClick={() => handleOpenTransitionModal('approved')}
                className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Sign & Approve v{doc.current_version}</span>
              </button>
            </div>
          )}

          {doc.status === 'changes_requested' && (
            <button
              onClick={() => handleOpenTransitionModal('resubmitted')}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Resubmit Revised Draft</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Split Workbench: Document on Left, Findings on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Pane: Document Text (Col 7) */}
        <div className="lg:col-span-7 bg-navy-950 rounded-2xl border border-navy-800 p-6 shadow-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-navy-800 mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-slate-300">Draft Content Canvas</span>
                <span className="text-xs text-slate-500">({doc.current_text.length} chars)</span>
              </div>
              <div>
                {!isEditingDraft ? (
                  <button
                    onClick={() => setIsEditingDraft(true)}
                    className="flex items-center space-x-1 text-xs text-teal-400 hover:text-teal-300 font-semibold"
                  >
                    <Edit className="w-3.5 h-3.5" />
                    <span>Edit Canvas Directly</span>
                  </button>
                ) : (
                  <button
                    onClick={handleSaveDraftEdits}
                    className="flex items-center space-x-1 px-3 py-1 bg-teal-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-teal-400"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Save Revision</span>
                  </button>
                )}
              </div>
            </div>

            {isEditingDraft ? (
              <div className="space-y-3">
                {isApproved && (
                  <div className="p-2.5 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300 flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>Warning: Saving changes to this approved draft will revoke approval and create version v{doc.current_version + 1}.</span>
                  </div>
                )}
                <textarea
                  rows={14}
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-700 rounded-xl p-4 text-xs font-mono text-slate-200 leading-relaxed focus:outline-none focus:border-teal-400"
                />
                <input
                  type="text"
                  placeholder="Changelog note for this revision..."
                  value={changelogNote}
                  onChange={(e) => setChangelogNote(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-750 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none"
                />
              </div>
            ) : (
              <div className="bg-navy-900/60 rounded-xl p-5 border border-navy-850 font-mono text-xs leading-relaxed text-slate-200 whitespace-pre-wrap selection:bg-teal-500/30">
                {doc.current_text}
              </div>
            )}
          </div>

          <div className="pt-4 mt-6 border-t border-navy-800 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Historical baseline: Preserved permanently in version ledger.</span>
            <span>Reviewed with snapshot of {Object.keys(job?.guideline_snapshot || {}).length} active guidelines.</span>
          </div>
        </div>

        {/* Right Pane: Correction Studio Tabs (Col 5) */}
        <div className="lg:col-span-5 bg-navy-950 rounded-2xl border border-navy-800 p-6 shadow-md flex flex-col">
          {/* Tabs */}
          <div className="flex items-center space-x-2 border-b border-navy-800 pb-3 mb-4 text-xs">
            <button
              onClick={() => setActiveTab('findings')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeTab === 'findings'
                  ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>Findings</span>
              <span className="font-mono text-[10px] bg-navy-900 px-1.5 py-0.5 rounded text-teal-300">
                {job?.findings?.length ?? 0}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('comments')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeTab === 'comments'
                  ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Review Log</span>
              <span className="font-mono text-[10px] bg-navy-900 px-1.5 py-0.5 rounded text-slate-400">
                {comments.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('versions')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeTab === 'versions'
                  ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Versions</span>
              <span className="font-mono text-[10px] bg-navy-900 px-1.5 py-0.5 rounded text-slate-400">
                {versions.length}
              </span>
            </button>
          </div>

          {/* Tab 1: Findings List */}
          {activeTab === 'findings' && (
            <div className="space-y-4 overflow-y-auto max-h-[600px] pr-1">
              {job?.findings && job.findings.length > 0 ? (
                job.findings.map((finding) => (
                  <FindingCard
                    key={finding.id}
                    finding={finding}
                    onResolve={(status, notes, customText) =>
                      handleResolveFinding(finding.id, status, notes, customText, notes)
                    }
                  />
                ))
              ) : (
                <div className="p-8 text-center bg-navy-900/40 rounded-xl border border-navy-800 text-slate-400">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                  <div className="text-sm font-bold text-white">No Compliance Violations Detected</div>
                  <p className="text-xs text-slate-500 mt-1">This draft complies with all approved brand guidelines, pricing schedules, and required disclaimers.</p>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Comments / Review Actions Log */}
          {activeTab === 'comments' && (
            <div className="flex flex-col h-full justify-between space-y-4">
              <div className="space-y-3 overflow-y-auto max-h-[460px]">
                {comments.map((c) => (
                  <div key={c.id} className="p-3 bg-navy-900/70 rounded-xl border border-navy-800 text-xs">
                    <div className="flex items-center justify-between text-slate-400 mb-1">
                      <div className="flex items-center space-x-1.5">
                        <strong className="text-slate-200">{c.user_name}</strong>
                        <Badge variant="neutral">{c.user_role}</Badge>
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div className="text-slate-300 font-medium">{c.comment_text}</div>
                  </div>
                ))}
                {comments.length === 0 && (
                  <div className="text-xs text-slate-500 py-6 text-center">No comments or decisions logged yet.</div>
                )}
              </div>

              {/* Inline Comment Input */}
              <form onSubmit={handleAddInlineComment} className="pt-3 border-t border-navy-800 flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Post reviewer note or inquiry..."
                  value={newCommentInput}
                  onChange={(e) => setNewCommentInput(e.target.value)}
                  className="flex-1 bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
                />
                <button
                  type="submit"
                  disabled={submittingComment || !newCommentInput.trim()}
                  className="p-2 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 rounded-xl transition-all"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          )}

          {/* Tab 3: Versions Timeline */}
          {activeTab === 'versions' && (
            <div className="space-y-3 overflow-y-auto max-h-[600px]">
              {versions.map((v) => (
                <div key={v.id} className="p-3 bg-navy-900/60 rounded-xl border border-navy-800 text-xs">
                  <div className="flex items-center justify-between font-semibold text-slate-200 mb-1">
                    <span className="flex items-center space-x-1.5">
                      <span>Version v{v.version_number}</span>
                      {doc.approved_version === v.version_number && (
                        <span className="bg-emerald-950 text-emerald-300 border border-emerald-800 text-[9px] px-1.5 py-0.2 rounded font-bold">
                          APPROVED
                        </span>
                      )}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(v.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="text-slate-400 text-[11px] mb-2">{v.changelog || 'Snapshot taken'}</div>
                  <div className="p-2 bg-navy-950 rounded text-[10px] font-mono text-slate-300 max-h-24 overflow-y-auto">
                    {v.text_snapshot.slice(0, 180)}...
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Version Diff Modal */}
      {showDiffModal && diffData && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-4xl p-6 shadow-2xl flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <GitCompare className="w-5 h-5 text-teal-400" />
                <h2 className="text-base font-bold text-white">
                  Version Comparison: v{diffData.v1} → v{diffData.v2}
                </h2>
                <Badge variant="teal">{diffData.total_changes} change hunk(s)</Badge>
              </div>
              <button onClick={() => setShowDiffModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="flex items-center space-x-3 mb-4 text-xs">
              <label className="text-slate-400 font-semibold">Compare:</label>
              <select
                value={diffV1}
                onChange={(e) => setDiffV1(Number(e.target.value))}
                className="bg-navy-900 text-slate-200 border border-navy-700 rounded-lg px-2 py-1"
              >
                {versions.map((v) => (
                  <option key={v.version_number} value={v.version_number}>
                    v{v.version_number} ({v.changelog ? v.changelog.slice(0, 25) : 'Snapshot'})
                  </option>
                ))}
              </select>
              <span className="text-slate-500">with</span>
              <select
                value={diffV2}
                onChange={(e) => setDiffV2(Number(e.target.value))}
                className="bg-navy-900 text-slate-200 border border-navy-700 rounded-lg px-2 py-1"
              >
                {versions.map((v) => (
                  <option key={v.version_number} value={v.version_number}>
                    v{v.version_number} ({v.changelog ? v.changelog.slice(0, 25) : 'Snapshot'})
                  </option>
                ))}
              </select>
              <button
                onClick={handleFetchDiff}
                className="px-3 py-1 bg-teal-500 text-slate-950 font-bold rounded-lg hover:bg-teal-400"
              >
                Update Diff
              </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-navy-900/80 rounded-xl p-4 border border-navy-800 font-mono text-xs leading-relaxed space-y-2">
              {diffData.hunks && diffData.hunks.length > 0 ? (
                diffData.hunks.map((h: any, i: number) => {
                  if (h.type === 'insert') {
                    return (
                      <div key={i} className="bg-emerald-950/40 text-emerald-300 p-2 rounded border border-emerald-800/60">
                        + {h.text}
                      </div>
                    );
                  }
                  if (h.type === 'delete') {
                    return (
                      <div key={i} className="bg-rose-950/40 text-rose-300 p-2 rounded border border-rose-800/60 line-through opacity-80">
                        - {h.text}
                      </div>
                    );
                  }
                  return (
                    <div key={i} className="text-slate-400 p-1">
                      {h.text}
                    </div>
                  );
                })
              ) : (
                <div className="text-center text-slate-400 py-8">
                  Both versions contain identical text.
                </div>
              )}
            </div>

            <div className="flex justify-end pt-4 mt-4 border-t border-navy-800">
              <button
                onClick={() => setShowDiffModal(false)}
                className="px-4 py-2 bg-navy-800 hover:bg-navy-700 text-slate-200 font-semibold text-xs rounded-xl"
              >
                Close Diff
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transition / Decision Modal */}
      {showCommentModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-1">
              Transition to <span className="text-teal-400 capitalize">{pendingTransition?.replace('_', ' ')}</span>
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Add a mandatory review comment or instruction for the audit log.
            </p>

            {actionError && (
              <div className="p-3 mb-4 bg-rose-950/80 border border-rose-800 rounded-lg text-xs text-rose-300">
                {actionError}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Reviewer Note / Decision Reason</label>
                <textarea
                  rows={4}
                  placeholder="e.g. Please replace unsupported guarantees with approved clinical efficacy data..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-teal-400"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowCommentModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleExecuteTransition}
                  className="px-4 py-1.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
                >
                  Confirm Transition
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
