/**
 * Tests for SearchInput Component
 *
 * Tests the search input component functionality including:
 * - User input handling
 * - Search mode switching
 * - Basic rendering
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';

// Mock the query store
const mockSearch = vi.fn();
const mockSetSearchMode = vi.fn();
const mockFetchSuggestions = vi.fn();
const mockClearSuggestions = vi.fn();

// Create a mutable state object for tests to modify
let mockStoreState = {
  searchQuery: '',
  searchMode: 'hybrid' as const,
  isSearching: false,
  suggestions: [] as string[],
  search: mockSearch,
  setSearchMode: mockSetSearchMode,
  fetchSuggestions: mockFetchSuggestions,
  clearSuggestions: mockClearSuggestions,
};

vi.mock('@/lib/query-store', () => ({
  useQueryStore: vi.fn((selector: (state: typeof mockStoreState) => unknown) =>
    selector(mockStoreState)
  ),
}));

// Import after mocking
import { SearchInput } from './search-input';

describe('SearchInput', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    // Reset store state
    mockStoreState = {
      searchQuery: '',
      searchMode: 'hybrid',
      isSearching: false,
      suggestions: [],
      search: mockSearch,
      setSearchMode: mockSetSearchMode,
      fetchSuggestions: mockFetchSuggestions,
      clearSuggestions: mockClearSuggestions,
    };
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Rendering', () => {
    it('should render search input field', () => {
      render(<SearchInput />);

      expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument();
    });

    it('should render search mode selector', () => {
      render(<SearchInput />);

      expect(
        screen.getByRole('combobox', { name: /search mode/i })
      ).toBeInTheDocument();
    });

    it('should show search button', () => {
      render(<SearchInput />);

      expect(screen.getByRole('button', { name: /^search$/i })).toBeInTheDocument();
    });

    it('should show loading state while searching', () => {
      mockStoreState = {
        ...mockStoreState,
        searchQuery: 'test',
        isSearching: true,
      };

      render(<SearchInput />);

      expect(screen.getByRole('button', { name: /searching/i })).toBeDisabled();
    });
  });

  describe('Input Handling', () => {
    it('should update input value on typing', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'test query' } });

      expect(input).toHaveValue('test query');
    });

    it('should trigger search on form submit', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'test' } });

      const form = input.closest('form')!;
      fireEvent.submit(form);

      expect(mockSearch).toHaveBeenCalledWith('test', 'hybrid');
    });

    it('should trigger search on search button click', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'test' } });

      const searchButton = screen.getByRole('button', { name: /^search$/i });
      fireEvent.click(searchButton);

      expect(mockSearch).toHaveBeenCalledWith('test', 'hybrid');
    });

    it('should not search with empty query', () => {
      render(<SearchInput />);

      const searchButton = screen.getByRole('button', { name: /^search$/i });
      fireEvent.click(searchButton);

      expect(mockSearch).not.toHaveBeenCalled();
    });

    it('should clear input on clear button click', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'test' } });

      const clearButton = screen.getByRole('button', { name: /clear/i });
      fireEvent.click(clearButton);

      expect(input).toHaveValue('');
      expect(mockClearSuggestions).toHaveBeenCalled();
    });
  });

  describe('Mode Selection', () => {
    it('should change search mode', () => {
      render(<SearchInput />);

      const modeSelector = screen.getByRole('combobox', { name: /search mode/i });
      fireEvent.change(modeSelector, { target: { value: 'keyword' } });

      expect(mockSetSearchMode).toHaveBeenCalledWith('keyword');
    });

    it('should display current search mode', () => {
      mockStoreState = {
        ...mockStoreState,
        searchMode: 'semantic',
      };

      render(<SearchInput />);

      const modeSelector = screen.getByRole('combobox', { name: /search mode/i });
      expect(modeSelector).toHaveValue('semantic');
    });
  });

  describe('Suggestions', () => {
    it('should call fetchSuggestions when typing (debounced)', async () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'art' } });

      // Advance timers to trigger debounce
      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(mockFetchSuggestions).toHaveBeenCalledWith('art');
    });

    it('should not fetch suggestions for short queries', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'a' } });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(mockFetchSuggestions).not.toHaveBeenCalled();
    });

    it('should clear suggestions when input is cleared', () => {
      render(<SearchInput />);

      const input = screen.getByPlaceholderText(/search/i);
      fireEvent.change(input, { target: { value: 'art' } });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Clear input
      fireEvent.change(input, { target: { value: '' } });

      expect(mockClearSuggestions).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible form elements', () => {
      render(<SearchInput />);

      expect(screen.getByRole('combobox', { name: /search mode/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^search$/i })).toBeInTheDocument();
    });

    it('should disable search button when searching', () => {
      mockStoreState = {
        ...mockStoreState,
        isSearching: true,
      };

      render(<SearchInput />);

      const searchButton = screen.getByRole('button', { name: /searching/i });
      expect(searchButton).toBeDisabled();
    });
  });
});