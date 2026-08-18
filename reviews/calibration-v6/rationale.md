# Calibration v6 — transition-tick smoothing rationale

Sprint-6 question (the banked v5 next-hypothesis): the closed five-state
lane-B grammar has two sharp single-tick pose swaps — **idle→a0 onset**
(the v4 Q4 pop risk: crouch vs pop unproven) and **k0→r0 settle** (the
−6px return + full-pose change; council Q6b: 360 px/s instantaneous,
recoil-vs-teleport unproven). Do one-tick in-between (breakdown) keys
make these two boundaries read as continuous motion at native 1x —
without weakening any banked state read or the deliberately-sharp
release? Scope: `player_1_lane_b` only; the v0 idles, v1 walks, v2
strike keys, v3 coils, and v5 settles are FROZEN inputs; **at most 4 new
frames** (`player_1_lane_b_attack_{down,right}_w0`,
`player_1_lane_b_attack_{down,right}_s0`) are the only new pixels this
sprint. No game-two code runs; nothing in `../game-two` changes.

## Declarations fixed before any artifact exists

- **In-betweens consume pinned ticks, never add them.** Verified at the
  pinned commit: `advance_attack_state` draws each state for exactly its
  configured count; there is no extra tick to insert. Timeline B's windup
  = w0 ×1 + a0 ×4 (total 5, pinned); recovery = s0 ×1 + r0 ×7 (total 8,
  pinned). **The pre-registered cost, stated honestly:** the a0 hold
  shrinks 5→4 ticks (83.3→66.7 ms) and the r0 hold 8→7 (133.3→116.7 ms).
  The banked per-tick/single-tick-recognizability claims survive by
  construction (each held tick still shows the banked pose); whether the
  shortened held spans still beat the incumbents is rubric line 5,
  judged on the sheet.
- **Position snaps are engine-owned and unfixable asset-side.**
  `lunge_offset` is constant per state (windup −3, active +6, else 0; no
  tween). w0 draws at −3 (it occupies windup tick 1); s0 draws at 0
  (recovery tick 1). **The −6px k0→s0 position jump REMAINS** — this
  sprint smooths only the POSE component (declared exclusion, not
  defect: the v5 boundary profile showed the pose swap is the larger
  visual component). Likewise the −3px arrival shift at t14→t15 remains
  under w0.
- **One tick = 16.7 ms is below state-recognition thresholds BY
  DESIGN.** An in-between is a bridge, not a state. The pre-registered
  claim is motion decomposition — the per-tick silhouette jump across
  the boundary shrinks — never "the player reads w0/s0". Every rubric
  line is scoped accordingly.
- **The release stays deliberately unsmoothed.** a0→k0 (27.18/31.97 with
  the +9px release) is the correct salience: the sharpest motion in the
  sequence IS the strike (v4 banked; KB timing doctrine below). No
  frame, no offset change, nothing touches it. Timeline B must not
  reduce the a0→k0 contrast — w0/s0 sit on OTHER boundaries and the
  release delta is machine-compared identical between timelines.

## KB grounding (re-verified in the vault this session, 2026-08-18)

- `game-research/pixel-art-pygame-and-2d-engine-reference.md` §7.2
  (Combat Animation — Smear Frames and Timing), non-uniform-timing
  table, read at source lines 456–462: **Anticipation 100–200 ms "Hold
  frame to build tension"; Strike ~50 ms (1 frame); Follow-through
  ~150 ms "Hold conclusion frame to emphasize weight."** The asymmetry
  is doctrine: anticipation eases in, the strike is instant, the
  follow-through cushions. In-betweens on the onset and settle
  boundaries implement the ease-in and cushion; smoothing the release
  would violate the same table and is out of scope.
- `game-research/aseprite-pixel-art-mastery.md` §7.6 (Smear Frames),
  read at source lines 367–373: smears are elongation/trailing-pixel
  motion-blur vocabulary for high-speed actions, 1–2 frames bridging
  distant positions. **Smears remain OUT** — the in-between here is a
  breakdown pose (a structural midpoint of two keys), a different tool.
- `game-research/technical-drawing-for-game-art.md` §5.4 (Animation
  Timing), lines 242–248: walk-cycle vocabulary distinguishes held
  contact frames from **passing frames at standard timing** — the
  transitional-pose-between-keys concept this sprint applies to the
  attack grammar. The corpus has no attack-specific breakdown doctrine;
  that gap is why this is a calibration sprint rather than a settled
  convention.

