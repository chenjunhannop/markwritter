import { FileText } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import type { Citation } from "@/types/chat";

interface CitationBadgeProps {
  citation: Citation;
  index: number;
}

function getFileName(path: string): string {
  return path.split("/").pop() ?? path;
}

export function CitationBadge({ citation, index }: CitationBadgeProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1 rounded-md border bg-muted/50 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <FileText className="h-3 w-3" />
          <span>{getFileName(citation.file_path)}</span>
          {citation.page_num > 0 && (
            <span className="text-muted-foreground">p.{citation.page_num}</span>
          )}
          <sup>{index + 1}</sup>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" side="top">
        <div className="space-y-2">
          <p className="text-xs font-medium">{citation.file_path}</p>
          {citation.page_num > 0 && (
            <p className="text-xs text-muted-foreground">
              Page {citation.page_num}, Paragraph {citation.paragraph_idx}
            </p>
          )}
          {citation.text_snippet && (
            <p className="rounded-md bg-muted p-2 text-xs leading-relaxed">
              {citation.text_snippet}
            </p>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
