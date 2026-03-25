'use client';

/**
 * Knowledge Graph Component
 *
 * Interactive graph visualization using React Flow.
 * Features:
 * - Node positioning based on connections
 * - Color coding by connection count
 * - Drag, zoom, pan interactions
 * - Click to select node
 */

import { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { GraphData } from '@/lib/explore-api';

// Color scale for connection counts
const getConnectionColor = (count: number): string => {
  if (count === 0) return '#94a3b8'; // gray-400
  if (count <= 2) return '#22c55e'; // green-500
  if (count <= 5) return '#3b82f6'; // blue-500
  if (count <= 10) return '#f59e0b'; // amber-500
  return '#ef4444'; // red-500
};

// Calculate node size based on connections
const getNodeSize = (count: number): number => {
  const baseSize = 20;
  const maxExtra = 30;
  const maxConnections = 20;
  const extra = Math.min(count / maxConnections, 1) * maxExtra;
  return baseSize + extra;
};

interface KnowledgeGraphProps {
  data: GraphData;
  onNodeClick: (nodeId: string) => void;
}

export function KnowledgeGraph({ data, onNodeClick }: KnowledgeGraphProps) {
  // Convert graph data to React Flow format
  const initialNodes: Node[] = useMemo(() => {
    // Simple layout algorithm - position nodes in a circle
    const nodeCount = data.nodes.length;
    const centerX = 400;
    const centerY = 300;
    const radius = Math.min(250, Math.max(150, nodeCount * 10));

    return data.nodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / nodeCount;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: node.id,
        type: 'default',
        position: { x, y },
        data: {
          label: node.title || node.id,
          tags: node.tags,
          connections: node.connections_count,
        },
        style: {
          background: getConnectionColor(node.connections_count),
          color: '#fff',
          border: '2px solid #fff',
          borderRadius: '50%',
          fontSize: 12,
          width: getNodeSize(node.connections_count),
          height: getNodeSize(node.connections_count),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        },
      };
    });
  }, [data.nodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return data.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      type: 'default',
      animated: false,
      style: { stroke: '#64748b', strokeWidth: 1 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#64748b',
      },
    }));
  }, [data.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when data changes
  useMemo(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Handle node click
  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      onNodeClick(node.id);
    },
    [onNodeClick]
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        attributionPosition="bottom-left"
        className="bg-gray-50 dark:bg-gray-900"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#94a3b8"
        />
        <Controls
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm"
        />
        <MiniMap
          nodeColor={(node) => {
            const connections = node.data?.connections as number | undefined;
            return getConnectionColor(connections || 0);
          }}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm">
        <h3 className="text-xs font-medium text-gray-900 dark:text-gray-100 mb-2">
          Connections
        </h3>
        <div className="flex flex-col gap-1">
          {[
            { color: '#94a3b8', label: '0' },
            { color: '#22c55e', label: '1-2' },
            { color: '#3b82f6', label: '3-5' },
            { color: '#f59e0b', label: '6-10' },
            { color: '#ef4444', label: '10+' },
          ].map(({ color, label }) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}