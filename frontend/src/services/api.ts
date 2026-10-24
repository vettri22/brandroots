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
  DashboardMetrics,
  AuditEvent,
  UserRole
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('brandroots_token');
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    localStorage.setItem('brandroots_token', data.access_token);
    return data;
  },

  async switchRole(role: UserRole) {
    const res = await fetch(`${API_BASE}/auth/switch-demo-role?role=${role}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Failed to switch role');
    const data = await res.json();
    localStorage.setItem('brandroots_token', data.access_token);
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch user');
    return res.json();
  },

  // Documents
  async listDocuments(statusFilter?: string): Promise<ContentDocument[]> {
    const url = statusFilter
      ? `${API_BASE}/documents?status_filter=${statusFilter}`
      : `${API_BASE}/documents`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(id: string): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch document');
    return res.json();
  },

  async createTextDocument(title: string, raw_text: string): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, raw_text, content_type: 'text' }),
    });
    if (!res.ok) throw new Error('Failed to create document');
    return res.json();
  },

  async uploadDocument(title: string, file: File): Promise<ContentDocument> {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);

    const token = localStorage.getItem('brandroots_token');
    const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async updateDocumentText(id: string, current_text: string, changelog?: string): Promise<ContentDocument> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_text, changelog }),
    });
    if (!res.ok) throw new Error('Failed to update document');
    return res.json();
  },

  async getDocumentVersions(id: string): Promise<DocumentVersion[]> {
    const res = await fetch(`${API_BASE}/documents/${id}/versions`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch versions');
    return res.json();
  },

  // Reviews
  async triggerReview(documentId: string): Promise<ReviewJob> {
    const res = await fetch(`${API_BASE}/reviews/check/${documentId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to run compliance check');
    return res.json();
  },

  async getDocumentReviewJobs(documentId: string): Promise<ReviewJob[]> {
    const res = await fetch(`${API_BASE}/reviews/jobs/${documentId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch review jobs');
    return res.json();
  },

  async resolveFinding(
    findingId: string,
    status: 'accepted' | 'edited' | 'dismissed' | 'escalated',
    resolution_notes?: string,
    custom_replacement_text?: string
  ): Promise<Finding> {
    const res = await fetch(`${API_BASE}/reviews/findings/${findingId}/resolve`, {
      method: 'PUT',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, resolution_notes, custom_replacement_text }),
    });
    if (!res.ok) throw new Error('Failed to resolve finding');
    return res.json();
  },

  async transitionStatus(documentId: string, new_status: string, comment?: string) {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/transition`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status, comment }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Status transition denied');
    }
    return res.json();
  },

  async getComments(documentId: string): Promise<ReviewComment[]> {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/comments`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch comments');
    return res.json();
  },

  async addComment(documentId: string, comment_text: string, action_type: string = 'comment'): Promise<ReviewComment> {
    const res = await fetch(`${API_BASE}/reviews/documents/${documentId}/comments`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment_text, action_type }),
    });
    if (!res.ok) throw new Error('Failed to post comment');
    return res.json();
  },

  // Guideline Debugger (Signature Feature)
  async clusterDebugger(): Promise<GuidelineInsight[]> {
    const res = await fetch(`${API_BASE}/debugger/cluster`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to cluster debugger findings');
    return res.json();
  },

  async getDebuggerInsights(): Promise<GuidelineInsight[]> {
    const res = await fetch(`${API_BASE}/debugger/insights`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch debugger insights');
    return res.json();
  },

  async evaluateHypothesis(insightId: string, action: 'confirm' | 'dismiss', decision_notes?: string): Promise<GuidelineInsight> {
    const res = await fetch(`${API_BASE}/debugger/insights/${insightId}/evaluate`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, decision_notes }),
    });
    if (!res.ok) throw new Error('Failed to evaluate hypothesis');
    return res.json();
  },

  async getProposedClarifications(): Promise<ProposedClarification[]> {
    const res = await fetch(`${API_BASE}/debugger/clarifications?status_filter=all`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch clarifications');
    return res.json();
  },

  async decideClarification(proposalId: string, decision: 'approve' | 'reject', edited_rule_text?: string, notes?: string) {
    const res = await fetch(`${API_BASE}/debugger/clarifications/${proposalId}/decide`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, edited_rule_text, notes }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Permission denied. Only Brand Owner can approve guideline changes.');
    }
    return res.json();
  },

  // Brand Knowledge
  async getGuidelines(): Promise<BrandGuideline[]> {
    const res = await fetch(`${API_BASE}/brand/guidelines`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch guidelines');
    return res.json();
  },

  async getFacts(): Promise<ApprovedFact[]> {
    const res = await fetch(`${API_BASE}/brand/facts`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch facts');
    return res.json();
  },

  async getTerminology(): Promise<ApprovedTerminology[]> {
    const res = await fetch(`${API_BASE}/brand/terminology`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch terminology');
    return res.json();
  },

  // Dashboard & Audit
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const res = await fetch(`${API_BASE}/dashboard/metrics`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },

  async getAuditLogs(): Promise<AuditEvent[]> {
    const res = await fetch(`${API_BASE}/dashboard/audit-logs`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  async resetDemoData() {
    const res = await fetch(`${API_BASE}/seed/reset-demo`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  }
};
