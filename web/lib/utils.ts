/**
 * Utility functions for Markwritter
 *
 * This module provides common utility functions used throughout the application.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge class names with Tailwind CSS conflict resolution.
 *
 * Combines clsx for conditional classes and tailwind-merge for
 * deduplicating conflicting Tailwind classes.
 *
 * @param inputs - Class values to merge (strings, objects, arrays)
 * @returns Merged class string with conflicts resolved
 *
 * @example
 * ```ts
 * cn('p-4', 'p-2') // 'p-2' (last wins)
 * cn('foo', { bar: true }) // 'foo bar'
 * cn('text-red-500', 'text-blue-500') // 'text-blue-500'
 * ```
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}