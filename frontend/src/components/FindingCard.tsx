import React, { useState } from 'react';
import { Finding } from '../types';
import { Badge } from './Badge';
import { CheckCircle2, XCircle, AlertTriangle, ArrowRight, BookOpen, Edit3, ShieldAlert } from 'lucide-react';

interface FindingCardProps {
  finding: Finding;
  onResolve: (status: 'accepted' | 'edited' | 'dismissed' | 'escalated', notes?: string, customText?: string) => Promise<void>;
  isReadOnly?: boolean;
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding, onResolve, isReadOnly = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [customText, setCustomText] = useState(finding.suggested_correction || '');
  const [dismissReason, setDismissReason] = useState('');
  const [showDismissModal, setShowDismissModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const severityVariant = {
    critical: 'critical',
    high: 'critical',
    warning: 'warning',
    medium: 'warning',
    low: 'suggestion',
    suggestion: 'suggestion',
  }[finding.severity] as any;

  const handleAccept = async () => {
    setIsSubmitting(true);
    try {
      await onResolve('accepted', 'Applied canonical brand correction');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCustomApply = async () => {
    setIsSubmitting(true);
    try {
      await onResolve('edited', 'Applied custom editor revision', customText);
      setIsEditing(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDismiss = async () => {
    setIsSubmitting(true);
    try {
      await onResolve('dismissed', dismissReason || 'Dismissed as intentional exception');
      setShowDismissModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`p-4 rounded-xl border transition-all ${
      finding.status === 'accepted'
        ? 'bg-emerald-950/20 border-emerald-800/40'
        : finding.status === 'dismissed'
        ? 'bg-slate-900/40 border-slate-800 opacity-60'
        : 'bg-navy-900/90 border-navy-700/80 shadow-md hover:border-teal-500/40'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Badge variant={severityVariant}>{finding.severity.toUpperCase()}</Badge>
          <span className="text-xs font-mono text-slate-400 bg-navy-950 px-2 py-0.5 rounded border border-navy-800">
            {finding.category.replace('_', ' ').toUpperCase()}
          </span>
          <span className="text-xs text-slate-400">#{finding.id}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="text-xs text-slate-400">Confidence:</span>
          <span className="text-xs font-medium text-teal-400 bg-teal-950/40 px-1.5 py-0.5 rounded border border-teal-800/40">
            {finding.confidence}
          </span>
        </div>
      </div>

      {/* Flagged snippet */}
      <div className="mb-3 bg-navy-950/90 p-2.5 rounded-lg border border-navy-800/80">
        <div className="text-xs text-slate-400 mb-1 flex items-center space-x-1">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          <span>Flagged content:</span>
        </div>
        <div className="text-sm font-semibold text-rose-300 font-mono bg-rose-950/30 px-2 py-1 rounded inline-block">
          "{finding.affected_text}"
        </div>
      </div>

      {/* Explanation */}
      <div className="mb-3">
        <div className="text-xs font-medium text-slate-400 mb-0.5">Why it matters:</div>
        <div className="text-sm text-slate-200 leading-relaxed">{finding.explanation}</div>
      </div>

      {/* Source Citation */}
      <div className="mb-3 flex items-center justify-between text-xs bg-navy-850 p-2 rounded border border-navy-700/60">
        <div className="flex items-center space-x-1.5 text-slate-300">
          <BookOpen className="w-3.5 h-3.5 text-teal-400" />
          <span>Rule: <strong className="text-teal-300">{finding.rule_id || 'System Heuristic'}</strong> (v{finding.rule_version})</span>
        </div>
        <div className="text-slate-400 text-right truncate max-w-[200px]" title={finding.source_reference || ''}>
          Source: {finding.source_reference || 'Unverified'}
        </div>
      </div>

      {/* Suggested Correction */}
      {finding.suggested_correction && (
        <div className="mb-3 bg-teal-950/20 p-2.5 rounded-lg border border-teal-800/30">
          <div className="text-xs font-semibold text-teal-400 mb-1 flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
            <span>Suggested Brand Correction:</span>
          </div>
          <div className="text-sm text-teal-200 font-medium">
            {finding.suggested_correction}
          </div>
        </div>
      )}

      {/* Custom Edit Box */}
      {isEditing && (
        <div className="mb-3 p-3 bg-navy-950 rounded border border-navy-700">
          <label className="text-xs font-medium text-slate-300 mb-1 block">Custom replacement text:</label>
          <input
            type="text"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            className="w-full bg-navy-900 border border-navy-700 rounded px-2.5 py-1.5 text-sm text-white focus:outline-none focus:border-teal-400 mb-2"
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setIsEditing(false)}
              className="text-xs px-2.5 py-1 text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={handleCustomApply}
              disabled={isSubmitting}
              className="text-xs px-3 py-1 bg-teal-500 text-slate-950 font-semibold rounded hover:bg-teal-400"
            >
              Apply Custom Text
            </button>
          </div>
        </div>
      )}

      {/* Dismiss Modal */}
      {showDismissModal && (
        <div className="mb-3 p-3 bg-navy-950 rounded border border-rose-900/60">
          <label className="text-xs font-medium text-slate-300 mb-1 block">Reason for dismissing this finding:</label>
          <input
            type="text"
            placeholder="e.g. Approved clinical trial exception..."
            value={dismissReason}
            onChange={(e) => setDismissReason(e.target.value)}
            className="w-full bg-navy-900 border border-navy-700 rounded px-2.5 py-1.5 text-sm text-white focus:outline-none focus:border-rose-400 mb-2"
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowDismissModal(false)}
              className="text-xs px-2.5 py-1 text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={handleDismiss}
              disabled={isSubmitting}
              className="text-xs px-3 py-1 bg-rose-600 text-white font-semibold rounded hover:bg-rose-500"
            >
              Confirm Dismissal
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isReadOnly && finding.status === 'open' && (
        <div className="flex items-center justify-between pt-2 border-t border-navy-800">
          <div className="flex items-center space-x-2">
            {finding.suggested_correction && (
              <button
                onClick={handleAccept}
                disabled={isSubmitting}
                className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold bg-teal-500 text-slate-950 rounded-lg hover:bg-teal-400 transition-colors shadow-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Accept Suggestion</span>
              </button>
            )}
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="flex items-center space-x-1 px-2.5 py-1.5 text-xs font-medium text-slate-300 bg-navy-800 hover:bg-navy-700 rounded-lg border border-navy-700 transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5 text-slate-400" />
              <span>Edit</span>
            </button>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowDismissModal(true)}
              className="text-xs text-slate-400 hover:text-rose-400 transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Resolution State Tag */}
      {finding.status !== 'open' && (
        <div className="pt-2 border-t border-navy-800/80 flex items-center justify-between text-xs">
          <span className="text-slate-400">Status: <strong className="text-teal-400 capitalize">{finding.status}</strong></span>
          {finding.resolved_by && (
            <span className="text-slate-400">by {finding.resolved_by}</span>
          )}
        </div>
      )}
    </div>
  );
};
