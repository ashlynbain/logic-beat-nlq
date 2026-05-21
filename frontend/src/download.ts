import { apiUrl } from "./api";

/** Fetch MIDI as a blob so cross-origin hosted sites still get a real file download. */
export async function downloadMidiFile(
  sessionPath: string,
  filename = "beat_combined.mid",
): Promise<void> {
  const res = await fetch(apiUrl(`/api/download/${sessionPath}`));
  if (!res.ok) {
    throw new Error(`Download failed (${res.status})`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
