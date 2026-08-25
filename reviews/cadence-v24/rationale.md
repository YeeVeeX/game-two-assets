# Post-adoption cadence corpus — v24 pre-registration (rationale)

Status: PATH B (the capture-contract tool spec was NOT in the inbox at
step 0 — root empty). This file is commit 1 of 2 and lands BEFORE any
measurement is banked; `measurements.json` + `verdict.md` land at
commit 2. Questions, sources, and labeling rules below are FIXED at
this commit; any mid-flight deviation is a new pre-registered addendum
committed before use, never a silent edit.

Trigger: the v21 verdict re-armed questions (a) and (d) for ">= 3
clean post-adoption windows". That bar is MET — three completed clean
windows exist (v21 / v22 / v23; sizes re-derived mechanically this
session from reflog + rev-list, expected 4/1/1). This sprint runs the
corpus. Scope: mechanical mining ONLY (git primaries, the brief-carried
chain numbers, banked corpora, this session's own `time` outputs);
zero new tools, zero instrumentation, zero pixels, zero exports, zero
register movement.

## The four questions (wording fixed)

- **(a) Commits-per-push, post-adoption vs pre-adoption.** Raw band
  across the n=3 completed clean post-adoption windows (expect 1–4)
  vs the banked pre-adoption raw band 1–6 (n=4, v17–v19 era, banked
  in `reviews/cadence-v21/measurements.json`). v20 = 9 is
  TRANSITIONAL and never pooled. Sensitivity treatments named:
  (i) raw band, every window counted (headline, per the banked
  outlier law); (ii) sprint-bearing-only view (pre-adoption 5–6 n=3;
  all three post-adoption windows are sprint-bearing — the view is
  labeled, not a substitute headline); (iii) with/without v24's own
  at-bank window (provisional 4th point, v21 `commits_at_bank`
  precedent).
- **(b) Fast-hook headroom vs the 600 s budget.** Inherited green
  hook-real distribution n=12 points, 160–197.6 s, across 4 sessions
  (v20 n=6, v21 n=4, v22 n=1, v23 n=1 — the v21 bank real and the
  v22/v23 points arrive via the chain numbers below) + this sprint's
  own accruals (the step-0 re-pin hook real, already observed at
  3m29.102s = 209.1 s green BEFORE this commit — observed is not
  banked; it banks at commit 2, named transparently, the v21
  `53f08c1` precedent — plus this commit's own real and any
  mid-sprint re-pin reals). Observed-points-only wording; no trend
  licensed; green-only construction named with any red reported
  alongside.
- **(c) Push-window cost at 693 tests.** Span-reconcile the four
  TOTAL-HOOK points at 693: banked v20 11205 s + the three
  chain-carried points (v21 10722.7 s, v22 10448.3 s, v23 12873.5 s).
  The v23 high point folds into the raw band per the banked outlier
  law — labeled, never excluded; its parallel-seat machine-load
  confound is NAMED as non-measured; no cause claim, no trend claim.
  One-sided-bound honesty: every carrier is total-hook, so only
  suite-stage <= total-hook bounds are licensed vs the v17/v18
  suite-stage anchors (cross-span claims bounded/directional only).
  Re-read observed timeout headroom at the worst point vs 21600 s.
- **(d) Bisect exposure + the behavioral question.** Module-scoped
  bisect arithmetic (~15 min/step, steps ~= ceil(log2(N)), banked
  v19) at the observed post-adoption window sizes (N in {1, 4}; N=1
  needs 0 bisect steps — the single commit is the culprit). Then the
  re-armed behavioral question: did cheaper commits RAISE
  commits-per-push? Answered from the n=3 completed windows with the
  scope confound stated as dominant; the honest answer may be
  bounded or INSUFFICIENT — bank exactly what the n licenses.

## Sources (fixed)

1. `git reflog show origin/main --date=iso` + `git rev-list --count
   <prev>..<tip>` per adjacent pair (window sizes; surprise windows
   folded LABELED, never excluded and never deferred).
2. The SIX chain numbers carried by the v24 spark brief (their only
   carrier; quoted verbatim below). They bank verbatim in
   `measurements.json` at commit 2 and the six-number chain
   TERMINATES there. v24's own post-bank reals (bank-commit hook
   real + push total-hook real) ride the close log/receipt for v25 —
   the inheritance-lag mechanism continues with NEW numbers only
   (structural, banked v21 reconciliation item 8).
3. Banked corpora (read-only): `reviews/cadence-v21/measurements.json`
   (pre-adoption band, v20 anchors, hook-real distribution, span
   law), `reviews/cadence-v19/*` (per-class cost model, bisect
   model, outlier-law precursor), `reviews/impl-v20/verdict.md`
   (v20 hook reals, frozen hashes, partition law).
