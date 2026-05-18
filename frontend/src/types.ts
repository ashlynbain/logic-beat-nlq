export interface BeatSpec {
  genre: string;
  bpm: number;
  key: string;
  scale: string;
  instruments: string[];
  bars: number;
  mood: string;
}

export interface BeatResponse {
  spec: BeatSpec;
  midi_path: string;
  track_paths: Record<string, string>;
  message: string;
  adjustments: string[];
  original_prompt: string;
}
