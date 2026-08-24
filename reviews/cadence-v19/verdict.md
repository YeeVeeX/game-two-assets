# Cadence measurement + two owner decision briefs — v19 verdict

**Answer first: (1) Gauntlet latency — recommend the stage partition
(option iii): pre-commit drops the nine pure determinism-re-proof
modules and keeps everything else; measured, that cuts the pre-commit
test stage from ~56–65 min to ~3 min while the pre-push ship gate's
command and config stay byte-identical (all 668 tests under coverage,
`fail_under=80`, LFS). (2) Q4 upgrade ratification — recommend
ratification scoped to the aggregate answer only (option iii): the
header's "Current answer" line gets an owner-ratification law; row
upgrades keep the two-commit law.** Both are PROPOSALS for an async
owner decision — this sprint implemented nothing: hooks, gauntlet
config, tests, tools, and the register are byte-untouched, and the
banked numbers stand on their own whatever the owner decides.

This was a PATH B sprint (spark brief, v19): the capture-contract tool
spec had NOT arrived at step 0 (inbox root empty; only `done/`
present) and did not arrive mid-sprint. Zero pixels, zero exports,
zero register edits.

Reviewed artifacts:

- `reviews/cadence-v19/rationale.md` (`9bafded`) — protocol + rubrics,
  committed BEFORE any timing run (the standing two-commit law).
- `reviews/cadence-v19/measurements.json` — every number cited here.
- The hard-gate map — verified from the FILES this session
  (`.git/hooks/*`, `swarmforge.toml`, `bin/full_gate.py`,
  `.coveragerc`, swarm-forge `gauntlet/crap/complexity/report/config`
  sources), never from memory.
- Session model `us.anthropic.claude-fable-5` (verified from
  `PI_MODEL`). Council seat cross-vendor (Kimi K2.5), one consolidated
  adversarial call: brief 7,610 bytes (~1.9k tokens) inlining the
  hard-gate map, the key measurements, and both draft recommendations;
  `--max-tokens 3000`; total well under the 8k budget. Response
  file-redirected, read as UTF-8; reconciliation in the appendix.

Sprint question (rationale, fixed first): where does the gauntlet's
wall-clock actually live, how fast is it growing, and which options
honestly reduce latency without weakening ANY hard gate — plus the
carried v18 council Q4: should MET upgrades require an owner
ratification line?

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Protocol pre-registered before any timing run | PASS | `9bafded` landed (with its full pre-commit hook run) before the block opened at 04:27:48Z |
| 2 | Measurements reproducible within tolerance | PASS | top-5 stability: 3/5 within 10% on two runs; 2/5 (turn 10.2%, timeline 10.5%) took the protocol's third run — runs 2–3 agree within 0.6%, medians adopted, noise named (systematic ambient decline, never smoothed) |
| 3 | Reference discover run green | PASS | 668 tests, OK, 3369.01 s (doubles as the verification run per protocol; −2.5% vs the v18 anchor at identical count) |
| 4 | Both asset_gate runs exit 0; pin_drift at every drift | PASS | step 0: drift `fc19b70e→7aec5170` routed approve-by-default (`40e7814`), gate exit 0; mid-sprint hop `7aec5170→473c3d2f` routed with recorded judgment (`33c480d`), gate exit 0; pre-banking: mechanical re-pin to `65936ea`-current HEAD + clean exit-0 re-run (see Mail and pin status) |
| 5 | Five standing `--check`s exit 0 at banking | PASS | `track_recompose`, `pose_integrity_metrics`, `remedy_metrics`, `adoption_demo`, `exports_guard` — run after all v19 edits existed |
| 6 | Zero edits to hooks/gauntlet config/tests/tools/register/pinned modules/banked artifacts | PASS | deliverables are three new files under `reviews/cadence-v19/` + protocol re-pins of one manifest line pair; `git status` and the staged lists prove nothing else moved |
| 7 | Zero pixels; zero `exports/` additions; zero writes into `../game-two` | PASS | exports_guard `--check` exit 0; game-two touched only by read-only `git -C` reads |
| 8 | Temp instrumentation deleted | PASS | `g2a_v19_module_timer.py` + `g2a_v19_timing/` + council brief/response temps removed after banking; deletion `ls` in the close log |
| 9 | ≤ 3 new files; ambient files untouched; staged list verified per commit | PASS | rationale, measurements.json, this verdict; every commit staged explicit paths only |
| 10 | Council: one call, ≤ 8k tokens, REFUTEDs re-verified | PASS | appendix below; the one REFUTED verdict re-verified against this verdict's own text, the two REFUTED-on-primaries council scenarios re-verified against gauntlet.py bytes |

