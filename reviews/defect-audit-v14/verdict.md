# Defect audit v14 — attack-read integrity verdict (the classified register)

**Answer first:** the owner's sighting is real, in the banked bytes, and
fully characterized. The strike key (k0) paints its jaw-gape marker in the
frozen ramp accent `#140e0c` — a color measured at **1.09:1 WCAG contrast
against the zone_1 floor** (1.16:1 zone_2): optically the floor color. On
the down facing the gape band **absorbs both eye clusters into one 24px
interior mass**; on the right facing (the one the owner watched — the demo
attack runs facing `[1,0]`, track ticks 29–45) it separates the snout tip
from the head with a floor-colored void. For the pinned 4 active ticks
(66.7 ms) per attack, the head interior reads as an aperture, then the eyes
return. **Zero interior transparency holes exist anywhere** (22/22 sprites)
— the "piece missing" is opaque paint that matches the background, not
alpha. One bytes-domain finding (DEF-1), one temporal (DEF-2), one viewer
(DEF-3); nothing is fixed, authored, or re-opened here; routing proposals
go to the owner.

Reviewed artifacts (SHA-256 prefixes; full hashes in `defect-manifest.json`):

- `pose-integrity-report.json` (`3489686149dc8b11…`) — the machine facts:
  22/22 sprites (hole inventory, accent-cluster table, color histograms),
  7 cuts per facing (silhouette + recolor clusters, hole deltas, accent
  deltas), context contrast table.
- Per-tick 8x NN strips, both facings x both zones
  (`synthetic-audit-strip-{down,right}-{z1,z2}-8x.png`, `27d52c64…`,
  `213c47d2…`, `bb90fe13…`, `0e7fba7a…`) — the stills-domain evidence.
- APNGs at exact 1/60 s and slowed 6/60 s, 4x and 8x pre-scaled integer NN
  (`synthetic-audit-attack[-slow6]-{down,right}-{4,8}x.apng`, eight files,
  hashes in the manifest) — the at-speed evidence, banked encoder, delay
  lists declared.
- `defect-manifest.json` (`ac0610cc524ef576…`) — provenance (SYNTHETIC), 18 module
  hash pins, artifact hashes, double-build evidence
  (`double_build_identical: true`), the pinned viewing protocol.
- Pre-registration: `reviews/defect-audit-v14/rationale.md`, committed with
  the toolchain (`6548590`) **before any artifact existed**. No bar was
  added, removed, or reworded afterwards.
- Generator: `tools/pose_integrity_metrics.py` — audit stream derived via
  the banked v13 `select_pose` (imported unmodified), composition via the
  banked `compose_cell`/`Rgba8Canvas`/`encode_apng`.
- Session model `us.anthropic.claude-fable-5` (verified from `PI_MODEL`).
  Council seat cross-vendor (Kimi K2.5, `moonshotai.kimi-k2.5`), one
  consolidated adversarial call: 2,113 in / 2,600 out = 4,713 of the 8k
  cap (`stop_reason=max_tokens` inside its closing summary table; all five
  question verdicts complete — the v3 precedent); response file-redirected
  and read as UTF-8.

