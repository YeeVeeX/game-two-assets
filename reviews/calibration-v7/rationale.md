# Calibration v7 — completion-rise smoothing rationale (ready-again boundary)

Sprint-7 question (the banked v6 next-hypothesis): the closed lane-B
grammar's one remaining un-smoothed pose-only discontinuity is the
**ready-again beat** — r0→idle at t31→t32, **37.09/37.64** (down/right)
at 0px: the largest single-tick silhouette change on the sheet,
identical in every banked timeline. Does a one-tick rise breakdown
(r0→**x0**→idle, x0 consuming recovery tick 8) make the completion read
as a rise rather than a swap — without erasing the completion signal,
without introducing direction ambiguity against the banked bridges, and
without weakening any banked read? Scope: `player_1_lane_b` only; the
v0 idles, v1 walks, v2 strike keys, v3 coils, v5 settles, and v6
bridges are FROZEN inputs; **at most 2 new frames**
(`player_1_lane_b_attack_{down,right}_x0`) are the only new pixels this
sprint. No game-two code runs; nothing in `../game-two` changes.

## The central tension, stated before any artifact exists

Unlike v6, the boundary under test is a banked SIGNAL, not noise. v5
banked this boundary's EXISTENCE as the value (rubric line 3: "the
boundary EXISTS in R and is single-tick recognizable… in A it does not
exist — that is the point"): recovery ending visibly is the
attack/dodge unlock cue. The v6 onset pop and settle swap were
discontinuity artifacts; the ready-again snap may be CORRECT salience.
Smoothing trades crispness for continuity. The decision rule below
therefore makes **REJECT — incumbent snap banked as the correct
salience for "ready again" — a fully respectable, first-class outcome**;
nothing in this rationale leans the rubric toward B. If B loses, the v5
beat-existence claim stands unmodified and the finding is recorded.

## Declarations fixed before any artifact exists

- **x0 consumes a pinned tick, never adds one.** Verified at the pinned
  commit (state machine unchanged 88fd36d): `advance_attack_state`
  exhausts recovery after 8 drawn ticks then `interrupt_action!` →
  `:idle`; there is no post-recovery state to hang a pose on (the
  exhaust tail draws `:idle` — the banked v5 exclusion). x0 can ONLY
  occupy recovery tick 8 (t31). Timeline B's recovery = s0 ×1 + r0 ×6 +
  x0 ×1 (total 8, pinned); windup stays w0 ×1 + a0 ×4 (5, pinned).
- **The cumulative r0-hold cost, stated honestly:** the r0 conclusion
  hold shrinks across the series 8 ticks (133.3 ms, v5) → 7 (116.7 ms,
  v6 winner) → **6 in B (100.0 ms)** against the KB ~150 ms
  follow-through reference — now 50 ms under. Total recovery span stays
  8 ticks of follow-through-family content (s0+r0+x0). **If the sheet
  shows the settle read degrading at 6 held columns, that alone REJECTS
  on rubric line 5.**
- **This is a PURE pose swap — the cleanest isolation yet.** t31 and
  t32 both draw at position 32 (recovery draws at the lunge_offset
  else-branch 0; idle draws at 0). No position component exists at the
  boundary; nothing engine-owned is excluded because nothing engine-side
  moves.
- **One tick = 16.7 ms is below state-recognition thresholds BY
  DESIGN.** x0 is a bridge, never a state. The pre-registered claim is
  motion decomposition — the per-tick silhouette jump across the
  boundary shrinks — never "the player reads x0". Every rubric line is
  scoped accordingly.
- **The release and the banked v6 bridges stay untouched.** The a0→k0
  release (27.18/31.97 with the +9px step) and the banked w0/s0
  transition ticks (t15, t24) are IDENTICAL in timelines A and B —
  machine-compared, and additionally subsumed by tick-identity (the
  timelines differ at t31 only). No frame, no offset change, nothing.

## KB grounding (re-verified in the vault this session, 2026-08-18)

- `game-research/pixel-art-pygame-and-2d-engine-reference.md` §7.2
  (Combat Animation — Smear Frames and Timing), non-uniform-timing
  table, re-read at source: **Anticipation 100–200 ms "Hold frame to
  build tension"; Strike ~50 ms (1 frame); Follow-through ~150 ms "Hold
  conclusion frame to emphasize weight."** The banked v4–v6 asymmetry
  doctrine stands: the strike is the instant beat; neighbors ease and
  cushion. The follow-through reference is the yardstick for the
  100.0 ms disclosure above.
