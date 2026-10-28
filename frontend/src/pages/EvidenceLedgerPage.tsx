import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { BrandEvidence, UserRole } from '../types';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Plus,
  Search,
  Filter,
  AlertTriangle,
  Clock,
  FileText,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Archive,
  RefreshCw,
  Sparkles,
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { Badge } from '../components/Badge';

export const EvidenceLedgerPage: React.FC = () => {
  const { user, role, activeBrand } = useAuth();
  const [evidenceList, setEvidenceList] = useState<BrandEvidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  
  // Conflicting and expiring state
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [expiringSoon, setExpiringSoon] = useState<any[]>([]);
  
  // Interactive Verification Sandbox
  const [claimText, setClaimText] = useState('');
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [verifying, setVerifying] = useState(false);

  // Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newWording, setNewWording] = useState('');
  const [newStructuredValue, setNewStructuredValue] = useState('');
  const [newCategory, setNewCategory] = useState('pricing');
  const [newSourceLocation, setNewSourceLocation] = useState('');
  const [newPageSection, setNewPageSection] = useState('');
  const [newExpiryDate, setNewExpiryDate] = useState('');
  const [newProhibitedOld, setNewProhibitedOld] = useState('');
  const [newPublicUse, setNewPublicUse] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchEvidence = async () => {
    setLoading(true);
    try {
      const records = await api.listEvidence({
        brand_id: activeBrand?.id,
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
        status_filter: statusFilter !== 'all' ? statusFilter : undefined,
        search: search.trim() ? search.trim() : undefined,
      });
      setEvidenceList(records);

      const conflictData = await api.getEvidenceConflicts(activeBrand?.id).catch(() => ({ conflicts: [] }));
      setConflicts(conflictData.conflicts || []);

      const expiringData = await api.getExpiringEvidence(45).catch(() => ({ expiring_soon_records: [] }));
      setExpiringSoon(expiringData.expiring_soon_records || []);
    } catch (err) {
      console.error('Failed to load evidence', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [activeBrand, statusFilter, categoryFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvidence();
  };

  const handleVerifyClaim = async () => {
    if (!claimText.trim()) return;
    setVerifying(true);
    try {
      const res = await api.verifyClaim(claimText, activeBrand?.id);
      setVerificationResult(res);
    } catch (err) {
      console.error('Claim verification failed', err);
    } finally {
      setVerifying(false);
    }
  };

  const handleCreateEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newWording.trim()) return;
    setSaving(true);
    try {
      const prohibitedList = newProhibitedOld
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      await api.createEvidence({
        brand_id: activeBrand?.id,
        claim_title: newTitle,
        approved_wording: newWording,
        structured_value: newStructuredValue || undefined,
        category: newCategory,
        source_location: newSourceLocation || 'Internal Compliance Spec',
        page_or_section: newPageSection || 'Section 1',
        expiry_date: newExpiryDate || undefined,
        prohibited_old_values: prohibitedList,
        public_use_permission: newPublicUse,
        evidence_owner: user?.full_name || 'Brand Owner',
        status: 'approved',
      });
      setShowCreateModal(false);
      // Reset form
      setNewTitle('');
      setNewWording('');
      setNewStructuredValue('');
      setNewSourceLocation('');
      setNewPageSection('');
      setNewExpiryDate('');
      setNewProhibitedOld('');
      fetchEvidence();
    } catch (err: any) {
      alert(err.message || 'Failed to create evidence');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (evidenceId: string, newStatus: string) => {
    try {
      await api.changeEvidenceStatus(evidenceId, newStatus);
      fetchEvidence();
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Brand Evidence Ledger</h1>
              <p className="text-sm text-slate-400">
                Traceable, expiry-aware repository of approved claims, structured facts, sources, and public-use permissions.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => fetchEvidence()}
            className="p-2 text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-lg transition-colors"
            title="Refresh Ledger"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold rounded-xl text-sm transition-all shadow-lg shadow-cyan-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>Add Evidence Record</span>
          </button>
        </div>
      </div>

      {/* Warning Banners */}
      {conflicts.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/80 text-amber-200 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-sm">
            <span className="font-semibold text-amber-300">
              {conflicts.length} Conflicting Evidence Record(s) Detected
            </span>
            <p className="text-amber-200/90 text-xs">
              Multiple approved records contain overlapping or mutually contradictory values. Resolve these discrepancies to prevent conflicting preflight findings.
            </p>
            <ul className="text-xs list-disc list-inside space-y-1 mt-2 text-amber-300/80">
              {conflicts.map((c, i) => (
                <li key={i}>{c.reason}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {expiringSoon.length > 0 && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/80 text-rose-200 flex items-start space-x-3">
          <Clock className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-sm">
            <span className="font-semibold text-rose-300">
              {expiringSoon.length} Evidence Record(s) Expiring Soon
            </span>
            <p className="text-rose-200/90 text-xs">
              Evidence nearing review dates must be verified with current audit documents before expiration invalidates dependent drafts.
            </p>
          </div>
        </div>
      )}

      {/* Interactive Claim Verification Sandbox */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur space-y-4">
        <div className="flex items-center space-x-2 text-sm font-semibold text-cyan-400">
          <Sparkles className="w-4 h-4" />
          <span>Interactive Claim Substantiation Sandbox</span>
        </div>
        <p className="text-xs text-slate-400">
          Test any marketing claim, pricing statement, or clinical promise in real time against the authorized Brand Evidence Ledger.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={claimText}
            onChange={(e) => setClaimText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleVerifyClaim()}
            placeholder="e.g. 'NovusBio Pro plan is $29/mo with guaranteed triage results...'"
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleVerifyClaim}
            disabled={verifying || !claimText.trim()}
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white font-medium text-sm rounded-xl transition-colors"
          >
            {verifying ? 'Verifying...' : 'Substantiate Claim'}
          </button>
        </div>

        {verificationResult && (
          <div
            className={`p-4 rounded-xl border mt-3 text-sm ${
              verificationResult.status === 'supported'
                ? 'bg-emerald-950/40 border-emerald-800/80 text-emerald-200'
                : verificationResult.status === 'contradicted'
                ? 'bg-rose-950/40 border-rose-800/80 text-rose-200'
                : verificationResult.status === 'expired'
                ? 'bg-amber-950/40 border-amber-800/80 text-amber-200'
                : 'bg-slate-950 border-slate-800 text-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold uppercase tracking-wider text-xs">
                Status: {verificationResult.status.replace('_', ' ')}
              </span>
              <span className="text-xs text-slate-400">
                Confidence: {verificationResult.confidence}
              </span>
            </div>
            <p className="text-xs mb-2">{verificationResult.explanation}</p>
            {verificationResult.matched_evidence_id && (
              <div className="text-xs opacity-90 flex items-center space-x-1.5 font-mono">
                <span>Citation:</span>
                <span className="underline">{verificationResult.matched_evidence_id}</span>
                <span>({verificationResult.source_reference})</span>
              </div>
            )}
            {verificationResult.suggested_correction && (
              <div className="mt-2 text-xs font-medium">
                Suggested Replacement: <span className="underline">{verificationResult.suggested_correction}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search claims, wording, or sources..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs px-3 py-2 rounded-xl focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Statuses</option>
            <option value="approved">Approved</option>
            <option value="pending_review">Pending Review</option>
            <option value="draft">Draft</option>
            <option value="expired">Expired</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-300 text-xs px-3 py-2 rounded-xl focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Categories</option>
            <option value="pricing">Pricing</option>
            <option value="clinical">Clinical Efficacy</option>
            <option value="security">Security & SLA</option>
            <option value="legal">Legal & Compliance</option>
          </select>
        </div>
      </div>

      {/* Evidence Table */}
      {loading ? (
        <div className="py-20 text-center text-slate-500 text-sm">Loading Brand Evidence Ledger...</div>
      ) : evidenceList.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
          <HelpCircle className="w-8 h-8 text-slate-600 mx-auto" />
          <div className="font-semibold text-slate-300">No Evidence Records Found</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            No authorized evidence records match the current filter. Add canonical claims or facts to empower automated preflight verification.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {evidenceList.map((ev) => (
            <div
              key={ev.id}
              className={`p-5 rounded-2xl bg-slate-900/70 border transition-all flex flex-col justify-between space-y-4 ${
                ev.is_expired || ev.status === 'expired'
                  ? 'border-rose-900/60 bg-rose-950/10'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-[11px] text-cyan-400 font-bold">{ev.id}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      v{ev.version}
                    </span>
                    {ev.is_expired && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                        EXPIRED
                      </span>
                    )}
                  </div>
                  <Badge variant={ev.status === 'approved' ? 'teal' : ev.status === 'expired' ? 'critical' : 'warning'}>
                    {ev.status.replace('_', ' ')}
                  </Badge>
                </div>

                <h3 className="font-semibold text-slate-100 text-base">{ev.claim_title}</h3>
                <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed font-sans">
                  "{ev.approved_wording}"
                </p>

                {ev.structured_value && (
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="text-slate-400">Canonical Value:</span>
                    <span className="font-mono font-semibold text-cyan-300 bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-800/60">
                      {ev.structured_value}
                    </span>
                  </div>
                )}

                {ev.prohibited_old_values && ev.prohibited_old_values.length > 0 && (
                  <div className="flex items-center space-x-1.5 text-[11px] text-rose-400">
                    <span className="text-slate-500">Superseded figures:</span>
                    <span className="line-through">{ev.prohibited_old_values.join(', ')}</span>
                  </div>
                )}
              </div>

              {/* Provenance & Ownership Metadata */}
              <div className="pt-3 border-t border-slate-800/80 text-xs space-y-1.5">
                <div className="flex items-center justify-between text-slate-400">
                  <div className="flex items-center space-x-1.5 truncate max-w-[240px]">
                    <FileText className="w-3.5 h-3.5 shrink-0 text-slate-500" />
                    <span className="truncate">{ev.source_location || 'Internal File'}</span>
                  </div>
                  <span>{ev.page_or_section || 'Section 1'}</span>
                </div>

                <div className="flex items-center justify-between text-slate-500 text-[11px]">
                  <span>Owner: {ev.evidence_owner}</span>
                  <span>Expires: {ev.expiry_date || 'No Expiration'}</span>
                </div>

                {/* Status Switcher for Reviewers / Owners */}
                {(role === 'brand_owner' || role === 'reviewer' || role === 'brand_admin') && (
                  <div className="flex items-center justify-end space-x-2 pt-2">
                    {ev.status !== 'approved' && (
                      <button
                        onClick={() => handleStatusChange(ev.id, 'approved')}
                        className="text-[11px] text-emerald-400 hover:text-emerald-300 bg-emerald-950/40 border border-emerald-800/60 px-2.5 py-1 rounded-lg"
                      >
                        Approve
                      </button>
                    )}
                    {ev.status === 'approved' && (
                      <button
                        onClick={() => handleStatusChange(ev.id, 'expired')}
                        className="text-[11px] text-amber-400 hover:text-amber-300 bg-amber-950/40 border border-amber-800/60 px-2.5 py-1 rounded-lg"
                      >
                        Mark Expired
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Evidence Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white">Add New Evidence Record</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-500 hover:text-slate-300 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateEvidence} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Claim Title *</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. NovusBio Enterprise SLA Latency"
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Approved Wording *</label>
                <textarea
                  required
                  rows={3}
                  value={newWording}
                  onChange={(e) => setNewWording(e.target.value)}
                  placeholder="Exact phrasing authorized for public or commercial citation..."
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Structured Value</label>
                  <input
                    type="text"
                    value={newStructuredValue}
                    onChange={(e) => setNewStructuredValue(e.target.value)}
                    placeholder="e.g. $49/mo or 99.9% SLA"
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="pricing">Pricing</option>
                    <option value="clinical">Clinical Efficacy</option>
                    <option value="security">Security & Certification</option>
                    <option value="legal">Legal & Compliance</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Source Document</label>
                  <input
                    type="text"
                    value={newSourceLocation}
                    onChange={(e) => setNewSourceLocation(e.target.value)}
                    placeholder="e.g. Commercial Schedule Q4-2026.pdf"
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Page / Section Ref</label>
                  <input
                    type="text"
                    value={newPageSection}
                    onChange={(e) => setNewPageSection(e.target.value)}
                    placeholder="e.g. Section 4.1 or Page 12"
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Expiry Date (YYYY-MM-DD)</label>
                  <input
                    type="date"
                    value={newExpiryDate}
                    onChange={(e) => setNewExpiryDate(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Prohibited Old Values</label>
                  <input
                    type="text"
                    value={newProhibitedOld}
                    onChange={(e) => setNewProhibitedOld(e.target.value)}
                    placeholder="e.g. $29/mo, $39/mo (comma-separated)"
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="publicUseCheck"
                  checked={newPublicUse}
                  onChange={(e) => setNewPublicUse(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-cyan-500 focus:ring-0"
                />
                <label htmlFor="publicUseCheck" className="text-xs text-slate-300 cursor-pointer">
                  Authorized for public marketing and commercial distribution
                </label>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition-colors"
                >
                  {saving ? 'Saving...' : 'Authorize Evidence'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
