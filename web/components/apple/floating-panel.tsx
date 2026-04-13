'use client';

import { cn } from '@/lib/utils';

interface FloatingPanelProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'dark';
}

export function FloatingPanel({ children, className, variant = 'default' }: FloatingPanelProps) {
  return (
    <div
      className={cn(
        'rounded-[var(--panel-radius)] border border-[var(--panel-border)] shadow-[var(--panel-shadow)]',
        variant === 'dark'
          ? 'bg-[oklch(35%_0.03_250/0.94)] text-white'
          : 'bg-[var(--panel-bg)] backdrop-blur-xl',
        className
      )}
    >
      {children}
    </div>
  );
}
