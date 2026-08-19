# Calibration v8 — walk→attack onset-seam measurement rationale (mid-walk onset classes)

Sprint-8 question (the banked v7 alternative next-hypothesis): the
lane-B attack grammar is CLOSED at asset level (five states, three
bridges, one deliberately-sharp release), and **the walk-phase→w0 seam
is the only pose-only discontinuity class left unmeasured** — every
banked timeline models onset from the f3 arrival tick (t14→t15,
16.48/19.69 at −3px), but the engine legally starts an attack MID-WALK.
Do the onset seams read at native 1x, per tick, without weakening any
banked read — and does the strike keep its salience when it fires on a
moving base? **This is a measurement sprint: ZERO new frames, zero new
exports, zero tick changes. Every pixel is frozen (all 26 banked
export pins across v0–v7); the deliverables are seam timelines, machine
jump tables, and a banked per-onset-class verdict.** No game-two code
runs; nothing in `../game-two` changes (read-only `git show` at the
pinned commit).

A FAIL here is an ENGINE-TERRITORY finding (the v4/v5-banked EXP-row
remedy-attribution class: the failing variable is input timing, not the
pose), recorded as an input-buffering/gating recommendation for the
future runtime-replay integration design — never a rescue frame, never
a smear, never a tick reallocation. Both outcomes are first-class.

## Verified in-tick ordering (game commit `766cfa2e`, read-only)

All citations re-verified this session via `git show` at the live pin
(the step-0 re-pin commit carries the same table; `creature.rb` is
content-pinned — sha256_lf verified by the gate at this commit):

- **World tick order** (`src/game/world.rb` L686–697): first
  `tick_body` for every creature, THEN the seat-ordered
  `controller.tick` loop. So within one world tick the tween advances
  and the attack state decrements BEFORE input fires `start_attack`.
- **`tick_body`** (`src/game/creature.rb` L124–140): `@walker.tick`
  runs unconditionally (L126) — nothing pauses or snaps the tween when
  an attack begins — then `advance_attack_state` (L139).
- **`start_attack`** (`creature.rb` L153–154): refused only for
  dead/staggered/`attack_state != :idle`/exhaust — **there is no
  `moving?` guard**. `begin_action` (L451–467) sets
  `@attack_state = :windup`, `@state_frames = windup_frames`.
- **Controller** (`src/game/controllers.rb` L64, seized branch L46):
  `creature.start_attack if down?(input, :attack)` — fired from held
  input with no tween/moving guard upstream. The step attempt (L56)
  resolves earlier in the same controller tick but cannot interfere:
  `step` is refused while moving (`grid_walker.rb` L35–36) and during
  windup/active (`creature.rb` L146–148).
- **Tween** (`src/game/grid_walker.rb` L90–97): smoothstep
  `3t² − 2t³` eases the visual px over `step_frames` ticks;
  `commit_dash` (L80–88) commits the logical tile at step START, so
  during mid-tween onset the visual body lags the committed tile and
  the front1 attack arc (`creature.rb` L185–186) targets one tile ahead
  of the COMMITTED tile. Engine fact; this sprint measures only its
  readability consequence.
- **State machine** (`creature.rb` L478–498): decrement-then-transition
  — a state set to N frames is drawn for exactly N ticks; windup 5,
  active 4, recovery 8 (`attack_timing` re-verified 5/4/8/13 at
  `766cfa2e`). Draw happens after update (`window.rb` L78–89, one sim
  tick per update, no `update_interval` override).

**Consequences, fixed as tick definitions:** "onset at walk tick k"
means the attack input lands on the world tick whose `walker.tick` was
the k-th tween advance; that same tick draws windup tick 1 (w0) at
tween position pos(k) with the −3 offset. The tween then continues
under the attack (one advance per tick) until arrival; no new step can
begin once windup starts (L147), so each lane contains exactly one
in-flight step and one attack. **If `start_attack` or its callers gain
a moving/tween guard at a future pin, this seam class becomes
unreachable and the sprint's model is fiction — re-verify at every
re-pin (done at 766cfa2e: no guard).**

