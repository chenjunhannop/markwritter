'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/lib/store';
import { FloatingTopBar } from '@/components/apple/floating-top-bar';
import { GlobalNav } from '@/components/apple/global-nav';
import { FloatingPanel } from '@/components/apple/floating-panel';
import { GradientPage } from '@/components/apple/gradient-page';
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

  const [isNarrow, setIsNarrow] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const userPrefRef = useRef({ left: false, right: false });
  const wasNarrowRef = useRef(false);

  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${NARROW_BREAKPOINT}px)`);

    const handleChange = (e: MediaQueryListEvent) => {
      const nowNarrow = e.matches;
      const wasNarrow = wasNarrowRef.current;

      if (nowNarrow && !wasNarrow) {
        userPrefRef.current = {
          left: useUIStore.getState().leftPanelCollapsed,
          right: useUIStore.getState().rightPanelCollapsed,
        };
        useUIStore.getState().setLeftPanelCollapsed(true);
        useUIStore.getState().setRightPanelCollapsed(true);
      } else if (!nowNarrow && wasNarrow) {
        useUIStore.getState().setLeftPanelCollapsed(userPrefRef.current.left);
        useUIStore.getState().setRightPanelCollapsed(userPrefRef.current.right);
      }

      wasNarrowRef.current = nowNarrow;
      setIsNarrow(nowNarrow);
    };

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

  const leftOpen = isNarrow && !leftPanelCollapsed;
  const rightOpen = isNarrow && !rightPanelCollapsed;

  const closeLeftSheet = useCallback(() => {
    setLeftPanelCollapsed(true);
  }, [setLeftPanelCollapsed]);

  const closeRightSheet = useCallback(() => {
    setRightPanelCollapsed(true);
  }, [setRightPanelCollapsed]);

  const handleExpandLeft = useCallback(() => {
    setLeftPanelCollapsed(false);
  }, [setLeftPanelCollapsed]);

  const handleExpandRight = useCallback(() => {
    setRightPanelCollapsed(false);
  }, [setRightPanelCollapsed]);

  return (
    <GradientPage>
      <div className="flex h-screen flex-col overflow-hidden">
        <FloatingTopBar
          title="Conversation Studio"
          statusBadge="Live Workspace"
          onToggleNav={() => setNavOpen(true)}
        />

        <div className="flex flex-1 overflow-hidden gap-3 px-4 pb-4">
          {/* Left Panel: Sources (inline only on wide viewport) */}
          {!isNarrow && !leftPanelCollapsed && (
            <FloatingPanel className="w-[240px] shrink-0 overflow-hidden">
              <SourcesPanel />
            </FloatingPanel>
          )}

          {/* Collapsed strip for left panel */}
          {leftPanelCollapsed && (
            <button
              onClick={handleExpandLeft}
              aria-label="Expand left panel"
              className="flex w-6 shrink-0 flex-col items-center justify-center rounded-lg bg-[var(--panel-bg)] border border-[var(--panel-border)] backdrop-blur-xl hover:bg-accent transition-colors"
            >
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
            </button>
          )}

          {/* Center: Chat */}
          <FloatingPanel className="flex min-w-0 flex-1 flex-col overflow-hidden">
            {children}
          </FloatingPanel>

          {/* Collapsed strip for right panel */}
          {rightPanelCollapsed && (
            <button
              onClick={handleExpandRight}
              aria-label="Expand right panel"
              className="flex w-6 shrink-0 flex-col items-center justify-center rounded-lg bg-[var(--panel-bg)] border border-[var(--panel-border)] backdrop-blur-xl hover:bg-accent transition-colors"
            >
              <ChevronLeft className="h-3 w-3 text-muted-foreground" />
            </button>
          )}

          {/* Right Panel: Studio (inline only on wide viewport) */}
          {!isNarrow && !rightPanelCollapsed && (
            <FloatingPanel className="w-[320px] shrink-0 overflow-hidden">
              <StudioPanel />
            </FloatingPanel>
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
      </div>

      <GlobalNav open={navOpen} onClose={() => setNavOpen(false)} />
    </GradientPage>
  );
}
