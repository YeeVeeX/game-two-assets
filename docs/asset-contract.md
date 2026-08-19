# Asset contract v1

## Decision

`game-two-assets` is the source/studio system of record. `game-two` remains the runtime system of record. They share no runtime mechanism; approved exports cross the boundary only as reviewed copies in a later game-two change.

This avoids two failures at once: binary experimentation cannot perturb v17 build identity, and a release cannot drift silently because its source commit, target commit, and byte hashes are pinned.

## Compatibility baseline

The machine-readable pin is `manifests/runtime-baseline.json`, captured from game-two commit `219121d3ca2cfabfd39c3a1533b8227b52f68617`.

- view: 960x540
- grid: 32x32 square tiles
- creature export canvas: 32x32
- allowed creature pixel bounds: inclusive `[2,2,29,29]`
- creature anchor: `[16,30]`
- initial projection: top-down/top-down-with-tilt, with no cell overhang

Oblique height, overlap, Y-sorting, or sprites larger than one cell require an explicit future engine contract. Concepts may study those ideas; phase-0 exports may not assume them.

## Native PNG law

Every release PNG must:

- be non-interlaced 8-bit RGBA (PNG color type 6);
- use only alpha 0 or 255;
- use integer pixel coordinates with no antialiasing or resampling;
- declare every opaque `#rrggbb` color in its manifest;
- use no more than eight opaque colors during sprint 0;
- match the dimensions and SHA-256 recorded in its manifest;
- use nearest-neighbor at every preview scale.

Creature art may be narrower or shorter than 28 pixels; it does **not** need to fill a 28x28 block. Its occupied bounding box must remain inside the current footprint so art does not imply collision or layering the engine lacks.

## Visual-role law

The runtime colors in `manifests/runtime-baseline.json` are semantic signals, not a mandatory global indexed palette. A candidate may add controlled shades, but it must:

- keep each player role's baseline color dominant and recognizable;
- leave white readable for the possession ring;
- avoid reusing open-transition gold as an ordinary focal highlight;
- remain legible over the actual dark floors and light walls;
- preserve facing, attack tells, hurt response, and co-op ownership when evaluated.

Changing game colors to rescue an asset is prohibited during sprint 0.

## Naming

Use generic snake_case identifiers. Examples:

- `player_1_lane_a`
- `human_1_idle_down`
- `zone_1_floor_01`
- `station_1_idle`

Fiction names, place names, dialogue, and narrative labels are invalid in this repository.

## Source and provenance

A release must point to at least one file under `sources/` and record its exact SHA-256. Each export records one origin:

- `human` — native human-authored pixels;
- `procedural` — deterministic local generation with source retained;
- `ai_reconstruction` — native pixels reconstructed from a generated concept.

For `ai_reconstruction`, record provider, exact model, generation date, full prompt, seed or explicit `unavailable`, terms URL, terms retrieval date, concept path, and all material edits. Never label a general-model raster as a native sprite. Do not assign CC0 or any other license unless the rights holder actually granted it.

Reference images stay out of Git unless their license permits storage. Prefer URLs, citations, and written functional observations. Do not request imitation of a named living artist.

## Release manifest

Each release lives at `exports/<release_id>/release.json`. The gate requires:

- contract version;
- generic release ID;
- full 40-hex source commit;
- source paths and hashes;
- pinned game commit and runtime baseline path;
- pinned toolchain baseline plus deterministic exporter path and hash;
- per-export generic asset ID, kind, path, dimensions, anchor where relevant, palette, provenance, and hash.

`manifests/toolchain-baseline.json` pins the exact local Aseprite version output and executable SHA-256. A release is not reproducible merely because it names Aseprite; the exporter script and binary identity must both be auditable.

Run:

```bash
.venv/Scripts/python.exe tools/asset_gate.py
.venv/Scripts/python.exe tools/asset_gate.py --game-root ../game-two --aseprite C:/tools/aseprite/build/bin/aseprite.exe
```

The second command is intentionally manual: it detects when the live game checkout or Aseprite binary no longer matches a compatibility pin. Pin comparison reads game-two's **committed HEAD content** (LF-normalized): another agent's uncommitted worktree edits, and commit-identity drift with identical pinned content, are reported as warnings, never failures — both sessions run in parallel by design (owner directive 2026-08-18). Committed content drift in a pinned file is a hard failure requiring owner review. Baseline changes require review; never auto-update them.

## Visual gate

Technical validity is necessary but not sufficient. A selectable candidate needs:

1. a deterministic contact sheet over pixels sampled from real game captures;
2. native 1x presentation plus nearest-neighbor 2x/4x inspection views;
3. a vision critique against the sprint rubric;
4. separate verdicts for technical accuracy and visual presentation;
5. explicit winner/reject decision and unresolved risks.

