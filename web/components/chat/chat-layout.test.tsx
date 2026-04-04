/**
 * Tests for ChatLayout Component - Mobile Responsive Behavior
 *
 * Tests the three-panel layout for responsive behavior:
 * - Panels render inline on wide viewports
 * - Panels auto-collapse on narrow viewports (< 900px)
 * - User preferences are preserved when resizing
 * - Panels render as Sheet overlays on mobile when opened
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatLayout } from './chat-layout';

// Mock child components to isolate ChatLayout logic
vi.mock('@/components/chat/sources-panel', () => ({
  SourcesPanel: () => <div data-testid="sources-panel">SourcesPanel</div>,
}));

vi.mock('@/components/chat/answer-context-panel', () => ({
  AnswerContextPanel: () => <div data-testid="answer-context-panel">AnswerContextPanel</div>,
}));

vi.mock('@/components/layout/top-bar', () => ({
  TopBar: ({ onToggleDrawer }: { onToggleDrawer: () => void }) => (
    <header data-testid="top-bar">
      <button onClick={onToggleDrawer}>Menu</button>
    </header>
  ),
}));

vi.mock('@/components/layout/drawer-nav', () => ({
  DrawerNav: () => <div data-testid="drawer-nav">DrawerNav</div>,
}));

// We do NOT mock @/components/ui/sheet - we test with the real component.
// But Radix Dialog (used by Sheet) needs ResizeObserver which is already mocked in setup.ts.

// Track matchMedia listeners so we can simulate viewport changes
type MediaQueryListener = (event: { matches: boolean; media: string }) => void;
let mediaQueryListeners: Array<{ query: string; listener: MediaQueryListener }> = [];

// Helper to create a matchMedia mock that supports listener tracking
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

    // Save original and replace with our mock
    originalMatchMedia = window.matchMedia;
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: createMatchMediaMock(),
    });
  });

  afterEach(() => {
    // Restore original matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: originalMatchMedia,
    });
    mediaQueryListeners = [];
  });

  // --- Test Case 1: Wide viewport - panels visible as inline aside ---
  describe('wide viewport (>= 900px)', () => {
    it('should render left panel as inline aside when not collapsed', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      // The SourcesPanel should be rendered inside an inline aside
      const sourcesPanel = screen.getByTestId('sources-panel');
      expect(sourcesPanel).toBeInTheDocument();

      // Verify it is inside an <aside> element (not a Sheet overlay)
      const asideElement = sourcesPanel.closest('aside');
      expect(asideElement).toBeInTheDocument();
    });

    it('should render right panel as inline aside when not collapsed', () => {
      render(
        <ChatLayout>
          <div data-testid="chat-content">Chat Content</div>
        </ChatLayout>
      );

      const answerContextPanel = screen.getByTestId('answer-context-panel');
      expect(answerContextPanel).toBeInTheDocument();

      // Verify it is inside an <aside> element (not a Sheet overlay)
      const asideElement = answerContextPanel.closest('aside');
      expect(asideElement).toBeInTheDocument();
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

    it('should render the top bar', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      expect(screen.getByTestId('top-bar')).toBeInTheDocument();
    });

    it('should not render Sheet overlays on wide viewport', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Sheet uses [data-slot="sheet-content"] attribute
      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBe(0);
    });
  });

  // --- Test Case 2: Narrow viewport - panels auto-collapse ---
  describe('narrow viewport (< 900px)', () => {
    beforeEach(() => {
      // Override matchMedia to report narrow viewport
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

      // Both aside panels should have collapsed styling (w-0 opacity-0)
      const asides = document.querySelectorAll('aside');
      for (const aside of asides) {
        expect(aside.className).toContain('w-0');
        expect(aside.className).toContain('opacity-0');
      }
    });

    it('should show collapsed strip buttons when panels are collapsed on narrow viewport', () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Left collapsed strip button should be visible
      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      expect(expandLeftButton).toBeInTheDocument();
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

  // --- Test Case 3: Viewport resize - restore user preferences ---
  describe('viewport resize behavior', () => {
    it('should auto-collapse panels when viewport narrows', async () => {
      // Start with wide viewport
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Panels should be visible initially (wide viewport) -- rendered as aside elements
      const asidesBefore = document.querySelectorAll('aside');
      // On wide viewport, aside elements should exist (not Sheet overlays)
      expect(asidesBefore.length).toBeGreaterThan(0);

      // Simulate viewport narrowing by firing the media query listener
      await act(async () => {
        mediaQueryListeners.forEach((entry) => {
          if (entry.query === '(max-width: 900px)') {
            entry.listener({ matches: true, media: entry.query });
          }
        });
      });

      // On narrow viewport, aside elements are removed (panels render as Sheet overlays when opened)
      // Both panels should be collapsed (expand strip buttons visible instead of asides)
      const asidesAfter = document.querySelectorAll('aside');
      expect(asidesAfter.length).toBe(0);

      // Expand strip buttons should appear
      expect(screen.getByRole('button', { name: /expand left panel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /expand right panel/i })).toBeInTheDocument();
    });

    it('should restore user preferences when viewport widens after being narrow', async () => {
      // Start with narrow viewport
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: createMatchMediaMock({ '(max-width: 900px)': true }),
      });

      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // User opens left panel on mobile (clicks expand button)
      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      // Simulate viewport widening
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

      // After widening, the left panel should be visible as inline aside (not Sheet)
      // The left panel should be rendered somewhere in the document
      expect(screen.getByTestId('sources-panel')).toBeInTheDocument();

      // No Sheet overlays should be present
      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBe(0);
    });
  });

  // --- Test Case 4: Mobile - panels open as Sheet overlays ---
  describe('mobile Sheet overlay behavior', () => {
    beforeEach(() => {
      // Set narrow viewport
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

      // Initially both panels are collapsed, no Sheet
      const sheetContentsBefore = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContentsBefore.length).toBe(0);

      // Click the expand left button
      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      // Now a Sheet overlay should appear containing SourcesPanel
      const sheetContentsAfter = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContentsAfter.length).toBeGreaterThan(0);

      // SourcesPanel should be inside the Sheet
      expect(screen.getByTestId('sources-panel')).toBeInTheDocument();
    });

    it('should render right panel as Sheet overlay when opened on mobile', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Click the expand right button
      const expandRightButton = screen.getByRole('button', { name: /expand right panel/i });
      await userEvent.click(expandRightButton);

      // A Sheet overlay should appear containing StudioPanel
      const sheetContents = document.querySelectorAll('[data-slot="sheet-content"]');
      expect(sheetContents.length).toBeGreaterThan(0);

      expect(screen.getByTestId('answer-context-panel')).toBeInTheDocument();
    });

    it('should close Sheet and return to collapsed state on close', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Open left panel
      const expandLeftButton = screen.getByRole('button', { name: /expand left panel/i });
      await userEvent.click(expandLeftButton);

      // Sheet should be visible with data-state="open"
      const sheetContent = document.querySelector('[data-slot="sheet-content"]');
      expect(sheetContent).toBeInTheDocument();
      expect(sheetContent?.getAttribute('data-state')).toBe('open');

      // Close the Sheet via the Close button inside the Sheet dialog
      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toBeInTheDocument();
      await userEvent.click(closeButton);

      // After closing, Sheet should be removed from DOM or have data-state="closed"
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
      });

      const sheetContentAfter = document.querySelector('[data-slot="sheet-content"]');
      // Radix may remove the element entirely or set it to "closed"
      if (sheetContentAfter) {
        expect(sheetContentAfter.getAttribute('data-state')).toBe('closed');
      } else {
        // Element removed entirely -- also acceptable
        expect(sheetContentAfter).toBeNull();
      }
    });

    it('should close right Sheet and return to collapsed state on close', async () => {
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      // Open right panel
      const expandRightButton = screen.getByRole('button', { name: /expand right panel/i });
      await userEvent.click(expandRightButton);

      // Sheet should be visible with data-state="open"
      const sheetContent = document.querySelector('[data-slot="sheet-content"]');
      expect(sheetContent).toBeInTheDocument();
      expect(sheetContent?.getAttribute('data-state')).toBe('open');

      // Close the Sheet via the Close button
      const closeButton = screen.getByRole('button', { name: /close/i });
      await userEvent.click(closeButton);

      // After closing, Sheet should be removed or closed
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

  // --- Edge cases ---
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

      // Rapidly toggle viewport width
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

      // Should not throw and should still render
      expect(screen.getByTestId('top-bar')).toBeInTheDocument();
    });

    it('should handle TopBar drawer toggle', async () => {
      const user = userEvent.setup();
      render(
        <ChatLayout>
          <div>Chat</div>
        </ChatLayout>
      );

      const menuButton = screen.getByRole('button', { name: /menu/i });
      await user.click(menuButton);

      // DrawerNav should be rendered (it's always in the DOM but controlled by state)
      expect(screen.getByTestId('drawer-nav')).toBeInTheDocument();
    });
  });
});
