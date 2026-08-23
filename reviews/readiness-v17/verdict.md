# Readiness register + exports guard v17 — verdict

**Answer first: "can we integrate yet?" is now a document read — the
answer today is NOT YET (C6 OPEN, doubly gated) — and the two-sprint-old
exports-tree hole is closed by a guard the suite enforces continuously.**
`docs/integration-readiness.md` instantiates the asset-contract's six
runtime-integration stop conditions as carrier-cited statuses under a
test-enforced status-only law (C1/C2/C4/C5 MET, C3 MET-AT-CHECKPOINT,
C6 OPEN); it states its own advisory class — input to the hub's
parking-lot gate, the hub decides — and preempts none of the three
pending decisions (role re-pin, gate lift, capture tool spec).
`tools/exports_guard.py` closes the v15 council Q3 residue with a
whitelist DERIVED from three banked exporter constants (never
duplicated — test-enforced), proven in both directions on fixture trees
and asserted clean on the live tree by the suite. Zero pixels, zero
exports, zero pinned-module edits; the v13+v14+v15+v16 lattice is
machine-proved untouched at banking. Mid-sprint, game-two's live seat
landed two pinned-file drifts during the 51-minute suite runs; both were
routed through the owner-extended approve-by-default protocol
(additive-only diffs; the renderer hop got the full 14-constant
value-re-verify) and re-pinned in their own commits with fire-and-forget
notes mailed.

Reviewed artifacts:

- `docs/integration-readiness.md` — the register (status-only law,
  shape-test-enforced by `tests/test_exports_guard.py`).
- `tools/exports_guard.py` + `tests/test_exports_guard.py` — the guard
  and its both-directions proof (27 tests, 11 register-shape).
- Pre-registration: `reviews/readiness-v17/rationale.md`, committed
  `8f31234` with the toolchain BEFORE the register or this verdict
  existed. Rules (a)–(c), the row skeleton, and every bar are unchanged
  from it; rule (d) is a council-adopted post-pre-registration
  strengthening, recorded below and marked in the module docstring.
- Session model `us.anthropic.claude-fable-5` (verified from
  `PI_MODEL`). Council seat cross-vendor (Kimi K2.5,
  `moonshotai.kimi-k2.5`), one consolidated adversarial call: 4,389 in /
  2,600 out = 6,989 of the 8k cap, `stop_reason=max_tokens` (the trailing
  summary table was cut; all five question bodies returned complete);
  response file-redirected, read as UTF-8; reconciliation in the
  appendix.

