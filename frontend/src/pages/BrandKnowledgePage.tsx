import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { BrandGuideline, ApprovedFact, ApprovedTerminology } from '../types';
import { Badge } from '../components/Badge';
import { useAuth } from '../context/AuthContext';
import {
  BookOpen,
  CheckCircle,
  AlertTriangle,
  Layers,
  Calendar,
  FileText,
  Plus,
  UploadCloud,
  Play,
  CheckCircle2,
  XCircle,
  FileCheck,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

export const BrandKnowledgePage: React.FC = () => {
  const { user, role, activeBrand } = useAuth();
  const [activeTab, setActiveTab] = useState<'guidelines' | 'facts' | 'terminology' | 'ingestion' | 'tester'>('guidelines');
  const [guidelines, setGuidelines] = useState<BrandGuideline[]>([]);
  const [facts, setFacts] = useState<ApprovedFact[]>([]);
  const [terms, setTerms] = useState<ApprovedTerminology[]>([]);
  const [loading, setLoading] = useState(true);

  // Rule Condition Tester State
  const [testRuleType, setTestRuleType] = useState('prohibited_phrase');
  const [testPattern, setTestPattern] = useState('guaranteed cure');
  const [testSampleText, setTestSampleText] = useState('Our clinical trials offer a guaranteed cure for metabolic stress.');
  const [testingRule, setTestingRule] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testError, setTestError] = useState('');

  // Guideline Ingestion State
  const [ingestFile, setIngestFile] = useState<File | null>(null);
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [ingestError, setIngestError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadData();
  }, [activeBrand]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [g, f, t] = await Promise.all([
        api.listGuidelines(activeBrand?.id),
        api.getFacts(),
        api.listTerminology(),
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

  const handleRunRuleTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setTestingRule(true);
    setTestError('');
    setTestResult(null);
    try {
      const res = await api.testRuleCondition(testRuleType, testPattern, testSampleText);
      setTestResult(res);
    } catch (err: any) {
      setTestError(err.message || 'Rule testing failed');
    } finally {
      setTestingRule(false);
    }
  };

  const handleIngestDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestFile) return;
    setIngesting(true);
    setIngestError('');
    setIngestResult(null);
    try {
      const res = await api.ingestGuidelineDocument(ingestFile);
      setIngestResult(res);
      await loadData();
    } catch (err: any) {
      setIngestError(err.message || 'Guideline ingestion failed');
    } finally {
      setIngesting(false);
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
          <div className="flex items-center space-x-2 text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">
            <BookOpen className="w-4 h-4" />
            <span>Policy & Rule Authority</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">Brand Knowledge & Guideline Ingestion</h1>
          <p className="text-xs text-slate-400 mt-1">
            Canonical truth source: versioned guidelines, approved product facts, commercial pricing, and guideline ingestion pipeline.
          </p>
        </div>
        <div className="text-xs text-slate-400">
          Brand Workspace: <strong className="text-teal-400">{activeBrand?.name || 'NovusBio Health'}</strong>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-navy-800 pb-3 text-xs">
        <button
          onClick={() => setActiveTab('guidelines')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'guidelines'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
          }`}
        >
          Brand Guidelines ({guidelines.length})
        </button>
        <button
          onClick={() => setActiveTab('facts')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'facts'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
          }`}
        >
          Approved Facts & Claims ({facts.length})
        </button>
        <button
          onClick={() => setActiveTab('terminology')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'terminology'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
          }`}
        >
          Terminology Glossary ({terms.length})
        </button>
        <button
          onClick={() => setActiveTab('ingestion')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'ingestion'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
          }`}
        >
          PDF/DOCX Guideline Ingestion
        </button>
        <button
          onClick={() => setActiveTab('tester')}
          className={`px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
            activeTab === 'tester'
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
              : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
          }`}
        >
          Rule Condition Tester
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
                          Clarification: {g.clarification_notes}
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
                      <Badge variant={g.is_active ? 'teal' : 'neutral'}>
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

      {/* Tab 2: Approved Facts & Claims */}
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
                  <th className="py-3 px-4">Prohibited Variants</th>
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

      {/* Tab 4: Guideline Ingestion Pipeline */}
      {activeTab === 'ingestion' && (
        <div className="bg-navy-950 rounded-2xl border border-navy-800 p-6 shadow-xl space-y-6">
          <div className="max-w-2xl">
            <h2 className="text-base font-bold text-white mb-1">Guideline Document Ingestion Pipeline</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload brand style manuals, messaging guidelines, or compliance handbooks (PDF or DOCX).
              The parser extracts text, sanitizes prompt injection threats, identifies candidate rules,
              and stages them for human administrator approval before entering active enforcement.
            </p>
          </div>

          <form onSubmit={handleIngestDocument} className="space-y-4 max-w-xl">
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-navy-700 hover:border-teal-500/50 bg-navy-900/60 rounded-xl p-8 text-center cursor-pointer transition-colors"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setIngestFile(e.target.files[0]);
                  }
                }}
              />
              <UploadCloud className="w-10 h-10 text-teal-400 mx-auto mb-2 opacity-80" />
              <div className="text-xs font-semibold text-slate-200">
                {ingestFile ? ingestFile.name : 'Click to select or drop a guideline file (PDF, DOCX)'}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">
                {ingestFile ? `${(ingestFile.size / 1024).toFixed(1)} KB` : 'Maximum file size 25MB'}
              </div>
            </div>

            <button
              type="submit"
              disabled={!ingestFile || ingesting}
              className="w-full py-2.5 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all flex items-center justify-center space-x-2"
            >
              {ingesting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Extracting & Validating Rules...</span>
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  <span>Extract & Ingest Guidelines</span>
                </>
              )}
            </button>

            {ingestError && (
              <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300">
                {ingestError}
              </div>
            )}
          </form>

          {ingestResult && (
            <div className="pt-4 border-t border-navy-800 space-y-4">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-5 h-5" />
                <span>Ingestion Successful: {ingestResult.total_rules_extracted || 0} candidate rules extracted</span>
              </div>
              <div className="text-xs text-slate-400">
                Document: <strong className="text-slate-200">{ingestResult.filename || ingestFile?.name}</strong> • Pages:{' '}
                <span className="font-mono">{ingestResult.page_count || 1}</span>
              </div>
              {ingestResult.rules && (
                <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                  {ingestResult.rules.map((r: any, idx: number) => (
                    <div key={idx} className="p-3 bg-navy-900 rounded-xl border border-navy-800 text-xs flex items-start justify-between">
                      <div>
                        <div className="font-semibold text-white">{r.title}</div>
                        <div className="text-slate-400 text-[11px] mt-0.5">{r.rule_text}</div>
                      </div>
                      <Badge variant="teal">{r.category}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Rule Condition Tester */}
      {activeTab === 'tester' && (
        <div className="bg-navy-950 rounded-2xl border border-navy-800 p-6 shadow-xl space-y-6">
          <div className="max-w-2xl">
            <h2 className="text-base font-bold text-white mb-1">Interactive Rule Condition Tester</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Verify deterministic rule regexes and phrase matching conditions against sample content before publishing them to the live engine.
            </p>
          </div>

          <form onSubmit={handleRunRuleTest} className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-6 space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Rule Condition Type</label>
                <select
                  value={testRuleType}
                  onChange={(e) => setTestRuleType(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
                >
                  <option value="prohibited_phrase">Prohibited Phrase / Term</option>
                  <option value="required_phrase">Required Phrase / Mandatory Disclaimer</option>
                  <option value="regex_pattern">Regex Pattern Match</option>
                  <option value="pricing_claim">Pricing & Commercial Claim</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Condition Pattern or Phrase</label>
                <input
                  type="text"
                  required
                  value={testPattern}
                  onChange={(e) => setTestPattern(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-teal-400"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Sample Text to Test</label>
                <textarea
                  rows={4}
                  required
                  value={testSampleText}
                  onChange={(e) => setTestSampleText(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-teal-400"
                />
              </div>

              <button
                type="submit"
                disabled={testingRule}
                className="w-full py-2.5 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all flex items-center justify-center space-x-2"
              >
                {testingRule ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Evaluating Condition...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Test Condition Execution</span>
                  </>
                )}
              </button>

              {testError && (
                <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300">
                  {testError}
                </div>
              )}
            </div>

            <div className="md:col-span-6 bg-navy-900/70 rounded-xl border border-navy-800 p-5 flex flex-col justify-between">
              {testResult ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-navy-800 pb-3">
                    <div className="flex items-center space-x-2">
                      {testResult.matched ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <XCircle className="w-5 h-5 text-slate-500" />
                      )}
                      <span className="text-sm font-bold text-white">
                        {testResult.matched ? 'Condition Triggered (Match Found)' : 'No Match Found'}
                      </span>
                    </div>
                    <Badge variant={testResult.matched ? 'critical' : 'teal'}>
                      {testResult.matched ? 'TRIGGERED' : 'CLEAN'}
                    </Badge>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                      <span className="text-slate-500 block mb-0.5">Matched Substring</span>
                      <strong className="text-rose-400 font-mono">
                        {testResult.matched_text ? `"${testResult.matched_text}"` : 'None'}
                      </strong>
                    </div>

                    <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                      <span className="text-slate-500 block mb-0.5">Execution Latency</span>
                      <strong className="text-teal-400 font-mono">
                        {testResult.execution_ms ? `${testResult.execution_ms.toFixed(2)} ms` : '< 1 ms'}
                      </strong>
                    </div>

                    <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                      <span className="text-slate-500 block mb-0.5">Suggested Finding Severity</span>
                      <strong className="text-amber-400 uppercase">{testResult.suggested_severity || 'HIGH'}</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center h-full py-8 text-slate-500">
                  <FileCheck className="w-10 h-10 text-slate-600 mb-2" />
                  <div className="text-xs font-semibold text-slate-400">Ready to Test</div>
                  <p className="text-[11px] text-slate-500 mt-1 max-w-xs">
                    Enter rule parameters and sample text on the left to verify deterministic trigger logic.
                  </p>
                </div>
              )}
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
