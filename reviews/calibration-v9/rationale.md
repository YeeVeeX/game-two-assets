# Calibration v9 — cross-facing onset-seam measurement rationale (facing change mid-tween)

Sprint-9 question (the banked v8 next-hypothesis): **cross-facing onset**
— an attack input carrying a facing change during the walk tween — is the
one pose-only seam class still unmeasured at asset level. The onset cut
becomes fN(facing A)→w0(facing B): a simultaneous state-and-facing swap.
Both members are composable from banked frames: walk-DOWN→attack-RIGHT
(**DR**) and walk-RIGHT→attack-DOWN (**RD**). Does the cut read as one
action beginning (turn-and-coil), not an identity break or sprite error;
do the attack poses keep their banked reads while the lunge offset runs
PERPENDICULAR to the residual tween; does the strike keep salience; and
which tile does the perpendicular strike visually bind to? The
committed-tile lag now displaces the arc tile SIDEWAYS from the visual
body — **mis-anchoring, a graded 2D failure mode, replaces v8's binary
un-anchoring.** **This is a measurement sprint: ZERO new frames, zero new
exports, zero tick changes. Every pixel is frozen (all 26 banked export
pins across v0–v3, v5–v7); the deliverables are 2D seam timelines,
machine jump tables with vector displacements, a graded
anchoring-overlap table, and a banked per-class-per-pair verdict.** No
game-two code runs; nothing in `../game-two` changes (read-only
`git show` at the pinned commit).

A FAIL here extends the v8 ENGINE-TERRITORY finding (the v4/v5-banked
EXP-row remedy-attribution class: the failing variable is input timing,
not the pose), recorded as a facing-aware buffering/gating or
facing-lock-during-tween recommendation for the future runtime-replay
integration design — never a rescue frame, never a smear, never a tick
reallocation. Mixed outcomes are expected and first-class.

## Verified reachability and in-tick ordering (game commit `74fb3b8b`, read-only)

All citations verified this session via `git show` at the live pin (the
step-0 mechanical re-pin commit; all five pinned hashes LF-identical,
`attack_timing` re-verified 5/4/8/13 at `74fb3b8b`; the identity drift
from `5850df13` is docs-only — `docs/CHECKPOINT.md` + `drafts/`):

- **World tick order** (`src/game/world.rb` L686–698): first `tick_body`
  for every pack member and human (L686–687), THEN the seat-ordered
  `controller.tick` loop (L692–698). `tick_body`
  (`src/game/creature.rb` L125–126) runs `@walker.tick` unconditionally.
  So within one world tick the tween advances BEFORE input fires
  `face` + `start_attack` — the onset tick draws w0 facing B at the
  post-advance tween position with the −3 offset along B.
- **Controller order** (`src/game/controllers.rb`): within one
  controller tick, `creature.face(dir)` (L52) → step attempt (L56,
  inside `elsif dir != [0, 0]`) → `creature.start_attack if
  down?(input, :attack)` (L64). `face` carries NO moving/attack-state
  guard at the controller level; the step attempt cannot interfere
  mid-tween (`grid_walker.rb` L36: `return false if moving?`).
- **`face`** (`creature.rb` L142–144): `@facing = dir unless
  dir == [0, 0]` — unconditional for any non-zero direction. A held new
  direction re-faces a mid-tween creature on the same tick the attack
  starts.
- **`start_attack`** (`creature.rb` L153–157): refused only for
  dead/staggered/`attack_state != :idle`/exhaust — **no `moving?` guard,
  no facing lock**. `begin_action` (L451–467) sets
  `@attack_state = :windup`.
- **Arc tile** (`creature.rb` L185–186, `front1`): `[[tx + @facing[0],
  ty + @facing[1]]]` — reads LIVE `@facing` at call time, one tile ahead
  of the COMMITTED tile. The modeled class (direction B held from onset
  through the swing) therefore has a stable facing and a stable arc
  tile. Facing drift DURING windup (B released or rolled to C
  mid-windup) is REACHABLE but OUT of scope — recorded as a future
  class, not measured.
