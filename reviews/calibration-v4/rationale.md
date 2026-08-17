# Calibration v4 — temporal grammar verification rationale

Sprint-4 question (the banked v3 next-hypothesis plus the council-caught
anchoring risk): does the held coil at the pinned −3px windup offset,
followed by the strike key at +6px, read as tension→release at combat speed
on the lane-B body at native 1x — and does the 9px windup→lunge excursion
read as attack motion rather than position error? Sprint 3 banked the
**spatial** half (coil distinct from every walk frame and from the strike
at the pinned offsets); this sprint tests the **temporal** half with a
tick-accurate, harness-side compositor over banked export bytes and pinned
constants only. Scope: `player_1_lane_b` only; the v0 idles, v1 walk
frames, v2 strike keys, and v3 coils are frozen inputs — **zero new
creature pixels this sprint.** No game-two code runs; nothing in
`../game-two` changes.

## The incumbent and the burden of proof

Sprint 2 banked that the runtime's own windup treatment — the same pose
held at the −3px draw offset — is subthreshold as a windup tell at 1x.
The coil's value-add is therefore proven only by direct comparison under
identical pinned timing:

- **Timeline A (incumbent):** idle held at −3px for the pinned windup
  ticks → k0 at +6px for the active ticks → recovery. This is today's
  runtime behavior mapped onto the banked sprite set: the same rest pose
  a player already watched for seconds, redrawn at the windup offset.
- **Timeline B (candidate):** a0 (coil) held at −3px for the same windup
  ticks → k0 at +6px → identical recovery.

A and B are tick-for-tick identical in timing, position, active pose, and
recovery treatment; **the only variable is the windup-hold pose.** If B
does not beat A, the sprint answer is REJECT and the v3 spatial pass
stands with a recorded temporal limitation.

## Timing capture (read-only, at the pinned game commit `3869958c…`)

All values captured via `git show` at
`3869958c804b87996e03019830d9cdd7aa7397ee` (the `runtime-baseline.json`
pin; worktree tracked-clean). Pinned additively into
`manifests/render-reference.json` as the new `attack_timing` block — the
baseline manifest itself is untouched.

- **Kit identity:** the lane-B `player_1` body is the **striker** kit.
  Evidence: `src/app/renderer.rb@3869958c` L15–20 `KIT_BODY` maps
  `striker` to `Gosu::Color.new(255, 235, 120, 40)` — RGB (235,120,40) =
  `#eb7828` = `runtime-baseline.json role_colors.player_1` and
  `render-reference.json primitive_body.body_rgb`. `data/balance/
  combat.json /pack/members` lists striker as a pack kit. (Possession is
  ring-carried; body color is per-kit, so the asset's color identity maps
  to the striker regardless of which member is initially possessed.)
- **Attack timing** (`data/balance/combat.json`, JSON pointers):
  `/kits/striker/attack/windup_frames = 5`,
  `/kits/striker/attack/active_frames = 4`,
  `/kits/striker/attack/recovery_frames = 8`,
  `/kits/striker/step_frames = 13`.
- **State machine:** `src/game/creature.rb@3869958c` L424 `begin_action`
  (L435–436 `@attack_state = :windup; @state_frames =
  @action_frames[:windup]`), L451–468 `advance_attack_state` (decrement,
  then windup→active→recovery→idle on exhaustion). Each state is drawn for
  exactly its configured tick count; the striker's target arc is `front1`
  — one precise tile ahead (creature.rb L185).
- **Draw offsets:** `src/app/renderer.rb@3869958c` L418–421
  `draw_creature` adds `lunge_offset` to the tween position; L500–509
  `lunge_offset`: windup −3px, active +6px along facing, **else [0,0]** —
  recovery draws at rest position. Constant per state, no tween: the
  windup→active transition is a single-tick 9px jump, and active→recovery
  is a single-tick 6px return. (Offset magnitudes were already pinned in
  `feedback_states.lunge_offset`; this sprint adds the durations.)
- **Walk tween:** `src/game/grid_walker.rb@3869958c` L90–96 `tick()`:
  visual px eases origin→destination with smoothstep (3t²−2t³) over the
  step duration; L35 `step` (refused while moving) passes
  `frames: step_frames`; L80–85 `commit_dash` commits the logical tile
  instantly; L102–103 centers the 28px body in the 32px tile (+2px — the
  same inset as the export canvas, so sprite-canvas origin ≡ tile origin).
