# Recompose v13 — state-track recomposer + draft schema verdict

Reviewed artifacts (SHA-256 prefixes; full hashes in
`recompose-manifest.json` and the git objects):

- `tools/track_recompose.py` — the reference consumer: DRAFT-schema
  validation (typed refusals), the declared mapping
  (`declared-integration-mapping-v1`) composed of banked modules imported
  unmodified, recomposition/APNG via the banked encoders, `--check`
  self-verification.
- `docs/state-track-schema.md` (`ed1c096fefbb15f2…`) — DRAFT,
  proposal-input, game-seat-pinned-later; field table with engine file:line
  at the fresh pin; 16/16 sufficiency table.
- `reviews/recompose-v13/synthetic-demo-track.json`
  (`b76858075ad6e46a…`), `synthetic-demo-sheet.png`
  (`bc28ae90c595df3a…`), `synthetic-demo.apng` (`3cb8361a7bd4cddc…`),
  `recompose-manifest.json` (`a8661e68bb646024…`) — the one SYNTHETIC demo
  bundle: idle → step down → boundary turn at the arrival tick → step
  right → full attack cycle → idle, 48 ticks, all 11 banked pose classes,
  banked bytes only.
- Pre-registration: `reviews/recompose-v13/rationale.md`, committed with
  the toolchain **before any demo artifact existed** (in `fbe849b`; see
  the deviation note). No bar was added, removed, or reworded afterwards;
  the two bar-text touches before that commit were pin-reference updates
  (bars 2/9) recording the mid-sprint re-pins, made before any artifact
  existed.
- **No release, no new pixels, zero adjudication:** every artifact composes
  banked export bytes; the 26 banked export pins byte-verified; no new
  `exports/` directory (guard extended to `recompose-v13`);
  `tools/export_assets.py` / `make_release.py` untouched; no lettered
  register item is answered, previewed, or named by anything here.
- Baseline: THREE re-pins this sprint — `c5cc2d8` (step-0 identity,
  `5ce4414`→`746ee8b`, blobs identical), `5c61113` (content,
  `746ee8b`→`3fdfae9`: T3 wave, renderer.rb +13/−0 additive + nest.json
  two added keys), and the `c5c146d` re-pin inside `fbe849b` (T4 wave,
  renderer.rb +25/−3 — a semantic-preserving way-lock refactor plus
  additive drained-well state, **owner-approved live** under the extended
  approve-by-default class: semantic-preserving refactors + additions that
  move no `render-reference.json` constant self-approve with constants
  re-verified and a note). Every `render-reference.json` constant
  value-re-verified at each new renderer blob; `attack_timing` 5/4/8/13
  re-verified at every hop; consolidated protocol note sent to the dev
  seat (`from-game-two-assets-v13-repin-c5c146d.md`, md5
  `192b95aa47b510485282694c77ca2408`). Gate exit 0 after every re-pin and
  immediately before banking.
- Session model `us.anthropic.claude-fable-5` (verified from `PI_MODEL`,
  not self-report). Council seat cross-vendor (Kimi K2.5,
  `moonshotai.kimi-k2.5`), one consolidated adversarial call: 5,882 in /
  1,890 out = 7,772 of the 8k cap, `stop_reason=end_turn`, no truncation;
  response file-redirected and read as UTF-8.

