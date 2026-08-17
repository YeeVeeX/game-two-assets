# Calibration v3 — windup-anticipation coherence verdict

Reviewed artifacts:

- `reviews/calibration-v3/anticipation-sheet.png` — SHA-256
  `52688d14a85596ce101f1d05106c425f5f04dca7735a437bea6c9803a63e13b2`,
  regenerated twice byte-identically.
- `reviews/calibration-v3/anticipation-metrics.json` — SHA-256
  `424b42bfd8c12baa68023ab33965a765adfc65691d1adadf3e50f285ccd1c898`,
  regenerated twice byte-identically.
- Release under review: `exports/calibration-v3/release.json` (2 creature
  exports), gate-valid against the re-pinned live game commit
  (`3869958c…`, worktree clean of tracked changes; the owner-approved
  conditional re-pin was executed twice this sprint — HEAD moved mid-session
  both times, all five pinned source hashes verified LF-identical each
  time, content-identical to the original capture commit `219121d3…`).
- Banked inputs (untouched): calibration-v0 idles, v1 walk frames, v2
  attack keys. All three banked sheets regenerate byte-identically under
  the new toolchain (`tests/test_feedback_tools.py`, mechanically
  enforced; the v2 feedback sheet is now covered by the same regression).
- Viewing-aid GIFs: declined — the GRAMMAR row carries the windup→strike
  sequence spatially at the pinned draw offsets; a temporal proof belongs
  to an integration replay capture, not a repainted preview.
- Vision-critical judgment: session model `us.anthropic.claude-fable-5`
  (verified from `PI_MODEL`, not self-report), per the owner's
  quality-over-cost directive; the council seat stays cross-vendor by
  design — independence is its evidentiary value.

Question under test (banked v2 next-hypothesis): does a held anticipation
(coil) pose make the windup state readable on the lane-B body at native 1x
— distinct from every walk frame AND from the strike key — at the pinned
−3px windup offset?

## Accuracy — all-must-pass

| Item | Verdict | Evidence |
|---|---|---|
| 32x32 RGBA8, hard alpha, 5-color frozen ramp, declared palettes | PASS | asset gate + exporter pixel verification, both poses |
| Occupied pixels inside `[2,2,29,29]`, anchor `[16,30]` | PASS | spec validation + gate bbox check (down `[9,8,22,27]`, right `[7,7,26,27]`) |
| a0 feet-contact row within ±1px of idle | PASS | row 27 both poses, 0 drift (`anticipation_metrics --check`) |
| Walk-side confusability floor ≥ 25% vs idle and every walk frame | PASS | down 31.10%, right 36.57% (`--check`) |
| Pre-registered a0-vs-k0 distinctness ≥ 25% | PASS | down 27.18%, right 31.97% (`--check`) |
| No delta at/above the 44.44% cross-facing identity ceiling | PASS | max 37.04 / 42.86 (`--check`) |
| Derivation from frozen frames declared and machine-verified | PASS | head blocks byte-exact at declared shifts — down (0,+4) rows 4–14, right (−2,+3) rows 4–9 (test); ramp unchanged (test) |
| No new manifest capture needed; `feedback_states` pins reused | PASS | flash rgb, flicker cadence, lunge −3/+6 all read from the banked block; `runtime-baseline.json` touched only by the two step-0 re-pin commits |
| Sheet + metrics deterministic; v0/v1/v2 artifacts byte-stable | PASS | double-SHA above; regression tests |
| Release manifest: new id, full hash chain, real source commit | PASS | asset gate over all four releases, exit 0 |
| No game-two changes | PASS | read-only `git show`/`rev-parse` against `../game-two` only; its worktree carries one untracked draft from a parallel session, not ours |

**Accuracy: 11/11.**

## Presentation — anticipation rubric at native 1x

Measured evidence (`tools/anticipation_metrics.py`, tested; silhouette
delta = 100·XOR/union):

