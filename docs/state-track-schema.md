# State-track schema — DRAFT (proposal input, v13)

**Status: DRAFT.** This document is this repo's proposal input to the
capture-tool specification. **The game seat pins the schema — including
`schema_version` — at tool-spec time** (open question 1 of the banked design,
`docs/replay-capture-design.md` section 4/9). Nothing here is pinned law;
nothing here schedules, requests, or implements anything game-side. The
emitter is game-side conditional tooling (design section 2.3, gap 3), and
this repo's part is the consumer: `tools/track_recompose.py` reads exactly
this shape today, so every field below is backed by a working parser and a
machine-proved recomposition path rather than a paper proposal. The parser
is the **disposable half** of that pair: if the pinned schema differs from
this draft in any way, this repo adapts the consumer to the pinned shape —
never the reverse.

A state track is **one member of a capture bundle** (design section 4): the
bundle carries `game_commit`, seed, preconditions, the input log, the
end-state digest, and the member manifest; the track is the per-tick
semantic layer Mode T emits during offline re-execution on the strong seat.
A track is never a standalone evidence class — intake verifies it through
its bundle's `capture-manifest.json` (design section 5).

Engine citations below are file:line at game-two
`c5c146d0954260743ba895295a85caec88751f13` (the v13 pin after the
mid-sprint content re-pins: the T3/T4 waves touched `renderer.rb` —
additive typed-tile overlay + a semantic-preserving way-lock refactor, no
draw-path constant moved, owner-approved — and `nest.json`, two added
keys; every `render-reference.json` constant value-re-verified at the new
blobs; `creature.rb`, `grid_walker.rb`, `display.json`, `district.json`,
`combat.json` blob-identical `746ee8b6`→`c5c146d0`), read this session,
read-only.

## Sufficiency criterion (design section 4, restated)

The track must carry **(1)** every input the renderer's creature draw reads
and **(2)** every index the declared pose-selection mapping needs. At the
pin, `draw_creature` (renderer.rb:549-597) reads: position
(`c.x`/`c.y` = `walker.px`/`walker.py`, creature.rb:60-61, drawn at
renderer.rb:551-552 plus `lunge_offset`), `facing` (the notch,
renderer.rb:595, 615-627; the lunge axis, :634), `attack_state`
(renderer.rb:576, 635-638, 642-643), `current_action` (renderer.rb:633), and
`faction` (renderer.rb:553-596 branches). The declared mapping
(`declared-integration-mapping-v1`, `tools/track_recompose.py`) needs:
`tween_left`/`tween_total` (the walk-frame index k = total − left),
`attack_state` + `state_frames` (the attack-timeline index), `facing`, and
`px`/`py` (the draw vector).

## Top-level shape

```json
{
  "schema_version": "draft-1",
  "class": "SYNTHETIC",
  "tick_ms": 16.666666,
  "zone": "zone_1",
  "view": { "origin_px": [0, 0], "width": 96, "height": 64 },
  "constants": { "step_frames": 13, "windup_frames": 5, "active_frames": 4,
                 "recovery_frames": 8, "windup_px": -3, "active_px": 6 },
  "creatures": [ { "name": "player_1", "faction": "pack", "kit": "striker" } ],
  "ticks": [ "... per-tick records, consecutive frames ..." ],
  "provenance": { "class": "SYNTHETIC", "producer": "...", "statement": "..." }
}
```

| field | type | source | notes |
|---|---|---|---|
| `schema_version` | string | **game-seat-owned** | `draft-1` until pinned at tool-spec time |
| `class` | `SYNTHETIC` \| `RUNTIME` | producer | `RUNTIME` only for tracks emitted by re-executing a verified bundle; everything this sprint produces is `SYNTHETIC` |
| `tick_ms` | number | `src/net/lockstep.rb:30` (16.67 ms tick law) | provenance; adjudication clips derive delays from the pinned 1/60 s |
| `zone` | string | world zone at capture | selects the pinned palette for recomposition |
| `view` | object | producer | the window recomposition composes into: `origin_px` in world pixels, integer `width`/`height` |
| `constants` | object | `data/balance/combat.json` `/kits/<kit>/...` + `manifests/render-reference.json` `lunge_offset` | denormalized so a track validates self-contained; the bundle's `game_commit` stays authoritative and intake cross-checks |
| `creatures` | list | roster at capture | `name`, `faction`, `kit` (creature.rb:13-14) |
| `ticks` | list | Mode T emitter | consecutive `frame` values; one record per declared creature per tick |
| `provenance` | object | producer | `class` must equal `track.class`; producing-tool identity (design section 5 provenance law) |

Bundle-level identity (`game_commit`, seed, seats, preconditions digest,
input-log sha256, end digest) lives in the bundle's `capture-manifest.json`
(design section 5), not here — a track never self-certifies.

