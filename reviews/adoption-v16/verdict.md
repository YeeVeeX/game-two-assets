# Adoption record v16 — K-S adoption + sighting-context demo proof verdict

**Answer first: the adoption record stands, and the proof now lives in the
artifact class the defect was sighted in.** The register entry
(`docs/selection-register.md`) records the owner-ratified v15 K-S
selection as this repo's k0-of-record for future compositions —
pointer-only, one line to reverse, zero pixels moved. The machine proof:
this sprint's module rebuilt the v13 demo APNG byte-identically to the
committed bytes the owner watched (sha `3cb8361a…`, exact match), then ran
the SAME code path with only the k0 sprite substituted; the two builds'
in-process frames differ at exactly the four k0 ticks (T34–T37), at
exactly the 8px gape mask transformed by the draw vector (128 pane px per
frame), with every changed pixel shade `#8c3818` in the K-S build and
accent `#140e0c` in the incumbent build. At the pinned protocol on the
committed artifacts, the DEF-1 aperture percept is absent from the K-S
demo, the strike tell reads, and the swap introduces no new percept class
at the cuts. Per the pre-registered disposition rule, DEF-2's
register-candidate proposal is recorded DISSOLVED (its subject — the
4-tick exposure of a floor-colored aperture — no longer exists in the
selected bytes), with the forwarded-if-reversal contingency retained
verbatim and the at-speed non-claim intact. No banked byte moved; no
integration implied.

Reviewed artifacts (SHA-256 prefixes; full hashes in
`adoption-manifest.json`):

- `adoption-report.json` (`026308793d40e57d…`) — the machine tables:
  incumbent reproduction, swap purity per tick, staged-source identity.
- `synthetic-adoption-ks-demo-{4,8}x.apng` (`92da2ed1…`, `08a82a9f…`) and
  `-slow6-{4,8}x` (`6ef9169c…`, `fd010389…`) — the K-S demo, real 1/60 s
  and slowed 6/60 s, banked encoder, declared delay lists.
- `synthetic-adoption-sbs-demo-{4,8}x.apng` (`53ebd01c…`, `00efdd95…`)
  and `-slow6-{4,8}x` (`5e522c2c…`, `609a3d1e…`) — incumbent pane over
  K-S pane per frame, drawn stream labels.
- `synthetic-adoption-strip-attack-8x.png` (`fd7fbb48…`) — the demo
  attack window T27–T47, two aligned streams (INCUMBENT, KS SELECTED),
  8x NN, declared viewport crop, 4088x3230 (under the png_reader cap).
- Pre-registration: `reviews/adoption-v16/rationale.md`, committed with
  the toolchain (`2c024b9`) **before any v16 artifact existed**. No bar
  was added, removed, or reworded afterwards.
- Session model `us.anthropic.claude-fable-5` (verified from `PI_MODEL`).
  Council seat cross-vendor (Kimi K2.5, `moonshotai.kimi-k2.5`), one
  consolidated adversarial call: 2,435 in / 1,415 out = 3,850 of the 8k
  cap, `stop_reason=end_turn`; response file-redirected and read as
  UTF-8; reconciliation in the appendix.

