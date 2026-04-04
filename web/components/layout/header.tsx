'use client';

import { Menu, PanelLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { useUIStore, type ConnectionStatus } from '@/lib/store';
import { cn } from '@/lib/utils';

interface HeaderProps {
  readonly title: string;
}

const statusColors: Record<ConnectionStatus, string> = {
  connected: 'bg-emerald-500',
  disconnected: 'bg-gray-400',
  connecting: 'bg-amber-500 animate-pulse',
  error: 'bg-rose-500',
};

export function Header({ title }: HeaderProps) {
  const sidebarCollapsed = useUIStore((state) => state.sidebarCollapsed);
  const connectionStatus = useUIStore((state) => state.connectionStatus);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <header className="h-14 px-4 flex items-center justify-between border-b bg-background">
      {/* Left side: Toggle button and title */}
      <div className="flex items-center gap-3">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Toggle sidebar"
              onClick={toggleSidebar}
            >
              {sidebarCollapsed ? (
                <PanelLeft className="w-4 h-4" />
              ) : (
                <Menu className="w-4 h-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          </TooltipContent>
        </Tooltip>

        <h1 className="text-lg font-semibold">{title}</h1>
      </div>

      {/* Right side: Connection status */}
      <div className="flex items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  'w-2 h-2 rounded-full',
                  statusColors[connectionStatus]
                )}
                aria-label={`Connection status: ${connectionStatus}`}
              />
              <span className="text-xs text-muted-foreground capitalize">
                {connectionStatus}
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            Server connection: {connectionStatus}
          </TooltipContent>
        </Tooltip>
      </div>
    </header>
  );
}
