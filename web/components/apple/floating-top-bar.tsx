'use client';

import { cn } from '@/lib/utils';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FloatingTopBarProps {
  title: string;
  statusBadge?: string;
  onToggleNav?: () => void;
  className?: string;
}

function BrandDot() {
  return <div className="h-2 w-2 rounded-full bg-[var(--brand-dot)]" />;
}

function BrandCapsule() {
  return (
    <div className="flex items-center gap-2 rounded-2xl bg-[var(--topbar-bg)] border border-[var(--panel-border)] px-3 py-1.5 shadow-[var(--panel-shadow)]">
      <BrandDot />
      <span className="text-xs font-semibold text-[hsl(var(--foreground))]">
        Markwritter
      </span>
    </div>
  );
}

export function FloatingTopBar({ title, statusBadge, onToggleNav, className }: FloatingTopBarProps) {
  return (
    <header className={cn('flex items-center justify-between px-4 pt-3 pb-2', className)}>
      <div className="mx-auto flex w-full max-w-[1328px] items-center justify-between">
        <div className="flex items-center gap-3">
          {onToggleNav && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleNav}
              className="h-8 w-8 shrink-0"
              aria-label="Toggle navigation"
            >
              <Menu className="h-4 w-4" />
            </Button>
          )}
          <BrandCapsule />
          <h1 className="text-[17px] font-semibold text-[hsl(var(--foreground))]">
            {title}
          </h1>
        </div>
        {statusBadge && (
          <div className="rounded-full bg-[var(--status-bg)] border border-[var(--panel-border)] px-3 py-1">
            <span className="text-[11px] font-medium text-[var(--status-text)]">
              {statusBadge}
            </span>
          </div>
        )}
      </div>
    </header>
  );
}