## The two boundaries and the burden of proof (A / B)

Boundary magnitudes at the banked exports (silhouette delta =
100·XOR/union; down/right): idle→a0 = **31.10/36.57**; k0→r0 =
**27.12/29.90**; a0→k0 = 27.18/31.97 with the +9px release (untouched).
The v4/v5 timeline protocol extends to an A/B comparison under identical
pinned timing:

- **Timeline A (incumbent):** the v5-banked winner grammar, unmodified —
  a0 held all 5 windup ticks at −3, k0 held 4 active ticks at +6, r0
  held all 8 recovery ticks at 0. Both tested boundaries are single-tick
  full swaps.
- **Timeline B (candidate):** w0 occupying windup tick 1 (t15, at −3)
  then a0 held t16–t19; k0 unchanged t20–t23; s0 occupying recovery tick
  1 (t24, at 0) then r0 held t25–t31. Timelines are tick-identical
  except t15 and t24.

Per-boundary sub-verdicts are independent: bank w0 alone, s0 alone,
both, or full REJECT. If a boundary cannot pass its bars after honest
iteration, its incumbent single-tick swap is banked as the answer with
the finding recorded.

## In-between design doctrine (fixed before pixels; iterated against the bars at spec level — the bars did not move)

Shared constraints (inherited, unchanged): 32×32 RGBA8, hard alpha,
pixels inside `[2,2,29,29]`, anchor `[16,30]`, the frozen 5-color ramp
(`#140e0c`, `#401c10`, `#8c3818`, `#eb7828`, `#ffa050`), no new colors,
feet row 27 ±1, head/eye cluster byte-exact under rigid translation at a
declared (dx,dy) per facing (test-enforced), **jaw/gape closed in all
four in-betweens** (the gape is k0-exclusive and binary — a half-gape
would invent a new marker; jaw-close on the first settle tick is the
KB-correct energy decay), generic IDs.

Each in-between is a **structural midpoint**, never a smear. Parts move
staggered (head leads, legs trail — successive breaking of joints), so
each in-between commits the head half-way while the legs resolve at the
following key; this keeps every in-between leg-stable with its earlier
endpoint and puts the onset read where the eye goes first (the
byte-exact head).

- **Down w0 (onset breakdown, idle→a0):** head = frozen idle_down rows
  4–14 rigidly translated **(0,+2)** — half of a0's (0,+4) drop. The
  pre-registered collision: (0,+2) is k0's exact down head translation;
  the nearest-neighbor bar below is the honest guard (v5 design analysis
  predicted a (0,+2)-head pose with a non-brace body still separates
  from k0 via body/legs — confirmed in the estimates: d(w0,k0) = 21.75,
  4.5pt above both endpoint deltas). Body: idle-width torso rows 17–19,
  lower torso rows 20–21 widened to a0's 12 columns (the haunch bulge
  beginning at the base); bands at a0 width. Legs: 4-row at idle
  columns — the fold completes in a0 (legs trail). Jaw closed.
- **Down s0 (settle breakdown, k0→r0):** head translated **(+1,+2)** —
  between k0's (0,+2) and r0's (+2,+3); the off-axis slump begins. Gape
  CLOSED (the binary marker flips at this boundary). Body rows 17–19 at
  15 columns (between k0's 16-wide brace and r0's 13–14-wide slab),
  sagging toward the shaded side; rows 20–21 at r0's 14 columns. Legs:
  left mid-return at cols 11–13 (k0 splay 10–12 → r0 home 12–14), right
  planted at 19–21 (identical in k0 and r0).
- **Right w0 (onset breakdown, idle→a0):** head = frozen idle_right rows
  4–9 rigidly translated **(−1,+2)** — half of a0's (−2,+3) retraction;
  the translation is virgin (no frozen right state sits at (−1,+2)).
  Upper body: one slab row at cols 12–27 (idle carries three at 13–28) —
  the neck compressing; snout staircase descends rows 13–14; tail block
  kept at the idle rows (identity anchor shared by both endpoints) with
  body behind it at a0's width. Legs: 4-row at idle columns (a0 gathers
  and folds them — legs trail). Jaw closed.
