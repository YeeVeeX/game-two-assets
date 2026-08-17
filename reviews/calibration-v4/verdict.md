# Calibration v4 — temporal grammar verification verdict

Reviewed artifacts:

- `reviews/calibration-v4/timeline-sheet.png` — SHA-256
  `ec8b62ab63b7568d00a9ace2d58694e7b78d3b42b74185322469d899f9f0f123`,
  regenerated twice byte-identically (in-process double-build in
  `timeline_metrics --check` plus a full CLI re-run compared with `cmp`).
- `reviews/calibration-v4/timeline-metrics.json` — SHA-256
  `9bc0e2f6ddc6303779e555ef07a69633f16434229063cecb7e388e4c8250b5c3`,
  regenerated twice byte-identically.
- Viewing aids (non-blocking): `timeline-ab-down.apng`
  (`000ac5fdf49db7d1…`) and `timeline-ab-right.apng` (`6b96285f9a0d…`) —
  timelines A|B side by side, 34 frames, exact 1/60 s per-frame delay
  (APNG rational delays; the v1 GIF method quantizes to centiseconds),
  0.5 s final hold, infinite loop, 4x nearest-neighbor. Byte-identical on
  regeneration, structure machine-verified (acTL/fcTL/fdAT sequence and
  delays asserted by test); they carry the combat-speed viewing for the
  owner and are never the blocking evidence.
- **No new release**: this sprint composed banked bytes only — the
  `make_release.py` registry is untouched; zero new creature pixels
  (machine-enforced, below).
- Banked inputs (untouched): calibration-v0 idles, v1 walks, v2 strike
  keys, v3 coils. All four banked sheets regenerate byte-identical under
  the extended toolchain (existing regression suites, all green).
- Baseline: one owner-approved conditional re-pin executed at step 0
  (game HEAD moved to `6a5e0df0…`, v18 docs-only commits; all five pinned
  source hashes LF-identical, plus `combat.json` / `window.rb` /
  `grid_walker.rb` spot-verified identical for the timing capture).
  At banking time HEAD is still `6a5e0df0…` and **committed content
  matches all five pins**; the parallel v18 session holds an uncommitted
  `creature.rb` seam (`load_hp!`, +9 lines, draw-path-irrelevant) in its
  worktree — reported as a gate warning under the committed-content
  semantics adopted this session (owner directive 2026-08-18: sessions
  run in parallel; committed HEAD content decides, worktree edits and
  identity drift warn). The owner pre-approved the content re-baseline
  for that seam; it executes at the next checkpoint once the sibling
  commits. Live gate exit 0 at step 0 and immediately before banking.
- Vision-critical judgment: session model `us.anthropic.claude-fable-5`
  (verified from `PI_MODEL`, not self-report). Judged on the committed
  sheet plus deterministic band crops of the same bytes (ephemeral
  diagnostics, regenerated from the committed PNG; native 1x decides).
  Council seat cross-vendor (Kimi K2.5), one consolidated adversarial
  verdict, 2,846 tokens of the 8k cap (1,244 in / 1,602 out, single
  call), response archived to file and read as UTF-8.

Question under test (banked v3 next-hypothesis + council anchoring risk):
does the held coil at the pinned −3px windup offset, followed by k0 at
+6px, read as tension→release at combat speed on the lane-B body at 1x —
and does the 9px windup→lunge excursion read as attack motion, not
position error? The comparison that decides value: timeline B (coil held)
versus timeline A (idle held — the v2-banked subthreshold incumbent
treatment) under identical pinned timing.

## Accuracy — all-must-pass

| Item | Verdict | Evidence |
|---|---|---|
| Compositor byte-determinism (sheet, metrics, both APNGs) | PASS | double-build SHAs above; `--check` determinism bar; committed bytes equal fresh builds |
| Composition purity: every creature cell = banked export bytes at the computed integer offset over pinned-palette tiles | PASS | 314 cells, dual per-cell verification (region reconstruction + direct export-byte pixel equality), 0 failures |
| Tick math exact: 5/4/8/13 cells; offsets −3/+6/0; A≡B except windup pose; walk = independently recomputed smoothstep | PASS | `timeline_metrics --check`, 0 failures |
| Zero new creature pixels: every consumed export SHA-256 equals its banked release.json pin | PASS | 14/14 files verified against v0–v3 manifests |
| Timing captured read-only, additive, cited to exact lines/pointers | PASS | `attack_timing` block in `render-reference.json`; `runtime-baseline.json` touched only by the step-0 re-pin commit |
| Pass bars pre-registered before artifacts existed | PASS | rationale + toolchain committed (change set 1) before the sheet was generated (change set 2) |
| Banked v0/v1/v2/v3 sheets byte-stable under the new toolchain | PASS | full suite green (133 tests incl. the four regression suites) |
| Tools coverage ≥ 80 (`.coveragerc`) | PASS | 95% total; new tools 99% / 93% |
| Live gate at the pinned commit | PASS | exit 0 at step 0 and immediately before banking |
| No game-two changes | PASS | read-only `git show` against `../game-two` only; its untracked drafts belong to a parallel session |

