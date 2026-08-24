# Implementation of the two v19-ratified decisions — v20 pre-registration

This file is the fixed contract for the v20 PATH B bundle. It lands
BEFORE the activation commit and the register-law commit; everything
below binds those commits. Committed with it, inert: `bin/fast_gate.py`
and `tests/test_fast_gate.py` (the v18 pattern — banked inert before
wire-up; the gauntlet config is untouched by this commit).

## The ratification of record (program fact, recorded verbatim)

After the v19 close surfaced both recommendations "awaiting async
owner decision," the owner replied, verbatim:

> "Approved, proceed to design the next session spark-up prompt with
> clear directions, guidelines and instructions as you consider
> optimal for maximum quality results (quality over cost), clipboard
> it for me so I can start the fresh new session with focused context
> headroom."

Reading of record: "Approved" ratifies BOTH v19 recommendations —
(1) gauntlet latency, option (iii), the stage partition; (2) Q4
upgrade ratification, option (iii), the aggregate-answer-scoped
ratification law. The owner read the v20 spark brief (which states
this reading) before launching the session — a second confirmation of
the reading. Contradiction check at step 0: the inbox root was empty
(only `done/` receipts); no mail, owner note, or hub evidence
contradicts the reading. Both v19 decision briefs live in
`reviews/cadence-v19/verdict.md`; their option rows carry the
council-adopted duties this implementation must honor (stale-list
rule, budget assertion, behavioral re-measure deferral to v21+).

## Branch record (step 0)

- pin_drift at step 0: identity-only drift `65936ea → ed73ee0`, all
  five pinned blobs byte-identical, constants 20/20, attack_timing
  5/4/8/13 — ROUTE: mechanical re-pin, executed solo as `be0d0bc`
  (its pre-commit hook ran the full old-config suite, ~56 min
  wall-clock: session start ~08:05, commit landed 09:04:20 — a live
  data point for the cost this sprint removes).
- asset_gate step 0: exit 0 (2 WARNINGs: commit-identity drift
  pre-re-pin + a worktree-vs-HEAD note on `creature.rb`, committed
  content matching the pin — the v19-class parallel-seat mid-edit,
  warn-only by design).
- Mail: root EMPTY → the capture-contract tool spec has NOT arrived →
  PATH B. If it arrives mid-sprint it is recorded verbatim,
  md5-stamped, and PARKED in the verdict; PATH A becomes v21.
- Session model `us.anthropic.claude-fable-5` (from `PI_MODEL`).
  Council seat cross-vendor (Kimi K2.5 default), one consolidated
  call, ≤ 8k tokens, file-redirected, UTF-8.

## Decision 1 implementation — stage partition (v19 brief 1, option iii)

### The hard-gate map, re-verified from files this session

- `.git/hooks/pre-commit` = `exec swarmforge gauntlet --changed`
  (sha256 `c8557faf…`); `.git/hooks/pre-push` = git-lfs guard +
  `exec swarmforge gauntlet --full` (sha256 `5997892e…`).
- `swarmforge.toml` today: `test_command` = full raw discover
  (`unittest discover -s tests -v`); `full_command` =
  `bin/full_gate.py` (sha256 `4fefb0c1…`) = coverage erase → coverage
  run full discover → coverage report, with `.coveragerc` (sha256
  `5f38035a…`) `branch=True, source=tools, fail_under=80` — the
  coverage floor is a HARD ship-gate at push.
- swarm-forge `src/swarmforge/gauntlet.py` (editable install — the
  hook executes these bytes): `--full` routes to
  `full_command or test_command`; `--changed` routes to
  `test_command`; the metric stages scope by `changed_py_files(repo)`
  (git-diffed FILES, never executed tests) and are warn-only here.
  Therefore changing `test_command` alone leaves the push path
  byte-untouched.

### The exact change (activation commit; nothing else in it)

`swarmforge.toml`, one line:

- OLD: `test_command = [".venv/Scripts/python.exe", "-m", "unittest", "discover", "-s", "tests", "-v"]`
- NEW: `test_command = [".venv/Scripts/python.exe", "bin/fast_gate.py"]`

