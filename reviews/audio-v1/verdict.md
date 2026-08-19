# audio-v1 ingest verdict — BANKED

Date: 2026-08-19. Session model: `us.anthropic.claude-fable-5` (verified from env, not
self-report). Pass bars and rubric were pre-registered in `reviews/audio-v1/rationale.md`
BEFORE any artifact existed; this verdict scores against them line by line.
Artifacts under verdict: `exports/audio-v1/` (7 WAVs + release.json),
`reviews/audio-v1/audio-metrics.json`, `reviews/audio-v1/audio-sheet.png`
(sha256 `c86c58063623d2ba05dfc23a8d31d35587d90b094b926f8a1fa4a96d9b4bc5f7`).

## Headline

**INTEGRITY 10/10 GREEN — release banked.** The conversion law reproduced all seven
upstream PCM16 evaluation-twin hashes bit-exact from the handoff originals alone; the
gate validates the audio release alongside all seven visual releases; determinism
proven end-to-end. **MEASUREMENT: 4 of 5 KB-mapped files sit BELOW their KB §7 LUFS
bands** — banked as routed findings (owner/game-two-audio mix territory), exactly as
the pre-registered law requires: report-only, never gain-rescued (the twin-hash law
makes gain edits mechanically impossible).

## Machine bars (rationale §8), line by line

| # | Bar | Result |
|---|-----|--------|
| 1 | handoff md5 `4ec54531…` + dir bit-exact vs `cfef3117…` | PASS (md5 match; 8/8 working-tree blobs == `cfef311` tree; step 0) |
| 2 | sources byte-identical to handoff (sha256 7/7 + manifest copy) | PASS (LFS oids == manifest sha256s; manifest copy `cmp`-clean, md5 pin preserved via `-text` routing) |
| 3 | conversion law: export bytes == twin sha256, 7/7; frames export==source==manifest | PASS (7/7 twin hashes exact; frames equal 7/7) |
| 4 | dur_s ↔ frames ↔ 48 kHz; `mstem_*` % 96 000 == 0; headers PCM16/24 mono 48 kHz | PASS (gate + `--check` + tests) |
| 5 | meter vectors V1–V6 in tolerance | PASS (`meter_validation: vectors V1-V6 passed`; V4 corrected pre-measurement, correction disclosed in rationale §4) |
| 6 | source sample peak within ±0.05 dB of declared `peak_dbfs` | PASS 7/7 (max deviation ≈ 0.005 dB, e.g. −19.4453 vs −19.45) |
| 7 | `asset_gate.py` exit 0 over 8 releases, both invocations; 26 visual pins + frozen builders untouched | PASS (plain gate 0; live gate 0; `git status` clean on all pinned paths; `export_assets.py`/`make_release.py` byte-untouched) |
| 8 | determinism: two in-process builds + CLI re-run `cmp`-clean vs committed bytes | PASS (suite determinism tests + live CLI re-run: all 10 artifacts byte-identical) |
| 9 | full suite green incl. visual regressions; tools coverage ≥ 80 | PASS (369 tests OK; coverage 93%, `full_gate` exit 0) |
| 10 | naming: ids == handoff mechanical ids, snake_case, no fiction, no new ids | PASS (gate-enforced path/id equality; 7 ids verbatim) |
| 11 (M) | LUFS within KB band | **4 RED / 1 GREEN / 2 N-A** — see findings |
| 12 (M) | peak vs KB dBTP column | advisory only (sample peak ≠ dBTP, gap pre-disclosed) |

## Per-file conversion / consistency / loudness table

| asset_id | frames | twin repro | peak16 dBFS | src24 vs declared | LUFS (int.) | KB band | verdict |
|---|---|---|---|---|---|---|---|
| mstem_calm_6s | 288 000 (3 bars) | YES | −19.445 | −19.4453 / −19.45 ✓ | −32.4476 | [−18, −16] | **BELOW −14.45 LU** |
| mstem_combat_6s | 288 000 (3 bars) | YES | −10.9272 | −10.927 / −10.93 ✓ | −23.4042 | [−16, −14] | **BELOW −7.40 LU** |
| msfx_drone_4s | 192 000 | YES | −8.654 | −8.6538 / −8.65 ✓ | −21.6830 | [−24, −20] | **IN BAND** |
| msfx_stinger_2s | 96 000 | YES | −13.9908 | −13.9901 / −13.99 ✓ | −31.3756 | [−14, −10] | **BELOW −17.38 LU** |
| msfx_swarmpip_4s | 192 000 | YES | −21.8638 | −21.8633 / −21.86 ✓ | −41.9713 | none (stacked texture) | report-only |
| mui_confirm_200ms | 9 600 | YES | −21.1544 | −21.1537 / −21.15 ✓ | null (< 400 ms block) | [−16, −12] | n/a (undefined) |
| mui_ping_1200ms | 57 600 | YES | −15.794 | −15.7933 / −15.79 ✓ | −33.0283 | [−16, −12] | **BELOW −17.03 LU** |

## ACCURACY — PASS

- A1 (sheet == metrics to the digit): PASS. Vision pass over the committed sheet
  cross-checked all 7 rows against `audio-metrics.json`: LUFS, target bands, PEAK /
  SRC24 / DECL triplets, DUR/FR, twin-hash prefixes (uppercased hex) — all exact.
- A2 (envelopes from decoded export samples at full scale): PASS. Min/max per column,
  no smoothing, no normalization; amplitudes rank visually as the peaks rank
  numerically (drone tallest at −8.65; swarmpip/confirm visibly faint; ping's decay
  tail reads left-to-right).
