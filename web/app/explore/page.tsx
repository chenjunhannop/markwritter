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
import { KnowledgeGraph } from '@/components/explore/knowledge-graph';
import { NodeDetails } from '@/components/explore/node-details';
import { useExploreStore } from '@/lib/explore-store';

export default function ExplorePage() {
  // Use individual selectors to avoid creating new object references
  const graphData = useExploreStore((state) => state.graphData);
  const selectedNode = useExploreStore((state) => state.selectedNode);
  const isLoading = useExploreStore((state) => state.isLoading);
  const error = useExploreStore((state) => state.error);
  const fetchGraph = useExploreStore((state) => state.fetchGraph);
  const clearError = useExploreStore((state) => state.clearError);

  // Fetch graph on mount
  useEffect(() => {
    if (!graphData) {
      fetchGraph();
    }
  }, [graphData, fetchGraph]);

  // Handle node click
  const handleNodeClick = useCallback((nodeId: string) => {
    useExploreStore.getState().selectNode(nodeId);
  }, []);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    fetchGraph();
  }, [fetchGraph]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Knowledge Graph
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Explore connections between your notes
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="px-6 py-3 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
            <div className="flex items-center justify-between">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              <button
                onClick={clearError}
                className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
              >
                <span className="sr-only">Dismiss</span>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Graph Area */}
          <div className="flex-1 relative">
            {isLoading && !graphData ? (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Loading knowledge graph...
                  </p>
                </div>
              </div>
            ) : graphData ? (
              <KnowledgeGraph data={graphData} onNodeClick={handleNodeClick} />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    No graph data available
                  </p>
                  <button
                    onClick={handleRefresh}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                  >
                    Load Graph
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Details Panel */}
          {selectedNode && (
            <div className="w-80 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-y-auto">
              <NodeDetails />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}