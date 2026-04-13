'use client';

import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actions?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, actions, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center p-8', className)}>
      <FloatingEmptyCard icon={Icon} title={title} description={description} actions={actions} />
    </div>
  );
}

interface FloatingEmptyCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actions?: React.ReactNode;
  className?: string;
}

export function FloatingEmptyCard({ icon: Icon, title, description, actions, className }: FloatingEmptyCardProps) {
  return (
    <div
      className={cn(
        'rounded-[var(--panel-radius)] border border-[var(--panel-border)] bg-[var(--panel-bg)] backdrop-blur-xl shadow-[var(--panel-shadow)] px-8 py-10 text-center max-w-md w-full',
        className
      )}
    >
      <Icon className="h-10 w-10 mx-auto mb-4 text-muted-foreground/30" aria-hidden="true" />
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 leading-relaxed">{description}</p>
      {actions && <div className="flex items-center justify-center gap-3 flex-wrap">{actions}</div>}
    </div>
  );
}
