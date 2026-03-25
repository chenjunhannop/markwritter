/**
 * Tests for Query API Client
 *
 * Tests the query API functions for keyword search, semantic search,
 * Q&A, and streaming responses.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock environment variable
vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000');

// Import after mocking
import {
  keywordSearch,
  semanticSearch,
  hybridSearch,
  askQuestion,
  askQuestionStream,
  getSuggestions,
  ApiError,
} from './query-api';

describe('Query API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('keywordSearch', () => {
    it('should send POST request to /api/v1/query/search', async () => {
      const mockResponse = {
        query: 'test query',
        results: [
          { id: '1', title: 'Note 1', content: 'Content 1', score: 0.9 },
        ],
        total: 1,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await keywordSearch('test query');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/search',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'test query', limit: 10 }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should accept custom limit parameter', async () => {
      const mockResponse = {
        query: 'test',
        results: [],
        total: 0,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await keywordSearch('test', { limit: 20 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ query: 'test', limit: 20 }),
        })
      );
    });

    it('should throw ApiError on non-OK response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server error'),
      });

      await expect(keywordSearch('test')).rejects.toThrow(ApiError);
    });

    it('should return empty results on error', async () => {
      const mockResponse = {
        query: 'test',
        results: [],
        total: 0,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await keywordSearch('nonexistent');

      expect(result.results).toEqual([]);
      expect(result.total).toBe(0);
    });
  });

  describe('semanticSearch', () => {
    it('should send POST request to /api/v1/query/semantic', async () => {
      const mockResponse = {
        query: 'meaning of life',
        results: [
          { id: '1', title: 'Philosophy', content: '...', score: 0.95 },
        ],
        total: 1,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await semanticSearch('meaning of life');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/semantic',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'meaning of life', top_k: 5 }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should accept custom top_k parameter', async () => {
      const mockResponse = {
        query: 'test',
        results: [],
        total: 0,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await semanticSearch('test', { topK: 10 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ query: 'test', top_k: 10 }),
        })
      );
    });
  });

  describe('hybridSearch', () => {
    it('should send POST request to /api/v1/query/hybrid', async () => {
      const mockResponse = {
        query: 'test query',
        results: [],
        total: 0,
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await hybridSearch('test query');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/hybrid',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: 'test query',
            mode: 'balanced',
            top_k: 5,
          }),
        })
      );
    });

    it('should accept different search modes', async () => {
      const mockResponse = {
        query: 'test',
        results: [],
        total: 0,
      };
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await hybridSearch('test', { mode: 'keyword' });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ query: 'test', mode: 'keyword', top_k: 5 }),
        })
      );

      await hybridSearch('test', { mode: 'semantic' });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ query: 'test', mode: 'semantic', top_k: 5 }),
        })
      );
    });
  });

  describe('askQuestion', () => {
    it('should send POST request to /api/v1/query/ask', async () => {
      const mockResponse = {
        question: 'What is AI?',
        answer: 'AI stands for Artificial Intelligence...',
        sources: [{ id: '1', title: 'AI Notes', content: '...' }],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await askQuestion('What is AI?');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/ask',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: 'What is AI?', top_k: 5 }),
        })
      );
      expect(result.answer).toBe('AI stands for Artificial Intelligence...');
      expect(result.sources).toHaveLength(1);
    });

    it('should accept optional context parameter', async () => {
      const mockResponse = {
        question: 'test',
        answer: 'answer',
        sources: [],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const context = [{ role: 'user', content: 'previous question' }];
      await askQuestion('test', { context });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ question: 'test', top_k: 5, context }),
        })
      );
    });
  });

  describe('askQuestionStream', () => {
    it('should return Response object for SSE processing', async () => {
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

      const result = await askQuestionStream('What is AI?');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/ask/stream',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: 'What is AI?', top_k: 5 }),
        })
      );
      expect(result).toBe(mockResponse);
    });

    it('should include AbortSignal if provided', async () => {
      const controller = new AbortController();
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

      await askQuestionStream('test', { signal: controller.signal });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: controller.signal,
        })
      );
    });

    it('should throw ApiError on non-OK response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server error'),
      });

      await expect(askQuestionStream('test')).rejects.toThrow(ApiError);
    });
  });

  describe('getSuggestions', () => {
    it('should send GET request to /api/v1/query/suggest', async () => {
      const mockResponse = {
        query: 'art',
        suggestions: ['artificial intelligence', 'art history', 'article'],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getSuggestions('art');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/suggest?query=art&limit=5',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result.suggestions).toHaveLength(3);
    });

    it('should accept custom limit parameter', async () => {
      const mockResponse = {
        query: 'test',
        suggestions: [],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await getSuggestions('test', { limit: 10 });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/suggest?query=test&limit=10',
        expect.any(Object)
      );
    });

    it('should return empty suggestions for empty query', async () => {
      const mockResponse = {
        query: '',
        suggestions: [],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getSuggestions('');

      expect(result.suggestions).toEqual([]);
    });

    it('should encode query parameter in URL', async () => {
      const mockResponse = {
        query: 'test query',
        suggestions: [],
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse),
      });

      await getSuggestions('test query');

      // URLSearchParams encodes spaces as '+' which is valid
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/query/suggest?query=test+query&limit=5',
        expect.any(Object)
      );
    });

    it('should throw ApiError on fetch failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server error'),
      });

      await expect(getSuggestions('test')).rejects.toThrow(ApiError);
    });
  });
});