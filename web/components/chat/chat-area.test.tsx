/**
 * Tests for ChatArea Component
 *
 * Tests the main chat area component including:
 * - Message list display
 * - Input integration
 * - SSE streaming
 * - Session management
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChatArea } from './chat-area';
import * as useChatModule from '@/hooks/use-chat';
import type { Message } from '@/lib/types';

// Mock the useChat hook
vi.mock('@/hooks/use-chat', () => ({
  useChat: vi.fn(),
}));

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

describe('ChatArea Component', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      role: 'user',
      content: 'Hello',
      timestamp: 1000,
    },
    {
      id: '2',
      role: 'assistant',
      content: 'Hi there!',
      timestamp: 2000,
    },
  ];

  const mockUseChatReturn = {
    messages: mockMessages,
    currentResponse: '',
    isStreaming: false,
    isThinking: false,
    error: null,
    sendMessage: vi.fn(),
    stopStreaming: vi.fn(),
    retry: vi.fn(),
    clearError: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useChatModule.useChat).mockReturnValue(mockUseChatReturn);
  });

  describe('rendering', () => {
    it('should render message list', () => {
      render(<ChatArea />);

      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });

    it('should render input area', () => {
      render(<ChatArea />);

      expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    });

    it('should render empty state when no messages', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        messages: [],
      });

      render(<ChatArea />);

      expect(screen.getByText(/start a conversation/i)).toBeInTheDocument();
    });
  });

  describe('message sending', () => {
    it('should call sendMessage when submitting', async () => {
      const user = userEvent.setup();
      const sendMessage = vi.fn().mockResolvedValue(undefined);
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        sendMessage,
      });

      render(<ChatArea />);

      const input = screen.getByPlaceholderText(/type a message/i);
      await user.type(input, 'Test message');

      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      expect(sendMessage).toHaveBeenCalledWith('Test message');
    });

    it('should clear input after sending', async () => {
      const user = userEvent.setup();
      const sendMessage = vi.fn().mockResolvedValue(undefined);
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        sendMessage,
      });

      render(<ChatArea />);

      const input = screen.getByPlaceholderText(/type a message/i) as HTMLTextAreaElement;
      await user.type(input, 'Test message');

      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      expect(input.value).toBe('');
    });

    it('should not send empty messages', async () => {
      const user = userEvent.setup();
      const sendMessage = vi.fn();
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        sendMessage,
      });

      render(<ChatArea />);

      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      expect(sendMessage).not.toHaveBeenCalled();
    });
  });

  describe('streaming state', () => {
    it('should show streaming indicator when streaming', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isStreaming: true,
        currentResponse: 'Loading...',
      });

      render(<ChatArea />);

      // Use getAllByText since text appears in multiple places
      const matches = screen.getAllByText('Loading...');
      expect(matches.length).toBeGreaterThan(0);
    });

    it('should show stop button when streaming', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isStreaming: true,
      });

      render(<ChatArea />);

      expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
    });

    it('should call stopStreaming when stop button clicked', async () => {
      const user = userEvent.setup();
      const stopStreaming = vi.fn();
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isStreaming: true,
        stopStreaming,
      });

      render(<ChatArea />);

      const stopButton = screen.getByRole('button', { name: /stop/i });
      await user.click(stopButton);

      expect(stopStreaming).toHaveBeenCalled();
    });

    it('should disable input when streaming', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isStreaming: true,
      });

      render(<ChatArea />);

      expect(screen.getByPlaceholderText(/type a message/i)).toBeDisabled();
    });
  });

  describe('error handling', () => {
    it('should show error message when error occurs', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        error: 'Network error',
      });

      render(<ChatArea />);

      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });

    it('should show retry button when error occurs', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        error: 'Network error',
      });

      render(<ChatArea />);

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should call retry when retry button clicked', async () => {
      const user = userEvent.setup();
      const retry = vi.fn().mockResolvedValue(undefined);
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        error: 'Network error',
        retry,
      });

      render(<ChatArea />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      expect(retry).toHaveBeenCalled();
    });

    it('should call clearError when dismiss error clicked', async () => {
      const user = userEvent.setup();
      const clearError = vi.fn();
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        error: 'Network error',
        clearError,
      });

      render(<ChatArea />);

      const dismissButton = screen.getByRole('button', { name: /dismiss/i });
      await user.click(dismissButton);

      expect(clearError).toHaveBeenCalled();
    });
  });

  describe('thinking state', () => {
    it('should show thinking indicator when thinking', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isThinking: true,
      });

      render(<ChatArea />);

      expect(screen.getByText(/thinking/i)).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<ChatArea />);

      expect(screen.getByRole('main', { name: /chat/i })).toBeInTheDocument();
    });

    it('should have aria-live for streaming content', () => {
      vi.mocked(useChatModule.useChat).mockReturnValue({
        ...mockUseChatReturn,
        isStreaming: true,
        currentResponse: 'Loading...',
      });

      render(<ChatArea />);

      // Multiple status elements exist (streaming indicator and live region)
      const statusElements = screen.getAllByRole('status');
      expect(statusElements.length).toBeGreaterThan(0);
    });
  });

  describe('custom className', () => {
    it('should apply custom className', () => {
      render(<ChatArea className="custom-class" />);

      const main = screen.getByRole('main', { name: /chat/i });
      expect(main).toHaveClass('custom-class');
    });
  });
});