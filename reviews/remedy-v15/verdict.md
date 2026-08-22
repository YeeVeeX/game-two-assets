# Remedy exploration v15 — DEF-1 k0 gape treatment selection verdict

**Answer first: K-S is selected.** The shade recolor (`#8c3818` over exactly
the 16px/8px machine-derived gape masks) resolves the DEF-1 aperture percept
on both facings over both pinned zone palettes — the eyes return as two
separate clusters through the whole active window on down, the snout tip
reads attached on right — while the strike tell still lands instantly at the
pinned protocol. K-R (two-tone) also qualifies; the pre-registered tie-break
selects K-S on both prongs (cleaner line-1 resolution: no near-floor pixel
remains inside the face; smaller departure: single-color recolor). K-O, the
bracketing control, fails the aperture line exactly as pre-registered — the
threshold sits between outline-level (~1.1–1.2:1) and shade-level
(~2.1–2.3:1) floor contrast. Status per contract: **selectable candidate
only** — no integration (v17 open), no banked byte moved, the banked k0
remains the pinned history every banked sheet regenerates from; adopting
K-S anywhere is a later owner decision costing one pointer.

Reviewed artifacts (SHA-256 prefixes; full hashes in `remedy-manifest.json`):

- `exports/remedy-v15/release.json` (`37ea4a8a8925eb4b…`) — six variant
  exports, gate-valid at the live pin (source commit `0615288`, game commit
  `da5119c8`); first export `65192abbe5ff3fe4…`.
- `reviews/remedy-v15/gape-masks.json` (`9dd81786121fd947…`) — the
  machine-derived masks (16 px down `[12,13,19,14]`, 8 px right
  `[24,13,27,14]`), committed with the pre-registration before any variant
  pixel existed (`7935a0e`).
- `remedy-report.json` (`662a77c7d010a7d5…`) — the machine tables: per
  variant diff/eye/hole/cut verdicts, lane contrast, incumbent reference.
- Comparison strips, four stream-rows each (INCUMBENT, KS, KO, KR) over
  T05–T12 at 8x NN: `synthetic-remedy-strip-down-z1-8x.png`
  (`e0cbd1dd…`), `-down-z2-` (`adb419f6…`), `-right-z1-` (`8f099821…`),
  `-right-z2-` (`41073e3d…`).
- Twenty-four side-by-side APNGs (incumbent pane + variant pane per frame,
  full 21-tick stream, real 1/60 s and slowed 6/60 s, 4x and 8x) — hashes
  in the manifest; all 29 artifacts double-build identical
  (`double_build_identical: true`) and `--check`-regenerated.
- Pre-registration: `reviews/remedy-v15/rationale.md`, committed with the
  toolchain (`7935a0e`) **before any variant pixel or artifact existed**.
  No bar was added, removed, or reworded afterwards.
- Session model `us.anthropic.claude-fable-5` (verified from `PI_MODEL`).
  Council seat cross-vendor (Kimi K2.5, `moonshotai.kimi-k2.5`), one
  consolidated adversarial call (3,745 of the 8k cap); reconciliation in
  the appendix — both REFUTED verdicts re-verified against primaries and
  partially dissolved, four kernels adopted.

Sprint question (rationale, fixed first): can an in-ramp,
silhouette-invariant recolor of the k0 gape resolve the DEF-1 aperture
percept without losing the banked strike tell — or should the incumbent
stand?

## Accuracy — all-must-pass (the pre-registered INTEGRITY bars)