- **Tween** (`grid_walker.rb` L90–97): facing-blind — `tick()` eases the
  visual px toward the committed tile with smoothstep `3t² − 2t³`
  regardless of `@facing`; `commit_dash` (L80–88) committed the logical
  tile at step START; no snap on attack or on re-face. During mid-tween
  onset the visual body lags the committed tile along A while the arc
  targets one tile ahead of the committed tile along B ⊥ A — the TRUE
  arc tile sits diagonally off the visual body. Engine fact; this sprint
  measures only its readability consequence.
- **State machine** (`creature.rb` L478–498 class,
  `advance_attack_state`): decrement-then-transition — windup 5, active
  4, recovery 8 (`attack_timing` re-verified 5/4/8/13 at `74fb3b8b`
  via `/kits/striker/...` in `data/balance/combat.json`).

**Consequences, fixed as tick definitions:** "onset at walk tick k" means
the attack input (with direction B held) lands on the world tick whose
`walker.tick` was the k-th tween advance; that same tick draws w0 facing
B at (tween position pos(k) along A) + (−3 along B). The tween then
continues along A under the attack (one advance per tick) until arrival;
no new step can begin once windup starts (`creature.rb` L146–148), so
each lane contains exactly one in-flight step and one attack. Draw
position is a 2-vector: tween scalar along A, tile-centered along B,
plus offset·B̂. **If `face` or `start_attack` gains a
moving/tween/facing-lock guard at a future pin, the cross-facing seam
class becomes unreachable and this sprint's model is fiction — re-verify
at every re-pin (done at `74fb3b8b`: no guard on either).**

## Drawing model (pre-registered; the banked convention, extended one clause)

`attack_state != :idle` draws the banked v7-winner grammar pose for that
state's tick — windup = w0 ×1 + a0 ×4 at −3 ∥ facing; active = k0 ×4 at
+6 ∥ facing; recovery = s0 ×1 + r0 ×6 + x0 ×1 at 0 — **in the creature's
CURRENT facing**. Pre-onset walk ticks draw facing-A frames per the
banked v1 mapping (f0×4/f1×3/f2×3/f3×3 across the 13 step ticks);
pre-walk idle ticks draw idle facing A; post-attack idle draws idle
facing B. Facing is held at B from the onset tick (the modeled input).
Draw position = 2D tween + offset·facing (renderer.rb: `draw_creature`
adds `lunge_offset` along facing to the tween position — pinned in
`render-reference.json`). Recovery-overlap ticks draw s0/r0 on the
still-moving base under this model; the recovery-walk pose-priority
question (carried v5–v8) is NOT adjudicated here — every overlap claim
and every facing-keyed claim is explicitly conditional on the declared
model, and the priority item stays a carried integration finding. The
engine itself draws a pose-less primitive body: the drawing model is the
declared review convention carried from the v4–v8 banked timelines, not
an engine contract.

## Conventions block (evidence-table law, banked v8 council Q1 — fixed before the first number)

- **Window coordinates:** x increases rightward, y increases downward;
  positions are canvas-origin vectors (the 32×32 export canvas's
  top-left) in window coordinates. Every jump-table row reports the
  window delta (dx, dy) AND the semantic delta (dA, dB).
- **Axes per lane:** A = the walk axis, positive in the walk direction
  (DR: A = +y; RD: A = +x). B = the attack facing, positive toward the
  arc tile (DR: B = +x; RD: B = +y). For the degenerate lanes A and B
  coincide (DEGEN-D: down; DEGEN-R: right); dA carries the full
  along-axis delta and dB-perpendicular is 0 by construction.
- **w0 draws at the windup offset** (banked v6/v7 convention,
  machine-checked in both banked sheets): w0 IS windup tick 1, so
  onset rows carry dB = −3 and w0→a0 rows carry dB = 0 (pure tween dA).
- **Squared displacement** = dA² + dB² (exact integer, never a rounded
  float). No scalarized pose+position metric anywhere (banked v6
  correction): pose Δ% (100·XOR/union on export bytes, canvas-aligned —
  position-independent) and displacement are separate axes.
