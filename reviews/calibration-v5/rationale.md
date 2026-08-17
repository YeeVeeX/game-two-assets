# Calibration v5 — recovery/follow-through readability rationale

Sprint-5 question (the banked v4 next-hypothesis, elevated from the council
Q6 catch): does a distinct follow-through pose during the pinned 8-tick
recovery make the locked state readable against ready-idle on the lane-B
body at native 1x — without confusing with the coil (a0) or the strike
(k0)? Sprint 4 banked that the recovery span is **invisible today**: the
runtime draws the rest pose at rest position for all 8 recovery ticks, so
"recovering" is visually identical to "ready idle" and the −6px return
snap is the only event boundary. Scope: `player_1_lane_b` only; the v0
idles, v1 walks, v2 strike keys, and v3 coils are frozen inputs; **at most
2 new frames** (`player_1_lane_b_attack_{down,right}_r0`) are the only new
pixels this sprint. No game-two code runs; nothing in `../game-two`
changes.

## Precise lock semantics (the hypothesis wording, verified at the pin)

All verified read-only via `git show` at the pinned game commit
`b7d442f4…` (re-pinned at step 0, all five source hashes LF-identical,
four timing values re-verified):

- During `attack_state == :recovery` the creature **cannot attack**
  (`creature.rb` `start_attack`: requires `:idle` + `exhaust_ready?`) and
  **cannot dodge** (`dodge`: requires `@attack_state == :idle`), but
  **can walk** (`step` blocks only `%i[windup active]`). Recovery =
  attack/dodge locked, movement allowed — never "cannot act".
- **Recovery is invisible today:** `renderer.rb` `lunge_offset`
  else-branch draws recovery at `[0,0]`; `draw_attack` overlays windup/
  active only. Nothing on screen distinguishes the 8 recovery ticks from
  idle.
- **State machine:** `begin_action` → windup(5) → active(4) →
  recovery(8) → `interrupt_action!` → `:idle` (`advance_attack_state`;
  each state drawn exactly its configured tick count). The owner-approved
  `load_hp!` seam touches none of this.
- **Exhaust tail, DECLARED EXCLUSION:** `/kits/striker/attack/
  exhaust_frames = 35` — the attack lock outlasts recovery by ~18 ticks
  during which the creature is `:idle` (no attack_state to hang a pose
  on). r0 marks the **recovery state only**; full attack-lock visibility
  is impossible with attack_state alone. Recorded as context, not defect.
- **Moving recovery, DECLARED:** walking is legal during recovery, so an
  integration design must choose pose priority (walk frames vs r0) for a
  moving-recovery creature. The canonical timeline models stand-still
  recovery; pose priority is a recorded integration finding, not sheet
  scope.

## KB grounding (re-verified in the vault this session)

- KB `game-research/pixel-art-pygame-and-2d-engine-reference.md`,
  Animation Timing Reference (verified 2026-04-10; re-read 2026-08-18):
  "Attack follow-through: ~150ms hold", and the non-uniform-timing table:
  "Follow-through | ~150ms | Hold conclusion frame to emphasize weight."
  At the unoverridden 16.666666 ms tick, recovery 8 ticks ≈ **133.3 ms —
  inside the ~150 ms follow-through band.** Unlike v4's below-band windup,
  **duration is not the risk here; pose distinctness is.** A held
  conclusion frame is the correct native unit — no new timing constant is
  consumed.
- KB `game-research/aseprite-pixel-art-mastery.md` §7.6 (re-read
  2026-08-18): smear frames remain out of scope (in-flight motion
  vocabulary, not a held settle).
- The banked grammar doctrine (v3/v4): a0 owns "mass bunched low+back /
  retraction" (loading); k0 owns "gape + brace/stretch" (release). r0
  must own a **third dimension** reading as spent/settling.

## The incumbents and the burden of proof (A / R / C)

The v4 timeline protocol extends to a three-way recovery comparison under
identical pinned timing; all three timelines share the **banked-winner
grammar** for every non-recovery span (a0 held at −3 for the 5 windup
ticks, k0 at +6 for the 4 active ticks — the v4 timeline-B result, which
needs no re-test), so **the only variable is the recovery-span pose**:

- **Timeline A (incumbent):** recovery = idle at offset 0 — the v4-banked
  treatment whose recovery span is invisible. If R does not beat A, the
  sprint answer is REJECT and the recovery stays invisible at asset level
  (engine-side cue recorded as the finding).
- **Timeline R (candidate):** r0 held at offset 0 for the 8 recovery
  ticks.
