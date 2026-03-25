/**
 * Tests for Record API Client
 *
 * Tests the API client functions for record-related backend endpoints.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock environment variable
vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000');

// Import after mocking
import {
  createRecord,
  updateRecord,
  aiContinueStream,
  aiRewrite,
  aiPolish,
  classifyNote,
  suggestTags,
  suggestFolder,
  type CreateRecordRequest,
  type UpdateRecordRequest,
} from './record-api';
import { ApiError } from './api';

describe('Record API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('createRecord', () => {
    const validRequest: CreateRecordRequest = {
      title: 'Test Note',
      content: '# Test Content\n\nThis is a test note.',
      folder_id: null,
      tags: ['test', 'note'],
    };

    it('should send a POST request to /api/v1/record/create', async () => {
      const mockResponse = {
        id: 'note-123',
        title: 'Test Note',
        content: '# Test Content\n\nThis is a test note.',
        folder_id: null,
        tags: ['test', 'note'],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await createRecord(validRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/create',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(validRequest),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on non-OK response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Invalid request'),
      });

      await expect(createRecord(validRequest)).rejects.toThrow(ApiError);
    });

    it('should handle minimal request with only content', async () => {
      const minimalRequest: CreateRecordRequest = {
        content: 'Just some content',
      };

      const mockResponse = {
        id: 'note-456',
        content: 'Just some content',
        title: null,
        folder_id: null,
        tags: [],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await createRecord(minimalRequest);
      expect(result.id).toBe('note-456');
    });

    it('should handle empty content validation error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        text: () => Promise.resolve('Content is required'),
      });

      const error = await createRecord({ content: '' }).catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(422);
    });
  });

  describe('updateRecord', () => {
    const validRequest: UpdateRecordRequest = {
      id: 'note-123',
      title: 'Updated Title',
      content: 'Updated content',
      tags: ['updated'],
    };

    it('should send a PUT request to /api/v1/record/update', async () => {
      const mockResponse = {
        id: 'note-123',
        title: 'Updated Title',
        content: 'Updated content',
        folder_id: null,
        tags: ['updated'],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await updateRecord(validRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/update',
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(validRequest),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError when record not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Record not found'),
      });

      const error = await updateRecord({ id: 'nonexistent' }).catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
    });

    it('should handle partial updates', async () => {
      const partialRequest: UpdateRecordRequest = {
        id: 'note-123',
        tags: ['new-tag'],
      };

      const mockResponse = {
        id: 'note-123',
        title: 'Original Title',
        content: 'Original content',
        folder_id: null,
        tags: ['new-tag'],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await updateRecord(partialRequest);
      expect(result.tags).toEqual(['new-tag']);
    });
  });

  describe('aiContinueStream', () => {
    it('should send a POST request to /api/v1/record/ai-assist/continue/stream', async () => {
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

      const controller = new AbortController();
      const result = await aiContinueStream('note-123', 'Some content', controller.signal);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/continue/stream',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            record_id: 'note-123',
            content: 'Some content',
          }),
          signal: controller.signal,
        })
      );
      expect(result).toBe(mockResponse);
    });

    it('should throw ApiError on stream request failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('AI service unavailable'),
      });

      const error = await aiContinueStream('note-123', 'content').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(500);
    });

    it('should work without AbortSignal', async () => {
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

      const result = await aiContinueStream('note-123', 'content');
      expect(result.ok).toBe(true);
    });
  });

  describe('aiRewrite', () => {
    it('should send a POST request to /api/v1/record/ai-assist/rewrite', async () => {
      const mockResponse = {
        original: 'Original text',
        rewritten: 'Rewritten text with improvements',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await aiRewrite('note-123', 'Original text');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/rewrite',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            record_id: 'note-123',
            content: 'Original text',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on rewrite failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Content too short'),
      });

      await expect(aiRewrite('note-123', '')).rejects.toThrow(ApiError);
    });
  });

  describe('aiPolish', () => {
    it('should send a POST request to /api/v1/record/ai-assist/polish', async () => {
      const mockResponse = {
        original: 'rough text',
        polished: 'Polished and refined text',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await aiPolish('note-123', 'rough text');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/polish',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            record_id: 'note-123',
            content: 'rough text',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on polish failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Polish service error'),
      });

      await expect(aiPolish('note-123', 'text')).rejects.toThrow(ApiError);
    });
  });

  describe('classifyNote', () => {
    it('should send a POST request to /api/v1/record/classify', async () => {
      const mockResponse = {
        suggested_tags: ['programming', 'tutorial'],
        suggested_folder: 'dev-notes',
        confidence: 0.85,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await classifyNote('How to write unit tests');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/classify',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'How to write unit tests',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on classification failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Content too short for classification'),
      });

      await expect(classifyNote('')).rejects.toThrow(ApiError);
    });

    it('should handle empty classification response', async () => {
      const mockResponse = {
        suggested_tags: [],
        suggested_folder: null,
        confidence: 0,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await classifyNote('vague content');
      expect(result.suggested_tags).toEqual([]);
      expect(result.suggested_folder).toBeNull();
    });
  });

  describe('suggestTags', () => {
    it('should send a POST request to /api/v1/record/suggest/tags', async () => {
      const mockResponse = {
        tags: ['javascript', 'frontend', 'react'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await suggestTags('React hooks tutorial');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/suggest/tags',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'React hooks tutorial',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on tag suggestion failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Tag suggestion failed'),
      });

      await expect(suggestTags('content')).rejects.toThrow(ApiError);
    });

    it('should return empty tags array for no suggestions', async () => {
      const mockResponse = {
        tags: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await suggestTags('random gibberish xyz');
      expect(result.tags).toEqual([]);
    });
  });

  describe('suggestFolder', () => {
    it('should send a POST request to /api/v1/record/suggest/folder', async () => {
      const mockResponse = {
        folder: 'projects/frontend',
        confidence: 0.92,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await suggestFolder('Frontend component architecture');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/suggest/folder',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'Frontend component architecture',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw ApiError on folder suggestion failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Folder suggestion failed'),
      });

      await expect(suggestFolder('content')).rejects.toThrow(ApiError);
    });

    it('should return null folder when no suggestion', async () => {
      const mockResponse = {
        folder: null,
        confidence: 0,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await suggestFolder('unrelated content');
      expect(result.folder).toBeNull();
    });
  });
});