- `game-research/technical-drawing-for-game-art.md` §5.4 (Animation
  Timing), re-read at source: contact frames 100 ms ("impact"), passing
  frames 80–100 ms standard, and **"Rise frames 80 ms — slightly faster
  — upward motion is lighter."** Walk-cycle vocabulary, not attack
  doctrine — but it is the corpus's only rise-specific timing note, and
  its direction (rises read light and quick) is consistent with a
  one-tick rise breakdown rather than a held rise state.
- `game-research/aseprite-pixel-art-mastery.md` §7.6 (Smear Frames),
  re-read at source: smears are elongation/trailing-pixel motion-blur
  for high-speed actions. **Smears remain OUT** — x0 is a breakdown
  pose (structural midpoint), a different tool.
- **Corpus gap, disclosed:** the corpus carries no doctrine on
  completion/settle-exit/ready-again beats — nothing prescribes whether
  a recovery-end boundary should be sharp (a beat) or smoothed (a
  rise). The sharp-vs-smooth question is genuinely open; this sprint is
  a calibration experiment, not the application of a settled
  convention, and the incumbent-wins outcome is exactly as
  doctrine-compatible as the candidate.

## The boundary and the burden of proof (A / B)

Boundary magnitudes at the banked exports (silhouette delta =
100·XOR/union; down/right): r0→idle = **37.09/37.64** — the largest gap
yet bridged (v6 bridged 31.10/36.57 and 27.12/29.90), so the bridging
bar has the most headroom yet. Nearest-neighbor margins to beat: r0 vs
a0 = 27.94/29.60, r0 vs k0 = 27.12/29.90; ceiling 44.44.

- **Timeline A (incumbent):** the v6-banked winner grammar UNMODIFIED —
  w0 t15, a0 t16–t19, k0 t20–t23, s0 t24, r0 t25–t31. The ready-again
  boundary is the banked single-tick full swap at t31→t32.
- **Timeline B (candidate):** identical except t31, where x0 occupies
  recovery tick 8 — recovery = s0 ×1 + r0 ×6 + x0 ×1. Timelines are
  tick-identical except t31 (the only differing tick).

Single-boundary sub-verdict: BANK x0 or REJECT (incumbent wins); both
first-class. If the boundary cannot pass its bars after honest
iteration, the incumbent snap is banked as the answer with the finding
recorded.

## The two direction-ambiguity risks (pre-registered)

1. **x0 vs s0** — both are r0-neighborhood bridges; one pose must not
   encode both "collapsing in" (s0) and "rising out" (x0) — the v5
   C-inversion class. The idle-distance asymmetry separates them:
   d(s0,idle) = 32.24/34.52 (banked) while x0 sits far idle-ward
   (estimates below: d(x0,idle) = 20.43/23.62). Disclosed honestly at
   spec level: **d(x0,s0)-down estimates at 16.25 — the tightest
   bridge-to-bridge proximity in the set** (v6's w0↔s0 cross-delta was
   23.40/22.55). The two bridges never appear adjacent (x0 at t31, s0
   at t24, separated by six r0 ticks), carry no state claim, and no
   floor applies (the banked v6 convention: the machine NN bar stays on
   the four STATES); the separation cues are pose-structural (below)
   and the direction read is judged at 4X on rubric line 3.
2. **x0 vs w0** — BOTH are idle-adjacent half-poses (w0 sinking in at
   −3px, x0 rising out at 0px); heads land 1–2px apart. Mitigated in
   the pose itself, not only context: each x0 carries at least TWO
   settle-family residues w0 lacks — down: the +1 lateral head residue
   (the v5-banked virgin lateral axis = settle marker) + asymmetric
   legs (right leg still at r0's 19–21; w0-down legs are symmetric at
   the idle columns) + the lower-torso width residue extending RIGHT to
   col 22 (w0's haunch bulge extends LEFT to col 10); right: the +1
   forward head residue (overshoot axis; w0-right retracts −1) + the
   tail block one row above the idle rows (residue of r0's raise;
   w0-right keeps the tail exactly at the idle rows) + asymmetric legs
   at r0's columns (w0 symmetric at idle's). d(x0,w0) and d(x0,s0) are
   reported per facing (no floor — bridges carry no state claim).

## x0 design doctrine (fixed at spec level; iterated against the bars before committing — the bars did not move)

