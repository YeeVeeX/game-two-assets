# audio-v1 ingest rationale — first audio lane (owner renders → gate-valid exports)

Pre-registered 2026-08-19, BEFORE any source copy, export, metrics file, or sheet
exists in this repository. The calibration series (v0–v9) is banked and untouched;
the v10 pure-turn lane stays parked. Zero audio-content edits anywhere in this lane:
no gain, no trim, no fade, no resample, no dither decision beyond the twin-hash-proven
conversion law below, no synthesis, no Bedrock.

## 1. What is being ingested

The seven owner renders of game-two-audio's `handoff/audio-v1/` package, committed at
game-two-audio `cfef3117b48ae35831ffb5834aec25885b0a7149` (short `cfef311`), manifest
md5 `4ec54531b6c9bda71acbe57252e01194`. Verified live at session start (step 0):

- manifest md5 matches; all seven WAVs present;
- every working-tree file's git blob hash equals the `cfef311` tree entry
  (`git hash-object` vs `git ls-tree -r cfef311`), i.e. the handoff dir is bit-exact
  the committed package;
- every original's sha256 matches its manifest entry (probe, 7/7);
- originals are WAV PCM (fmt tag 1) 24-bit mono 48 000 Hz with chunk layout
  `fmt (16) + bext (602) + junk (28) + data` (REAPER render layout), data frame
  counts equal the manifest `frames` exactly (7/7).

Provenance carried verbatim into the release (blocks-release data): in-house owner
performances — owner VST instruments driven by MIDI compositions authored in
game-two-audio `data/audio_listen/fixtures.json`, rendered through REAPER 7.79 on
2026-08-18. NO third-party audio, NO sample packs. Music stems are bar-exact at
120 bpm 4/4: one bar = 96 000 frames @ 48 kHz.

