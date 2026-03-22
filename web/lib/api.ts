const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchSkills() {
  const response = await fetch(`${API_BASE}/api/skills/`);
  if (!response.ok) throw new Error("Failed to fetch skills");
  return response.json();
}

export async function fetchSkill(name: string) {
  const response = await fetch(`${API_BASE}/api/skills/${name}`);
  if (!response.ok) throw new Error("Failed to fetch skill");
  return response.json();
}

export async function runSkill(name: string, params: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/api/skills/${name}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params }),
  });
  if (!response.ok) throw new Error("Failed to run skill");
  return response.json();
}