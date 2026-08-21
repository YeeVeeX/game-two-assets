# Remedy exploration v15 — DEF-1 k0 gape treatment (pre-registration)

Sprint question: can an **in-ramp, silhouette-invariant recolor of the k0
jaw-gape marker** resolve the DEF-1 aperture percept (the gape reads as the
floor showing through / a detached piece) **without losing the banked strike
tell** — or should the incumbent stand? Deliverables: a mask-derivation tool
(`tools/remedy_masks.py`) with the machine-derived gape masks, a verification
+ selection toolchain (`tools/remedy_metrics.py`), tests, six candidate
sprites in a new additive release (`exports/remedy-v15/`), controlled
selection artifacts, and a selection verdict
(`reviews/remedy-v15/verdict.md`).

**Owner-approval record (verbatim), the authorization this sprint runs
under:** at v14 close the owner ruled **"Approved, proceed"** on the v14
register's routing — option 2, the bounded authoring-exploration sprint —
with accept-as-art remaining a first-class outcome. That approves the
EXPLORATION, not a foregone replacement: the pre-registered decision rule
below defaults to the incumbent on any tie or uncertainty, and the v7 REJECT
precedent makes incumbent-wins a respectable, complete verdict. Nothing
banked is destroyed either way (the release is additive; the banked k0 stays
the pinned history; a later owner reversal costs one pointer, not pixels).

These bars are fixed BEFORE any variant pixel, spec, export, or artifact
exists (v11/v13/v14 rationale law). No bar may be added, removed, reworded,
or reinterpreted after artifacts exist. The gape masks themselves are
committed with this bundle: they are measurements of BANKED bytes, not
variant pixels.

## The subject (fixed here; the two decisive banked numbers)

The v14 register resolved the owner's live sighting ("the head losing a
piece inside it when it does the attack movement") to **DEF-1 (bytes)**: the
k0 strike key paints its jaw-gape marker in the frozen ramp accent
`#140e0c`, measured at **1.09:1 / 1.16:1 WCAG contrast vs the pinned
zone_1/zone_2 floors** — optically the floor color — while the same pixels
measure **6.6:1 against the body**: the tell works against the body; the
collision is against the floor. On down the band absorbs both 2x2 eye
clusters into one 24px interior mass (`[12,11,19,14]`); on right it severs
the snout tip with an 8px band (`[24,13,27,14]`) beside the intact eye
(`[22,11,23,12]`). Zero interior transparency holes exist anywhere (22/22).
DEF-2 (temporal, the 4-tick exposure) is contingent on DEF-1's disposition
and is NOT adjudicated here; DEF-3 (viewer) is mitigated by the pinned
protocol every artifact in this sprint carries.

## The gape masks (machine-derived; no hand-picked rectangles)

Definition, fixed: per facing,

```
gape = k0 accent pixels
       MINUS the v2-banked translated idle eye pixels
       MINUS the feet caps (row 27)
```

where the translated idle eye pixels are the idle accent pixels off row 27,
translated by the **v2-banked rigid head shift** — down `(0,+2)`, right
`(0,+3)` ("dome and eye rows are byte-exact copies at the declared shifts",
v2 verdict, machine-verified there in tests). The derivation MUST assert:
the translated eye set is a subset of the k0 accent set (both facings), and
the derived masks match the v14 expectations exactly — **16 px down
(`[12,13,19,14]`), 8 px right (`[24,13,27,14]`)**, with down eyes at rows
11–12 cols 12–13 / 18–19 and the right eye at `[22,11,23,12]`. The masks
are written to `reviews/remedy-v15/gape-masks.json` by
`tools/remedy_masks.py --make-masks`, deterministically.

Both derived bands span exactly rows 13–14; the K-R split rule below is
total over them by construction.

## The three variant lanes (fixed here; six sprites total, {down, right} x 3)

