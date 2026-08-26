# E3a capture-contract spec — cross-seat intake review verdict (v29)

**Answer first: PASS on all eight spec-facing bars (B1–B8) and on the
reply itself (B9) — the s81 spec is fence-clean, deterministic without
touching simulation identity, schema-sufficient against the banked
sufficiency criterion, boundary-correct in both directions, and
provenance-complete with its one weakening (commit → best-effort)
argued strictly stronger (fingerprint-first, the v17 W6 trap this repo
banked itself). Two under-specified semantics at the s81 blob (roster
presence across death/respawn windows; tick-range domain) carry no
open ask — both are since PINNED upstream by the parked s84 delivery
(pin text read + md5-verified; parser-fitness verdict rides the next
intake sprint). The at-speed K-S watch item becomes MEASURED-claim-
capable end-to-end; protocol-vs-viewport becomes measurable as a
declared-viewport read with the live-camera-true half named uncovered.
The reply is drafted and BANKED (`reply-draft.md`); it is sent only on
recorded owner approval. Zero pixels, zero exports, zero register
movement; C6 stays OPEN.**

Review object: game-two
`docs/superpowers/specs/2026-08-26-e3a-capture-contract.md` at
`0f3e9e5`, git-blob md5 `f531709a41e89aea5cf4409cc058a817`
(md5-verified over blob bytes; full identity chain in
`spec-received.md`). Rubric pre-registered with every verdict cell
NULL at commit A (`1182cc6`); this file + the judged rubric + the
reply draft land together at commit B. Session model
`us.anthropic.claude-fable-5` (verified from `PI_MODEL`). Council seat
cross-vendor (Kimi K2.5), one consolidated adversarial call: brief
8,564 bytes inlining the fence, spec section 5 essentials, all draft
verdicts, and the reply draft verbatim; `--max-tokens 3000`; response
file-redirected, read as UTF-8; 2,087 in + 2,006 out = 4,093 tokens,
within the 8k budget; reconciliation below.

## The bars, judged (full line-cited evidence: `rationale.md`)

| # | Bar | Verdict |
|---|---|---|
| B1 | Fence conformance | PASS — every producer offline or close-time/host-side/env-gated; P3 refused with the consequence named |
| B2 | Deterministic capture w/o changing sim identity | PASS — existing input seam; identity in the manifest; double re-execution gate = the intake attestation; zero sim-code moves |
| B3 | Schema sufficiency | PASS with u1 — all draw reads + mapping indexes ride v1; four corrections sound; exclusions starve no register item |
| B4 | Watch-item coverage | PASS — K-S MEASURED-capable; viewport = declared-model read, live-camera half named uncovered; brackets serve neither, named |
| B5 | Boundary / one-way | PASS — mail + sha256 delivery; read-only + copy-under-intake; the draft-1 constants wrinkle RESOLVED, not inherited |
| B6 | DEF-3 packaging + adjudication env | PASS — declared 165 Hz per verdict; packaging law stays repo-side, no conflict |
| B7 | Capture provenance | PASS with a1 — fingerprint-first argued stronger; attestation-trust is the banked intake law's own design |
| B8 | Ratification-shape conformance | PASS — two recorded deviations (headless re-executor; fingerprint-over-commit), both grill-defended; zero silent deviations |
| B9 | Reply boundary | PASS — receipt-shaped, asks-only, C6 untouched; council sentence-scan CONFIRMED clean |

## Findings (typed per the pre-registered classes)

- **u1 (under-specification, since pinned upstream):** roster
  presence semantics + legal tick-range domain unstated at the s81
  blob; pinned by the parked s84 delivery (union roster; range
  1..ticks_executed). Pin text verified-read; parser fitness
  unverified — rides the next intake sprint. No open ask.
- **a1 (adaptation, queued):** consumer adaptation set to v1 —
  fingerprint-first intake identity (game_commit best-effort),
  tick_ms 16.67, per-kit constants map + selection rule, px pair
  dropped (lunge stays mapping-side), `possessed`, RUNTIME intake
  path, s84 roster-union/range semantics. The parser is the
  disposable half; it adapts to the pin, never the reverse.