Division of law (both seats' mails, agreed): this repo owns loudness measurement
(LUFS per KB `music-production/game-audio-pipeline.md` §7 — their gate deliberately
measures only sample peak); mechanical ids stay; game-two consumes THIS repo's
exports only; the fixtures re-point is game-two-audio contract §4 territory and is
not touched from here. One-way boundary: read-only `git show`/`ls-tree` against
`../game-two` and `../game-two-audio`; the only bytes that enter this repo come from
`handoff/audio-v1/` (their evaluation stems in `data/audio_listen/stems/` are
quarantined and never read as content).

## 2. Twin-hash semantics, as read from their manifest (risk 1 — resolved)

Each manifest asset carries `evaluation_twin: {path, sha256, pinned_commit}` — the
sha256 of a complete PCM16 WAV **file** (whole-file hash, not data-chunk hash): the
`_what` header states "the sha-verified PCM16 evaluation twins live in
data/audio_listen/stems/".

**Conversion law (learned deterministically from the handoff originals alone, no stems
bytes read):** candidate deterministic 24→16 conversions were computed in memory from
the handoff originals and hashed against the manifest twin sha256s. Result, 7/7 exact:

```
s16 = round(s24 / 8388608.0 * 32767.0)        # IEEE-754 float64, banker's rounding
      clamped to [-32768, 32767]               # pure guard; never engages on real range
```

written as a canonical Python-`wave`-module PCM16 mono 48 kHz WAV: 44-byte header
(`RIFF` size / `WAVE` / `fmt ` 16-byte PCM tag-1 chunk / `data`), little-endian
samples, no ancillary chunks, no timestamps. Rejected candidates (0/7 each) all used
the divide-by-256 scale (truncation `s24 >> 8`, round-half-away of `s24/256`,
round-half-even of `s24/256`): the distinguishing fact is the **scale 32767/2^23**
(peak-preserving), not the rounding mode. Rounding-mode ambiguity is immaterial in
this domain: `s24·32767/2^23` hits a half-integer only for `s24 ≡ 2^22 (mod 2^23)`
(32767 is odd), i.e. exactly s24 = ±2^22 → ±16383.5, where round-half-even and
round-half-away coincide (±16384, verified live). Python's `round()` (half-even) is
pinned as the canonical statement. Determinism: `|s24|·32767 < 2^38 < 2^53` makes
the float64 expression mathematically exact (division by 2^23 is an exponent shift),
so the computed value IS `s24·32767/2^23` and `round()` is bit-identical on every
IEEE-754 platform. Because the export bytes must equal the twin hash, **any**
gain/trim/dither edit is mechanically impossible — the conversion is the only
transformation.

STOP rule (pre-registered): if at build time any export's sha256 differs from its
manifest twin sha256, the conversion lane STOPS (INTEGRITY red), only the sources
lane + the STOP finding are banked, and game-two-audio gets one bounded mail asking
for their exact conversion spec. No divergent conversion ships.

## 3. KB §7 loudness targets (pre-registered before measurement)

Source: KB `music-production/game-audio-pipeline.md` §7, table "LUFS Targets for Game
Audio" (queried via `hub kb query --domain music-production` this session):

| Content type | LUFS target (integrated) | Peak (dBTP) |
|---|---|---|
| Music (exploration) | −18 to −16 | −3 |
| Music (combat) | −16 to −14 | −1 |
| Ambient/drone | −24 to −20 | −6 |
| Sound effects | −14 to −10 | −1 |
| UI sounds | −16 to −12 | −3 |

Role mapping for the seven (from the handoff manifest's role/level_band vocabulary):

| asset_id | KB row | LUFS band | Notes |
|---|---|---|---|
| mstem_calm_6s | Music (exploration) | [−18, −16] | "calm-state music loop" |
| mstem_combat_6s | Music (combat) | [−16, −14] | "combat-state music loop" |
| msfx_drone_4s | Ambient/drone | [−24, −20] | "low ambient drone" |
| msfx_stinger_2s | Sound effects | [−14, −10] | "cuts above the music bed" |
| msfx_swarmpip_4s | **none** | n/a | stacked-texture role ("very quiet per pip", engine stacks ≤47 copies); §7 has no per-voice-of-N-stack row — **report-only, no invented target** |
| mui_confirm_200ms | UI sounds | [−16, −12] | integrated LUFS is **undefined** for a 0.2 s file (shorter than one 400 ms gating block) — reported null, conformance n/a |
| mui_ping_1200ms | UI sounds | [−16, −12] | |

Disclosed gaps: (a) the KB peak column is **dBTP (true peak)**; this lane measures
**sample peak** (stdlib-only, no oversampler in scope) — peak-vs-dBTP conformance is
therefore report-only/advisory, never a pass bar; (b) swarmpip has no KB row;
(c) sub-400 ms files have no integrated LUFS by BS.1770-4 construction.
LUFS conformance is MEASUREMENT, not INTEGRITY: out-of-band files are banked findings
routed to game-two-audio/owner (mix decisions), never gain-rescued — the twin-hash
law makes gain changes impossible anyway.

## 4. LUFS meter (risk 3) — spec + pre-registered validation vectors

Pure-Python (stdlib) ITU-R BS.1770-4 integrated loudness, REPORT-ONLY (no gain is
ever applied):

- K-weighting at 48 kHz, the published BS.1770-4 biquad coefficients (all files are
  native 48 kHz; no resampling anywhere):
  - stage 1 (shelf): b = (1.53512485958697, −2.69169618940638, 1.19839281085285),
    a = (1.0, −1.69065929318241, 0.73248077421585)
  - stage 2 (RLB high-pass): b = (1.0, −2.0, 1.0),
    a = (1.0, −1.99004745483398, 0.99007225036621)
- gating blocks: 400 ms (19 200 samples), 75 % overlap (step 100 ms = 4 800 samples);
  block loudness = −0.691 + 10·log10(mean square of the K-weighted block);
- absolute gate −70 LKFS, then relative gate at (power-mean of surviving blocks) − 10 LU;
  integrated = −0.691 + 10·log10(power mean of blocks surviving both gates);
- mono: one channel, weight G = 1.0 (BS.1770 channel sum; no dual-mono +3 dB
  convention — pinned and documented);
- fewer than one complete block (frames < 19 200) ⇒ integrated LUFS = null;
- sample peak dBFS = 20·log10(max|s| / 2^(bits−1)), measured on both the 24-bit
  source and the 16-bit export.

**Validation vectors** (INTEGRITY — meter must pass them inside `--check` and in the
test suite before any real measurement is trusted). Expectations derived analytically
from the pinned coefficients by direct transfer-function evaluation on the unit
circle — `ms = (a²/2)·|H1(e^jω)|²·|H2(e^jω)|²`, `LUFS = −0.691 + 10·log10(ms)` — an
independent path from the meter's time-domain filtering (derivation script output,
this session: K-gain at 997 Hz = +0.691014 dB, i.e. the standard's −0.691 offset
cancels at ~1 kHz as published):

| Vector | Signal (48 kHz mono PCM16) | Expected | Tolerance |
|---|---|---|---|
| V1 | 997 Hz sine, amplitude 0.5 FS, 5.0 s | −9.0309 LUFS | ±0.05 LU |
| V2 | 997 Hz sine, amplitude 0.25 FS, 5.0 s | −15.0515 LUFS; delta vs V1 = −6.0206 | ±0.05 LU; delta ±0.02 LU |
| V3 | 3.0 s of V3-sine (997 Hz, a=0.1) + 3.0 s digital silence | within 0.30 LU of the same sine alone (gating drops silent blocks; an ungated meter reads ≈3 LU low) | 0.30 LU |
| V4a | 4.0 s digital silence | null (no block above the −70 absolute gate) | exact |
| V4b | DC 0.5 FS, 4.0 s | < −25 LUFS (stage-2 high-pass rejects DC; only the onset **step transient** carries energy — a broken high-pass reads ≈−6.7, the naive un-weighted level) | bound |
| V5 | one +32767 sample in silence | sample peak −0.00027 dBFS (= 20·log10(32767/32768)) | ±0.001 dB |
| V6 | 997 Hz sine a=0.5 scaled to int16 16384 max | sample peak −6.0206 dBFS | ±0.01 dB |

Tolerances absorb onset transients of the IIR filters and PCM16 quantization of the
synthetic signals; the vectors sit far from every tolerance edge relative to the bug
classes they catch (sign/coefficient errors ≥ several dB; missing gate ≈ 3 LU; block
mis-sizing ≥ 0.1 LU). Correction during meter validation (before any release
artifact was measured): V4 was originally registered as "DC → null"; the live meter
falsified that expectation — a DC **step** at t=0 is broadband, so its onset
transient passes the high-pass and gates in at ≈32.3 LUFS below full-scale-sine
level. The physics-correct pair V4a/V4b above replaced it; the meter itself was
never wrong (measured DC value −32.30 LUFS, silence null — both inside the
corrected bars).

**Sample-peak cross-check** (INTEGRITY — a free correctness check on our reader
against their independently measured gate): per file, measured 24-bit source sample
peak within **±0.05 dB** of the handoff manifest's declared `peak_dbfs`; the 16-bit
export peak is reported alongside (expected within ~0.001 dB of the source peak:
the conversion rescales by 32767/32768 ≈ −0.000265 dB plus ±0.5 LSB rounding).

## 5. Release schema extension (design call of this seat)

`exports/audio-v1/release.json` keeps the existing header/source/target/toolchain law
byte-for-byte (contract_version 1, release_id, THIS repo's 40-hex source commit with
sources committed clean, pinned game commit + runtime baseline path, toolchain
baseline + exporter pin). The exporter pin names **`tools/ingest_audio.py`** — the new
audio builder; `tools/export_assets.py` and `tools/make_release.py` stay byte-frozen
(SHA-pinned/registry-frozen by the banked visual releases; audio extends AROUND them).

Per-export audio entry (`kind: "audio"` — the additive discriminator):

```json
{
  "asset_id": "<handoff mechanical id, snake_case, unchanged>",
  "kind": "audio",
  "path": "exports/audio-v1/<asset_id>.wav",
  "sha256": "<export file sha256>",
  "format": {"container": "wav", "codec": "pcm_s16le",
             "sample_rate_hz": 48000, "channels": 1, "bit_depth": 16},
  "frames": <exact frame count>,
  "dur_s": <manifest duration>,
  "role": "<verbatim from handoff manifest>",
  "level_band": "<verbatim from handoff manifest>",
  "loudness": {"lufs_integrated": <float|null>, "sample_peak_dbfs": <float>,
               "kb_target_lufs": [lo, hi] | null,
               "kb_target_ref": "<KB row citation>" | null},
  "conversion": {"law": "<the §2 law, spelled out>",
                 "evaluation_twin_sha256": "<from handoff manifest>",
                 "reproduces_evaluation_twin": true},
  "source": {"path": "sources/audio-v1/<asset_id>.wav",
             "sha256": "<original sha256>",
             "source_revision": "<verbatim>", "twin_pinned_commit": "<verbatim>"},
  "provenance": {
    "origin": "human",
    "author": "project owner (in-house performance; owner VST instruments)",
    "created": "2026-08-18",
    "rights": "private-project",
    "method": "<owner performance, MIDI from fixtures.json, REAPER 7.79 render,
               conversion-only ingest per the twin-hash law>",
    "upstream": {"repository": "game-two-audio",
                 "handoff_path": "handoff/audio-v1",
                 "handoff_commit": "cfef3117b48ae35831ffb5834aec25885b0a7149",
                 "handoff_manifest_md5": "4ec54531b6c9bda71acbe57252e01194"}
  }
}
```

Release-level `source.files` = the seven originals + `sources/audio-v1/handoff-manifest.json`
(the manifest copy; the upstream file is CRLF, so it is routed `-text` in
`.gitattributes` — byte-exact under the repo's default `eol=lf` normalization, which
would otherwise rewrite the blob and break the md5 pin on fresh checkout).

Gate law for `kind: "audio"` (additive branch in `tools/asset_gate.py`; every visual
code path untouched): asset_id snake_case + unique; path
`exports/<release_id>/<asset_id>.wav` + unique; sha256 matches the file; format object
exactly as above; WAV header re-parsed and asserted (PCM tag 1, 16-bit, mono,
48 000 Hz, data frames == `frames`); `|dur_s·48000 − frames| < 1e−6`; `mstem_*` frames
≡ 0 mod 96 000 (bar-exact law); loudness fields present and typed
(`sample_peak_dbfs` number ≤ 0, `lufs_integrated` number or null);
`conversion.evaluation_twin_sha256` == entry sha256 (the gate re-proves the
conversion law forever) and `reproduces_evaluation_twin` == true; source path under
`sources/` exists with matching sha256; provenance = existing law (origin/author/
created/rights) + non-empty method + upstream {repository, 40-hex handoff_commit,
32-hex handoff_manifest_md5}; role and level_band non-empty.

## 6. Contract extension plan (docs/asset-contract.md)

One additive section, "Audio contract v1 (audio-v1 lane)", after the existing visual
sections, leaving every visual law untouched: export format law (WAV PCM16 mono
48 kHz canonical header), the twin-hash conversion law + STOP rule, frame-count/
duration/bar-exact laws, loudness report law (BS.1770-4 integrated LUFS + sample
peak, report-only, KB §7 targets advisory with the dBTP gap disclosed), provenance
fields (upstream block), mechanical-id naming (no fiction names), and the audio gate
list above. The PNG law, palette law, visual-role law, and visual gate sections are
not modified in any way.

## 7. Toolchain (three new tools, stdlib-only, deterministic)

1. `tools/ingest_audio.py` — staged builder, the release's pinned exporter:
   `--stage sources` verifies the handoff (manifest md5 pin, per-file sha256) and
   copies originals + manifest into `sources/audio-v1/`; `--stage release` requires
   sources/ tools/ manifests/ committed clean (same honesty law as make_release),
   converts per §2, verifies every twin hash (STOP on mismatch), writes
   `exports/audio-v1/*.wav` + `release.json`. No timestamps anywhere in output.
2. `tools/audio_metrics.py` — strict RIFF/WAV reader (chunk walker: padding, single
   fmt/data, PCM tags only) + the §4 meter + `--check` validator writing
   `reviews/audio-v1/audio-metrics.json`; failures grouped INTEGRITY vs MEASUREMENT
   (v9 pattern): INTEGRITY red stops the sprint, MEASUREMENT red is banked evidence.
3. `tools/make_audio_sheet.py` — deterministic per-file analysis sheet
   (`reviews/audio-v1/audio-sheet.png`) via `png_writer.Rgba8Canvas` + the repo's
   3×5 glyph convention: per file, min/max waveform envelope drawn from the decoded
   export samples, duration/frames, role band, LUFS vs KB target, peak vs declared —
   every number rendered from `audio-metrics.json` verbatim.

`tests/test_audio_tools.py` mirrors the repo pattern: synthetic WAV fixtures
(pass AND fail directions), conversion-law unit vectors, meter vectors V1–V6, WAV
walker edge cases, gate-extension suites (valid audio release passes; corrupted
hash/format/frames/provenance/bar-exactness caught; visual releases unaffected),
skip-guarded real-artifact regressions (committed exports/twin hashes/metrics/sheet
regenerate byte-identical). `tools/` coverage ≥ 80 under `bin/full_gate.py`.

## 8. Pass bars (fixed now; grouped INTEGRITY vs MEASUREMENT)

INTEGRITY (any red stops the sprint):

1. handoff manifest md5 == `4ec54531b6c9bda71acbe57252e01194`; handoff dir bit-exact
   vs game-two-audio `cfef3117…` (verified at step 0);
2. all seven `sources/audio-v1/*.wav` byte-identical to the handoff originals
   (sha256 == manifest originals), manifest copy byte-identical to the handoff manifest;
3. **conversion law:** every export's bytes reproduce the manifest's evaluation-twin
   sha256 exactly (whole-file semantic, §2); frame count export == source == manifest,
   per file;
4. consistency: per file, dur_s ↔ frames ↔ 48 000 Hz (|dur_s·48000 − frames| < 1e−6);
   `mstem_*` frames ≡ 0 mod 96 000; sample rate 48 000 and channels == 1 asserted
   from the WAV headers of BOTH source and export; export bit depth 16, source 24;
5. meter validation: vectors V1–V6 inside their pre-registered tolerances;
6. sample-peak cross-check: source sample peak within ±0.05 dB of the declared
   manifest `peak_dbfs`, per file;
7. gate: `asset_gate.py` exit 0 over ALL releases (7 visual + audio-v1), both
   invocations (plain and `--game-root ../game-two --aseprite …`); the 26 visual
   export pins byte-verified untouched; `tools/export_assets.py` and
   `tools/make_release.py` bytes untouched;
8. determinism: conversion + release.json + metrics JSON + sheet byte-identical
   across two in-process builds AND a CLI re-run `cmp`-clean against committed bytes;
9. full suite green including all existing visual regression suites (v0–v9 sheets
   regenerate byte-identical); `tools/` coverage ≥ 80;
10. naming: every release asset id == its handoff mechanical id, snake_case, no
    fiction names, no new ids beyond the seven.

MEASUREMENT (red = banked evidence + routed finding, never a rescue):

11. integrated LUFS inside the §3 KB band for the five mapped files (swarmpip:
    no target, report-only; confirm_200ms: null, n/a);
12. sample peak vs the KB dBTP column — advisory only (sample peak ≠ true peak,
    disclosed §3).

## 9. Review rubric (pre-registered, critique-blocking)

This repo cannot listen; the owner already performed and approved these sounds. The
review artifact's job is INSPECTION, not taste. Accuracy and presentation are scored
separately; a failed critique blocks banking.

Accuracy bars:
- A1: every number on the sheet (duration, frames, LUFS, peak, declared peak, target
  band, delta flags) equals `audio-metrics.json` to the printed digit;
- A2: every waveform envelope is drawn from the decoded export samples of the named
  file (min/max per column, no smoothing, no normalization — amplitude is rendered
  against full scale so the quiet files LOOK quiet);
- A3: any LUFS-vs-target deviation or peak disagreement is named per file with its
  number, framed as a routing finding (owner mix decision), never softened or "fixed".

Presentation bars:
- P1: legible mechanical-id labels (3×5 glyph font, native rendering, no
  antialiasing), deterministic fixed layout;
- P2: per-row structure scannable (id / envelope / numbers aligned in columns);
  in-band vs out-of-band flags visually distinct but not alarmist;
- P3: sheet renders correctly at native scale (no clipped text, no overlapping rows).

Vision critique of the final sheet bytes (sha256 recorded in the verdict) runs on the
session model (Fable-5-class, verified `PI_MODEL=us.anthropic.claude-fable-5` at
session start) against A1–A3/P1–P3. Council (cross-vendor, Kimi K2.5 default, ≤ 8k
tokens total, one consolidated adversarial pass) reviews the contract extension +
conversion/LUFS law + measured results BEFORE the verdict is banked; council output
goes to a file, read as UTF-8, every numeric claim recomputed before adoption.

## 10. Bounded change set + stop conditions

Commits: (0) baseline re-pin alone [landed: `e6c2d05`]; (1) this rationale +
contract § + gate extension + three tools + tests + `.gitattributes` additive LFS
rules (`/sources/**/*.wav`, `/exports/**/*.wav`); (2a) `sources/audio-v1/` (7
originals + manifest copy) — sources must be committed before the release builder
runs (source-commit honesty law); (2b) `exports/audio-v1/` (7 WAVs + release.json) +
`reviews/audio-v1/audio-metrics.json` + `audio-sheet.png` + `verdict.md` after the
verdict. Push after banking (pre-push = LFS preserve + full gauntlet). Receipts after
push: mail to `~/.pi/agent/mail/game-two/` with absolute export paths + sha256s
(consume-on-hash), update `drafts/audio-handoff-v1-receipt.md` to BANKED.

Stop: one banked audio release + review + receipts; no second lane. If the twin-hash
law fails at build time: bank sources + STOP finding, mail game-two-audio (one
bounded ask), end the sprint.
