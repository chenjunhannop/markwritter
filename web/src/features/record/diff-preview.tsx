import { Check, RotateCcw, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { DiffDelta } from "@/types/record";
import { trackTelemetry } from "./record-api";

interface DiffPreviewProps {
  delta: DiffDelta[];
  original: string;
  modified: string;
  actionType: string;
  startTime: number;
  onAccept: (modified: string) => void;
  onReject: () => void;
}

function DiffSegment({ segment }: { segment: DiffDelta }) {
  if (segment.op === "equal") {
    return <span>{segment.text}</span>;
  }
  if (segment.op === "insert") {
    return (
      <span className="bg-green-500/15 rounded-sm px-0.5">{segment.text}</span>
    );
  }
  if (segment.op === "delete") {
    return (
      <span className="bg-red-500/15 line-through rounded-sm px-0.5">
        {segment.text}
      </span>
    );
  }
  return null;
}

export function DiffPreview({
  delta,
  modified,
  actionType,
  startTime,
  onAccept,
  onReject,
}: DiffPreviewProps) {
  const [accepted, setAccepted] = useState(false);
  const [undoDeadline, setUndoDeadline] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleAccept = useCallback(() => {
    setAccepted(true);
    onAccept(modified);
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: true,
    });
    timerRef.current = setTimeout(() => {
      setUndoDeadline(true);
    }, 30_000);
  }, [modified, actionType, startTime, onAccept]);

  const handleUndo = useCallback(() => {
    setAccepted(false);
    setUndoDeadline(false);
    if (timerRef.current) clearTimeout(timerRef.current);
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: false,
    });
  }, [modified, actionType, startTime]);

  const handleReject = useCallback(() => {
    onReject();
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: false,
    });
  }, [modified, actionType, startTime, onReject]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  if (accepted && undoDeadline) return null;

  if (accepted) {
    return (
      <div className="flex items-center gap-2 rounded-md border border-green-500/30 bg-green-500/10 px-3 py-2">
        <Check className="h-4 w-4 text-green-600" />
        <span className="text-sm text-green-600">Changes accepted</span>
        <Button
          variant="outline"
          size="sm"
          onClick={handleUndo}
          className="ml-auto"
        >
          <RotateCcw className="mr-1 h-3 w-3" />
          Undo
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <div className="flex items-center justify-between border-b px-3 py-2">
        <span className="text-sm font-medium">Diff Preview</span>
      </div>
      <ScrollArea className="max-h-64">
        <div className="whitespace-pre-wrap px-3 py-2 font-mono text-sm leading-relaxed">
          {delta.map((segment, i) => (
            <DiffSegment key={String(i)} segment={segment} />
          ))}
        </div>
      </ScrollArea>
      <div className="flex items-center gap-2 border-t px-3 py-2">
        <Button size="sm" onClick={handleAccept}>
          <Check className="mr-1 h-3 w-3" />
          Accept
        </Button>
        <Button variant="outline" size="sm" onClick={handleReject}>
          <X className="mr-1 h-3 w-3" />
          Reject
        </Button>
      </div>
    </div>
  );
}
