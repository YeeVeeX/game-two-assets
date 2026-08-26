# game-two-assets

Source/studio repo for `../game-two` visual assets: research, concepts, native sources, provenance, deterministic exports, and reviews. It is **never** a runtime dependency, submodule, or automatic fetch target. Integration with the game repo stays OUT of scope until game-two's hub lifts its parking-lot gate (assets integration gated on pipeline maturity) — never modify or integrate from this side.

<!-- FAMILY-BLOCK BEGIN -->
## Workspace family (game-two program) — synced 2026-08-24

- **Peers:** Gabriel (owner-founder, es-CR) + Junior (co-creator,
  pt-br) co-direct the whole program with equal creative standing —
  design, code, audio/assets, ideas flow from BOTH; neither is the
  other's worker. Owner overrides are law and get RECORDED (one line)
  in the affected repo.
- **Never gate on peer availability (owner order 2026-08-22):** solo
  progress is the default in every repo — peer online = good, absent =
  keep moving, symmetric both ways; the dev of record proactively
  surfaces REAL recorded work items (never fabricated ones). Peer
  ratifications land async in the hub chat.
- **Hub-and-spoke:** the game-two dev chat is the HUB; work in this
  repo runs as bounded sessions under its own dev-of-record.
  Cross-repo asks travel by SEAT MAIL (`~/.pi/agent/mail/<repo>/`),
  digest-stamped (md5), answered with `RECEIPT:` lines. Deliveries
  INTO game-two obey game-two's intake rules (owner-approved +
  digest-grounded + docs-only banking).
- **Seat-lease law:** no session ever writes into a sibling workspace
  tree — read tool for reading, mail for asking, md5 as the
  byte-identity arbiter.
- **Service seats:** game-two-audio (audio increments on owner word) ·
  game-two-uiux (UI/UX spec/prototype/critique service + research
  lanes; owner-ordered genesis 2026-08-24, charter = its AGENTS.md,
  git-blob md5 `6ddeb63023b3884961f241a2091ed366`). Service seats
  never fork this repo's lanes — integration lands only through this
  seat, under this repo's gates; critique passes arrive by mail as
  take-or-leave evidence.
- **Sovereignty:** this block never overrides local law — this repo's
  own invariants win inside this repo.
- **Contract mirror:** AGENTS.md is ground truth; CLAUDE.md is a thin
  pointer to it so Claude sessions load the same contract (AGENTS.md
  wins on any disagreement).
<!-- FAMILY-BLOCK END -->

## Commands

- Setup: `py -3.12 -m venv .venv` then `.venv/Scripts/python.exe -m pip install -r requirements-dev.txt`
- Test: `.venv/Scripts/python.exe -m unittest discover -s tests -v`
- Asset gate: `.venv/Scripts/python.exe tools/asset_gate.py`
- Verify live pins: `.venv/Scripts/python.exe tools/asset_gate.py --game-root ../game-two --aseprite C:/tools/aseprite/build/bin/aseprite.exe`
- Full gate: `swarmforge gauntlet --full --repo .`
- Aseprite: `C:/tools/aseprite/build/bin/aseprite.exe`

## Architectural invariants

1. **One-way boundary.** A later game-two change may copy an approved PNG plus manifest; never symlink, package, fetch, or resolve “latest.”
2. **Contract first.** Phase-0 PNGs are native 32x32 RGBA8 with hard alpha. Creature pixels stay in `[2,2,29,29]`, anchored at `[16,30]`. See `docs/asset-contract.md`.
3. **Pinned identity.** Releases record full source/game commits and SHA-256 for every source/export. Cross-platform text baselines hash LF-normalized bytes.
4. **Provenance blocks release.** Generated references record provider/model/date/prompt/seed/terms/edits. General models produce concepts only; sprites are authored or reconstructed at native resolution.
5. **No lore.** Use generic/mechanical IDs (`player_1`, `human_1`, `zone_1`). No fiction names, narrative, dialogue, or worldbuilding.
6. **Visual proof.** Selection requires a scripted contact sheet over real palettes, native-scale inspection, and saved accuracy/presentation verdicts.

## Human-facing surfaces

Assets, contact sheets, review docs, and README target the owner and future contributors. Use concise technical art direction and generic labels. Generated-media provenance belongs in manifests; preserve provider markings where available. Visual capture + critique is a blocking ship-gate.

## Never

- Touch `../game-two` from this repo — the hub's parking-lot gate governs integration sequencing (one-way boundary).
- Build a full pack before one calibration lane wins.
- Imitate a named living artist or store unlicensed references.
- Call a Bedrock/general-model output a production sprite.
- Rebank game canaries or alter runtime colors to rescue an asset.
- Commit credentials or exports without a valid release manifest.

## Pointers and enforcement

- `docs/asset-contract.md` — export/release law
- `docs/research/2d-asset-playbooks/` — external 2D/GenAI research corpus (subordinate to the contract; trust notes in its README)
- `.agents/skills/concept-research/` — concept-stage generation + critique workflow (auto-discovered by pi)
- `docs/sprint-0.md` — bounded first calibration
- `manifests/runtime-baseline.json` / `toolchain-baseline.json` — compatibility pins
- Hooks are untracked: pre-commit runs swarmforge `--changed`; pre-push preserves Git LFS then runs `--full`. Reinstall from the quality-gauntlet recipe.
