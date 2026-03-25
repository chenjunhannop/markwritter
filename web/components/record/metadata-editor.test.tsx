/**
 * Tests for Metadata Editor Component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MetadataEditor } from './metadata-editor';

// Mock the record store
const mockState = {
  title: '',
  tags: [],
  aliases: [],
  setTitle: vi.fn(),
  addTag: vi.fn(),
  removeTag: vi.fn(),
  setAliases: vi.fn(),
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

describe('MetadataEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState.title = '';
    mockState.tags = [];
    mockState.aliases = [];
  });

  describe('rendering', () => {
    it('should render title input', () => {
      render(<MetadataEditor />);

      expect(screen.getByLabelText('Title')).toBeInTheDocument();
    });

    it('should render tags section', () => {
      render(<MetadataEditor />);

      expect(screen.getByLabelText('Tags')).toBeInTheDocument();
    });

    it('should render aliases section', () => {
      render(<MetadataEditor />);

      expect(screen.getByLabelText('Aliases')).toBeInTheDocument();
    });

    it('should display existing title', () => {
      mockState.title = 'Existing Title';

      render(<MetadataEditor />);

      expect(screen.getByDisplayValue('Existing Title')).toBeInTheDocument();
    });

    it('should display existing tags', () => {
      mockState.tags = ['tag1', 'tag2'];

      render(<MetadataEditor />);

      expect(screen.getByText('#tag1')).toBeInTheDocument();
      expect(screen.getByText('#tag2')).toBeInTheDocument();
    });

    it('should display existing aliases', () => {
      mockState.aliases = ['alias1'];

      render(<MetadataEditor />);

      expect(screen.getByText('alias1')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('should update title on change', async () => {
      const user = userEvent.setup();

      render(<MetadataEditor />);

      const titleInput = screen.getByLabelText('Title');
      await user.type(titleInput, 'New Title');

      expect(mockState.setTitle).toHaveBeenCalled();
    });

    it('should add tag on button click', async () => {
      const user = userEvent.setup();

      render(<MetadataEditor />);

      const tagInput = screen.getByPlaceholderText('Add tag');
      await user.type(tagInput, 'new-tag');

      // Find the first add button (for tags)
      const addButtons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('svg') && !btn.getAttribute('aria-label')
      );
      await user.click(addButtons[0]);

      expect(mockState.addTag).toHaveBeenCalledWith('new-tag');
    });

    it('should add tag on Enter key', async () => {
      const user = userEvent.setup();

      render(<MetadataEditor />);

      const tagInput = screen.getByPlaceholderText('Add tag');
      await user.type(tagInput, 'new-tag{Enter}');

      expect(mockState.addTag).toHaveBeenCalledWith('new-tag');
    });

    it('should remove tag on click', async () => {
      const user = userEvent.setup();
      mockState.tags = ['removable'];

      render(<MetadataEditor />);

      const removeButton = screen.getByLabelText('Remove tag removable');
      await user.click(removeButton);

      expect(mockState.removeTag).toHaveBeenCalledWith('removable');
    });

    it('should add alias on button click', async () => {
      const user = userEvent.setup();

      render(<MetadataEditor />);

      const aliasInput = screen.getByPlaceholderText('Add alias');
      await user.type(aliasInput, 'new-alias');

      // Find the second add button (for aliases)
      const addButtons = screen.getAllByRole('button', { name: '' });
      await user.click(addButtons[1]);

      expect(mockState.setAliases).toHaveBeenCalled();
    });

    it('should remove alias on click', async () => {
      const user = userEvent.setup();
      mockState.aliases = ['removable-alias'];

      render(<MetadataEditor />);

      const removeButton = screen.getByLabelText('Remove alias removable-alias');
      await user.click(removeButton);

      expect(mockState.setAliases).toHaveBeenCalledWith([]);
    });

    it('should not add empty tag', async () => {
      const user = userEvent.setup();

      render(<MetadataEditor />);

      // Find the first add button (for tags) without typing anything
      const addButtons = screen.getAllByRole('button').filter(
        (btn) => btn.querySelector('svg') && !btn.getAttribute('aria-label')
      );
      await user.click(addButtons[0]);

      expect(mockState.addTag).not.toHaveBeenCalled();
    });
  });
});