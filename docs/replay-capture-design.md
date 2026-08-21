# Runtime-replay-capture measurement design (v12)

## 1. Status

**Design only.** This document specifies how a future game-two capture
effort could answer the fifteen banked runtime temporal questions
deterministically. It is **intake-gated**: nothing here is implemented,
scheduled, or requested for a named release. It **supersedes nothing** —
every banked verdict (v0–v11) stands unmodified, and the game-two lag-P0
lane owns its own tickets and pace. Sequencing belongs to the owner;
capture implementation, if queued, happens **in game-two by the game-two
seat**. This repo's part is the question register, the intake/adjudication
law, and the recomposition toolchain it already owns.

Pass bars fixed before content (v12 pre-registration): the register
validator (`tests/test_temporal_register.py`) was written before
`docs/temporal-questions.json` was filled and enforces the verbatim-quote
law in both pass and fail directions; the suite and both asset-gate runs
must be green; zero writes into `../game-two`; zero new pixels, exports,
or releases; every engine claim below cites file:line at the pinned
commit; every hub-state claim cites a commit SHA.

Pin for every engine citation in this document: game-two
`df38cb71226f119516341ceffe848faaaf01af64` (the v12 step-0 re-pin; all
five pinned sources plus `combat.json` blob-identical across the
`b6724ec3` → `df38cb71` hop). A second hop landed mid-sprint
(`df38cb71` → `5ce4414f`): one pinned file changed — `src/app/renderer.rb`,
additive-only (+34/−0, the R-A2 BUY-hint text lane; no draw-path constant
touched), re-pinned at banking under the dev-seat standing protocol with
every `render-reference.json` constant value-re-verified at the new blob
and `attack_timing` 5/4/8/13 re-verified. File:line citations below are
exact at the named pin `df38cb71`.

## 2. Engine substrate at the pin (what exists today)

### 2.1 Deterministic spine — established by engine law, not assumed

- **Tick-locked timebase.** `update()` = exactly one sim tick; under load
  the game slows rather than skipping — "replays are deterministic by
  tick count" is the stated law (`src/app/window.rb:25-28`). The tick
  duration constant is 16.67 ms (`src/net/lockstep.rb:30`).
- **Input seam.** Game code never reads the keyboard directly; it asks an
  input source about abstract actions — "the seam that makes
  deterministic replay possible" (`src/core/input.rb:1-6`). Live play
  feeds `KeyboardInput`; replays feed `ScriptedInput`
  (`src/core/input.rb:39-55`); an absent seat reads `NullInput`
  (`src/core/input.rb:31-34`).
- **Seeded, split, counted RNG.** `World#initialize(data, seed:, seats:,
  save:)` (`src/game/world.rb:45`) builds `@rng =
  Core::CountingRng.new(Random.new(seed))` (`:64`) and a salted respawn
  stream (`:71`). Draw counts enter the digest
  (`src/core/counting_rng.rb`, `src/game/world.rb:642`).
- **Seat-ordered resolution.** `World#tick(input)` normalizes to a
  `{seat => input}` hash (`src/game/world.rb:263-264`); `tick_world`
  iterates seats in pinned order (`:674, :678, :682, :693`). Netplay
  enforces the same seat-order and sampling laws mechanically
  (`src/net/lockstep.rb:9-17, :102-118`).
- **State digests.** `Net::StateDigest` folds every registered bus event,
  the per-tick consumed input masks (`fold_input`,
  `src/net/state_digest.rb:36-38`, called at
  `src/net/session.rb:510`), and the canonical scalar snapshot
  (`World#digest_snapshot`, `src/game/world.rb:633-645`) into one md5 per
  window, versioned by `DIGEST_VERSION` and exchanged at the handshake
  (`src/net/state_digest.rb:17-27`). Sessions retain a `[tick, md5]`
  digest log (`src/net/session.rb:513`).
- **Saves are canonical facts.** Pinned canonicalizer, scalar leaves only,
  floats unrepresentable, md5 over canonical bytes
  (`src/game/save_state.rb:4-34, :118`).
