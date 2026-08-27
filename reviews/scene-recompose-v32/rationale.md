# v32 — first SCENE recomposition: engine-true neighbors around the sprite proposal (EXP-class) — rationale (PRE-REGISTERED)

**Status: protocols and bars FIXED BEFORE any scene manifest, scene code,
or scene artifact bytes exist.** This file is committed with every verdict
cell NULL (commit A). The two anchored manifests + the consumer extension
land at commit B, the artifacts at commit C, the judged verdict at commit D
— the commit-A discipline every calibration sprint used. No cell may be
filled before its evidence exists. Every pre-registered PIXEL string below
was glyph-checked against the live SEAM_FONT set
(`' 0123456789ABCDEFGHIJKLMNOPRSTUWXYZ'` — no Q, no V, no punctuation
beyond space) BEFORE this commit (v31 f2 deviation class, now mechanized).

**Authorization (owner order, recorded verbatim from the v32 brief):**
"AUTHORIZATION: the v31 verdict pinned that 'full-scene multi-creature
composition (draw order, neighbors) is a SEPARATE owner decision' - THIS
brief is that decision, owner-launched (record this line in the verdict as
the owner order)."

## Review objects

- The intaken evidence (unchanged from v31): bundle `20260826T175326Z_p1_42`
  (`evidence/replay/20260826T175326Z_p1_42/`); track 1 =
  `tracks/reference-attack-window.json` sha256
  `dd68c8cbb324dd7faf19197df05922e32d20a65b8c3b08928f775da76f44545d`
  (frames 420..560, 141 ticks, 18 creatures — 3 pack + 15 human — zone
  `district`, possessed exactly 1/tick, view origin [0,0] 1408x832).
- The banked single-creature instrument this sprint extends AROUND (never
  through): `reviews/runtime-recompose-v31/` — subject `striker`/kit
  striker, span [420,483], the ONLY qualifying run; its artifacts and
  manifest stay byte-identical through this sprint.
- The consumer: `tools/track_recompose.py`, extended IN PLACE (unpinned-
  tool census stays 4; zero new tool files). Scene code gets its OWN
  `SCENE_*` constants and builders; `RUNTIME_*` constants,
  `SHEET_BANNER_*`/`APNG_HEADER_*` strings, and the single-creature
  builders (`build_runtime_sheet`, `build_runtime_apng_frames`,
  `_runtime_bundle_bytes`, `make_runtime_artifacts`) stay byte-frozen in
  behavior.
- The engine substrate law: `docs/replay-capture-design.md` section 2.3
  ("the renderer draws creatures as solid quads plus a facing notch") and
  section 6 (artifact law); the intake law: section 5, live in code
  (`verify_runtime_intake`).
- Pinned game bytes at the runtime-baseline pin (commit
  `ad7f6a1e5700481c0ed455970790e66d89501358`; all content sha256_lf equal
  to the banked baseline pins, verified this session): `src/app/renderer.rb`
  (sha256_lf `45827b9a2f9ef473659a8353fcb9c9aa6eb7fccd73776e572572f7f383c5ac04`),
  `data/zones/district.json` (sha256_lf
  `9774cdd04ebaf6e1a429a1aceb26ca8b7ddd13f97f3086ff862d22ee305cd5f4`).

## Role boundary (pre-registered)

EXP-class instrument readiness ONLY. Every artifact answers ZERO register
items and says so in pixels, filename, and manifest. Zero adjudication
language anywhere (no bar, no severity, no "reads correctly").
MEASURED-capable is not measured. Layer honesty is the sprint's law: every
layer's provenance is disclosed in pixels (subject = proposal; neighbors =
engine primitive bodies at the pin; feedback states beyond the ring NOT
modeled). Zero new art pixels — the subject re-places banked export bytes;
neighbors/tiles/ring are ENGINE-ANCHORED PROCEDURAL primitives, the banked
contact-sheet convention class (`primitive_sprite`/`draw_wall_tile`/
`draw_ring` lineage). Zero exports; zero release manifests; zero
register/status edits; mapping SEMANTICS untouched (`select_pose`,
`recompose_track`, `compose_cell` byte-identical); typed refusals never
weakened; RUNTIME composition admitted only through
`verify_runtime_intake`, run LIVE in the generation path. ONE scene lane
(track 1, the banked span). `docs/state-track-schema.md` stays draft-1
history; frozen docs and surfaces byte-untouched.