- **Tile names per cross lane:** T0 = the step's origin tile; T1 = the
  committed (landing) tile, one tile along A; TRUE arc tile = T1 + B̂
  (what the hit strikes, `front1` at the committed tile); NEAR tile =
  T0 + B̂ (the wrong-tile candidate the strike visually crosses into
  when the body still sits at T0's A-span). The arc-side grid line is
  the shared T0+B̂/T1+B̂ boundary edge at window B-coordinate 64.
- **Pose names are facing-qualified** in every table: `f0@down`,
  `w0@right`. The onset cut is fN@A → w0@B.

## Onset classes and lane set (pre-registered)

Two facing pairs — **DR** (walk DOWN, attack RIGHT) and **RD** (walk
RIGHT, attack DOWN) — each at the four v8 onset ticks for cross-sprint
comparability, PLUS two degenerate regression lanes. Walk starts at t02
(walk tick k = t01+k); the 13th advance arrives at t14 — arrival is
absolute t14 in every lane. Onset tick t_o; windup t_o..t_o+4, active
t_o+5..t_o+8, recovery t_o+9..t_o+16, idle from t_o+17. REM = 13 −
(t_o − 1). Overlap arithmetic is v8's unchanged.

| lane | onset | REM | arrival t14 lands in | note |
|---|---|---|---|---|
| EARLY | t03 (walk tick 2) | 11 | recovery tick 3 | along-facing EARLY is banked engine-broken; cross-facing at REM 11 measures whether the v8 breakpoint table (4/8/11) holds or TIGHTENS under facing change |
| MID | t06 (walk tick 5) | 8 | active tick 4 | v8's marginal class |
| LATE | t10 (walk tick 9) | 4 | windup tick 5 | v8's clean class |
| CONTROL | t15 (arrival + 1) | 0 | pre-onset | the stationary cross-facing onset — itself UNMEASURED (f3@A at rest → w0@B at −3 along B): the pure state+facing swap with no tween in the frame. The class's cleanest member, NOT a banked regression anchor |
| DEGEN-D | t15 | 0 | pre-onset | same-facing (down/down), identical to v8's CONTROL down lane — the hard toolchain-regression bar |
| DEGEN-R | t15 | 0 | pre-onset | same-facing (right/right), identical to v8's CONTROL right lane |

Ten lanes total (4 classes × 2 pairs + 2 degenerate). Recorded future
classes, NOT measured: facing drift after onset, onset on the
step-initiation tick (REM 13), onset ON the arrival tick (REM 0 at t14),
and pure-turn readability (the walk-A→walk-B lane with no attack).

**Pre-registered explicitly: the banked cross-facing identity reference
(idle↔idle 44.44) BOUNDS nothing here.** A cross-facing cut may
legitimately exceed it — it IS a facing swap; no ceiling bar applies to
the cut itself, and any session that adds one is assuming the answer.
The fN@A↔fN@B context deltas (the engine's own free mid-tween turn,
which `face` permits on any tick) are REPORTED so the onset cut is
judged against the turn the engine already allows — but the pure-turn
lane itself is out of scope. Estimate nothing about the cross-facing
pose deltas; measure them.

## Hand-estimated seam arithmetic (analysis, not evidence — the tool recomputes everything from pinned constants and export bytes)

Tween positions pos(k) = round_half_up(32·smoothstep(k/13)), k=0..13:
0, 1, 2, 4, 7, 11, 14, 18, 21, 25, 28, 30, 31, 32 — per-tick deltas
1,1,2,3,4,3,4,3,4,3,2,1,1 (peak exactly 4 px/tick). Tick t draws
pos(clamp(t−1, 0, 13)) along A. Banked single-facing deltas reused from
the committed v8 metrics (recomputed from bytes, never hand-copied into
the tool): the attack-grammar rows from onset on are single-facing-B
banked numbers (w0→a0 17.25 down / 20.83 right; a0→k0 27.18/31.97;
k0→s0 15.38/21.31; s0→r0 16.18/14.98). The NEW pose numbers this sprint
measures: fN@A↔w0@B per lane (EARLY/MID cut f0; LATE cuts f2; CONTROL
cuts f3) and the context deltas fN@A↔fN@B (N=0..3) + idle↔idle
(must reproduce 44.44).

Key draw vectors (window coords; DR shown as (x=B, y=A); RD mirrors
axes; creature B-baseline = 32, the middle tile of the 3-tile B span):

- **EARLY** (onset t03): f0@A t02 (32,1) | w0@B t03 (29,2) | a0@B
  (29,4)(29,7)(29,11)(29,14) | k0@B t08–t11 (38,18)(38,21)(38,25)(38,28)
  | s0@B t12 (32,30) | r0 t13.. (32,31)(32,32)… arrival t14 on recovery
  tick 3.
- **MID** (onset t06): f0 t05 (32,7) | w0 t06 (29,11) | a0 (29,14)…
  (29,25) | k0 t11–t14 (38,28)(38,30)(38,31)(38,32) — arrival ON active
  tick 4 | s0 t15 (32,32).
- **LATE** (onset t10): f2 t09 (32,21) | w0 t10 (29,25) | a0 (29,28)
  (29,30)(29,31)(29,32) — arrival on windup tick 5 | k0 t15–t18
  (38,32)×4 | s0 t19 (32,32).
- **CONTROL** (onset t15): f3 t14 (32,32) arrival | w0 t15 (29,32) | a0
  ×4 (29,32) | k0 t20–t23 (38,32)×4 | s0 t24 (32,32).
- **DEGEN-D/R**: the v8 CONTROL lanes exactly — 1D positions
  pos + offset along the single shared axis.

Displacement vectors (dA, dB) and exact squared magnitudes, the
pre-registered salience comparison:

| event | EARLY | MID | LATE | CONTROL |
|---|---|---|---|---|
| onset fN→w0 | (+1,−3) sq 10 | (+4,−3) sq 25 | (+4,−3) sq 25 | (0,−3) sq 9 |
| release a0→k0 | (+4,+9) **sq 97** | (+3,+9) **sq 90** | (0,+9) **sq 81** | (0,+9) **sq 81** |
| k0→s0 | (+2,−6) sq 40 | (0,−6) sq 36 | (0,−6) sq 36 | (0,−6) sq 36 |
| max other (holds/walk) | sq ≤ 16 | sq ≤ 16 | sq ≤ 16 | sq ≤ 1 |

The release strictly dominates the squared-displacement axis in every
lane by construction arithmetic (97/90/81/81 vs in-lane maxima 40/36 —
the brief's theoretical ≤ 52 ceiling for k0→s0 refines to 40 actual in
EARLY, 36 elsewhere). The POSE axis is genuinely open: the cross-facing
onset cut fN@A→w0@B is unmeasured and MAY exceed the release pose delta
(27.18 RD / 31.97 DR) — that is a measurement outcome, not a toolchain
failure (semantics fixed under "pass bars" below). A cross-lane onset
row is also a DIAGONAL jump — the v8 scalar onset deltas (−2/+1/+1/−3)
were the SUM of tween and offset on one axis; cross-facing splits them
into components (peak (+4,−3) at MID/LATE), disclosed now so the tables
read correctly.

## Anchoring-overlap derivation (pre-registered exactly; reported per lane per active tick, never gated)

Banked k0 bboxes (canvas coords [x0,y0,x1,y1], from banked bytes,
gate-verified): down [8,6,23,27]; right [7,7,28,27]. Crossing pixels =
opaque k0 pixels with canvas-B ≥ 26 (window-B = 38 + canvas-B ≥ 64 at
the active offset): k0-right carries 12 crossing px at canvas-A rows
{10..15}; k0-down carries 12 crossing px at canvas-A cols
{10,11,12,19,20,21} (the two jaw halves — machine-recomputed from
bytes). The arc-side grid line sits at window-B = 64.

Per active tick the tool reports:

1. **B-crossing depth (px past the grid line):** leading edge − 63 =
   (38 + bboxB1) − 63. Cross lanes: constant — DR (k0-right, bboxB1=28)
   = **3px**; RD (k0-down, bboxB1=27) = **2px** — the crossing always
   exists because the B-offset is tween-independent, and the constants
   equal the banked v4 anchoring values (2px down / 3px right), an
   independent cross-check of the derivation. Degenerate lanes: depth =
   pos + 6 + bboxB1 − 63 (the v8 formula; 2/3px at arrival).
2. **Body A-extent** [pos + bboxA0, pos + bboxA1] and its overlap (px)
   with the TRUE arc tile's A-span [32,63] and the NEAR tile's A-span
   [0,31].
3. **Crossing-pixel bind counts:** how many of the 12 crossing pixels
   land in the TRUE arc tile vs the NEAR tile (window-A = pos +
   canvas-A, split at 32).

Hand tables (recompute exactly in the tool; ≈ marks nothing — these are
exact from the banked bboxes and plan positions):

DR (A-extent = pos+[7,27], 21px body span; crossing rows pos+{10..15}):

| active tick pos | body∩TRUE / body∩NEAR (px) | crossing px TRUE/NEAR |
|---|---|---|
| EARLY 18 | 14 / 7 | 2 / 4 |
| EARLY 21 | 17 / 4 | 5 / 1 |
| EARLY 25 | 21 / 0 | 6 / 0 |
| EARLY 28 | 21 / 0 | 6 / 0 |
| MID 28,30,31,32 | 21 / 0 ×4 | 6 / 0 ×4 |
| LATE + CONTROL 32 | 21 / 0 | 6 / 0 |

RD (A-extent = pos+[8,23], 16px body span; crossing cols
pos+{10,11,12,19,20,21}):

| active tick pos | body∩TRUE / body∩NEAR (px) | crossing px TRUE/NEAR |
|---|---|---|
| EARLY 18 | 10 / 6 | 3 / 3 **(split)** |
| EARLY 21 | 13 / 3 | 5 / 1 |
| EARLY 25 | 16 / 0 | 6 / 0 |
| EARLY 28 | 16 / 0 | 6 / 0 |
| MID 28,30,31,32 | 16 / 0 ×4 | 6 / 0 ×4 |
| LATE + CONTROL 32 | 16 / 0 | 6 / 0 |

Reading (hypothesis space, not conclusions): cross-facing, the strike
ALWAYS crosses the arc-side grid line (unlike v8's EARLY, whose leading
edge never reached it along-facing) — but at EARLY the crossing pixels
enter the WRONG tile or straddle both (RD's first active tick splits its
jaw halves 3/3 across NEAR and TRUE), and the bind migrates to the TRUE
tile as the tween closes. Whether a wrong-tile or split bind reads as
mis-anchoring at 1x is exactly what the rubric judges with these
numbers. **No pass/fail px bar is invented for anchoring; the table is
reported and the rubric line judges bind quality per class.**

## KB re-grounding (re-verified in the vault this session, 2026-08-18)

- `game-research/pixel-art-pygame-and-2d-engine-reference.md` §7.2/§8:
  anticipation 100–200 ms hold, strike ~50 ms, follow-through ~150 ms —
  the banked v4 strike-dominance doctrine the salience bar reuses.
  Unchanged, carried from v8.
- `game-research/technical-drawing-for-game-art.md` §8: the standard 2D
  pattern is EXCLUSIVE animation states — the attack pose replaces the
  walk wholesale, and facing selects a sprite row per state. This
  grounds the declared drawing model (attack pose in CURRENT facing
  wins) and frames the compound under test: this engine lets the walk
  TWEEN continue under a re-faced attack — a compound the standard
  pattern never renders.
- **Corpus gap, disclosed (the v7/v8 disclosure class):** queried
  `hub kb query --domain game-research` for turn-cancel / facing-buffer
  / attack-input-buffering-under-turn doctrine this session — the top
  hits are lifecycle/game-feel generalities, UI/UX input-verb mapping,
  and the exclusive-state pattern; **nothing prescribes whether a
  mid-tween facing-change attack should cut, defer, or lock facing.**
  The engine-territory FAIL routing is a recommendation space, not
  settled convention.

## Pass bars (fixed now, before any artifact exists)

Machine-checkable (`tools/cross_seam_metrics.py --check`, exit nonzero
on any failure). Failures are grouped and named on output:
**INTEGRITY** failures mean the sprint's toolchain or frozen-state law
is broken — the sprint stops until fixed; **MEASUREMENT** failures are
banked evidence feeding the affected lane's sub-verdict (the decision
rule below). The split is fixed here, before any number exists, so a
red measurement bar cannot be re-spun post-hoc.

