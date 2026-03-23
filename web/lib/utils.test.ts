/**
 * Utility function tests for Markwritter
 *
 * These tests verify the cn() function for className merging.
 */

import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('cn utility', () => {
  describe('basic functionality', () => {
    it('should merge simple class names', () => {
      const result = cn('foo', 'bar');
      expect(result).toBe('foo bar');
    });

    it('should handle empty strings', () => {
      const result = cn('foo', '', 'bar');
      expect(result).toBe('foo bar');
    });

    it('should handle no arguments', () => {
      const result = cn();
      expect(result).toBe('');
    });

    it('should handle undefined and null', () => {
      const result = cn('foo', undefined, null, 'bar');
      expect(result).toBe('foo bar');
    });
  });

  describe('conditional classes', () => {
    it('should handle conditional object syntax', () => {
      const result = cn('foo', { bar: true, baz: false });
      expect(result).toBe('foo bar');
    });

    it('should handle all false conditions', () => {
      const result = cn('foo', { bar: false, baz: false });
      expect(result).toBe('foo');
    });

    it('should handle mixed conditions', () => {
      const isActive = true;
      const isDisabled = false;
      const result = cn('btn', { active: isActive, disabled: isDisabled });
      expect(result).toBe('btn active');
    });
  });

  describe('tailwind-merge functionality', () => {
    it('should merge conflicting Tailwind classes correctly', () => {
      // tailwind-merge should keep the last class when there's a conflict
      const result = cn('p-4', 'p-2');
      expect(result).toBe('p-2');
    });

    it('should handle conflicting margin classes', () => {
      const result = cn('m-2', 'm-4');
      expect(result).toBe('m-4');
    });

    it('should handle conflicting text color classes', () => {
      const result = cn('text-red-500', 'text-blue-500');
      expect(result).toBe('text-blue-500');
    });

    it('should handle conflicting background color classes', () => {
      const result = cn('bg-white', 'bg-gray-100');
      expect(result).toBe('bg-gray-100');
    });

    it('should preserve non-conflicting classes', () => {
      const result = cn('p-4', 'text-center', 'm-2');
      expect(result).toBe('p-4 text-center m-2');
    });
  });

  describe('arrays and nested values', () => {
    it('should handle arrays of classes', () => {
      const result = cn(['foo', 'bar'], 'baz');
      expect(result).toBe('foo bar baz');
    });

    it('should handle nested arrays', () => {
      const result = cn(['foo', ['bar', 'baz']], 'qux');
      expect(result).toBe('foo bar baz qux');
    });

    it('should handle mixed types', () => {
      const result = cn('foo', ['bar', { baz: true }], { qux: false });
      expect(result).toBe('foo bar baz');
    });
  });

  describe('real-world scenarios', () => {
    it('should handle button variant classes', () => {
      const result = cn(
        'inline-flex items-center justify-center rounded-md',
        'px-4 py-2 text-sm font-medium',
        'bg-primary text-primary-foreground',
        'hover:bg-primary/90',
        { 'opacity-50 pointer-events-none': false }
      );
      expect(result).toContain('inline-flex');
      expect(result).toContain('bg-primary');
      expect(result).not.toContain('opacity-50');
    });

    it('should handle card component classes', () => {
      const result = cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        { 'border-red-500': false },
        'p-6'
      );
      expect(result).toBe('rounded-lg border bg-card text-card-foreground shadow-sm p-6');
    });

    it('should override responsive classes correctly', () => {
      const result = cn('sm:p-4', 'sm:p-6');
      expect(result).toBe('sm:p-6');
    });

    it('should handle dark mode classes', () => {
      const result = cn('bg-white dark:bg-gray-900', 'dark:bg-black');
      expect(result).toContain('bg-white');
      expect(result).toContain('dark:bg-black');
      expect(result).not.toContain('dark:bg-gray-900');
    });
  });
});