- **Timeline C (cheap alternative, tested honestly):** a0 **reused** as
  the recovery pose at offset 0 — zero new pixels. **The a0-reuse risk,
  pre-registered:** v2 banked that the ±3px offset alone is subthreshold,
  so if a0 appears post-strike the player likely reads the POSE — i.e.
  "coiling again", a grammar **inversion** (loading vs spending). The
  expected outcome is that C fails rubric line 2. If C passes everything
  and R adds nothing material, **C wins and r0 is not banked** — an
  honest outcome.

The two boundaries this sprint exists for: **k0→recovery** (release→
settle, t23→t24, the −6px return + pose change) and **recovery-end→idle**
(the "ready again" beat, t31→t32 — in R a pose-only boundary at constant
position; in A it does not exist).

## r0 design doctrine (fixed before pixels; iterated against the bars, the bars may not move)

Shared constraints (inherited, unchanged): 32x32 RGBA8, hard alpha,
pixels inside `[2,2,29,29]`, anchor `[16,30]`, the frozen 5-color ramp
(`#140e0c`, `#401c10`, `#8c3818`, `#eb7828`, `#ffa050`), no new colors,
feet row 27 ±1, head/eye cluster byte-exact under rigid translation at a
declared (dx,dy) per facing (test-enforced), **no jaw gape** (k0's
exclusive marker), generic IDs.

The third dimension r0 owns: **weight collapsed forward-and-down off the
strike line** — mass spent and dispersing, against a0's gathered spring
and k0's directed reach.

- **Down r0 (settle-slump, off-axis):** head block = frozen idle_down
  rows 4–14 rigidly translated **(+2,+3)** — a lateral+down slump. The
  lateral axis is virgin for down states (idle/a0/k0 are all symmetric at
  x=0; walks translate the whole body ±1 but never combine a head drop
  with asymmetric legs). Magnitude +3 sits between k0's +2 and a0's +4 —
  the lateral component, not the drop alone, carries the separation
  (pairwise translations on the shared y-axis measured confusable at
  design time; see estimates). Body: a low 13–14-wide slab sagged toward
  the shaded side (rows 18–22), mass pooled at the base. Legs asymmetric
  mid-return: left leg planted home at the idle columns (12–14), right
  leg still at the k0 splay column (19–21) — a freeze-frame of "legs
  returning from splay", a combination no frozen down frame occupies.
  Jaw closed; the byte-exact face stays front-on (no turn implied).
- **Right r0 (forward overshoot):** head block = frozen idle_right dome+
  eye rows 4–9 rigidly translated **(+1,+4)** — dipped forward-and-down,
  the **+x head axis is virgin** (a0 retracted −2; k0 and every walk hold
  the idle head columns). Momentum spent toward the target: nose low over
  the front feet, back line sloping down toward the front, **tail raised
  2 rows** (rows 14–18 vs idle 16–20 — follow-through weight-tip; every
  frozen frame keeps the `oss` tail at idle rows). Legs carried 1px
  forward of idle (rear 11–13, front 19–21 — between idle 18–20 and k0's
  21–23 reach). Jaw/snout closed (`kk` eye block byte-exact; no `kkkk`
  gape).

Nearest confusables, designed against explicitly:

- **vs a0 (grammar inversion, THE failure mode):** down — a0 is symmetric,
  bunched (12-wide bulge, folded 3-row legs at idle columns, head (0,+4));
  r0 is off-axis (+2 lateral), spread at the base, legs asymmetric with
  4-row height. Right — a0 retracts (−2,+3) with tail at idle rows and
  legs gathered inward; r0 overshoots (+1,+4) with tail raised and legs
  carried forward. Retraction vs overshoot is the axis-level opposition.
- **vs k0:** down — k0 is the symmetric 16-wide brace with splayed legs
  and head (0,+2); r0 is narrower (13–14), lower, off-axis, legs
  half-returned, no gape. Right — k0 stretches (head at idle columns
  (0,+3), gape, front leg 21–23, level back); r0 dips below it (+1,+4)
  with a closed snout, raised tail, and front leg pulled back to 19–21.
- **vs idle/walks:** the head drop (+3/+4) exceeds every walk's ±1
  vertical; the asymmetric legs (down) and raised tail + forward stance
  (right) occupy dimensions no walk frame uses; walks translate the body
  rigidly, r0 reshapes it.

Design-time spec-level estimates (analysis, not evidence — the banked
bars are judged on export bytes by the new metrics tool):

| delta (100·XOR/union) | down r0 | right r0 |
|---|---|---|
| vs idle / f3 | 37.1 | 37.6 |
| vs f0, f1, f2 | 42.8, 41.4, 34.2 | 41.3, 41.4, 41.3 |
| vs a0 | 27.9 | 29.6 |
| vs k0 | 27.1 | 29.9 |
| mass drift vs idle | −4.0% | −8.5% |

