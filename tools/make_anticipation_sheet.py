#!/usr/bin/env python3
"""Scripted anticipation contact sheet over exact ZONE 1 / ZONE 2 palettes.

Extends the calibration sheet toolchain (shared tile drawing, strict export
PNGs, deterministic writer) with the sprint-3 windup rows per facing:

- FILM:    static v0 idle (control) + four walk frames + anticipation coil +
           attack key at 1x (seven columns)
- FLASH:   the same strip with the pinned runtime hurt-flash applied — every
           opaque pixel replaced by the pack crimson, exactly as the renderer
           replaces its body color on flicker-on frames
- ACC:     flash-accent exploration — the same crimson fill, then pixels
           whose ORIGINAL color is the frozen ramp accent (#140e0c eyes/feet)
           redrawn on top, mirroring how the runtime redraws its facing notch
           over the flash; stacked directly under FLASH for comparison;
           exploration for a future integration design only — phase-0 exports
           may not assume it
- GRAMMAR: attack grammar at 1x — idle static | mid-walk f1 | a0 static |
           a0 at the pinned -3px windup offset | k0 static | k0 at the pinned
           +6px active lunge offset
- DIFF:    anticipation coil versus idle, every walk frame, and the strike
           key at 2x
- 2X/4X:   nearest-neighbor diagnostic rows

Both zone palettes cover the FILM/FLASH/ACC rows; layout is fixed;
regeneration is byte-identical. Existing sheet tools are imported unmodified.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_contact_sheet as base  # noqa: E402
import make_feedback_sheet as feedback  # noqa: E402
import make_motion_sheet as motion  # noqa: E402
from anticipation_metrics import ACCENT_RGB  # noqa: E402
from make_contact_sheet import (  # noqa: E402
    GUTTER,
    LABEL,
    MARGIN_LEFT,
    MARGIN_TOP,
    TILE,
    Sprite,
    draw_floor_tile,
    load_reference,
    sprite_from_png,
)
from make_feedback_sheet import flash_sprite, tell_cell  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
FONT = dict(feedback.FONT)

FACINGS = ("down", "right")
FRAME_COUNT = 4
STRIP = ("IDLE", "F0", "F1", "F2", "F3", "A0", "K0")
DIFF_LABELS = ("IDLE", "F0", "F1", "F2", "F3", "K0")
DIFF_SCALE = 2


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)


def accent_flash_sprite(sprite: Sprite, flash_rgb: tuple[int, int, int]) -> Sprite:
    """Crimson flash fill, then original ramp-accent pixels redrawn on top.

    Mirrors the runtime pattern of redrawing the facing notch over the flash
    (renderer.rb body_color flash + notch-on-top). Uses only the pinned flash
    color and the frozen ramp accent — no new colors exist anywhere.
    """
    flashed = flash_sprite(sprite, flash_rgb)
    original = {(x, y): rgb for x, y, rgb in sprite.pixels}
    return Sprite(
        tuple(
            (x, y, ACCENT_RGB if original[(x, y)] == ACCENT_RGB else rgb)
            for x, y, rgb in flashed.pixels
        )
    )


def load_strip(
    anticipation_dir: Path, attack_dir: Path, walk_dir: Path, idle_dir: Path, facing: str
) -> list[Sprite]:
    """The review strip: frozen idle control, walk frames, coil, strike key."""
    sprites = [sprite_from_png(idle_dir / f"player_1_lane_b_idle_{facing}.png")]
    sprites.extend(
        sprite_from_png(walk_dir / f"player_1_lane_b_walk_{facing}_f{index}.png")
        for index in range(FRAME_COUNT)
    )
    sprites.append(
        sprite_from_png(anticipation_dir / f"player_1_lane_b_attack_{facing}_a0.png")
    )
    sprites.append(sprite_from_png(attack_dir / f"player_1_lane_b_attack_{facing}_k0.png"))
    return sprites


def facing_height(facing: str) -> int:
    header = 8 + GUTTER
    zone_rows = 6 * (TILE + GUTTER)
    grammar = (2 * TILE if facing == "down" else TILE) + GUTTER
    diff = TILE * DIFF_SCALE + GUTTER
    diag = (TILE * 2 + GUTTER) + (TILE * 4 + GUTTER)
    return header + zone_rows + grammar + diff + diag


def draw_facing(cv, y, facing, reference, strip: list[Sprite]) -> int:
    zones = reference["zones"]
    zone1 = zones["zone_1"]
    flash_rgb = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
    lunge = reference["feedback_states"]["lunge_offset"]
    step = TILE + GUTTER
    idle, walks, coil, attack = strip[0], strip[1:5], strip[5], strip[6]

    draw_text(cv, 2, y, facing.upper())
    for index, name in enumerate(STRIP):
        draw_text(cv, MARGIN_LEFT + index * step, y, name)
    y += 8 + GUTTER

    for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
        zone = zones[zone_key]
        for row_label, sprites in (
            ("FILM", strip),
            ("FLASH", [flash_sprite(sprite, flash_rgb) for sprite in strip]),
            ("ACC", [accent_flash_sprite(sprite, flash_rgb) for sprite in strip]),
        ):
            draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} {row_label}"[:11])
            for index, sprite in enumerate(sprites):
                x = MARGIN_LEFT + index * step
                draw_floor_tile(cv, x, y, zone)
                base.blit_sprite(cv, sprite, x, y)
            y += TILE + GUTTER

    cell_w = TILE if facing == "down" else 2 * TILE
    cell_h = 2 * TILE if facing == "down" else TILE
    draw_text(cv, 2, y + cell_h // 2 - 2, "GRAMMAR"[:7])
    grammar_cells = (
        ("IDLE", idle, 0),
        ("F1", walks[1], 0),
        ("A0", coil, 0),
        ("WIND", coil, lunge["windup_px"]),
        ("K0", attack, 0),
        ("LUNGE", attack, lunge["active_px"]),
    )
    for index, (label, sprite, offset) in enumerate(grammar_cells):
        x = MARGIN_LEFT + index * (cell_w + GUTTER)
        tell_cell(cv, x, y, zone1, facing, sprite, offset)
        draw_text(cv, x, y + cell_h - 6, label)
    y += cell_h + GUTTER

    draw_text(cv, 2, y + TILE - 2, "DIFF")
    for index, sprite in enumerate([idle, *walks, attack]):
        x = MARGIN_LEFT + index * (TILE * DIFF_SCALE + GUTTER)
        cv.fill_rect(x, y, TILE * DIFF_SCALE, TILE * DIFF_SCALE, (30, 30, 30, 255))
        cv.blit_scaled(motion.diff_pixels(sprite, coil), x, y, DIFF_SCALE)
        draw_text(cv, x, y + TILE * DIFF_SCALE - 6, DIFF_LABELS[index])
    y += TILE * DIFF_SCALE + GUTTER

    for scale in (2, 4):
        draw_text(cv, 2, y + 2, f"{scale}X")
        for index, sprite in enumerate(strip):
            x = MARGIN_LEFT + index * (TILE * scale + GUTTER)
            cv.fill_rect(x, y, TILE * scale, TILE * scale, (*zone1["floor"], 255))
            base.blit_sprite(cv, sprite, x, y, scale)
        y += TILE * scale + GUTTER
    return y


def build_sheet(
    anticipation_dir: Path, attack_dir: Path, walk_dir: Path, idle_dir: Path,
    reference: dict,
) -> Rgba8Canvas:
    width = MARGIN_LEFT + len(STRIP) * (TILE * 4 + GUTTER)
    height = (
        MARGIN_TOP
        + sum(facing_height(facing) + GUTTER for facing in FACINGS)
        + MARGIN_TOP
    )
    cv = Rgba8Canvas(width, height, BG)
    y = MARGIN_TOP
    for facing in FACINGS:
        strip = load_strip(anticipation_dir, attack_dir, walk_dir, idle_dir, facing)
        y = draw_facing(cv, y, facing, reference, strip) + GUTTER
    return cv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--anticipation-exports", type=Path, default=ROOT / "exports" / "calibration-v3"
    )
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
        default=ROOT / "reviews" / "calibration-v3" / "anticipation-sheet.png",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = build_sheet(
        args.anticipation_exports, args.attack_exports, args.walk_exports,
        args.idle_exports, reference,
    )
    sheet.save(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
