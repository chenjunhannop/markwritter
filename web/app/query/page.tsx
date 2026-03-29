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
import { MainLayout } from '@/components/layout';
import { SearchInput } from '@/components/query/search-input';
import { ResultsList } from '@/components/query/results-list';
import { QueryChatArea } from '@/components/query/query-chat-area';
import { useHasResults, useHasAnswer } from '@/lib/query-store';
import { cn } from '@/lib/utils';

export default function QueryPage() {
  const [view, setView] = useState<'search' | 'chat'>('search');
  const hasResults = useHasResults();
  const hasAnswer = useHasAnswer();

  const handleResultClick = useCallback(() => {
    setView('chat');
  }, []);

  return (
    <MainLayout title="Query">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* View Toggle */}
        {(hasResults || hasAnswer) && (
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setView('search')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                view === 'search'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              )}
            >
              Search Results
            </button>
            <button
              onClick={() => setView('chat')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                view === 'chat'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              )}
            >
              Q&A Chat
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="bg-background rounded-xl shadow-sm border p-6">
          {view === 'search' ? (
            <ResultsList onResultClick={handleResultClick} />
          ) : (
            <QueryChatArea />
          )}
        </div>
      </div>
    </MainLayout>
  );
}
