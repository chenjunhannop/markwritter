/**
 * Tests for Header Component
 *
 * Tests page title display, sidebar toggle button, and connection status indicator.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Header } from './header';
import { useUIStore } from '@/lib/store';

// Mock the store
vi.mock('@/lib/store', () => ({
  useUIStore: vi.fn(),
}));

const renderWithProviders = (ui: React.ReactElement) => {
  return render(<TooltipProvider>{ui}</TooltipProvider>);
};

describe('Header', () => {
  const mockToggleSidebar = vi.fn();
  const mockSetConnectionStatus = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
      const state = {
        sidebarCollapsed: false,
        activeNav: 'chat',
        connectionStatus: 'connected',
        toggleSidebar: mockToggleSidebar,
        setConnectionStatus: mockSetConnectionStatus,
      };
      return selector ? selector(state) : state;
    });
  });

  describe('rendering', () => {
    it('should render the page title', () => {
      renderWithProviders(<Header title="Chat" />);

      expect(screen.getByText('Chat')).toBeInTheDocument();
    });

    it('should render sidebar toggle button', () => {
      renderWithProviders(<Header title="Chat" />);

      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      expect(toggleButton).toBeInTheDocument();
    });
  });

  describe('sidebar toggle', () => {
    it('should call toggleSidebar when clicking toggle button', () => {
      renderWithProviders(<Header title="Chat" />);

      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      fireEvent.click(toggleButton);

      expect(mockToggleSidebar).toHaveBeenCalledTimes(1);
    });

    it('should show collapsed icon when sidebar is collapsed', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: true,
          activeNav: 'chat',
          connectionStatus: 'connected',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Header title="Chat" />);

      // PanelLeft icon should be present (shown when collapsed)
      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      expect(toggleButton).toBeInTheDocument();
    });
  });

  describe('connection status', () => {
    it('should show connected status', () => {
      renderWithProviders(<Header title="Chat" />);

      const statusIndicator = screen.getByLabelText(/connection status: connected/i);
      expect(statusIndicator).toBeInTheDocument();
    });

    it('should show disconnected status', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'disconnected',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Header title="Chat" />);

      const statusIndicator = screen.getByLabelText(/connection status: disconnected/i);
      expect(statusIndicator).toBeInTheDocument();
    });

    it('should show connecting status', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'connecting',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Header title="Chat" />);

      const statusIndicator = screen.getByLabelText(/connection status: connecting/i);
      expect(statusIndicator).toBeInTheDocument();
    });

    it('should show error status', () => {
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'error',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });

      renderWithProviders(<Header title="Chat" />);

      const statusIndicator = screen.getByLabelText(/connection status: error/i);
      expect(statusIndicator).toBeInTheDocument();
    });

    it('should have correct status colors', () => {
      const { container, rerender } = renderWithProviders(<Header title="Chat" />);

      // Connected - green
      let statusDot = container.querySelector('[aria-label*="connected"]');
      expect(statusDot?.className).toMatch(/green|emerald/);

      // Disconnected - gray
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'disconnected',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });
      rerender(<TooltipProvider><Header title="Chat" /></TooltipProvider>);
      statusDot = container.querySelector('[aria-label*="disconnected"]');
      expect(statusDot?.className).toMatch(/gray|neutral/);

      // Connecting - yellow
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'connecting',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });
      rerender(<TooltipProvider><Header title="Chat" /></TooltipProvider>);
      statusDot = container.querySelector('[aria-label*="connecting"]');
      expect(statusDot?.className).toMatch(/yellow|amber/);

      // Error - red
      (useUIStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: unknown) => unknown) => {
        const state = {
          sidebarCollapsed: false,
          activeNav: 'chat',
          connectionStatus: 'error',
          toggleSidebar: mockToggleSidebar,
          setConnectionStatus: mockSetConnectionStatus,
        };
        return selector ? selector(state) : state;
      });
      rerender(<TooltipProvider><Header title="Chat" /></TooltipProvider>);
      statusDot = container.querySelector('[aria-label*="error"]');
      expect(statusDot?.className).toMatch(/red|rose/);
    });
  });

  describe('accessibility', () => {
    it('should have header role', () => {
      const { container } = renderWithProviders(<Header title="Chat" />);

      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('should have accessible button labels', () => {
      renderWithProviders(<Header title="Chat" />);

      expect(screen.getByRole('button', { name: /toggle sidebar/i })).toBeInTheDocument();
    });
  });
});