`full_command`, `bin/full_gate.py`, `.coveragerc`, and both hook files
are byte-frozen this sprint; the verdict banks hash/diff evidence.
Reversal is this one line back; the runner file is inert without it.

### The runner: `bin/fast_gate.py`

Placed in `bin/` (like `bin/full_gate.py`), NOT `tools/` — verified
from `.coveragerc`: `source = tools` means a runner in `tools/` would
join the measured set and count against the hard 80% branch-coverage
floor at push. In `bin/` it is outside the floor; its fixture tests
exercise it via subprocess/import without coverage-floor effect.

**SLOW list (fixed here, from the v19 banked measurements — the 9
pure determinism-re-proof modules, 2963 s of the 3149 s module sum):**

1. `test_corner_tools`
2. `test_cross_seam_tools`
3. `test_recovery_tools`
4. `test_rise_tools`
5. `test_seam_tools`
6. `test_timeline_tools`
7. `test_track_recompose`
8. `test_transition_tools`
9. `test_turn_tools`

**Fast-tier derivation (the v19 council-adopted rule):** fast tier =
ALL `tests/test_*.py` MINUS the SLOW list, derived by glob at every
run — a NEW test module defaults INTO the fast tier automatically;
there is no allow-list to rot. Today that yields the 12 modules
measured at ~186 s summed (including EVERY live-pin surface:
asset_gate, maturity, exports_guard, audio, adoption).

**Execution model:** one subprocess per fast module —
`<venv python> -m unittest discover -s tests -p "<module>.py" -v`,
serial, cwd = repo root. This preserves today's loader semantics
(discover imports top-level module names exactly as the current hook
does) and matches the v19 measurement conditions (per-module runs;
interpreter startup measured at 0.04 s — 12 startups ≈ 0.5 s, noise).
Serial by design: the v19 brief rejected parallel execution (split-HEAD
live-pin flakes, option iv, REJECTED).

**Failure contract (all typed, all exit nonzero):**

- `stale-slow-entry: <path>` — a SLOW-list entry is missing on disk
  (the v19 stale-list tripwire). Checked BEFORE any test runs;
  derivation failures short-circuit the run.
- `empty-fast-tier` — the derivation found no fast modules (defensive;
  a rotten tests dir must never pass silently).
- `test-failure: <module> (rc=N)` — a module's unittest run exited
  nonzero; the module's output tail is printed above the typed line.
- `zero-tests: <module> (ran 0 tests)` — defensive: fires only if a
  run exits 0 having collected nothing. On this venv (Python 3.12)
  unittest already exits 5 with "NO TESTS RAN", so a hollow module
  surfaces as `test-failure: <module> (rc=5)`; the zero-tests guard
  holds the invariant against future/older unittest semantics where
  an empty run exits 0.
- `unparsed-output: <module>` — the "Ran N tests" line could not be
  parsed from a green run (defensive determinism guard).
- `budget-exceeded: fast tier <X>s > budget <N>s` — wall-clock
  assertion, checked after all modules run.

CLI output law (human-facing, hook-visible): silent-on-pass except ONE
summary line (`fast gate OK: <n> module(s), <n> test(s), <X>s
(budget <N>s)`); on failure, failing-module tails first, then ALL
typed failure lines grouped, then the critical line LAST (`fast gate
FAILED: <n> failure(s)`) — swarmforge tails the last 30 output lines,
so the typed lines and verdict must sit at the end.

**Budget N = 600 s (fixed here, with reasoning):** the fast tier
measured 185.85 s summed (v19 block conditions). Between-session noise
is ±3–6% (v19 banked band) — a high session reads ~197 s; even a
doubled-ambient pathological session reads ~400 s, still under 600.
Logic-sprint growth is ~5–15 s per sprint (v19 per-class rates), so
600 s leaves ~30+ sprints of headroom. Detection power at 600: a
corner-class module smuggled into the fast tier (~892–927 s alone)
trips it outright; a mid-size determinism suite (~500–600 s, the v19
projection for +40 determinism tests) lands the tier at ~690–790 s and
trips it. At N = 900 that mid-size class would pass — 600 is the
tightest bound in the sane band and the reason to prefer it. A budget
breach therefore signals a COMPOSITION change (determinism-class tests
inside fast-tier modules), not session noise. Flags (`--tests-dir`,
`--budget`, `--slow`) exist for fixture tests only; the pinned
swarmforge.toml argv passes none, so production always runs the
defaults.

