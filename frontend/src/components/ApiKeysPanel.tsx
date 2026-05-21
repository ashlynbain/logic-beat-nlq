import type { LlmProvider } from "../types";
import { PixelSelect } from "./PixelSelect";

const PROVIDERS: { id: LlmProvider; label: string; placeholder: string; defaultModel: string }[] = [
  { id: "openai", label: "OpenAI (GPT)", placeholder: "sk-…", defaultModel: "gpt-4o-mini" },
  {
    id: "anthropic",
    label: "Anthropic (Claude)",
    placeholder: "sk-ant-…",
    defaultModel: "claude-3-5-haiku-20241022",
  },
  {
    id: "google",
    label: "Google (Gemini)",
    placeholder: "AIza…",
    defaultModel: "gemini-1.5-flash",
  },
];

export interface ApiKeysState {
  llmProvider: LlmProvider | "";
  llmApiKey: string;
  llmModel: string;
  tavilyApiKey: string;
  useLlm: boolean;
}

interface Props {
  keys: ApiKeysState;
  onChange: (keys: ApiKeysState) => void;
}

export function ApiKeysPanel({ keys, onChange }: Props) {
  const providerMeta = PROVIDERS.find((p) => p.id === keys.llmProvider);

  function patch(partial: Partial<ApiKeysState>) {
    onChange({ ...keys, ...partial });
  }

  function clearKeys() {
    onChange({
      llmProvider: "",
      llmApiKey: "",
      llmModel: "",
      tavilyApiKey: "",
      useLlm: false,
    });
  }

  return (
    <section className="keys-panel pixel-inset" aria-labelledby="keys-heading">
      <h2 id="keys-heading" className="keys-title">
        ✦ Quest settings (API keys)
      </h2>
      <p className="keys-note">
        Keys stay in your browser for this session only. They are sent once per beat request and are{" "}
        <strong>never saved</strong> on the server.
      </p>

      <label className="checkbox field keys-toggle">
        <input
          type="checkbox"
          checked={keys.useLlm}
          onChange={(e) => patch({ useLlm: e.target.checked })}
        />
        <span>Use an LLM to interpret my prompt</span>
      </label>

      {keys.useLlm && (
        <div className="keys-grid">
          <label className="field">
            <span>Provider</span>
            <PixelSelect
              compact
              value={keys.llmProvider}
              placeholder="Choose…"
              options={[
                { value: "", label: "Choose…" },
                ...PROVIDERS.map((p) => ({ value: p.id, label: p.label })),
              ]}
              onChange={(v) =>
                patch({
                  llmProvider: v as LlmProvider | "",
                  llmModel: "",
                })
              }
            />
          </label>

          <label className="field keys-wide">
            <span>API key</span>
            <input
              type="password"
              autoComplete="off"
              spellCheck={false}
              value={keys.llmApiKey}
              onChange={(e) => patch({ llmApiKey: e.target.value })}
              placeholder={providerMeta?.placeholder ?? "Paste key…"}
            />
          </label>

          <label className="field keys-wide">
            <span>Model (optional)</span>
            <input
              type="text"
              autoComplete="off"
              value={keys.llmModel}
              onChange={(e) => patch({ llmModel: e.target.value })}
              placeholder={providerMeta?.defaultModel ?? "Default model"}
            />
          </label>
        </div>
      )}

      <label className="field keys-wide tavily-field">
        <span>Tavily API key (optional)</span>
        <input
          type="password"
          autoComplete="off"
          spellCheck={false}
          value={keys.tavilyApiKey}
          onChange={(e) => patch({ tavilyApiKey: e.target.value })}
          placeholder="tvly-…"
        />
      </label>

      <button type="button" className="keys-clear" onClick={clearKeys}>
        Clear all keys from memory
      </button>
    </section>
  );
}

export function buildClientKeysPayload(keys: ApiKeysState): {
  client_keys?: {
    llm_provider: LlmProvider;
    llm_api_key: string;
    llm_model?: string;
    tavily_api_key?: string;
  };
} {
  const body: {
    client_keys?: {
      llm_provider: LlmProvider;
      llm_api_key: string;
      llm_model?: string;
      tavily_api_key?: string;
    };
  } = {};

  const ck: NonNullable<typeof body.client_keys> = {} as NonNullable<typeof body.client_keys>;
  let hasAny = false;

  if (keys.useLlm && keys.llmProvider && keys.llmApiKey.trim()) {
    ck.llm_provider = keys.llmProvider;
    ck.llm_api_key = keys.llmApiKey.trim();
    if (keys.llmModel.trim()) ck.llm_model = keys.llmModel.trim();
    hasAny = true;
  }

  if (keys.tavilyApiKey.trim()) {
    ck.tavily_api_key = keys.tavilyApiKey.trim();
    hasAny = true;
  }

  if (hasAny) body.client_keys = ck;
  return body;
}
