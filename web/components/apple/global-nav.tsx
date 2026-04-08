'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  MessageSquare,
  Search,
  FileEdit,
  Compass,
  Sparkles,
  Settings,
} from 'lucide-react';
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet';

const NAV_ITEMS = [
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/query', label: 'Query', icon: Search },
  { href: '/record', label: 'Record', icon: FileEdit },
  { href: '/explore', label: 'Explore', icon: Compass },
  { href: '/skills', label: 'Skills', icon: Sparkles },
  { href: '/settings', label: 'Settings', icon: Settings },
] as const;

interface GlobalNavProps {
  open: boolean;
  onClose: () => void;
}

export function GlobalNav({ open, onClose }: GlobalNavProps) {
  const pathname = usePathname();

  return (
    <Sheet open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <SheetContent side="left" className="w-[220px] p-0 rounded-r-[var(--panel-radius)] border-r border-[var(--panel-border)] bg-[var(--panel-bg)] backdrop-blur-xl">
        <SheetTitle className="sr-only">Navigation</SheetTitle>
        <div className="flex items-center gap-2 px-4 pt-4 pb-3 border-b border-[var(--panel-border)]">
          <div className="h-2 w-2 rounded-full bg-[var(--brand-dot)]" />
          <span className="text-xs font-semibold">Markwritter</span>
        </div>
        <nav aria-label="Main navigation" className="p-2">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href || pathname.startsWith(href + '/');
              return (
                <li key={href}>
                  <Link
                    href={href}
                    onClick={onClose}
                    aria-current={isActive ? 'page' : undefined}
                    className={cn(
                      'flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-[13px] font-medium transition-colors',
                      isActive
                        ? 'bg-[var(--status-bg)] text-[hsl(var(--foreground))]'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </SheetContent>
    </Sheet>
  );
}