- **Float/order discipline.** Coop scaling is explicit `.round` Integers —
  "no Float ever enters" the seat-scaled balance path
  (`src/game/world.rb:61-63`); AI claim/pressure orders are pinned to
  roster order and documented deterministic (`src/game/world.rb:323,
  :337`).
- **Live cross-machine proof.** The v18 ritual sessions ran two machines
  in lockstep for 36,079 ticks with `desyncs=0`, save digests chaining
  `3a518bcc` (s9) → `b5cae357` (s10) on both seats (game-two commits
  `c415be8`, `aba02af`, `4a98474`).

### 2.2 Record/replay machinery that exists today

- **A deterministic replay + capture harness.** "Rule 2 harness:
  deterministic input replay + frame capture"
  (`harness/replay_runner.rb:1`). A script JSON carries scenario, seed,
  held/per-frame actions, capture frames, and run length (`:5-15`);
  captures happen inside `update()` right after the sim tick via
  `Gosu.render` (`:18-19, :70-83`); `VIDEO_EVERY=1` dumps every rendered
  frame (`:52-58`). `WorldScene` drives the **real** `Game::World` and
  the **real** renderer under scripted input — "No mocks — what the
  harness captures is what the player sees"
  (`harness/scenes/world_scene.rb:10-11, :22`). Captures pin locale and
  bindings to canonical for cross-machine comparability (`:24-30`), and
  the wall gates byte-compare captures against committed baselines
  (game-two `a49a2d3`, lag-spec determinism section).
- **Seeds are already surfaced.** Solo play generates a per-session seed
  and prints it: `TELEMETRY session seed=…` (`src/main.rb:94-95`).
  Netplay seeds come from the host handshake (`src/main.rb:143`,
  `src/app/window.rb:117`).
- **Netplay retains both seats' consumed inputs in memory.** "Consumed
  slots stay in the queue so late duplicates are still checkable"
  (`src/net/lockstep.rb:117-119`) — a full per-tick per-seat mask history
  exists at close, today, at zero added per-tick cost.

### 2.3 The three gaps (the pre-registered pivot, executed)

The brief's pivot condition ("if no replay primitive exists, propose the
minimal contract") lands **narrower** than feared — the primitive exists
for scripted input. What does **not** exist:

1. **No live-session input recorder.** Consumed masks are folded into
   digests transiently and retained in memory, but nothing persists an
   input log at close. Live-session replay is therefore not yet possible;
   scripted-session replay is. Every requirement below that depends on
   live traces is marked **CONDITIONAL** on the hub accepting the
   recorder contract (§4).
2. **No sprite draw path.** The renderer draws creatures as solid quads
   plus a facing notch (`src/app/renderer.rb:478-527`; notch called at
   `:524`, defined `:544-557`; `lunge_offset` `:560-569`). The banked
   sprite frames are not loaded anywhere in the game. **A framebuffer
   capture of the current game cannot show the frames the fifteen
   questions are about.** The bridge is repo-side recomposition (§6), not
   a game-side sprite integration — which remains a separate, unproposed
   owner decision.
3. **No state-track emitter.** Nothing in the engine or harness exports
   per-tick semantic state today — `StateDigest` folds to one md5 per
   window, the harness captures pixels. Mode T's emitter (§4) is **new,
   proposed game-side tooling**, part of the capture tool itself;
   everything downstream of it is conditional exactly like the recorder
   (council finding Q3, adopted).

Remaining determinism audit items for the game seat (named, not asserted):
(1) same-machine bundle re-execution identity — digest chains equal across
two offline re-executions; (2) cross-machine framebuffer byte-identity
scope for `Gosu.render` readback (state tracks and digests are the
identity anchor if GL rasterization differs); (3) confirmation that no
wall-clock read reaches sim state (none found in the `World#tick` path at
this pin; `Gosu.milliseconds` appears in the app layer only,
`src/app/window.rb:92`).

## 3. The temporal-question register (prose; the JSON is the contract)

