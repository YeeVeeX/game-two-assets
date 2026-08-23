# Pre-registration — v18 pipeline-maturity maintenance: clean-checkout C3 proof + pin-drift verifier

Committed BEFORE any proof artifact, register edit, or verdict exists
(the standing two-commit law). This file fixes both proof protocols,
the decidable-class table, the C3 target wording (drafted, UNJUDGED),
and the pass bars. Commit 2 judges the C3 row against the actual
checkout outcome and banks the verdict.

## Sprint question

Two banked carriers name the only honest unilateral residues after v17:
the C3 row's own caveat ("banked gate runs execute on the maintained
working tree; no banked artifact records a from-scratch-clone run") and
the v17 pin-cadence finding (three pinned-file hops in one session, the
14-constant re-verify living in a deleted throwaway script, a
json.dumps array-explosion trap hit live on the manifest). Can the C3
caveat close with a scripted, both-directions clean-checkout proof —
judged honestly against what "clean checkout" can mean for a gate that
contracts against live externals — and can the re-pin protocol's
MECHANICAL half become a permanent read-only verifier so every future
hop costs minutes and zero re-derivation? Zero pixels; one register row;
the register's FIRST maintenance cycle, proving the update law works.

## Protocol A — clean-checkout proof (`tools/checkout_gate.py`), fixed verbatim

**Externals statement (named up front, carried into the report and any
C3 wording):** the asset gate deliberately contracts against live
externals — the sibling `../game-two` checkout (read-only `git -C`
reads), the pinned Aseprite binary, and an invoking Python
interpreter. "Clean checkout" therefore means a from-scratch clone of
THIS repo's committed HEAD, never a hermetic environment. LFS smudge
and pypi are network surfaces; the primary proof uses neither.

**Script steps (primary, zero network):**

1. Resolve this repo's root; record its HEAD (`git rev-parse HEAD`).
2. `git clone --no-hardlinks` from the repo's own `.git` into a fresh
   temp dir with `GIT_LFS_SKIP_SMUDGE=1` (deterministic two-phase LFS:
   clone leaves pointers, never depends on clone-time smudge).
3. `git lfs pull` in the clone, exactly once, from the local origin
   (file-path remote — the source repo's `.git/lfs` object store; zero
   network). Scan for remaining LFS pointer files; record the count.
4. Run the CLONE's own gate copy with the existing interpreter:
   `<python> <clone>/tools/asset_gate.py --root <clone> --game-root
   <absolute ../game-two> --aseprite <absolute pinned path>`, cwd = the
   clone, `GIT_*` scrubbed from the environment, `PYTHONIOENCODING=utf-8`.
   Capture exit code + full stdout/stderr.
5. **Negative control (mandatory, clone-only):** tamper the CLONE's
   `manifests/runtime-baseline.json` by replacing the first
   `source_files[].sha256_lf` hex literal with 64 zeros — a SURGICAL
   byte-level text replacement (the v17 array-explosion trap: never
   re-serialize the manifest), and the hard-failure class (a tampered
   `game_commit` would only WARN under the parallel-session law).
   Re-run the gate; REQUIRE nonzero exit AND output naming the
   violation (`sha256_lf does not match`). Restore the original bytes.
6. **Secondary (best-effort, network surface):** create a fresh venv in
   the temp dir, `pip install -r <clone>/requirements-dev.txt`, re-run
   the gate with the fresh interpreter. Any venv/pip failure records
   `SKIPPED` with the reason — never a sprint fail.
7. Write ONE JSON report to the explicitly passed `--report` path:
   source HEAD, clone HEAD, LFS phase results, externals (game root +
   its HEAD at run time, aseprite path, interpreter paths), both/all
   exit codes with outputs, per-direction verdicts, overall verdict.
   The tool writes ONLY under its temp dir and that report path, and
   removes the temp dir at exit.

**PASS definition:** primary gate run exits 0 AND the negative control
exits nonzero naming the violation. Secondary PASS or SKIPPED never
changes the overall verdict; a secondary that RUNS and fails is
recorded as its own typed outcome (`SECONDARY-FAIL`) for session
judgment, never silently folded.

**Contingencies (both outcomes bankable):** if LFS pointers survive the
one `lfs pull` and the gate fails on source hashes, or the clean run
fails for any other legitimate reason, that failure IS the C3 answer —
the row stays as-is and the finding banks in the verdict. If game-two's
seat lands a pinned-file content hop between the step-0 gate run and
the checkout run, the gate fails against live committed drift: route
the re-pin per the standing protocol, then re-run the checkout proof.

