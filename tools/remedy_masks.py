#!/usr/bin/env python3
"""Machine-derive the k0 gape masks and the six DEF-1 remedy variant specs.

Sprint v15 (reviews/remedy-v15/rationale.md). The v14 register resolved the
owner's sighting to DEF-1: the k0 strike key paints its jaw-gape marker in
the frozen ramp accent #140e0c at 1.09:1 / 1.16:1 WCAG contrast against the
pinned zone floors. This tool derives — mechanically, no hand-picked
rectangles — the gape mask per facing from BANKED bytes:

    gape = k0 accent pixels
           MINUS the v2-banked translated idle eye pixels
           MINUS the feet caps (row 27)

where the eye translation is the v2-banked rigid head shift (down (0,+2),
right (0,+3); "dome and eye rows are byte-exact copies at the declared
shifts" — reviews/calibration-v2/verdict.md). The derivation asserts the
translated eye set is a subset of the k0 accent set and that the derived
masks match the v14 expectations exactly (16 px down, 8 px right).

Variant specs are derived from the banked k0 export bytes (PNG -> grid ->
masked recolor -> spec JSON), one per lane per facing:

- ks: gape -> shade #8c3818 (primary candidate)
- ko: gape -> outline #401c10 (bracketing control, expected to fail the
  aperture line)
- kr: two-tone (row 13 -> shade, row 14 -> outline; both derived bands span
  exactly rows 13-14) — mouth-with-depth, the lit interior kept against the
  eyes

Alpha is untouched by construction (recolor only); every color stays inside
the frozen 5-color ramp. ``--make-release`` emits the gate-schema release
manifest for exports/remedy-v15 under the same honesty rule as the banked
tools/make_release.py (which stays byte-frozen: its registry is pinned by
banked releases). ``--check`` verifies the committed masks and specs
regenerate byte-identically. Banked modules are imported unmodified.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from anticipation_metrics import ACCENT_RGB  # noqa: E402  (banked)
from asset_gate import sha256_file  # noqa: E402  (banked)
from make_seam_timeline import (  # noqa: E402  (banked pose IO)
    POSE_DIRS,
    default_dirs,
    pose_filename,
)
from pixel_spec import load_spec  # noqa: E402  (banked contract law)
from png_reader import read_rgba  # noqa: E402  (banked)

CANVAS = 32
FACINGS = ("down", "right")
FEET_ROW = 27
# The v2-banked rigid head translations (idle -> k0), cited not fitted:
# "dome and eye rows are byte-exact copies at the declared shifts"
# (reviews/calibration-v2/verdict.md; machine-verified there in tests).
EYE_SHIFTS = {"down": (0, 2), "right": (0, 3)}
# v14 expectations the derivation must reproduce exactly.
EXPECTED_GAPE_PX = {"down": 16, "right": 8}
EXPECTED_GAPE_BBOX = {"down": [12, 13, 19, 14], "right": [24, 13, 27, 14]}

# The frozen 5-color ramp, banked spec key convention (calibration-v0..v7).
RAMP = {
    "k": "#140e0c",  # accent (eyes, feet caps, incumbent gape)
    "o": "#401c10",  # outline
    "s": "#8c3818",  # shade
    "b": "#eb7828",  # body
    "h": "#ffa050",  # highlight
}
RGB_TO_KEY = {
    (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)): key
    for key, color in RAMP.items()
}
SHADE = RAMP["s"]
OUTLINE = RAMP["o"]

LANES = ("ks", "ko", "kr")
# kr split rule (total over both derived bands, rows 13-14): the lit
# interior stays against the eyes, the jaw-line shadow at the bottom rim.
KR_SPLIT = {13: SHADE, 14: OUTLINE}

RELEASE_ID = "remedy-v15"
REVIEW_DIR = ROOT / "reviews" / RELEASE_ID
MASKS_PATH = REVIEW_DIR / "gape-masks.json"
SOURCE_DIR = ROOT / "sources" / RELEASE_ID
SPEC_DIR = SOURCE_DIR / "specs"
EXPORT_DIR = ROOT / "exports" / RELEASE_ID
EXPORTER = "tools/export_assets.py"

LANE_NOTES = {
    "ks": (
        "lane K-S (primary candidate): gape recolored to shade #8c3818 "
        "(measured 2.26:1 / 2.12:1 WCAG vs the pinned zone_1/zone_2 floors; "
        "2.69:1 vs the body)"
    ),
    "ko": (
        "lane K-O (bracketing control, pre-registered as expected to fail "
        "the aperture line): gape recolored to outline #401c10 (measured "
        "1.17:1 / 1.10:1 WCAG vs the pinned zone floors)"
    ),
    "kr": (
        "lane K-R (two-tone redesign, mouth-with-depth): gape row 13 "
        "recolored to shade #8c3818, row 14 to outline #401c10 - the lit "
        "interior kept adjacent to the eyes (accent-vs-shade 2.45:1), the "
        "jaw-line shadow at the bottom rim"
    ),
}


class RemedyMaskError(ValueError):
    """A deterministic derivation or release failure."""


# -- banked-byte access -----------------------------------------------------------


def load_banked_raw(dirs: dict[str, Path], pose: str, facing: str) -> bytes:
    path = dirs[POSE_DIRS[pose]] / pose_filename(pose, facing)
    width, height, raw = read_rgba(path)
    if (width, height) != (CANVAS, CANVAS):
        raise RemedyMaskError(f"{path.name}: expected {CANVAS}x{CANVAS}")
    return raw


def accent_cells(raw: bytes) -> set[tuple[int, int]]:
    cells = set()
    for y in range(CANVAS):
        for x in range(CANVAS):
            offset = (y * CANVAS + x) * 4
            if raw[offset + 3] == 255 and (
                raw[offset], raw[offset + 1], raw[offset + 2]
            ) == ACCENT_RGB:
                cells.add((x, y))
    return cells


def cells_bbox(cells: set[tuple[int, int]]) -> list[int]:
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    return [min(xs), min(ys), max(xs), max(ys)]


# -- mask derivation ---------------------------------------------------------------


def derive_mask(dirs: dict[str, Path], facing: str) -> dict:
    """The pre-registered derivation, with its assertions."""
    idle_accent = accent_cells(load_banked_raw(dirs, "idle", facing))
    k0_accent = accent_cells(load_banked_raw(dirs, "k0", facing))
    idle_eyes = {cell for cell in idle_accent if cell[1] != FEET_ROW}
    dx, dy = EYE_SHIFTS[facing]
    translated_eyes = {(x + dx, y + dy) for x, y in idle_eyes}
    if not translated_eyes <= k0_accent:
        raise RemedyMaskError(
            f"{facing}: translated idle eyes are not a subset of the k0 "
            "accent set - the v2-banked rigid-head premise does not hold"
        )
    feet = {cell for cell in k0_accent if cell[1] == FEET_ROW}
    gape = k0_accent - translated_eyes - feet
    if len(gape) != EXPECTED_GAPE_PX[facing]:
        raise RemedyMaskError(
            f"{facing}: derived gape {len(gape)} px != v14 expectation "
            f"{EXPECTED_GAPE_PX[facing]}"
        )
    if cells_bbox(gape) != EXPECTED_GAPE_BBOX[facing]:
        raise RemedyMaskError(
            f"{facing}: derived gape bbox {cells_bbox(gape)} != v14 "
            f"expectation {EXPECTED_GAPE_BBOX[facing]}"
        )
    rows = sorted({y for _, y in gape})
    if any(y not in KR_SPLIT for y in rows):
        raise RemedyMaskError(
            f"{facing}: gape rows {rows} escape the declared kr split rows "
            f"{sorted(KR_SPLIT)}"
        )
    return {
        "eye_translation": list(EYE_SHIFTS[facing]),
        "idle_eye_pixels": [list(c) for c in sorted(idle_eyes)],
        "translated_eye_pixels": [list(c) for c in sorted(translated_eyes)],
        "feet_pixels": [list(c) for c in sorted(feet)],
        "gape_pixels": [list(c) for c in sorted(gape)],
        "gape_px": len(gape),
        "gape_bbox": cells_bbox(gape),
        "k0_accent_px": len(k0_accent),
        "idle_accent_px": len(idle_accent),
    }


def masks_payload(dirs: dict[str, Path]) -> dict:
    return {
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tools/remedy_masks.py --make-masks",
            "statement": (
                "machine-derived measurement over banked export bytes; the "
                "pre-registered mask definition of "
                "reviews/remedy-v15/rationale.md; adjudicates nothing"
            ),
        },
        "definition": (
            "gape = k0 accent pixels MINUS the v2-banked translated idle eye "
            "pixels MINUS the feet caps (row 27); eye translation = the "
            "v2-banked rigid head shift (down (0,+2), right (0,+3))"
        ),
        "accent_rgb": list(ACCENT_RGB),
        "feet_row": FEET_ROW,
        "facings": {facing: derive_mask(dirs, facing) for facing in FACINGS},
    }


def masks_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")


# -- variant recolor maps + specs ---------------------------------------------------


def gape_cells(payload: dict, facing: str) -> list[tuple[int, int]]:
    return [tuple(c) for c in payload["facings"][facing]["gape_pixels"]]


def recolor_map(payload: dict, facing: str, lane: str) -> dict[tuple[int, int], str]:
    """(x, y) -> new #rrggbb over exactly the declared diff set."""
    cells = gape_cells(payload, facing)
    if lane == "ks":
        return {cell: SHADE for cell in cells}
    if lane == "ko":
        return {cell: OUTLINE for cell in cells}
    if lane == "kr":
        return {cell: KR_SPLIT[cell[1]] for cell in cells}
    raise RemedyMaskError(f"unknown lane {lane!r}")


