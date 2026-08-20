# Calibration v11 — corner-turn lane + settle-hold remedy preview (composition-only)

Sprint-11 question, two threads that both fall out of the banked v10 verdict
(`reviews/calibration-v10/verdict.md`), both zero-new-frames:

1. **The corner turn** (v10's banked next-hypothesis): B pressed exactly at
   t14, the ARRIVAL tick — the only boundary-turn class never rendered. The
   facing swaps ON the commit tick, so the turn cut rides the last tween
   pixel and the arrival wrap follows immediately: no stand beat, no strafe
   segment. Likely the cleanest turn the engine permits, and the natural
   comparison twin for v10's CONTROL (which pays a 1-tick pivot beat).
2. **The settle-hold remedy preview (EXP-class, the v4 EXP-row precedent):**
   v10's standing engine-side recommendation — "when facing ⊥ travel, select
   the settle frame instead of cycling the gait" — is frame-selection code at
   integration time and it is UNRENDERED. This sprint renders it as a
   DECLARED-MODEL VARIANT at v10's two failing turn ticks (EARLY t03, MID
   t06), so the recommendation can be judged as pixels instead of prose.

**This is a measurement sprint: ZERO new frames, zero new exports, zero tick
changes, zero releases, zero game-two changes.** Every pixel is frozen (all
26 banked export pins across v0–v3, v5–v7); the deliverables are 2D
timelines, machine jump tables with vector displacements, binding tables, and
a banked per-lane verdict.

**Remedy-lane status discipline (fixed here, before any artifact):** the two
REMEDY lanes are EXP-class — a declared-model preview of an ENGINE
recommendation. They are NEVER a production lane, never a tick change, never
a claim about current runtime behavior, and never a rescue of v10's banked
reds (those verdicts stand unmodified). Their verdicts may only be phrased as
evidence FOR or AGAINST reworking the recommendation; "ship it" language is
out of scope by construction, because nothing here is shippable — the remedy
is runtime frame selection and this repo owes zero pixels for it.

## Verified reachability and in-tick ordering (game commit `b6724ec3`, read-only)

All citations re-derived this session with `git show` at the live pin (step-0
mechanical identity re-pin `f0774a3`: all five pinned sources
content-identical, gate exit 0, `attack_timing` re-verified 5/4/8/13 via
`/kits/striker/...` in `data/balance/combat.json`). Blob-compare across the
re-pin hop `1360b272`→`b6724ec3`: `renderer.rb`, `creature.rb`,
`controllers.rb`, `grid_walker.rb` blob-identical; `world.rb` changed
(`de6a20df`→`661caac4`) — the diff is additive and confined to `load_zones`
(the T2 tile-type registry) plus one `require`, so the tick-order citation
shifts exactly +1 line and carries. **`renderer.rb` line numbers differ from
the v10 verdict's** (L520–531 / L536–544): those were the pre-`9762188`
blob; the current pin's numbers are cited below and were read this session.

- **World tick order** (`src/game/world.rb` L687–699, `tick_world`):
  `@pack.members.each(&:tick_body)` (L687) and `humans.each(&:tick_body)`
  (L688) run BEFORE the seat-ordered controller loop (L692–699,
  `controller.tick(body, seat_input(inputs, seat), self)` at L698).
  `tick_body` (`creature.rb` L125–126) runs `@walker.tick` unconditionally.
  Within one world tick the tween advances BEFORE input touches the
  creature.
- **Controller order** (`src/game/controllers.rb`, `PossessedController#tick`
  L24): `dir = held_direction(input)` (L51) → `creature.face(dir)` (L52,
  unconditional on the non-seized move path) → step attempt (L56, inside
  `elsif dir != [0, 0]`).
- **`held_direction`** (`controllers.rb` L85–89): `dx` and `dy` are resolved
  INDEPENDENTLY from held keys and returned as `[dx, dy]`.
- **`face`** (`creature.rb` L142–144): `@facing = dir unless dir == [0, 0]`
  — no guard, no walker interaction; ANY nonzero vector is accepted.
- **`step`** (`creature.rb` L146–149) → `@walker.step(dx, dy, frames:
  @kit[:step_frames])` — 13 frames for the striker kit (pinned).
- **Mid-tween step refusal** (`grid_walker.rb` L32, L35–39): `moving? =
  @tween_left.positive?`; `step` → `return false if moving?` (L36).
- **Facing-blind tween, no snap** (`grid_walker.rb` L90–97): the visual px
  eases toward the committed tile with smoothstep `3t² − 2t³` regardless of
  `@facing`; `commit_dash` (L80–88) commits the logical tile at step start
  and sets NO position.
