import { Loader2, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { NodeDetails } from "@/types/explore";

const NODE_COLORS: Record<string, string> = {
  person: "#6B8DB5",
  topic: "#6D9B5E",
  concept: "#9B7B8E",
  note: "#E6A23C",
};

interface NodeDetailPanelProps {
  detail: NodeDetails | null;
  isLoading: boolean;
  onClose: () => void;
  onNodeClick: (nodeId: string) => void;
}

export function NodeDetailPanel({
  detail,
  isLoading,
  onClose,
  onNodeClick,
}: NodeDetailPanelProps) {
  if (!detail && !isLoading) return null;

  return (
    <div className="absolute right-0 top-0 bottom-0 z-10 w-80 border-l border-border bg-background shadow-lg flex flex-col">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="text-sm font-semibold">Node Detail</span>
        <button
          type="button"
          onClick={onClose}
          className="rounded-sm p-1 hover:bg-muted transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      {isLoading && (
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </div>
      )}
      {detail && !isLoading && (
        <ScrollArea className="flex-1">
          <div className="space-y-4 p-4">
            <div>
              <h3 className="text-lg font-bold">{detail.node.label}</h3>
              <Badge
                className="mt-1.5 text-white"
                style={{
                  backgroundColor: NODE_COLORS[detail.node.type] ?? "#C75050",
                }}
              >
                {detail.node.type}
              </Badge>
            </div>
            {detail.connections.incoming.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Incoming
                </p>
                {detail.connections.incoming.map((edge) => (
                  <button
                    type="button"
                    key={edge.id}
                    onClick={() => onNodeClick(edge.source)}
                    className="block w-full rounded-md px-2 py-1.5 text-left text-sm hover:bg-muted transition-colors"
                  >
                    <span className="font-medium">{edge.source}</span>
                    <span className="text-muted-foreground">
                      {" "}
                      → {edge.label}
                    </span>
                  </button>
                ))}
              </div>
            )}
            {detail.connections.outgoing.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Outgoing
                </p>
                {detail.connections.outgoing.map((edge) => (
                  <button
                    type="button"
                    key={edge.id}
                    onClick={() => onNodeClick(edge.target)}
                    className="block w-full rounded-md px-2 py-1.5 text-left text-sm hover:bg-muted transition-colors"
                  >
                    <span className="font-medium">{edge.target}</span>
                    <span className="text-muted-foreground">
                      {" "}
                      → {edge.label}
                    </span>
                  </button>
                ))}
              </div>
            )}
            {detail.relatedNodes.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                  Related Nodes
                </p>
                {detail.relatedNodes.map((node) => (
                  <button
                    type="button"
                    key={node.id}
                    onClick={() => onNodeClick(node.id)}
                    className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted transition-colors"
                  >
                    <div
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{
                        backgroundColor: NODE_COLORS[node.type] ?? "#C75050",
                      }}
                    />
                    <span className="truncate">{node.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
