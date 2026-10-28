import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { OrganizationMembership, UserRole } from '../types';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/Badge';
import {
  Users,
  UserPlus,
  Shield,
  Check,
  X,
  Mail,
  Building2,
  Lock,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';

export const TeamPage: React.FC = () => {
  const { user, role } = useAuth();
  const [members, setMembers] = useState<OrganizationMembership[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<string>('creator');
  const [inviting, setInviting] = useState(false);
  const [inviteError, setInviteError] = useState('');
  const [inviteSuccess, setInviteSuccess] = useState('');

  const orgId = user?.organization_id || 'org-demo-001';

  const loadMembers = async () => {
    try {
      setLoading(true);
      const data = await api.listMembers(orgId);
      setMembers(data);
    } catch (err: any) {
      console.error('Failed to load organization members', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, [orgId]);

  const handleInviteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;
    setInviting(true);
    setInviteError('');
    setInviteSuccess('');
    try {
      await api.inviteMember(orgId, inviteEmail, inviteRole);
      setInviteSuccess(`Invitation successfully sent to ${inviteEmail} as ${inviteRole}`);
      setInviteEmail('');
      await loadMembers();
      setTimeout(() => {
        setShowInviteModal(false);
        setInviteSuccess('');
      }, 1500);
    } catch (err: any) {
      setInviteError(err.message || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  const permissionMatrix: { permission: string; description: string; roles: Record<string, boolean> }[] = [
    {
      permission: 'org:manage',
      description: 'Manage organization settings, billing, and workspace configuration',
      roles: { org_owner: true, brand_admin: false, reviewer: false, creator: false, read_only: false },
    },
    {
      permission: 'org:invite',
      description: 'Invite new team members and assign roles',
      roles: { org_owner: true, brand_admin: true, reviewer: false, creator: false, read_only: false },
    },
    {
      permission: 'brand:create',
      description: 'Create and configure new brand workspaces',
      roles: { org_owner: true, brand_admin: true, reviewer: false, creator: false, read_only: false },
    },
    {
      permission: 'guidelines:manage',
      description: 'Publish, edit, ingest, and deactivate brand rules and guidelines',
      roles: { org_owner: true, brand_admin: true, reviewer: false, creator: false, read_only: false },
    },
    {
      permission: 'evidence:create',
      description: 'Submit claims, clinical facts, and sources to Evidence Ledger',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: true, read_only: false },
    },
    {
      permission: 'evidence:approve',
      description: 'Authorize and sign off on evidence records and public-use permissions',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: false, read_only: false },
    },
    {
      permission: 'content:create',
      description: 'Draft, submit, and upload content documents for review',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: true, read_only: false },
    },
    {
      permission: 'content:review',
      description: 'Assign reviewers, request changes, and resolve findings',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: false, read_only: false },
    },
    {
      permission: 'content:approve',
      description: 'Execute version-bound formal approvals (Creators cannot self-approve)',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: false, read_only: false },
    },
    {
      permission: 'radar:view',
      description: 'View Guideline Clarity Radar analytics and signal clustering',
      roles: { org_owner: true, brand_admin: true, reviewer: true, creator: true, read_only: true },
    },
    {
      permission: 'radar:resolve',
      description: 'Adopt rule clarification proposals and resolve ambiguity signals',
      roles: { org_owner: true, brand_admin: true, reviewer: false, creator: false, read_only: false },
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">
            <Building2 className="w-4 h-4" />
            <span>Multi-Tenant Access Control</span>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">Team & Role-Based Permissions</h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage organization members, workspace privileges, and cryptographic access boundaries.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadMembers}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-navy-900 hover:bg-navy-800 text-slate-300 text-xs font-medium rounded-xl border border-navy-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-teal-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setShowInviteModal(true)}
            className="flex items-center space-x-1.5 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>Invite Member</span>
          </button>
        </div>
      </div>

      {/* Members List */}
      <div className="bg-navy-950 rounded-2xl border border-navy-800 overflow-hidden shadow-lg">
        <div className="p-5 border-b border-navy-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-teal-400" />
            <h2 className="text-sm font-bold text-white">Active Organization Members</h2>
          </div>
          <span className="text-xs text-slate-500 font-mono">Org ID: {orgId}</span>
        </div>

        {loading ? (
          <div className="p-10 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin text-teal-400 mx-auto mb-2" />
            <p className="text-xs">Loading members...</p>
          </div>
        ) : (
          <div className="divide-y divide-navy-800/80">
            {members.map((m) => {
              const displayEmail = m.user_email || m.user?.email || m.user_id || 'User';
              return (
              <div key={m.id} className="p-5 flex items-center justify-between hover:bg-navy-900/40 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500/20 to-cyan-500/10 border border-teal-500/30 flex items-center justify-center font-bold text-teal-300 text-sm">
                    {displayEmail.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-bold text-white">{displayEmail}</span>
                      {m.user_id === user?.id && (
                        <span className="text-[10px] bg-teal-950 text-teal-300 border border-teal-800 px-1.5 py-0.5 rounded font-mono">
                          YOU
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      Joined: {new Date(m.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <Badge variant={m.role === 'org_owner' ? 'critical' : m.role === 'brand_admin' ? 'teal' : 'neutral'}>
                    {m.role.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
              </div>
            );
            })}
          </div>
        )}
      </div>

      {/* Role-Based Permission Matrix */}
      <div className="bg-navy-950 rounded-2xl border border-navy-800 overflow-hidden shadow-lg">
        <div className="p-5 border-b border-navy-800">
          <div className="flex items-center space-x-2">
            <Lock className="w-4 h-4 text-teal-400" />
            <h2 className="text-sm font-bold text-white">System Permission Matrix (Zero Frontend Trust)</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Every backend API endpoint strictly verifies authorization against this matrix before executing any operation.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/80 text-slate-400 border-b border-navy-800 font-semibold">
              <tr>
                <th className="p-4 w-48">Capability</th>
                <th className="p-4">Description</th>
                <th className="p-4 text-center">Org Owner</th>
                <th className="p-4 text-center">Brand Admin</th>
                <th className="p-4 text-center">Reviewer</th>
                <th className="p-4 text-center">Creator</th>
                <th className="p-4 text-center">Read-Only</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-850">
              {permissionMatrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-navy-900/30">
                  <td className="p-4 font-mono font-bold text-teal-300">{row.permission}</td>
                  <td className="p-4 text-slate-300">{row.description}</td>
                  <td className="p-4 text-center">
                    {row.roles.org_owner ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  <td className="p-4 text-center">
                    {row.roles.brand_admin ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  <td className="p-4 text-center">
                    {row.roles.reviewer ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  <td className="p-4 text-center">
                    {row.roles.creator ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  <td className="p-4 text-center">
                    {row.roles.read_only ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-navy-950 border border-navy-700 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-base font-bold text-white mb-1">Invite Team Member</h2>
            <p className="text-xs text-slate-400 mb-4">
              Add a colleague to your organization with specific role privileges.
            </p>

            {inviteError && (
              <div className="p-3 mb-4 bg-rose-950/80 border border-rose-800 rounded-lg text-xs text-rose-300">
                {inviteError}
              </div>
            )}

            {inviteSuccess && (
              <div className="p-3 mb-4 bg-emerald-950/80 border border-emerald-800 rounded-lg text-xs text-emerald-300">
                {inviteSuccess}
              </div>
            )}

            <form onSubmit={handleInviteSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="email"
                    required
                    placeholder="colleague@company.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="w-full bg-navy-900 border border-navy-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-teal-400"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Assigned Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full bg-navy-900 border border-navy-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-400"
                >
                  <option value="creator">Content Creator (Draft & Submit)</option>
                  <option value="reviewer">Reviewer (Review, Request Changes, Approve)</option>
                  <option value="brand_admin">Brand Administrator (Manage Guidelines & Ledger)</option>
                  <option value="org_owner">Organisation Owner (Full System Control)</option>
                  <option value="read_only">Read-Only Contributor (Audit & View)</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inviting || !inviteEmail}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all flex items-center space-x-1.5"
                >
                  {inviting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Sending Invitation...</span>
                    </>
                  ) : (
                    <span>Send Invitation</span>
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
