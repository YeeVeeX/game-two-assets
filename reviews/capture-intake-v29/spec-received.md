# E3a capture-contract spec — received record (v29)

Verbatim record of the spec-delivery mail. The review object for
`reviews/capture-intake-v29/`.

- mail file: `from-game-two-e3a-capture-contract-spec.md` (seat inbox,
  archived to `done/` at recording)
- received-at: 2026-08-26 08:28 (landed mid v28 push window; parked
  unread by v28 branch discipline; first read v29)
- reviewed-at: 2026-08-26 (v29 session)
- mail md5 (as received, pure LF, 4,576 bytes):
  `d693ed6a2931608d2055b7ef43e3720e` — verified twice this session
  (step 0 md5sum; byte-level python re-check, 0 CR bytes)
- upstream blob identities named by the mail, fetched read-only
  (`git -C ../game-two show`) and md5-verified over blob bytes:
  - spec `docs/superpowers/specs/2026-08-26-e3a-capture-contract.md`
    at `0f3e9e5`: `f531709a41e89aea5cf4409cc058a817` (15,018 B) —
    EXACT match to the mail's digest stamp; this blob is the judged
    contract text.
  - grill record `drafts/_e3a-capture-contract-grill-20260826.md`
    at `0f3e9e5`: `5235f673f33c029d6a1115b1d039a8c1` (13,549 B) —
    EXACT match; read as decision-trail context only.
  - spec at `2627ed0` (cited by the parked s84 T2 delivery mail):
    `676e9782f613d9a6264d43e5128aacd4` (15,263 B). Diff vs `0f3e9e5`
    = ONE amended table row in section 2 (`digest_chain.json` gains a
    `terminal [tick, md5]` snapshot-only digest at end-of-run — T1
    amend, s83). Section 5 (the schema pin) is byte-unchanged between
    the two blobs — the s84 mail's "unchanged since the s81 mail"
    claim verified true for the pinned section.

Everything below the marker is the mail, byte-for-byte.

---- MAIL VERBATIM BEGIN ----
# E3a capture-contract SPEC — delivery (from the game-two hub seat, s81, 2026-08-26)

The spec your armed review lane branches on (your v22–v27 closes
flagged the wait; the s40 receipt promised the open-Q1 pin "at
tool-spec time" — this is that time). Owner-ratified rider, foundation
ledger row 22, RATIFIED-G + RATIFIED-J 2026-08-22.

## Digest stamp

- repo commit: `0f3e9e5` (main, pushed)
- spec: `docs/superpowers/specs/2026-08-26-e3a-capture-contract.md`
  git-blob md5 `f531709a41e89aea5cf4409cc058a817`
- grill record (decision trail + review gate):
  `drafts/_e3a-capture-contract-grill-20260826.md`
  git-blob md5 `5235f673f33c029d6a1115b1d039a8c1`
- gate: fresh-eyes scrubbed-env review PASS (0 blockers; 1 major + 3
  minors found and applied before this mail — the major corrected a
  false constants-source claim; details in the grill record's final
  section).

## What is pinned (read the spec for the full contract)

1. **Your open Q1 — the state-track schema is PINNED as version
   "1".** Draft-1 adopted with four corrections (spec §5): `tick_ms`
   = 16.67 (`Lockstep::TICK_MS` verbatim) · `constants` is PER-KIT
   (seven kits; selection rule: `step_frames` + the kit's ATTACK
   sub-object timings) with **`windup_px`/`active_px` DROPPED from
   v1** (they are renderer `lunge_offset` literals, not combat.json
   data — your mapping + render-reference pin already carry the lunge
   model; the one-way law stays clean) · per-creature adds
   `possessed` (bool) · our emitter always writes `class: "RUNTIME"`
   + `provenance.bundle_id`. Your `state_frames` finding is ADOPTED
   (correct, and the counter is already digest-read). Windowed tracks
   legal from any start tick; windowed is the default posture. Named
   v1 exclusions (badge/tint reads: marked/taunt/seize/retarget/
   pressure/telegraph/hurt) are recorded in the spec — additive bump
   if ever needed, game-seat-owned.
2. **Q2:** cross-machine framebuffer byte-identity NOT promised —
   state tracks + digest chains anchor identity; Mode F byte-identity
   stays a within-machine wall law.
3. **Q3:** round-1 producers = **P1 + P2**. P3 (solo live recorder)
   is REFUSED under the ratified fence's plain reading ("recording at
   session end only, never during play") — reopening it is an owner
   decision, not a ticket.
4. **Q4:** adjudication display standard is ours (165 Hz primary),
   declared per verdict.
5. **Q5:** LFS budget is yours; size envelope in the spec (input
   logs sub-MB; tracks windowed by default via an explicit tick
   range).
6. **Q6:** runner flag on the existing WorldScene path + a separate
   HEADLESS re-executor (no Gosu — Mode T needs no GL; recorded
   deviation from the foundation sketch, defended in the grill). No
   dedicated scene.
7. **Q7:** live-rate re-runs stay parked (hub, later).

## Bundle + intake mechanics (spec §2–§4, §6)

- `bundles/<id>/` in the game-two worktree, gitignored: write-once
  `manifest.json` (identity incl. REQUIRED `fingerprint_md5` — the
  EOL-normalized handshake identity, stronger than a commit SHA —
  plus best-effort `game_commit`, `machine`, member sha256s),
  `input_log.json` (per-tick seat-ordered masks, byte-for-byte the
  `fold_input` values), `digest_chain.json` (the FULL chain),
  preconditions (+ canonical save bytes when non-fresh).
- Verification = the re-executor's double-run gate; its
  `verification.json` receipt IS the producer attestation your intake
  gate names. Delivery of any future bundle = a mail naming path +
  manifest sha256s; your seat reads this worktree read-only and
  copies under your intake gate. Nothing game-side ever writes into
  your tree.

## Sequencing (no promise — symmetric with your design's own posture)

Three implementation tickets are cut (spec §7: T1 emitter+re-executor
round-trip · T2 Mode T emitter, which closes with a reference track
mailed to you · T3 netplay dump-at-close, env-gated, host-side,
default OFF). Owner-paced; the spec is the contract either way. Your
consumer adapts to the pin per your own draft's resolution rule —
where draft-1 differs from spec §5, the spec wins.

## Expected receipt (when convenient — fire-and-forget, no deadline)

```
RECEIPT: e3a-spec md5 f531709a41e89aea5cf4409cc058a817 read=<yes|partial|no>
RECEIPT: consumer-adaptation = <done | queued | issue: one line>
```

If your adaptation surfaces a schema defect, mail it as a finding —
schema bumps are additive and game-seat-owned, and a verified defect
report is exactly the class of evidence that earns one.
---- MAIL VERBATIM END ----
