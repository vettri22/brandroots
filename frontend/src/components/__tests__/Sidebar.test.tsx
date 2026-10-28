import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../Sidebar';

describe('Sidebar Navigation', () => {
  it('renders all key Proofline governance workflows', () => {
    const handleTabChange = vi.fn();
    render(<Sidebar currentTab="dashboard" onTabChange={handleTabChange} />);

    expect(screen.getByText('Governance Hub')).toBeDefined();
    expect(screen.getByText('Preflight Workbench')).toBeDefined();
    expect(screen.getByText('Review Queue')).toBeDefined();
    expect(screen.getByText('Brand Evidence Ledger')).toBeDefined();
    expect(screen.getByText('Guideline Clarity Radar')).toBeDefined();
    expect(screen.getByText('Brand Guidelines')).toBeDefined();
    expect(screen.getByText('Approved Asset Library')).toBeDefined();
    expect(screen.getByText('Team & RBAC')).toBeDefined();
    expect(screen.getByText('Audit Trail')).toBeDefined();
  });

  it('triggers onTabChange when navigation item is clicked', () => {
    const handleTabChange = vi.fn();
    render(<Sidebar currentTab="dashboard" onTabChange={handleTabChange} />);

    const evidenceButton = screen.getByText('Brand Evidence Ledger');
    fireEvent.click(evidenceButton);

    expect(handleTabChange).toHaveBeenCalledWith('evidence');
  });
});
