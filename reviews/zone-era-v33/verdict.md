# v33 — zone-era law + first era instance — verdict (judged)

**Answer first: PASS on both scores.** The standing law for zone-derived
manifests (immutable eras, content-sha naming, content-bound anchoring,
temp-script derivation, pin-and-migrate supersession) is ratified at
`docs/zone-era-manifests.md`; its first instance
`manifests/zone-palette-district-2eb1723d.json` (the rethemed
district's 14-key palette, UNCONSUMED by design) proves naming,
anchoring, and guard shape on real bytes; `tests/test_zone_eras.py`
guards every era file + the two grandfathered v32-era manifests in the
fast tier. Council (kimi-k2.5) verdict AMEND: five adoptions folded
into the law BEFORE commit B, four claims refuted against primary
bytes (appendix). Mid-session upstream drift (game 81cf358,
renderer.rb potion noun rename) was routed approve-by-default and —
proving L8 live — exposed and closed the LAST live-coupled anchoring
guard (scene-reference).

Accuracy and presentation are scored separately (Rule 2).

## Claims table (accuracy) — every claim carries its proving command; captured output in this file

| # | claim | proving command | captured output | verdict |
|---|---|---|---|---|
| 1 | commit A (rationale) precedes all law/instance/guard bytes | `git log --oneline --name-only <chore>..<C>` | chore 5122238 -> A e1d94e1 (rationale only, 261 ins) -> B 2c2283b (law+instance+guards, 422 ins) -> C (this file); no law/instance/guard bytes precede e1d94e1 | PASS |
| 2 | frozen zone manifests byte-identical to v31/v32 pins | `sha256sum manifests/zone-map-district.json manifests/zone-palette-district.json` | `b9843cbd... zone-map-district.json` / `ee2d185a... zone-palette-district.json` (= v31/v32 artifact-manifest pins, exact) | PASS |
| 3 | scene-reference.json byte-identical to its v32 pin (guard retarget touched TESTS only) | `sha256sum manifests/scene-reference.json` | `a013899f... scene-reference.json` (= v32 scene-exp-manifest pin, exact; chore commit stat: only runtime-baseline.json + tests/test_scene_compose.py) | PASS |
| 4 | era instance re-derives byte-identical from pinned game bytes | double-derive shas (P5) + installed sha256 | double-derive shas identical `47a6c169...` x2 (P5); installed file sha256 `47a6c1694b8169cebfc9391bc8856ba7c26da4de96cee4049909bba8d4e7fac9` | PASS |
| 5 | era filename = source content sha prefix | filename vs `anchoring.source_sha256_lf` | filename era `2eb1723d` == anchoring.source_sha256_lf[:8] `2eb1723d48bfa2a4...` (guarded every fast-gate run by test_zone_eras) | PASS |
| 6 | 81cf358 drift routed by class with mechanical evidence | `tools/pin_drift.py` output + cumulative diff read | pin_drift at 81cf3584 and again at d749458d: renderer.rb +4/-4 NOT additive-only, new sha f74b2fbb..., 20/20 constants OK, attack_timing OK, other four files [identical]; cumulative diff read = 3 text-fallback strings (PROVISION->POTION) + 1 comment, net-zero lines; class approve-by-default (MEMORY 2026-08-21), dev-seat note sent | PASS |
| 7 | asset_gate exit 0 post-routing AND immediately before commit C | two gate runs, captured exits | post-routing gate exit=0 (after chore edits, before commit); pre-commit-C gate exit=0 (g2a_v33_gate2.log tail clean); step-0 record: exit=0 at 05:06, then exit=1 at ~05:12 when 81cf358 landed mid-session (routed above) | PASS |
| 8 | five standing checks exit 0 at banking | 5x `--check` exits | track_recompose exit=0, pose_integrity_metrics exit=0, remedy_metrics exit=0, adoption_demo exit=0, exports_guard exit=0 | PASS |
| 9 | targeted suite green (zone_eras + scene_compose + runtime_extract + asset_gate) | unittest -v tail | `Ran 109 tests in 52.960s / OK` (test_zone_eras + test_scene_compose + test_runtime_extract + test_asset_gate, -v, zero skips - live re-derivation ran against real game-two) | PASS |
| 10 | zero edits to forbidden surfaces; ambient dirty state untouched | `git show --stat` of every v33 commit + `git status` | commit stats: chore = runtime-baseline.json + test_scene_compose.py only; A = rationale only; B = law doc + era manifest + test module only; `git status` after C: AGENTS.md still ' M' (owner edit untouched), untracked ambient files untouched; zero writes into ../game-two, zero tools/ edits, zero pixels/exports | PASS |
| 11 | council within Rule 7 budget, one consolidated call | measured tokens | 3534 in + 3340 out = 6874 <= 8k; one successful call (a kimi-thinking attempt died at the endpoint, 0 tokens) | PASS |
| 12 | cadence table: every number carries a named source | table below | see cadence table - every row names its carrier; two v32 rows banked UNAVAILABLE-AT-SPARK by name | PASS |

## Presentation (Rule 2, scored separately)

| surface | bar | verdict |
|---|---|---|
| docs/zone-era-manifests.md | answer-first one-liner; 005eab3 worked example; "what this means for you" close; terms defined on first use (era, anchoring, sha256_lf) | PASS - one-line law up top, 005eab3 worked example, dependency chain in L7, close: 'cost: one derivation, zero emergencies' |
| era manifest purpose field | names UNCONSUMED state + expected consumer + standing guard | PASS - purpose names UNCONSUMED, the expected consumer class, and the guard as standing consumer |
| this verdict | claims separable from prose; commands reproducible | PASS - claims table separable, commands reproducible, captured outputs inline |

## Cadence table (banked)

| item | real | source |
|---|---|---|
| v32 commit D (verdict) hook | UNAVAILABLE-AT-SPARK | rides the v32 session receipt in the hub; not carried in the v33 spark (banked gap, never interpolated) |
| v32 push (full gauntlet) | UNAVAILABLE-AT-SPARK | same carrier |
| d7294e9 fast-gate hook | UNTIMED | named gap in the v33 spark (authoring session did not wrap it) |
| d7294e9 push (full gauntlet) | 3h37m wall (launched 04:52, marker `exit=0 Sat Aug 29 08:29:06`); suite-stage split UNAVAILABLE - the log carried only the warn stream + push confirmation (verified by grep before deletion: no Ran/timing lines) | `g2a_push_20260829.log` (launched 04:52) + `.done` marker timestamp, harvested this session before deletion |
| v33 chore re-pin commit hook | 3m56.5s (commit 5122238) | this session, `time git commit` real |
| v33 commit A hook | 3m54.3s (commit e1d94e1) | same |
| v33 commit B hook | 3m57.4s (commit 2c2283b) | same |
| v33 commit C hook | banked in the session receipt (this file cannot carry its own hook real; measured by `time git commit` at commit C) | same |

## Council reconciliation appendix (one call, kimi-k2.5, verdict AMEND)

Adoptions (folded into the law BEFORE commit B):

1. **L2 clarity (from amendment 1's readability half):** council read
   "invariant 5" as a shape claim about zone ids and attacked
   content-sha ids as human-opaque. Adopted: the invariant-5
   parenthetical now says generic/mechanical ids verbatim
   (`district_two` qualifies), and L2 gained a "reading an era id"
   paragraph (derived_at + game_commit live inside the file; git dates
   the banking) plus the stated rationale for 8-hex (repo's standing
   citation width) and for content-addressing (era identity = content
   identity).
2. **L4 schema fixing (amendment 3, the sound half):** the deriving
   rationale must fix the era SCHEMA verbatim before the instance
   exists, and the sprint rides the house ship-gates. Adopted verbatim
   into L4 (this sprint already practiced it: rationale P4).
3. **L5 consumer declaration (amendment 6, the sound half):** an
   UNCONSUMED era declares its expected consumer class in `purpose`,
   and its guard is named as its standing consumer. Adopted into L5 +
   the instance's purpose field.
4. **L7 dependency chain (amendments 4/5, the sound core):** map-era
   derivation is now explicitly BLOCKED-ON (1) glyph semantics from
   PINNED game bytes with per-glyph citations (never visual
   interpretation), (2) pin-set extension for any cited semantics
   source file not already pinned — THIS is the mechanical closure of
   council's "semantics drift" story: once the cited source is pinned,
   a semantics change is content drift and gates like any other —
   and (3) the load_zone_map extension + typed-transition draw
   conventions; all owned by the first consuming lane.
5. **Race disclosure (amendment on multi-lane derivation):** derivation
   collisions are structurally dedup'd — era identity = content
   identity, and P3 asserts not-exists (no overwrite path). Adopted as
   L2's "identity-only churn can never mint duplicate eras" sentence;
   the seat-lease law (one LIVE writer per workspace) serializes
   actual writes. No tracking file added (new permanent surface
   refused; the v34 inheritance list carries the lane).

Refuted (re-verified against primary bytes; v18 precedent — council
scenarios must survive live git demos):

1. **"Era id should be game_commit-prefixed (`ad7f6a1e-2eb1723d`)."**
   REFUTED mechanically: the same source content exists at MANY
   commits (identity-only drift is this repo's daily weather — three
   re-pin chores in the last five HEAD commits). A commit-prefixed
   name mints a NEW filename for byte-identical content at every
   re-pin-era derivation, violating era=content dedup; council's own
   cons row concedes rebases invalidate commit ids. Chronology needs
   are served inside the file (adoption 1).
2. **"At the NEXT retheme the old map era goes gate-red / an emergency
   fires if the loader lags" (attack 1a).** REFUTED against the
   post-d7294e9 guard bytes: the frozen-era guards assert frozen
   constants (`9774cdd0…`), NOT live equality — a retheme reddens
   ONLY the runtime-baseline live-pin surfaces, which route by the
   standing drift protocol (routed twice live during THIS session,
   zero emergencies). A lane needing the NEW map before the loader
   lane exists is sequenced WORK (L7 dependency chain), not an
   integrity emergency: nothing banked reddens while it waits.
3. **"Executable value_citations / CI-verified line numbers"
   (amendment 2).** REFUTED as stated: citations cite lines in CONTENT
   FROZEN by source_sha256_lf — they cannot rot against their own
   pinned source. Live-drift protection is pin_drift's job (20
   derived constants + lunge needles re-verified at every re-pin,
   proven again this session) plus adoption 4's pin-set extension for
   map semantics. A permanent citation-executor tool would grow the
   unpinned-tool census L4 forbids, for a risk already covered.
4. **"Unconsumed eras must gain a consumer within 2 sprints or be
   removed" (amendment 6, the sunset half).** REFUTED: contradicts L1
   (immutability is the load-bearing simplicity) and mis-models the
   guard — `test_zone_eras.py` re-derives the instance from pinned
   game bytes on EVERY fast-gate run, so "stale before consumed" is
   impossible while the guard is green; anchoring cannot dangle
   (game-two history rewrite would be a program-level integrity event
   far beyond era files). Deletion stays L5's banked-decision path.
5. **"district_two might be missed / manual discovery risk" (attack
   1b).** REFUTED as a failure mode: eras are PULL-model — derived by
   the first consuming lane, not pushed at every upstream zone. An
   underived zone costs nothing and reddens nothing; the v34
   inheritance list carries the watch item.

Confirmed by council (banked as-is): the scene-reference retarget
closes the last live-coupled GUARD surface (attack 2's table matches
this session's grep); track_recompose fan-out named fragile-but-
pinned (already law, L4); the unconsumed instance is "necessary as
proof" with the guard as its consumer (attack 4's own loss table:
without it the guard module guards nothing and the re-derivation
mechanism ships unverified).

## v34 inheritance

- **Zone-map/glyph lane** (L7, full dependency chain): glyph semantics
  from pinned loader/renderer bytes (census `# , . g w ~`), pin-set
  extension for cited semantics sources, `load_zone_map` multi-glyph
  extension, typed-transition draw conventions (`stairs_up`, `hole`),
  track_recompose fan-out ownership (six manifests, --make flags).
- **district_two watch**: upstream zone id exists (transition
  `{"at":[40,0],"to":"district_two","type":"hole"}`); first consuming
  lane derives `zone-<kind>-district_two-<era>.json` under the law.
- **First consumer for `zone-palette-district-2eb1723d.json`**: the
  next runtime/scene recomposition lane over the rethemed district
  pins it (L5 migration path) — note the rethemed palette also carries
  non-RGB values (`motif: "chip"`): the consuming lane owns mapping
  semantics, the era file stays verbatim.
- **Upstream churn expectation**: game v20-T3/T4 staged; expect
  further renderer/display drift → route by class, re-pin at
  checkpoints; the era law removes zone manifests from that blast
  radius.
- **Cadence**: v32 D + v32 push reals still ride the hub receipt
  (UNAVAILABLE-AT-SPARK here); carry forward until banked.
