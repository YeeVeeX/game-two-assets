# Cadence measurement + two decision briefs — v19 pre-registration

**Status: protocol and rubrics FIXED before any timing run and before
either brief exists.** This sprint measures the gauntlet's real cost,
banks the numbers, and prepares two owner decision briefs. It
implements NOTHING: zero edits to hooks, gauntlet config, tests,
tools, the readiness register, pinned modules, or banked artifacts.
The owner decides async; implementation rides a future sprint with its
own pre-registration.

Branch discipline (step 0, recorded): the seat inbox root was EMPTY at
session start (only `done/` present) — the capture-contract tool spec
has NOT arrived, so this session runs PATH B only. If the spec arrives
mid-sprint it is recorded verbatim, md5-stamped, and PARKED in the
verdict; PATH A becomes v20.

Session model: `us.anthropic.claude-fable-5` (verified from
`PI_MODEL`). Step-0 pin state: content hop `fc19b70e → 7aec5170`
routed approve-by-default (`data/display.json` +8/-1; sole deletion a
re-emission-for-extension; 20/20 constants + attack_timing green),
banked `40e7814`, note mailed; asset_gate exit 0 after re-pin.

## Sprint question

Where does the gauntlet's wall-clock actually live (per stage, per
test module, per cost class), how fast is it growing, and which
options honestly reduce latency without weakening ANY hard gate — and
separately, should register-status upgrades require an owner
ratification line (the v18 council Q4 question), answered as a
decision brief, not an edit?

## The hard-gate map (verified from FILES this session; the law both briefs cite)

Verified by reading `.git/hooks/pre-commit`, `.git/hooks/pre-push`,
`swarmforge.toml`, `bin/full_gate.py`, `.coveragerc`, and swarm-forge
`src/swarmforge/{gauntlet,crap,complexity,report,config}.py` — never
from memory:

- **Pre-commit** = `swarmforge gauntlet --changed`:
  1. tests stage = `test_command` = `.venv/Scripts/python.exe -m
     unittest discover -s tests -v` — the FULL raw suite —
     **hard-gates** (any nonzero → `fail` → exit 2; gauntlet.py:
     "Only test failure hard-gates by default").
  2. complexity on git-diffed .py files — **warn-only**
     (`fail_on_cc` absent from swarmforge.toml; default False).
  3. CRAP on git-diffed .py files — **warn-only** (`fail_on_crap`
     absent; default False). Reads `.coverage` left by the LAST
     `--full` run (stale data or "no data" worst-case scoring — a
     loud warn, never a fail).
- **Pre-push** = `git lfs pre-push` (**hard**, exit propagates) +
  `swarmforge gauntlet --full`:
  1. tests stage = `full_command` = `bin/full_gate.py` = `coverage
     erase` → `coverage run -m unittest discover -s tests -v`
     (branch=True, source=tools per `.coveragerc`) → `coverage
     report` with **`fail_under = 80`** — any nonzero return from any
     of the three steps fails the stage → exit 2. **The 80% branch-
     coverage floor on `tools/` is therefore a HARD ship-gate today.**
  2. complexity, repo-wide — warn-only.  3. CRAP, repo-wide, fresh
     `.coverage` — warn-only.

Consequence pre-registered for brief-1 option (ii): "move coverage to
pre-commit, push runs raw" REMOVES the fail_under hard gate from the
ship gate unless the floor is re-proven elsewhere at equal strength —
it must be costed as a gate relocation with a detection-power
argument, and it is NOT recommendable in any form that reduces what
the push-time hard gate proves (Rule 6; spark-brief risk B1).

## Measurement protocol (fixed verbatim; runs AFTER commit 1's hook completes)

Banked anchors (inputs, not re-measured): raw discover (645 tests,
3060 s v17), (668 tests, 3456 s v18); gauntlet suite stage coverage-on
(645, 10733 s), (668, 12311 s) → full-suite multiplier ~3.51x/3.56x;
upstream cadence ~3 commits/hour (re-confirmed this session: 14
commits / 4.47 h = 3.1/h, 1 content hop in 14 commits, p ≈ 0.07).

1. **Run-condition log** (recorded in measurements.json): UTC
   timestamp at block start/end; this repo's HEAD; game-two HEAD at
   block start and end (read-only `git -C`); pin_drift ROUTE line
   before and after the timing block; count of running `python.exe` /
   `ruby.exe` processes at block start (tasklist, MSYS_NO_PATHCONV);
   the box is SHARED (game seat live, other pi sessions possible) —
   noise is named, never smoothed.
