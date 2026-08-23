# Pipeline-maturity maintenance v18 — verdict

**Answer first: C3 is MET — the clean-checkout caveat the register
carried since v17 is closed by a scripted both-directions proof
(clone-of-committed-HEAD gate run exit 0; tampered-clone negative
control exit 1 naming the violation), and the re-pin protocol's
mechanical half is now a permanent read-only verifier that routed two
LIVE identity hops during this same sprint.** This was the register's
FIRST maintenance cycle: one status row moved (C3
MET-AT-CHECKPOINT → MET), all 11 shape tests stayed green with ZERO
test edits, and the update law (new carrier + sprint commit against
the shape tests) held in practice. Zero pixels, zero exports, zero
pinned-module edits; the v13–v17 lattice is machine-proved untouched
at banking. The current answer remains NOT integration-ready — C6
stays OPEN, doubly gated; nothing here asks for anything.

Reviewed artifacts:

- `reviews/maturity-v18/checkout-report.json` — the banked
  both-directions proof (run 2; run 1 recorded below).
- `tools/checkout_gate.py` + `tools/pin_drift.py` +
  `tests/test_maturity_tools.py` (23 fixture-only tests).
- `docs/integration-readiness.md` — the C3 row + header/summary-table
  lines it implies (the only register delta).
- Pre-registration: `reviews/maturity-v18/rationale.md`, committed
  `612d79a` WITH both tools and their tests BEFORE any proof artifact
  or register edit existed (the standing two-commit law). Both
  protocols, the decidable-class table, the C3 target wording, and
  every bar are unchanged from it; two council-adopted
  post-pre-registration strengthenings are recorded below and marked
  in the module docstring (the v17 rule-d pattern).
- Session model `us.anthropic.claude-fable-5` (verified from
  `PI_MODEL`). Council seat cross-vendor (Kimi K2.5), one consolidated
  adversarial call: brief 13,379 bytes (~3.5k tokens) inlining the
  FULL old/new C3 rows, the banked checkout report, and pin_drift's
  docstring + decidable-class table; `--max-tokens 2600`,
  `stop_reason=end_turn` (answer completed under the cap; the shim did
  not echo a usage block this run — budget respected by construction:
  prompt size + output cap ≤ 8k). Response file-redirected, read as
  UTF-8; reconciliation in the appendix.

Sprint question (rationale, fixed first): can the C3 caveat close with
a scripted both-directions clean-checkout proof judged honestly against
what "clean checkout" can mean for a gate that contracts against live
externals, and can the re-pin protocol's mechanical half become a
permanent read-only verifier — without moving a pixel, a pin, or any
row but C3?

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS | one full discover run after all edits: **668 tests, OK, 3456 s** (645 at v17 close + 23 new); no live-pin red mid-run this time — both upstream hops this session were identity-class and re-pinned at the protocol checkpoints |
| 2 | Both asset_gate runs exit 0 | PASS | step 0: exit 0, SILENT (HEAD == pin `d687f3a` at session start — no drift, no re-pin due); pre-banking: exit 0 with the identity WARNING at `75627d85`, then the due mechanical re-pin `d8dfbb3` and a clean exit-0 re-run (no warning) immediately before commit 2 |
| 3 | Five standing `--check`s exit 0 at banking | PASS | `track_recompose`, `pose_integrity_metrics`, `remedy_metrics`, `adoption_demo`, `exports_guard` all exit 0 after every v18 edit existed — module-pin lattice + 26/26 export pins + zero-new-exports machine-proved untouched |
| 4 | Checkout proof captured in BOTH directions | PASS | banked report (run 2, clone of `393e195`): primary exit 0; negative control exit 1 with `source_files[0].sha256_lf does not match game-two` named; LFS two-phase clean (pull exit 0, 0 pointers remaining); secondary fresh-venv PASS (pip exit 0, gate exit 0). Run 1 (clone of `612d79a`, superseded, quoted here as evidence): identical outcomes — primary exit 0 carrying the identity-drift WARNING that exposed the due re-pin, negative exit 1 named, secondary PASS |
| 5 | pin_drift proven on all four fixture classes AND read-only | PASS | fixture matrix green: identity→mechanical; additive-only clean→candidate; moved constant (`swell = 6`→`7`)→constant FAIL + judgment, never candidate; deletion→judgment quoting the clause; PLUS timing-moved-while-blobs-identical→judgment (the not-pinned combat.json seam); read-only proven by full-tree byte-hash (`.git` included) before/after a complete CLI run |
| 6 | Zero additions under `exports/`; zero new pixels | PASS | exports_guard `--check` exit 0 (9/9 dirs manifest-complete); deliverables are docs + tooling + one JSON report; trees that grew: `tools/` (+2), `tests/` (+1), `reviews/maturity-v18/` (this bundle) |
| 7 | Zero edits to pinned modules, banked artifacts/verdicts, `docs/selection-register.md` | PASS | bar-3 pin checks prove the module lattice; selection register byte-untouched; the only non-new file edits: the C3 register delta + two one-line `game_commit` re-pins (protocol class) |
| 8 | Register shape tests 11/11 post-edit, zero test edits | PASS | `tests.test_exports_guard` 27/27 green after the C3 edit (11 `ReadinessRegisterShape` among them); the shape file's git blob is untouched this sprint |
| 9 | Zero writes into `../game-two`; citations fresh; quotes verbatim | PASS | read-only `git -C` + `git show` throughout (temp-file dumps for blob greps); carriers re-read from committed texts this session; pin_drift quotes the owner-extended clause verbatim with provenance |

