/**
 * Tests for Query Store
 *
 * Tests the Zustand store for managing query state including:
 * - Search results
 * - Q&A conversations
 * - Streaming state
 * - Suggestions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';

// Mock the query API
vi.mock('./query-api', () => ({
  keywordSearch: vi.fn(),
  semanticSearch: vi.fn(),
  hybridSearch: vi.fn(),
  askQuestion: vi.fn(),
  askQuestionStream: vi.fn(),
  getSuggestions: vi.fn(),
}));

// Import after mocking
import {
  useQueryStore,
  useHasResults,
  useHasAnswer,
  useHasError,
} from './query-store';
import * as queryApi from './query-api';

describe('Query Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useQueryStore.setState({
      searchQuery: '',
      searchResults: [],
      searchMode: 'hybrid',
      isSearching: false,
      searchError: null,
      currentQuestion: '',
      answer: '',
      sources: [],
      isStreaming: false,
      streamError: null,
      suggestions: [],
      isFetchingSuggestions: false,
      abortController: null,
    });
    vi.clearAllMocks();
  });

  describe('Search Actions', () => {
    it('should set search query', () => {
      const { setSearchQuery } = useQueryStore.getState();

      act(() => {
        setSearchQuery('test query');
      });

      expect(useQueryStore.getState().searchQuery).toBe('test query');
    });

    it('should set search mode', () => {
      const { setSearchMode } = useQueryStore.getState();

      act(() => {
        setSearchMode('keyword');
      });

      expect(useQueryStore.getState().searchMode).toBe('keyword');
    });

    it('should clear search results', () => {
      // Set some initial state
      useQueryStore.setState({
        searchResults: [{ id: '1', title: 'Test', content: 'Content', score: 0.9 }],
        searchQuery: 'test',
      });

      const { clearSearch } = useQueryStore.getState();

      act(() => {
        clearSearch();
      });

      expect(useQueryStore.getState().searchResults).toEqual([]);
      expect(useQueryStore.getState().searchQuery).toBe('');
      expect(useQueryStore.getState().searchError).toBeNull();
    });

    it('should perform keyword search', async () => {
      const mockResults = [
        { id: '1', title: 'Note 1', content: 'Content 1', score: 0.9 },
      ];
      vi.mocked(queryApi.keywordSearch).mockResolvedValueOnce({
        query: 'test',
        results: mockResults,
        total: 1,
      });

      const { search } = useQueryStore.getState();

      await act(async () => {
        await search('test', 'keyword');
      });

      expect(queryApi.keywordSearch).toHaveBeenCalledWith('test', { limit: 10 });
      expect(useQueryStore.getState().searchResults).toEqual(mockResults);
      expect(useQueryStore.getState().isSearching).toBe(false);
    });

    it('should perform semantic search', async () => {
      const mockResults = [
        { id: '1', title: 'Semantic Note', content: 'Content', score: 0.95 },
      ];
      vi.mocked(queryApi.semanticSearch).mockResolvedValueOnce({
        query: 'meaning',
        results: mockResults,
        total: 1,
      });

      const { search } = useQueryStore.getState();

      await act(async () => {
        await search('meaning', 'semantic');
      });

      expect(queryApi.semanticSearch).toHaveBeenCalledWith('meaning', { topK: 5 });
      expect(useQueryStore.getState().searchResults).toEqual(mockResults);
    });

    it('should perform hybrid search', async () => {
      const mockResults = [
        { id: '1', title: 'Hybrid Note', content: 'Content', score: 0.92 },
      ];
      vi.mocked(queryApi.hybridSearch).mockResolvedValueOnce({
        query: 'test',
        results: mockResults,
        total: 1,
      });

      const { search } = useQueryStore.getState();

      await act(async () => {
        await search('test', 'hybrid');
      });

      expect(queryApi.hybridSearch).toHaveBeenCalledWith('test', {
        mode: 'balanced',
        topK: 5,
      });
      expect(useQueryStore.getState().searchResults).toEqual(mockResults);
    });

    it('should handle search errors', async () => {
      vi.mocked(queryApi.hybridSearch).mockRejectedValueOnce(
        new Error('Network error')
      );

      const { search } = useQueryStore.getState();

      await act(async () => {
        await search('test', 'hybrid');
      });

      expect(useQueryStore.getState().searchError).toBe('Network error');
      expect(useQueryStore.getState().isSearching).toBe(false);
    });

    it('should set isSearching flag during search', async () => {
      vi.mocked(queryApi.hybridSearch).mockResolvedValueOnce({
        query: 'test',
        results: [],
        total: 0,
      });

      const { search } = useQueryStore.getState();

      // Start the search
      let isSearchingDuringSearch: boolean | undefined;

      await act(async () => {
        // Fire the search and check state immediately
        const promise = search('test', 'hybrid');
        // isSearching should be true right after starting
        isSearchingDuringSearch = useQueryStore.getState().isSearching;
        await promise;
      });

      // During the search, isSearching should have been true
      expect(isSearchingDuringSearch).toBe(true);
      // After completion, isSearching should be false
      expect(useQueryStore.getState().isSearching).toBe(false);
    });
  });

  describe('Q&A Actions', () => {
    it('should ask a question and get answer', async () => {
      const mockResponse = {
        question: 'What is AI?',
        answer: 'AI stands for Artificial Intelligence.',
        sources: [{ id: '1', title: 'AI Notes', content: '...' }],
      };
      vi.mocked(queryApi.askQuestion).mockResolvedValueOnce(mockResponse);

      const { ask } = useQueryStore.getState();

      await act(async () => {
        await ask('What is AI?');
      });

      expect(queryApi.askQuestion).toHaveBeenCalledWith('What is AI?', { topK: 5 });
      expect(useQueryStore.getState().answer).toBe(
        'AI stands for Artificial Intelligence.'
      );
      expect(useQueryStore.getState().sources).toHaveLength(1);
    });

    it('should clear answer', () => {
      useQueryStore.setState({
        currentQuestion: 'test',
        answer: 'answer',
        sources: [{ id: '1', title: 'Test', content: 'test' }],
      });

      const { clearAnswer } = useQueryStore.getState();

      act(() => {
        clearAnswer();
      });

      expect(useQueryStore.getState().answer).toBe('');
      expect(useQueryStore.getState().sources).toEqual([]);
      expect(useQueryStore.getState().currentQuestion).toBe('');
    });
  });

  describe('Streaming Actions', () => {
    it('should start streaming question', async () => {
      const mockReader = {
        read: vi
          .fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode(
              'data: {"type":"text_delta","content":"Hello"}\n\n'
            ),
          })
          .mockResolvedValueOnce({
            done: true,
            value: undefined,
          }),
        releaseLock: vi.fn(),
      };

      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader },
      };

      vi
        .mocked(queryApi.askQuestionStream)
        .mockResolvedValueOnce(mockResponse as unknown as Response);

      const { askStream } = useQueryStore.getState();

      await act(async () => {
        await askStream('What is AI?');
      });

      expect(queryApi.askQuestionStream).toHaveBeenCalledWith(
        'What is AI?',
        expect.objectContaining({ topK: 5 })
      );
    });

    it('should handle streaming error', async () => {
      vi.mocked(queryApi.askQuestionStream).mockRejectedValueOnce(
        new Error('Stream failed')
      );

      const { askStream } = useQueryStore.getState();

      await act(async () => {
        await askStream('test');
      });

      expect(useQueryStore.getState().streamError).toBe('Stream failed');
    });

    it('should cancel streaming', () => {
      const mockAbort = vi.fn();
      useQueryStore.setState({
        abortController: { abort: mockAbort } as unknown as AbortController,
        isStreaming: true,
      });

      const { cancelStream } = useQueryStore.getState();

      act(() => {
        cancelStream();
      });

      expect(mockAbort).toHaveBeenCalled();
      expect(useQueryStore.getState().isStreaming).toBe(false);
      expect(useQueryStore.getState().abortController).toBeNull();
    });
  });

  describe('Suggestions Actions', () => {
    it('should fetch suggestions', async () => {
      vi.mocked(queryApi.getSuggestions).mockResolvedValueOnce({
        query: 'art',
        suggestions: ['artificial intelligence', 'art history'],
      });

      const { fetchSuggestions } = useQueryStore.getState();

      await act(async () => {
        await fetchSuggestions('art');
      });

      expect(queryApi.getSuggestions).toHaveBeenCalledWith('art', { limit: 5 });
      expect(useQueryStore.getState().suggestions).toEqual([
        'artificial intelligence',
        'art history',
      ]);
    });

    it('should clear suggestions', () => {
      useQueryStore.setState({
        suggestions: ['suggestion 1', 'suggestion 2'],
      });

      const { clearSuggestions } = useQueryStore.getState();

      act(() => {
        clearSuggestions();
      });

      expect(useQueryStore.getState().suggestions).toEqual([]);
    });

    it('should not fetch suggestions for short queries', async () => {
      const { fetchSuggestions } = useQueryStore.getState();

      await act(async () => {
        await fetchSuggestions('a');
      });

      expect(queryApi.getSuggestions).not.toHaveBeenCalled();
      expect(useQueryStore.getState().suggestions).toEqual([]);
    });
  });

  describe('State Selector Hooks', () => {
    describe('useHasResults', () => {
      it('should return false when no results', () => {
        useQueryStore.setState({ searchResults: [] });
        const { result } = renderHook(() => useHasResults());
        expect(result.current).toBe(false);
      });

      it('should return true when has results', () => {
        useQueryStore.setState({
          searchResults: [
            { id: '1', title: 'Test', content: 'test', score: 0.9 },
          ],
        });
        const { result } = renderHook(() => useHasResults());
        expect(result.current).toBe(true);
      });
    });

    describe('useHasAnswer', () => {
      it('should return false when no answer', () => {
        useQueryStore.setState({ answer: '' });
        const { result } = renderHook(() => useHasAnswer());
        expect(result.current).toBe(false);
      });

      it('should return true when has answer', () => {
        useQueryStore.setState({ answer: 'This is the answer' });
        const { result } = renderHook(() => useHasAnswer());
        expect(result.current).toBe(true);
      });
    });

    describe('useHasError', () => {
      it('should return false when no errors', () => {
        useQueryStore.setState({ searchError: null, streamError: null });
        const { result } = renderHook(() => useHasError());
        expect(result.current).toBe(false);
      });

      it('should return true when has search error', () => {
        useQueryStore.setState({ searchError: 'Search failed' });
        const { result } = renderHook(() => useHasError());
        expect(result.current).toBe(true);
      });

      it('should return true when has stream error', () => {
        useQueryStore.setState({
          searchError: null,
          streamError: 'Stream failed',
        });
        const { result } = renderHook(() => useHasError());
        expect(result.current).toBe(true);
      });
    });
  });
});