Shared constraints (inherited, unchanged): 32×32 RGBA8, hard alpha,
pixels inside `[2,2,29,29]`, anchor `[16,30]`, the frozen 5-color ramp
(`#140e0c`, `#401c10`, `#8c3818`, `#eb7828`, `#ffa050`), no new colors,
feet row 27 ±1, head/eye cluster byte-exact under rigid translation at
a declared virgin (dx,dy) per facing (test-enforced), **jaw/gape closed**
(the gape is k0-exclusive and binary), generic IDs.

x0 = structural midpoint of r0 and idle with an **idle-ward energy
direction**: head rising off the slump, torso narrowing from r0's
13–14 columns toward idle's 10, slump/overshoot unwinding, mass
monotone, tail descending toward the idle rows (right), jaw closed,
feet row 27. Parts move staggered per the banked v6 convention — head
leads, legs trail: each x0 commits the head half-way home while the
legs stay at r0's columns (leg-stable with the EARLIER endpoint; the
leg return completes inside the arrival tick, exactly as w0's fold
completes in a0). One measured deviation from the sprint brief's design
sketch, disclosed: the brief suggested the down right leg at 18–20
(1px off-home); iteration showed r0's own 19–21 both balances the
bridge (21.45/20.43 vs a lopsided 24.37/17.52 with the 18–20 leg) and
strengthens the w0 separation (20.88 vs 17.91) — the legs-trail
doctrine and the numbers agree, so the leg stays at r0's column.

- **Down x0:** head = frozen idle_down rows 4–14 rigidly translated
  **(+1,+1)** — virgin (banked down translations: a0 (0,+4), k0 (0,+2),
  r0 (+2,+3), w0 (0,+2), s0 (+1,+2); the brief's alternative (+1,+2)
  is s0-down's exact translation, avoided as pre-registered). Halfway
  home on both axes with an idle-lean on y (the rise direction). Upper
  torso rows 17–18 re-formed AT the idle columns (11–20, byte-equal
  rows to the idle torso pattern — the rise reads top-down); lower
  torso rows 19–21 still pooled 12 wide with the width residue
  extending right to col 22 (r0's slump side); belly band 12 wide;
  outline row 23 at 11–21; legs: left home at 12–14, right still at
  r0's 19–21 (legs trail). Jaw closed.
- **Right x0:** head = frozen idle_right rows 4–9 rigidly translated
  **(+1,+2)** — virgin (banked right translations: a0 (−2,+3), k0
  (0,+3), r0 (+1,+4), w0 (−1,+2), s0 (0,+4)); carries r0's +1 forward
  lean while rising +2 of the +4 drop. One re-stacked neck slab row 12
  (idle carries three; r0 none — its mass pools low) continuing the
  rigid flow, tapers 13–14 with a +1 forward-reach residue; tail block
  rows 15–19 with oss rows 16–18 — exactly one row above the idle
  block (16–20/oss 17–19) and one below r0's raised block (14–18/oss
  15–17): the weight-tip unwinding; torso rows 16–21 reaching col 23
  (between idle's 21 and r0's 24 — the forward pool draining); belly
  and outline rows 14 wide; legs at r0's columns (rear 11–13, front
  19–21; legs trail). Jaw closed.

**Design-time spec-level estimates (analysis, not evidence — the banked
bars are judged on export bytes by `tools/rise_metrics.py`; exports are
verified pixel-for-pixel against these specs, so the numbers are
expected to transfer exactly):**

| bridging decomposition | down | right |
|---|---|---|
| d(r0,x0) / d(x0,idle) vs d(r0,idle) | 21.45 / 20.43 vs **37.09** | 19.67 / 23.62 vs **37.64** |

| nearest-neighbor ordering (four grammar states) | down | right |
|---|---|---|
| x0 (must be {idle, r0}) | idle 20.43, r0 21.45, k0 26.42, a0 30.85 | r0 19.67, idle 23.62, k0 28.89, a0 29.66 |
| margin, 3rd smallest − 2nd | 4.97pt | 5.27pt |

| other estimates | down x0 | right x0 |
|---|---|---|
| vs w0 / vs s0 (reported, no floor) | 20.88 / 16.25 | 19.87 / 22.04 |
| vs walks f0–f3 | 31.76, 26.37, 18.25, 20.43 | 27.84, 30.12, 27.84, 23.62 |
| max delta (ceiling 44.44) | 31.76 | 30.12 |
| mass chain r0 → x0 → idle | 241 → 250 → 251 | 270 → 280 → 295 |
| feet row / drift | 27 / 0 | 27 / 0 |
| bbox | [10,5,23,27] | [7,6,29,27] |

