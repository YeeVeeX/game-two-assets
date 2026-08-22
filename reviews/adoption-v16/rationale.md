# Adoption record v16 — K-S selection recorded + sighting-context demo proof (pre-registration)

Sprint question: record the owner-ratified v15 K-S selection as this repo's
k0-of-record for FUTURE compositions (a mechanical, pointer-only,
one-line-reversible register entry), and prove the selected bytes in the
EXACT artifact class where the defect was sighted — the v13 demo APNG —
through the banked demo pipeline itself, with only the k0 sprite
substituted. Zero new pixels; zero exports; no banked byte moved; no
integration. Deliverables: `docs/selection-register.md` (new mechanical
register), `tools/adoption_demo.py` (new module; banked modules imported
unmodified), `tests/test_adoption_tools.py`, <= 12 committed
playback/inspection artifacts + report + manifest at
`reviews/adoption-v16/`, and an adoption verdict
(`reviews/adoption-v16/verdict.md`).

**Owner-approval record (verbatim), the authorization this sprint runs
under:** at v15 close the owner ruled **"Approved, proceed"** — the v15
receipt (the K-S selection verdict: shade `#8c3818` over exactly the
machine-derived gape masks resolves the DEF-1 aperture percept on both
facings and both zones while the strike tell still lands at the pinned
protocol, with the measured trade disclosed) is what was approved, and the
next sprint was authorized. That ratifies the SELECTION and authorizes
THIS recording sprint; it is NOT an integration order and not a game-two
decision. The register entry is pointer-only and explicitly reversible
(one line to revert, zero pixels moved); it scopes the consequence to THIS
repo's future compositions; `exports/calibration-v2` k0 remains the pinned
regeneration history every banked `--check` rebuilds from; integration
remains owner-sequenced at the hub. If drafting the register surfaces a
genuine ambiguity that materially changes the entry, the sprint STOPS and
asks with options (typed abstention) instead of guessing.

These bars are fixed BEFORE any v16 artifact exists (v11/v13/v14/v15
rationale law). No bar may be added, removed, reworded, or reinterpreted
after artifacts exist.

## The subject (fixed here; the pinned facts this sprint stands on)

- The v15 selection: `player_1_lane_b_attack_down_k0_ks` +
  `player_1_lane_b_attack_right_k0_ks` (release `remedy-v15`, gate-valid,
  alpha byte-identical to the banked k0, RGB differing at exactly the
  machine-derived gape masks — 16 px down `[12,13,19,14]`, 8 px right
  `[24,13,27,14]`).
