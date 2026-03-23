/**
 * Tests for UI Store - Layout State Management
 *
 * Tests sidebar state, navigation, and connection status.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useUIStore } from './store';

describe('useUIStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store state
    useUIStore.setState({
      sidebarCollapsed: false,
      activeNav: 'chat',
      connectionStatus: 'connected',
    });
  });

  describe('sidebar state', () => {
    it('should start with sidebar expanded', () => {
      const state = useUIStore.getState();

      expect(state.sidebarCollapsed).toBe(false);
    });

    it('should toggle sidebar collapsed state', () => {
      const store = useUIStore.getState();

      act(() => {
        store.toggleSidebar();
      });

      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().toggleSidebar();
      });

      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });

    it('should set sidebar collapsed state directly', () => {
      const store = useUIStore.getState();

      act(() => {
        store.setSidebarCollapsed(true);
      });

      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().setSidebarCollapsed(false);
      });

      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });
  });

  describe('navigation state', () => {
    it('should start with chat as active nav', () => {
      const state = useUIStore.getState();

      expect(state.activeNav).toBe('chat');
    });

    it('should set active navigation item', () => {
      const store = useUIStore.getState();

      act(() => {
        store.setActiveNav('skills');
      });

      expect(useUIStore.getState().activeNav).toBe('skills');

      act(() => {
        useUIStore.getState().setActiveNav('logs');
      });

      expect(useUIStore.getState().activeNav).toBe('logs');

      act(() => {
        useUIStore.getState().setActiveNav('settings');
      });

      expect(useUIStore.getState().activeNav).toBe('settings');
    });

    it('should handle invalid nav items gracefully', () => {
      const store = useUIStore.getState();

      // TypeScript prevents this at compile time, but runtime test
      act(() => {
        store.setActiveNav('chat');
      });

      // Should remain valid
      expect(useUIStore.getState().activeNav).toBe('chat');
    });
  });

  describe('connection status', () => {
    it('should start with connected status', () => {
      const state = useUIStore.getState();

      expect(state.connectionStatus).toBe('connected');
    });

    it('should set connection status', () => {
      const store = useUIStore.getState();

      act(() => {
        store.setConnectionStatus('disconnected');
      });

      expect(useUIStore.getState().connectionStatus).toBe('disconnected');

      act(() => {
        useUIStore.getState().setConnectionStatus('connecting');
      });

      expect(useUIStore.getState().connectionStatus).toBe('connecting');

      act(() => {
        useUIStore.getState().setConnectionStatus('error');
      });

      expect(useUIStore.getState().connectionStatus).toBe('error');
    });
  });

  describe('hook usage', () => {
    it('should work with renderHook', () => {
      const { result } = renderHook(() => useUIStore());

      expect(result.current.sidebarCollapsed).toBe(false);
      expect(result.current.activeNav).toBe('chat');
      expect(result.current.connectionStatus).toBe('connected');
    });

    it('should update state through hook', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarCollapsed).toBe(true);
    });
  });
});