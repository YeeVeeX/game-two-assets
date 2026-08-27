# E3a-T2 RUNTIME intake + v1 consumer adaptation — verdict (v30)

**Answer first: PASS on all seven bars — the s84 T2 delivery is INTAKEN
under the banked intake law (six for six mailed sha256s exact at source and
after copy; verification receipt PASS over runs=2 at the manifest's
fingerprint), the consumer is ADAPTED to schema v1 in place with draft-1
behavior machine-proven unchanged (672/672 + 340/340 green through every
edit; the banked draft-1 test file unedited and green), and the parser
verdict on the roster-union delta is ADAPTED: both reference tracks
validate with ZERO schema violations, track 2's union gaps surface as
information reproducing the mail's four machine-verified frames exactly,
and every mapping refusal on both tracks lands in a banked LAWFUL class
with counts documented. Emitter defects: NONE found. Zero pixels — no
RUNTIME track was rendered; the verdict is validation + decision-stream
statistics (TEXT), and adjudication stays owner-sequenced. C6 stays OPEN.**

Review objects: the s84 delivery mail (md5
`98fb30332c8a84023eb0251de7f5757b`, verified at step 0) and bundle
`20260826T175326Z_p1_42` (identity = the mailed sha256s; full chain in
`evidence/replay/20260826T175326Z_p1_42/intake-record.md`). Rubric
pre-registered cells-NULL at commit A (`474c7d1`); adaptation at commit B
(`7b0a2dc`); this file + the judged rubric + the receipt draft + both
decision-stream captures land together at commit C. Session model
`us.anthropic.claude-fable-5` (verified from `PI_MODEL`). Council seat
cross-vendor (DeepSeek V3.2), one consolidated adversarial call: brief
9,494 bytes inlining the pin, the trust split, the decision-relevant code
snippets, the machine results, and the receipt draft; `--max-tokens 3000`;
file-redirected, read as UTF-8; 2,448 in + 1,045 out = 3,493 tokens, within
the 8k budget; reconciliation below.

## The bars, judged (full line-cited evidence: `rationale.md`)

| # | Bar | Verdict |
|---|---|---|
| B1 | Intake integrity | PASS — 6/6 mailed sha256 exact source AND copy; staged blobs re-hashed exact; PASS runs=2; fingerprint equality; `-text` routed in the staging commit; 0 CR bytes |
| B2 | Draft-1 regression | PASS — `--check` green after the edit; 33 banked tests unedited and green; four manifest re-banks each moved ONLY the consumer pin + generation commit; discover green at N=748 |
| B3 | v1 sufficiency | PASS — both tracks zero violations; union gaps both directions as information; 2538 + 9120 decisions, all pose-or-typed-refusal, accounting balanced |
| B4 | Semantics fidelity | PASS — pinned record semantics carried verbatim; 1-based domain enforced both levels; per-kit selection + exact coverage; constants cross-check 5/5 + striker == banked pins; possessed enforced; bundle_id enforced |
| B5 | Refusal-class correctness | PASS — draft-1 refusals unchanged; intake-only RUNTIME lift (11 fail-direction tests); lawful refusal profile documented with counts; zero unexplained classes |
| B6 | Receipt boundary | PASS — exactly the s84 asks answered; findings typed; council sentence-scan CONFIRMED clean |
| B7 | HFO gate | PASS — accuracy and presentation judged separately per artifact (section below) |

## Findings (typed per the pre-registered classes)

- **a1 (adaptation, DONE):** v29's queued consumer adaptation executed
  end-to-end — schema-version dispatch, per-kit constants map + selection
  rule, mapping-side lunge px pair, `possessed`, per-tick `masks`,
  union-roster semantics, 1-based windowed domain, `provenance.bundle_id`,
  and the RUNTIME intake path (`verify_runtime_intake`,
  design-section-5 gate). The a1 queue from `capture-intake-v29/verdict.md`
  is CLOSED; the intake gate's "established" status is carried by this
  verdict + the code, never by register edits.
