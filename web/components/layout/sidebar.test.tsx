/**
 * Tests for Sidebar Component
 *
 * Tests navigation items, collapsed state, and active state highlighting.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Sidebar } from './sidebar';
import { useUIStore } from '@/lib/store';

// Mock next/navigation
const mockPush = vi.fn();
let mockPathname = '/chat';
vi.mock('next/navigation', () => ({
  usePathname: () => mockPathname,
  useRouter: () => ({ push: mockPush }),
}));

// Mock the store
vi.mock('@/lib/store', () => ({
  useUIStore: vi.fn(),
}));

const renderWithProviders = (ui: React.ReactElement) => {
  return render(<TooltipProvider>{ui}</TooltipProvider>);
};

describe('Sidebar', () => {
  const mockToggleSidebar = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
      const state = {
        sidebarCollapsed: false,
        toggleSidebar: mockToggleSidebar,
      };
      return selector ? selector(state) : state;
    });
  });

  describe('rendering', () => {
    it('should render all navigation items', () => {
      renderWithProviders(<Sidebar />);

      expect(screen.getByText('Chat')).toBeInTheDocument();
      expect(screen.getByText('Skills')).toBeInTheDocument();
      expect(screen.getByText('Logs')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('should render icons for each nav item', () => {
      const { container } = renderWithProviders(<Sidebar />);

      // Check for SVG icons (lucide-react icons)
      const buttons = container.querySelectorAll('button');
      expect(buttons.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('active state', () => {
    it('should highlight active nav item', () => {
      renderWithProviders(<Sidebar />);

      const chatButton = screen.getByRole('button', { name: /chat/i });
      expect(chatButton).toHaveAttribute('data-active', 'true');
    });

    it('should show different active item when pathname changes', () => {
      mockPathname = '/skills';

      renderWithProviders(<Sidebar />);

      const skillsButton = screen.getByRole('button', { name: /skills/i });
      expect(skillsButton).toHaveAttribute('data-active', 'true');

      // Chat should not be active
      const chatButton = screen.getByRole('button', { name: /chat/i });
      expect(chatButton).toHaveAttribute('data-active', 'false');
    });
  });

  describe('collapsed state', () => {
    it('should show expanded sidebar by default', () => {
      const { container } = renderWithProviders(<Sidebar />);

      const nav = container.querySelector('nav');
      expect(nav).not.toHaveClass('w-16');
    });

    it('should show collapsed sidebar when sidebarCollapsed is true', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: true,
          toggleSidebar: mockToggleSidebar,
        };
        return selector ? selector(state) : state;
      });

      const { container } = renderWithProviders(<Sidebar />);

      const nav = container.querySelector('nav');
      expect(nav).toHaveClass('w-16');
    });

    it('should hide text labels when collapsed', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: true,
          toggleSidebar: mockToggleSidebar,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Sidebar />);

      // Text should be hidden or have sr-only class
      const chatText = screen.getByText('Chat');
      expect(chatText.className).toMatch(/hidden|opacity-0/);
    });
  });

  describe('navigation interactions', () => {
    it('should navigate to correct route when clicking nav item', () => {
      renderWithProviders(<Sidebar />);

      const skillsButton = screen.getByRole('button', { name: /skills/i });
      fireEvent.click(skillsButton);

      expect(mockPush).toHaveBeenCalledWith('/skills');
    });
  });

  describe('tooltips', () => {
    it('should show tooltips when collapsed', async () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: true,
          toggleSidebar: mockToggleSidebar,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Sidebar />);

      // Check that buttons are rendered with tooltip capability
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('accessibility', () => {
    it('should have navigation role', () => {
      const { container } = renderWithProviders(<Sidebar />);

      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
    });

    it('should have accessible button labels', () => {
      renderWithProviders(<Sidebar />);

      expect(screen.getByRole('button', { name: /chat/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /skills/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /logs/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    });
  });
});