Specs are procedurally derived from the **banked k0 export bytes**
(PNG -> grid -> masked recolor -> spec JSON), then built through the pinned
spec -> aseprite -> export chain into `exports/remedy-v15/`. All lanes:
**frozen 5-color ramp only, zero new colors; alpha channel byte-identical
to the banked k0** (decoded-pixel comparison via `png_reader.read_rgba`);
RGB differs ONLY at the declared set.

- **K-S (primary candidate)** — gape -> shade `#8c3818`. Banked context:
  2.26:1 / 2.12:1 vs the zone floors. Trade to measure: shade vs body is
  2.69:1 (vs the accent's 6.6:1) — the tell-softening axis the rubric
  scores separately.
- **K-O (bracketing control)** — gape -> outline `#401c10` (1.17:1 /
  1.10:1 vs floors). **EXPECTED to fail the aperture line**; its role is
  calibrating where the perceptual threshold sits. If K-O unexpectedly
  resolves line 1, that is evidence the aperture percept is not purely
  floor-contrast-driven — a finding either way. K-O failing line 1 is not
  a sprint failure and does not disqualify the sprint's other lanes.
- **K-R (two-tone redesign)** — declared interior diff set = exactly the
  gape mask, recolored with the total split rule: **row 13 -> shade
  `#8c3818`, row 14 -> outline `#401c10`** (both facings; both derived
  bands span exactly rows 13–14). Design intent: mouth-with-depth — the
  lit interior sits at the top (maximizing eye separation: accent vs shade
  2.45:1, vs the accent-vs-outline 1.27:1 that would rebuild the merged
  dark mass under the eyes), the jaw-line shadow at the bottom rim.

Declared diff sets: K-S and K-O recolor exactly the gape mask to one color;
K-R recolors exactly the gape mask under the split rule. All three sets are
disjoint from the eye pixels and the feet caps by derivation. Asset ids,
mechanical: `player_1_lane_b_attack_{facing}_k0_{ks|ko|kr}`.

Silhouette invariance is the load-bearing scope bound: alpha untouched
means every banked v2/v3 NUMERIC bar (XOR/union deltas, confusability
floor/ceiling, mass, bbox, feet row) stays literally valid by construction
— machine-verified here, never re-argued.

## Release mechanics (frozen-state law, risk 1)

- The release lives at `exports/remedy-v15/` — outside the
  `check_export_pins` glob (`exports/calibration-*/*.png`) and outside its
  frozen `RELEASE_IDS`. No new directory matching `calibration-*` may be
  created by this sprint.
- `tools/make_release.py` (frozen registry) and `tools/export_assets.py`
  are pinned by banked releases and are NOT edited. `tools/remedy_masks.py
  --make-release` emits the remedy-v15 release.json with the same honesty
  rule (refuse unless sources/, tools/, manifests/ are clean vs HEAD) and
  the same gate schema: origin `procedural`, derivation notes naming source
  bytes + mask + lane, toolchain pinning the unmodified
  `tools/export_assets.py`.
- Commit shape: (1) THIS pre-registration bundle (rationale + derivation
  tool + masks + metrics tool + tests) before any variant pixel exists;
  (2) variant sources (specs + .aseprite) — the release-manifest honesty
  rule requires sources committed before the manifest can record their
  commit (the banked v5 pattern: sources commit, then bank commit);
  (3) the bank commit (exports + release.json + selection artifacts +
  remedy-manifest + verdict) after the council pass and HFO review are
  folded. The two-commit LAW's intent — every bar fixed before any
  artifact it judges exists — is carried by commit 1.
- `exports/calibration-v2` k0 bytes stay untouched: the variants are
  ADDITIVE candidates; the banked k0 remains the pinned history every
  banked sheet regenerates from.

## The pinned viewing protocol (v14, restated; every artifact carries it)

- Artifacts are pre-scaled integer nearest-neighbor at 4x AND 8x; viewed at
  100% viewer zoom with fit-to-window OFF. No other viewing condition may
  ground a verdict line.
- APNG delays via the banked encoder: real-speed = exact `(1, 60)` per tick
  with the banked `(30, 60)` final hold; slowed variant = `(6, 60)` per
  tick (6x slower, integer tick multiple) with the same final hold. Both
  delay lists declared in the manifest.
- Per-tick strips at 8x NN over both zone palettes are the stills-domain
  evidence; the APNGs are the at-speed evidence.
- Percepts reproducible only outside this protocol are viewer-domain by
  the v14 taxonomy and ground nothing here.

## Selection artifacts (fixed matrix)

Composition via the banked chain only (`select_pose` stream via
`pose_integrity_metrics.audit_stream`, `compose_cell`, `encode_apng`,
banked font — drawn labels avoid the missing Q/V/punctuation glyphs). The
audited stream is the same 21-tick declared integration mapping as v14
(T00–T01 idle, T02 w0, T03–T06 a0 at −3, T07–T10 k0 at +6, T11 s0,
T12–T17 r0, T18 x0, T19–T20 idle). Variants substitute ONLY the k0 sprite.

- **Strips (4):** `synthetic-remedy-strip-{down,right}-{z1,z2}-8x.png` —
  per (facing, zone), four stream-rows stacked for direct comparison
  (INCUMBENT, KS, KO, KR) over the pre-registered comparison window
  **T05–T12** (one a0 context tick + the a0->k0 cut + the full 4-tick k0
  hold + the k0->s0 cut + one r0 context tick), 8x NN, drawn SYNTHETIC/EXP
  banner + protocol line. The banked v14 strips remain the full-sequence
  incumbent context.
- **APNGs (24):** `synthetic-remedy-{ks,ko,kr}-{down,right}[-slow6]-{4,8}x.apng`
  — full 21-tick stream, incumbent pane and variant pane side by side in
  every frame (down: horizontal panes; right: vertical panes), per-frame
  drawn labels, zone_1, real 1/60 s and slowed 6/60 s, 4x and 8x.
- `remedy-report.json` (machine tables) + `remedy-manifest.json`
  (provenance class SYNTHETIC, module pins, declared recolor maps,
  protocol, artifact hashes, double-build evidence).

## INTEGRITY bars (any red stops the sprint; all-must-pass)

1. **Full suite green** including the new tests
   (`.venv/Scripts/python.exe -m unittest discover -s tests`).
2. **Both asset_gate runs exit 0** — step 0 (done: mechanical identity
   re-pin `3c0ff6c` -> `da5119c` committed alone, all 5 pinned blobs
   identical, attack_timing 5/4/8/13 re-verified) and again immediately
   before banking, with the new release gate-valid at the live pin.
3. **`tools/track_recompose.py --check` AND
   `tools/pose_integrity_metrics.py --check` both exit 0 at banking** —
   machine proof no pinned module or banked artifact moved.
4. **Alpha identity, machine-proved, 6/6:** every variant's decoded alpha
   plane byte-identical to the banked k0's (via `png_reader.read_rgba`).
5. **Diff declaration, machine-proved, 6/6:** RGB differs from the banked
   k0 at EXACTLY the declared set (K-S/K-O: the gape mask; K-R: the gape
   mask under the declared split), every new color inside the frozen
   5-color ramp, the diff set disjoint from eye pixels and feet caps.
6. **Eye integrity, machine-proved, 6/6:** down variants carry exactly two
   SEPARATE 2x2 accent eye clusters at the banked translated positions
   (`[12,11,13,12]`, `[18,11,19,12]`) plus the two banked feet caps and no
   other accent; right variants carry exactly the banked k0 accent set
   minus the gape band (eye `[22,11,23,12]` + feet caps).
7. **Interior holes = 0** in all six variants (banked detector, unmodified).
8. **26 banked export pins byte-verified** (`check_export_pins`) AND the
   remedy-v15 release's own pins verified AND `exports/remedy-v15/`
   contains exactly the six declared PNGs + release.json AND no
   `exports/calibration-*` file changed or appeared.
9. **Banked tool files untouched** — every imported banked module SHA-256
   pinned in `remedy-manifest.json` and re-verified by `--check` and
   tests; `tools/export_assets.py` / `tools/make_release.py` untouched;
   zero edits to any module pinned by the v13/v14 manifests.
10. **Specs contract-valid:** every variant spec loads under the banked
    `pixel_spec.load_spec` (32x32, palette <= 8, bounds `[2,2,29,29]`,
    anchor `[16,30]`) and the pinned exporter's own verification passes.
11. **Determinism:** masks JSON, specs, report, strips, and APNGs
    double-build byte-identical in-process; `--check` regenerates every
    committed artifact byte-identically; the spec -> aseprite -> export
    chain reproduces each variant PNG byte-identically across two builds.
    If the chain cannot reproduce byte-exact pixels, STOP and re-ask
    (contract break, not a workaround target).
12. **Zero writes into `../game-two`**; read-only `git -C ../game-two
    show/log/diff` from this repo's cwd only.
13. **SYNTHETIC/EXP labels on every review artifact** — filename, manifest
    (`provenance.class = "SYNTHETIC"`), and pixels (drawn banner on strips;
    drawn per-frame label on APNGs).
14. **Citations at the fresh pin with file:line**; banked-verdict quotes
    read from the committed texts this session; the owner-approval record
    verbatim in this rationale (above).

## MEASUREMENT bars (machine facts; fixed definitions)

- **Mask derivation** per the fixed definition above, with the subset and
  16/8 expectation assertions.
- **Diff-declaration verification** (per variant): decode banked k0 and
  variant via `read_rgba`; alpha planes byte-equal; the set
  `{(x,y): rgb differs}` equals the declared set exactly; every variant
  color in the frozen ramp; declared set disjoint from translated eyes and
  feet caps.
- **Eye-integrity verification** (per variant): the exact accent-cluster
  tables of bar 6, computed by the banked `accent_clusters` unmodified.
- **v14 audit re-run per variant:** `interior_holes` (= 0), accent-cluster
  table, color histogram, and the two k0-adjacent cut localizations
  (a0 -> k0v, k0v -> s0) via the banked `cut_changes` — silhouette
  clusters must equal the banked k0's exactly (alpha identity corollary,
  asserted); recolor clusters reported.
