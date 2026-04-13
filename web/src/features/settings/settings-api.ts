import { apiFetch } from "@/lib/api-client";
import type { AppSettings, SettingsUpdateResponse } from "@/types/api";

export async function getSettings(): Promise<AppSettings> {
  return apiFetch<AppSettings>("/api/v1/settings/");
}

export async function updateSettings(
  settings: Partial<AppSettings>,
): Promise<SettingsUpdateResponse> {
  return apiFetch<SettingsUpdateResponse>("/api/v1/settings/", {
    method: "PUT",
    body: JSON.stringify(settings),
  });
}

export async function getHealth(): Promise<{
  status: string;
  version: string;
  vault_connected: boolean;
}> {
  return apiFetch<{
    status: string;
    version: string;
    vault_connected: boolean;
  }>("/health");
}