- The sighting context: the owner sighted DEF-1 live in the v13 demo APNG
  (`reviews/recompose-v13/synthetic-demo.apng`, sha256
  `3cb8361a7bd4cddc070e587da023d5f3de84c3ceaeed3b311df68e40deb1392d`,
  48 frames, exact 1/60 s, 4x panes) — Edge, maximized, browser-scaled
  (the v14 register's DEF-3 note). The demo attack runs facing `[1,0]`,
  track ticks 29–45 (v14 verdict), so the demo proof covers the
  RIGHT-facing sighting context; the down case stays covered by the v15
  verdict. This is a context-specific proof, not a re-adjudication.
- The demo pipeline: `tools/track_recompose.py` — `build_demo_track` →
  `load_poses` → `build_demo_apng_frames` (4x panes, 10 px drawn label
  band) → `encode_apng` at the banked delays. `pose_filename("k0",
  facing)` is fixed, and `load_poses` resolves k0 through
  `POSE_DIRS["k0"] = "attack_dir"` — so a staged attack directory holding
  substitute bytes under the k0 filenames is a clean dirs-level seam that
  touches no pinned module.

## The two machine proof obligations (fixed definitions)

### Incumbent-reproduction bar (the harness IS the sighting pipeline)

`tools/adoption_demo.py` rebuilds the v13 demo through ITS OWN code path —
`tr.build_demo_track(reference)`, `tr.load_poses(default_dirs())`,
`tr.build_demo_apng_frames(...)`, `encode_apng(frames,
apng_delays(len(frames)))`, all banked functions imported unmodified —
and the resulting APNG bytes MUST equal the committed
`reviews/recompose-v13/synthetic-demo.apng` exactly (sha256
`3cb8361a7bd4cddc…`). Supporting row, same run: the freshly built track
bytes equal the committed `synthetic-demo-track.json` (sha256
`b76858075ad6e46a…`). Nothing is written into `reviews/recompose-v13/`.
Only after this bar passes does the SAME code path run with the k0 slot
substituted. If the rebuild does not reproduce the committed bytes, the
sprint STOPS and banks the finding (contract break, not a workaround
target).

### Swap-purity bar (two clauses, both machine-proved)

The substituted build stages a temporary attack directory (under the
system temp root, never inside the repo) containing the two remedy-v15
K-S exports copied under the banked k0 filenames
(`player_1_lane_b_attack_{down,right}_k0.png`), and passes
`{**default_dirs(), "attack_dir": staged}` through the identical code
path. No pinned module is edited; no repo file is staged over.

- **Clause A — positional purity.** Comparing the two builds' in-process
  4x pane buffers (the exact frame bytes handed to the encoder, before
  encoding): frames are byte-identical at every tick whose mapped pose is
  not k0, and at each k0 tick the changed-pixel set equals EXACTLY the
  right-facing gape mask transformed by that tick's draw vector and the
  pane transform — gape cell `(gx, gy)` → the 4x4 pane block at
  `((dx + gx) * 4, 10 + (dy + gy) * 4)` (the 10 is the banked label
  band). Expected from the pinned constants: k0 ticks = t34–t37 (onset 29
  = commit 15 + step 13 + 1; w0@29, a0@30–33, k0@34–37, s0@38, r0@39–44,
  x0@45 — consistent with the v14 verdict's "track ticks 29–45"), draw
  vector `[38, 32]` (px 32 + active_px 6 along `[1,0]`), changed pixels
  per k0 frame = 8 gape cells x 16 = 128. The k0 tick list and draw
  vectors are COMPUTED from the banked mapping's decision records at run
  time, never hardcoded in the tool; the expected values above are
  pre-registered so a mismatch is a red bar, not a surprise.
- **Clause B — swap-source byte identity.** The staged substitute files
  must byte-equal the banked remedy-v15 K-S exports (sha256 pinned by the
  committed `exports/remedy-v15/release.json`), asserted at staging; AND
  every changed pane pixel at every k0 tick must carry the K-S shade RGB
  `#8c3818` in the substituted build and the incumbent accent `#140e0c`
  in the incumbent build. (Clause A alone is color-blind and would accept
  any of the three v15 lanes — all share the positional diff set; clause
  B pins the swap to the SELECTED bytes.)

Both clauses are proven in BOTH directions in the tests: the correct swap
passes; a planted off-k0 frame delta fails clause A; a wrong-bytes k0
substitute (K-R-style two-tone) fails clause B.

### Scale-mirror fidelity (for the 8x protocol variants)

The banked `build_demo_apng_frames` fixes 4x. The 8x artifacts use this
module's scale-parameterized mirror of that function; the mirror at
scale 4 MUST produce frame buffers byte-identical to the banked builder's
(machine-asserted at every artifact build and in the tests). The 8x
artifacts are therefore the banked construction at the other
pre-registered protocol scale, not a second compositor.

## Selection artifacts (fixed matrix; 9 playback/inspection files + report + manifest)

Composition via the banked chain only (`tr.build_demo_apng_frames` /
the fidelity-asserted scale mirror, `encode_apng`, `apng_delays`,
`pim.slow_delays`, banked font). Real speed = exact 1/60 s per tick with
the banked final hold; slowed = 6/60 s per tick, same final hold; both
delay lists declared in the manifest. Zone: the demo's own zone_1
(the sighting context; both-zone coverage is banked in v15).

1. `synthetic-adoption-ks-demo-4x.apng` — the K-S demo, real speed
   (the sighting artifact class, only k0 swapped)
2. `synthetic-adoption-ks-demo-8x.apng`
3. `synthetic-adoption-ks-demo-slow6-4x.apng`
4. `synthetic-adoption-ks-demo-slow6-8x.apng`
5. `synthetic-adoption-sbs-demo-4x.apng` — side-by-side incumbent pane
   over K-S pane per frame, drawn stream labels, real speed
6. `synthetic-adoption-sbs-demo-8x.apng`
7. `synthetic-adoption-sbs-demo-slow6-4x.apng`
8. `synthetic-adoption-sbs-demo-slow6-8x.apng`
9. `synthetic-adoption-strip-attack-8x.png` — the demo attack window,
   ticks T27–T47 (approach tail, the full attack envelope, idle return),
   two aligned streams (INCUMBENT, KS SELECTED), 8x NN, chunked 7 columns
   per stream-row; each cell is the composed 96x64 demo window cropped to
   the fixed rect x ∈ [24, 96) (creature + lunge room stay fully inside:
   sprite spans x 31–69 across the window; the crop is a viewport crop of
   identically composed bytes, declared here) — fits the png_reader 4096
   cap (7 columns x 578 px + margins = 4056 wide; 2 streams x 3 chunk
   rows x 530 px + header = 3206 tall)

Plus `adoption-report.json` (machine tables: reproduction bar, swap
purity per tick, staged-source identity, k0 stream cross-check) and
`adoption-manifest.json` (provenance class SYNTHETIC, module pins, the
pinned viewing protocol restated, artifact hashes, delay declarations,
double-build evidence).

Labels: every artifact carries SYNTHETIC/EXP in filename, manifest, and
pixels. The demo-class APNGs carry the banked builder's own drawn
per-frame label (`SYNTHETIC DEMO EXP` — byte-purity of the sighting
pipeline wins over label novelty; filename + manifest carry the adoption
context). Artifacts composed by THIS module (side-by-sides, strip) carry
`SYNTHETIC ADOPTION EXP` + the protocol line, drawn with SEAM_FONT-safe
glyphs only.

## INTEGRITY bars (any red stops the sprint; all-must-pass)

1. **Full suite green** including the new tests
   (`.venv/Scripts/python.exe -m unittest discover -s tests`).
2. **Both asset_gate runs exit 0** — step 0 (done: mechanical identity
   re-pin `aa36857`, `da5119c8`→`546769ff`, all 5 pinned blobs identical,
   attack_timing 5/4/8/13 re-verified, committed alone) and again
   immediately before banking.
3. **`track_recompose --check` AND `pose_integrity_metrics --check` AND
   `remedy_metrics --check` ALL exit 0 at banking** — machine proof the
   whole v13+v14+v15 lattice is untouched.
4. **The incumbent-reproduction bar** byte-exact (definition above).
5. **The swap-purity bar**, clauses A and B, machine-proved, and proven
   in both directions in the tests.
6. **Scale-mirror fidelity** at 4x, machine-asserted.
7. **Zero additions under `exports/`** — `exports/adoption-v16` must not
   exist; `check_export_pins` verifies all 26 banked pins; the remedy-v15
   release pin check and the calibration directory guard stay green.
8. **Banked files untouched** — zero edits to any pinned module, banked
   artifact, banked verdict, or the six remedy PNGs; every module this
   sprint imports (directly or transitively) SHA-256-pinned in
   `adoption-manifest.json` (the v13+v14+v15 pin lattice + this module),
   re-verified by `--check` and the tests.
9. **Determinism** — every artifact double-builds byte-identically
   in-process; `--check` regenerates every committed artifact
   byte-identically from banked bytes + the staged swap.
10. **Zero writes into `../game-two`**; read-only `git -C ../game-two`
    from this repo's cwd only.
11. **SYNTHETIC/EXP labels** on every review artifact — filename,
    manifest (`provenance.class = "SYNTHETIC"`), and pixels (per the
    labels paragraph above).
12. **Citations at the fresh pin with file:line**; banked-verdict quotes
    read from the committed texts this session; the owner-approval record
    verbatim in this rationale (above) and in the register.
13. **Register-entry shape** — dated entry, quote verbatim, carrier
    named, consequence scoped to this repo's future compositions,
    reversal = one line, no lore (mechanical ids only; owner quotes are
    carriers, not narrative).

## MEASUREMENT bars (machine facts; fixed definitions)

- The incumbent-reproduction comparison (APNG bytes + track bytes).
- The swap-purity tables: per-tick changed-pixel counts, set equality
  against the transformed mask, color identity per clause B, staged
  source SHA-256 vs the release pins.
- The k0 stream cross-check: the mapped pose stream of the demo track
  (from the banked mapping's decision records) must carry k0 at exactly
  4 consecutive ticks inside the v14-cited attack window 29–45.
- Determinism as INTEGRITY bar 9.

Structural machine bars only. **"The aperture percept is absent in the
demo", "the strike tell reads", and "no new percept class" are perceptual
lines judged at the pinned protocol on committed artifacts, never numeric
bars.**

## PERCEPTUAL rubric (fixed verbatim; judged at the v14 pinned protocol on committed artifacts, over the demo's actual coverage — right-facing, the demo's zone)

1. **DEF-1 aperture absent in the demo context** — in the K-S demo the k0
   interior no longer reads as the background showing through or a piece
   detached from the head (the snout tip reads attached through the
   active window T34–T37).
2. **The strike tell reads in the demo context** — the k0 ticks still
   read instantly as the attack state against their a0/s0 neighbors in
   the demo stream (v15's line-2 PASS is the reference, not re-opened).
3. **No NEW percept class introduced by the swap** at the a0→k0 and
   k0→s0 demo cuts, judged on the slowed APNGs — the swap must not
   manufacture a new discontinuity read (flash, pop, or state confusion)
   that the incumbent demo does not carry.

Viewing per the pinned protocol: 100% viewer zoom, fit-to-window OFF,
pre-scaled integer NN only (4x and 8x), real-speed and slowed 6/60 s.
Percepts reproducible only outside this protocol are viewer-domain (the
v14 taxonomy) and ground nothing here.

## Disposition rules (fixed verbatim)

> If all machine bars pass AND lines 1–3 pass, the adoption record STANDS
> as banked and DEF-2's register-candidate proposal is recorded DISSOLVED
> (retaining v15's forwarded-if-reversal note verbatim: "If the owner
> reverses to the incumbent, DEF-2 forwards to the temporal register
> exactly as v14 proposed (P1-bundle falsifiable)."); any machine-bar red
> STOPS the sprint at the red; if a perceptual line fails, the adoption
> record still stands as the owner's decision but the verdict records the
> failed line as a NEW owner-facing finding with a proposed routing —
> never silently absorbed.

The verdict additionally records: a DEF-3 note (the original sighting was
resampled viewing; these artifacts carry the pinned protocol; if the
owner re-watches in Edge the resampling contributor applies — context,
not evidence); explicit non-claims (no integration, no runtime claims,
at-speed fusion STILL unmeasured — the banked capture design remains the
owner-sequenced instrument; zero banked bytes moved); the council
reconciliation appendix; presentation scored separately from accuracy.

## QUALITY bars (blocking)

- **HFO pass** on `verdict.md` and the register entry (owner register;
  severity-honest verbs; no promises; no lore; accuracy and presentation
  scored separately).
- **One consolidated cross-vendor council call** (Kimi K2.5, <= 8k tokens
  total, `--max-tokens ~2600`, response redirected to a file and read as
  UTF-8, the FULL primary evidence inlined — the register text, the
  reproduction/swap-purity results, the rubric verdicts, the relevant v15
  verdict quotes) attacking: (1) adoption-record scope honesty (does the
  pointer over-claim the owner's words? does it imply integration?);
  (2) demo-harness equivalence (does the incumbent-reproduction bar
  actually pin the swap to the sighting pipeline, or is there a seam it
  misses?); (3) frozen-state integrity across the deepened v13/v14/v15
  pin lattice; (4) DEF-2 dissolution honesty (is dissolving before
  at-speed capture honest, given the contingency logic?); (5) the biggest
  unthought risk. Every REFUTED re-verified against primary bytes before
  adoption (v12–v15 precedent); reconciliation banked in the verdict
  appendix; adoptions folded before the final commit.

## Hard boundaries (this sprint)

ZERO new pixels, sprites, or releases — nothing added under `exports/`;
no edits to any banked pose PNG, banked tool, banked verdict, pinned
module (including `remedy_masks.py` and `remedy_metrics.py`), or the
remedy-v15 bytes; no re-opening or re-scoring the v15 selection (K-O and
K-R remain banked alternatives, not re-litigated); no integration, no
game-two writes, no runtime claims, no capture execution; no DEF-2
adjudication beyond the disposition recording; no work on "other visual
flaws"; no lore; no polling mail; staging under the system temp root
only, never inside the repo; APNG delays and composition via banked
encoders only; drawn labels SEAM_FONT glyphs only. Budget: one sprint,
zero new sprites, <= 12 committed playback/inspection artifacts + report
+ manifest, one council call <= 8k tokens, no second proof family.

## Stop conditions

The sprint stops after: this bundle (rationale + register + tool + tests)
committed before any v16 artifact exists → artifacts built and
self-checked → full suite + pre-banking gate green → the three prior
`--check`s green → council + HFO folded → verdict banked → push.
STOP-and-re-ask conditions (all valid, bankable outcomes): the demo
pipeline cannot be driven with substituted poses without editing a pinned
module; the incumbent rebuild does not reproduce the committed v13 bytes;
a genuine ambiguity in what "Approved, proceed" covers materially changes
the register entry. Any INTEGRITY red stops the sprint at the red.

## Mail-in status (step 0, recorded here for the verdict)

Inbox at step 0: only `done/` — no new receipts, nothing owed, nothing
polled. No outbound mail is due: the step-0 drift (`da5119c8`→`546769ff`,
all 5 pinned blobs byte-identical, attack_timing 5/4/8/13 re-verified at
the new pin) was identity-only, committed alone as `aa36857`; the
standing content-drift note protocol did not trigger. The only outbound
mail this sprint would be a re-pin note if committed content drift lands
mid-sprint.
