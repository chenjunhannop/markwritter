'use client';

import { cn } from '@/lib/utils';

interface ActionPillProps {
  label: string;
  onClick?: () => void;
  className?: string;
}

export function ActionPill({ label, onClick, className }: ActionPillProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-full border border-[var(--panel-border)] bg-[oklch(99%_0.001_250/0.94)] px-4 py-2 text-[11px] font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
        className
      )}
    >
      {label}
    </button>
  );
}