| Metric | down a0 | right a0 |
|---|---|---|
| delta vs idle, f0–f3 (%) | 31.10, 33.92, 37.04, 33.92, 31.10 | 36.57, 42.86, 40.77, 36.57, 36.57 |
| walk confusability floor (bar 25.0) | 31.10 | 36.57 |
| a0-vs-k0 distinctness (bar 25.0) | **27.18** (tightest margin on the sheet) | 31.97 |
| max delta / identity ceiling | 37.04 / 44.44 | **42.86** / 44.44 (closest approach yet, 1.58pt) |
| banked walk envelope (max pair delta) | 22.09 | 22.09 |
| mass vs idle | 227 vs 251 (−9.56%) | 277 vs 295 (−6.10%) |
| feet row / drift | 27 / 0 | 27 / 0 |
| bbox height vs idle | 20 vs 24 rows (−4) | 21 vs 24 rows (−3) |
| head-region share of vs-idle change | 75.0% | 71.88% |
| bbox-ring idle→a0 / a0→k0 max edge (integration record) | 4 / 2 px | 3 / 2 px |
| ACC surviving accent px (idle+walks+a0 / k0) | 14 / 30 | 10 / 18 |
| accent-vs-crimson contrast (WCAG non-text minimum 3:1) | 3.33 | 3.33 |

Structural separation, verified at spec level (not inference):

- **Down coil vs walk band:** head-drop magnitude +4 (walks use ±1, the
  strike +2); lower-torso rows 19–22 measure 12 wide where idle and every
  walk frame measure 10; the leg zone folds to 3 rows with row 24 a solid
  band — every frozen down frame keeps a 4-row two-group leg zone
  footprint. The Y axis is shared with the walk bob; the magnitude and the
  width/fold reshaping are not.
- **Down coil vs strike:** the k0 jaw-gape rows contribute **zero** to the
  27.18% silhouette delta (coverage identical — the gape is an interior
  recolor); the separation is carried by geometry: head top 8 vs 6, brace
  zone 12 vs 16 wide, legs folded-under at idle columns vs splayed 2px
  outward with 4-row height. The closed-vs-open jaw is an additional color
  cue on top of a passing silhouette bar, not its substance.
- **Right coil:** the −2px head retraction is a virgin axis — idle, all
  four walks, and k0 all keep the dome at cols 16–23; a0 alone sits at
  14–21. Low slab + rear haunch ridge + 1px-gathered folded legs vs k0's
  forward stretch (front leg cols 21–23, snout gape).

Rubric line by line (1x FILM/FLASH/ACC/GRAMMAR rows over exact zone
palettes; DIFF and 2x/4x diagnostics; judged on the sheet by the session
vision model, Fable 5):

1. **Windup reads at 1x.** PASS. Both coils exceed the entire banked walk
   envelope against every frozen frame (floors 31.10/36.57 vs 22.09) and
   the native read agrees: in FILM both read instantly as
   hunkered-and-ready against the tall walking silhouettes — down drops
   the byte-exact face onto a bulged haunch; right pulls the face back and
   down over a low slab. The −3px GRAMMAR cell strengthens the read: pose
   carries the state, offset carries the direction.
2. **Windup is not the strike.** PASS, tightest result on the sheet and
   disclosed as such (down 27.18 vs bar 25.0). The two states share one
   grammar by design; at 1x they read as coil vs release — closed face +
   folded legs + narrower body against gape + brace/stretch + splayed
   legs. The silhouette bar passes on geometry alone (jaw contributes 0 to
   it); combat-speed reading under motion remains an integration item.
3. **Grammar sequence reads as escalation.** PASS. idle → f1 → a0 →
   a0@−3px → k0 → k0@+6px reads as stand → step → crouch → recoil →
   strike → hit in both facings; the recoil direction (up-screen for down,
   back-screen for right) is the pinned runtime windup direction, opposite
   the lunge — the 9px excursion between the two offset cells is visibly
   causal, not positional noise, when the poses differ (the v2 finding
   that the offset alone was subthreshold used the *same* pose at both
   offsets).
