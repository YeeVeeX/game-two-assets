# Capture-spec intake review — rationale (v29, PRE-REGISTERED)

**Status: rubric FIXED BEFORE judging.** This file is committed with
every verdict cell NULL. Judgment happens after this commit, line-cited
against the spec bytes; the judged copy + `verdict.md` land in a later
commit (the commit-A/commit-B discipline every calibration sprint used).

## Review object and identity

- The contract text: game-two
  `docs/superpowers/specs/2026-08-26-e3a-capture-contract.md` at
  `0f3e9e5`, git-blob md5 `f531709a41e89aea5cf4409cc058a817` —
  fetched read-only, md5-verified (see `spec-received.md`).
- The delivery mail (md5 `d693ed6a2931608d2055b7ef43e3720e`) is the
  received artifact; where mail summary and spec blob disagree, the
  BLOB governs and the disagreement is itself a finding.
- Context, not review objects: the grill record at `0f3e9e5`
  (`5235f673f33c029d6a1115b1d039a8c1`); the spec blob at `2627ed0`
  (verified delta: one additive terminal-digest row, section 5
  byte-unchanged); the PARKED s84 T2 delivery mail
  (`98fb30332c8a84023eb0251de7f5757b` — recorded, unprocessed this
  sprint by brief order).

## Role boundary (pre-registered, brief A1-A3)

