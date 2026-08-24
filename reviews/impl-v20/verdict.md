# Implementation of the two v19-ratified decisions — v20 verdict

**Answer first: both owner-ratified decisions are LANDED and proven.
(1) The stage partition is active — the activation commit's own
pre-commit hook ran in 3m01s against 52m39s/49m18s old-config hooks
measured live the same session (~17.5x), with the pre-push ship gate
byte-identical (hashes banked below). (2) The aggregate-answer law is
register law with mechanical enforcement — dormant today by design,
negative-control-proven, hardened by two council adoptions (header
multiplicity fail-close; quote-must-appear-in-carrier). Full suite
after all edits: Ran 691 tests, OK. Zero pixels, zero exports, zero
status-row or "Current answer" movement.**

This was a PATH B sprint (spark brief, v20): the capture-contract tool
spec had NOT arrived at step 0 (inbox root empty, only `done/`) and
did not arrive mid-sprint; nothing is parked. PATH A (spec intake
review) remains first-priority the moment the spec lands.

## The ratification of record

Recorded verbatim with its reading in
`reviews/impl-v20/rationale.md` (commit `6641a2c`, before any
implementation): the owner's "Approved, proceed to design the next
session spark-up prompt…" line ratifies BOTH v19 recommendations —
brief 1 option (iii) stage partition, brief 2 option (iii)
aggregate-answer law. Step-0 contradiction check: none found. A
second in-session owner line ("approved, proceed", 2026-08-24)
resolved the one protocol stop this sprint hit (the `crossed→struck`
re-pin, below).

## Commit chain (this sprint, in order)

| Commit | Content | Own pre-commit hook |
|---|---|---|
| `be0d0bc` | identity re-pin `65936ea→ed73ee0` | ~56 min (old config) |
| `6641a2c` | pre-registration + inert `bin/fast_gate.py` + 17 fixture tests | 52m39s (old config) |
| `a41c17b` | content re-pin `ed73ee0→0ff0ba0` (creature.rb +4/-0 additive, approve-by-default) | 49m18s (old config) |
| `ac40ce0` | ACTIVATION: the one `swarmforge.toml` line | **3m01s (new config — the live proof)** |
| `daed539` | register law block (+18/0) + 6 shape tests (+141/0) | 2m56s |
| `7b0a6d8` | content re-pin `0ff0ba0→e51e26f` (creature.rb +3/-1, owner-approved) | 3m06s |
| `e03b8d0` | council adoptions folded into the checker (+70/-12, all within v20-added region) | 2m52s |
| `f150428` | identity re-pin `e51e26f→daaddd4` (pre-banking checkpoint) | 2m53s |

