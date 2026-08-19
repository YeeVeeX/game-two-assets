# Calibration v10 — pure-turn lane measurement rationale (walk-A→walk-B mid-tween, no attack)

Sprint-10 question (the banked v9 next-hypothesis and council Q2's explicit
ask): does a bare mid-tween facing swap read as a TURN at 1x? Every v9
cross-facing judgment leaned on free-turn BYTE PAIRS as magnitude calibration
only — the rendered pure-turn lane was never built. This sprint renders that
yardstick: walk-A→walk-B mid-tween with NO attack, the premise under v9's L1
PASSes and under the buffering recommendation's "render the turn first"
clause. **This is a measurement sprint: ZERO new frames, zero new exports,
zero tick changes, zero releases. Every pixel is frozen (all 26 banked export
pins across v0–v3, v5–v7); the deliverables are 2D turn timelines, machine
jump tables with vector displacements, a body-tile binding table, and a
banked per-class-per-pair verdict.** No game-two code runs; nothing in
`../game-two` changes (read-only `git show` at the pinned commit).

A FAIL here extends the banked v8/v9 ENGINE-TERRITORY findings (the v4/v5
EXP-row remedy-attribution class: the failing variable is input timing, never
the pose), refining the facing-aware-buffering / facing-lock recommendation
with pure-turn evidence — never a rescue frame, never a smear, never a tick
reallocation. Mixed outcomes are expected and first-class.

## Verified reachability and in-tick ordering (game commit `fd006f91`, read-only)

All citations verified this session via `git show` at the live pin (step-0
mechanical re-pin commit `5fd7efd`; all five pinned hashes LF-identical at
`fd006f91`, `attack_timing` re-verified 5/4/8/13 via `/kits/striker/...` in
`data/balance/combat.json`; the stale `game_branch` field was corrected
`junior-tibia`→`main` in the same re-pin — provenance-only, not gate-checked).

- **World tick order** (`src/game/world.rb` L686–698): `tick_body` for every
  pack member and human (L686–687), THEN the seat-ordered `controller.tick`
  loop (L692–698). `tick_body` (`src/game/creature.rb` L124–126) runs
  `@walker.tick` unconditionally. Within one world tick the tween advances
  BEFORE input re-faces the creature — the turn tick draws the post-advance
  tween position in the NEW facing.
- **Controller order** (`src/game/controllers.rb`): within one controller
  tick, `dir = held_direction(input)` (L51) → `creature.face(dir)` (L52,
  unconditional on the non-seized move path) → step attempt (L56, inside
  `elsif dir != [0, 0]`). `held_direction` (L85–89) resolves held keys to a
  direction vector. The modeled input holds exactly one direction at a time
  (A released on the tick B is pressed), so no diagonal ever forms.
- **`face`** (`creature.rb` L142–144): `@facing = dir unless dir == [0, 0]` —
  a held new direction re-faces a mid-tween creature the same tick, with no
  guard and no interaction with the walker.
- **Mid-tween step rejection** (`grid_walker.rb` L32, L35–39): `moving? =
  @tween_left.positive?`; `step` → `return false if moving?` (L36). Holding B
  mid-tween re-faces every tick but commits NO step until the tween ends.
  `creature.step` (L146–148) adds dead/staggered/windup/active gates — none
  bind here (no attack anywhere in the lane).
- **Facing-blind tween, no snap** (`grid_walker.rb` L90–97): `tick()` eases
  the visual px toward the committed tile with smoothstep `3t² − 2t³`
  regardless of `@facing`; `commit_dash` (L80–88) committed the logical tile
  at step START; nothing in `face` or the walker snaps or retargets on
  re-face.
- **THE V10-SPECIFIC FACT — what a mid-tween re-face draws** (`renderer.rb`):
  `draw_creature` draws the body rect at the tween position (L490) and
  `draw_facing_notch` (L500, L520–531) reads `c.facing` LIVE at every draw —
  the facing marker flips on the very next rendered frame after `face(B)`.
  `lunge_offset` (L536–544) returns `[0, 0]` for `attack_state == :idle`, so
  a pure walk carries NO offset: draw position = tween position exactly.
  Nothing else is facing-keyed for a non-attacking creature. **The engine
  draws no walk frames at all** (flat rect + notch): walk-frame selection is
  the asset repo's declared review convention (v1 mapping, carried v2–v9),
  not an engine contract. The engine facts that ARE binding: the drawn facing
  swaps immediately mid-tween, the position is facing-independent, and the
  step restarts only at arrival.
