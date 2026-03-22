"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";

import { fetchSkills } from "@/lib/api";
import { SkillCard } from "@/components/skills/SkillCard";
import type { Skill } from "@/lib/store";

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSkills()
      .then(setSkills)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="p-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-8">
        <div className="text-center text-red-500">Error: {error}</div>
      </main>
    );
  }

  return (
    <main className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Skills</h1>
        <Link
          href="/skills/new"
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          <Plus size={16} />
          New Skill
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <SkillCard key={skill.name} skill={skill} />
        ))}
      </div>
      {skills.length === 0 && (
        <div className="text-center text-gray-500 mt-8">
          No skills found. Create your first skill!
        </div>
      )}
    </main>
  );
}