**Accuracy: 9/9 integrity bars.**

## Machine findings

- **The C3 flip is evidence-first.** The banked report embeds RAW exit
  codes and full gate stdout/stderr for every direction — a reader can
  judge the proof without trusting the tool's verdict labels. The
  clone's HEAD equals the source HEAD (recorded both ways), LFS
  resolved from the local origin (zero network in the primary), and
  the negative control tampered exactly the hard-failure seam
  (`sha256_lf`, not the WARNING-class `game_commit`).
- **"Clean checkout" is now a defined claim, not a vibe.** The row
  states the variant proven (from-scratch clone of committed HEAD),
  states why a hermetic reading is structurally impossible for THIS
  gate (it contracts against the live sibling checkout, the Aseprite
  pin, and an interpreter by design), and names every external. The
  proof is re-provable on demand — against the then-current pin, which
  is what "re-judged at every sprint" has always meant here.
- **pin_drift paid for itself inside its own sprint.** Two live
  identity hops routed during v18 (`d687f3a`→`139d812b` at `393e195`,
  `139d812b`→`75627d85` at `d8dfbb3`): each took one tool run, one
  surgical edit-tool line replacement from the printed pair, one
  gate re-run, one solo commit — minutes per hop, zero re-derivation,
  the exact cost the v17 finding predicted. Constants 20/20 (19
  derived needles + 1 JSON-internal consistency law) and attack_timing
  5/4/8/13 re-verified mechanically at both hops.
- **The derived-constant battery is continuously self-testing.** The
  needles are rebuilt from `render-reference.json` at every call and
  checked even when blobs are identical — a needle-derivation bug
  surfaces as a false FAIL on an identical blob, loudly, rather than
  as silence on a real drift.
- **The unpinned-tool class now has three members** (`exports_guard`
  v17; `checkout_gate` + `pin_drift` v18), all sharing one identity
  chain: unpinned means not hash-frozen against FUTURE edits, never
  unidentifiable — every banked carrier names the commit whose tree
  content-addresses the exact tool bytes that produced it, and each
  tool's behavior is suite-carried (guard: both-directions fixtures +
  live-tree assertion; v18 tools: 23 fixture tests incl. the
  read-only proof). None of the three gates anything by itself.

## Register HFO gate (accuracy and presentation scored separately)

Register delta accuracy: the new C3 row claims exactly what the banked
report proves (both directions, named externals, variant definition,
temporal binding of re-provability); the header and summary table carry
the same exact split with no aggregation term; no other row moved; no
scheduling verbs (machine-scanned by the suite). Verdict-checked
against the report bytes line by line.