## Drawing model (pre-registered; the same precedence every banked timeline uses)

`attack_state != :idle` draws the attack-grammar pose for that state's
tick — the banked v7-winner composition: windup = w0 ×1 + a0 ×4 at −3;
active = k0 ×4 at +6; recovery = s0 ×1 + r0 ×6 + x0 ×1 at 0. Walk
frames (banked v1 mapping f0×4/f1×3/f2×3/f3×3 across the 13 step
ticks) draw only on pre-onset ticks. Draw position = tween position +
state offset (renderer.rb: `draw_creature` adds `lunge_offset` to the
tween position — pinned in `render-reference.json`). Seam ticks inside
recovery-overlap draw s0/r0 on the still-moving base under this model;
the recovery-walk pose-priority question (carried v5–v7) is NOT
adjudicated here — every overlap claim is explicitly conditional on
the declared model, and the priority item stays a carried integration
finding. The engine itself draws a pose-less primitive body: the
drawing model is the declared review convention carried from the
v4–v7 banked timelines, not an engine contract.

## Onset classes (pre-registered; one written adjustment from the brief)

Per facing (down, right), attack along the walk direction, facing
preserved. Cross-facing onset is OUT of scope (recorded as a future
class). Walk starts at t02 (walk tick k = t01+k); the 13th advance
arrives at t14 — arrival is absolute t14 in every lane. Onset tick
t_o; windup t_o..t_o+4, active t_o+5..t_o+8, recovery t_o+9..t_o+16,
idle from t_o+17. Tween ticks remaining after the onset tick's advance:
REM = 13 − (t_o − 1).

| class | onset | REM | arrival t14 lands in | moving-base attack ticks |
|---|---|---|---|---|
| EARLY | t03 (walk tick 2) | 11 | recovery tick 3 | windup 5, active 4, recovery 2 (+arrival on rec 3) |
| MID | t06 (walk tick 5) | 8 | active tick 4 | windup 5, active 3 (+arrival on act 4) |
| LATE | t10 (walk tick 9) | 4 | windup tick 5 | windup 4 (+arrival on wind 5) |
| CONTROL | t15 (arrival + 1) | 0 | pre-onset (t14 = onset−1) | none — the banked seam |

**Written adjustment, fixed before any artifact exists:** the brief
sketched EARLY at "~12 remaining" (walk tick 1). Walk tick 1's
onset−1 tick is the idle_pre context tick, so its onset seam pose pair
(idle→w0) is byte-identical to the banked f3→w0 arrival pair (f3 is
the banked idle byte-copy) and measures nothing new. Walk tick 2 is
the earliest onset whose seam cuts a TRUE mid-walk frame (f0→w0,
banked 22.91/28.27 — the unmeasured class the sprint exists for), and
its overlap still reaches recovery tick 3, matching the brief's "~3
recovery ticks". The brief's own claim that "mid-walk classes exceed
the banked f3-arrival boundary" requires a real walk frame at
onset−1, which walk tick 1 cannot supply. EARLY = walk tick 2
(REM 11). The unmeasured sub-cases — onset on the step-initiation tick
(step and attack in the same controller tick, REM 13), onset ON the
arrival tick (REM 0 at t14), and cross-facing onset — are recorded as
future classes, not measured.

## Hand-estimated seam arithmetic (analysis, not evidence — the tool recomputes everything from pinned constants and export bytes)

Tween positions pos(k) = round_half_up(32·smoothstep(k/13)), k=1..13:
1, 2, 4, 7, 11, 14, 18, 21, 25, 28, 30, 31, 32 — per-tick deltas
1,1,2,3,4,3,4,3,4,3,2,1,1 (peak exactly 4 px/tick; the continuous peak
1.5·32/13 ≈ 3.69). Banked pose deltas reused (recomputed from bytes,
never hand-copied into the tool): fN→w0 = v6 walk_deltas (down
22.91/23.49/22.91/16.48, right 28.27/27.51/28.27/19.69); walk pairs =
v1 (down ≤ 19.64, right ≤ 22.09); w0→a0 17.25/20.83; a0→k0
27.18/31.97; k0→s0 15.38/21.31; s0→r0 16.18/14.98.

