import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Badge } from '../Badge';

describe('Badge Component', () => {
  it('renders critical badge correctly', () => {
    render(<Badge variant="critical">CRITICAL VIOLATION</Badge>);
    expect(screen.getByText('CRITICAL VIOLATION')).toBeDefined();
  });

  it('renders teal badge correctly', () => {
    render(<Badge variant="teal">APPROVED v2</Badge>);
    expect(screen.getByText('APPROVED v2')).toBeDefined();
  });
});
