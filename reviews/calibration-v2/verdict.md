# Calibration v2 — feedback-state coherence verdict

Reviewed artifacts:

- `reviews/calibration-v2/feedback-sheet.png` — SHA-256
  `d2bd50d5ed22e76a76698fb7c2e1bcac52b85dafd446ed67fbf8735b3b20a059`,
  regenerated twice byte-identically.
- `reviews/calibration-v2/feedback-metrics.json` — SHA-256
  `4498ceefd0ec33ff2108452bc479c36667bd3c26ab9d878379d01fb239786f95`,
  regenerated twice byte-identically.
- Release under review: `exports/calibration-v2/release.json` (2 creature
  exports), gate-valid against the live game pin (`219121d3…`, worktree
  clean) and the pinned Aseprite binary.
- Banked inputs (untouched): calibration-v0 idles, calibration-v1 walk
  frames. Both banked sheets regenerate byte-identically under the new
  toolchain (`tests/test_feedback_tools.py`, mechanically enforced).
- Viewing-aid GIFs: declined this sprint — a flash-recolor GIF would require
  flash-colored native sources (new colors in specs, prohibited); the
  stacked FILM/FLASH rows carry the flicker alternation spatially.

Question under test (banked v1 next-hypothesis): do body-scale state
changes stay readable on the lane-B body at native 1x (Vlambeer
body-carries-state)?

## Accuracy — all-must-pass

| Item | Verdict | Evidence |
|---|---|---|
| 32x32 RGBA8, hard alpha, 5-color frozen ramp, declared palettes | PASS | asset gate + exporter pixel verification, both poses |
| Occupied pixels inside `[2,2,29,29]`, anchor `[16,30]` | PASS | spec validation + gate bbox check (down `[8,6,23,27]`, right `[7,7,28,27]`) |
| Attack feet-contact row within ±1px of idle | PASS | row 27 both poses, 0 drift (`feedback_metrics --check`) |
| Confusability floor ≥ 25% vs idle and every walk frame | PASS | down 33.87%, right 30.06% (`--check`) |
| No delta at/above the 44.44% cross-facing identity ceiling | PASS | max 39.14 / 39.08 (`--check`) |
| Derivation from frozen frames declared and machine-verified | PASS | dome+eye rows byte-exact at the declared shifts (test); jaw rows silhouette-identical to source idle rows (verified: interior recolor only) |
| Pinned constants captured read-only, additive, cited | PASS | `feedback_states` block; exact lines in rationale; `runtime-baseline.json` untouched |
| Sheet + metrics deterministic; v0/v1 artifacts byte-stable | PASS | double-SHA above; regression tests |
| Release manifest: new id, full hash chain, real source commit | PASS | asset gate over all three releases |
| No game-two changes | PASS | `git -C ../game-two status` clean at pinned commit |

**Accuracy: 10/10.**

## Presentation — feedback rubric at native 1x

Measured evidence (`tools/feedback_metrics.py`, tested; silhouette delta =
100·XOR/union):

| Metric | down k0 | right k0 |
|---|---|---|
| delta vs idle, f0-f3 (%) | 33.87, 35.87, 39.14, 35.87, 33.87 | 30.06, 31.1, 39.08, 33.13, 30.06 |
| confusability floor / max (%) | 33.87 / 39.14 | 30.06 / 39.08 |
| identity ceiling (cross-facing) | 44.44 | 44.44 |
| walk-cycle max pair delta (banked) | 22.09 | 22.09 |
| mass vs idle | 269 vs 251 (+7.17%) | 259 vs 295 (−12.2%) |
| feet row / drift | 27 / 0 | 27 / 0 |
| head-region share of change | 37.74% | 64.29% |
| recolored-in-overlap (jaw) px | 95–117 | 64–84 |

Flash (pinned `(200,30,30)`): WCAG contrast vs floors 3.07 (Z1) / 2.88
(Z2); vs walls 1.53 / 1.84. RGB distance to telegraph edge 47.2, telegraph
core 189.2, transition gold 174.4, role base 97.1.

Rings (visible-white-margin ÷ body mass): SIZE geometry 2.92–3.66 across
idle/walk/attack; bbox-fit 1.29–1.92. Bbox-ring breathing: 1px max edge
shift across the walk cycle (incl. seam), 2–3px on idle→attack.