The partition's value showed inside its own sprint: the two re-pins
BEFORE activation cost ~56+49 min of hook each; the two after cost ~3
min each.

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Rationale + inert tool committed before activation | PASS | `6641a2c` (config untouched) precedes `ac40ce0` |
| 2 | Activation commit = exactly one config line; own hook banked | PASS | `git diff 54bd639..HEAD -- swarmforge.toml` = one line (`test_command` → `bin/fast_gate.py`); hook wall-clock `real 3m0.972s`, commit output banked in-session |
| 3 | Runner fails loudly (stale entry, budget, test failure) — fixture-proven, never on live config | PASS | 17 fixture tests in `tests/test_fast_gate.py` (derivation, stale `stale-slow-entry`, `empty-fast-tier`, `test-failure (rc=1)`, hollow-module `rc=5`, `budget-exceeded` on synthetic input, critical-line-last, SLOW-list + budget pins); plus one UNPLANNED live proof: the manual pre-activation run caught a REAL upstream content hop red (`test-failure: test_asset_gate (rc=1)`, exit 1, 2m53s) before going green post-re-pin (`fast gate OK: 13 module(s), 299 test(s), 190.4s (budget 600s)`) |
| 4 | Full discover green after all edits | PASS | `Ran 691 tests … OK`, rc=0, 3236.8s (668 inherited + 17 fast_gate + 6 aggregate-law at that point; the two 3b probes land the file at 8 — see honesty note) |
| 5 | `full_command`, `bin/full_gate.py`, `.coveragerc`, both hooks byte-identical | PASS | sha256 at close == session-start baseline: pre-commit `c8557faf…`, pre-push `5997892e…`, full_gate `4fefb0c1…`, .coveragerc `5f38035a…`; `git diff --stat 54bd639..HEAD` on full_gate/.coveragerc empty; hooks are untracked files, hash-compared directly |
| 6 | Register: "Current answer" + status rows + 11 existing shape tests byte-identical; new tests green incl. negative control | PASS | header/rows diffs vs `54bd639` empty (`HEADER-IDENTICAL`, `ROWS-IDENTICAL`); `ReadinessRegisterShape` class region diff vs `54bd639` empty (`EXISTING-SHAPE-TESTS-IDENTICAL`); register change = +18/-0; 35/35 in `test_exports_guard.py` green incl. flip-goes-red, satisfiability, bogus-carrier, quote-not-in-carrier, fake-second-header, fail-closed-header |
| 7 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 (2 warnings: identity drift + worktree note); pre-banking: exit 0 (identity-drift warning, re-pinned at checkpoint `f150428`) |
| 8 | pin_drift at every drift; re-pins solo | PASS | four drift events, four solo re-pin commits (table above); every routing followed the printed ROUTE line; the one SESSION JUDGMENT case went to owner review per protocol and was approved verbatim before landing |
| 9 | Five standing `--check`s exit 0 at banking | PASS | track_recompose, pose_integrity_metrics, remedy_metrics, adoption_demo, exports_guard — all rc=0, re-run after the final content edit (`e03b8d0`) |
| 10 | Zero pixels / exports / writes into `../game-two` | PASS | exports_guard clean; game-two touched only by `git -C` reads; the two outbound notes went to the MAIL directory, not the repo |
| 11 | Temp instrumentation deleted | PASS | session temp files (`v20_*` logs/brief/response, probe dir) deleted after banking; deletion `ls` in the close log |
| 12 | Unpinned-tool class = exactly 4 | PASS | exports_guard, checkout_gate, pin_drift (v17/v18) + fast_gate (declared by the v19 verdict, pre-registered here); `bin/` census: full_gate.py (pinned-frozen), fast_gate.py |
| 13 | Ambient files untouched; explicit staged paths per commit | PASS | `M AGENTS.md` + untracked ambient set present and unstaged in every staged-list check (printed before each commit) |

