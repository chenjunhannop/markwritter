'use client';

/**
 * Query Page
 *
 * Main query interface with:
 * - Search input with mode selection
 * - Results list
 * - Q&A chat area for streaming responses
 */

import { useState, useCallback } from 'react';
import { SearchInput } from '@/components/query/search-input';
import { ResultsList } from '@/components/query/results-list';
import { QueryChatArea } from '@/components/query/query-chat-area';
import { useHasResults, useHasAnswer } from '@/lib/query-store';
import { cn } from '@/lib/utils';

export default function QueryPage() {
  const [view, setView] = useState<'search' | 'chat'>('search');
  // Use pre-defined selector hooks to avoid creating new object references
  const hasResults = useHasResults();
  const hasAnswer = useHasAnswer();

  const handleResultClick = useCallback(() => {
    // Switch to chat view when clicking a result
    setView('chat');
    // Could pre-fill a question about this result
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Query Your Notes
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Search through your notes or ask questions about your content.
          </p>
        </header>

        {/* Search Input */}
        <div className="mb-6">
          <SearchInput autoFocus />
        </div>

        {/* View Toggle */}
        {(hasResults || hasAnswer) && (
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setView('search')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                view === 'search'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              )}
            >
              Search Results
            </button>
            <button
              onClick={() => setView('chat')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                view === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              )}
            >
              Q&A Chat
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          {view === 'search' ? (
            <ResultsList onResultClick={handleResultClick} />
          ) : (
            <QueryChatArea />
          )}
        </div>
      </div>
    </div>
  );
}