**Accuracy: 10/10.**

## Presentation — temporal rubric at native 1x

Measured evidence (`tools/timeline_metrics.py`; ticks are the contract,
ms derived from the unoverridden 16.666666 ms default):

| Metric | value |
|---|---|
| windup / active / recovery / step | 5 / 4 / 8 / 13 ticks (83.3 / 66.7 / 133.3 / 216.7 ms) |
| KB anticipation band | 100–200 ms — **the pinned 83.3 ms hold sits below it** (pre-registered finding space) |
| walk per-tick displacement | 1,1,2,3,4,3,4,3,4,3,2,1,1 px (smoothstep ease-in/out, max 4) |
| windup entry / release / recovery return | −3 / **+9** / −6 px, each in a single tick |
| release vs max walk speed | 2.25× — the sharpest motion in the sequence |
| k0 landing at +6 vs target tile | leading edge **2px (down) / 3px (right) inside the target tile**, crossing its boundary grid line (derived from banked bboxes + pinned offsets, visible in the 2X row) |
| a0 retreat at −3 | leading edge 7px (down) / 8px (right) short of the boundary |
| ACC flicker (pinned 3-on/3-off) | 6 of 12 ticks ON; eyes/feet accents survive every ON tick: 14 px (down) / 10 px (right); accent-vs-crimson contrast 3.33 (≥ WCAG non-text 3:1, banked v3) |

Rubric line by line (pre-registered; judged on the committed sheet at
native 1x, both zones, both facings, with 2x zooms for diagnosis):

1. **The coil hold reads as tension, not freeze.** PASS at sheet scope.
   Timeline B's five windup cells show a single-tick-recognizable state
   change (head dropped onto the bunched body / retracted low slab) held
   steady, bracketed by visibly different states — walk-arrival rest
   before, the 9px gaped release after. The hold reads as "loaded"
   because the pose itself is the signal; it does not depend on
   accumulating duration. Disclosed honestly: at 83.3 ms the real-time
   window is below the KB band, and a static sheet proves per-tick
   legibility plus single-tick recognizability — **not** temporal
   integration under motion (council correction adopted; see
   reconciliation and the integration item).
2. **Timeline B beats timeline A as a windup tell.** PASS, decisive, in
   both facings and both zones. A's windup span (idle at −3px — the
   incumbent treatment) is near-invisible at 1x: five cells that read as
   "standing", confirming the v2 subthreshold finding at temporal
   cadence. B's windup span changes silhouette at T15 and stays changed.
   Scope precision (council): A and B share k0/recovery by design to
   isolate the windup variable; A's non-windup phases are already richer
   than today's pose-less runtime, so B-beats-A **understates** the gap
   to the true incumbent on everything except the windup segment, which
   is exactly the segment under test.
3. **The +6px release snap reads as attack motion, not position error.**
   PASS at sheet scope, both zones. The anchoring geometry is now
   measured, not asserted: the coil holds 7–8px short of the target-tile
   boundary, then the strike's leading edge lands 2–3px **inside** the
   target tile, crossing its drawn grid line — the displacement has a
   destination, and the directional pose (gape down-screen / stretch
   right with forward reach) explains it as a lunge. The sheet omits the
   runtime's target-tile overlay and hitstop (declared) — both would add
   anchoring context, so the sheet is the conservative case. Residual
   risk at 60 tps (a 9px + full-pose single-tick change under motion)
   is recorded as the runtime confirmation item.