2. **No timing while any commit/push hook runs** — enforced by
   sequencing: commit 1 lands and its pre-commit hook completes
   before the timing block opens; no other commit of mine happens
   until the block closes.
3. **Reference run** (doubles as the sprint's verification discover
   run, as the spark brief permits): `time .venv/Scripts/python.exe
   -m unittest discover -s tests` from repo root, timeout ≥ 10800 s.
   Green required (668 tests expected; any live-pin red → route the
   re-pin per protocol, plain re-run). Note: the hooks run discover
   with `-v`; verbosity changes stderr volume only — treated as
   timing-equivalent and stated as an assumption.
4. **Per-module raw timing**: throwaway runner at
   `C:/Users/gabri/AppData/Local/Temp/g2a_v19_module_timer.py`
   (deleted after; deletion shown by `ls`). For each of the 21
   modules under `tests/` (inventory in measurements.json):
   `subprocess.run([".venv/Scripts/python.exe", "-m", "unittest",
   "tests.<module>"], cwd=repo)` wrapped in `time.perf_counter()`;
   record seconds (2 dp), return code, and the "Ran N tests" line
   parsed from output. Command form verified live this session
   (test_motion_tools: 4.0 s, rc 0).
5. **Interpreter-startup correction**: 3 runs of
   `.venv/Scripts/python.exe -c "pass"` timed the same way; mean ×21
   reported next to the sum-vs-reference delta.
6. **Validation**: Σ(per-module) compared to the reference run;
   expected Σ ≥ reference (21 process startups + re-imports); the
   delta is reported, not hidden. If Σ deviates from reference by
   more than ±15% after startup correction, say so and investigate
   before using per-module numbers in the brief.
7. **Stability re-check**: the top-5 slowest modules get a second
   run. Tolerance: per module, |t2−t1| / max(t1,t2) ≤ 0.10. Exceeded
   → one third run, report ALL runs, use the median, name the noise
   in the verdict (never smooth silently).
8. **Coverage-multiplier sample**: the single slowest module, one
   run: `.venv/Scripts/python.exe -m coverage run -m unittest
   tests.<module>` (repo `.coveragerc` in effect) timed identically,
   after `coverage erase`; multiplier = coverage time / raw mean of
   that module. Acceptance band for "consistent with the full-suite
   anchor": 2.5x–4.5x. Outside the band → banked as a finding with
   the module named; the full-suite anchor (3.56x) stays the
   planning number either way. `.coverage` is restored/erased after
   so the working tree carries no measurement residue (`.coverage`
   is untracked; verify with `git status`).
9. **Cost classes** (for the top-10 table): each module classified by
   inspection (grep for Aseprite invocation, `game-two`/`game_root`
   live reads, subprocess use, banked-artifact byte re-derivation):
   `determinism-reproof` (re-renders or re-hashes banked byte
   artifacts), `live-pin` (reads the sibling game repo), `logic`
   (pure fixtures/temp dirs). Mixed modules get the dominant class
   plus a note.
10. **Growth fit**: marginal s/test from the two banked point-pairs
    (raw: 396 s / 23 tests ≈ 17.2; coverage-on: 1578 s / 23 ≈ 68.6);
    linear projection to +5 sprints at the observed ~23 tests/sprint;
    stated as illustrative (two points), with this session's fresh
    668-test reference as the third raw point / same-count variance
    check.
11. **Drift-hop model**: expected content-hops per gate window =
    (upstream commits/hour) × p(content hop per commit) × window
    hours; parameters from observed data (3.1/h; p ≈ 0.07 this
    window, cross-checked against v17's 3 routed hops and v18's 1
    content + 2 identity); each mid-hook content hop costs one full
    plain retry of that window (v17 precedent). Presented as expected
    retry-hours per push as a function of suite length; coarseness
    stated (small-sample p).
12. **Budget**: timing block wall-clock ≤ 3.5 h. Estimated: reference
    ~1.0 h + 21 modules ~1.1 h + top-5 re-runs ~0.6 h + coverage
    sample ~0.25 h + startup runs negligible ≈ 3.0 h. Overrun → stop
    the block at whatever completed, bank what exists, name the cut.
13. **Mid-block upstream drift**: pin_drift after the block (and
    before banking); a content hop that landed DURING the block is
    routed first (gate-clean tree), then any module whose timing run
    overlapped a live-pin red is re-run once for a clean number; the
    dirty number is reported alongside, labeled.

## Decision-brief rubric (both briefs; fixed before writing either)

