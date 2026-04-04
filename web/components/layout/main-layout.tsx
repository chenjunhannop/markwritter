'use client';

import { Sidebar } from './sidebar';
import { Header } from './header';

interface MainLayoutProps {
  readonly title?: string;
  readonly children: React.ReactNode;
}

export function MainLayout({ title = 'Markwritter', children }: MainLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-auto p-4">
          {children}
        </main>
      </div>
    </div>
  );
}