`docs/temporal-questions.json` is the machine-readable register: fifteen
lettered questions (a)–(o) plus the x0 banking-reversal head, each with
its origin sprint, source file, **verbatim** pre-registered condition,
status, capture requirements, adjudication artifact, and routing.
`tests/test_temporal_register.py` enforces that every quote is a
whitespace-normalized byte-substring of its named source file — **prose
may paraphrase; the JSON may not.**

Two-quote design: each of (a)–(f) carries the origin sprint's
full-precision wording as the adjudication bar (v7 for a–c and x0, v6
for d–e underlying, v4 for f) **plus** the v9 consolidated letter-binding
quote; (g)–(o) originate where they are lettered (v8, v9, v10, v11). A
validator-checked `carry_chain` proves the letters ride unmodified
through v10 and v11. Origin map:

| ids | origin | coined in |
|---|---|---|
| a, b, c, x0 | v7 | the x0 in-between banking; x0 reversal head |
| d, e | v6 (lettered v7) | w0/s0 bridges, a0 hold; k0→s0 recoil |
| f | v4 (lettered v7) | ACC flash-accent under live flicker |
| g, h, i | v8 | mid-walk onset seams |
| j, k | v9 | cross-facing onset compound; migrating bind |
| l, m | v10 | turn compound fusion; moonwalk severity |
| n, o | v11 | single-tick facing exposure; dead-drag gradient |

Status split (validator-enforced semantics): **fusion-question** (13
items — does tick-level structure fuse/read correctly at 60 tps;
unanswerable on a static sheet by construction), **severity-only** (m, o —
the static condition is a banked FAIL; runtime measures at-speed severity
and can never soften the banked red), **banking-reversal-head** (x0 — if
(a) fails at runtime, the pre-registered disposition is to reverse the x0
banking; timeline A is byte-recoverable). A second, non-mandatory section
carries the recorded-not-measured classes (step-initiation turn,
multi-turn chatter, 8-direction, live notch-strafe, diagonal facing) with
the same schema.

## 4. Capture-bundle contract (proposal)

A **replay bundle** is the atom of runtime evidence. Proposed minimal
contract — everything a deterministic re-execution needs and nothing
more:

1. `game_commit` — full SHA the session ran at (re-execution must run the
   identical commit; the netplay handshake-law precedent).
2. `seed` — the world seed (solo: the printed session seed; netplay: the
   handshake seed).
3. Preconditions — seats count, start zone, and either `fresh` or the
   canonical save-facts bytes + md5 (`src/game/save_state.rb` vocabulary).
4. Per-tick per-seat input log — the consumed masks for every executed
   tick, seat-ordered; byte-for-byte the values `fold_input` sees
   (`src/net/session.rb:510`).
5. Expected end-state digest — the final `StateDigest` window md5 with
   its tick, cadence, and `DIGEST_VERSION`; optionally the full
   `[tick, md5]` chain for windowed verification.
6. Bundle manifest — sha256 of every member plus producing-tool identity.

Fields 3 and 6 extend the four-field minimum (commit + seed + input log +
end digest) deliberately: without the save-facts precondition a
non-fresh world re-executes differently, and without member hashes the
bundle cannot be intake-verified (§5).

Producer paths, cheapest first:

- **P1 — scripted (exists today).** A harness script already is a
  hand-authored bundle (seed + per-frame actions). Missing only the
  end-digest emission to close the verification loop. All fifteen
  lettered questions are answerable from P1 bundles — they are
  controlled-stimulus questions (exact press ticks relative to tween
  phase), which scripted input expresses more precisely than a hand —
  with one carve-out: item (h)'s sample-hold half additionally needs the
  physical-display capture step of §6.2, which no bundle can carry.
- **P2 — netplay dump-at-close (proposed).** Serialize the
  already-retained consumed-mask queues at `conclude`
  (`src/net/lockstep.rb:117-119`, `src/net/session.rb:531`). The
  retention itself is the engine's existing behavior ("the consumed
  queue retains ~74k slots by design" — game-two `a49a2d3`, lag-spec
  killed-metrics note), so P2 adds zero per-tick work and zero memory on
  either seat; the one close-time file write is routed **host-side
  (strong seat) only** — the host retains both seats' masks, so the weak
  seat writes nothing, ever (council finding Q2, adopted).
