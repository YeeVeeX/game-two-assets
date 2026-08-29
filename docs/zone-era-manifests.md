# Zone-era manifests — how zone-derived manifests are named, anchored, guarded, and superseded

**The law in one line:** a zone-derived manifest is immutable once
banked; consumers pin its path + sha256; when upstream zone content
changes, you derive a NEW era file beside the old one — you never
regenerate in place.

Ratified 2026-08-29 (v33; pre-registered in
`reviews/zone-era-v33/rationale.md`, council-reviewed, reconciliation
in `reviews/zone-era-v33/verdict.md`). Subordinate to
`docs/asset-contract.md`.

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
`manifests/zone-<kind>-<zone>-<era>.json` (kind: `palette`, `map`, …;
zone: the game's own zone id verbatim — these are generic/mechanical
ids per repo invariant 5, e.g. `district`, `district_two`). Example:
the rethemed district palette derives from district.json content
`2eb1723d…` → `zone-palette-district-2eb1723d.json`.

Era identity IS content identity: the same source content derived at
any two game commits produces the same filename, so identity-only
upstream churn can never mint duplicate eras (date- or commit-suffixed
schemes break exactly there, and a commit suffix additionally dies on
upstream rebases). 8 hex is the repo's standing citation width for
these shas (`9774cdd0…`, `2eb1723d…` in commits, memory, and reviews).
Prefix collision inside one `<kind>-<zone>` family (32-bit space, a
handful of eras per family lifetime): the NEW file takes the first 12
hex instead; existing files never rename.

Reading an era id: the era is deliberately content-addressed, not
chronological — `derived_at` and `anchoring.game_commit` inside the
file carry the human timeline
(`python -c "import json; a=json.load(open(PATH)); print(a['derived_at'], a['anchoring']['game_commit'])"`),
and `git log --diff-filter=A -- <path>` dates its banking.

Grandfather: `zone-map-district.json` and `zone-palette-district.json`
(v32-era, source `9774cdd0…`) keep their legacy unsuffixed names;
guards pin them frozen.

**L3 — Anchoring binds to content, never to the live pin.** Every era
file carries an `anchoring` block: `game_commit` (a game-two commit
whose committed source_file content hashes LF to source_sha256_lf —
recorded from the runtime-baseline pin at derivation; the
re-derivation handle), `source_file`, `source_sha256_lf`
(LF-normalized sha256 of the source blob — the BINDING identity), and
per-field `value_citations`. Guards assert the frozen sha constants
recorded in the manifest — NEVER equality with the live
runtime-baseline pin, which moves with upstream development (project
MEMORY 2026-08-29; d7294e9 is the precedent). Identity-only baseline
re-pins never invalidate an era.

**L4 — No permanent deriver tool.** Eras are derived by a TEMP script
(run, deleted): values copied VERBATIM from pinned game bytes
(`git -C ../game-two show <game_commit>:<source_file>`), citations per
field, double-derive byte-identical before banking. The deriving
sprint's rationale pre-registers the protocol AND fixes the era
schema verbatim BEFORE the instance exists, and the sprint rides the
house ship-gates. The unpinned-tool census does not grow (v24 census:
exports_guard, checkout_gate, pin_drift in tools/, fast_gate in bin/).
Rationale: editing a pinned permanent tool moves its sha into every
consumer manifest — track_recompose.py's sha rides SIX banked
manifests, each regenerated only by its own --make flag (the v32
verdict documents the mechanism).

**L5 — Supersession.** A new era never edits or retires an old one.
Consumers migrate by pinning the new path + sha in their OWN
manifests. An UNCONSUMED era declares its expected consumer class in
its `purpose` field, and its guard (L6) is its standing consumer until
a lane pins it. An era file is deleted only by a banked decision
recorded in `reviews/` after zero consumers remain (grep the artifact
manifests); "a newer era exists" never implies "the old one retired."

**L6 — Guards (fast tier).** `tests/test_zone_eras.py` guards every
`zone-<kind>-<zone>-<era>.json`: filename era == prefix of
`anchoring.source_sha256_lf`; anchoring block complete; schema shape
loads; palette instances re-derive VALUE-BY-VALUE byte-equal from
pinned game bytes on every fast-gate run (loud skip when `../game-two`
is absent); and the two grandfathered files still hash to the shas the
v31/v32 artifact manifests pin — redundant with the push-tier artifact
checks BY DESIGN (a ~seconds fast-tier early warning vs the 3-4 h push
gate).

**L7 — Scope: zone-MAP eras are deferred, with the dependency chain
named.** A map era for the new zone content is BLOCKED-ON, in order:
(1) glyph-semantics derivation — the meaning of every census glyph
(`# , . g w ~`) copied from PINNED game loader/renderer bytes with a
per-glyph citation, never from visual interpretation; (2) any game
source file those citations name that is not already in the
runtime-baseline pin set joins it (so later semantics drift gates like
any other pinned-file drift); (3) a `load_zone_map` extension (the
loader today accepts only `.`/`#`) plus draw conventions for the typed
transitions (`stairs_up`, `hole`). All three are owned by the FIRST
lane that consumes a new-era map; that lane pre-registers its own
derivation protocol and owns the track_recompose.py fan-out
consequence (L4). Until then, scene builds keep consuming the frozen
v32-era map.

**L8 — Generalization.** L1/L3/L5 govern EVERY anchored derived
manifest in `manifests/`, not only zone-derived ones — proven live
this sprint: `scene-reference.json` (renderer-derived, byte-pinned by
the v32 artifact manifest) still carried a live-equality guard; the
first renderer content drift after v32 (game `81cf358`, a
text-fallback noun rename) re-exposed the catch-22, and the guard was
retargeted to its frozen content pin under the same law. L2 naming
binds only zone-derived manifests; new derived manifests of other
kinds SHOULD adopt an era suffix from birth (that adoption call rides
the lane that creates them).

## What this means for you

When upstream rethemes a zone (or ships `district_two`): run the gate,
route the baseline re-pin by the standing drift protocol, then derive
a NEW `zone-<kind>-<zone>-<era>.json` by temp script from the pinned
bytes — commit it beside the old era. Touch nothing banked: the old
era files and every artifact that pins them stay byte-frozen, green,
and re-provable. Cost: one derivation, zero emergencies.