- **Contrast table per lane color:** WCAG ratio + RGB distance of `#8c3818`
  and `#401c10` vs zone_1/zone_2 floor and grid and vs the body — via the
  banked `contrast_ratio`. Context for the perceptual read, never a bar:
  shade 2.26/2.12 floors, 2.69 body; outline 1.17/1.10 floors, 5.21 body;
  accent (incumbent) 1.09/1.16 floors, 6.60 body.
- **Determinism** as INTEGRITY bar 11.

Structural machine bars only. **"The aperture reads as resolved" and "the
strike tell still lands" are perceptual lines judged at the pinned protocol
on committed artifacts, never numeric bars** (the v9 category-law lesson:
no cross-class numeric dominance claim is registered or needed; no contrast
number above is a pass/fail threshold).

## PERCEPTUAL rubric (fixed verbatim; judged per line, per facing, per zone, at the pinned protocol, on committed artifacts)

1. **DEF-1 aperture resolved** — the k0 interior no longer reads as the
   background showing through or a piece detached from the head (down: the
   face carries visible eye structure through the active window; right:
   the snout tip reads attached to the head).
2. **Strike tell preserved** — the k0 tick still reads instantly as the
   attack state against idle/walk, judged against the banked v2 read (the
   v2 PASS is the reference, not re-opened; the open-jaw marker may change
   color, not legibility-as-state).
