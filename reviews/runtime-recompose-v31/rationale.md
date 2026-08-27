# v31 — first RUNTIME recomposition: single-creature instrument readiness (EXP-class) — rationale (PRE-REGISTERED)

**Status: protocols and bars FIXED BEFORE any palette bytes, extraction
code, or artifact bytes exist.** This file is committed with every verdict
cell NULL (commit A). The palette + extraction code land at commit B, the
artifacts at commit C, the judged verdict at commit D — the commit-A
discipline every calibration sprint used. No cell may be filled before its
evidence exists.

**Authorization (owner order, recorded verbatim from the v31 brief):**
"AUTHORIZATION: the v30 verdict pinned that rendering any RUNTIME track
'waits for its own owner brief' - THIS is that brief, owner-launched
(record this line in the verdict as the owner order)."

## Review objects

- The intaken evidence: bundle `20260826T175326Z_p1_42`
  (`evidence/replay/20260826T175326Z_p1_42/`; intake chain in
  `intake-record.md`); subject track = `tracks/reference-attack-window.json`
  sha256 `dd68c8cbb324dd7faf19197df05922e32d20a65b8c3b08928f775da76f44545d`
  (frames 420..560, 141 ticks, 18 creatures, zone `district`, possessed
  exactly 1/tick — v30 n2).
- The consumer: `tools/track_recompose.py`
  (`declared-integration-mapping-v1`), extended IN PLACE (unpinned-tool
  census stays 4; zero new tool files).
- The artifact law: `docs/replay-capture-design.md` section 6 (native +
  integer zoom, exact 1/60 s, mapping version-pin, EXP disclosure); the
  intake law: section 5, already live in code (`verify_runtime_intake`).

## Role boundary (pre-registered)

EXP-class instrument readiness ONLY. Every artifact answers ZERO register
items and says so in pixels, filename, and manifest. Zero adjudication
language anywhere (no bar, no severity, no "reads correctly"). The
at-speed and declared-viewport watch items become artifact-VIEWABLE
(MEASURED-capable) through this sprint and stay NOT MEASURED — the owner
views at the declared display and sequences adjudication separately.
Full-scene multi-creature composition (draw order, neighbors) is a
SEPARATE owner decision — out of scope. Item (h) display-chain half and
the live-camera-true viewport stay named uncovered: the declared
sub-window below is the recomposition's OWN window (s84 item 2's
allowance), never the game camera. Zero new art pixels — composition
re-places banked export bytes only. Zero exports; zero release manifests;
zero register/status edits; mapping SEMANTICS untouched (`select_pose`
byte-identical); typed refusals never weakened; RUNTIME composition
admitted only through `verify_runtime_intake`, run LIVE in the generation
path. `docs/state-track-schema.md` stays draft-1 history; frozen docs and
surfaces byte-untouched.

## Extraction protocol (pre-registered verbatim; executed AFTER this commit)

1. **Subject.** The possessed creature of track 1 (exactly one per tick,
   v30 n2). Mechanically: for every tick, exactly one record carries
   `possessed == true`; the holder must be ONE name across all 141 ticks.
   Zero or multiple holders on any tick, or possession moving between
   names inside the window → typed refusal, STOP and bank (no owner
   ruling exists for possession handoffs under single-subject
   extraction). RECORD the subject's name + kit from bytes in the subject
   decision capture and the artifact manifest.
2. **Kit gate.** If the subject's kit is NOT `striker`, STOP and bank —
   the banked pose set is striker art; substituting it for another kit in
   a RUNTIME-labeled artifact needs an owner call.
3. **Subject decision stream FIRST (TEXT).** Extend the consumer with a
   per-creature filter (`--decisions <track> --creature <name>`): for
   every tick where the subject is present, emit frame + either the
   mapped decision (pose, facing, offset_px, draw vector) or the TYPED
   refusal class. This capture is the span-derivation input and is banked
   as evidence (`decisions-subject.json`).
4. **Span policy (FIXED).** Candidate spans = maximal runs of consecutive
   frames where the subject is present AND maps refusal-free (a typed
   refusal on the subject breaks the run; refusals on OTHER creatures are
   irrelevant — single-subject extraction). A candidate qualifies iff it
   contains a COMPLETE ATTACK CYCLE: a contiguous subsequence of the
   subject's pose stream equal to
   `[w0] + [a0] * (windup_frames - 1) + [k0] * active_frames + [s0] +
   [r0] * (recovery_frames - 2) + [x0]`
   (under the subject's OWN kit constants; for striker 13/5/4/8 that is
   w0, a0 x4, k0 x4, s0, r0 x6, x0 = 17 ticks), followed by at least one
   later tick INSIDE the span with `attack_state == "idle"` (returned to
   idle). Selection: the LONGEST qualifying span; tie → the EARLIEST
   (lowest first frame). If NO candidate qualifies → STOP branch: bank
   the TEXT analysis as the sprint's finding, produce ZERO artifacts, the
   verdict still lands.
