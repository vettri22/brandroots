export type UserRole = 'creator' | 'reviewer' | 'brand_owner' | 'brand_admin' | 'org_owner' | 'read_only';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  workspace_id?: string;
  organization_id?: string;
  avatar_url?: string;
  is_active?: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface OrganizationMembership {
  id: string;
  organization_id: string;
  user_id: string;
  role: string;
  created_at: string;
  user?: User;
  user_email?: string;
  user_name?: string;
}

export interface Brand {
  id: string;
  workspace_id: string;
  name: string;
  slug: string;
  description?: string;
  website?: string;
  supported_channels: string[];
  supported_markets: string[];
  content_types: string[];
  tone_guidelines: Record<string, any>;
  claim_restrictions: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BrandEvidence {
  id: string;
  workspace_id: string;
  brand_id?: string;
  claim_title: string;
  approved_wording: string;
  structured_value?: string;
  unit?: string;
  prohibited_old_values: string[];
  category: string;
  description?: string;
  applicable_context?: string;
  source_type: string;
  source_location?: string;
  source_url?: string;
  source_document_id?: string;
  page_or_section?: string;
  evidence_owner: string;
  status: 'draft' | 'pending_review' | 'approved' | 'rejected' | 'expired' | 'archived';
  approval_date?: string;
  approved_by?: string;
  effective_date?: string;
  expiry_date?: string;
  review_date?: string;
  applicable_product?: string;
  applicable_market?: string;
  applicable_channel?: string;
  public_use_permission: boolean;
  version: number;
  is_active: boolean;
  is_expired?: boolean;
  created_at: string;
  updated_at: string;
}

export interface BrandGuideline {
  id: string;
  brand_id?: string;
  category: string;
  title: string;
  rule_text: string;
  rule_type?: string;
  severity: 'critical' | 'warning' | 'suggestion';
  owner_role: string;
  source_reference?: string;
  page_reference?: string;
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

export interface BrandAsset {
  id: string;
  asset_type: string;
  name: string;
  value: string;
  file_path?: string;
  sha256_hash?: string;
  file_hash?: string;
  mime_type?: string;
  width?: number;
  height?: number;
  min_width?: number;
  min_height?: number;
  color_hex?: string;
  alt_text_required: boolean;
  usage_guideline?: string;
  is_active: boolean;
  is_approved?: boolean;
  created_at: string;
}

export interface ImageComplianceResult {
  is_compliant: boolean;
  file_type: string;
  width: number;
  height: number;
  file_size_bytes: number;
  sha256_hash: string;
  exact_match_asset?: Record<string, any>;
  similarity_match?: Record<string, any>;
  matching_asset_id?: string;
  is_exact_sha256_match?: boolean;
  contrast_ratio?: number;
  contrast_status: string;
  alt_text_status: string;
  alt_text_valid?: boolean;
  findings: Array<Record<string, any>>;
  violations?: string[];
  details: string;
}

export type DocumentStatus =
  | 'draft'
  | 'submitted'
  | 'in_review'
  | 'changes_requested'
  | 'resubmitted'
  | 'approved'
  | 'rejected'
  | 'archived';

export interface ContentDocument {
  id: string;
  workspace_id: string;
  organization_id?: string;
  brand_id?: string;
  title: string;
  content_type: string;
  channel?: string;
  market?: string;
  original_filename?: string;
  raw_text: string;
  current_text: string;
  status: DocumentStatus;
  creator_id: string;
  creator_name: string;
  assigned_reviewer_id?: string;
  assigned_reviewer_name?: string;
  current_version: number;
  approved_version?: number;
  approved_at?: string;
  approved_by_name?: string;
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
  author_name?: string;
  created_at: string;
}

export interface Finding {
  id: string;
  review_job_id: string;
  category: string;
  severity: 'critical' | 'high' | 'warning' | 'medium' | 'low' | 'suggestion';
  confidence: string;
  detection_method?: string;
  location_start: number;
  location_end: number;
  affected_text: string;
  explanation: string;
  rule_id?: string;
  rule_version: number;
  evidence_ids?: string[];
  source_reference?: string;
  suggested_correction?: string;
  status: 'open' | 'accepted' | 'edited' | 'dismissed' | 'rejected' | 'escalated';
  creator_decision?: string;
  creator_decision_reason?: string;
  reviewer_decision?: string;
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
  evidence_snapshot?: Record<string, number>;
  provider_used: string;
  model_name?: string;
  execution_duration_ms?: number;
  risk_level?: string;
  requires_human_review?: boolean;
  created_at: string;
  completed_at?: string;
  findings: Finding[];
}

export interface ReviewComment {
  id: string;
  document_id: string;
  document_version: number;
  user_id: string;
  user_name: string;
  user_role: string;
  comment_text: string;
  action_type: string;
  created_at: string;
}

export interface ApprovalRecord {
  id: string;
  document_id: string;
  document_version: number;
  review_job_id: string;
  status: string;
  approver_id: string;
  approver_name: string;
  approver_role: string;
  decision_reason?: string;
  created_at: string;
}

export interface GuidelineInsight {
  id: string;
  workspace_id: string;
  organization_id?: string;
  brand_id?: string;
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
  status_marking: 'under_investigation' | 'needs_clarification' | 'updated' | 'resolved' | 'not_an_issue';
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

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  reference_type?: string;
  reference_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface DashboardMetrics {
  data_mode: string;
  is_empty?: boolean;
  total_documents: number;
  pending_reviews: number;
  completed_reviews: number;
  approved_documents: number;
  changes_requested_documents: number;
  rejected_documents: number;
  approvals_recorded: number;
  average_compliance_score: number;
  unresolved_high_severity: number;
  findings_by_severity: {
    critical: number;
    warning: number;
    suggestion: number;
  };
  findings_by_category: Record<string, number>;
  top_recurring_violations: Array<{ rule_id: string; title?: string; count: number }>;
  expired_evidence_count: number;
  repeated_overrides_count: number;
  guideline_clarity_signals_count: number;
  guideline_ambiguity_candidates?: number;
  active_guidelines_count: number;
  active_evidence_count: number;
  active_facts_count?: number;
}

export interface AuditEvent {
  id: string;
  workspace_id: string;
  organization_id?: string;
  brand_id?: string;
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
