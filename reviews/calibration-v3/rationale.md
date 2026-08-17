# Calibration v3 — windup-anticipation coherence rationale

Sprint-3 question (the banked v2 next-hypothesis): does a held anticipation
(coil) pose make the windup state readable on the lane-B body at native 1x?
Sprint 2 banked that the strike key reads and that the pinned −3px draw
offset alone is subthreshold as a windup tell. Concretely: (a) one
anticipation pose per facing, static and at the pinned −3px windup offset;
(b) full attack-grammar coherence at 1x — idle → mid-walk → a0 at −3px →
k0 at +6px must read as four distinct sequential states, with a0 confusable
with neither any walk frame nor the strike key; (c) the v2
flash-accent-persistence finding explored as a sheet-level row. Scope:
`player_1_lane_b` only; the v0 idles, v1 walk frames, and v2 attack keys
are frozen inputs.

## Shared constraints (inherited, unchanged)

- 32x32 RGBA8, hard alpha, pixels inside `[2,2,29,29]`, anchor `[16,30]`.
- The frozen 5-color ramp: `#140e0c` accent, `#401c10` outline, `#8c3818`
  shade, `#eb7828` base, `#ffa050` highlight. No new colors in specs or
  exports; flash and flash-accent rows are sheet-level simulations driven by
  pinned runtime constants.
- Generic mechanical IDs: `player_1_lane_b_attack_{facing}_a0`.
- `feedback_states` in `manifests/render-reference.json` already pins every
  constant this sprint touches (hurt flash `(200,30,30)` + 3-frame cadence,
  lunge offsets −3/+6 draw-only, telegraph swell). No new manifest capture
  is expected; `manifests/runtime-baseline.json` changed only in the
  step-0 owner-approved re-pin (game commit `15509d32…`, all five pinned
  source hashes verified LF-identical — content-identical to the capture
  commit `219121d3…`, so every cited renderer line number remains valid).

## KB and corpus grounding (re-verified against the vault this session)

- KB `game-research/pixel-art-pygame-and-2d-engine-reference.md`, Animation
  Timing Reference (verified 2026-04-10; re-read 2026-08-17): "Attack
  anticipation: 100–200ms hold; attack strike: ~50ms (single smear frame);
  attack follow-through: ~150ms hold." The anticipation is a **held** frame
  — a static pose is the correct native unit for it, and the runtime's own
  windup treatment (held body at −3px until the strike) matches. Smear
  doctrine stays with the in-flight swing (out of scope, per the v2
  reconciliation).
- KB `game-research/aseprite-pixel-art-mastery.md` §7.4 + §7.7 (verified
  2026-04-11; re-read 2026-08-17): the compression vocabulary — "'Down'
  frame: character compressed 1–2 pixels (simulates landing weight)";
  boxing-loop table: "'Compression' — knees bend, body drops." The coil is
  this vocabulary pushed to a key pose: body drops, mass bunches low.
- KB `game-research/technical-drawing-for-game-art.md` §4.4 (verified
  2026-04-11): the silhouette test — the windup must read from silhouette
  alone at 1x, because the banked identity mechanism (44.44% cross-facing
  separation) and the hurt flash are both silhouette-only.
- Playbook A §3 (`docs/research/2d-asset-playbooks/`, subordinate to the
  contract): "Animation must read clearly at game size and speed;
  exaggerated key poses are prioritized over subtle detail." The coil is an
  exaggerated key extreme, not interior detail.

## Anticipation pose plan (per facing, derived from frozen frames)

New pixels this sprint: `player_1_lane_b_attack_down_a0`,
`player_1_lane_b_attack_right_a0` — at most these two frames. Design
doctrine: the coil attacks the **height** dimension (body drops, mass
bunches) — the one dimension no walk frame and no strike key owns. The
head/eye cluster — the banked identity anchor — is preserved byte-exact
under rigid translation, machine-verified by test exactly like v2. Feet
stay planted at row 27 (the −3px windup displacement is the pinned
draw-only offset, never pose pixels). The pose vocabulary below is the
starting point; it iterates against `tools/anticipation_metrics.py` before
banking — the coil may move, the pass bars below may not.