- **Arrival handoff (engine-exact, the risk-1 item):** step A commits at
  t01's controller tick; its 13 advances land at t02..t14 `tick_body`s
  (t14's advance takes `tween_left` 1→0, px = 32). At t14's controller,
  `moving?` is FALSE, so with B held the B step COMMITS at t14 — tile
  commits along B, `tween_total = tween_left = 13`, but `@px` is unchanged
  until the next `tick_body` (L80–88 sets no position). t14 therefore draws
  the creature AT the A-arrival position; the first B advance lands at t15's
  `tick_body` (1 px along B). CONTROL (B pressed at t15, A released before
  t14's controller): t14 draws the arrival with no commit; t15's controller
  faces B and commits; t15 draws standing at T1 in facing B; the first B
  advance lands at t16.

**Unreachability pivot branch (pre-registered per risk 1): CLOSED.** The
branch — "if the renderer only read facing at step start, or a re-face
snapped/locked the tween, the strafe segment would be unreachable and the
sprint would pivot to CONTROL-class turn points plus the stationary free-turn
yardstick" — does not trigger: the notch reads live facing every draw
(L520–531), `face` carries no guard (L142–144), and the tween is
facing-blind (L90–97). The full lane set is reachable at `fd006f91`. **If
`face` gains a moving/tween guard or the renderer gains facing-at-step-start
caching at a future pin, this model is fiction — re-verify at every re-pin.**

## Drawing model (pre-registered; the banked convention, extended one clause)

Carried v4–v9 convention: walk ticks draw the banked v1 walk mapping —
`walk_frame_index` distributes f0×4 / f1×3 / f2×3 / f3×3 across the 13 step
ticks (walk tick k = the tick whose `tick_body` did the k-th advance); the
step-commit tick draws the STANDING pose (banked precedent: t01 draws idle —
the v9 jump tables' t01→t02 idle→f0 row); f3 is the idle byte-copy (banked
release note). **V10 extension clause (one sentence): a mid-tween re-face
swaps the FACING of the drawn walk frame from the turn tick on; the frame
INDEX continues from step progress (the same v1 mapping over the A step's
advances), and the B step's frames restart at f0 under the same mapping.**
Basis: facing selects the sprite row, state progress selects the frame — the
KB exclusive-state pattern (technical-drawing-for-game-art §8, carried from
v9's grounding) — and the engine's only facing-keyed visual (the notch)
swaps immediately at the pin while position continues, which this clause
mirrors exactly. Step progress (not global tick, not a facing-scoped
counter) drives the index: the banked mapping is DEFINED over the step's 13
advances, and no banked sheet has ever keyed frames to anything else. The
declared model is a review convention; every facing-keyed claim in this
sprint is conditional on it, exactly as v4–v9 banked their drawing models.

Draw position = 2D tween, NO offset anywhere (no attack ⇒ `lunge_offset`
[0,0] at the pin — engine fact above). Post-walk standing draws idle in the
current facing.

## Conventions block (evidence-table law, carried v8 council Q1 / v9 Q6 — fixed before the first number)

- **Window coordinates:** x right, y down, canvas-origin (the 32×32 export
  canvas's top-left) in window coordinates. Every jump-table row reports the
  window delta (dx, dy) AND the semantic delta (dA, dB).
- **Axes per lane:** A = the FIRST walk axis, positive in the walk direction
  (DR: A = +y; RD: A = +x). B = the SECOND walk direction — the facing the
  creature turns TO (DR: B = +x; RD: B = +y). Degenerate lanes: A and B
  coincide (both steps along A); dA carries the full along-axis delta, dB = 0
  by construction.
- **Pose Δ%** = 100·XOR/union on canvas-aligned export bytes in SPRITE-LOCAL
  space — position-independent; the draw vector never enters the comparison
  (v9 council Q6 duty, restated). 0.0 only for identical pose AND facing.
- **Squared displacement** = dA² + dB², exact integer. No scalarized
  pose+position metric anywhere (banked v6 correction).
- **Tile names per turn lane:** T0 = the A step's origin tile; T1 = the
  committed/landing tile of step A (one tile along A); T2 = T1 + B̂ (the B
  step's landing). The T0/T1 boundary is the grid line the strafing body
  crosses; window tile spans are declared in the plan and asserted
  in-window.
- **Pose names are facing-qualified** in every table: `f0@down`, `f1@right`.
  The turn cut is pose(t_turn−1)@A → pose(t_turn)@B.
- **REM** = 13 − (t_turn − 1): tween advances remaining AFTER the turn
  tick's own advance (v9's formula unchanged). The strafe SEGMENT (facing B
  over residual A-tween) spans the turn tick through arrival: REM + 1 drawn
  ticks.

## Lane set and tick definitions (pre-registered)

Two facing pairs — **DR** (walk DOWN, turn RIGHT) and **RD** (walk RIGHT,
turn DOWN) — each at the four banked onset ticks reused as TURN ticks, plus
two degenerate uncut lanes. Walk A commits at t01 (t00–t01 idle_pre @A, the
banked IDLE_PRE_TICKS = 2); advances t02..t14; arrival absolute t14 in every
lane. "Turn at tick t" = direction B replaces direction A at t's controller
tick (A released, B pressed — held from there through the B step; B released
after the B step's last advance so no third step commits).

| lane | turn tick | REM | strafe ticks (facing B over A-tween) | B commit | first B advance | note |
|---|---|---|---|---|---|---|
| EARLY | t03 (walk tick 2) | 11 | t03..t14 (12 drawn, ≈183 ms of residual advances) | t14 | t15 | the stress class; v9's wrong-tile precedent transposes here |
| MID | t06 (walk tick 5) | 8 | t06..t14 (9) | t14 | t15 | **turn lands ON the f0→f1 frame boundary (k4→k5): the cut is a COMPOUND f0@A→f1@B — the sprint's one novel pose number** |
| LATE | t10 (walk tick 9) | 4 | t10..t14 (5) | t14 | t15 | the clean class |
| CONTROL | t15 (arrival+1) | 0 | none (stand tick t15 idle@B; first B advance t16) | t15 | t16 | the ordinary tile-boundary direction change |
| DEGEN-D | — | — | — | t14 (step 2 along A) | t15 | uncut two-step walk DOWN — every same-facing row's uncut twin |
| DEGEN-R | — | — | — | t14 | t15 | uncut two-step walk RIGHT |

Ten lanes (4 classes × 2 pairs + 2 degenerate). Recorded future classes, NOT
measured: turn on the step-initiation tick (t01/t02 class), turn ON the
arrival tick (t14 — the no-stand seamless wrap with the facing swap riding
the wrap cut), multi-turn chatter (A→B→A mid-tween), 8-direction turns.

**Tick tables (the full plan; DR draw = (b_px, a_px), RD mirrors to
(a_px, b_px); pos(k) = round_half_up(32·smoothstep(k/13)) = 0,1,2,4,7,11,
14,18,21,25,28,30,31,32; per-tick deltas 1,1,2,3,4,3,4,3,4,3,2,1,1):**

| tick | EARLY | MID | LATE | CONTROL | DEGEN | a/b px |
|---|---|---|---|---|---|---|
| t01 | idle@A | idle@A | idle@A | idle@A | idle@A | a 0 |
| t02 | f0@A | f0@A | f0@A | f0@A | f0@A | a 1 |
| t03 | **f0@B** | f0@A | f0@A | f0@A | f0@A | a 2 |
| t04 | f0@B | f0@A | f0@A | f0@A | f0@A | a 4 |
| t05 | f0@B | f0@A | f0@A | f0@A | f0@A | a 7 |
| t06 | f1@B | **f1@B** | f1@A | f1@A | f1@A | a 11 |
| t07 | f1@B | f1@B | f1@A | f1@A | f1@A | a 14 |
| t08 | f1@B | f1@B | f1@A | f1@A | f1@A | a 18 |
| t09 | f2@B | f2@B | f2@A | f2@A | f2@A | a 21 |
| t10 | f2@B | f2@B | **f2@B** | f2@A | f2@A | a 25 |
| t11 | f2@B | f2@B | f2@B | f2@A | f2@A | a 28 |
| t12 | f3@B | f3@B | f3@B | f3@A | f3@A | a 30 |
| t13 | f3@B | f3@B | f3@B | f3@A | f3@A | a 31 |
| t14 | f3@B | f3@B | f3@B | f3@A | f3@A | a 32 (arrival; B/step-2 commits) |
| t15 | f0@B | f0@B | f0@B | **idle@B** | f0@A | b 1 (CONTROL b 0; DEGEN a 33) |
| t16 | f0@B | f0@B | f0@B | f0@B | f0@A | b 2 (CONTROL b 1; DEGEN a 34) |
| t17 | f0@B | f0@B | f0@B | f0@B | f0@A | b 4 (CONTROL b 2; DEGEN a 36) |
| t18 | f0@B | f0@B | f0@B | f0@B | f0@A | b 7 (CONTROL b 4; DEGEN a 39) |
| t19 | f1@B | f1@B | f1@B | f0@B | f1@A | b 11 (CONTROL b 7; DEGEN a 43) |
| t20 | f1@B | f1@B | f1@B | f1@B | f1@A | b 14 (CONTROL b 11; DEGEN a 46) |
| t21 | f1@B | f1@B | f1@B | f1@B | f1@A | b 18 (CONTROL b 14; DEGEN a 50) |

(Bold = the turn cut's arrival tick per lane. The plan generates t00..t29 —
B/step-2 advances complete at t27, CONTROL t28; direction released after the
last advance; idle_post follows. Sheet and jump tables cover t01..t21: the
commit row, the full A step, the wrap, and 7 B-walk ticks including the
post-wrap f0→f1 boundary. During the strafe a_px keeps advancing per the
tween deltas and b_px = 0; from the wrap on, a_px = 32 and b_px advances per
the same deltas; DEGEN carries a single along-axis total 0..32, 33..64.)

**Turn-cut identities (forced by the mapping — an INTEGRITY self-check, not
a finding):** EARLY cuts f0@A→f0@B (frame-identical); LATE cuts f2@A→f2@B
(frame-identical); CONTROL cuts f3@A→idle@B (f3 IS the idle byte-copy, so
byte-frame-identical); MID cuts f0@A→f1@B — NOT frame-identical, the one
novel pose number this sprint measures (two numbers: DR f0@down→f1@right and
RD f0@right→f1@down). The turn ticks were fixed by v8/v9 comparability
BEFORE this consequence was derived; that MID lands on a frame boundary is a
property of the banked mapping, disclosed now: MID's cut is a
turn+frame-advance COMPOUND, exactly one mapping-step worse than a pure
swap, and its number is measured, never assumed.

**Turn-cut displacement contexts (dA, dB at the cut):** EARLY (1, 0); MID
(4, 0) — the swap rides a peak-velocity tick; LATE (4, 0); CONTROL (0, 0) —
the stationary swap. The four cuts render the SAME facing swap at four
different displacements: the swap-under-displacement compound is the novel
perceptual content the stationary CONTEXT row cannot carry.

## Anchor map (machine-equal or it's a plan bug — the risk-2 discipline)

Most v10 rows are machine-derivable from banked numbers. Every equality
below is an INTEGRITY bar: a near-miss is a derivation bug, and the sprint
stops. The NOVEL content is exactly: MID's two compound-cut numbers, the
swap-under-displacement read, the strafe segment, the arrival restart, and
the tile binding — nothing else is new.

1. **Free-turn context rows** (fN@A↔fN@B for N=0..3 + idle↔idle, both
   computed fresh from bytes): == the banked
   `reviews/calibration-v9/cross-seam-metrics.json` `context_deltas` on all
   four fields (popping_pct / recolored_px / silhouette_changed_px /
   union_px): f0 53.64/63/199/371, f1 45.00/64/162/360, f2 36.45/55/121/332,
   f3 44.44/64/156/351, idle 44.44/64/156/351.
2. **Frame-identical turn cuts == their own context pair:** EARLY == f0
   context (53.64), LATE == f2 context (36.45), CONTROL == f3 context ==
   idle context (44.44), both pairs. MID is asserted NOT frame-identical and
   its cut is reported as measured.
3. **f3/idle byte-copy law:** the f3@F opaque pixel map == idle@F pixel map
   exactly, both facings (basis of anchor 2's CONTROL equality and anchor
   4's wrap equality; the banked v1 release note made law).
4. **Wrap rows** (f3@B→f0@B at t14→t15, moving lanes; DEGEN f3@A→f0@A):
   popping == the banked `reviews/calibration-v1/motion-metrics.json` pair
   `f3->f0` for the row's facing — right 10.29, down 15.87 (also equal to
   v9's banked idle→f0 rows, 10.29/15.87 — two independent banked sources
   agree by the byte-copy law).
5. **CONTROL restart row** (idle@B→f0@B at t15→t16): == the same banked
   numbers (10.29 DR / 15.87 RD) by the byte-copy law.
6. **Every same-facing walk-cycle boundary row** == the banked v1
   motion-metrics pair for its facing: down f0→f1 19.64 / f1→f2 19.00 /
   f2→f3 15.87; right f0→f1 22.09 / f1→f2 22.09 / f2→f3 10.29. (v9's banked
   spot rows — f1→f2 19.0@down in DR/LATE, 22.09@right in RD/LATE, idle→f0
   15.87/10.29 in the EARLY tables — agree; cited as the cross-check.)
   Same-pose-same-facing rows are 0.0 by convention.
7. **Cross-lane consistency web:** every repetition of the same
   (pose_from@facing → pose_to@facing) pair anywhere in the v10 tables
   carries the identical popping_pct (pose deltas are pure byte-pair
   functions — position never enters).
8. **DEGEN prefix equality:** DEGEN rows t01→t02 .. t13→t14 machine-equal
   the same pair's CONTROL rows (both are the identical uncut walk @A to
   arrival), row for row — poses, deltas, dA, dB=0.
9. **Tween-delta law:** per-tick displacement along the active axis follows
   1,1,2,3,4,3,4,3,4,3,2,1,1 exactly; wrap row (0,1) sq 1 for moving lanes,
   (0,0) then (0,1) for CONTROL's stand+restart; DEGEN wrap (1,0) sq 1
   along-axis. Max any-row squared = 16 (the peak-velocity tick).

## Body-tile binding derivation (pre-registered exactly; report-only, never a machine failure)

The v9 EARLY finding was arc-side wrong-tile binding; the pure turn has no
arc — the binding question transposes to the BODY: from t01 the engine's
committed tile is T1 while the visual body trails in T0's span (the standing
Tibia lag), and after the turn the body faces B while still traveling A —
which tile does it visually claim? Per strafe tick the tool reports: body
A-extent = a_px + [bboxA0, bboxA1] of the DRAWN frame (per-frame bbox from
bytes; right-facing frames span y≈[3,27], down-facing x≈[7,28] per the
banked v1 motion metrics — the tool recomputes, never hand-copies); overlap
px with T0's A-span [0,31] and T1's [32,63]; the majority tile (ties → T0,
the tile being left — declared); and the majority-crossover tick.

Hand estimate (midpoint ≈ a_px + 15.5 crosses the boundary at a_px ≥ 17 ⇒
first T1-majority tick is the a=18 tick): EARLY strafes a = 2,4,7,11,14
before the flip — **~5 consecutive T0-majority strafe ticks (~83 ms) facing
B**; MID a = 11,14 — ~2 ticks; LATE a = 25,28,... — zero (T1-majority from
the turn tick on); CONTROL — none (stand at T1 center). The tool's exact
per-frame table is the evidence; the rubric judges the read.

## KB grounding (carried, no new claims)

Carried from the v9 rationale (re-verified there this series; no new query
needed for a composition-only sprint): the exclusive-state pattern — facing
selects a sprite row, the state replaces the walk wholesale
(`game-research/technical-drawing-for-game-art.md` §8) — grounds the
declared model and names the artifact class the strafe risks: a walk cycle
pointing perpendicular to travel is the classic moonwalk/strafe read. The
v9 corpus-gap disclosure stands: nothing in the vault prescribes whether a
mid-tween turn should cut, defer, or lock — the FAIL routing remains a
recommendation space, not settled convention.

## Pass bars (fixed now, before any artifact exists)

Machine-checkable (`tools/turn_seam_metrics.py --check`, exit nonzero on any
failure; failures named and grouped on output). **INTEGRITY** failures mean
the toolchain or frozen-state law is broken — the sprint stops until fixed;
**MEASUREMENT** failures are banked evidence feeding the affected lane's
sub-verdict. The split is fixed here, before any number exists.

INTEGRITY:

1. **Zero new exports:** `exports/` contains exactly the 26 pinned PNGs of
   the seven banked releases, every file SHA-256-verified against its
   release.json pin (the banked checker, reused); no
   `exports/calibration-v9/` and no `exports/calibration-v10/` exist; the
   `make_release.py` registry and `tools/export_assets.py` bytes untouched
   (SHA-pinned by every banked release.json — enforced by the banked chain).
2. **Jump tables complete:** per lane per pair — pose Δ% AND (dA, dB) +
   window (dx, dy) + exact integer squared for EVERY consecutive tick pair
   t01→t02 .. t20→t21 (20 rows × 10 lanes), positions from independently
   recomputed smoothstep.
3. **Anchor map holds:** every equality in anchors 1–9 above, exact.
4. **Tick math exact:** walk mapping f0×4/f1×3/f2×3/f3×3 via the banked
   `walk_frame_index`; facing A before the turn tick, B from it (DEGEN: A
   throughout); commit ticks draw the standing pose (t01 idle@A; CONTROL t15
   idle@B); wrap structure per the verified engine handoff (B commit t14
   moving / t15 CONTROL; first B advance t15 / t16); REM 11/8/4/0; tween
   deltas exact per axis; poses restricted to {idle, f0..f3} — no attack
   pose anywhere; no tick added, consumed, or reallocated.
5. **In-window by construction:** every draw vector + the [2,2,29,29]
   contract bounds inside the window dims — lane windows (turn lanes 2×2
   tiles 64×64; DEGEN the banked 3-tile axis window), 3X turn-zoom crops
   (the A-tile pair at B-column 0: 32×64 DR / 64×32 RD), and 2X wrap-strip
   full windows — proven from the plan, never from put() clipping; T0, T1,
   T2 and their grid lines inside every turn-lane window by construction.
6. **Determinism + purity:** sheet + metrics + both APNGs byte-identical
   across two independent in-process builds and equal to committed bytes
   (plus a CLI re-run compared with `cmp`); every creature cell
   dual-verified (region reconstruction + direct export-byte equality at
   the computed integer draw vector).
7. **Banked artifacts stand:** the v0–v9 sheets/metrics regenerate
   byte-identical under the extended toolchain (the existing regression
   suites stay green); `tools/` coverage ≥ 80 under `bin/full_gate.py`.
8. **Category law (structural):** every numeric bar in this sprint compares
   within ONE facing-category. The only cross-facing numbers are the turn
   cuts and contexts (compared to each other); the only same-facing numbers
   are walk-cycle rows (compared to banked walk-cycle values). No raw
   pose-axis dominance bar across categories exists anywhere in the tool —
   the v9 category-error lesson is law.

MEASUREMENT (numeric):

M1. **Compound-cut band (per turn lane):** the turn cut's popping_pct ≤ the
    free-turn context band max (53.64, f0's context — the largest facing
    swap the walk system can draw). Frame-identical cuts satisfy it by
    anchor equality; the LIVE test is MID's compound cut, both pairs. A red
    = the turn+frame-advance compound exceeds every pure facing swap —
    banked evidence feeding that lane's L1, routed engine-side (defer the
    frame advance one tick alongside the turn — the render-the-turn-first
    clause), never a rescue. (No floor bar: a cut below the band is milder
    than the mildest pure swap — not a failure of anything.)

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone palettes,
both pairs, on the COMMITTED sheet; every claim is sheet-scope — per-tick
legibility under identical pinned timing, never temporal fusion at 60 tps,
never "reads at combat speed"):

- **L1 — turn-read (the swap under displacement).** Per class per pair: the
  turn tick reads as the SAME creature rotating in place while its slide
  continues — structure carries identity (frozen 5-color ramp, body mass,
  eye accent, feet row). **Named FAIL: the cut reads as an identity pop — a
  second creature, a sprite-swap error, or a teleport — at 1x.** Judged on
  the lane rows, the 3X turn zooms, and against the rendered CONTEXT row
  (the stationary yardstick) and the DEGEN no-turn baseline. MID's compound
  cut is judged under the same line, with M1's number as evidence.
- **L2 — strafe legibility.** Post-turn, the B-facing walk frames displacing
  along A for REM more advances read as momentum carry — the body finishing
  its committed slide already turned. **Named FAIL: broken slide — the leg
  cycle fights the displacement direction (moonwalk/dragged read) or the
  segment reads as knockback/ice.** Expected stress ranking EARLY (11
  residual advances ≈ 183 ms, the full f0→f1→f2→f3 cycle under facing B) >
  MID (8) > LATE (4). CONTROL has no strafe: its L2 judges the stand beat —
  **named FAIL: the 1-tick idle@B at T1 reads as a freeze/hiccup rather
  than a pivot beat.**
- **L3 — arrival restart.** The f3@B→f0@B wrap plus the first B
  displacement reads as a NEW step beginning in the new direction. **Named
  FAIL: stutter/rewind — the wrap reads as an animation hiccup (gait pop or
  frame skip) rather than a deliberate restart.** The wrap's pose delta is
  machine-pinned to the banked walk-cycle wrap (10.29/15.87 — the smallest
  cuts in the cycle); the risk is the simultaneous 90° displacement pivot,
  not magnitude. Judged on the 2X wrap strips (t13..t16; CONTROL t14..t17)
  and the 1x lanes. CONTROL's restart (idle@B→f0@B) is judged under the
  same line.
- **L4 — tile binding during the strafe.** With the binding table as
  evidence: does the B-facing strafing body read as bound to its committed
  tile T1? **Named FAIL: the body visually claims T0 (majority overlap) or
  reads as parked between tiles for a sustained span (≥ 3 consecutive
  strafe ticks) while facing B.** Expected reds, stated in advance per the
  arithmetic: **EARLY is expected to FAIL L4** (~5 consecutive T0-majority
  strafe ticks — the v9 EARLY wrong-tile precedent transposed to the body);
  MID sits at ~2 ticks (below the named span — expected borderline PASS on
  the table, decided by the 1x read); LATE and CONTROL expected clean.
  CONTROL's L4 judges the stand+start binding T1 (trivially clean by
  arithmetic).
