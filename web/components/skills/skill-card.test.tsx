/**
 * Tests for SkillCard Component
 *
 * Tests the skill card component including:
 * - Display of skill information
 * - User interactions (run, edit)
 * - Badge display for version
 * - Loading and disabled states
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { SkillCard } from './skill-card';
import type { Skill } from '@/lib/types';

// Mock Next.js Link
vi.mock('next/link', () => ({
  default: ({
    children,
    href,
    className,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

describe('SkillCard Component', () => {
  const mockSkill: Skill = {
    name: 'test-skill',
    description: 'A test skill for testing',
    version: '1.0.0',
    inputs: [
      { name: 'param1', type: 'string', description: 'First parameter', required: true },
      { name: 'param2', type: 'number', description: 'Second parameter', required: false },
    ],
    output: { type: 'string', description: 'Output result' },
  };

  describe('rendering', () => {
    it('should render skill name', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText('test-skill')).toBeInTheDocument();
    });

    it('should render skill description', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText('A test skill for testing')).toBeInTheDocument();
    });

    it('should render skill version badge', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText('1.0.0')).toBeInTheDocument();
    });

    it('should render input parameter count', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText(/2 inputs/i)).toBeInTheDocument();
    });

    it('should render output type', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText(/output: string/i)).toBeInTheDocument();
    });
  });

  describe('actions', () => {
    it('should render Run button with correct link', () => {
      render(<SkillCard skill={mockSkill} />);

      const runLink = screen.getByRole('link', { name: /run/i });
      expect(runLink).toHaveAttribute('href', '/skills/test-skill');
    });

    it('should render Edit button with correct link', () => {
      render(<SkillCard skill={mockSkill} />);

      const editLink = screen.getByRole('link', { name: /edit/i });
      expect(editLink).toHaveAttribute('href', '/skills/test-skill/edit');
    });

    it('should call onDelete when delete button clicked', async () => {
      const user = userEvent.setup();
      const onDelete = vi.fn();

      render(<SkillCard skill={mockSkill} onDelete={onDelete} />);

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      expect(onDelete).toHaveBeenCalledWith('test-skill');
    });

    it('should not render delete button if onDelete not provided', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    });
  });

  describe('required inputs indicator', () => {
    it('should show required inputs count', () => {
      render(<SkillCard skill={mockSkill} />);

      expect(screen.getByText(/1 required/i)).toBeInTheDocument();
    });

    it('should not show required count if no required inputs', () => {
      const skillNoRequired: Skill = {
        ...mockSkill,
        inputs: [
          { name: 'param1', type: 'string', description: 'Optional', required: false },
        ],
      };

      render(<SkillCard skill={skillNoRequired} />);

      expect(screen.queryByText(/required/i)).not.toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('should disable buttons when loading', () => {
      render(<SkillCard skill={mockSkill} isLoading />);

      const runLink = screen.getByRole('link', { name: /run/i });
      expect(runLink).toHaveClass('pointer-events-none');
      expect(runLink).toHaveClass('opacity-50');
    });

    it('should show loading indicator when loading', () => {
      render(<SkillCard skill={mockSkill} isLoading />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('custom className', () => {
    it('should apply custom className', () => {
      render(<SkillCard skill={mockSkill} className="custom-class" />);

      const card = screen.getByTestId('skill-card');
      expect(card).toHaveClass('custom-class');
    });
  });

  describe('edge cases', () => {
    it('should handle skill with no inputs', () => {
      const skillNoInputs: Skill = {
        ...mockSkill,
        inputs: [],
      };

      render(<SkillCard skill={skillNoInputs} />);

      expect(screen.getByText(/0 inputs/i)).toBeInTheDocument();
    });

    it('should handle skill with special characters in name', () => {
      const specialSkill: Skill = {
        ...mockSkill,
        name: 'my-special-skill_v2',
      };

      render(<SkillCard skill={specialSkill} />);

      const runLink = screen.getByRole('link', { name: /run/i });
      expect(runLink).toHaveAttribute('href', '/skills/my-special-skill_v2');
    });

    it('should handle long description with truncation', () => {
      const longDescSkill: Skill = {
        ...mockSkill,
        description:
          'This is a very long description that should be truncated when displayed in the card to prevent layout issues.',
      };

      render(<SkillCard skill={longDescSkill} />);

      const description = screen.getByText(/This is a very long description/);
      expect(description).toHaveClass('line-clamp-2');
    });
  });

  describe('accessibility', () => {
    it('should have proper card title structure', () => {
      render(<SkillCard skill={mockSkill} />);

      // CardTitle is a div with font-semibold, not a semantic heading
      const titleElement = screen.getByText('test-skill');
      expect(titleElement).toHaveClass('font-semibold');
    });

    it('should have accessible button labels', () => {
      render(<SkillCard skill={mockSkill} onDelete={vi.fn()} />);

      expect(screen.getByRole('button', { name: /delete test-skill/i })).toBeInTheDocument();
    });
  });
});