# Post-adoption cadence re-measurement — v21 verdict

**Answer first: all four pre-registered questions are answered AS
LABELED, and the honest headline is that two of them cannot be
answered yet. (a) Commits-per-push: INSUFFICIENT WINDOWS — exactly one
clean post-adoption window exists (this sprint's own, 4 commits) and
its size is set by sprint scope, not commit cost; re-ask at v23+.
(b) Fast-hook headroom: every observed point across 2 sessions (n=9
green hook reals 160–197.6 s, plus 185.85/190.4 s tier-span points)
sits at ≤ 32.9 % of the 600 s budget — observed points only, no trend
licensed. (c) Push cost at 693 tests: only the bounded claim is
licensed — v20's suite stage ran ≤ 11205 s, at or below the
composition-model band floor, so there is NO cost-growth signal
v18→v20; observed push-timeout headroom ≥ 48 %. (d) Bisect exposure:
the arithmetic is banked and benign (30–60 min worst-case,
module-scoped) across every observed window size; the behavioral
question (did cheaper commits raise commits-per-push) is INSUFFICIENT
at n=1. Zero pixels, zero exports, zero register movement; suite 693
green, file-captured.**

This was a PATH B sprint (spark brief, v21): the capture-contract tool
spec had NOT arrived at step 0 — the inbox held one unrelated
fire-and-forget drift note from the game seat
(`from-game-two-creature-dash-strike-19b4310.md`), which step 0
absorbed (its change was already inside the banked `daaddd4` pin) and
archived to `done/`. No spec arrived mid-sprint; nothing is parked.
PATH A (spec intake review) remains first-priority the moment it
lands.

Reviewed artifacts:

- `reviews/cadence-v21/rationale.md` (`d488257`) — questions, sources,
  labeling rules, bars; committed BEFORE any measurement was banked.
- `reviews/cadence-v21/measurements.json` — every number cited here,
  each with its source and span label.
- Push record: `git reflog show origin/main` — 20 entries, all
  "update by push" (a corroborating primary the v19 sprint did not
  use; it makes push windows directly measurable and showed pushes do
  NOT always land at verdict-close commits).
- Session model `us.anthropic.claude-fable-5` (verified from
  `PI_MODEL`). Council seat cross-vendor (Kimi K2.5,
  `moonshotai.kimi-k2.5`), one consolidated adversarial call: brief
  5,563 bytes inlining the window series, hook points, span
  reconciliation, and all four draft answers; 1,498 input + 2,601
  output = 4,099 tokens, within the 8k budget; response
  file-redirected, read as UTF-8; reconciliation below.

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Pre-registration committed before any measurement banked | PASS | `d488257` (rationale alone) precedes the bank commit; measurements.json and this verdict land together in commit 2 |
| 2 | `reviews/cadence-v19/*` + `reviews/impl-v20/*` byte-untouched | PASS | `git diff b4765ba..HEAD --stat` on both trees: empty |
| 3 | Zero new tools; unpinned census = 4 at close | PASS | `git diff b4765ba..HEAD --stat -- tools/ bin/ tests/`: empty; census unchanged (exports_guard, checkout_gate, pin_drift, fast_gate) |
| 4 | One full discover green, file-captured | PASS | `Ran 693 tests in 3436.897s`, `OK`, rc=0 (block 01:39:00Z–02:36:18Z, real 57m17.186s); judged by `grep "^Ran \|^OK\|^FAILED"` on the captured log |
| 5 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 (after the `17b0ae8` re-pin); pre-banking: exit 0 (after the `a2113f3` re-pin) |
| 6 | Five standing `--check`s exit 0 at banking | PASS | track_recompose, pose_integrity_metrics, remedy_metrics, adoption_demo, exports_guard — all rc=0 this session, after all v21 edits existed |
| 7 | pin_drift at every drift; re-pins solo | PASS | two drift events, two solo commits: `53f08c1` (content hop `daaddd4→17b0ae8`, creature.rb +17/-0 additive zone-tier seam, approve-by-default, cumulative-diff read, note mailed) and `067645e` (identity-only `→a2113f3`, mechanical) |
| 8 | Zero pixels/exports/`../game-two` writes/register edits; frozen surfaces byte-identical | PASS | exports_guard rc=0; game-two touched only via read-only `git -C`; register diff empty; live hashes match v20 close (pre-commit `c8557faf`, pre-push `5997892e`, full_gate `4fefb0c1`, .coveragerc `5f38035a`) + `git diff b4765ba..HEAD -- swarmforge.toml bin/full_gate.py .coveragerc` empty |
| 9 | Temp files deleted; ambient untouched; explicit staged paths per commit | PASS | deletion `ls` in the close log; `M AGENTS.md` + untracked ambient set present and unstaged at every staged-list check |
| 10 | ≤ 3 new files | PASS | rationale.md, measurements.json, this verdict — nothing else added |

## The four questions, answered as labeled

**(a) Commits-per-push before vs after activation — INSUFFICIENT
WINDOWS (n=1).** The reflog-derived pre-adoption band (v17–v19 era,
full-suite hooks at 645–668 tests) is 1–6 raw across 4 windows — 5–6
for the three sprint-bearing windows plus one 1-commit owner-ordered
sync push (reported, not hidden; the push predates adoption by 2 days
so it cannot preview post-adoption behavior; the verdict is identical
under either band). v20 = 9, TRANSITIONAL (activation mid-window),
never pooled — and the pre-registered rule costs nothing here:
pooled, split, or excluded, every treatment yields the same
INSUFFICIENT verdict (sensitivity banked). v21's own window = 4
commits (two protocol re-pins, the pre-registration, the bank),
scope-confounded by a deliberately small sprint. Re-derivation note:
the brief's quoted "3–6 observed v17–v19" did not reproduce exactly
from primaries; the reflog numbers are banked as the stronger source
and the discrepancy is named. Re-ask at v23+ with ≥ 3 clean windows.

**(b) Fast-hook wall-clock vs the 600 s budget — every observed point
≤ 32.9 % of budget; no trend licensed.** n=9 green hook reals across
2 sessions (v20: 172–186 s; v21: 160.0, 184.0, 197.6 s) plus two
tier-span points (185.85, 190.4 s), spans labeled per point and never
mixed. The v21 max (197.6 s, a re-pin committed while the game seat
ran live) exceeds every v20 point by ~6 % — session variance visible
at n=2 sessions, another reason no trend is claimed. The one red in
the record (v20's pre-activation drift catch) cost ~3 min wall — the
detection that cost 3917 s in the v19 era is now cheap. The bank
commit's own hook real lands after this file and prints in the close
log (inherited by v22, the standing mechanism).

**(c) Push-window cost at 693 tests — bounded claim only: no growth
signal.** Spans reconciled before comparing (pre-registered rule 4):
v17 10733 s @ 645 and v18 12311 s @ 668 are SUITE-STAGE (coverage-on);
v20's only carrier is 186m45s = 11205 s TOTAL-HOOK @ 693 (recorded by
the v21 spark brief — the verdict banks before its own push, so the
next sprint's brief is the standing carrier). Total-hook = LFS +
suite-stage + repo-wide warn metrics + overhead, every term
non-negative, so v20's suite stage ≤ 11205 s unconditionally — at or
below the composition-model band [11591, 13103] s for 693 tests. The
bound is one-sided (the true miss is ≥ 3.3 % and its magnitude
unknowable from this carrier); what it licenses is exactly one claim:
push cost did NOT rise v18→v20. Observed timeout headroom: 11205 s vs
21600 s = 48.1 % (observed point, no forward claim). This session's
reference discover (3436.9 s @ 693 raw, +2.0 % vs v19's 3369.0 s @
668) is consistent and load-bearing for nothing.

**(d) Bisect exposure — arithmetic banked; behavioral question
INSUFFICIENT (n=1).** Module-scoped bisect at ~15 min/step (banked
v19): N=4 → 2 steps ≈ 30 min; N=5–6 → 3 steps ≈ 45 min; N=9
(transitional) → 4 steps ≈ 60 min. Benign at every observed window
size. Whether cheaper commits RAISE commits-per-push is neither
confirmed nor refuted: the single clean window sits inside the
historical 1–6 range and sprint scope — not commit cost — currently
sets N. Re-ask at v23+.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

Returned verdicts: Q1 UNCERTAIN/PARTIALLY-REFUTED, Q2 REFUTED, Q3
UNCERTAIN, Q4 REFUTED+CONFIRMED, Q5 five candidate gaps. Per the
v12–v20 precedent every adverse claim was re-verified against primary
bytes; the reconciliation:

1. **Q2 core (span law invalid / unit confusion / LFS could reverse
   the bound) — REFUTED on primaries.** The pre-push hook's
   composition is verified from live bytes this session (`git lfs
   pre-push` then `exec swarmforge gauntlet --full`) and from the
   banked v19 hard-gate map: total-hook is a sum of non-negative
   terms including the suite stage, so total ≥ suite holds whatever
   LFS costs — a large LFS term would SHRINK the suite-stage bound
   and strengthen the claim, not reverse it (v20 was additionally a
   zero-new-exports sprint). The unit reading stands: 186m45s = 11205 s
   matches the banked "~3.1–3.4 h at 693" scale and the 21600 s
   timeout sizing; a 186 s full coverage gauntlet is impossible when
   the raw suite alone runs ~3400 s. The claimed "54×/scale anomaly"
   conflated pre-COMMIT tier points with the pre-PUSH gauntlet.
   ADOPTED anyway: the corpus now states the composition, the
   zero-new-LFS fact, and the strengthening direction explicitly.
2. **Q1 (outlier exclusion is post-hoc; could be a treatment-effect
   preview) — kernel ADOPTED, preview scenario REFUTED on the
   timeline.** The 1-commit push (08-22 13:42) predates activation
   (08-24 12:04) by two days; it cannot preview post-adoption
   behavior. ADOPTED: the raw 1–6 band is now the headline, the 5–6
   sprint-bearing band is the labeled sensitivity view, the exclusion
   rationale cites the commit message (an owner order), and the
   answer is shown identical under either band.
3. **Q1 (activation "mid-window" exogeneity unverified) — answered
   from banked carriers the council did not have.** The activation
   timing was owner-ratified and pre-registered (`6641a2c` rationale
   records the ratification verbatim; the v20 brief pre-declared the
   window structure). The adoption WAS motivated by hook cost — that
   is the program's recorded decision path, and the TRANSITIONAL
   label exists precisely because the window mixes regimes.
4. **Q3 (never-pooled = precision destruction; report sensitivity) —
   ADOPTED.** The corpus now banks all three treatments (pooled 4–9
   n=2; split 4–6 n=2 synthetic — no push event exists inside the
   window to cut at; excluded n=1) and shows every treatment yields
   the same INSUFFICIENT verdict — the pre-registered rule costs
   nothing at this n. The "small-by-design = post-treatment
   selection" point is CONFIRMED and banked as the dominant confound
   in (a)/(d).
5. **Q4 (n=8 pooling, green-only selection, headroom implies
   stability) — ADOPTED as wording law.** Headroom is now an
   observed-points-only statement; the green-only construction is
   named with the red reported alongside (at its new ~3 min cost);
   the freeze boundary and the inheritance mechanism for post-freeze
   reals are explicit. (The distribution grew to n=9 with the
   pre-banking re-pin before freeze.)
6. **Q4 ("insufficient windows" is the right answer but the draft
   launders precision) — split.** CONFIRMED for the two claims that
   implied inference: "similar magnitude" in (c) (dropped —
   one-sided-bound honesty) and "≥ 3.1x headroom" phrasing in (b)
   (reworded per item 5). The bisect table and the point lists stay:
   they are mechanical facts with n labels, not inferences.
7. **Q5 gap: local full-suite substitution (developers running the
   full suite manually pre-commit, making cadence a selected sample)
   — ADOPTED as a named non-measured confound.** Measuring it needs
   instrumentation → out of scope by pre-registration; banked so v23+
   inherits the question honestly.
8. **Q5 gap: inheritance lag / "push gates may be simulated" — lag
   ADOPTED, simulation REFUTED on hook mechanics.** No sprint's
   corpus contains its own push point (structural, now banked). But
   nothing is simulated: the pre-push hook runs live at push time and
   its rc gates the ref-update — v20's 186m45s was observed at its
   real push, then carried forward.
9. **Q5 gap: "+20–50 s for +25 tests is 10× off the 18.4 s/test
   observed rate" — REFUTED on banked primaries.** 18.4 s/test is the
   suite AVERAGE, dominated by the nine determinism-re-proof modules
   (12–15 s/test); the banked v19 class model puts logic-class tests
   at 0.02–0.5 s/test raw (~0.8–2 s coverage-on), and the 25 tests
   added v18→v20 are all logic-class (17 fast-gate fixtures, 6
   aggregate-law shape tests, 2 council probes). Applying the suite
   average to a class-specific delta is exactly the composition error
   the v19 corpus banked against.
10. **Q5 gap: re-pin/docs/feature commit heterogeneity — ADOPTED.**
    The unit caveat now sits in (a): commit count is the right unit
    for hook/bisect COST (each commit triggers one hook) and a weak
    unit for cross-era behavioral comparison.

Net: three council scenarios refuted on primary bytes or timeline
(span-law reversal + unit confusion; outlier-as-preview; simulated
push gates) and one on the banked class model; seven kernels adopted
and folded before this bank commit (raw-band headline + sensitivity
treatments, composition/LFS explicitness, one-sided-bound wording,
observed-points-only headroom + green-only note, two named
non-measured confounds, the unit caveat). No adoption weakened a bar;
the corpus got stricter. Neither of the two INSUFFICIENT verdicts
moved — the council's own Q4 confirmed "insufficient windows" as the
right banked answer.

## HFO gate (accuracy vs presentation, separately)

- **measurements.json** — machine-consumed corpus (HFO step-0 exempt
  from humanization; sourcing law still applies). Accuracy: every
  number carries source + span + n label; the two REFUTED-prone
  spots (span law, band derivation) now cite their primaries. PASS.
- **Verdict (this file)** — accuracy: every number traced to the
  corpus, a banked file, or printed session output; the two
  unanswerable questions are surfaced first, not absorbed; the
  brief-vs-reflog band discrepancy is named. PASS. Presentation:
  answer-first with the negative result as the headline, machine
  table, typed reconciliation, labeled claims throughout; no
  unlabeled precision. PASS.

## Non-claims

No behavioral claim about commit cadence under the partition — that
is the point of the two INSUFFICIENT verdicts, and they are the
banked answer, not a deferral of one. No forward stability claim on
hook headroom or push cost (observed points only; the growth model
stays composition-based). No coverage claim about the fast tier
(unchanged law: coverage lives at push). No register movement: C1–C5
MET, C6 OPEN doubly gated, unchanged; the aggregate-answer header
shape tests stayed green with zero edits of mine. No capture-contract
content (the spec has not arrived; PATH A outranks everything the
moment it does). Zero pixels, zero exports, mechanical ids
throughout.

## Mail and pin status

- Inbox at step 0: one item, NOT the spec — the game seat's
  fire-and-forget dash-strike note (`19b4310`). Absorbed at step 0
  (the change was already inside the banked `daaddd4` pin; the
  combat.json arc row is commit-anchored by owner decision
  2026-08-18 and re-verified green), archived to `done/`, answered
  inside the outbound re-pin note (no reply was expected). No
  arrivals mid-sprint; no polling.
- Outbound: one fire-and-forget content-hop note
  (`from-game-two-assets-v21-repin-17b0ae8.md`) recording the
  approve-by-default judgment and the kit-arc answer.
- Pins: `daaddd4 → 17b0ae8` content hop routed approve-by-default
  (`53f08c1`, +17/-0 additive, constants 20/20 + attack_timing
  green); `→ a2113f3` identity-only, mechanical (`067645e`,
  pre-banking checkpoint); asset_gate exit 0 after each. Upstream ran
  4 commits during the sprint window (seat live throughout).

## Stop

Sprint 21 stops here: one pre-registration, one measured corpus with
two honest INSUFFICIENT verdicts and two bounded answers, council
reconciled with adoptions folded before banking, two protocol
re-pins, this verdict. Carried to v22+: capture-spec intake (PATH A,
first priority on arrival), the commits-per-push and behavioral
questions re-armed for v23+ (≥ 3 clean windows), the hook-real
distribution accruing for free each sprint, this push's own cost
point riding the close log, the local-full-suite-substitution
confound if cadence questions ever sharpen, and the at-speed /
viewport / shade / DEF-3 watch items riding upstream instruments.
