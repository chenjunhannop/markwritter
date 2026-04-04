'use client';

/**
 * AnswerContextPanel - Right rail panel showing citation sources for chat messages.
 * Lists source cards with file_path, page_num, and text_snippet.
 * Clicking a citation number highlights the corresponding card.
 */

import { useMemo, useState, useCallback } from 'react';
import { ChevronRight, FileText, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { useChatStore, useUIStore } from '@/lib/store';
import type { Citation } from '@/lib/types';

/** Indexed citation paired with its 1-based display number */
interface IndexedCitation {
  readonly number: number;
  readonly citation: Citation;
}

/**
 * Collects all citations from assistant messages in the current session,
 * assigning sequential 1-based numbers.
 */
function useCitationsFromCurrentSession(): IndexedCitation[] {
  const sessions = useChatStore((s) => s.sessions);
  const currentSessionId = useChatStore((s) => s.currentSessionId);

  return useMemo(() => {
    const session = sessions.find((s) => s.id === currentSessionId);
    if (!session) return [];

    const allCitations: IndexedCitation[] = [];
    let index = 1;

    for (const message of session.messages) {
      if (message.role === 'assistant' && message.citations) {
        for (const citation of message.citations) {
          allCitations.push({ number: index, citation });
          index += 1;
        }
      }
    }

    return allCitations;
  }, [sessions, currentSessionId]);
}

/**
 * Extracts a short filename from a full file path.
 */
function getFileName(filePath: string): string {
  const segments = filePath.split('/');
  return segments[segments.length - 1] || filePath;
}

/**
 * Empty state shown when no messages with citations exist.
 */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
      <BookOpen className="h-10 w-10 mb-3 opacity-30" />
      <p className="text-sm font-medium mb-1">No citations yet</p>
      <p className="text-xs text-center max-w-[200px] leading-relaxed">
        Citation sources from assistant responses will appear here.
      </p>
    </div>
  );
}

/**
 * Single source card displaying citation details.
 */
function SourceCard({
  indexed,
  isActive,
  onClick,
}: {
  readonly indexed: IndexedCitation;
  readonly isActive: boolean;
  readonly onClick: () => void;
}) {
  const { number, citation } = indexed;
  const fileName = getFileName(citation.file_path);

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'w-full rounded-lg p-3 text-left transition-all',
        'hover:bg-muted/50',
        isActive && 'ring-2 ring-primary bg-muted/30'
      )}
      aria-label={`Citation source ${number}: ${fileName}`}
    >
      <div className="flex items-start gap-2.5">
        <Badge
          variant="secondary"
          className="shrink-0 h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[11px] font-medium"
        >
          {number}
        </Badge>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            <span className="text-xs font-medium text-foreground truncate">
              {fileName}
            </span>
          </div>
          {citation.page_num > 0 && (
            <span className="mt-0.5 block text-[11px] text-muted-foreground">
              Page {citation.page_num}
            </span>
          )}
          {citation.text_snippet && (
            <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground line-clamp-3">
              {citation.text_snippet}
            </p>
          )}
        </div>
      </div>
    </button>
  );
}

export function AnswerContextPanel() {
  const toggleRightPanel = useUIStore((s) => s.toggleRightPanel);
  const citations = useCitationsFromCurrentSession();
  const [activeNumber, setActiveNumber] = useState<number | null>(null);

  const handleCardClick = useCallback((number: number) => {
    setActiveNumber((prev) => (prev === number ? null : number));
  }, []);

  if (citations.length === 0) {
    return (
      <div className="flex h-full flex-col">
        <div className="flex h-[42px] shrink-0 items-center justify-between border-b px-3">
          <span className="text-[13px] font-semibold">Answer Context</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleRightPanel}
            className="h-7 w-7"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Panel Header */}
      <div className="flex h-[42px] shrink-0 items-center justify-between border-b px-3">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-semibold">Answer Context</span>
          <Badge variant="secondary" className="h-5 px-1.5 text-[11px]">
            {citations.length}
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleRightPanel}
          className="h-7 w-7"
        >
          <ChevronRight className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Citation List */}
      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-1 p-2">
          {citations.map((indexed) => (
            <SourceCard
              key={`${indexed.number}-${indexed.citation.file_path}`}
              indexed={indexed}
              isActive={activeNumber === indexed.number}
              onClick={() => handleCardClick(indexed.number)}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
