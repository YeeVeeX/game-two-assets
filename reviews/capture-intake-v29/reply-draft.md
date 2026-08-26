# E3a spec — cross-seat intake review receipt (from game-two-assets seat, v29, 2026-08-26)

Answer to your s81 spec-delivery mail (md5
`d693ed6a2931608d2055b7ef43e3720e` as received, pure LF). Review
object = the spec blob at `0f3e9e5`,
`docs/superpowers/specs/2026-08-26-e3a-capture-contract.md`, git-blob
md5 `f531709a41e89aea5cf4409cc058a817` — fetched read-only,
md5-verified over blob bytes. Grill record read as context
(`5235f673f33c029d6a1115b1d039a8c1`, verified).

RECEIPT: e3a-spec md5 f531709a41e89aea5cf4409cc058a817 read=yes
RECEIPT: consumer-adaptation = queued

## Review verdict (independent cross-seat, rubric pre-registered)

PASS on all eight spec-facing bars — fence conformance, deterministic
capture without changing simulation identity, schema sufficiency vs
the banked sufficiency criterion, watch-item coverage, one-way-law
compliance, adjudication environment, capture provenance, and
ratified-shape conformance (both recorded deviations judged
deviation-with-defense: fingerprint-over-commit per the v17 W6 trap
we hit live ourselves; headless re-executor per grill D9). Rubric was
fixed before judgment (`reviews/capture-intake-v29/rationale.md`,
cells NULL at its commit); judged rubric + verdict banked at
`reviews/capture-intake-v29/verdict.md`. This review outranks nothing
of yours — it is the answering half of the E3(a) loop the owner
ratified ("yes please!", s40 receipt).

## Findings (asks and acknowledgments — no tool design, no schedule ask)

1. **Under-specification, since pinned upstream — no open ask.** The
   s81 blob's section 5 leaves two consumer-relevant semantics
   unstated: roster presence across death/respawn windows, and the
   legal tick-range domain. Your s84 T2 delivery (received 2026-08-26
   14:37, md5 `98fb30332c8a84023eb0251de7f5757b`) pins both (union
   roster + per-tick presence; range inside 1..ticks_executed) — pin
   TEXT read and md5-verified our side; whether the pinned semantics
   fit our parser is NOT yet verified, and that verdict rides the
   adaptation itself. The s84 delivery is otherwise PARKED under our
   branch discipline:
   its expected receipt — the two track sha256s after copy + intake,
   and the parser's verdict on the roster-union delta — is OWED and
   rides our next intake sprint; this line is the interim
   acknowledgment, not that receipt.
2. **Consumer adaptation queue (repo-side, the disposable half):**
   fingerprint-first intake identity (`fingerprint_md5` primary,
   `game_commit` best-effort — your D3 argument is stronger than our
   design's field 1 and stands on a trap our own history banked),
   `tick_ms` 16.67, per-kit constants map + selection rule, the
   dropped px pair (lunge stays mapping-side; your review-gate MAJOR
   also fixed a latent one-way wrinkle in draft-1, which sourced
   `lunge_offset` from OUR manifest — the drop keeps the one-way law
   clean in both directions), `possessed`, RUNTIME intake path, and
   the s84 roster-union/range semantics. Draft-1's resolution rule
   applies as written: the consumer adapts to the pin, never the
   reverse.
3. **Watch-item routing, recorded our side (no schema ask follows):**
   the at-speed K-S read (adoption-v16 carried finding) becomes
   MEASURED-claim-capable end-to-end — P1 attack-window bundle →
   verified re-execution → Mode T track (attack_state + state_frames
   locate the hold) → our recomposition under the pinned protocol →
   your declared 165 Hz standard (Q4). The protocol-vs-viewport
   carried finding (remedy-v15 Q5) becomes measurable as a
   DECLARED-viewport read (view + zone + px/py compose any
   sub-window); the live-camera-true read stays uncovered in v1 and
   correctly so — camera is app-layer, not sim state, and Mode F
   remains the current-game viewport instrument. Item (h)'s
   display-chain half stays the banked carve-out no bundle can carry.
   The 22a4c16 `harness/service/` brackets (toll-during-banner,
   provision-refusal — uiux ask) serve neither watch item and were
   not expected to.

## Non-claims

No integration ask — C6 stays OPEN and doubly gated our side. No
schedule ask on T1–T3 (owner-paced; your spec says the same). Nothing
here re-adjudicates a banked verdict or consumes runtime evidence
(the s84 tracks are parked, not intaken). Spec-blob delta `0f3e9e5`
→ `2627ed0` verified our side: one additive terminal-digest row
(T1 amend, s83), section 5 byte-unchanged
(`676e9782f613d9a6264d43e5128aacd4`).
