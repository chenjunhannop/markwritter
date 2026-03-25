/**
 * Tests for Quick Record Component
 *
 * Tests the quick record interface for fast note creation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QuickRecord } from './quick-record';

// Mock the record store
const mockState = {
  content: '',
  currentRecord: null,
  isSaving: false,
  saveError: null,
  setContent: vi.fn(),
  saveRecord: vi.fn().mockResolvedValue(undefined),
  clearRecord: vi.fn(),
};

vi.mock('@/lib/record-store', () => ({
  useRecordStore: Object.assign(
    vi.fn((selector) => {
      if (typeof selector === 'function') {
        return selector(mockState);
      }
      return mockState;
    }),
    {
      getState: () => mockState,
    }
  ),
}));

// Mock router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('QuickRecord', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState.content = '';
    mockState.currentRecord = null;
    mockState.isSaving = false;
    mockState.saveError = null;
  });

  describe('rendering', () => {
    it('should render the quick record input', () => {
      render(<QuickRecord />);

      expect(screen.getByPlaceholderText(/quick note/i)).toBeInTheDocument();
    });

    it('should render the submit button', () => {
      render(<QuickRecord />);

      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    });

    it('should show saving state', () => {
      mockState.isSaving = true;

      render(<QuickRecord />);

      expect(screen.getByText(/saving/i)).toBeInTheDocument();
    });

    it('should show error message', () => {
      mockState.saveError = 'Failed to save';

      render(<QuickRecord />);

      expect(screen.getByText('Failed to save')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('should update content on input', async () => {
      const user = userEvent.setup();

      render(<QuickRecord />);

      const input = screen.getByPlaceholderText(/quick note/i);
      await user.type(input, 'New note');

      expect(mockState.setContent).toHaveBeenCalled();
    });

    it('should save on form submit', async () => {
      const user = userEvent.setup();
      mockState.content = 'Test note';

      render(<QuickRecord />);

      const button = screen.getByRole('button', { name: /save/i });
      await user.click(button);

      expect(mockState.saveRecord).toHaveBeenCalled();
    });

    it('should clear form after save', async () => {
      const user = userEvent.setup();
      mockState.content = 'Test note';
      mockState.currentRecord = {
        id: 'record-1',
        title: 'Test',
        content: 'Test note',
        folder_id: null,
        tags: [],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      render(<QuickRecord redirectAfterSave={false} />);

      const button = screen.getByRole('button', { name: /save/i });
      await user.click(button);

      expect(mockState.saveRecord).toHaveBeenCalled();
    });

    it('should disable submit when empty', () => {
      mockState.content = '';

      render(<QuickRecord />);

      const button = screen.getByRole('button', { name: /save/i });
      expect(button).toBeDisabled();
    });

    it('should enable submit when has content', () => {
      mockState.content = 'Some content';

      render(<QuickRecord />);

      const button = screen.getByRole('button', { name: /save/i });
      expect(button).not.toBeDisabled();
    });
  });

  describe('keyboard shortcuts', () => {
    it('should submit on Ctrl+Enter', async () => {
      const user = userEvent.setup();
      mockState.content = 'Test note';

      render(<QuickRecord />);

      const input = screen.getByPlaceholderText(/quick note/i);
      input.focus();

      await user.keyboard('{Control>}{Enter}{/Control}');

      expect(mockState.saveRecord).toHaveBeenCalled();
    });
  });

  describe('accessibility', () => {
    it('should have accessible form', () => {
      render(<QuickRecord />);

      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should have accessible textarea', () => {
      render(<QuickRecord />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();
    });
  });
});