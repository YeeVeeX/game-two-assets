# Tile-era intake — world-builder constraints + owner style signals (banked 2026-08-19)

Source of record: two seat-mails from the game-two hub seat (2026-08-19),
banked here so sprint planning sees the tile era before it opens. Nothing
here is actionable until the corresponding game-two decisions land; the
asset contract and the calibration lanes are untouched.

## Roadmap constraint: tile/terrain exports (when the tile art era opens)

game-two ratified a world-builder lane (game-two AGENTS.md Lane 3, commit
`2471b5d`): external editor front-end (LDtk lead) + strict importer +
floors + a tile-type registry ("tile grammar" — each tile type declares
render + footstep material + passability + behavior hooks). Grill record:
`game-two/drafts/_world-builder-grill-20260819.md`.

What lands on THIS repo's roadmap:

- Tile/terrain exports as **tile-sized modular sheets with per-tile
  MATERIAL METADATA** — sprite <-> behavior bind by id, never filename
  convention.
- One material id per tile family (`stone`, `wood`, `water`, `lava`,
  `grass`, `sand`, `ice`, ...) carried in the export manifest beside the
  sha256s — the existing release.json pattern fits; add a `material:`
  field per sheet/region when that era opens.
- Material-STATES pattern welcomed (reference shape: ore -> shards ->
  chunk -> pebbles -> ingot per material) — states are extra columns in
  the same sheet, same id.
- game-two's registry consumes ids + sheets; behaviors stay game-side
  data; the sha-pinned delivery lane is unchanged.

## Owner style signals (direction data, not adopted rules)

Live taste board, three references so far (verbatims banked in the
game-two hub records; ref image copies live untracked in
`game-two/drafts/_refs/` with md5s in the grill record — NOT copied into
this repo per the unlicensed-reference law; consult them read-only):

1. **CryoFall** (twice in one session): "the asset style is pretty
   charming on my opinion" — top-down 2D survival-sim readability +
   charm is a live owner preference. Also: we can "create our own that
   look and animate even cooler (Tibia is a very good example of it but
   with a bit uglier rendering than what I intend to create)".
2. **Gnomoria (true 2:1 iso):** "this style of isometric pixel art which
   is simple but well detailed and beautifully designed looks even more
   appealing to my eye instead of the plain top view". Style reads:
   3-face block shading sells the depth; 2-tone floor checker inside
   each tile; decor sprites break flat fields.
3. **RavenDawn (Tibia-style 3/4 top-down, painterly):** "we can adapt it
   to an even grimmer or 'realistic' view/detailed view such as HD
   Tibia, or RavenQuest/RavenDawn for that sort, but with the isometric
   perspective". Style reads: painterly material families
   (stone/moss/foliage); architecture with drawn height; layered
   canopies + soft shadows; grim-elegant palette.

Cross-reference read from the hub seat: the two 2026-08-19 refs use
DIFFERENT projections (Gnomoria true 2:1 iso vs RavenDawn 3/4 top-down
with drawn height faces); what the owner's eye tracks across both is
material richness + visible height + lived-in detail in a grim register.
game-two's combat-clean law rides along: environment rich, combat
surfaces (telegraphs/enemies/drops) high-contrast clean.

## Decision gates this repo waits on (game-two side)

- **Projection** (flat vs 3/4 vs iso): game-two runs a projection-preview
  spike with placeholder geometry (banked as v19 intake idea 5); owner's
  eyes pick.
- **Fidelity** (chunky pixel vs painterly HD): asset-era decision, lands
  at the v19 brainstorm WITH this repo's pipeline constraints in the room.

Branch consequences for exports (planning heads-up only): 3/4 adds wall
FRONT faces + height pieces per material; true iso adds 2:1 diamond
floors + 3-face-shaded wall prisms + edge caps; painterly-HD adds painted
variants + edge blends per material family. The per-tile material
metadata contract above carries the seam identically in every branch.
