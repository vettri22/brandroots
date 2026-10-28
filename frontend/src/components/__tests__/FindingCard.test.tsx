import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FindingCard } from '../FindingCard';
import { Finding } from '../../types';

describe('FindingCard Component', () => {
  const mockFinding: Finding = {
    id: 'f-test-01',
    review_job_id: 'job-01',
    rule_id: 'RULE-CLAIM-01',
    rule_version: 1,
    category: 'claim_restriction',
    severity: 'critical',
    affected_text: '100% cure guaranteed in all cases',
    suggested_correction: 'clinically observed to support metabolic recovery in Phase 2 trials',
    explanation: 'Absolute outcome guarantees violate compliance standards and lack substantiating evidence.',
    source_reference: 'Brand Compliance Playbook §4.1',
    confidence: 'HIGH',
    status: 'open',
    location_start: 0,
    location_end: 32,
    created_at: new Date().toISOString(),
  };

  it('renders severity, flagged passage, and suggested correction', () => {
    const handleResolve = vi.fn();
    render(<FindingCard finding={mockFinding} onResolve={handleResolve} />);

    expect(screen.getByText('CRITICAL')).toBeDefined();
    expect(screen.getByText('"100% cure guaranteed in all cases"')).toBeDefined();
    expect(screen.getByText('clinically observed to support metabolic recovery in Phase 2 trials')).toBeDefined();
    expect(screen.getByText(/RULE-CLAIM-01/)).toBeDefined();
  });

  it('calls onResolve with accepted when user clicks Accept Suggestion', () => {
    const handleResolve = vi.fn();
    render(<FindingCard finding={mockFinding} onResolve={handleResolve} />);

    const acceptBtn = screen.getByText('Accept Suggestion');
    fireEvent.click(acceptBtn);

    expect(handleResolve).toHaveBeenCalledWith('accepted', 'Applied canonical brand correction');
  });

  it('renders dismiss confirmation form when user clicks Dismiss', () => {
    const handleResolve = vi.fn();
    render(<FindingCard finding={mockFinding} onResolve={handleResolve} />);

    const dismissBtn = screen.getByText('Dismiss');
    fireEvent.click(dismissBtn);

    expect(screen.getByPlaceholderText(/e\.g\. Approved clinical trial exception/)).toBeDefined();
    expect(screen.getByText('Confirm Dismissal')).toBeDefined();
  });
});