- **Down a0 (coil under the viewer-facing pounce):** head block = frozen
  idle_down spec rows 4–14 rigidly translated (0,+4) — a 4px drop, deeper
  than k0's 2px, onto a bunched body. Haunch bulge widens the lower torso
  to 12 wide (cols 10–21) against the idle's 10; legs folded under at the
  idle columns (12–14 / 17–19) with height compressed to rows 25–27; feet
  caps row 27. **No jaw gape** — the open jaw stays the strike's exclusive
  marker; the coil's eyes stay the closed idle face.
- **Right a0 (recoil before the lunge):** head block = the frozen
  idle_right dome+eye rows (the v2-verified rows 4–9) rigidly translated
  (−2,+4) — retracted back AND down, the recoil dimension no walk frame
  and not k0 uses (k0 holds the idle head columns and drops 3px; every
  walk frame holds the idle head columns within ±1px vertical). Body
  compressed to a low slab (~rows 14–24) with a rear haunch ridge (mass
  bunches over the hindquarters); the `oss` tail marker is kept
  (identity); legs gathered ~1px inward vs idle and folded; feet caps
  row 27. The snout stays closed — k0 keeps the `kkkk` gape.

Nearest confusables, designed against explicitly:

- **f1 (pass-high):** whole body up 1px, both feet planted — shares
  planted feet with a0. The coil differs by direction and magnitude:
  f1 rises 1px, a0 drops 4px (5px head separation) and reshapes the
  torso; f1 never changes body width or leg height.