Budget honesty: the timing block ran 3.58 h against the 3.5 h budget
(~5 min over; every protocol phase completed, nothing cut). The
overrun is named here rather than absorbed silently.

## Machine findings (the numbers that drive both briefs)

- **Latency is concentrated, not diffuse.** Top-3 modules = 71.3% of
  summed module time; top-5 = 82.7%; top-10 = 97.7%. The bottom 11
  modules cost 72.8 s TOTAL. The top-9 by class are pure
  determinism-re-proof suites (v9–v12 banked-artifact re-derivation:
  full metric reports rebuilt over the real banked exports, repeatedly
  per test method) at ~12–15 s/test measured across all nine; logic
  modules run at ~0.02–0.5 s/test.
- **The live-pin surfaces are cheap.** Every module that reads the
  sibling game repo (asset_gate 3.7 s, maturity 4.1 s, exports_guard
  0.4 s, audio 20.2 s, adoption 113.0 s) sits outside the top-4. The
  class that catches mid-sprint drift costs ~2–4% of the suite; the
  class that costs 82%+ of the suite (determinism re-proofs) has
  nothing to do with drift.
- **The coverage multiplier is real and stable — at suite scale.**
  Sampled on the slowest module: 3154.92 s under coverage vs 892.36 s
  raw mean = 3.536x, inside the pre-registered 2.5–4.5 band and
  matching the full-suite anchors (v17 3.508x, v18 3.562x). Scope
  (council-sharpened): the multiplier is asserted for the sampled
  module and the two full-suite anchors only — never per-module.
- **The banked "growth trend" is partly noise.** v18 added 23 tests
  whose module runs in 4.13 s, yet the raw anchor grew +396 s — this
  session re-measured the same 668 tests at 3369 s, BELOW the v18
  anchor (3456 s). Between-session variance is ±3–6%; every
  cross-session cost in these briefs is therefore quoted as a RANGE
  spanning that band (e.g., "commits ~56–65 min"), and the honest
  growth model is composition-based (which CLASS of tests a sprint
  adds), not a constant per test. The per-class rates are direct
  measurements from this session; the forward projection (a
  determinism-suite sprint adds ~500–600 s raw / ~1800–2100 s at push)
  assumes future determinism sprints resemble the nine banked ones —
  stated, not hidden. At the midpoint the 21600 s push timeout is
  crossed on the ~5th determinism sprint (range 4–6); docs/logic
  sprints never cross it at current scale.
- **The sum-vs-reference anomaly is named, bounded, and load-bearing
  for nothing.** Σ(modules) = 3149.2 s vs reference 3369.0 s (−6.5%),
  where the measured interpreter-startup correction (21 × 0.04 s =
  0.85 s) is a LOWER bound (it excludes per-module import cost, which
  would push the expected sign further positive) — so the negative
  delta is entirely ambient variance, attributed (not proven) to load
  decline across the block; the same systematic decline shows in every
  top-5 run-2. No conclusion rests on the point values: within-block
  comparisons (concentration, fast-tier sums) share conditions, and
  cross-session claims use the noise-band ranges above.
- **Drift-hop compounding is measured, not hypothetical.** The
  UPSTREAM seat (game-two — the only drift source; this repo's own
  commits move no pin) ran 3.12 commits/active-hour across the
  observed window; 2 of 27 commits touched a pinned file (p ≈ 0.074).
  Expected mid-hook content hops: ~0.25 per pre-commit window
  (1.09 h), ~0.79 per pre-push window (3.4 h) during active seat hours
  (bursty: overnight and the whole timing block = 0). Observed live
  this sprint (n=1, quoted as the worked example, not a distribution):
  commit 1's first hook FAILED at 3917 s on exactly this (2 live-pin
  reds), costing a solo re-pin commit (own full hook) plus a full
  retry — ~+2.2 h on a ~1.1 h commit.
- **Hook suite runs observed this session:** 3917 s (failed, drifted,
  morning ambient load) and 3369 s (timed reference) bracket the
  observed range; three passing hook runs were not separately timed.
  Pre-commit hard-gates all 668 tests on every commit today.

## Decision brief 1 — gauntlet latency (owner decision, async)