Sprint question (rationale, fixed first): characterize the owner-observed
attack-read defect class over banked bytes only — what exists in the bytes,
what emerges only across cuts at speed, what the viewing chain manufactures
— fixing nothing.

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS | commit-1 pre-commit hook green (changed-scope gauntlet over the bundle; exit 0 = the commit landed); the module standalone: 30 tests, 5 pre-bank skips before artifacts, **30/30 with 0 skips after**; the commit-2 hook is the final gate (exit code governs banking) |
| 2 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 at `1b0d3dd` after the content re-pin `3841ded` (J1 renderer.rb perf refactor, approve-by-default class, all render-reference constants value-re-verified, note sent); pre-banking: exit 0 at `3c0ff6c` after the mechanical identity re-pin `33238f9` (test-only hops, blobs identical, attack_timing 5/4/8/13 re-verified) |
| 3 | Hole detector proven in BOTH directions | PASS | planted-fixture tests: ring hole found (exact area 8, bbox, band), two/three holes counted separately, diagonal-sealed ring encloses (4-connectivity convention asserted); silent on solid, concave-open, channel-to-edge, edge-touching fixtures |
| 4 | All 22 banked sprites analyzed, zero skipped | PASS | report `coverage.sprites_analyzed = 22`, machine-checked by `--check` and tests |
| 5 | Playback artifacts deterministic + `--check`-regenerated | PASS | manifest `double_build_identical: true` over all 13 artifacts; `--check` exit 0: "committed report + strips + APNGs regenerate byte-identically" |
| 6 | Banked tool files untouched | PASS | 18 module hash pins in the manifest re-verified by `--check` and tests; `tools/export_assets.py`/`make_release.py` untouched; git status clean of banked-file modifications |
| 7 | 26 banked export pins byte-verified | PASS | `check_export_pins`: 26 verified, zero failures (in `--check` and the test suite) |
| 8 | Zero writes into `../game-two` | PASS | read-only `git -C ../game-two show/log/diff` from this repo's cwd throughout |
| 9 | Zero new exports/pixels/releases | PASS | no `exports/` additions (guard extended to `defect-audit-v14`); zero pixel edits; no release manifests |
| 10 | SYNTHETIC/EXP labels everywhere | PASS | filenames carry `synthetic-audit`; manifest + report carry `provenance.class = "SYNTHETIC"`; strips carry the drawn banner `SYNTHETIC AUDIT EXP BANKED BYTES ZERO ADJUDICATION` + protocol line; every APNG frame carries `SYNTHETIC AUDIT EXP` in pixels |
| 11 | Citations at the fresh pin | PASS | lunge −3/+6 at renderer.rb L699-708, ring/dim/telegraph/hurt constants L15-28/L622/L645-651/L670-675, all value-re-verified at `1b0d3dd` step 0 (blobs identical through `3c0ff6c`); banked-verdict quotes read from the committed v2/v3/v5/v6/v7 texts this session |
| 12 | Owner-redirect note mechanical-register-only | PASS | `docs/owner-redirects.md`: two dated one-liners naming carrier and consequence; no lore, no narrative |

**Accuracy: 12/12 integrity bars.** Measurement-bar compliance: hole
inventory/deltas, cluster localization, accent table, contrast table, and
stream consistency all machine-generated per the fixed definitions; the
stream's ordered classes equal the pre-registered
`idle → w0 → a0 → k0 → s0 → r0 → x0 → idle` (machine-checked, both
facings), and every per-tick (pose, offset) record comes from the banked
`select_pose` unmodified (test-enforced).

## The machine findings (report highlights; exact numbers in the JSON)

- **Interior transparency: zero holes in all 22 sprites.** The flood-fill
  detector (both-directions-proven) finds no unreachable transparent
  region anywhere. The contract's `[2,2,29,29]` bounds law additionally
  guarantees no banked sprite touches the canvas edge, so the
  edge-cropped-negative-space blind spot the council named (Q1) cannot
  occur in banked inputs — the detector's "geometric enclosure, not
  artistic negative space" scope is sufficient here by construction.
- **The accent color is triple-booked.** `#140e0c` draws the eyes, the
  feet caps, AND the k0 jaw-gape marker. Accent px per pose: down = 14 in
  every pose except k0 = 30; right = 10 everywhere except k0 = 18. The
  +16/−16 (down) and +8/−8 (right) land exactly at the a0→k0 and k0→s0
  cuts — the pinned 4-tick active window.
- **Cluster geometry, the decisive fact:** down idle carries two separate
  2x2 eye clusters (`[12,9,13,10]`, `[18,9,19,10]`); down k0 carries **no
  separate eye clusters** — one merged 24px mass `[12,11,19,14]` spanning
  the face. Right k0 keeps its eye (`[22,11,23,12]`) with an 8px gape band
  `[24,13,27,14]` at the snout.
- **Context contrast (WCAG sRGB relative-luminance ratio / RGB distance):**
  accent vs zone_1 floor **1.09 / 16.2**, vs zone_2 floor 1.16 / 24.0, vs
  grids 1.19–1.28; accent vs body **6.6 / 241.3**. The full-ramp table:
  body 6.08/5.7, highlight 8.72/8.18, shade 2.26/2.12, outline 1.17/1.10
  against the two floors — measured context, not a bar.
