# Calibration v1 — lane-B motion-coherence rationale

Sprint-1 question (the banked v0 next-hypothesis, and the cross-vendor
untested-risk finding): does the winning lane-B compact silhouette hold
identity frame-to-frame in motion at native 1x, or does it degrade into an
unstable blob? Scope: `player_1_lane_b` 4-frame walk cycles, down and right
facings only, derived from the frozen calibration-v0 idles. No new lanes, no
idle redesign, no other poses.

## Shared constraints (inherited, unchanged)

- 32x32 RGBA8, hard alpha, pixels inside `[2,2,29,29]`, anchor `[16,30]`.
- The frozen 5-color ramp: `#140e0c` accent, `#401c10` outline, `#8c3818`
  shade, `#eb7828` base, `#ffa050` highlight. No new colors, no recolors.
- Feet-contact row within +-1px of the idle baseline (row 27) on every frame.
- Generic mechanical IDs: `player_1_lane_b_walk_{facing}_f{0..3}`.

## Source-format decision: one-spec-one-frame stills (spike evidence)

The mandated spike (`tmp/spike/run_spike.py`, discarded; output reproduced
here) compared the proven one-spec-one-frame chain against a multi-frame
`.aseprite` built by script and exported with `--save-as` frame patterns:

```
single spike_frame_a: STABLE e21c14618821c2c0
single spike_frame_b: STABLE dccde6b8da821832
multi walk.aseprite: STABLE 56675958f0a41d93
multi frame0.png: STABLE e21c14618821c2c0
multi frame1.png: STABLE dccde6b8da821832
multi walk.gif: STABLE 8999f1fcd4e4ca71
bytes spike_frame_a vs frame0.png: EQUAL
bytes spike_frame_b vs frame1.png: EQUAL
```

Findings: (1) both chains are byte-deterministic across runs; (2) multi-frame
per-frame PNGs are byte-identical to the stills, so the container adds zero
output value; (3) `spike_frame_a` (the idle grid) hashed `e21c1461…` — equal
to the banked calibration-v0 idle export, confirming cross-session
determinism of the whole chain; (4) GIF export is also byte-stable, so an
animated viewing aid is feasible without becoming a blocking artifact.

**Decision: stills win.** Per-frame pixel verification (`export_assets.py`
verifies every PNG against its spec), the gate's per-asset hash chain, and
the release manifest format all continue unchanged; a multi-frame source
would add a second pixel truth without adding any capability. The .aseprite
sources here are per-frame, exactly as in v0.

## Cycle structure (KB-grounded)

KB `game-research/aseprite-pixel-art-mastery.md` (verified 2026-04-11):
contact -> down -> pass -> up are the four key poses; 4 frames is the pixel-art
minimum; the pass phase carries the vertical bob. KB
`game-research/technical-drawing-for-game-art.md` (verified 2026-04-11):
1-2px body bounce; contact frames hold longest. KB
`game-research/pixel-art-pygame-and-2d-engine-reference.md` (verified
2026-04-10): height offsets are quantized to +-1px at 32x32, and the planted
leg slides while the body stays centered — translation supplies forward
motion, the cycle supplies gait. Sub-pixel animation (AA-cluster
manipulation) is explicitly not applicable under a 5-color hard-alpha ramp,
and smear frames are doctrine for fast attacks, not walk cycles; both are
consciously out of scope.

The 4-frame sampling used here: **contact A (body at idle height) -> pass
(body +1px, legs extended) -> contact B (mirror) -> pass (the frozen idle
verbatim)**. Amplitude is deliberately conservative — 1px bob, feet-only
stagger — because the hypothesis under test is identity stability, not
maximal liveliness; translation at 8px/frame dominates apparent motion.
Including the idle as f3 also guarantees a seamless walk<->stand transition
(the cycle passes through the standing pose every stride).

## Per-frame pose plan

Down (front view; feet at cols 12-14 and 17-19, contact row 27):