The hard-gate map today, verified from files: pre-commit hard-gates
the FULL raw suite (~56–65 min) with warn-only metrics on changed
files; pre-push hard-gates LFS + the full suite under coverage
(~3.4 h) INCLUDING the `fail_under = 80` tools/ branch-coverage floor,
with warn-only metrics repo-wide. Everything below is traced against
that map. Two structural facts the tracing relies on (verified in
`gauntlet.py`): the metric stages scope by CHANGED FILES, never by
which tests executed — so no test-stage option below changes what
complexity/CRAP analyze; and LFS lives only in the push path today —
no option adds or removes a commit-stage LFS check.

| Option | What changes | What is preserved | Detection power | Cost-benefit (measured) | Risks | Reversal |
|---|---|---|---|---|---|---|
| (i) Status quo + timeout escalation | Nothing but timeout numbers | Everything | Unchanged | Commits ~56–65 min each (~6/sprint ≈ 6 h); push 3.4 h; +2.2 h per mid-hook content hop at 0.25–0.79 expected/window (active hours); timeouts must grow past 21600 s around the ~5th future determinism sprint (range 4–6) | The cost is paid every sprint forever; longer windows catch MORE hops (compounding); docs sprints pay the full 668-test tax per one-line commit | n/a |
| (ii) Coverage/CRAP to pre-commit only; push runs raw | Push loses instrumentation; commits gain it | NOT the ship gate | **Fails Rule 6: `fail_under=80` hard-gates at push TODAY (verified: `bin/full_gate.py` chains `coverage report` nonzero into stage failure). Removing coverage from push removes a hard gate.** | Also self-defeating: fresh CRAP data at pre-commit requires generating coverage per commit → 56 min × 3.54 ≈ 3.3 h PER COMMIT — strictly worse than today | Gate downgrade + latency regression in one move | n/a — not proposable |
| (iii) Stage partition: pre-commit drops the 9 pure determinism-re-proof modules | `swarmforge.toml` `test_command` points at a fast-tier runner (config line + one small runner script, future sprint); hooks byte-untouched | Pre-push command and config BYTE-IDENTICAL: all 668 under coverage + `fail_under` + LFS. Pre-commit still hard-gates every live-pin surface, all logic tests, all shape tests; its metric stages are unchanged (file-scoped, see above). What pre-commit's TEST stage proves is less — that reduction is exactly the option, stated plainly | Every dropped test still gates every push (nothing leaves the machine unproven). Window lost: a determinism-re-proof regression surfaces at push instead of commit — bounded by commits-per-push (3–6 observed), and those 9 modules re-derive BANKED v9–v12 artifacts that docs sprints never touch; any tools/*.py edit still gets file-scoped warn-metrics at commit + full proof at push | Pre-commit test stage 3149 s → **186 s** (measured module sums: keeps 12 modules incl. every live-pin surface; drops 2963 s of re-proofs). ~18–20x faster commits; mid-hook hop expectation drops 0.25 → ~0.02 per commit window (the 3.3 h commit-1 saga this session becomes ~10 min) | (a) Behavioral response: cheaper commits may RAISE commits-per-push, widening the push-time exposure window — the implementing sprint re-measures it after adoption; (b) push-time re-proof failure needs module-scoped bisect over the batch (each bisect step ~15 min on the slowest module, never a full suite); (c) tier rot: intra-module additions could smuggle slow tests into fast-tier modules — countered by a runner that FAILS if any `tests/test_*.py` is in neither list AND a fast-tier wall-clock budget assertion (fail loudly past N min) | One config line back (the dead runner file deleted or left inert — it gates nothing by itself) |
| (iv) Parallel runner | Test execution model | Gate semantics (in principle) | Same tests, BUT: live-pin tests reading ONE shared `../game-two` concurrently can split-HEAD within a single run (worker A green at old HEAD, worker B red at new — nondeterministic flakes in the blocking class; today's serial runs read the pin once-ish and stay coherent, and option (iii)'s fast tier stays serial too); Windows temp-junction ACL trap (hit live on this box, global memory 2026-08-15); GIT_* env leakage into nested test git repos (hit live, project memory 2026-08-17); `.coverage` needs parallel+combine through `bin/full_gate.py` | Amdahl floor: corner_tools alone is 892 s median → best-case wall ~15 min regardless of workers; unittest has no native parallel runner → a NEW permanent harness (4th unpinned-class member) for a bounded win | Verdict-integrity risk in the ship gate itself; new tooling against the bias-toward-subtraction law | REJECTED — reasons banked here |