- **P3 — solo recorder (proposed, env-gated, default OFF).** Append the
  consumed mask per tick, following the `GAME_FRAME_PROBE` precedent
  exactly (off = no allocation, no branch — game-two `dacf946`).
  Ecological-validity gravy only; never default-on; the weak seat never
  sets it (procedural law, same class as "the wall never sets it").

**Weak-seat law (hard constraint, from S0-J2 — game-two `87cbf01`: 59 Hz
display, Intel HD 3000 (2011), i3-2310M, 5.9 GB RAM):** capture adds zero
overhead to the weak seat during live play. All capture runs **offline,
from a bundle, on the strong machine**. P2's cost model (nothing per
tick, one write at close) is the only live-loop touch this design ever
proposes, and it is optional and hub-owned.

Offline capture modes (strong seat, from a bundle, never live):

- **Mode T — state track (primary).** Re-execute the bundle headless;
  emit per tick, per creature: name, faction, kit, `tile_x/tile_y`,
  `px/py`, facing, `tween_left/tween_total` (public, digest-read state —
  `src/game/grid_walker.rb:11-13`), `attack_state`, `current_action`,
  hp, iframes; plus world frame, zone, and the consumed masks. Sufficiency
  criterion: the track must carry every input the renderer's creature
  draw reads plus every index the declared pose-selection mapping needs.
  Exact field list is pinned by the game seat when the tool is specced
  (open question 1). A DRAFT field list with a working reference consumer
  is banked as proposal input: `docs/state-track-schema.md` (v13).
- **Mode F — framebuffer.** Per-tick PNG of the current quad+notch draw
  via the existing capture path. Evidence about the **current** game only
  (e.g. the live notch-strafe class); never evidence about banked frames.

## 5. Evidence intake into this repo

Mirrors the release-manifest discipline in reverse (this repo consumes
pinned evidence; game-two never depends on this repo):

- Location: `evidence/replay/<bundle-id>/` (new top-level; `exports/`
  stays release-only). Large binaries ride LFS from day one.
- `capture-manifest.json` per bundle: game commit, seed, seats,
  preconditions digest, input-log sha256, end-state digest + cadence +
  `DIGEST_VERSION`, state-track sha256(s), capture-tool identity (repo +
  commit + invocation line), producing machine class, date, and the
  sha256 of every file in the bundle. Byte-pinned upstream text artifacts
  are routed `-text` in `.gitattributes` (standing law: the repo's
  `* text=auto eol=lf` default would silently rewrite CRLF bytes and
  break the pin).
- Intake gate: a bundle is admissible only if manifest hashes verify and
  the end-state digest matches a local re-verification by the game seat
  (recorded in the manifest as the producer's attestation; this repo does
  not run game code).
- Provenance: capture tooling identity is recorded like generation
  provenance in the release law — no anonymous artifacts.

## 6. Adjudication procedure