**What pre-commit proves after activation (stated plainly, from the
v19 brief):** every live-pin surface, all logic tests, all shape
tests, ~3–4 min instead of ~56–65. What it no longer proves at commit:
the 9 determinism-re-proof modules — every one still gates EVERY push
via the byte-identical `full_command` under coverage. A determinism
regression surfaces at push instead of commit, bounded by
commits-per-push (3–6 observed); those modules re-derive banked
v9–v12 artifacts that docs/logic sprints never touch.

### Fixture tests: `tests/test_fast_gate.py` (land inert with this file)

Fixture-proven, never proven on the live config: (1) fast-list
derivation = all-minus-SLOW on a synthetic tree; (2) the live SLOW
list matches this pre-registration's 9 names exactly and every entry
exists on disk (the banked 12/9 split is test-carried; an unilateral
SLOW-list edit goes red); (3) stale SLOW entry → nonzero + typed line;
(4) budget exceed → nonzero on synthetic input (tiny fixture module,
near-zero budget); (5) a failing fast-tier test → nonzero + typed
line; (6) a zero-test (hollow) module → nonzero (typed `test-failure
(rc=5)` on this venv — verified live — with the `zero-tests` guard
fixture-covered at the function level); (7) a passing
synthetic tier → exit 0 + the OK line. All fixture modules are
synthetic temp files; the real 186 s tier is never run inside a test.

### Sequencing law (the v18 inert-first pattern)

1. **Commit 1 (this one):** rationale + `bin/fast_gate.py` +
   `tests/test_fast_gate.py`. Config untouched; the runner gates
   nothing. This commit's own pre-commit hook still runs the OLD full
   config (~56–65 min) — its pass is the last full-suite commit gate
   of the old regime.
2. **Manual pre-activation run (recorded in the verdict):** invoke
   `bin/fast_gate.py` once by hand; expect the OK line at ~186–260 s.
   A green live run is instrument validation, not a failure-mode
   proof; failure modes are fixture-proven only.
3. **Commit 2 (activation):** the one `swarmforge.toml` line, nothing
   else. Its OWN pre-commit hook is the live proof — the printed
   output and wall-clock (minutes, not an hour) are banked in the
   verdict.
4. Reversal: one config line back; the runner file gates nothing
   without it.

## Decision 2 implementation — aggregate-answer law (v19 brief 2, option iii)

### The register edit (one block added; nothing else moves)

`docs/integration-readiness.md` gains ONE section, placed after the
status table and before "Upstream rulings on record". The law text is
copied verbatim from the v19 verdict's decision brief 2 (its
recommendation block); the carrier citation and enforcement pointer
are appended. The "Current answer" line, every status row, every
existing section, and the 11 existing shape tests stay byte-identical.
Exact block to land:

> ## Aggregate-answer law (adopted v20; owner-ratified 2026-08-24)
>
> **Aggregate-answer law.** The header's "Current answer" line may
> drop "NOT" only by a sprint commit whose register edit quotes,
> verbatim and dated, a recorded owner ratification line for that
> specific flip — the quote must cite its carrier file (a `done/`
> mail receipt or `docs/owner-redirects.md` entry) so the line is
> re-checkable against bytes on disk. Row-level status changes stay
> under the two-commit law and require no ratification line.
>
> **Carrier:** `reviews/cadence-v19/verdict.md` (decision brief 2 —
> the law text above is copied verbatim from its recommendation) +
> `reviews/impl-v20/rationale.md` (the owner ratification line of
> 2026-08-24, recorded verbatim there). Mechanical enforcement:
> `tests/test_exports_guard.py` (`AggregateAnswerLaw`) — dormant while
> the header carries "NOT integration-ready"; the negative control
> runs by fixture mutation, never against this file.

Banned-verb compliance checked against the register's own shape law
(no `will`/`schedul*`/`propos*`/`should integrate`; no lore words).
The block adds no `###`-level heading, so the six-condition split and
every carrier-per-condition assertion see an unchanged universe.

