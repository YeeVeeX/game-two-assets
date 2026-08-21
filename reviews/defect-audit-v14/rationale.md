# Defect audit v14 — attack-read integrity audit (pre-registration)

Sprint question: the owner reviewed the v13 demo APNG live (Edge, maximized
window, browser-scaled) and reported "the head losing a piece inside it when
it does the attack movement, plus other visual flaws." Characterize that
defect class deterministically over BANKED BYTES ONLY: for every banked pose
and every cut of the banked attack sequence, what interior-structure
conditions exist in the bytes, which emerge only across cuts at speed, and
which are artifacts of the viewing chain? Deliverables: one audit tool
(`tools/pose_integrity_metrics.py`), its tests, controlled playback +
inspection artifacts in this directory, and a classified defect register
(`verdict.md`) with per-defect routing proposals.

**This sprint fixes nothing.** Zero new creature pixels, zero exports, zero
releases, zero edits to any banked pose PNG, banked tool, or banked verdict
(fix-before-characterize is the named failure mode; a banked-pose edit is an
owner-approved authoring decision, v15+ candidate). If the audit finds ZERO
bytes-domain defects and the temporal/viewer analysis fully explains the
sighting, that is a valid and complete verdict — no defect is manufactured
to justify the sprint.

These bars are fixed BEFORE the tool, the tests, or any artifact exists
(v11/v13 rationale law). No bar may be added, removed, reworded, or
reinterpreted after artifacts exist.

## The audit subject (fixed here)

- **Sprite set (hole/accent inventory):** all 22 banked creature exports —
  11 poses (`idle, f0, f1, f2, f3, a0, k0, r0, w0, s0, x0`) x 2 facings
  (down, right), consumed at their banked release.json pins.
- **The attack sequence (cut analysis):** the banked lane-B timeline
  (v7 winner, carried v9/v13) — `w0 | a0x4 | k0x4 | s0 | r0x6 | x0` over
  the pinned windup 5 / active 4 / recovery 8, with idle context ticks on
  both ends; lunge offsets windup −3 / active +6 along facing
  (`manifests/render-reference.json`, value-anchored at the fresh pin).
  Pose selection per tick is derived via the banked v13 consumer's
  `select_pose` (imported unmodified) over mechanically built attack-state
  records, so the audited stream is BY CONSTRUCTION the declared
  integration mapping — the same mapping that produced the demo APNG the
  owner watched. The cut sequence under analysis is the stream's ordered
  pose classes: `idle -> w0 -> a0 -> k0 -> s0 -> r0 -> x0 -> idle`
  (7 cuts), per facing.
- **Playback geometry:** stationary attack cycle (the demo's attack segment
  was post-arrival, stationary), creature in the middle tile of a 3-tile
  window along facing, over the exact zone_1/zone_2 palettes, composed via
  the banked `compose_cell` — banked bytes at integer offsets, no
  repainting, no resampling.

## The domain taxonomy (fixed here; every register entry gets exactly one)

- **`bytes`** — the condition is demonstrable in a single banked export's
  pixels: an interior transparent hole, or an interior opaque region whose
  color is optically background-equivalent (measured against the pinned
  zone palettes). Machine evidence on the PNG bytes decides presence.
- **`temporal`** — the condition emerges only ACROSS pose cuts at playback
  speed under the pinned viewing protocol below; each single frame is
  unremarkable or already banked as adjudicated art.
- **`viewer`** — the condition is absent in the bytes AND absent under the
  pinned integer-NN protocol; it appears only under resampled viewing
  (browser auto-fit, non-integer scaling, smoothing). The sighting context
  (Edge, maximized, browser-scaled 4x APNG) makes this class live.

Assignment rule, applied in order: demonstrable in a single frame's bytes
-> `bytes`; else reproducible under the pinned integer-NN playback ->
`temporal`; else -> `viewer`. Secondary contributors are cross-referenced,
never double-registered. The bytes-domain analysis (machine, on banked
export bytes) is the ONLY authority for presence/absence in pixels; no
"sprite defect" verdict may rest on a resampled view.

## The pinned viewing protocol (fixed here; every playback artifact carries it)

- Artifacts are pre-scaled integer nearest-neighbor at 4x AND 8x; viewed at
  100% viewer zoom with fit-to-window OFF. No other viewing condition may
  ground a verdict line.
- APNG delays via the banked encoder: real-speed = exact `(1, 60)` per tick
  with a `(30, 60)` final hold; slowed variant = `(6, 60)` per tick (6x
  slower, integer multiple of the tick) with the same `(30, 60)` final
  hold. Both delay lists are declared in the manifest.
- Per-tick strips at 8x NN over both zone palettes are the stills-domain
  evidence; the APNGs are the at-speed evidence.
- Percepts reproducible only outside this protocol are `viewer`-domain by
  definition.

## Banked-verdict scope check (risk 2, verified against the banked texts)

What the attack-era verdicts DID adjudicate about head/interior structure:

