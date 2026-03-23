/**
 * IntentDisplay Component for Markwritter
 *
 * Displays parsed intent information including:
 * - Skill name and parameters
 * - Confidence score
 * - Visual indicators
 */

'use client';

import { Wrench, MessageSquare } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import type { Intent, SkillIntent } from '@/lib/types';
import { isSkillIntent } from '@/lib/types';

interface IntentDisplayProps {
  /** The intent to display */
  intent: Intent;
  /** Show compact view */
  compact?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * Get confidence level styling
 */
function getConfidenceStyle(confidence: number): string {
  if (confidence >= 0.8) {
    return 'text-green-500';
  }
  if (confidence >= 0.5) {
    return 'text-amber-500';
  }
  return 'text-red-500';
}

/**
 * Get progress bar color
 */
function getProgressColor(confidence: number): string {
  if (confidence >= 0.8) {
    return 'bg-green-500';
  }
  if (confidence >= 0.5) {
    return 'bg-amber-500';
  }
  return 'bg-red-500';
}

/**
 * Render parameter value
 */
function renderParamValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'null';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

/**
 * Parameters display component
 */
function ParamsDisplay({ params }: { params: Record<string, unknown> }) {
  const entries = Object.entries(params);

  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="space-y-1 text-sm">
      {entries.map(([key, value]) => (
        <div key={key} className="flex gap-2">
          <span className="text-muted-foreground">{key}:</span>
          <span className="font-medium truncate max-w-[200px]" title={renderParamValue(value)}>
            {renderParamValue(value)}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Skill intent display
 */
function SkillIntentDisplay({
  intent,
  compact,
}: {
  intent: SkillIntent;
  compact?: boolean;
}) {
  const confidencePercent = Math.round(intent.confidence * 100);

  return (
    <>
      <div className="flex items-center gap-2">
        <Wrench className="h-4 w-4" aria-label="Skill" />
        <span className="font-semibold truncate" title={intent.skillName}>
          {intent.skillName}
        </span>
        <Badge variant="outline" className="ml-auto">
          Skill
        </Badge>
      </div>

      {!compact && intent.params && Object.keys(intent.params).length > 0 && (
        <div className="mt-2 pt-2 border-t">
          <ParamsDisplay params={intent.params} />
        </div>
      )}

      <div className="flex items-center gap-2 mt-2">
        <Progress
          value={confidencePercent}
          className="flex-1 h-2"
          // Custom color based on confidence
          style={
            {
              '--progress-background': getProgressColor(intent.confidence),
            } as React.CSSProperties
          }
        />
        <span
          className={cn(
            'text-sm font-medium',
            getConfidenceStyle(intent.confidence)
          )}
        >
          {confidencePercent}%
        </span>
      </div>
    </>
  );
}

/**
 * Chat intent display
 */
function ChatIntentDisplay({ intent }: { intent: Intent }) {
  const confidencePercent = Math.round(intent.confidence * 100);

  return (
    <>
      <div className="flex items-center gap-2">
        <MessageSquare className="h-4 w-4" aria-label="Chat" />
        <span className="font-semibold">Chat</span>
        <Badge variant="secondary" className="ml-auto">
          Conversation
        </Badge>
      </div>

      <div className="flex items-center gap-2 mt-2">
        <Progress
          value={confidencePercent}
          className="flex-1 h-2"
          style={
            {
              '--progress-background': getProgressColor(intent.confidence),
            } as React.CSSProperties
          }
        />
        <span
          className={cn(
            'text-sm font-medium',
            getConfidenceStyle(intent.confidence)
          )}
        >
          {confidencePercent}%
        </span>
      </div>
    </>
  );
}

export function IntentDisplay({
  intent,
  compact = false,
  className,
}: IntentDisplayProps) {
  const confidencePercent = Math.round(intent.confidence * 100);

  return (
    <Card
      className={cn('w-full', className)}
      role="region"
      aria-label="Intent information"
    >
      <CardHeader className="p-3 pb-0">
        <CardTitle className="text-sm sr-only">
          {isSkillIntent(intent)
            ? `Skill: ${intent.skillName}`
            : 'Chat intent'}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        {isSkillIntent(intent) ? (
          <SkillIntentDisplay intent={intent} compact={compact} />
        ) : (
          <ChatIntentDisplay intent={intent} />
        )}

        {/* Hidden progress bar for accessibility */}
        <div
          role="progressbar"
          aria-valuenow={confidencePercent}
          aria-valuemin={0}
          aria-valuemax={100}
          className="sr-only"
        >
          Confidence: {confidencePercent}%
        </div>
      </CardContent>
    </Card>
  );
}