5. **Window policy (FIXED declared sub-window).** For each span tick t
   with subject record r: `(pose, facing, offset) = select_pose(r,
   constants)`; world draw vector `wx = round_half_up(r.px) + offset *
   r.facing[0]`, `wy = round_half_up(r.py) + offset * r.facing[1]`; the
   sprite covers `[wx, wx + TILE) x [wy, wy + TILE)` (TILE = 32).
   Bounding box over the span: `min_x, min_y, max_x, max_y` over all
   `wx, wy`. Window (whole-TILE aligned to the world tile grid, one full
   TILE margin, rounding outward):
   - `x0 = floor(min_x / TILE) * TILE - TILE`
   - `y0 = floor(min_y / TILE) * TILE - TILE`
   - `x1 = ceil((max_x + TILE) / TILE) * TILE + TILE` (exclusive)
   - `y1 = ceil((max_y + TILE) / TILE) * TILE + TILE` (exclusive)
   - view = `{origin_px: [x0, y0], width: x1 - x0, height: y1 - y0}`.
   Width and height are whole-TILE multiples; margin beyond the sprite
   bbox is >= 1 TILE on every side. The derived span and window dims are
   RECORDED in the artifact manifest. Zero post-hoc adjustments: if the
   derived window is somehow uncomposable, that is a STOP, never a tweak.
6. **Sub-track extraction.** The extracted track copies the subject's
   records, the per-tick masks, tick_ms, zone, and the subject's roster
   entry VERBATIM from the intaken track; constants = the subject's kit
   entry only; view = the derived window; class RUNTIME, schema v1;
   provenance carries the source `bundle_id` (so `require_runtime_admission`
   still binds it to the verified intake context), the source track
   sha256, and the extraction parameters. The sub-track feeds the
   EXISTING single-creature composition path (`recompose_track`) —
   extraction changes WHAT is composed, never HOW.

## Palette route (pre-registered; enumeration evidence inline)

**Enumeration ran FIRST (this session, before this commit):**

- No `releases/` directory exists; release manifests live at
  `exports/*/release.json`. None references `render-reference.json`.
- All four historical sha256s of `manifests/render-reference.json`
  (`3e5f676f…`, `7945e5b4…`, `b200caaf…` current, `d3a1a17c…`) grep clean
  across the tree (excluding `.git`): NO file pins its bytes.
- Name references are default CLI paths + docs only (tools/tests read the
  live file).
- Zone-key ITERATION census: `feedback_metrics.flash_metrics` iterates
  `sorted(zones.items())` — its banked output
  (`reviews/calibration-v2/feedback-metrics.json`) has NO
  regenerate-and-compare guard, and its tests assert a zone_1/zone_2
  SUBSET; `pin_drift.derive_constant_checks` derives from
  `primitive_body`/`telegraph`/`possession_ring`/`feedback_states`, never
  `zones`; every sheet builder indexes explicit zone keys.
