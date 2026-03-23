/**
 * Tests for SkillList Component
 *
 * Tests the skill list component including:
 * - Display of skill cards
 * - Search/filter functionality
 * - Loading and error states
 * - Empty state
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SkillList } from './skill-list';
import * as skillStoreModule from '@/lib/store';
import type { Skill } from '@/lib/types';

// Mock the skill store
vi.mock('@/lib/store', () => ({
  useSkillStore: vi.fn(),
}));

// Mock SkillCard component
vi.mock('./skill-card', () => ({
  SkillCard: ({ skill, onDelete }: { skill: Skill; onDelete?: (name: string) => void }) => (
    <div data-testid={`skill-card-${skill.name}`}>
      <span>{skill.name}</span>
      {onDelete && (
        <button onClick={() => onDelete(skill.name)} aria-label={`Delete ${skill.name}`}>
          Delete
        </button>
      )}
    </div>
  ),
}));

describe('SkillList Component', () => {
  const mockSkills: Skill[] = [
    {
      name: 'skill-one',
      description: 'First skill',
      version: '1.0.0',
      inputs: [{ name: 'input1', type: 'string', description: 'Input', required: true }],
      output: { type: 'string', description: 'Output' },
    },
    {
      name: 'skill-two',
      description: 'Second skill',
      version: '2.0.0',
      inputs: [],
      output: { type: 'object', description: 'Output' },
    },
    {
      name: 'another-skill',
      description: 'Another skill',
      version: '1.5.0',
      inputs: [{ name: 'param', type: 'number', description: 'Parameter', required: false }],
      output: { type: 'number', description: 'Result' },
    },
  ];

  const mockStoreReturn = {
    skills: mockSkills,
    selectedSkill: null,
    isLoading: false,
    error: null,
    loadSkills: vi.fn(),
    selectSkill: vi.fn(),
    clearSelection: vi.fn(),
    executeSelectedSkill: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(skillStoreModule.useSkillStore).mockReturnValue(mockStoreReturn);
  });

  describe('rendering', () => {
    it('should render all skills', () => {
      render(<SkillList />);

      expect(screen.getByTestId('skill-card-skill-one')).toBeInTheDocument();
      expect(screen.getByTestId('skill-card-skill-two')).toBeInTheDocument();
      expect(screen.getByTestId('skill-card-another-skill')).toBeInTheDocument();
    });

    it('should render skills in a grid layout', () => {
      render(<SkillList />);

      const grid = screen.getByRole('list');
      expect(grid).toHaveClass('grid');
    });
  });

  describe('loading state', () => {
    it('should show loading indicator when loading', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        isLoading: true,
        skills: [],
      });

      render(<SkillList />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('should not show skills when loading', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        isLoading: true,
        skills: [],
      });

      render(<SkillList />);

      expect(screen.queryByTestId(/skill-card-/)).not.toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('should show error message when error occurs', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        error: 'Failed to load skills',
      });

      render(<SkillList />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/failed to load skills/i)).toBeInTheDocument();
    });

    it('should show retry button when error occurs', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        error: 'Failed to load skills',
      });

      render(<SkillList />);

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should call loadSkills when retry button clicked', async () => {
      const user = userEvent.setup();
      const loadSkills = vi.fn();
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        error: 'Failed to load skills',
        loadSkills,
      });

      render(<SkillList />);

      await user.click(screen.getByRole('button', { name: /retry/i }));

      expect(loadSkills).toHaveBeenCalled();
    });
  });

  describe('empty state', () => {
    it('should show empty state when no skills', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        skills: [],
      });

      render(<SkillList />);

      expect(screen.getByText(/no skills found/i)).toBeInTheDocument();
    });

    it('should show create skill button in empty state', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        skills: [],
      });

      render(<SkillList />);

      expect(screen.getByRole('link', { name: /create skill/i })).toBeInTheDocument();
    });
  });

  describe('search functionality', () => {
    it('should render search input', () => {
      render(<SkillList />);

      expect(screen.getByPlaceholderText(/search skills/i)).toBeInTheDocument();
    });

    it('should filter skills by name', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'skill-one');

      expect(screen.getByTestId('skill-card-skill-one')).toBeInTheDocument();
      expect(screen.queryByTestId('skill-card-skill-two')).not.toBeInTheDocument();
      expect(screen.queryByTestId('skill-card-another-skill')).not.toBeInTheDocument();
    });

    it('should filter skills by description', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'Second');

      expect(screen.queryByTestId('skill-card-skill-one')).not.toBeInTheDocument();
      expect(screen.getByTestId('skill-card-skill-two')).toBeInTheDocument();
      expect(screen.queryByTestId('skill-card-another-skill')).not.toBeInTheDocument();
    });

    it('should show no results message when search has no matches', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'nonexistent');

      expect(screen.getByText(/no skills match your search/i)).toBeInTheDocument();
    });

    it('should clear search when clear button clicked', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i) as HTMLInputElement;
      await user.type(searchInput, 'skill-one');
      expect(searchInput.value).toBe('skill-one');

      const clearButton = screen.getByRole('button', { name: /clear search/i });
      await user.click(clearButton);

      expect(searchInput.value).toBe('');
    });
  });

  describe('skill deletion', () => {
    it('should call onDelete when skill is deleted', async () => {
      const user = userEvent.setup();
      const onDelete = vi.fn();

      render(<SkillList onDelete={onDelete} />);

      const deleteButton = screen.getByRole('button', { name: /delete skill-one/i });
      await user.click(deleteButton);

      expect(onDelete).toHaveBeenCalledWith('skill-one');
    });
  });

  describe('initial load', () => {
    it('should call loadSkills on mount if skills are empty', () => {
      const loadSkills = vi.fn();
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        skills: [],
        loadSkills,
      });

      render(<SkillList />);

      expect(loadSkills).toHaveBeenCalled();
    });

    it('should not call loadSkills on mount if skills exist', () => {
      const loadSkills = vi.fn();
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        loadSkills,
      });

      render(<SkillList />);

      expect(loadSkills).not.toHaveBeenCalled();
    });
  });

  describe('custom className', () => {
    it('should apply custom className', () => {
      render(<SkillList className="custom-class" />);

      const container = screen.getByTestId('skill-list-container');
      expect(container).toHaveClass('custom-class');
    });
  });

  describe('edge cases', () => {
    it('should handle case-insensitive search', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'SKILL-ONE');

      expect(screen.getByTestId('skill-card-skill-one')).toBeInTheDocument();
    });

    it('should handle special characters in search', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'skill-one');

      expect(screen.getByTestId('skill-card-skill-one')).toBeInTheDocument();
    });

    it('should show skill count', () => {
      render(<SkillList />);

      expect(screen.getByText(/3 skills/i)).toBeInTheDocument();
    });

    it('should update skill count based on search', async () => {
      const user = userEvent.setup();
      render(<SkillList />);

      const searchInput = screen.getByPlaceholderText(/search skills/i);
      await user.type(searchInput, 'skill-one');

      expect(screen.getByText(/1 skill/i)).toBeInTheDocument();
    });
  });
});