/**
 * Tests for AI Assist Panel Component
 *
 * Tests the AI assistance panel with continue, rewrite, polish buttons.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AIAssistPanel } from './ai-assist-panel';

// Mock the record store
const mockStore = {
  currentRecord: null,
  content: '',
  isStreaming: false,
  streamError: null,
  aiContinue: vi.fn(),
  aiRewrite: vi.fn(),
  aiPolish: vi.fn(),
  aiRewriteWithDiff: vi.fn(),
  aiPolishWithDiff: vi.fn(),
  cancelStream: vi.fn(),
  showDiffPreview: false,
  diffResult: null,
  baseContent: null,
  generatedContent: null,
  acceptDiff: vi.fn(),
  rejectDiff: vi.fn(),
  undoLastAccept: vi.fn(),
  canUndo: false,
};

vi.mock('@/lib/record-store', () => ({
  useRecordStore: vi.fn((selector) => {
    if (typeof selector === 'function') {
      return selector(mockStore);
    }
    return mockStore;
  }),
}));

function createMockCurrentRecord(): import('@/lib/record-api').NoteResponse {
  return {
    path: 'note-1.md',
    title: 'Test',
    content: 'Some content',
    metadata: {},
    tags: [],
    links: [],
    backlinks: [],
  };
}

describe('AIAssistPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.currentRecord = null;
    mockStore.content = '';
    mockStore.isStreaming = false;
    mockStore.streamError = null;
  });

  describe('rendering', () => {
    it('should render all AI assistance buttons', () => {
      render(<AIAssistPanel />);

      expect(screen.getByText('Continue')).toBeInTheDocument();
      expect(screen.getByText('Rewrite')).toBeInTheDocument();
      expect(screen.getByText('Polish')).toBeInTheDocument();
    });

    it('should show disabled buttons when no record', () => {
      render(<AIAssistPanel />);

      expect(screen.getByText('Continue')).toBeDisabled();
      expect(screen.getByText('Rewrite')).toBeDisabled();
      expect(screen.getByText('Polish')).toBeDisabled();
    });

    it('should enable buttons when record exists', () => {
      mockStore.currentRecord = createMockCurrentRecord();
      mockStore.content = 'Some content';

      render(<AIAssistPanel />);

      expect(screen.getByText('Continue')).not.toBeDisabled();
      expect(screen.getByText('Rewrite')).not.toBeDisabled();
      expect(screen.getByText('Polish')).not.toBeDisabled();
    });

    it('should show streaming state', () => {
      mockStore.isStreaming = true;
      mockStore.currentRecord = createMockCurrentRecord();

      render(<AIAssistPanel />);

      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('should show error message', () => {
      mockStore.streamError = 'AI service unavailable';

      render(<AIAssistPanel />);

      expect(screen.getByText('AI service unavailable')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    beforeEach(() => {
      mockStore.currentRecord = createMockCurrentRecord();
      mockStore.content = 'Some content';
    });

    it('should call aiContinue when Continue button clicked', async () => {
      const user = userEvent.setup();

      render(<AIAssistPanel />);

      const continueButton = screen.getByText('Continue');
      await user.click(continueButton);

      expect(mockStore.aiContinue).toHaveBeenCalled();
    });

    it('should call aiRewrite when Rewrite button clicked', async () => {
      const user = userEvent.setup();

      render(<AIAssistPanel />);

      const rewriteButton = screen.getByText('Rewrite');
      await user.click(rewriteButton);

      expect(mockStore.aiRewriteWithDiff).toHaveBeenCalled();
    });

    it('should call aiPolish when Polish button clicked', async () => {
      const user = userEvent.setup();

      render(<AIAssistPanel />);

      const polishButton = screen.getByText('Polish');
      await user.click(polishButton);

      expect(mockStore.aiPolishWithDiff).toHaveBeenCalled();
    });

    it('should call cancelStream when Cancel button clicked during streaming', async () => {
      const user = userEvent.setup();
      mockStore.isStreaming = true;

      render(<AIAssistPanel />);

      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(mockStore.cancelStream).toHaveBeenCalled();
    });

    it('should disable buttons when content is empty', () => {
      mockStore.content = '';

      render(<AIAssistPanel />);

      // All buttons disabled when content is empty
      expect(screen.getByText('Continue')).toBeDisabled();
      // Rewrite and Polish need content
      expect(screen.getByText('Rewrite')).toBeDisabled();
      expect(screen.getByText('Polish')).toBeDisabled();
    });
  });

  describe('accessibility', () => {
    it('should have accessible buttons', () => {
      render(<AIAssistPanel />);

      expect(screen.getByRole('button', { name: /continue/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /rewrite/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /polish/i })).toBeInTheDocument();
    });

    it('should have descriptive labels', () => {
      render(<AIAssistPanel />);

      expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    });
  });
});