- **Cut structure:** a0→k0 simultaneously carries the sequence's largest
  silhouette change (right 102px, down 78px), the +9px lunge displacement
  (offset −3 → +6), and the accent-band appearance. Every cut's recolor
  clusters (the class all banked cut metrics are alpha-blind to) are
  localized with bboxes in the report; the recurring large recolor
  clusters are the rigid head translations (banked art).

## The defect register

### DEF-1 — `bytes` — k0 strike key, both facings: the gape marker is optically background-equivalent

- **Machine evidence (viewer-independent relationship between pinned
  values):** the k0 interior gape region is painted `#140e0c`; the pinned
  zone floors are `(28,24,22)` / `(36,30,20)`; measured 1.09:1 / 1.16:1 —
  both sides of the comparison are banked constants (sprite bytes;
  render-reference palettes), which is what makes this bytes-domain under
  the pre-registered taxonomy. Down: the band absorbs the eyes (cluster
  merge above) — the face carries no eye structure for the active window.
  Right: the band severs the snout tip from the head mass.
- **Perceptual read (pinned protocol, committed stills, session vision
  model):** down T07–T10 reads as a single dark aperture where the face
  was — over both zone floors the region is indistinguishable from the
  background, so the head reads as hollowed; right T07–T10 reads as the
  snout tip floating ahead of a void — a piece visually detached from the
  head. This is the stills-domain half only; the at-speed half is DEF-2.
- **Owner-sighting resolution:** the demo attack the owner watched is the
  right-facing instance (track bytes). "The head losing a piece inside it
  when it does the attack movement" maps to this condition: an interior
  region that reads as background appears inside the head exactly during
  the attack's active ticks. Down-k0 carries the same condition in
  stronger form (full eye absorption).
- **Banked-scope cross-reference (nothing re-opened):** v2 banked the gape
  + brace as the readable strike tell at 1x — that PASS stands; the gape
  IS readable as a state marker against the body (6.6:1). v3 banked the
  gape as "an additional color cue on top of a passing silhouette bar" —
  also stands. The council charged these framings as incompatible with
  DEF-1 (Q3); the numbers refute the incompatibility: **6.6:1 against the
  body is the cue; 1.09:1 against the floor is the collision** — the same
  pixels do both, against different grounds. What no banked line ever
  measured is the second number's axis (the scope check quotes the v2/v3
  texts; v2 measured flash-vs-floor, v3 accent-vs-crimson, all cut metrics
  alpha-XOR). Per the sprint brief's own scope law, a confirmed finding on
  a never-adjudicated axis is a NEW finding — not a softening of any
  banked PASS.
- **Severity: high — on empirical grounds, not a new normative bar:** the
  owner flagged it live and unprompted (the first owner-observed candidate
  defect in the banked set); the condition sits on the strike key, drawn 4
  ticks in every attack, in both facings, over both pinned zone palettes.
  This verdict deliberately registers no threshold that the banked set
  "should" have met (council Q3 kernel adopted).
- **Proposed routing, ranked by THIS repo's cost (the ranking criterion,
  stated; the decision is the owner's — council Q4 adopted):**
  0. **Accept-as-art** (zero cost): the owner may rule the aperture read
     acceptable or desirable at production scale. Fully available; the
     v2 tell-readability PASS is untouched either way.
  1. **Defer until the redirected frame pins its zones** (zero cost now):
     the owner redirect (docs/owner-redirects.md) un-pins the creature
     set's integration role; if the eventual frame runs lighter floors,
     the collision weakens or vanishes. Cost of deferral: the condition
     ships in any interim use over dark palettes.
  2. **Propose a bounded authoring-exploration sprint (v15+ candidate,
     owner-approved authoring decision):** the option CLASS is an in-ramp
     gape treatment (recolor to a ramp color with measured floor
     separation, or a jaw redesign that keeps a lighter interior) — this
     verdict deliberately binds no specific shade (council Q4 adopted);
     the measured full-ramp table above is the owner's decision context.
     A recolor-only change cannot move any banked silhouette bar by
     construction (v3: the gape contributes zero to XOR), so the
     re-verification cascade is bounded: new k0 release + v2 metrics
     re-run + this audit's re-run. Costs: 2 poses re-authored, one
     release, one review sprint.
  3. **Runtime zone repalette:** recorded as an option that exists, NOT
     ranked and NOT proposed — zone palettes are runtime-owned pinned
     constants; proposing them crosses the one-way boundary. Feasibility
     unassessable from this repo (council Q4 kernel: stated plainly
     rather than silently omitted).

