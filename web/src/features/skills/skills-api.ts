import { apiFetch } from "@/lib/api-client";
import type { Skill, SkillRunResponse } from "@/types/skills";

export async function getSkills(): Promise<Skill[]> {
  return apiFetch<Skill[]>("/api/v1/skills/");
}

export async function getSkill(name: string): Promise<Skill> {
  return apiFetch<Skill>(`/api/v1/skills/${encodeURIComponent(name)}`);
}

export async function executeSkill(
  name: string,
  params: Record<string, unknown>,
): Promise<SkillRunResponse> {
  return apiFetch<SkillRunResponse>(
    `/api/v1/skills/${encodeURIComponent(name)}/run`,
    {
      method: "POST",
      body: JSON.stringify({ params }),
    },
  );
}
