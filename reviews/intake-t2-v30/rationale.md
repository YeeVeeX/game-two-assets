# E3a-T2 RUNTIME intake + v1 consumer adaptation — rationale (v30, PRE-REGISTERED)

**Status: rubric FIXED BEFORE the parser work.** This file is committed with
every verdict cell NULL, alongside the intake evidence (commit A). The
adaptation (commit B) and the judged copy + `verdict.md` (commit C) land
after — the commit-A/commit-B discipline every calibration sprint used. No
cell may be filled before its evidence exists.

## Review objects and identity

- The delivery: s84 mail `from-game-two-e3a-t2-track-delivery.md`, md5
  `98fb30332c8a84023eb0251de7f5757b` (6,713 B, pure LF), verified at v30
  step 0. Its schema section (v1 = spec section 5 at game-two `2627ed0`) is
  the PIN; the mail restates it with the draft-1 deltas.
- The evidence: bundle `20260826T175326Z_p1_42` members intaken at commit A
  under `evidence/replay/20260826T175326Z_p1_42/` — mailed-vs-computed
  table, verification receipt, and the attestation trust split recorded in
  `intake-record.md` (same commit).
- The consumer under adaptation: `tools/track_recompose.py`
  (`declared-integration-mapping-v1`), extended IN PLACE per draft-1's own
  resolution rule ("the parser is the disposable half... this repo adapts
  the consumer to the pinned shape — never the reverse",
  `docs/state-track-schema.md`).

## Role boundary (pre-registered)

Zero pixels, zero exports, zero register edits, zero rendering of RUNTIME
tracks — the parser verdict this sprint is validation verdicts + mapping
decision-stream statistics (TEXT). Rendering the intaken tracks is
adjudication-adjacent and waits for its own owner brief (owner-sequenced).
Mapping decision SEMANTICS stay untouched: `declared-integration-mapping-v1`
is version-pinned in banked artifacts; changing what any banked record maps
TO is a separate owner decision. `docs/state-track-schema.md` stays frozen
as draft-1 HISTORY; v1 adaptation is new code + these review docs, never a
rewrite of the draft. Emitter-shaped findings route as MAILED findings
(their intake law: docs-only triage their side first) — never worked
around.

## Pre-registered mechanical consequence (named before the edit)

`tools/track_recompose.py` is itself in `MAPPING_SOURCE_FILES`, and the
banked `reviews/recompose-v13/recompose-manifest.json` pins every
mapping-source sha256 (`--check` + `DemoBundleGuards` enforce it). Editing
the consumer therefore REQUIRES regenerating that manifest (`--make-demo`) —
the manifest is self-describing mechanical output, not a judged verdict.
The re-bank is lawful ONLY under bar B2's condition: the demo track, sheet,
and APNG bytes must be BYTE-IDENTICAL after the edit (git diff shows the
manifest alone moving, its artifact sha256 pins unchanged); any pixel or
track byte moving = draft-1 behavior broke = the edit is wrong, not the
baseline.

## Bars (all-must-pass; verdicts NULL here, judged in commit C)