- **f2 gather (right {12–14}/{16–18}, down trailing-foot step):** a walk
  gather moves feet columns only; a0's gather is 1px inward from **idle**
  columns ({11–13}/{17–19}, distinct from f2's), plus folded leg height
  and the dropped head — dimensions the walk never touches.
- **k0 (the strike, same grammar family):** down k0 = 16-wide brace +
  splayed legs + jaw gape at head +2; down a0 = 12-wide bulge + folded
  legs + closed jaw at head +4. Right k0 = forward stretch (front leg
  cols 21–23, snout `kkkk`, head straight down 3px); right a0 = backward
  retraction (head −2 in x, legs gathered inward, closed snout). Related
  silhouettes are expected — windup and strike are two states of one
  grammar; the pre-registered distinctness bar below is the honesty check.

Hand-estimated deltas going in (analysis, not evidence): ~30% vs idle,
~27% vs k0, mass ~−5%. The estimates sit 2–5pt above the floors — this
sprint may honestly REJECT.

## Flash-accent exploration row (ACC) design

The v2 verdict recorded the integration finding: eyes/feet accents vanish
on flicker-on frames; the runtime redraws its facing notch over the flash
(renderer.rb L470–480 + L484–496 pattern), so a sprite integration should
redraw accent pixels over the flash fill. The ACC row simulates exactly
that, using only pinned values:

1. full pinned-crimson fill `(200,30,30)` on every opaque pixel — the v2
   `flash_sprite`, the renderer's own flicker-on treatment;
2. redraw the pixels whose **original** color is the ramp accent `#140e0c`
   (20,14,12) — eyes and feet caps — over the crimson, mirroring how the
   runtime redraws its notch on top of the flash.

The accent constant is tied to the frozen ramp mechanically: a test asserts
it equals the calibration-v0 idle spec palette `k`. No new colors exist
anywhere; the ACC row sits stacked directly under the plain FLASH row for
direct comparison. Measured: surviving accent pixel count per strip frame
and WCAG contrast of accent vs crimson fill. **Labeled exploration for a
future integration design; phase-0 exports may not assume it**
(asset-contract law — same status as the v2 bbox-fit ring).

## Measurement plan (what the verdict must cite)

`tools/anticipation_metrics.py` (new, tested; imports the banked
motion/feedback helpers unmodified) reports:

- a0 poses: mass, bbox, feet row, centroid, mass drift vs idle; silhouette
  delta (100·XOR/union) vs the idle, **every** walk frame, AND k0; the
  walk-side confusability floor and the separate a0-vs-k0 distinctness
  value; max delta vs the cross-facing identity ceiling; head-region
  (rows ≤15) share of the a0-vs-idle change.
- flash-accent: surviving accent pixel count for every strip frame (idle,
  f0–f3, a0, k0) per facing; WCAG contrast of accent vs crimson fill;
  accent share of pose mass.
- bbox-ring breathing extended to a0 (metrics only, integration record):
  idle→a0 and a0→k0 max edge shifts alongside the banked walk breathing.
- `--check` hard lines (exit nonzero) — the four bars below.

`tools/make_anticipation_sheet.py` (new, tested, deterministic) renders per
facing: FILM + FLASH + ACC rows over both exact zone palettes (idle +
f0–f3 + a0 + k0, seven columns, static v0 idle as the control column);
GRAMMAR row (idle static | mid-walk f1 | a0 static | a0 at the pinned −3px
windup offset | k0 static | k0 at the pinned +6px lunge offset); DIFF row
(a0 vs idle, every walk frame, and k0 at 2x); 2x/4x diagnostic rows.
Existing tools are imported unmodified; the v0 contact sheet, v1 motion
sheet, AND v2 feedback sheet must regenerate byte-identical (mechanically
enforced by the extended regression test).

## Pass bars (fixed now, before any pixel or sheet exists)

Accuracy: all asset-gate checks; specs validate; exports verified
pixel-for-pixel; `anticipation_metrics --check` passes; sheet and metrics
byte-identical on regeneration; v0/v1/v2 artifacts untouched and their
sheets byte-stable; head/eye cluster byte-exact at the declared (dx,dy)
per facing, machine-verified by test; no game-two changes.

The four hard `--check` bars:

1. **Walk-side confusability floor:** a0 silhouette delta vs the idle AND
   every walk frame ≥ 25.0% (the banked walk envelope 22.09% plus declared
   margin — the v2 convention, unchanged).
2. **Strike distinctness (pre-registered, separate):** a0 vs k0 ≥ 25.0%.
   Windup and strike are two states of one grammar — related silhouettes
   are expected, confusable ones fail.
3. **Identity ceiling:** every a0 delta (vs idle, every walk frame, and
   k0) below the 44.44% cross-facing reference.
4. **Grounding:** a0 feet-contact row within ±1px of the idle's row 27.

Presentation, judged at native 1x on both zones:

1. **Windup reads at 1x:** a0 is instantly distinct from the idle and from
   every walk frame in FILM and GRAMMAR rows (the floor must agree with
   the native read); the −3px windup cell strengthens the pose read — the
   pose carries the state, the offset carries the direction.
2. **Windup is not the strike:** a0 and k0 read as two different moments
   of one action (coil vs release), not as interchangeable frames — the
   distinctness bar must agree with the native read.
3. **Grammar sequence reads as escalation:** idle → f1 → a0(−3) → k0(+6)
   reads as four sequential, causally-ordered states at 1x.
4. **Flash-accent judged on identity recovery without new colors:** the
   ACC row is judged on whether redrawn eyes/feet restore identity during
   flicker-on frames versus the plain FLASH row, using only the frozen
   ramp accent over the pinned crimson; measured contrast cited.

A REJECT on any bar is a legitimate sprint answer — banked with the
finding; no rescue edits to frozen frames, runtime colors, or banked
verdicts.

## Known limitation, declared up front

The sheet proves the windup **spatially**: a static a0 at the pinned −3px
offset. The runtime windup is **temporal** — the same frame held for the
windup duration, then replaced by k0 at +6px. A static sheet cannot prove
that the hold duration reads as tension; that requires an integration
replay capture and is recorded as an integration caveat, not claimed by
this sprint. The GRAMMAR row is the strongest static proxy: the four
states side by side in runtime draw positions.

## Stop conditions

One asset cycle: at most 2 anticipation frames, one anticipation sheet,
one banked verdict, council ≤ 8k tokens with one consolidated verdict,
claims re-verified against pixels before acceptance. No lore, no
8-direction sets, no full attack animation or smear frames, no
terrain/enemies/pack, no runtime integration, no game-two changes.