## Scene layer law (pre-registered verbatim; executed AFTER this commit)

The scene composition id is **`declared-scene-composition-v1`**, layered ON
TOP of the untouched `declared-integration-mapping-v1`; both ids are
version-pinned in every artifact.

**Position ground truth (citations shared by all layers):** the track's
`px`/`py` ARE the engine creature's body top-left (`c.x`/`c.y` =
`walker.px`/`walker.py`, creature.rb:60-61, restated
`docs/state-track-schema.md` row px/py) — the +2px tile inset is already
INSIDE px (grid_walker.rb:102-103 centers the 28px body at +2px in the
tile, cited in render-reference `walk_tween`; corroborated from track
bytes this session: all 2,146 at-rest records sit at px%32==2, py%32==2).
The engine draws the body rect AT `c.x + lunge` with NO further offset
(renderer.rb:797-799, 833). Therefore the neighbor body rect anchors at
`round_half_up(px) + lunge` directly — adding `primitive_body.tile_offset`
on top would DOUBLE the inset (named trap; the render-reference
`tile_offset [2,2]` describes the body's rest position inside its tile,
which px already carries). The SUBJECT keeps the banked mapping-v1
position law verbatim (sprite canvas anchored at `round_half_up(px) +
lunge`, v13 law): its opaque body pixels (canvas inset [2,2]) therefore
land 2px right+down of where the engine's own body rect sits — a property
of the banked DECLARED mapping, not of this sprint; disclosed in the
manifest prose.

1. **TILE LAYER** — source: a NEW anchored manifest
   `manifests/zone-map-district.json` carrying the `tiles` array (26 row
   strings, glyph census `.` and `#` only), `tile_size` 32, and
   `transitions` copied VERBATIM from pinned `data/zones/district.json`;
   anchoring block = game_commit at derivation + `source_sha256_lf` (= the
   runtime-baseline pin for district.json, test-asserted — the
   zone-palette-district pattern, CONTENT-bound so identity re-pins never
   invalidate it) + per-field citations. Glyph semantics cited: `#` = wall
   (renderer.rb:432 wall run collection via `map.wall?`; the "'#' law"
   comment renderer.rb:259); `.` = plain floor (draw_map paints the whole
   map floor first, renderer.rb:279+; plain cells carry no overlay);
   transition cells = gold rect inset 3 over floor (renderer.rb:349,
   unsealed branch). Drawing uses the BANKED conventions over the district
   palette (`draw_floor_tile`/`draw_wall_tile`/`draw_gold_tile` from
   `tools/make_contact_sheet.py` — draw_gold_tile is byte-the-same law as
   renderer.rb:349's inset-3 gold rect), palette merged OPT-IN from
   `manifests/zone-palette-district.json` (the v31 `load_zone_palette`
   pattern; the PLAIN reference stays banked-zones-only, guarded by the
   banked v30 unmapped-zone test). NOT modeled (disclosed in pixels +
   manifest): stations, decor, motif rects, ambient tint, seal/lock
   states, the engine's full-map grid lines over walls (the banked
   draw_floor_tile draws grid on each floor tile's top/left edge only),
   drop-gradient markers. Window tiles outside the map bounds = background
   void (the banked BG presentation constant), COUNTED in the participants
   capture and disclosed (expected 0 for the derived window; counting is
   the proof). Transition seal state is runtime state the track does not
   carry: ALL transition cells draw the unsealed gold convention (both
   district transitions sit outside the expected window; the census
   discloses the count).
2. **NEIGHBOR LAYER** — the engine's OWN primitive bodies, value-anchored
   per kit to pinned renderer bytes via a NEW anchored manifest
   `manifests/scene-reference.json`: 28px body rect (SIZE =
   Game::Creature::SIZE, renderer.rb:76, = render-reference
   `primitive_body.size` anchored to creature.rb:9) at `round_half_up(px/
   py) + lunge` (position law above), body color per kit from pinned
   KIT_BODY (renderer.rb:16-21: striker [235,120,40], blocker [190,80,35],
   lobber [225,170,90], rusher_hater = HUMAN_BODY; HUMAN_BODY
   [205,198,180] renderer.rb:15; DEFAULT for any unlisted kit — e.g.
   `rusher` — is HUMAN_BODY via `Hash.new(HUMAN_BODY)` renderer.rb:16,
   cited as a VALUE, not a guess); 6px facing notch in NOTCH [20,14,12]
   (renderer.rb:43 = render-reference `primitive_body.notch_rgb`) with the
   ENGINE'S OWN three-branch geometry (renderer.rb:863-877,
   draw_facing_notch): fx==0 → notch spans centered horizontally at the
   facing edge (`x + SIZE/2 - 3`, `y + SIZE - 6` if fy>0 else `y`); fy==0
   → centered vertically at the facing edge (`x + SIZE - 6` if fx>0 else
   `x`, `y + SIZE/2 - 3`); diagonal → corner notch at the facing corner —
   legal for ALL FOUR cardinal facings AND diagonals (the up/left refusal
   class that blocks sprite neighbors does not apply; the engine's law is
   total over integer facings). Lunge = the ENGINE's law verbatim
   (renderer.rb:879-888): pack faction only, suppressed when
   current_action == "special", windup −3px / active +6px along facing,
   else 0 (= render-reference `feedback_states.lunge_offset`, re-verified
   by pin_drift every re-pin). Participants = creatures whose 32x32 draw
   rect `[wx, wx+32) x [wy, wy+32)` (wx/wy = rounded position + lunge)
   intersects the window on that tick; present records outside the window
   are OMITTED and counted per creature in the participants capture. Any
   record a primitive cannot draw = typed refusal STOP (`scene-neighbor-
   undrawable`; none expected — primitives are state-independent). NOT
   modeled (disclosed): hurt flash, iframes flicker, telegraph swell +
   core, ally dim, seized weight/underlines, taunt underline, pressure
   outline, retarget cues, god marks, nameplates, attack action tiles,
   enemy strike tiles, corpses, drops, projectiles, chant rings.
