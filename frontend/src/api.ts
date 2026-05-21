/** API base URL: build env, then config.json (editable on static hosting). */

let apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export function getApiBase(): string {
  return apiBase;
}

export function isRemoteApi(): boolean {
  if (!apiBase) return false;
  try {
    const u = new URL(apiBase, window.location.origin);
    return u.origin !== window.location.origin;
  } catch {
    return true;
  }
}

/** Static public_html builds: auto-download MIDI instead of opening Logic. */
export function isHostedMode(): boolean {
  if (import.meta.env.VITE_AUTO_DOWNLOAD === "true") return true;
  return isRemoteApi();
}

export async function loadRuntimeConfig(): Promise<void> {
  try {
    const base = import.meta.env.BASE_URL || "/";
    const res = await fetch(`${base}config.json`, { cache: "no-store" });
    if (!res.ok) return;
    const data = (await res.json()) as { apiBaseUrl?: string };
    if (data.apiBaseUrl?.trim()) {
      apiBase = data.apiBaseUrl.trim().replace(/\/$/, "");
    }
  } catch {
    /* same-origin / local dev */
  }
}

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${apiBase}${p}`;
}
