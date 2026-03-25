'use client';

/**
 * SearchInput Component
 *
 * A search input component with:
 * - Search mode selector (keyword/semantic/hybrid)
 * - Real-time suggestions
 * - Keyboard navigation
 * - Loading state
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { useQueryStore } from '@/lib/query-store';
import { cn } from '@/lib/utils';

interface SearchInputProps {
  className?: string;
  autoFocus?: boolean;
}

export function SearchInput({ className, autoFocus = false }: SearchInputProps) {
  const [localQuery, setLocalQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  // Use individual selectors to avoid creating new object references
  const searchMode = useQueryStore((state) => state.searchMode);
  const isSearching = useQueryStore((state) => state.isSearching);
  const suggestions = useQueryStore((state) => state.suggestions);
  const search = useQueryStore((state) => state.search);
  const setSearchMode = useQueryStore((state) => state.setSearchMode);
  const fetchSuggestions = useQueryStore((state) => state.fetchSuggestions);
  const clearSuggestions = useQueryStore((state) => state.clearSuggestions);

  // Fetch suggestions with debounce
  useEffect(() => {
    if (localQuery.length >= 2) {
      const timer = setTimeout(() => {
        fetchSuggestions(localQuery);
        setShowSuggestions(true);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setShowSuggestions(false);
      clearSuggestions();
    }
  }, [localQuery, fetchSuggestions, clearSuggestions]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setLocalQuery(e.target.value);
      setHighlightedIndex(-1);
    },
    []
  );

  const handleSearch = useCallback(
    (query: string) => {
      if (query.trim()) {
        search(query.trim(), searchMode);
        setShowSuggestions(false);
        clearSuggestions();
      }
    },
    [search, searchMode, clearSuggestions]
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      handleSearch(localQuery);
    },
    [handleSearch, localQuery]
  );

  const handleClear = useCallback(() => {
    setLocalQuery('');
    setShowSuggestions(false);
    clearSuggestions();
    inputRef.current?.focus();
  }, [clearSuggestions]);

  const handleModeChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setSearchMode(e.target.value as 'keyword' | 'semantic' | 'hybrid');
    },
    [setSearchMode]
  );

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      setLocalQuery(suggestion);
      handleSearch(suggestion);
    },
    [handleSearch]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!showSuggestions || suggestions.length === 0) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setHighlightedIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;

        case 'ArrowUp':
          e.preventDefault();
          setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;

        case 'Enter':
          e.preventDefault();
          if (highlightedIndex >= 0) {
            handleSuggestionClick(suggestions[highlightedIndex]);
          } else {
            handleSearch(localQuery);
          }
          break;

        case 'Escape':
          setShowSuggestions(false);
          setHighlightedIndex(-1);
          break;
      }
    },
    [showSuggestions, suggestions, highlightedIndex, handleSuggestionClick, handleSearch, localQuery]
  );

  const handleBlur = useCallback(() => {
    // Delay to allow suggestion clicks to register
    setTimeout(() => {
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    }, 200);
  }, []);

  const handleFocus = useCallback(() => {
    if (localQuery.length >= 2 && suggestions.length > 0) {
      setShowSuggestions(true);
    }
  }, [localQuery.length, suggestions.length]);

  return (
    <div className={cn('relative', className)}>
      <form onSubmit={handleSubmit} className="flex gap-2">
        {/* Search Mode Selector */}
        <select
          name="searchMode"
          aria-label="Search mode"
          value={searchMode}
          onChange={handleModeChange}
          className="h-10 px-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="hybrid">Hybrid</option>
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
        </select>

        {/* Search Input */}
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            placeholder="Search your notes..."
            value={localQuery}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onBlur={handleBlur}
            onFocus={handleFocus}
            autoFocus={autoFocus}
            className="w-full h-10 pl-10 pr-10 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          {/* Search Icon */}
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />

          {/* Clear Button */}
          {localQuery && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Clear search"
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={isSearching || !localQuery.trim()}
          aria-label={isSearching ? 'Searching' : 'Search'}
          className="h-10 px-4 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSearching ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
        </button>
      </form>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <ul
          className="absolute z-10 w-full mt-1 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg"
          role="listbox"
        >
          {suggestions.map((suggestion, index) => (
            <li key={suggestion}>
              <button
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={cn(
                  'w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700',
                  highlightedIndex === index && 'bg-gray-100 dark:bg-gray-700'
                )}
                role="option"
                aria-selected={highlightedIndex === index}
              >
                {suggestion}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}