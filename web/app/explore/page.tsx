'use client';

import { useEffect, useCallback } from 'react';
import { AppShell } from '@/components/apple';
import { FloatingPanel } from '@/components/apple';
import { KnowledgeGraph } from '@/components/explore/knowledge-graph';
import { NodeDetails } from '@/components/explore/node-details';
import { useExploreStore } from '@/lib/explore-store';

export default function ExplorePage() {
  const graphData = useExploreStore((state) => state.graphData);
  const selectedNode = useExploreStore((state) => state.selectedNode);
  const isLoading = useExploreStore((state) => state.isLoading);
  const error = useExploreStore((state) => state.error);
  const fetchGraph = useExploreStore((state) => state.fetchGraph);
  const clearError = useExploreStore((state) => state.clearError);

  useEffect(() => {
    if (!graphData) {
      fetchGraph();
    }
  }, [graphData, fetchGraph]);

  const handleNodeClick = useCallback((nodeId: string) => {
    useExploreStore.getState().selectNode(nodeId);
  }, []);

  const handleRefresh = useCallback(() => {
    fetchGraph();
  }, [fetchGraph]);

  return (
    <AppShell title="Knowledge Atlas" statusBadge="Live Graph">
      {error && (
        <div className="px-4 py-2 bg-destructive/10 border-b border-destructive/20 rounded-lg mb-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-destructive">{error}</p>
            <button
              onClick={clearError}
              className="text-destructive hover:text-destructive/80 text-sm"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-3 py-4 h-[calc(100vh-6rem)] overflow-hidden">
        {/* Graph Area */}
        <FloatingPanel className="flex-1 relative overflow-hidden">
          {isLoading && !graphData ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">
                  Loading knowledge graph...
                </p>
              </div>
            </div>
          ) : graphData ? (
            <KnowledgeGraph data={graphData} onNodeClick={handleNodeClick} />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground mb-4">
                  No graph data available
                </p>
                <button
                  onClick={handleRefresh}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90"
                >
                  Load Graph
                </button>
              </div>
            </div>
          )}
        </FloatingPanel>

        {/* Details Panel */}
        {selectedNode && (
          <FloatingPanel className="w-80 overflow-y-auto">
            <NodeDetails />
          </FloatingPanel>
        )}
      </div>
    </AppShell>
  );
}