3. **Eyes visible on down through the active window** (T07–T10).
4. **Identity / no new state confusion** — the variant reads as the same
   creature in the same state grammar; the recolored mouth must not read
   as a new signal class (hurt flash, telegraph, transition gold) or a
   different creature.

## Decision rule (fixed verbatim)

> A variant is selected only if ALL machine bars pass AND perceptual lines
> 1–4 pass on both facings and both zones AND it beats the incumbent on
> line 1 without losing line 2. Any tie or uncertainty on any line -> the
> incumbent stands and accept-as-art is recorded as the disposition. If
> every lane fails line 2, the incumbent wins and the verdict routes a v16
> silhouette-class redesign PROPOSAL instead. If MULTIPLE variants qualify,
> select by (a) the stronger line-1 resolution at the pinned protocol; if
> still tied, (b) the smaller departure from the banked k0 (single-color
> recolor beats two-tone) — K-S is the pre-registered primary candidate.
> Incumbent-wins is a complete, bankable outcome; no variant is forced to
> justify the sprint.

The verdict additionally records: DEF-1 disposition cross-referenced to the
v14 register (banked verdicts untouched); DEF-2 contingency resolution
(dissolved-if-selected / forwarded-if-incumbent — recorded, not
adjudicated); explicit non-claims (no integration, no banked byte moved,
at-speed fusion still unmeasured and routed to the banked capture
instrument); council reconciliation appendix; presentation scored
separately from accuracy.