- **L5 — degenerate gate (sheet-wide).** The DEGEN lanes read as the banked
  v1-class continuous walk (wrap included), all DEGEN rows machine-equal
  their anchors (bars 3/8), and the identity law holds sheet-wide
  (byte-frozen frames at computed vectors, frozen ramp, feet/anchor law
  inside the moving cells, nearest-neighbor everywhere).

**Decision rule (fixed):** per-class-per-pair sub-verdicts, independent — 8
sub-verdicts (EARLY/MID/LATE/CONTROL × DR/RD) + the degenerate gate. A
class+pair PASSES only if L1–L4 pass for it AND L5 holds sheet-wide. PASS ⇒
the bare mid-tween turn at that tick class is banked as READABLE — the
premise under v9's L1 and the buffering recommendation's render-the-turn-
first clause is confirmed for that class. FAIL ⇒ banked as an
ENGINE-TERRITORY finding naming the failing ticks and magnitudes, extending
the v8/v9 recommendation (facing-aware buffering / facing-lock-during-tween
/ REM-gating), never a rescue frame, never a smear, never bar softening.
Mixed outcomes are expected and first-class: a clean LATE/CONTROL with a red
EARLY refines the REM breakpoint table; a red EVERYWHERE means even the
engine's cheapest legal turn does not read mid-tween — the strongest
possible evidence FOR the buffer clause.