1. **Zero new exports (INTEGRITY):** `exports/` contains exactly the 26
   pinned PNGs of the seven banked releases (v0–v3, v5–v7 — v0 banks 6
   idles across lanes a/b/c), every file SHA-256-verified against its
   release.json pin; no `exports/calibration-v8/` AND no
   `exports/calibration-v9/` exist; the `make_release.py` registry and
   `tools/export_assets.py` bytes untouched.
2. **2D seam jump tables (INTEGRITY for structure):** per lane per
   facing-pair — pose Δ% (100·XOR/union on export bytes) AND position
   Δ(dA,dB) (+ window (dx,dy) + exact integer squared magnitude) for
   EVERY consecutive tick pair from onset−2 through onset+10 (EARLY:
   onset+12, so every table ends on the s0→r0 row and EARLY covers its
   recovery overlap), positions from independently recomputed
   smoothstep + offset·facing.
3. **Degenerate regression (INTEGRITY, hard):** DEGEN-D/DEGEN-R jump
   tables machine-equal to the committed
   `reviews/calibration-v8/seam-metrics.json` CONTROL rows — pose names,
   pose Δ%, AND position exactly (my along-axis dA == the v8
   position_delta_px scalar; my perpendicular component == 0), row for
   row. This is the hard toolchain-regression bar: the 2D machinery
   degenerated to along-facing must reproduce v8's numbers.