- **n1 (noted, LAW not defect):** the reference tracks' refusal profile is
  entirely the two banked lawful classes — `unrenderable-facing` 504 (track
  1) + 1425 (track 2): up/left facings dominate full-roster windows and the
  banked pose rows exist for down/right only (a separate, unrequested asset
  decision, unchanged since v13); `unmapped-tween-class` 12 + 4: records
  moving with `tween_total` off the kit's `step_frames` (dash/knockback
  classes; no banked frame-selection evidence — the mapping refuses rather
  than guesses). `unmapped-action-class` stays legal-but-unobserved: no
  specials appear in either window.
- **n2 (noted, corroboration):** `possessed` is exactly one per tick across
  all 681 ticks of both windows — consistent with the manifest's seats=1;
  reported as statistics, never guessed into law (seats is bundle-level).
- **n3 (noted):** emitter defects NONE — every mail claim checked
  reproduced from bytes (window ranges, tick counts, roster sizes, the four
  gap frames, per-kit constants, all four attack_states mapping through the
  banked timeline w0/a0/k0/s0/r0/x0).
- **n4 (noted, council Q3 kernel adopted):** a same-name death-then-respawn
  INSIDE one window is accepted by the per-tick subset law and is
  DETECTABLE in the banked stats (`ticks_present` < last−first+1 implies
  interior gaps) without listing interior boundaries; the pin asks for
  presence-as-information, which first/last/count carries. Explicit
  interior-gap boundary listing is a future stat if a consumer of the stats
  needs it — not a validation-law change.
- **n5 (noted, council Q5 kernel adopted):** the per-kit constants
  cross-check against `combat.json` at the manifest's `game_commit` is
  TIME-STAMPED CORROBORATION recorded at intake (a read of mutable git
  history), not standing identity — the delivery's primary identity is and
  stays the mailed sha256s + the fingerprint chain, which the intake law
  verifies over bytes.

## Pre-registered mechanical consequence, resolved as registered

The commit-A rationale named it before the edit: the consumer's own sha256
is pinned by `reviews/recompose-v13/recompose-manifest.json`. Live, the
same class surfaced in THREE sibling manifests the fast gate flagged
mid-commit (`defect-audit-v14/defect-manifest.json`,
`remedy-v15/remedy-manifest.json`, `adoption-v16/adoption-manifest.json` —
their guard tests pin the consumer too). All four were regenerated by their
OWN tools (`--make-demo`, `--make-audit`, `--make-artifacts` ×2) under the
pre-registered lawfulness condition, and the condition held everywhere: git
diff per manifest = the consumer's pin line + `repo_commit_at_generation`,
NOTHING else —

```
-    "tools/track_recompose.py": "606f027b8c23...358f69e2"
+    "tools/track_recompose.py": "c1a114b981a0...0379c765"
-  "repo_commit_at_generation": "<v13/v14/v15/v16 commit>",
+  "repo_commit_at_generation": "474c7d1377d4229e9aa010e8c6695705777de2b2",
```

Every banked artifact reproduced byte-identically (v13's demo track/sheet/
APNG sha256 pins unchanged inside the manifest; v14's 12, v15's 28, v16's 9
artifacts rewritten with zero git diff). The banked METRICS and VERDICTS of
those sprints are untouched; what moved is each manifest's mechanical
cross-reference to the live consumer — the "disposable half" law made
concrete.

## Structured critique and cross-vendor review (DeepSeek V3.2, adversarial)

Returned verdicts: Q1 CONFIRMED, Q2 UNCERTAIN, Q3 REFUTED, Q4 CONFIRMED,
Q5 UNCERTAIN. Per the v12–v29 precedent every adverse or uncertain claim
was re-verified against primary bytes before folding:

1. **Q1 (trust boundary) — CONFIRMED as drawn.** "No other verification
   exists beyond what we already performed"; the one unexploitable remedy
   (re-emission) is game-side by construction and the receipt names it as
   the standing remedy for doubted deliveries. Non-delta.
2. **Q2 (draft-1 regression) — UNCERTAIN, closed by machine proof.** The
   reviewer verified the `mapping_constants` draft-1 short-circuit from the
   snippet and found no other delta, abstaining honestly on unseen code
   ("we cannot verify that no other changes exist outside the snippets").
   UNCERTAIN is not support — the closure our side is mechanical, not
   council opinion: 672/672 + 340/340 equivalence green, 33 banked tests
   unedited and green, demo artifacts byte-identical, discover green.