Per-lane draw positions (axis = pos(clamp(t−1, 0, 13)); draw = axis +
offset; both facings share the axis):

- **EARLY** t01..t16: idle@0 | f0@1 | **w0@−1** | a0@1 | a0@4 | a0@8 |
  a0@11 | **k0@24** | k0@27 | k0@31 | k0@34 | s0@30 | r0@31 | r0@32
  (arrival) | r0@32 | r0@32. Onset seam f0→w0 at Δpos −2; release
  a0@11→k0@24 = **+13 px** (peak tween +4 riding the +9 offset jump);
  k0→s0 = −4 (recoil −6 partially absorbed by tween +2... exact: 30−34);
  recovery overlap rows r0@31 (+1), r0@32 (+1).
- **MID** t04..t19: f0@4 | f0@7 | **w0@8** | a0@11 | a0@15 | a0@18 |
  a0@22 | **k0@34** | k0@36 | k0@37 | k0@38 (arrival) | s0@32 | r0@32
  … Onset seam f0→w0 at Δpos +1 (w0 replaces the f0→f1 frame advance
  that walk tick 5 would have drawn); release +12; k0→s0 = −6 (banked
  value, from rest).
- **LATE** t08..t23: f1@18 | f2@21 | **w0@22** | a0@25 | a0@27 | a0@28 |
  a0@29 (arrival) | **k0@38** | k0@38 | k0@38 | k0@38 | s0@32 …
  Onset seam f2→w0 at Δpos +1, with the real f1→f2 walk cut
  (19.00/22.09) in the adjacent pre-onset column — a built-in native
  comparison of walk noise vs onset signal; release +9 and everything
  after it byte- and position-identical to CONTROL.
- **CONTROL** t13..t28: f3@31 | f3@32 (arrival) | **w0@29** | a0@29 ×3
  … | k0@38 ×4 | s0@32 | r0@32 … — the banked t13..t28 grammar
  exactly; onset seam f3→w0 = **16.48/19.69 at −3px, the hard
  regression bar**, and rows (14,15), (15,16), (19,20), (23,24),
  (24,25) must equal the banked v7 timeline-metrics values exactly.

Estimated salience consequence, pre-registered: in every lane the
release remains the strictly largest pose delta (27.18/31.97 vs
in-lane maxima ≤ 23.49 down / ≤ 28.27 right) AND the strictly largest
displacement (+13/+12/+9/+9 vs ≤ 4 tween, ≤ 6 recoil) — dominance on
both axes separately (no invented combined metric, the banked v6 Q3
correction). The machine table must agree; assume neither answer for
the native read.

## KB re-grounding (re-verified in the vault this session, 2026-08-18)