Sprint question (rationale, fixed first): can this repo's toolchain consume
a per-tick state track and recompose banked frames under the declared
integration mapping — the section 6.1 duty of the banked design — proven
byte-for-byte against already-banked artifacts, without producing anything
that could be mistaken for runtime evidence?

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS | 529 tests OK at the pre-bundle hook run; the new module alone 33/33 (both refusal adoptions covered); demo guards live (0 skips) after banking |
| 2 | Both asset_gate runs exit 0 | PASS | step 0 exit 0 (`746ee8b`), exit 0 after each content re-pin, exit 0 immediately before banking (`c5c146d`) |
| 3 | **Byte equivalence: 672/672 covered cells** | PASS | tracks derived mechanically from the banked Model-A lane plans recompose byte-identically to the committed sheets: 420/420 v10 lane cells (EARLY/MID/LATE/CONTROL/DEGEN) + 252/252 v11 Model-A lane cells (CORNER/CONTROL/DEGEN), both pairs, both zones, all 21 sheet ticks, zero failures — compared against committed PNG bytes at the recorded cell rects. REM lanes excluded by construction (Model B, the EXP settle-hold variant, is precisely not the declared mapping) |
| 4 | **Plan equivalence: 340/340 attack records** | PASS | the mapping's (pose byte-class, facing, lunge scalar) stream equals the banked v9 `lane_tick` outputs for every tick of all ten walk+attack lanes; f3/idle compared at byte-class per the banked byte-copy law |
| 5 | Double-build determinism on every artifact | PASS | track/sheet/APNG double-built byte-identical in-process (`determinism.double_build_identical: true`); `--check` regenerates all three from the committed track and byte-compares against committed files — clean |
| 6 | Banked modules untouched | PASS | all nine mapping-source modules SHA-256-pinned in the manifest; `--check` and the test suite compare live files against the pins; exporter/registry untouched; 26/26 export pins byte-verified |
| 7 | Zero writes into `../game-two` | PASS | read-only `git -C ../game-two show/log/diff` from this repo's cwd throughout |
| 8 | Zero new exports/pixels/releases | PASS | export-pin checker + stale-dir guard (now including `recompose-v13`); demo composes banked export bytes only |
| 9 | Engine citations fresh | PASS | every schema-doc engine claim cites file:line at `c5c146d0954260743ba895295a85caec88751f13`, re-derived after each mid-sprint hop (renderer.rb and the unpinned world.rb were the only citation shifts) |
| 10 | SYNTHETIC labeling | PASS | filenames carry `synthetic-demo`; manifest and track carry `provenance.class = "SYNTHETIC"` (machine-asserted); the sheet carries the drawn banner `SYNTHETIC DEMO EXP CLASS DECLARED MODEL ZERO ADJUDICATION` and the APNG carries `SYNTHETIC DEMO EXP` per frame, in pixels |
| 11 | Zero lettered items adjudicated | PASS | **this is a bar, not a footnote: no artifact, filename, test name, or doc section answers, previews, or is named after any of (a)–(o)/x0.** The only claim produced is the machine-proved equivalence claim of bars 3–4 |

**Accuracy: 11/11 integrity bars.** The equivalence claim's scope, stated
precisely (council Q2/Q5 adoption): byte-equality over the covered window
plus the v9 decision-stream identity **pins the mapping against the banked
evidence base** — a future consumer edit that drifts any covered clause
breaks a machine bar. It does not and cannot validate the mapping against
a live sprite renderer, because none exists at the pin (design section 2.3
gap 2); the mapping is a **declared model**, disclosed in every artifact,
and correctness-vs-engine only becomes a category if a sprite integration
ships — a separate, unproposed owner decision.

## Schema-doc bars (blocking; judged on the final rendered doc)

| Bar | Verdict | Evidence |
|---|---|---|
| DRAFT framing, game seat pins + owns `schema_version` | PASS | first section states it twice; non-claims restate it; the consumer named the disposable half (council Q4 adoption) |
| Field table with engine file:line at the fresh pin | PASS | every row cites `c5c146d0` sources, read this session |
| Record shape + worked example | PASS | top-level + per-tick JSON with a mid-walk record |
| Bundle-member framing | PASS | identity fields live in the bundle manifest; "a track never self-certifies" |
| Sufficiency table 16/16 | PASS | every `capture_requirements` entry maps to fields; three non-track artifacts named rather than papered over: (h) display-chain smear capture, (n) adjudication display standard, (f) flicker-treatment consumer extension (both candidate cadence counters already ride the track; the anchor rule is pinned with the extension — council Q1 adoption) |
| Explicit non-claims | PASS | draft; emitter game-side conditional; zero adjudication; declared-model disclosure |

The one field this consumer adds to the design's Mode T list —
`state_frames`, the attack-phase index (creature.rb:480, digest-visible at
:100) — is flagged as a finding for the game seat, with the windowed-track
argument for why the emitter should carry it.

