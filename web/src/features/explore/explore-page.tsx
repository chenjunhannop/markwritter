import { useQuery } from "@tanstack/react-query";
import {
  Background,
  Controls,
  type Edge,
  MiniMap,
  type Node,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { AlertCircle, Loader2, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { GraphData } from "@/types/explore";
import {
  getGraph,
  getGraphStats,
  getNodeDetail,
  searchGraph,
} from "./explore-api";
import { GraphNode } from "./graph-node";
import { NodeDetailPanel } from "./node-detail-panel";

const NODE_COLORS: Record<string, string> = {
  person: "#6B8DB5",
  topic: "#6D9B5E",
  concept: "#9B7B8E",
  note: "#E6A23C",
};

const nodeTypes = { custom: GraphNode };

function graphDataToFlowNodes(data: GraphData): Node[] {
  const cols = Math.ceil(Math.sqrt(data.nodes.length));
  return data.nodes.map((gn, i) => ({
    id: gn.id,
    type: "custom",
    position: {
      x: (i % cols) * 140 + Math.random() * 40,
      y: Math.floor(i / cols) * 140 + Math.random() * 40,
    },
    data: { label: gn.label, nodeType: gn.type, ...gn.data },
  }));
}

function graphDataToFlowEdges(data: GraphData): Edge[] {
  return data.edges.map((ge) => ({
    id: ge.id,
    source: ge.source,
    target: ge.target,
    label: ge.label,
    type: "smoothstep",
    animated: true,
  }));
}

export function ExplorePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [appliedQuery, setAppliedQuery] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const {
    data: graphData,
    isLoading: graphLoading,
    isError: graphError,
    refetch: refetchGraph,
  } = useQuery({
    queryKey: ["explore-graph"],
    queryFn: getGraph,
  });

  const { data: searchData, isLoading: searchLoading } = useQuery({
    queryKey: ["explore-search", appliedQuery],
    queryFn: () => searchGraph(appliedQuery),
    enabled: appliedQuery.length > 0,
  });

  const { data: stats } = useQuery({
    queryKey: ["explore-stats"],
    queryFn: getGraphStats,
  });

  const { data: nodeDetail, isLoading: detailLoading } = useQuery({
    queryKey: ["explore-node-detail", selectedNodeId],
    queryFn: () => getNodeDetail(selectedNodeId as string),
    enabled: !!selectedNodeId,
  });

  const activeData = appliedQuery ? searchData : graphData;
  const flowNodes = useMemo(
    () => (activeData ? graphDataToFlowNodes(activeData) : []),
    [activeData],
  );
  const flowEdges = useMemo(
    () => (activeData ? graphDataToFlowEdges(activeData) : []),
    [activeData],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const handleSearch = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setAppliedQuery(searchQuery.trim());
      setSelectedNodeId(null);
    },
    [searchQuery],
  );

  const handleClearSearch = useCallback(() => {
    setSearchQuery("");
    setAppliedQuery("");
    setSelectedNodeId(null);
  }, []);

  const handlePanelNodeClick = useCallback((nodeId: string) => {
    setSelectedNodeId(nodeId);
  }, []);

  const handlePanelClose = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  if (graphLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (graphError) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-sm text-muted-foreground">
          Failed to load graph data.
        </p>
        <Button variant="outline" onClick={() => refetchGraph()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <div className="absolute left-4 right-4 top-4 z-10 flex items-center gap-3">
        <form onSubmit={handleSearch} className="relative flex-1 max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search nodes..."
            className="pl-9 pr-16 bg-background/90 backdrop-blur-sm border-border shadow-sm"
          />
          {appliedQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              Clear
            </button>
          )}
        </form>

        {stats && (
          <div className="flex items-center gap-3 rounded-md border border-border bg-background/90 backdrop-blur-sm px-3 py-1.5 text-xs text-muted-foreground shadow-sm whitespace-nowrap">
            <span>{stats.total_nodes} nodes</span>
            <span className="text-border">|</span>
            <span>{stats.total_edges} edges</span>
          </div>
        )}

        {searchLoading && (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        )}
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
      >
        <MiniMap
          nodeColor={(node) => {
            const nodeData = node.data as { nodeType?: string };
            return NODE_COLORS[nodeData?.nodeType ?? ""] ?? "#C75050";
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
          className="!bg-background !border-border"
        />
        <Controls className="!bg-background !border-border [&>button]:!bg-background [&>button]:!border-border [&>button:hover]:!bg-muted" />
        <Background color="var(--color-border)" gap={16} size={1} />
      </ReactFlow>

      <div className="absolute bottom-4 left-4 z-10 flex items-center gap-3 rounded-md border border-border bg-background/90 backdrop-blur-sm px-3 py-2 text-xs shadow-sm">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-muted-foreground capitalize">{type}</span>
          </span>
        ))}
      </div>

      <NodeDetailPanel
        detail={nodeDetail ?? null}
        isLoading={detailLoading}
        onClose={handlePanelClose}
        onNodeClick={handlePanelNodeClick}
      />
    </div>
  );
}
