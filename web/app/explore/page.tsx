'use client';

/**
 * Explore Page
 *
 * Knowledge graph visualization with:
 * - Interactive graph with React Flow
 * - Node details panel
 * - Related notes list
 */

import { useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout';
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
    <MainLayout title="Explore">
      {/* Error Banner */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 border-b border-destructive/20">
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

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Graph Area */}
        <div className="flex-1 relative">
          {isLoading && !graphData ? (
            <div className="absolute inset-0 flex items-center justify-center bg-background">
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
            <div className="absolute inset-0 flex items-center justify-center bg-background">
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
        </div>

        {/* Details Panel */}
        {selectedNode && (
          <div className="w-80 border-l bg-background overflow-y-auto">
            <NodeDetails />
          </div>
        )}
      </div>
    </MainLayout>
  );
}
