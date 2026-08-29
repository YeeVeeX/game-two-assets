# v33 — zone-era law: naming, anchoring, guarding, and supersession of zone-derived manifests — rationale (PRE-REGISTERED)

**Status: the era-law draft, derivation protocol, and pass bars below are
FIXED BEFORE any law, instance, or guard bytes exist in the repo.** This
file is commit A of the house three-commit shape: the ratified law + the
first era instance + the guard module land at commit B, the judged
verdict at commit C. The law draft is recorded VERBATIM as it went to
council (one consolidated call, Rule 7 budget <= 8k tokens); council
adoptions fold into `docs/zone-era-manifests.md` BEFORE commit B and the
reconciliation lands in the verdict appendix.

**Authorization:** owner-greenlit SPARK-UP v33 (2026-08-29), inheriting
d7294e9's v33 note ("scene work on the NEW zone needs an era design for
district manifests") and project MEMORY 2026-08-29 (anchored-manifest
guards bind to derivation-era shas, never live-equality — the ZONE 2
retheme catch-22 is the precedent).

## Step-0 record (evidence in the verdict claims table)

- Push marker `g2a_push_20260829.done` ABSENT at session start (05:05):
  repo HOOK-BUSY until the d7294e9 pre-push gauntlet lands; all law
  drafting, council work, and derivation prep ran read-only in temp.
- Seat mail inbox: EMPTY at session start (re-checked at close).
- asset_gate run 1 (05:06): exit 0 — identity-only drift WARNING (game
  HEAD 5dacb7d vs pin 2808a44d, content identical) + renderer.rb
  worktree-only WARNING. asset_gate run 2 (~05:12): exit 1 — upstream
  81cf358 (2026-08-29 05:05:49) landed renderer.rb CONTENT drift
  mid-session.
- pin_drift (2808a44d → 81cf3584): renderer.rb +4/-4 NOT additive-only;
  creature.rb / display.json / nest.json / district.json all
  [identical]; 20/20 render-reference constants OK; attack_timing OK.
  Full cumulative diff read (= hop diff; the pin IS the last banked
  baseline): 4 replaced line-pairs, net-zero lines — 3 frozen
  text-fallback strings (PROVISION→POTION noun rename: CUE_TEXT_FALLBACK
  provision_bought/provision_used, HUD_STOCK_FALLBACK) + 1 comment line.
  Zero render-reference constants moved, zero draw geometry/color/timing
  values, zero value_citation line numbers shifted (all cited spans are
  outside lines 185-212 or unshifted by the net-zero diff). CLASS:
  approve-by-default (2026-08-21 owner-extended protocol: moves NO
  render-reference constant; deletions are re-emissions with a noun
  swap, no true removals). ROUTE: re-pin at the first checkpoint after
  the marker lands + dev-seat note (mail, at close).
- Consequence discovered while routing: `manifests/scene-reference.json`
  (renderer-derived, byte-pinned sha256 `a013899f…` by the v32 artifact
  manifest) still carried a LIVE-equality anchoring guard
  (`test_scene_compose.test_anchoring_bound_to_runtime_baseline_content_pin`
  asserts manifest sha == live baseline renderer pin). The 81cf358 drift
  re-fires the d7294e9 catch-22 on the renderer axis: gate red without
  the re-pin, that guard red with it. ROUTE (rides the re-pin commit,
  the d7294e9 owner-ratified pattern + project MEMORY 2026-08-29):
  retarget the guard to the frozen derivation-era content pin
  `45827b9a…` and additionally pin the manifest's own frozen bytes
  (sha256 `a013899f…`) — strictly stronger than the live coupling it
  replaces. scene-reference.json itself: ZERO edits.

## The era-law draft (VERBATIM, as sent to council)

<law-draft — the exact bytes reviewed by council; adoptions fold into
docs/zone-era-manifests.md, deltas reconciled in the verdict appendix>

# Zone-era manifests — how zone-derived manifests are named, anchored, guarded, and superseded

**The law in one line:** a zone-derived manifest is immutable once
banked; consumers pin its path + sha256; when upstream zone content
changes, you derive a NEW era file beside the old one — you never
regenerate in place.

## Why this law exists (the 005eab3 retheme, worked example)

On 2026-08-29 upstream deliberately rethemed ZONE 2 (game `005eab3`,
descent floor -1): `data/zones/district.json` took draw-value moves
(floor/grid/wall/motif/ambient) plus geometry replacement (26x44 →
88x52 tiles, glyph census `.#` → `# , . g w ~`, typed transitions, a
new `district_two` id). Two repo guards asserted that our derived
district manifests' anchoring equaled the LIVE baseline pin. Result: a
commit-blocking catch-22 — asset_gate red without a re-pin, the
anchoring guards red with it — resolved only by an owner-review
emergency (d7294e9). The banked v31/v32 artifacts byte-pin those
manifests, so "just regenerate them" would have corrupted banked
evidence. This document is the standing law so the NEXT retheme (or
`district_two`) costs one derivation instead of one emergency.

## The law

