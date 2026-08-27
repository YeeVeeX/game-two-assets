# E3a-T2 RUNTIME intake + v1 consumer adaptation — rationale (v30, PRE-REGISTERED)

**Status: rubric FIXED BEFORE the parser work.** This file is committed with
every verdict cell NULL, alongside the intake evidence (commit A). The
adaptation (commit B) and the judged copy + `verdict.md` (commit C) land
after — the commit-A/commit-B discipline every calibration sprint used. No
cell may be filled before its evidence exists. *(Commit C note: cells below
are now JUDGED; the bar text is byte-unchanged from the commit-A
registration — only the Verdict column moved, evidence line-cited.)*

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
| B1 | Intake integrity | Every mailed sha256 exact over source bytes BEFORE copy and over copied bytes AFTER write (manifest + both tracks); sidecars state exactly the mailed hashes and match computed bytes; verification.json verdict PASS with runs >= 2; fingerprint equality manifest-vs-verification; `/evidence/replay/**` routed `-text` in the SAME commit that stages the bytes; zero CR bytes in every copied file; intake-record complete (mailed-vs-computed table, worktree state, receipt summary quoted, machine class, trust split stated plainly, date). | **PASS** — intake script (session-run, output banked in `intake-record.md`): 6/6 mailed sha256 exact at source, 6/6 exact post-copy; sidecars state exactly the mailed hashes; verification.json `verdict: "PASS", runs: 2`; `fingerprint_at_verification` == manifest `fingerprint_md5` (`d8abc55a...`); `git check-attr` printed `text: unset` on the evidence paths before staging and the staged blobs re-hashed to the mailed values (`e5682280.../dd68c8cb.../3d05a1f8...`); CR-byte count 0 for all six copies; intake-record carries the table, worktree state (game HEAD `ea0e37c7` at read, bundle gitignored), the quoted receipt, machine class `GABO_DESKTOP`, the trust split, and the date |
| B2 | Draft-1 regression | `track_recompose --check` exits 0 after EVERY parser edit (672/672 lane cells + 340/340 plan records + demo determinism + module pins + export pins); every existing draft-1 test in `tests/test_track_recompose.py` passes UNEDITED; the recompose-v13 re-bank moves ONLY `recompose-manifest.json` (demo track/sheet/APNG byte-identical, artifact pins unchanged inside it); the full suite discover runs green at a recorded count N. | **PASS** — `--check` exit 0 immediately after the parser edit batch (the single intermediate FAIL was exactly the pre-registered pin consequence, resolved by the pre-registered re-bank) and exit 0 again as standing check 1 at the gate; all 33 `tests/test_track_recompose.py` tests green with the file UNEDITED (git touches only `tests/test_track_v1.py`); the consequence widened to the SAME class in three sibling manifests (defect-audit-v14, remedy-v15, adoption-v16 — their tests pin the consumer's sha256 too): each regenerated by its OWN tool, git diff = consumer pin line + `repo_commit_at_generation` ONLY (quoted in `verdict.md`), every artifact byte-identical (demo track/sheet/APNG sha256 pins unchanged; v14's 12, v15's 28, v16's 9 artifacts reproduced with zero diffs); full discover green at N=748 (`Ran 748 tests in 3067.871s` / `OK`, EXIT:0, captured `v30_discover.log`; the +55 over the closed 693 band = exactly `tests/test_track_v1.py`) | 
| B3 | v1 sufficiency | The adapted parser VALIDATES both reference tracks with zero schema violations (the roster-union shape of track 2 — deaths AND respawns — accepted, never `roster-mismatch`); union gaps BOTH directions surface as per-creature presence statistics (first/last frame, present-tick count) — information, not noise and not refusal; the mapping decision stream runs to completion over every record of both tracks with every decision either a pose selection or a TYPED refusal. | **PASS** — `validate_track` returned `[]` for both reference tracks (smoke run + test-pinned in `CommittedEvidenceIntegration`); track 2 (20-creature union, per-tick sizes 16-18) accepted with presence gaps EXACTLY `[rusher0, rusher1, rusher15, rusher16]` and the mail's four machine-verified frames reproduced from bytes (rusher1 last 615, rusher0 last 688, rusher15 first 916, rusher16 first 989 — both directions, deaths AND joins); decision stream completed 2538 decisions (track 1) and 9120 (track 2) with accounting balanced (mapped + refused == decisions, test-asserted) and every refusal typed | 
| B4 | Semantics fidelity | Record-semantics item 4 honored: the consumer reads a record at frame F as post-tick state and documents the masks[F-1] alignment (no off-by-one re-derivation of its own); range domain enforced v1-side: first frame >= 1 (frame 0 refused as out-of-range), window-vs-`ticks_executed` cross-checked at intake; per-kit constants: selection rule = `constants[creature.kit]`, coverage must equal the roster's kit set exactly (both directions), track constants cross-checked vs the producing tree's combat.json at the manifest's game_commit AND vs this repo's banked attack_timing pins for the shared kit (striker); `possessed` required boolean on every v1 record, per-tick possessed counts reported as stats (seats is bundle-level, so count law is reported, not guessed); RUNTIME provenance: `provenance.class` == class, `provenance.bundle_id` == manifest bundle_id, both enforced. | **PASS** — record semantics: the stream output carries the pinned reading verbatim (`record_semantics` field: post-tick state, masks = `input_log.masks[F-1]`) and no code re-derives its own alignment; domain: frame-0 window refuses `out-of-range` (test), window-vs-`ticks_executed` enforced through the intake context (`10..13 outside 1..12` test) and both real windows sit inside 1..1249; per-kit selection rule test-pinned (rusher windup state_frames 15 legal under its own kit where the striker law refuses); coverage both directions (missing kit → `missing-field`, extra kit → `roster-mismatch`, tests); constants cross-check 5/5 kits exact vs combat.json at `c6ceb8c0` + striker == banked attack_timing 13/5/4/8 (intake-record); `possessed` bool enforced (missing/non-bool tests) with histogram exactly `{1: 141}` and `{1: 540}` — reported as stats, count law not guessed; provenance.class equality (draft-1 law carried) + `bundle_id` required and admission-checked against the manifest (mismatch test) | 
| B5 | Refusal-class correctness | Draft-1 refusal classes and triggers UNCHANGED for draft-1 tracks (the banked test file is the proof — zero edits to it); `runtime-intake-not-established` lifted ONLY through the verified `evidence/replay/` intake path (manifest + verification present, member hash recomputed, PASS + runs>=2) — a v1 RUNTIME track WITHOUT that context still refuses with the same class, and a SYNTHETIC v1 fixture is never admitted as evidence (v13 law carried); lawful mapping refusals on the reference tracks (e.g. `unmapped-action-class` on specials, `unrenderable-facing` off down/right, `unmapped-tween-class` off step_frames) documented as LAW with counts, never as defects; every refusal on the reference tracks accounted to a banked refusal class (an UNEXPLAINED refusal class = a finding, typed and routed). | **PASS** — draft-1 refusal law byte-carried (the banked test file unedited and green; the ONE dispatch delta is named in `verdict.md`: an unknown `schema_version` now refuses `bad-enum` early instead of falling through to flat-constants law — unreachable for any draft-1 track); `runtime-intake-not-established` lifted ONLY through `verify_runtime_intake` (11 fail-direction fixture tests: outside-root, missing manifest, RED verdict, runs 1, runs "2", bundle_id mismatch, fingerprint mismatch, missing sidecar, sidecar hash mismatch, ticks_executed 0 — plus the real-bundle PASS direction); RUNTIME fixtures without context refuse with the SAME class (decision_stream + recompose_track + draft-1-RUNTIME-with-context tests); SYNTHETIC v1 fixtures never admitted (class check precedes intake); lawful refusals on the reference tracks documented with counts — `unrenderable-facing` 504 + 1425 (up/left facings; banked rows are down/right only), `unmapped-tween-class` 12 + 4 (off-kit-step tween while moving) — and test-asserted ⊆ the banked lawful set (zero unexplained classes; `unmapped-action-class` legal but unobserved: no specials in these windows); two ADDITIVE typed refusals named: `unmapped-zone` (replaces a raw KeyError crash) and `missing-reference` (v1 internal guard) | 
| B6 | Receipt boundary | The receipt mail answers EXACTLY the three asked lines — (a) mail md5 as received, (b) both track sha256s after copy + intake, (c) parser verdict on the roster-union delta (adapted / needs discussion) — plus findings typed as findings (emitter-shaped ones as MAILED findings per their intake law); zero sentences design game-side tools; zero integration asks; zero schedule claims; C6 untouched. | **PASS** — `receipt-draft.md` opens with the four RECEIPT lines (mail md5 / both track sha256s / roster-union-delta = ADAPTED — exactly the s84 ask, in its order); findings section: emitter defects NONE + one our-side note; council Q4 sentence-scan CONFIRMED clean ("does not design game-side tools, impose schedule, or overclaim visual/adjudication conclusions"); non-claims paragraph carries C6 OPEN, no schedule, fence untouched | 
| B7 | HFO gate (blocking) | intake-record.md, verdict.md, and the receipt mail each critiqued with accuracy and presentation scored SEPARATELY; accuracy = every hash/number traceable to a computation this session or a named banked source; presentation = truncated pyramid, typed findings, no unlabeled precision, register technical-concise. | **PASS** — judged separately per artifact in `verdict.md` (HFO gate section): intake-record accuracy PASS / presentation PASS; verdict accuracy PASS / presentation PASS; receipt accuracy PASS / presentation PASS — axis-by-axis evidence there | 

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
