# Recompose v13 — state-track recomposer + draft schema (pre-registration)

Sprint question: can this repo's toolchain consume a per-tick state track and
recompose banked frames under the **declared integration mapping** exactly as
the banked design assigns it (`docs/replay-capture-design.md` section 6.1),
proven byte-for-byte against the already-banked lane artifacts? Deliverables:
one DRAFT schema document (`docs/state-track-schema.md` — proposal input; the
game seat pins the schema at tool-spec time, design open question 1), one
reference consumer (`tools/track_recompose.py`), its tests, and one SYNTHETIC
demo bundle in this directory.

**This is a toolchain sprint: ZERO new frames, zero exports, zero releases,
zero adjudication.** No artifact in this sprint answers, previews, or is
named after any lettered register item (a)–(o) or x0. The only claim this
sprint may produce is the machine-proved equivalence claim defined below.
Every demo artifact is SYNTHETIC-class: a synthetic track is a declared-model
state stream, not runtime evidence, and each one carries the label in its
filename, its manifest, and (for images) drawn into its pixels.

These bars are fixed BEFORE the tool, the tests, the schema doc, or any
artifact exists (v12 validator-first precedent; v9–v11 rationale law). No bar
may be added, removed, reworded, or reinterpreted after artifacts exist.

## The declared mapping under test (fixed here)

`mapping_id = "declared-integration-mapping-v1"`, composed of banked pieces
only, imported unmodified:

- **Walk:** the banked v1 walk mapping — `f0x4/f1x3/f2x3/f3x3` across the
  13-advance step via `walk_frame_index` (`tools/make_grammar_timeline.py`),
  positions via `tween_position` (`tools/make_seam_timeline.py`); the step's
  commit tick (state `tween_left == tween_total`, no advance yet) draws the
  standing pose; `tween_left == 0` draws the standing pose; f3 is the idle
  byte-copy (banked law), so arrival/settle labels agree byte-for-byte.
- **Attack:** the banked lane-B timeline (v7 winner, carried v9) —
  `w0 | a0x4 | k0x4 | s0 | r0x6 | x0` over windup 5 / active 4 / recovery 8,
  with the phase index derived from engine state as
  `into_phase = pinned_phase_frames - state_frames`; lunge offsets
  windup −3 / active +6 along facing (`manifests/render-reference.json`,
  value-anchored to `renderer.rb` `lunge_offset` at the pin). Attack pose
  priority over walk frames (the banked moving-recovery pose-priority
  finding, carried v5–v11).
- **Facing:** `[0,1]`→down, `[1,0]`→right; anything else is a typed refusal
  (no mirrored or diagonal row exists in the banked set — banked findings,
  carried).
- **Position:** draw vector = `round_half_up(px/py)` (banked function) minus
  the declared view origin, plus the state-derived lunge.
- **Composition/encoding:** `compose_cell` (banked v9 compositor),
  `Rgba8Canvas` (banked writer), `encode_apng` + `apng_delays` (banked
  encoder, exact 1/60 s per-tick delays).

Out of mapping-v1 scope, declared (not silently absent): the (f)-class
accent-flicker treatment (the schema carries its fields; the consumer
extension lands only when the hub queues that item); tween classes with
`tween_total != step_frames` while moving (dash/knockback — typed refusal,
no banked evidence base); facings other than down/right (typed refusal).

## INTEGRITY bars (any red stops the sprint; all-must-pass)

1. **Full suite green** including the new tests
   (`.venv/Scripts/python.exe -m unittest discover -s tests`).
2. **Both asset_gate runs exit 0** — step 0 (gate exit 0 at game-two HEAD
   `746ee8b6`, mechanical identity re-pin `c5cc2d8`, `attack_timing`
   re-verified 5/4/8/13), the mid-sprint content re-pins (the T3
   tile-materials wave `746ee8b6`→`3fdfae93`: `renderer.rb` +13/−0
   additive, `nest.json` two added keys; then the T4 wave
   `3fdfae93`→`c5c146d0`: `renderer.rb` +25/−3 — a semantic-preserving
   way-lock refactor plus additive drained-well state, no draw-path
   constant moved, **owner-approved live** under the extended
   approve-by-default class — dev-seat standing protocol executed both
   times: every `render-reference.json` constant value-re-verified at the
   new blobs, sha256_lf recomputed, other pins blob-identical, note sent
   to the dev seat), and again immediately before banking.
