import Link from "next/link";
import { Edit, Play, Trash2 } from "lucide-react";

import type { Skill } from "@/lib/store";

interface SkillCardProps {
  skill: Skill;
}

export function SkillCard({ skill }: SkillCardProps) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold">{skill.name}</h3>
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
          {skill.version}
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-4">{skill.description}</p>
      <div className="flex gap-2">
        <Link
          href={`/skills/${skill.name}`}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
        >
          <Play size={14} />
          Run
        </Link>
        <Link
          href={`/skills/${skill.name}/edit`}
          className="flex items-center justify-center p-2 border rounded hover:bg-gray-50"
        >
          <Edit size={14} />
        </Link>
        <button className="flex items-center justify-center p-2 border border-red-200 text-red-500 rounded hover:bg-red-50">
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}