- **v2 (k0):** "dome and eye rows are byte-exact copies at the declared
  shifts (machine-verified in tests); the jaw rows are silhouette-identical
  to their source idle rows in both facings (verified: pure interior
  recolor) — the head translates rigidly and does not deform; the state
  marker is added below the intact eyes." Rubric line 1 banked the jaw gape
  + brace as the readable strike tell at 1x. Head-region share of change
  reported (37.74% / 64.29%).
- **v3 (a0):** "the k0 jaw-gape rows contribute **zero** to the 27.18%
  silhouette delta (coverage identical — the gape is an interior recolor)";
  head blocks byte-exact at declared shifts; the head-led delta adjudicated
  as deliberate crouch-compression, not defect (council Q3).
- **v5 (r0):** "r0 head/eye cluster byte-exact at the declared translation"
  (down (+2,+3), right (+1,+4)); no jaw gape authored.
- **v6 (w0/s0):** head/eye cluster byte-exact at declared translations for
  all four in-betweens; "no gape authored in any in-between"; all cut
  metrics silhouette XOR (bridging bar, nearest-neighbor bar).
- **v7 (x0):** head/eye cluster byte-exact at the declared VIRGIN
  translation; no gape authored; cut metrics silhouette XOR.

What NO banked rubric line adjudicated (the unadjudicated remainder this
sprint audits):

1. **Interior-color continuity across cuts.** Every banked cut metric is
   silhouette XOR (100·XOR/union on alpha) — structurally blind to interior
   recolors by v3's own banked words ("the gape... contributes zero to the
   silhouette delta"). No banked bar measured what an interior region DOES
   at a cut.
2. **Interior-region-vs-background discriminability.** v2 measured
   flash-vs-floor and v3 accent-vs-crimson contrast; no banked line measured
   the gape/eye accent color against the ZONE FLOOR palettes — the condition
   under which an interior region reads as the background showing through.
3. **Interior transparency.** The phase-0 contract enforces hard alpha; no
   banked bar asserted the absence (or cataloged the presence) of interior
   transparent regions.

Scope consequence, stated plainly: v2's PASS ("the gape + brace read as the
strike tell at 1x") stands and is not re-opened — "the tell reads as a
state" and "the tell's interior placement/color can read as structural
dropout" can both be true; the second question is the new, unadjudicated
one. Nothing in this sprint re-opens a banked PASS or softens a banked
FAIL; a confirmed defect is a NEW finding banked under this sprint's own
bars. Register items (a)–(o)/x0 stay a separate track: if a temporal-domain
finding here overlaps a lettered item, the verdict cross-references it and
routes the at-speed half to that register rather than duplicating it.

## INTEGRITY bars (any red stops the sprint; all-must-pass)

1. **Full suite green** including the new tests
   (`.venv/Scripts/python.exe -m unittest discover -s tests`).
2. **Both asset_gate runs exit 0** — step 0 (done: content re-pin
   `c5c146d` -> `1b0d3dd`, the J1 renderer.rb perf refactor, executed
   approve-by-default with every render-reference constant value-re-verified
   and `attack_timing` 5/4/8/13 re-verified; gate exit 0 at `1b0d3dd`) and
   again immediately before banking.
3. **Hole detector proven in BOTH directions on synthetic fixtures** —
   finds every planted interior hole (exact count/area/bbox) AND stays
   silent on hole-free fixtures (solid, concave-open, channel-to-edge,
   edge-touching transparency); the 4-connectivity convention is
   test-asserted explicitly (a diagonally-sealed ring encloses under the
   declared convention).
4. **All 22 banked sprites analyzed** (11 poses x 2 facings), zero skipped
   — machine-counted in the report.
5. **Every playback artifact double-build deterministic** (two independent
   in-process builds byte-identical) **and regenerated byte-identical by
   `--check`** against the committed files.
6. **Banked tool files untouched** — every imported banked module SHA-256
   pinned in `defect-manifest.json` and re-verified by `--check` and the
   tests; `tools/export_assets.py` / `tools/make_release.py` untouched.
7. **26 banked export pins byte-verified** (the standing
   `check_export_pins`).
