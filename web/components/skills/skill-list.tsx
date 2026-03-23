/**
 * SkillList Component
 *
 * Displays a searchable, filterable list of skill cards.
 * Uses useSkillStore for state management.
 */

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { Search, X, Loader2, AlertCircle, Plus } from 'lucide-react';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useSkillStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { SkillCard } from './skill-card';

interface SkillListProps {
  /** Custom class name */
  className?: string;
  /** Callback when a skill is deleted */
  onDelete?: (skillName: string) => void;
}

/**
 * SkillList displays a searchable grid of skill cards.
 */
export function SkillList({ className, onDelete }: SkillListProps) {
  const { skills, isLoading, error, loadSkills } = useSkillStore();
  const [searchQuery, setSearchQuery] = useState('');

  // Load skills on mount if empty
  useEffect(() => {
    if (skills.length === 0 && !isLoading) {
      loadSkills();
    }
  }, [skills.length, isLoading, loadSkills]);

  // Filter skills based on search query
  const filteredSkills = useMemo(() => {
    if (!searchQuery.trim()) {
      return skills;
    }

    const query = searchQuery.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(query) ||
        skill.description.toLowerCase().includes(query)
    );
  }, [skills, searchQuery]);

  const handleClearSearch = () => {
    setSearchQuery('');
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12"
        role="status"
      >
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading skills...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive" role="alert">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between w-full">
          <span>{error}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadSkills()}
            className="ml-4"
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div
      data-testid="skill-list-container"
      className={cn('space-y-6', className)}
    >
      {/* Search and Count */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchQuery && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearSearch}
              className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <div className="text-sm text-muted-foreground">
          {filteredSkills.length} skill{filteredSkills.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Empty State */}
      {skills.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">No skills found.</p>
          <Link href="/skills/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Skill
            </Button>
          </Link>
        </div>
      )}

      {/* No Search Results */}
      {skills.length > 0 && filteredSkills.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground">
            No skills match your search &quot;{searchQuery}&quot;
          </p>
        </div>
      )}

      {/* Skill Grid */}
      {filteredSkills.length > 0 && (
        <ul
          role="list"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filteredSkills.map((skill) => (
            <li key={skill.name}>
              <SkillCard skill={skill} onDelete={onDelete} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}