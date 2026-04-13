import type { NodeProps } from "@xyflow/react";
import { Handle, Position } from "@xyflow/react";

const NODE_COLORS: Record<string, string> = {
  person: "#6B8DB5",
  topic: "#6D9B5E",
  concept: "#9B7B8E",
  note: "#E6A23C",
};

function truncateLabel(label: string, maxLen = 15): string {
  if (label.length <= maxLen) return label;
  return `${label.slice(0, maxLen)}…`;
}

export interface GraphNodeData {
  label: string;
  nodeType: string;
  [key: string]: unknown;
}

export function GraphNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as GraphNodeData;
  const color = NODE_COLORS[nodeData.nodeType] ?? "#C75050";

  return (
    <div
      className="group relative flex items-center justify-center"
      style={{ width: 72, height: 72 }}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!w-2 !h-2 !bg-muted-foreground"
        style={{ top: 0 }}
      />

      <div
        className="flex h-16 w-16 items-center justify-center rounded-full border-2 transition-shadow"
        style={{
          borderColor: selected ? color : "transparent",
          backgroundColor: `${color}20`,
          boxShadow: selected ? `0 0 0 2px ${color}40` : undefined,
        }}
      >
        <div
          className="h-12 w-12 rounded-full flex items-center justify-center text-white text-xs font-semibold"
          style={{ backgroundColor: color }}
          title={nodeData.label}
        >
          {truncateLabel(nodeData.label)}
        </div>
      </div>

      <div
        className="pointer-events-none absolute -bottom-5 text-xs text-muted-foreground text-center whitespace-nowrap max-w-20 truncate"
        title={nodeData.label}
      >
        {truncateLabel(nodeData.label)}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-2 !h-2 !bg-muted-foreground"
        style={{ bottom: 0 }}
      />
    </div>
  );
}