## Protocol B — pin-drift verifier (`tools/pin_drift.py`), fixed verbatim

READ-ONLY by contract AND by proof: the tool writes NOTHING anywhere
(no files, no manifest edits); the test suite byte-hashes a fixture
tree before/after a full run and requires identity. It is never wired
into hooks, and its tests contain NO live-drift assertions (fixtures
only — `test_asset_gate`'s live-pin tests remain the ONE suite surface
that reds on upstream drift).

**What it computes (the re-pin protocol's mechanical half):**

1. Read `manifests/runtime-baseline.json` (old pin: `game_commit` +
   per-file `sha256_lf`) and `manifests/render-reference.json` (the
   derivation source). Parameterizable:
   `--game-root/--baseline/--reference/--new-commit` (default new
   commit: the game root's HEAD) so fixtures can drive it.
2. Per pinned file: blob id at old pin vs new commit
   (`git -C <game-root> rev-parse <sha>:<path>`); for drifted files,
   `git diff --numstat/--stat` (+/- line counts) and the recomputed
   `sha256_lf` over LF-normalized COMMITTED bytes (`git show`, CRLF
   folded to LF — the manifest's cross-platform hash law).
3. Constant battery, DERIVED from `render-reference.json` at call time
   (the guard's derive-don't-duplicate law; zero hardcoded values in
   the tool): every needle is built from the JSON values and checked
   against the renderer.rb/creature.rb blob at the NEW commit — body
   colors (striker/human), hurt flashes + flicker period, ALLY_DIM,
   telegraph edge/core colors, swell + core-expand + inner-inset
   rects, possession-ring color + expand rect, notch color + size,
   lunge windup/active offsets, SIZE — plus the JSON-internal
   consistency `edge_expand_px * 2 == swell_px`. Verified on every
   run (identical blobs double as a continuous needle self-test).
   Zone-palette JSONs carry no needle battery: their drift routes by
   diff class alone.
4. attack_timing ALWAYS re-verified at the new commit (its source
   `data/balance/combat.json` is commit-anchored, NOT in the pin set —
   it can move while all five pinned blobs stay identical): each
   `json_pointer` from the reference resolved in the new blob and
   compared to the recorded value (5/4/8/13 at v18 open).
5. Exact old/new manifest line pairs (the literal lines as they appear
   in the baseline text, old value → new value) for `game_commit` and
   each drifted `sha256_lf` — the session applies them via the edit
   tool as surgical replacements; the tool writes nothing.
6. ONE routing line per the decidable-class table below. Exit codes:
   0 = analysis complete (WHATEVER the route — the tool is an advisor,
   never a gate); 2 = analysis failure (bad args, git failure, missing
   reference path). Never exit 1: nothing may mistake it for a
   pass/fail gate.

**Decidable-class table (recommendation lines ONLY for mechanically
decidable classes; everything else quotes the protocol clause):**

| Machine finding | Routing line |
|---|---|
| All five pinned blobs identical at the new commit, attack_timing green | `ROUTE: mechanical re-pin (identity drift only)` |
| Every drifted file additive-only (numstat deletions == 0) AND all derived constants green AND attack_timing green | `ROUTE: approve-by-default candidate — the session applies the protocol; the tool decides nothing` |
| ANY deletion in a pinned file (including binary/unparseable diffs) | `ROUTE: SESSION JUDGMENT REQUIRED` + the quoted clause |
| ANY constant-check failure or attack_timing mismatch | `ROUTE: SESSION JUDGMENT REQUIRED` + the quoted clause |
| Baseline/reference/git surprise (missing file at commit, malformed manifest) | exit 2, typed analysis failure |

The quoted clause (owner-extended protocol, project MEMORY 2026-08-21):
"semantic-preserving refactors + additive features in a pinned file
that move NO render-reference.json constant join the approve-by-default
class — only draw-value moves or true removals still stop for owner
review." Deletions are NOT mechanically decidable as removals-vs-
refactors — that is exactly the session-judgment hop; the tool never
attempts it.

**Automation-bias guards (fixed):** the tool never prints "approved";
the candidate line names itself a candidate and the session as the
decider; judgment routes quote the clause rather than summarize it;
recommendation wording is test-pinned on fixtures for all four classes.

## Test law (`tests/test_maturity_tools.py`)

Fixtures only — synthetic git repos under tempfile (`GIT_*` scrubbed,
the repo's `remedy_masks._git_env` pattern), a miniature baseline +
reference + renderer/creature/combat fixture set. All four pin_drift
classes proven: identity → mechanical line; additive-only clean →
candidate line; an in-place moved constant (reference says swell 8,
blob says 9) → constant FAIL + judgment route, MUST NOT recommend
approve; a deletion → judgment route quoting the clause. Read-only
proof: every file under the fixture tree (including `.git`) SHA-256
hashed before/after a full `pin_drift` run — byte-identical. Needle
derivation unit-proven (missing reference path → typed failure; needle
absent from blob string → FAIL). checkout_gate is covered by
pure-function tests (tamper is surgical + line-count-preserving +
still-parseable, pointer detection, violation naming, report schema,
overall-verdict logic) WITHOUT running a full clone in the suite — the
live both-directions run is commit 2's banked artifact, not a suite
surface.

## C3 target wording (DRAFTED here; judged at commit 2 against the actual outcome)

If and only if the primary passes AND the negative control fails
correctly, the C3 row moves to MET with this shape: proven in both
directions on a from-scratch local clone of committed HEAD via
`tools/checkout_gate.py`; externals NAMED in the row (live sibling
game-two checkout read-only, pinned Aseprite binary, invoking
interpreter, LFS bytes from the local origin's object store);
working-tree runs stay the per-sprint checkpoint; the clean-checkout
variant re-provable on demand by the tool; carrier =
`reviews/maturity-v18/checkout-report.json` + `tools/checkout_gate.py`
+ `reviews/maturity-v18/verdict.md`. The header's exact status split
and the summary table row move with it. If the clean run fails
legitimately, the row STAYS as-is and the failure banks as the finding
— both outcomes are bankable wins; the shape law outranks the upgrade
(if the wording cannot keep all 11 shape tests green unmodified, the
row stays and the finding banks).

## Pass bars

**INTEGRITY (any red stops the sprint):** full suite green including
the new tests (>= 10800 s; 645 at v17 close; drift-routing recorded
honestly, never hidden); both asset_gate runs exit 0 (step 0 +
immediately before banking); five standing `--check`s ALL exit 0 at
banking (`track_recompose`, `pose_integrity_metrics`, `remedy_metrics`,
`adoption_demo`, `exports_guard`); checkout proof captured in BOTH
directions (clean exit 0 + tampered-clone nonzero) OR the clean-run
failure banked as the finding with C3 unchanged; pin_drift proven on
all four fixture classes AND read-only by byte-hash; zero additions
under `exports/`; zero new pixels; zero edits to any pinned module,
banked artifact, banked verdict, or `docs/selection-register.md`;
register shape tests 11/11 green after the C3 edit with ZERO shape-test
edits; zero writes into `../game-two`; citations at the fresh pin;
verbatim quotes wherever rulings are cited.

**QUALITY (blocking):** HFO pass on the register delta, the verdict,
and both tools' CLI output (typed failures, one-line OK, silent-on-pass
suite behavior; accuracy vs presentation scored separately); one
consolidated cross-vendor council call (<= 8k tokens total, Kimi K2.5,
output file-redirected, read as UTF-8; the FULL old and new C3 row, the
checkout report, and pin_drift's decidable-class table + docstring
inlined) attacking: (1) C3 MET honesty against the literal "clean
checkout" contract wording; (2) pin_drift misclassification and
automation bias; (3) frozen-state integrity + the growing unpinned-tool
class; (4) register-maintenance precedent — the first status flip rides
a carrier the same session produced; what stops carrier inflation?;
(5) the biggest unthought risk. Every REFUTED re-verified against
primary bytes before adoption; reconciliation banked in the verdict
appendix; adoptions folded before the final commit.

## Boundaries (restated as committed law)

Zero new pixels, sprites, releases, exports; no capture-spec drafting
(park on arrival); no integration design content; no game-two writes;
no re-opening banked verdicts; no edits to pinned modules or existing
selection-register entries; no hook rewiring; no shape-test weakening;
mechanical ids only. pin_drift and checkout_gate join the deliberately
UNPINNED tool class (the v17 verdict's rationale: hash-pinning
maintenance tools recreates the frozen-exporter trap); their integrity
is test-carried, and neither ever gates anything.