Rubric line by line (1x FILM/FLASH/TELL/ADJ/RING rows over exact zone
palettes; DIFF and 2x/4x diagnostics):

1. **Tell reads at 1x.** PASS. Both poses exceed the entire walk envelope
   (floor 30.06/33.87 vs walk max 22.09) against *every* frozen frame while
   staying under the identity ceiling; at native scale the open jaw + brace
   (down) and the 3px head-drop pounce + jaw (right) read instantly in FILM
   and TELL rows — no walk frame changes head interior, body width, or head
   height, so the tell occupies dimensions the walk never uses. The +6px
   active-lunge cell amplifies the read. Finding: the windup cell (idle at
   the pinned −3px, today's runtime behavior) is subthreshold as a pose
   tell at 1x — recorded as the next-hypothesis candidate, not a defect of
   the key poses.
2. **Flash preserves identity.** PASS. The full-crimson replacement is the
   runtime's own treatment (renderer.rb L470-480) and the KB silhouette
   test passes on both zones: dome+legs (down) and snout+tail profile
   (right) stay unmistakable, facing stays readable, and the k0-flash
   silhouette still reads as the attack state — silhouette carries identity
   AND state through the flash. Floor contrast 3.07/2.88 is clean.
   Disclosed degradations: eyes vanish on flicker-on frames (interior
   pixels; the runtime keeps only its separately-drawn notch), and
   wall-edge contrast drops to 1.53–1.84 on flash-on frames (normal frames
   measure 4.0–5.0 via the outline; the 3-on/3-off alternation restores the
   boundary half the time). Both are recorded as integration findings
   below, not sheet failures.
3. **Ring dominant without drowning the body.** PASS, with the geometry
   question answered. The SIZE ring signals unmistakably but measures
   2.9–3.7× the body in visible white — the v0 "backdrop plate" finding now
   quantified. The bbox-fit exploration variant keeps the possession signal
   unambiguous at 1.3–1.9× while freeing the body silhouette, and its
   animation cost is small (1px walk breathing, 2–3px on attack). **The
   bbox-fit variant wins the exploration question for a future integration
   design; phase-0 exports assume nothing** (asset-contract law; the SIZE
   ring remains the runtime truth).
4. **No cross-signal confusion.** PASS. Telegraph red is chromatically
   close to the flash (distance 47.2) but never shares geometry or
   subject: the swell is a 2px hot-red band around a 32px gold-core slab on
   a bone human body (pinned L446-452, human-faction only, creature.rb
   L70), while the flash is a solid 16–22px creature silhouette; the ADJ
   cells show no confusion at 1x. Player-on-red-tile cannot arise from
   telegraphs: attack-tile overlays are pack-only at the pinned commit
   (renderer.rb L465) — humans telegraph via the body swell alone, so
   adjacency (tested) is the true worst case. Flash vs transition gold:
   174.4 apart, no interaction in the gold ADJ cell. k0 uses only the
   banked ramp, so the v0 gold analysis stands.

**Presentation scores (accuracy scored separately above):**

- **Attack-down k0: 9/10.** The cleanest state read on the sheet: gape +
  brace + splay are unmistakable at 1x in both zones and at the lunge
  offset.
- **Attack-right k0: 8/10.** Strong pounce read; the −12.2% crouch
  compression is deliberate squash and is disclosed; head-drop carries
  64% of the change and the byte-exact head block keeps it the same
  creature.
- **Flash grammar: 8/10.** Identity and state survive the honest worst
  case (full replacement); the eye-vanish and wall-edge caveats belong to
  integration, where the runtime's own notch-over-flash pattern shows the
  fix shape.
- **Ring exploration: bbox-fit recommended** for the future integration
  design.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

Council verdict was **REJECT on claims 1–4, CONFIRM on claim 5** (2,301
tokens spent of the 8k cap: one call, one consolidated verdict). Models see
text, not pixels; every attack was re-verified against artifacts:

1. "25%-floor/44.44%-ceiling window is post-hoc and the ceiling is the
   wrong reference" — **PARTIALLY ACCEPTED, already doctrine:** the window
   is necessary-not-sufficient (v1 reconciliation, reaffirmed); the bar was
   fixed in the rationale before the sheet existed, and the floor is not
   arbitrary — it is the banked walk envelope (22.09%) plus margin: a tell
   inside the walk cycle's own frame-to-frame variation is confusable by
   construction. Sufficiency evidence is the native-scale read plus
   structure analysis (jaw/width/height dimensions unused by the walk).
2. "Eyes vanishing during flash is identity fracture at the worst moment;
   wall contrast 1.53 is catastrophic" — **PARTIALLY ACCEPTED:** recorded
   as the two flash integration findings (redraw accent pixels over the
   flash the way the runtime redraws its notch; verify wall-edge cases in
   integration replay capture). REFUTED as a sheet failure: the treatment
   is the pinned runtime behavior, the silhouette test (the banked
   identity mechanism — 44.44% cross-facing separation is silhouette-only)
   passes on both zones, and the flicker restores full detail every 3
   frames.
3. "Head-region change breaks the v1 rigid-head doctrine; dome becomes a
   C-shape" — **REFUTED with pixels:** dome and eye rows are byte-exact
   copies at the declared shifts (machine-verified in tests); the jaw rows
   are silhouette-identical to their source idle rows in both facings
   (verified: pure interior recolor) — the head translates rigidly and
   does not deform; the state marker is added below the intact eyes.
4. "Flash-on-telegraph overlap untested chaos condition" — **PARTIALLY
   ACCEPTED:** overlap-vs-adjacency was re-verified against the pinned
   renderer: human telegraphs paint no floor tiles (L465 pack-only attack
   overlays), so body-adjacency is the physical worst case and it is
   tested. Remaining chaos conditions (volley-tile proximity to the orange
   ramp, colorblind flash/telegraph separation, ring+flash simultaneity)
   are recorded under unresolved risks.
5. Bbox-fit ring verdict — **CONFIRMED** ("clear metric win; safe
   procedural note").

## Decision

**PASS — feedback-state coherence is banked as answered YES: body-scale
state changes stay readable on the lane-B body at native 1x.** The attack
tells occupy pose dimensions the walk cycle never uses and exceed its
entire measured envelope against every frozen frame; the runtime-faithful
hurt flash preserves identity through silhouette exactly as the banked
identity mechanism predicts; the ring geometry question is answered for
integration (bbox-fit) with the possession signal intact.

Status per contract: **selectable candidates only.** No integration —
game-two v17 remains open; every runtime-integration stop condition in
`docs/asset-contract.md` still applies. The optional anticipation frames
were declined mid-sprint: the brief gates them on the key-pose *verdict*,
which now exists — they are the natural next hypothesis, not a rushed
addendum.

## Findings for any future integration design (recorded, no action now)

- **Ring/dim geometry:** draw possession ring (and ally-dim, same SIZE
  finding, renderer.rb L455) against the sprite bbox + pinned expand, not
  the SIZE constant; accept 1px walk breathing or lock the ring rect per
  facing.
- **Flash accents:** the runtime redraws its facing notch over the flash;
  a sprite integration should redraw the eye/feet accent pixels (`#140e0c`)
  over the flash fill so identity detail survives flicker-on frames, and
  verify flash-body wall-edge readability in a replay capture.
- **Windup tell:** the pinned −3px offset alone is subthreshold on this
  body at 1x; an anticipation pose is required if windup readability
  matters at body scale (see next hypothesis).
- **Uniform pack grammar:** all pack bodies flash the same crimson
  (L471-476); ownership stays ring-carried (v17 decision 10) — consistent,
  but a co-op capture should confirm two flashing bodies don't read as one.
- **Out-of-scope color risks noted for later sheets:** volley-tile orange
  vs the role-base ramp; colorblind separation of flash vs telegraph.

## Next hypothesis (single, for a future bounded sprint — not started)

Windup anticipation coherence: author one anticipation (coil) pose per
facing and re-run this sheet's TELL protocol — does a held anticipation
pose at the pinned −3px windup offset make the windup state readable at 1x
(floor above the walk envelope) without confusing with any walk frame or
the strike key? Optionally include the flash-accent-persistence variant as
a sheet-level row using only ramp colors.

## Stop

Sprint 2 stops here: one reviewed feedback sheet, one banked verdict, two
attack-key exports. No anticipation frames, no full attack animation, no
8-direction set, no terrain, no enemies, no pack, no game-two changes.
