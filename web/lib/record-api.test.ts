/**
 * Tests for Record API Client
 *
 * Tests the API client functions for record-related backend endpoints.
 * Includes tests for both legacy Record API and new Notes API.
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
  createNote,
  updateNote,
  getNote,
  deleteNote,
  aiContinueStream,
  aiRewrite,
  aiPolish,
  classifyNote,
  suggestTags,
  suggestFolder,
  type CreateRecordRequest,
  type UpdateRecordRequest,
  type NoteCreateRequest,
  type NoteUpdateRequest,
} from './record-api';
import { ApiError } from './api';

describe('Record API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ==================== Legacy Record API ====================

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

  // ==================== Notes API ====================

  describe('createNote', () => {
    const validRequest: NoteCreateRequest = {
      path: 'test-note.md',
      content: '# Test Content\n\nThis is a test note.',
      metadata: { title: 'Test Note' },
    };

    it('should send a POST request to /api/v1/notes', async () => {
      const mockResponse = {
        success: true,
        path: 'test-note.md',
        message: 'Note created successfully',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await createNote(validRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(validRequest),
        })
      );
      expect(result).toEqual(mockResponse);
      expect(result.success).toBe(true);
      expect(result.path).toBe('test-note.md');
    });

    it('should throw ApiError on non-OK response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Invalid path'),
      });

      await expect(createNote(validRequest)).rejects.toThrow(ApiError);
    });

    it('should throw ApiError on 409 conflict (note exists)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: 'Conflict',
        text: () => Promise.resolve('Note already exists: test-note.md'),
      });

      const error = await createNote(validRequest).catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(409);
    });

    it('should send request without optional metadata and overwrite', async () => {
      const minimalRequest: NoteCreateRequest = {
        path: 'minimal.md',
        content: 'Content',
      };

      const mockResponse = {
        success: true,
        path: 'minimal.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await createNote(minimalRequest);
      expect(result.path).toBe('minimal.md');

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody).not.toHaveProperty('metadata');
      expect(sentBody).not.toHaveProperty('overwrite');
    });

    it('should include overwrite flag when set to true', async () => {
      const requestWithOverwrite: NoteCreateRequest = {
        path: 'overwrite.md',
        content: 'New content',
        overwrite: true,
      };

      const mockResponse = {
        success: true,
        path: 'overwrite.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve(mockResponse),
      });

      await createNote(requestWithOverwrite);

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody.overwrite).toBe(true);
    });

    it('should handle paths with special characters via request body', async () => {
      const specialPathRequest: NoteCreateRequest = {
        path: 'folder/sub folder/note.md',
        content: 'Content',
      };

      const mockResponse = {
        success: true,
        path: 'folder/sub folder/note.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve(mockResponse),
      });

      await createNote(specialPathRequest);
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('updateNote', () => {
    const validRequest: NoteUpdateRequest = {
      content: 'Updated content',
      metadata: { title: 'Updated Title' },
    };

    it('should send a PUT request to /api/v1/notes/{path}', async () => {
      const mockResponse = {
        success: true,
        path: 'test-note.md',
        message: 'Note updated successfully',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await updateNote('test-note.md', validRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/test-note.md',
        expect.objectContaining({
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(validRequest),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should URL-encode the note path', async () => {
      const mockResponse = {
        success: true,
        path: 'folder/note with spaces.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await updateNote('folder/note with spaces.md', { content: 'content' });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/folder%2Fnote%20with%20spaces.md',
        expect.any(Object)
      );
    });

    it('should throw ApiError when note not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Note not found: nonexistent.md'),
      });

      const error = await updateNote('nonexistent.md', { content: 'content' }).catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
    });

    it('should handle mode parameter', async () => {
      const appendRequest: NoteUpdateRequest = {
        content: 'Appended text',
        mode: 'append',
      };

      const mockResponse = {
        success: true,
        path: 'test-note.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await updateNote('test-note.md', appendRequest);

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody.mode).toBe('append');
    });

    it('should handle minimal update with only content', async () => {
      const mockResponse = {
        success: true,
        path: 'test-note.md',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await updateNote('test-note.md', { content: 'Only content' });

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody).not.toHaveProperty('metadata');
      expect(sentBody).not.toHaveProperty('mode');
    });
  });

  describe('getNote', () => {
    it('should send a GET request to /api/v1/notes/{path}', async () => {
      const mockResponse = {
        path: 'test-note.md',
        title: 'Test Note',
        content: '# Test Content\n\nThis is a test note.',
        metadata: { title: 'Test Note' },
        tags: ['test', 'note'],
        links: [],
        backlinks: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getNote('test-note.md');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/test-note.md'
      );
      expect(result).toEqual(mockResponse);
      expect(result.path).toBe('test-note.md');
      expect(result.tags).toEqual(['test', 'note']);
    });

    it('should URL-encode the note path', async () => {
      const mockResponse = {
        path: 'folder/note with spaces.md',
        title: 'Note',
        content: 'Content',
        metadata: {},
        tags: [],
        links: [],
        backlinks: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await getNote('folder/note with spaces.md');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/folder%2Fnote%20with%20spaces.md'
      );
    });

    it('should throw ApiError when note not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Note not found: nonexistent.md'),
      });

      const error = await getNote('nonexistent.md').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
    });

    it('should throw ApiError on vault not configured (503)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: () => Promise.resolve('Vault not configured'),
      });

      const error = await getNote('any.md').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(503);
    });

    it('should handle notes with links and backlinks', async () => {
      const mockResponse = {
        path: 'linked-note.md',
        title: 'Linked Note',
        content: 'Content linking to [[other-note]].',
        metadata: {},
        tags: [],
        links: ['other-note.md'],
        backlinks: ['index.md'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getNote('linked-note.md');
      expect(result.links).toEqual(['other-note.md']);
      expect(result.backlinks).toEqual(['index.md']);
    });
  });

  describe('deleteNote', () => {
    it('should send a DELETE request to /api/v1/notes/{path}', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await deleteNote('test-note.md');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/test-note.md',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should URL-encode the note path', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await deleteNote('folder/note with spaces.md');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/notes/folder%2Fnote%20with%20spaces.md',
        expect.any(Object)
      );
    });

    it('should throw ApiError when note not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Note not found: nonexistent.md'),
      });

      const error = await deleteNote('nonexistent.md').catch((e) => e);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(404);
    });

    it('should return void on success', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      const result = await deleteNote('test-note.md');
      expect(result).toBeUndefined();
    });
  });

  // ==================== AI Assistance ====================

  describe('aiContinueStream', () => {
    it('should send a POST request with only content (no record_id)', async () => {
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
      const result = await aiContinueStream('Some content', controller.signal);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/continue/stream',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'Some content',
          }),
          signal: controller.signal,
        })
      );
      expect(result).toBe(mockResponse);
    });

    it('should not include record_id in request body', async () => {
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

      await aiContinueStream('Test content');

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody).not.toHaveProperty('record_id');
      expect(sentBody).toEqual({ content: 'Test content' });
    });

    it('should throw ApiError on stream request failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('AI service unavailable'),
      });

      const error = await aiContinueStream('content').catch((e) => e);
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

      const result = await aiContinueStream('content');
      expect(result.ok).toBe(true);
    });
  });

  describe('aiRewrite', () => {
    it('should send a POST request with only content (no record_id)', async () => {
      const mockResponse = {
        original: 'Original text',
        rewritten: 'Rewritten text with improvements',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await aiRewrite('Original text');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/rewrite',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'Original text',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should not include record_id in request body', async () => {
      const mockResponse = {
        original: 'rough',
        rewritten: 'polished',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await aiRewrite('rough');

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody).not.toHaveProperty('record_id');
      expect(sentBody).toEqual({ content: 'rough' });
    });

    it('should throw ApiError on rewrite failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Content too short'),
      });

      await expect(aiRewrite('')).rejects.toThrow(ApiError);
    });
  });

  describe('aiPolish', () => {
    it('should send a POST request with only content (no record_id)', async () => {
      const mockResponse = {
        original: 'rough text',
        polished: 'Polished and refined text',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await aiPolish('rough text');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/record/ai-assist/polish',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: 'rough text',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should not include record_id in request body', async () => {
      const mockResponse = {
        original: 'rough',
        polished: 'polished',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await aiPolish('rough');

      const sentBody = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(sentBody).not.toHaveProperty('record_id');
      expect(sentBody).toEqual({ content: 'rough' });
    });

    it('should throw ApiError on polish failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Polish service error'),
      });

      await expect(aiPolish('text')).rejects.toThrow(ApiError);
    });
  });

  // ==================== Classification ====================

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