The instrument is the game seat's host-side build. This review outputs
rubric verdicts, field-list gap asks, and packaging-law citations —
never tool internals, never writes into `../game-two`, never capture
tooling here. A FAIL on any bar routes as a mailed finding/ask (schema
bumps are additive and game-seat-owned per the spec's own law), never
as a block from this side. The reply mail is drafted and banked; it is
SENT only with owner approval recorded verbatim in-session. C6 stays
OPEN regardless of every verdict below; a review is not an integration
ask.

## Sources of law (each bar cites only these)

- E3(a) ratification: `done/from-game-two-v19-brainstorm-receipts.md`
  (s40) — owner-ratified verbatim "yes please!"; fence "session-end
  only, zero per-tick cost"; build shape "session-end bundle (commit +
  seed + preconditions + per-tick consumed masks + digest window, from
  the already-retained lockstep queues) + offline state-track
  re-execution on the existing replay runner; P2 dump routed host-side
  only"; "Your open question 1 (state-track field list) gets pinned by
  this seat at tool-spec time."
- Banked capture design: `docs/replay-capture-design.md` (v12) — the
  deterministic spine, the bundle contract proposal (section 4), the
  intake law (section 5: manifest hashes + producer attestation; this
  repo does not run game code), the adjudication law (section 6:
  pre-registered bars, native + integer-zoom artifacts, declared
  display, mapping version-pinning), the weak-seat law.
- Draft-1 schema: `docs/state-track-schema.md` (v13) — the sufficiency
  criterion ("every input the renderer's creature draw reads plus
  every index the declared pose-selection mapping needs"), the field
  table, the 16/16 register-coverage table, and its own resolution
  rule: "if the pinned schema differs from this draft in any way, this
  repo adapts the consumer to the pinned shape — never the reverse."
- Watch items (must become MEASURABLE): adoption-v16 verdict — "the
  at-speed read of the selected band (does the shade mouth read
  correctly at 60 tps?) remains unmeasured, part of the same
  owner-sequenced capture class as v15's protocol-vs-viewport carried
  finding"; remedy-v15 council Q5 — "protocol-vs-player-viewport gap —
  this selection is proven at the pinned adjudication standard, not in
  a runtime viewport; the banked capture design remains the instrument
  for the shipped read"; shade double-duty (remedy-v15 Q5(i)); DEF-3
  packaging (adoption-v16: resampled viewing "amplifies percepts, it
  does not create bytes" — pinned-protocol viewing law).
- Boundary law: AGENTS.md invariant 1 (one-way boundary) + the family
  block (seat-lease, mail-and-md5).

## Bars (all-must-pass for a PASS headline; verdicts NULL here)

| # | Bar | What passes it (measurable) | Verdict |
|---|---|---|---|
| B1 | Fence conformance | Every producer/tool path in the spec satisfies the ratified fence verbatim (session-end only, never during play, zero per-tick cost, either seat). Any per-tick live-play cost or during-play recording = FAIL. P3's disposition must respect the fence's plain reading. | NULL |
| B2 | Deterministic capture without changing simulation identity | Scripted input via the existing input seam; seed + tick pinning carried in bundle identity; machine-checked re-execution identity (a byte-stable verification gate the intake law can cite as producer attestation); ZERO World/creature/renderer code changes in any ticket. | NULL |
| B3 | Schema sufficiency (the open-Q1 pin vs the sufficiency criterion) | Every renderer-draw read and every declared-mapping index rides v1 fields; each of the four corrections vs draft-1 is sound against engine facts this repo's banked docs already cite; named exclusions don't starve any of the sixteen register items' `capture_requirements`. | NULL |
| B4 | Watch-item coverage | For each of: at-speed K-S, protocol-vs-viewport, shade double-duty, DEF-3 packaging — state which spec instrument (producer + track fields + declared display) makes the claim MEASURED, or name it uncovered. Map the 22a4c16 brackets (toll-during-banner, provision-refusal, `harness/service/`, uiux ask) to watch items served, or state that neither serves any. An honest "uncovered, out of v1 scope by construction" passes; a papered-over gap fails. | NULL |
| B5 | Boundary / one-way compliance | Bundles stay game-side and gitignored; delivery = mail + sha256s; this seat reads read-only and copies under its intake gate; nothing game-side writes into this tree; NO game tool reads an assets-repo manifest (the draft-1 constants-source wrinkle must be resolved, not inherited). | NULL |
| B6 | DEF-3 packaging + adjudication environment | The adjudication display standard is declared per verdict (design section 6.5); nothing in the spec conflicts with the pinned-protocol viewing law (native + integer zoom, no browser resampling); packaging law explicitly stays repo-side. | NULL |
| B7 | Capture provenance | Bundle/track identity carries: run identity (fingerprint and/or commit — if commit is weakened, the replacement must be argued stronger), seed, seats, tick range/count, schema version, digest version + cadence, producing-tool identity + invocation, machine class, member hashes; production manifest immutable; verification receipt separate. | NULL |
| B8 | Ratification-shape conformance | The spec matches the s40 ratified build shape; every deviation is RECORDED and defended in the grill (deviation-with-defense passes; silent deviation fails). | NULL |
| B9 | Reply boundary (judged on `reply-draft.md`, not the spec) | The reply answers ONLY the expected receipt + rubric findings as asks; zero sentences design the tool; zero integration asks; C6 untouched; digest-stamped with the spec mail md5. | NULL |

## Finding classes (pre-registered routing)

- **defect** — spec contradicts banked law or its own cited engine
  facts → mailed as a finding (their intake law: mail it, docs-only
  triage their side).
- **under-specification** — a consumer-relevant semantic the spec pin
  leaves open → mailed as an ask; if the parked s84 delivery already
  pins it, record the pointer and fold no s84 content into judgment.
- **adaptation** — consumer-side work this pin creates repo-side →
  named in the reply as queued (draft-1's own resolution rule; the
  parser is the disposable half).
- **noted** — observations with no action owed.

## Pre-registered non-claims

Zero adjudication of any lettered item (no RUNTIME evidence is being
consumed this sprint — the s84 tracks are parked, not intaken). Zero
schedule claims on T1-T3 (owner-paced; the spec says the same). Zero
re-adjudication of banked verdicts; nothing here can soften a banked
red (design section 6.4). Zero cadence claims beyond the v29 carry
block in `verdict.md`. C1-C5 MET / C6 OPEN unchanged.
