#!/usr/bin/env python3
"""Tick-accurate attack-grammar timeline sheet over exact ZONE 1 / ZONE 2 palettes.

Sprint-4 temporal verification: renders the pinned runtime attack timing
(manifests/render-reference.json `attack_timing`, captured read-only from the
pinned game commit) as a one-column-per-tick timeline, composing ONLY banked
export bytes at computed integer offsets — no repainting, no resampling, no
new creature pixels.

- RULER rows:   phase labels + per-tick indices (1 column = 1 tick, no
                cadence compression anywhere)
- APPROACH:     idle_pre + the 13-tick walk step (smoothstep tween positions,
                pinned step_frames; walk-frame mapping is a declared review
                convention, NOT an engine contract — banked v1 finding);
                identical in timelines A and B, so one row per zone
- ATTACK:       timelines A (incumbent: idle held at the pinned -3px windup
                offset) and B (candidate: a0 coil held at -3px) stacked per
                zone; both continue k0 at +6px for the pinned active ticks and
                idle at 0 for the pinned recovery ticks
- EXP:          down facing only, labeled NOT RUNTIME - timeline B's attack
                segment with a 10-tick windup hold (inside the KB 100-200ms
                anticipation band) for duration-vs-pose attribution
- FLICKER:      the pinned hurt-flash cadence (3 on / 3 off) as ACC (crimson +
                frozen-ramp-accent redraw, the v3 exploration treatment) over
                PLAIN crimson - the v3 adoption condition; pose held static
- 2X:           the four transition ticks of timeline B at 2x (diagnostic)
- GRAMMAR:      the static v3 grammar cells via the banked tell_cell (control)

Every creature cell is recorded in a machine-readable manifest consumed by
tools/timeline_metrics.py for composition-purity and tick-math verification.
Layout is fixed; regeneration is byte-identical. Existing sheet tools are
imported unmodified. Optional APNG viewing aids (A|B side by side, 4x
nearest-neighbor, exact 1/60s per-frame delay) are never blocking.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_contact_sheet as base  # noqa: E402
import make_feedback_sheet as feedback  # noqa: E402
from make_anticipation_sheet import accent_flash_sprite  # noqa: E402
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
FONT = {
    **feedback.FONT,
    "P": ("110", "101", "110", "100", "100"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "001", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}

FACINGS = ("down", "right")
PHASE_LABELS = {
    "idle_pre": "IDLE",
    "walk": "WALK",
    "windup": "WIND",
    "active": "ACT",
    "recovery": "REC",
    "idle_post": "IDLE",
    "on": "ON",
    "off": "OFF",
}
IDLE_PRE_TICKS = 2   # declared context padding (rationale), not a runtime pin
IDLE_POST_TICKS = 2  # declared context padding (rationale), not a runtime pin
EXP_WINDUP_TICKS = 10  # KB 100-200ms band exploration - NOT RUNTIME
FLICKER_TICKS = 12
TWOX_SCALE = 2
APNG_SCALE = 4
APNG_TICK_DELAY = (1, 60)      # exact one tick at the unoverridden 60 tps
APNG_LAST_DELAY = (30, 60)     # declared 0.5s hold before the loop restarts
WALK_FRAME_COUNT = 4


def smoothstep(t: float) -> float:
    """The pinned runtime tween (grid_walker.rb L94): 3t^2 - 2t^3."""
    return t * t * (3.0 - 2.0 * t)


def round_half_up(value: float) -> int:
    """Declared integer-position rule: floor(v + 0.5), fixed for determinism."""
    import math

    return math.floor(value + 0.5)


def walk_frame_index(step_tick: int, step_frames: int) -> int:
    """Declared review convention (banked v1 grid-phase-lock finding: not an
    engine contract): distribute the four banked walk frames across the real
    step duration; the step arrives on f3 (byte-identical to the idle)."""
    return min(
        WALK_FRAME_COUNT - 1,
        (step_tick - 1) * WALK_FRAME_COUNT // step_frames,
    )


def build_plan(reference: dict) -> dict:
    """The tick plan: a pure function of the pinned constants."""
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    step = timing["step_frames"]["value"]

    ticks = []

    def add(phase: str, pose_a: str, pose_b: str, axis_px: int, offset_px: int) -> None:
        ticks.append(
            {
                "tick": len(ticks),
                "phase": phase,
                "pose_a": pose_a,
                "pose_b": pose_b,
                "axis_px": axis_px,
                "offset_px": offset_px,
            }
        )

    for _ in range(IDLE_PRE_TICKS):
        add("idle_pre", "idle", "idle", 0, 0)
    for k in range(1, step + 1):
        pose = f"f{walk_frame_index(k, step)}"
        add("walk", pose, pose, round_half_up(TILE * smoothstep(k / step)), 0)
    for _ in range(windup):
        add("windup", "idle", "a0", TILE + lunge["windup_px"], lunge["windup_px"])
    for _ in range(active):
        add("active", "k0", "k0", TILE + lunge["active_px"], lunge["active_px"])
    for _ in range(recovery):
        add("recovery", "idle", "idle", TILE, 0)
    for _ in range(IDLE_POST_TICKS):
        add("idle_post", "idle", "idle", TILE, 0)

    approach = [t for t in ticks if t["tick"] <= IDLE_PRE_TICKS + step - 1]
    arrival = IDLE_PRE_TICKS + step - 1
    attack = [t for t in ticks if t["tick"] >= arrival]  # overlap column t14
    return {
        "constants": {
            "windup_frames": windup,
            "active_frames": active,
            "recovery_frames": recovery,
            "step_frames": step,
            "windup_px": lunge["windup_px"],
            "active_px": lunge["active_px"],
            "idle_pre_ticks": IDLE_PRE_TICKS,
            "idle_post_ticks": IDLE_POST_TICKS,
        },
        "ticks": ticks,
        "approach_ticks": approach,
        "attack_ticks": attack,
        "arrival_tick": arrival,
    }


def build_exp_plan(reference: dict) -> dict:
    """EXP row plan: timeline B's attack segment with a 10-tick hold.
    Labeled NOT RUNTIME on the sheet - duration-vs-pose attribution only."""
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    ticks = []

    def add(phase: str, pose: str, offset_px: int) -> None:
        ticks.append(
            {"tick": len(ticks), "phase": phase, "pose_b": pose, "offset_px": offset_px}
        )

    for _ in range(IDLE_PRE_TICKS):
        add("idle_pre", "idle", 0)
    for _ in range(EXP_WINDUP_TICKS):
        add("windup", "a0", lunge["windup_px"])
    for _ in range(timing["active_frames"]["value"]):
        add("active", "k0", lunge["active_px"])
    for _ in range(timing["recovery_frames"]["value"]):
        add("recovery", "idle", 0)
    for _ in range(IDLE_POST_TICKS):
        add("idle_post", "idle", 0)
    return {"ticks": ticks, "windup_ticks": EXP_WINDUP_TICKS}


def flicker_on(tick: int, period: int) -> bool:
    """The pinned hurt-flash cadence: `period` on, `period` off."""
    return tick % (2 * period) < period


def load_poses(
    anticipation_dir: Path, attack_dir: Path, walk_dir: Path, idle_dir: Path, facing: str
) -> dict[str, Sprite]:
    poses = {"idle": sprite_from_png(idle_dir / f"player_1_lane_b_idle_{facing}.png")}
    for index in range(WALK_FRAME_COUNT):
        poses[f"f{index}"] = sprite_from_png(
            walk_dir / f"player_1_lane_b_walk_{facing}_f{index}.png"
        )
    poses["a0"] = sprite_from_png(
        anticipation_dir / f"player_1_lane_b_attack_{facing}_a0.png"
    )
    poses["k0"] = sprite_from_png(attack_dir / f"player_1_lane_b_attack_{facing}_k0.png")
    return poses


def treat(sprite: Sprite, treatment: str, flash_rgb: tuple[int, int, int]) -> Sprite:
    if treatment == "none":
        return sprite
    if treatment == "flash":
        return flash_sprite(sprite, flash_rgb)
    if treatment == "acc":
        return accent_flash_sprite(sprite, flash_rgb)
    raise ValueError(f"unknown treatment {treatment!r}")


def compose_window(
    zone: dict, facing: str, tiles: int, sprite: Sprite, win_px: int
) -> Rgba8Canvas:
    """One 1x window cell: `tiles` grid-lined floor tiles along the facing
    axis, the sprite canvas blitted at the integer axis position."""
    if facing == "down":
        cv = Rgba8Canvas(TILE, tiles * TILE, BG)
        for i in range(tiles):
            draw_floor_tile(cv, 0, i * TILE, zone)
        base.blit_sprite(cv, sprite, 0, win_px)
    else:
        cv = Rgba8Canvas(tiles * TILE, TILE, BG)
        for i in range(tiles):
            draw_floor_tile(cv, i * TILE, 0, zone)
        base.blit_sprite(cv, sprite, win_px, 0)
    return cv


def canvas_pixels(cv: Rgba8Canvas) -> list[tuple[int, int, tuple[int, int, int]]]:
    return [
        (x, y, cv.get(x, y)[:3])
        for y in range(cv.height)
        for x in range(cv.width)
        if cv.get(x, y)[3] == 255
    ]


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)


def cell_size(facing: str, tiles: int, scale: int = 1) -> tuple[int, int]:
    if facing == "down":
        return TILE * scale, tiles * TILE * scale
    return tiles * TILE * scale, TILE * scale


class TimelineSheet:
    """Deterministic sheet builder that records every creature cell."""

    def __init__(
        self,
        anticipation_dir: Path,
        attack_dir: Path,
        walk_dir: Path,
        idle_dir: Path,
        reference: dict,
    ):
        self.reference = reference
        self.plan = build_plan(reference)
        self.exp_plan = build_exp_plan(reference)
        self.flash_rgb = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        self.flicker_period = reference["feedback_states"]["hurt_flash"][
            "flicker_period_frames"
        ]
        self.poses = {
            facing: load_poses(anticipation_dir, attack_dir, walk_dir, idle_dir, facing)
            for facing in FACINGS
        }
        self.cells: list[dict] = []

    # -- geometry -----------------------------------------------------------

    def sheet_width(self) -> int:
        attack_cols = len(self.plan["attack_ticks"])
        widest = attack_cols * (cell_size("right", 2)[0] + GUTTER)
        return MARGIN_LEFT + widest + MARGIN_TOP

    def facing_height(self, facing: str) -> int:
        header = 8 + GUTTER
        ruler = 16 + GUTTER
        h2 = cell_size(facing, 2)[1]
        total = header
        total += ruler + 2 * (h2 + GUTTER)  # approach rows
        total += ruler + 4 * (h2 + GUTTER)  # attack rows
        if facing == "down":
            total += 8 + ruler + h2 + GUTTER  # EXP note + ruler + row
        total += 8 + ruler + 2 * (TILE + GUTTER)  # flicker note + labels + rows
        total += ruler + cell_size(facing, 2, TWOX_SCALE)[1] + GUTTER  # 2x row
        grammar_h = 2 * TILE if facing == "down" else TILE
        total += ruler + grammar_h + GUTTER
        return total

    # -- cells --------------------------------------------------------------

    def record(self, **cell) -> None:
        self.cells.append(cell)

    def window_cell(
        self,
        cv: Rgba8Canvas,
        x: int,
        y: int,
        zone_key: str,
        facing: str,
        tiles: int,
        pose: str,
        win_px: int,
        *,
        section: str,
        timeline: str,
        tick: int,
        phase: str,
        treatment: str = "none",
        scale: int = 1,
    ) -> None:
        zone = self.reference["zones"][zone_key]
        sprite = treat(self.poses[facing][pose], treatment, self.flash_rgb)
        composed = compose_window(zone, facing, tiles, sprite, win_px)
        w, h = cell_size(facing, tiles, scale)
        if scale == 1:
            for px, py, rgb in canvas_pixels(composed):
                cv.put(x + px, y + py, (*rgb, 255))
        else:
            cv.blit_scaled(canvas_pixels(composed), x, y, scale)
        self.record(
            section=section, facing=facing, zone=zone_key, timeline=timeline,
            tick=tick, phase=phase, pose=pose, treatment=treatment,
            window_tiles=tiles, win_px=win_px, scale=scale, rect=[x, y, w, h],
        )

    # -- rows ---------------------------------------------------------------

    def ruler(self, cv, y: int, ticks: list[dict], step_w: int, prefix: str) -> None:
        previous_phase = None
        for index, tick in enumerate(ticks):
            x = MARGIN_LEFT + index * step_w
            label = f"{prefix}{tick['tick']:02d}"
            draw_text(cv, x, y, label)
            if tick["phase"] != previous_phase:
                draw_text(cv, x, y - 8, PHASE_LABELS[tick["phase"]])
                previous_phase = tick["phase"]

    def approach_rows(self, cv, y: int, facing: str) -> int:
        ticks = self.plan["approach_ticks"]
        w, h = cell_size(facing, 2)
        step_w = w + GUTTER
        self.ruler(cv, y + 8, ticks, step_w, "T")
        y += 16 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + h // 2 - 2, f"{zone_label} WALK")
            for index, tick in enumerate(ticks):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, facing, 2,
                    tick["pose_a"], tick["axis_px"],
                    section="approach", timeline="AB", tick=tick["tick"],
                    phase=tick["phase"],
                )
            y += h + GUTTER
        return y

    def attack_rows(self, cv, y: int, facing: str) -> int:
        ticks = self.plan["attack_ticks"]
        w, h = cell_size(facing, 2)
        step_w = w + GUTTER
        self.ruler(cv, y + 8, ticks, step_w, "T")
        y += 16 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            for timeline in ("A", "B"):
                draw_text(cv, 2, y + h // 2 - 2, f"{zone_label} {timeline}")
                pose_key = "pose_a" if timeline == "A" else "pose_b"
                for index, tick in enumerate(ticks):
                    self.window_cell(
                        cv, MARGIN_LEFT + index * step_w, y, zone_key, facing, 2,
                        tick[pose_key], tick["axis_px"] - TILE,
                        section="attack", timeline=timeline, tick=tick["tick"],
                        phase=tick["phase"],
                    )
                y += h + GUTTER
        return y

    def exp_row(self, cv, y: int, facing: str) -> int:
        ticks = self.exp_plan["ticks"]
        w, h = cell_size(facing, 2)
        step_w = w + GUTTER
        draw_text(
            cv, MARGIN_LEFT, y,
            f"EXP B WINDUP {self.exp_plan['windup_ticks']} TICKS KB BAND NOT RUNTIME",
        )
        y += 8
        self.ruler(cv, y + 8, ticks, step_w, "E")
        y += 16 + GUTTER
        draw_text(cv, 2, y + h // 2 - 2, "EXP B")
        for index, tick in enumerate(ticks):
            self.window_cell(
                cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 2,
                tick["pose_b"], tick["offset_px"],
                section="exp", timeline="B", tick=tick["tick"], phase=tick["phase"],
            )
        return y + h + GUTTER

    def flicker_rows(self, cv, y: int, facing: str) -> int:
        period = self.flicker_period
        step_w = TILE + GUTTER
        draw_text(
            cv, MARGIN_LEFT, y,
            f"HURT FLICKER {period} ON {period} OFF PINNED CADENCE IDLE HELD",
        )
        y += 8
        for index in range(FLICKER_TICKS):
            draw_text(cv, MARGIN_LEFT + index * step_w, y + 8, f"H{index:02d}")
        y += 16 + GUTTER
        for row_label, on_treatment in (("ACC", "acc"), ("FLASH", "flash")):
            draw_text(cv, 2, y + TILE // 2 - 2, row_label)
            for index in range(FLICKER_TICKS):
                treatment = on_treatment if flicker_on(index, period) else "none"
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 1,
                    "idle", 0,
                    section="flicker", timeline=row_label, tick=index,
                    phase="on" if flicker_on(index, period) else "off",
                    treatment=treatment,
                )
            y += TILE + GUTTER
        return y

    def twox_row(self, cv, y: int, facing: str) -> int:
        transitions = self.transition_ticks()
        w, h = cell_size(facing, 2, TWOX_SCALE)
        step_w = w + GUTTER
        for index, tick in enumerate(transitions):
            draw_text(cv, MARGIN_LEFT + index * step_w, y + 8, f"T{tick['tick']:02d}")
        y += 16 + GUTTER
        draw_text(cv, 2, y + h // 2 - 2, "2X B")
        for index, tick in enumerate(transitions):
            self.window_cell(
                cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 2,
                tick["pose_b"], tick["axis_px"] - TILE,
                section="twox", timeline="B", tick=tick["tick"],
                phase=tick["phase"], scale=TWOX_SCALE,
            )
        return y + h + GUTTER

    def transition_ticks(self) -> list[dict]:
        """Last windup, first active, last active, first recovery."""
        ticks = self.plan["ticks"]
        windup = [t for t in ticks if t["phase"] == "windup"]
        active = [t for t in ticks if t["phase"] == "active"]
        recovery = [t for t in ticks if t["phase"] == "recovery"]
        return [windup[-1], active[0], active[-1], recovery[0]]

    def grammar_row(self, cv, y: int, facing: str) -> int:
        """The static v3 grammar control row via the banked tell_cell."""
        zone1 = self.reference["zones"]["zone_1"]
        lunge = self.reference["feedback_states"]["lunge_offset"]
        cell_w = TILE if facing == "down" else 2 * TILE
        cell_h = 2 * TILE if facing == "down" else TILE
        cells = (
            ("IDLE", "idle", 0),
            ("F1", "f1", 0),
            ("A0", "a0", 0),
            ("WIND", "a0", lunge["windup_px"]),
            ("K0", "k0", 0),
            ("LUNGE", "k0", lunge["active_px"]),
        )
        for index, (label, _, _) in enumerate(cells):
            draw_text(cv, MARGIN_LEFT + index * (cell_w + GUTTER), y + 8, label)
        y += 16 + GUTTER
        draw_text(cv, 2, y + cell_h // 2 - 2, "GRAMMAR")
        for index, (label, pose, offset) in enumerate(cells):
            x = MARGIN_LEFT + index * (cell_w + GUTTER)
            tell_cell(cv, x, y, zone1, facing, self.poses[facing][pose], offset)
            self.record(
                section="grammar", facing=facing, zone="zone_1", timeline="STATIC",
                tick=index, phase=label.lower(), pose=pose, treatment="none",
                window_tiles=2, win_px=offset, scale=1,
                rect=[x, y, cell_w, cell_h],
            )
        return y + cell_h + GUTTER

    # -- assembly -----------------------------------------------------------

    def build(self) -> Rgba8Canvas:
        self.cells = []
        width = self.sheet_width()
        height = (
            MARGIN_TOP
            + sum(self.facing_height(facing) + GUTTER for facing in FACINGS)
            + MARGIN_TOP
        )
        cv = Rgba8Canvas(width, height, BG)
        y = MARGIN_TOP
        for facing in FACINGS:
            draw_text(cv, 2, y, facing.upper())
            y += 8 + GUTTER
            y = self.approach_rows(cv, y, facing)
            y = self.attack_rows(cv, y, facing)
            if facing == "down":
                y = self.exp_row(cv, y, facing)
            y = self.flicker_rows(cv, y, facing)
            y = self.twox_row(cv, y, facing)
            y = self.grammar_row(cv, y, facing) + GUTTER
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _scanlines(cv: Rgba8Canvas) -> bytes:
    raw = bytearray()
    for y in range(cv.height):
        raw.append(0)
        for x in range(cv.width):
            raw.extend(cv.get(x, y))
    return zlib.compress(bytes(raw), level=9)


def encode_apng(frames: list[Rgba8Canvas], delays: list[tuple[int, int]]) -> bytes:
    """Minimal deterministic APNG: acTL + fcTL/IDAT + fcTL/fdAT, no ancillary
    chunks, infinite loop, full-frame replace on every frame."""
    if not frames or len(frames) != len(delays):
        raise ValueError("frames and delays must be non-empty and equal length")
    first = frames[0]
    if any((f.width, f.height) != (first.width, first.height) for f in frames):
        raise ValueError("APNG frames must share one size")
    header = struct.pack(">IIBBBBB", first.width, first.height, 8, 6, 0, 0, 0)
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += _chunk(b"IHDR", header)
    out += _chunk(b"acTL", struct.pack(">II", len(frames), 0))
    sequence = 0
    for index, (frame, (num, den)) in enumerate(zip(frames, delays)):
        fctl = struct.pack(
            ">IIIIIHHBB", sequence, frame.width, frame.height, 0, 0, num, den, 0, 0
        )
        out += _chunk(b"fcTL", fctl)
        sequence += 1
        data = _scanlines(frame)
        if index == 0:
            out += _chunk(b"IDAT", data)
        else:
            out += _chunk(b"fdAT", struct.pack(">I", sequence) + data)
            sequence += 1
    out += _chunk(b"IEND", b"")
    return bytes(out)


def build_apng_frames(sheet: TimelineSheet, facing: str) -> list[Rgba8Canvas]:
    """Per tick: timelines A and B side by side over a 3-tile window, 4x NN."""
    zone = sheet.reference["zones"]["zone_1"]
    frames = []
    for tick in sheet.plan["ticks"]:
        panes = []
        for key, tag in (("pose_a", "A"), ("pose_b", "B")):
            pane = compose_window(
                zone, facing, 3, sheet.poses[facing][tick[key]], tick["axis_px"]
            )
            draw_text(pane, 2, 2, tag)
            panes.append(pane)
        if facing == "down":
            frame = Rgba8Canvas(
                (TILE * 2 + GUTTER) * APNG_SCALE, TILE * 3 * APNG_SCALE, BG
            )
            offsets = ((0, 0), ((TILE + GUTTER) * APNG_SCALE, 0))
        else:
            frame = Rgba8Canvas(
                TILE * 3 * APNG_SCALE, (TILE * 2 + GUTTER) * APNG_SCALE, BG
            )
            offsets = ((0, 0), (0, (TILE + GUTTER) * APNG_SCALE))
        for pane, (ox, oy) in zip(panes, offsets):
            frame.blit_scaled(canvas_pixels(pane), ox, oy, APNG_SCALE)
        frames.append(frame)
    return frames


def apng_delays(count: int) -> list[tuple[int, int]]:
    return [APNG_TICK_DELAY] * (count - 1) + [APNG_LAST_DELAY]


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
        default=ROOT / "reviews" / "calibration-v4" / "timeline-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write timeline-ab-<facing>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = TimelineSheet(
        args.anticipation_exports, args.attack_exports, args.walk_exports,
        args.idle_exports, reference,
    )
    canvas = sheet.build()
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for facing in FACINGS:
            frames = build_apng_frames(sheet, facing)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"timeline-ab-{facing}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
