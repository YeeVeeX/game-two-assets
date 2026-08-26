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
| B1 | Fence conformance | Every producer/tool path in the spec satisfies the ratified fence verbatim (session-end only, never during play, zero per-tick cost, either seat). Any per-tick live-play cost or during-play recording = FAIL. P3's disposition must respect the fence's plain reading. | **PASS** — P1 "Offline tooling — zero live-play surface by construction" (§4); P2 "env-gated GAME_BUNDLE_DUMP=1, default OFF... off = no branch in play; the env is read once at the close seam", host-side only, failed dump "warns ONE line and never disturbs the quit path" (§4); P3 REFUSED under the fence's plain reading with the consequence named honestly ("solo live sessions produce no bundles in v1", grill D1) — stricter than our own design's env-gated P3 proposal; grill fence audit: "no producer records during play; P2 adds no retention and no per-tick branch; all analysis is offline" |
| B2 | Deterministic capture without changing simulation identity | Scripted input via the existing input seam; seed + tick pinning carried in bundle identity; machine-checked re-execution identity (a byte-stable verification gate the intake law can cite as producer attestation); ZERO World/creature/renderer code changes in any ticket. | **PASS** — P1 rides the existing runner path, folds masks per executed tick, "Protocol.mask covers all 12 game actions" (§4); manifest carries seed/seats/ticks_executed/digest_version/digest_every, preconditions verbatim (§2-§3); "TWO fresh re-executions; both chains must equal each other AND the recorded chain" with the receipt made "the 'producer's attestation' their intake gate names" (§4) — directly closes design §2.3 audit item 1 and the §5 attestation requirement; "no sim/renderer code moves in any ticket" (§6; T3 touches the net-session close seam only, not sim state); Q2's framebuffer non-promise lands on our design's own fallback ("state tracks and digests are the identity anchor if GL rasterization differs", design §2.3 item 2) |
| B3 | Schema sufficiency (the open-Q1 pin vs the sufficiency criterion) | Every renderer-draw read and every declared-mapping index rides v1 fields; each of the four corrections vs draft-1 is sound against engine facts this repo's banked docs already cite; named exclusions don't starve any of the sixteen register items' `capture_requirements`. | **PASS with u1** — draw reads all ride: px/py, facing, attack_state, current_action per tick; faction in the roster list; `possessed` ADDED (a draw read at HEAD). Mapping indexes all ride: tween_left/tween_total, state_frames, frame, masks, hp/iframes, zone, view. Corrections: (1) tick_ms 16.67 = the engine constant our own design §2.1 cites — draft-1's 16.666666 contradicted its own source note; (2) per-kit constants — seven kits, flat block would lie for mixed rosters; px pair dropped correctly: they are DRAW OFFSETS (lunge displacement), never timing — phase timing rides per-kit windup/active/recovery_frames + step_frames, all IN the v1 constants; the mapping's lunge model stays repo-side (render-reference pin), which also fixes draft-1's latent one-way wrinkle; (3) possessed additive + useful; (4) RUNTIME class = draft-1's own class law made unconditional. Exclusions: no register row in draft-1's 16/16 table reads any excluded field ((f) rides iframes + frame — carried). Windowing semantics (council Q1 kernel, named explicitly): `frame` is the engine's session-absolute counter and `state_frames` self-describes mid-phase starts — draft-1's own adopted finding, so windowed legality starves no index. u1 (under-specification): roster presence across death/respawn windows + legal tick-range domain unstated at the s81 blob; both since PINNED upstream by the parked s84 delivery (pin text read + md5-verified this session; the pin's fitness for our parser is NOT verified — that verdict rides the next intake sprint's adaptation). No open ask. |
| B4 | Watch-item coverage | For each of: at-speed K-S, protocol-vs-viewport, shade double-duty, DEF-3 packaging — state which spec instrument (producer + track fields + declared display) makes the claim MEASURED, or name it uncovered. Map the 22a4c16 brackets (toll-during-banner, provision-refusal, `harness/service/`, uiux ask) to watch items served, or state that neither serves any. An honest "uncovered, out of v1 scope by construction" passes; a papered-over gap fails. | **PASS** — **at-speed K-S**: MEASURED-claim-capable end-to-end: P1 attack-window bundle → double-run-verified re-execution → Mode T track (attack_state == active locates the k0 hold; state_frames + per-kit active_frames index within it; the px pair is a mapping-side draw constant, never a timing input) → repo recomposition (native + integer-zoom 1/60 s APNG, design §6.2) → declared 165 Hz standard (Q4, satisfies §6.5 true-60). Two-layer split stated (council Q5 kernel): the chain gate proves the STATE STREAM's identity; the visual layer is the declared-model recomposition, disclosed per §6.1 ("Captured state is real; frame selection is the proposal's") — "MEASURED" = measured-under-declared-mapping, the same EXP-class disclosure every banked lane carried; recomposition is per-tick pure (no interpolation exists in the pipeline). **Protocol-vs-viewport**: measurable as a DECLARED-viewport read (view + zone + px/py compose any sub-window); the live-camera-true read is UNCOVERED in v1 and named — camera is app-layer, not sim state; Mode F remains the current-game viewport instrument. **Shade double-duty**: at-speed half rides the same K-S windows (same fields); the authoring half is not a capture question. **DEF-3 packaging**: viewing-protocol law stays repo-side (design §6.2, adoption-v16); Q4's per-verdict display declaration is compatible; not a field concern. **Brackets**: 22a4c16 = `harness/service/toll_during_banner.json` + `provision_refusal_bracket.json`, "(uiux ask, non-wall)" — a service-capture lane for the uiux seat; NEITHER serves any watch item, and nothing in E3a claims otherwise. **Uncovered, named without papering**: live-camera-true viewport; item (h)'s ≥120 fps display-chain half (design's own "no bundle can carry" carve-out). |
| B5 | Boundary / one-way compliance | Bundles stay game-side and gitignored; delivery = mail + sha256s; this seat reads read-only and copies under its intake gate; nothing game-side writes into this tree; NO game tool reads an assets-repo manifest (the draft-1 constants-source wrinkle must be resolved, not inherited). | **PASS** — §2/D2: bundles gitignored, outside fingerprint + DataStore (s55 twin law structural); §6: "Delivery = a MAIL naming bundle path + manifest sha256; the assets seat reads this worktree read-only... Nothing game-side ever writes into their tree (seat-lease law); game-two never depends on their repo (one-way, both directions)"; the wrinkle RESOLVED: "no game tool ever reads an assets-repo manifest" (§5 correction 3) — the review-gate MAJOR's px-pair drop keeps the law clean in both directions; gitignored-artifact grounding = manifest sha256s + verification receipt, consistent with design §5 |
| B6 | DEF-3 packaging + adjudication environment | The adjudication display standard is declared per verdict (design section 6.5); nothing in the spec conflicts with the pinned-protocol viewing law (native + integer zoom, no browser resampling); packaging law explicitly stays repo-side. | **PASS** — Q4: "adjudication display standard is ours (165 Hz primary), declared per verdict" — satisfies §6.5's declared-display + true-60 requirement (S0-J2's 59 Hz seat excluded by the same law); the spec never touches artifact packaging/viewing, so the pinned protocol (resampling "amplifies percepts, it does not create bytes") stays wholly repo-side with no conflict |
| B7 | Capture provenance | Bundle/track identity carries: run identity (fingerprint and/or commit — if commit is weakened, the replacement must be argued stronger), seed, seats, tick range/count, schema version, digest version + cadence, producing-tool identity + invocation, machine class, member hashes; production manifest immutable; verification receipt separate. | **PASS with a1** — manifest: bundle_id, mode, produced_at, producer (tool identity + invocation line), `fingerprint_md5` REQUIRED, `game_commit` best-effort, digest_version, digest_every, seed, seats, ticks_executed, end_reason, `machine` ("stated at the source instead of derived" — our §5 intake field answered directly), members sha256 (§2); track: schema_version/class/provenance.bundle_id + explicit tick range at emission (§5); write-once manifest + separate verification.json (D7). Commit weakened to best-effort but the replacement is argued STRONGER on a trap this repo banked itself (v17 W6: "a commit SHA lies twice: uncommitted drift... autocrlf checkouts of the SAME commit differ byte-wise") — bar's own condition met. Attestation-trust named plainly (council Q1 kernel): delegating re-execution to the game seat is the banked intake law's OWN design ("this repo does not run game code", design §5); member-hash verification stays OURS at intake when bundles arrive. a1 (adaptation): intake manifest goes fingerprint-primary, game_commit recorded-when-present. |
| B8 | Ratification-shape conformance | The spec matches the s40 ratified build shape; every deviation is RECORDED and defended in the grill (deviation-with-defense passes; silent deviation fails). | **PASS** — shape elements: session-end bundle ✓ (P2 any end reason, host-side ✓ = the ratified council-Q2 routing); seed ✓ preconditions ✓ per-tick consumed masks ✓; digest window → FULL chain (within design §4 field 5's own option space, strengthening, D4); commit → fingerprint REQUIRED + commit best-effort (recorded deviation, defended D3); "on the existing replay runner" → HEADLESS re-executor (recorded deviation named in §4 AND the mail, defended D9 — the runner exists for pixels, Mode T needs none; Mode F stays on the runner unchanged). Zero silent deviations found. |
| B9 | Reply boundary (judged on `reply-draft.md`, not the spec) | The reply answers ONLY the expected receipt + rubric findings as asks; zero sentences design the tool; zero integration asks; C6 untouched; digest-stamped with the spec mail md5. | **PASS** — the reply carries the two expected RECEIPT lines verbatim-shaped, findings 1-3 (acknowledgment / adaptation queue / watch-item routing with "no schema ask follows"), and non-claims (C6 OPEN, no schedule ask); council Q2 scanned it sentence-by-sentence: "No sentence designs game-side tools, imposes schedule, or constitutes integration ask. CONFIRMED clean." Digest stamps present: spec mail md5 + blob md5 + s84 md5. |

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