4. **Release-salience (MEASUREMENT):** per lane the a0→k0 row is
   STRICTLY the largest pose delta AND STRICTLY the largest squared
   displacement among the lane's rows — both axes separately, no
   combined metric. The squared axis is expected to pass by the
   arithmetic above; the pose axis is genuinely open cross-facing (the
   onset cut may exceed the release) — a red here is evidence for
   rubric line 3 of that lane, routed by the decision rule.
5. **Anchoring-overlap table (report-only, never a failure):** per lane
   per active tick — B-crossing depth, body A-overlap with TRUE and
   NEAR tiles, crossing-pixel bind counts, derived exactly as
   pre-registered above.
6. **Cross-facing context deltas (INTEGRITY):** fN@A↔fN@B for N=0..3
   reported, and idle↔idle MUST reproduce the banked 44.44 exactly.
7. **Tick math exact (INTEGRITY):** per lane — grammar composition
   w0×1+a0×4 / k0×4 / s0×1+r0×6+x0×1; offsets along B only from onset
   (−3 windup / +6 active / 0 recovery; dA never carries offset); walk
   frames facing A before onset per the banked mapping; attack poses
   facing B from onset; per-tick tween deltas along A exactly
   1,1,2,3,4,3,4,3,4,3,2,1,1; REM 11/8/4/0/0/0 and arrival-phase
   assertions per class (rec 3 / act 4 / wind 5 / pre-onset ×3); no
   tick added, consumed, or reallocated; the 6-tick r0-hold floor
   untouched by construction and asserted.
