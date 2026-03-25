/**
 * Tests for Classify Suggestions Component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClassifySuggestions } from './classify-suggestions';

// Mock the record store
const mockState = {
  content: '',
  isClassifying: false,
  classificationResult: null,
  tagSuggestions: [],
  folderSuggestion: null,
  classify: vi.fn().mockResolvedValue(undefined),
  addTag: vi.fn(),
  setFolderId: vi.fn(),
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

describe('ClassifySuggestions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState.content = '';
    mockState.isClassifying = false;
    mockState.classificationResult = null;
    mockState.tagSuggestions = [];
    mockState.folderSuggestion = null;
  });

  describe('rendering', () => {
    it('should render the classification card', () => {
      render(<ClassifySuggestions />);

      expect(screen.getByText('Classification')).toBeInTheDocument();
    });

    it('should show suggest button when no suggestions', () => {
      render(<ClassifySuggestions />);

      expect(screen.getByText('Suggest')).toBeInTheDocument();
    });

    it('should disable suggest button when no content', () => {
      mockState.content = '';

      render(<ClassifySuggestions />);

      expect(screen.getByText('Suggest')).toBeDisabled();
    });

    it('should enable suggest button when has content', () => {
      mockState.content = 'Some content';

      render(<ClassifySuggestions />);

      expect(screen.getByText('Suggest')).not.toBeDisabled();
    });

    it('should show loading state when classifying with suggestions', () => {
      mockState.isClassifying = true;
      mockState.classificationResult = {
        suggested_tags: ['tag'],
        suggested_folder: null,
        confidence: 0.8,
      };

      render(<ClassifySuggestions />);

      expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    });
  });

  describe('suggestions display', () => {
    it('should display suggested tags', () => {
      mockState.classificationResult = {
        suggested_tags: ['tag1', 'tag2'],
        suggested_folder: null,
        confidence: 0.8,
      };

      render(<ClassifySuggestions />);

      expect(screen.getByText('+tag1')).toBeInTheDocument();
      expect(screen.getByText('+tag2')).toBeInTheDocument();
    });

    it('should display suggested folder', () => {
      mockState.classificationResult = {
        suggested_tags: [],
        suggested_folder: 'folder/path',
        confidence: 0.9,
      };

      render(<ClassifySuggestions />);

      expect(screen.getByText('folder/path')).toBeInTheDocument();
    });

    it('should display tag suggestions from store', () => {
      mockState.tagSuggestions = ['suggested1'];

      render(<ClassifySuggestions />);

      expect(screen.getByText('+suggested1')).toBeInTheDocument();
    });

    it('should show re-analyze button when suggestions exist', () => {
      mockState.classificationResult = {
        suggested_tags: ['tag'],
        suggested_folder: null,
        confidence: 0.8,
      };

      render(<ClassifySuggestions />);

      expect(screen.getByText('Re-analyze')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('should call classify on suggest button click', async () => {
      const user = userEvent.setup();
      mockState.content = 'Some content';

      render(<ClassifySuggestions />);

      const suggestButton = screen.getByText('Suggest');
      await user.click(suggestButton);

      expect(mockState.classify).toHaveBeenCalled();
    });

    it('should add tag when clicked', async () => {
      const user = userEvent.setup();
      mockState.classificationResult = {
        suggested_tags: ['clickable'],
        suggested_folder: null,
        confidence: 0.8,
      };

      render(<ClassifySuggestions />);

      const tagBadge = screen.getByText('+clickable');
      await user.click(tagBadge);

      expect(mockState.addTag).toHaveBeenCalledWith('clickable');
    });

    it('should accept folder on button click', async () => {
      const user = userEvent.setup();
      mockState.folderSuggestion = {
        folder: 'accepted-folder',
        confidence: 0.9,
      };

      render(<ClassifySuggestions />);

      const acceptButton = screen.getByText('Accept');
      await user.click(acceptButton);

      expect(mockState.setFolderId).toHaveBeenCalledWith('accepted-folder');
    });
  });
});