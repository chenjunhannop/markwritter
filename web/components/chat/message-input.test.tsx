/**
 * Tests for MessageInput Component
 *
 * Tests the message input component including:
 * - Text input handling
 * - Submit behavior (Enter to send, Shift+Enter for newline)
 * - Loading state
 * - Disabled state
 * - Character limit
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MessageInput } from './message-input';

describe('MessageInput Component', () => {
  const mockOnSubmit = vi.fn();
  const mockOnStop = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render textarea element', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    });

    it('should render send button when not streaming', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });

    it('should render stop button when streaming', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} onStop={mockOnStop} isStreaming={true} />
      );

      expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
    });

    it('should disable textarea when streaming', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={true} />
      );

      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should disable send button when input is empty', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
    });
  });

  describe('input handling', () => {
    it('should update input value on change', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Hello');

      expect(textarea).toHaveValue('Hello');
    });

    it('should clear input after submit', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Hello');

      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      expect(mockOnSubmit).toHaveBeenCalledWith('Hello');
      expect(textarea).toHaveValue('');
    });
  });

  describe('submit behavior', () => {
    it('should submit on Enter key', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Hello{Enter}');

      expect(mockOnSubmit).toHaveBeenCalledWith('Hello');
    });

    it('should add newline on Shift+Enter', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Hello{Shift>}{Enter}{/Shift}World');

      expect(textarea).toHaveValue('Hello\nWorld');
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should not submit empty input', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '{Enter}');

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should not submit whitespace-only input', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '   {Enter}');

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should trim whitespace on submit', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '  Hello World  {Enter}');

      expect(mockOnSubmit).toHaveBeenCalledWith('Hello World');
    });

    it('should not submit when streaming', async () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={true} />
      );

      // Try to type while streaming (should be disabled)
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeDisabled();
    });
  });

  describe('stop button', () => {
    it('should call onStop when clicked', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} onStop={mockOnStop} isStreaming={true} />
      );

      const stopButton = screen.getByRole('button', { name: /stop/i });
      await user.click(stopButton);

      expect(mockOnStop).toHaveBeenCalled();
    });

    it('should not show stop button when onStop is not provided', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={true} />
      );

      expect(screen.queryByRole('button', { name: /stop/i })).not.toBeInTheDocument();
    });
  });

  describe('character limit', () => {
    it('should show character count when maxLength is set', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} maxLength={100} />
      );

      expect(screen.getByText('0/100')).toBeInTheDocument();
    });

    it('should update character count on input', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} maxLength={100} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Hello');

      expect(screen.getByText('5/100')).toBeInTheDocument();
    });

    it('should show warning when near limit', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} maxLength={10} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '12345678'); // 8 chars

      // Should show warning style (at 80% of limit)
      expect(screen.getByText('8/10')).toHaveClass('text-amber-500');
    });

    it('should show error when at limit', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} maxLength={10} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '1234567890'); // 10 chars

      expect(screen.getByText('10/10')).toHaveClass('text-red-500');
    });

    it('should prevent input beyond maxLength', async () => {
      const user = userEvent.setup();
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} maxLength={10} />
      );

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, '123456789012345'); // Try to type 15 chars

      expect(textarea).toHaveValue('1234567890');
    });
  });

  describe('focus management', () => {
    it('should focus textarea on mount when autoFocus is true', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} autoFocus />
      );

      expect(screen.getByRole('textbox')).toHaveFocus();
    });

    it('should not focus textarea on mount by default', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      expect(screen.getByRole('textbox')).not.toHaveFocus();
    });
  });

  describe('accessibility', () => {
    it('should have accessible label', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={false} />
      );

      expect(screen.getByLabelText(/message input/i)).toBeInTheDocument();
    });

    it('should have aria-disabled when streaming', () => {
      render(
        <MessageInput onSubmit={mockOnSubmit} isStreaming={true} />
      );

      expect(screen.getByRole('textbox')).toHaveAttribute('aria-disabled', 'true');
    });
  });
});