**Recommendation (one): option (iii), stage partition.** The numbers:
pre-commit test stage 3149 s → 186 s measured, pre-push gate
byte-identical in command and config, drift-hop exposure cut ~12x,
zero hook edits, one-line reversal. Implementation rides a future
sprint with its own pre-registration, which must fix: the fast-tier
module list (the 12/9 split above), the neither-list failure rule, the
fast-tier budget assertion, and a post-adoption re-measurement of
commits-per-push (risk (a)). If the owner prefers do-nothing: option
(i) is honestly survivable for ~4–6 more determinism sprints of
timeout escalation — the cost is ~6 h of hook time per sprint plus one
~2.2 h drift retry every few windows, paid forever.

## Decision brief 2 — Q4 upgrade ratification (owner decision, async)

Carried verbatim from the v18 verdict (council Q4, CONFIRMED there as
a real structural question): "should MET upgrades require an async
owner ratification line the way selections do?"

| Option | What changes | What is preserved | Detection power | Cost | Risks | Reversal |
|---|---|---|---|---|---|---|
| (i) Status quo | Nothing | Two-commit law + 11 shape tests + advisory class + hub authority | v18 track record: the one upgrade executed under the law held (carrier-cited, shape tests green, council-reviewed, hub reads the verdict); but no owner sign-off is RECORDED anywhere on a status flip | Zero | A future sprint marks a row MET on a thin-but-cited carrier and the hub skims past it; the register's authority quietly becomes the sprint's authority | n/a |
| (ii) Owner ratification for ANY upgrade | Every C1–C6 row flip waits for an owner line | Row law otherwise | Adds a recorded human check per flip — but upgrades already ride sprint commits + shape tests + council + hub-read verdicts; the marginal catch is small | Collides with the standing order "never gate on peer availability" (owner order 2026-08-22; solo progress is the default): an absent owner makes the register STALE relative to its carriers, violating its own statuses-follow-carriers law; v18's C3 flip would have stalled in limbo | Ceremony that ages into a bypass habit | Strike the law line |
| (iii) Ratification scoped to the aggregate "Current answer" line | ONLY the header flip (NOT-integration-ready → integration-ready) requires a quoted, dated owner ratification line; C1–C6 row flips keep the two-commit law | Everything else | The aggregate line is the only sentence with integration consequence, and while C6's own gates are already owner/hub decisions, nothing today binds the REGISTER EDIT to those decision records — this law makes the flip commit quote its authority, exactly where mistake cost is maximal and frequency is minimal (≤ once per program phase) | ~Zero cadence cost (C1–C5 maintenance stays solo-progress); one extra quoted line at the single rarest, highest-stakes edit. The owner-availability objection collapses here: the flip cannot precede the hub's parking-lot lift, which is itself an owner/hub act — the ratification line waits on a decision that must already exist | Adds a law that fires once — must not creep into row-level ceremony (the wording below scopes it explicitly) | Strike the law line |

**Recommendation (one): option (iii).** Proposed register-law wording
(TEXT ONLY — the register is untouched this sprint; a future
register-touching sprint adopts or rejects it). Ratification format
specified (council-sharpened) so the law is mechanical, not vibes:

> **Aggregate-answer law.** The header's "Current answer" line may
> drop "NOT" only by a sprint commit whose register edit quotes,
> verbatim and dated, a recorded owner ratification line for that
> specific flip — the quote must cite its carrier file (a `done/`
> mail receipt or `docs/owner-redirects.md` entry) so the line is
> re-checkable against bytes on disk. Row-level status changes stay
> under the two-commit law and require no ratification line.

Strengthening shape-test sketch (TEXT ONLY): a
`ReadinessRegisterShape` case asserting that if the header's "Current
answer" line lacks "NOT integration-ready", the register must contain
an `Owner ratification:` block whose quote names an existing carrier
file. Until the flip is attempted the case is vacuously green — that
is not theater, it is a tripwire: it is mechanically testable TODAY
(mutate the header in a fixture copy and the assertion fires — the
same negative-control pattern checkout_gate banked in v18), and it
converts a future silent flip into a red suite.

## Run-condition log (summary; full detail in measurements.json)