| # | Bar | Verdict | Evidence |
|---|---|---|---|
| 1 | Full suite green including new tests | PASS | full run: 593 tests, 0 failures, exit 0 (~2845 s; the 3 pre-bank skips activated post-bank); commit hooks green on every commit |
| 2 | Both asset_gate runs exit 0 | PASS | step 0: exit 0 after the mechanical identity re-pin `a69b2a2` (`3c0ff6c`→`da5119c`, 9 docs/test-only hops, all 5 pinned blobs identical, attack_timing 5/4/8/13 re-verified); pre-banking: exit 0 with remedy-v15 gate-validated at the live pin (trailing identity WARNING `da5119c8`→`513b53c`, content verified identical by the gate's committed-HEAD hash check — re-pins at the v16 checkpoint) |
| 3 | `track_recompose --check` AND `pose_integrity_metrics --check` exit 0 at banking | PASS | both run at banking this session, both exit 0; plus the pin-compare test over both manifests in the suite |
| 4 | Alpha identity 6/6 | PASS | `machine_bars.alpha_identity_all: true` — decoded alpha planes byte-identical to the banked k0 (silhouette invariance by construction: every banked v2/v3 XOR/mass/bbox/feet bar stays literally valid) |
| 5 | Diff declaration 6/6 | PASS | `diff_declaration_all: true` — RGB differs at exactly the declared sets (K-S/K-O: the gape mask; K-R: the mask under the row split), frozen ramp only, disjoint from eyes and feet caps |
| 6 | Eye integrity 6/6 | PASS | `eye_integrity_all: true` — down variants carry exactly two separate 2x2 accent eye clusters `[12,11,13,12]` / `[18,11,19,12]` + the two banked feet caps (the un-merge, machine-proved); right variants carry the banked accent set minus the gape band |
| 7 | Interior holes = 0 in all six | PASS | `interior_holes_zero_all: true` (banked detector, unmodified) |
| 8 | 26 banked pins + own release pins + directory guards | PASS | `check_export_pins`: 26 verified, zero failures; release pins verified; `exports/remedy-v15/` contains exactly the six PNGs + release.json; `exports/calibration-*` dirs equal the seven banked ids |
| 9 | Banked tools untouched | PASS | 23 module pins in `remedy-manifest.json` re-verified by `--check` and tests; v13/v14 manifest pins compared against live files in the suite; `export_assets.py`/`make_release.py` untouched |
| 10 | Specs contract-valid | PASS | all six load under the banked `pixel_spec.load_spec`; the pinned exporter's verification passed on every export |
| 11 | Determinism | PASS | spec→aseprite→export chain byte-identical across two independent builds (verified before sources were committed); all 29 artifacts double-build identical; `--check` regenerates everything byte-identically |
| 12 | Zero writes into `../game-two` | PASS | read-only `git -C ../game-two show/log/rev-parse` from this repo's cwd throughout |
| 13 | SYNTHETIC/EXP labels everywhere | PASS | filenames carry `synthetic-remedy`; manifest + report carry `provenance.class = "SYNTHETIC"`; strips carry the drawn banner + protocol line; every APNG frame carries `SYNTHETIC REMEDY EXP` in pixels |
| 14 | Citations at the fresh pin; owner-approval verbatim | PASS | v2/v3/v14 quotes read from committed texts this session; "Approved, proceed" recorded verbatim in the rationale before any pixel existed |

**Accuracy: 14/14 integrity bars.**

## The machine findings (report highlights; exact numbers in the JSON)

- **The un-merge is in the cluster tables.** Incumbent k0-down: one merged
  24px accent mass `[12,11,19,14]`, no separate eyes. Every down variant:
  two separate 2x2 eye clusters at the v2-banked translated positions plus
  the two 3px feet caps — nothing else. Right variants: eye `[22,11,23,12]`
  and feet caps unchanged; the gape band is simply no longer accent.
- **Lane contrast (WCAG, banked `contrast_ratio`):** accent (incumbent)
  1.09/1.16 vs floors, 6.60 vs body; shade 2.26/2.12 vs floors, 2.69 vs
  body; outline 1.17/1.10 vs floors, 5.21 vs body. Context, never a bar.
- **Cut structure preserved exactly.** Every variant's a0→k0 and k0→s0
  silhouette clusters equal the banked k0's
  (`silhouette_cuts_equal_banked_all: true`) — the alpha-identity
  corollary, asserted per cut. Only the recolor class moves (e.g. ks-down
  a0→k0: silhouette 78px = banked, recolor 87px vs the incumbent's 79 —
  the gape pixels now change color instead of matching the accent eyes).
- **Ramp discipline.** Every variant histogram spans exactly the frozen
  five colors; e.g. kr-right: accent 10 (eyes+feet only), outline 85 (+4),
  shade 26 (+4), body 112, highlight 26.

## Perceptual rubric (judged at the pinned protocol on the committed artifacts; per line, per facing, per zone)

Viewing per the manifest protocol: 100% zoom, fit-to-window off, pre-scaled
integer NN, strips at 8x over both zone palettes, APNGs real-speed and
slowed 6/60 s at 4x/8x. Session-vision verdicts on the committed strips and
APNG frames; the at-speed fusion question stays routed (non-claims below).

**Line 1 — DEF-1 aperture resolved:**

| Lane | down z1 | down z2 | right z1 | right z2 |
|---|---|---|---|---|
| K-S | PASS | PASS | PASS | PASS |
| K-O | FAIL | FAIL | FAIL | FAIL |
| K-R | PASS | PASS | PASS | PASS |

K-S: the mouth band reads as creature material (the shade family already
shades the body flank), the face keeps visible eye structure through
T07–T10, the right snout tip reads attached — in the side-by-side APNG
frames the incumbent's floating-tip/hollow-face percept is absent from the
K-S pane. K-R: same resolution; the outline lower row reads as a mouth
line, not floor. K-O: the band still reads near-floor over both palettes
(1.17/1.10); the aperture percept is reduced but present; at 8x the eyes
separate from the band only with effort (accent-vs-outline 1.27). The
bracketing control behaved exactly as pre-registered, which localizes the
perceptual threshold between outline-level and shade-level floor contrast
— and its failure alongside K-S's pass is consistent with the aperture
percept being floor-contrast-driven, the v14 DEF-1 mechanism.

**Line 2 — strike tell preserved (v2 rubric line 1, "Tell reads at 1x —
PASS", is the reference, not re-opened):**

| Lane | down z1 | down z2 | right z1 | right z2 |
|---|---|---|---|---|
| K-S | PASS | PASS | PASS | PASS |
| K-O | PASS | PASS | PASS | PASS |
| K-R | PASS | PASS | PASS | PASS |

The measured trade is stated first: the band's contrast against the body
drops from the incumbent's 6.60:1 to 2.69:1 on K-S — a large reduction in
the marker's color pop, not a small one. The state read does not rest on
that number alone: the tell is carried by structure — a 16px/8px interior
mouth band plus the 2px-wider brace (down) / crouch + forward reach
(right) plus the +6px lunge cell, in pose dimensions no walk frame uses
(v2's banked structural finding) — and the k0 ticks read instantly as the
strike against their a0/s0 neighbors in every strip column, all three
lanes, both zones. That judgment is session-vision at the pinned protocol
on the committed artifacts (no blind A/B instrument exists in this repo);
K-R keeps a 5.21:1 dark line inside the mouth; K-O keeps 5.21 everywhere
at the cost of line 1.

**Line 3 — eyes visible on down through the active window (T07–T10):**
K-S PASS / K-O FAIL (the eye row separates from the band only with effort
at 8x; at the APNG scales they fuse into the incumbent-style dark mass) /
K-R PASS. Both zones.

**Line 4 — identity / no new state confusion:** PASS all lanes, both
facings, both zones. All colors are existing ramp members already present
in every pose; no read resembles the hurt flash (bright crimson full-body
replacement), the telegraph (gold slab + hot-red rim on humans), or
transition gold. K-R's two-tone mouth stays within the creature's own
shading grammar.

## Decision-rule application (rule fixed verbatim in the rationale)

- Machine bars: all pass, 6/6 variants.
- K-O: fails line 1 (and line 3 on down) → not selectable; its
  pre-registered control role is fulfilled.
- K-S and K-R: pass lines 1–4 on both facings and both zones, and both
  beat the incumbent on line 1 without losing line 2 — the incumbent's
  aperture read (eyes absorbed on down; snout severed on right) is absent
  in both, decisively, in the aligned strips and side-by-side APNGs.
- Multiple qualifiers → pre-registered tie-break: (a) stronger line-1
  resolution — K-S leaves no near-floor-contrast pixel inside the face
  (K-R's row 14 keeps outline at 1.17/1.10 as a deliberate depth line;
  legible at 8x, but at 4x it darkens the mouth's lower half back toward
  the incumbent percept); if judged even, (b) smaller departure from the
  banked k0 — single-color recolor beats two-tone. Both prongs select
  **K-S**.
- Incumbent-wins was genuinely reachable (the rule defaults there on any
  tie or uncertainty; K-O demonstrates a full lane failing the aperture
  line); it was not needed — no tie, no uncertainty on the deciding lines.

**Selected: `player_1_lane_b_attack_down_k0_ks` +
`player_1_lane_b_attack_right_k0_ks`** (release `remedy-v15`, origin
`procedural`, derivation notes in the release manifest).

## Register dispositions (cross-referenced, nothing re-opened)

- **DEF-1 (bytes):** remedied by the selected candidate — as a selectable
  candidate pair, owner adoption pending. The v14 register entry stands
  as banked history; no banked verdict, bar, or PASS is touched. The v2
  tell PASS is confirmed intact at this sprint's protocol on the selected
  lane (reference, not re-adjudication). If the owner prefers the
  incumbent read as art, accept-as-art remains available at zero cost —
  nothing was destroyed.
- **DEF-2 (temporal, contingent):** the v14 register-candidate proposal
  **dissolves contingent on this selection standing** — the 4-tick
  exposure of a floor-colored aperture no longer exists in the selected
  bytes. If the owner reverses to the incumbent, DEF-2 forwards to the
  temporal register exactly as v14 proposed (P1-bundle falsifiable).
  Recorded, not adjudicated.
- **DEF-3 (viewer):** unchanged; every v15 artifact carries the pinned
  protocol line; the demo-packaging convention stands.

## Presentation scores (accuracy scored separately above)

- **Comparison strips: 9/10.** The four aligned stream-rows make the
  selection question answerable in one look per zone: the incumbent's
  aperture columns sit directly above K-S's eyed, attached-mouth columns.
  Cost: right strips chunk each stream into two rows (png_reader cap).
- **Side-by-side APNGs: 8.5/10.** The per-frame incumbent/variant pairing
  puts the decisive percept in a single fixation at both speeds; per-frame
  labels keep every frame self-identifying. Cost: 24 files — the honest
  protocol matrix (3 lanes x 2 facings x 2 speeds x 2 scales) is bulky.
- **Report JSON: 8.5/10.** Every rubric-relevant machine fact (diff sets,
  cluster tables, cut identity, contrast) in one deterministic artifact.
- **Release provenance notes: 8/10.** Each export names its source bytes,
  mask, lane, and measured contrast context; concise and lore-free.

HFO gate (owner register): answer-first pyramid; severity-honest verbs
("reads as", "measured", "softer as a color pop"); the tell trade-off
disclosed with numbers rather than smoothed; no promises (selection ≠
integration; adoption is the owner's); typed uncertainty (at-speed fusion
named unmeasured, instrument named); accuracy and presentation scored on
separate axes; mechanical ids throughout; provenance notes re-read against
the same checklist.

## Structured critique and cross-vendor review (Kimi K2.5, adversarial)

One consolidated call (1,901 in / 1,844 out = 3,745 of the 8k cap,
`stop_reason=end_turn`; response file-redirected and read as UTF-8)
attacking five numbered claims with the full primary evidence inlined
(masks, contrast/cluster numbers, rubric verdicts, decision rule, banked
v2/v3 quotes). Returned verdicts: **Q1 UNCERTAIN, Q2 REFUTED, Q3
UNCERTAIN, Q4 REFUTED, Q5 UNCERTAIN.** Per the v12–v14 precedent every
charge was re-verified against primaries before adoption; both REFUTEDs
partially dissolve on the banked texts, and four real kernels were
adopted. The reconciliation:

1. **Q1 (mask-derivation soundness) — UNCERTAIN from the council; one
   kernel adopted, one charge refuted by construction.** The council
   could not verify the v2 shift constants or sprite data from a text
   brief (an evidence-availability limit, not a defect: in-repo, the
   subset assertion, the 16/8 + bbox expectations, and the v2 quotes are
   machine-enforced and tested). ADOPTED — the consistency-vs-correctness
   distinction: the diff-declaration bar proves the *implementation*
   matches the declaration (consistency); the *derivation's* correctness
   is pinned separately by the mask assertions (translated eyes must be a
   subset of k0 accent; derived mask must equal the independent v14
   report's 16/8 px and bboxes) and by the eye-integrity bar, which
   independently requires the exact banked 2x2 clusters. The
   off-by-one-baked-into-six charge is refuted by construction: the mask
   is a subtraction *from the accent set*, so it cannot contain a
   non-accent pixel, and its exact extent is cross-checked against v14's
   independently generated numbers.
2. **Q2 (tell-preservation honesty) — REFUTED by the council; the charge
   dissolves on the primary text, the wording kernel is adopted.** The
   council charged that "v2's PASS was silhouette coverage, not
   readability" — but the quote it attacked is v3's coverage line; the
   line-2 reference is v2 rubric line 1, which reads: "**Tell reads at
   1x.** PASS. … the open jaw + brace (down) and the 3px head-drop pounce
   + jaw (right) read instantly" — a readability adjudication
   (re-verified in the committed v2 verdict this session). Its companion
   charge — that the owner sighting was itself a tell-readability failure
   — contradicts the banked v14 register ("6.6:1 against the body is the
   cue; 1.09:1 against the floor is the collision"). ADOPTED: the line-2
   wording above now leads with the measured 6.60→2.69 drop, calls it
   large, grounds the surviving read in the structural mechanism rather
   than an adjective, and names its evidence class (session-vision at the
   pinned protocol; no blind A/B exists here).
3. **Q3 (frozen-state integrity) — UNCERTAIN from the council; verified
   with primaries; one residue recorded.** The registry freeze, the
   `calibration-*` glob text, the directory guard, the 23 module pins,
   and the exporter-sha equality are all machine-checked in-repo
   (`--check`, the suite, and the asset gate, which validates
   `exporter_sha256` against the live file). RESIDUE recorded as a
   carried observation, no bar added post-hoc: the standing toolchain has
   no *global* stray-file guard for exports/ outside `calibration-*` —
   remedy-v15 guards its own directory exactly; a future sprint could
   generalize the guard.
4. **Q4 (decision-rule honesty) — REFUTED by the council; the
   circularity charge dissolves on this sprint's own data; the residue is
   kept.** The charge "any recolor that separates eyes resolves the
   aperture by construction, so the incumbent was pre-defined to lose" is
   disproved by K-O: mechanically it separates the eye/band colors
   (accent ≠ outline), yet it FAILS line 1 at the protocol — the line is
   perceptual, and a full lane failed it live. Incumbent-wins was
   genuinely reachable ex ante (had the aperture percept not been
   floor-contrast-driven, all three lanes failed line 1), and this
   program has banked exactly that outcome before (v7: "The REJECT
   outcome was fully available on this line" — the pre-registered
   favorite class losing is precedented). KEPT from the council: the
   rubric's line-1 phrasing biases attention toward the fix's axis; the
   guards are line 2's independent banked reference and the
   default-to-incumbent rule — both exercised; the K-S-over-K-R tie-break
   was resolved by the two pre-registered prongs, with prong (a)
   admittedly a perceptual judgment (that is why prong (b) is mechanical).
5. **Q5 (biggest unthought risk) — UNCERTAIN; two charges refuted with
   pinned values, two kernels carried.** Refuted: "mixed combat may put
   shade on human bodies" — humans are bone `#cdc6b4` at the pinned
   baseline, not the creature ramp; "frame-adjacent merged mass at
   1/60 s" — the adjacent poses a0/s0 carry no gape band at all (the
   banked gape is k0-exclusive and binary; the k0 hold is 4 ticks, not
   2). CARRIED (recorded, not adjudicated): (i) **shade double-duty** —
   `#8c3818` now serves flank shading and the mouth marker; a future
   pose family leaning harder on shade shrinks the mouth's distinctness
   budget (watch item for v16+ authoring); (ii)
   **protocol-vs-player-viewport gap** — this selection is proven at the
   pinned adjudication standard, not in a runtime viewport; the banked
   capture design remains the instrument for the shipped read (the same
   instrument DEF-2 waits on).

Net: one wording adoption (line 2), one consistency-vs-correctness
statement (Q1), one carried toolchain observation (Q3), one recorded
rubric residue (Q4), two carried findings (Q5). No machine number
changed; no bar moved; no banked verdict touched; the selection stands.

## Non-claims

No integration and no integration schedule — game-two v17 stays open; the
one-way boundary held (read-only `git -C ../game-two` throughout). No
banked byte moved: the banked k0, all 26 banked export pins, every pinned
module, and every banked verdict are untouched (machine-verified at
banking). The at-speed fusion read of the selected candidate is
**unmeasured here** — stills and stepped playback at the pinned protocol
ground this verdict; the banked capture design (P1 scripted bundle) is the
instrument that measures 60 tps behavior, owner-sequenced. No DEF-2
adjudication (contingency recorded only). No claim about player-side
viewing environments (protocol-scoped percepts, the v14 DEF-3 law). No
work on "other visual flaws"; nothing else authored.

## Mail and pin status (step 0 + close, recorded)

- Inbox at step 0: only `done/` — no new receipts, nothing owed, nothing
  polled. Outbound: none due (the step-0 drift was identity-only; the
  standing content-drift note protocol did not trigger).
- Pins: mechanical identity re-pin `a69b2a2` (`3c0ff6c`→`da5119c8`, 9
  docs/test-only hops, all 5 pinned blobs identical, attack_timing
  5/4/8/13 re-verified), committed alone, staged-list verified. Gate exit
  0 at step 0 and immediately before banking; the pre-banking run reports
  a trailing identity-drift WARNING (`da5119c8`→`513b53c` at the final
  gate run; game-two lands ~3 commits/hour and every pinned blob stayed
  content-identical per the gate's committed-HEAD hash check) — re-pins
  at the v16 checkpoint per the banked v13/v14-close pattern.

## Stop

Sprint 15 stops here: one derivation tool, one metrics tool, 28 tests (25
pre-bank + 3 activated post-bank; full suite 593 green), one gate-valid
additive release (six
variants), 29 SYNTHETIC-labeled artifacts, one selection verdict (K-S
selected under the pre-registered rule; K-O control confirmed the
threshold; incumbent unharmed and recoverable at one pointer). Carried to
v16+: the owner adoption decision on K-S, the trailing identity re-pin,
the shade-double-duty watch item, the protocol-vs-viewport capture
question (unchanged, owner-sequenced), and — only if the owner reverses to
the incumbent — the DEF-2 register-candidate forward. No second remedy
family, no silhouette-class work, no settle-bob, no capture execution, no
game-side code; audio and tile era stay parked.