Scope discipline carried from v4–v9: no temporal/fusion claims (60 tps
questions live in the consolidated runtime item); no facing-drift, no
recovery-walk adjudication, no step-initiation or arrival-tick turn
variants, no 8-direction sets, no terrain, enemies, pack, lore, or Bedrock
generation; AD-C1/AD-C2 triggers not met; audio thread parked (acknowledge
mail at close only); the runtime-replay design stays parked until the game
cycle closes.

## Toolchain plan

Two new thin modules (stdlib, deterministic, no timestamps); banked helpers
imported unmodified (`compose_cell`, `draw_floor_tile`, sprite loaders,
`smoothstep`/`round_half_up`/`walk_frame_index`/`tween_position`, the
seam-extended glyph font + `draw_text`, APNG encoder + exact 1/60 s delays,
`pair_stats`/`frame_stats`/`load_opaque`, `check_export_pins`, `TICK_MS`,
`pose_filename`/`POSE_DIRS`/`default_dirs`):

- `tools/make_turn_timeline.py`: the ten-lane pure-turn tick plan (a pure
  function of the pinned constants + the pre-registered turn ticks + the
  pair axes + the declared model) and the deterministic sheet — per pair
  section: lane label + RULER + Z1/Z2 rows (21 columns t01..t21) over the
  lane window (turn lanes 2×2 tiles; DEGEN the banked 3-tile axis window);
  TURN 3X zooms (turn−1 | turn | turn+1 per turn lane, cropped to the
  A-tile pair at B-column 0); WRAP 2X strips (t13..t16 per lane; CONTROL
  t14..t17; DEGEN included — full window); CONTEXT 2X row (the rendered
  stationary yardstick: [fN@A | fN@B] for f0..f3 + idle); FILM rows (the
  walk-pose identity strip, both facings, both zones). Machine-readable
  cell manifest (section, pair, lane, zone, tick, phase, pose, pose_facing,
  window, draw, scale, rect). Optional APNG aids (`turn-lanes-<pair>.apng`:
  the four turn lanes side by side, full t00..t29, exact 1/60 s per-tick
  delay, 0.5 s final hold, 4x NN, banked encoder; DEGEN's motion is the
  banked v1 walk, already animated in the banked previews).
