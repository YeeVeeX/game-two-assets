# The armed post-adoption cadence corpus — v24 verdict

**Answer first, one line per question. (a) Commits-per-push:
BOUNDED-DESCRIPTIVE — the post-adoption raw band is 1–4 (n=3
completed clean windows, 2 of 3 being 1-commit pins-only closes),
inside the pre-adoption raw band 1–6; but the populations are
non-comparable (scope-set windows; the pins-only close class did not
exist pre-adoption), so the pre-registered before/after behavioral
comparison is NOT LICENSED even though the >= 3-window bar was met.
(b) Fast-hook headroom: every observed green hook real — n=15 across
5 sessions, 160–268.3 s, condition-labeled per point — sits at
<= 44.7% of the 600 s budget; observed points only, no trend. (c) Push
cost at 693 tests: four total-hook points span 10448.3–12873.5 s
(+23.2%, non-monotone, v23 high point load-confounded and labeled);
symmetric signal-detection negative — no growth signal AND no decrease
signal, detection power low and stated; worst observed timeout
headroom 40.4%. (d) Bisect arithmetic benign at every observed window
size (0–2 steps; 1-commit windows need none); the behavioral risk
monitor reads GREEN at n=3 (no exposure widening observed,
descriptive) while the CAUSAL question is INSUFFICIENT/untested —
scope endogeneity named. The six brief-carried chain numbers are
banked verbatim in `measurements.json` and the six-number chain
TERMINATES at this bank commit. Zero pixels, zero exports, zero
register movement; suite 693 green, file-captured.**

This was a PATH B sprint (spark brief, v24): the capture-contract
tool spec had NOT arrived at step 0 (inbox root empty) and did not
arrive mid-sprint; nothing is parked. PATH A (spec intake review)
remains first-priority the moment it lands.

Reviewed artifacts:

- `reviews/cadence-v24/rationale.md` (`a290066`) — questions,
  sources, labeling rules, chain numbers quoted, bars; committed
  BEFORE any measurement was banked; answer cells null at commit 1.
- `reviews/cadence-v24/measurements.json` — every number cited here,
  each with source + span + n label; the six chain numbers verbatim.
- Push record: `git reflog show origin/main --date=iso` — 23 entries,
  all "update by push"; the three post-adoption windows re-derived
  mechanically (4/1/1 via `rev-list --count`); zero surprise windows.
- Session model `us.anthropic.claude-fable-5` (verified from
  `PI_MODEL`). Council seat cross-vendor (Kimi K2.5), one consolidated
  adversarial call: brief 6,599 bytes inlining the window series, the
  four total-hook points, the outlier treatment, and all four draft
  answers; `--max-tokens 3000`; response file-redirected, read as
  UTF-8; within the 8k budget; reconciliation below.

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Pre-registration committed before any measurement banked | PASS | `a290066` (rationale alone, cells null) precedes this bank commit; measurements.json + verdict land together at commit 2 |
| 2 | `reviews/cadence-v19/*` + `reviews/impl-v20/*` + `reviews/cadence-v21/*` byte-untouched | PASS | `git diff 9f2797a..HEAD --stat` over all three trees: empty |
| 3 | Zero new tools; unpinned census = 4 at close | PASS | `bin/` = fast_gate.py + full_gate.py (pinned-frozen) only; tools/ diff empty; census unchanged (exports_guard, checkout_gate, pin_drift, fast_gate) |
| 4 | One full discover green, file-captured | PASS | `Ran 693 tests in 4232.691s`, `OK`, zero FAILED lines; judged by `grep "^Ran \|^OK\|^FAILED"` on the captured log (wrapper real 70m32.970s; concurrent-session ambient caveat banked) |
| 5 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 (after content re-pin `205fe6b`); pre-banking: exit 0 (identity-drift warning resolved by mechanical re-pin `5d827a9`, clean exit-0 re-run after the edit) |
| 6 | Five standing `--check`s exit 0 at banking | PASS | track_recompose, pose_integrity_metrics, remedy_metrics, adoption_demo, exports_guard — all rc=0 this session, after all v24 edits existed |
| 7 | pin_drift at every drift; re-pins solo | PASS | two drift events, two solo commits: `205fe6b` (content hop `a30837d→3b85b55`, +6/-5 non-additive routed by session judgment — breach_line_top keying same-value, comment rewrite, dead `wipe_font` removal proven zero-call-site at the banked baseline via `git grep`; 20/20 constants + attack_timing green; note mailed) and `5d827a9` (identity-only `→e4e6474`, mechanical) |
| 8 | Zero pixels/exports/register edits/`../game-two` writes; frozen surfaces byte-identical | PASS | exports_guard rc=0; game-two touched only via read-only `git -C`; `docs/integration-readiness.md` + `docs/selection-register.md` + `swarmforge.toml` diffs vs `9f2797a` empty; live hashes match v20 close (pre-commit `c8557faf`, pre-push `5997892e`, full_gate `4fefb0c1`, .coveragerc `5f38035a`) |
| 9 | Ambient untouched; temp files deleted | PASS | `M AGENTS.md` + untracked ambient set present and unstaged at every staged-list check; temp deletion `ls` in the close log |
| 10 | <= 3 new files | PASS | rationale.md, measurements.json, this verdict — nothing else added |

