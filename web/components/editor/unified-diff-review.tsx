'use client';

/**
 * UnifiedDiffReview Component (WRT-005-V2)
 *
 * Replaces DiffPreview with a unified diff view showing change blocks.
 * Each DiffDelta operation is rendered as a collapsible block with:
 * - Added lines: green background
 * - Removed lines: red background with strikethrough
 * - Replaced lines: red-to-green transition
 *
 * Actions: Accept All (green), Reject (outline), Accept Block (per block).
 * Stats bar shows additions, deletions, and character count change.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  ChevronDown,
  ChevronRight,
  Check,
  X,
  Plus,
  Minus,
  RefreshCw,
} from 'lucide-react';
import type { DiffDelta } from '@/lib/record-api';

// ==================== Types ====================

interface UnifiedDiffReviewProps {
  /** The diff operations from AI response */
  diff: DiffDelta[];
  /** Original content (before AI changes) */
  original: string;
  /** Modified content (after AI changes) */
  modified: string;
  /** Accept all changes */
  onAccept: () => void;
  /** Reject all changes, restore original */
  onReject: () => void;
  /** Accept specific block by index, returns new content */
  onAcceptBlock?: (blockIndex: number) => void;
  /** Optional className for the container */
  className?: string;
}

interface DiffStats {
  additions: number;
  deletions: number;
  charDelta: number;
}

interface BlockState {
  expanded: boolean;
  accepted: boolean;
}

// ==================== Helpers ====================

/**
 * Count the number of lines in a string.
 */
function countLines(text: string): number {
  if (text.length === 0) return 0;
  return text.split('\n').length;
}

/**
 * Compute diff statistics from DiffDelta operations.
 */
function computeStats(diff: DiffDelta[], original: string, modified: string): DiffStats {
  let additions = 0;
  let deletions = 0;

  for (const delta of diff) {
    switch (delta.type) {
      case 'add':
        additions += countLines(delta.text);
        break;
      case 'remove':
        deletions += countLines(delta.original ?? delta.text);
        break;
      case 'replace':
        deletions += countLines(delta.original ?? '');
        additions += countLines(delta.text);
        break;
    }
  }

  return {
    additions,
    deletions,
    charDelta: modified.length - original.length,
  };
}

/**
 * Get a human-readable label for a delta type.
 */
function getDeltaTypeLabel(type: string): string {
  switch (type) {
    case 'add':
      return 'Addition';
    case 'remove':
      return 'Deletion';
    case 'replace':
      return 'Replacement';
    default:
      return 'Change';
  }
}

/**
 * Get badge variant for a delta type.
 */
function getDeltaBadgeVariant(
  type: string
): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (type) {
    case 'add':
      return 'secondary';
    case 'remove':
      return 'destructive';
    case 'replace':
      return 'default';
    default:
      return 'outline';
  }
}

/**
 * Split text into lines for rendering with line numbers.
 */
function splitLines(text: string): string[] {
  if (text.length === 0) return [];
  return text.split('\n');
}

// ==================== Sub-Components ====================

interface DiffLineProps {
  line: string;
  lineNum: number;
  variant: 'added' | 'removed' | 'context';
}

function DiffLine({ line, lineNum, variant }: DiffLineProps) {
  return (
    <div
      className={cn(
        'flex font-mono text-xs leading-5',
        variant === 'added' && 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-300',
        variant === 'removed' && 'bg-red-50 text-red-800 dark:bg-red-950/30 dark:text-red-300 line-through',
      )}
    >
      <span
        className={cn(
          'select-none shrink-0 w-10 text-right pr-2 border-r border-border/50',
          variant === 'added' && 'text-emerald-500 dark:text-emerald-400',
          variant === 'removed' && 'text-red-500 dark:text-red-400',
        )}
      >
        {lineNum}
      </span>
      <span
        className={cn(
          'shrink-0 w-5 text-center',
          variant === 'added' && 'text-emerald-600 dark:text-emerald-400',
          variant === 'removed' && 'text-red-600 dark:text-red-400',
        )}
      >
        {variant === 'added' && '+'}
        {variant === 'removed' && '-'}
      </span>
      <span className="px-2 whitespace-pre-wrap break-all">{line}</span>
    </div>
  );
}

interface ChangeBlockProps {
  delta: DiffDelta;
  blockIndex: number;
  expanded: boolean;
  accepted: boolean;
  onToggleExpand: (index: number) => void;
  onAcceptBlock: (index: number) => void;
  /** Line number offset for context */
  lineOffset: number;
}