## Demo bars

One SYNTHETIC bundle, novel arrangement (no banked lane ever chained
walk → boundary-turn → walk → attack in one sequence), all 11 banked pose
classes exercised, 48 ticks, exact 1/60 s APNG delays via the banked
encoder, native-scale sheet over both zone palettes. Manifest records
mapping id, repo commit at generation, all nine module hashes, track
SHA-256, schema version, SYNTHETIC provenance, and double-build evidence.
Visual read (session model, on the committed sheet + 3x/2x crops of the
same bytes): the boundary turn reads at T15 exactly as the CORNER class
banked it (profile appears on the arrival tick, step-off follows), the
windup coil and +6 active lunge read at T29–T35, and the banner/disclaimer
rows are legible at 1x.

## Presentation scores (accuracy scored separately above)

- **Schema doc: 9/10.** The field table's consumed-by column does the
  argumentative work (sufficiency criterion → fields, row by row); the
  16/16 table turns coverage into an audit rather than a claim. Cost: the
  table density asks a full-width read.
- **Demo sheet: 8/10.** One glance carries the whole sequence; the drawn
  SYNTHETIC banner + closing disclaimer make the class unmistakable at
  pixel level. Cost: 48 columns need horizontal scrolling at native scale.
- **Verdict + manifest surfaces: 8.5/10.** Bar-by-bar evidence with exact
  counts; the manifest is self-contained provenance.

HFO pass (hub-dev/owner register): truncated pyramid (status → shape →
proof), typed uncertainty (draft/pinned-later, named carve-outs), no
promises, no filler, generic mechanical IDs throughout; accuracy and
presentation scored on separate axes here per the standing gate.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call attacking five numbered claims; every REFUTED
re-verified against primary bytes before adoption (v12 precedent upheld —
two of five verdicts dissolved on the primary). Reconciliation:

1. **Q1 (schema sufficiency) — REFUTED by the council on (f); kernel
   ADOPTED as wording, the absolute REFUTED on re-verification.** The
   charge: no field carries the 3-on/3-off cadence phase, so a windowed
   track cannot anchor the flicker. Re-verified: both candidate cadence
   counters (`frame` for a world-anchored rule; `iframes` against the
   kit's pinned maximum for a hit-anchored rule) already ride the track —
   what is genuinely deferred is the anchor RULE, a mapping clause of the
   (f) consumer extension, not a field. The (f) row now says exactly that.
   The council's x0-position UNCERTAIN dissolved on the primary the brief
   could not carry: `RISE_INBETWEEN = "x0"` (make_seam_timeline:87, banked
   v7, recovery tick 8 = `state_frames` 1), and bar 4 machine-proves the
   mapping hits it on all ten lanes.
2. **Q2 (unpinned engine states) — CONFIRMED on one of five sub-claims;
   that one ADOPTED as a tool refusal; three REFUTED with primary
   evidence; the fifth reframed as the scope statement above.**
   ADOPTED: `current_action == "special"` with a non-idle `attack_state`
   was silently mapped with the basic-attack timeline AND a lunge the
   engine suppresses for specials (renderer.rb:633 at the pin) — the
   mapping now refuses with `unmapped-action-class` (specials have no
   banked timeline; guessing twice is exactly the risk-2 drift class),
   test-covered in both directions. REFUTED: hitstop — the mapping is
   per-tick pure, so frozen state recomposes as repeated frames, which IS
   the hitstop rendering (now a documented property); mid-tween facing
   swaps — the v10/v11 turn lanes are precisely that class and sit inside
   the 672-cell byte bar; walk+attack "dropped walk component" — attack
   pose priority is the banked moving-recovery law and the walk component
   rides the position, machine-proved by bar 4 over the v9 compound lanes.
   The "validator accepts lying tracks" charge is by-design and already
   documented: single-record semantic coherence beyond the range/state
   checks is the bundle intake gate's job (design section 5); a track
   never self-certifies.
3. **Q3 (contamination) — CONFIRMED; adopted in modified form.** The
   council proposed deleting `RUNTIME` from the enum. Deleting it would
   gut the document's purpose (it is the proposal for the runtime
   contract), so the adopted form is stronger where it matters: the
   schema keeps `RUNTIME` as proposal vocabulary, and the **reference
   consumer refuses to recompose any RUNTIME-class track**
   (`runtime-intake-not-established`, typed, test-covered) until the
   design-section-5 intake gate is banked. No synthetic artifact can be
   processed as runtime evidence by this repo's own tooling, structurally.
