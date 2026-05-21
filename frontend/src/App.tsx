import { useEffect, useState } from "react";
import { apiConfigHint, apiUrl, getApiBase, isHostedMode, loadRuntimeConfig } from "./api";
import { downloadMidiFile } from "./download";
import { ApiKeysPanel, buildClientKeysPayload, type ApiKeysState } from "./components/ApiKeysPanel";
import { MeadowScene, PixelFlower, PixelHeart } from "./components/PixelDecor";
import type { BeatResponse } from "./types";

const EXAMPLES = [
  "Make me a beat for a great R&B song at 90 bpm",
  "Lo-fi study beat at 78 bpm, dusty and chill",
  "Energetic trap beat 140 BPM with heavy 808 bass and snare",
];

export default function App() {
  const [prompt, setPrompt] = useState(EXAMPLES[0]);
  const [openInLogic, setOpenInLogic] = useState(true);
  const [hostedMode, setHostedMode] = useState(false);
  const [apiKeys, setApiKeys] = useState<ApiKeysState>({
    llmProvider: "",
    llmApiKey: "",
    llmModel: "",
    tavilyApiKey: "",
    useLlm: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [result, setResult] = useState<BeatResponse | null>(null);

  useEffect(() => {
    loadRuntimeConfig().then(async () => {
      const hosted = isHostedMode();
      setHostedMode(hosted);
      if (hosted) setOpenInLogic(false);
      try {
        const res = await fetch(apiUrl("/api/health"));
        setApiOnline(res.ok);
      } catch {
        setApiOnline(false);
      }
    });
  }, []);

  async function generate(lucky = false) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(apiUrl("/api/generate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: lucky ? "" : prompt,
          bars: 8,
          open_in_logic: !hostedMode && openInLogic,
          lucky,
          use_web_search: !lucky && Boolean(apiKeys.tavilyApiKey.trim()),
          ...buildClientKeysPayload(apiKeys),
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const detail = body.detail;
        let message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d: { msg?: string }) => d.msg).join(", ")
              : `Request failed (${res.status})`;
        if (res.status === 404) {
          message = `${message}. ${apiConfigHint()}`;
        }
        throw new Error(message);
      }

      const data: BeatResponse = await res.json();
      if (data.original_prompt) {
        setPrompt(data.original_prompt);
      }
      setResult(data);

      if (hostedMode && data.midi_path) {
        try {
          await downloadMidiFile(data.midi_path, "beat_combined.mid");
        } catch (dlErr) {
          setError(
            dlErr instanceof Error
              ? `${dlErr.message} — use Download again below.`
              : "Auto-download failed — use Download again below.",
          );
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="game-wrap">
      <MeadowScene />

      <div className="page">
        <header className="hero pixel-box">
          <div className="hero-badge">
            <PixelFlower color="pink" />
            <span>LV.1 BEAT MAKER</span>
            <PixelFlower color="yellow" />
          </div>
          <h1>
            <span className="title-line">Bloom Beats</span>
            <span className="title-sub">Logic Quest</span>
          </h1>
          <p className="subtitle">
            {hostedMode
              ? "Describe your beat — we\u2019ll send a MIDI file you can open in Logic, GarageBand, FL Studio, or any DAW ✿"
              : "Tell the meadow fairy what vibe you want — she\u2019ll craft MIDI tracks for your Logic Pro adventure ✿"}
          </p>
        </header>

        <main className="panel pixel-box">
          <div className="panel-header">
            <PixelHeart />
            <label className="label" htmlFor="prompt">
              Quest log (your prompt)
            </label>
          </div>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            placeholder="e.g. cozy R&B at 120 BPM, synth + bass + snare for singing..."
          />

          <ApiKeysPanel keys={apiKeys} onChange={setApiKeys} />

          {apiOnline === false && (
            <div className="alert error pixel-inset api-offline" role="alert">
              <span className="alert-icon">!</span>
              <span>
                Cannot reach the beat API ({apiUrl("/api/health")}). {apiConfigHint()}
                {window.location.hostname === "bloombeats.ashlynbain.com" && (
                  <>
                    {" "}
                    Set <strong>config.json</strong> to{" "}
                    <strong>https://logic-beat-nlq.onrender.com</strong> if beats fail.
                  </>
                )}
              </span>
            </div>
          )}

          <p className="chip-label">✦ Quick spells</p>
          <div className="chips">
            {EXAMPLES.map((ex, i) => (
              <button key={ex} type="button" className="chip" onClick={() => setPrompt(ex)}>
                <span className="chip-num">{i + 1}</span>
                {ex.slice(0, 36)}…
              </button>
            ))}
          </div>

          <div className="controls">
            {!hostedMode && (
              <label className="checkbox field">
                <input
                  type="checkbox"
                  checked={openInLogic}
                  onChange={(e) => setOpenInLogic(e.target.checked)}
                />
                <span>Open in Logic Pro</span>
              </label>
            )}
            <div className="action-buttons">
              <button
                type="button"
                className="lucky"
                onClick={() => generate(true)}
                disabled={loading}
                title="Random genre, BPM, key, and mood"
              >
                {loading ? "…" : "🎲 I'm feeling lucky"}
              </button>
              <button
                type="button"
                className="primary"
                onClick={() => generate(false)}
                disabled={loading || !prompt.trim()}
              >
                {loading ? (
                  <>
                    <span className="blink">▶</span> Crafting…
                  </>
                ) : (
                  <>▶ Start quest</>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="alert error pixel-inset" role="alert">
              <span className="alert-icon">!</span>
              {error}
            </div>
          )}

          {result && (
            <section className="result pixel-inset">
              <h2>
                <PixelFlower color="purple" /> Quest complete!
              </h2>
              {result.adjustments?.length > 0 && (
                <div className="adjustments">
                  <p className="adjustments-title">✿ Fairy tweaked your quest:</p>
                  <ul>
                    {result.adjustments.map((note) => (
                      <li key={note}>{note}</li>
                    ))}
                  </ul>
                </div>
              )}
              {hostedMode ? (
                <p className="logic-msg download-msg">
                  Your ~{formatLoopLength(result.spec.bpm, result.spec.bars)} beat should download as{" "}
                  <strong>beat_combined.mid</strong> (all instruments). Open in any DAW at{" "}
                  <strong>{result.spec.bpm} BPM</strong>, loop bars 1–{result.spec.bars}, then add vocals.
                </p>
              ) : (
                <p className="logic-msg">{result.message}</p>
              )}

              <div className="spec-grid">
                <Spec label="Genre" value={result.spec.genre} icon="♫" />
                <Spec label="BPM" value={String(result.spec.bpm)} icon="♪" />
                <Spec label="Length" value={formatLoopLength(result.spec.bpm, result.spec.bars)} icon="⏱" />
                <Spec label="Key" value={`${result.spec.key} ${result.spec.scale}`} icon="🎹" />
                <Spec label="Mood" value={result.spec.mood} icon="☺" />
                <Spec label="Tracks" value={result.spec.instruments.join(", ")} icon="✿" wide />
              </div>

              <div className="downloads">
                <h3>{hostedMode ? "◆ Download again" : "◆ Your beat (all instruments)"}</h3>
                <button
                  type="button"
                  className="loot-link special loot-button"
                  onClick={() => downloadMidiFile(result.midi_path, "beat_combined.mid")}
                >
                  ★ Download beat_combined.mid
                </button>
              </div>

              <p className="hint">
                {hostedMode
                  ? dawHint(result.spec.bpm, result.spec.bars)
                  : logicHint(result.spec.genre, result.spec.bpm, result.spec.bars)}
              </p>
            </section>
          )}
        </main>

        <section className="about-panel pixel-box" aria-labelledby="about-heading">
          <h2 id="about-heading" className="about-title">
            <PixelHeart /> Why Bloom Beats?
          </h2>
          <p>
            I made this because I love music — writing songs, lyrics, and melodies is one of my
            favorite things. But I always got stuck on <strong>beats</strong>. Bloom Beats is my way
            to get unstuck: describe a vibe, get about <strong>two minutes</strong> of loopable MIDI
            (drums, bass, and keys together), and brainstorm vocals in Logic, GarageBand, or any DAW
            you like.
          </p>
          <p className="about-sign">— Ashlyn ✿</p>
        </section>

        <footer className="game-footer">
          <span>made with pixels & petals</span>
          <PixelFlower color="pink" />
        </footer>
      </div>
    </div>
  );
}

const GENRE_LOGIC_HINTS: Record<string, string> = {
  lofi: "Drums → mellow kit. Bass → Studio Bass (soft). Pads → Alchemy with lo-fi tape/delay.",
  rnb: "Drums → Drum Kit Designer (Neo Soul). Bass → Studio Bass. Keys → Vintage Electric Piano.",
  hiphop: "Drums → Drum Machine Designer. Bass → Studio Bass. Keys → Vintage Electric Piano.",
  house: "Drums → Drum Machine Designer. Bass → Studio Bass. Synth → Retro Synth.",
  pop: "Drums → Drum Kit Designer. Bass → Studio Bass. Keys → Vintage Electric Piano.",
};

function formatLoopLength(bpm: number, bars: number): string {
  const seconds = Math.round((bars * 240) / bpm);
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}:${s.toString().padStart(2, "0")}` : `${s}s`;
}

function dawHint(bpm: number, bars: number) {
  return (
    `In your DAW: import beat_combined.mid, set project tempo to ${bpm} BPM, ` +
    `enable loop/cycle over bars 1–${bars}, assign drum/bass/synth sounds, then record vocals.`
  );
}

function logicHint(genre: string, bpm: number, bars: number) {
  const stack = GENRE_LOGIC_HINTS[genre] ?? "Load Logic stock plugins per track name.";
  return (
    `Loop bars 1–${bars} at ${bpm} BPM (cycle mode: C). Match Logic tempo to ${bpm}. ` +
    `${stack} See LOGIC_SETUP.txt.`
  );
}

function Spec({
  label,
  value,
  icon,
  wide,
}: {
  label: string;
  value: string;
  icon: string;
  wide?: boolean;
}) {
  return (
    <div className={`spec pixel-inset ${wide ? "wide" : ""}`}>
      <span className="spec-icon">{icon}</span>
      <span className="spec-label">{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
