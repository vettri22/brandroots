import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { BrandAsset, ImageComplianceResult } from '../types';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/Badge';
import {
  Image as ImageIcon,
  UploadCloud,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Plus,
  Search,
  Shield,
  FileCheck,
  Eye,
  Hash,
  Maximize2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

export const AssetsPage: React.FC = () => {
  const { user, role, activeBrand } = useAuth();
  const [assets, setAssets] = useState<BrandAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  // Verify Image Sandbox State
  const [testFile, setTestFile] = useState<File | null>(null);
  const [testAltText, setTestAltText] = useState('');
  const [testChannel, setTestChannel] = useState('website');
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<ImageComplianceResult | null>(null);
  const [verifyError, setVerifyError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // New Asset Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newAssetName, setNewAssetName] = useState('');
  const [newAssetType, setNewAssetType] = useState('logo');
  const [newAssetUsage, setNewAssetUsage] = useState('');
  const [newAssetFile, setNewAssetFile] = useState<File | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [registerError, setRegisterError] = useState('');
  const newAssetFileInputRef = useRef<HTMLInputElement>(null);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const data = await api.listAssets(activeBrand?.id);
      setAssets(data);
    } catch (err: any) {
      console.error('Failed to load assets', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssets();
  }, [activeBrand]);

  const handleTestImageSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testFile) return;
    setVerifying(true);
    setVerifyError('');
    setVerifyResult(null);
    try {
      const res = await api.verifyImage(testFile, activeBrand?.id, testAltText, testChannel);
      setVerifyResult(res);
    } catch (err: any) {
      setVerifyError(err.message || 'Image verification failed');
    } finally {
      setVerifying(false);
    }
  };

  const handleRegisterAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAssetFile || !newAssetName) return;
    setIsRegistering(true);
    setRegisterError('');
    try {
      await api.registerAsset(newAssetName, newAssetType, newAssetFile, activeBrand?.id, newAssetUsage);
      setShowAddModal(false);
      setNewAssetName('');
      setNewAssetType('logo');
      setNewAssetUsage('');
      setNewAssetFile(null);
      await loadAssets();
    } catch (err: any) {
      setRegisterError(err.message || 'Failed to register brand asset');
    } finally {
      setIsRegistering(false);
    }
  };

  const filteredAssets = assets.filter((asset) => {
    if (typeFilter !== 'all' && asset.asset_type !== typeFilter) return false;
    if (searchQuery && !asset.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">
            <ImageIcon className="w-4 h-4" />
            <span>Visual Brand Governance</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">Approved Asset Library & Validator</h1>
          <p className="text-xs text-slate-400 mt-1">
            Cryptographic SHA-256 asset registration, contrast verification, and WCAG accessibility standards.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadAssets}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-navy-900 hover:bg-navy-800 text-slate-300 text-xs font-medium rounded-xl border border-navy-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-teal-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-1.5 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register Asset</span>
          </button>
        </div>
      </div>

      {/* Interactive Image Compliance Validator Sandbox */}
      <div className="bg-gradient-to-br from-navy-950 to-navy-900 rounded-2xl border border-teal-500/20 p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-teal-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-4 h-4 text-teal-400" />
          <h2 className="text-base font-bold text-white tracking-tight">Image Compliance Preflight Sandbox</h2>
        </div>
        <p className="text-xs text-slate-400 mb-6 max-w-2xl leading-relaxed">
          Test any image before publishing. The engine performs exact cryptographic SHA-256 fingerprinting,
          perceptual dHash similarity analysis, automated luminance contrast ratio calculation, and WCAG alt-text validation.
        </p>

        <form onSubmit={handleTestImageSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-6">
          <div className="md:col-span-6 space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Select Image File (PNG, JPG, WebP)</label>
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-navy-700 hover:border-teal-500/50 bg-navy-900/60 rounded-xl p-6 text-center cursor-pointer transition-colors"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setTestFile(e.target.files[0]);
                    }
                  }}
                />
                <UploadCloud className="w-8 h-8 text-teal-400 mx-auto mb-2 opacity-80" />
                <div className="text-xs font-medium text-slate-300">
                  {testFile ? testFile.name : 'Click to select or drop an image file'}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">
                  {testFile ? `${(testFile.size / 1024).toFixed(1)} KB` : 'Maximum file size 10MB'}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Target Channel</label>
                <select
                  value={testChannel}
                  onChange={(e) => setTestChannel(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
                >
                  <option value="website">Website (WCAG AA)</option>
                  <option value="social">Social Media</option>
                  <option value="email">Email Campaign</option>
                  <option value="print">Print Collateral</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Proposed Alt Text</label>
                <input
                  type="text"
                  placeholder="e.g. NovusBio Logo in Cobalt Blue..."
                  value={testAltText}
                  onChange={(e) => setTestAltText(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-400"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={!testFile || verifying}
              className="w-full py-2.5 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md flex items-center justify-center space-x-2"
            >
              {verifying ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Analyzing Image Signatures...</span>
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  <span>Run Visual Preflight Check</span>
                </>
              )}
            </button>

            {verifyError && (
              <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300">
                {verifyError}
              </div>
            )}
          </div>

          {/* Result Output */}
          <div className="md:col-span-6 bg-navy-900/80 rounded-xl border border-navy-800 p-5 flex flex-col justify-between">
            {verifyResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-navy-800 pb-3">
                  <div className="flex items-center space-x-2">
                    {verifyResult.is_compliant ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-rose-400" />
                    )}
                    <span className="text-sm font-bold text-white">
                      {verifyResult.is_compliant ? 'Image Approved for Use' : 'Non-Compliant Image'}
                    </span>
                  </div>
                  <Badge variant={verifyResult.is_compliant ? 'teal' : 'critical'}>
                    {verifyResult.is_compliant ? 'PASS' : 'FLAGGED'}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                    <span className="text-slate-500 block mb-0.5">Asset Registry Match</span>
                    <strong className="text-slate-200">
                      {verifyResult.matching_asset_id ? 'Approved Brand Asset' : 'Unregistered Asset'}
                    </strong>
                  </div>
                  <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                    <span className="text-slate-500 block mb-0.5">SHA-256 Match</span>
                    <strong className="text-slate-200">{verifyResult.is_exact_sha256_match ? 'Exact 100%' : 'None'}</strong>
                  </div>
                  <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                    <span className="text-slate-500 block mb-0.5">Calculated Contrast Ratio</span>
                    <strong className={`font-mono ${verifyResult.contrast_ratio >= 4.5 ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {verifyResult.contrast_ratio}:1 {verifyResult.contrast_ratio >= 4.5 ? '(WCAG AA Pass)' : '(Low Contrast)'}
                    </strong>
                  </div>
                  <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-850">
                    <span className="text-slate-500 block mb-0.5">Accessibility (Alt-Text)</span>
                    <strong className={verifyResult.alt_text_valid ? 'text-emerald-400' : 'text-rose-400'}>
                      {verifyResult.alt_text_valid ? 'Provided & Valid' : 'Missing or Inadequate'}
                    </strong>
                  </div>
                </div>

                {verifyResult.violations.length > 0 && (
                  <div className="space-y-1.5 pt-2">
                    <div className="text-xs font-semibold text-rose-300">Identified Violations:</div>
                    {verifyResult.violations.map((v, i) => (
                      <div key={i} className="text-xs text-rose-400 bg-rose-950/40 p-2 rounded border border-rose-900/50 flex items-start space-x-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-rose-400" />
                        <span>{v}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center h-full py-8 text-slate-500">
                <FileCheck className="w-10 h-10 text-slate-600 mb-2" />
                <div className="text-xs font-semibold text-slate-400">Preflight Engine Ready</div>
                <p className="text-[11px] text-slate-500 mt-1 max-w-xs">
                  Upload an image file on the left and click "Run Visual Preflight Check" to inspect compliance metrics.
                </p>
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Asset Library Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <span className="text-xs font-semibold text-slate-400">Category:</span>
            {['all', 'logo', 'imagery', 'typography', 'color_palette'].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all ${
                  typeFilter === t
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                    : 'text-slate-400 hover:text-white bg-navy-900 border border-transparent'
                }`}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search assets by name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-navy-900 border border-navy-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-400"
            />
          </div>
        </div>

        {/* Assets Grid */}
        {loading ? (
          <div className="p-12 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin text-teal-400 mx-auto mb-2" />
            <p className="text-xs">Loading approved assets...</p>
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="p-12 text-center bg-navy-950 rounded-2xl border border-navy-800 text-slate-400">
            <ImageIcon className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-white mb-1">No Brand Assets Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Register logos, palettes, and imagery to enable automated visual preflight validation.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredAssets.map((asset) => (
              <div
                key={asset.id}
                className="bg-navy-950 rounded-2xl border border-navy-800 p-5 hover:border-teal-500/30 transition-all shadow-md flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="teal">{asset.asset_type.toUpperCase()}</Badge>
                    <Badge variant={asset.is_approved ? 'teal' : 'neutral'}>
                      {asset.is_approved ? 'APPROVED' : 'DRAFT'}
                    </Badge>
                  </div>
                  <h3 className="text-sm font-bold text-white tracking-tight">{asset.name}</h3>
                  {asset.usage_guideline && (
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2">
                      {asset.usage_guideline}
                    </p>
                  )}
                </div>

                <div className="space-y-2 pt-3 border-t border-navy-850 text-xs">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Hash className="w-3 h-3 text-teal-400" />
                      <span>SHA-256 Hash:</span>
                    </span>
                    <span className="font-mono text-[10px] text-slate-300 truncate max-w-[140px]" title={asset.file_hash}>
                      {asset.file_hash ? asset.file_hash.slice(0, 16) + '...' : 'Pending'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Maximize2 className="w-3 h-3 text-slate-500" />
                      <span>Dimensions:</span>
                    </span>
                    <span className="text-slate-300 font-mono text-[11px]">
                      {asset.width && asset.height ? `${asset.width} × ${asset.height} px` : 'Vector / N/A'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-400">
                    <span>Alt Text Required:</span>
                    <span className={asset.alt_text_required ? 'text-teal-400 font-semibold' : 'text-slate-500'}>
                      {asset.alt_text_required ? 'Yes (Strict WCAG)' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Register Asset Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-1">Register Approved Brand Asset</h2>
            <p className="text-xs text-slate-400 mb-4">
              Upload canonical brand files. Cryptographic hashes are generated and verified on the server.
            </p>

            {registerError && (
              <div className="p-3 mb-4 bg-rose-950/80 border border-rose-800 rounded-lg text-xs text-rose-300">
                {registerError}
              </div>
            )}

            <form onSubmit={handleRegisterAsset} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Asset Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. NovusBio Primary Logo Lockup"
                  value={newAssetName}
                  onChange={(e) => setNewAssetName(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Asset Type</label>
                  <select
                    value={newAssetType}
                    onChange={(e) => setNewAssetType(e.target.value)}
                    className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
                  >
                    <option value="logo">Logo</option>
                    <option value="imagery">Imagery / Photography</option>
                    <option value="color_palette">Color Palette</option>
                    <option value="typography">Typography</option>
                    <option value="iconography">Iconography</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">File Upload</label>
                  <input
                    ref={newAssetFileInputRef}
                    type="file"
                    required
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setNewAssetFile(e.target.files[0]);
                      }
                    }}
                    className="w-full text-xs text-slate-400 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:bg-navy-800 file:text-teal-400 hover:file:bg-navy-700 cursor-pointer"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Usage Guidelines</label>
                <textarea
                  rows={3}
                  placeholder="Specify clear space requirements, minimum dimensions, or prohibited backgrounds..."
                  value={newAssetUsage}
                  onChange={(e) => setNewAssetUsage(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-teal-400"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isRegistering || !newAssetFile || !newAssetName}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all flex items-center space-x-1.5"
                >
                  {isRegistering ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Hashing & Storing...</span>
                    </>
                  ) : (
                    <span>Register Asset</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
