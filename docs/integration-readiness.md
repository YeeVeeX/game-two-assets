# Integration readiness — pipeline-maturity status register

**Current answer: NOT integration-ready — C6 (integration design) is
OPEN; C1, C2, C3, C4 and C5 are MET.** This
register is a mechanical STATUS record: advisory input to
the hub's parking-lot gate ("assets integration — gated on
game-two-assets pipeline maturity"); the hub decides, and nothing here
asks for, sequences, or designs anything. Every row is a status plus a
carrier citation; statuses change only when a new carrier lands, by a
future sprint's commit against this file's shape tests
(`tests/test_exports_guard.py`). Status vocabulary: `MET` /
`MET-AT-CHECKPOINT` / `OPEN` (`BANKED` for the affordance row). Mail
carriers live under `~/.pi/agent/mail/game-two-assets/` and are cited by
their `done/` filename. Pre-registration:
`reviews/readiness-v17/rationale.md` (row skeleton and this law, fixed
before this file existed).

| Condition (docs/asset-contract.md) | Status |
|---|---|
| C1 fun verdict closed | MET |
| C2 one lane wins, not least bad | MET |
| C3 asset gate clean | MET |
| C4 provenance and rights | MET |
| C5 native-scale critique | MET |
| C6 integration design | OPEN |

## Upstream rulings on record (quoted verbatim from their carriers)

- **Boundary + gate** (`done/from-game-two-family-block-sync-20260822.md`):
  "v17 and v18 are both CLOSED. The standing gate is game-two's
  parking-lot entry ('assets integration — gated on game-two-assets
  pipeline maturity')." Applied to `AGENTS.md` at `51851f4`.
- **Gating-decision** (`done/from-game-two-v19-brainstorm-receipts.md`):
  "gating-decision = deferred" — owner verbatim "I agree with you,
  defer, maybe revisit later if needed"; "settle-bob condition stays
  pending, zero pixels owed, nothing else moves."
- **Capture-contract** (same carrier): "capture-contract =
  queued-for-v19-intake" — owner-ratified E3(a), verbatim "yes
  please!"; "Sequenced AFTER the four v19 lanes' first ships"; "Your
  open question 1 (state-track field list) gets pinned by this seat at
  tool-spec time"; "Next mail from us = capture-contract tool spec when
  its slot arrives."
- **Role reassignment** (`docs/owner-redirects.md`, 2026-08-21): the
  creature set's integration role is un-pinned (pet/world-fauna named
  as candidate roles); "No asset action until the game pins its new
  frame."

## The six runtime-integration stop conditions (docs/asset-contract.md)

### C1 — game-two v17 fun verdict is closed