- **Right s0 (settle breakdown, k0→r0):** head translated **(0,+4)** —
  between k0's (0,+3) and r0's (+1,+4): the drop completes first, the
  forward drift completes in r0 (head leads with the collapse). Gape
  kkkk CLOSED to plain body. Tail block at rows 15–19 with three oss
  rows — exactly between k0's block (rows 17–20, two oss rows) and r0's
  raised block (rows 14–18, three oss rows): the weight-tip beginning.
  Forward mass shortens to col 27 (k0 reaches 28 gaped; r0 pools low to
  26–27). Front leg at cols 20–22 (k0 reach 21–23 → r0 19–21), rear at
  k0's 10–12; r0's 4-row leg structure.

**Design-time spec-level estimates (analysis, not evidence — the banked
bars are judged on export bytes by `tools/transition_metrics.py`;
exports are verified pixel-for-pixel against these specs, so the numbers
are expected to transfer exactly):**

| bridging decomposition | down | right |
|---|---|---|
| d(idle,w0) / d(w0,a0) vs d(idle,a0) | 16.48 / 17.25 vs **31.10** | 19.69 / 20.83 vs **36.57** |
| d(k0,s0) / d(s0,r0) vs d(k0,r0) | 15.38 / 16.18 vs **27.12** | 21.31 / 14.98 vs **29.90** |

| nearest-neighbor ordering (four grammar states) | down | right |
|---|---|---|
| w0 (must be idle, a0) | idle 16.48, a0 17.25, k0 21.75, r0 28.57 | idle 19.69, a0 20.83, k0 25.48, r0 26.42 |
| s0 (must be k0, r0) | k0 15.38, r0 16.18, a0 28.87, idle 32.24 | r0 14.98, k0 21.31, a0 28.66, idle 34.52 |

| other estimates | down w0 | down s0 | right w0 | right s0 |
|---|---|---|---|---|
| vs walks f0–f3 | 22.91, 23.49, 22.91, 16.48 | 36.45, 37.22, 29.87, 32.24 | 28.27, 27.51, 28.27, 19.69 | 34.52, 40.79, 40.23, 34.52 |
| max delta (ceiling 44.44) | 28.57 | 37.22 | 28.27 | 40.79 |
| mass vs idle | −4.78% (239) | +3.19% (259) | −4.41% (282) | −11.53% (261) |
| feet row / drift | 27 / 0 | 27 / 0 | 27 / 0 | 27 / 0 |
| bbox | [9,6,22,27] | [9,6,23,27] | [7,6,27,27] | [7,8,28,27] |

Mass is monotone through both transitions in both facings (idle 251 →
w0 239 → a0 227; k0 269 → s0 259 → r0 241; idle 295 → w0 282 → a0 277;
k0 259 → s0 261 → r0 270) — no pumping artifact mid-bridge. The
w0-vs-s0 cross-delta (23.40 down / 22.55 right) is reported for honesty;
the two in-betweens never appear adjacent (separated by the a0 hold, the
k0 span, or both) and carry no state claim, so no floor applies.
Deliberate estimate properties, disclosed: w0's delta to f3 equals its
idle delta (f3 is the banked verbatim idle copy — expected and correct);
w0's walk deltas sit below the 25.0 state floor by design — w0 is a
bridge, not a state; it never coexists with a walk frame (windup tick 1
follows arrival) and the nearest-neighbor bar, not the state floor, is
its guard.

## Timeline design (fixed before any artifact exists)

**Cadence: 1 column = 1 tick** (the v4/v5 convention). The tick plan is
a pure function of the pinned constants (0-indexed); all v4/v5 declared
conventions carry unchanged (walk-frame mapping f0×4/f1×3/f2×3/f3×3,
round_half_up positions, windup begins the tick after arrival, 2-tile
grid-lined windows, overlap column t14; hitstop/exhaust/action-tile
overlay excluded — identical in A and B, none can bias the comparison):

| ticks | phase | count | timeline A pose | timeline B pose | position |
|---|---|---|---|---|---|
| t00–t01 | idle_pre | 2 (declared context) | idle | idle | 0 |
| t02–t14 | walk | 13 = `step_frames` | f0..f3 | f0..f3 | round_half_up(32·smoothstep(k/13)) |
| t15 | windup 1 | 1 | a0 | **w0** | 32 − 3 |
| t16–t19 | windup 2–5 | 4 | a0 | a0 | 32 − 3 |
| t20–t23 | active | 4 = `active_frames` | k0 | k0 | 32 + 6 |
| t24 | recovery 1 | 1 | r0 | **s0** | 32 |
| t25–t31 | recovery 2–8 | 7 | r0 | r0 | 32 |
| t32–t33 | idle_post | 2 (declared context) | idle | idle | 32 |

