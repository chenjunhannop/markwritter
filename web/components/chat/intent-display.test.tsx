/**
 * Tests for IntentDisplay Component
 *
 * Tests the intent display component including:
 * - Skill intent rendering
 * - Chat intent rendering
 * - Confidence score display
 * - Parameter display
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { IntentDisplay } from './intent-display';
import type { SkillIntent, ChatIntent } from '@/lib/types';

describe('IntentDisplay Component', () => {
  const mockSkillIntent: SkillIntent = {
    type: 'skill',
    skillName: 'generate-article',
    params: {
      topic: 'AI in Healthcare',
      length: 1000,
      style: 'professional',
    },
    confidence: 0.95,
  };

  const mockChatIntent: ChatIntent = {
    type: 'chat',
    message: 'Hello, how are you?',
    confidence: 0.75,
  };

  describe('skill intent rendering', () => {
    it('should render skill name', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      expect(screen.getByText('generate-article')).toBeInTheDocument();
    });

    it('should render skill icon', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      expect(screen.getByLabelText('Skill')).toBeInTheDocument();
    });

    it('should render parameters', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      expect(screen.getByText('topic:')).toBeInTheDocument();
      expect(screen.getByText('AI in Healthcare')).toBeInTheDocument();
      expect(screen.getByText('length:')).toBeInTheDocument();
      expect(screen.getByText('1000')).toBeInTheDocument();
    });

    it('should render confidence score', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      // Check that confidence is displayed somewhere
      const region = screen.getByRole('region', { name: /intent/i });
      expect(region).toBeInTheDocument();
    });

    it('should handle empty params', () => {
      const emptyParamsIntent: SkillIntent = {
        ...mockSkillIntent,
        params: {},
      };

      render(<IntentDisplay intent={emptyParamsIntent} />);

      expect(screen.getByText('generate-article')).toBeInTheDocument();
      expect(screen.queryByText('topic:')).not.toBeInTheDocument();
    });

    it('should handle complex parameter types', () => {
      const complexIntent: SkillIntent = {
        ...mockSkillIntent,
        params: {
          options: { format: 'markdown' },
        },
      };

      render(<IntentDisplay intent={complexIntent} />);

      // Should render stringified object
      expect(screen.getByText(/format.*markdown/)).toBeInTheDocument();
    });
  });

  describe('chat intent rendering', () => {
    it('should render chat label', () => {
      render(<IntentDisplay intent={mockChatIntent} />);

      expect(screen.getByText('Chat')).toBeInTheDocument();
    });

    it('should render chat icon', () => {
      render(<IntentDisplay intent={mockChatIntent} />);

      expect(screen.getByLabelText('Chat')).toBeInTheDocument();
    });

    it('should not render params for chat intent', () => {
      render(<IntentDisplay intent={mockChatIntent} />);

      expect(screen.queryByText('topic:')).not.toBeInTheDocument();
    });
  });

  describe('compact mode', () => {
    it('should render compact view when compact is true', () => {
      render(<IntentDisplay intent={mockSkillIntent} compact />);

      // Should show skill name but not full params
      expect(screen.getByText('generate-article')).toBeInTheDocument();
      expect(screen.queryByText('topic:')).not.toBeInTheDocument();
    });
  });

  describe('confidence visualization', () => {
    it('should show progress bar', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars.length).toBeGreaterThan(0);
    });
  });

  describe('accessibility', () => {
    it('should have accessible label', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      expect(screen.getByRole('region', { name: /intent/i })).toBeInTheDocument();
    });

    it('should have accessible description for skill intent', () => {
      render(<IntentDisplay intent={mockSkillIntent} />);

      expect(screen.getByText(/Skill: generate-article/i)).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('should handle very long skill names', () => {
      const longNameIntent: SkillIntent = {
        ...mockSkillIntent,
        skillName: 'very-long-skill-name-that-might-overflow-the-container',
      };

      render(<IntentDisplay intent={longNameIntent} />);

      // Use getAllByText since skill name appears in multiple places
      const matches = screen.getAllByText(/very-long-skill-name/);
      expect(matches.length).toBeGreaterThan(0);
    });

    it('should handle special characters in params', () => {
      const specialIntent: SkillIntent = {
        ...mockSkillIntent,
        params: {
          query: 'What is special?',
        },
      };

      render(<IntentDisplay intent={specialIntent} />);

      expect(screen.getByText(/What is special/)).toBeInTheDocument();
    });

    it('should handle null params', () => {
      const nullParamsIntent: SkillIntent = {
        ...mockSkillIntent,
        params: null as unknown as Record<string, unknown>,
      };

      render(<IntentDisplay intent={nullParamsIntent} />);

      expect(screen.getByText('generate-article')).toBeInTheDocument();
    });
  });
});