### DEF-2 — `temporal` — the 4-tick exposure of DEF-1 at the strike cuts

- **Machine evidence:** appear-hold(4)-disappear structure: accent +16px
  at a0→k0, −16px at k0→s0 (down; +8/−8 right), exactly the pinned active
  window (66.7 ms at 60 tps); the appearance cut coincides with the +9px
  displacement and the sequence's largest silhouette change (right 102px,
  down 78px) — three simultaneous discontinuities at one boundary.
- **Perceptual scope, stated honestly:** whether the 66.7 ms aperture
  fuses into "mouth opens" or reads as "head glitches/loses a piece" at
  speed is a fusion question — unprovable on stills (the banked v4–v7
  correction class). The slowed 6/60 APNGs let a human step the boundary;
  they do not decide 60 tps behavior. **The falsification instrument
  exists and is named** (council Q2 kernel adopted): a runtime replay
  capture per the banked capture design (P1 scripted bundle) measures the
  at-speed read; the temporal class is falsifiable by that instrument,
  not by this sprint.
- **Cross-reference:** no lettered register item covers the k0-hold
  interior read ((d) is the w0/s0 one-tick bridge strobe — different
  subject). No lettered item is adjudicated, previewed, or answered here.
- **Routing:** propose the at-speed half as a NEW candidate item for the
  temporal-question register at its next revision (a register-track
  action, not taken here), P1-bundle answerable. **Contingency and its
  cost, acknowledged** (council Q4 kernel): if DEF-1 is authored away, the
  temporal half likely dissolves — sequencing an authoring decision first
  avoids paying the register-revision + capture-adjudication cost twice.
- **Severity: contingent on DEF-1's disposition.**

### DEF-3 — `viewer` — the sighting context's resampling contributor

- **Mechanism (analysis, not measurement — no capture execution this
  sprint):** the v13 demo APNG is 4x-prescaled; Edge maximized applies
  auto-fit non-integer resampling, which smooths the 1px grid lines and
  bleeds the gape band's edges — softening and enlarging the DEF-1
  aperture percept. The pinned protocol (pre-scaled 4x AND 8x integer NN,
  100% zoom, fit-to-window off, declared delay lists) removes this
  confound from all v14 artifacts.
- **Explicitly not an explanation-away:** DEF-1 is in the bytes; the
  resampling contributor amplifies an existing condition. Classified
  `viewer` because the *contribution* exists only under resampled viewing
  (taxonomy assignment rule, third branch).
- **Scope statement (council Q5 kernel adopted):** the pinned protocol is
  this program's pre-registered adjudication display standard — one
  declared viewer, not neutral ground and not a claim about player
  environments. Bytes-domain findings are viewer-independent
  RELATIONSHIPS between pinned values (sprite bytes vs palette
  constants); every percept is protocol-scoped by construction. Contrast
  figures are WCAG sRGB relative-luminance ratios (gamma-aware; the
  banked `feedback_metrics.contrast_ratio`, source read this session) —
  and a ratio of ~1.0 between two near-identical dark colors is robust
  under any monotone per-channel recoding (both colors move together), so
  the equivalence finding does not hinge on display encoding. The
  council's premultiplied-alpha concern is refuted by the hard-alpha law:
  alpha ∈ {0,255} makes premultiplication an identity on visible pixels.
- **Routing:** none needed beyond the protocol already banked in this
  sprint's artifacts; any future demo handed to the owner should carry
  the protocol line (a packaging convention, not a new rule).

### Screened, no defect (the machine sweep's negative space)

- Zero interior transparency holes, 22/22 sprites — the literal
  "hole-in-the-bytes" class is EMPTY.
- Head-translation recolor clusters at every cut — the banked byte-exact
  rigid translations (v2–v7), art by adjudication.