Shared box; block 2026-08-24T04:27:48Z → 08:02:43Z (3.58 h); repo
`9bafded`; game-two `65936ea` at start AND end (0 upstream commits
during the block; identity-only drift pending, re-pinned at the
pre-banking checkpoint per protocol); 0 competing python/ruby
processes at both checks; no hook ran during any timing; systematic
ambient-load decline across the block named in the stability rows;
`.coverage` backed up/restored around the coverage sample.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call, five questions. Returned: **Q1 split (option-ii
bar CONFIRMED; option-iii wording UNCERTAIN; "hidden LFS gate"
CONFIRMED), Q2 mixed (growth-fit rejection CONFIRMED; multiplier
scope CONFIRMED; ambient/startup UNCERTAIN; one REFUTED), Q3
UNCERTAIN, Q4 UNCERTAIN×3 + two CONFIRMED omissions, Q5 five candidate
risks.** Per the v12–v18 precedent every adverse verdict was
re-verified against primary bytes; the reconciliation:

1. **Q1 option-iii "byte-identical" (UNCERTAIN) — the core scenario is
   REFUTED on primary bytes; the wording kernel is ADOPTED.** The
   council: dropping 9 modules from pre-commit means "no
   complexity/CRAP warnings on them at commit... never fires until
   push." Primary: `gauntlet.py` scopes the metric stages by
   `changed_py_files(repo)` — git-diffed FILES, never executed tests —
   so the metric stages are IDENTICAL under option (iii); editing
   `test_corner_tools.py` still gets complexity+CRAP at commit whether
   or not its tests ran. ADOPTED (wording): the option row now scopes
   the claim precisely — the pre-PUSH command/config are
   byte-identical; pre-COMMIT's test stage proves less (that reduction
   IS the option, stated plainly); metric stages unchanged.
2. **Q1 "hidden LFS gate" (CONFIRMED) — partially refuted; the tracing
   duty is ADOPTED.** The council: "LFS content verification also
   shifts exposure... no commit-stage counterpart" under (iii).
   Primary: the hooks show LFS lives ONLY in the push path TODAY —
   there is no commit-stage LFS check for any option to remove, so
   nothing shifts. ADOPTED: the brief now states the LFS trace
   explicitly (the two structural facts above the options table)
   instead of leaving it implicit.
