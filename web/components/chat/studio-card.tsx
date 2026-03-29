'use client';

/**
 * StudioCard - Individual tool card for the Studio panel.
 */

import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StudioCardProps {
  name: string;
  description: string;
  icon: LucideIcon;
  iconBgColor: string;
  iconColor: string;
  disabled?: boolean;
  onClick?: () => void;
}

export function StudioCard({
  name,
  description,
  icon: Icon,
  iconBgColor,
  iconColor,
  disabled = false,
  onClick,
}: StudioCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-start gap-3 rounded-lg border p-3.5 text-left transition-all',
        disabled
          ? 'cursor-not-allowed opacity-60'
          : 'cursor-pointer hover:border-primary/20 hover:shadow-sm hover:bg-accent/50'
      )}
    >
      <div
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
        style={{ backgroundColor: iconBgColor }}
      >
        <Icon className="h-5 w-5" style={{ color: iconColor }} />
      </div>
      <div className="min-w-0">
        <div className="text-[12.5px] font-semibold">{name}</div>
        <div className="text-[11px] text-muted-foreground leading-tight">
          {description}
        </div>
      </div>
    </button>
  );
}
