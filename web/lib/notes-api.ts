/**
 * Notes API Client for Markwritter
 *
 * Provides functions for interacting with vault file tree.
 */

import { createApiError } from './api';
import type { FileTreeResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get the vault file tree structure.
 * Returns nested tree of directories and .md files.
 *
 * @returns FileTreeResponse with nested TreeNode array
 * @throws ApiError if the request fails
 */
export async function getFileTree(): Promise<FileTreeResponse> {
  const response = await fetch(`${API_BASE}/api/v1/notes/tree`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}
