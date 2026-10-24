export type UserRole = 'creator' | 'reviewer' | 'brand_owner';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  workspace_id?: string;
  created_at: string;
}

export interface BrandGuideline {
  id: string;
  category: string;
  title: string;
  rule_text: string;
  severity: 'critical' | 'warning' | 'suggestion';
  owner_role: string;
  source_reference?: string;
  effective_date?: string;
  version: number;
  is_active: boolean;
  prohibited_patterns: string[];
  required_phrases: string[];
  clarification_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ApprovedFact {
  id: string;
  category: string;
  claim_statement: string;
  canonical_value?: string;
  unit?: string;
  prohibited_old_values: string[];
  source_document: string;
  version: number;
  effective_date: string;
  expiry_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApprovedTerminology {
  id: string;
  preferred_term: string;
  prohibited_variants: string[];
  rationale: string;
  context_guidance?: string;
  version: number;
  is_active: boolean;
  created_at: string;
}

export type DocumentStatus =
  | 'draft'
  | 'submitted'
  | 'in_review'
  | 'changes_requested'
  | 'resubmitted'
  | 'approved'
  | 'rejected';

export interface ContentDocument {
  id: string;
  workspace_id: string;
  title: string;
  content_type: string;
  original_filename?: string;
  raw_text: string;
  current_text: string;
  status: DocumentStatus;
  creator_id: string;
  creator_name: string;
  assigned_reviewer_id?: string;
  current_version: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  text_snapshot: string;
  changelog?: string;
  author_id: string;
  created_at: string;
}

export interface Finding {
  id: string;
  review_job_id: string;
  category: string;
  severity: 'critical' | 'high' | 'warning' | 'medium' | 'low' | 'suggestion';
  confidence: string;
  location_start: number;
  location_end: number;
  affected_text: string;
  explanation: string;
  rule_id?: string;
  rule_version: number;
  source_reference?: string;
  suggested_correction?: string;
  status: 'open' | 'accepted' | 'edited' | 'dismissed' | 'escalated';
  resolution_notes?: string;
  resolved_by?: string;
  resolved_at?: string;
  created_at: string;
}

export interface ReviewJob {
  id: string;
  document_id: string;
  document_version: number;
  status: string;
  compliance_score: number;
  findings_count: number;
  critical_count: number;
  warning_count: number;
  suggestion_count: number;
  guideline_snapshot: Record<string, number>;
  provider_used: string;
  created_at: string;
  completed_at?: string;
  findings: Finding[];
}

export interface ReviewComment {
  id: string;
  document_id: string;
  user_id: string;
  user_name: string;
  user_role: string;
  comment_text: string;
  action_type: string;
  created_at: string;
}

export interface GuidelineInsight {
  id: string;
  workspace_id: string;
  title: string;
  rule_id?: string;
  suspected_root_cause: string;
  pattern_type: string;
  occurrence_count: number;
  supporting_finding_ids: string[];
  supporting_document_ids: string[];
  evidence_summary: string;
  suggested_action: string;
  hypothesis_status: 'hypothesis' | 'confirmed' | 'dismissed';
  decision_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ProposedClarification {
  id: string;
  insight_id?: string;
  target_rule_id: string;
  current_rule_version: number;
  proposed_version: number;
  original_rule_text: string;
  proposed_rule_text: string;
  clarification_summary: string;
  proposing_actor: string;
  approval_status: 'pending' | 'approved' | 'rejected';
  reviewer_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface DashboardMetrics {
  data_mode: string;
  pending_reviews: number;
  total_documents: number;
  approved_documents: number;
  findings_by_severity: {
    critical: number;
    warning: number;
    suggestion: number;
  };
  findings_by_category: Record<string, number>;
  top_recurring_violations: Array<{ rule_id: string; count: number }>;
  guideline_ambiguity_candidates: number;
  active_guidelines_count: number;
  active_facts_count: number;
}

export interface AuditEvent {
  id: string;
  workspace_id: string;
  event_type: string;
  actor_id: string;
  actor_name: string;
  actor_role: string;
  target_type: string;
  target_id: string;
  summary: string;
  details: Record<string, any>;
  timestamp: string;
}
