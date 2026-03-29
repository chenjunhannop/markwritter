'use client';

/**
 * ChatLayout - Three-panel layout container for the chat page.
 * Replaces MainLayout for the chat page only.
 *
 * Responsive behavior:
 * - Wide viewport (>= 900px): panels render as inline aside elements.
 * - Narrow viewport (< 900px): panels auto-collapse. When opened, they
 *   render as Sheet overlays (mobile drawer).
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/lib/store';
import { TopBar } from '@/components/layout/top-bar';
import { DrawerNav } from '@/components/layout/drawer-nav';
import { SourcesPanel } from '@/components/chat/sources-panel';
import { StudioPanel } from '@/components/chat/studio-panel';
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from '@/components/ui/sheet';

const NARROW_BREAKPOINT = 900;

interface ChatLayoutProps {
  children: React.ReactNode;
}

export function ChatLayout({ children }: ChatLayoutProps) {
  const leftPanelCollapsed = useUIStore((s) => s.leftPanelCollapsed);
  const rightPanelCollapsed = useUIStore((s) => s.rightPanelCollapsed);
  const setLeftPanelCollapsed = useUIStore((s) => s.setLeftPanelCollapsed);
  const setRightPanelCollapsed = useUIStore((s) => s.setRightPanelCollapsed);

  // Use state so viewport changes trigger re-renders.
  const [isNarrow, setIsNarrow] = useState(false);

  // Track user preferences so we can restore them when viewport widens.
  const userPrefRef = useRef({ left: false, right: false });
  // Track previous narrow state to detect transitions.
  const wasNarrowRef = useRef(false);

  // Listen for viewport width changes.
  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${NARROW_BREAKPOINT}px)`);

    const handleChange = (e: MediaQueryListEvent) => {
      const nowNarrow = e.matches;
      const wasNarrow = wasNarrowRef.current;

      if (nowNarrow && !wasNarrow) {
        // Transitioning from wide to narrow: save user preferences, then collapse.
        userPrefRef.current = {
          left: useUIStore.getState().leftPanelCollapsed,
          right: useUIStore.getState().rightPanelCollapsed,
        };
        useUIStore.getState().setLeftPanelCollapsed(true);
        useUIStore.getState().setRightPanelCollapsed(true);
      } else if (!nowNarrow && wasNarrow) {
        // Transitioning from narrow to wide: restore user preferences.
        useUIStore.getState().setLeftPanelCollapsed(userPrefRef.current.left);
        useUIStore.getState().setRightPanelCollapsed(userPrefRef.current.right);
      }

      wasNarrowRef.current = nowNarrow;
      setIsNarrow(nowNarrow);
    };

    // Set initial state based on current viewport.
    const initialNarrow = mql.matches;
    wasNarrowRef.current = initialNarrow;
    if (initialNarrow) {
      userPrefRef.current = {
        left: useUIStore.getState().leftPanelCollapsed,
        right: useUIStore.getState().rightPanelCollapsed,
      };
      useUIStore.getState().setLeftPanelCollapsed(true);
      useUIStore.getState().setRightPanelCollapsed(true);
    }
    setIsNarrow(initialNarrow);

    mql.addEventListener('change', handleChange);
    return () => mql.removeEventListener('change', handleChange);
  }, []);

  // Derived: on narrow viewport, a panel is "open" only if the user explicitly toggled it.
  // Since narrow auto-collapses both, we track this via the collapsed state.
  // When collapsed=true + isNarrow, panels are hidden. Toggle to false = open as Sheet.
  const leftOpen = isNarrow && !leftPanelCollapsed;
  const rightOpen = isNarrow && !rightPanelCollapsed;

  const closeLeftSheet = useCallback(() => {
    setLeftPanelCollapsed(true);
  }, [setLeftPanelCollapsed]);

  const closeRightSheet = useCallback(() => {
    setRightPanelCollapsed(true);
  }, [setRightPanelCollapsed]);

  // On narrow viewport, clicking expand strip opens the Sheet instead of inline.
  const handleExpandLeft = useCallback(() => {
    setLeftPanelCollapsed(false);
  }, [setLeftPanelCollapsed]);

  const handleExpandRight = useCallback(() => {
    setRightPanelCollapsed(false);
  }, [setRightPanelCollapsed]);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <TopBar
        onToggleDrawer={() => useUIStore.getState().setDrawerOpen(true)}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Sources (inline only on wide viewport) */}
        {!isNarrow && (
          <aside
            className={cn(
              'shrink-0 border-r transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]',
              leftPanelCollapsed ? 'w-0 overflow-hidden opacity-0' : 'w-[240px]'
            )}
          >
            <SourcesPanel />
          </aside>
        )}

        {/* Collapsed strip for left panel (visible on both viewport sizes when collapsed) */}
        {leftPanelCollapsed && (
          <button
            onClick={handleExpandLeft}
            aria-label="Expand left panel"
            className="flex w-6 shrink-0 flex-col items-center justify-center border-r hover:bg-accent transition-colors"
          >
            <ChevronRight className="h-3 w-3 text-muted-foreground" />
          </button>
        )}

        {/* Center: Chat */}
        <main className="flex min-w-0 flex-1 flex-col">{children}</main>

        {/* Collapsed strip for right panel (visible on both viewport sizes when collapsed) */}
        {rightPanelCollapsed && (
          <button
            onClick={handleExpandRight}
            aria-label="Expand right panel"
            className="flex w-6 shrink-0 flex-col items-center justify-center border-l hover:bg-accent transition-colors"
          >
            <ChevronLeft className="h-3 w-3 text-muted-foreground" />
          </button>
        )}

        {/* Right Panel: Studio (inline only on wide viewport) */}
        {!isNarrow && (
          <aside
            className={cn(
              'shrink-0 border-l transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]',
              rightPanelCollapsed ? 'w-0 overflow-hidden opacity-0' : 'w-[320px]'
            )}
          >
            <StudioPanel />
          </aside>
        )}
      </div>

      {/* Mobile Sheet for left panel */}
      <Sheet open={leftOpen} onOpenChange={(open) => { if (!open) closeLeftSheet(); }}>
        <SheetContent side="left" className="p-0 w-[300px]" showCloseButton={true}>
          <SheetTitle className="sr-only">Sources Panel</SheetTitle>
          <SourcesPanel />
        </SheetContent>
      </Sheet>

      {/* Mobile Sheet for right panel */}
      <Sheet open={rightOpen} onOpenChange={(open) => { if (!open) closeRightSheet(); }}>
        <SheetContent side="right" className="p-0 w-[300px]" showCloseButton={true}>
          <SheetTitle className="sr-only">Studio Panel</SheetTitle>
          <StudioPanel />
        </SheetContent>
      </Sheet>

      <DrawerNav />
    </div>
  );
}