Honesty notes, named rather than absorbed: (a) the first
post-edit full discover ran green but its verdict line was lost to a
`tail -4` capture mistake — it was RE-RUN in full with file capture
(53m57s, `Ran 691 tests`, `OK`, rc=0); only the captured run is
claimed. (b) Commit `e03b8d0` (council fold) landed AFTER that
discover; its delta is covered by 35/35 on the changed module plus the
fast tier in its own hook, and the pre-push full-coverage gauntlet
re-proves the whole suite at push — the ship gate, not the mid-sprint
discover, is the binding full-suite proof. (c) `e03b8d0` shows -12
lines; all twelve are v20-added checker/docstring lines from
`daed539`, not banked bytes (bar 6's region diff is the proof).

## Detection power, restated against the LANDED diffs

- **What pre-commit proves now:** `bin/fast_gate.py` derives fast =
  ALL `tests/test_*.py` minus the 9 pinned SLOW modules → 13 modules
  today, 299+ tests, every live-pin surface — proven live when the
  manual run caught the `0ff0ba0` content hop red before activation.
  Its rc gates the hook hard (gauntlet custom-runner path: any nonzero
  = stage fail).
- **What pre-commit no longer proves:** the 9 determinism-re-proof
  modules (banked v9–v12 artifact re-derivations). Every one still
  hard-gates EVERY push through the byte-identical `full_command`
  under coverage with `fail_under=80` — surface delay bounded by
  commits-per-push, re-measured in v21+ (carried duty).
- **Tier-rot tripwires as landed:** `stale-slow-entry` (SLOW name
  missing on disk), `empty-fast-tier`, `zero-tests`/`unparsed-output`
  (a hollow module cannot pass silently; on this venv Python 3.12
  already rc=5s it), `budget-exceeded` at 600s (measured tier 190.4s
  live; the pre-registered reasoning: noise band tops ~197s, a
  smuggled corner-class module ~892–927s or mid-size determinism suite
  ~+500–600s both trip; at 900 the mid-size class would not).
- **Register law as landed + hardened:** a silent flip reds the suite
  (`missing-ratification-block`); a reworded or duplicated header
  fail-closes (`missing-current-answer-line` /
  `multiple-current-answer-lines`); a ratification block must carry
  date + verbatim quote + carrier citation, every cited `done/`
  carrier must exist on disk, and the quoted line must appear
  whitespace-flattened inside a cited existing carrier. Scope stated
  plainly: this is a tripwire against silent/sloppy flips, not a
  semantic adversary-proof — a bad-faith edit that forges carrier
  content is caught by the two-commit law, hub reads, and diffable
  carrier files, not by regex.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call (brief ~10.0KB ≈ 2.6k input tokens inlining the
landed diffs, checker, runner essentials, measured numbers;
`--max-tokens 3500`; response file-redirected, UTF-8; within the 8k
budget). Verdicts: Q1 CONFIRMED (no gate weakened), Q2 header
"REFUTED" contradicted by its own table (no false-PASS found), Q3
"REFUTED" with three claimed bypasses, Q4 one claimed drop + one
distortion, Q5 risk list. Reconciliation, every adverse claim
re-verified against primary bytes:

1. **Q2 `--slow` default (their evidence line) — REFUTED on
   primaries.** The council quoted
   `add_argument("--slow", action="append", default=SLOW_MODULES)` —
   the landed bytes are `default=None` with
   `slow = tuple(args.slow) if args.slow is not None else
   SLOW_MODULES` (exactly the append-to-default trap the council
   assumed). Their conclusion (no false PASS) stands anyway.
2. **Q2 no-timeout hang — non-delta, recorded.** True and true
   before: the old `discover` command had no timeout either; hook-
   and session-level timeouts govern. No delta, no action.
3. **Q3 unicode-hyphen "bypass" — REFUTED on direction.** Substituting
   U+2011 into the flipped answer makes the dormancy substring FAIL →
   the checker DEMANDS a ratification block → red. Fail-closed, not a
   bypass. (Their own analysis of case-games reached the same
   fail-close conclusion.)
4. **Q3 fake-first-header + spoofed block — CONFIRMED kernel,
   ADOPTED.** As landed at `daed539`, a fake "Current answer:
   integration-ready" line placed before the real one, with a
   well-formed block, passed the checker. Folded at `e03b8d0`:
   `multiple-current-answer-lines` fail-closes before the dormancy
   check (so a fake line hides on neither side of the real one);
   fixture probe added.
5. **Q3 empty/unrelated-carrier vouching — CONFIRMED kernel, ADOPTED.**
   Existence-only checking let any on-disk carrier vouch for any
   quote. Folded at `e03b8d0`: the first double-quoted segment must
   appear (whitespace-flattened) in at least one cited existing
   carrier (`ratification-quote-not-in-carrier`); satisfiability
   fixture now carries its own `done/` receipt containing the quote;
   unrelated-content probe added. Residual, stated: an attacker who
   also forges the carrier file itself defeats regexes by
   construction — that is the diffable-artifact layer's job.
6. **Q4 "neither-list rule dropped" — answered, not a drop.**
   Derivation (all-minus-SLOW) makes a neither-list state structurally
   impossible; the v19 council adoption and the v20 spark brief both
   specified exactly this derivation ("new modules default INTO the
   fast tier"). The council itself conceded behavioral equivalence.
7. **Q4 "quote not verified against carrier content" — CONFIRMED as an
   improvement, ADOPTED (same fold as #5).** Precision on the
   promise: the v19 sketch required a quote that "names an existing
   carrier file" — existence was the promised check and was landed;
   content verification goes beyond the promise and was adopted
   because it is cheap and closes #5.
8. **Q5 (risk list) — two answered, one non-delta.** Coverage-at-commit
   gap: pre-existing property of the old config too (pre-commit never
   measured coverage); push measures it — non-delta. Subdir
   reorganization: fails loud via `stale-slow-entry` (their own
   conclusion). `--no-verify`: standing git property, out of scope for
   this change set.

Net: two council-claimed bypass kernels adopted and landed
(`e03b8d0`), one council evidence line refuted on primary bytes, one
directional misread refuted, two claims answered from the banked
record, one non-delta recorded. No adopted item weakened any gate; the
adoptions only ADD failure modes to the checker.

## HFO gate (accuracy vs presentation, separately)

- **Runner CLI output** — accuracy: typed failure lines name the exact
  class and unit (module, path, seconds); the OK line reports
  modules/tests/elapsed/budget from measured values only. PASS.
  Presentation: silent-on-pass single line; failures group tails
  first, typed lines after, critical verdict LAST (inside swarmforge's
  30-line tail window); pluralization normalized ("module(s)"). PASS.
- **Register law text as landed** — accuracy: verbatim v19 brief-2 law
  text; carrier citation names both real files; enforcement pointer
  matches the landed class name; banned-verb scan green (suite-proven,
  `test_banned_verb_scan`). PASS. Presentation: one section, law bold
  and first, carrier and enforcement separated; no ceremony creep into
  row-level law (the exemption sentence is IN the law text). PASS.
- **Verdict (this file)** — accuracy: every number traced to a banked
  file, printed command output, or a named commit; the two capture
  flaws and the post-discover fold are surfaced, not absorbed. PASS.
  Presentation: answer-first, machine table, typed reconciliation.
  PASS.

## Mail and pin status

- Inbox at step 0: root EMPTY (10 receipts in `done/`) → PATH B. No
  arrivals mid-sprint; nothing parked; no polling.
- Outbound: two fire-and-forget content-hop notes to the game-two seat
  (`from-game-two-assets-v20-repin-0ff0ba0.md`,
  `from-game-two-assets-v20-repin-e51e26f.md` — the second records the
  owner-approved `crossed→struck` judgment verbatim).
- Pins at close: `daaddd4` (identity-current at the pre-banking
  checkpoint; upstream ran ~11 commits during this sprint's window
  with two content hops on `creature.rb`, both routed per protocol —
  one approve-by-default, one owner-approved after review).

## Non-claims

No behavioral claim about commits-per-push under the new cadence —
that re-measurement is v21+'s declared duty, data-gated. No coverage
claim about the fast tier (it runs raw by design; coverage lives at
push, unchanged). No register status movement: C6 stays OPEN, doubly
gated; the aggregate-answer law binds a FUTURE flip's form and grants
nothing about its timing. No capture-contract content (the spec has
not arrived; its intake review outranks other work the moment it
does). No integration design. The register's advisory class is
unchanged: the hub decides; this repo records.

## Stop

Sprint 20 stops here: one pre-registration, one inert-then-activated
fast gate (one config line; ship gate byte-frozen and hash-proven),
one register law with hardened mechanical enforcement, one council
reconciliation with two adoptions landed, four protocol re-pins (one
owner-reviewed), this verdict. Carried to v21+: capture-spec intake
(PATH A, first priority on arrival), commits-per-push re-measurement
under the new cadence, the at-speed / viewport / shade / DEF-3 watch
items riding upstream instruments, and the trailing identity re-pin as
game-two moves.