- **Renderer** (`src/app/renderer.rb`): `draw_creature` (L478) draws the body
  at the tween position plus `lunge_offset`; `draw_facing_notch` is CALLED at
  L524 and defined L544–557, reading `c.facing` LIVE at every draw;
  `lunge_offset` (L560–569) returns `[0, 0]` outside `:windup`/`:active`, so
  a pure walk carries NO draw offset. **The engine draws no walk frames at
  all** (flat rect + notch) — walk-frame selection is this repo's declared
  review convention (v1 mapping, carried v2–v10), not an engine contract.

**THE CORNER TICK, derived (the risk-1 item):** step A commits at t01's
controller; its 13 advances land at t02..t14 `tick_body`s (t14's advance
takes `tween_left` 1→0, px = 32). At **t14's controller** `moving?` is
therefore already FALSE, so with A released and B pressed on that same
controller tick: `held_direction` returns B → `face(B)` (L52) → `step(B)`
(L56) is ACCEPTED and commits at t14. `commit_dash` sets no pixel position,
so t14 still draws the A-arrival position, in facing B. The first B advance
lands at t15's `tick_body`. **Turn tick = commit tick = arrival tick = t14**;
REM = 13 − (14 − 1) = 0; B-facing ticks inside the A step = 1 (the arrival
tick itself); residual A advances after the turn = 0. This is the same
engine handoff v10 verified and used for its moving lanes — v11 changes only
WHEN the facing flips (t14 instead of t03/t06/t10), so the corner class needs
no new engine fact, only the tick that v10 recorded as unmeasured.

**Honest disclosure the model needs — the key-overlap/diagonal sub-class
(RECORDED, not measured):** the modeled input is frame-perfect (A released
and B pressed in the SAME controller tick). Real hands overlap keys. Because
`held_direction` resolves both axes independently (L85–89), a 1-tick overlap
returns the DIAGONAL `[1, 1]`, and `face` accepts it (L142–144). Diagonal
facing is LIVE engine behavior, not a hypothetical: `draw_facing_notch` has
an explicit diagonal branch (L554–555, "diagonal: corner notch"), and a
diagonal `step` is legal — `plan_dash` scales the duration by
`DIAGONAL = √2` (`grid_walker.rb` L8, L76), so a diagonal step tweens
`round(13·√2) = 18` frames instead of 13. **This sub-class is unrenderable
with banked bytes: no diagonal sprite row exists** (the export set is
down/right only). It is recorded as a finding — an integration design must
choose a sprite row for diagonal facing, and the 18-frame diagonal step is a
different timing class entirely — and it is explicitly NOT measured here. The
frame-perfect same-tick transition is the CLASS DEFINITION for the CORNER
lane.

**Pivot branch (pre-registered): NOT TRIGGERED.** The branch was: if any
cited fact diverged at the live pin, re-derive the corner tick table from the
new facts before building any artifact, and if the same-tick commit no longer
held (e.g. `face` gaining a moving guard, `step` gaining an arrival-tick
lockout, or the controller loop moving BEFORE `tick_body`), the corner class
would collapse into v10's CONTROL — render nothing new for it and say so.
Every fact verified above holds at `b6724ec3`; the four v10 facts carry
(`face` unconditional, mid-tween step refusal, facing-blind tween, live
facing read + zero walk offset) and walk timing is unchanged (13-tick step,
banked deltas and mapping). **If a future pin adds any of those guards, this
model is fiction — re-verify at every re-pin.**

## Drawing models (pre-registered; the banked convention plus ONE new clause)

**Model A — the v10 walk model, unchanged** (carried v4–v10): walk ticks draw
the banked v1 mapping — `walk_frame_index` distributes f0×4 / f1×3 / f2×3 /
f3×3 across a step's 13 ticks (walk tick k = the tick whose `tick_body` did
the k-th advance); the step-commit tick draws the STANDING pose (banked
precedent: t01 draws idle); f3 is the idle byte-copy (banked release note);
a mid-tween re-face swaps the FACING of the drawn walk frame from the turn
tick on while the frame INDEX continues from step progress; the B step's
frames restart at f0; draw position = 2D tween with no offset anywhere.
Lanes CORNER, CONTROL and DEGEN use Model A verbatim — CONTROL and DEGEN are
byte-identical to v10's lanes by construction (the same banked `lane_tick`
function, called with the same arguments).

**Model A's corner-tick self-consistency (disclosed, not resolved by fiat):**
at t14 two Model-A rules could both claim the pose — "the arrival tick draws
the A step's 13th walk frame" (f3) and "a commit tick draws the standing
pose" (idle). **They agree byte-for-byte: f3 IS the idle byte-copy** (banked
law, machine-checked every run). The tables below label the corner tick f3@B
because the arrival rule is the one v10 already applied to its moving lanes
(whose B step also commits at t14); the cut therefore anchors to the f3
context, which equals the idle context exactly (44.44). No pixel depends on
the choice of label.

