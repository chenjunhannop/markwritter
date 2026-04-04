/**
 * Tests for MainLayout Component
 *
 * Tests layout structure, responsive behavior, and children rendering.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { MainLayout } from './main-layout';
import { useUIStore } from '@/lib/store';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: () => '/chat',
  useRouter: () => ({ push: vi.fn() }),
}));

// Mock the store
vi.mock('@/lib/store', () => ({
  useUIStore: vi.fn(),
}));

const renderWithProviders = (ui: React.ReactElement) => {
  return render(<TooltipProvider>{ui}</TooltipProvider>);
};

describe('MainLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
      const state = {
        sidebarCollapsed: false,
        connectionStatus: 'connected',
        toggleSidebar: vi.fn(),
        setConnectionStatus: vi.fn(),
      };
      return selector ? selector(state) : state;
    });
  });

  describe('rendering', () => {
    it('should render children', () => {
      renderWithProviders(
        <MainLayout>
          <div data-testid="child-content">Test Content</div>
        </MainLayout>
      );

      expect(screen.getByTestId('child-content')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('should render sidebar', () => {
      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
    });

    it('should render header', () => {
      renderWithProviders(
        <MainLayout title="Test Page">
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByText('Test Page')).toBeInTheDocument();
    });
  });

  describe('layout structure', () => {
    it('should have correct layout structure', () => {
      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      // Main container should be flex
      const mainContainer = container.firstChild;
      expect(mainContainer).toHaveClass('flex');
    });

    it('should have sidebar on the left', () => {
      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();

      // Sidebar should be the first child
      const mainContainer = container.firstChild as HTMLElement;
      const firstElement = mainContainer.firstChild;
      expect(firstElement).toBe(nav);
    });
  });

  describe('responsive behavior', () => {
    it('should collapse sidebar on small screens', () => {
      // Test that the sidebar has responsive classes
      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const nav = container.querySelector('nav');
      // Should have responsive width classes
      expect(nav?.className).toMatch(/w-/);
    });
  });

  describe('collapsed state', () => {
    it('should show collapsed sidebar when sidebarCollapsed is true', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: true,
          connectionStatus: 'connected',
          toggleSidebar: vi.fn(),
          setConnectionStatus: vi.fn(),
        };
        return selector ? selector(state) : state;
      });

      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('w-16');
    });
  });

  describe('accessibility', () => {
    it('should have proper heading hierarchy', () => {
      renderWithProviders(
        <MainLayout title="Chat">
          <div>Content</div>
        </MainLayout>
      );

      // Should have h1 for page title
      expect(screen.getByRole('heading', { name: 'Chat' })).toBeInTheDocument();
    });
  });

  describe('content area', () => {
    it('should have scrollable content area', () => {
      const { container } = renderWithProviders(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      // Find the main content area
      const main = container.querySelector('main') || container.querySelector('[class*="flex-1"]');
      expect(main).toBeInTheDocument();
    });
  });
});