The estimates clear the floors by 2–5pt and the ceiling by ~1.7–3pt —
the ceiling approaches (42.8 down-vs-f0, 41.4 right-vs-f1) are the
closest structural risks and are disclosed up front; identity is carried
by the byte-exact head machinery, the unchanged ramp, and the kept `oss`
tail marker (right). This sprint may honestly REJECT.

## Timeline design (fixed before any artifact exists)

**Cadence: 1 column = 1 tick** (the v4 convention, unchanged). The tick
plan is a pure function of the pinned constants (0-indexed):

| ticks | phase | count | pose (all timelines) | recovery-span pose | position |
|---|---|---|---|---|---|
| t00–t01 | idle_pre | 2 (declared context) | idle | — | 0 |
| t02–t14 | walk | 13 = `step_frames` | f0..f3 (banked v1 convention) | — | round_half_up(32·smoothstep(k/13)) |
| t15–t19 | windup | 5 = `windup_frames` | **a0** (banked v4 winner) | — | 32 − 3 |
| t20–t23 | active | 4 = `active_frames` | k0 | — | 32 + 6 |
| t24–t31 | recovery | 8 = `recovery_frames` | — | **A=idle, R=r0, C=a0** | 32 (offset 0) |
| t32–t33 | idle_post | 2 (declared context) | idle | — | 32 |

All v4 declared conventions carry unchanged: walk-frame mapping
f0×4/f1×3/f2×3/f3×3 (review convention, not an engine contract);
round_half_up integer positions; windup begins the tick after arrival;
2-tile grid-lined world windows per cell (approach over origin→stand,
attack over stand→target, overlap column t14); hitstop/exhaust/action-
tile overlay excluded as before (identical across A/R/C, so none can
bias the comparison).

**Sheet structure, per facing:**

- RULER rows: phase labels + per-tick indices (both row groups).
- APPROACH rows (t00–t14; identical in all timelines so one row per
  zone): Z1, Z2.
- ATTACK rows (t14–t33): Z1 A/R/C, Z2 A/R/C — stacked for direct
  comparison, both zone palettes.
- 2X row (timeline R, Z1): the four boundary ticks — t23 (last active),
  t24 (first recovery), t31 (last recovery), t32 (first idle) — the two
  boundaries under test at 2x, diagnostic.
- FILM rows (Z1, Z2): the static strip idle | f0–f3 | a0 | k0 | **r0**
  over exact zone palettes (the v3 style, extended by one column).
- DIFF row: r0 vs idle, every walk frame, a0, AND k0 at 2x
  (`diff_pixels`, derived diagnostic — not a creature cell).
- GRAMMAR row (Z1): **seven cells** — idle | f1 | a0 | a0@−3 | k0 |
  k0@+6 | **r0@0** — the banked `tell_cell` control row extended with
  the recovery state at its runtime draw offset (0).

No FLICKER/ACC rows (the v3 adoption condition was MET at sheet level in
v4 — do not re-test) and no EXP row (recovery duration is inside the KB
band; duration attribution is not in question).

**Viewing aids (optional, never blocking):** one APNG per facing —
timelines A | R | C side by side, full 34-tick sequence over a 3-tile
window, 4x nearest-neighbor, exact 1/60 s per-frame delay (the banked
encoder), 0.5 s final hold, infinite loop. Byte-identical on regeneration
or dropped.

**Critique method:** the committed sheet is the single reviewed artifact;
the vision pass may additionally read deterministic band crops of the
same committed bytes at native scale (ephemeral diagnostics, never
separately banked evidence). Judged at native 1x on the session vision
model (verify `PI_MODEL` is Fable-5-class); the council seat stays
cross-vendor.

## Pass bars (fixed now, before any pixel or sheet exists)

Machine-checkable (`tools/recovery_metrics.py --check`, exit nonzero on
any failure):

1. **Static distinctness (export bytes):** per facing — confusability
   floors, all ≥ **25.0%**: r0 vs idle AND every walk frame; **r0 vs a0
   (separately pre-registered — grammar inversion is THE failure mode)**;
   r0 vs k0. Identity ceiling: every r0 delta < **44.44%** (the banked
   cross-facing reference). Feet-contact row within ±1px of the idle's
   row 27. (Head-block byte-exactness at the declared (dx,dy) per facing
   and ramp identity are test-enforced.)
2. **Compositor byte-determinism:** the timeline sheet, metrics JSON, and
   any APNG aid are SHA-256-identical across two independent in-process
   builds, and committed artifact bytes equal a fresh build.
3. **Composition purity:** every creature cell on the sheet equals a
   banked export's opaque pixels blitted at the computed integer offset
   over freshly reconstructed pinned-palette tiles — machine-compared per
   cell against export bytes (v0–v5); no repainting, no resampling, no
   new colors. The DIFF row is a derived diagnostic, declared, not a
   creature cell.