4. **The full sequence reads as one causal action.** PASS. idle →
   ease-in/out approach (no per-tick pop exceeds 4px) → arrival on the
   rest pose → coil recoil → boundary-crossing strike → return to rest:
   scanned at the tick cadence the sheet reads as
   approach-coil-strike-settle in both facings; the release is the
   sharpest motion on screen (2.25× max walk speed), which is the
   correct salience for the strike. The GRAMMAR control row ties the
   sequence to the banked v3 static verdict.
5. **(Optional, non-blocking) ACC flash-accent under the real cadence.**
   SURVIVED — the v3 adoption condition is met at sheet level. In the
   ACC row identity persists through the full 3-on/3-off cycle: eyes and
   feet caps are present on every crimson tick (counts above), so the
   face never disappears; in the plain FLASH row the face vanishes for
   every 3-tick ON span. Adoption for a future integration design is
   re-affirmed; live-flicker confirmation in a replay capture remains
   the final step (temporal integration is unprovable on a sheet).

**Presentation scores (accuracy scored separately above):**

- **Timeline B (down): 8.5/10.** The A/B windup differential is the
  cleanest visual argument any sheet in this project has produced; the
  release geometry lands measurably inside the target tile.
- **Timeline B (right): 8/10.** The retraction+compression read is
  clear but subtler against the already-low idle; the 3px target-tile
  penetration is the strongest anchoring of the two facings.
- **Sheet as artifact: 8.5/10.** One column per tick with phase-labeled
  rulers makes the temporal structure literal; A-over-B stacking makes
  the comparison a single eye movement.
- **EXP row (scope-corrected):** the 10-tick KB-band hold contains no
  per-tick content difference from the 5-tick hold — so if the runtime
  read fails, the remedy variable is **duration (engine-side)**, not the
  pose (asset-side). It proves remedy attribution, not temporal
  sufficiency (council correction adopted).

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated verdict; every attack re-verified against artifacts and
pinned numbers before acceptance (models see text, not pixels):

1. **Q1 scope honesty — REFUTED my wording, ACCEPTED.** "Reads at combat
   speed" overreaches what a static sheet can prove. Adopted throughout
   this verdict: the sheet proves per-tick screen content, single-tick
   recognizability, and A/B superiority under identical pinned timing;
   temporal integration at 60 tps is supported (APNG aids at exact tick
   timing) but confirmed only by a runtime replay capture — recorded as
   the integration item, exactly as v3's verdict pre-declared.
2. **Q2 fair incumbent — REFUTED as contamination, ACCEPTED as
   precision.** The council read A's shared k0/recovery as inflating the
   incumbent. The isolation was pre-registered (rationale, before
   artifacts): A and B differ **only** in the windup pose because the
   windup tell is the question; k0 was banked in v2. Adopted: the
   decision language now states the comparison isolates the windup
   segment and that A's other phases already exceed the pose-less
   runtime — making B-beats-A conservative for the segment under test.
3. **Q3 anchoring "claimed, not shown" — REFUTED WITH NUMBERS.** The
   landing overlap is derived from banked bboxes + pinned offsets (k0 at
   +6 → 2px/3px inside the target tile; a0 at −3 → 7/8px short) and is
   visible against the drawn boundary grid line in the 2X row.
   ACCEPTED from the same answer: overlay/hitstop omission means the
   sheet is the conservative case, and final anchoring confidence at
   speed belongs to the runtime item.
4. **Q4 onset pop — ACCEPTED as recorded risk.** The idle→coil swap is a
   single-tick full pose change; the sheet cannot prove it registers as
   a crouch rather than a pop at 16.7 ms. Counterweight (measured): the
   recognition window is the 5-tick held span, not the transition tick.
   Recorded under runtime confirmation; an in-between frame is
   next-hypothesis space, not authored.
5. **Q5 EXP attribution — REFUTED my claim, ACCEPTED the correction.**
   "The pose, not the duration, carries the tell" was too strong for
   static evidence. Corrected to remedy attribution (above): the row
   shows the 83→167 ms variable changes only hold length, locating any
   future fix engine-side. Duration sufficiency at 83 ms remains
   hypothesized until the runtime capture.