3. **SUBJECT LAYER** — the banked striker sprite under mapping-v1:
   `select_pose` UNTOUCHED, the SAME per-tick decisions the banked v31
   capture recorded (`decisions-subject.json`); the generation path
   asserts the subject's (pose, facing, offset) stream over the span is
   EQUAL to the banked capture's entries (any difference = code
   regression, typed STOP `scene-subject-decision-drift`). Sprite canvas
   anchored per the banked position law (above).
4. **RING LAYER** — possession ring from pinned constants at the possessed
   creature's draw position. Renderer-cited: the ring RIDES THE LUNGE
   (renderer.rb:798-802 — `x = c.x + lx` is computed BEFORE the ring rect
   at `(x-3, y-3, SIZE+6, SIZE+6)` in POSSESSED_RING [255,255,255]
   renderer.rb:23; ring drawn BEFORE the body, so the body covers its
   center and 3px of band shows) = render-reference `possession_ring`
   {rgb, expand 3}. Geometry in the scene = the banked `draw_ring`
   convention (make_contact_sheet.py) anchored at the SUBJECT'S drawn
   canvas position + lunge: ring rect `(wx + 2 - 3, wy + 2 - 3, 28+6,
   28+6)` around the render-reference primitive_body box = the sprite's
   own opaque bounds [2,2,29,29] — the engine law "3px white band around
   the possessed body, riding the lunge" applied to the body the proposal
   actually draws. The engine-true alternative (ring at raw px-3) would
   ring 2px off the sprite's body under the banked canvas law — rejected
   as misleading; this choice + both citations disclosed in the manifest.
5. **FEEDBACK STATES BEYOND THE RING NOT MODELED** — disclosed in pixels
   (banner line 3), filename class, and manifest (the full omission list
   in layer 2).

**Draw order (derived where pinned, declared where not — both disclosed):**
- Tile layer under everything (renderer.rb:96-99: draw() calls draw_map
  first) — DERIVED, cited.
- ALL humans before ALL pack (renderer.rb:108-109: `world.humans.each {
  draw_creature }` then `world.pack.living.each { draw_creature }` — pack
  bodies draw over humans) — DERIVED, cited.
