'use client';

import { useState, useCallback } from 'react';
import { GradientPage } from '@/components/apple/gradient-page';
import { FloatingTopBar } from '@/components/apple/floating-top-bar';
import { GlobalNav } from '@/components/apple/global-nav';

interface AppShellProps {
  title: string;
  statusBadge?: string;
  children: React.ReactNode;
}

export function AppShell({ title, statusBadge, children }: AppShellProps) {
  const [navOpen, setNavOpen] = useState(false);

  const closeNav = useCallback(() => {
    setNavOpen(false);
  }, []);

  return (
    <GradientPage>
      <div className="flex min-h-screen flex-col">
        <FloatingTopBar
          title={title}
          statusBadge={statusBadge}
          onToggleNav={() => setNavOpen(true)}
        />
        <main className="flex-1 overflow-auto px-4 pt-2 pb-6">
          <div className="mx-auto max-w-[1328px]">
            {children}
          </div>
        </main>
      </div>
      <GlobalNav open={navOpen} onClose={closeNav} />
    </GradientPage>
  );
}
