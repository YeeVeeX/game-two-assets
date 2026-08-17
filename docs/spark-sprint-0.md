Work in `C:/Users/gabri/workspace/game-two-assets` on the first bounded visual-asset calibration for game-two.

Read, in order:
1. `C:/Users/gabri/workspace/game-two-assets/AGENTS.md`
2. `README.md`
3. `docs/asset-contract.md`
4. `docs/sprint-0.md`
5. `manifests/runtime-baseline.json`
6. `C:/Users/gabri/workspace/game-two/AGENTS.md` only for live game constraints

Mission: complete sprint 0's three-lane silhouette calibration while Junior is unavailable. This work must be fully independent of multiplayer and must not modify `game-two` at all.

Before implementation, name the three biggest risks/wrong assumptions and state one recommended approach. Then execute end-to-end without asking design permission unless a genuinely irreversible new risk appears.

Hard boundaries:
- no lore, fiction names, dialogue, named places, or narrative art briefs;
- no runtime integration, symlink, submodule, fetch, or edit in `../game-two`;
- no deterministic canary changes or rebanking;
- Bedrock/general image models are concept-reference tools only, never production sprite tools;
- use generic IDs such as `player_1_lane_a`;
- do not create a full pack: stop after one reviewed calibration contact sheet;
- do not contact or poll Junior/WhatsApp.

Ground the work first:
- query the curated shelf with `hub kb query --domain game-research` for top-down 32x32 silhouette readability, palette discipline, Aseprite export, and pixel-art reconstruction;
- use the current game renderer and `../game-two/docs/assets/gameplay.png` as the runtime baseline;
- cite functional principles from Tibia grid-readability research and Vlambeer feedback research, without copying reference art or imitating a named living artist;
- verify the runtime and toolchain pins with `.venv/Scripts/python.exe tools/asset_gate.py --game-root ../game-two --aseprite C:/tools/aseprite/build/bin/aseprite.exe`.

Deliver exactly this bounded change set:
1. A concise `reviews/calibration-v0/rationale.md` defining lanes A/B/C from `docs/sprint-0.md` and the prediction each lane tests.
2. Native Aseprite sources for one generic body in idle-down and idle-right for each lane. If concept generation helps, use the `bedrock-image-gen` skill, retain exact provenance, and manually reconstruct at 32x32.
3. Deterministic Aseprite export tooling; no hand-export-only workflow.
4. Six native 32x32 RGBA8 PNGs under `exports/calibration-v0/`, hard alpha, at most eight declared opaque colors, all pixels within the current creature bounds.
5. A valid `exports/calibration-v0/release.json` with full source/export hashes and provenance.
6. A scripted contact sheet over exact ZONE 1 and ZONE 2 palette samples: native 1x rows decide readability; nearest-neighbor 2x/4x rows diagnose pixels. Include the current primitive body as baseline.
7. `reviews/calibration-v0/verdict.md` with separate accuracy and presentation scores, structured vision critique, and one cross-vendor taste review. Choose one lane only if it is a genuine improvement; otherwise reject all and state one next hypothesis.
8. Tests for every new deterministic tool or validator behavior.

Verification is blocking:
- `.venv/Scripts/python.exe -m unittest discover -s tests -v`
- `.venv/Scripts/python.exe tools/asset_gate.py --game-root ../game-two --aseprite C:/tools/aseprite/build/bin/aseprite.exe`
- `swarmforge gauntlet --full --repo .`
- scripted contact-sheet regeneration produces the same SHA-256 twice
- visual critique passes both technical accuracy and presentation; a failed critique blocks completion

Budget and stop condition: one asset cycle, at most three visual lanes and one contact sheet; any council use is capped at 8k total tokens and one consolidated verdict. Stop after banking the sprint-0 verdict. Do not integrate the winner into game-two.
