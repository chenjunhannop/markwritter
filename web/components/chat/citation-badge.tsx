'use client';

import { useState } from 'react';
import type { Citation } from '@/lib/types';

interface CitationBadgeProps {
  number: number;
  citation: Citation;
}

export function CitationBadge({ number, citation }: CitationBadgeProps) {
  const [open, setOpen] = useState(false);

  return (
    <span className="relative inline-flex align-baseline">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-primary/10 px-1.5 text-[11px] font-medium text-primary transition-colors hover:bg-primary/20"
        aria-expanded={open}
        aria-label={`Show citation ${number}`}
      >
        [{number}]
      </button>

      {open && (
        <div className="absolute left-0 top-full z-20 mt-2 w-72 rounded-lg border bg-background p-3 text-left shadow-lg">
          <div className="text-xs font-semibold text-foreground">{citation.file_path}</div>
          {citation.page_num > 0 && (
            <div className="mt-1 text-[11px] text-muted-foreground">
              Page {citation.page_num}
            </div>
          )}
          <p className="mt-2 text-xs leading-5 text-muted-foreground">
            {citation.text_snippet}
          </p>
        </div>
      )}
    </span>
  );
}