- WITHIN each faction pass: the engine iterates the world's live
  collection order — runtime state the track does not carry (unpinnable
  from this side, the "map iteration" class) — so the order is DECLARED:
  ascending drawn y (rounded py + lunge_y), tie → ascending creature name
  (bytewise), disclosed as the proposal's own. The participants capture
  counts same-faction overlapping pairs per tick so the declared order's
  actual pixel consequence is measurable.
- Within one creature: ring BEFORE body (renderer.rb:801-802 order), body,
  notch ON TOP (renderer.rb:842 draw_facing_notch called after the body
  rect; the hurt-flash note "facing notch drawn on top" corroborates).
- The subject (possessed pack striker) draws at its slot in the pack pass
  as ring + sprite (sprite replaces body+notch per mapping-v1).

## Span + window policy (pre-registered)

- **Span:** RE-DERIVED by the banked v31 policy (`derive_span` — longest
  refusal-free contiguous span of the subject containing a complete attack
  cycle w0→x0 returning to idle, tie → earliest) from the SAME evidence
  track, then asserted EQUAL to the banked
  `reviews/runtime-recompose-v31/runtime-exp-manifest.json` `span_frames`
  [420, 483]. Any difference = code regression → typed STOP
  (`scene-span-regression`), zero artifacts.
- **Window:** the v31 window formula with margin M = 4 TILEs instead of 1,
  same tile-aligned outward rounding, over the SUBJECT's world draw
  vectors across the span: `x0 = floor(min_x/TILE)*TILE − 4*TILE`, `y0 =
  floor(min_y/TILE)*TILE − 4*TILE`, `x1 = ceil((max_x+TILE)/TILE)*TILE +
  4*TILE` (exclusive), `y1` likewise; view = {origin [x0,y0], width
  x1−x0, height y1−y0}. Derived dims RECORDED in the manifest. Zero
  post-hoc adjustments: an uncomposable window is a STOP, never a tweak.
- **Sheet wrap:** 8 cells per row (pre-registered; the v31 layout
  convention at scene width). HARD assert: BOTH sheet pixel dimensions
  < 4096 (the v16 png_reader-cap precedent) else typed STOP
  (`scene-sheet-dims`), zero artifacts.
- **APNG:** exact 1/60 s per tick (banked encoder `apng_delays`, holds the
  last frame 0.5 s before loop, v13 convention), native 1x + ONE integer
  zoom 4x (banked APNG_SCALE convention), disclosure headers in pixels.

## Disclosure set (pre-registered VERBATIM; pixel strings glyph-checked before this commit)

Manifest + capture prose (`SCENE_EXP_DISCLOSURE`):
"SCENE-EXP: captured state is real; frame selection is the proposal's
(declared-integration-mapping-v1); scene composition is the proposal's
(declared-scene-composition-v1); subject sprite is the proposal; neighbors
are the engine's primitive bodies value-anchored at the pin; tile layer
from the pinned district map; possession ring from pinned constants;
feedback states beyond the ring not modeled; stations decor motif ambient
not modeled; temporal window is a selected span (see decisions capture);
not the live camera; answers ZERO register items."

Sheet banner (pixels, 4 lines; SEAM_FONT has no V — "RECT BODIES" carries
the primitive-body meaning; the version particles are digits, v13
precedent):
- line 1 `SCENE EXP  CAPTURED STATE IS REAL  FRAME SELECTION IS THE PROPOSAL`
- line 2 `SUBJECT SPRITE IS THE PROPOSAL  NEIGHBORS ARE ENGINE RECT BODIES AT THE PIN`
- line 3 `FEEDBACK STATES BEYOND THE RING NOT MODELED  STATIONS DECOR NOT MODELED  NOT THE GAME CAMERA`
- line 4 (the f4 temporal-selection line, ADOPTED; template instantiated
  from the derived values) `SPAN {first} TO {last} OF WINDOW {wf} TO {wl}
  SELECTED SPAN  SEE DECISIONS CAPTURE` — expected instantiation
  `SPAN 420 TO 483 OF WINDOW 420 TO 560  SELECTED SPAN  SEE DECISIONS
  CAPTURE` (glyph-checked as instantiated).
