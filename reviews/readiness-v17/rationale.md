# Pre-registration — v17 pipeline-maturity readiness register + exports-tree guard

Committed BEFORE `docs/integration-readiness.md` or `reviews/readiness-v17/verdict.md`
exist (the standing two-commit law). This file fixes the register's law and row
skeleton, the guard's derivation and extension law, and the pass bars. Statuses
stay UNJUDGED here; commit 2 judges each against its carrier.

## Sprint question

The hub's parking-lot gate names "assets integration — gated on game-two-assets
pipeline maturity" as the standing blocker, and nobody has defined pipeline
maturity mechanically. Can "can we integrate yet?" become a document read — a
mechanical, carrier-cited STATUS register instantiating the asset-contract's six
runtime-integration stop conditions — without preempting the three pending
owner/hub decisions (role re-pin, gate lift, capture tool spec)? And can the
v15 council Q3 residue ("the standing toolchain has no global stray-file guard
for exports/ outside `calibration-*`", carried two sprints) close with one new
module that derives its whitelist from banked constants and edits nothing
pinned?

## Register law (fixed verbatim; test-enforced)

**STATUS-ONLY LAW.** Every line of `docs/integration-readiness.md` is a status
plus a carrier citation (file path or done/ mail). Zero scheduling verbs, zero
design content, zero recommendations beyond naming what each open item waits
on. The register states its own advisory class in its header: input to the
hub's parking-lot gate; the hub decides; a status here never asks for anything.
Status vocabulary: `MET` / `MET-AT-CHECKPOINT` / `OPEN` (plus `BANKED` for the
mechanical-affordance row). Banned-verb scan (test-enforced, whole file,
case-insensitive, word-bounded): `will`, `schedul*`, `propos*`, `should
integrate`. No lore-class words (`lore`, `story`, `narrative` — word-bounded);
mechanical ids only (repo invariant 5). Owner/hub wording is quoted verbatim
from its carrier where a row records a ruling.

**Row format (test-enforced):** each stop-condition row is a `### C<n> —
<contract wording>` block carrying `**Status:**` and `**Carrier:**` lines;
carriers cite repo paths or done/ mail files.

## Row skeleton (the six `docs/asset-contract.md` stop conditions; statuses judged at commit 2)

- **C1 — game-two v17 fun verdict is closed.** Intended carrier:
  `done/from-game-two-family-block-sync-20260822.md` ("v17 and v18 are both
  CLOSED…") + the AGENTS.md boundary wording (synced `51851f4`).
- **C2 — one sprint-0 visual lane wins rather than merely being least bad.**
  Intended carriers: `reviews/calibration-v0/verdict.md` ("Lane B … wins
  calibration v0 — a genuine improvement, not least-bad"),
  `reviews/remedy-v15/verdict.md` (K-S selected under the pre-registered
  rule), `reviews/adoption-v16/verdict.md` + `docs/selection-register.md`
  (owner-ratified adoption, "Approved, proceed").
- **C3 — asset gate passes from a clean checkout.** Intended carrier: this
  sprint's own two gate runs recorded in the v17 verdict. The honest caveat is
  part of the row: these runs execute on the maintained working tree; no
  banked artifact records a from-scratch-clone run.
- **C4 — provenance and rights are complete.** Intended carrier: the nine
  banked `exports/*/release.json` manifests (+ `sources/` provenance the gate
  verifies).
- **C5 — visual critique passes at native scale.** Intended carriers:
  `reviews/remedy-v15/verdict.md` + `reviews/adoption-v16/verdict.md` (native
  1x rubric lines at the pinned protocol; calibration-v0 native-scale rubric).
  The protocol-vs-viewport gap stays a watch item, not a C5 qualifier dodge.
- **C6 — an integration design proves loading, draw order, and deterministic
  capture without changing simulation identity.** Intended carriers:
  `docs/owner-redirects.md` (2026-08-21 role re-pin pending, "No asset action
  until the game pins its new frame") + the hub parking-lot gate wording (mail
  carrier) + `done/from-game-two-v19-brainstorm-receipts.md` (capture
  instrument queued-for-v19-intake, owner-ratified E3(a) "yes please!";
  state-track field list pinned by the game seat at tool-spec time; the spec
  travels by mail). Expected shape: OPEN, doubly gated — status names what it
  waits on, nothing more.

Also fixed: an upstream-rulings section quoting the two done/ mail carriers
verbatim; a `BANKED` row for the k0-of-record mechanical affordance
(`tools/adoption_demo.py` `stage_ks_attack_dir`/`demo_dirs`, pinned by the v16
manifest; consequence clause in `docs/selection-register.md`); watch items
carried verbatim (shade double-duty v15 Q5; protocol-vs-viewport v15 Q5;
at-speed K-S band read rides the capture bundle, v16; DEF-3 packaging — the
pinned protocol line in any owner-handed demo); explicit non-claims (no
timetable, no design content, no integration ask, no re-opening of banked
verdicts, register existence is input to the gate — the hub decides).

## Guard design (fixed verbatim)

`tools/exports_guard.py`, NEW module; banked modules imported unmodified; no
hook rewiring; no edits to any pinned module.

**Whitelist derivation.** Derived at call time from the banked release-id
constants: `seam_metrics.RELEASE_IDS` + `remedy_masks.RELEASE_ID` +
`ingest_audio.RELEASE_ID` — never duplicated as quoted literals in the guard
(test-enforced). Recorded deviation from the sprint brief's two-constant
formula: the live tree carries the banked, gate-valid `audio-v1` release
(exporter `tools/ingest_audio.py`, its own `RELEASE_ID` constant, release.json
present); the brief's own live-tree-clean bar plus its derivation law ("derived
from banked constants") force the three-constant form. Council question 2
attacks this.

**Named top-level allowance.** `ALLOWED_TOP_FILES = {".gitkeep"}` — the
tracked hygiene file that keeps `exports/` present in a fresh clone. A named,
documented constant, not a stray blessing; anything else at top level is a
typed failure.

**Rules** (`check_exports_tree(exports_root) -> list[str]`, typed failures):

- (a) every directory directly under `exports/` must be whitelisted, else
  `stray-dir: <name>`;
- (b) every top-level file must be in the named allowance, else
  `stray-file: <name>`;
- (c) every whitelisted directory PRESENT on disk must carry `release.json`,
  else `missing-release-manifest: <id>`. Existence-only by design: content
  pinning stays `seam_metrics.check_export_pins`' and the asset gate's job. A
  whitelisted id absent from disk is not a tree failure (the pins check owns
  calibration completeness).
- a missing exports root is its own typed failure (`missing-exports-root`).

**CLI.** `--check` = this guard over the live tree + `check_export_pins` +
exit code (0 clean / 1 failures printed).

**Extension law (module docstring carries it).** A future release extends the
whitelist in ITS OWN pre-registration commit-1, by adding its exporter
module's release-id constant to the derivation — never by hardcoding an id,
never retroactively. Until that commit exists, the guard going red on a new
`exports/` entry is the designed behavior, not a defect.

**Proof obligations (test-enforced, both directions).** On synthetic fixture
trees under `tempfile`: a valid tree passes; a planted stray dir fails; a
planted top-level file fails; a removed release.json fails; a whitelisted name
present as a plain file fails. On the live tree: `check_exports_tree` returns
`[]` and `--check` exits 0 — asserted in the suite, so the guard is
continuously enforced from commit 1 forward. Whitelist-derivation test: the
guard's whitelist equals the union of the three banked constants, and no
whitelisted id appears as a quoted literal in the module source.

## INTEGRITY bars (any red stops the sprint)

1. Full suite green including new tests (>= 10800 s budget; 618 at v16 close).
2. Both asset_gate runs exit 0 (step 0 + immediately before banking).
3. `track_recompose --check` AND `pose_integrity_metrics --check` AND
   `remedy_metrics --check` AND `adoption_demo --check` ALL exit 0 at banking.
4. Exports guard clean on the live tree AND proven in both directions on
   fixtures.
5. Zero additions under `exports/`; zero new pixels.
6. Zero edits to any pinned module, banked artifact, banked verdict, or
   release bytes; `docs/selection-register.md` untouched (append-only law, no
   append due this sprint).
7. Zero writes into `../game-two` (read-only `git -C` from this repo's cwd).
8. Citations at the fresh pin with file:line where line-precision exists;
   every register status row carrier-cited (test-enforced); the two done/
   mail carriers quoted verbatim where the register records rulings.
9. The register passes its own shape tests (six conditions, carriers,
   banned-verb scan, watch items, advisory-class header).

## QUALITY bars (blocking)

- HFO pass on the register + the verdict: owner register, severity-honest,
  status-only, no promises; accuracy and presentation scored separately.
- One consolidated cross-vendor council call (<= 8k tokens total, Kimi K2.5,
  output file-redirected, read as UTF-8; the FULL register text, the guard
  design + whitelist derivation, and the carrier quotes inlined) attacking:
  (1) register over-claim — does any row preempt the owner's role re-pin, the
  hub's gate, or the capture tool spec? does MET overstate any carrier?
  (2) guard retroactivity + the extension law — can it go red on legitimate
  future state or bless strays? (the three-constant derivation deviation is
  named here); (3) frozen-state integrity across the five-manifest lattice;
  (4) readiness-register honesty — is a status register the right artifact, or
  does its existence pressure the gate? (5) the biggest unthought risk.
- Every REFUTED re-verified against primary bytes before adoption
  (v12–v16 precedent); reconciliation banked in the verdict appendix;
  adoptions folded before the final commit.

## Stop conditions (bankable outcomes, not failures)

The guard cannot be derived from banked constants without editing a pinned
module; a register row cannot be stated without design content or without
contradicting a carrier; the capture tool spec arrives asking for v17-scope
work (park + note unless the owner redirects live).

## Budget

One session; zero pixels; <= 6 new/changed files beyond the re-pin (this
file, guard, tests, register, verdict); one council call <= 8k tokens; no
second deliverable family.