Magnified views diagnose pixel placement; the native view decides runtime readability.

## Runtime-integration stop conditions

Do not integrate until all are true:

- game-two v17 fun verdict is closed;
- one sprint-0 visual lane wins rather than merely being least bad;
- asset gate passes from a clean checkout;
- provenance and rights are complete;
- visual critique passes at native scale;
- an integration design proves loading, draw order, and deterministic capture without changing simulation identity.

## Audio contract v1 (audio-v1 lane)

Audio is an additive asset kind (`kind: "audio"`). Every visual law above is
unchanged; audio entries never touch the PNG, palette, or bounds laws, and the
visual builder chain (`tools/export_assets.py`, `tools/make_release.py`) stays
byte-frozen — audio releases are built by their own pinned exporter
(`tools/ingest_audio.py`).

### Export format law

Every audio release WAV must:

- be WAV PCM16 (`pcm_s16le`) mono 48 000 Hz with the canonical 44-byte
  RIFF/WAVE/fmt/data header (Python `wave`-module layout, little-endian, no
  ancillary chunks, no timestamps);
- preserve the source frame count exactly (duration is never altered);
- satisfy `|dur_s · 48000 − frames| < 1e-6` in its manifest entry;
- for `mstem_*` ids, stay bar-exact: frames ≡ 0 (mod 96 000) — one bar at
  120 bpm 4/4 @ 48 kHz.

### Conversion law (twin-hash)

Exports are conversions of owner-rendered originals, never edits. The pinned
24→16 law is `s16 = clamp(round(s24 / 2^23 · 32767), −32768, 32767)`
(IEEE-754 float64, round-half-even; ties exist only at s24 = ±2^22 where
half-even and half-away coincide). The export's whole-file SHA-256 must equal
the upstream handoff manifest's PCM16 evaluation-twin sha256 for that asset:
the gate enforces `sha256 == conversion.evaluation_twin_sha256`, which makes
gain, trim, fade, resample, dither, or synthesis mechanically impossible. If a
conversion cannot reproduce its twin hash, the lane STOPS (bank sources + the
stop finding; ask upstream for the exact spec) — a divergent conversion never
ships.

### Loudness report law

This repository owns loudness measurement (upstream deliberately measures only
sample peak). Per export, the release records integrated LUFS (ITU-R
BS.1770-4: 48 kHz K-weighting, 400 ms blocks, 75% overlap, −70 LKFS absolute
+ −10 LU relative gating; null for files shorter than one 400 ms block) and
sample peak dBFS. Measurement is REPORT-ONLY: KB targets
(`music-production/game-audio-pipeline.md` §7) are conformance advisories;
out-of-band files are routed findings (owner mix decisions), never
gain-rescued. The meter must pass its pre-registered synthetic validation
vectors (reviews/audio-v1/rationale.md §4) before any measurement is trusted.
Sample peak ≠ true peak (dBTP); the KB peak column is advisory only.

### Audio release manifest

Audio releases use the standard header/source/target/toolchain law above
(exporter pin = the audio builder). Each `kind: "audio"` export additionally
requires: exact format object (wav / pcm_s16le / 48000 / 1 / 16); `frames` and
`dur_s` (consistency-checked); verbatim upstream `role` and `level_band`;
`loudness` (typed, report-only); `conversion` (law text +
`evaluation_twin_sha256` == export sha256 + `reproduces_evaluation_twin`);
`source` (path under `sources/` with matching sha256, `source_revision`,
`twin_pinned_commit`); provenance = the standard origin/author/created/rights
law plus non-empty `method` and an `upstream` block ({repository, 40-hex
handoff_commit, 32-hex handoff_manifest_md5}). The gate re-parses every WAV
header (PCM16 mono 48 kHz, frame count equals the manifest) and re-verifies
every hash.

### Naming and provenance

Mechanical snake_case ids from the upstream handoff manifest, unchanged — no
fiction names (standing lore ban). Origin for owner performances is `human`.
Generated or synthesized audio is not a valid audio export origin in v1.

### Audio gate

Technical validity is necessary but not sufficient. A banked audio release needs:

1. a deterministic per-file analysis sheet (waveform envelope at full scale,
   duration/frames, LUFS vs target, peak vs declared) rendered from the
   metrics artifact verbatim;
2. a metrics validator run (`tools/audio_metrics.py --check`) with failures
   grouped INTEGRITY (stops the lane) vs MEASUREMENT (banked evidence);
3. a vision critique of the sheet against the pre-registered rubric;
4. separate verdicts for technical accuracy and presentation;
5. determinism proof: conversion, release manifest, metrics, and sheet
   byte-identical across two builds.