4. **Flash-accent identity recovery without new colors.** PASS as an
   exploration verdict. The ACC row restores the eye clusters and feet
   caps (down: 14px in 4 clusters — two 2x2 eyes + two 3px caps; right:
   10px in 3 clusters) over the pinned crimson using only the frozen ramp
   accent; beside the eyeless plain-FLASH row the identity recovery is
   unmistakable at 1x, and the k0 gape band (30/18px) even keeps the
   strike state readable mid-flash. Accent-vs-crimson contrast 3.33
   clears the WCAG 1.4.11 non-text minimum (3:1) — the 4.5:1 figure is a
   text standard and does not apply. Temporal behavior under the 3-on/3-off
   flicker is untestable on a static sheet — recorded as the adoption
   condition below. **Exploration only; phase-0 exports assume nothing.**

**Presentation scores (accuracy scored separately above):**

- **Attack-down a0: 8.5/10.** The cleanest grammar row on any sheet so
  far; coil, recoil, strike, and lunge read as four causally ordered
  moments. The 27.18% strike margin is honest but thin — disclosed.
- **Attack-right a0: 8/10.** Strongest walk separation (36.57 floor) and
  the virgin retraction axis; runs closest to the identity ceiling
  (42.86 vs f0, 1.58pt) — the byte-exact face, kept `oss` tail marker,
  and unchanged ramp hold it as the same creature at 1x and 4x, but this
  is the least headroom any banked pose has consumed.
- **Flash-accent exploration: recommended** for the future integration
  design, conditional on a replay-capture check of the flicker cadence.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated verdict, 3,400 tokens spent of the 8k cap (1,400 in /
2,000 out, single call; the reviewer hit max_tokens inside its summary
table — all six question verdicts were complete). Models see text, not
pixels; every attack was re-verified against artifacts:

1. **Q1 (down a0-vs-k0 honesty) — UNCERTAIN**, on the premise that the
   differentiator is "a single binary pixel cluster" (the jaw). **REFUTED
   WITH PIXELS:** the gape rows are coverage-identical between the poses —
   the jaw contributes 0px to the silhouette delta; the 27.18% is carried
   by head height, brace width, and leg geometry (spec-level verification
   in this sprint's review notes). ACCEPTED from the same answer: the
   margin is the sheet's tightest and is disclosed in the score; motion
   readability at combat speed is an integration item.
2. **Q2 (right 42.86 vs ceiling) — CONFIRMED**, with the caveat that the
   44.44% ceiling transfers from cross-facing idles to same-facing action
   pairs. Already banked doctrine (v1 reconciliation, reaffirmed in v2):
   the window is necessary-not-sufficient; sufficiency evidence is the
   native read plus the byte-exact head, tail marker, and ramp. The
   "96.4% of identity budget consumed" framing is adopted as a disclosed
   watch-item above.
3. **Q3 (head-led delta = wrong design) — PARTIALLY ACCEPTED:** the
   claim that the down coil uses "a dimension walks never use" was
   imprecise — the Y axis is shared (f1 bobs −1, k0 drops +2); what is
   virgin is the magnitude (+4) plus torso width and leg-zone reshaping,
   and for right the −2 retraction axis (spec-verified: no frozen frame
   moves the dome in x). The rationale's wording is corrected by this
   verdict. REFUTED as a defect: bbox height compresses 4/3 rows with
   mass −9.6/−6.1% — measurable crouch-compression, and the byte-exact
   face + GRAMMAR sequencing carry "same creature crouching" at 1x.
4. **Q4 (ACC px too few) — UNCERTAIN** on clustering and temporal
   integration. RESOLVED WITH PIXELS: the accents are clustered (eye
   blocks + feet caps, counts above), not scattered; the WCAG figure the
   review cited (4.5:1) is the text standard — the applicable non-text
   minimum (3:1) is met at 3.33. ACCEPTED: temporal integration under
   flicker is unprovable statically → adoption condition.
5. **Q5 (spatial claim boundary) — CONFIRMED.** The suggestion to mark
   the decision explicitly spatial is adopted in the decision line below
   (the sprint question was pre-registered as spatial; the temporal hold
   was never claimed).
6. **Q6 (unconsidered risks):** Risk 1 (9px windup→lunge excursion could
   read as tracking error without ground anchors) — ACCEPTED as a new
   integration finding below; the offsets are pinned runtime behavior,
   not asset-side changes. Risk 2 (cross-facing mass variance 227 vs 277
   "same pose different mass") — REFUTED: the facings' idle masses differ
   by construction since v0 (251 vs 295); per-facing drifts are −9.56%
   and −6.10%, both inside the banked k0 precedent (−12.2%). Risk 3 (k0
   baseline contamination) — REFUTED: k0 and a0 derive from the same
   frozen v0 idles, machine-verified byte-exact in both test suites.
   Risk 4 (ceiling misapplication) — same as Q2, banked doctrine.

## Decision

**PASS — windup-anticipation coherence is banked as answered YES, with the
pre-registered spatial scope: a held coil pose makes the windup state
readable on the lane-B body at native 1x, distinct from every walk frame
and from the strike key, at the pinned −3px windup offset.** The coil
occupies pose dimensions verified virgin at spec level (drop magnitude +
torso/leg reshaping; retraction axis on right), exceeds the banked walk
envelope against every frozen frame, stays below the identity ceiling,
and the full attack grammar reads as causal escalation. What this sprint
does **not** claim: that the runtime's *temporal* hold (the same frame
held for the windup duration) reads as tension at combat speed — that is
an integration replay-capture question, recorded below.