**Model B — the settle-hold VARIANT (new clause, EXP-class):** on a REMEDY
lane, every STRAFE tick — the turn tick through arrival, inclusive — draws
`f3` (the settle/standing byte-copy) in facing B at the tween position,
instead of the cycling walk frame Model A would select. Everything else is
Model A untouched: the same turn ticks, the same tween positions, the same
facing rule, the same arrival wrap, the same B-step walk. Basis: this is
exactly v10's banked recommendation ("select the standing/settle frame (f3/
idle class) for strafe ticks instead of advancing the walk cycle") expressed
as a drawing rule; it is a PREVIEW of engine frame selection, not a claim
that the engine does this today. Because the hold ends on f3@B and the
banked wrap is f3@B→f0@B, the handoff to the B step is seamless BY
CONSTRUCTION — a property of the remedy, and one of the things R3 judges.

## Conventions block (evidence-table law, carried v8–v10 — fixed before the first number)

- **Window coordinates:** x right, y down, canvas-origin (the 32×32 export
  canvas's top-left). Every jump-table row reports the window delta (dx, dy)
  AND the semantic delta (dA, dB).
- **Axes per lane:** A = the FIRST walk axis, positive in the walk direction
  (DR: A = +y; RD: A = +x). B = the direction turned TO (DR: B = +x; RD:
  B = +y). Degenerate lanes: A and B coincide; dA carries the full along-axis
  delta, dB = 0 by construction.
- **Pose Δ%** = 100·XOR/union on canvas-aligned export bytes in SPRITE-LOCAL
  space — position-independent; the draw vector never enters the comparison.
  0.0 only for identical pose AND facing.
- **Squared displacement** = dA² + dB², exact integer. No scalarized
  pose+position metric anywhere (banked v6 correction).
- **Tile names:** T0 = the A step's origin tile; T1 = the committed/landing
  tile of step A; T2 = T1 + B̂ (the B step's landing). The T0/T1 boundary is
  the grid line the body crosses.
- **Pose names are facing-qualified** in every table: `f0@down`, `f3@right`.
  The turn cut is pose(t_turn−1)@A → pose(t_turn)@B.
- **REM** = 13 − (t_turn − 1): tween advances remaining AFTER the turn tick's
  own advance (v9/v10 formula unchanged). CORNER's REM is 0 with ONE B-facing
  tick inside the A step (the arrival tick); CONTROL's REM is 0 with ZERO
  (its turn tick is past arrival). Both numbers are reported per lane so the
  formula is never asked to carry a distinction it cannot make.
- **Phase vocabulary:** v10's labels are reused unchanged for Model-A lanes
  (`idle_pre`, `walk_a`, `turn_stand`, `walk_b`, `walk_1`, `walk_2`,
  `idle_post`) plus two v11 labels: `turn_arrive` (CORNER's t14 — turn,
  commit and arrival in one tick) and `strafe_hold` (a Model-B held tick).

## Lane set and tick definitions (pre-registered)

Two facing pairs — **DR** (walk DOWN, turn RIGHT) and **RD** (walk RIGHT,
turn DOWN) — each with five lanes. Walk A commits at t01 (t00–t01 idle_pre @A,
banked `IDLE_PRE_TICKS = 2`); advances t02..t14; arrival absolute t14 in
every lane. "Turn at tick t" = direction B replaces direction A at t's
controller tick (A released, B pressed, held through the B step).

| lane | model | turn tick | REM | B-facing ticks in the A step | B commit | first B advance | role |
|---|---|---|---|---|---|---|---|
| CORNER | A | t14 | 0 | 1 (the arrival tick) | t14 | t15 | **the new class**: turn = commit = arrival, no stand beat, no strafe |
| REM_EARLY | B | t03 | 11 | 12 (all held f3@B) | t14 | t15 | remedy preview at v10's EARLY tick (L2 + L4 red) |
| REM_MID | B | t06 | 8 | 9 (all held f3@B) | t14 | t15 | remedy preview at v10's MID tick (L2 red only) — the remedy's PRIMARY test subject |
| CONTROL | A | t15 | 0 | 0 (stand beat at t15) | t15 | t16 | v10's CONTROL, unchanged — hard regression bar |
| DEGEN | A | — | — | — | t14 (step 2 along A) | t15 | v10's uncut two-step walk — hard regression bar |

Ten lanes (5 × 2 pairs). Recorded future classes, NOT measured: the
key-overlap/diagonal corner sub-class (above); turn on the step-initiation
tick; multi-turn chatter (A→B→A mid-tween); 8-direction turns; facing drift
during windup.

**Tick tables (the full plan; DR draw = (b_px, a_px), RD mirrors to
(a_px, b_px); pos(k) = round_half_up(32·smoothstep(k/13)) = 0,1,2,4,7,11,14,
18,21,25,28,30,31,32; per-tick deltas 1,1,2,3,4,3,4,3,4,3,2,1,1):**

| tick | CORNER | REM_EARLY | REM_MID | CONTROL | DEGEN | a/b px |
|---|---|---|---|---|---|---|
| t01 | idle@A | idle@A | idle@A | idle@A | idle@A | a 0 |
| t02 | f0@A | f0@A | f0@A | f0@A | f0@A | a 1 |
| t03 | f0@A | **f3@B** | f0@A | f0@A | f0@A | a 2 |
| t04 | f0@A | f3@B | f0@A | f0@A | f0@A | a 4 |
| t05 | f0@A | f3@B | f0@A | f0@A | f0@A | a 7 |
| t06 | f1@A | f3@B | **f3@B** | f1@A | f1@A | a 11 |
| t07 | f1@A | f3@B | f3@B | f1@A | f1@A | a 14 |
| t08 | f1@A | f3@B | f3@B | f1@A | f1@A | a 18 |
| t09 | f2@A | f3@B | f3@B | f2@A | f2@A | a 21 |
| t10 | f2@A | f3@B | f3@B | f2@A | f2@A | a 25 |
| t11 | f2@A | f3@B | f3@B | f2@A | f2@A | a 28 |
| t12 | f3@A | f3@B | f3@B | f3@A | f3@A | a 30 |
| t13 | f3@A | f3@B | f3@B | f3@A | f3@A | a 31 |
| t14 | **f3@B** | f3@B | f3@B | f3@A | f3@A | a 32 (arrival; B/step-2 commits) |
| t15 | f0@B | f0@B | f0@B | **idle@B** | f0@A | b 1 (CONTROL b 0; DEGEN a 33) |
| t16 | f0@B | f0@B | f0@B | f0@B | f0@A | b 2 (CONTROL b 1; DEGEN a 34) |
| t17 | f0@B | f0@B | f0@B | f0@B | f0@A | b 4 (CONTROL b 2; DEGEN a 36) |
| t18 | f0@B | f0@B | f0@B | f0@B | f0@A | b 7 (CONTROL b 4; DEGEN a 39) |
| t19 | f1@B | f1@B | f1@B | f0@B | f1@A | b 11 (CONTROL b 7; DEGEN a 43) |
| t20 | f1@B | f1@B | f1@B | f1@B | f1@A | b 14 (CONTROL b 11; DEGEN a 46) |
| t21 | f1@B | f1@B | f1@B | f1@B | f1@A | b 18 (CONTROL b 14; DEGEN a 50) |

(Bold = the lane's turn tick. The plan generates t00..t29; the sheet rows and
jump tables cover t01..t21 — the commit row, the full A step, the wrap, and 7
B-walk ticks including the post-wrap f0→f1 boundary. During a strafe/hold
a_px keeps advancing per the tween deltas with b_px = 0; from the wrap on
a_px = 32 and b_px advances per the same deltas; DEGEN carries a single
along-axis total 0..32, 33..64.)

**Cut identities (forced by the models — INTEGRITY self-checks where noted):**

- **CORNER** cuts `f3@A→f3@B` at t13→t14, displacement (dA, dB) = (1, 0) —
  frame-identical (and f3 is the idle byte-copy), so it MUST equal the f3
  context = the idle context = 44.44 exactly. Integrity, not a finding.
- **REM_EARLY** cuts `f0@A→f3@B` at t02→t03, displacement (1, 0).
- **REM_MID** cuts `f0@A→f3@B` at t05→t06, displacement (4, 0) — the swap
  rides a peak-velocity tick. Both remedy classes cut FROM f0 (f0 spans
  t02..t05 under the banked mapping), so the two lanes share ONE novel pose
  number per pair direction: **f0@down→f3@right (DR) and f0@right→f3@down
  (RD)** — the sprint's only novel pose numbers, measured and never assumed.
  Their equality across the two remedy classes within a pair is an integrity
  bar (the cross-lane consistency web).
- **CONTROL** cuts `f3@A→idle@B` at t14→t15, displacement (0, 0) = 44.44
  (banked v10).
- **DEGEN** has no cut.

## Anchor map (machine-equal or it's a plan bug — the v10 risk-2 discipline is law)

Every equality below is an INTEGRITY bar: a near-miss is a derivation bug and
the sprint stops. The NOVEL content is exactly: the two remedy cut numbers,
the corner-tick read, the held-strafe read, and the recomputed remedy binding
tables — nothing else.

1. **Free-turn context rows** (fN@A↔fN@B for N=0..3 + idle↔idle, computed
   fresh from bytes) == the banked
   `reviews/calibration-v9/cross-seam-metrics.json` `context_deltas` on all
   four fields: f0 53.64/63/199/371, f1 45.00/64/162/360, f2
   36.45/55/121/332, f3 44.44/64/156/351, idle 44.44/64/156/351.
2. **f3/idle byte-copy law:** the f3@F opaque pixel map == idle@F pixel map
   exactly, both facings.
3. **CORNER cut == f3 context == idle context == 44.44**, both pairs, with
   the pose pair asserted `f3→f3` cross-facing.
4. **Remedy hold structure:** every `strafe_hold` tick draws pose f3 in
   facing B; consequently every remedy strafe ROW is **0.0** exactly (same
   pose, same facing) — the held-frame law, machine-asserted per row rather
   than assumed.
5. **Remedy cut consistency:** the REM_EARLY and REM_MID cut numbers are
   EQUAL within a pair (same byte pair), and the pose pair is asserted
   `f0→f3` cross-facing.
6. **All wraps == the banked v1 walk cycle:** f3@B→f0@B at t14→t15 (CORNER
   and both REMEDY lanes) == `reviews/calibration-v1/motion-metrics.json`
   pair `f3->f0` for the row's facing — right 10.29 (DR), down 15.87 (RD);
   CONTROL's stand→restart == 44.44 then the same 10.29/15.87; DEGEN's
   along-axis wrap == the same banked values.
7. **Every same-facing walk-cycle boundary row** == the banked v1
   motion-metrics pair for its facing: down f0→f1 19.64 / f1→f2 19.00 /
   f2→f3 15.87; right f0→f1 22.09 / f1→f2 22.09 / f2→f3 10.29.
   Same-pose-same-facing rows are 0.0 by convention. The ONLY cross-facing
   row in any lane is that lane's turn cut.
8. **Cross-lane consistency web:** every repetition of the same
   (pose_from@facing → pose_to@facing) pair anywhere in the v11 tables
   carries the identical pose Δ%.
9. **DEGEN prefix equality:** DEGEN rows t01→t02 .. t13→t14 machine-equal
   the same pair's CONTROL rows, row for row (the banked v10 check, reused).
10. **THE HARD TOOLCHAIN-REGRESSION BAR — CONTROL and DEGEN == committed
    v10:** every field of every CONTROL and DEGEN row (`from_tick`,
    `to_tick`, poses, facings, `pose_delta_pct`, `delta_a_px`,
    `delta_b_px`, `delta_window_px`, `squared_px`, `phase_to`) equals the
    corresponding row in the committed
    `reviews/calibration-v10/turn-metrics.json`, read at runtime; and the
    v11 PLAN's CONTROL/DEGEN tick dicts equal the v10 plan's tick dicts
    field-for-field (pose, facing, phase, a_px, b_px, draw). Any drift means
    the v11 toolchain changed v10's answers — the sprint stops.
11. **Cross-version lane webs:** CORNER rows with `to_tick ≤ 13` == v10
    CONTROL rows over the same range (both are the uncut walk @A); CORNER and
    REMEDY rows with `from_tick ≥ 14` (wrap + B-walk) == v10 EARLY/MID rows
    over the same range; REM_EARLY rows with `to_tick ≤ 2` == v10 EARLY's,
    REM_MID rows with `to_tick ≤ 5` == v10 MID's; every REMEDY binding row's
    `a_px` == v10's EARLY/MID binding `a_px` at the same tick (the remedy
    does NOT move the body).
12. **Tween-delta law:** per-tick displacement along the active axis follows
    1,1,2,3,4,3,4,3,4,3,2,1,1 exactly; the wrap row is (0,1) sq 1 for CORNER
    and REMEDY, (0,0) then (0,1) for CONTROL, (1,0) sq 1 along-axis for
    DEGEN. Max any-row squared = 16 (the peak-velocity tick).

## Body-tile binding derivation (pre-registered; report-only, never a machine failure)

Per reported tick the tool computes: body A-extent = a_px + [bboxA0, bboxA1]
of the DRAWN frame (per-frame bbox recomputed from bytes, never hand-copied);
overlap px with T0's A-span [0,31] and T1's [32,63]; the majority tile (ties
→ T0, the tile being left — declared); and the majority-crossover tick. The
reported tick sets are declared per lane class: REMEDY lanes report every
`strafe_hold` tick; CORNER reports its single `turn_arrive` tick (t14).

Hand estimate (the v10 arithmetic, same a_px sequence — midpoint ≈ a_px +
~15.5 crosses the T0/T1 boundary at a_px ≥ 17, so the first T1-majority tick
is the a = 18 tick, t08): **REM_EARLY ≈ 5 consecutive T0-majority ticks
(t03–t07, ~83 ms), REM_MID ≈ 2 (t06–t07), CORNER 0** (at t14 a_px = 32, the
body sits entirely inside T1's span — T0 overlap 0 px). The remedy holds f3
instead of f0/f1/f2, so the bbox — and therefore the exact overlap px and
possibly the crossover tick — is RECOMPUTED, not inherited: if f3's A-extent
shifts the crossover by a tick, R4 is decided by the recomputed table against
the same pre-registered ≥ 3-tick span, with no post-hoc adjustment in either
direction.

**Pre-registered asymmetry (risk 2, written down before the sheet exists):**
the settle-hold remedy targets L2/gait ONLY. It cannot fix EARLY's L4
body-bind, because the body travels the identical path either way (the plan
proves it: identical a_px, identical draw vectors). **REM_EARLY is EXPECTED
to keep its wrong-tile red.** The remedy's primary test subject is REM_MID,
which failed v10 on L2 alone.

## Pass bars (fixed now, before any artifact exists)

Machine-checkable via `tools/corner_metrics.py --check` (exit nonzero on any
failure; failures named and grouped). **INTEGRITY** failures mean the
toolchain or frozen-state law is broken — the sprint stops until fixed;
**MEASUREMENT** failures are banked evidence feeding the affected lane's
sub-verdict. The split is fixed here, before any number exists.

INTEGRITY:

1. **Zero new exports:** `exports/` contains exactly the 26 pinned PNGs of
   the seven banked releases, each SHA-256-verified against its release.json
   pin (the banked checker, reused); no `exports/calibration-v9`, `-v10` or
   `-v11` directory exists; the `make_release.py` registry and
   `tools/export_assets.py` bytes untouched.
2. **Jump tables complete:** per lane per pair — pose Δ% AND (dA, dB) +
   window (dx, dy) + exact integer squared for EVERY consecutive tick pair
   t01→t02 .. t20→t21 (20 rows × 10 lanes), positions from independently
   recomputed smoothstep.
3. **Anchor map holds:** every equality in anchors 1–12 above, exact.
4. **Tick math exact:** per lane class — CORNER: turn = commit = arrival =
   t14, REM 0, one B-facing tick in the A step, wrap at t14→t15; REMEDY: v10
   tick geometry with the Model-B pose substitution on strafe ticks ONLY
   (pre-turn, wrap and B-walk ticks identical to v10); CONTROL/DEGEN: v10
   verbatim. Walk mapping f0×4/f1×3/f2×3/f3×3 via the banked
   `walk_frame_index`; facing A before the turn tick, B from it; poses
   restricted to {idle, f0..f3}; no tick added, consumed, or reallocated.
5. **In-window by construction:** every draw vector + the [2,2,29,29]
   contract bounds inside the lane window, inside every declared zoom-strip
   crop (including CORNER's four-tick strip), inside the wrap strips and the
   two comparison bands — proven from the plan, never from `put()` clipping.
6. **Determinism + purity:** sheet + metrics + both APNGs byte-identical
   across two independent in-process builds and equal to committed bytes
   (plus a CLI re-run compared with `cmp`); every creature cell — including
   both comparison bands — dual-verified (region reconstruction + direct
   export-byte equality at the computed integer draw vector).
7. **Banked artifacts stand:** the v0–v10 sheets/metrics regenerate
   byte-identical under the extended toolchain (existing regression suites
   green); full suite green; `tools/` coverage ≥ 80 under `bin/full_gate.py`.
8. **Category law (structural):** every numeric bar compares within ONE
   facing-category. The only cross-facing numbers are the turn cuts and the
   contexts (compared to each other); the only same-facing numbers are
   walk-cycle rows (compared to banked walk-cycle values). No raw
   cross-category dominance bar exists anywhere in the tool — the v9
   category-error lesson is law.

MEASUREMENT (numeric, pre-registered):

M1. **Remedy turn-and-settle band:** the two novel remedy cuts
    (f0@down→f3@right, f0@right→f3@down) ≤ **53.64** — the free-turn context
    band max (f0's context, the largest facing swap the walk system can
    draw). A red = the turn-and-settle compound exceeds every pure swap:
    banked evidence feeding R1 for BOTH remedy classes and routed to
    recommendation rework (e.g. hold the CURRENT frame instead of jumping to
    f3), never a rescue and never a softened bar. The CORNER cut satisfies
    the band by anchor 3 (integrity), so M1's live subjects are exactly the
    two remedy numbers.

## Perceptual rubric (pre-registered, critique-blocking; sheet-scope)

Judged at native 1x on the COMMITTED sheet, both zone palettes, both pairs,
per lane per pair; the 3x zooms, 2x wrap strips, comparison bands and the
rendered CONTEXT row are diagnostic aids. **The v10 adjudication law binds:
a pre-registered perceptual FAIL condition that is STRUCTURALLY PRESENT in
the committed frames must be adjudicated HERE — "routed to runtime" is not an
available disposition for conditions the static evidence already contains;
only SEVERITY-at-speed may be routed to the consolidated runtime item.**

**Corner group (2 sub-verdicts, one per pair):**

- **B1 — corner-read.** t13 → t14 → t15 reads as ONE continuous corner: the
  creature completes its slide, turns, and steps off along B. **Named FAIL:
  a boundary pop or teleport — the corner reads as two disconnected motions
  (a stop-and-restart) or as a positional jump at the tile line.**
- **B2 — cut identity at dA = 1.** The frame-identical f3@A→f3@B swap, riding
  the last tween pixel, reads as the same creature rotating. **Named FAIL:
  identity pop — a second creature, a sprite-swap error, or a silhouette
  break at the cut.** The 44.44 anchor is derivation integrity, NOT evidence
  of perceptual equivalence (the v10 council Q1 precision, carried).
- **B3 — arrival restart.** The f3@B→f0@B wrap plus the first B advance reads
  as a new step in the new direction. **Named FAIL: stutter or rewind — the
  wrap reads as an animation hiccup rather than a deliberate step-off.**
- **B4 — corner-tick binding** (expected trivially clean by arithmetic).
  **Named FAIL: at the corner tick the body reads as parked BETWEEN tiles
  (or in T0) rather than arrived in T1.**

**Remedy group (4 sub-verdicts: 2 classes × 2 pairs, each judged on R1–R4):**

- **R1 — turn-and-settle cut read.** The f0@A→f3@B cut reads as one creature
  turning AND settling its legs (a plausible "brace and finish the slide"),
  not as a dropped frame. **Named FAIL: the compound reads as a stutter or
  identity pop — a skipped/rewound gait step at the turn.** M1's number is
  evidence under this line, never proof of it.
- **R2 — momentum carry vs DEAD DRAG.** The remedy kills the gait by
  construction, so the named failure INVERTS relative to v10: the risk is no
  longer moonwalk. **Named FAIL: dead drag — a frozen creature dragged
  across the tiles (statue-slide / ice read), reading as knockback, a
  physics push, or a paused animation rather than a body finishing its own
  committed step.** Prior for the PASS direction, cited in advance: v9's
  held-a0 glide (a held frame under displacement) PASSED its L2 line — a held
  frame under smooth tween is not automatically an ice read.
- **R3 — wrap seamlessness.** The hold ends on f3@B and the wrap IS the
  banked f3→f0 (10.29/15.87), so the restart should be the cleanest in the
  series. **Named FAIL: the wrap reads as the step's FIRST motion (the body
  appears to start walking only at t15, i.e. the whole strafe read as a
  non-event) or as a hiccup at the seam.**
- **R4 — tile binding during the hold.** With the recomputed binding table as
  evidence: does the held body read as bound to its committed tile T1?
  **Named FAIL: the body visually claims T0 (majority overlap) or reads as
  parked between tiles for ≥ 3 consecutive held ticks while facing B.**
  **Expected red, stated in advance: REM_EARLY fails R4** (~5 consecutive
  T0-majority ticks — the v9/v10 wrong-tile precedent, untouched by a
  frame-selection remedy). REM_MID expected ~2 ticks, below the span.

**Degenerate/regression gate (sheet-wide):** the DEGEN lanes read as the
banked v1-class continuous walk; CONTROL reads as v10's banked
arrive→pivot→go; both machine-equal the committed v10 rows (anchor 10); the
identity law holds across every dual-verified cell.

**Decision rules (fixed now):**

- **Corner:** a pair PASSES if B1–B4 all pass for it. PASS ⇒ the arrival-tick
  turn is banked as the cleanest legal boundary turn rendered in this series,
  and the "buffer the turn to the boundary" clause of the v8–v10
  recommendation gains its rendered endpoint. FAIL ⇒ an ENGINE-TERRITORY
  finding naming the failing tick.
- **Remedy:** **REM_MID passing R1–R4 ⇒ the settle-hold recommendation is
  banked as RENDERED-VALIDATED for REM ≤ 8.** REM_EARLY is expected mixed
  (R4 red persists) ⇒ **REM-gating stays necessary at REM 11 regardless of
  the remedy** — the two remedies are complementary, not alternatives. **Any
  R2 dead-drag red ⇒ the recommendation needs REWORK** (e.g. a 2-frame
  settle bob, or holding the CURRENT frame rather than jumping to f3 — still
  engine-side, still zero pixels owed from this repo).
- **CORNER vs CONTROL is a RECORDED NOTE, not a pass/fail bar.** Two
  banked-clean classes cannot fail against each other; the sprint records
  which boundary-turn treatment reads better and why, as input to the
  integration design.

Scope discipline carried v4–v10: no temporal/fusion claims (60 tps questions
live in the consolidated runtime item); no diagonal-facing rendering, no
8-direction set, no multi-turn chatter, no step-initiation turn; no attack
poses, no terrain, enemies, pack, lore, or Bedrock generation; AD-C1/AD-C2
triggers not met; the runtime-replay-capture design, the audio thread and the
tile era stay parked (mail acknowledged at close only).

## Toolchain plan

Two new thin modules (stdlib, deterministic, no timestamps). Banked v10
modules are imported UNMODIFIED and never edited — `tools/export_assets.py`
and `tools/make_release.py` stay byte-frozen, and so do
`make_turn_timeline.py` / `turn_seam_metrics.py` (the v0–v10 regeneration
tests must stay green). Where a banked check is bound to v10's lane names,
v11 re-implements only the ITERATION locally and imports the banked anchor
data and geometry helpers (`V1_PAIR_KEYS`, `load_v1_pairs`,
`check_context_anchor`, `check_bytecopy`, `check_degen_prefix`,
`check_bounds`, `check_purity`, `binding_rows`, `binding_summary`,
`lane_jump_table`, `turn_cut_row`, `context_deltas`, `check_band`,
`check_export_pins`).

- **`tools/make_corner_timeline.py`** — the ten-lane plan (a pure function of
  the pinned constants, the pre-registered turn ticks, the pair axes and the
  two declared models: Model-A lanes call the banked v10 `lane_tick`
  verbatim; Model-B lanes apply the settle-hold substitution to its output on
  strafe ticks only) and the deterministic sheet: per pair section, lane
  label + RULER + Z1/Z2 rows (21 columns t01..t21) over the lane window
  (turn lanes 2×2 tiles; DEGEN the banked 3-tile axis window); CUT 3X zooms
  (CORNER t13|t14|t15|t16, REMEDY turn−1|turn|turn+1, CONTROL t14|t15|t16);
  WRAP 2X strips (t13..t16; CONTROL t14..t17); a **CORNER vs CONTROL** 2X
  comparison band (absolute ticks t12..t18, tick-for-tick); a **REM_MID vs
  v10-MID** 2X comparison band (absolute ticks t05..t15, the settle-hold
  beside the banked cycling treatment — the v10 lane composed in-process from
  the banked v10 plan, an aid rather than a new measurement); the rendered
  CONTEXT 2X row; FILM rows. Machine-readable cell manifest. Optional APNG
  aids (`corner-lanes-<pair>.apng`: CORNER | REM_EARLY | REM_MID | v10-MID |
  CONTROL side by side, t00..t29, exact 1/60 s per-tick delays, 4x NN,
  banked encoder).
- **`tools/corner_metrics.py`** — jump tables, cut extraction, context
  deltas, the anchor map (bars 1–12, including the committed-v10 regression
  read at runtime), the binding tables, tick math, bounds, export pins,
  determinism, purity, M1; `--check` enforcing the INTEGRITY/MEASUREMENT
  split with named failures.
- **`tests/test_corner_tools.py`** mirroring `tests/test_turn_tools.py`:
  synthetic fixture (per-pose rects IDENTICAL across facings, f3 == idle) so
  the anchor bars are exercised in their FAILING direction on synthetic bytes
  while structure passes; plan invariants with hand-computed vectors; every
  check in pass AND fail directions; skip-guarded committed-artifact
  regressions that never assume the unmeasured remedy-cut numbers.

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default seat) of
the rationale + measured evidence + provisional rubric verdicts, ≤ 8k total
tokens, single call; response redirected to a file and read as explicit
UTF-8; every council numeric claim RECOMPUTED against pixels/numbers before
adoption; every REFUTED verdict re-verified against the primary evidence
(v5–v10 precedent: fabricated precision under adversarial framing).

## Stop conditions

One measurement cycle: zero new creature frames, zero new exports, one
deterministic sheet (byte-identical on regeneration), one metrics JSON,
optional APNG aids, one banked verdict with 2 corner + 4 remedy sub-verdicts
plus the regression gate and the corner-vs-CONTROL note, findings routed
engine-side, one next hypothesis. Change sets: (0) the executed step-0 re-pin
(`f0774a3`, committed alone); (1) this rationale + toolchain + tests; (2)
metrics + sheet + aids + verdict after council + vision critique. Gate re-run
immediately before banking. Push after banking (pre-push = LFS preserve +
full gauntlet). Stop after the verdict is banked and pushed, whichever way
the sub-verdicts land.
