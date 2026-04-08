/**
 * Tests for UI Store - Panel State Management
 *
 * Tests panel collapse state and connection status.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useUIStore } from './store';

describe('useUIStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useUIStore.setState({
      connectionStatus: 'connected',
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
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

  describe('panel state', () => {
    it('should start with both panels expanded', () => {
      const state = useUIStore.getState();

      expect(state.leftPanelCollapsed).toBe(false);
      expect(state.rightPanelCollapsed).toBe(false);
    });

    it('should toggle left panel collapsed state', () => {
      const store = useUIStore.getState();

      act(() => {
        store.toggleLeftPanel();
      });

      expect(useUIStore.getState().leftPanelCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().toggleLeftPanel();
      });

      expect(useUIStore.getState().leftPanelCollapsed).toBe(false);
    });

    it('should toggle right panel collapsed state', () => {
      const store = useUIStore.getState();

      act(() => {
        store.toggleRightPanel();
      });

      expect(useUIStore.getState().rightPanelCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().toggleRightPanel();
      });

      expect(useUIStore.getState().rightPanelCollapsed).toBe(false);
    });

    it('should set panel collapsed state directly', () => {
      act(() => {
        useUIStore.getState().setLeftPanelCollapsed(true);
      });

      expect(useUIStore.getState().leftPanelCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().setRightPanelCollapsed(true);
      });

      expect(useUIStore.getState().rightPanelCollapsed).toBe(true);

      act(() => {
        useUIStore.getState().setLeftPanelCollapsed(false);
        useUIStore.getState().setRightPanelCollapsed(false);
      });

      expect(useUIStore.getState().leftPanelCollapsed).toBe(false);
      expect(useUIStore.getState().rightPanelCollapsed).toBe(false);
    });
  });

  describe('hook usage', () => {
    it('should work with renderHook', () => {
      const { result } = renderHook(() => useUIStore());

      expect(result.current.leftPanelCollapsed).toBe(false);
      expect(result.current.rightPanelCollapsed).toBe(false);
      expect(result.current.connectionStatus).toBe('connected');
    });

    it('should update state through hook', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleLeftPanel();
      });

      expect(result.current.leftPanelCollapsed).toBe(true);

      act(() => {
        result.current.toggleRightPanel();
      });

      expect(result.current.rightPanelCollapsed).toBe(true);
    });
  });
});