- a0-right under-snout shading (outline `#401c10`, 1.17:1 vs floor) —
  present and stable across the pose family; the stable-across-poses rule
  classifies it art; noted as sharing the low-floor-contrast family for
  any future palette work.
- Walk frames f0–f3: accent counts identical to idle (14 down / 10
  right); no anomaly.
- The owner's "plus other visual flaws": not manufactured into entries.
  What the machine sweep covers (holes, accent structure, cut
  localization, 22/22) found exactly the register above; further
  owner-named sightings would seed their own audit passes.

## Presentation scores (accuracy scored separately above)

- **Register + verdict: 8.5/10.** Answer-first resolution of the owner's
  sighting with the two decisive numbers (6.6 vs 1.09) carrying the whole
  story; every entry pairs machine facts with a scoped perceptual line.
  Cost: the register is long; the pyramid mitigates.
- **Strips: 9/10.** The per-tick 8x rows make the aperture effect visible
  without any playback: eyes present → four aperture columns → eyes
  return, over both real palettes. The banner + protocol line make the
  class and viewing law unmissable.
- **APNG set: 8/10.** Real-speed and slowed variants at two pre-baked
  scales cover the protocol matrix; the per-frame label keeps every frame
  self-identifying. Cost: eight files — the matrix is honest but bulky.
- **Report JSON: 8.5/10.** Full cluster geometry per pose and per cut;
  self-contained context tables; deterministic bytes.

HFO gate (owner register): truncated pyramid, severity-honest verbs
("reads as", "measured", never "broken"), typed uncertainty (fusion
questions named unprovable-here with the instrument that decides them),
no promises, no lore; accuracy and presentation scored on separate axes
throughout; `docs/owner-redirects.md` re-read against the same checklist
(mechanical register, no narrative, carrier named).

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call attacking five numbered claims; every verdict
re-verified against primaries before adoption (v12/v13 precedent — the
council's strongest charges partially dissolved on the pre-registered
texts, and four real kernels were adopted):

1. **Q1 (detector soundness) — CONFIRMED by the council; two scope notes
   adopted.** The named blind spot (edge-cropped "artistic negative
   space" reads as exterior) is real in general and impossible on banked
   inputs — the `[2,2,29,29]` bounds law keeps every sprite off the
   canvas edge; recorded as a scope note rather than a detector change.
   The 4-connectivity fragmentation note (a diagonal transparent channel
   would report as multiple 1px holes) is carried with the convention —
   moot on a zero-hole set.
2. **Q2 (domain rigor) — UNCERTAIN from the council; one charge dissolved
   on the primary, one kernel adopted.** The charge that DEF-1 is "a
   viewer-domain claim dressed in bytes-domain metrics" dissolves against
   the pre-registered taxonomy text, which defines the bytes class to
   include "an interior opaque region whose color is optically
   background-equivalent (measured against the pinned zone palettes)" —
   fixed before any artifact existed; the classification followed the
   rule, not convenience. ADOPTED: DEF-1 now states its two layers
   explicitly (viewer-independent relationship between pinned values;
   protocol-scoped percept), and DEF-2 names its falsification instrument
   — the temporal class is falsifiable by the banked capture protocol,
   answering the unfalsifiability charge with the same structure the
   banked register's fusion questions already use.
3. **Q3 (re-adjudication creep) — CONFIRMED by the council; re-verified
   as PARTIALLY dissolving, kernels adopted.** The "incompatible
   framings" charge is refuted by the numbers (6.6:1 body cue and 1.09:1
   floor collision are the same pixels against different grounds — both
   banked statements and this finding are simultaneously true). The "de
   novo adjudication wearing cross-reference clothing" charge is answered
   by the sprint brief's own scope law: a confirmed finding on a
   never-adjudicated axis is a NEW finding banked under this sprint's
   pre-registered bars — that is this sprint's sanctioned mission, not
   creep; no banked bar, floor, or PASS is moved. ADOPTED from the
   kernel: severity is now grounded empirically (owner-observed, exposure
   frequency) with an explicit disclaimer that no retroactive normative
   bar is registered; routing is framed as an owner question, with
   accept-as-art as a first-class option.
