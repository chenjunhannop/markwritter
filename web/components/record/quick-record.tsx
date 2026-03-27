'use client';

/**
 * Quick Record Component
 *
 * A simplified interface for quickly creating notes.
 */

import { useCallback, type FormEvent, type KeyboardEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useRecordStore } from '@/lib/record-store';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Send } from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickRecordProps {
  className?: string;
  placeholder?: string;
  redirectAfterSave?: boolean;
}

export function QuickRecord({
  className,
  placeholder = 'Quick note...',
  redirectAfterSave = true,
}: QuickRecordProps) {
  const router = useRouter();

  const content = useRecordStore((state) => state.content);
  const isSaving = useRecordStore((state) => state.isSaving);
  const saveError = useRecordStore((state) => state.saveError);
  const setContent = useRecordStore((state) => state.setContent);
  const saveRecord = useRecordStore((state) => state.saveRecord);
  const clearRecord = useRecordStore((state) => state.clearRecord);

  const hasContent = content.trim().length > 0;

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();

      if (!hasContent || isSaving) return;

      await saveRecord();

      // Check if save was successful
      const state = useRecordStore.getState();
      if (state.currentRecord && !state.saveError) {
        if (redirectAfterSave) {
          router.push(`/note?path=${encodeURIComponent(state.currentRecord.path)}`);
        }
        clearRecord();
      }
    },
    [hasContent, isSaving, saveRecord, redirectAfterSave, router, clearRecord]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('flex flex-col gap-3', className)}
      role="form"
      aria-label="Quick note form"
    >
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isSaving}
        className="min-h-[120px] resize-none"
        aria-label="Quick note"
      />

      {saveError && (
        <p className="text-sm text-destructive" role="alert">
          {saveError}
        </p>
      )}

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Press Ctrl+Enter to save
        </p>

        <Button
          type="submit"
          disabled={!hasContent || isSaving}
          className="gap-2"
        >
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              Save
            </>
          )}
        </Button>
      </div>
    </form>
  );
}