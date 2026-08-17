#!/usr/bin/env python3
"""Scripted calibration contact sheet over exact ZONE 1 / ZONE 2 palette samples.

Reads the shipped export PNGs (never a repaint), composes them over pinned
runtime palettes with the current primitive body as baseline, and writes one
deterministic PNG. Native 1x rows decide readability; 2x/4x rows diagnose
pixels. Layout is fixed; regeneration is byte-identical.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from png_reader import read_rgba  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

TILE = 32
GUTTER = 6
MARGIN_LEFT = 46
MARGIN_TOP = 14
BG = (16, 16, 16, 255)
LABEL = (150, 150, 150, 255)

# Minimal 3x5 glyphs for sheet labels (generic mechanical labels only).
FONT = {
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "G": ("011", "100", "101", "101", "011"),
    "I": ("111", "010", "010", "010", "111"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "X": ("101", "101", "010", "101", "101"),
    "Z": ("111", "001", "010", "100", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("110", "001", "010", "100", "111"),
    "4": ("101", "101", "111", "001", "001"),
    " ": ("000", "000", "000", "000", "000"),
}

COLUMNS = (
    ("BASE D", "baseline", "down"),
    ("BASE R", "baseline", "right"),
    ("A D", "player_1_lane_a_idle_down", None),
    ("A R", "player_1_lane_a_idle_right", None),
    ("B D", "player_1_lane_b_idle_down", None),
    ("B R", "player_1_lane_b_idle_right", None),
    ("C D", "player_1_lane_c_idle_down", None),
    ("C R", "player_1_lane_c_idle_right", None),
)


@dataclass(frozen=True)
class Sprite:
    """Opaque pixels of one 32x32 candidate: (x, y, rgb)."""

    pixels: tuple[tuple[int, int, tuple[int, int, int]], ...]


def load_reference(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sprite_from_png(path: Path) -> Sprite:
    width, height, raw = read_rgba(path)
    if (width, height) != (TILE, TILE):
        raise ValueError(f"{path.name}: contact sheet expects 32x32 exports")
    pixels = []
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 4
            r, g, b, a = raw[offset : offset + 4]
            if a == 255:
                pixels.append((x, y, (r, g, b)))
    return Sprite(tuple(pixels))


def primitive_sprite(reference: dict, facing: str) -> Sprite:
    """The current runtime body: role rect + facing notch (pinned constants)."""
    body = reference["primitive_body"]
    size = body["size"]
    ox, oy = body["tile_offset"]
    rgb = tuple(body["body_rgb"])
    notch = tuple(body["notch_rgb"])
    n = body["notch_size"]
    pixels = [(ox + x, oy + y, rgb) for y in range(size) for x in range(size)]
    if facing == "down":
        nx0, ny0 = ox + size // 2 - n // 2, oy + size - n
    else:
        nx0, ny0 = ox + size - n, oy + size // 2 - n // 2
    for y in range(ny0, ny0 + n):
        for x in range(nx0, nx0 + n):
            pixels.append((x, y, notch))
    return Sprite(tuple(pixels))


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)


def draw_floor_tile(cv: Rgba8Canvas, x: int, y: int, zone: dict) -> None:
    cv.fill_rect(x, y, TILE, TILE, (*zone["floor"], 255))
    cv.fill_rect(x, y, TILE, 1, (*zone["grid"], 255))
    cv.fill_rect(x, y, 1, TILE, (*zone["grid"], 255))


def draw_wall_tile(cv: Rgba8Canvas, x: int, y: int, zone: dict) -> None:
    cv.fill_rect(x, y, TILE, TILE, (*zone["wall"], 255))


def draw_gold_tile(cv: Rgba8Canvas, x: int, y: int, zone: dict) -> None:
    """Open transition as the renderer draws it: gold square inset 3 on floor."""
    draw_floor_tile(cv, x, y, zone)
    cv.fill_rect(x + 3, y + 3, TILE - 6, TILE - 6, (*zone["transition"], 255))


def draw_telegraph_tile(cv: Rgba8Canvas, x: int, y: int, zone: dict, reference: dict) -> None:
    """Telegraph-pattern swatch from renderer constants (edge, core, bone body)."""
    telegraph = reference["telegraph"]
    draw_floor_tile(cv, x, y, zone)
    cv.fill_rect(x, y, TILE, TILE, (*telegraph["edge_rgb"], 255))
    cv.fill_rect(x + 2, y + 2, TILE - 4, TILE - 4, (*telegraph["core_rgb"], 255))
    cv.fill_rect(x + 7, y + 7, TILE - 14, TILE - 14, (*telegraph["body_rgb"], 255))


def blit_sprite(cv: Rgba8Canvas, sprite: Sprite, x: int, y: int, scale: int = 1) -> None:
    cv.blit_scaled(list(sprite.pixels), x, y, scale)


def draw_ring(cv: Rgba8Canvas, x: int, y: int, reference: dict) -> None:
    """Possession ring exactly as the renderer draws it: white rect body+-3."""
    ring = reference["possession_ring"]
    body = reference["primitive_body"]
    ox, oy = body["tile_offset"]
    size = body["size"]
    expand = ring["expand"]
    cv.fill_rect(
        x + ox - expand, y + oy - expand, size + 2 * expand, size + 2 * expand,
        (*ring["rgb"], 255),
    )


def main_cell(cv, x, y, zone, reference, sprite):
    """2x2 tiles: wall, gold transition, sprite on floor, telegraph swatch."""
    draw_wall_tile(cv, x, y, zone)
    draw_gold_tile(cv, x + TILE, y, zone)
    draw_floor_tile(cv, x, y + TILE, zone)
    draw_telegraph_tile(cv, x + TILE, y + TILE, zone, reference)
    blit_sprite(cv, sprite, x, y + TILE)


def ring_cell(cv, x, y, zone, reference, sprite):
    """2x2 tiles: wall above, floor around, ringed sprite bottom-left."""
    draw_wall_tile(cv, x, y, zone)
    draw_floor_tile(cv, x + TILE, y, zone)
    draw_floor_tile(cv, x, y + TILE, zone)
    draw_floor_tile(cv, x + TILE, y + TILE, zone)
    draw_ring(cv, x, y + TILE, reference)
    blit_sprite(cv, sprite, x, y + TILE)


def slide_cell(cv, x, y, zone, reference, sprite):
    """2x2 floor tiles: sprite mid-way through a one-tile translation."""
    for ty in (0, TILE):
        for tx in (0, TILE):
            draw_floor_tile(cv, x + tx, y + ty, zone)
    blit_sprite(cv, sprite, x + TILE // 2, y + TILE)


def build_sheet(exports_dir: Path, reference: dict) -> Rgba8Canvas:
    sprites: dict[str, Sprite] = {}
    for _, key, facing in COLUMNS:
        if key == "baseline":
            sprites[f"baseline_{facing}"] = primitive_sprite(reference, facing)
        else:
            sprites[key] = sprite_from_png(exports_dir / f"{key}.png")

    def column_sprite(column) -> Sprite:
        _, key, facing = column
        return sprites[f"baseline_{facing}"] if key == "baseline" else sprites[key]

    cell = 2 * TILE
    step = cell + GUTTER
    diag_width = MARGIN_LEFT + len(COLUMNS) * (TILE * 4 + GUTTER)
    width = max(MARGIN_LEFT + len(COLUMNS) * step, diag_width)
    zone_rows = 3 * 2  # main, ring, slide per zone
    diag_heights = TILE * 2 + GUTTER + TILE * 4 + GUTTER
    height = (
        MARGIN_TOP
        + zone_rows * (cell + GUTTER)
        + diag_heights
        + MARGIN_TOP
    )
    cv = Rgba8Canvas(width, height, BG)

    for index, (label, _, _) in enumerate(COLUMNS):
        draw_text(cv, MARGIN_LEFT + index * step, 4, label)

    y = MARGIN_TOP
    zones = reference["zones"]
    for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
        zone = zones[zone_key]
        for row_label, cell_fn in (
            ("MAIN", main_cell), ("RING", ring_cell), ("SLIDE", slide_cell),
        ):
            draw_text(cv, 2, y + cell // 2 - 6, zone_label)
            draw_text(cv, 2, y + cell // 2 + 1, row_label)
            for index, column in enumerate(COLUMNS):
                cell_fn(cv, MARGIN_LEFT + index * step, y, zone, reference,
                        column_sprite(column))
            y += cell + GUTTER

    zone1 = zones["zone_1"]
    for scale in (2, 4):
        draw_text(cv, 2, y + 2, f"{scale}X")
        for index, column in enumerate(COLUMNS):
            x = MARGIN_LEFT + index * (TILE * scale + GUTTER)
            cv.fill_rect(x, y, TILE * scale, TILE * scale, (*zone1["floor"], 255))
            blit_sprite(cv, column_sprite(column), x, y, scale)
        y += TILE * scale + GUTTER
    return cv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", type=Path, default=ROOT / "exports" / "calibration-v0")
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "manifests" / "render-reference.json"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "reviews" / "calibration-v0" / "contact-sheet.png"
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = build_sheet(args.exports, reference)
    sheet.save(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
