'use client';

import { useState, useCallback } from 'react';
import { AppShell } from '@/components/apple';
import { FloatingPanel } from '@/components/apple';
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
    <AppShell title="Knowledge Query" statusBadge="Answer Mode">
      <div className="py-4">
        {(hasResults || hasAnswer) && (
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setView('search')}
              className={cn(
                'px-4 py-2 rounded-full text-sm font-medium transition-colors',
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
                'px-4 py-2 rounded-full text-sm font-medium transition-colors',
                view === 'chat'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              )}
            >
              Q&A Chat
            </button>
          </div>
        )}

        <FloatingPanel className="p-6">
          {view === 'search' ? (
            <ResultsList onResultClick={handleResultClick} />
          ) : (
            <QueryChatArea />
          )}
        </FloatingPanel>
      </div>
    </AppShell>
  );
}