8. **Determinism + purity (INTEGRITY):** sheet + metrics + any APNG
   byte-identical across two independent in-process builds and equal to
   committed bytes; every creature cell dual-verified (2D region
   reconstruction + direct export-byte equality at the computed integer
   draw vector); banked sheets v0–v8 regenerate byte-identical under
   the extended toolchain (existing regression suites).
9. **In-window by construction (INTEGRITY):** every opaque pixel
   in-bounds proven from the plan + the [2,2,29,29] contract bounds —
   min/max draw extents per lane asserted against the window dims (no
   reliance on put() clipping); both the visually-struck (NEAR) tile
   and the TRUE arc tile inside every lane window with their grid
   lines, by window construction (cross windows: 2 A-tiles × 3 B-tiles
   [back | creature | arc]; degenerate windows: the v8 3-tile axis
   window).
10. **Coverage (INTEGRITY):** `tools/` coverage ≥ 80 under
    `bin/full_gate.py`.

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone
palettes, both pairs; every claim is sheet-scope — per-tick legibility
and single-tick recognizability under identical pinned timing, never
temporal fusion at 60 tps, never "reads at combat speed"):

1. **Per class per pair, the fN@A→w0@B cut reads as ONE action
   beginning** — the creature turning INTO the coil — not as an
   identity break, a sprite swap error, or a second creature; judged
   per tick on the lane bands and 2X onset strips, against the measured
   magnitude, the 44.44 identity reference, the fN@A↔fN@B turn context,
   and the degenerate baseline.