Every option states, in order: **what changes** / **what is
preserved** / **the detection-power argument** (each hard gate from
the map above traced before/after: what still catches what, where) /
**cost-benefit in measured minutes** (from this sprint's numbers or
the banked anchors, never vibes) / **risks** / **reversal** (one
line). Each brief ends with exactly ONE recommendation (sensei rule —
a recommendation, not a menu). Neither brief edits anything: proposed
wording and shape-test sketches appear as TEXT inside the verdict.

### Brief 1 — gauntlet latency (options fixed)

(i) Status quo + timeout escalation, costed as the do-nothing
baseline including drift-hop compounding; (ii) coverage/CRAP
instrumentation moved to the changed-scope pre-commit stage only,
pre-push runs the raw full suite — carrying the pre-registered
consequence above (fail_under=80 is a push-time HARD gate today;
relocating or weakening it must be argued explicitly and costed;
additionally pre-commit coverage generation would add the ~3.5x
multiplier to EVERY commit, and pre-commit CRAP today reads stale
data by design); (iii) stage partition — ALL tests still run at
pre-push (ship gate byte-identical in what it proves); slow
determinism re-proofs drop only from the pre-commit (changed-scope)
stage, priced with the measured top-10 table; (iv) parallel runner —
isolation analyzed honestly (Windows temp-junction ACL trap, GIT_*
env leakage, live-pin tests hitting ONE shared game repo
concurrently, `.coverage` parallel-combine) with the expectation of
REJECT with reasons.

### Brief 2 — Q4 upgrade ratification (options fixed; carried verbatim from the v18 verdict: "should MET upgrades require an async owner ratification line the way selections do?")

(i) Status quo — two-commit law + 11 shape tests + advisory class +
hub authority — defended or indicted on the v18 track record (the
only upgrade executed under the law so far); (ii) an owner-
ratification line required for any status UPGRADE (proposed register-
law wording + strengthening shape-test sketch, as text; costed
against the family "never gate on peer availability" order and the
register's statuses-follow-carriers law); (iii) ratification scoped
to aggregate-answer changes only (the header's "Current answer"
line). Exactly one recommendation.

## INTEGRITY bars (any red stops the sprint)

1. Measurement protocol pre-registered (this file, commit 1) before
   any timing run.
2. Measurements reproducible: top-5 stability within the stated 10%
   tolerance (or all runs + median + named noise banked).
3. Reference full-discover run green (668 + any step-0 delta; ≥
   10800 s timeout).
4. Both asset_gate runs exit 0 (step 0 — done, post-re-pin — and
   immediately before banking); pin_drift at every drift, routed per
   the owner-extended protocol; re-pins commit ALONE.
5. Five standing `--check`s exit 0 at banking (`track_recompose`,
   `pose_integrity_metrics`, `remedy_metrics`, `adoption_demo`,
   `exports_guard`).
6. ZERO edits to hooks, gauntlet config (`swarmforge.toml`,
   `bin/full_gate.py`, `.coveragerc`), tests, tools, the readiness
   register, pinned modules, banked artifacts/verdicts,
   `docs/selection-register.md`.
7. Zero pixels; zero additions under `exports/`; zero writes into
   `../game-two`.
8. Temp instrumentation deleted after use (the `ls` shown); results
   live only in committed artifacts.
9. New files this sprint ≤ 3 (this rationale, measurements.json,
   verdict.md) plus any protocol re-pins; ambient files untouched;
   staged list verified before every commit.
10. Council: ONE consolidated cross-vendor call, ≤ 8k tokens,
    file-redirected, UTF-8; every REFUTED re-verified against
    primary bytes; reconciliation in the verdict appendix; adoptions
    folded before commit 2.

## QUALITY bars (blocking)

1. HFO pass on both briefs and the verdict — answer-first, options
   tables, ONE recommendation each, measured numbers never vibes;
   accuracy and presentation scored separately.
2. Every option's detection-power argument explicit (each hard gate
   traced before/after).
3. The do-nothing baseline costed honestly, including drift-hop
   compounding.
4. Q4 brief proposes wording only; the register and its shape tests
   stay byte-untouched (bar 6 double-covers this).

## Non-claims

No implementation, no recommendation-by-stealth (an option argued is
not an option taken), no register status movement, no integration
content, no capture-spec content (not arrived), no new permanent
tools (the unpinned class stays at three: exports_guard,
checkout_gate, pin_drift). The briefs are advisory input for an async
owner decision; the owner may reject both recommendations and the
numbers still stand as banked measurement.