4. **Tick math exact:** recovery cells = **8 at offset 0 in ALL three
   timelines**; timelines tick-identical except the recovery-span pose
   (A=idle, R=r0, C=a0); windup 5 at −3 (pose a0 in all three), active 4
   at +6 (k0), walk cells = 13 at independently recomputed smoothstep
   positions.
5. **Export pins:** every export consumed hashes to its banked
   release.json SHA-256 (v0–v3 + the new v5); calibration-v5 release
   manifest complete and gate-valid (full hash chain, provenance origin
   `procedural`, derivation notes) at the live pin.
6. **Regression:** banked sheets v0, v1, v2, v3, v4 regenerate
   byte-identical under the extended toolchain; `tools/` coverage ≥ 80.

Perceptual rubric (pre-registered, critique-blocking; accuracy and
presentation scored separately; judged at native 1x on both zone
palettes, both facings):

1. **The recovery span in timeline R is READABLE:** scanned per tick,
   "settling/spent" is distinguishable from ready-idle where timeline A's
   recovery span is invisible (the banked incumbent finding).
2. **r0 does NOT read as a second windup or a strike:** judged directly
   against the a0 and k0 columns on the same sheet; and timeline C is
   judged for the pre-registered inversion — does a0-at-rest post-strike
   read as "coiling again"?
3. **The k0→recovery boundary reads as release→settle** (energy
   dissipating, causally continuous), and **the recovery-end→idle
   boundary is a perceptible "ready again" beat** in timeline R (in A it
   does not exist — that is the point).
4. **The full five-state grammar** idle → walk → a0(−3) → k0(+6) →
   r0(0) → idle **reads as ONE causal action with a visible completion**,
   both facings, both zones.
5. **Identity:** the same creature throughout (byte-exact head machinery
   + unchanged ramp carry it).

**Decision rule (fixed):** R wins only if lines 1–5 pass AND R beats both
A (readability) and C (semantic correctness). C winning with zero new
pixels, or a full REJECT (recovery stays invisible at asset level;
engine-side cue recorded as the finding), are both legitimate sprint
answers — no rescue edits to frozen frames, no invented runtime values,
no smear frames.

Scope discipline carried from v4: "reads at combat speed" is never
claimed from a static sheet — claims are per-tick legibility +
single-tick recognizability + A/R/C superiority under identical pinned
timing; the runtime replay capture stays an INTEGRATION item (blocked by
the one-way boundary), not a sprint hypothesis.

## Toolchain plan

At most 2 new tools; banked helpers imported unmodified
(`png_reader`/`png_writer`, `make_contact_sheet` tile drawing,
`make_feedback_sheet.flash_sprite`/`tell_cell`,
`make_motion_sheet.diff_pixels`, `motion_metrics.frame_stats`/
`pair_stats`/`load_opaque`, `make_grammar_timeline` compositor pieces,
`timeline_metrics.TICK_MS`):

- `tools/make_recovery_timeline.py` (new, tested): the A/R/C tick plan
  (pure function of the pinned constants), the timeline sheet with
  FILM/DIFF/GRAMMAR/2X rows, the cell manifest, and the APNG aids.
- `tools/recovery_metrics.py` (new, tested): the static distinctness
  suite in the `anticipation_metrics` pattern (r0 vs all six confusables
  + a0 separately), the displacement/boundary profile, and `--check`
  enforcing bars 1–5.

Sprint 5 DOES produce a release: `sources/calibration-v5/specs/*.json` →
`tools/build_sources.py`/`aseprite_build.lua` → `tools/export_assets.py`
(SHA-pinned — never edited) → `exports/calibration-v5/release.json` via
`tools/make_release.py` (registry append, trailing closers re-emitted
exactly). Tests cover every new deterministic behavior; the banked-sheet
regressions keep passing.

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default
seat) of the rationale + measured evidence + my provisional rubric
verdicts, ≤ 8k total tokens; response redirected to a file and read with
explicit UTF-8; every council claim re-verified against pixels/numbers
before acceptance (models see text, not pixels).

## Stop conditions

One asset cycle: at most 2 new creature frames (the r0 pair), one
deterministic timeline sheet, optional APNG aids, one banked verdict.
No lore, no 8-direction sets, no smear frames, no exhaust-state pose, no
terrain/enemies/pack, no runtime integration, no game-two changes, no
Bedrock generation. Timing constants read-only from the pinned commit;
no new constant consumed. Change sets: (0) conditional re-pins alone;
(1) this rationale + specs + sources + release + toolchain + tests;
(2) timeline sheet + metrics + verdict. Stop after banking the sprint-5
verdict.
