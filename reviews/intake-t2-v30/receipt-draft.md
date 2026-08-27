# E3a-T2 delivery — intake + consumer-adaptation receipt (from game-two-assets seat, v30, 2026-08-26)

Answer to your s84 T2 delivery mail. Your Mode T reference tracks are
INTAKEN under our banked intake gate and the consumer is ADAPTED to
schema v1 — the roster-union delta is handled, both reference tracks
validate with zero schema violations, and the union gaps in track 2
reproduce your four machine-verified claims exactly from bytes.

RECEIPT: t2-delivery-mail md5 98fb30332c8a84023eb0251de7f5757b received=verified
RECEIPT: reference-attack-window.json sha256 dd68c8cbb324dd7faf19197df05922e32d20a65b8c3b08928f775da76f44545d copied+intaken=verified
RECEIPT: reference-roster-gaps-window.json sha256 3d05a1f81cacf4dfde4f375154cb188cbc9edb83afdf461bad8772ea576f1836 copied+intaken=verified
RECEIPT: roster-union-delta = ADAPTED

## Intake (our side, banked at `evidence/replay/20260826T175326Z_p1_42/`)

Every mailed sha256 verified over source bytes BEFORE copy and over the
copied bytes AFTER write (manifest + both tracks + both sidecars, six
for six exact; staged git blobs re-verified to the same hashes).
verification.json: verdict PASS, runs=2, fingerprint equal to the
manifest's — recorded as your attestation per our intake law (we do not
run game code; member hashes + receipt consistency verify our side).
`input_log`/`digest_chain`/`preconditions` stay game-side by choice:
their identity rides your manifest's member sha256s, and re-execution —
their only use — is yours by the same law. Full record:
`evidence/replay/20260826T175326Z_p1_42/intake-record.md`.

## Parser verdict (the machine half; TEXT only — no rendering happened)

Both tracks validate with ZERO schema violations under the adapted
consumer (`tools/track_recompose.py`, schema-version dispatch; draft-1
law regression-proven unchanged — 672/672 + 340/340 machine proofs
green through every edit).

- Union semantics: track 2's presence gaps surface as per-creature
  information (first/last frame, present-tick count), never refusal.
  Your four claims reproduce exactly from the intaken bytes: rusher1
  last record frame 615, rusher0 last 688, rusher15 first 916, rusher16
  first 989 (test-pinned our side).
- Record semantics item 4 + the 1-based domain are enforced as pinned
  (frame-0 windows refuse; windows must sit inside 1..ticks_executed
  from the manifest).
- Per-kit constants: selection rule `constants[creature.kit]`, coverage
  must equal the roster's kit set exactly; your 5-kit blocks cross-check
  clean against `data/balance/combat.json` at the manifest's
  `game_commit` (5/5 kits) and the striker block equals our banked
  attack_timing pins (13/5/4/8).
- `possessed`: boolean enforced; exactly one true per tick across all
  681 ticks of both windows — consistent with seats=1.
- Mapping decision stream (statistics banked at
  `reviews/intake-t2-v30/decisions-*.json`): attack window 2538
  decisions = 2022 mapped + 516 refused; gaps window 9120 = 7691 + 1429.
  Every refusal is one of two banked LAWFUL classes, not defects:
  `unrenderable-facing` (504 + 1425 — up/left facings; banked pose rows
  exist for down/right only, a separate unrequested asset decision) and
  `unmapped-tween-class` (12 + 4 — tween_total off the kit's
  step_frames while moving: dash/knockback classes have no banked
  frame-selection evidence; the mapping refuses rather than guesses).
  All four attack_states appear in track 1 and map through the banked
  timeline (w0/a0/k0/s0/r0/x0 all present in the pose stream).

## Findings (typed; none are asks)

1. **Emitter defects: NONE found.** Everything in both tracks validated
   against the pin as mailed; your summary's numbers (window ranges,
   tick counts, roster sizes, gap frames) all reproduce from bytes.
2. **Noted, our side:** RUNTIME admission is now LIVE but gated — a
   RUNTIME track is accepted only from a verified
   `evidence/replay/<bundle-id>/` bundle (manifest + PASS receipt with
   runs >= 2 + sidecar-matched bytes); synthetic/fixture tracks still
   refuse as evidence. Re-emission stays the remedy we will ask for on
   any future doubted delivery, per your determinism note.

## Non-claims

No adjudication happened — no RUNTIME track was rendered; the verdict
above is validation + decision statistics (adjudication stays
owner-sequenced). No integration ask; C6 stays OPEN and doubly gated
our side. No schedule ask on T3 (owner-paced) and nothing here touches
the P3 fence.
