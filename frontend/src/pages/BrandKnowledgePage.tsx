import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { BrandGuideline, ApprovedFact, ApprovedTerminology } from '../types';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import { BookOpen, CheckCircle, AlertTriangle, Layers, Calendar, FileText, Plus } from 'lucide-react';

export const BrandKnowledgePage: React.FC = () => {
  const { role } = useAuth();
  const [activeTab, setActiveTab] = useState<'guidelines' | 'facts' | 'terminology' | 'assets'>('guidelines');
  const [guidelines, setGuidelines] = useState<BrandGuideline[]>([]);
  const [facts, setFacts] = useState<ApprovedFact[]>([]);
  const [terms, setTerms] = useState<ApprovedTerminology[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [g, f, t] = await Promise.all([
        api.getGuidelines(),
        api.getFacts(),
        api.getTerminology(),
      ]);
      setGuidelines(g);
      setFacts(f);
      setTerms(t);
    } catch (e) {
      console.error('Failed to load brand knowledge', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-teal-400">
          <div className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">Loading Brand Knowledge Repository...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Brand Knowledge Management</h1>
          <p className="text-xs text-slate-400 mt-1">
            Canonical truth source: versioned guidelines, approved product facts, commercial pricing, and terminology glossary.
          </p>
        </div>
        <div className="text-xs text-slate-400">
          Managed by: <strong className="text-teal-400">Elena Rostova (Brand Governance Owner)</strong>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-navy-800 pb-2 text-xs">
        <button
          onClick={() => setActiveTab('guidelines')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'guidelines'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Brand Guidelines ({guidelines.length})
        </button>
        <button
          onClick={() => setActiveTab('facts')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'facts'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Approved Facts & Pricing ({facts.length})
        </button>
        <button
          onClick={() => setActiveTab('terminology')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'terminology'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Terminology Glossary ({terms.length})
        </button>
        <button
          onClick={() => setActiveTab('assets')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'assets'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Brand Assets & Colors
        </button>
      </div>

      {/* Tab 1: Guidelines Table */}
      {activeTab === 'guidelines' && (
        <div className="bg-navy-950 rounded-2xl border border-navy-800 shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 bg-navy-900/40 text-slate-400 font-semibold">
                  <th className="py-3 px-4">Rule ID & Version</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Title & Guideline Text</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Source Reference</th>
                  <th className="py-3 px-4">Effective Date</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-900">
                {guidelines.map((g) => (
                  <tr key={g.id} className="hover:bg-navy-900/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-mono font-bold text-teal-300">{g.id}</div>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                        v{g.version}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono uppercase text-[10px] bg-navy-900 px-2 py-0.5 rounded border border-navy-800 text-slate-400">
                        {g.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-semibold text-slate-200 mb-1">{g.title}</div>
                      <div className="text-slate-400 text-[11px] leading-relaxed">{g.rule_text}</div>
                      {g.clarification_notes && (
                        <div className="mt-1.5 text-[10px] text-teal-300 font-mono bg-teal-950/40 p-1.5 rounded border border-teal-800/40">
                          {g.clarification_notes}
                        </div>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant={g.severity as any}>{g.severity.toUpperCase()}</Badge>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {g.source_reference || 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 font-mono text-[11px]">
                      {g.effective_date}
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant={g.is_active ? 'success' : 'neutral'}>
                        {g.is_active ? 'ACTIVE' : 'DEPRECATED'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Approved Facts & Pricing */}
      {activeTab === 'facts' && (
        <div className="bg-navy-950 rounded-2xl border border-navy-800 shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 bg-navy-900/40 text-slate-400 font-semibold">
                  <th className="py-3 px-4">Fact ID & Version</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Canonical Claim Statement</th>
                  <th className="py-3 px-4">Canonical Value</th>
                  <th className="py-3 px-4">Prohibited Old Figures</th>
                  <th className="py-3 px-4">Source Document</th>
                  <th className="py-3 px-4">Effective Dates</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-900">
                {facts.map((f) => (
                  <tr key={f.id} className="hover:bg-navy-900/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-mono font-bold text-teal-300">{f.id}</div>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-navy-900 text-slate-400 border border-navy-800">
                        v{f.version}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono uppercase text-[10px] bg-navy-900 px-2 py-0.5 rounded border border-navy-800 text-slate-400">
                        {f.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-sm font-medium text-slate-200">
                      {f.claim_statement}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                        {f.canonical_value}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="space-x-1">
                        {f.prohibited_old_values.map((v, i) => (
                          <span key={i} className="font-mono text-[10px] text-rose-400 bg-rose-950/50 px-1.5 py-0.5 rounded border border-rose-900 line-through">
                            {v}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {f.source_document}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 font-mono text-[10px]">
                      {f.effective_date} {f.expiry_date ? `to ${f.expiry_date}` : ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Terminology */}
      {activeTab === 'terminology' && (
        <div className="bg-navy-950 rounded-2xl border border-navy-800 shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 bg-navy-900/40 text-slate-400 font-semibold">
                  <th className="py-3 px-4">Term ID</th>
                  <th className="py-3 px-4">Approved Preferred Term</th>
                  <th className="py-3 px-4">Prohibited / Deprecated Variants</th>
                  <th className="py-3 px-4">Brand Rationale</th>
                  <th className="py-3 px-4">Context Guidance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-900">
                {terms.map((t) => (
                  <tr key={t.id} className="hover:bg-navy-900/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-300">{t.id}</td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-emerald-300 bg-emerald-950/60 px-2 py-1 rounded border border-emerald-800">
                        {t.preferred_term}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {t.prohibited_variants.map((v, i) => (
                          <span key={i} className="font-mono text-[10px] text-rose-300 bg-rose-950/50 px-1.5 py-0.5 rounded border border-rose-900">
                            ✕ {v}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 max-w-xs">{t.rationale}</td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px] max-w-xs">{t.context_guidance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Brand Assets */}
      {activeTab === 'assets' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 space-y-3">
            <div className="text-xs font-bold text-slate-300">Primary Color</div>
            <div className="h-16 rounded-xl bg-[#0A192F] border border-navy-700 flex items-center justify-center font-mono text-xs text-white">
              #0A192F (Deep Medical Navy)
            </div>
            <p className="text-[11px] text-slate-400">Primary background and brand banner surface.</p>
          </div>

          <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 space-y-3">
            <div className="text-xs font-bold text-slate-300">Accent Color</div>
            <div className="h-16 rounded-xl bg-[#0D9488] flex items-center justify-center font-mono text-xs text-slate-950 font-bold">
              #0D9488 (Clinical Cyan / Teal)
            </div>
            <p className="text-[11px] text-slate-400">Accent buttons, highlights, and verified badges.</p>
          </div>

          <div className="bg-navy-950 p-5 rounded-2xl border border-navy-800 space-y-3">
            <div className="text-xs font-bold text-slate-300">Typography</div>
            <div className="p-3 rounded-xl bg-navy-900 border border-navy-800 text-xs text-slate-200 font-sans space-y-1">
              <div className="font-bold text-sm">Inter Display</div>
              <div className="font-mono text-[11px] text-teal-400">JetBrains Mono (Data/Findings)</div>
            </div>
            <p className="text-[11px] text-slate-400">Approved corporate typography stack.</p>
          </div>
        </div>
      )}
    </div>
  );
};