- `f0` contact-L: left foot planted (idle geometry); right foot lifted 1px —
  dark cap `kkk` at row 26, row 27 empty beneath it; body rows 4-23 shifted
  1px LEFT (weight over the planted foot).
- `f1` pass-high: whole body shifted up 1 (rows 3-22); both feet planted with
  5-tall legs (rows 23-27) — legs extended, body risen.
- `f2` contact-R: mirror of f0 (right planted, left lifted, body 1px RIGHT).
- `f3` pass-mid: the frozen idle spec copied forward verbatim (declared in
  provenance; export bytes equal the v0 idle export).

Revision history: the first authored down cycle had no sway (contact frames
changed only the feet). The cross-vendor critique attacked its step beat, and
measurement confirmed the attack: the f2->f3 and f3->f0 transitions changed
only 3 dark near-floor-value pixels (popping 1.2%) against 9.43% on the pass
transitions — an asymmetric beat whose step tick was near-invisible on dark
floors at 1x. The 1px weight-shift sway (KB front-walk bounce/sway doctrine)
moves the whole bright mass every transition: pair deltas became
19.64/19.0/15.87/15.87 with centroid-x oscillating +-0.95px. The right cycle
and both pass frames were not touched.

Right (profile; rear foot cols 10-12, front foot cols 18-20, contact row 27):

- `f0` stride-wide: rear foot -2 (cols 8-10), front foot +2 (cols 20-22),
  both planted — full extension under tail and snout.
- `f1` pass-high: body up 1, feet at idle columns with 5-tall legs.
- `f2` stride-narrow: rear +2 (cols 12-14), front -2 (cols 16-18), 1px gap —
  legs gathered mid-scissor; antiphase interpolation is monotonic
  (rear 8->10->12->10, front 20->18->16->18).
- `f3` pass-mid: the frozen idle verbatim (declared).

Foot positions never cross or merge (minimum 1px gap), all masses stay
within a few pixels of idle (feet stagger costs 3px; extended legs add 6px),
and the head/eye/snout cluster — the identity anchor — translates rigidly
(1px sway/bob) and never deforms in any frame.

## Derivation integrity

Frames were derived from the frozen idle specs by mechanical row edits
(authoring script asserted the expected idle feet geometry before writing;
every spec passed `pixel_spec.load_spec` contract validation). Exports are
verified pixel-for-pixel against specs by the pinned exporter; `walk_*_f3`
export hashes equal the calibration-v0 idle export hashes, proving verbatim
derivation. `tools/export_assets.py` is byte-identical to the version pinned
by the calibration-v0 release manifest.

## Measurement plan (what the verdict must cite)

`tools/motion_metrics.py` (tested) reports per facing: per-frame mass, bbox,
feet-contact row and drift vs idle, centroid; per consecutive cyclic pair:
silhouette XOR, union, popping percentage, recolored-overlap count; plus the
idle-down vs idle-right cross-pose delta as the popping ceiling reference
(v0 measured 44.4% between facings — a walk cycle that pops anywhere near
the cross-facing delta is changing identity, not animating). Hard `--check`
lines: feet row within +-1px of idle on every frame; no static consecutive
pair. `tools/make_motion_sheet.py` (tested, deterministic) renders per
facing: FILM strip (idle control + 4 frames), WALK phase row (frames along a
one-tile slide at 8px/frame including the f3->f0 loop seam), sliding-IDLE
control row, both zones; RING row; consecutive-DIFF row at 2x; 2x/4x
diagnostics.

Pass bar (fixed before looking): accuracy — all gate checks, feet rule, no
static pair; presentation — identity holds at 1x in both zones, no pop at
any pair including the loop seam, feet contact reads, facing never
ambiguous mid-cycle, ring dominance and body-flash headroom preserved, and
the WALK row must beat the sliding-IDLE control row (otherwise animation
adds nothing and the sprint answer is "reject, next hypothesis").
