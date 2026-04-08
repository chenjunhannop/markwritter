'use client';

/**
 * StudioPanel - Right panel with tool grid and recent outputs.
 * Phase 1: All tools are placeholder ("Coming soon").
 */

import { Network, FileText, Mic, Monitor, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/store';
import { toast } from 'sonner';
import { StudioCard } from './studio-card';

const STUDIO_TOOLS = [
  {
    id: 'mindmap',
    name: 'Mind Map',
    description: 'Visualize knowledge connections',
    icon: Network,
    iconBgColor: 'hsl(220 70% 95%)',
    iconColor: 'hsl(220 70% 40%)',
  },
  {
    id: 'summary',
    name: 'Summary',
    description: 'Generate content summary',
    icon: FileText,
    iconBgColor: 'hsl(160 60% 93%)',
    iconColor: 'hsl(160 60% 35%)',
  },
  {
    id: 'voice',
    name: 'Voice',
    description: 'Text to speech playback',
    icon: Mic,
    iconBgColor: 'hsl(30 90% 95%)',
    iconColor: 'hsl(30 90% 40%)',
  },
  {
    id: 'slides',
    name: 'Slides',
    description: 'Create presentation',
    icon: Monitor,
    iconBgColor: 'hsl(280 60% 95%)',
    iconColor: 'hsl(280 60% 40%)',
  },
] as const;

export function StudioPanel() {
  const toggleRightPanel = useUIStore((s) => s.toggleRightPanel);

  const handleToolClick = (name: string) => {
    toast.info(`${name} is coming soon`);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Panel Header */}
      <div className="flex h-[42px] shrink-0 items-center justify-between border-b border-[var(--panel-border)] px-3">
        <span className="text-[13px] font-semibold">Studio</span>
        <Button variant="ghost" size="icon" onClick={toggleRightPanel} className="h-7 w-7">
          <ChevronRight className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Tool Grid */}
      <div className="flex flex-col gap-3 p-3">
        {STUDIO_TOOLS.map((tool, idx) => (
          <StudioCard
            key={tool.id}
            name={tool.name}
            description={tool.description}
            icon={tool.icon}
            iconBgColor={tool.iconBgColor}
            iconColor={tool.iconColor}
            variant={tool.id === 'summary' ? 'dark' : 'default'}
            disabled
            onClick={() => handleToolClick(tool.name)}
          />
        ))}
      </div>

      {/* Recent Outputs */}
      <div className="border-t px-3 pb-3 pt-3">
        <div className="mb-2 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          Recent Outputs
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Generated outputs will appear here. Add sources and try the tools
          above.
        </p>
      </div>
    </div>
  );
}
