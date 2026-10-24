import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ContentDocument, DocumentStatus } from '../types';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Upload,
  Plus,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  FileCode2
} from 'lucide-react';

interface ReviewWorkbenchPageProps {
  onOpenDocument: (documentId: string) => void;
}

export const ReviewWorkbenchPage: React.FC<ReviewWorkbenchPageProps> = ({ onOpenDocument }) => {
  const { user, role } = useAuth();
  const [documents, setDocuments] = useState<ContentDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [showTextModal, setShowTextModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  // New Draft Form
  const [newTitle, setNewTitle] = useState('');
  const [newText, setNewText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    loadDocuments();
  }, [statusFilter]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await api.listDocuments(statusFilter === 'all' ? undefined : statusFilter);
      setDocuments(docs);
    } catch (e) {
      console.error('Failed to load documents', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTextDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newText.trim()) return;

    setSubmitting(true);
    setErrorMsg('');
    try {
      const doc = await api.createTextDocument(newTitle, newText);
      setShowTextModal(false);
      setNewTitle('');
      setNewText('');
      onOpenDocument(doc.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create draft');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUploadDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !selectedFile) return;

    setSubmitting(true);
    setErrorMsg('');
    try {
      const doc = await api.uploadDocument(newTitle, selectedFile);
      setShowUploadModal(false);
      setNewTitle('');
      setSelectedFile(null);
      onOpenDocument(doc.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Upload failed');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.creator_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusBadge = (status: DocumentStatus) => {
    const map: Record<DocumentStatus, { variant: any; label: string }> = {
      draft: { variant: 'neutral', label: 'Draft' },
      submitted: { variant: 'info', label: 'Submitted' },
      in_review: { variant: 'warning', label: 'In Review' },
      changes_requested: { variant: 'critical', label: 'Changes Requested' },
      resubmitted: { variant: 'info', label: 'Resubmitted' },
      approved: { variant: 'success', label: 'Approved' },
      rejected: { variant: 'critical', label: 'Rejected' },
    };
    const s = map[status] || { variant: 'neutral', label: status };
    return <Badge variant={s.variant}>{s.label}</Badge>;
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Content Review Workbench</h1>
          <p className="text-xs text-slate-400 mt-1">
            Pre-publication governance inspection across marketing drafts, press releases, and clinical collateral.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center space-x-2 px-3.5 py-2 bg-navy-900 hover:bg-navy-800 text-slate-200 rounded-xl text-xs font-semibold border border-navy-700 transition-colors shadow-sm"
          >
            <Upload className="w-4 h-4 text-teal-400" />
            <span>Upload Document (PDF/DOCX)</span>
          </button>
          <button
            onClick={() => setShowTextModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 rounded-xl text-xs font-bold shadow-lg shadow-teal-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Draft (Paste Text)</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-navy-950 p-3 rounded-xl border border-navy-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-navy-900 border border-navy-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-400"
          />
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-slate-400 font-medium">Status:</span>
          {['all', 'draft', 'submitted', 'in_review', 'changes_requested', 'approved'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1 rounded-md capitalize transition-colors ${
                statusFilter === s
                  ? 'bg-teal-500/20 text-teal-300 font-semibold border border-teal-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-navy-950 rounded-2xl border border-navy-800 shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-navy-800 bg-navy-900/40 text-slate-400 font-semibold">
                <th className="py-3 px-4">Document Title</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Version</th>
                <th className="py-3 px-4">Author</th>
                <th className="py-3 px-4">Last Updated</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-900">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    Loading drafts...
                  </td>
                </tr>
              ) : filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    No documents found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-navy-900/40 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-200">{doc.title}</div>
                      <div className="text-[11px] text-slate-500 font-mono">#{doc.id}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono uppercase text-[10px] bg-navy-900 px-2 py-0.5 rounded border border-navy-800 text-slate-400">
                        {doc.content_type}
                      </span>
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(doc.status)}</td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-slate-300">v{doc.current_version}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{doc.creator_name}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(doc.updated_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onOpenDocument(doc.id)}
                        className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-navy-850 hover:bg-teal-500 hover:text-slate-950 text-slate-300 rounded-lg text-xs font-semibold border border-navy-700 hover:border-teal-400 transition-all shadow-sm"
                      >
                        <span>Open Workbench</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: New Draft (Paste Text) */}
      {showTextModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-2xl p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-1">Create New Draft for Compliance Check</h2>
            <p className="text-xs text-slate-400 mb-4">Paste marketing, sales, or clinical copy to evaluate against brand rules.</p>

            {errorMsg && (
              <div className="p-3 mb-4 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreateTextDoc} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g. Q4 Clinical Onboarding Deck - Hero Pitch"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  className="w-full bg-navy-900 border border-navy-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-400"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Draft Content (Text)</label>
                <textarea
                  rows={8}
                  placeholder="Paste or write your promotional or clinical text here..."
                  value={newText}
                  onChange={(e) => setNewText(e.target.value)}
                  required
                  className="w-full bg-navy-900 border border-navy-800 rounded-lg p-3 text-xs text-white font-mono focus:outline-none focus:border-teal-400"
                />
                <div className="text-right text-[11px] text-slate-500 mt-1">
                  {newText.length} characters
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-2 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowTextModal(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md"
                >
                  {submitting ? 'Creating...' : 'Create & Open Review'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Upload Document (PDF/DOCX) */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-xl p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-1">Upload Document (PDF or DOCX)</h2>
            <p className="text-xs text-slate-400 mb-4">
              Safely extract text with prompt-injection neutralization and PyMuPDF / python-docx engine.
            </p>

            {errorMsg && (
              <div className="p-3 mb-4 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleUploadDoc} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g. Clinical Protocol Whitepaper"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  className="w-full bg-navy-900 border border-navy-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-400"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Select File (.pdf, .docx, .txt)</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  required
                  className="w-full bg-navy-900 border border-navy-800 rounded-lg p-2 text-xs text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-teal-500 file:text-slate-950 hover:file:bg-teal-400"
                />
                <div className="text-[11px] text-slate-500 mt-1.5">
                  Max size: 10 MB. Server-side prompt injection detection automatically active.
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-2 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md"
                >
                  {submitting ? 'Extracting & Scanning...' : 'Upload & Scan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