Sprint question (rationale, fixed first): can pipeline maturity become a
mechanical, carrier-cited status document without preempting the three
pending owner/hub decisions, and can the v15 Q3 exports-guard residue
close from banked constants without touching anything pinned?

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS (drift-routed) | Two full discover runs, 645 tests each (618 at v16 close + 27 new): every non-pin test green in both runs; the only failures were the live-pin tests catching REAL upstream drift mid-run (run 1: creature.rb hop `97964ed8`→`91fdc00b`; run 2: renderer.rb+display.json hop `91fdc00b`→`efc65a0` — game-two's held seat lands ~3 commits/hour against 51-minute runs, the banked cadence pattern). Each drift re-pinned per protocol, then the drifted scope re-proven green (`test_asset_gate` 21/21 post-re-pin; guard file 27/27). The pre-push full gauntlet remains the blocking whole-suite gate at push (exit code is the verdict; drift mid-hook → re-pin, plain retry) |
| 2 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 with the expected identity-drift WARNING, then the due mechanical re-pin `ccbd460` (`546769ff`→`97964ed8`, 5 blobs byte-identical, attack_timing 5/4/8/13, committed alone); pre-banking: exit 0 at pin `efc65a0` (run after the final re-pin, no WARNING) |
| 3 | Four standing `--check`s exit 0 at banking | PASS | `track_recompose`, `pose_integrity_metrics`, `remedy_metrics`, `adoption_demo` all exit 0 this session after the guard and register existed — the v13+v14+v15+v16 module-pin lattice and all release pins machine-proved untouched |
| 4 | Guard both directions + live tree clean | PASS | fixture proofs: valid tree passes; planted stray dir, stray top-level file, missing release.json, whitelisted-name-as-file, nested stray, nested directory, unreadable manifest each fail with exactly their typed failure; live tree: `check_exports_tree` returns `[]` in-suite and `--check` exits 0 (9 release ids whitelisted, 9 present, pins 26/26) — the suite now enforces the guard on every run |
| 5 | Zero additions under `exports/`; zero new pixels | PASS | no new entry under `exports/` (the guard itself proves it); deliverables are docs + tooling only; trees that grew, named exactly: `tools/` (+1 module), `tests/` (+1 file), `docs/` (+1 register), `reviews/readiness-v17/` (this bundle) |
| 6 | Zero edits to pinned modules, banked artifacts, banked verdicts, release bytes; selection register untouched | PASS | the guard imports `seam_metrics`, `remedy_masks`, `ingest_audio` unmodified (bar-3 pin checks prove the lattice; `ingest_audio` is gate-pinned via the audio release's `toolchain.exporter_sha256`, verified against the live file by `tools/asset_gate.py` L184-195); `docs/selection-register.md` byte-untouched |
| 7 | Zero writes into `../game-two` | PASS | read-only `git -C ../game-two rev-parse/show/log/diff` throughout; one seat-lease block fired on a read-shaped temp-file script (game-two's seat is LIVE this session) — rerouted to plain `git -C` reads per the pre-authorized fallback; no write occurred, no gate routed around |
| 8 | Citations at the fresh pin; carriers verbatim | PASS | all v15/v16 quotes re-read from committed texts this session; both done/ mail carriers quoted verbatim in the register's rulings section; register rows carrier-cited (test-enforced) |
| 9 | Register shape tests active and green | PASS | 11 shape tests activated at banking (six C-rows with status+carrier, carrier location classes, banned-verb scan, no-lore-class scan, advisory header, contract kernels, watch items, verbatim quotes, non-claims, affordance row) |

**Accuracy: 9/9 integrity bars.**

## Machine findings

- **The whitelist is derived, not declared.** `release_whitelist()` is a
  call-time union of `seam_metrics.RELEASE_IDS` (7),
  `remedy_masks.RELEASE_ID`, and `ingest_audio.RELEASE_ID`; the
  no-literal test forbids any of the nine ids appearing as text in the
  module. Recorded deviation from the sprint brief, fixed in the
  pre-registration: the brief's two-constant formula misses the banked,
  gate-valid audio release on the live tree — the brief's own
  live-tree-clean bar forces the three-constant form (council Q2
  attacked it; reconciliation below).
- **Rule (d) — nested strays — is a council adoption.** Pre-registered
  rules (a)–(c) guard the top level; the council named the
  release-dir-interior hole (a stray inside `exports/<id>/` invisible to
  (a)–(c), and only partially visible to the pins check, whose stray
  scan is `calibration-*/*.png`). Adopted as rule (d): every entry
  inside a whitelisted dir must be the manifest or a file its `exports`
  list names, else `nested-stray: <id>/<name>`; unparseable manifests
  are their own typed failure. Both directions test-proven; the live
  tree passes — all nine release dirs are manifest-complete.
- **The guard is deliberately UNPINNED.** Its extension law requires
  future releases to edit `release_whitelist()` in their own
  pre-registration commits; hash-pinning it would recreate the
  frozen-exporter trap this repo already banked (any edit invalidates
  banked pins). Its integrity is test-carried (both-directions fixtures
  + live-tree assertion on every suite run), not hash-carried.
- **Pin cadence, measured live:** three re-pins in one session —
  `ccbd460` (identity, due from v16), `0eb5f52` (creature.rb +9/-0,
  `grow_max_hp!` sim-side, approve-by-default), `ee35720` (renderer.rb
  +35/-0 `draw_level_pops` + HUD level strip + banner suffix,
  display.json +19/-0 new keys; all 14 `render-reference.json`
  constants value-re-verified at the new blob, none moved;
  approve-by-default, renderer branch). `attack_timing` 5/4/8/13
  re-verified at every hop. Two fire-and-forget notes mailed; no ask
  owed.

## Register HFO gate (accuracy and presentation scored separately)

Accuracy: every status restates its carrier without extrapolation — C1
quotes the closure ruling; C2 quotes the v0 win verbatim ("a genuine
improvement, not least-bad") plus the selection chain; C3 names its own
evidence class honestly (working-tree runs; the literal clean-clone
variant unrecorded — the caveat IS the status); C4/C5 are scoped to the
banked set with the at-speed gap carried as a watch item, not hidden;
C6 names its two decision gates and one queued dependency strictly from
carriers. No scheduling verbs (machine-scanned), no design content, no
recommendation weight (stated in non-claims).

Presentation: **9/10.** Answer-first header (the exact status split, no
aggregation), a six-row scan table, verbatim rulings quarantined in one
section so quotes are carriers rather than prose, watch items one
fixation each. Cost: the C6 row is dense (three "waits on" items with
their quote fragments inline).

Verdict presentation: **8.5/10.** Machine table + findings + single
reconciliation appendix; the drift narrative is confined to bar 1 and
the pin-cadence finding. Cost: bar 1's cell is long — the honest price
of banking a drift-routed suite claim.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call with the FULL register text, the FULL guard
module, and the carrier quotes inlined, attacking five numbered
questions. Returned: **Q1 CONFIRMED-no-preemption (one wording
UNCERTAIN), Q2 REFUTED-in-part with CONFIRMED holes, Q3 CONFIRMED
side-effect + UNCERTAIN pinning, Q4 REFUTED on header honesty +
CONFIRMED pressure, Q5 CONFIRMED boundary charge.** Per the v12–v16
precedent every adverse verdict was re-verified against primary bytes;
the reconciliation:

1. **Q1 (register over-claim) — no preemption found on any row; the
   "doubly gated" wording kernel ADOPTED.** The council confirmed every
   status matches its carrier and C6's "waits on" list adds no
   sequencing. Its one catch: "doubly gated" fronting a three-item list
   reads inconsistent. Adopted: the header states the exact status
   split; C6 now separates "two pending decisions" from "one queued
   upstream dependency, not a decision gate."
2. **Q2 (guard retroactivity + extension law) — the designed-red charge
   dissolves on the pre-registered law; the as-file charge dissolves on
   a test the council could not see; the nested-stray hole is REAL and
   ADOPTED as rule (d); the "extension law already violated" charge
   dissolves on its own text.** (i) "Guard goes red on legitimate
   mid-sprint state" — that is the docstring's own pre-registered law
   ("going red on a new `exports/` entry is the designed behavior"):
   red-before-pre-registration is the feature. (ii) "Whitelisted name
   as a plain file is silently ignored" — refuted by construction and
   by a green pre-council test
   (`test_whitelisted_name_present_as_plain_file_fails`: the `elif`
   routes it to `stray-file`); evidence-availability, the test file was
   not in the brief. (iii) Nested strays: CONFIRMED hole, adopted as
   rule (d) with both-directions tests (see machine findings). (iv)
   "Hardcoded module references violate the law in spirit" — the law
   bans id LITERALS; module-attribute references are the derivation
   itself (the constants live in banked, pin-verified modules). Adopted
   instead: the docstring now states the enforcement split plainly —
   mechanical half (no-literal test + suite red), temporal half
   (commit-1 ordering) is process law carried by pre-registration
   review, not by code. (v) Case/symlink exotica: recorded — both
   degrade to loud typed failures, never silent blessing.
3. **Q3 (frozen-state) — the `sys.path` observation is the repo's
   standard tools-import pattern (every banked tool does it; the suite
   already imports them all); the real kernel ADOPTED is the pinning
   question.** `ingest_audio` is not unpinned: the audio release's
   `toolchain.exporter_sha256` pins it and the asset gate verifies it
   against the live file (re-verified this session). The guard itself
   is deliberately unpinned — stated as a design decision in the
   machine findings (the extension law requires future edits;
   test-carried integrity).
4. **Q4 (register honesty) — ADOPTED WHOLE.** The council caught real
   status inflation: the draft header said "the five other stop
   conditions carry MET-class status," collapsing C3's
   MET-AT-CHECKPOINT into an aggregate term outside the defined
   vocabulary. The banked header names the exact split and drops the
   aggregation; non-claims gains: "No recommendation weight: OPEN rows
   do not age into asks, and no count of MET rows constitutes one."
   The structural-pressure charge is recorded as inherent to any status
   artifact; the mitigations are the advisory-class header, the hub's
   named authority, and the commissioning context (the hub's gate needs
   a live input — this register is that input, not an argument).
5. **Q5 (unthought risk: the k0 affordance IS integration
   design/capture, boundary already violated) — substantially REFUTED
   on primaries; the wording kernel ADOPTED.** The staging seam
   composes SYNTHETIC review artifacts from banked bytes inside this
   repo (`adoption_demo` docstring: zero new pixels, zero exports, zero
   adjudication; v16 verdict non-claims: no integration, no schedule).
   C6's "deterministic capture" is the game-state instrument — per the
   v19 receipt a session-end bundle + state-track re-execution on the
   game's own replay runner, built host-side by the game seat; it
   shares nothing with APNG staging. The one-way boundary means
   game-two never consumes this repo's tools (invariant 1: a later
   game-two change copies an approved PNG plus manifest, nothing else) —
   no dependency direction exists for the charge. Adopted: the
   affordance row now states its class explicitly ("not loading, not
   draw order, not runtime capture — C6 is untouched by it"), killing
   the misread at the source.

Net: one code strengthening (rule d + tests), one header rewrite (exact
split), two row precisions (C6 gates/dependency; affordance class), one
non-claims sentence, one docstring enforcement-split statement, two
design decisions recorded (unpinned guard; derive-don't-duplicate
coupling). No bar moved; no banked byte touched; no register status
changed by the council pass — the wording around statuses did.

## Non-claims

No integration, no integration timetable, no integration ask — the
register is advisory input to the hub's parking-lot gate and says so in
its header. No design content anywhere in the bundle: loading, draw
order, and capture design remain behind C6's gates; the capture tool
spec belongs to the game seat (nothing drafted here). No re-opening of
banked verdicts: v15's selection and v16's adoption stand exactly as
banked; the register restates their outcomes with citations. No claim
that the guard protects release CONTENT (bytes stay `check_export_pins`
+ the asset gate's job; the guard is shape-only). No claim of a
clean-clone gate run (C3's caveat). The at-speed and viewport reads
remain unmeasured, owner-sequenced (watch items carried verbatim). No
new pixels, no exports, no lore; mechanical ids throughout.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: empty (all prior receipts in `done/`). The expected
  capture-contract tool spec has NOT arrived — nothing to park, no
  reply owed, no polling done.
- Outbound: two fire-and-forget re-pin notes to the game-two seat
  (creature hop; renderer+display hop with the 14-constant
  re-verify) — the standing protocol's note class, no ask in either.
- Pins: `ccbd460` (identity re-pin, step 0, due from v16) → `0eb5f52`
  (creature.rb content re-pin, additive-only) → `ee35720`
  (renderer.rb+display.json content re-pin, additive-only, constants
  re-verified). Gate exit 0 after each; final pre-banking run exit 0 at
  `efc65a0` with no warning. game-two's seat is LIVE and landing ~3
  commits/hour: the pre-push gauntlet may catch another hop — the
  routing is re-pin per protocol and plain-retry, per the banked
  cadence pattern.

## Stop

Sprint 17 stops here: one readiness register (six condition rows, one
affordance row, four watch items, verbatim rulings), one guard module
(four tree rules, typed failures, derived whitelist, extension law),
27 tests (16 active pre-bank + 11 register-shape at banking; suite 645),
one pre-registration, this verdict, three re-pins, two notes. Zero
pixels; zero exports; nothing pinned touched. Carried to v18+: the
capture-contract tool spec intake (parks as proposal input when it
arrives), the role re-pin and gate-lift decisions (owner/hub), the
at-speed + viewport watch items riding the queued capture instrument,
the shade double-duty authoring watch, and the trailing identity re-pin
as game-two moves. The register updates only when a new carrier lands —
by a future sprint, against its shape tests.