## Per-tick record

```json
{
  "frame": 17,
  "creatures": {
    "player_1": {
      "tile_x": 1, "tile_y": 1,
      "px": 4.0, "py": 32.0,
      "facing": [1, 0],
      "tween_left": 11, "tween_total": 13,
      "attack_state": "idle", "current_action": null, "state_frames": 0,
      "hp": 80, "iframes": 0
    }
  },
  "masks": { "1": 0 }
}
```

| field | type | engine source (at `c5c146d0`) | consumed by |
|---|---|---|---|
| `frame` | int | `src/game/world.rb:77` (`@frame`), incremented once per executed tick (`:270` hitstop path, `:306` normal path) | adjudication windows; (f)'s cadence counter |
| `tile_x`, `tile_y` | int | `src/game/grid_walker.rb:13` — the committed logical tile (commits at step start, `:80-88`) | adjudication context — tile-binding reads ((i), (k)); grid rendering |
| `px`, `py` | number | `grid_walker.rb:13`; smoothstep ease `:90-97`; read by the renderer via creature.rb:60-61 at renderer.rb:551-552 | **renderer-draw** — the draw vector (mapping rounds with the banked `round_half_up`) |
| `facing` | `[int, int]` | creature.rb:13-14; set by `face` (:142-144); read live at every draw (renderer.rb:615-627, :634) | **both** — pose row selection and lunge axis |
| `tween_left`, `tween_total` | int | `grid_walker.rb:13` (v17 digest lane, `:11-12`); decremented in `tick` (:92) after `commit_dash` sets both to the step duration (:85-86) | **mapping-index** — walk frame k = total − left; commit tick (left == total) and completed step (left == 0) draw the standing pose |
| `attack_state` | enum `idle\|windup\|active\|recovery` | creature.rb:13-14, advanced in `advance_attack_state` (:478-498) | **both** — timeline phase; lunge selection (renderer.rb:635-638) |
| `current_action` | string \| null | creature.rb:13-14; read at renderer.rb:633 | **both** — action identity; specials suppress the lunge |
| `state_frames` | int | creature.rb `@state_frames` — set per phase (:463, :485, :493), decremented at :480; digest-visible as `action_frames` (:100) | **mapping-index** — phase index `into = pinned_phase_frames − state_frames` selects w0/a0/k0/s0/r0/x0 |
| `hp` | int | creature.rb:13 (`:26`, digest `:95`) | adjudication context |
| `iframes` | int | creature.rb `@iframes` (:37, :65, :130; digest :97) | adjudication context; bounds (f)'s flicker window |
| `masks` | object (seat → int) | the consumed per-tick input masks, byte-for-byte the values `fold_input` sees (`src/net/session.rb:510`; design section 4 field 4) | adjudication context — exact press ticks relative to tween phase |

**`state_frames` is the one field this consumer adds to the design's
section 4 Mode T list** — the finding a working parser surfaces:
`attack_state` alone says *windup* but not *which windup tick*, and the
banked timeline is positional (w0 is windup tick 1, a0 holds 2-5; s0/r0/x0
split recovery). The counter already exists engine-side (creature.rb:480)
and is already digest-read (:100), so the emitter pays nothing new. Without
it a consumer must count in-state ticks itself, which breaks on windowed
tracks that begin mid-phase.

## Validation and refusal classes

`tools/track_recompose.py` validates every field above with typed, loud
refusals (`missing-field`, `bad-type`, `bad-enum`, `out-of-range`,
`non-consecutive`, `roster-mismatch`, `state-mismatch`,
`provenance-mismatch`) and refuses at mapping time with
`unrenderable-facing` (no banked row exists outside down/right — mirrored
and diagonal rows are separate, unrequested asset decisions),
`unmapped-tween-class` (`tween_total != step_frames` while moving:
dash/knockback classes have no banked frame-selection evidence; the mapping
refuses rather than guesses), `unmapped-action-class` (specials have no
banked timeline, and the engine suppresses their lunge — renderer.rb:633 —
so the mapping refuses rather than guesses twice), and
`runtime-intake-not-established` (the reference consumer recomposes
SYNTHETIC tracks only until the intake gate of design section 5 is banked —
`RUNTIME` stays a schema proposal, so no synthetic artifact can ever be
processed as admitted runtime evidence).

The mapping is **per-tick pure** — no state is carried between records — so
spans where the engine freezes creature state while `frame` advances
(hitstop, `world.rb:265-270`) recompose correctly as repeated frames by
construction.

## Sufficiency vs the sixteen register items

Every `capture_requirements` entry in `docs/temporal-questions.json` maps to
track fields (or is named as a non-track artifact — nothing is papered
over). "Recomposition under the declared mapping" is the consumer itself,
version-pinned per artifact (mapping id + repo commit + module hashes;
design section 6.1 duty).

