/**
 * Tests for SkillExecutor Component
 *
 * Tests the skill executor component including:
 * - Display of execution results
 * - Error display
 * - Copy functionality
 * - Status indicators
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SkillExecutor } from './skill-executor';

describe('SkillExecutor Component', () => {
  // Store original clipboard
  const originalClipboard = navigator.clipboard;

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock clipboard
    const mockClipboard = {
      writeText: vi.fn().mockResolvedValue(undefined),
    };
    Object.defineProperty(navigator, 'clipboard', {
      value: mockClipboard,
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    // Restore original clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
      configurable: true,
    });
  });

  describe('result display', () => {
    it('should display execution result', () => {
      render(<SkillExecutor result="Test result output" error={null} />);

      expect(screen.getByText('Test result output')).toBeInTheDocument();
    });

    it('should not display anything when no result or error', () => {
      const { container } = render(<SkillExecutor result={null} error={null} />);

      expect(container.firstChild).toBeNull();
    });

    it('should handle multiline results', () => {
      render(
        <SkillExecutor
          result={'Line 1\nLine 2\nLine 3'}
          error={null}
        />
      );

      expect(screen.getByText(/Line 1/)).toBeInTheDocument();
    });

    it('should handle long results with scrolling', () => {
      const longResult = 'A'.repeat(1000);
      render(<SkillExecutor result={longResult} error={null} />);

      const resultContainer = screen.getByTestId('execution-result');
      expect(resultContainer).toHaveClass('overflow-auto');
    });
  });

  describe('error display', () => {
    it('should display error message', () => {
      render(<SkillExecutor result={null} error="Execution failed" />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Execution failed')).toBeInTheDocument();
    });

    it('should have error styling on card', () => {
      render(<SkillExecutor result={null} error="Error message" />);

      const card = screen.getByTestId('skill-executor');
      expect(card).toHaveClass('border-destructive');
    });
  });

  describe('copy functionality', () => {
    it('should have copy button when result exists', () => {
      render(<SkillExecutor result="Result to copy" error={null} />);

      expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument();
    });

    it('should copy result to clipboard when copy button clicked', async () => {
      const user = userEvent.setup();
      const writeTextSpy = vi.fn().mockResolvedValue(undefined);
      vi.spyOn(navigator, 'clipboard', 'get').mockReturnValue({
        writeText: writeTextSpy,
      } as unknown as Clipboard);

      render(<SkillExecutor result="Result to copy" error={null} />);

      const copyButton = screen.getByRole('button', { name: /copy result/i });
      await user.click(copyButton);

      expect(writeTextSpy).toHaveBeenCalledWith('Result to copy');
    });

    it('should show copied feedback after copying', async () => {
      const user = userEvent.setup();
      vi.spyOn(navigator, 'clipboard', 'get').mockReturnValue({
        writeText: vi.fn().mockResolvedValue(undefined),
      } as unknown as Clipboard);

      render(<SkillExecutor result="Result to copy" error={null} />);

      const copyButton = screen.getByRole('button', { name: /copy result/i });
      await user.click(copyButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /copied/i })).toBeInTheDocument();
      });
    });
  });

  describe('result label', () => {
    it('should show "Result" label for successful execution', () => {
      render(<SkillExecutor result="Success" error={null} />);

      expect(screen.getByText('Result')).toBeInTheDocument();
    });

    it('should show "Error" label for failed execution', () => {
      render(<SkillExecutor result={null} error="Failed" />);

      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have proper ARIA attributes for error', () => {
      render(<SkillExecutor result={null} error="Error occurred" />);

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('should have accessible copy button', () => {
      render(<SkillExecutor result="Result" error={null} />);

      const copyButton = screen.getByRole('button', { name: /copy result/i });
      expect(copyButton).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('should handle empty string result as no result', () => {
      const { container } = render(<SkillExecutor result="" error={null} />);

      // Empty string is falsy, so component should not render
      expect(container.firstChild).toBeNull();
    });

    it('should handle special characters in result', () => {
      render(
        <SkillExecutor
          result={'Special: <>&"\'\n\t'}
          error={null}
        />
      );

      expect(screen.getByTestId('execution-result')).toBeInTheDocument();
    });

    it('should handle JSON result', () => {
      const jsonResult = JSON.stringify({ key: 'value', nested: { a: 1 } });
      render(<SkillExecutor result={jsonResult} error={null} />);

      // JSON.stringify doesn't add spaces after colons
      expect(screen.getByText(/key.*value/)).toBeInTheDocument();
    });
  });

  describe('custom className', () => {
    it('should apply custom className', () => {
      render(<SkillExecutor result="Result" error={null} className="custom-class" />);

      const container = screen.getByTestId('skill-executor');
      expect(container).toHaveClass('custom-class');
    });
  });
});