| # | Bar | What passes it (measurable) | Verdict |
|---|---|---|---|
| B1 | Intake integrity | Every mailed sha256 exact over source bytes BEFORE copy and over copied bytes AFTER write (manifest + both tracks); sidecars state exactly the mailed hashes and match computed bytes; verification.json verdict PASS with runs >= 2; fingerprint equality manifest-vs-verification; `/evidence/replay/**` routed `-text` in the SAME commit that stages the bytes; zero CR bytes in every copied file; intake-record complete (mailed-vs-computed table, worktree state, receipt summary quoted, machine class, trust split stated plainly, date). | NULL |
| B2 | Draft-1 regression | `track_recompose --check` exits 0 after EVERY parser edit (672/672 lane cells + 340/340 plan records + demo determinism + module pins + export pins); every existing draft-1 test in `tests/test_track_recompose.py` passes UNEDITED; the recompose-v13 re-bank moves ONLY `recompose-manifest.json` (demo track/sheet/APNG byte-identical, artifact pins unchanged inside it); the full suite discover runs green at a recorded count N. | NULL |
| B3 | v1 sufficiency | The adapted parser VALIDATES both reference tracks with zero schema violations (the roster-union shape of track 2 — deaths AND respawns — accepted, never `roster-mismatch`); union gaps BOTH directions surface as per-creature presence statistics (first/last frame, present-tick count) — information, not noise and not refusal; the mapping decision stream runs to completion over every record of both tracks with every decision either a pose selection or a TYPED refusal. | NULL |
| B4 | Semantics fidelity | Record-semantics item 4 honored: the consumer reads a record at frame F as post-tick state and documents the masks[F-1] alignment (no off-by-one re-derivation of its own); range domain enforced v1-side: first frame >= 1 (frame 0 refused as out-of-range), window-vs-`ticks_executed` cross-checked at intake; per-kit constants: selection rule = `constants[creature.kit]`, coverage must equal the roster's kit set exactly (both directions), track constants cross-checked vs the producing tree's combat.json at the manifest's game_commit AND vs this repo's banked attack_timing pins for the shared kit (striker); `possessed` required boolean on every v1 record, per-tick possessed counts reported as stats (seats is bundle-level, so count law is reported, not guessed); RUNTIME provenance: `provenance.class` == class, `provenance.bundle_id` == manifest bundle_id, both enforced. | NULL |
| B5 | Refusal-class correctness | Draft-1 refusal classes and triggers UNCHANGED for draft-1 tracks (the banked test file is the proof — zero edits to it); `runtime-intake-not-established` lifted ONLY through the verified `evidence/replay/` intake path (manifest + verification present, member hash recomputed, PASS + runs>=2) — a v1 RUNTIME track WITHOUT that context still refuses with the same class, and a SYNTHETIC v1 fixture is never admitted as evidence (v13 law carried); lawful mapping refusals on the reference tracks (e.g. `unmapped-action-class` on specials, `unrenderable-facing` off down/right, `unmapped-tween-class` off step_frames) documented as LAW with counts, never as defects; every refusal on the reference tracks accounted to a banked refusal class (an UNEXPLAINED refusal class = a finding, typed and routed). | NULL |
| B6 | Receipt boundary | The receipt mail answers EXACTLY the three asked lines — (a) mail md5 as received, (b) both track sha256s after copy + intake, (c) parser verdict on the roster-union delta (adapted / needs discussion) — plus findings typed as findings (emitter-shaped ones as MAILED findings per their intake law); zero sentences design game-side tools; zero integration asks; zero schedule claims; C6 untouched. | NULL |
| B7 | HFO gate (blocking) | intake-record.md, verdict.md, and the receipt mail each critiqued with accuracy and presentation scored SEPARATELY; accuracy = every hash/number traceable to a computation this session or a named banked source; presentation = truncated pyramid, typed findings, no unlabeled precision, register technical-concise. | NULL |

## Finding classes (pre-registered routing)

- **defect** — track content contradicts the s84 pin or spec section 5 →
  MAILED finding (their intake law: docs-only triage their side first;
  never worked around); intake stops if the defect breaks identity.
- **under-specification** — a consumer-relevant semantic the v1 pin leaves
  open → named in the receipt as an ask (findings-as-asks).
- **adaptation** — consumer-side work this delivery creates → done this
  sprint or queued with its trigger named.
- **noted** — observations with no action owed.

## Pre-registered non-claims

Zero adjudication of any lettered register item — validation verdicts and
decision statistics are TEXT about toolchain fitness, never visual
evidence; no register row moves, no "Current answer" edits, C1–C5 MET / C6
OPEN doubly gated, untouched. Zero schedule claims on T3/P2 (owner-paced).
Zero re-adjudication of banked verdicts. Test fixtures never enter
`evidence/` and are never admitted as evidence. The cadence-carry block in
`verdict.md` banks the SEVEN v29 numbers verbatim from the v30 brief (their
only carrier) — observed points only, never a trend; v30's push lands at a
NEW suite count (first composition change since v21) and is labeled "first
point at N tests", never pooled with the closed 693 band.