4. This session's own `time` outputs (hook reals; the push real).

## Chain numbers (verbatim from the v24 brief — this sprint is the banking event)

- v21 push: total-hook real 178m42.718s = 10722.7s at 693 tests
- v21 bank-commit hook real: 3m4.454s = 184.5s
- v22 push: total-hook real 174m8.285s = 10448.3s at 693 tests
  (window label: "pins-only - maximally scope-confounded"; window =
  exactly 1 commit)
- v22 re-pin hook real: 2m53.048s = 173.0s green
- v23 re-pin hook real: 2m59.794s = 179.8s green
- v23 push: total-hook real 214m33.513s = 12873.5s at 693 tests
  (window label: "pins-only - maximally scope-confounded"; window =
  exactly 1 commit; the game-two seat ran LIVE in parallel the whole
  ~3.6h window, ~11 upstream commits landed - machine-load confound
  NAMED, not measured; observed timeout headroom 40.4% vs 21600s,
  prior worst 48%)

## Labeling rules (fixed)

1. Every number carries source + span + n label; observed points
   only; no trend claims at these n.
2. Span law (banked v21): hook-real / tier-elapsed / suite-stage /
   total-hook are distinct spans, labeled per point, never mixed in
   one distribution; cross-span comparisons bounded/directional only.
3. v20 window TRANSITIONAL, never pooled; sensitivity treatments
   shown where pooling could matter.
4. Outlier law (banked): 1-commit windows count in the raw band,
   labeled — never silently excluded; the v23 push high point folds
   the same way.
5. Green-only construction of hook-real distributions is named; reds
   reported alongside at their cost.
6. Named non-measured confounds: (i) parallel-seat machine load
   (shared box; the game-two seat may run live during this session's
   own timed spans too); (ii) local full-suite substitution (banked
   v21 council item 7, dormant; instrumenting it stays OUT of
   scope).
7. Banked-number supremacy: any mined value contradicting a BANKED
   number is a STOP — the banked corpus wins unless primary bytes
   prove otherwise; the discrepancy banks named (brief stop
   condition).
8. Scope confound honesty: all three completed windows are scope-set
   (v21 small-by-design; v22/v23 pins-only) — post-treatment
   selection is the dominant confound for (a)/(d) and the answers
   say so.

## Answer cells (NULL at this commit; filled at commit 2 from captured primaries)

- (a): null
- (b): null
- (c): null
- (d): null

## Council plan (fixed)

One consolidated adversarial call: alias `kimi`, `--max-tokens 3000`,
<= 8k tokens total, response file-redirected and read as explicit
UTF-8. Brief inlines the window series, the four total-hook points,
the outlier treatment, and all four DRAFT answers; demands the
strongest objection per question + the biggest unthought risk, each
with VERDICT (CONFIRMED / REFUTED / UNCERTAIN). Every REFUTED is
re-verified against primary bytes before folding; adoptions folded
before commit 2. No adoption may weaken a bar.

## INTEGRITY bars (all-must-pass at commit 2)

1. This pre-registration committed before any measurement banked.
2. `reviews/cadence-v19/*` + `reviews/impl-v20/*` +
   `reviews/cadence-v21/*` byte-untouched.
3. Zero new tools; unpinned census = 4 at close (exports_guard,
   checkout_gate, pin_drift, fast_gate).
4. One full discover green, file-captured (expect 693), judged by
   grep "^Ran |^OK|^FAILED" on the captured log.
5. Both asset_gate runs exit 0 (step 0 + pre-banking).
6. Five standing `--check`s exit 0 at banking: track_recompose,
   pose_integrity_metrics, remedy_metrics, adoption_demo,
   exports_guard.
7. pin_drift at every drift; re-pins solo.
8. Zero pixels / exports / register edits / `../game-two` writes;
   frozen-surface hashes match (pre-commit `c8557faf`, pre-push
   `5997892e`, full_gate `4fefb0c1`, .coveragerc `5f38035a`).
9. Ambient untouched; temp files deleted (deletion `ls` in the close
   log).
10. <= 3 new files (this rationale, measurements.json, verdict.md).

## QUALITY bars (blocking)

1. The six chain numbers banked VERBATIM in measurements.json (chain
   terminates there).
2. Every corpus number carries source + span + n label.
3. Council reconciled; adoptions folded before commit 2.
4. HFO gate on the verdict: accuracy and presentation scored
   separately.
5. Receipt carries v24's own post-bank reals labeled for v25.