Register delta presentation: **9/10.** The row reads answer-first
(MET, then the proof shape, then scope), and the variant-definition
sentence kills the strongest misreading at the source. Cost: the row
is now the register's longest; accepted — it carries the register's
only external-contract definition.

Tool CLI output (HFO, text-surface critique): typed failures
(`checkout gate HARNESS ERROR:`, `pin-drift ANALYSIS FAILURE:`,
per-constant `FAIL <name>: pattern not found in <file>@<sha>`),
one-line OK/route lines, loss-framed failures, silent-on-pass suite
behavior preserved (both tools print only when invoked, never in
tests). The pin_drift report puts the ROUTE line LAST — the critical
line stays visible at the prompt. Accuracy of output claims: the
"writes nothing" banner is byte-hash-proven; the candidate line's
duty list matches the protocol's residual duties exactly.
Presentation: **9/10** (cost: the judgment route line is long because
it quotes the clause verbatim — the pre-registered choice).

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call, five questions. Returned: **Q1 UNCERTAIN
(variant wording), Q2 CONFIRMED (misclassification + framing), Q3
CONFIRMED (unpinned-class circularity), Q4 CONFIRMED (upgrade
ratification gap), Q5 CONFIRMED (temporal binding).** Per the v12–v17
precedent every adverse verdict was re-verified against primary bytes;
the reconciliation:

1. **Q1 (C3 wording) — the honesty charge dissolves into a wording
   adoption, taken whole.** The council: "'never a hermetic
   environment' is defensive disclosure, not honest closure; the
   contract's original intent is lost to history." Primary: the
   contract is THIS repo's own law and its gate REQUIRES live
   externals (`--game-root` content checks, the Aseprite executable
   pin) — under a hermetic reading C3 is unsatisfiable by
   construction, which would have made v17's MET-AT-CHECKPOINT equally
   over-claimed. ADOPTED: the row now states the definitional split
   explicitly ("The contract wording names no checkout variant; this
   row records the variant proven") instead of silently redefining —
   closure, not disclosure.
2. **Q2 (pin_drift misclassification) — the core scenario is REFUTED
   on primary bytes; the framing kernel is ADOPTED.** The council's
   concrete case ("content mutations with zero net deletion — numstat
   shows 0 deletions if the hunk structure aligns"; `attack_damage:
   10 → 100` same-line-count routes candidate) is factually wrong
   about git: a live re-verification (in-place mutation, identical
   line count) prints `1  1` — git's line-diff model counts every
   in-place change as +1/-1, so `deletions == 0` mechanically
   guarantees pure appends/insertions; the fixture test
   (`swell = 6`→`7`) proves the moved-constant class routes to
   judgment, and balance values live in combat.json — NOT a pinned
   file — which is exactly why attack_timing is re-verified on every
   run (fixture-proved to block even with all blobs identical).
   ADOPTED (framing): the candidate route line now carries the
   session's REMAINING duties (read the diff, apply the pairs, commit
   alone, mail the note) so "candidate" can never read as pre-vetted;
   docstring updated and marked as a council adoption.
3. **Q3 (unpinned-class circularity) — partially refuted on identity;
   the census kernel is recorded.** "If checkout_gate falsely reports
   PASS there's no hash-pin to detect drift" — the carrier names the
   commit (`393e195`) whose tree content-addresses the exact tool
   bytes (git IS the hash pin for banked runs), and the report embeds
   raw exit codes + full gate output, so the evidence is readable
   without trusting the tool's labels; the 23 behavioral tests
   (including tamper logic and the read-only proof) were not in the
   brief — evidence-availability, the v17 Q2(ii) pattern. The
   council's own JSON misread ("negative_control verdict PASS is
   ambiguous... reading carefully, exit_code is 1 and violation_named
   true") resolved itself in-flight. RECORDED as real: the class is
   now three modules and growing; this verdict's machine findings
   state the identity chain and the census so the next member must
   argue against a named list, not a vibe.
4. **Q4 (upgrade-ratification gap) — CONFIRMED as a real structural
   question; carried, not legislated.** Mitigations that exist today:
   the two-commit law (protocol committed before the artifact), 11
   shape tests, the register's advisory class ("the hub decides"), and
   the non-claims line that no count of MET rows constitutes an ask —
   status inflation cannot force integration because the register
   decides nothing. What does NOT exist: an owner-ratification hop for
   status UPGRADES specifically. That is a register-law change outside
   this sprint's one-row scope; CARRIED to the next register-touching
   sprint as an explicit open question for the owner: should MET
   upgrades require an async owner ratification line the way
   selections do? (The hub reads this verdict; no mail owed.)
5. **Q5 (temporal binding / re-provability) — the design half is the
   gate's law; the wording half is ADOPTED.** "Re-running produces
   DIFFERENT results because the game repo moved" — that is the gate
   WORKING: the live-external verdict is SUPPOSED to track current
   compatibility (content decides, identity warns, drift re-pins at
   checkpoints — the owner's parallel-session law). The report records
   `game_head_at_run` for identification, and the negative control
   tampers the pin seam — the assets-side half of exactly the
   load-bearing comparison the council said was unvalidated. ADOPTED:
   the row now says "re-provable on demand by the tool against the
   then-current pin," making the temporal binding explicit; the
   snapshot-game-two alternative is structurally banned (one-way
   boundary — this repo never packages game content).

Net: two wording adoptions folded into the register row (variant
definition; then-current pin), one tool strengthening (candidate line
carries residual duties, docstring marked), one identity-chain
statement + class census recorded, one open register-law question
carried to the next register sprint, one REFUTED-on-primaries council
scenario documented with the live git demonstration. No bar moved; no
banked byte touched; the C3 status itself was not contested by any
verdict — the wording around it got stronger.

## Non-claims

No integration, no timetable, no integration ask — the register stays
advisory input to the hub's parking-lot gate; C6 stays OPEN behind its
two decision gates and one queued upstream dependency, none of which
this sprint touched. No claim of hermetic reproducibility — the C3 row
defines its variant and names its externals. No claim that pin_drift
approves anything: it is an advisor with two mechanically decidable
routes and a quoted-clause stop for everything else; the session
applies the protocol, and draw-value moves or true removals still stop
for owner review. No capture-spec content (the tool spec has not
arrived; nothing drafted, nothing parked). No new pixels, no exports,
no lore; mechanical ids throughout.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: empty (all prior receipts in `done/`); the expected
  capture-contract tool spec has NOT arrived — nothing to park, no
  reply owed, no polling done. Nothing arrived mid-sprint.
- Outbound: none owed, none sent — both re-pins this session were
  identity-class (the protocol's note duty attaches to CONTENT
  re-pins; identity hops carry no note).
- Pins: step-0 gate SILENT at `d687f3a` (HEAD == pin, first
  no-drift session open since the cadence pattern was banked) →
  mid-sprint mechanical re-pin `393e195` (→`139d812b`, pin_drift's
  first live hop) → mechanical re-pin `d8dfbb3` (→`75627d85`, second
  hop) → final pre-banking gate exit 0, no warning. game-two's seat
  stays LIVE (~3 commits/hour measured again this sprint); the
  pre-push gauntlet may catch another hop — pin_drift does the
  mechanical half, route per protocol, plain retry.

## Stop

Sprint 18 stops here: one both-directions clean-checkout proof (banked
report + the run-1 evidence above), one C3 row MET with the variant
defined and externals named, one read-only pin-drift verifier proven on
four fixture classes and two live hops, 23 tests (suite 668), one
pre-registration, this verdict, two mechanical re-pins. Zero pixels;
zero exports; nothing pinned touched; every other register row
byte-identical. Carried to v19+: the capture-contract tool spec intake
(parks as proposal input when it arrives), the role re-pin and
gate-lift decisions (owner/hub), the at-speed + viewport watch items
riding the queued capture instrument, the shade double-duty authoring
watch, the Q4 upgrade-ratification question for the next
register-touching sprint, and the trailing identity re-pin as game-two
moves. The register updates only when a new carrier lands — by a
future sprint, against its shape tests, exactly as this one did.