6. **Q6 unthought risks — three adopted, two refuted with evidence.**
   ADOPTED: (a) *recovery readability* — 8 recovery ticks draw the rest
   pose at rest position, so "recovering (can't act)" is visually
   identical to "idle (ready)"; the −6px return is the only event
   boundary. Elevated to the next hypothesis below. (b) *attention
   economics* — valid for future enemy-side reuse of the grammar;
   for player_1 (the player's own body) gaze-lock at input time is a
   fair assumption, so recorded for enemy adoption only. (c) *genre
   priors / jank at 60 fps* — folded into the runtime confirmation item.
   REFUTED: (d) "coil may read as an unseen walk frame in motion" — the
   coil exceeds the walk's own frame-to-frame envelope against every
   walk frame (banked v3 floors 31.1/36.6 vs 22.09) and appears only
   stationary at the windup offset, a combination no walk cell occupies;
   (e) "offset-pose conflation" — pose and offset are deliberately
   redundant signals of one pinned state machine; redundancy is the
   design, not a confound.

## Decision

**PASS at the pre-registered artifact scope — and the windup hypothesis
now closes at the asset level, both halves held:**

- **v3 (spatial):** the coil is distinct from every walk frame and from
  the strike key at the pinned offsets, under the identity ceiling.
- **v4 (temporal structure):** under the pinned 5/4/8-tick timing at
  one-column-per-tick, the coil-held timeline beats the incumbent
  idle-held timeline as a windup tell in both facings and zones; the
  hold reads as loaded, the 9px release reads as a lunge with a measured
  destination (2–3px inside the target tile, across its grid line); the
  full sequence reads as one causal action; and the ACC accent treatment
  survives the real flicker cadence.

What this sprint does **not** claim (council-corrected wording):
perceptual temporal integration at a live 60 tps — motion fusion, onset
registration, attention under play. That is a **runtime replay capture**
question, now narrowed to exactly those perceptual unknowns: pose
superiority, tick structure, anchoring geometry, and flicker identity
are settled here and need no re-test.

The pinned 83.3 ms hold sits below the KB 100–200 ms anticipation band —
recorded as engine feedback, not an asset defect: the asset-side signal
is single-tick recognizable, and the EXP row locates any future remedy
in the windup duration constant, engine-side.

Status per contract: **selectable candidates only.** No integration —
v18 is open in game-two, which changes nothing: the one-way boundary and
every runtime-integration stop condition in `docs/asset-contract.md`
hold.

## Findings for any future integration design (recorded, no action now)

- **Runtime temporal confirmation (the remaining unknown):** replay
  capture of the real windup→active→recovery cycle with the lane-B
  sprites; confirm (a) the 83 ms coil hold registers under motion, (b)
  the single-tick coil onset reads as a crouch, not a pop, (c) the 9px
  release under the real target-tile overlay + hitstop reads as attack.
  If (a) fails, the EXP-row evidence points the fix at
  `windup_frames`/duration, not at the pose.
- **Anchoring gap:** `data/balance/combat.json` is not hash-anchored by
  `runtime-baseline.json:source_files`. Decision under the owner's
  parallelism directive (2026-08-18): do **not** add this fast-moving
  balance file to the hard-STOP pin set (it is the sibling session's
  active workbench and would multiply drift stops); instead, every
  future re-pin re-verifies the four pinned timing values at the new
  commit (a value-level check, done twice this sprint). The
  `attack_timing` block stays commit-qualified and therefore auditable.
- **Recovery ambiguity (council catch):** recovery is visually identical
  to ready-idle for 8 ticks; if recovery readability matters (input
  denial feedback), it needs either a follow-through pose (asset-side,
  see next hypothesis) or an engine-side cue.
- **Enemy-side reuse:** the windup grammar's attention assumptions hold
  for the player's own body; enemy adoption should re-verify the tell
  under divided attention (it becomes a dodge prompt there).
- **ACC flash-accent:** adoption condition met at sheet level under the
  pinned cadence; confirm once in the same replay capture.

## Next hypothesis (single, for a future bounded sprint — not started)

Recovery/follow-through readability: author one follow-through key per
facing (or test reuse of a0) and re-run this sheet's timeline protocol —
does a distinct recovery pose during the pinned 8-tick recovery (133 ms,
inside the KB ~150 ms follow-through band) make "recovering, cannot act"
readable against ready-idle at 1x without confusing with the coil or the
strike? The runtime replay capture stays an integration item, not a
sprint hypothesis, while the one-way boundary holds.

## Stop

Sprint 4 stops here: one reviewed timeline sheet, one banked verdict,
two non-blocking APNG aids, zero new creature frames, one re-pin commit
plus two bounded change sets. No smear frames, no recovery pose authored,
no 8-direction set, no terrain, no enemies, no pack, no game-two changes.
