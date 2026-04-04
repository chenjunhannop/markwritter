'use client';

/**
 * Shared UI primitives for page-level states.
 *
 * PageHeader  - Reusable page header bar with icon, title, and actions slot.
 * EmptyState  - Generic empty/placeholder state.
 * ErrorState  - Generic error state with optional retry.
 * LoadingState - Generic loading spinner with message.
 */

import type { LucideIcon } from 'lucide-react';
import { Loader2 } from 'lucide-react';
import type { ReactNode } from 'react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// ---------------------------------------------------------------------------
// PageHeader
// ---------------------------------------------------------------------------

interface PageHeaderProps {
  icon?: LucideIcon;
  title: string;
  actions?: ReactNode;
  className?: string;
}

export default function PageHeader({
  icon: Icon,
  title,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        'flex h-[42px] shrink-0 items-center justify-between border-b px-3',
        className,
      )}
    >
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        <span className="text-[13px] font-semibold">{title}</span>
      </div>
      {actions && (
        <div className="flex items-center gap-1.5">{actions}</div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// EmptyState
// ---------------------------------------------------------------------------

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 text-muted-foreground',
        className,
      )}
    >
      {Icon && <Icon className="mb-3 h-10 w-10 opacity-30" />}
      <h3 className="mb-1 text-lg font-medium">{title}</h3>
      {description && (
        <p className="max-w-xs text-center text-sm">{description}</p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// ErrorState
// ---------------------------------------------------------------------------

interface ErrorStateProps {
  icon?: LucideIcon;
  title: string;
  error?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  icon: Icon,
  title,
  error,
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 text-destructive',
        className,
      )}
    >
      {Icon && <Icon className="mb-3 h-10 w-10 opacity-30" />}
      <h3 className="mb-1 text-lg font-medium">{title}</h3>
      {error && (
        <p className="max-w-xs text-center text-sm">{error}</p>
      )}
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="mt-4"
        >
          Retry
        </Button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// LoadingState
// ---------------------------------------------------------------------------

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({
  message = 'Loading...',
  className,
}: LoadingStateProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-center py-12 text-muted-foreground',
        className,
      )}
    >
      <Loader2 className="h-5 w-5 animate-spin" />
      <span className="ml-2 text-sm">{message}</span>
    </div>
  );
}