- A3 (deviations named per file with numbers, framed as routing findings): PASS —
  the four BELOW-BAND rows carry amber flags on the sheet, exact values in the
  metrics JSON and the findings below; nothing softened, nothing "fixed".

## PRESENTATION — PASS

- P1: mechanical-id labels in the repo's 3×5 glyph convention at 2× native scale,
  no antialiasing, deterministic layout. Legible in the committed PNG.
- P2: id / envelope / metric columns aligned; flags color-coded (green IN BAND /
  MATCH, amber BELOW BAND, gray REPORT ONLY / N-A) — distinct, not alarmist.
- P3: no clipped text, no overlapping rows at native scale.

## Council reconciliation (Kimi K2.5, cross-vendor, 2 calls ≈ 6.8k tokens, ≤ 8k cap)

- Q1 conversion exactness/ties/clamp: **CONFIRMED** — council independently re-derived
  the tie set {±2^22} via 32767⁻¹ mod 2^23 and clamp non-engagement (max |value|
  32766.996 → 32767).
- Q2 BS.1770-4 mechanics: **CONFIRMED** (block/overlap/offset/gating order/mono
  weight 1.0/null-below-one-block all match the standard as published).
- Q3 vectors: **CONFIRMED** — completed the 997 Hz computation to −9.0309 LUFS
  (exactly the pre-registered expectation) and judged the DC-step −32.30 LUFS
  plausible via transient-energy estimate.
- Q4 combat delta: council said **REFUTED** ("expect ≈ +2 dB for dense music; −3.97
  suggests meter bug / wrong channel count"). **Re-verified mechanically and
  overturned:** decomposition (banked in this verdict) shows our plain RMS equals
  upstream's declared rms_dbfs to ≤ 0.001 dB on ALL SEVEN files (two independent
  gates agreeing on the meter's input path), and combat's delta is entirely the
  K-filter term (K-effect −3.98, gating-effect 0.00). K-weighting can only cut
  below ~100 Hz; a bass-dominant combat loop measures exactly like this. The
  council's premise was an unevidenced spectral assumption about the owner's mix;
  the filter cascade itself is proven by V1/V2 and the council's own Q1–Q3.
  Per-file decomposition (K-effect / gate-effect): calm −0.53/+0.04,
  combat −3.98/0.00, drone −1.26/+0.04, stinger +0.92/−0.27, swarmpip +1.73/+0.09,
  ping −0.51/−1.77. Ping's negative gate term is the standard's block structure
  under-weighting the first ~300 ms of a short decaying one-shot (edge samples
  appear in fewer overlapped blocks) — a known BS.1770 property for sub-second
  signals, not a defect.
- Q5 unthought-of risk: council named upstream re-renders breaking hashes and
  divergent conversion paths. Both are pre-routed: consume-on-hash + pinned
  `cfef3117…` makes a re-render a NEW handoff batch by design, and the
  reproduced-twin law eliminates divergent conversions (a future twin-regeneration
  with a different upstream tool would trip the gate loudly — the intended STOP).

## Findings (routed, not rescued)

1. **Four files measure BELOW their KB §7 LUFS bands** (calm −14.45 LU low, combat
   −7.40, stinger −17.38, ping −17.03; drone IN band). The exports are bit-exact the
   owner-approved evaluation twins, so this is upstream mix-level territory:
   routed to game-two-audio/owner via the receipt mail. Two structural notes for
   that conversation: (a) the deltas are internally consistent (music bed quieter
   than drone contradicts the handoff's own level-band ordering "music bed over the
   drone" — calm at −32.4 sits 10.8 LU under the drone at −21.7); (b) if the owner's
   levels are intentional for in-engine bus mixing, the KB bands should be
   re-scoped to post-mix bus targets in a future contract rev — a design decision,
   not this seat's call.
2. **swarmpip has no KB row** (stacked-texture role, ≤ 47 concurrent copies);
   −41.97 LUFS per pip reported for the record. A 47-stack raises level by up to
   10·log10(47) ≈ 16.7 dB (coherent worst case more), landing near −25 LUFS —
   plausible design; noted for the upstream conversation only.
3. **mui_confirm_200ms has no integrated LUFS by construction** (< one 400 ms
   block). Its sample peak (−21.15 dBFS) and the declared RMS carry the level
   information; any future loudness law for sub-400 ms UI sounds needs a different
   metric (momentary max or RMS), pre-registered before use.
4. Handoff manifest is CRLF — caught at staging when the repo's `eol=lf` default
   would have silently broken the md5 pin on fresh checkout; routed `-text` in
   `.gitattributes`. Recorded because it is a repeatable trap for byte-pinned
   upstream text artifacts.

## One next hypothesis (parked, not started)

The level findings predict: in-engine listening will feel music-starved (bed ≈ 11 LU
under the drone). Hypothesis for the upstream seat: the owner mixed each render solo
against REAPER's meters rather than against the stack; a single bus-level listen
session with the seven files at declared levels will either confirm the KB deltas as
intentional layering or produce one re-render batch (new handoff, new twins, new
release id `audio-v2`) — this repo's lane re-runs unchanged either way.

## Boundaries audit

Zero edits to `../game-two` and `../game-two-audio` (read-only `git show`/`ls-tree`
only). Zero audio-content edits (twin-hash-proven). No fixtures re-point, no runtime
claims, no lore, no new ids. v10 pure-turn lane still parked. Visual releases, banked
sheets, `tools/export_assets.py`, `tools/make_release.py`: byte-frozen, verified.