Disclosed estimate properties: mass is monotone through the bridge in
both facings (no pumping artifact), but x0-down sits mass-adjacent to
idle (250 vs 251) — the pose divergence, not mass, carries that bridge;
mass is a no-pumping diagnostic, never a midpoint bar. The down bridge
is near-centered (21.45/20.43); the right bridge leans r0
(19.67/23.62) — the arrival leg is deliberately the LARGER leg, which
is the completion-preserving shape (the strongest remaining beat lands
on the arrival at idle), and the facing asymmetry echoes the banked v6
bridge-lean finding on the same facing. x0-down's closest frozen
neighbor is s0 at 16.25 (risk 1 above, disclosed); x0-right's walk
deltas sit comfortably above its endpoint deltas; f3 tracks the idle
delta by construction (f3 = banked idle byte-copy). Estimated
boundary-jump consequence, pre-registered: in timeline B the sheet-wide
sharpest pose jump becomes the RELEASE (27.18/31.97) on both facings —
in timeline A it is the un-smoothed ready-again swap (37.09/37.64); if
B banks, the last salience inversion (the completion out-jumping the
strike pose-wise) resolves. Whether that trade is worth a softer
completion beat is exactly rubric line 2's question, judged
head-to-head, REJECT fully available.

## Timeline design (fixed before any artifact exists)

**Cadence: 1 column = 1 tick** (the banked v4–v6 convention). The tick
plan is a pure function of the pinned constants (0-indexed); all
declared conventions carry unchanged (idle_pre ×2, walk-frame mapping
f0×4/f1×3/f2×3/f3×3, round_half_up smoothstep positions, windup begins
the tick after arrival, 2-tile grid-lined windows, overlap column t14,
idle_post ×2; hitstop/exhaust/action-tile overlay excluded — identical
in A and B):

| ticks | phase | count | timeline A pose | timeline B pose | position |
|---|---|---|---|---|---|
| t00–t01 | idle_pre | 2 (declared context) | idle | idle | 0 |
| t02–t14 | walk | 13 = `step_frames` | f0..f3 | f0..f3 | round_half_up(32·smoothstep(k/13)) |
| t15 | windup 1 | 1 | w0 (banked v6) | w0 (identical) | 32 − 3 |
| t16–t19 | windup 2–5 | 4 | a0 | a0 | 32 − 3 |
| t20–t23 | active | 4 = `active_frames` | k0 | k0 | 32 + 6 |
| t24 | recovery 1 | 1 | s0 (banked v6) | s0 (identical) | 32 |
| t25–t30 | recovery 2–7 | 6 | r0 | r0 | 32 |
| t31 | recovery 8 | 1 | r0 | **x0** | 32 |
| t32–t33 | idle_post | 2 (declared context) | idle | idle | 32 |

**Sheet structure, per facing** (`tools/make_rise_timeline.py`):

- RULER rows: phase labels + per-tick indices (both row groups).
- APPROACH rows (t00–t14; identical in A and B, one row per zone).
- ATTACK rows (t14–t33): Z1 A/B, Z2 A/B stacked — t31 is the only
  differing column.
- 2X row (timeline B, Z1): the four boundary-region ticks — t30 (last
  held r0), t31 (x0), t32 (arrival idle), t33 (held idle) — at 2x.
- RISE 4X strip (timeline B, Z1): r0@0 (t30) | x0@0 (t31) | idle@0
  (t32) at 4x nearest-neighbor (pixel diagnosis).
- FILM rows (Z1, Z2): the static strip extended to eleven columns —
  idle | f0–f3 | a0 | k0 | r0 | w0 | s0 | **x0**.
- DIFF row: x0 vs r0, x0 vs idle (the endpoints), plus x0 vs s0 and
  x0 vs w0 (the declared ambiguity diagnostics) at 2x (banked
  diff_pixels; derived diagnostic, not a creature cell).
- GRAMMAR row (Z1): **ten cells** — idle | f1 | w0@−3 | a0 | a0@−3 |
  k0 | k0@+6 | s0@0 | r0@0 | **x0@0** — the banked control row with x0
  inserted at its timeline position after r0.