Status per contract: **selectable candidates only.** No integration —
v17 closed and v18 opened in game-two mid-sprint, which changes nothing
here: the runtime-integration stop conditions in `docs/asset-contract.md`
still apply, and the one-way boundary holds.

## Findings for any future integration design (recorded, no action now)

- **Temporal windup proof:** hold a0 at −3px for the pinned windup
  duration in a replay capture and verify the hold reads as tension, not
  freeze; this is the missing half of the windup answer.
- **Displacement anchoring (council catch):** the 9px windup→lunge
  excursion is drawn without ground anchors; verify in the same capture
  that it reads as attack motion, not position error. Any smoothing or
  dust/shadow anchoring is engine-side, outside this repo's scope.
- **Flash-accent adoption:** redraw the ramp-accent pixels over the flash
  fill exactly as the ACC row simulates (mirrors the runtime's
  notch-over-flash pattern); confirm eye recovery under the real
  3-on/3-off cadence before adopting.
- **Ring breathing across the grammar:** bbox-fit ring edge shifts are
  4px/3px (idle→a0) and 2px (a0→k0) — larger than the 1px walk breathing
  banked in v2; an integration that adopts the bbox-fit ring should decide
  between per-state ring rects or accepting the attack-cycle jump.
- **Sequence timing:** the anticipation hold at 100–200ms with a ~1-frame
  strike (KB timing reference) is the vocabulary the runtime's windup
  duration should be checked against when the full grammar is captured.

## Next hypothesis (single, for a future bounded sprint — not started)

Temporal grammar verification: drive the banked idle → walk → a0(−3px
hold) → k0(+6px) sequence through a scripted replay capture at real tick
timing (still outside game-two, e.g. a harness-side compositor over the
pinned constants) and verify the windup hold and strike release read as
tension→release at combat speed — the temporal half this sheet could not
prove, plus the displacement-anchoring check from the council review.

## Stop

Sprint 3 stops here: one reviewed anticipation sheet, one banked verdict,
two anticipation exports, three re-pin/change-set commits. No smear
frames, no full attack animation, no 8-direction set, no terrain, no
enemies, no pack, no game-two changes.
