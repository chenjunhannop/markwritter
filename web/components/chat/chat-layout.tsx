'use client';

/**
 * ChatLayout - Three-panel layout for the chat page.
 * Now shares Sidebar + Header with all other pages via MainLayout.
 * The content area contains: Sources | ChatArea | AnswerContext.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/lib/store';
import { MainLayout } from '@/components/layout/main-layout';
import { SourcesPanel } from '@/components/chat/sources-panel';
import { AnswerContextPanel } from '@/components/chat/answer-context-panel';
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
    <MainLayout title="Chat">
      <div className="flex h-full -m-4 overflow-hidden">
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

        {/* Collapsed strip for left panel */}
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

        {/* Collapsed strip for right panel */}
        {rightPanelCollapsed && (
          <button
            onClick={handleExpandRight}
            aria-label="Expand right panel"
            className="flex w-6 shrink-0 flex-col items-center justify-center border-l hover:bg-accent transition-colors"
          >
            <ChevronLeft className="h-3 w-3 text-muted-foreground" />
          </button>
        )}

        {/* Right Panel: Answer Context (inline only on wide viewport) */}
        {!isNarrow && (
          <aside
            className={cn(
              'shrink-0 border-l transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]',
              rightPanelCollapsed ? 'w-0 overflow-hidden opacity-0' : 'w-[320px]'
            )}
          >
            <AnswerContextPanel />
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
          <SheetTitle className="sr-only">Answer Context Panel</SheetTitle>
          <AnswerContextPanel />
        </SheetContent>
      </Sheet>
    </MainLayout>
  );
}
