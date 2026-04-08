'use client';

import Link from 'next/link';
import { Plus } from 'lucide-react';

import { AppShell } from '@/components/apple';
import { SkillList } from '@/components/skills';

export default function SkillsPage() {
  return (
    <AppShell title="Skill Library" statusBadge="24 active">
      <div className="py-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Skills</h2>
          <Link
            href="/skills/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            <Plus size={16} />
            New Skill
          </Link>
        </div>
        <SkillList />
      </div>
    </AppShell>
  );
}