3. **THE EQUIVALENCE BAR (byte half).** For state tracks derived
   mechanically from the banked Model-A lane plans, track-driven
   recomposition reproduces the committed lane-row cells BYTE-FOR-BYTE:
   every `section == "lane"` cell of `reviews/calibration-v10/turn-sheet.png`
   (lanes EARLY, MID, LATE, CONTROL, DEGEN) and of
   `reviews/calibration-v11/corner-sheet.png` (lanes CORNER, CONTROL, DEGEN),
   both pairs, both zones, all 21 sheet ticks — expected cell count exactly
   420 (v10) + 252 (v11) = **672 cells, zero tolerance, zero failures**,
   compared against the committed PNG bytes at the recorded cell rects.
   The v11 REM_EARLY/REM_MID lanes are EXCLUDED by construction: they render
   Model B, the EXP-class settle-hold variant — a declared-model preview
   that is precisely NOT the declared integration mapping (their geometry is
   still covered via the v10 EARLY/MID lanes). If byte-equality is
   unreachable for a principled reason, the sprint STOPS and re-asks; the
   bar is never softened to approximate equality.
4. **THE EQUIVALENCE BAR (attack half, plan-level).** For state tracks
   derived mechanically from the banked v9 cross-seam lane plans, the
   mapping's per-tick output equals the banked v9 `lane_tick` output on
   (pose byte-class, pose_facing, lunge-offset scalar) for every tick of
   every lane — 10 lanes × 34 ticks = **340 records, zero failures**. Pose
   comparison is at byte-class level: `f3` ≡ `idle` by the banked byte-copy
   law (the mapping labels a completed step's standing tick `idle` where the
   banked plan labels it `f3`; the drawn bytes are identical and the byte
   half of the bar proves it). The v9 sheet's cell layout is not
   re-rendered; the pose/offset decision stream is the subject.
5. **Double-build determinism on every artifact** — track JSON, sheet PNG,
   APNG, manifest-recorded hashes: two independent in-process builds
   byte-identical, and `--check` re-verifies committed demo bytes against a
   fresh build (the banked in-process + CLI discipline).
6. **Banked modules untouched.** `tools/track_recompose.py` imports the
   banked modules unmodified; every mapping-source module's SHA-256 is
   recorded in the demo manifest and the tests assert the live files match
   the committed manifest pins; `tools/export_assets.py` and
   `tools/make_release.py` untouched; the 26 banked export pins byte-verified
   via the standing `check_export_pins`; no `exports/` additions of any kind.