2. **The attack poses riding the perpendicular tween keep their banked
   reads** (w0 sink, a0 telegraph, k0 strike, settle family per the
   declared model): a sideways sub-tile glide beneath a B-facing pose
   must not read as knockback, ice-slide, or error.
3. **The strike keeps salience:** on every lane the release remains the
   sharpest single-tick event at native 1x, the machine table (bar 4)
   agreeing with the native read.
4. **Anchoring:** the perpendicular strike visually binds to a tile —
   judged per class with the graded overlap table: TRUE-arc bind
   (pass), WRONG-tile bind (mis-anchor — name the tile and the px), or
   no bind; the v8 anchoring doctrine (the displacement has a
   destination) is the yardstick.
5. **Degenerate lanes read exactly as v8's CONTROL** (no regression)
   and identity law holds sheet-wide (byte-frozen frames at computed
   positions, frozen ramp, feet/anchor law within the moving cell).

**Decision rule (fixed):** per-class-per-pair sub-verdicts, independent
— 8 sub-verdicts (EARLY/MID/LATE/CONTROL × DR/RD) + the degenerate
regression gate (bar 3 + rubric line 5, sheet-wide). A class+pair
PASSES only if rubric lines 1–4 pass for it AND line 5 holds
sheet-wide. PASS ⇒ the direct cross-facing cut is banked as the answer
for that class+pair. FAIL ⇒ banked as an ENGINE-TERRITORY finding
naming the failing ticks, magnitudes, and mis-anchor px, extending the
v8 recommendation (facing-aware onset buffering/gating, or facing-lock
during tween — game-two decisions for after the cycle closes, never
implemented from here, never compensated with pixels). Mixed outcomes
are expected and first-class. No rescue edits, no new frames, no tick
changes, no smears, no second drawing model, no new ceiling bars.

Scope discipline carried from v4–v8: no temporal/fusion claims (60 tps
questions live in the consolidated runtime item, whose x0
banking-reversal condition is untouched); the 6-tick r0-hold floor and
every banked stop-condition stand; no facing-drift-after-onset
measurement, no pure-turn lane, no recovery-walk adjudication, no
step-initiation-tick or arrival-tick onset variants, no 8-direction
sets, no terrain, enemies, pack, lore, or Bedrock generation; AD-C1/
AD-C2 scope triggers (effect/feedback frames) are NOT met this sprint —
they do not gate; `docs/research/itexo-visual-grammar-2019.md` is
era-tagged continuity reference only (paths cited, nothing copied).

## Toolchain plan

Two new tools; banked helpers imported unmodified (`draw_floor_tile`,
sprite loaders, `smoothstep`/`round_half_up`/`walk_frame_index` +
`tween_position`, the seam-extended glyph font + `draw_text`, APNG
encoder + delays, `pair_stats`/`frame_stats`/`load_opaque`, `TICK_MS`,
`pose_filename`/`POSE_DIRS`/`default_dirs`):

