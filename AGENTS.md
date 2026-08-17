# game-two-assets

Source/studio repo for `../game-two` visual assets: research, concepts, native sources, provenance, deterministic exports, and reviews. It is **never** a runtime dependency, submodule, or automatic fetch target. While game-two v17 is open, do not modify or integrate with the game repo.

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

- Touch `../game-two` during v17 asset exploration.
- Build a full pack before one calibration lane wins.
- Imitate a named living artist or store unlicensed references.
- Call a Bedrock/general-model output a production sprite.
- Rebank game canaries or alter runtime colors to rescue an asset.
- Commit credentials or exports without a valid release manifest.

## Pointers and enforcement

- `docs/asset-contract.md` — export/release law
- `docs/sprint-0.md` — bounded first calibration
- `manifests/runtime-baseline.json` / `toolchain-baseline.json` — compatibility pins
- Hooks are untracked: pre-commit runs swarmforge `--changed`; pre-push preserves Git LFS then runs `--full`. Reinstall from the quality-gauntlet recipe.
