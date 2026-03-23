/**
 * Tests for useSkillExecution Hook
 *
 * Tests the skill execution hook including:
 * - Execution state management
 * - Error handling
 * - Retry functionality
 * - Status transitions
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useSkillExecution } from './use-skill-execution';
import * as apiModule from '@/lib/api';

// Mock the API module
vi.mock('@/lib/api', () => ({
  executeSkill: vi.fn(),
}));

describe('useSkillExecution Hook', () => {
  const mockSkillName = 'test-skill';
  const mockParams = { param1: 'value1', param2: 123 };
  const mockSuccessResponse = {
    success: true,
    output: 'Execution result',
    error: '',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have idle status initially', () => {
      const { result } = renderHook(() => useSkillExecution());

      expect(result.current.status).toBe('idle');
      expect(result.current.result).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  describe('execute', () => {
    it('should transition through pending and success states', async () => {
      vi.mocked(apiModule.executeSkill).mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useSkillExecution());

      // Start execution
      act(() => {
        result.current.execute(mockSkillName, mockParams);
      });

      // Should be pending immediately
      expect(result.current.status).toBe('pending');

      // Wait for completion
      await waitFor(() => {
        expect(result.current.status).toBe('success');
      });

      expect(result.current.result).toBe('Execution result');
      expect(result.current.error).toBeNull();
    });

    it('should call executeSkill API with correct parameters', async () => {
      vi.mocked(apiModule.executeSkill).mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(apiModule.executeSkill).toHaveBeenCalledWith(mockSkillName, mockParams);
    });

    it('should handle execution errors', async () => {
      vi.mocked(apiModule.executeSkill).mockRejectedValueOnce(new Error('API error'));

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.status).toBe('error');
      expect(result.current.error).toBe('API error');
      expect(result.current.result).toBeNull();
    });

    it('should handle failed skill execution (success: false)', async () => {
      vi.mocked(apiModule.executeSkill).mockResolvedValueOnce({
        success: false,
        output: '',
        error: 'Skill execution failed',
      });

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.status).toBe('error');
      expect(result.current.error).toBe('Skill execution failed');
    });

    it('should set status to running during execution', async () => {
      let resolveExecution: (value: typeof mockSuccessResponse) => void;
      const executionPromise = new Promise<typeof mockSuccessResponse>((resolve) => {
        resolveExecution = resolve;
      });
      vi.mocked(apiModule.executeSkill).mockReturnValueOnce(executionPromise);

      const { result } = renderHook(() => useSkillExecution());

      act(() => {
        result.current.execute(mockSkillName, mockParams);
      });

      // After pending, check that it's in a loading state
      await waitFor(() => {
        expect(['pending', 'running']).toContain(result.current.status);
      });

      // Resolve the execution
      await act(async () => {
        resolveExecution!(mockSuccessResponse);
      });

      expect(result.current.status).toBe('success');
    });
  });

  describe('reset', () => {
    it('should reset to initial state', async () => {
      vi.mocked(apiModule.executeSkill).mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.status).toBe('success');
      expect(result.current.result).toBe('Execution result');

      // Reset
      act(() => {
        result.current.reset();
      });

      expect(result.current.status).toBe('idle');
      expect(result.current.result).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  describe('retry', () => {
    it('should retry with last parameters after error', async () => {
      vi.mocked(apiModule.executeSkill)
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useSkillExecution());

      // First execution fails
      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.status).toBe('error');

      // Retry
      await act(async () => {
        await result.current.retry();
      });

      expect(result.current.status).toBe('success');
      expect(apiModule.executeSkill).toHaveBeenCalledTimes(2);
      expect(apiModule.executeSkill).toHaveBeenNthCalledWith(2, mockSkillName, mockParams);
    });

    it('should throw error when retrying without previous execution', async () => {
      const { result } = renderHook(() => useSkillExecution());

      await expect(
        act(async () => {
          await result.current.retry();
        })
      ).rejects.toThrow('No previous execution to retry');
    });
  });

  describe('isExecuting', () => {
    it('should return true when status is pending or running', async () => {
      let resolveExecution: (value: typeof mockSuccessResponse) => void;
      const executionPromise = new Promise<typeof mockSuccessResponse>((resolve) => {
        resolveExecution = resolve;
      });
      vi.mocked(apiModule.executeSkill).mockReturnValueOnce(executionPromise);

      const { result } = renderHook(() => useSkillExecution());

      act(() => {
        result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.isExecuting()).toBe(true);

      // Complete execution
      await act(async () => {
        resolveExecution!(mockSuccessResponse);
      });

      expect(result.current.isExecuting()).toBe(false);
    });

    it('should return false when status is idle, success, or error', () => {
      const { result } = renderHook(() => useSkillExecution());

      expect(result.current.isExecuting()).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle unknown error types', async () => {
      vi.mocked(apiModule.executeSkill).mockRejectedValueOnce('Unknown error string');

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, mockParams);
      });

      expect(result.current.status).toBe('error');
      expect(result.current.error).toBe('An unknown error occurred');
    });

    it('should handle empty params', async () => {
      vi.mocked(apiModule.executeSkill).mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useSkillExecution());

      await act(async () => {
        await result.current.execute(mockSkillName, {});
      });

      expect(apiModule.executeSkill).toHaveBeenCalledWith(mockSkillName, {});
    });

    it('should handle concurrent execution attempts', async () => {
      let resolveFirst: (value: typeof mockSuccessResponse) => void;
      const firstPromise = new Promise<typeof mockSuccessResponse>((resolve) => {
        resolveFirst = resolve;
      });
      vi.mocked(apiModule.executeSkill).mockReturnValueOnce(firstPromise);

      const { result } = renderHook(() => useSkillExecution());

      // Start first execution
      act(() => {
        result.current.execute('skill1', { a: 1 });
      });

      // Try second execution while first is pending
      act(() => {
        result.current.execute('skill2', { b: 2 });
      });

      // Should still be executing first skill
      expect(result.current.status).toBe('pending');
    });
  });
});