# game-two-assets

Visual-asset source studio for the sibling `game-two` project. This repo isolates art-direction experiments from the still-open v17 deterministic multiplayer cycle.

**Status:** sprint 0 only. No asset here is approved for runtime use, and no integration may begin before the game-two v17 fun verdict closes.

## Boundary

This is not a submodule or dependency. The future flow is deliberately one-way:

1. author/reconstruct native source here;
2. export deterministically;
3. pass the technical asset gate;
4. capture a contact sheet over real game palettes;
5. bank visual and provenance verdicts;
6. copy only the approved PNG and its release manifest in a separate game-two change.

That explicit copy preserves game-two build identity and makes every imported byte reviewable.

## Layout

- `concepts/` — large exploratory references; Git LFS; never runtime-ready
- `sources/` — native Aseprite/source files; Git LFS for binaries
- `exports/` — deterministic native PNGs and release manifests
- `manifests/` — runtime/toolchain compatibility pins and shared metadata
- `reviews/` — contact sheets and blocking visual verdicts
- `tools/` / `tests/` — deterministic export validation
- `docs/asset-contract.md` — technical and provenance contract
- `docs/sprint-0.md` — first bounded art-direction calibration

## Setup and verification

```bash
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe tools/asset_gate.py --game-root ../game-two --aseprite C:/tools/aseprite/build/bin/aseprite.exe
swarmforge gauntlet --full --repo .
```

Aseprite is available at `C:/tools/aseprite/build/bin/aseprite.exe`.

## Current runtime baseline

- 960x540 view
- 32x32 square tiles
- 32x32 creature canvases with pixels bounded to the current 28x28 body footprint
- RGBA8 exports, hard alpha, nearest-neighbor display
- generic labels only; no lore or fiction names

General image models may produce concept references, but not production pixel art. Native candidates must be authored or reconstructed on the actual pixel grid, palette-declared, and hash-verified.

Private project: no redistribution license is granted for repository contents unless a file says otherwise.