- `tools/make_cross_seam_timeline.py` (new, tested): the ten-lane 2D
  tick plan (a pure function of the pinned constants + the
  pre-registered onset ticks + the pair axes) — per pair section:
  RULER + lane rows (Z1 then Z2, 16 columns t_o−2..t_o+13 per lane)
  over the lane's uniform window (cross lanes: 2 A-tiles × 3 B-tiles
  [back | creature | arc], sized so every opaque pixel is in-bounds by
  construction and both candidate strike tiles are visible with grid
  lines; degenerate lanes: the v8 3-tile axis window); 2X ONSET strips
  (onset−1 | onset | onset+1 per lane, cropped to the 2×2-tile
  [back|creature]×[T0|T1] sub-window — the onset event's extent never
  reaches the arc column, and the crop is recorded in the manifest);
  2X RELEASE strips (onset+4 | onset+5 per lane, FULL window — the arc
  tiles must be visible at the release); FILM continuity rows (the
  banked eleven-column strip, both facings, Z1+Z2); a machine-readable
  cell manifest (section, pair, lane, zone, tick, phase, pose,
  pose_facing, window spec, draw vector, scale, rect); optional APNG
  aids (`cross-lanes-<pair>.apng`: the four cross lanes side by side,
  full t00..t33 at exact 1/60 s tick delay, 4x NN, banked encoder —
  the degenerate lanes are v8's CONTROL, already animated in the
  banked v8 aids).
- `tools/cross_seam_metrics.py` (new, tested): 2D jump tables,
  degenerate regression against the committed v8 metrics,
  squared-magnitude salience, the anchoring-overlap table, context
  deltas (incl. the 44.44 reproduction bar), tick math, in-bounds
  proof, export pins + zero-new-exports (reusing the banked v8 checker
  + the calibration-v9 guard), determinism, purity, `--check` enforcing
  bars 1–10 with the INTEGRITY/MEASUREMENT split named per failure.

Tests in `tests/test_cross_seam_tools.py` mirroring
`tests/test_seam_tools.py`: synthetic fixture with per-pose rects
crafted so the salience mechanism exercises its passing direction on
synthetic bytes (a0/k0 disjoint; identical rects across facings so
cross-facing context deltas are near-zero on synthetic bytes — the
44.44 bar and the degenerate bar are then exercised in their FAILING
direction on synthetic bytes, v8's control-regression test pattern);
plan/sheet/validator suites; skip-guarded real-artifact regressions
that assert committed-artifact consistency without assuming unmeasured
values. No release chain (no exports); `tools/export_assets.py` bytes
untouchable regardless (SHA-pinned by every banked release).

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default
seat) of the rationale + measured evidence + provisional rubric
verdicts, ≤ 8k total tokens, single call (a truncation continuation
within the same budget is acceptable — v8 precedent); response
redirected to a file and read with explicit UTF-8; every council
numeric claim RECOMPUTED against pixels/numbers before adoption
(v5–v8 precedent: inverted metrics, fabricated precision, premise
errors from unstated conventions).

## Stop conditions

One measurement cycle: zero new creature frames, zero new exports, one
deterministic cross-facing sheet (byte-identical on regeneration), one
metrics JSON, optional APNG aids, one banked verdict with 8
per-class-per-pair sub-verdicts + the degenerate gate and the FULL v8
standing findings list carried unmodified (including the
onset-anchoring geometry entry and the retreat-cue inversion) plus the
cross-facing findings and any breakpoint-table update. No lore, no
8-direction sets, no terrain/enemies/pack, no runtime integration, no
game-two changes, no Bedrock generation. Timing constants read-only
from the pinned commit; no new runtime constant consumed. Change sets:
(0) re-pins alone per the step-0 protocol (executed: mechanical
identity re-pin to `74fb3b8b`, attack_timing re-verified, committed
alone); (1) this rationale + toolchain + tests; (2) sheet + metrics
(+ APNG aids) + verdict after the verdict. Push to origin after
banking (pre-push = full gauntlet + LFS). Stop after banking the
sprint-9 verdict — the runtime-replay integration design stays parked
until the game cycle closes, whichever way the sub-verdicts land.
