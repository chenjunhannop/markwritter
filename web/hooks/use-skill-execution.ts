/**
 * useSkillExecution Hook
 *
 * Encapsulates skill execution logic with state management.
 * Handles execution states: idle, pending, running, success, error.
 */

import { useState, useCallback, useRef } from 'react';
import { executeSkill } from '@/lib/api';

type ExecutionStatus = 'idle' | 'pending' | 'running' | 'success' | 'error';

interface UseSkillExecutionReturn {
  /** Current execution status */
  status: ExecutionStatus;
  /** Execution result (output string) */
  result: string | null;
  /** Error message if execution failed */
  error: string | null;
  /** Execute a skill with given parameters */
  execute: (skillName: string, params: Record<string, unknown>) => Promise<void>;
  /** Reset to initial state */
  reset: () => void;
  /** Retry last execution */
  retry: () => Promise<void>;
  /** Check if currently executing */
  isExecuting: () => boolean;
}

interface LastExecution {
  skillName: string;
  params: Record<string, unknown>;
}

/**
 * Hook for managing skill execution state.
 *
 * @example
 * ```tsx
 * const { execute, status, result, error, retry, reset } = useSkillExecution();
 *
 * await execute('my-skill', { param1: 'value' });
 * ```
 */
export function useSkillExecution(): UseSkillExecutionReturn {
  const [status, setStatus] = useState<ExecutionStatus>('idle');
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lastExecutionRef = useRef<LastExecution | null>(null);

  const execute = useCallback(async (skillName: string, params: Record<string, unknown>) => {
    // Store for retry
    lastExecutionRef.current = { skillName, params };

    // Reset state and start execution
    setError(null);
    setResult(null);
    setStatus('pending');

    try {
      const response = await executeSkill(skillName, params);

      if (response.success) {
        setResult(response.output);
        setStatus('success');
      } else {
        setError(response.error || 'Skill execution failed');
        setStatus('error');
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      setStatus('error');
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setResult(null);
    setError(null);
  }, []);

  const retry = useCallback(async () => {
    if (!lastExecutionRef.current) {
      throw new Error('No previous execution to retry');
    }

    const { skillName, params } = lastExecutionRef.current;
    await execute(skillName, params);
  }, [execute]);

  const isExecuting = useCallback(() => {
    return status === 'pending' || status === 'running';
  }, [status]);

  return {
    status,
    result,
    error,
    execute,
    reset,
    retry,
    isExecuting,
  };
}