## QUALITY bars (blocking)

- **HFO pass** on `verdict.md` and the release provenance notes (owner
  register; severity-honest verbs; no promises; accuracy and presentation
  scored separately).
- **One consolidated cross-vendor council call** (Kimi K2.5, <= 8k tokens
  total, `--max-tokens ~2600`, response redirected to a file and read as
  UTF-8, the FULL primary evidence inlined — the masks, the per-variant
  contrast/cluster numbers, the rubric verdicts, the banked v2/v3 quotes)
  attacking: (1) mask-derivation soundness — eye-subtraction correctness;
  does the diff-declaration bar actually pin silhouette invariance;
  (2) tell-preservation honesty — is the selected variant's strike read
  really intact, or is the rubric biased toward the fix; (3) frozen-state
  integrity — does anything in the release mechanics or new tooling
  threaten a banked pin; (4) decision-rule honesty — is incumbent-wins
  genuinely reachable; (5) the biggest unthought risk. Every REFUTED
  re-verified against primary bytes before adoption (v12/v13/v14
  precedent); reconciliation banked in the verdict appendix; adoptions
  folded before the final commit.

## Mail-in status (step 0, recorded here for the verdict)

Inbox at step 0: only `done/` — no new receipts, nothing owed, nothing
polled. No outbound mail is due: the step-0 drift (`3c0ff6c` ->
`da5119c8`, 9 docs/test-only hops, all 5 pinned blobs identical) was
identity-only, so the standing content-drift note protocol does not
trigger. The only outbound mail this sprint would be a re-pin note if
committed content drift lands mid-sprint.

## Hard boundaries (this sprint)

Only the six declared variant sprites — zero other new pixels; no edits to
any banked pose PNG, banked tool, banked verdict, or pinned module; no new
export dirs matching `calibration-*`; no integration, no game-two writes,
no runtime claims; no DEF-2 adjudication (disposition-recording only); no
work on "other visual flaws"; no lore (mechanical ids; owner quotes are
carriers, not narrative); no generated imagery (pure procedural
derivation); no polling mail; no settle-bob; no capture execution; audio
and tile era stay parked. Budget: one sprint, six sprites max, one
release, council <= 8k tokens; no second remedy family; silhouette-class
redesign is the v16 PROPOSAL path, never this sprint's edit.

## Stop conditions

The sprint stops after: this bundle (rationale + derivation tool + masks +
metrics tool + tests) banked before any variant pixel exists -> variant
sources committed -> exports + release built and self-checked -> full
suite + pre-banking gate green -> both prior `--check`s green -> council +
HFO folded -> verdict banked -> push. Any INTEGRITY red stops the sprint
at the red. Incumbent-wins stops the sprint exactly as completely as a
selection does.