**Sheet structure, per facing** (`tools/make_transition_timeline.py`):

- RULER rows: phase labels + per-tick indices (both row groups).
- APPROACH rows (t00–t14; identical in A and B, one row per zone): Z1, Z2.
- ATTACK rows (t14–t33): Z1 A/B, Z2 A/B stacked — the two transition
  ticks are the only differing columns.
- 2X row (timeline B, Z1): the six transition-region ticks — t14 (last
  walk/arrival), t15 (w0), t16 (first a0), t23 (last k0), t24 (s0), t25
  (first r0) — both boundaries under test at 2x.
- 4X boundary strips (timeline B, Z1): one row per boundary showing the
  X | M | Y triplet at its real timeline offsets — ONSET: idle@0(t14) |
  w0@−3(t15) | a0@−3(t16); SETTLE: k0@+6(t23) | s0@0(t24) | r0@0(t25) —
  at 4x nearest-neighbor for pixel diagnosis.
- FILM rows (Z1, Z2): the static strip extended to ten columns — idle |
  f0–f3 | a0 | k0 | r0 | **w0** | **s0** over exact zone palettes.
- DIFF row: each in-between vs its two endpoints at 2x (w0 vs idle, w0
  vs a0, s0 vs k0, s0 vs r0; `diff_pixels`, derived diagnostic — not a
  creature cell).
- GRAMMAR row (Z1): **nine cells** — idle | f1 | **w0@−3** | a0 |
  a0@−3 | k0 | k0@+6 | **s0@0** | r0@0 — the banked control row with the
  in-betweens inserted at their timeline positions.

**Viewing aids (optional, never blocking):** one APNG per facing —
timelines A | B side by side, full 34-tick sequence over a 3-tile
window, 4x nearest-neighbor, exact 1/60 s per-frame delay (the banked
encoder), 0.5 s final hold, infinite loop. Byte-identical on
regeneration or dropped.

**Critique method:** the committed sheet is the single reviewed
artifact; the vision pass may additionally read deterministic band crops
of the same committed bytes at native scale (ephemeral diagnostics,
never separately banked evidence). Judged at native 1x on the session
vision model (verify `PI_MODEL` is Fable-5-class; never trust
self-report); the council seat stays cross-vendor (owner directive
2026-08-17).

## Pass bars (fixed now, before any export or sheet exists)

Machine-checkable (`tools/transition_metrics.py --check`, exit nonzero
on any failure):

1. **Release chain:** all asset-gate checks over all six releases; specs
   validate; exports verified pixel-for-pixel; calibration-v6 release
   manifest complete (full hash chain, provenance origin `procedural`,
   derivation notes naming each in-between's endpoints) at the live pin.
2. **Bridging bar (export bytes), per in-between, per facing:**
   max(d(X,M), d(M,Y)) < d(X,Y) — the boundary's largest single-tick
   silhouette jump strictly decreases; the full decomposition is
   reported.
3. **Nearest-neighbor bar:** among the four grammar states {idle, a0,
   k0, r0}, M's two smallest deltas are exactly its two endpoints
   (deltas to all walk frames reported; w0's expected near the idle
   delta).
4. **Identity ceiling:** every M delta < 44.44%; head byte-exact at the
   declared (dx,dy) (test-enforced); feet row 27 ±1; ramp unchanged.
5. **Frozen-state protection:** the five banked state exports are
   byte-untouched (pin check over v0–v6 release manifests) — their
   banked floors stand by construction; the release boundary (a0→k0
   delta and the +9px offset step) is IDENTICAL in timelines A and B
   (machine-compared from the cell manifest + export bytes).
6. **Timeline bars (v5 conventions):** sheet + metrics + any APNG
   byte-identical across two independent in-process builds and equal to
   committed bytes; composition purity per creature cell against export
   bytes (v0–v6, dual verification); tick math exact — windup span = 5
   cells at −3 in both timelines (B: w0 ×1 + a0 ×4), active = 4 at +6
   (k0, both), recovery = 8 at 0 (B: s0 ×1 + r0 ×7), walk = 13 at
   independently recomputed smoothstep positions; timelines
   tick-identical except t15 and t24.
7. **Regression:** banked sheets v0–v5 regenerate byte-identical under
   the extended toolchain; `tools/` coverage ≥ 80.

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone
palettes, both facings):

