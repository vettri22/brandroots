import {
  User,
  ContentDocument,
  DocumentVersion,
  ReviewJob,
  Finding,
  ReviewComment,
  GuidelineInsight,
  ProposedClarification,
  BrandGuideline,
  ApprovedFact,
  ApprovedTerminology,
  BrandEvidence,
  Brand,
  Organization,
  OrganizationMembership,
  BrandAsset,
  ImageComplianceResult,
  NotificationItem,
  ApprovalRecord,
  DashboardMetrics,
  AuditEvent,
  UserRole
} from '../types';

const API_BASE =
  (import.meta as any).env?.VITE_API_URL ||
  (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000')
    ? 'http://127.0.0.1:8000/api/v1'
    : '/api/v1');

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('proofline_token') || localStorage.getItem('brandroots_token');
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // --- Auth & Profile ---
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid credentials');
    }
    const data = await res.json();
    localStorage.setItem('proofline_token', data.access_token);
    return data;
  },

  async register(fullName: string, email: string, password: string, role: string = 'creator') {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: fullName, email, password, role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async logout() {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    }).catch(() => {});
    localStorage.removeItem('proofline_token');
    localStorage.removeItem('brandroots_token');
  },

  async switchRole(role: UserRole) {
    const res = await fetch(`${API_BASE}/auth/switch-demo-role?role=${role}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Failed to switch role');
    const data = await res.json();
    localStorage.setItem('proofline_token', data.access_token);
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch user');
    return res.json();
  },

  async requestPasswordReset(email: string) {
    const res = await fetch(`${API_BASE}/auth/password-reset/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    return res.json();
  },

  async confirmPasswordReset(token: string, newPassword: string) {
    const res = await fetch(`${API_BASE}/auth/password-reset/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Password reset failed');
    }
    return res.json();
  },

  // --- Organizations & Memberships ---
  async listOrganizations(): Promise<Organization[]> {
    const res = await fetch(`${API_BASE}/auth/organizations`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch organizations');
    return res.json();
  },

  async createOrganization(name: string, slug: string): Promise<Organization> {
    const res = await fetch(`${API_BASE}/auth/organizations`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, slug }),
    });
    if (!res.ok) throw new Error('Failed to create organization');
    return res.json();
  },

  async listMembers(orgId: string): Promise<OrganizationMembership[]> {
    const res = await fetch(`${API_BASE}/auth/organizations/${orgId}/members`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch members');
    return res.json();
  },

  async inviteMember(orgId: string, email: string, role: string) {
    const res = await fetch(`${API_BASE}/auth/organizations/${orgId}/invitations`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, role }),
    });
    if (!res.ok) throw new Error('Failed to send invitation');
    return res.json();
  },

  // --- Brands ---
  async listBrands(): Promise<Brand[]> {
    const res = await fetch(`${API_BASE}/brand/brands`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch brands');
    return res.json();
  },

  async createBrand(brandData: Partial<Brand>): Promise<Brand> {
    const res = await fetch(`${API_BASE}/brand/brands`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(brandData),
    });
    if (!res.ok) throw new Error('Failed to create brand');
    return res.json();
  },

  async getBrand(id: string): Promise<Brand> {
    const res = await fetch(`${API_BASE}/brand/brands/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch brand');
    return res.json();
  },

  async updateBrand(id: string, brandData: Partial<Brand>): Promise<Brand> {
    const res = await fetch(`${API_BASE}/brand/brands/${id}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(brandData),
    });
    if (!res.ok) throw new Error('Failed to update brand');
    return res.json();
  },

  // --- Brand Evidence Ledger (Signature Module) ---
  async listEvidence(params?: { brand_id?: string; category?: string; status_filter?: string; search?: string }): Promise<BrandEvidence[]> {
    const q = new URLSearchParams();
    if (params?.brand_id) q.append('brand_id', params.brand_id);
    if (params?.category) q.append('category', params.category);
    if (params?.status_filter) q.append('status_filter', params.status_filter);
    if (params?.search) q.append('search', params.search);

    const res = await fetch(`${API_BASE}/evidence?${q.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evidence ledger');
    return res.json();
  },

  async createEvidence(evidenceData: Partial<BrandEvidence>): Promise<BrandEvidence> {
    const res = await fetch(`${API_BASE}/evidence`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(evidenceData),
    });
    if (!res.ok) throw new Error('Failed to create evidence record');
    return res.json();
  },

  async getEvidence(id: string): Promise<BrandEvidence> {
    const res = await fetch(`${API_BASE}/evidence/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evidence record');
    return res.json();
  },

  async updateEvidence(id: string, evidenceData: Partial<BrandEvidence>): Promise<BrandEvidence> {
    const res = await fetch(`${API_BASE}/evidence/${id}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(evidenceData),
    });
    if (!res.ok) throw new Error('Failed to update evidence record');
    return res.json();
  },

  async changeEvidenceStatus(id: string, newStatus: string, reason?: string): Promise<BrandEvidence> {
    const res = await fetch(`${API_BASE}/evidence/${id}/status?new_status=${newStatus}${reason ? `&reason=${encodeURIComponent(reason)}` : ''}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to update evidence status');
    return res.json();
  },

  async archiveEvidence(id: string) {
    const res = await fetch(`${API_BASE}/evidence/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to archive evidence record');
    return res.json();
  },

  async verifyClaim(claimText: string, brandId?: string, channel?: string) {
    const res = await fetch(`${API_BASE}/evidence/verify-claim`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ claim_text: claimText, brand_id: brandId, channel }),
    });
    if (!res.ok) throw new Error('Failed to verify claim');
    return res.json();
  },

  async getEvidenceConflicts(brandId?: string) {
    const url = brandId ? `${API_BASE}/evidence/conflicts?brand_id=${brandId}` : `${API_BASE}/evidence/conflicts`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evidence conflicts');
    return res.json();
  },

  async getExpiringEvidence(days: number = 30) {
    const res = await fetch(`${API_BASE}/evidence/expiring-soon?days=${days}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch expiring evidence');
    return res.json();
  },

  // --- Guidelines & Ingestion ---
  async listGuidelines(brandId?: string, includeInactive: boolean = false): Promise<BrandGuideline[]> {
    const q = new URLSearchParams();
    if (brandId) q.append('brand_id', brandId);
    if (includeInactive) q.append('include_inactive', 'true');

    const res = await fetch(`${API_BASE}/brand/guidelines?${q.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch guidelines');
    return res.json();
  },

  async createGuideline(rule: Partial<BrandGuideline>): Promise<BrandGuideline> {
    const res = await fetch(`${API_BASE}/brand/guidelines`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(rule),
    });
    if (!res.ok) throw new Error('Failed to create guideline');
    return res.json();
  },

  async updateGuideline(id: string, updates: Partial<BrandGuideline>): Promise<BrandGuideline> {
    const res = await fetch(`${API_BASE}/brand/guidelines/${id}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error('Failed to update guideline');
    return res.json();
  },

  async deactivateGuideline(id: string) {
    const res = await fetch(`${API_BASE}/brand/guidelines/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to deactivate guideline');
    return res.json();
  },

  async getGuidelineVersions(ruleId: string) {
    const res = await fetch(`${API_BASE}/brand/guidelines/${ruleId}/versions`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch guideline versions');
    return res.json();
  },

  async testRuleCondition(ruleType: string, patternOrPhrase: string, sampleText: string) {
    const res = await fetch(`${API_BASE}/brand/guidelines/test`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ rule_type: ruleType, pattern_or_phrase: patternOrPhrase, sample_text: sampleText }),
    });
    if (!res.ok) throw new Error('Failed to test rule');
    return res.json();
  },

  async ingestGuidelineDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];

    const res = await fetch(`${API_BASE}/brand/guidelines/ingest-document`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to ingest guideline document');
    return res.json();
  },

  async listFacts(brandId?: string): Promise<ApprovedFact[]> {
    const url = brandId ? `${API_BASE}/brand/facts?brand_id=${brandId}` : `${API_BASE}/brand/facts`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  async getFacts(brandId?: string): Promise<ApprovedFact[]> {
    return this.listFacts(brandId);
  },

  async listTerminology(): Promise<ApprovedTerminology[]> {
    const res = await fetch(`${API_BASE}/brand/terminology`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch terminology');
    return res.json();
  },

  // --- Visual Assets & Accessibility ---
  async listAssets(brandId?: string): Promise<BrandAsset[]> {
    const url = brandId ? `${API_BASE}/assets?brand_id=${brandId}` : `${API_BASE}/assets`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch brand assets');
    return res.json();
  },

  async verifyImage(file: File, brandId?: string, altText?: string, channel?: string): Promise<ImageComplianceResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (brandId) formData.append('brand_id', brandId);
    if (altText !== undefined) formData.append('alt_text', altText);
    if (channel) formData.append('intended_channel', channel);

    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];

    const res = await fetch(`${API_BASE}/assets/verify-image`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to verify image compliance');
    return res.json();
  },

  async registerAsset(name: string, assetType: string, file: File, brandId?: string, usageGuideline?: string): Promise<BrandAsset> {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('asset_type', assetType);
    formData.append('file', file);
    if (brandId) formData.append('brand_id', brandId);
    if (usageGuideline) formData.append('usage_guideline', usageGuideline);

    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];

    const res = await fetch(`${API_BASE}/assets/register`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to register brand asset');
    return res.json();
  },

  // --- Content Documents ---
  async listDocuments(brandId?: string, statusFilter?: string): Promise<ContentDocument[]> {
    const q = new URLSearchParams();
    if (brandId) q.append('brand_id', brandId);
    if (statusFilter) q.append('status_filter', statusFilter);

    const res = await fetch(`${API_BASE}/documents?${q.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(id: string): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch document');
    return res.json();
  },

  async createTextDocument(title: string, raw_text: string, brandId?: string, channel: string = 'website', market: string = 'Global'): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, raw_text, content_type: 'text', brand_id: brandId, channel, market }),
    });
    if (!res.ok) throw new Error('Failed to create document');
    return res.json();
  },

  async uploadDocument(title: string, file: File, brandId?: string, channel: string = 'website', market: string = 'Global'): Promise<ContentDocument> {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);
    if (brandId) formData.append('brand_id', brandId);
    formData.append('channel', channel);
    formData.append('market', market);

    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async updateDocument(id: string, current_text: string, changelog?: string): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_text, changelog }),
    });
    if (!res.ok) throw new Error('Failed to update document');
    return res.json();
  },

  async getDocumentVersions(id: string): Promise<DocumentVersion[]> {
    const res = await fetch(`${API_BASE}/documents/${id}/versions`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch versions');
    return res.json();
  },

  async getVersionDiff(documentId: string, v1: number, v2: number) {
    const res = await fetch(`${API_BASE}/documents/${documentId}/diff?v1=${v1}&v2=${v2}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch version diff');
    return res.json();
  },

  // --- Preflight Review & Correction Studio ---
  async triggerReview(documentId: string): Promise<ReviewJob> {
    const res = await fetch(`${API_BASE}/reviews/check/${documentId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Review failed to execute');
    return res.json();
  },

  async getDocumentReviews(documentId: string): Promise<ReviewJob[]> {
    const res = await fetch(`${API_BASE}/reviews/jobs/${documentId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch reviews');
    return res.json();
  },

  async resolveFinding(findingId: string, status: string, notes?: string, customReplacement?: string, reason?: string): Promise<Finding> {
    const res = await fetch(`${API_BASE}/reviews/findings/${findingId}/resolve`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status,
        resolution_notes: notes,
        custom_replacement_text: customReplacement,
        reason
      }),
    });
    if (!res.ok) throw new Error('Failed to resolve finding');
    return res.json();
  },

  async getReviewQueue(brandId?: string, assigneeId?: string) {
    const q = new URLSearchParams();
    if (brandId) q.append('brand_id', brandId);
    if (assigneeId) q.append('assignee_id', assigneeId);

    const res = await fetch(`${API_BASE}/reviews/queue?${q.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch review queue');
    return res.json();
  },

  async assignReviewer(documentId: string, reviewerId: string) {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/assign?reviewer_id=${reviewerId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to assign reviewer');
    return res.json();
  },

  async transitionStatus(documentId: string, newStatus: string, comment?: string) {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/transition`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status: newStatus, comment }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'State transition rejected');
    }
    return res.json();
  },

  async getDocumentApprovals(documentId: string): Promise<ApprovalRecord[]> {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/approvals`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch approvals');
    return res.json();
  },

  async getComments(documentId: string): Promise<ReviewComment[]> {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/comments`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch comments');
    return res.json();
  },

  async addComment(documentId: string, commentText: string, actionType: string = 'comment'): Promise<ReviewComment> {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/comments`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment_text: commentText, action_type: actionType }),
    });
    if (!res.ok) throw new Error('Failed to post comment');
    return res.json();
  },

  // --- Guideline Clarity Radar ---
  async getClarityRadarInsights(): Promise<GuidelineInsight[]> {
    const res = await fetch(`${API_BASE}/debugger/insights`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch Clarity Radar insights');
    return res.json();
  },

  async triggerRadarClustering(): Promise<GuidelineInsight[]> {
    const res = await fetch(`${API_BASE}/debugger/cluster`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to execute clustering');
    return res.json();
  },

  async evaluateClarityInsight(insightId: string, action: string, statusMarking?: string, notes?: string): Promise<GuidelineInsight> {
    const res = await fetch(`${API_BASE}/debugger/insights/${insightId}/evaluate`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, status_marking: statusMarking, decision_notes: notes }),
    });
    if (!res.ok) throw new Error('Failed to evaluate insight');
    return res.json();
  },

  async listClarificationProposals(statusFilter: string = 'pending'): Promise<ProposedClarification[]> {
    const res = await fetch(`${API_BASE}/debugger/clarifications?status_filter=${statusFilter}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch clarification proposals');
    return res.json();
  },

  async decideClarification(proposalId: string, decision: 'approve' | 'reject', editedText?: string, notes?: string) {
    const res = await fetch(`${API_BASE}/debugger/clarifications/${proposalId}/decide`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, edited_rule_text: editedText, notes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Clarification decision failed');
    }
    return res.json();
  },

  // --- Notifications ---
  async listNotifications(unreadOnly: boolean = false): Promise<NotificationItem[]> {
    const res = await fetch(`${API_BASE}/notifications?unread_only=${unreadOnly}`, { headers: getAuthHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  async markNotificationRead(id: string) {
    await fetch(`${API_BASE}/notifications/${id}/read`, {
      method: 'PUT',
      headers: getAuthHeaders(),
    });
  },

  async markAllNotificationsRead() {
    await fetch(`${API_BASE}/notifications/read-all`, {
      method: 'PUT',
      headers: getAuthHeaders(),
    });
  },

  // --- Dashboard & Audit ---
  async getDashboardMetrics(brandId?: string): Promise<DashboardMetrics> {
    const url = brandId ? `${API_BASE}/dashboard/metrics?brand_id=${brandId}` : `${API_BASE}/dashboard/metrics`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
    return res.json();
  },

  async getAuditLogs(limit: number = 50, targetType?: string): Promise<AuditEvent[]> {
    const url = targetType
      ? `${API_BASE}/dashboard/audit-logs?limit=${limit}&target_type=${targetType}`
      : `${API_BASE}/dashboard/audit-logs?limit=${limit}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },
};