## The four questions, answered as labeled

**(a) Commits-per-push — bounded-descriptive; the behavioral
comparison is not licensed.** The v21 verdict re-armed this question
for ">= 3 clean windows"; that bar is MET (v21=4, v22=1, v23=1,
re-derived from reflog + rev-list). The observed post-adoption raw
band is 1–4, with 1-commit windows 2 of 3 — stated in the headline,
per the banked outlier law (counted, labeled, never excluded). What
the data cannot support (council-sharpened, and the honest headline):
a before/after cadence-behavior comparison. The post-adoption windows
sample a DIFFERENT work-mix population — v22/v23 are pins-only sprint
closes, a window class with no pre-adoption analogue (the only
pre-adoption 1-commit window was an owner sync push), and every
completed window is scope-set (v21 small-by-design; v22/v23
pins-only). The sprint-bearing sensitivity view (pre 5–6 vs post 1–4)
compares unlike classes and is labeled descriptive-only. Sensitivity:
including v24's own at-bank window (4 commits, provisional) leaves
the band 1–4; pooling TRANSITIONAL v20 is barred and moot. Alternative
cause named, not adjudicated: the program entered an upstream-gated
phase (new art gated on the game's frame pin) in the same period.

**(b) Fast-hook headroom — every observed point <= 44.7% of budget;
no trend licensed.** n=15 green hook reals across 5 sessions
(inherited n=12: v20 172–186, v21 160–197.6 + 184.5 bank, v22 173.0,
v23 179.8; this sprint n=3: 209.1, 196.4, 268.3), each carrying a
per-point condition label. The two new maxima are condition-labeled
rather than absorbed: 209.1 s on a clean box (+5.8% over the prior
max — a manifest-only re-pin commit, attribution open), and 268.3 s
measured while this session's own full-suite discover ran concurrently
on the same box (self-inflicted load, labeled — the parallel-load
confound made visible at hook-real scale instead of left ambient).
With n=1–3 points in three of five sessions, intra- vs inter-session
variance is not decomposable and no session-effect claim is made. The
distribution is green-only by construction, named: no red hook real
occurred this sprint (upstream drift was caught by pin_drift before
any commit was attempted). Even the loaded worst case leaves 55.3%
budget headroom; the 600 s assertion has never fired. The bank
commit's own hook real lands after this file and rides the close
log/receipt for v25 (standing mechanism).

**(c) Push cost at 693 — symmetric signal-detection negative; bounds
and headroom only.** Four TOTAL-HOOK points at constant test count:
11205 (v20, banked) / 10722.7 (v21) / 10448.3 (v22) / 12873.5 (v23) —
raw band spread +23.2%, non-monotone in time, the v23 high point
folded per the outlier law with its parallel-seat confound named (the
chain label records ~11 upstream commits landing during that ~3.6 h
window), never excluded, no cause claim. Composition is unchanged
(zero tests added since v21), so the model predicts zero
composition-driven growth; the licensed statement is a symmetric
signal-detection negative — no growth signal AND no decrease signal
detected — with detection power stated: a real drift smaller than the
±23% ambient spread would be invisible at n=4 with one confounded
point. Cross-span honesty: every carrier is total-hook, so only
one-sided bounds are licensed vs the suite-stage model band ([11591,
13103] s at 693): the tightest is v22's suite-stage <= 10448.3 s,
>= 9.9% below the model floor, miss magnitude unknowable (no
suite-stage carrier exists at 693 — inherent to the carriers, named).
Worst observed timeout headroom: 12873.5 vs 21600 s = 40.4% (was
48.1% before v23) — observed point, no forward claim. v24's own push
point lands after this bank (structural lag) and rides the receipt.

**(d) Bisect exposure benign; risk monitor green; causal question
INSUFFICIENT.** Module-scoped bisect at ~15 min/step: N=1 → 0 steps
(the culprit commit is known; one targeted repro), N=4 → 2 steps
≈ 30 min, N=9 transitional → 4 steps ≈ 60 min (context). The window
sizes that dominate observed post-adoption data (1-commit) have the
best possible bisect property. The v19 pre-registered exposure risk —
"cheaper commits may RAISE commits-per-push, widening the push-time
exposure window" — has NOT materialized in any observed window
(descriptive risk-monitor readout, green at n=3). The CAUSAL question
is split out and marked INSUFFICIENT/untested rather than "answered
no" (council-adopted): scope is endogenous to both the treatment
(adoption itself made 1-commit closes viable — the opposite mechanism
to the pre-registered one) and the program phase (upstream-gated
sprints shrink scope for hook-independent reasons). It re-arms
whenever a post-adoption window with pre-adoption-like scope (a
multi-commit feature sprint) exists in the record.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

Returned verdicts: Q1 REFUTED, Q2 UNCERTAIN, Q3 REFUTED, Q4 REFUTED,
Q5 UNCERTAIN with four candidate gaps. Per the v12–v21 precedent every
adverse claim was re-verified against primary bytes before folding:

1. **Q1 core ("the sprint-bearing filter is post-hoc; the
   pre-registration didn't see the scope labels") — REFUTED on
   primary bytes; the kernel ADOPTED anyway.** The scope labels are
   banked artifacts that PRECEDE this sprint (v21 verdict:
   "small-by-design"; the v22/v23 "pins-only — maximally
   scope-confounded" labels ride the chain numbers quoted verbatim in
   `a290066`), and the sprint-bearing sensitivity view + the
   scope-confound-dominates rule were pre-registered in `a290066`
   before any measurement was banked (rationale lines verified this
   session). ADOPTED: the population non-comparability finding is now
   the HEADLINE of (a) — the bands are descriptive facts side by
   side, not a comparison; 1-commit dominance (2 of 3) moved into the
   headline; the sprint-bearing class is labeled UNSTABLE across the
   adoption boundary.
2. **Q2 ("'session variance visible across 5 sessions' — n=1 sessions
   cannot show variance") — ADOPTED.** The phrase is gone; the corpus
   states the range, the per-point condition labels, and the
   non-decomposability of intra- vs inter-session variance at n=1–3
   points per session. The green-only selection concern was already
   pre-registered (rule 5) and stays named with the historical red
   reported.
3. **Q3 ("'no cost-growth signal' is asymmetric skepticism and
   claims absence from noisy confounded data") — ADOPTED as
   wording law.** The answer is now a SYMMETRIC signal-detection
   negative (no growth signal AND no decrease signal) with detection
   power stated explicitly (±23% spread masks smaller drift at n=4).
   The ">= 9.9% below the model floor" figure is kept — re-verified
   as sound: suite-stage <= 10448.3 < 11591 makes 9.9% a LOWER bound
   on the floor miss, the same one-sided construction v21 banked at
   3.3% — with the unknowable-magnitude caveat attached.
4. **Q4 ("'no increase observed' launders a causal frame; scope is
   endogenous to the treatment") — ADOPTED as the answer's
   structure.** (d) now splits the risk-monitor readout (descriptive,
   green at n=3 — the thing the v19 risk actually asked to watch)
   from the causal claim (INSUFFICIENT/untested; endogeneity +
   program-phase alternative cause named). The council's mechanism
   observation (cheaper commits → smaller viable closes → FEWER
   commits/push) is banked as the named opposite mechanism.
5. **Q5 gap ("units differ: old hook blocking-serial, fast hook
   non-blocking") — REFUTED on hook mechanics.** Both eras' pre-commit
   hooks run synchronously inside `git commit` (`exec swarmforge
   gauntlet --changed`, verified from the live hook bytes this
   session); the span (`time git commit` wall) is identical across
   eras. Nothing is non-blocking.
6. **Q5 gap ("local full suites make the fast hook theater; green
   after invisible retries") — pre-registered, extended.** This IS
   the banked local-full-suite-substitution confound (v21 item 7),
   re-named per pre-registration rule 6; the council's
   selection-into-measurement extension (only landed commits produce
   points; abandoned/split work is invisible) is ADOPTED into the
   confound block as unmeasurable-without-instrumentation.
7. **Q5 gap ("pins-only sprints look like gaming the fast hook — are
   non-pin commits slower?") — answered from the corpus, alternative
   cause banked.** Per-point commit-class labels show no segregation
   signal: the observed maxima ARE manifest-only re-pin commits
   (209.1, 268.3) while content-bearing commits (pre-registration,
   register law, bank commits) sit at 174–196.4 — direction opposite
   to the gaming hypothesis at these n; and sprint scope is set by
   owner briefs under an upstream-gated program phase, which is
   banked in (a)/(d) as the named alternative cause. No causal claim
   either way.
8. **Q5 gap ("the model band is untested at 693; the one-sided bound
   is theoretical") — TRUE and inherent, named.** No suite-stage
   carrier exists at 693 (all carriers total-hook; structural since
   v20 — the verdict banks before its own push). The corpus states
   exactly this; the bound is the honest maximum the carriers
   license. Non-delta.

Net: two council scenarios refuted on primary bytes (pre-registration
timeline; hook mechanics), one figure re-verified sound (the floor
bound), and four kernels adopted before this bank commit
(non-comparability headline, session-variance wording, symmetric
signal + detection power, risk-monitor/causal split + endogeneity +
selection-into-measurement). Every adoption made a claim SMALLER; no
bar weakened. Note the asymmetry with v21's outcome: v21's council
confirmed "INSUFFICIENT windows" and this corpus MET that bar — the
non-comparability finding is not a retreat from the v21 answer but
the thing the extra windows revealed: more windows of the same
scope-set kind sharpen n, not comparability.

## HFO gate (accuracy vs presentation, separately)

- **measurements.json** — machine-consumed corpus (HFO step-0 exempt
  from humanization; sourcing law applies). Accuracy: every number
  carries source + span + n label; the six chain numbers byte-copied
  from the brief; per-point condition labels on every session timing.
  PASS.
- **Verdict (this file)** — accuracy: every number traced to the
  corpus, a banked file, or captured session output; the two REFUTED
  council re-verifications cite the primary checked (rationale bytes;
  hook bytes); nothing pre-filled before evidence existed (the suite
  cells were null until the captured log landed). PASS. Presentation:
  answer-first with the strongest limitation (non-comparability) as
  the headline of its own answer, machine table, typed
  reconciliation, labeled claims throughout; no unlabeled precision.
  PASS.

## Non-claims

No before/after cadence-behavior claim (the populations are
non-comparable — that finding IS the banked answer to (a)). No causal
claim about commit cost and batching in either direction (d splits
the green risk monitor from the untested causal question). No trend
or forward-stability claim on hook reals or push cost (observed
points only; symmetric signal statement with detection power stated).
No coverage claim about the fast tier (coverage lives at push,
unchanged). No register movement: C1–C5 MET, C6 OPEN doubly gated,
unchanged; header shape guards stayed green with zero edits of mine.
No capture-contract content (the spec has not arrived; PATH A
outranks everything the moment it does). Zero pixels, zero exports,
mechanical ids throughout.

## Mail and pin status

- Inbox at step 0: EMPTY → PATH B. No arrivals mid-sprint; nothing
  parked; no polling.
- Outbound: one fire-and-forget content-hop note
  (`from-game-two-assets-v24-repin-note.md`) recording the
  approve-by-default judgment on the +6/-5 renderer diff (keyed
  breach_line_top same-value; comment rewrite; dead `wipe_font`
  removal proven zero-call-site at the banked baseline).
- Pins: `a30837d → 3b85b55` content hop routed by session judgment
  under the owner-extended protocol (`205fe6b`, 20/20 constants +
  attack_timing green, note mailed); `→ e4e6474` identity-only,
  mechanical (`5d827a9`, pre-banking checkpoint); asset_gate exit 0
  after each.
- The six-number cadence chain: BANKED verbatim in
  measurements.json; TERMINATED at this commit. v24's own post-bank
  reals (bank-commit hook real + push total-hook real) ride the
  close log/receipt for v25 — new numbers only.

## Stop

Sprint 24 stops here: one pre-registration, one measured corpus
banking the six chain numbers and answering all four armed questions
as labeled (one bounded-descriptive, one distribution, one symmetric
signal negative with bounds, one split green-monitor/INSUFFICIENT),
council reconciled with adoptions folded before banking, two protocol
re-pins, this verdict. Carried to v25+: capture-spec intake (PATH A,
first priority on arrival), the causal behavioral question re-armed
on a multi-commit feature window, v24's own push point riding the
receipt, the named confounds (parallel-seat load, local-full-suite
substitution, selection-into-measurement, scope endogeneity), and the
at-speed / viewport / shade / DEF-3 watch items riding upstream
instruments.