def variant_asset_id(facing: str, lane: str) -> str:
    return f"player_1_lane_b_attack_{facing}_k0_{lane}"


def variant_spec(dirs: dict[str, Path], payload: dict, facing: str, lane: str) -> dict:
    """Banked k0 export bytes -> grid -> masked recolor -> spec object."""
    raw = load_banked_raw(dirs, "k0", facing)
    recolor = recolor_map(payload, facing, lane)
    grid_rows = []
    for y in range(CANVAS):
        row = ""
        for x in range(CANVAS):
            offset = (y * CANVAS + x) * 4
            if raw[offset + 3] != 255:
                if (x, y) in recolor:
                    raise RemedyMaskError(
                        f"{facing}/{lane}: recolor target ({x},{y}) is "
                        "transparent in the banked k0"
                    )
                row += "."
                continue
            if (x, y) in recolor:
                color = recolor[(x, y)]
                rgb = (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
            else:
                rgb = (raw[offset], raw[offset + 1], raw[offset + 2])
            key = RGB_TO_KEY.get(rgb)
            if key is None:
                raise RemedyMaskError(
                    f"{facing}/{lane}: pixel ({x},{y}) color {rgb} is outside "
                    "the frozen ramp"
                )
            row += key
        grid_rows.append(row)
    used = {char for row in grid_rows for char in row if char != "."}
    return {
        "asset_id": variant_asset_id(facing, lane),
        "kind": "creature",
        "anchor": [16, 30],
        "palette": {key: RAMP[key] for key in sorted(used)},
        "grid": grid_rows,
    }


def spec_bytes(spec: dict) -> bytes:
    ordered = {
        "asset_id": spec["asset_id"],
        "kind": spec["kind"],
        "anchor": spec["anchor"],
        "palette": dict(sorted(spec["palette"].items())),
        "grid": spec["grid"],
    }
    return (json.dumps(ordered, indent=2) + "\n").encode("ascii")


def all_specs(dirs: dict[str, Path], payload: dict) -> dict[str, dict]:
    return {
        variant_asset_id(facing, lane): variant_spec(dirs, payload, facing, lane)
        for facing in FACINGS
        for lane in LANES
    }


# -- release manifest (gate schema; the banked make_release.py stays frozen) --------


def _git_env() -> dict[str, str]:
    """Scrub hook-injected git overrides (the banked make_release pattern)."""
    env = dict(os.environ)
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(key, None)
    return env


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True, capture_output=True, text=True, env=_git_env(),
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RemedyMaskError(f"git failed: {exc}") from exc


def source_commit(root: Path) -> str:
    """HEAD, required to have sources/, tools/, manifests/ committed clean
    (the banked honesty rule: a manifest may not lie about provenance)."""
    head = _git(root, "rev-parse", "HEAD")
    dirty = _git(root, "status", "--porcelain", "--", "sources", "tools", "manifests")
    if dirty:
        raise RemedyMaskError(
            "sources/, tools/, or manifests/ differ from HEAD; commit them "
            "first:\n" + dirty
        )
    return head


def game_commit(root: Path) -> str:
    baseline = json.loads(
        (root / "manifests" / "runtime-baseline.json").read_text(encoding="utf-8")
    )
    return baseline["game_commit"]


def provenance_note(payload: dict, root: Path, facing: str, lane: str) -> str:
    facts = payload["facings"][facing]
    banked = (
        root / "exports" / "calibration-v2"
        / f"player_1_lane_b_attack_{facing}_k0.png"
    )
    return (
        f"DEF-1 remedy candidate, {LANE_NOTES[lane]}; source bytes: the "
        f"banked calibration-v2 {facing} k0 export "
        f"(sha256 {sha256_file(banked)[:16]}...), recolored at exactly the "
        f"{facts['gape_px']}px machine-derived gape mask "
        f"{facts['gape_bbox']} (reviews/remedy-v15/gape-masks.json); alpha "
        "byte-identical to the banked k0 - silhouette-invariant by "
        "construction; selection adjudicated in reviews/remedy-v15/verdict.md"
    )


def build_release_manifest(root: Path, commit: str, payload: dict) -> dict:
    source_files = []
    exports = []
    for facing in FACINGS:
        for lane in LANES:
            asset_id = variant_asset_id(facing, lane)
            spec_path = SPEC_DIR / f"{asset_id}.json"
            ase_path = SOURCE_DIR / f"{asset_id}.aseprite"
            png_path = EXPORT_DIR / f"{asset_id}.png"
            for path in (spec_path, ase_path, png_path):
                if not path.is_file():
                    raise RemedyMaskError(f"missing {path}")
            spec = load_spec(spec_path)  # banked contract law re-applied
            source_files.append(
                {"path": f"sources/{RELEASE_ID}/specs/{asset_id}.json",
                 "sha256": sha256_file(spec_path)}
            )
            source_files.append(
                {"path": f"sources/{RELEASE_ID}/{asset_id}.aseprite",
                 "sha256": sha256_file(ase_path)}
            )
            exports.append(
                {
                    "asset_id": asset_id,
                    "kind": "creature",
                    "path": f"exports/{RELEASE_ID}/{asset_id}.png",
                    "sha256": sha256_file(png_path),
                    "width": 32,
                    "height": 32,
                    "anchor": [16, 30],
                    "palette": list(spec.used_colors),
                    "provenance": {
                        "origin": "procedural",
                        "author": "dev agent (pi session, sprint 15)",
                        "created": "2026-08-21",
                        "rights": "private-project",
                        "method": (
                            "derived procedurally from the frozen "
                            "calibration-v2 attack-key export bytes: PNG "
                            "decoded, recolored at exactly the "
                            "machine-derived gape mask "
                            "(tools/remedy_masks.py, "
                            "reviews/remedy-v15/gape-masks.json), "
                            "re-authored as a reviewable pixel-grid spec "
                            "(sources/remedy-v15/specs), built into a "
                            "native Aseprite source via "
                            "tools/aseprite_build.lua, exported "
                            "deterministically via tools/export_assets.py "
                            "and verified pixel-for-pixel against the spec "
                            "and alpha-identical to the banked k0"
                        ),
                        "note": provenance_note(payload, root, facing, lane),
                    },
                }
            )
    return {
        "contract_version": 1,
        "release_id": RELEASE_ID,
        "source": {"commit": commit, "files": source_files},
        "target": {
            "game_commit": game_commit(root),
            "runtime_baseline": "manifests/runtime-baseline.json",
        },
        "toolchain": {
            "baseline": "manifests/toolchain-baseline.json",
            "exporter_path": EXPORTER,
            "exporter_sha256": sha256_file(root / EXPORTER),
        },
        "exports": exports,
    }


# -- entry points -----------------------------------------------------------------


def make_masks(dirs: dict[str, Path]) -> Path:
    payload = masks_payload(dirs)
    again = masks_bytes(masks_payload(dirs))
    encoded = masks_bytes(payload)
    if encoded != again:
        raise RemedyMaskError("mask derivation is not deterministic")
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    MASKS_PATH.write_bytes(encoded)
    return MASKS_PATH


def make_specs(dirs: dict[str, Path]) -> list[Path]:
    if not MASKS_PATH.is_file():
        raise RemedyMaskError(f"missing {MASKS_PATH}; run --make-masks first")
    committed = json.loads(MASKS_PATH.read_text(encoding="utf-8"))
    if masks_bytes(masks_payload(dirs)) != MASKS_PATH.read_bytes():
        raise RemedyMaskError(
            "committed gape-masks.json differs from a fresh derivation"
        )
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for asset_id, spec in sorted(all_specs(dirs, committed).items()):
        encoded = spec_bytes(spec)
        if spec_bytes(spec) != encoded:
            raise RemedyMaskError(f"{asset_id}: spec bytes not deterministic")
        path = SPEC_DIR / f"{asset_id}.json"
        path.write_bytes(encoded)
        load_spec(path)  # the banked contract law must accept every spec
        written.append(path)
    return written


def make_release(root: Path, commit_override: str | None = None) -> Path:
    dirs = default_dirs()
    if masks_bytes(masks_payload(dirs)) != MASKS_PATH.read_bytes():
        raise RemedyMaskError(
            "committed gape-masks.json differs from a fresh derivation"
        )
    payload = json.loads(MASKS_PATH.read_text(encoding="utf-8"))
    commit = commit_override or source_commit(root)
    manifest = build_release_manifest(root, commit, payload)
    out_path = EXPORT_DIR / "release.json"
    out_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return out_path


def run_check(dirs: dict[str, Path]) -> int:
    failures: list[str] = []
    if not MASKS_PATH.is_file():
        failures.append(f"missing committed {MASKS_PATH.name}")
    elif masks_bytes(masks_payload(dirs)) != MASKS_PATH.read_bytes():
        failures.append("committed gape-masks.json differs from a fresh derivation")
    if not failures and SPEC_DIR.is_dir():
        payload = json.loads(MASKS_PATH.read_text(encoding="utf-8"))
        for asset_id, spec in sorted(all_specs(dirs, payload).items()):
            path = SPEC_DIR / f"{asset_id}.json"
            if not path.is_file():
                failures.append(f"missing committed spec {path.name}")
            elif spec_bytes(spec) != path.read_bytes():
                failures.append(f"{path.name} differs from a fresh derivation")
    for failure in failures:
        print(f"CHECK FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print("checks passed: committed masks (and specs, if present) regenerate "
          "byte-identically")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--make-masks", action="store_true")
    parser.add_argument("--make-specs", action="store_true")
    parser.add_argument("--make-release", action="store_true")
    parser.add_argument("--commit", help="override source commit (tests only)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    dirs = default_dirs()
    try:
        if args.make_masks:
            print(f"wrote {make_masks(dirs)}")
            return 0
        if args.make_specs:
            for path in make_specs(dirs):
                print(f"wrote {path}")
            return 0
        if args.make_release:
            print(f"wrote {make_release(ROOT, args.commit)}")
            return 0
        if args.check:
            return run_check(dirs)
    except (RemedyMaskError, ValueError, OSError) as exc:
        print(f"remedy masks failed: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
