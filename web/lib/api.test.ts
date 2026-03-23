/**
 * Tests for API Client
 *
 * Tests the API client functions for communicating with the backend.
 * Uses MSW (Mock Service Worker) patterns for fetch mocking.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock environment variable
vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000');

// Import after mocking
import {
  sendMessage,
  getSkills,
  getSkill,
  executeSkill,
  getSettings,
  updateSettings,
  ApiError,
  type AppSettings,
} from './api';

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('ApiError', () => {
    it('should create an ApiError with status and message', () => {
      const error = new ApiError(404, 'Not found');
      expect(error.status).toBe(404);
      expect(error.message).toBe('Not found');
      expect(error.name).toBe('ApiError');
    });
  });

  describe('sendMessage', () => {
    it('should send a POST request to /api/chat/message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        body: {
          getReader: () => ({
            read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
            releaseLock: vi.fn(),
          }),
        },
      });

      await sendMessage('Hello, world!');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/chat/message',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'Hello, world!' }),
        })
      );
    });

    it('should return the response object for SSE processing', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        body: {
          getReader: () => ({
            read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
            releaseLock: vi.fn(),
          }),
        },
      };
      mockFetch.mockResolvedValueOnce(mockResponse);

      const result = await sendMessage('Test message');

      expect(result).toBe(mockResponse);
    });

    it('should throw ApiError on non-OK response', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server error details'),
      });

      const error = await sendMessage('Test').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(500);
      expect(error.message).toContain('500');
    });

    it('should include AbortSignal if provided', async () => {
      const controller = new AbortController();
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        body: {
          getReader: () => ({
            read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
            releaseLock: vi.fn(),
          }),
        },
      });

      await sendMessage('Test', controller.signal);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: controller.signal,
        })
      );
    });

    it('should handle empty message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        body: {
          getReader: () => ({
            read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
            releaseLock: vi.fn(),
          }),
        },
      });

      await sendMessage('');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ message: '' }),
        })
      );
    });
  });

  describe('getSkills', () => {
    it('should fetch skills from /api/skills', async () => {
      const mockSkills = [
        { name: 'skill1', description: 'Skill 1', version: '1.0.0' },
        { name: 'skill2', description: 'Skill 2', version: '1.0.0' },
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockSkills),
      });

      const result = await getSkills();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/skills',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockSkills);
    });

    it('should throw ApiError on fetch failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Not found'),
      });

      await expect(getSkills()).rejects.toThrow(ApiError);
    });

    it('should return empty array for empty response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });

      const result = await getSkills();
      expect(result).toEqual([]);
    });
  });

  describe('getSkill', () => {
    it('should fetch a single skill by name', async () => {
      const mockSkill = {
        name: 'translate',
        description: 'Translate text',
        version: '1.0.0',
        inputs: [],
        output: { type: 'string', description: 'Translated text' },
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockSkill),
      });

      const result = await getSkill('translate');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/skills/translate',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockSkill);
    });

    it('should throw ApiError when skill not found', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Skill not found'),
      });

      const error = await getSkill('nonexistent').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
    });

    it('should encode skill name in URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ name: 'my skill', description: '', version: '1.0.0' }),
      });

      await getSkill('my skill');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/skills/my%20skill',
        expect.any(Object)
      );
    });
  });

  describe('executeSkill', () => {
    it('should execute a skill with parameters', async () => {
      const mockResponse = {
        success: true,
        output: 'Result text',
        error: '',
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await executeSkill('translate', { text: 'Hello', target: 'es' });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/skills/translate/execute',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ params: { text: 'Hello', target: 'es' } }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should execute a skill with empty parameters', async () => {
      const mockResponse = {
        success: true,
        output: 'Done',
        error: '',
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await executeSkill('ping', {});

      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on execution failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Invalid parameters'),
      });

      await expect(executeSkill('skill', {})).rejects.toThrow(ApiError);
    });

    it('should handle skill execution error response', async () => {
      const mockResponse = {
        success: false,
        output: '',
        error: 'Skill execution failed',
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await executeSkill('failing-skill', {});
      expect(result.success).toBe(false);
      expect(result.error).toBe('Skill execution failed');
    });
  });

  describe('getSettings', () => {
    it('should fetch settings from /api/settings', async () => {
      const mockSettings = {
        theme: 'dark',
        language: 'en',
        notifications: true,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockSettings),
      });

      const result = await getSettings();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/settings',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockSettings);
    });

    it('should throw ApiError on fetch failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server error'),
      });

      await expect(getSettings()).rejects.toThrow(ApiError);
    });
  });

  describe('updateSettings', () => {
    it('should update settings via PUT to /api/settings', async () => {
      const newSettings = { theme: 'light' as const };
      const mockResponse = {
        success: true,
        settings: { theme: 'light', language: 'en' },
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await updateSettings(newSettings);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/settings',
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newSettings),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on update failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Invalid settings'),
      });

      await expect(updateSettings({ theme: 'dark' } as Partial<AppSettings>)).rejects.toThrow(ApiError);
    });

    it('should handle partial updates', async () => {
      const partialSettings = { theme: 'dark' as const };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ success: true, settings: partialSettings }),
      });

      const result = await updateSettings(partialSettings);
      expect(result.success).toBe(true);
    });
  });
});