function ChangeBlock({
  delta,
  blockIndex,
  expanded,
  accepted,
  onToggleExpand,
  onAcceptBlock,
  lineOffset,
}: ChangeBlockProps) {
  const originalLines = splitLines(delta.original ?? '');
  const newTextLines = splitLines(delta.text);

  const isReplace = delta.type === 'replace';
  const isRemove = delta.type === 'remove';
  const isAdd = delta.type === 'add';

  return (
    <div
      className={cn(
        'border rounded-md overflow-hidden',
        accepted && 'opacity-50',
        isAdd && 'border-l-2 border-l-emerald-400 dark:border-l-emerald-600',
        isRemove && 'border-l-2 border-l-red-400 dark:border-l-red-600',
        isReplace && 'border-l-2 border-l-blue-400 dark:border-l-blue-600',
      )}
    >
      {/* Block header */}
      <button
        type="button"
        onClick={() => onToggleExpand(blockIndex)}
        className={cn(
          'flex items-center gap-2 w-full px-3 py-2 text-xs font-medium',
          'bg-muted/50 hover:bg-muted transition-colors text-left',
        )}
      >
        {expanded ? (
          <ChevronDown className="h-3 w-3 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-3 w-3 shrink-0 text-muted-foreground" />
        )}

        <Badge
          variant={getDeltaBadgeVariant(delta.type)}
          className="text-[10px] h-4 px-1.5"
        >
          {delta.type === 'add' && <Plus className="h-2.5 w-2.5 mr-0.5" />}
          {delta.type === 'remove' && <Minus className="h-2.5 w-2.5 mr-0.5" />}
          {delta.type === 'replace' && <RefreshCw className="h-2.5 w-2.5 mr-0.5" />}
          {getDeltaTypeLabel(delta.type)}
        </Badge>

        <span className="text-muted-foreground truncate flex-1">
          {isReplace && `${originalLines.length} line${originalLines.length !== 1 ? 's' : ''} replaced`}
          {isAdd && `${newTextLines.length} line${newTextLines.length !== 1 ? 's' : ''} added`}
          {isRemove && `${originalLines.length} line${originalLines.length !== 1 ? 's' : ''} removed`}
        </span>

        {!accepted && (
          <span
            role="button"
            tabIndex={0}
            onClick={(e) => {
              e.stopPropagation();
              onAcceptBlock(blockIndex);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.stopPropagation();
                onAcceptBlock(blockIndex);
              }
            }}
            className={cn(
              'shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px]',
              'text-emerald-600 hover:bg-emerald-100 dark:text-emerald-400 dark:hover:bg-emerald-900/30',
              'transition-colors cursor-pointer',
            )}
          >
            <Check className="h-3 w-3" />
            Accept
          </span>
        )}

        {accepted && (
          <span className="shrink-0 text-[10px] text-muted-foreground flex items-center gap-1">
            <Check className="h-3 w-3" />
            Accepted
          </span>
        )}
      </button>

      {/* Block content (collapsible) */}
      {expanded && (
        <div className="border-t">
          {/* Removed lines (for replace/remove) */}
          {(isRemove || isReplace) && originalLines.length > 0 && (
            <div className="bg-red-50/50 dark:bg-red-950/20">
              {originalLines.map((line, i) => (
                <DiffLine
                  key={`rem-${blockIndex}-${i}`}
                  line={line}
                  lineNum={lineOffset + i + 1}
                  variant="removed"
                />
              ))}
            </div>
          )}

          {/* Added lines (for add/replace) */}
          {(isAdd || isReplace) && newTextLines.length > 0 && (
            <div className="bg-emerald-50/50 dark:bg-emerald-950/20">
              {newTextLines.map((line, i) => (
                <DiffLine
                  key={`add-${blockIndex}-${i}`}
                  line={line}
                  lineNum={lineOffset + i + 1}
                  variant="added"
                />
              ))}
            </div>
          )}

          {/* Error delta fallback */}
          {delta.type === 'error' && (
            <div className="px-3 py-2 text-xs text-destructive bg-destructive/10">
              {delta.text}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface StatsBarProps {
  stats: DiffStats;
}

function StatsBar({ stats }: StatsBarProps) {
  const parts: string[] = [];

  if (stats.additions > 0) {
    parts.push(`${stats.additions} addition${stats.additions !== 1 ? 's' : ''}`);
  }
  if (stats.deletions > 0) {
    parts.push(`${stats.deletions} deletion${stats.deletions !== 1 ? 's' : ''}`);
  }

  const charSign = stats.charDelta >= 0 ? '+' : '';
  const charDisplay = `${charSign}${stats.charDelta} chars`;

  if (parts.length === 0) {
    return (
      <div className="text-xs text-muted-foreground px-4 py-2">
        No changes detected
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 text-xs px-4 py-2 border-t border-border bg-muted/30">
      {stats.additions > 0 && (
        <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
          <Plus className="h-3 w-3" />
          {stats.additions}
        </span>
      )}
      {stats.deletions > 0 && (
        <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
          <Minus className="h-3 w-3" />
          {stats.deletions}
        </span>
      )}
      <span className="text-muted-foreground">
        ({charDisplay})
      </span>
    </div>
  );
}

// ==================== Main Component ====================

export function UnifiedDiffReview({
  diff,
  original,
  modified,
  onAccept,
  onReject,
  onAcceptBlock,
  className,
}: UnifiedDiffReviewProps) {
  const [blockStates, setBlockStates] = useState<BlockState[]>(
    () => diff.map(() => ({ expanded: true, accepted: false }))
  );

  const stats = useMemo(
    () => computeStats(diff, original, modified),
    [diff, original, modified]
  );

  const allAccepted = blockStates.every((s) => s.accepted);
  const someAccepted = blockStates.some((s) => s.accepted);

  const handleToggleExpand = useCallback((index: number) => {
    setBlockStates((prev) =>
      prev.map((s, i) =>
        i === index ? { ...s, expanded: !s.expanded } : s
      )
    );
  }, []);

  const handleAcceptBlock = useCallback(
    (index: number) => {
      setBlockStates((prev) =>
        prev.map((s, i) =>
          i === index ? { ...s, accepted: true } : s
        )
      );
      if (onAcceptBlock) {
        onAcceptBlock(index);
      }
    },
    [onAcceptBlock]
  );

  const handleCollapseAll = useCallback(() => {
    setBlockStates((prev) =>
      prev.map((s) => ({ ...s, expanded: false }))
    );
  }, []);

  const handleExpandAll = useCallback(() => {
    setBlockStates((prev) =>
      prev.map((s) => ({ ...s, expanded: true }))
    );
  }, []);

  // Compute line offsets for each block based on original content
  const lineOffsets = useMemo(() => {
    const offsets: number[] = [];
    let runningOffset = 0;
    for (const delta of diff) {
      offsets.push(runningOffset);
      if (delta.type === 'remove' || delta.type === 'replace') {
        runningOffset += countLines(delta.original ?? '');
      }
    }
    return offsets;
  }, [diff]);

  if (diff.length === 0) {
    return (
      <div
        className={cn(
          'border rounded-lg bg-card text-card-foreground',
          className,
        )}
      >
        <div className="px-4 py-3 text-sm text-muted-foreground text-center">
          No changes detected between original and modified content.
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'border rounded-lg bg-card text-card-foreground overflow-hidden',
        className,
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b bg-muted/50">
        <h3 className="text-sm font-medium">
          AI Change Review
        </h3>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={handleExpandAll}
            className="text-[10px] text-muted-foreground hover:text-foreground transition-colors px-1.5 py-0.5"
          >
            Expand All
          </button>
          <span className="text-muted-foreground text-[10px]">|</span>
          <button
            type="button"
            onClick={handleCollapseAll}
            className="text-[10px] text-muted-foreground hover:text-foreground transition-colors px-1.5 py-0.5"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Change blocks */}
      <div className="max-h-80 overflow-y-auto p-2 space-y-2">
        {diff.map((delta, index) => (
          <ChangeBlock
            key={`block-${index}`}
            delta={delta}
            blockIndex={index}
            expanded={blockStates[index]?.expanded ?? true}
            accepted={blockStates[index]?.accepted ?? false}
            onToggleExpand={handleToggleExpand}
            onAcceptBlock={handleAcceptBlock}
            lineOffset={lineOffsets[index] ?? 0}
          />
        ))}
      </div>

      {/* Stats bar */}
      <StatsBar stats={stats} />

      {/* Action bar */}
      <div className="flex items-center justify-between px-4 py-3 border-t bg-muted/30">
        <span className="text-xs text-muted-foreground">
          {diff.length} change{diff.length !== 1 ? 's' : ''}
          {someAccepted && ` (${blockStates.filter((s) => s.accepted).length} accepted)`}
        </span>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onReject}
            className="flex items-center gap-1.5"
          >
            <X className="h-3.5 w-3.5" />
            Reject
          </Button>
          <Button
            size="sm"
            onClick={onAccept}
            disabled={allAccepted}
            className={cn(
              'flex items-center gap-1.5',
              'bg-emerald-600 hover:bg-emerald-700 text-white',
              'dark:bg-emerald-700 dark:hover:bg-emerald-600',
            )}
          >
            <Check className="h-3.5 w-3.5" />
            Accept All
          </Button>
        </div>
      </div>
    </div>
  );
}
