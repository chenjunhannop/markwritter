/**
 * Query API Client for Markwritter
 *
 * Provides functions for communicating with the query-related backend APIs:
 * - Keyword search
 * - Semantic search
 * - Hybrid search
 * - Q&A (ask)
 * - Streaming Q&A (SSE)
 * - Search suggestions
 */

import { ApiError } from './api';

// API base URL from environment variable
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ==================== Types ====================

/**
 * Search result item
 */
export interface SearchResult {
  id: string;
  title: string;
  content: string;
  score: number;
  highlighted?: string;
  [key: string]: unknown;
}

/**
 * Search response from API
 */
export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

/**
 * Source reference for Q&A answers
 */
export interface SourceReference {
  id: string;
  title: string;
  content: string;
  score?: number;
  [key: string]: unknown;
}

/**
 * Ask response from API
 */
export interface AskResponse {
  question: string;
  answer: string;
  sources: SourceReference[];
}

/**
 * Suggestion response from API
 */
export interface SuggestResponse {
  query: string;
  suggestions: string[];
}

/**
 * SSE event types for streaming Q&A
 */
export type QueryEventType = 'thinking' | 'text_delta' | 'sources' | 'done' | 'error';

/**
 * SSE event from streaming Q&A
 */
export interface QueryStreamEvent {
  type: QueryEventType;
  content: string;
  sources?: SourceReference[];
}

/**
 * Options for keyword search
 */
export interface KeywordSearchOptions {
  limit?: number;
}

/**
 * Options for semantic search
 */
export interface SemanticSearchOptions {
  topK?: number;
}

/**
 * Options for hybrid search
 */
export interface HybridSearchOptions {
  mode?: 'keyword' | 'semantic' | 'balanced';
  topK?: number;
}

/**
 * Options for ask question
 */
export interface AskOptions {
  topK?: number;
  context?: Array<{ role: string; content: string }>;
}

/**
 * Options for streaming ask
 */
export interface AskStreamOptions extends AskOptions {
  signal?: AbortSignal;
}

/**
 * Options for suggestions
 */
export interface SuggestOptions {
  limit?: number;
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

// ==================== API Functions ====================

/**
 * Perform keyword search using SQLite FTS5 full-text search.
 *
 * @param query - The search query string
 * @param options - Search options (limit)
 * @returns Search response with results
 * @throws ApiError if the request fails
 */
export async function keywordSearch(
  query: string,
  options: KeywordSearchOptions = {}
): Promise<SearchResponse> {
  const { limit = 10 } = options;

  const response = await fetch(`${API_BASE}/api/v1/query/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Perform semantic search using vector similarity.
 *
 * @param query - The search query string
 * @param options - Search options (topK)
 * @returns Search response with semantically similar results
 * @throws ApiError if the request fails
 */
export async function semanticSearch(
  query: string,
  options: SemanticSearchOptions = {}
): Promise<SearchResponse> {
  const { topK = 5 } = options;

  const response = await fetch(`${API_BASE}/api/v1/query/semantic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Perform hybrid search combining keyword and semantic approaches.
 *
 * @param query - The search query string
 * @param options - Search options (mode, topK)
 * @returns Search response with combined and ranked results
 * @throws ApiError if the request fails
 */
export async function hybridSearch(
  query: string,
  options: HybridSearchOptions = {}
): Promise<SearchResponse> {
  const { mode = 'balanced', topK = 5 } = options;

  const response = await fetch(`${API_BASE}/api/v1/query/hybrid`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, mode, top_k: topK }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Ask a question and get an answer using RAG.
 *
 * @param question - The question to ask
 * @param options - Ask options (topK, context)
 * @returns Answer with source references
 * @throws ApiError if the request fails
 */
export async function askQuestion(
  question: string,
  options: AskOptions = {}
): Promise<AskResponse> {
  const { topK = 5, context } = options;

  const response = await fetch(`${API_BASE}/api/v1/query/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK, context }),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Ask a question with streaming response using SSE.
 *
 * @param question - The question to ask
 * @param options - Ask options (topK, context, signal)
 * @returns Response object for SSE processing
 * @throws ApiError if the request fails
 */
export async function askQuestionStream(
  question: string,
  options: AskStreamOptions = {}
): Promise<Response> {
  const { topK = 5, context, signal } = options;

  const response = await fetch(`${API_BASE}/api/v1/query/ask/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK, context }),
    signal,
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response;
}

/**
 * Get search suggestions based on query prefix.
 *
 * @param query - The query prefix for suggestions
 * @param options - Suggest options (limit)
 * @returns List of suggested queries
 * @throws ApiError if the request fails
 */
export async function getSuggestions(
  query: string,
  options: SuggestOptions = {}
): Promise<SuggestResponse> {
  const { limit = 5 } = options;

  const params = new URLSearchParams({
    query,
    limit: String(limit),
  });

  const response = await fetch(`${API_BASE}/api/v1/query/suggest?${params}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}