export type LlmProvider = "openai" | "anthropic" | "google";

export interface ClientApiKeys {
  llm_provider?: LlmProvider | null;
  llm_api_key?: string | null;
  llm_model?: string | null;
  tavily_api_key?: string | null;
}

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

export interface HealthResponse {
  status: string;
  parsing?: {
    default?: string;
    openai_configured?: boolean;
    tavily_configured?: boolean;
  };
}