**Viewing aids (optional, never blocking):** one APNG per facing —
timelines A | B side by side, full 34-tick sequence over a 3-tile
window, 4x nearest-neighbor, exact 1/60 s per-frame delay (the banked
encoder), 0.5 s final hold, infinite loop. Byte-identical on
regeneration or dropped.

**Critique method:** the committed sheet is the single reviewed
artifact; the vision pass may additionally read deterministic band
crops of the same committed bytes at native scale (ephemeral
diagnostics, never separately banked evidence). Judged at native 1x on
the session vision model (verify `PI_MODEL` is Fable-5-class; never
trust self-report); the council seat stays cross-vendor (owner
directive 2026-08-17).

## Pass bars (fixed now, before any export or sheet exists)

Machine-checkable (`tools/rise_metrics.py --check`, exit nonzero on any
failure):

1. **Release chain:** all asset-gate checks over all SEVEN releases;
   specs validate; exports verified pixel-for-pixel; calibration-v7
   release manifest complete (full hash chain, provenance origin
   `procedural`, derivation notes naming the in-between's endpoints and
   its direction residues) at the live pin.
2. **Bridging bar (export bytes), per facing:** max(d(r0,x0),
   d(x0,idle)) < d(r0,idle) — the boundary's largest single-tick
   silhouette jump strictly decreases; the full decomposition is
   reported.
3. **Nearest-neighbor bar:** among the four grammar states {idle, a0,
   k0, r0}, x0's two smallest deltas are exactly {r0, idle} (deltas to
   all walk frames AND to w0/s0 reported — walk deltas expected near
   the idle delta, f3 = idle byte-copy precedent).
4. **Identity ceiling:** every x0 delta < 44.44%; head byte-exact at
   the declared (dx,dy) (test-enforced); feet row 27 ±1; ramp
   unchanged.
5. **Frozen-state protection:** all 22 consumed exports (11 poses × 2
   facings) hash to banked release.json pins across v0–v7 — the six
   banked frame-sets byte-untouched; the release boundary (a0→k0,
   27.18/31.97 at +9px) AND the banked w0/s0 transition ticks (t15,
   t24) are IDENTICAL in timelines A and B (machine-compared; subsumed
   by tick-identity but checked explicitly — defense in depth).
6. **Timeline bars (v6 conventions):** sheet + metrics + any APNG
   byte-identical across two independent in-process builds and equal to
   committed bytes; composition purity per creature cell against export
   bytes (v0–v7, dual verification); tick math exact — windup 5 at −3
   (w0 ×1 + a0 ×4, BOTH timelines), active 4 at +6 (k0), recovery 8 at
   0 (A: s0 ×1 + r0 ×7; B: s0 ×1 + r0 ×6 + x0 ×1), walk 13 at
   independently recomputed smoothstep positions; timelines
   tick-identical except t31 (the only differing tick).
7. **Boundary-jump table** across A and B covering (14,15), (15,16),
   (19,20), (23,24), (24,25), (30,31), (31,32), (32,33) with pose delta
   + position delta per row and sharpest-single-tick attributions per
   timeline.
8. **Regression:** banked sheets v0–v6 regenerate byte-identical under
   the extended toolchain; `tools/` coverage ≥ 80.

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone
palettes, both facings; every judgment is sheet-scope — per-tick
legibility and single-tick recognizability, never temporal fusion at
60 tps):

1. **The r0→x0→idle span in timeline B reads as one continuous rise**
   (mass lifting, slump/overshoot unwinding, tall stance re-forming)
   where timeline A's r0→idle is a single-tick full swap — judged per
   tick on the stacked rows and the 2X/RISE-4X strips.
2. **The completion signal survives:** the arrival at the tall
   symmetric ready idle at t32 remains a clear, single-tick-
   recognizable state arrival in B (d(x0,idle) must still read as a
   state boundary at 1x, not a mush) — judged head-to-head against A's
   crisp snap; **if A's snap reads BETTER as a readiness signal at
   native 1x, that is grounds for REJECT and is a finding, not a
   failure.**
