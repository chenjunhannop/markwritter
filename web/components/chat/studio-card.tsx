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
  variant?: 'default' | 'dark';
}

export function StudioCard({
  name,
  description,
  icon: Icon,
  iconBgColor,
  iconColor,
  disabled = false,
  onClick,
  variant = 'default',
}: StudioCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-start gap-3 rounded-[var(--panel-radius)] border p-3.5 text-left transition-all',
        variant === 'dark'
          ? 'bg-[oklch(35%_0.03_250/0.94)] border-transparent text-white'
          : 'bg-[var(--panel-bg)] border-[var(--panel-border)]',
        disabled
          ? 'cursor-not-allowed opacity-60'
          : 'cursor-pointer hover:shadow-[var(--panel-shadow)]'
      )}
    >
      {variant === 'dark' ? (
        <div className="min-w-0">
          <div className="text-[14px] font-semibold">{name}</div>
          <div className="text-[12px] text-[oklch(85%_0.02_250)] leading-tight mt-1">
            {description}
          </div>
        </div>
      ) : (
        <>
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
        </>
      )}
    </button>
  );
}
