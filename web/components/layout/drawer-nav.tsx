'use client';

/**
 * DrawerNav - Slide-in navigation overlay.
 * Triggered by the hamburger menu in TopBar.
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MessageSquare,
  Boxes,
  GitGraph,
  Search,
  FileEdit,
  ScrollText,
  Settings,
} from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/lib/store';

const navItems = [
  { label: 'Chat', path: '/', icon: MessageSquare },
  { label: 'Skills', path: '/skills', icon: Boxes },
  { label: 'Explore', path: '/explore', icon: GitGraph },
  { label: 'Query', path: '/query', icon: Search },
  { label: 'Record', path: '/record', icon: FileEdit },
  { label: 'Logs', path: '/logs', icon: ScrollText },
  { label: 'Settings', path: '/settings', icon: Settings },
] as const;

export function DrawerNav() {
  const drawerOpen = useUIStore((s) => s.drawerOpen);
  const setDrawerOpen = useUIStore((s) => s.setDrawerOpen);
  const pathname = usePathname();

  return (
    <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
      <SheetContent side="left" className="w-[240px] p-0">
        <SheetHeader className="px-4 pt-4 pb-2">
          <SheetTitle className="text-sm font-semibold">Navigation</SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col gap-0.5 px-2 pb-4">
          {navItems.map((item) => {
            const isActive =
              item.path === '/' ? pathname === '/' : pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                href={item.path}
                onClick={() => setDrawerOpen(false)}
                className={cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-secondary font-medium'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
