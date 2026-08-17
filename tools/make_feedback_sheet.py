#!/usr/bin/env python3
"""Scripted feedback-state contact sheet over exact ZONE 1 / ZONE 2 palettes.

Extends the calibration sheet toolchain (shared tile/ring drawing, strict
export PNGs, deterministic writer) with the sprint-2 feedback rows per facing:

- FILM:   static v0 idle (control) + four walk frames + attack key at 1x
- FLASH:  the same strip with the pinned runtime hurt-flash applied — every
          opaque pixel replaced by the pack crimson, exactly as the renderer
          replaces its body color on flicker-on frames (FILM directly above
          is the flicker-off phase)
- TELL:   attack grammar at 1x — idle, mid-walk, windup (idle at the pinned
          -3px offset), attack key static, attack key at the pinned +6px
          active lunge offset
- ADJ:    cross-signal adjacency — flash-on body and attack key beside a
          runtime-faithful telegraphing human (pinned swell geometry), and
          flash-on body beside an open-transition gold tile
- RING S: possession ring, current renderer geometry (SIZE square + expand)
- RING B: possession ring, bbox-fit exploration variant (per-frame sprite
          bbox + pinned expand) — exploration for a future integration
          design; phase-0 exports may not assume it
- DIFF:   attack key versus idle and every walk frame at 2x
- 2X/4X:  nearest-neighbor diagnostic rows

Both zone palettes cover the FILM/FLASH rows; layout is fixed; regeneration
is byte-identical. Existing sheet tools are imported unmodified.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_contact_sheet as base  # noqa: E402
import make_motion_sheet as motion  # noqa: E402
from make_contact_sheet import (  # noqa: E402
    GUTTER,
    LABEL,
    MARGIN_LEFT,
    MARGIN_TOP,
    TILE,
    Sprite,
    draw_floor_tile,
    draw_gold_tile,
    draw_wall_tile,
    load_reference,
    sprite_from_png,
)
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
FONT = {
    **motion.FONT,
    "J": ("001", "001", "001", "101", "010"),
    "U": ("101", "101", "101", "101", "111"),
}

FACINGS = ("down", "right")
FRAME_COUNT = 4
STRIP = ("IDLE", "F0", "F1", "F2", "F3", "K0")
DIFF_SCALE = 2


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)


def flash_sprite(sprite: Sprite, rgb: tuple[int, int, int]) -> Sprite:
    """The pinned runtime hurt-flash: full body-color replacement."""
    return Sprite(tuple((x, y, rgb) for x, y, _ in sprite.pixels))


def sprite_bbox(sprite: Sprite) -> tuple[int, int, int, int]:
    xs = [x for x, _, _ in sprite.pixels]
    ys = [y for _, y, _ in sprite.pixels]
    return min(xs), min(ys), max(xs), max(ys)


def load_strip(attack_dir: Path, walk_dir: Path, idle_dir: Path, facing: str) -> list[Sprite]:
    """The review strip: frozen idle control, four walk frames, attack key."""
    sprites = [sprite_from_png(idle_dir / f"player_1_lane_b_idle_{facing}.png")]
    sprites.extend(
        sprite_from_png(walk_dir / f"player_1_lane_b_walk_{facing}_f{index}.png")
        for index in range(FRAME_COUNT)
    )
    sprites.append(sprite_from_png(attack_dir / f"player_1_lane_b_attack_{facing}_k0.png"))
    return sprites


def draw_bbox_ring(cv: Rgba8Canvas, x: int, y: int, reference: dict, sprite: Sprite) -> None:
    """Bbox-fit exploration ring: white rect at the sprite bbox + pinned expand."""
    ring = reference["possession_ring"]
    expand = ring["expand"]
    left, top, right, bottom = sprite_bbox(sprite)
    cv.fill_rect(
        x + left - expand, y + top - expand,
        (right - left + 1) + 2 * expand, (bottom - top + 1) + 2 * expand,
        (*ring["rgb"], 255),
    )


def ring_variant_cell(cv, x, y, zone, reference, sprite: Sprite, variant: str) -> None:
    """2x2 tiles: wall above, floor around, ringed sprite bottom-left."""
    draw_wall_tile(cv, x, y, zone)
    draw_floor_tile(cv, x + TILE, y, zone)
    draw_floor_tile(cv, x, y + TILE, zone)
    draw_floor_tile(cv, x + TILE, y + TILE, zone)
    if variant == "size":
        base.draw_ring(cv, x, y + TILE, reference)
    else:
        draw_bbox_ring(cv, x, y + TILE, reference, sprite)
    base.blit_sprite(cv, sprite, x, y + TILE)


def draw_telegraph_body(cv: Rgba8Canvas, x: int, y: int, reference: dict) -> None:
    """A telegraphing human exactly as the renderer draws it (pinned swell)."""
    body = reference["primitive_body"]
    swell = reference["feedback_states"]["telegraph_swell"]
    telegraph = reference["telegraph"]
    ox, oy = body["tile_offset"]
    size = body["size"]
    bx, by = x + ox, y + oy
    edge, core, inset = (
        swell["edge_expand_px"], swell["core_expand_px"], swell["inner_body_inset_px"]
    )
    cv.fill_rect(bx - edge, by - edge, size + 2 * edge, size + 2 * edge,
                 (*telegraph["edge_rgb"], 255))
    cv.fill_rect(bx - core, by - core, size + 2 * core, size + 2 * core,
                 (*telegraph["core_rgb"], 255))
    cv.fill_rect(bx + inset, by + inset, size - 2 * inset, size - 2 * inset,
                 (*telegraph["body_rgb"], 255))


def adjacency_cell(cv, x, y, zone, reference, context: str, sprite: Sprite) -> None:
    """2x2 tiles: context body/tile bottom-left, reviewed sprite bottom-right."""
    draw_wall_tile(cv, x, y, zone)
    draw_floor_tile(cv, x + TILE, y, zone)
    draw_floor_tile(cv, x, y + TILE, zone)
    draw_floor_tile(cv, x + TILE, y + TILE, zone)
    if context == "telegraph":
        draw_telegraph_body(cv, x, y + TILE, reference)
    else:
        draw_gold_tile(cv, x, y + TILE, zone)
    base.blit_sprite(cv, sprite, x + TILE, y + TILE)


def tell_cell(cv, x, y, zone, facing: str, sprite: Sprite, offset: int) -> None:
    """Two floor tiles along the facing axis; sprite at a pinned draw offset."""
    half = TILE // 2
    if facing == "down":
        draw_floor_tile(cv, x, y, zone)
        draw_floor_tile(cv, x, y + TILE, zone)
        base.blit_sprite(cv, sprite, x, y + half + offset)
    else:
        draw_floor_tile(cv, x, y, zone)
        draw_floor_tile(cv, x + TILE, y, zone)
        base.blit_sprite(cv, sprite, x + half + offset, y)


def facing_height(facing: str) -> int:
    header = 8 + GUTTER
    zone_rows = 4 * (TILE + GUTTER)
    tell = (2 * TILE if facing == "down" else TILE) + GUTTER
    adj = 2 * TILE + GUTTER
    rings = 2 * (2 * TILE + GUTTER)
    diff = TILE * DIFF_SCALE + GUTTER
    diag = (TILE * 2 + GUTTER) + (TILE * 4 + GUTTER)
    return header + zone_rows + tell + adj + rings + diff + diag


def draw_facing(cv, y, facing, reference, strip: list[Sprite]) -> int:
    zones = reference["zones"]
    zone1 = zones["zone_1"]
    flash_rgb = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
    lunge = reference["feedback_states"]["lunge_offset"]
    step = TILE + GUTTER
    idle, walks, attack = strip[0], strip[1:5], strip[5]

    draw_text(cv, 2, y, facing.upper())
    for index, name in enumerate(STRIP):
        draw_text(cv, MARGIN_LEFT + index * step, y, name)
    y += 8 + GUTTER

    for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
        zone = zones[zone_key]
        for row_label, sprites in (
            ("FILM", strip),
            ("FLASH", [flash_sprite(sprite, flash_rgb) for sprite in strip]),
        ):
            draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} {row_label}"[:11])
            for index, sprite in enumerate(sprites):
                x = MARGIN_LEFT + index * step
                draw_floor_tile(cv, x, y, zone)
                base.blit_sprite(cv, sprite, x, y)
            y += TILE + GUTTER

    tell_w = TILE if facing == "down" else 2 * TILE
    tell_h = 2 * TILE if facing == "down" else TILE
    draw_text(cv, 2, y + tell_h // 2 - 2, "TELL")
    tell_cells = (
        ("IDLE", idle, 0),
        ("F1", walks[1], 0),
        ("WIND", idle, lunge["windup_px"]),
        ("K0", attack, 0),
        ("LUNGE", attack, lunge["active_px"]),
    )
    for index, (label, sprite, offset) in enumerate(tell_cells):
        x = MARGIN_LEFT + index * (tell_w + GUTTER)
        tell_cell(cv, x, y, zone1, facing, sprite, offset)
        draw_text(cv, x, y + tell_h - 6, label)
    y += tell_h + GUTTER

    draw_text(cv, 2, y + TILE - 2, "ADJ")
    flash_idle = flash_sprite(idle, flash_rgb)
    adj_cells = (
        ("telegraph", flash_idle),
        ("telegraph", attack),
        ("gold", flash_idle),
    )
    for index, (context, sprite) in enumerate(adj_cells):
        adjacency_cell(
            cv, MARGIN_LEFT + index * (2 * TILE + GUTTER), y, zone1, reference,
            context, sprite,
        )
    y += 2 * TILE + GUTTER

    for variant, label in (("size", "RING S"), ("bbox", "RING B")):
        draw_text(cv, 2, y + TILE - 2, label)
        for index, sprite in enumerate(strip):
            ring_variant_cell(
                cv, MARGIN_LEFT + index * (2 * TILE + GUTTER), y, zone1, reference,
                sprite, variant,
            )
        y += 2 * TILE + GUTTER

    draw_text(cv, 2, y + TILE - 2, "DIFF")
    for index, sprite in enumerate([idle, *walks]):
        x = MARGIN_LEFT + index * (TILE * DIFF_SCALE + GUTTER)
        cv.fill_rect(x, y, TILE * DIFF_SCALE, TILE * DIFF_SCALE, (30, 30, 30, 255))
        cv.blit_scaled(motion.diff_pixels(sprite, attack), x, y, DIFF_SCALE)
        draw_text(cv, x, y + TILE * DIFF_SCALE - 6, STRIP[index])
    y += TILE * DIFF_SCALE + GUTTER

    for scale in (2, 4):
        draw_text(cv, 2, y + 2, f"{scale}X")
        for index, sprite in enumerate(strip):
            x = MARGIN_LEFT + index * (TILE * scale + GUTTER)
            cv.fill_rect(x, y, TILE * scale, TILE * scale, (*zone1["floor"], 255))
            base.blit_sprite(cv, sprite, x, y, scale)
        y += TILE * scale + GUTTER
    return y


def build_sheet(attack_dir: Path, walk_dir: Path, idle_dir: Path, reference: dict) -> Rgba8Canvas:
    width = MARGIN_LEFT + len(STRIP) * (TILE * 4 + GUTTER)
    height = (
        MARGIN_TOP
        + sum(facing_height(facing) + GUTTER for facing in FACINGS)
        + MARGIN_TOP
    )
    cv = Rgba8Canvas(width, height, BG)
    y = MARGIN_TOP
    for facing in FACINGS:
        strip = load_strip(attack_dir, walk_dir, idle_dir, facing)
        y = draw_facing(cv, y, facing, reference, strip) + GUTTER
    return cv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--attack-exports", type=Path, default=ROOT / "exports" / "calibration-v2"
    )
    parser.add_argument(
        "--walk-exports", type=Path, default=ROOT / "exports" / "calibration-v1"
    )
    parser.add_argument(
        "--idle-exports", type=Path, default=ROOT / "exports" / "calibration-v0"
    )
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "manifests" / "render-reference.json"
    )
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v2" / "feedback-sheet.png",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = build_sheet(args.attack_exports, args.walk_exports, args.idle_exports, reference)
    sheet.save(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