3. **x0 introduces no readable NEW state and NO DIRECTION AMBIGUITY:**
   in FILM and sequence context x0 reads as rising toward idle — never
   as the settle beginning (s0's opposite) and never as the crouch
   beginning (w0's opposite); the NN bar must agree with the native
   read; the settle-family residues (lateral/forward head lean,
   leg/tail residue) must be visible at 4X.
4. **Untouched salience holds:** the release remains the sheet's
   sharpest attack-boundary event (pose + 9px displacement) and the
   banked w0/s0 bridges read exactly as banked (byte-identical cells).
5. **The banked reads survive the shortened hold:** r0 ×6 columns still
   read as the held settle (vs the v5/v6 incumbent memory), s0's
   first-tick read is unchanged, and identity holds throughout
   (byte-exact heads, frozen ramp, 0-drift feet).

**Decision rule (fixed):** B wins ONLY if lines 1–3 pass AND lines 4–5
hold sheet-wide; otherwise REJECT and bank the incumbent single-tick
snap as the correct salience for "ready again", recording the finding
(the v5 beat-existence claim then stands unmodified). No rescue edits
to frozen frames, no invented runtime values, no smear frames, no added
ticks, no second in-between on this boundary.

Scope discipline carried from v4–v6: claims are per-tick legibility +
single-tick recognizability + A/B superiority under identical pinned
timing — never "reads at combat speed"; beat-crispness UNDER MOTION is
unprovable on a sheet and goes to the runtime replay item EITHER way.
Pre-registered items NOT re-tested: w0/s0 bridging (banked v6), release
preservation semantics (the machine check carries unchanged), r0 state
distinctness (v5), C's inversion (v5), ACC cadence (v4).

## Toolchain plan

At most 2 new tools; banked helpers imported unmodified
(`png_reader`/`png_writer`, `make_contact_sheet` tile drawing,
`make_feedback_sheet.tell_cell`, `make_motion_sheet.diff_pixels`,
`motion_metrics.frame_stats`/`pair_stats`/`load_opaque`,
`make_grammar_timeline` compositor pieces + APNG encoder,
`timeline_metrics.TICK_MS`):

- `tools/make_rise_timeline.py` (new, tested): the A/B tick plan (pure
  function of the pinned constants; A = the v6-banked winner grammar,
  B differs at t31 only), the timeline sheet with 2X/RISE-4X/FILM/DIFF/
  GRAMMAR rows per the design above, the cell manifest, the APNG aids.
- `tools/rise_metrics.py` (new, tested): the bridging +
  nearest-neighbor + ceiling suite on export bytes, the extended
  boundary-jump table across A and B (including the preserved release
  and the banked w0/s0 ticks), durations with the 100.0 ms disclosure,
  and `--check` enforcing bars 1–8.

Tests in `tests/test_rise_tools.py` mirroring
`tests/test_transition_tools.py`: synthetic fixture + spec-contract
suite (head-translation and no-gape guards for x0, frozen ramp, feet
row) + skip-guarded real-artifact regressions.

Release chain: `sources/calibration-v7/specs/*.json` →
`tools/build_sources.py`/`aseprite_build.lua` → `tools/export_assets.py`
(SHA-pinned — never edited; invoked with ABSOLUTE paths) →
`exports/calibration-v7/release.json` via `tools/make_release.py`
(registry append — trailing closers re-emitted exactly; sources +
toolchain committed BEFORE the manifest is generated).

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default
seat) of the rationale + measured evidence + my provisional rubric
verdicts, ≤ 8k total tokens; response redirected to a file and read
with explicit UTF-8; every council numeric claim RECOMPUTED against
pixels/numbers before adoption (v5 precedent: metric inversion +
fabricated precedent; v6 precedent: fabricated "mass increases then
decreases" against a monotone chain).

## Stop conditions

One asset cycle: at most 2 new creature frames (the x0 pair — fewer is
fine; the boundary may be attempted and honestly rejected at spec
stage), one deterministic timeline sheet, optional APNG aids, one
banked verdict with the single-boundary sub-verdict. No lore, no
8-direction sets, no smear frames, no exhaust-state pose, no
terrain/enemies/pack, no runtime integration, no game-two changes, no
Bedrock generation. Timing constants read-only from the pinned commit;
x0 consumes recovery tick 8 only; no new runtime constant consumed (no
`render-reference.json` change expected, none made). Change sets: (0)
re-pins alone per the step-0 protocol (executed: the renderer.rb
sustain-presentation re-baseline at 88fd36d, verification table in its
commit message); (1) this rationale + specs + .aseprite sources +
toolchain + tests, then exports + release.json; (2) timeline sheet +
metrics + verdict. Stop after banking the sprint-7 verdict.