- **Tick rate:** `src/app/window.rb@3869958c` header L24–27: "update() =
  exactly ONE sim tick (tick-locked)". No `update_interval` override
  anywhere in the file; the pinned Gosu 1.4.6 gem documents the default as
  16.666666 ms (installed gem `rdoc/gosu.rb` L838–846), ≈60 ticks/s;
  `FRAME_BUDGET_MS = 17` (L34) corroborates. **Ticks are the contract
  numbers; ms figures below are derived from the unoverridden default and
  labeled as such.**
- **Excluded, declared:** hitstop (`/feel/hitstop_frames_hit = 3`) applies
  only on landed hits — the timeline models a whiff into an empty target
  tile; `exhaust_frames = 35` is a post-recovery cooldown outside the
  drawn window; the `draw_attack` action-tile overlay (renderer.rb
  L511–537, translucent WINDUP/SLASH fills) is state-driven context that
  would be **identical in both timelines**, its colors are not pinned in
  `render-reference.json`, and omitting it makes the anchoring test
  strictly harder than the runtime (no target-tile highlight to explain
  the excursion) — a conservative simplification, recorded.

### Anchoring gap (flagged, not fixed)

`data/balance/combat.json` is **not** in `runtime-baseline.json
source_files`, so its content hash is unpinned — the timing values are
anchored to the commit hash only. Recorded as an owner-review
recommendation: add it to the baseline's `source_files` at the next
approved re-pin. This sprint does not edit the baseline beyond re-pins.

## KB grounding (re-verified in the vault this session)

- KB `game-research/pixel-art-pygame-and-2d-engine-reference.md`,
  Animation Timing Reference (verified 2026-04-10; re-read 2026-08-18):
  "Attack anticipation: 100–200ms hold; Attack strike: ~50ms (single smear
  frame); Attack follow-through: ~150ms hold."
- At the derived 16.67 ms/tick: windup 5 ticks ≈ **83.3 ms — below the
  100–200 ms anticipation band**; active 4 ticks ≈ 66.7 ms (slightly above
  the ~50 ms strike); recovery 8 ticks ≈ 133.3 ms (inside the ~150 ms
  follow-through band). **Pre-registered finding space:** if the pinned
  5-tick hold is too short to read as tension, that is a legitimate
  REJECT-or-finding outcome recorded for integration/engine feedback —
  runtime values are never invented or inflated to rescue the read.
- KB `game-research/aseprite-pixel-art-mastery.md` §7.6 (verified
  2026-04-11; re-read 2026-08-18): smear frames "elongate or 'smear' the
  object between two distant positions in a single frame … bridge the gap
  between keyframes." Smears are **finding-space vocabulary only** this
  sprint: if the 9px release jump fails to anchor, the recorded next
  hypothesis is an intermediate/smear frame — not authored now.
- The v3 verdict's banked findings drive the two rubric additions:
  temporal hold proof and displacement anchoring (council catch).

## Timeline design (fixed before any artifact exists)

**Cadence: 1 column = 1 tick, everywhere on the sheet.** No compression;
the tick counts on the sheet are the pinned constants, machine-checked.

The tick plan, pure function of the pinned constants (0-indexed):

| ticks | phase | count | pose A | pose B | position (axis px from origin tile) |
|---|---|---|---|---|---|
| t00–t01 | idle_pre | 2 (declared context) | idle | idle | 0 |
| t02–t14 | walk | 13 = `step_frames` | f0..f3 (convention below) | same | round_half_up(32·smoothstep(k/13)), k=1..13 |
| t15–t19 | windup | 5 = `windup_frames` | **idle** | **a0** | 32 − 3 (offset −3 along facing) |
| t20–t23 | active | 4 = `active_frames` | k0 | k0 | 32 + 6 (offset +6) |
| t24–t31 | recovery | 8 = `recovery_frames` | idle | idle | 32 (offset 0) |
| t32–t33 | idle_post | 2 (declared context) | idle | idle | 32 |

Declared conventions (pre-registered, all identical across A and B so
none can bias the comparison):

