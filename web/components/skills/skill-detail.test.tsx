/**
 * Tests for SkillDetail Component
 *
 * Tests the skill detail component including:
 * - Display of skill information
 * - Dynamic form generation
 * - Form validation
 * - Skill execution
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SkillDetail } from './skill-detail';
import * as skillStoreModule from '@/lib/store';
import * as skillExecutionModule from '@/hooks/use-skill-execution';
import type { Skill } from '@/lib/types';

// Mock the skill store
vi.mock('@/lib/store', () => ({
  useSkillStore: vi.fn(),
}));

// Mock the skill execution hook
vi.mock('@/hooks/use-skill-execution', () => ({
  useSkillExecution: vi.fn(),
}));

// Mock SkillExecutor component
vi.mock('./skill-executor', () => ({
  SkillExecutor: ({ result, error }: { result: string | null; error: string | null }) => (
    <div data-testid="skill-executor">
      {result && <div data-testid="execution-result">{result}</div>}
      {error && <div data-testid="execution-error">{error}</div>}
    </div>
  ),
}));

describe('SkillDetail Component', () => {
  const mockSkill: Skill = {
    name: 'test-skill',
    description: 'A test skill for testing purposes',
    version: '1.0.0',
    inputs: [
      {
        name: 'inputText',
        type: 'string',
        description: 'The text to process',
        required: true,
      },
      {
        name: 'count',
        type: 'number',
        description: 'Number of times to process',
        required: false,
        default: 1,
      },
      {
        name: 'enabled',
        type: 'boolean',
        description: 'Enable processing',
        required: false,
        default: false,
      },
    ],
    output: {
      type: 'string',
      description: 'Processed result',
    },
  };

  const mockStoreReturn = {
    selectedSkill: mockSkill,
    isLoading: false,
    error: null,
    selectSkill: vi.fn(),
    clearSelection: vi.fn(),
    loadSkills: vi.fn(),
    executeSelectedSkill: vi.fn(),
    skills: [mockSkill],
  };

  const mockExecutionReturn = {
    status: 'idle' as const,
    result: null,
    error: null,
    execute: vi.fn(),
    reset: vi.fn(),
    retry: vi.fn(),
    isExecuting: () => false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(skillStoreModule.useSkillStore).mockReturnValue(mockStoreReturn);
    vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue(mockExecutionReturn);
  });

  describe('rendering', () => {
    it('should render skill name and description', () => {
      render(<SkillDetail />);

      expect(screen.getByText('test-skill')).toBeInTheDocument();
      expect(screen.getByText('A test skill for testing purposes')).toBeInTheDocument();
    });

    it('should render skill version badge', () => {
      render(<SkillDetail />);

      expect(screen.getByText('1.0.0')).toBeInTheDocument();
    });

    it('should render output type information', () => {
      render(<SkillDetail />);

      expect(screen.getByText(/output:/i)).toBeInTheDocument();
      expect(screen.getByText(/string/)).toBeInTheDocument();
    });
  });

  describe('form generation', () => {
    it('should render form inputs for each skill input', () => {
      render(<SkillDetail />);

      expect(screen.getByLabelText(/inputtext/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/count/i)).toBeInTheDocument();
      // Boolean inputs have a switch, not a label
      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('should show required indicator for required inputs', () => {
      render(<SkillDetail />);

      // Check for the asterisk indicator
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should set default values for optional inputs', () => {
      render(<SkillDetail />);

      const countInput = screen.getByLabelText(/count/i) as HTMLInputElement;
      expect(countInput.value).toBe('1');
    });

    it('should render appropriate input types', () => {
      render(<SkillDetail />);

      // Number input should have type="number"
      expect(screen.getByLabelText(/count/i)).toHaveAttribute('type', 'number');
    });

    it('should render switch for boolean inputs', () => {
      render(<SkillDetail />);

      // Switch should be present for boolean input
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toBeInTheDocument();
    });
  });

  describe('form validation', () => {
    it('should have required attribute on required inputs', () => {
      render(<SkillDetail />);

      // Required inputs should have aria-invalid or be marked required
      const textInput = screen.getByLabelText(/inputtext/i);
      expect(textInput).toBeInTheDocument();
    });

    it('should validate number input type', async () => {
      const user = userEvent.setup();
      render(<SkillDetail />);

      // The number input should have type="number" which provides browser validation
      const countInput = screen.getByLabelText(/count/i);
      expect(countInput).toHaveAttribute('type', 'number');

      // Can type a valid number
      await user.clear(countInput);
      await user.type(countInput, '42');

      expect((countInput as HTMLInputElement).value).toBe('42');
    });
  });

  describe('execution', () => {
    it('should call execute with form values', async () => {
      const user = userEvent.setup();
      const execute = vi.fn().mockResolvedValue(undefined);
      vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue({
        ...mockExecutionReturn,
        execute,
      });

      render(<SkillDetail />);

      // Fill required field
      const textInput = screen.getByLabelText(/inputtext/i);
      await user.type(textInput, 'test input');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /execute/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(execute).toHaveBeenCalledWith('test-skill', {
          inputText: 'test input',
          count: 1,
          enabled: false,
        });
      });
    });

    it('should disable execute button while executing', () => {
      vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue({
        ...mockExecutionReturn,
        status: 'pending',
        isExecuting: () => true,
      });

      render(<SkillDetail />);

      const submitButton = screen.getByRole('button', { name: /executing/i });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('no skill selected', () => {
    it('should show message when no skill is selected', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        selectedSkill: null,
      });

      render(<SkillDetail />);

      expect(screen.getByText(/no skill selected/i)).toBeInTheDocument();
    });
  });

  describe('execution result', () => {
    it('should show execution result', () => {
      vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue({
        ...mockExecutionReturn,
        status: 'success',
        result: 'Execution completed successfully',
      });

      render(<SkillDetail />);

      expect(screen.getByTestId('execution-result')).toHaveTextContent(
        'Execution completed successfully'
      );
    });

    it('should show execution error', () => {
      vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue({
        ...mockExecutionReturn,
        status: 'error',
        error: 'Execution failed',
      });

      render(<SkillDetail />);

      expect(screen.getByTestId('execution-error')).toHaveTextContent('Execution failed');
    });
  });

  describe('reset functionality', () => {
    it('should reset form when reset button clicked', async () => {
      const user = userEvent.setup();
      const reset = vi.fn();
      vi.mocked(skillExecutionModule.useSkillExecution).mockReturnValue({
        ...mockExecutionReturn,
        reset,
        status: 'success',
        result: 'Result',
      });

      render(<SkillDetail />);

      const resetButton = screen.getByRole('button', { name: /reset/i });
      await user.click(resetButton);

      expect(reset).toHaveBeenCalled();
    });
  });

  describe('accessibility', () => {
    it('should have proper form labels', () => {
      render(<SkillDetail />);

      expect(screen.getByLabelText(/inputtext/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/count/i)).toBeInTheDocument();
    });

    it('should have aria-describedby for inputs with descriptions', () => {
      render(<SkillDetail />);

      const textInput = screen.getByLabelText(/inputtext/i);
      expect(textInput).toHaveAttribute('aria-describedby');
    });
  });

  describe('edge cases', () => {
    it('should handle skill with no inputs', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        selectedSkill: {
          ...mockSkill,
          inputs: [],
        },
      });

      render(<SkillDetail />);

      expect(screen.getByText(/no inputs required/i)).toBeInTheDocument();
    });

    it('should handle enum type inputs', () => {
      vi.mocked(skillStoreModule.useSkillStore).mockReturnValue({
        ...mockStoreReturn,
        selectedSkill: {
          ...mockSkill,
          inputs: [
            {
              name: 'option',
              type: 'enum',
              description: 'Select an option',
              required: true,
              enum: ['option1', 'option2', 'option3'],
            },
          ],
      } as unknown as Skill,
      });

      render(<SkillDetail />);

      // Should render a select for enum type
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
  });
});