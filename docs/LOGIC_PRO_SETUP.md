# Logic Pro setup guide

Generated beats include a per-session **`LOGIC_SETUP.txt`** under `output/<session_id>/`. This doc is the static reference.

---

## 1. Tempo

- Set the **project tempo** to the BPM shown in the app (e.g. **90**).
- If Logic asks when importing MIDI: choose **Use MIDI file tempo** / do not adapt to a different project tempo.

---

## 2. Loop for singing

1. Drag the **cycle** strip over **bars 1–N** (N = bars you chose, usually 8).
2. Press **C** to enable **cycle mode**.
3. Press play — all tracks should stay locked together.

---

## 3. Assign instruments (required for good sound)

MIDI does not include Logic’s sounds. Select each track → **Inspector (i)** → instrument slot:

| Track name in MIDI | Logic plugin | Suggested preset |
|--------------------|--------------|----------------|
| **Drums** | Drum Kit Designer (R&B) or Drum Machine Designer (trap/house) | Neo Soul / Modern R&B kit |
| **Bass** or **808 Bass** | Studio Bass | Default finger / 808-style |
| **Keys** | Vintage Electric Piano | Mercury Rhodes, Smooth Jazz |
| **Synth** (house) | Retro Synth | Short stab / pluck |

---

## 4. Vocals

- **Track → New Audio Track**
- Record vocals over the loop.

---

## 5. Troubleshooting

| Problem | Fix |
|---------|-----|
| Drums/bass/keys feel out of sync | Match project tempo to MIDI; re-import with file tempo |
| Sounds like cheap piano | Plugins not assigned — see table above |
| Loop clicks | Trim regions to bar 1–N; enable cycle, not one-shot |
| Wrong speed | Explicitly set BPM in transport |

---

## Why we don’t auto-load plugins

Apple does not ship a stable public API for loading Logic instruments from external apps. See [REFERENCES.md](./REFERENCES.md) for MCP projects that may automate this in the future.