1. **Walk-frame mapping is a review convention, not an engine contract**
   (the banked v1 grid-phase-lock finding): frame index =
   floor((k−1)·4/13) for walk tick k — f0×4, f1×3, f2×3, f3×3 across the
   13-tick step. The runtime draws a rect and owns no sprite-frame timing;
   walk cells are approach context, excluded from the A/B verdict. The
   step naturally arrives on f3 ≡ idle (banked byte-identity), so the
   stand pose at arrival is seamless by construction.
2. **Recovery pose = idle at offset 0** in both timelines: the runtime
   recovery offset is 0 (`lunge_offset` else-branch) and idle is the only
   banked rest pose. A dedicated follow-through pose is future-hypothesis
   space, not this sprint's variable.
3. **Integer positions:** round_half_up(v) = floor(v + 0.5) of the
   smoothstep tween — the runtime hands floats to the GPU; a 1x integer
   compositor must land on whole pixels, and the rounding rule is fixed
   here for byte-determinism.
4. **Windup begins the tick after arrival** (t15): the arrival draw
   (t14, f3 ≡ idle at rest) is the attack's starting frame — the tightest
   causal chain the sim allows without inventing input-buffer behavior.

**World windows.** Each timeline cell is a 2-tile window along the facing
axis with the banked grid-line convention (`draw_floor_tile`: 1px grid on
each tile's top/left edge), so every position reads against a fixed tile
grid: approach rows over tiles origin→stand, attack rows over tiles
stand→target (the striker's `front1` tile). The windows overlap at the
stand tile and both groups carry tick labels; the arrival column t14
appears in both groups for continuity (declared overlap). Down-facing
cells are 32×64, right-facing 64×32; the −3 hold and +6 snap are always
judged against the drawn tile boundary they retreat from / cross toward.

**Sheet structure, per facing:**

- RULER: phase labels + per-tick indices (both row groups).
- APPROACH rows (t00–t14; A≡B so one row per zone): Z1, Z2.
- ATTACK rows (t14–t33): Z1 A, Z1 B, Z2 A, Z2 B — A over B, stacked for
  direct comparison, both zone palettes (rubric line 3 is judged in both
  zones).
- EXP row (down facing, Z1 only, labeled on-sheet "NOT RUNTIME"): timeline
  B's attack segment with the windup hold stretched to **10 ticks ≈ 167 ms
  (inside the KB 100–200 ms band)** — duration-vs-pose attribution if the
  pinned 5-tick hold fails to read. Exploration only; proves nothing about
  the runtime.
- FLICKER rows (per facing, Z1, 12 ticks, idle pose held, labeled): the
  pinned hurt-flash cadence (`flicker_period_frames = 3` → 3 on / 3 off)
  as ACC (crimson + frozen-ramp-accent redraw, the v3 exploration
  treatment) over PLAIN (crimson only) — the v3 adoption condition.
  Optional, non-blocking; pose held static to isolate the cadence
  variable (movement/knockback excluded, declared).
- 2X row: the four transition ticks (t19 last windup, t20 first active,
  t23 last active, t24 first recovery) of timeline B at 2x — diagnostic.
- GRAMMAR row: the static v3 grammar cells (idle | f1 | a0 | a0@−3 | k0 |
  k0@+6) via the banked `tell_cell` — the spatial control this sprint
  extends.

**Viewing aids (optional, never blocking):** one APNG per facing —
timelines A and B side by side, full 34-tick sequence over a 3-tile
window, 4x nearest-neighbor, **exact** per-frame delay 1/60 s (APNG
rational delays; the v1 GIF method quantizes to centiseconds, so APNG is
the faithful container), last frame held 0.5 s, infinite loop. Built by
the same compositor from the same banked bytes; byte-identical on
regeneration or dropped.

**Critique method:** the committed sheet is the single reviewed artifact;
the vision pass may additionally read deterministic band crops of that
same PNG at native scale (ephemeral diagnostics regenerated from the
committed bytes, exactly like the banked 2x/4x rows — never separately
banked evidence).

## Pass bars (fixed now, before any artifact exists)

Machine-checkable (`tools/timeline_metrics.py --check`, exit nonzero on
any failure):

1. **Compositor byte-determinism:** the timeline sheet (and any APNG aid)
   is SHA-256-identical across two independent in-process builds, and the
   committed artifact bytes equal a fresh build.
2. **Composition purity:** every creature cell on the sheet equals a
   banked export's opaque pixels blitted at the computed integer offset
   over freshly reconstructed pinned-palette tiles — machine-compared
   per cell against the export bytes; no repainting, no resampling, no
   new colors (permitted treatments: identity, the pinned crimson flash,
   the v3 ACC accent redraw — recolors driven by pinned constants only).
3. **Tick math exact:** windup/active/recovery/walk cell counts equal the
   pinned constants (5/4/8/13); offsets exactly −3/+6/0 along the facing
   axis per state; timelines A and B tick-for-tick identical except the
   windup pose; walk positions equal the independently recomputed
   smoothstep values.
4. **Zero new creature pixels:** every export consumed hashes to its
   banked `release.json` SHA-256 (v0/v1/v2/v3), untouched.

Perceptual rubric (pre-registered, critique-blocking, accuracy and
presentation scored separately; judged at native 1x on the session vision
model, with the cross-vendor council seat adversarial as always):

1. **The coil hold reads as tension** ("about to strike"), not
   freeze/stuck, at the pinned 5-tick cadence — judged on timeline B's
   windup span against its own idle/recovery spans.
2. **Timeline B beats timeline A as a windup tell** — the five B windup
   cells must telegraph in a way the five A cells (rest pose at −3px, the
   v2-banked subthreshold incumbent) do not. If B does not beat A, the
   sprint answer is REJECT; the v3 spatial pass stands with a recorded
   temporal limitation.
3. **The +6px release snap reads as attack motion, not position error**
   (the council-caught anchoring risk): over the grid-lined 2-tile
   windows, the −3 hold → +6 snap must read as a lunge toward the target
   tile, judged in both zones.
4. **The full sequence reads as one causal action:** idle → walk-in →
   hold → release → recovery → idle, scanned at the tick cadence, reads
   as approach-coil-strike-settle, not as disconnected states.
5. *(Optional, non-blocking)* the ACC flash-accent treatment preserves
   identity recovery under the real 3-on/3-off cadence better than the
   plain flash — the v3 adoption condition; failure records the finding
   without blocking the sprint.

A REJECT on any blocking line is a legitimate sprint answer — no rescue
edits to banked frames, no invented runtime values, no smear frames
authored this sprint.

## Toolchain plan

`tools/make_grammar_timeline.py` (new, tested): the tick plan (pure
function of the pinned constants), the timeline sheet, and the APNG aids.
`tools/timeline_metrics.py` (new, tested — the one new metrics/validator
tool): the displacement profile per tick, phase durations vs pins, jump
magnitudes, ACC survival counts, and `--check` enforcing the four machine
bars. Banked helpers imported unmodified: `png_reader`/`png_writer`,
`make_contact_sheet` tile drawing, `make_feedback_sheet.flash_sprite`/
`tell_cell`, `make_anticipation_sheet.accent_flash_sprite`.
`tools/export_assets.py` is never touched (SHA-pinned by every banked
release); no new exports, no release manifest, `make_release.py` registry
untouched. Tests cover every new deterministic behavior; `tools/`
coverage stays ≥ the `.coveragerc` fail_under (80); the banked-sheet
regression (v0, v1, v2, v3 byte-identical regeneration) must keep passing
under the extended toolchain, and the v4 sheet joins it once banked.

## Council plan and budget

One consolidated cross-vendor adversarial review (Kimi K2.5 default seat)
of the rationale + measured evidence + my provisional rubric verdicts,
capped at 8k total tokens; the response JSON is redirected to a file and
read with explicit UTF-8; every council claim is re-verified against
frames/pixels/metrics before acceptance (models see text, not pixels).

## Stop conditions

One asset cycle: zero new creature frames, one deterministic timeline
sheet, optional APNG aids, one banked verdict. No lore, no 8-direction
sets, no smear frames, no terrain/enemies/pack, no runtime integration,
no game-two changes, no Bedrock generation, no new release. Change sets:
(0) conditional re-pins alone if HEAD moves; (1) timing pin + toolchain +
tests + this rationale; (2) timeline sheet + metrics + verdict. Stop
after banking the sprint-4 verdict.
