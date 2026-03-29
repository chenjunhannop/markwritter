'use client';

/**
 * TopBar for the chat page.
 * Replaces Header for the three-panel chat layout.
 */

import { useRouter } from 'next/navigation';
import { Menu, Settings, PanelRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore, type ConnectionStatus } from '@/lib/store';

const statusColors: Record<ConnectionStatus, string> = {
  connected: 'bg-green-500',
  disconnected: 'bg-gray-400',
  connecting: 'bg-amber-400',
  error: 'bg-red-500',
};

interface TopBarProps {
  onToggleDrawer: () => void;
}

export function TopBar({ onToggleDrawer }: TopBarProps) {
  const router = useRouter();
  const connectionStatus = useUIStore((s) => s.connectionStatus);
  const toggleRightPanel = useUIStore((s) => s.toggleRightPanel);

  return (
    <header className="flex h-[52px] shrink-0 items-center gap-2 border-b px-3">
      <Button variant="ghost" size="icon" onClick={onToggleDrawer}>
        <Menu className="h-4 w-4" />
      </Button>

      <span className="text-[15px] font-semibold tracking-tight">Markwritter</span>

      <div className="flex-1" />

      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground">Backend</span>
        <span className={`inline-block h-2 w-2 rounded-full ${statusColors[connectionStatus]}`} />

        <Button variant="ghost" size="icon" onClick={toggleRightPanel}>
          <PanelRight className="h-4 w-4" />
        </Button>

        <Button variant="ghost" size="icon" onClick={() => router.push('/settings')}>
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
