/**
 * Tests for ChatLayout Component - Apple Refresh Layout
 *
 * Tests the three-panel layout for responsive behavior:
 * - Panels render as FloatingPanels on wide viewports
 * - Panels auto-collapse on narrow viewports (< 900px)
 * - User preferences are preserved when resizing
 * - Panels render as Sheet overlays on mobile when opened
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatLayout } from './chat-layout';
import { useUIStore } from '@/lib/store';

vi.mock('@/components/chat/sources-panel', () => ({
  SourcesPanel: () => <div data-testid="sources-panel">SourcesPanel</div>,
}));

vi.mock('@/components/chat/studio-panel', () => ({
  StudioPanel: () => <div data-testid="studio-panel">StudioPanel</div>,
}));

vi.mock('@/components/apple/floating-top-bar', () => ({
  FloatingTopBar: ({ onToggleNav }: { onToggleNav?: () => void; title?: string; statusBadge?: string }) => (
    <header data-testid="floating-top-bar">
      {onToggleNav && <button onClick={onToggleNav}>Toggle Nav</button>}
    </header>
  ),
}));

vi.mock('@/components/apple/global-nav', () => ({
  GlobalNav: ({ open, onClose }: { open: boolean; onClose: () => void }) => (
    <div data-testid="global-nav" data-open={open}>
      {open && <button onClick={onClose}>Close Nav</button>}
    </div>
  ),
}));

vi.mock('@/components/apple/gradient-page', () => ({
  GradientPage: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('@/components/apple/floating-panel', () => ({
  FloatingPanel: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="floating-panel" className={className}>{children}</div>
  ),
}));

type MediaQueryListener = (event: { matches: boolean; media: string }) => void;
let mediaQueryListeners: Array<{ query: string; listener: MediaQueryListener }> = [];

function createMatchMediaMock(overrides: Record<string, boolean> = {}) {
  return vi.fn().mockImplementation((query: string) => {
    const matches = overrides[query] ?? false;
    return {
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn((_event: string, listener: MediaQueryListener) => {
        mediaQueryListeners.push({ query, listener });
      }),
      removeEventListener: vi.fn((_event: string, listener: MediaQueryListener) => {
        mediaQueryListeners = mediaQueryListeners.filter(
          (entry) => !(entry.query === query && entry.listener === listener)
        );
      }),
      dispatchEvent: vi.fn(),
    };
  });
}

describe('ChatLayout', () => {
  let originalMatchMedia: typeof window.matchMedia;

  beforeEach(() => {
    vi.clearAllMocks();
    mediaQueryListeners = [];
    useUIStore.setState({
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      connectionStatus: 'connected',
    });

    originalMatchMedia = window.matchMedia;
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: createMatchMediaMock(),
    });
  });

  afterEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: originalMatchMedia,
    });
    mediaQueryListeners = [];
  });

  describe('wide viewport (>= 900px)', () => {
    it('should render left panel as FloatingPanel when not collapsed', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      const sourcesPanel = screen.getByTestId('sources-panel');
      expect(sourcesPanel).toBeInTheDocument();

      const panels = screen.getAllByTestId('floating-panel');
      const leftPanel = panels.find(p => p.contains(sourcesPanel));
      expect(leftPanel).toBeDefined();
    });

    it('should render right panel as FloatingPanel when not collapsed', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      const studioPanel = screen.getByTestId('studio-panel');
      expect(studioPanel).toBeInTheDocument();

      const panels = screen.getAllByTestId('floating-panel');
      const rightPanel = panels.find(p => p.contains(studioPanel));
      expect(rightPanel).toBeDefined();
    });

    it('should render the center main content area', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      expect(screen.getByTestId('chat-content')).toBeInTheDocument();
      expect(screen.getByText('Chat Content')).toBeInTheDocument();
    });

    it('should render the floating top bar', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      expect(screen.getByTestId('floating-top-bar')).toBeInTheDocument();
    });

    it('should not render Sheet overlays on wide viewport', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBe(0);
    });

    it('should not show collapsed strip buttons when panels are expanded', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      expect(screen.queryByRole('button', { name: /expand left panel/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /expand right panel/i })).not.toBeInTheDocument();
    });
  });

  describe('narrow viewport (< 900px)', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: createMatchMediaMock({ '(max-width: 900px)': true }),
      });
    });

    it('should auto-collapse both panels on narrow viewport', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      expect(screen.queryByTestId('sources-panel')).not.toBeInTheDocument();
      expect(screen.queryByTestId('studio-panel')).not.toBeInTheDocument();
    });

    it('should show collapsed strip buttons when panels are collapsed on narrow viewport', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      expect(screen.getByRole('button', { name: /expand left panel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /expand right panel/i })).toBeInTheDocument();
    });

    it('should not render Sheet overlays when both panels are collapsed', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBe(0);
    });
  });

  describe('viewport resize behavior', () => {
    it('should auto-collapse panels when viewport narrows', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      expect(screen.getByTestId('sources-panel')).toBeInTheDocument();
      expect(screen.getByTestId('studio-panel')).toBeInTheDocument();

      await act(async () => {
        mediaQueryListeners.forEach((entry) => {
          if (entry.query === '(max-width: 900px)') {
            entry.listener({ matches: true, media: entry.query });
          }
        });
      });

      expect(screen.queryByTestId('sources-panel')).not.toBeInTheDocument();
      expect(screen.queryByTestId('studio-panel')).not.toBeInTheDocument();

      expect(screen.getByRole('button', { name: /expand left panel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /expand right panel/i })).toBeInTheDocument();
    });

    it('should restore user preferences when viewport widens after being narrow', async () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: createMatchMediaMock({ '(max-width: 900px)': true }),
      });

      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: createMatchMediaMock({ '(max-width: 900px)': false }),
      });

      await act(async () => {
        mediaQueryListeners.forEach((entry) => {
          if (entry.query === '(max-width: 900px)') {
            entry.listener({ matches: false, media: entry.query });
          }
        });
      });

      expect(screen.getByTestId('sources-panel')).toBeInTheDocument();

      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBe(0);
    });
  });

  describe('mobile Sheet overlay behavior', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: createMatchMediaMock({ '(max-width: 900px)': true }),
      });
    });

    it('should render left panel as Sheet overlay when opened on mobile', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const sheetContentsBefore = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContentsBefore.length).toBe(0);

      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      const sheetContentsAfter = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContentsAfter.length).toBeGreaterThan(0);

      expect(screen.getByTestId('sources-panel')).toBeInTheDocument();
    });

    it('should render right panel as Sheet overlay when opened on mobile', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const expandRightButton = screen.getByRole('button', { name: /expand right panel/i });
      await userEvent.click(expandRightButton);

      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBeGreaterThan(0);

      expect(screen.getByTestId('studio-panel')).toBeInTheDocument();
    });

    it('should close Sheet and return to collapsed state on close', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      const sheetContent = document.querySelector('[data-slot="sheet-content"]');
      expect(sheetContent).toBeInTheDocument();
      expect(sheetContent?.getAttribute('data-state')).toBe('open');

      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toBeInTheDocument();
      await userEvent.click(closeButton);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
      });

      const sheetContentAfter = document.querySelector('[data-slot="sheet-content"]');
      if (sheetContentAfter) {
        expect(sheetContentAfter.getAttribute('data-state')).toBe('closed');
      } else {
        expect(sheetContentAfter).toBeNull();
      }
    });

    it('should close right Sheet and return to collapsed state on close', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const expandRightButton = screen.getByRole('button', { name: /expand right panel/i });
      await userEvent.click(expandRightButton);

      const sheetContent = document.querySelector('[data-slot="sheet-content"]');
      expect(sheetContent).toBeInTheDocument();
      expect(sheetContent?.getAttribute('data-state')).toBe('open');

      const closeButton = screen.getByRole('button', { name: /close/i });
      await userEvent.click(closeButton);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
      });

      const sheetContentAfter = document.querySelector('[data-slot="sheet-content"]');
      if (sheetContentAfter) {
        expect(sheetContentAfter.getAttribute('data-state')).toBe('closed');
      } else {
        expect(sheetContentAfter).toBeNull();
      }
    });
  });

  describe('edge cases', () => {
    it('should render with null children without crashing', () => {
      expect(() => {
        render(<ChatLayout>{null}</ChatLayout>);
      }).not.toThrow();
    });

    it('should render with multiple children', () => {
      render(
        <ChatLayout>
          <div data-testid="child-1">First</div>
          <div data-testid="child-2">Second</div>
        </ChatLayout>
      );

      expect(screen.getByTestId('child-1')).toBeInTheDocument();
      expect(screen.getByTestId('child-2')).toBeInTheDocument();
    });

    it('should handle rapid viewport changes without error', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const narrow = { matches: true, media: '(max-width: 900px)' };
      const wide = { matches: false, media: '(max-width: 900px)' };

      await act(async () => {
        for (let i = 0; i < 10; i++) {
          mediaQueryListeners.forEach((entry) => {
            if (entry.query === '(max-width: 900px)') {
              entry.listener(i % 2 === 0 ? narrow : wide);
            }
          });
        }
      });

      expect(screen.getByTestId('floating-top-bar')).toBeInTheDocument();
    });

    it('should handle GlobalNav toggle', async () => {
      const user = userEvent.setup();
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const toggleButton = screen.getByRole('button', { name: /toggle nav/i });
      await user.click(toggleButton);

      expect(screen.getByTestId('global-nav')).toBeInTheDocument();
    });
  });
});