4. **Q4 (sovereignty) — one kernel ADOPTED, two charges REFUTED.**
   ADOPTED: the working parser could read as adopt-or-break pressure —
   the doc now names the parser the disposable half (if the pinned schema
   differs, this repo adapts the consumer, never the reverse). REFUTED:
   citing the banked design is required grounding, not pre-answering (the
   design is the council-reconciled joint artifact whose open question 1
   this doc feeds, and the receipt queued exactly this input class for
   v19 intake); explicit non-claims are the banked house style (v4–v12),
   not self-negation.
5. **Q5 (unthought risk: "validating a model against itself") — the
   kernel ADOPTED as the scope statement under the accuracy table.** The
   charge that the proof is circular mistakes its target: the bar exists
   to pin the mapping against the banked evidence base (the risk-2
   anti-drift law), and a ground-truth sprite renderer does not exist to
   validate against — by construction, disclosed since v12. What the
   council read as a hole is the sprint's declared epistemic boundary;
   the verdict now states it in one paragraph rather than leaving it
   distributed.

Net: two tool refusals added (specials; RUNTIME-until-intake), two doc
precisions (the (f) anchor rule; consumer disposability), one documented
property (per-tick purity ⇒ hitstop correctness), one scope statement.
Every adoption folded before the bundle commit; no bar moved; no banked
verdict touched.

## Mail-in status (step 0, recorded)

One receipt (`from-game-two-v12-design-receipt.md`, hub dev seat,
2026-08-20): v12 design + register md5s re-verified clean at `4c3bc35`;
**gating-decision = DEFERRED** to the v19 owners' brainstorm (sim-feel
class, decided against post-aim feel; recorded as a v19 docket row
game-side) — per design Q6 the **settle-bob condition stays pending**, and
the deferral is recorded in design section 8; **capture-contract =
queued-for-v19-intake** — the schema draft therefore stays DRAFT framing,
and it now rides that same intake row as proposal input (design section 4
pointer). No reply owed ("no further mail unless the gating class gets
decided"); none sent on that thread. The only outbound mail this sprint is
the protocol-mandated re-pin note (a different, standing thread; carries
no ask and requests no receipt).

## Deviations (recorded, not repeated)

- The `c5c146d` re-pin and the pre-registration bundle landed in ONE
  commit (`fbe849b`): the toolchain files were still staged from a
  hook-blocked attempt when the re-pin was committed. Content-wise both
  halves are exactly what their messages describe and the hook ran green
  on the union; the re-pin-rides-alone discipline was violated by staging
  error and is called out here rather than history-rewritten.
- Two hook runs (~45 min each) were consumed by live game-two drift
  landing mid-run — the cadence note is banked in project memory with the
  owner's protocol extension.

## Non-claims

Zero lettered items adjudicated — synthetic throughout; no runtime
evidence exists or is claimed; the mapping is a declared model of an
unproposed integration; the schema is a draft the game seat may replace
wholesale; no capture execution, no game-side code, no scheduling, no new
asset lanes, no release.

## Stop

Sprint 13 stops here: one reference consumer, one DRAFT schema, 33 tests,
one SYNTHETIC demo bundle, three baseline re-pins (one owner-approved
class extension recorded), two design-doc lines inside the standing
allowance, one banked verdict. The settle-bob calibration stays
closed-by-condition (deferred upstream); capture execution stays
owner-sequenced; the audio thread and tile era stay parked. Next evidence
that can move the register is a verified RUNTIME bundle — nothing in this
repo manufactures one.
