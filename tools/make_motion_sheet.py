#!/usr/bin/env python3
"""Scripted motion contact sheet for a 4-frame walk cycle over runtime palettes.

Extends the calibration-v0 contact-sheet toolchain (shared tile/ring drawing,
strict export PNGs, deterministic writer) with motion-specific rows per facing:

- FILM:  static v0 idle (control) plus the four walk frames at 1x
- WALK:  successive frames laid along a one-tile slide (8px per frame), the
         runtime view of one tile of movement, including the f3->f0 loop seam
- IDLE:  the static idle at the same slide phases (the sliding-idle control)
- RING:  possession ring over idle + every frame (renderer geometry)
- DIFF:  consecutive-frame pixel differences at 2x (cyclic pairs)
- 2X/4X: nearest-neighbor diagnostic rows

Layout is fixed; regeneration is byte-identical.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_contact_sheet as base  # noqa: E402
from make_contact_sheet import (  # noqa: E402
    GUTTER,
    LABEL,
    MARGIN_LEFT,
    MARGIN_TOP,
    TILE,
    Sprite,
    draw_floor_tile,
    load_reference,
    ring_cell,
    sprite_from_png,
)
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
FONT = {
    **base.FONT,
    "F": ("111", "100", "110", "100", "100"),
    "H": ("101", "101", "111", "101", "101"),
    "K": ("101", "110", "100", "110", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "T": ("111", "010", "010", "010", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "0": ("111", "101", "101", "101", "111"),
    "3": ("111", "001", "011", "001", "111"),
}

FACINGS = ("down", "right")
FRAME_COUNT = 4
PHASES = (0, 8, 16, 24, 32)  # one-tile slide, 8px per frame, loop seam at 32
DIFF_SCALE = 2
DIFF_SAME = (70, 70, 70, 255)
DIFF_RECOLORED = (230, 200, 60, 255)
DIFF_REMOVED = (220, 70, 50, 255)
DIFF_ADDED = (90, 210, 100, 255)


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)


def load_cycle(exports_dir: Path, idle_dir: Path, facing: str) -> tuple[Sprite, list[Sprite]]:
    idle = sprite_from_png(idle_dir / f"player_1_lane_b_idle_{facing}.png")
    frames = [
        sprite_from_png(exports_dir / f"player_1_lane_b_walk_{facing}_f{index}.png")
        for index in range(FRAME_COUNT)
    ]
    return idle, frames


def phase_cell(cv, x, y, zone, sprite: Sprite, facing: str, phase: int) -> None:
    """Two floor tiles along the facing axis; sprite offset by the slide phase."""
    if facing == "down":
        draw_floor_tile(cv, x, y, zone)
        draw_floor_tile(cv, x, y + TILE, zone)
        base.blit_sprite(cv, sprite, x, y + phase)
    else:
        draw_floor_tile(cv, x, y, zone)
        draw_floor_tile(cv, x + TILE, y, zone)
        base.blit_sprite(cv, sprite, x + phase, y)


def diff_pixels(before: Sprite, after: Sprite) -> list[tuple[int, int, tuple[int, int, int]]]:
    """Categorized per-pixel difference between two frames."""
    before_map = {(x, y): rgb for x, y, rgb in before.pixels}
    after_map = {(x, y): rgb for x, y, rgb in after.pixels}
    out: list[tuple[int, int, tuple[int, int, int]]] = []
    for position in sorted(before_map.keys() | after_map.keys()):
        in_before, in_after = position in before_map, position in after_map
        if in_before and in_after:
            same = before_map[position] == after_map[position]
            color = DIFF_SAME if same else DIFF_RECOLORED
        elif in_before:
            color = DIFF_REMOVED
        else:
            color = DIFF_ADDED
        out.append((position[0], position[1], color[:3]))
    return out


def strip_columns() -> list[str]:
    return ["IDLE"] + [f"F{index}" for index in range(FRAME_COUNT)]


def facing_height(facing: str) -> int:
    """Total pixel height of one facing section (used for canvas sizing)."""
    header = 8
    film = TILE + GUTTER
    slide = (2 * TILE if facing == "down" else TILE) + GUTTER
    zone_rows = 2 * (film + 2 * slide)
    ring = 2 * TILE + GUTTER
    diff = TILE * DIFF_SCALE + GUTTER
    diag = (TILE * 2 + GUTTER) + (TILE * 4 + GUTTER)
    return header + GUTTER + zone_rows + ring + diff + diag


def draw_facing(cv, y, facing, zones, reference, idle: Sprite, frames: list[Sprite]) -> int:
    step = TILE + GUTTER
    walk_cell_h = 2 * TILE if facing == "down" else TILE
    walk_cell_w = TILE if facing == "down" else 2 * TILE
    walk_step = walk_cell_w + GUTTER
    strip = [idle, *frames]

    draw_text(cv, 2, y, facing.upper())
    for index, name in enumerate(strip_columns()):
        draw_text(cv, MARGIN_LEFT + index * step, y, name)
    y += 8 + GUTTER

    for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
        zone = zones[zone_key]
        draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} FILM")
        for index, sprite in enumerate(strip):
            x = MARGIN_LEFT + index * step
            draw_floor_tile(cv, x, y, zone)
            base.blit_sprite(cv, sprite, x, y)
        y += TILE + GUTTER

        for row_label, row_sprites in (
            ("WALK", [frames[0], frames[1], frames[2], frames[3], frames[0]]),
            ("IDLE", [idle] * len(PHASES)),
        ):
            draw_text(cv, 2, y + walk_cell_h // 2 - 2, f"{zone_label} {row_label}")
            for index, phase in enumerate(PHASES):
                x = MARGIN_LEFT + index * walk_step
                phase_cell(cv, x, y, zone, row_sprites[index], facing, phase)
            y += walk_cell_h + GUTTER

    zone1 = zones["zone_1"]
    draw_text(cv, 2, y + TILE - 2, "RING")
    for index, sprite in enumerate(strip):
        ring_cell(cv, MARGIN_LEFT + index * (2 * TILE + GUTTER), y, zone1, reference, sprite)
    y += 2 * TILE + GUTTER

    draw_text(cv, 2, y + TILE - 2, "DIFF")
    cycle = [*frames, frames[0]]
    for index in range(FRAME_COUNT):
        x = MARGIN_LEFT + index * (TILE * DIFF_SCALE + GUTTER)
        cv.fill_rect(x, y, TILE * DIFF_SCALE, TILE * DIFF_SCALE, (30, 30, 30, 255))
        cv.blit_scaled(diff_pixels(cycle[index], cycle[index + 1]), x, y, DIFF_SCALE)
    y += TILE * DIFF_SCALE + GUTTER

    for scale in (2, 4):
        draw_text(cv, 2, y + 2, f"{scale}X")
        for index, sprite in enumerate(strip):
            x = MARGIN_LEFT + index * (TILE * scale + GUTTER)
            cv.fill_rect(x, y, TILE * scale, TILE * scale, (*zone1["floor"], 255))
            base.blit_sprite(cv, sprite, x, y, scale)
        y += TILE * scale + GUTTER
    return y


def build_sheet(exports_dir: Path, idle_dir: Path, reference: dict) -> Rgba8Canvas:
    zones = reference["zones"]
    width = MARGIN_LEFT + 5 * (TILE * 4 + GUTTER)
    height = (
        MARGIN_TOP
        + sum(facing_height(facing) + GUTTER for facing in FACINGS)
        + MARGIN_TOP
    )
    cv = Rgba8Canvas(width, height, BG)
    y = MARGIN_TOP
    for facing in FACINGS:
        idle, frames = load_cycle(exports_dir, idle_dir, facing)
        y = draw_facing(cv, y, facing, zones, reference, idle, frames) + GUTTER
    return cv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", type=Path, default=ROOT / "exports" / "calibration-v1")
    parser.add_argument(
        "--idle-exports", type=Path, default=ROOT / "exports" / "calibration-v0"
    )
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "manifests" / "render-reference.json"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "reviews" / "calibration-v1" / "motion-sheet.png"
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = build_sheet(args.exports, args.idle_exports, reference)
    sheet.save(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
