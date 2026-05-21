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

const PRODUCTION_SITE = "bloombeats.ashlynbain.com";
const PRODUCTION_API = "https://api.bloombeats.ashlynbain.com";

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

  if (
    !apiBase &&
    typeof window !== "undefined" &&
    window.location.hostname === PRODUCTION_SITE
  ) {
    apiBase = PRODUCTION_API;
  }
}

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${apiBase}${p}`;
}

export function apiConfigHint(): string {
  if (apiBase) return `API: ${apiBase}`;
  if (import.meta.env.VITE_AUTO_DOWNLOAD === "true") {
    return "Set apiBaseUrl in config.json to your Python API URL (static hosting has no /api routes).";
  }
  return "Start the backend on port 8000 (uvicorn app.main:app --reload --port 8000).";
}
