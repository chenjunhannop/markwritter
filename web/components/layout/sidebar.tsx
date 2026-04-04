'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Separator } from '@/components/ui/separator';
import { useUIStore, type NavItem } from '@/lib/store';
import { navItems } from '@/lib/nav-config';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const sidebarCollapsed = useUIStore((state) => state.sidebarCollapsed);
  const activeNav = useUIStore((state) => state.activeNav);
  const setActiveNav = useUIStore((state) => state.setActiveNav);

  const handleNavClick = (item: typeof navItems[number]) => {
    setActiveNav(item.id as NavItem);
    router.push(item.path);
  };

  return (
    <nav
      className={cn(
        'flex flex-col h-full bg-muted/30 border-r transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-56'
      )}
    >
      {/* Logo / Brand */}
      <div className="flex items-center h-14 px-4 border-b">
        <span
          className={cn(
            'font-bold text-lg transition-opacity duration-200',
            sidebarCollapsed ? 'opacity-0 w-0' : 'opacity-100'
          )}
        >
          Markwritter
        </span>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeNav === item.id || pathname === item.path;

          return (
            <Tooltip key={item.id} delayDuration={0}>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  data-active={isActive}
                  aria-label={item.label}
                  onClick={() => handleNavClick(item)}
                  className={cn(
                    'w-full justify-start gap-3 px-3 mx-2 mb-1',
                    isActive
                      ? 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                      : 'hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span
                    className={cn(
                      'transition-opacity duration-200',
                      sidebarCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
                    )}
                  >
                    {item.label}
                  </span>
                </Button>
              </TooltipTrigger>
              {sidebarCollapsed && (
                <TooltipContent side="right">
                  {item.label}
                </TooltipContent>
              )}
            </Tooltip>
          );
        })}
      </div>

      {/* Footer */}
      <Separator />
      <div className="p-4">
        <span
          className={cn(
            'text-xs text-muted-foreground transition-opacity duration-200',
            sidebarCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
          )}
        >
          v1.0.0
        </span>
      </div>
    </nav>
  );
}