8. **Zero writes into `../game-two`** (read-only `git -C ../game-two
   show/log/diff` from this repo's cwd only).
9. **Zero new exports, pixels, or releases** — no new `exports/`
   directories (guard extended to `defect-audit-v14`), no release
   manifests, no pixel edits anywhere.
10. **SYNTHETIC/EXP labels on every artifact** — filename (`synthetic-`),
    manifest (`provenance.class = "SYNTHETIC"`), and pixels (drawn banner
    on strips; drawn per-frame label on APNGs).
11. **Every engine/banked citation at the fresh pin** — game-two
    `1b0d3dd16bc53a84696d5d179213f764f2e3343f` — with file:line, read this
    session.
12. **The owner-redirect note banked mechanical-register-only**
    (`docs/owner-redirects.md`: dated one-liners, no lore, no narrative).

## MEASUREMENT bars (machine facts; fixed definitions)

- **Interior-hole detection** (per pose, per facing): flood-fill the
  transparent field from outside the 32x32 canvas (via a 1px border ring,
  4-connected over non-opaque cells); any transparent region unreachable
  from outside is an interior hole. Report count, area, bbox, and
  canvas-row band per hole. Convention notes, fixed: 4-connectivity means a
  diagonally-sealed enclosure counts as interior; a region connected to the
  border by any transparent path (however thin) is exterior; alpha 255 is
  opaque, anything else is transparent (the contract's hard-alpha law makes
  the set {0, 255} in practice, and the gate enforces it upstream).
- **Hole deltas across the attack sequence** (per facing, 7 cuts): holes
  matched between neighboring poses by pixel-set overlap; `appear` /
  `disappear` at a cut = the candidate class; a hole stable across all
  poses is art, not defect.
- **Consecutive-pair change localization** (per facing, 7 cuts, sprite-local
  32x32 space): 4-connected clusters of changed pixels per cut, reported in
  two classes — `silhouette` (opaque in exactly one of the pair; the banked
  XOR class) and `recolor` (opaque in both, RGB differs; the class every
  banked cut metric was blind to). Per cluster: area, bbox, canvas-row
  band. **Localization is REPORTING, not a bar** — no hardcoded "head"
  rectangle anywhere; region naming happens at read time from the reported
  bands.
- **Accent-pixel table** (per pose, per facing): 4-connected clusters of
  the frozen ramp accent `#140e0c` (the banked ACCENT_RGB, eyes/feet/gape
  marker); per cluster: area, bbox, centroid. The eye clusters and any
  other accent structure fall out mechanically — no cluster is pre-labeled.
- **Context contrast reporting**: WCAG contrast ratio + RGB distance of the
  accent color vs zone_1/zone_2 floor and grid and vs the body color —
  context numbers for the perceptual read, never a bar.
- **Stream consistency** (machine bar): the audit tick stream's ordered
  pose classes must equal the pre-registered cut sequence exactly
  (`idle, w0, a0, k0, s0, r0, x0, idle`), and its per-tick (pose, offset)
  records must be produced by the banked `select_pose` unmodified.
- **Determinism**: report JSON, strips, and APNGs double-build
  byte-identical in-process; `--check` regenerates all committed artifacts
  byte-identically.

Structural machine bars only — hole inventories, deltas, cluster tables,
and contrast numbers are machine facts. **"Reads as the head losing a
piece" is a perceptual line judged at the pre-registered viewing protocol
above, never a numeric bar** (the banked category-law lesson: v9's
pre-registered-salience class error is not repeated here — no cross-class
numeric dominance claim is registered or needed).

## The defect register (verdict.md shape, fixed here)

One entry per finding: id `DEF-1..n`, pose(s) + facing(s), domain
(`bytes` | `temporal` | `viewer`), machine evidence with exact numbers,
perceptual read at the declared protocol, cross-reference to the
banked-verdict scope check (which banked line, if any, sits adjacent and
why it is not re-opened), severity, and proposed routing ranked by cost.
The owner's sighting is explicitly resolved to a register entry (or
explicitly recorded as not-reproduced-in-bytes with the viewer/temporal
analysis that remains). Routing for any bytes-domain defect is "propose an
authoring sprint" — never "author now". Presentation scores separate from
accuracy. Explicit non-claims: no banked verdict touched, zero new pixels,
nothing authored, nothing scheduled.

## QUALITY bars (blocking)

- **HFO pass** on `verdict.md` and `docs/owner-redirects.md` (owner
  register; no promises; severity-honest verbs; accuracy and presentation
  scored separately).
- **One consolidated cross-vendor council call** (Kimi K2.5, <= 8k tokens
  total, response redirected to a file and read as UTF-8, ~2600 max output
  tokens) attacking: (1) hole-detector soundness — does flood-fill
  unreachability define "interior hole" for hard-alpha 32x32 sprites; edge
  cases; (2) domain-classification rigor — could a `viewer` finding
  actually be `bytes`; is the temporal class falsifiable; (3)
  re-adjudication creep — does any register entry re-open a banked verdict;
  (4) routing honesty — is "propose authoring" smuggling a decision; (5)
  the biggest unthought risk. The brief inlines the FULL primary evidence
  (register draft, detector core functions, the banked-verdict quotes).
  Every REFUTED re-verified against primary bytes before adoption (v12/v13
  precedent); reconciliation banked in the verdict appendix; adoptions
  folded before the final commit.

## Mail-in status (step 0, recorded here for the verdict)

Inbox at step 0: only `done/` (no new receipts; nothing owed). The only
outbound mail this sprint is the protocol-mandated re-pin note for the
`c5c146d` -> `1b0d3dd` content drift
(`from-game-two-assets-v14-repin-1b0d3dd.md`, fire-and-forget, no receipt
requested — the standing exception named in the brief).

## Stop conditions

The sprint stops after: rationale + owner-redirect record + tool + tests
banked before any artifact exists (this commit) -> artifacts generated and
self-checked -> full suite + pre-banking gate green -> council + HFO folded
-> verdict banked -> push. Any INTEGRITY red stops the sprint at the red.
No authoring, no second audit tool, no new lanes, no settle-bob work, no
capture execution, no game-side code, no adjudication of any lettered
register item, no polling mail.