7. **Zero writes into `../game-two`** (read-only `git -C ../game-two show`
   from this repo's own cwd only).
8. **Zero new exports, pixels, or releases** — the demo composes banked
   export bytes only; no release manifest; no new export directories
   (stale-dir guard extended to this sprint's names).
9. **Engine citations fresh.** Every engine claim in the schema doc cites
   file:line at game-two `c5c146d0954260743ba895295a85caec88751f13` (the
   mid-sprint content re-pin; only `renderer.rb` and the unpinned
   `world.rb` line numbers shifted from the step-0 pin), read this
   session.
10. **SYNTHETIC labeling.** Every demo artifact filename carries
    `synthetic-demo` (the sidecar manifest, named `recompose-manifest.json`
    per the sprint brief, carries `provenance.class = "SYNTHETIC"` instead);
    the demo sheet and APNG carry a drawn SYNTHETIC/EXP-class label in their
    pixels; the track JSON carries a SYNTHETIC provenance block.
11. **Zero lettered items adjudicated.** No artifact, filename, test name,
    or doc section in this sprint claims, previews, or is named after a
    register item; the verdict states "zero lettered items adjudicated" as a
    bar, not a footnote.

## Schema-doc bars (blocking, judged at review)

- Titled DRAFT / proposal-input; states in its first section that the game
  seat pins the schema (and owns `schema_version`) at tool-spec time.
- Field table: name, type, source attr with engine file:line at `746ee8b6`,
  consumed-by (renderer-draw / mapping-index / both / adjudication-context).
- Per-tick record shape plus one worked example (one creature, three ticks).
- Bundle-member framing consistent with design section 4 (the track is a
  capture-bundle member, never a standalone evidence class).
- **The sufficiency table (coverage proof):** every field maps to design
  section 4's sufficiency criterion (every renderer creature-draw input +
  every index the declared mapping needs), AND all 16 register items'
  `capture_requirements` map to the fields that satisfy them — coverage
  demonstrated item by item, not asserted. The (h) smear half and the (f)
  consumer extension are named explicitly rather than papered over.
- Explicit non-claims: draft status; emitter is game-side conditional
  tooling (design section 2.3 gap 3); nothing here schedules, requests, or
  implements anything game-side.

## Demo bars (the one synthetic bundle this sprint banks)

- One synthetic track exercising idle → walk (one full step) → boundary
  turn (commit-at-arrival class) → walk (one full step) → full attack cycle
  → idle, in one continuous sequence — a NOVEL arrangement composed of
  banked bytes only, chosen because no banked lane ever chained these
  classes in one lane (novelty of arrangement, not of evidence class).
- Its recomposed sheet (native scale, both zones), one APNG (banked encoder,
  exact 1/60 s delays), the track JSON, and the manifest — all deterministic
  per bar 5, all labeled per bar 10.
- The manifest records: `mapping_id`, this repo's commit at generation, the
  consumer's own SHA-256, every mapping-source module SHA-256, the track
  SHA-256, `schema_version`, `provenance.class = "SYNTHETIC"`, determinism
  evidence (double-build hashes), and the artifact hashes.

## QUALITY bars (blocking)

- **HFO pass** on the schema doc and the verdict (hub-dev/owner register;
  accuracy and presentation scored separately; no promises; explicit
  non-goals).
- **One consolidated cross-vendor council call** (Kimi K2.5 default,
  ≤ 8k tokens total, response redirected to a file and read as UTF-8)
  attacking: (1) schema sufficiency vs all 16 `capture_requirements`;
  (2) equivalence-proof soundness — does byte-equality over the covered
  window plus the v9 plan-identity actually pin the mapping; (3)
  contamination — could any artifact be mistaken for runtime evidence; (4)
  sovereignty — does anything read as pinned law; (5) the biggest unthought
  risk. Every REFUTED re-verified against primary bytes before adoption
  (v12 precedent); the reconciliation banked in the verdict appendix;
  adoptions folded before the bundle commit.

## Mail-in status (step 0, recorded here for the verdict)

One receipt arrived (`from-game-two-v12-design-receipt.md`, hub dev seat,
2026-08-20): design + register md5s re-verified clean at `4c3bc35`;
**gating-decision = DEFERRED** (turn-handling is a v19-class sim-feel change,
decided at the owners' brainstorm against post-aim feel; recorded as a v19
docket row game-side) — per the design's own Q6 consequence the settle-bob
condition **stays pending** and nothing else moves; **capture-contract =
queued-for-v19-intake** (docs-only input; emitters remain game-side
conditional additions). Consequence for this sprint: the schema doc stays
DRAFT/proposal-input framing, and NO reply mail is owed (their mirror line:
"no further mail unless the gating class gets decided"). No settle-bob work
of any kind is opened by this sprint regardless.

## Stop conditions

The sprint stops after: rationale + toolchain + tests + schema doc banked
before any demo artifact exists (the v11 `1ec6632` pattern) → demo artifacts
generated and self-checked → full suite + pre-banking gate green → council +
HFO folded → one bundle commit → push. Any INTEGRITY red stops the sprint at
the red. No second design document, no new asset lanes, no capture
execution, no game-side code, no outbound mail.
