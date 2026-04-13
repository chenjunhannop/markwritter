'use client';

import { cn } from '@/lib/utils';

interface GradientPageProps {
  children: React.ReactNode;
  className?: string;
}

export function GradientPage({ children, className }: GradientPageProps) {
  return (
    <div className={cn('gradient-page min-h-screen', className)}>
      {children}
    </div>
  );
}