4. **Q4 (routing honesty) — REFUTED by the council (my draft's routing
   was asymmetric); adopted nearly whole.** The draft over-specified the
   fix (a bound shade) and under-specified alternatives. The register now:
   binds no shade (the full-ramp measured table is context); adds
   accept-as-art (option 0) and defer-until-frame-pins (option 1, made
   live by the owner redirect); states the ranking criterion (this repo's
   cost); names the runtime-repalette option as existing but structurally
   out of this repo's proposal space (one-way boundary) rather than
   silently ranking it; and acknowledges DEF-2's contingent cost and the
   sequencing that avoids paying it twice.
5. **Q5 (unthought risk: color management / "the protocol is itself a
   viewer") — PARTIALLY ADOPTED, partially refuted with primaries.**
   ADOPTED: the scope statement in DEF-3 (the protocol is one declared
   adjudication standard; bytes findings are relationships, percepts are
   protocol-scoped). REFUTED with source: the contrast figures are WCAG
   relative-luminance ratios (gamma-aware sRGB, banked implementation
   read this session), not raw-RGB-only as charged (Euclidean distance is
   reported alongside, labeled as such); a ~1.0 ratio is robust under
   monotone per-channel recoding; premultiplied-alpha effects are
   identity under the hard-alpha law. The residue worth keeping: exact
   ratios wobble across display encodings even though the equivalence
   class does not — carried inside DEF-3's scope statement.

Net: two scope notes (Q1), two precision layers + a named falsification
instrument (Q2), empirical-severity + owner-question framing (Q3), a
rebuilt four-option routing with stated criterion (Q4), one scope
statement + two source-level refutations (Q5). No machine number changed;
no bar moved; no banked verdict touched.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: only `done/` — no new receipts, nothing owed, nothing
  polled. Outbound: exactly one protocol-mandated re-pin note
  (`from-game-two-assets-v14-repin-1b0d3dd.md`, fire-and-forget).
- Pins: content re-pin `3841ded` (`c5c146d`→`1b0d3dd`, J1 renderer.rb
  merged-rect-runs perf refactor — semantic-preserving by its banked
  in-code byte-safety argument, no draw-path constant moved, every
  render-reference constant value-re-verified, attack_timing 5/4/8/13
  re-verified); mechanical identity re-pin `33238f9` (`1b0d3dd`→`3c0ff6c`,
  test-only hops, blobs identical, timing re-verified). Both committed
  alone, staged-list verified. Gate exit 0 after each and immediately
  before banking — the pre-banking run reports a trailing identity-drift
  WARNING (`3c0ff6c` → `57aaeb0`, docs-only hops, all pinned blobs
  identical, attack_timing 5/4/8/13 re-verified read-only at `57aaeb0`);
  per the standing rule it re-pins at the next sprint checkpoint (the
  banked v13-close pattern).

## Non-claims

No banked verdict is touched, softened, or re-opened (v2's k0 tell PASS
and v3's distinctness bars stand on their own axes); zero new creature
pixels; zero exports; zero releases; nothing authored; nothing scheduled —
every routing line is a proposal for an owner decision. Zero lettered
register items ((a)–(o)/x0) adjudicated, previewed, or answered; the
temporal register is untouched (DEF-2 proposes a future candidate item,
it does not add one). No runtime evidence exists or is claimed — every
artifact is SYNTHETIC-class, composed of banked bytes under the declared
mapping. The at-speed behavior of the aperture percept is explicitly
unmeasured here; the instrument that measures it is the banked capture
design, owner-sequenced.

## Stop

Sprint 14 stops here: one audit tool, 30 tests, one machine report, 12
labeled playback/inspection artifacts, one classified defect register
(1 bytes / 1 temporal / 1 viewer, owner sighting resolved to DEF-1 with
DEF-2/DEF-3 as amplifiers), two re-pin commits, one owner-redirect
record, one dev-seat note. Routing proposals carried to v15+: the DEF-1
owner question (accept / defer / authoring-exploration), the DEF-2
register-candidate contingent on it. No authoring, no second audit tool,
no capture execution, no game-side code, no settle-bob work; audio and
tile era stay parked.
