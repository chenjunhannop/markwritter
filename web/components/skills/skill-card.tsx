/**
 * SkillCard Component
 *
 * Displays a skill card with name, description, version, and actions.
 * Uses Shadcn Card components for styling.
 */

import Link from 'next/link';
import { Play, Pencil, Trash2, Loader2 } from 'lucide-react';

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Skill } from '@/lib/types';

interface SkillCardProps {
  /** Skill data to display */
  skill: Skill;
  /** Custom class name */
  className?: string;
  /** Loading state */
  isLoading?: boolean;
  /** Delete callback */
  onDelete?: (skillName: string) => void;
}

/**
 * SkillCard displays a single skill's information with actions.
 */
export function SkillCard({ skill, className, isLoading, onDelete }: SkillCardProps) {
  const requiredInputs = skill.inputs.filter((input) => input.required).length;
  const hasRequiredInputs = requiredInputs > 0;

  return (
    <Card
      data-testid="skill-card"
      className={cn('flex flex-col', className)}
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg">{skill.name}</CardTitle>
          <Badge variant="secondary">{skill.version}</Badge>
        </div>
        <CardDescription className="line-clamp-2">
          {skill.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1">
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <span>
            {skill.inputs.length} input{skill.inputs.length !== 1 ? 's' : ''}
          </span>
          {hasRequiredInputs && (
            <span className="text-destructive">
              ({requiredInputs} required)
            </span>
          )}
          <span className="text-muted-foreground/50">|</span>
          <span>Output: {skill.output.type}</span>
        </div>
      </CardContent>

      <CardFooter className="gap-2">
        <Link
          href={`/skills/${skill.name}`}
          className={cn(
            'flex-1',
            isLoading && 'pointer-events-none opacity-50'
          )}
        >
          <Button className="w-full" disabled={isLoading}>
            <Play className="mr-2 h-4 w-4" />
            Run
          </Button>
        </Link>

        <Link
          href={`/skills/${skill.name}/edit`}
          className={cn(isLoading && 'pointer-events-none opacity-50')}
        >
          <Button variant="outline" size="icon" disabled={isLoading}>
            <Pencil className="h-4 w-4" />
            <span className="sr-only">Edit</span>
          </Button>
        </Link>

        {onDelete && (
          <Button
            variant="outline"
            size="icon"
            disabled={isLoading}
            onClick={() => onDelete(skill.name)}
            aria-label={`Delete ${skill.name}`}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            <span className="sr-only">Delete</span>
          </Button>
        )}
      </CardFooter>

      {isLoading && (
        <div
          role="status"
          className="absolute inset-0 flex items-center justify-center bg-background/50"
        >
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      )}
    </Card>
  );
}