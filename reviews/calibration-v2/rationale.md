# Calibration v2 — feedback-state coherence rationale

Sprint-2 question (the banked v1 next-hypothesis): do body-scale state
changes stay readable on the lane-B body at native 1x (the Vlambeer
body-carries-state doctrine)? Concretely: (a) hurt-flash recolor over the
idle and all four walk frames, (b) one attack-key tell pose per facing,
static and at the pinned lunge offset, (c) possession-ring geometry — the
current 28x28-SIZE ring versus a bbox-fit exploration variant. Scope:
`player_1_lane_b` only; the v0 idles and v1 walk frames are frozen inputs.

## Shared constraints (inherited, unchanged)

- 32x32 RGBA8, hard alpha, pixels inside `[2,2,29,29]`, anchor `[16,30]`.
- The frozen 5-color ramp: `#140e0c` accent, `#401c10` outline, `#8c3818`
  shade, `#eb7828` base, `#ffa050` highlight. No new colors in specs or
  exports; hurt-flash and ring variants are sheet-level simulations driven
  by pinned runtime constants.
- Generic mechanical IDs: `player_1_lane_b_attack_{facing}_k0`.

## Pinned-constant capture (read-only, game commit `219121d3…`)

Captured via `git show 219121d3ca2cfabfd39c3a1533b8227b52f68617:<path>` —
the live checkout was verified clean at the pinned commit by the asset gate
before capture. Exact lines:

`src/app/renderer.rb`:

- L22 `POSSESSED_RING = Gosu::Color.new(255, 255, 255, 255)` and L423
  `Gosu.draw_rect(x - 3, y - 3, SIZE + 6, SIZE + 6, POSSESSED_RING)` —
  already pinned (`possession_ring.rgb`, `expand: 3`); unchanged.
- L23 `ALLY_DIM = Gosu::Color.new(120, 10, 8, 12)` with L455
  `Gosu.draw_rect(x, y, SIZE, SIZE, ALLY_DIM)` — alpha-120 dark overlay over
  the full SIZE rect, no expand. **New pin:** `feedback_states.ally_dim`.
