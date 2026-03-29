'use client';

/**
 * useSources Hook - Orchestrates file tree loading and connects stores.
 */

import { useEffect, useCallback } from 'react';
import { useSourcesStore } from '@/lib/sources-store';
import { useSettingsStore } from '@/lib/settings-store';
import { getSettings } from '@/lib/api';

export function useSources() {
  const tree = useSourcesStore((s) => s.tree);
  const isLoading = useSourcesStore((s) => s.isLoading);
  const error = useSourcesStore((s) => s.error);
  const searchQuery = useSourcesStore((s) => s.searchQuery);
  const setSearchQuery = useSourcesStore((s) => s.setSearchQuery);
  const loadTree = useSourcesStore((s) => s.loadTree);
  const vaultPath = useSettingsStore((s) => s.vaultPath);

  // Sync vault path from server on mount
  useEffect(() => {
    getSettings()
      .then((settings) => {
        if (settings.vault_path && settings.vault_path !== vaultPath) {
          useSettingsStore.getState().setVaultPath(settings.vault_path as string);
        }
      })
      .catch(() => {
        // Server unreachable, use local value
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load tree when vault path is available
  useEffect(() => {
    if (vaultPath && tree.length === 0 && !isLoading) {
      loadTree();
    }
  }, [vaultPath]); // eslint-disable-line react-hooks/exhaustive-deps

  const refreshTree = useCallback(async () => {
    await loadTree();
  }, [loadTree]);

  return {
    tree,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    refreshTree,
  };
}
