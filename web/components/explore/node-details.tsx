'use client';

/**
 * Node Details Component
 *
 * Displays details for a selected node including:
 * - Title and path
 * - Tags
 * - Connection count
 * - Related notes
 */

import { useEffect } from 'react';
import { useExploreStore } from '@/lib/explore-store';

export function NodeDetails() {
  // Use individual selectors to avoid creating new object references
  const selectedNode = useExploreStore((state) => state.selectedNode);
  const selectedNodeEdges = useExploreStore((state) => state.selectedNodeEdges);
  const relatedNotes = useExploreStore((state) => state.relatedNotes);
  const isLoading = useExploreStore((state) => state.isLoading);
  const fetchRelatedNotes = useExploreStore((state) => state.fetchRelatedNotes);
  const clearSelection = useExploreStore((state) => state.clearSelection);

  // Fetch related notes when node is selected
  useEffect(() => {
    if (selectedNode) {
      fetchRelatedNotes(selectedNode.id, 1);
    }
  }, [selectedNode, fetchRelatedNotes]);

  if (!selectedNode) {
    return null;
  }

  const incomingEdges = selectedNodeEdges.filter((e) => e.target === selectedNode.id);
  const outgoingEdges = selectedNodeEdges.filter((e) => e.source === selectedNode.id);

  return (
    <div className="p-4">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {selectedNode.title}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {selectedNode.path}
          </p>
        </div>
        <button
          onClick={clearSelection}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {selectedNode.connections_count}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Connections
          </div>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {outgoingEdges.length}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Links Out</div>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {incomingEdges.length}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Links In</div>
        </div>
      </div>

      {/* Tags */}
      {selectedNode.tags.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Tags
          </h3>
          <div className="flex flex-wrap gap-1">
            {selectedNode.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Outgoing Links */}
      {outgoingEdges.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Links To
          </h3>
          <ul className="space-y-1">
            {outgoingEdges.map((edge) => (
              <li key={edge.target}>
                <button
                  onClick={() => useExploreStore.getState().selectNode(edge.target)}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline truncate block w-full text-left"
                >
                  {edge.target}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Incoming Links */}
      {incomingEdges.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Linked From
          </h3>
          <ul className="space-y-1">
            {incomingEdges.map((edge) => (
              <li key={edge.source}>
                <button
                  onClick={() => useExploreStore.getState().selectNode(edge.source)}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline truncate block w-full text-left"
                >
                  {edge.source}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Related Notes */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Related Notes
        </h3>
        {isLoading ? (
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        ) : relatedNotes.length > 0 ? (
          <ul className="space-y-2">
            {relatedNotes.map((note) => (
              <li key={note.path}>
                <button
                  onClick={() => useExploreStore.getState().selectNode(note.path)}
                  className="w-full text-left p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {note.title || note.path}
                  </div>
                  {note.tags.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {note.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="text-xs text-gray-500 dark:text-gray-400"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No related notes found
          </p>
        )}
      </div>
    </div>
  );
}