# Intake record — bundle 20260826T175326Z_p1_42 (E3a-T2 delivery, v30)

**Intaken 2026-08-26 under the banked intake law
(`docs/replay-capture-design.md` section 5). Every mailed sha256 verified at
the source worktree BEFORE copy and re-verified over the copied bytes AFTER
write — six for six exact. Verification receipt: verdict PASS, runs=2.**

## Delivery identity

- Delivery mail: `from-game-two-e3a-t2-track-delivery.md` (s84), md5
  `98fb30332c8a84023eb0251de7f5757b` as received (6,713 B, pure LF) —
  verified at v30 step 0 against the mailed value.
- Source: game-two worktree `bundles/20260826T175326Z_p1_42/`, read
  READ-ONLY via plain `open()` (seat-lease law). game-two HEAD at read time:
  `ea0e37c7090e1a3e18565e658db9842c0b4fd0fd` (= this repo's pinned baseline
  at the v30 step-0 re-pin). Bundle path confirmed gitignored game-side
  (`git check-ignore` exit 0) — no git blobs exist; the mailed sha256s are
  the ONLY identity, per the mail's own delivery-grounding law.
- Emitter provenance (from the mail's digest stamp): game-two `2627ed0`,
  `harness/state_track.rb` git-blob md5 `bf3c740f911ab24162f69e358212a1c0`;
  pinning spec section 5 blob md5 `676e9782f613d9a6264d43e5128aacd4`
  (verified byte-unchanged `0f3e9e5`→`2627ed0` at v29, finding n2).

## Mailed vs computed sha256 (source, then post-copy)

| member | mailed / sidecar sha256 | source | copy |
|---|---|---|---|
| `manifest.json` | `e56822806f93e63803beab56c49d5feea2bb47c09a1a3b2236b4b247eed40eee` | exact | exact |
| `tracks/reference-attack-window.json` | `dd68c8cbb324dd7faf19197df05922e32d20a65b8c3b08928f775da76f44545d` | exact | exact |
| `tracks/reference-roster-gaps-window.json` | `3d05a1f81cacf4dfde4f375154cb188cbc9edb83afdf461bad8772ea576f1836` | exact | exact |

Sidecars (`<track>.json.sha256`, sha256sum format): both state exactly the
mailed track hashes and both match the computed bytes — sidecar-verified as
the mail claims. Copies of `verification.json` + both sidecars verified
byte-identical to source post-write. All six copied files carry ZERO CR
bytes (pure LF, matching the emitter's write-once LF law);
`/evidence/replay/** -text` routed in `.gitattributes` in this same commit
(byte-pin law — the repo's `* text=auto eol=lf` default would otherwise
rewrite bytes at checkout).

File sizes: manifest.json 784 B · verification.json 271 B ·
reference-attack-window.json 1,082,816 B ·
reference-roster-gaps-window.json 3,864,045 B · sidecars 95/100 B. All
under the 5 MB LFS threshold — committed as regular `-text` blobs.

## Verification receipt (the producer's attestation)

`verification.json` verbatim summary: `verdict: "PASS"`, `runs: 2`,
`first_divergent_window: null`, `reason: null`,
`tool: "harness/bundle_replay.rb"`, `date: "2026-08-26T20:36:39Z"`,
`fingerprint_at_verification: "d8abc55a547161da23a105ca02695fd4"` — equal to
the manifest's `fingerprint_md5` (cross-checked this intake). Machine class
from the manifest: `GABO_DESKTOP`; seed 42, seats 1, ticks_executed 1249,
end_reason `run_until`, digest_version 3, digest_every 60.

## What was verified vs what is trusted (the attestation split, stated plainly)

- **Verified our side (recomputed over bytes this session):** every mailed
  member sha256 at source and after copy; sidecar-vs-track equality;
  manifest/verification fingerprint equality; provenance `bundle_id` equality
  across manifest, verification, and both tracks; per-kit constants equality
  against the producing tree's `data/balance/combat.json` at the manifest's
  `game_commit` `c6ceb8c0` (read-only `git show`; 5/5 kits exact — striker
  13/5/4/8 also equals this repo's banked attack_timing pins).
- **Trusted as the producer's attestation (design section 5's own law —
  this repo does not run game code):** the re-execution identity claim
  itself (verdict PASS over runs=2, chains equal), the fingerprint→build
  binding, and the claim that the sampled run was run 1 of the gate. The
  mail's determinism note names the remedy for any future doubt: re-emit
  from pristine copies and compare sha256s.

## Intake-set choice (recorded)

Copied the MINIMAL set the consumer needs: `manifest.json`,
`verification.json`, both tracks, both sidecars. `input_log.json`,
`digest_chain.json`, `preconditions.json` stay game-side by choice: their
identity rides the manifest's `members` sha256s (verified structure), and
re-execution — the only use those members have — is game-side by the banked
intake law. Nothing in this repo can or does run them.

Layout preserved from the bundle (`tracks/` subdir) so member paths in
future tooling resolve identically on both sides.