### The shape tests (pure ADDITIONS to `tests/test_exports_guard.py`)

A module-level checker plus one new test class appended to the file;
zero edits to existing lines. The checker is a pure function on text —
`check_aggregate_answer_flip(text, repo_root=…, mail_done_dir=…) →
list[str]` — so the negative control mutates a COPY and never touches
the live register.

Checker semantics (mechanical form of the law):

- Locate the bold "Current answer:" line (whitespace-flattened). A
  register with no such line fails typed (`missing-current-answer-line`)
  — a reworded header cannot dodge into silence; the tripwire
  fail-closes.
- If the answer contains "NOT integration-ready" → the law is dormant
  → no failures (vacuously green today; that is the tripwire design,
  the v18 checkout_gate negative-control precedent).
- If the answer has flipped → require an `**Owner ratification:**`
  block containing: a date (`YYYY-MM-DD`), a verbatim quote (a
  double-quoted segment of real length), and a carrier reference that
  resolves to bytes on disk — `done/from-game-two-*.md` (checked
  against the mail done/ dir) or `docs/owner-redirects.md` (checked
  against the repo root). Typed failures name each missing element.

New tests (one class, `AggregateAnswerLaw`):

1. law-presence — the live register carries the law block (heading +
   kernel phrases + the carrier citation).
2. live-dormant — the checker returns no failures on the live
   register today (the vacuously-green tripwire, wired).
3. negative control (fixture mutation) — flip "NOT
   integration-ready" → "integration-ready" on a COPY: the checker
   fires `missing-ratification-block`. Proves a silent flip goes red.
4. satisfiability (fixture) — the same flipped copy PLUS a well-formed
   ratification block citing `docs/owner-redirects.md`: the checker
   returns clean. Proves the law is satisfiable, not a dead end.
5. bogus-carrier (fixture) — a flipped copy whose ratification block
   cites a nonexistent `done/` file against an empty fixture mail dir:
   typed `ratification-carrier-not-on-disk`. Proves the
   bytes-on-disk clause is enforced.

### Sequencing

Register block + shape-test additions land together as commit 3 (the
law and its enforcement are one change); its pre-commit hook runs the
NEW fast config. All shape tests (11 existing + new) green; zero other
register bytes moved (verdict banks the `git diff --stat` and the
byte-identity of the "Current answer" line and status rows).

## Bundle-wide bars (fixed before implementation)

**INTEGRITY (any red stops):** rationale + inert tool committed before
activation; activation commit contains exactly the one config line,
its own hook output banked as proof; runner failure modes
fixture-proven (stale entry, budget, test failure, zero-tests), never
proven on the live config; full discover green after all edits
(≥ 10800 s timeout; 668 + new tests); `full_command`,
`bin/full_gate.py`, `.coveragerc`, both hooks byte-identical (evidence
banked); register "Current answer" line + all status rows + 11
existing shape tests byte-identical, new shape tests green including
the negative control; both asset_gate runs exit 0 (step 0 +
pre-banking); pin_drift at every drift, re-pins solo; five standing
`--check`s exit 0 at banking; zero pixels; zero exports additions;
zero writes into `../game-two`; temp instrumentation deleted (ls
banked); unpinned-tool class = exactly 4 after this sprint
(exports_guard, checkout_gate, pin_drift + fast_gate, declared here);
ambient files untouched; explicit staged paths verified before EVERY
commit.

**QUALITY (blocking):** HFO pass on the verdict, the register law text
as landed, and the runner's CLI output (typed failures,
silent-on-pass, critical line last) — accuracy and presentation scored
separately; every detection-power claim restated against the LANDED
diff; council (one consolidated call, ≤ 8k, Kimi K2.5, five attack
questions per the spark brief) reconciled with adoptions folded before
the bank commit; every REFUTED re-verified against primary bytes.

**Carried duty (v21+, not this sprint):** post-adoption re-measurement
of commits-per-push (v19 brief 1, risk (a) — no data until the
partition has lived a sprint).

**STOP-and-re-ask conditions:** the ratification reading contradicted
by any evidence; the partition requiring more than the one config
line; the shape-test law inexpressible as pure additions; budget N
unjustifiable against the measured noise band.