1. **Recomposition (this repo's toolchain).** Map the state track onto
   banked frame bytes under the **declared integration mapping** — the
   banked walk mapping (f0×4/f1×3/f2×3/f3×3 across the 13-tick step), the
   banked attack timeline, and the same composition/APNG encoders the
   v9–v11 lanes used (byte-determinism discipline carries: in-process
   double build + CLI re-run `cmp`). The mapping is a **declared model**
   of a future integration — the game draws no sprites today (§2.3) —
   and every artifact discloses that (EXP-class discipline, carried
   v4/v11). Captured state is real; frame selection is the proposal's.
   The mapping is **version-pinned in every artifact** — mapping id plus
   this repo's commit — so a future mapping revision can never silently
   re-ground an old verdict (council finding Q7.1, adopted).
2. **Artifacts.** Exact 1/60 s-per-tick APNG at native scale plus integer
   zoom copies, and a per-tick contact sheet of the same window. For item
   (h)'s sample-hold half: additionally a high-frame-rate (≥120 fps)
   capture of a physical display playing the clip at native 1x — a
   display-chain artifact that recomposition cannot produce.
3. **Bars.** Each adjudication sprint pre-registers its rubric before
   artifacts exist (the rationale.md discipline, unchanged), and the bars
   for the lettered items are the register's `verbatim_condition` fields —
   not paraphrases of them.
4. **The sheet-vs-severity split law, restated.** Statically-present
   conditions were adjudicated at sheet scope in their sprints (v10
   adjudication law; v11's visible-fact extension). The runtime items are
   the **severity/fusion halves only**: a runtime read can refine severity
   or answer fusion; it can never soften a banked red or re-open a banked
   PASS. Re-adjudicating banked verdicts is out of scope by construction.
5. **Adjudication environment.** The playback display is declared in
   every verdict (hardware, refresh rate). Item (n)'s one-tick exposure
   and every fusion bar require true 60 fps playback — a 59 Hz seat
   cannot adjudicate them (S0-J2). The strong seat's 165 Hz primary
   (game-two `a49a2d3`, F4 machine facts) satisfies this.
6. **Verdict discipline.** Accuracy and presentation scored separately;
   cross-vendor council pass on the verdict; verdicts banked in
   `reviews/` like every calibration sprint.

## 7. Shared substrate with the lag-P0 lane (and hard separations)

Both lanes stand on the same deterministic spine — tick-locked update,
seeded RNG, digests, the harness. They answer different questions in
different domains:

| | lag-P0 (hub, in flight) | replay capture (this design) |
|---|---|---|
| domain | wall-clock, **live** play | tick-domain, **offline** re-execution |
| question | who/what eats frames (T1a/T1b shipped: game-two `7629052`, `dacf946`; T2 probes owner-paced) | what the ticks look like drawn with banked frames |
| live-loop cost | log-only lines, always-on/env-gated | zero (P2's close-time dump, host-side only, is the only optional touch) |
| invalidated by | offline re-execution (timing is the re-executing machine's) | nothing the lag lane changes at tick level |

The one genuinely shared mechanism candidate is the **replay bundle**.
Offered to the lag lane, theirs to take or leave: (i) a bundle makes any
future desync reproducible offline (the digest artifact already retains
snapshot + window lines; adding inputs closes the loop); (ii) T4
before/after comparability — re-executing one recorded co-op session on
both builds measures a fix on identical work (`GAME_FRAME_PROBE` over a
replay); (iii) P2 costs nothing per tick. This design invents **no new
digest form** (bundle verification reuses `StateDigest` as-is,
`DIGEST_VERSION` pinned) and duplicates **no telemetry**: T1a's close
line carries aggregate wall-clock counters only (ticks, desyncs, stalls,
stall_ms_max, d, link_slow, run_ms, the worst-run pair —
`src/net/session.rb:164-174`), so no per-tick data crosses between the
lanes in either direction.

Separations, stated plainly: this document proposes no ticket, no
ordering, and no v19 slot; the owner sequences (lag instrumentation was
named the first v19 brainstorm input — game-two `2b566a0`); v18 is closed
and v19 is not opened (`2b566a0`); recording is never default-on; the
weak seat's live loop is untouched under every option; and if the owner
queues capture work, it is implemented in game-two by the game-two seat.

## 8. The gating-decision ask (carried to the hub with this design)

v11 left one decision pending upstream, and the settle-bob calibration
named in v11's next-hypothesis is **closed-by-condition** on it (opens
only if gating-class solutions are rejected). Evidence summary, from
banked verdicts only:

- Turn cuts are clean at every measured REM; the **strafe segment** is
  the failing surface (v10 headline).
- Frame-selection remedies are measured dead: the settle-hold rendered
  0/4 (v11) — it removes the moonwalk and installs a statue-slide
  (dead-drag), and its substitution is a no-op exactly where the walk
  already passes (the deceleration tail). It cannot rescue REM ≥ 8.
- The boundary turn is clean at REM 0 (v11 CORNER, 2/2) **and** at one
  tick late (CONTROL, banked clean) — the class tolerates ±1 tick of
  input timing, so boundary buffering does not demand tick-perfect input.
- Facing-lock during the tween is the structural alternative (~217 ms
  worst-case turn latency, specified in v9).
- A buffered-turn implementation owes a diagonal-input rule: pick an
  axis or queue the second press (`held_direction` can return `[1,1]`;
  the notch has a diagonal branch, `src/app/renderer.rb:554-555`; a
  diagonal step tweens 18 frames; no diagonal sprite row exists).

The three options and their consequences:

1. **Adopt gating-class turn handling** (REM-gating / boundary buffering —
   the banked primary recommendation; and/or facing-lock). Consequence:
   the settle-bob stays closed **forever**; zero pixels owed from this
   repo; the engine chooses the turn-apply tick and the corner lane is
   its rendered target state.
2. **Reject gating-class.** Consequence: the settle-bob calibration
   sprint becomes eligible — the minimal add-motion test (two
   weight-shift frames at native resolution, held under perpendicular
   travel, judged against v11's R2 line with the same lanes and band).
   Frame selection **without** added motion stays measured-dead.
3. **Frame-selection rework with a dedicated side-step/strafe pair.**
   Consequence: new pixels on this repo's plate — a named asset decision
   requiring its own owner-approved sprint; nothing banked asks for it.

**The ask:** which class does the hub adopt for the integration design?
The answer resolves the settle-bob condition automatically. No deadline
attaches; the decision belongs to the hub and the owner. Deferral is
harmless and needs no option of its own: an unanswered ask leaves the
settle-bob condition pending and this design unaffected (council finding
Q6, adopted as an explicit consequence). Recorded 2026-08-20 (hub receipt,
v12 mail thread): gating-decision DEFERRED to the v19 owners' brainstorm as
a sim-feel class decision — the settle-bob condition stays pending exactly
as this paragraph provides.

## 9. Non-goals and open questions

**Non-goals (this sprint and this document):** no capture execution; no
engine patches, PRs, or code destined for game-two; no sprite-integration
proposal (a separate owner decision); no re-adjudication of banked
verdicts; no schedule or priority claim relative to lag-P0; no
8-direction or diagonal asset proposals beyond restating banked findings;
no audio, no tile era; no default-on recording anywhere; no new pixels of
any kind.

**Open questions (owner/hub-paced):**

1. State-track field list — pinned by the game seat at tool-spec time
   against §4's sufficiency criterion.
2. Cross-machine framebuffer byte-identity scope for `Gosu.render`
   readback (state tracks and digests anchor identity if GL differs).
3. Round-1 producer choice: scripted-only (P1) vs adding the P2
   dump-at-close.
4. The adjudication display standard (who owns the declared 60-fps-true
   playback environment).
5. Storage: `evidence/` LFS budget for per-tick PNG sets and APNGs.
6. Harness surface: a dedicated track-emitting scene vs a flag on
   `WorldScene`.
7. Whether any question later re-runs at measured live rates (the ~53.5
   tps co-op pacing the lag lane corrected — game-two `a49a2d3`) after a
   lag fix lands; parked until the hub decides.

## 10. Adversarial-review record (appendix)

One consolidated cross-vendor pass (Kimi K2.5, `moonshotai.kimi-k2.5`,
adversarial brief per the council-consult skill; 1,881 tokens in / 2,227
out = 4,108 of the 8k cap, `stop_reason=end_turn`, no truncation;
response file-redirected and read as UTF-8). Seven numbered questions:
lag-P0 overlap, weak-seat feasibility, substrate soundness, register
fidelity, contract sufficiency, gating-ask framing, unthought risk. Every
verdict re-verified against primary evidence before adoption (v5–v11
precedent); the reconciliation:

1. **Q1 (lag overlap) — council REFUTED the separation; re-verification
   REFUTED the refutation, kernel adopted.** The charge — T1a is shipped
   and "could include tick-correlated data (unspecified scope)" —
   dissolved on reading the primary: `telemetry_line` carries aggregate
   wall-clock counters only (`src/net/session.rb:164-174`), and the
   design never claimed T1a was unscheduled — it claims *this design*
   schedules nothing. Adopted: §7 now cites T1a's exact payload instead
   of asserting non-duplication. (An instance of the standing precedent:
   under adversarial framing, reviewers assert unverified precision — the
   "unspecified scope" was specified all along.)
2. **Q2 (weak seat) — feasibility CONFIRMED; the zero-overhead attack
   half-adopted.** Real kernel: P2's close-time write is I/O on whichever
   seat writes. Adopted: §4 routes the dump **host-side (strong seat)
   only**; the weak seat writes nothing. The "unbounded memory pressure"
   half was REFUTED by primary evidence: consumed-slot retention is the
   engine's existing behavior (`src/net/lockstep.rb:117-119`; "retains
   ~74k slots by design", game-two `a49a2d3`), pre-dates this design, and
   ran live on the weak machine for 36,079 ticks in the ritual sessions —
   P2 adds no retention. P3's "default-off is not impossible-to-enable":
   adopted as wording (the `GAME_FRAME_PROBE` precedent named, procedural
   law explicit); compile-time exclusion rejected as beyond the hub's own
   accepted env-gate pattern.
3. **Q3 (substrate) — CONFIRMED: a third gap existed.** The state-track
   emitter is new proposed tooling, and the draft had described it in §4
   without naming it a gap. Adopted: §2.3 gap 3, with everything
   downstream of Mode T marked conditional exactly like the recorder.
4. **Q4 (register fidelity) — UNCERTAIN on (n)'s classification;
   resolved against the register's own semantics, no change.**
   `fusion-question` is defined as a perceptual-integration question
   unanswerable on a static sheet; `severity-only` requires a banked
   static FAIL to grade. (n) sits behind a banked PASS group (v11
   B-group) and asks fuse-vs-flicker — there is no red to grade severity
   against, so fusion is the correct class. (m)/(o) confirmed as
   severity-only. The council could not see the full register (prompt
   budget); the validator, not the council, is the fidelity mechanism —
   its spot-checks of (n)/(o)/x0 wording against the pasted v11/v7 lines
   raised no drift.
5. **Q5 (sufficiency) — CONFIRMED for the (h) carve-out, already routed;
   made explicit.** The smear half needs a physical-display capture no
   bundle can carry; §4 P1 now names the carve-out instead of implying
   it. The "preconditions drift" charge was an artifact of the prompt's
   one-line contract summary; the doc now states explicitly that fields 3
   and 6 extend the four-field minimum and why.
6. **Q6 (gating ask) — "not exhaustive" ADOPTED; the rest REFUTED.**
   Adopted: §8 now records that deferral is harmless and leaves the
   settle-bob condition pending. Refuted: consequence-framing from banked
   verdicts is required, not smuggled — Rule 6 forbids presenting banked
   reds neutrally; and "specify a hub deadline and a default" would have
   this repo imposing decisions on the hub, which hub-and-spoke
   sovereignty forbids — the ask defers by design.
7. **Q7 (unthought risk) — one adopted, three refuted, one out of
   scope.** Adopted: the declared mapping must be version-pinned in every
   artifact (§6.1) so a mapping revision can never silently re-ground an
   old verdict. Refuted: MD5-collision/losslessness — the digest verifies
   re-execution identity, not perception, collision is outside the
   cooperative threat model, and the recomposition chain's
   byte-determinism is the banked toolchain discipline; P2 OOM — see
   Q2 (retention pre-existing, masks are small integers); adjudication
   procedure undefined — §6.3/6.6 carry the banked rationale.md
   pre-registration and split-scoring discipline. Out of scope: x0's
   "byte-recoverable" is v7's banked verdict clause quoted verbatim, not
   a claim this design introduces or must re-prove.

Net: three design changes (§2.3 gap 3; §4 P2 host-side routing + P3
enforcement wording; §8 deferral consequence), two claims strengthened
from assertion to citation (§7 T1a payload; §4 P1 carve-out +
field-extension note), one new duty (§6.1 mapping version-pinning). No
council claim that survived re-verification contradicts the design's
decisions; no banked verdict was touched.

