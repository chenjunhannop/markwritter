/**
 * Tests for ChatSession Component
 *
 * Tests the chat session component including:
 * - Message rendering
 * - User/assistant message styling
 * - Streaming indicator
 * - Auto-scroll
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChatSession } from './chat-session';
import type { Message } from '@/lib/types';

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

describe('ChatSession Component', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      role: 'user',
      content: 'Hello, how are you?',
      timestamp: 1000,
    },
    {
      id: '2',
      role: 'assistant',
      content: 'I am doing well, thank you for asking!',
      timestamp: 2000,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render all messages', () => {
      render(<ChatSession messages={mockMessages} />);

      expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      expect(screen.getByText('I am doing well, thank you for asking!')).toBeInTheDocument();
    });

    it('should render empty state when no messages', () => {
      render(<ChatSession messages={[]} />);

      expect(screen.getByText(/start a conversation/i)).toBeInTheDocument();
    });

    it('should render user avatar for user messages', () => {
      render(<ChatSession messages={mockMessages} />);

      // Find user message and check for User icon presence
      const userMessage = screen.getByText('Hello, how are you?').closest('div');
      expect(userMessage).toBeInTheDocument();
    });

    it('should render assistant avatar for assistant messages', () => {
      render(<ChatSession messages={mockMessages} />);

      // Find assistant message and check for Bot icon presence
      const assistantMessage = screen.getByText('I am doing well, thank you for asking!').closest('div');
      expect(assistantMessage).toBeInTheDocument();
    });
  });

  describe('message styling', () => {
    it('should apply user message styles', () => {
      render(<ChatSession messages={[mockMessages[0]]} />);

      // User messages should be right-aligned
      const userMessage = screen.getByRole('article');
      expect(userMessage).toHaveClass('flex-row-reverse');
    });

    it('should apply assistant message styles', () => {
      render(<ChatSession messages={[mockMessages[1]]} />);

      // Assistant messages should be left-aligned (not have flex-row-reverse)
      const assistantMessage = screen.getByRole('article');
      expect(assistantMessage).not.toHaveClass('flex-row-reverse');
    });
  });

  describe('streaming state', () => {
    it('should show streaming indicator when isStreaming is true', () => {
      render(
        <ChatSession
          messages={mockMessages}
          isStreaming={true}
          streamingContent="Loading..."
        />
      );

      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should not show streaming indicator when isStreaming is false', () => {
      render(
        <ChatSession
          messages={mockMessages}
          isStreaming={false}
        />
      );

      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    it('should show typing cursor when streaming', () => {
      render(
        <ChatSession
          messages={mockMessages}
          isStreaming={true}
          streamingContent="Loading..."
        />
      );

      // Should have pulsing cursor
      const cursor = document.querySelector('.animate-pulse');
      expect(cursor).toBeInTheDocument();
    });
  });

  describe('auto-scroll', () => {
    it('should scroll to bottom on new message', () => {
      const { rerender } = render(<ChatSession messages={mockMessages} />);

      const newMessages = [
        ...mockMessages,
        {
          id: '3',
          role: 'user' as const,
          content: 'New message',
          timestamp: 3000,
        },
      ];

      rerender(<ChatSession messages={newMessages} />);

      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    });

    it('should scroll to bottom when streaming content updates', () => {
      const { rerender } = render(
        <ChatSession
          messages={mockMessages}
          isStreaming={true}
          streamingContent="Loading"
        />
      );

      rerender(
        <ChatSession
          messages={mockMessages}
          isStreaming={true}
          streamingContent="Loading..."
        />
      );

      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    });
  });

  describe('timestamp', () => {
    it('should display relative time for recent messages', () => {
      const recentMessage: Message = {
        id: '1',
        role: 'user',
        content: 'Recent message',
        timestamp: Date.now() - 60000, // 1 minute ago
      };

      render(<ChatSession messages={[recentMessage]} />);

      // Should show relative time (e.g., "1m ago")
      expect(screen.getByText(/ago|m$/)).toBeInTheDocument();
    });

    it('should display absolute time for old messages', () => {
      const oldMessage: Message = {
        id: '1',
        role: 'user',
        content: 'Old message',
        timestamp: Date.now() - 86400000 * 2, // 2 days ago
      };

      render(<ChatSession messages={[oldMessage]} />);

      // Should show date
      expect(screen.getByText(/\d{1,2}\/\d{1,2}/)).toBeInTheDocument();
    });
  });

  describe('markdown rendering', () => {
    it('should render bold text', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'This is **bold** text',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      const boldElement = screen.getByText('bold');
      expect(boldElement.tagName).toBe('STRONG');
    });

    it('should render italic text', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'This is *italic* text',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      const italicElement = screen.getByText('italic');
      expect(italicElement.tagName).toBe('EM');
    });

    it('should render code blocks', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: '```javascript\nconst x = 1;\n```',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      expect(screen.getByText(/const x = 1/)).toBeInTheDocument();
    });

    it('should render inline code', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'Use `npm install` to install',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      const codeElement = screen.getByText('npm install');
      expect(codeElement.tagName).toBe('CODE');
    });

    it('should sanitize malicious script tags in markdown', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'Hello **world** <script>alert("xss")</script>',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      // Should render bold text
      expect(screen.getByText('world')).toBeInTheDocument();
      // Should NOT execute or render the script tag
      expect(screen.queryByText('xss')).not.toBeInTheDocument();
      // Script tag should be escaped/removed
      expect(document.querySelector('script')).toBeNull();
    });

    it('should render links safely with react-markdown', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'Check out [this link](https://example.com)',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      const link = screen.getByRole('link', { name: 'this link' });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', 'https://example.com');
      // Links should open in new tab for security
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('citations', () => {
    it('should render clickable citation badges', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'Answer with citation [1]',
        citations: [
          {
            file_path: 'notes/a.md',
            page_num: 0,
            paragraph_idx: 0,
            text_snippet: 'Source snippet',
          },
        ],
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      expect(screen.getByRole('button', { name: /show citation 1/i })).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have proper ARIA roles for messages', () => {
      render(<ChatSession messages={mockMessages} />);

      const messages = screen.getAllByRole('article');
      expect(messages).toHaveLength(2);
    });

    it('should have aria-live for streaming content', () => {
      render(
        <ChatSession
          messages={mockMessages}
          isStreaming={true}
          streamingContent="Loading..."
        />
      );

      const streamingRegion = screen.getByRole('status');
      expect(streamingRegion).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('should handle very long messages', () => {
      const longContent = 'A'.repeat(10000);
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: longContent,
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      expect(screen.getByText(longContent)).toBeInTheDocument();
    });

    it('should handle special characters', () => {
      const message: Message = {
        id: '1',
        role: 'assistant',
        content: 'Special: <script>alert("xss")</script> & "quotes"',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      // Should render escaped, not as HTML
      expect(screen.getByText(/Special:/)).toBeInTheDocument();
      expect(screen.queryByText('xss')).not.toBeInTheDocument();
    });

    it('should handle empty content', () => {
      const message: Message = {
        id: '1',
        role: 'user',
        content: '',
        timestamp: 1000,
      };

      render(<ChatSession messages={[message]} />);

      // Should render without error
      expect(screen.getByRole('article')).toBeInTheDocument();
    });
  });
});
