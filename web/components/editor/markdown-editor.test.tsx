/**
 * Tests for Markdown Editor Component
 *
 * Tests the markdown editor with toolbar and content management.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MarkdownEditor } from './markdown-editor';

// Mock the record store
const mockStore = {
  content: '',
  title: '',
  tags: [],
  isStreaming: false,
  setContent: vi.fn(),
  setTitle: vi.fn(),
};

vi.mock('@/lib/record-store', () => ({
  useRecordStore: vi.fn((selector) => {
    if (typeof selector === 'function') {
      return selector(mockStore);
    }
    return mockStore;
  }),
}));

describe('MarkdownEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.content = '';
    mockStore.title = '';
    mockStore.tags = [];
    mockStore.isStreaming = false;
  });

  describe('rendering', () => {
    it('should render the editor textarea', () => {
      render(<MarkdownEditor />);

      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should render the toolbar', () => {
      render(<MarkdownEditor />);

      expect(screen.getByLabelText('Bold')).toBeInTheDocument();
      expect(screen.getByLabelText('Italic')).toBeInTheDocument();
      expect(screen.getByLabelText('Heading')).toBeInTheDocument();
      expect(screen.getByLabelText('Link')).toBeInTheDocument();
      expect(screen.getByLabelText('Code')).toBeInTheDocument();
    });

    it('should display current content from store', () => {
      mockStore.content = '# Existing content';

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveValue('# Existing content');
    });

    it('should be disabled when streaming', () => {
      mockStore.isStreaming = true;

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeDisabled();
    });
  });

  describe('content editing', () => {
    it('should call setContent when content changes', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'New content');

      expect(mockStore.setContent).toHaveBeenCalled();
    });

    it('should handle empty content', async () => {
      const user = userEvent.setup();
      mockStore.content = 'Existing';

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      await user.clear(textarea);

      expect(mockStore.setContent).toHaveBeenCalledWith('');
    });
  });

  describe('toolbar actions', () => {
    it('should insert bold formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const boldButton = screen.getByLabelText('Bold');
      await user.click(boldButton);

      // Should call setContent with bold formatting
      expect(mockStore.setContent).toHaveBeenCalledWith('****');
    });

    it('should insert italic formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const italicButton = screen.getByLabelText('Italic');
      await user.click(italicButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('__');
    });

    it('should insert heading formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const headingButton = screen.getByLabelText('Heading');
      await user.click(headingButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('# ');
    });

    it('should insert link formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const linkButton = screen.getByLabelText('Link');
      await user.click(linkButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('[](url)');
    });

    it('should insert code formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const codeButton = screen.getByLabelText('Code');
      await user.click(codeButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('``');
    });

    it('should insert code block formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const codeBlockButton = screen.getByLabelText('Code block');
      await user.click(codeBlockButton);

      // Should call setContent with code block formatting
      const calls = mockStore.setContent.mock.calls;
      expect(calls.length).toBeGreaterThan(0);
      expect(calls[0][0]).toContain('```');
    });

    it('should insert wikilink formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const wikilinkButton = screen.getByLabelText('Wikilink');
      await user.click(wikilinkButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('[[]]');
    });

    it('should insert callout formatting', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const calloutButton = screen.getByLabelText('Callout');
      await user.click(calloutButton);

      expect(mockStore.setContent).toHaveBeenCalledWith('> [!note]\n> ');
    });
  });

  describe('keyboard shortcuts', () => {
    it('should handle Ctrl+B for bold', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      textarea.focus();

      await user.keyboard('{Control>}b{/Control}');

      expect(mockStore.setContent).toHaveBeenCalled();
    });

    it('should handle Ctrl+I for italic', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      textarea.focus();

      await user.keyboard('{Control>}i{/Control}');

      expect(mockStore.setContent).toHaveBeenCalled();
    });

    it('should handle Ctrl+K for link', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox');
      textarea.focus();

      await user.keyboard('{Control>}k{/Control}');

      expect(mockStore.setContent).toHaveBeenCalled();
    });
  });

  describe('selection handling', () => {
    it('should wrap selected text with formatting', async () => {
      mockStore.content = 'Hello world';

      render(<MarkdownEditor />);

      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      // Simulate selection
      fireEvent.select(textarea, {
        target: {
          selectionStart: 0,
          selectionEnd: 5,
        },
      });

      const boldButton = screen.getByLabelText('Bold');
      fireEvent.click(boldButton);

      // Should wrap "Hello" with bold
      expect(mockStore.setContent).toHaveBeenCalledWith('**Hello** world');
    });
  });

  describe('accessibility', () => {
    it('should have accessible toolbar buttons', () => {
      render(<MarkdownEditor />);

      expect(screen.getByRole('button', { name: 'Bold' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Italic' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Heading' })).toBeInTheDocument();
    });

    it('should have tooltip descriptions', () => {
      render(<MarkdownEditor />);

      // Tooltips are rendered on hover, check that buttons exist with aria-labels
      expect(screen.getByLabelText('Bold')).toBeInTheDocument();
      expect(screen.getByLabelText('Italic')).toBeInTheDocument();
    });
  });

  describe('Obsidian syntax support', () => {
    it('should support wikilink button', () => {
      render(<MarkdownEditor />);

      expect(screen.getByLabelText('Wikilink')).toBeInTheDocument();
    });

    it('should support callout button', () => {
      render(<MarkdownEditor />);

      expect(screen.getByLabelText('Callout')).toBeInTheDocument();
    });

    it('should show callout type selector', async () => {
      const user = userEvent.setup();

      render(<MarkdownEditor />);

      const calloutButton = screen.getByLabelText('Callout');
      await user.click(calloutButton);

      // Should insert note callout by default
      expect(mockStore.setContent).toHaveBeenCalledWith('> [!note]\n> ');
    });
  });
});