3. **Q3 (union edge cases) — REFUTED ("nothing wrong"), kernel ADOPTED as
   n4.** Same-name interior gaps and single-tick presence are both
   consistent with the pin; the stats' implicit interior-gap detectability
   is now NAMED (n4) instead of left as an unstated property.
4. **Q4 (receipt boundary) — CONFIRMED clean**, sentence-scan quoted in the
   judged B6 cell. Non-delta.
5. **Q5 (biggest unthought risk) — two kernels, one adopted, one refuted on
   primary bytes.** (i) Git-history mutability under the constants
   cross-check: ADOPTED as n5 — the cross-check is recorded as time-stamped
   corroboration; primary identity stays the mailed hashes + fingerprint.
   (ii) "`mapping_constants` with reference None/malformed could raise an
   exception not caught by validation, breaking draft-1 compatibility
   indirectly": REFUTED — the draft-1 path returns
   `track["constants"]` BEFORE any reference use (`if
   track["schema_version"] != SCHEMA_V1: return track["constants"]`,
   verified in the shipped bytes), so no draft-1 flow can reach the
   reference branch; the v1 path raises the TYPED `missing-reference`
   refusal, and every in-repo v1 caller passes the loaded reference.

Net: two CONFIRMED (both non-delta), one REFUTED with its kernel adopted as
explicit documentation (n4), one UNCERTAIN closed by machine proof rather
than argument, one UNCERTAIN split into an adopted disclosure (n5) and a
refutation on primary bytes. No bar moved post-registration; every adoption
made a claim smaller or more explicit; all adoptions folded before this
commit.

## HFO gate (accuracy vs presentation, separately)

- **intake-record.md** (owner + future-contributor audience): Accuracy —
  every hash in the table recomputed this session over named bytes; the
  verified-vs-trusted split states exactly which claims ride the producer's
  attestation; sizes and CR counts from the captured intake run; PASS.
  Presentation — headline verdict first, mechanical table, trust split under
  its own heading, no unlabeled precision; PASS.
- **verdict.md (this file):** Accuracy — headline claims only what the
  judged cells carry; council verdicts quoted with the exact failing/holding
  premise named; the seven carried numbers below are byte-copied from the
  v30 brief, never re-derived; the one pre-fill slip this session (a
  derived discover count briefly written before the log existed) was caught
  and reverted to a pending marker before any commit — the committed cell
  carries only the measured value; PASS. Presentation — truncated pyramid
  (verdict → bars → findings → consequence → reconciliation → carry), typed
  findings, machine table; PASS.
- **receipt-draft.md** (cross-seat mail, game-seat + owner audience):
  Accuracy — the four RECEIPT lines carry values verified this session;
  every body claim traceable to the banked captures or intake-record; the
  refusal explanation states LAW with counts rather than apologizing for
  defects; PASS. Presentation — receipt lines first (the thing s84 asked
  for), findings typed and numbered, non-claims explicit, register
  technical-concise; PASS.

## Non-claims

No adjudication of any lettered item — no RUNTIME track was rendered to
pixels; decision statistics are toolchain-fitness TEXT, and rendering the
intaken tracks waits for its own owner brief. No integration ask; C1–C5
MET, C6 OPEN doubly gated, untouched; `docs/integration-readiness.md` and
`docs/selection-register.md` byte-frozen. No schedule claims on T3/P2
(owner-paced). `docs/state-track-schema.md` stays draft-1 HISTORY;
`docs/replay-capture-design.md` section 5 was cited, never edited. Nothing
here re-adjudicates or softens a banked verdict. No cadence analysis beyond
the carry block below (observed points only, never a trend). Zero pixels,
zero exports, mechanical ids throughout.

## Mail and pin status (v30)

