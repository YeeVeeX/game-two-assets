# Post-adoption cadence re-measurement — v21 rationale (pre-registered)

Commit 1 of the two-commit law: this file fixes the questions, data
sources, labeling rules, and pass bars BEFORE any measurement is
banked. The measurement corpus (`measurements.json`) and verdict land
in commit 2 only.

Context: v20 landed both v19-ratified decisions — the stage partition
is ACTIVE (`ac40ce0`, pre-commit runs `bin/fast_gate.py`, ~3 min) and
the pre-push ship gate is byte-frozen (full coverage gauntlet,
`fail_under=80`, ~3.1–3.4 h at 693 tests). This sprint executes the
v19-declared post-adoption duty (brief 1, option iii, risk (a)): the
commits-per-push re-measurement, deferred until the partition had
lived a sprint. It now has — exactly one.

Branch observable at step 0: the capture-contract tool spec was NOT
in the inbox (one unrelated fire-and-forget drift note received,
absorbed at step 0, archived to `done/`) → PATH B. Zero pixels, zero
exports, docs-only, ≤ 3 new files, SMALL BY DESIGN (~half a session).

## The four questions (fixed verbatim; answered only as labeled)

- **(a) Commits-per-push, before vs after activation.** Prior band
  3–6 observed v17–v19 (re-derived this session from git primaries,
  not quoted from memory); v20 = 9 (TRANSITIONAL, see rule 1); v21's
  own window = the FIRST clean post-adoption point.
- **(b) Fast-hook wall-clock distribution vs the 600 s budget**
  (headroom trend). Inherited points: v20 observed 181/176/186/172/
  173/174 s hook reals + one 190.4 s manual tier-OK run + one 2m53s
  drift-red. New points: every v21 commit's `time` real (the step-0
  re-pin already banked one live at 2m39.952s, printed before this
  file was written).
- **(c) Push-window cost at 693 tests vs anchors.** Anchors: v17
  10733 s @ 645 (suite stage, coverage-on), v18 12311 s @ 668 (suite
  stage, coverage-on), v20 186m45s @ 693 (TOTAL pre-push hook). The
  anchors measure DIFFERENT SPANS (suite-stage vs total-hook);
  reconcile spans explicitly before any comparison (rule 4), carry
  the ±3–6 % noise band (rule 3). v21's own push adds one point,
  span-labeled from the hook's printed stage output where available.
- **(d) The v19 risk-(a) question restated.** Did cheaper commits
  raise commits-per-push, and what does the answer do to push-time
  bisect exposure? Exposure model banked at v19: module-scoped bisect
  ~15 min/step, never a full suite; steps ≈ ceil(log2(N commits)).

## Data sources (named; mechanical mining only)

1. Git primaries: `git rev-list --count` + `git log` timestamps
   between banked sprint-close commits — v16 `bb52ff7` → v17
   `ec0e534` → v18 `bc6e603` → v19 `54bd639` → v20 `b4765ba` → v21's
   own close. Push points = sprint closes per the banked verdicts
   (each verdict records its push; v20's window verified as
   `54bd639..b4765ba` = 9 commits). The local reflog of `origin/main`
   is checked as a corroborating push record; if it does not carry
   push events, the verdict-push-point model stands and is named as
   an assumption.
2. Banked wall-clocks: `reviews/cadence-v19/measurements.json`
   (anchors, noise band, drift-hop model, bisect costing),
   `reviews/impl-v20/verdict.md` (hook table, 186m45s push, budget
   reasoning), the v20/v21 spark briefs' recorded reals.
3. This session's own `time` output on every commit and on the push,
   plus hook-printed stage lines where the gauntlet emits them.
4. NO new instrumentation, NO new tools (unpinned census stays 4). A
   question that turns out to need instrumentation gets the banked
   answer "out of scope, bank the question for the owner."

## Labeling rules (pre-registered; violations are QUALITY reds)

1. **v20-transitional rule.** v20's 9-commit window contains the
   activation itself: 3 commits under the old config (two ~50 min
   hooks) + 6 under the new. It is labeled TRANSITIONAL everywhere it
   appears and is never pooled into a pre- or post-adoption band.
2. **n-labeling rule.** Every claim carries its n and names its
   window(s). n=1 claims are worked examples, never trends;
   "insufficient windows, re-ask at v23+" is a VALID banked answer;
   no extrapolation from n=1.
3. **Noise band.** ±3–6 % (banked v19) is carried on every
   cross-session comparison; within-session comparisons share
   conditions and say so.
4. **Span reconciliation.** Suite-stage and total-hook numbers are
   never compared as equals. Every (c) comparison names each side's
   span; where spans differ, only bounded/directional statements are
   licensed (total-hook ≥ suite-stage).

## INTEGRITY bars (any red stops the sprint)

1. This pre-registration committed before any measurement is banked.
2. `reviews/cadence-v19/*` and `reviews/impl-v20/*` byte-untouched.
3. Zero new tools; unpinned census = 4 at close (exports_guard,
   checkout_gate, pin_drift, fast_gate).
4. One full discover green, CAPTURED to a file (≥ 10800 s timeout;
   judged by `grep "^Ran |^OK|^FAILED"`, never `| tail`/`$?`).
5. Both asset_gate runs exit 0 (step 0 + pre-banking).
6. Five standing `--check`s exit 0 at banking (track_recompose,
   pose_integrity_metrics, remedy_metrics, adoption_demo,
   exports_guard).
7. pin_drift at every drift; re-pins solo per protocol.
8. Zero pixels; zero exports additions; zero writes into
   `../game-two`; zero register edits; hooks + `bin/full_gate.py` +
   `.coveragerc` + `swarmforge.toml` byte-frozen.
9. Temp files deleted (deletion `ls` in the close log); ambient files
   untouched; explicit staged paths verified before every commit.
10. ≤ 3 new files (this file, `measurements.json`, `verdict.md`).

## QUALITY bars (blocking)

- HFO pass on the verdict — accuracy and presentation scored
  separately.
- Every claim n-labeled with its window named (rule 2).
- Council (one call, ≤ 8k tokens, alias `kimi`, file-redirected,
  UTF-8): attack the methodology — window definitions, span
  reconciliation in (c), transitional-window handling, whether ANY
  conclusion is licensed at this n, biggest unthought risk. Every
  REFUTED re-verified against primary bytes; adoptions folded before
  the bank commit.

## Budget and stop

Half a session; one council call ≤ 8k; ≤ 3 new files + protocol
re-pins; push timeout ≥ 21600 s, judged by the printed ref-update
line. Stop after the bank commit and push. A spec arriving mid-sprint
is recorded verbatim, md5-stamped, PARKED (PATH A becomes v22).