- `tools/turn_seam_metrics.py`: jump tables, turn-cut extraction, context
  deltas, the anchor map (bars 1–9), the body-binding table, tick math,
  bounds, export pins, determinism, purity, M1 band check; `--check`
  enforcing the INTEGRITY/MEASUREMENT split with named failures.

Tests in `tests/test_turn_tools.py` mirroring `test_cross_seam_tools.py`:
synthetic fixture (per-pose rects, IDENTICAL across facings, f3 == idle —
so the context/anchor bars are exercised in their FAILING direction on
synthetic bytes while structure passes, the banked test pattern);
plan/sheet/validator suites with hand-computed draw vectors; every check
exercised in pass AND fail directions; skip-guarded real-artifact
regressions asserting committed-artifact consistency and banked-value
equalities without assuming the unmeasured MID numbers. No release chain;
`tools/export_assets.py` untouchable regardless.

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default seat) of
the rationale + measured evidence + provisional rubric verdicts, ≤ 8k total
tokens, single call; response redirected to a file and read with explicit
UTF-8; every council numeric claim RECOMPUTED against pixels/numbers before
adoption; every REFUTED verdict re-verified against the primary evidence
(v5–v9 precedent: fabricated precision under adversarial framing).

## Stop conditions

One measurement cycle: zero new creature frames, zero new exports, one
deterministic turn sheet (byte-identical on regeneration), one metrics JSON,
optional APNG aids, one banked verdict with 8 per-class-per-pair
sub-verdicts + the degenerate gate, findings routed engine-side, one next
hypothesis. Change sets: (0) the executed step-0 re-pin (`5fd7efd`,
committed alone); (1) this rationale + toolchain + tests; (2) metrics +
sheet + aids + verdict after council + vision critique. Gate re-run
immediately before banking. Push after banking (pre-push = LFS preserve +
full gauntlet). Stop after the verdict is banked and pushed, whichever way
the sub-verdicts land.