- Inbox at step 0: the s84 T2 delivery alone, md5-exact vs the brief
  (`98fb30332c8a84023eb0251de7f5757b`, 6,713 B). No new mail arrived
  mid-session as of commit C. The receipt mail is banked here as
  `receipt-draft.md` and is SENT post-push as a byte-identical copy
  (standing order: the delivery's expected receipt); the s84 mail archives
  to done/ after the send.
- Pins: one identity-only hop absorbed at step 0 (`5a311604` → `ea0e37c7`,
  all five pinned blobs byte-identical, 20/20 constants + attack_timing
  green, mechanical re-pin `7e66fbc`); asset_gate exit 0 after the re-pin
  (identity-drift WARNING class only). Later hops, if any, absorb as solo
  re-pins at the pre-push checkpoint per standing law.

## Cadence carry (BANKED here per the v30 brief's duty; the SEVEN v29
numbers verbatim — the brief is their only carrier until this bank)

- v29 re-pin `c191ab2` hook real 2m51.656s = 171.7s green (22nd observed; identity-only solo re-pin at PATH A open; box quiet, no concurrent discover, game seat live upstream)
- v29 M1 `6ba7079` hook real 2m51.963s = 172.0s green (23rd; docs-only 2-file family-block+mirror content commit; box quiet)
- v29 commit A `1182cc6` hook real 2m53.751s = 173.8s green (24th; 2 new review files; box quiet)
- v29 commit B `151d8db` hook real 3m10.491s = 190.5s green (25th; 3 review files; box quiet)
- v29 re-pin `c5e7168` hook real 4m9.690s = 249.7s green (26th; identity-only solo re-pin, post-discover same session; upstream hopped AGAIN inside the hook window)
- v29 re-pin `80b74d8` hook real 4m16.988s = 257.0s green (27th; identity-only solo re-pin, post-discover, box otherwise quiet; inside the frozen band max 268.3s)
- v29 push: total-hook real 209m45.326s = 12585.3s at 693 tests ("v29 PATH A close"; window = exactly 6 commits; game-two seat live - 3 identity hops absorbed in-session; foreign imagesmith seat process live on the box mid-window - confounds NAMED, not measured; first-attempt green, zero mid-hook drift; 434 advisory WARN; headroom 41.7%)

Reading (observed points only, never a trend): total-hook at 693 spans
10329.5–12873.5 across TEN points (11205 / 10722.7 / 10448.3 / 12873.5 /
12802.7 / 10969.7 / 10329.5 / 11081.1 / 12204.7 / 12585.3); v23's 12873.5 =
40.4% headroom remains the worst; seat-live labels sit on highs, the
minimum, and interior points. Post-adoption clean windows n=9, newest-first
sizes 6/2/1/1/1/4/1/1/4.

**COMPOSITION BREAK (named per the brief's duty):** the 693-test band
CLOSES at those ten points. v30 adds `tests/test_track_v1.py` (55 tests) —
the first suite-composition change since v21 — so v30's push lands at
N=748 tests (discover-measured: `Ran 748 tests in 3067.871s` / `OK` /
EXIT:0; 693 + 55 exactly accounted by the new module) and is labeled
"first point at 748 tests", never pooled with the closed 693 band. The new module enters the pre-commit FAST
tier (fast_gate derives the tier as all test modules minus the frozen SLOW
list); measured hook effect ≈ +1s (the module runs in ~0.6s) — v30 hook
reals sit inside the prior 160–190s quiet-box shape.

v30's OWN reals (each condition-labeled; they ride the session receipt and
the v31 brief per the standing structural-lag mechanism):

- v30 re-pin `7e66fbc` hook real 2m50.042s = 170.0s green (28th observed; identity-only solo re-pin at session open; box quiet, no concurrent discover, game seat live upstream)
- v30 commit A `474c7d1` hook real 2m53.691s = 173.7s green (29th; 10-file evidence+review commit incl. two multi-MB `-text` track blobs; box quiet)
- v30 commit B attempt 1 hook real 3m4.370s = 184.4s RED (fast-gate red, not drift: three sibling manifests pin the consumer's sha256 — the pre-registered consequence class, wider than pre-registered; resolved by their own tools' re-banks inside the same change set)
- v30 commit B `7b0a2dc` hook real 2m58.784s = 178.8s green (30th; code + 55-test module + four manifest re-banks; box quiet; first hook run WITH test_track_v1 in the fast tier; two `WARN [complexity]`/`WARN [crap]` lines = warn-metrics, not gates, v22–v29 precedent)
- v30 commit C + push reals land after this file and ride the session receipt (composition-break label carried there).
