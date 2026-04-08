'use client';

/**
 * SourcesPanel - Left panel containing file tree, search, and vault path bar.
 */

import { useEffect, useRef } from 'react';
import { Search, ChevronLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { clearSelectedSources, getSelectedSources, selectSources } from '@/lib/api';
import { useChatStore, useUIStore } from '@/lib/store';
import { useSources } from '@/hooks/use-sources';
import { FileTree } from './file-tree';
import { VaultPathBar } from './vault-path-bar';

export function SourcesPanel() {
  const toggleLeftPanel = useUIStore((s) => s.toggleLeftPanel);
  const currentSessionId = useChatStore((s) => s.currentSessionId);
  const selectedSources = useChatStore((s) => s.selectedSources);
  const setSelectedSources = useChatStore((s) => s.setSelectedSources);
  const { tree, isLoading, searchQuery, setSearchQuery } = useSources();
  const isHydratingRef = useRef(false);
  const lastSyncedKeyRef = useRef<string>('');

  useEffect(() => {
    if (!currentSessionId) return;

    isHydratingRef.current = true;
    getSelectedSources(currentSessionId)
      .then((response) => {
        setSelectedSources(response.selected_sources);
        lastSyncedKeyRef.current = JSON.stringify(response.selected_sources);
      })
      .catch(() => {
        lastSyncedKeyRef.current = JSON.stringify(selectedSources);
      })
      .finally(() => {
        isHydratingRef.current = false;
      });
  }, [currentSessionId, setSelectedSources]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!currentSessionId || isHydratingRef.current) return;

    const serialized = JSON.stringify(selectedSources);
    if (serialized === lastSyncedKeyRef.current) return;

    const persist = async () => {
      if (selectedSources.length === 0) {
        await clearSelectedSources(currentSessionId);
      } else {
        await selectSources({
          session_id: currentSessionId,
          source_paths: selectedSources,
        });
      }
      lastSyncedKeyRef.current = serialized;
    };

    persist().catch(() => {
      // Ignore persistence errors here; the chat request still sends sources directly.
    });
  }, [currentSessionId, selectedSources]);

  return (
    <div className="flex h-full flex-col">
      {/* Panel Header */}
      <div className="flex h-[42px] shrink-0 items-center justify-between border-b border-[var(--panel-border)] px-3">
        <span className="text-[13px] font-semibold">Sources</span>
        <Button variant="ghost" size="icon" onClick={toggleLeftPanel} className="h-7 w-7">
          <ChevronLeft className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Search */}
      <div className="px-2 pt-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 text-sm"
          />
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto px-1 pt-1">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <FileTree tree={tree} />
        )}
      </div>

      {/* Vault Path Bar */}
      <VaultPathBar />
    </div>
  );
}
