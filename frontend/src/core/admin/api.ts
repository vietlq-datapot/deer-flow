import { getBackendBaseURL } from "@/core/config";

export interface AdminConfigStatus {
  deepseek_api_key_set: boolean;
  deepseek_api_key_hint: string;
  telegram_bot_token_set: boolean;
  telegram_bot_token_hint: string;
  tavily_api_key_set: boolean;
  tavily_api_key_hint: string;
}

export interface AdminConfigUpdate {
  deepseek_api_key?: string;
  telegram_bot_token?: string;
  tavily_api_key?: string;
}

export async function fetchAdminConfig(): Promise<AdminConfigStatus> {
  const res = await fetch(`${getBackendBaseURL()}/api/admin/config`);
  if (!res.ok) throw new Error(`Failed to load admin config: ${res.statusText}`);
  return res.json() as Promise<AdminConfigStatus>;
}

export async function saveAdminConfig(
  update: AdminConfigUpdate,
): Promise<{ success: boolean; updated: string[] }> {
  const res = await fetch(`${getBackendBaseURL()}/api/admin/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(err.detail ?? `Failed to save config: ${res.statusText}`);
  }
  return res.json() as Promise<{ success: boolean; updated: string[] }>;
}