- **n1 (noted):** delivery-mail summary checked against the blob —
  faithful; no disagreement found (Q1–Q7, px drop, fence, mechanics).
- **n2 (noted):** spec delta `0f3e9e5` → `2627ed0` = ONE additive
  terminal-digest table row (T1 amend, s83); section 5 byte-unchanged
  (`676e9782f613d9a6264d43e5128aacd4`) — the s84 "unchanged since the
  s81 mail" claim verified true for the pinned section.
- **n3 (noted):** the upstream review-gate MAJOR (false
  constants-source claim) was corrected before delivery; B3/B5 lean
  on the corrected text, and the correction also fixed a latent
  one-way wrinkle originating in OUR draft-1 (which sourced
  `lunge_offset` from this repo's manifest).

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

Returned verdicts: Q1 UNCERTAIN, Q2 CONFIRMED, Q3 REFUTED, Q4
REFUTED, Q5 CONFIRMED. Per the v12–v24 precedent every adverse claim
was re-verified against primary bytes before folding:

1. **Q3 ("at-speed measurability REFUTED: locating the hold needs the
   dropped windup_px/active_px; no windup_frames constant per attack
   type exists") — the refutation is itself REFUTED on primary
   bytes.** The px pair are DRAW OFFSETS (lunge displacement -3/+6,
   `render-reference.json` lunge_offset), never timing; phase timing
   rides `windup_frames`/`active_frames`/`recovery_frames` +
   `step_frames`, which ARE the v1 per-kit constants — present in the
   very schema line the brief quoted. `state_frames` is positional by
   draft-1's own banked semantics ("phase index into =
   pinned_phase_frames − state_frames"), machine-proved by
   `track_recompose --check` (340/340 lane_tick equality). The
   k0 hold = the active phase: `attack_state == "active"` locates it;
   state_frames + per-kit active_frames index within it. An instance
   of the banked precedent: under adversarial framing, reviewers
   assert unverified precision. B4's PASS stands; ADOPTED anyway: the
   judged B3/B4 evidence now spells the exact index chain and names
   the px pair as draw constants.
2. **Q4 ("'superseded by parked s84' is temporal sleight-of-hand —
   you assume resolution you haven't verified") — premise wrong,
   kernel ADOPTED.** The premise ("you have not verified s84's
   content") is false — the s84 mail bytes were read and md5-verified
   this session; PARKED means the DELIVERY (track copy, intake,
   parser adaptation, s84's own receipt) is unprocessed, not that the
   text is unread. But the kernel is real: "superseded" smuggled an
   unverified claim — the pin's TEXT is verified, its FITNESS for our
   parser is not. ADOPTED as wording law: "superseded" → "since
   pinned upstream (pin text read + md5-verified; parser-fitness
   verdict rides the next intake sprint)" in the rationale, this
   verdict, and the reply draft. The claim got smaller; the split got
   explicit.
3. **Q1 (rubric completeness UNCERTAIN: windowing semantics + the
   verification.json trust delegation) — both kernels ADOPTED as
   named evidence; no bar moved post-registration.** Windowing:
   covered by B3 + u1 all along (`frame` is the engine's
   session-absolute counter; `state_frames` self-describes mid-phase
   starts — draft-1's own adopted finding), now NAMED explicitly in
   the judged B3 cell. Trust delegation: the banked intake law
   ITSELF delegates re-execution to the game seat ("this repo does
   not run game code", design section 5) while member-hash
   verification stays ours at intake — now NAMED in the judged B7
   cell. Adding a post-hoc bar would have broken pre-registration;
   naming where existing bars carry the kernels does not.
4. **Q5 (biggest unthought risk: "chain-hash equality is not visual
   fidelity; the verification gate does not cover your adjudication
   standard") — CONFIRMED as stated and ADOPTED as the two-layer
   split, which is the banked architecture made explicit.** The chain
   gate proves the STATE STREAM's identity; the visual layer is the
   declared-model recomposition, disclosed per design section 6.1
   ("Captured state is real; frame selection is the proposal's").
   "MEASURED" in B4 = measured-under-declared-mapping with EXP-class
   disclosure — the same disclosure every banked lane carried;
   recomposition is per-tick pure (no interpolation exists in the
   pipeline); display-chain effects are exactly the DEF-3/(h) class,
   already named uncovered. The judged B4 cell now states the split
   in so many words.
5. **Q2 (reply boundary) — CONFIRMED clean**, sentence-by-sentence
   scan quoted in the judged B9 cell. Non-delta.

Net: one REFUTED re-verified false on primary bytes (Q3 — the claim
stands), one REFUTED reduced to a real wording kernel (Q4 — adopted),
two UNCERTAIN kernels adopted as explicit evidence naming (Q1), one
CONFIRMED risk adopted as explicit disclosure language (Q5). Every
adoption made a claim smaller or more explicit; no bar moved, no bar
weakened, all adoptions folded before this commit.

## HFO gate (accuracy vs presentation, separately)

- **reply-draft.md** (human-async mail, owner + game seat audience):
  Accuracy — every md5 computed this session over the named bytes;
  every claim traceable to the judged rubric; the u1 split states
  exactly what is and is not verified; PASS. Presentation — receipt
  lines first (the thing the spec asked for), findings typed and
  numbered, non-claims explicit, register technical-concise per the
  house style, no filler; PASS.
- **verdict.md (this file)** (owner-facing review doc): Accuracy —
  answer-first headline claims only what the judged cells carry;
  council reconciliation quotes verdicts and names which premise
  failed against which primary; the eleven carried numbers below are
  byte-copied from the v29 brief, never re-derived; PASS.
  Presentation — truncated pyramid (verdict → bars → findings →
  reconciliation → carry), machine table over the bars, typed
  findings, no unlabeled precision; PASS.

## Non-claims

No adjudication of any lettered item — no RUNTIME evidence was
consumed (the s84 tracks are parked, not intaken). No integration ask
and no integration schedule; C1–C5 MET, C6 OPEN doubly gated,
untouched. No schedule claim on T1–T3 (owner-paced; the spec says the
same). Nothing here re-adjudicates or softens a banked verdict. No
cadence analysis beyond the verbatim carry block below (the four
banked cadence-v24 answers stand uncontradicted; no trend, no
comparison, no new corpus). Zero pixels, zero exports, mechanical ids
throughout.

## Mail and pin status (v29)

- Inbox at step 0: spec mail (s81) + hub family-block mail (s83),
  both md5-exact vs the brief; s84 T2 delivery present as a
  mid-v28-window arrival (md5 `98fb30332c8a84023eb0251de7f5757b`,
  6,713 B, pure LF) — PARKED, recorded, unprocessed; its expected
  receipt rides the next intake sprint.
- Spec mail archived to done/ at recording; hub mail archived after
  the post-push receipt; reply mail SENT only on recorded owner
  approval, else banked unsent (status in the session receipt).
- Pins: one identity-only hop absorbed at step 0
  (`87aefb4e → 56faba85`, all five pinned blobs byte-identical,
  20/20 constants + attack_timing green, mechanical re-pin
  `c191ab2`); asset_gate exit 0 after the re-pin. M1 landed the
  2026-08-24 family block (span md5 `993fb261a58066039285275be1047253`)
  + bare CLAUDE.md mirror (`e7ffe48362bb9590a10aa47958dd5818`), both
  verified at the HEAD blob (`6ba7079`).

## Cadence carry (BANKED here per the v29 brief's duty; the eleven
numbers verbatim — the v24–v28 carry chain terminates at this bank)

Carried numbers (v24–v28; five consecutive PATH B closes banked none;
structural one-sprint lag, banked law):

- v24 bank-commit hook real: 4m3.982s = 244.0s green (16th observed green point - the banked corpus froze at n=15, max 268.3s; condition: post-discover, box otherwise quiet)
- v24 push: total-hook real 213m22.661s = 12802.7s at 693 tests ("cadence-corpus close"; window = exactly 4 commits; game-two seat live, 5 upstream commits in the ~3.6h window - confound NAMED, not measured; headroom 40.7% vs 21600s)
- v25 re-pin commit hook real: 2m46.338s = 166.3s green (17th; box quiet, no concurrent discover, single-re-pin PATH B; 27.7% of the 600s budget)
- v25 push: total-hook real 182m49.739s = 10969.7s at 693 tests ("v25 pins-only close"; window = exactly 1 commit; game-two seat live and MID-EDIT on both re-pinned files - confound NAMED, not measured; first-attempt green, zero mid-hook drift; headroom 49.2%)
- v26 re-pin commit hook real: 2m39.842s = 159.8s green (18th; single-re-pin PATH B, no concurrent discover, game-two seat live upstream; 26.6% of budget; observed floor - 0.2s UNDER the frozen n=15 band floor of 160s; the frozen corpus stays frozen - post-bank carry point, not a band rewrite)
- v26 push: total-hook real 172m9.521s = 10329.5s at 693 tests ("v26 pins-only close"; window = exactly 1 commit; game-two seat live upstream - confound NAMED, not measured; first-attempt green, zero mid-hook drift; headroom 52.2%; minimum of the observed points)
- v27 re-pin commit hook real: 3m0.815s = 180.8s green (19th; single-re-pin PATH B, no concurrent discover, post-drift-absorb; 30.1% of budget)
- v27 push: total-hook real 184m41.120s = 11081.1s at 693 tests ("v27 pins-only close"; window = exactly 1 commit; game-two seat live, 4 upstream commits in the ~3.1h window - confound NAMED, not measured; first-attempt green, zero mid-hook drift; headroom 48.7%)
- v28 re-pin commit 1 hook real: 3m8.122s = 188.1s green (20th; single-re-pin PATH B, identity-only hop, no concurrent discover, box quiet; 31.4% of budget)
- v28 re-pin commit 2 hook real: 4m21.483s = 261.5s green (21st; second solo re-pin same session, post-content-hop absorb, box quiet; 43.6% of budget; inside the frozen band max 268.3s)
- v28 push: total-hook real 203m24.679s = 12204.7s at 693 tests ("v28 pins-only close"; window = exactly 2 commits; game-two seat live, 5 upstream commits mid-session - confound NAMED, not measured; THIRD-attempt green, attempts 1-2 killed by session aborts not gate reds, attempt 3 PowerShell-detached; zero mid-hook drift; 434 advisory WARN; headroom 43.5%)

Reading (observed points only, never a trend): total-hook at 693 now
spans 10329.5-12873.5 across nine points (11205 / 10722.7 / 10448.3 /
12873.5 / 12802.7 / 10969.7 / 10329.5 / 11081.1 / 12204.7); v23's
12873.5 = 40.4% headroom remains the worst. Seat-live labels sit on
highs, the minimum, and interior points - the label never sorts the
points. Post-adoption clean windows n=8, newest-first sizes
2/1/1/1/4/1/1/4.

The carry chain shrinks to zero at this bank. v29's OWN reals (every
commit hook + the push, each condition-labeled) start the new chain:
they ride the v29 close receipt and the v30 brief — new numbers only,
per the standing structural-lag mechanism. Banked so far this
session: re-pin `c191ab2` hook real 2m51.656s = 171.7s green (22nd;
identity-only solo re-pin, PATH A session, box quiet, no concurrent
discover, game seat live upstream); M1 `6ba7079` hook real 2m51.963s
= 172.0s green (23rd; docs-only 2-file content commit, box quiet);
commit A `1182cc6` hook real 2m53.751s = 173.8s green (24th;
docs-only 2-new-file review commit, box quiet). Commit B's hook real
and the push total land after this file and ride the receipt.

## Stop

Sprint 29 stops here: one identity-only re-pin, the owner-ruling-v2
family-block resync + bare mirror, one spec recorded verbatim, one
pre-registered rubric judged PASS across nine bars with council
reconciled and adoptions folded before banking, one reply drafted and
banked pending owner approval, the eleven carried cadence numbers
banked verbatim. Carried to v30+: the s84 T2 delivery intake (track
copy under the intake gate + parser adaptation + its owed receipt),
the consumer adaptation queue a1, the causal cadence question
(re-arms on a multi-commit feature window), v29's own post-bank reals
riding the receipt, and the watch items now instrument-routed
(at-speed K-S measurable end-to-end once RUNTIME bundles are
intaken; live-camera-true viewport + item (h) display-chain half
named uncovered).
