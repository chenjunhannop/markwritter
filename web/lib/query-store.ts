/**
 * Query Store for Markwritter
 *
 * Zustand store for managing query state including:
 * - Search results and search state
 * - Q&A conversations
 * - Streaming state
 * - Search suggestions
 */

import { create } from 'zustand';
import {
  keywordSearch,
  semanticSearch,
  hybridSearch,
  askQuestion,
  askQuestionStream,
  getSuggestions,
  type SearchResult,
  type SourceReference,
} from './query-api';
import { processSSEStream } from './sse';

// ==================== Types ====================

export type SearchMode = 'keyword' | 'semantic' | 'hybrid';

interface QueryState {
  // Search state
  searchQuery: string;
  searchResults: SearchResult[];
  searchMode: SearchMode;
  isSearching: boolean;
  searchError: string | null;

  // Q&A state
  currentQuestion: string;
  answer: string;
  sources: SourceReference[];
  isStreaming: boolean;
  streamError: string | null;
  abortController: AbortController | null;

  // Suggestions state
  suggestions: string[];
  isFetchingSuggestions: boolean;

  // Search actions
  setSearchQuery: (query: string) => void;
  setSearchMode: (mode: SearchMode) => void;
  search: (query: string, mode?: SearchMode) => Promise<void>;
  clearSearch: () => void;

  // Q&A actions
  ask: (question: string) => Promise<void>;
  askStream: (question: string) => Promise<void>;
  cancelStream: () => void;
  clearAnswer: () => void;

  // Suggestions actions
  fetchSuggestions: (query: string) => Promise<void>;
  clearSuggestions: () => void;
}

// ==================== Store ====================

export const useQueryStore = create<QueryState>()((set, get) => ({
  // Initial state
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
  abortController: null,

  suggestions: [],
  isFetchingSuggestions: false,

  // Search actions
  setSearchQuery: (query) => {
    set({ searchQuery: query });
  },

  setSearchMode: (mode) => {
    set({ searchMode: mode });
  },

  search: async (query, mode) => {
    const searchMode = mode ?? get().searchMode;

    set({
      isSearching: true,
      searchError: null,
      searchQuery: query,
    });

    try {
      let response;

      switch (searchMode) {
        case 'keyword':
          response = await keywordSearch(query, { limit: 10 });
          break;
        case 'semantic':
          response = await semanticSearch(query, { topK: 5 });
          break;
        case 'hybrid':
        default:
          response = await hybridSearch(query, { mode: 'balanced', topK: 5 });
          break;
      }

      set({
        searchResults: response.results,
        isSearching: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Search failed';
      set({
        searchError: message,
        isSearching: false,
      });
    }
  },

  clearSearch: () => {
    set({
      searchQuery: '',
      searchResults: [],
      searchError: null,
    });
  },

  // Q&A actions
  ask: async (question) => {
    set({
      currentQuestion: question,
      answer: '',
      sources: [],
      streamError: null,
    });

    try {
      const response = await askQuestion(question, { topK: 5 });

      set({
        answer: response.answer,
        sources: response.sources,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to get answer';
      set({
        streamError: message,
      });
    }
  },

  askStream: async (question) => {
    // Cancel any existing stream
    const existingController = get().abortController;
    if (existingController) {
      existingController.abort();
    }

    const controller = new AbortController();

    set({
      currentQuestion: question,
      answer: '',
      sources: [],
      isStreaming: true,
      streamError: null,
      abortController: controller,
    });

    try {
      const response = await askQuestionStream(question, {
        signal: controller.signal,
        topK: 5,
      });

      await processSSEStream(
        response,
        (event) => {
          const state = get();

          switch (event.type) {
            case 'text_delta':
              set({
                answer: state.answer + event.content,
              });
              break;

            case 'sources':
              if (event.sources) {
                set({
                  sources: event.sources,
                });
              }
              break;

            case 'error':
              set({
                streamError: event.content,
                isStreaming: false,
              });
              break;

            case 'done':
              set({
                isStreaming: false,
              });
              break;
          }
        },
        controller.signal
      );
    } catch (error) {
      if (error instanceof Error && error.message === 'Aborted') {
        // User cancelled, don't show error
        return;
      }

      const message = error instanceof Error ? error.message : 'Streaming failed';
      set({
        streamError: message,
        isStreaming: false,
      });
    } finally {
      set({
        isStreaming: false,
        abortController: null,
      });
    }
  },

  cancelStream: () => {
    const controller = get().abortController;
    if (controller) {
      controller.abort();
    }

    set({
      isStreaming: false,
      abortController: null,
    });
  },

  clearAnswer: () => {
    set({
      currentQuestion: '',
      answer: '',
      sources: [],
      streamError: null,
    });
  },

  // Suggestions actions
  fetchSuggestions: async (query) => {
    // Don't fetch for very short queries
    if (query.length < 2) {
      set({ suggestions: [] });
      return;
    }

    set({ isFetchingSuggestions: true });

    try {
      const response = await getSuggestions(query, { limit: 5 });

      set({
        suggestions: response.suggestions,
        isFetchingSuggestions: false,
      });
    } catch {
      // Silently fail suggestions
      set({
        suggestions: [],
        isFetchingSuggestions: false,
      });
    }
  },

  clearSuggestions: () => {
    set({ suggestions: [] });
  },
}));

// ==================== Selector Hooks ====================

/**
 * Selector hook for checking if there are search results.
 */
export function useHasResults(): boolean {
  return useQueryStore((state) => state.searchResults.length > 0);
}

/**
 * Selector hook for checking if there is an answer.
 */
export function useHasAnswer(): boolean {
  return useQueryStore((state) => state.answer.length > 0);
}

/**
 * Selector hook for checking if there is an error.
 */
export function useHasError(): boolean {
  return useQueryStore(
    (state) => state.searchError !== null || state.streamError !== null
  );
}