1. **The idle→w0→a0 span in timeline B reads as one continuous crouch**
   (beginning → deepened) where timeline A's idle→a0 is a single-tick
   pop — judged per tick on the stacked rows and the boundary 2X/4X
   strips.
2. **The k0→s0→r0 span reads as strike energy decaying through the
   settle** (gape closes, mass collapses in two steps) where A's k0→r0
   is a single-tick full swap — same judgment method.
3. **Neither w0 nor s0 introduces a readable NEW state:** in FILM
   context each reads as "between" its endpoints (the nearest-neighbor
   bar must agree with the native read); no sixth/seventh grammar state
   emerges.
4. **The release keeps its salience:** in timeline B the a0→k0 snap
   remains the sharpest, most attention-grabbing single-tick change on
   the sheet (the strike must not be upstaged by its neighbors'
   smoothing).
5. **The banked state reads survive the shortened holds** (a0 ×4 windup
   ticks still telegraphs vs the v4-incumbent memory; r0 ×7 still reads
   settle-vs-idle) and identity holds throughout (byte-exact heads,
   frozen ramp).

**Decision rule (fixed):** B wins a boundary only if the boundary's own
lines pass AND lines 3–5 hold sheet-wide; per-boundary sub-verdicts are
independent (bank w0 alone, s0 alone, both, or full REJECT — an honest
incumbent win is a legitimate answer). No rescue edits to frozen frames,
no invented runtime values, no smear frames, no added ticks.

Scope discipline carried from v4/v5: claims are per-tick legibility +
single-tick recognizability + A/B superiority under identical pinned
timing — never "reads at combat speed"; the runtime replay capture stays
an INTEGRATION item (one-way boundary), not a sprint hypothesis.

## Toolchain plan

At most 2 new tools; banked helpers imported unmodified
(`png_reader`/`png_writer`, `make_contact_sheet` tile drawing,
`make_feedback_sheet.tell_cell`, `make_motion_sheet.diff_pixels`,
`motion_metrics.frame_stats`/`pair_stats`/`load_opaque`,
`make_grammar_timeline` compositor pieces + APNG encoder,
`timeline_metrics.TICK_MS`):

- `tools/make_transition_timeline.py` (new, tested): the A/B tick plan
  (pure function of the pinned constants), the timeline sheet with
  2X/4X-boundary/FILM/DIFF/GRAMMAR rows, the cell manifest, the APNG
  aids.
- `tools/transition_metrics.py` (new, tested): the bridging +
  nearest-neighbor + ceiling suite on export bytes, the boundary-jump
  table across A and B (including the preserved release), and `--check`
  enforcing bars 1–7.

Release chain: `sources/calibration-v6/specs/*.json` →
`tools/build_sources.py`/`aseprite_build.lua` → `tools/export_assets.py`
(SHA-pinned — never edited; invoked with ABSOLUTE paths) →
`exports/calibration-v6/release.json` via `tools/make_release.py`
(registry append — trailing closers re-emitted exactly). Tests cover
every new deterministic behavior mirroring `tests/test_recovery_tools.py`
(synthetic fixture + spec-contract suite + skip-guarded real-artifact
regressions).

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default
seat) of the rationale + measured evidence + my provisional rubric
verdicts, ≤ 8k total tokens; response redirected to a file and read with
explicit UTF-8; every council claim re-verified against pixels/numbers
before acceptance (v5 precedent: the council inverted the distinctness
metric and fabricated a precedent — recompute EVERY numeric claim it
makes before adopting).

## Stop conditions

One asset cycle: at most 4 new creature frames (the w0/s0 pairs), one
deterministic timeline sheet, optional APNG aids, one banked verdict
with per-boundary sub-verdicts. No lore, no 8-direction sets, no smear
frames, no exhaust-state pose, no terrain/enemies/pack, no runtime
integration, no game-two changes, no Bedrock generation. Timing
constants read-only from the pinned commit; in-betweens consume pinned
ticks; no new runtime constant consumed (no `render-reference.json`
change expected). Change sets: (0) re-pins alone per the step-0
protocol; (1) this rationale + specs + sources + release + toolchain +
tests; (2) timeline sheet + metrics + verdict. Stop after banking the
sprint-6 verdict.