Sprint question (rationale, fixed first): record the owner-ratified K-S
selection as a mechanical, reversible register entry, and prove the
selected bytes in the exact artifact class where the defect was sighted,
through the banked demo pipeline itself, gated by the
incumbent-reproduction and swap-purity bars.

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS | 618 tests, 0 failures, exit 0 (~2835 s; the 6 post-bank guards active after artifact generation); commit hooks green |
| 2 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 after the mechanical identity re-pin `aa36857` (`da5119c8`→`546769ff`, all 5 pinned blobs identical, attack_timing 5/4/8/13 re-verified, committed alone); pre-banking: exit 0 with a trailing identity-drift WARNING (`546769ff`→`98e52e57`, content verified identical by the gate's committed-HEAD hash check — re-pins at the v17 checkpoint) |
| 3 | `track_recompose --check` + `pose_integrity_metrics --check` + `remedy_metrics --check` all exit 0 at banking | PASS | all three run this session after artifact generation, all exit 0 — machine proof the v13+v14+v15 lattice is untouched |
| 4 | Incumbent-reproduction bar byte-exact | PASS | rebuilt APNG sha `3cb8361a7bd4cddc…` == committed v13 demo; rebuilt track sha `b76858075ad6e46a…` == committed (`incumbent_reproduction.*_byte_identical: true`) |
| 5 | Swap-purity bar, clauses A + B, both directions | PASS | 48 frames compared: 44 non-k0 ticks byte-identical; k0 ticks exactly [34,35,36,37], draw [38,32], 128 changed px per frame == the transformed 8px gape mask; colors shade/accent as declared; staged sources sha-equal the release pins; tests prove rejection of a planted off-k0 delta (clause A) and of staged K-R bytes (clause B — positional purity alone would accept them, the pre-registered reason clause B exists) |
| 6 | Scale-mirror fidelity at 4x | PASS | machine-asserted byte equality against the banked builder's frames at every artifact build; divergence-detection test-proven |
| 7 | Zero additions under `exports/` | PASS | `exports/adoption-v16` does not exist; `check_export_pins` 26/26; remedy release pins verified; calibration directory guard green. The trees that DID grow this sprint, named exactly: `tools/` (+1 module), `tests/` (+1 file), `docs/` (+1 register), `reviews/adoption-v16/` (this bundle) — all pre-registered deliverables |
| 8 | Banked files untouched; pin lattice | PASS | 24 module pins in `adoption-manifest.json` (the v15 manifest's 23 + this module) re-verified by `--check`; the suite's pin-compare test extends to v13+v14+v15 manifests; zero edits to any pinned module, banked artifact, banked verdict, or the six remedy PNGs |
| 9 | Determinism | PASS | `double_build_identical: true` over all 10 artifacts; `--check` regenerates every committed artifact byte-identically from banked bytes + the release-pinned staged swap |
| 10 | Zero writes into `../game-two` | PASS | read-only `git -C ../game-two rev-parse/show/log` from this repo's cwd throughout |
| 11 | SYNTHETIC/EXP labels everywhere | PASS | filenames carry `synthetic-adoption`; manifest + report carry `provenance.class = "SYNTHETIC"`; demo-class APNG frames carry the banked builder's drawn `SYNTHETIC DEMO EXP` (byte-purity of the sighting pipeline wins, per the rationale's labels paragraph); side-by-sides and strip carry drawn `SYNTHETIC ADOPTION EXP` + the protocol line |
| 12 | Citations at the fresh pin; owner-approval verbatim | PASS | v13/v14/v15 quotes read from committed texts this session; "Approved, proceed" recorded verbatim in the rationale (pre-artifacts) and the register |
| 13 | Register-entry shape | PASS | dated entry, quote verbatim, carriers named with the derivation chain (which words carry which weight — council Q1 adoption), consequence scoped to this repo's future compositions, reversal = one line with banked-history-after-reversal stated, no lore (shape test-enforced) |

**Accuracy: 13/13 integrity bars.**

## The machine findings (report highlights; exact numbers in the JSON)

- **The harness IS the sighting pipeline, machine-proved.** The rebuild
  path is the banked `build_demo_track` → `load_poses` →
  `build_demo_apng_frames` → `encode_apng`, called as the same function
  objects with the dirs dict as the ONLY varying input (`load_poses`
  carries no path-dependent branching — it resolves `POSE_DIRS` →
  filename and reads bytes). Byte-identity of the incumbent rebuild
  against the committed v13 demo closes the equivalence: any hidden
  divergence in the code path would have to reproduce the committed
  bytes exactly to hide (council Q2, mechanization stated).
- **The swap is total and exactly bounded.** Per k0 tick: changed set ==
  the 8px gape mask under `(gx,gy) → ((38+gx)·4, 10+(32+gy)·4)` 4x4
  blocks, 128 px; nothing else in 48 frames differs. The staged
  substitute is pinned to the committed release: report
  `swap_source_sha256` == `exports/remedy-v15/release.json` entries ==
  on-disk export bytes (chain re-verified live this session; council Q5
  check closed).
- **k0 stream cross-check:** the mapped pose stream carries k0 at
  exactly 4 consecutive ticks (34–37) inside the v14-cited attack window
  29–45 (`k0_stream_consistent_with_v14_window: true`).

## Perceptual rubric (judged at the pinned protocol on the committed artifacts; coverage = the demo's actual content — right-facing, zone_1)

Viewing per the manifest protocol: 100% zoom, fit-to-window off,
pre-scaled integer NN 4x and 8x, real 1/60 s and slowed 6/60 s. Session
vision on committed artifact frames. The down facing is not in the demo;
its aperture resolution rests on the banked v15 verdict (context-specific
proof here, not a re-adjudication — the rationale fixed this scope).

- **Line 1 — DEF-1 aperture absent in the demo context: PASS.** Through
  T34–T37 in the K-S demo the snout tip reads attached — the shade band
  bridges tip to head and reads as creature material over the zone_1
  floor. In the per-frame side-by-sides the incumbent pane carries the
  floating-tip/void percept and the K-S pane does not, at both scales
  and both speeds; the aligned strip shows the same column-by-column.
- **Line 2 — the strike tell reads in the demo context: PASS.** The k0
  ticks read instantly as the strike against their a0/s0 neighbors:
  crouch + forward reach + the +6px lunge + the interior mouth band.
  The v15 measured trade is restated, not re-litigated: the band's
  color pop against the body is 2.69:1 vs the incumbent's 6.60:1 — the
  tell is carried by structure (v15 line-2, the banked reference).
- **Line 3 — no new percept class at the swap cuts: PASS.** Stepping the
  slowed APNGs across a0→k0 (T33→T34) and k0→s0 (T37→T38): the
  discontinuity structure (head drop, lunge, band appear/disappear) is
  the banked incumbent structure; the only in-cut difference is the
  band's color during the hold. No flash, pop, or state-confusion read;
  shade is a mid-luminance ramp member already present in every pose.

## Disposition (the pre-registered rule, applied)

All machine bars passed and lines 1–3 passed, so per the rule fixed
verbatim in the rationale:

- **The adoption record STANDS as banked.** The register entry is the
  owner's decision, recorded with its derivation chain; this sprint's
  demo proof accompanies it as evidence in the sighting artifact class.
- **DEF-2's register-candidate proposal is recorded DISSOLVED**,
  retaining v15's forwarded-if-reversal note verbatim: "If the owner
  reverses to the incumbent, DEF-2 forwards to the temporal register
  exactly as v14 proposed (P1-bundle falsifiable)." Category stated
  plainly (council Q4 adoption): this dissolves a register-CANDIDATE
  whose subject — the 4-tick exposure of a floor-colored aperture — no
  longer exists in the selected bytes; it is NOT an at-speed
  adjudication. What does not dissolve: the at-speed read of the
  selected band (does the shade mouth read correctly at 60 tps?) remains
  unmeasured, part of the same owner-sequenced capture class as v15's
  protocol-vs-viewport carried finding. The sequencing itself is the
  banked v14 position ("if DEF-1 is authored away, the temporal half
  likely dissolves — sequencing an authoring decision first avoids
  paying the register-revision + capture-adjudication cost twice").
- **DEF-3 note (context, not evidence):** the original sighting was
  resampled viewing (Edge, maximized, browser-scaled). Every v16
  artifact carries the pinned protocol; if the owner re-watches the K-S
  demo in Edge, the DEF-3 resampling contributor applies to that viewing
  exactly as v14 classified it — it amplifies percepts, it does not
  create bytes.

## Presentation scores (accuracy scored separately above)

- **Register entry: 9/10.** The derivation chain makes each carrier bear
  exactly its own weight; consequence, scope, and reversal are one
  readable block. Cost: the entry is long for a register line.
- **K-S demo APNGs: 9/10.** The artifact class the owner actually
  watched, byte-anchored to the committed v13 demo by the reproduction
  bar — the adoption question is answerable by watching the same demo
  again. Cost: the drawn per-frame label says `SYNTHETIC DEMO EXP`
  (pipeline purity), so the filename/manifest carry the adoption
  context.
- **Side-by-side APNGs: 8.5/10.** The decisive percept (incumbent void
  vs K-S attached tip) sits in one fixation per frame at both speeds.
  Cost: 4 more files — the honest 2-scale x 2-speed matrix is bulky.
- **Strip: 8.5/10.** Aligned INCUMBENT/KS columns over the full attack
  envelope make the absence checkable without playback; protocol line
  and stream labels drawn in. Cost: the 4088px width asks a wide viewer;
  the crop (declared) trims approach context.
- **Report JSON: 8.5/10.** Reproduction, purity, and source identity in
  one deterministic artifact.

HFO gate (owner register): answer-first pyramid; severity-honest verbs
("reads as", "recorded", "dissolves a candidate", never "fixed");
uncertainty typed (at-speed named unmeasured with its instrument; DEF-3
scoped as context); no promises (adoption ≠ integration; reversal cost
stated); accuracy and presentation on separate axes; mechanical ids
throughout; the register re-read against the same checklist.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call attacking five numbered claims with the register
text, machine results, rubric verdicts, and v15 quotes inlined. Returned:
**Q1 REFUTED, Q2 UNCERTAIN, Q3 REFUTED, Q4 REFUTED, Q5 CONFIRMED (as a
checkable risk)**. Per the v12–v15 precedent every charge was re-verified
against primaries before adoption; the reconciliation:

1. **Q1 (register over-claims the owner's words) — REFUTED by the
   council; the charge partially dissolves on the primary it could not
   see, and the wording kernel is adopted.** The charge: "the owner said
   'Approved, proceed' to the sprint, not to a perpetual policy; the
   register conflates verdict content with owner authorization." The
   primary the council brief did not carry: the owner-issued v16 sprint
   brief itself commissions "a mechanical adoption record naming the
   remedy-v15 K-S pair … as the selected k0-of-record for future
   compositions in this repo" — the consequence clause is the
   commissioned recording, not an extrapolation from two words. ADOPTED
   (real kernel): the entry now states its derivation chain explicitly —
   the two words ratify the receipt and authorize the sprint; the
   of-record consequence is what the owner's brief commissioned — so no
   reader can mistake which carrier bears which weight. Also ADOPTED:
   the reversal clause now states that artifacts banked under the entry
   stay banked history (reversal changes future compositions only) —
   the council's "the entry creates a dependency" charge dissolves
   against the pinned-regeneration-history line but the explicit
   sentence is better than the inference.
2. **Q2 (demo-harness equivalence) — UNCERTAIN from the council; an
   evidence-availability limit (the v15 Q1 pattern), mechanization now
   stated.** The council could not verify "same code path" from a text
   brief. In-repo it is machine-enforced: the module calls the banked
   functions as the same function objects with the dirs dict as the only
   varying input; `load_poses` is a small pure loader with no
   path-dependent branching; the mirror-fidelity assertion is a byte
   comparison proven able to fail (divergence test); and the
   reproduction bar's byte-identity means any hidden code-path
   divergence would have to reproduce the committed v13 bytes exactly to
   hide. ADOPTED: the machine-findings section states this mechanization
   rather than asserting "same code path" as a phrase.
3. **Q3 (frozen-state integrity) — REFUTED by the council; both
   sub-charges dissolve on primaries; two precisions adopted.** The
   "zero additions is misleading" charge conflates "zero `exports/`
   additions" (claimed, machine-checked: the guard, the pins, the
   directory checks) with "zero new files anywhere" (never claimed — the
   new module/tests/register/review bundle are pre-registered
   deliverables). ADOPTED: bar 7 now names exactly which trees grew.
   The temp-lifecycle charge dissolves on mechanics: staging uses a
   fresh unique `TemporaryDirectory` per invocation (auto-cleaned, no
   cross-run persistence, no shared path for concurrent processes), the
   staged bytes are sha-verified against the committed release before
   use, and `--check` re-stages from scratch — a polluted or stale dir
   cannot survive the sha gate. Recorded residue: the test fixtures use
   `mkdtemp` (OS-cleaned), cosmetic only.
4. **Q4 (DEF-2 dissolution is a category error) — REFUTED by the
   council; the charge partially dissolves on the banked texts; the
   category kernel is adopted whole.** The charge: "dissolution is
   claimed on static byte identity while DEF-2 was temporal — the sprint
   silently converted a temporal risk into a static one." Against the
   primaries: not silent, and not new — v14's own DEF-2 routing
   pre-committed exactly this sequencing ("if DEF-1 is authored away,
   the temporal half likely dissolves…"), v15 recorded the dissolution
   as contingent, the v16 rule fixed DISSOLVED as the outcome before
   artifacts existed, and the at-speed non-claim is carried in all three
   verdicts. What the dissolution claims is narrow: the register
   CANDIDATE named a specific subject (the 4-tick exposure of a
   floor-colored aperture) and that subject has no referent in the
   selected bytes. ADOPTED whole: the disposition and the register line
   now state the category explicitly — candidate-dissolution, not
   at-speed adjudication — and name what does NOT dissolve (the at-speed
   read of the selected band, owner-sequenced instrument unchanged).
   The council is right that line 3's slowed-APNG evidence is not
   at-speed evidence; nothing in this verdict claims otherwise.
5. **Q5 (unthought risk: the report's swap-source shas are self-reported
   and unverified against the committed release) — CONFIRMED as a
   checkable risk; the check was already mechanized, and it was also run
   live.** The chain is closed in-repo three ways: staging refuses bytes
   whose sha differs from the committed `release.json` pin; the
   post-bank test compares the manifest's recorded swap-source shas
   against `release.json`; `remedy_metrics --check` verifies
   `release.json`'s pins against the on-disk exports. Re-verified live
   this session: report == release.json == on-disk bytes, both facings,
   printed in the session log. ADOPTED: this chain is now stated in the
   machine-findings section instead of living only in code.

Net: two register precisions (derivation chain; banked-history-after-
reversal), one mechanization statement (Q2), one named-trees precision
(Q3), the DEF-2 category statement adopted whole (Q4), one closed-chain
statement (Q5). No machine number changed; no bar moved; no banked
verdict touched; the disposition rule's outcome is unchanged.

## Non-claims

No integration and no integration schedule — game-two v17 stays open; the
one-way boundary held (read-only `git -C ../game-two` throughout; zero
writes). No runtime claims: every artifact is SYNTHETIC-class, composed
of banked export bytes and the release-pinned K-S exports under the
declared mapping. **The at-speed fusion read of the selected candidate
remains unmeasured** — real-speed APNG playback at the pinned protocol is
still not a 60 tps runtime measurement; the banked capture design (P1
scripted bundle) remains the owner-sequenced instrument (unchanged from
v15). No DEF-2 adjudication (candidate-dissolution recorded per the
pre-registered rule; the temporal question class survives in the capture
instrument's scope). No down-facing re-adjudication (v15 covers it). No
claim about player-side viewing environments (DEF-3 scope law). Zero
banked bytes moved; the banked k0, all 26 banked export pins plus the
six remedy release pins, every pinned module, and every banked verdict
are untouched (machine-verified at banking). No work on "other visual flaws"; nothing else authored; K-O
and K-R remain banked alternatives, not re-litigated.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: only `done/` — no new receipts, nothing owed, nothing
  polled. Outbound: none due (the step-0 drift was identity-only; the
  content-drift note protocol did not trigger).
- Pins: mechanical identity re-pin `aa36857` (`da5119c8`→`546769ff`,
  committed alone, staged-list verified, all 5 pinned blobs
  byte-identical across the hop, attack_timing 5/4/8/13 re-verified at
  the new pin; HEAD moved once mid-step and the re-pin targeted the
  newest HEAD). Gate exit 0 at step 0 and immediately before banking —
  the pre-banking run reports a trailing identity-drift WARNING
  (`546769ff`→`98e52e57`, all pinned blobs content-identical per the
  gate's committed-HEAD hash check); per the standing rule it re-pins at
  the v17 checkpoint (game-two lands ~3 commits/hour).

## Stop

Sprint 16 stops here: one register (two entries: the adoption record,
the DEF-2 disposition), one new module, 19 tests (13 pre-bank + 6
activated post-bank; full suite 618 green), 9 SYNTHETIC-labeled
double-build-deterministic artifacts + report + manifest, one adoption
verdict, one mechanical re-pin. Carried to v17+: the trailing identity
re-pin (as it lands), the shade-double-duty watch item (v15, unchanged),
the protocol-vs-viewport capture question (unchanged, owner-sequenced —
now also the home of the at-speed read of the selected band), and the
standing owner decisions on integration sequencing. No second proof
family, no settle-bob, no capture execution, no game-side code; audio
and tile era stay parked.
