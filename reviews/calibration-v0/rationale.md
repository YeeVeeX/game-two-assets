# Calibration v0 — three-lane silhouette rationale

Sprint-0 question: which visual language keeps a possessed body readable at
native 32x32 over real zone palettes while improving on the current flat-rect
primitive? One generic body (`player_1`), two poses (`idle_down`, `idle_right`)
per lane. Role color, canvas, anchor, and background are held constant so the
review isolates shape language.

## Shared constraints

- 32x32 RGBA8, hard alpha, pixels inside `[2,2,29,29]`, anchor `[16,30]`
  (`docs/asset-contract.md`).
- One shared 5-color ramp (of 8 allowed), hue-shifted cool-dark to warm-light
  per the KB pixel-workflow notes (shadows cooler, highlights warmer,
  desaturated base, one light direction: top-left):
  `#140e0c` accent (the runtime notch color — continuity), `#401c10` outline,
  `#8c3818` shade, `#eb7828` base (player_1 role color, dominant), `#ffa050`
  highlight. Highlight is hue-distant from open-transition gold `#ebbe5a`.
- 1px selective dark outline on every candidate: the KB technical-drawing note
  recommends a hard dark outline at 32x32 for separation against varied
  terrain (the functional lesson from Tibia-style grids); bright interior
  carries separation on dark floors, dark outline carries it on light walls.
- Facing is the calibration axis: the 2026-08-09 game-two vision critique
  ("from a still frame I cannot tell if this character is walking left or
  right") produced the current notch; every lane must beat it without labels.
- Feedback headroom (Vlambeer touchstone, game-two digest): the body must
  stay recognizable under hurt-flash crimson and remain subordinate to the
  white possession ring; telegraph red and transition gold are reproduced on
  the contact sheet to test competition directly.

## Lane A — geometric lineage (`player_1_lane_a_*`)

Evolves the current rectangle: chamfered 20x24 slab, top light band, bottom
shade band, and the notch grown into a bold `#140e0c` visor block flush with
the facing edge (horizontal at the bottom for down, vertical at the right for
right; back edge carries the highlight column in profile).

**Prediction:** strongest continuity and wall/floor separation for the lowest
risk; but down-vs-right may still read as "same square, different sticker"
at 1x because the outer silhouette stays symmetric. Tests whether outline +
value banding alone can rescue the rectangle language.

## Lane B — compact bodily form (`player_1_lane_b_*`)

Big-head creature grouping per the KB proportion rule (head mass ~11px, torso
~9, feet nubs): rounded head with 2x2 eyes, narrower torso, staggered dark
feet; profile pose leads with a 4px snout, single eye, and a small tail nub.
Occupies ~16x24, leaving real floor around the figure.

**Prediction:** best down-vs-right distinction and the only lane that reads
as "a creature" rather than "a marker"; risk is per-tile role-color mass —
the smaller silhouette may weaken player_1 identification at a glance and the
face detail may dissolve at 1x (the classic 4x-looks-good/1x-disappears
failure this sprint exists to catch).

## Lane C — asymmetric action form (`player_1_lane_c_*`)

One deliberate directional mass, no overhang: down pose is a broad low wedge
with forward claws (mass pushed toward the facing edge); right pose is a
stepped beast — low rear block, tall front block, leading wedge nose, heavy
front foot. Weight distribution itself signals facing before any accent does.

**Prediction:** strongest facing/attack readability (the renderer's lunge
offsets would amplify the lean) and the most distinct silhouette pair; risk
is idle stability — an asymmetric mass can read as mid-motion or damaged when
standing still, and it strays furthest from the current language.

## Baseline

The current primitive (28x28 role rect + 6x6 notch, constants copied from the
pinned `src/app/renderer.rb`) appears on every sheet row as the control.

## Concept generation decision

No Bedrock/general-model concepts were used. The KB 2026 sprite-pipeline note
is explicit that general models emit "a picture of a sprite, not a sprite"
(wrong grid, thousands of colors) and Bedrock has no pixel-native path; for
three functional silhouette lanes the shape decisions live on the 32x32 grid
itself, so candidates were authored directly as reviewable pixel-grid specs
(`sources/calibration-v0/specs/`) and built into native Aseprite sources.
Origin is declared `procedural` in the release manifest; no provider
provenance applies.

## References (principles extracted, no imagery copied)

- KB `game-research/technical-drawing-for-game-art.md` — silhouette test,
  32x32 proportion rules, outline strategy, down/right view content.
- KB `game-research/aseprite-pixel-art-mastery.md` — palette construction:
  hue-shifted ramps, value contrast at low resolution, single light source.
- KB `game-research/ai-sprite-pixel-art-pipeline-2026.md` — general-model
  sprite failure modes; reconstruction-at-native-resolution doctrine.
- game-two `docs/design-corpus/tibia-research.md` — readability from strict
  tile occupancy and grid quantization (loops/economy touchstone only).
- game-two `drafts/_gamesmith-touchstone-digest.md` — Vlambeer feedback
  doctrine; body must carry state changes at body scale.
- game-two `docs/design-corpus/vision-critique-20260809.md` — the facing
  readability failure that defined this calibration's axis.