3. **Q2 −6.5% "double-use" (REFUTED, council's only REFUTED) —
   re-verified and RESOLVED as ranges.** The charge: the anomaly is
   used both to reject linear growth and as a valid costing anchor.
   Re-verification against this verdict's own text: every
   cross-session cost is quoted as a RANGE spanning the ±3–6% noise
   band (commits "56–65 min"; hook runs "3917 s and 3369 s bracket the
   range"), while within-block comparisons share conditions — the
   anomaly is load-bearing for nothing. ADOPTED: that scoping is now
   an explicit machine-findings bullet instead of an implicit
   practice.
4. **Q2 startup correction (UNCERTAIN) — ADOPTED as a lower-bound
   statement that STRENGTHENS the finding.** The council: 0.04 s
   uniform startup is unverified against per-module import cost.
   Correct — and import cost pushes the expected sum-vs-reference sign
   further POSITIVE, making the observed negative delta more clearly
   ambient, not less. The verdict now says "lower bound" explicitly.
   The ambient attribution itself stays labeled attributed-not-proven
   (the protocol's honesty rule, pre-registered).
5. **Q2 multiplier representativeness (CONFIRMED) — already
   pre-registered as a scope limit; wording tightened.** The
   multiplier is asserted for the sampled module + the two full-suite
   anchors, never per-module; option (iii) makes no coverage claim
   about the fast tier (pre-commit stays raw).
6. **Q3 (integrity vs ceremony, UNCERTAIN: "unfalsifiable...
   unspecified format... same availability collision, narrower
   scope") — ADOPTED as three sharpenings.** (a) The ratification
   format is now specified in the proposed wording (dated verbatim
   quote citing a carrier FILE, re-checkable against bytes); (b) the
   redundancy question is answered in the option row: C6's gates are
   owner/hub decisions, but nothing today binds the REGISTER EDIT to
   those decision records — the law binds the edit to its authority;
   (c) the availability collision is answered: the flip cannot precede
   the hub's parking-lot lift (itself an owner/hub act), so the
   ratification line waits on a decision that must already exist —
   unlike option (ii), which gates routine maintenance. The
   "vacuously green = theater" charge is answered with the
   negative-control pattern: the assertion is testable today by
   fixture mutation, the v18 checkout_gate precedent.
7. **Q4 (drift-hop model, UNCERTAIN×3) — parameters clarified, n=1
   labeled.** The 3.12/h rate is the UPSTREAM seat's arrival rate (the
   only drift source — this repo's commits move no pin); now stated.
   The +2.2 h recovery cost is one live observation, now labeled n=1
   worked-example. The ~4–5-sprint survivability now reads "~5th
   sprint (range 4–6)" per the council's own arithmetic check — same
   conclusion, honester error bars.
8. **Q4 omissions (CONFIRMED×2) — one ADOPTED into the option row, one
   recorded as a non-delta.** (a) Behavioral response (cheaper commits
   → more commits-per-push → wider exposure window) is now option
   (iii) risk (a) with a post-adoption re-measurement duty. (b)
   Coverage freshness at pre-commit: CRAP reads stale `.coverage`
   today AND under every option — a real property, zero delta between
   options; recorded here so nobody mistakes it for an option-(iii)
   cost.
9. **Q5 (five candidate risks) — two ADOPTED, three answered.**
   ADOPTED: tier-rot via intra-module additions (fast-tier budget
   assertion added to option (iii)'s implementing-sprint contract,
   alongside the neither-list failure rule the draft already carried);
   push-batch bisectability (costed: module-scoped bisect ~15 min per
   step, never a full suite). Answered: the register/C6 interaction
   rests on a misread (C6 validation is not commit-stage and no
   register dependency maps to test modules); fast-tier live-pin
   concurrency does not exist (the tier stays serial, as today — the
   council's own aside concedes it); "one-line reversal" now names the
   dead runner file explicitly (config line back; the inert script
   gates nothing).

Net: two REFUTED-on-primaries council scenarios documented against
`gauntlet.py` bytes (metric-stage scoping; commit-stage LFS), one
REFUTED-of-mine resolved as explicit range-scoping, six wording/scope
adoptions folded (option-iii claim precision, LFS trace, lower-bound
startup, n=1 label, sprint-range error bars, multiplier scope), three
substantive adoptions into the briefs (ratification format +
redundancy/availability answers; behavioral-response risk +
re-measurement duty; tier-rot budget assertion + bisect costing).
Neither RECOMMENDATION moved: the council confirmed option (ii)'s bar
and rejected nothing about options (iii)/(iii); no verdict challenged
the measured numbers themselves.

## Non-claims

No implementation: hooks, `swarmforge.toml`, `bin/full_gate.py`,
`.coveragerc`, tests, tools, and the readiness register are
byte-identical to v18 close (nothing moved but the manifest re-pin
line pairs). No recommendation-by-stealth: both recommendations await
an async owner decision and bind nothing until a future sprint
pre-registers the chosen one. No register status movement; C6 stays
OPEN, doubly gated; the register's Q4 row is not edited by this brief
ABOUT it. No capture-spec content (it did not arrive; nothing parked).
No new permanent tools — the unpinned class stays at three; the
fast-tier runner, if adopted, is the implementing sprint's declared
addition under its own pre-registration. Zero pixels, zero exports,
mechanical ids throughout.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: root EMPTY (5 historical receipts in `done/`) → the
  branch observable resolved to PATH B. Nothing arrived mid-sprint; no
  reply owed; no polling done.
- Outbound: two fire-and-forget content-hop notes to the game-two seat
  (`40e7814` / 7aec5170 and `33c480d` / 473c3d2f — the second records
  the intermediate-hop-churn judgment verbatim). No reply expected.
- Pins: step-0 content hop routed (`40e7814`); mid-sprint content hop
  routed with recorded judgment (`33c480d`, the +4/-6 hop whose
  deletions were intermediate-window churn — cumulative diff from the
  banked baseline +6/-1 additive); identity-only drift re-pinned
  mechanically at the pre-banking checkpoint; final gate exit 0, no
  warning, before commit 2.

## Stop

Sprint 19 stops here: one pre-registration, one measured cadence
corpus (banked JSON), two owner decision briefs with one
recommendation each, council reconciled with adoptions folded,
protocol re-pins, this verdict. Zero pixels; zero exports; nothing
pinned touched; no register row moved. Carried to v20+: the
capture-contract tool spec intake (PATH A becomes v20 the moment it
lands), both owner decisions (latency option iii; Q4 option iii)
awaiting async ratification, the at-speed + viewport + shade + DEF-3
watch items riding upstream instruments, and the trailing identity
re-pin as game-two moves.