**L1 — Immutability.** A zone-derived manifest is IMMUTABLE from the
moment any banked artifact manifest under `reviews/` byte-pins it
(path + sha256). Regenerate-in-place is forbidden. New upstream zone
content = a new era file beside the old one.

**L2 — Naming.** Era id = the first 8 hex of the SOURCE file's
sha256_lf at derivation. Filename:
`manifests/zone-<kind>-<zone>-<era>.json` (kind: `palette`, `map`,
...; zone: the game's zone id, generic — invariant 5). Example: the
rethemed district palette derives from district.json content
`2eb1723d…` → `zone-palette-district-2eb1723d.json`. Prefix collision
inside one `<kind>-<zone>` family (32-bit space): the NEW file takes
the first 12 hex instead; existing files never rename. Grandfather:
`zone-map-district.json` and `zone-palette-district.json` (v32-era,
source `9774cdd0…`) keep their legacy unsuffixed names; guards pin
them frozen.

**L3 — Anchoring binds to content, never to the live pin.** Every era
file carries an `anchoring` block: `game_commit` (a game-two commit
whose committed source_file content hashes LF to source_sha256_lf —
recorded from the runtime-baseline pin at derivation; the re-derivation
handle), `source_file`, `source_sha256_lf` (LF-normalized sha256 of the
source blob — the BINDING identity), and per-field `value_citations`.
Guards assert the frozen sha constants recorded in the manifest —
NEVER equality with the live runtime-baseline pin, which moves with
upstream development (project MEMORY 2026-08-29; d7294e9 is the
precedent). Identity-only baseline re-pins never invalidate an era.

**L4 — No permanent deriver tool.** Eras are derived by a TEMP script
(run, deleted; protocol pre-registered in the deriving sprint's
rationale): values copied VERBATIM from pinned game bytes
(`git -C ../game-two show <game_commit>:<source_file>`), citations per
field, double-derive byte-identical before banking. The unpinned-tool
census does not grow (v24 census: exports_guard, checkout_gate,
pin_drift in tools/, fast_gate in bin/). Rationale: editing a pinned
permanent tool moves its sha into every consumer manifest —
track_recompose.py's sha rides SIX banked manifests, each regenerated
only by its own --make flag (v32 verdict documents the mechanism).

**L5 — Supersession.** A new era never edits or retires an old one.
Consumers migrate by pinning the new path + sha in their OWN
manifests. An era file is deleted only by a banked decision recorded
in `reviews/` after zero consumers remain (grep the artifact
manifests); "a newer era exists" never implies "the old one retired."

**L6 — Guards (fast tier).** `tests/test_zone_eras.py` guards every
`zone-<kind>-<zone>-<era>.json`: filename era == first 8 hex of
`anchoring.source_sha256_lf`; anchoring block complete; schema loads;
the palette instance re-derives byte-equal from pinned game bytes
(loud skip when `../game-two` is absent); and the two grandfathered
files still hash to the shas the v31/v32 artifact manifests pin —
redundant with the push-tier artifact checks BY DESIGN (a ~seconds
fast-tier early warning vs the 3-4 h push gate).

**L7 — Scope: zone-MAP eras are deferred.** A map era for the new
zone content needs glyph-semantics derivation (live census
`# , . g w ~`; the current `load_zone_map` accepts only `.`/`#`) and a
loader extension. Both are DEFERRED to the first lane that consumes a
new-era map; that lane pre-registers its own derivation protocol and
owns the track_recompose.py fan-out consequence (L4). Until then,
scene builds keep consuming the frozen v32-era map.

**L8 — Generalization.** L1/L3/L5 govern EVERY anchored derived
manifest in `manifests/`, not only zone-derived ones — proven live
this sprint: `scene-reference.json` (renderer-derived, byte-pinned by
the v32 artifact manifest) still carried a live-equality guard; the
first renderer content drift after v32 (game `81cf358`, a text-fallback
noun rename) re-exposed the catch-22, and the guard was retargeted to
its frozen content pin under the same law. L2 naming binds only
zone-derived manifests; new derived manifests of other kinds SHOULD
adopt an era suffix from birth (that adoption call rides the lane that
creates them).

## What this means for you

When upstream rethemes a zone (or ships `district_two`): run the gate,
route the baseline re-pin by the standing drift protocol, then derive
a NEW `zone-<kind>-<zone>-<era>.json` by temp script from the pinned
bytes — commit it beside the old era. Touch nothing banked: the old
era files and every artifact that pins them stay byte-frozen, green,
and re-provable. Cost: one derivation, zero emergencies.

</law-draft>

## Derivation protocol — palette era instance (pre-registered)

P1. Precondition: drift routed, asset_gate exit 0; runtime-baseline pins
    game_commit G; read the district source sha S (source_files entry
    `data/zones/district.json`, sha256_lf) from the baseline.
P2. `git -C ../game-two show G:data/zones/district.json` → bytes B
    (GIT_* env scrubbed); assert sha256_lf(B) == S; parse JSON.
P3. era = S[:8]. Target `manifests/zone-palette-district-<era>.json`;
    assert the path does NOT exist (immutability; a collision with
    identical content is a no-op stop, never an overwrite).
P4. Compose (temp script, deleted at close; json indent=2, source key
    order preserved, LF newlines, trailing newline):
    contract_version 1; purpose (UNCONSUMED until a lane pins it; names
    the expected consumer class); derived_at 2026-08-29; anchoring
    {game_commit: G, source_file, source_sha256_lf: S, binding note
    (content, never live pin — project MEMORY 2026-08-29),
    value_citations: one per palette key (14 keys, each
    "data/zones/district.json palette.<key>"), registration: this
    file}; zones.district = the source palette dict VERBATIM (all 14
    keys, values and order exactly as pinned bytes parse).
P5. Double-derive: run the script twice into two temp paths;
    byte-compare; install only on identical bytes.
P6. Record the installed file's raw sha256 in the verdict — the pin a
    future consumer cites.

## Guard module (pre-registered shape)

`tests/test_zone_eras.py`, fast tier (new modules default in):
- every `manifests/zone-<kind>-<zone>-<era>.json` (era = 8, or 12 on
  the law's collision escalation, lowercase hex): filename era ==
  prefix of anchoring.source_sha256_lf; anchoring block complete
  (game_commit, source_file, source_sha256_lf, value_citations);
  schema shape loads (contract_version, purpose, derived_at, zones for
  palette kind, one zone entry matching the filename zone).
- palette era instances: values re-derive byte-equal from
  `git -C ../game-two show <anchoring.game_commit>:<source_file>`
  (sha256_lf of shown bytes asserted == anchoring.source_sha256_lf
  first; GIT_* scrubbed; LOUD skip naming the reason when ../game-two
  is absent — the test_asset_gate live-test pattern; no mocks, Rule 3);
  every palette key carries a value_citation.
- grandfather assertions: `zone-map-district.json` hashes (raw sha256)
  to `b9843cbd…` and `zone-palette-district.json` to `ee2d185a…` — the
  exact pins the v31/v32 artifact manifests carry; redundant with the
  push-tier artifact checks BY DESIGN (fast-tier early warning vs the
  3-4 h push gate).

## Pass bars (fixed; any INTEGRITY red stops, Rule 6)

INTEGRITY: commit A precedes any law/instance/guard bytes; asset_gate
exit 0 post-routing AND immediately before commit C; pin_drift routed
by class at every drift; five standing checks exit 0 at banking
(track_recompose / pose_integrity_metrics / remedy_metrics /
adoption_demo / exports_guard, each `--check` via .venv python); the
two frozen zone manifests byte-identical to their v31/v32 pins (sha
shown in the verdict); era instance re-derivable byte-identical
(double-derive); zero pixels, zero exports, zero writes into
../game-two, zero tools/ edits; ambient dirty state untouched;
explicit-path staging, staged list verified before every commit (plain
`git commit`, never pathspec-limited); temp scripts under explicit
C:/Users/gabri/AppData/Local/Temp/ paths, deleted at close; repo files
written with LF newlines; PYTHONIOENCODING=utf-8 for Unicode printing.

QUALITY (blocking): the law doc passes a human-facing-output pass
(answer-first; the 005eab3 retheme as worked example; a "what this
means for you" close); verdict claims each carry the proving command +
captured output; council reconciled with adoptions named; cadence table
cites a source for every number — no interpolation.

## Cadence-carry table (sources named; UNAVAILABLE-AT-SPARK is a
banked value, never interpolated)

| item | real | source |
|---|---|---|
| v32 commit D (verdict) hook | UNAVAILABLE-AT-SPARK | rides the v32 session receipt in the hub; not carried in the v33 spark |
| v32 push (full gauntlet) | UNAVAILABLE-AT-SPARK | same carrier |
| d7294e9 fast-gate hook | UNTIMED | named gap in the v33 spark (authoring session did not wrap it) |
| d7294e9 push (full gauntlet) | 3h37m wall (launched 04:52, marker `exit=0 Sat Aug 29 08:29:06`) | log ctime + `.done` marker, harvested this session before deletion; suite-stage split UNAVAILABLE - the log carries only the warn stream + push confirmation (verified by grep: no Ran/timing lines) |
| v33 chore re-pin commit hook | 3m56.5s real (commit 5122238) | this session, `time git commit` |
| v33 commit A hook | banked in the verdict (this file commits first) | same |
| v33 commit B hook | banked in the verdict (this file commits first) | same |
| v33 commit C hook | banked in the verdict (this file commits first) | same |

## Council registration

One consolidated `council ask` (kimi-k2.5; a first attempt on
kimi-k2-thinking died at the Bedrock endpoint with 0 tokens consumed —
transport failure, not a consult), brief inlining the FULL law draft +
both frozen anchoring blocks + the live census/transition facts; six
assigned attacks (next-retheme walk, district_two walk, residual live
coupling, era-id scheme, unconsumed-instance value, deferred-map risk,
biggest unthought risk). Measured 3534 in + 3340 out tokens (<= 8k
budget). Every REFUTED claim re-verified against primary bytes before
adoption (v18 precedent); reconciliation appendix in the verdict.