- **The decisive pin site is a banked TEST, not a release:**
  `tests/test_track_v1.py::RecomposeTrackV1::test_unbanked_zone_refuses_typed`
  (v30, banked) sets `track["zone"] = "district"` and asserts
  `recompose_track(..., reference())` raises `unmapped-zone` against the
  PLAIN render reference. An additive `zones.district` entry in
  `render-reference.json` (the brief's Route A shape) would flip that
  banked test red — violating this sprint's own additive-only-test-diffs
  law (bar B2). Route A is therefore unlawful on the enumeration
  evidence.

**Chosen route: Route B's mechanism — a NEW additive manifest file,
merged OPT-IN at load.** `manifests/zone-palette-district.json` carries
the `district` entry plus its full anchoring block; a new loader
(`load_zone_palette(reference, path)`) returns a DEEP-COPIED reference
with the additive zones merged, refusing any collision with an existing
banked zone key. ONLY the RUNTIME artifact-generation path (and tests
that explicitly opt in) load it. Zero existing bytes of
`render-reference.json` move (diff proof at commit B: the file is
untouched). The plain reference keeps the banked-zones-only refusal law —
the banked v30 test stays green and the `unmapped-zone` refusal is NOT
weakened; the district palette is admitted only where explicitly loaded.

**Value anchoring (every value byte-anchored to the PINNED blobs; the pin
set guarantees blob identity at the re-pinned baseline `a2f66446`):**

| key | value | anchor |
|---|---|---|
| floor | [36, 30, 20] | `data/zones/district.json` `palette.floor` at the pin |
| grid | [46, 38, 26] | `data/zones/district.json` `palette.grid` at the pin |
| wall | [176, 140, 88] | `data/zones/district.json` `palette.wall` at the pin |
| motif | [62, 50, 30] | `data/zones/district.json` `palette.motif_rgb` at the pin (the zone_1/zone_2 convention maps `motif_rgb` → `motif`) |
| transition | [235, 190, 90] | `data/zones/district.json` `palette.transition` at the pin |

- The five-key entry SHAPE `{floor, grid, wall, motif, transition}` is the
  zone_1/zone_2 convention (NAMED as convention; `compose_cell` consumes
  floor + grid; the other three ride for shape parity and are equally
  anchored). Sheet gutter/background/label colors are presentation
  convention copied from the banked layout constants (`GUTTER`, `v10.BG`,
  `LABEL`) and NAMED as convention.
- Corroboration: the derived values are byte-equal to the banked
  `zones.zone_2` entry — zone_2 was itself captured from
  `data/zones/district.json` (its `display_name` is "ZONE 2";
  `captured_from.files` lists the file), so the derivation convention is
  the SAME one the banked entries used.
- `data/display.json` at the pin was examined; NO value in this sprint's
  artifact set derives from it (the sub-window is span-derived; view
  dims/tick source are the track's own). If any needed value had been
  derivable from neither pinned blob, that is a STOP owner ask — none is.
- The palette file's anchoring block records the derivation commit and
  the source blob's `sha256_lf`
  (`9774cdd04ebaf6e1a429a1aceb26ca8b7ddd13f97f3086ff862d22ee305cd5f4`, =
  the runtime-baseline pin for `data/zones/district.json`) — anchored to
  CONTENT, so identity-only re-pins never invalidate it and any upstream
  content change to district.json trips both the pin gate and the guard
  test.

## Artifact set (pre-registered; all under `reviews/runtime-recompose-v31/`)

1. `decisions-subject.json` — the subject decision capture (TEXT; full
   window 420..560).
2. `runtime-exp-attack-sheet.png` — native 1x per-tick contact sheet of
   the derived span, 10 cells per row (layout convention), frame labels,
   disclosure banner + footer IN PIXELS.
3. `runtime-exp-attack-native.apng` — exact 1/60 s per tick (banked
   encoder `apng_delays`), native 1x, disclosure header in pixels.
4. `runtime-exp-attack-zoom4.apng` — the SAME frames at ONE integer zoom,
   4x (the banked APNG_SCALE convention), exact 1/60 s.
5. `runtime-exp-manifest.json` — mapping id + repo commit + mapping-source
   module sha256s + source track sha256 + intake context (bundle id,
   verification verdict/runs) + subject (name, kit) + derived span +
   window (origin, dims, formula restated) + double-build determinism
   flags + every artifact sha256 + the disclosure verbatim.

**Disclosure (pre-registered verbatim).** Manifest + rationale prose:
"RUNTIME-EXP: captured state is real; frame selection is the proposal's
(declared-integration-mapping-v1); single-creature window, neighbors
omitted; not the live camera; answers ZERO register items."
Sheet banner (SEAM_FONT has no V or apostrophe; the version particle is
spelled as its digit, v13 precedent):
line 1 `RUNTIME EXP  CAPTURED STATE IS REAL  FRAME SELECTION IS THE PROPOSAL`,
line 2 `DECLARED INTEGRATION MAPPING 1  SINGLE CREATURE WINDOW  NEIGHBORS OMITTED  NOT THE LIVE CAMERA`,
footer `ANSWERS ZERO REGISTER ITEMS`. APNG header (both zooms):
line 1 `RUNTIME EXP  MAPPING 1`, line 2 `ANSWERS ZERO REGISTER ITEMS`.
Filenames carry `runtime-exp-`. Zero SYNTHETIC labels (these are
RUNTIME-EXP; the v13 demo's SYNTHETIC label law does not transfer
verbatim).

**Generation law.** `verify_runtime_intake` runs LIVE in the generation
path on the evidence track (refuse-not-guess on any failure); the
extracted sub-track re-passes validation + `require_runtime_admission`
against the SAME intake context; every composition builds TWICE
in-process and byte-compares before writing (double-build determinism);
a regeneration guard (SLOW tier, pre-bank-skip pattern) recomposes the
committed artifacts from the committed evidence and compares bytes, and
`--check` gains the same guard additively (skips while unbanked).

## Known mechanical consequence (pre-registered)

Editing `tools/track_recompose.py` moves its sha256, pinned by FOUR
banked manifests (recompose-v13, defect-audit-v14, remedy-v15,
adoption-v16). Resolution at commit B, per the banked class: regenerate
each with its OWN tool AFTER the final parser edit; per-manifest git diff
= exactly the consumer pin line + `repo_commit_at_generation`; every
banked artifact byte-identical. Fan-out beyond these four that is not the
same class = STOP. NEW consequence this sprint CREATES: the v31 artifact
manifest pins the mapping-source module hashes too, so future consumer
edits fan out to FIVE manifests — named for v32 in the verdict/receipt.

## Bars (all-must-pass; verdicts NULL here, judged at commit D)

| # | Bar | What passes it (measurable) | Verdict |
|---|---|---|---|
| B1 | Protocol fidelity | Artifacts match the pre-registered extraction + palette protocols EXACTLY: subject/span/window derived by the pinned rules from bytes (derivation recorded in the manifest and reproducible by the committed code); zero post-hoc span/window adjustments; the STOP branches taken if their conditions bind. | NULL |
| B2 | Regression | `track_recompose --check` exit 0 after EVERY edit; 672/672 + 340/340 equivalence green; draft-1 test file byte-identical; v1 test file additive-only diff (existing tests byte-identical); the four-manifest fan-out resolved pin-line-only with banked artifacts byte-identical; full discover green at recorded N (= 748 + exactly the new tests). | NULL |
| B3 | Palette anchoring | Every district palette value cited anchored-or-convention per the table above; `manifests/render-reference.json` byte-UNTOUCHED (git diff empty); the banked `unmapped-zone` refusal test green and the refusal class unweakened; the palette file's anchoring block records source blob sha256_lf equal to the runtime-baseline pin. | NULL |
| B4 | Determinism | Every composed artifact built twice in-process byte-identically at generation (flags in the manifest); committed sha256s in the manifest match the committed files; the SLOW regeneration guard recomposes the committed artifacts byte-identically from committed evidence; `--check` extension green. | NULL |
| B5 | EXP boundary | The RUNTIME-EXP disclosure appears in pixels (sheet banner+footer, APNG headers), in every artifact filename (`runtime-exp-`), and in the manifest verbatim; zero adjudication language in any artifact string or doc sentence (machine-scanned before council; council Q1 audits); zero SYNTHETIC labels on RUNTIME artifacts; zero register/status edits. | NULL |
| B6 | HFO gate (blocking) | Disclosure text, verdict.md, and the artifact manifest each critiqued with accuracy and presentation scored SEPARATELY (accuracy = every number/hash traceable to a computation this session or a named banked source; presentation = truncated pyramid, typed findings, no unlabeled precision, register technical-concise). | NULL |

## Finding classes (pre-registered routing)

- **protocol-stop** — a pre-registered STOP condition bound (kit not
  striker; possession handoff; no qualifying span; unanchorable value;
  fan-out beyond class; double-build nondeterminism) → bank the TEXT
  analysis + the stop, zero artifacts on the stopped lane, verdict lands.
- **emitter-shaped** — track content contradicting the s84 pin → MAILED
  finding (their intake law), never worked around.
- **noted** — observations with no action owed.

## Pre-registered non-claims

Zero adjudication of any lettered register item; the artifacts are
instruments, not verdicts — MEASURED-capable is not measured. No register
row moves; C1–C5 MET, C6 OPEN doubly gated, untouched;
`docs/integration-readiness.md` + `docs/selection-register.md` +
`docs/state-track-schema.md` + `docs/replay-capture-design.md` +
banked verdict trees byte-frozen. No schedule claims. No multi-creature
scene claims — neighbors omitted BY DECLARATION, and the artifacts say
so. The v31 verdict banks the SIX v30 cadence numbers verbatim from the
brief (their only carrier); v31's own reals ride the receipt and the v32
brief, each condition-labeled; the suite count moves past 748 (second
composition change since v21) and v31's push lands labeled "first point
at N tests", never pooled.