| item | capture needs (abbreviated) | carried by |
|---|---|---|
| (a) | full attack cycle to ready; attack_state, action, per-tick input masks | `attack_state` + `state_frames` + `current_action` (the r0 hold → x0 → ready sequence is positional in `state_frames`), `masks`, `frame` |
| (b) | (a)'s capture; window centered on the x0 tick; s0 comparison clip | same fields; the x0 tick is `attack_state = recovery, state_frames = 1`; s0 context recomposes from any tick with `recovery, state_frames = 8` |
| (c) | the 6-tick r0 held span ± 1 tick | `attack_state` + `state_frames` (r0 = recovery, `state_frames` 7..2) |
| (d) | w0 onset tick, w0/s0 one-tick bridges, the 4-tick a0 hold | `attack_state` + `state_frames` (w0 = windup 5; s0 = recovery 8; a0 = windup 4..1) |
| (e) | the k0→s0 boundary tick (−6 px return) ± 2 ticks | `attack_state` transition active→recovery; the −6 px is the mapping's lunge drop (+6 → 0), anchored by `px`/`py` |
| (f) | post-hit iframes window; the frame counter driving the 3-on/3-off cadence | `iframes` (the window) + `frame` (the candidate cadence counter); a hit-anchored cadence derives from `iframes` against the kit's pinned maximum, a world-anchored one from `frame` parity — **the anchor rule is part of the consumer extension the hub pins when it queues the item**; both candidate counters already ride the track. The accent-flicker treatment is not in mapping-v1 | 
| (g) | mid-walk onsets at EARLY/MID/LATE REM; tween_left/tween_total, attack_state, masks; onset cut windows | `tween_left`/`tween_total` + `attack_state` + `state_frames` + `masks` |
| (h) | release ticks (+13/+12 px); PLUS ≥120 fps physical-display capture | `px`/`py` per tick carry the displacements. The smear half is a display-chain artifact **no track can carry** (design section 4 carve-out, restated here) |
| (i) | MID last active tick, shallow arc crossing, tile grid visible | `attack_state`/`state_frames` (last active tick) + `tile_x`/`tile_y` + `px`/`py`; the grid is recomposition-side rendering |
| (j) | cross-facing turn+coil compound; turn and release tick windows | `facing` (the swap tick) + `attack_state`/`state_frames` mid-tween (`tween_left` > 0) |
| (k) | EARLY's 3 active ticks, migrating bind, tile grid | `attack_state`/`state_frames` + `tile_x`/`tile_y` + `px`/`py` |
| (l) | pure turn mid-walk at REM 8; compound cut tick ± 2 | `facing` + `tween_left`/`tween_total` (REM = `tween_left` at the turn tick) |
| (m) | pure turns at REM 11/8; full strafe segments | same as (l); strafe = `facing` ⊥ travel while `tween_left` > 0 |
| (n) | boundary corner turn (REM 0), window t13..t16; true-60 fps display | `facing` + `tween_left`/`tween_total` (the corner tick is the arrival tick: left hits 0 and the next commit lands the same tick); display standard is an adjudication-environment declaration (design section 6.5), not a field |
| (o) | settle-hold declared-model recomposition over cruise vs tail ticks | recomposition-side variant over the same fields; velocity regimes read from `px`/`py` deltas (no engine change — design's own carve-out) |
| x0 | no separate capture: consumes (a) | — |

Coverage: 16/16 items map to fields plus the two named non-track artifacts
((h) display capture; (n) display standard) and one named consumer
extension ((f) flicker treatment).

## What the reference consumer proves (machine-checked, this repo)

`tools/track_recompose.py --check`: state tracks derived mechanically from
the banked Model-A lane plans recompose **byte-identically** to the
committed calibration sheets (672/672 lane cells across
`reviews/calibration-v10/turn-sheet.png` and
`reviews/calibration-v11/corner-sheet.png`), and the mapping's decision
stream equals the banked v9 walk+attack `lane_tick` outputs (340/340
records). The schema is sufficient to drive the banked composition path —
demonstrated, not asserted.

## Non-claims

- **Draft.** The game seat pins the schema and owns `schema_version`;
  disagreements resolve in the game seat's favor at tool-spec time.
- **The emitter does not exist.** Mode T's emitter is proposed game-side
  conditional tooling (design section 2.3 gap 3); nothing here builds,
  schedules, or requests it.
- **No adjudication.** Consuming a SYNTHETIC track proves toolchain
  readiness only; zero lettered items are answered by anything in this
  repo until verified RUNTIME bundles exist and the owner sequences
  adjudication.
- **The mapping is a declared model** of a future integration — the game
  draws no sprites at the pin (design section 2.3 gap 2); every recomposed
  artifact carries the mapping version pin and, when synthetic, SYNTHETIC
  labels in filename, manifest, and pixels.