- L24 `PACK_HURT = Gosu::Color.new(255, 200, 30, 30)` ("crimson, never
  white") — the player_1 body is pack faction, so this is the hurt-flash
  color under test. **New pin:** `feedback_states.hurt_flash.pack_rgb`.
- L25 `HUMAN_HURT = Gosu::Color.new(255, 255, 80, 80)` — captured for
  completeness. **New pin:** `feedback_states.hurt_flash.human_rgb`.
- L470-480 `body_color`: pack + (`iframes?` L471 or `hurt?` L475) +
  `(world.frame / 3).even?` → the **whole body rect** is drawn in PACK_HURT.
  The flash is a full color replacement flickering 3 frames on / 3 off, not
  a tint; the facing notch (L484-496) draws on top of it. **New pins:**
  `hurt_flash.treatment`, `hurt_flash.flicker_period_frames`.
- L498-508 `lunge_offset`: pack, non-special: windup `[-3*fx, -3*fy]`,
  active `[+6*fx, +6*fy]`, draw-only ("tiles never move"). **New pin:**
  `feedback_states.lunge_offset`.
- L446-452 telegraph swell (human faction only, `telegraphing?` =
  `attack_state == :windup`, creature.rb L70): `swell = 8`; edge rect at
  `(x-4, y-4, SIZE+8, SIZE+8)` TELEGRAPH_EDGE; core at `(x-2, y-2, SIZE+4,
  SIZE+4)` TELEGRAPH_CORE; inner body held visible at `(x+5, y+5, SIZE-10,
  SIZE-10)` HUMAN_BODY. **New pin:** `feedback_states.telegraph_swell`.

`src/game/creature.rb`: L9 `SIZE = 28`; L64 `hurt?`, L65 `iframes?`; L70
`telegraphing?`.

`src/game/feel.rb`: hitstop + screen-shake only — **no body-scale color or
geometry constant exists there** (finding recorded; no rubric line and no
pin derived from feel.rb).

All additions to `manifests/render-reference.json` are additive;
`manifests/runtime-baseline.json` is untouched.

## KB and corpus grounding

- KB `game-research/pixel-art-pygame-and-2d-engine-reference.md` §7.2
  (verified 2026-04-10): anticipation is a **held** frame (100-200ms), the
  strike is ~1 frame with smear pixels, follow-through holds. Smear frames
  are motion-bridging artifacts for the in-flight swing — **smear doctrine
  does not apply to a static strike tell**; it becomes relevant only if a
  full attack animation is authored later (out of scope).
- KB `game-research/aseprite-pixel-art-mastery.md` §7.6 (verified
  2026-04-11): smears bridge two distant positions in a single frame, 1-2
  per action — same conclusion.
- KB `game-research/technical-drawing-for-game-art.md` §4.4 (verified
  2026-04-11): the silhouette test — fill the sprite solid; if it is still
  recognizable, the design works. The runtime hurt-flash **is** this test in
  crimson: identity under flash rests on silhouette alone.
- KB `game-research/game-ui-ux-patterns.md` §2 (verified 2026-08-15,
  Swink R193): juice/polish amplifies feel; state must be carried by the
  body the player already watches.
- Playbook A §3 (`docs/research/2d-asset-playbooks/`, subordinate to the
  contract): "Animation must read clearly at game size and speed;
  exaggerated key poses are prioritized over subtle detail" — the tell is an
  exaggerated key extreme, pose-to-pose.

## Flash simulation design (runtime-faithful, no invented colors)

The sheet FLASH rows recolor **every opaque pixel** of a frozen export to
the pinned `(200, 30, 30)` — exactly what the renderer does to its body
rect on flicker-on frames. No ramp-preserving tint exists in the runtime;
painting one would invent runtime colors (prohibited). The FILM row
(flash-off phase) sits directly above the FLASH row (flash-on phase), so the
3-frame temporal alternation is reproduced spatially for review. Recorded
integration delta: the runtime keeps its facing notch drawn over the flash;
a sprite integration must decide the equivalent (eyes/feet accents are body
pixels here and flash with the body). Judged under rubric line 2.

## Attack-key pose plan (per facing, derived from frozen frames)

New pixels this sprint: `player_1_lane_b_attack_down_k0`,
`player_1_lane_b_attack_right_k0` (one key pose per facing; anticipation
frames only if the key poses measure clean — see stop conditions).

Design doctrine: the tell is a held key extreme (KB §7.2), the +6px lunge
carry is the pinned draw offset, not pose pixels. The head/eye cluster —
the banked identity anchor — is preserved byte-exact and rigidly
translated; the state is carried by an open jaw (dark `#140e0c` gape, the
strike read) plus a braced/stretched stance. Both poses keep feet contact
at row 27 (the lunge is draw-only, so the pose itself stays grounded).

- **Down k0 (pounce at the viewer):** head block (dome + eyes) rigidly
  lowered 2px; open jaw replaces two plain body rows directly under the
  eyes; mid-body braced 2px wider each side (splay); legs splayed 2px
  outward, feet caps at row 27. No walk frame changes the head interior or
  body width — the tell attacks a dimension the walk never uses.
- **Right k0 (lunging pounce right):** head block rigidly lowered 3px
  (walk frames keep the head high at rows 4-14 — height drop is the
  unused dimension); jaw opens at the snout tip; body flattened into the
  crouch; front leg extended forward, rear leg trailing back, both distinct
  from the f0 stride and f2 gather column positions.

## Ring-variant design (exploration, not contract)

RING S row: the current renderer geometry — white filled rect at the SIZE
square (`tile_offset - 3` … `SIZE + 6`), body drawn on top (v0 finding: a
backdrop plate under a 16-22px body). RING B row: the bbox-fit exploration
variant — white filled rect at the **per-frame sprite bbox** expanded by
the pinned `expand: 3`, body on top. Both use only pinned white and pinned
expand. The bbox-fit row is labeled exploration for a future integration
design; phase-0 exports may not assume it (asset-contract law). Ring
breathing (per-frame bbox change) is measured across idle + walk + attack
frames — a bbox ring inherits animation jitter that the SIZE ring does not
have; that trade-off is exactly what this row exists to expose. Ally-dim
shares the SIZE-geometry finding (L455); its geometry question is answered
by proxy by the ring rows and it is pinned but not separately simulated.

## Measurement plan (what the verdict must cite)

`tools/feedback_metrics.py` (new, tested) reports:

- attack poses: mass, bbox, feet row, centroid, mass drift vs idle;
  silhouette delta (100 * XOR / union) vs the idle **and vs every walk
  frame** — the confusability floor is the minimum of those five deltas;
  head-region (rows ≤15) share of the k0-vs-idle delta.
- flash: WCAG contrast of the pinned flash RGB against both zones' floor
  and wall; RGB distance from flash to telegraph edge, telegraph core,
  transition gold, and the role base color.
- rings: per frame (idle, f0-f3, k0) and per variant: ring rect, visible
  ring margin px, ring-margin-to-body-mass dominance ratio; bbox-ring
  breathing (max edge shift across consecutive cycle frames).
- `--check` hard lines (exit nonzero): every attack pose within bounds with
  feet row within ±1 of idle; confusability floor ≥ 25%; ceiling: no
  attack-vs-frozen delta ≥ the 44.44% cross-facing reference.

`tools/make_feedback_sheet.py` (new, tested, deterministic) renders per
facing: FILM + FLASH rows over both exact zone palettes (idle + f0-f3 +
k0); TELL row (idle | mid-walk f1 | windup at -3px | k0 static | k0 at
+6px active lunge); ADJ row (flash-on body and k0 beside a runtime-faithful
telegraphing human, and flash-on body beside an open-transition gold tile);
RING S / RING B rows; DIFF row (k0 vs idle and vs every walk frame, 2x);
2x/4x diagnostic rows. The static v0 idle is the first strip column
(control). Existing tools are imported unmodified; v0 and v1 sheets must
regenerate byte-identical (tested).

## Pass bar (fixed before looking)

Accuracy: all asset-gate checks; specs validate; exports verified
pixel-for-pixel; `feedback_metrics --check` passes; sheet and metrics
byte-identical on regeneration; v0/v1 artifacts untouched and their sheets
byte-stable; no game-two changes.

Presentation, judged at native 1x on both zones:

1. **Tell reads at 1x:** k0 is instantly distinct from the idle and from
   every walk frame (confusability floor ≥ 25%, and the native read must
   agree); the lunge-offset cell strengthens, not replaces, the pose read.
2. **Flash preserves identity:** the crimson silhouette + stacked FILM/FLASH
   alternation still reads as the same creature on both zones (silhouette
   test); flash contrast against both zone floors and walls stays readable.
3. **Ring dominant without drowning:** the white ring signals possession in
   both variants; the bbox-fit row is judged on whether it keeps the signal
   while freeing the body from the v0 backdrop-plate effect; breathing is
   reported, not hidden.
4. **No cross-signal confusion:** flash-on body and k0 are not confusable
   with telegraph red or transition gold in the ADJ cells; measured RGB
   distances cited.

If any line fails, the failure is the sprint answer — banked as REJECT with
the finding; no rescue edits to frozen frames, runtime colors, or banked
verdicts.

## Stop conditions

One asset cycle: at most 2 attack-key frames (+2 anticipation frames only
if the key poses measure clean before release), one feedback sheet, one
banked verdict, council use ≤ 8k tokens with one consolidated verdict. No
lore, no 8-direction sets, no full attack animation, no terrain/enemies/
pack, no game-two changes.