- `game-research/pixel-art-pygame-and-2d-engine-reference.md` §7.2 /
  §8: anticipation 100–200 ms hold, strike ~50 ms, follow-through
  ~150 ms — the banked v4 strike-dominance doctrine this sprint's
  salience bar reuses ("the sharpest motion in the sequence IS the
  strike"). Unchanged, re-read at source.
- `game-research/technical-drawing-for-game-art.md` §8 (state-machine
  patterns): the standard 2D pattern is EXCLUSIVE animation states
  (IDLE/WALK/ATTACK) — the attack pose replaces the walk wholesale.
  This grounds the declared drawing model (attack pose wins) and frames
  the engine fact under test: this engine lets the walk TWEEN continue
  under the attack states, a compound the standard pattern never
  renders. Whether that compound stays readable is exactly the open
  question.
- **Corpus gap, disclosed (the v7 disclosure class):** the corpus
  carries no doctrine on mid-walk attack onset, input buffering to
  arrival, or attack-canceling readability. Nothing prescribes whether
  a mid-tween onset cut should read or be deferred; this is a genuine
  calibration measurement, and the engine-territory FAIL routing is a
  recommendation space, not settled convention.

## Pass bars (fixed now, before any artifact exists)

Machine-checkable (`tools/seam_metrics.py --check`, exit nonzero on any
failure):

1. **Zero new exports:** `exports/` contains exactly the 26 pinned
   PNGs of the seven banked releases (v0–v3, v5–v7; the brief's "24"
   corrected against release.json ground truth: v0 banks 6 idles across
   lanes a/b/c), every file SHA-256-verified against its release.json
   pin; no `exports/calibration-v8/` exists; the `make_release.py`
   registry and `tools/export_assets.py` bytes untouched.
2. **Seam jump tables:** per onset class, per facing — pose Δ%
   (100·XOR/union on export bytes) AND position Δpx for every
   consecutive tick pair from onset−2 through onset+10 (EARLY: through
   onset+12, covering its recovery overlap and first settled hold
   tick), so every table ends on the s0→r0 seam row; positions computed
   as tween + state offset from independently recomputed smoothstep.
3. **CONTROL regression (hard):** CONTROL's onset row = f3→w0 at
   exactly the banked 16.48 (down) / 19.69 (right) at −3px, and its
   rows (13,14), (14,15), (15,16), (19,20), (23,24), (24,25) equal the
   committed `reviews/calibration-v7/timeline-metrics.json` timeline-B
   values exactly (pose and position).
4. **Release-salience table:** in every lane, both facings, the a0→k0
   tick is STRICTLY the largest pose delta AND STRICTLY the largest
   absolute position delta in that lane's table — dominance on both
   axes separately, machine-compared across all lanes.
5. **Tick math exact:** per lane — windup 5 (w0 ×1 + a0 ×4) at −3,
   active 4 (k0) at +6, recovery 8 (s0 ×1 + r0 ×6 + x0 ×1) at 0, walk
   ticks at recomputed smoothstep positions with the banked frame
   mapping, per-tick tween deltas exactly 1,1,2,3,4,3,4,3,4,3,2,1,1;
   REM per class = 11/8/4/0 with the arrival tick (t14) landing in the
   pre-registered phase (rec 3 / act 4 / wind 5 / pre-onset); no tick
   added, consumed, or reallocated anywhere (the r0-hold floor — 6 held
   ticks — is untouched by construction and asserted).
6. **Determinism + purity:** sheet + metrics + any APNG byte-identical
   across two independent in-process builds and equal to committed
   bytes; every creature cell dual-verified against banked export bytes
   at the computed integer offsets (region reconstruction + direct
   export-byte equality); banked sheets v0–v7 regenerate byte-identical
   under the extended toolchain (existing regression suites); `tools/`
   coverage ≥ 80 (`bin/full_gate.py`).

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone
palettes, both facings; every claim is sheet-scope — per-tick
legibility and single-tick recognizability under identical pinned
timing, never temporal fusion at 60 tps, never "reads at combat
speed"):

1. **Per onset class, the fN→w0 cut reads as attack onset** — the coil
   beginning — not as a sprite error, a flicker, or a new state; judged
   per tick on the stacked lane rows and the 2X onset strips (LATE's
   adjacent f1→f2 walk cut is the in-sheet noise comparison).
2. **The windup/active poses riding the moving base keep their banked
   reads** (w0 rising at −3, a0 telegraph, k0 strike): sub-tile motion
   beneath the pose must not dissolve state identity at 1x.
3. **The strike keeps salience:** on every seam lane the release
   remains the sharpest, most attention-grabbing single-tick event at
   native 1x, and the machine table (bar 4) agrees with the native
   read.
4. **The CONTROL lane reads exactly as banked** — no regression in the
   arrival seam (and bar 3 holds).
5. **Identity holds throughout:** byte-exact frozen frames at computed
   positions, frozen ramp, feet/anchor law within the moving cell.

**Decision rule (fixed):** per-onset-class sub-verdicts, independent.
A class PASSES only if rubric lines 1–3 pass for it AND lines 4–5 hold
sheet-wide; PASS ⇒ the direct cut is banked as the answer for that
class. FAIL ⇒ banked as an ENGINE-TERRITORY finding naming the precise
failing ticks and magnitudes, with an input-buffering/gating
recommendation recorded for the future integration design (e.g., defer
`start_attack` to tween arrival — a game-two decision for AFTER the
cycle closes; never implemented from here, never compensated with
pixels). Both outcomes are first-class. No rescue edits, no new
frames, no tick changes, no smears, no second drawing model.

Scope discipline carried from v4–v7: no temporal/fusion claims (60 tps
questions stay in the consolidated v7 runtime item, whose x0
banking-reversal condition is untouched); the 6-tick r0-hold floor and
every banked stop-condition stand; no cross-facing onset; no
recovery-walk priority adjudication; AD-C1/AD-C2 scope triggers
(effect/feedback frames) are not met this sprint — they do not gate.

## Toolchain plan

Two new tools; banked helpers imported unmodified
(`make_grammar_timeline` compositor pieces: `compose_window`,
`canvas_pixels`, `cell_size`, `smoothstep`, `round_half_up`,
`walk_frame_index`, `draw_text`, APNG encoder + delays;
`make_contact_sheet` tile drawing; `make_feedback_sheet.tell_cell`;
`motion_metrics.frame_stats`/`pair_stats`/`load_opaque`;
`timeline_metrics.TICK_MS`):

- `tools/make_seam_timeline.py` (new, tested): the four-lane tick plan
  (a pure function of the pinned constants + the pre-registered onset
  ticks), per facing — RULER + lane rows (Z1 then Z2, 16 columns
  t_o−2..t_o+13 per lane, 3-tile windows so the arc tile and the
  behind-boundary excursion stay visible), 2X ONSET strips (onset−1 |
  onset | onset+1 per lane) and 2X RELEASE strips (onset+4 | onset+5
  per lane), the banked 11-column FILM rows (identity/context anchor),
  a machine-readable cell manifest, and optional APNG aids
  (`seam-lanes-<facing>.apng`: the four lanes side by side, full
  t00..t33 at exact 1/60 s tick delay, 4x NN, banked encoder).
- `tools/seam_metrics.py` (new, tested): jump tables, CONTROL
  regression against the committed v7 metrics, release-salience
  dominance, tick math + overlap arithmetic, export-pin and
  zero-new-exports enforcement, determinism + purity, `--check`
  enforcing bars 1–6.

Tests in `tests/test_seam_tools.py` mirroring `tests/test_rise_tools.py`
(synthetic fixture + plan/sheet/validator suites + skip-guarded
real-artifact regressions). No release chain this sprint (no exports);
`tools/export_assets.py` is SHA-pinned by every banked release and is
not touched.

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default
seat) of the rationale + measured evidence + provisional rubric
verdicts, ≤ 8k total tokens, single call; response redirected to a file
and read with explicit UTF-8; every council numeric claim RECOMPUTED
against pixels/numbers before adoption (v5/v6/v7 precedent: inverted
metrics and fabricated banking claims under adversarial framing).

## Stop conditions

One measurement cycle: zero new creature frames, zero new exports, one
deterministic seam sheet (byte-identical on regeneration), one metrics
JSON, optional APNG aids, one banked verdict with four per-class
sub-verdicts and the FULL v7 standing findings list carried unmodified
plus the seam findings. No lore, no 8-direction sets, no cross-facing
onset, no terrain/enemies/pack, no runtime integration, no game-two
changes, no Bedrock generation. Timing constants read-only from the
pinned commit; no new runtime constant consumed. Change sets: (0)
re-pins alone per the step-0 protocol (executed: mechanical identity
re-pin to `766cfa2e`, verification table in its commit message); (1)
this rationale + toolchain + tests; (2) sheet + metrics + verdict
(+ APNG aids) after the verdict. Push to origin after banking. Stop
after banking the sprint-8 verdict — the runtime-replay integration
design stays parked until the game cycle closes, whichever way the
sub-verdicts land.
