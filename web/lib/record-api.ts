/**
 * Record API Client for Markwritter
 *
 * Provides functions for communicating with the record-related backend APIs:
 * - Create/update notes
 * - AI assistance (continue, rewrite, polish)
 * - Classification and suggestions
 */

import { ApiError } from './api';

// API base URL from environment variable
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ==================== Types ====================

/**
 * Request to create a new record
 */
export interface CreateRecordRequest {
  /** Record content (markdown) */
  content: string;
  /** Record title (optional, can be auto-generated) */
  title?: string | null;
  /** Folder ID for organization */
  folder_id?: string | null;
  /** Tags for the record */
  tags?: string[];
  /** Aliases for the record (Obsidian-style) */
  aliases?: string[];
}

/**
 * Request to update an existing record
 */
export interface UpdateRecordRequest {
  /** Record ID */
  id: string;
  /** Updated title */
  title?: string | null;
  /** Updated content */
  content?: string;
  /** Updated folder */
  folder_id?: string | null;
  /** Updated tags */
  tags?: string[];
  /** Updated aliases */
  aliases?: string[];
}

/**
 * Record response from API
 */
export interface RecordResponse {
  /** Unique record identifier */
  id: string;
  /** Record title */
  title: string | null;
  /** Record content (markdown) */
  content: string;
  /** Folder ID */
  folder_id: string | null;
  /** Tags */
  tags: string[];
  /** Aliases */
  aliases: string[];
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}

/**
 * AI rewrite response
 */
export interface AIRewriteResponse {
  /** Original content */
  original: string;
  /** Rewritten content */
  rewritten: string;
}

/**
 * AI polish response
 */
export interface AIPolishResponse {
  /** Original content */
  original: string;
  /** Polished content */
  polished: string;
}

/**
 * Classification response
 */
export interface ClassifyResponse {
  /** Suggested tags */
  suggested_tags: string[];
  /** Suggested folder */
  suggested_folder: string | null;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Tag suggestion response
 */
export interface TagSuggestionResponse {
  /** Suggested tags */
  tags: string[];
}

/**
 * Folder suggestion response
 */
export interface FolderSuggestionResponse {
  /** Suggested folder path */
  folder: string | null;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * SSE event types for AI continue stream
 */
export type AIStreamEventType = 'thinking' | 'text_delta' | 'done' | 'error';

/**
 * SSE event from AI continue stream
 */
export interface AIStreamEvent {
  type: AIStreamEventType;
  content: string;
}

// ==================== Helper Functions ====================

/**
 * Create an ApiError from a failed Response.
 */
async function createApiError(response: Response): Promise<ApiError> {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  try {
    const body = await response.text();
    if (body) {
      errorMessage = `${response.status}: ${body}`;
    }
  } catch {
    // Ignore parsing errors
  }
  return new ApiError(response.status, errorMessage);
}

// ==================== Record CRUD ====================

/**
 * Create a new record/note.
 *
 * @param request - The create request
 * @returns The created record
 * @throws ApiError if the request fails
 */
export async function createRecord(
  request: CreateRecordRequest
): Promise<RecordResponse> {
  const response = await fetch(`${API_BASE}/api/v1/record/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Update an existing record/note.
 *
 * @param request - The update request
 * @returns The updated record
 * @throws ApiError if the request fails
 */
export async function updateRecord(
  request: UpdateRecordRequest
): Promise<RecordResponse> {
  const response = await fetch(`${API_BASE}/api/v1/record/update`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

// ==================== AI Assistance ====================

/**
 * Request AI to continue writing (streaming).
 *
 * @param recordId - The record ID
 * @param content - Current content
 * @param signal - Optional AbortSignal for cancellation
 * @returns Response object for SSE processing
 * @throws ApiError if the request fails
 */
export async function aiContinueStream(
  recordId: string,
  content: string,
  signal?: AbortSignal
): Promise<Response> {
  const response = await fetch(
    `${API_BASE}/api/v1/record/ai-assist/continue/stream`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: recordId,
        content,
      }),
      signal,
    }
  );

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response;
}

/**
 * Request AI to rewrite content.
 *
 * @param recordId - The record ID
 * @param content - Content to rewrite
 * @returns Rewritten content
 * @throws ApiError if the request fails
 */
export async function aiRewrite(
  recordId: string,
  content: string
): Promise<AIRewriteResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/record/ai-assist/rewrite`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: recordId,
        content,
      }),
    }
  );

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Request AI to polish content.
 *
 * @param recordId - The record ID
 * @param content - Content to polish
 * @returns Polished content
 * @throws ApiError if the request fails
 */
export async function aiPolish(
  recordId: string,
  content: string
): Promise<AIPolishResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/record/ai-assist/polish`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: recordId,
        content,
      }),
    }
  );

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

// ==================== Classification ====================

/**
 * Auto-classify a note (tags + folder).
 *
 * @param content - Note content to classify
 * @returns Classification suggestions
 * @throws ApiError if the request fails
 */
export async function classifyNote(
  content: string
): Promise<ClassifyResponse> {
  const response = await fetch(`${API_BASE}/api/v1/record/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Get tag suggestions for content.
 *
 * @param content - Note content
 * @returns Suggested tags
 * @throws ApiError if the request fails
 */
export async function suggestTags(
  content: string
): Promise<TagSuggestionResponse> {
  const response = await fetch(`${API_BASE}/api/v1/record/suggest/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Get folder suggestion for content.
 *
 * @param content - Note content
 * @returns Suggested folder
 * @throws ApiError if the request fails
 */
export async function suggestFolder(
  content: string
): Promise<FolderSuggestionResponse> {
  const response = await fetch(`${API_BASE}/api/v1/record/suggest/folder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}