const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchSkills() {
  const response = await fetch(`${API_BASE}/api/skills/`);
  if (!response.ok) throw new Error("Failed to fetch skills");
  return response.json();
}