**Status:** MET. Closed upstream, recorded 2026-08-22; the standing
blocker moved from this condition to the hub's parking-lot gate (see the
boundary ruling above).
**Carrier:** `done/from-game-two-family-block-sync-20260822.md` ("v17
and v18 are both CLOSED") + the `AGENTS.md` boundary wording (`51851f4`).

### C2 — one sprint-0 visual lane wins rather than merely being least bad

**Status:** MET. "Lane B (`player_1_lane_b_*`) wins calibration v0 — a
genuine improvement, not least-bad"; "Winner status per contract:
selectable candidate only." The lane's k0 defect arc is closed: K-S
selected under the v15 pre-registered rule, owner-ratified ("Approved,
proceed"), adoption-proven in the sighting artifact class at v16.
**Carrier:** `reviews/calibration-v0/verdict.md` +
`reviews/remedy-v15/verdict.md` + `reviews/adoption-v16/verdict.md` +
`docs/selection-register.md`.

### C3 — asset gate passes from a clean checkout

**Status:** MET. Proven in both directions on a from-scratch local
clone of this repo's committed HEAD (`tools/checkout_gate.py`, v18):
the clone's own gate run exits 0, and the negative control — a
tampered `sha256_lf` in the CLONE's baseline — exits nonzero naming
the violation. The contract wording names no checkout variant; this
row records the variant proven — a from-scratch clone of committed
HEAD — and a hermetic reading is structurally impossible for this
gate, which contracts against live externals by design. Externals
named, not hidden: the live sibling game-two checkout (read-only), the
pinned Aseprite binary, an invoking Python interpreter; LFS bytes come
from the local origin's object store (zero network in the primary run;
the fresh-venv secondary also passed). Working-tree gate runs stay the
per-sprint checkpoint (exit 0 at this sprint's step-0 and pre-banking
runs); the clean-checkout variant is re-provable on demand by the tool
against the then-current pin.
**Carrier:** `reviews/maturity-v18/checkout-report.json` (both
directions, externals, exit codes) + `tools/checkout_gate.py` +
`reviews/maturity-v18/verdict.md`.

### C4 — provenance and rights are complete

**Status:** MET for every banked release. Nine `release.json` manifests
(seven calibration releases, the remedy release, the audio release) each
carry source commits, per-file SHA-256 pins, and provenance
(reconstruction notes; the audio release carries the conversion twin-hash
law); the asset gate validates them on every run, and both v17 runs exit
0. A future release re-proves this at its own gate.
**Carrier:** `exports/*/release.json` (all nine) + the gate runs in
`reviews/readiness-v17/verdict.md`.

### C5 — visual critique passes at native scale

**Status:** MET for the banked set, at the pinned protocol. The
calibration-v0 winner passed the native-scale rubric; the v15 selection
passed native 1x rubric lines at the pinned protocol; the v16 adoption
proof passed perceptual lines 1–3 in the sighting demo context. Scope
limit carried, not hidden: at-speed and runtime-viewport reads are
unmeasured (watch items below; the capture instrument is C6's third
gate).
**Carrier:** `reviews/calibration-v0/verdict.md` +
`reviews/remedy-v15/verdict.md` + `reviews/adoption-v16/verdict.md`.

### C6 — an integration design proves loading, draw order, and deterministic capture without changing simulation identity

**Status:** OPEN — gated by two pending decisions, with its capture
prong additionally queued upstream. No integration design exists, by law
(this repo's one-way
boundary; design content is out of this register's scope). What it
waits on, named from carriers: decision gate (i) the owner's role re-pin
("No asset
action until the game pins its new frame"); decision gate (ii) the hub's
parking-lot
gate ("assets integration — gated on game-two-assets pipeline
maturity"); queued upstream dependency, not a decision gate, (iii) the
deterministic-capture instrument
("capture-contract = queued-for-v19-intake", "Sequenced AFTER the four
v19 lanes' first ships"; the state-track field list "gets pinned by
this seat at tool-spec time"; the tool spec travels by mail).
**Carrier:** `docs/owner-redirects.md` (2026-08-21) +
`done/from-game-two-family-block-sync-20260822.md` +
`done/from-game-two-v19-brainstorm-receipts.md`.

### k0-of-record mechanical affordance (recorded; not a stop condition)

**Status:** BANKED. Future compositions in this repo draw the selected
K-S bytes for the k0 slot through the pinned staging seam:
`tools/adoption_demo.py` `stage_ks_attack_dir()` (release-pinned SHA
verification at staging; refuses divergent bytes) + `demo_dirs()` (the
dirs-level substitution seam). The module is hash-pinned by the v16
manifest; the consequence clause and its one-line reversal live in the
selection register. Class, stated to prevent misreading: this is a
review-composition affordance inside this repo (SYNTHETIC artifact class
over banked bytes); it is not loading, not draw order, and not runtime
capture — C6 is untouched by it.
**Carrier:** `docs/selection-register.md` (2026-08-21 entry) +
`reviews/adoption-v16/adoption-manifest.json` (pin) +
`tools/adoption_demo.py`.

## Watch items (carried verbatim; carriers named inline)

- **Shade double-duty** — "`#8c3818` now serves flank shading and the
  mouth marker; a future pose family leaning harder on shade shrinks
  the mouth's distinctness budget (watch item for v16+ authoring)"
  (`reviews/remedy-v15/verdict.md`, council Q5).
- **Protocol-vs-player-viewport gap** — "this selection is proven at
  the pinned adjudication standard, not in a runtime viewport; the
  banked capture design remains the instrument for the shipped read"
  (`reviews/remedy-v15/verdict.md`, council Q5).
- **At-speed K-S band read** — "the at-speed read of the selected band
  (does the shade mouth read correctly at 60 tps?) remains unmeasured"
  (`reviews/adoption-v16/verdict.md`); it rides the queued capture
  instrument (C6 carrier).
- **DEF-3 packaging** — every owner-handed demo artifact carries the
  pinned protocol line; resampled viewing "amplifies percepts, it does
  not create bytes" (`reviews/adoption-v16/verdict.md`, DEF-3 note).

## Non-claims

No timetable and no sequencing content — what each open item waits on
is named from its carrier, nothing more. No design content: loading,
draw order, and capture design are exactly the gated next things and
live behind C6's three gates. No integration ask: this register is
input to the hub's gate; the hub decides. No re-opening of banked
verdicts: the v15 selection and the v16 adoption stand as banked;
statuses here restate their carriers. No recommendation weight: OPEN
rows do not age into asks, and no count of MET rows constitutes one.
Mechanical ids only (repo
invariant 5). A status row here never moves a pixel, a pin, or a byte
under `exports/`.
