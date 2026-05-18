import { useState } from "react";
import { MeadowScene, PixelFlower, PixelHeart } from "./components/PixelDecor";
import type { BeatResponse } from "./types";

const EXAMPLES = [
  "Make me a beat for a great R&B song at 90 bpm",
  "Lo-fi study beat at 78 bpm, dusty and chill",
  "Energetic trap beat 140 BPM with heavy 808 bass and snare",
];

export default function App() {
  const [prompt, setPrompt] = useState(EXAMPLES[0]);
  const [bars, setBars] = useState(8);
  const [openInLogic, setOpenInLogic] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BeatResponse | null>(null);

  async function generate(lucky = false) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: lucky ? "" : prompt,
          bars,
          open_in_logic: openInLogic,
          lucky,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const detail = body.detail;
        const message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d: { msg?: string }) => d.msg).join(", ")
              : `Request failed (${res.status})`;
        throw new Error(message);
      }

      const data: BeatResponse = await res.json();
      if (data.original_prompt) {
        setPrompt(data.original_prompt);
      }
      if (data.spec.bars) {
        setBars(data.spec.bars);
      }
      setResult(data);
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
            Tell the meadow fairy what vibe you want — she&apos;ll craft MIDI tracks for your
            Logic Pro adventure ✿
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
            <label className="field">
              <span>Bars</span>
              <select value={bars} onChange={(e) => setBars(Number(e.target.value))}>
                {[4, 8, 16].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <label className="checkbox field">
              <input
                type="checkbox"
                checked={openInLogic}
                onChange={(e) => setOpenInLogic(e.target.checked)}
              />
              <span>Open in Logic Pro</span>
            </label>
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
              <p className="logic-msg">{result.message}</p>

              <div className="spec-grid">
                <Spec label="Genre" value={result.spec.genre} icon="♫" />
                <Spec label="BPM" value={String(result.spec.bpm)} icon="♪" />
                <Spec label="Key" value={`${result.spec.key} ${result.spec.scale}`} icon="🎹" />
                <Spec label="Mood" value={result.spec.mood} icon="☺" />
                <Spec label="Loot" value={result.spec.instruments.join(", ")} icon="✿" wide />
              </div>

              <div className="downloads">
                <h3>◆ Treasure (MIDI)</h3>
                <ul>
                  {Object.entries(result.track_paths).map(([name, path]) => (
                    <li key={name}>
                      <a href={`/api/download/${path}`} download className="loot-link">
                        {name}.mid
                      </a>
                    </li>
                  ))}
                  <li>
                    <a href={`/api/download/${result.midi_path}`} download className="loot-link special">
                      ★ beat_combined.mid
                    </a>
                  </li>
                </ul>
              </div>

              <p className="hint">{logicHint(result.spec.genre, result.spec.bpm, result.spec.bars)}</p>
            </section>
          )}
        </main>

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
