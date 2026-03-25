'use client';

/**
 * ResultsList Component
 *
 * Displays search results with:
 * - Result cards with title, score, and preview
 * - Loading and error states
 * - Empty state
 * - Keyboard navigation
 * - XSS protection via DOMPurify for highlighted content
 */

import DOMPurify from 'dompurify';
import { FileText, AlertCircle, Loader2 } from 'lucide-react';
import { useQueryStore } from '@/lib/query-store';
import { cn } from '@/lib/utils';

interface ResultsListProps {
  className?: string;
  onResultClick?: () => void;
}

const MAX_CONTENT_LENGTH = 150;

/**
 * Sanitize HTML content to prevent XSS attacks
 * Allows safe HTML elements like mark, strong, em while removing dangerous content
 */
function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['mark', 'strong', 'em', 'b', 'i', 'span', 'code', 'a'],
    ALLOWED_ATTR: ['href', 'class'],
    ALLOW_DATA_ATTR: false,
    // Only allow safe URL schemes
    ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  });
}

export function ResultsList({ className, onResultClick }: ResultsListProps) {
  // Use individual selectors to avoid creating new object references
  const searchResults = useQueryStore((state) => state.searchResults);
  const isSearching = useQueryStore((state) => state.isSearching);
  const searchError = useQueryStore((state) => state.searchError);
  const searchQuery = useQueryStore((state) => state.searchQuery);

  // Loading state
  if (isSearching) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400">Searching...</p>
      </div>
    );
  }

  // Error state
  if (searchError) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <AlertCircle className="w-8 h-8 text-red-500 mb-4" />
        <p className="text-red-500 font-medium">Error</p>
        <p className="text-gray-500 dark:text-gray-400 text-sm">{searchError}</p>
      </div>
    );
  }

  // Empty state
  if (searchResults.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <FileText className="w-8 h-8 text-gray-300 dark:text-gray-600 mb-4" />
        <p className="text-gray-500 dark:text-gray-400">
          {searchQuery ? 'No results found' : 'Enter a search query to get started'}
        </p>
      </div>
    );
  }

  // Format score as percentage
  const formatScore = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  // Truncate content
  const truncateContent = (content: string): string => {
    if (content.length <= MAX_CONTENT_LENGTH) return content;
    return content.slice(0, MAX_CONTENT_LENGTH) + '...';
  };

  const handleResultClick = () => {
    onResultClick?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleResultClick();
    }
  };

  return (
    <div className={cn('space-y-2', className)}>
      {/* Results count */}
      {searchQuery && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for &ldquo;{searchQuery}&rdquo;
        </p>
      )}

      {/* Results list */}
      <ul role="list" aria-label="Search results" className="space-y-2">
        {searchResults.map((result) => (
          <li key={result.id} role="listitem">
            <button
              onClick={handleResultClick}
              onKeyDown={handleKeyDown}
              className="w-full text-left p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              {/* Title and score */}
              <div className="flex items-start justify-between gap-4 mb-2">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                  {result.title || <span className="text-gray-400">Untitled</span>}
                </h3>
                {result.score !== undefined && (
                  <span className="shrink-0 text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                    {formatScore(result.score)}
                  </span>
                )}
              </div>

              {/* Content preview */}
              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {truncateContent(result.content)}
              </p>

              {/* Highlighted content if available - sanitized for XSS prevention */}
              {result.highlighted && (
                <div
                  className="mt-2 text-sm text-gray-600 dark:text-gray-400"
                  dangerouslySetInnerHTML={{ __html: sanitizeHtml(result.highlighted) }}
                />
              )}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}