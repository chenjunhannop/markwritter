'use client';

/**
 * Editor Toolbar Component
 *
 * A toolbar for the markdown editor with formatting buttons.
 */

import { Button } from '@/components/ui/button';
import {
  Bold,
  Italic,
  Heading,
  Link,
  Code,
  FileCode,
  Braces,
  Quote,
  List,
  MessageSquarePlus,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface EditorToolbarProps {
  onBold: () => void;
  onItalic: () => void;
  onHeading: () => void;
  onLink: () => void;
  onCode: () => void;
  onCodeBlock: () => void;
  onWikilink: () => void;
  onCallout: (type?: string) => void;
  onQuote: () => void;
  onList: () => void;
  disabled?: boolean;
  className?: string;
}

interface ToolbarButtonProps {
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  tooltip: string;
  disabled?: boolean;
}

function ToolbarButton({
  onClick,
  icon,
  label,
  tooltip,
  disabled,
}: ToolbarButtonProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onClick}
          disabled={disabled}
          aria-label={label}
          className="h-8 w-8 p-0"
        >
          {icon}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <p>{tooltip}</p>
      </TooltipContent>
    </Tooltip>
  );
}

export function EditorToolbar({
  onBold,
  onItalic,
  onHeading,
  onLink,
  onCode,
  onCodeBlock,
  onWikilink,
  onCallout,
  onQuote,
  onList,
  disabled,
  className,
}: EditorToolbarProps) {
  return (
    <TooltipProvider>
      <div
        className={cn(
          'flex items-center gap-0.5 p-2 border-b bg-muted/30',
          className
        )}
        role="toolbar"
        aria-label="Formatting toolbar"
      >
        <ToolbarButton
          onClick={onBold}
          icon={<Bold className="h-4 w-4" />}
          label="Bold"
          tooltip="Bold (Ctrl+B)"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={onItalic}
          icon={<Italic className="h-4 w-4" />}
          label="Italic"
          tooltip="Italic (Ctrl+I)"
          disabled={disabled}
        />

        <div className="w-px h-6 bg-border mx-1" />

        <ToolbarButton
          onClick={onHeading}
          icon={<Heading className="h-4 w-4" />}
          label="Heading"
          tooltip="Heading"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={onQuote}
          icon={<Quote className="h-4 w-4" />}
          label="Quote"
          tooltip="Quote"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={onList}
          icon={<List className="h-4 w-4" />}
          label="List"
          tooltip="List"
          disabled={disabled}
        />

        <div className="w-px h-6 bg-border mx-1" />

        <ToolbarButton
          onClick={onLink}
          icon={<Link className="h-4 w-4" />}
          label="Link"
          tooltip="Link (Ctrl+K)"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={onCode}
          icon={<Code className="h-4 w-4" />}
          label="Code"
          tooltip="Inline code"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={onCodeBlock}
          icon={<FileCode className="h-4 w-4" />}
          label="Code block"
          tooltip="Code block"
          disabled={disabled}
        />

        <div className="w-px h-6 bg-border mx-1" />

        <ToolbarButton
          onClick={onWikilink}
          icon={<Braces className="h-4 w-4" />}
          label="Wikilink"
          tooltip="Wikilink [[link]]"
          disabled={disabled}
        />

        <ToolbarButton
          onClick={() => onCallout('note')}
          icon={<MessageSquarePlus className="h-4 w-4" />}
          label="Callout"
          tooltip="Callout"
          disabled={disabled}
        />
      </div>
    </TooltipProvider>
  );
}