/**
 * API Client for Markwritter
 *
 * Provides functions for communicating with the backend API.
 * All functions use fetch and return typed responses.
 */

import type { Skill, SkillRunRequest, SkillRunResponse } from './types';

// API base URL from environment variable
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors.
 * Contains HTTP status code and response body.
 */
export class ApiError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

/**
 * Create an ApiError from a failed Response.
 */
export async function createApiError(response: Response): Promise<ApiError> {
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

/**
 * Send a chat message and return the Response for SSE streaming.
 *
 * @param content - The message content to send
 * @param signal - Optional AbortSignal for cancellation
 * @returns The Response object for SSE processing
 * @throws ApiError if the request fails
 */
export async function sendMessage(
  content: string,
  signal?: AbortSignal
): Promise<Response> {
  const response = await fetch(`${API_BASE}/api/v1/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: content }),
    signal,
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response;
}

/**
 * Get all available skills.
 *
 * @returns Array of Skill objects
 * @throws ApiError if the request fails
 */
export async function getSkills(): Promise<Skill[]> {
  const response = await fetch(`${API_BASE}/api/v1/skills/`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Get a single skill by name.
 *
 * @param name - The skill name
 * @returns The Skill object
 * @throws ApiError if the request fails
 */
export async function getSkill(name: string): Promise<Skill> {
  const encodedName = encodeURIComponent(name);
  const response = await fetch(`${API_BASE}/api/v1/skills/${encodedName}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Execute a skill with the given parameters.
 *
 * @param name - The skill name
 * @param params - Parameters for skill execution
 * @returns SkillRunResponse with execution result
 * @throws ApiError if the request fails
 */
export async function executeSkill(
  name: string,
  params: Record<string, unknown>
): Promise<SkillRunResponse> {
  const encodedName = encodeURIComponent(name);
  const requestBody: SkillRunRequest = { params };

  const response = await fetch(`${API_BASE}/api/v1/skills/${encodedName}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Application settings type.
 */
export interface AppSettings {
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  [key: string]: unknown;
}

/**
 * Settings update response.
 */
export interface SettingsUpdateResponse {
  success: boolean;
  settings: AppSettings;
}

/**
 * Get current application settings.
 *
 * @returns The current settings object
 * @throws ApiError if the request fails
 */
export async function getSettings(): Promise<AppSettings> {
  const response = await fetch(`${API_BASE}/api/v1/settings`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Update application settings.
 *
 * @param settings - Partial settings object to update
 * @returns Updated settings response
 * @throws ApiError if the request fails
 */
export async function updateSettings(
  settings: Partial<AppSettings>
): Promise<SettingsUpdateResponse> {
  const response = await fetch(`${API_BASE}/api/v1/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}