- footer `ANSWERS ZERO REGISTER ITEMS`

APNG headers (both zooms): line 1 `SCENE EXP  MAPPING 1  COMPOSITION 1`,
line 2 `ANSWERS ZERO REGISTER ITEMS`. Cell labels `T{frame}` (digits).

Filenames carry `scene-exp-`. Zero SYNTHETIC labels (RUNTIME-lineage
evidence; the v13 SYNTHETIC label law does not transfer). Artifact class
string: `SCENE-EXP`.

## Artifact set (pre-registered; all under `reviews/scene-recompose-v32/`)

1. `scene-exp-participants.json` — TEXT capture: per-creature per-tick
   presence/draw/omission statistics over the scene window and span
   (name, kit, faction, ticks present in span, ticks drawn, ticks omitted
   outside the window), per-tick drawn counts, same-faction and
   cross-faction overlap-pair counts, tile census (floor/wall/transition/
   void counts inside the window), subject-decision equality result,
   window/span/ids/intake context, disclosure verbatim. Written BEFORE the
   composed artifacts (the v31 decisions-capture pattern) so a STOP after
   it still banks the TEXT analysis.
2. `scene-exp-attack-sheet.png` — native 1x per-tick contact sheet of the
   span, 8 cells/row, frame labels, 4-line banner + footer IN PIXELS.
3. `scene-exp-attack-native.apng` — exact 1/60 s per tick, native 1x,
   disclosure header in pixels.
4. `scene-exp-attack-zoom4.apng` — the SAME frames at 4x, exact 1/60 s.
5. `scene-exp-manifest.json` — BOTH mapping ids + artifact class + repo
   commit at generation + mapping-source module sha256s + source track
   sha256 + intake context (bundle id, verification verdict/runs,
   fingerprint) + subject + span (+ equality-assert result) + window
   (origin, dims, formula restated with M=4) + participants summary +
   per-layer source citations (kit colors, notch geometry, lunge law,
   ring law + lunge-riding citation, draw-order derivation + declared
   tiebreak, tile glyph semantics, position ground truth incl. the 2px
   canvas-vs-engine-body property) + zone-map + scene-reference + palette
   file sha256s + determinism flags + every artifact sha256 + the
   disclosure verbatim.

If ZERO neighbors intersect the window across the span: banked as a typed
finding (`scene-zero-participants`), artifacts still land (subject + tiles
+ ring is still the instrument), the verdict names it.

## Generation law (pre-registered)

`verify_runtime_intake` runs LIVE in the generation path on the evidence
track (refuse-not-guess); the track re-passes `validate_track` +
`require_runtime_admission` against the SAME intake context; the span
equality assert runs against the banked v31 manifest value; every composed
artifact builds TWICE in-process and byte-compares before writing
(double-build determinism; the CLI hard-fails otherwise); committed
sha256s land in the manifest; a regeneration guard (SLOW tier,
pre-bank-skip pattern, NEW test class only) recomposes the committed
artifacts from committed evidence and compares bytes; `--check` gains the
same guard additively (skips while unbanked). New fast-tier scene units
run on TINY fixtures only (<= 4x4 tiles, <= 12 ticks, 2-3 creatures).

## Known mechanical consequence (pre-registered)

Editing `tools/track_recompose.py` moves its sha256, pinned by FIVE banked
manifests (recompose-v13, defect-audit-v14, remedy-v15, adoption-v16,
runtime-recompose-v31). Resolution at commit B, per the banked class:
regenerate each with its OWN tool AFTER the final parser edit; per-manifest
git diff = exactly the consumer pin line + `repo_commit_at_generation`;
every banked artifact byte-identical. **The v31 regen is the sharp one:
ANY v31 artifact byte moving = the edit broke single-creature composition
behavior = fix the edit, never re-bank.** Fan-out beyond the five =
enumerate, verify same class, else STOP. NEW consequence this sprint
CREATES: the v32 scene manifest pins the mapping-source hashes too, so
future consumer edits fan out to SIX manifests — named for v33 in the
verdict/receipt. A mid-change `--check` red on the v31 pin between the
parser edit and the regen = the v30-commit-B-attempt-1 class: expected,
resolved by the regen in the same change set, labeled EVENT if it hits the
hook.

## Bars (all-must-pass; verdicts NULL here, judged at commit D)

| # | Bar | What passes it (measurable) | Verdict |
|---|---|---|---|
| B1 | Protocol fidelity | Layers/span/window/order match this registration exactly; the span equality assert runs green against the banked [420,483]; window = the M=4 formula output recorded in the manifest; draw order = the derived+declared law verbatim; zero post-hoc adjustments (any uncomposable state took its typed STOP). | NULL |
| B2 | Regression | `track_recompose --check` exit 0 after EVERY edit batch; 672/672 + 340/340 equivalence green; draft-1 + v1 + runtime-extract suites additive-only or untouched; the FIVE-manifest fan-out resolved pin-line-only with the v31 artifact bytes IDENTICAL (empty artifact diffs); full discover green at recorded N (= 788 + exactly the new tests). | NULL |
| B3 | Anchoring | Every neighbor color, notch geometry rule, tile glyph, ring constant, lunge value, and draw-order rule cited to pinned bytes (file+line at the pin) or a named banked convention; zero invention; both new manifests carry anchoring blocks bound to CONTENT (`source_sha256_lf` = the runtime-baseline pins, test-asserted); the double-offset trap named and avoided (neighbor rect at px directly). | NULL |
| B4 | Determinism | Every composed artifact built twice in-process byte-identically at generation (manifest flags); committed sha256s match the committed files from `git show HEAD:`; the SLOW regeneration guard recomposes the committed artifacts byte-identically from committed evidence; `--check` extension green (pre-bank skip before commit C, "(banked)" after). | NULL |
| B5 | EXP boundary | The SCENE-EXP disclosure set appears in pixels (4-line banner + footer, APNG headers), in every artifact filename (`scene-exp-`), and verbatim in the manifest + capture; the temporal-selection line (v31 f4 adoption) in pixels; zero adjudication language in any artifact string (machine-scanned BEFORE council; council Q1 audits); zero SYNTHETIC labels; zero register/status edits; frozen docs/surfaces byte-untouched; census 4. | NULL |
| B6 | HFO gate (blocking) | Disclosure text, verdict.md, and scene-exp-manifest.json each critiqued with accuracy and presentation scored SEPARATELY (accuracy = every number/hash traceable to a computation this session or a named banked source; presentation = truncated pyramid, typed findings, no unlabeled precision). | NULL |

## Finding classes (pre-registered routing)

- **protocol-stop** — a pre-registered STOP bound (span mismatch vs
  banked; sheet dim >= 4096; undrawable neighbor record; unanchorable
  value; fan-out beyond the five named manifests; double-build
  nondeterminism; uncomposable window) → bank the TEXT analysis + the
  stop, zero composed artifacts on the stopped lane, verdict lands.
- **scene-zero-participants** — zero neighbors intersect across the span →
  typed finding, artifacts still land.
- **emitter-shaped** — track content contradicting the s84 pin → MAILED
  finding, never worked around.
- **noted** — observations with no action owed.

## Pre-registered non-claims

Zero adjudication of any lettered register item — the artifacts are
instruments; MEASURED-capable is not measured; the register's fusion-class
items someday need exactly this composition and this sprint still answers
NONE of them. No register row moves; C1–C5 MET, C6 OPEN doubly gated,
untouched; `docs/integration-readiness.md` + `docs/selection-register.md` +
`docs/state-track-schema.md` (draft-1 HISTORY) +
`docs/replay-capture-design.md` + all banked verdict trees (incl.
runtime-recompose-v31) byte-frozen. The live-camera-true viewport and item
(h)'s display-chain half stay named uncovered — the declared sub-window is
the recomposition's own (s84 item 2's allowance), never the game camera.
No schedule claims. Zero exports; zero release manifests; zero new tool
files (census 4); no capture tooling; no integration design content;
mechanical ids only. The v32 verdict BANKS the FOUR v31 cadence numbers
verbatim from the brief (their only carrier); v32's own reals ride the
receipt and the v33 brief, condition-labeled. v32 adds tests, so the suite
count moves past 788 — the THIRD composition change since v21; the 788
band closes at its single point and v32's push lands labeled "first point
at N tests", never pooled.
