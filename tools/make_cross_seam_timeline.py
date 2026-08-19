#!/usr/bin/env python3
"""Tick-accurate cross-facing onset-seam timeline sheet (sprint 9, calibration-v9).

Measurement sprint: ZERO new frames. The engine legally re-faces a mid-tween
creature on the same controller tick the attack starts (controllers.rb L52
face -> L64 start_attack; creature.rb face L142-144 unconditional; verified at
the pinned commit), so the walk->attack onset cut can be a simultaneous
state-and-facing swap: fN(facing A) -> w0(facing B). Ten pre-registered lanes
render the class from frozen banked bytes only:

- Pair DR (walk DOWN, attack RIGHT) and pair RD (walk RIGHT, attack DOWN),
  each at the four banked onset classes: EARLY t03 (REM 11), MID t06 (REM 8),
  LATE t10 (REM 4), CONTROL t15 (REM 0 - the stationary cross-facing onset,
  itself unmeasured).
- DEGEN lanes (DR section: down/down; RD section: right/right): the 2D
  toolchain degenerated to along-facing, which must reproduce the committed
  calibration-v8 CONTROL jump-table rows exactly (the hard regression bar,
  enforced by tools/cross_seam_metrics.py).

Drawing model (pre-registered in reviews/calibration-v9/rationale.md): the
banked v7-winner grammar - windup w0 x1 + a0 x4 at -3, active k0 x4 at +6,
recovery s0 x1 + r0 x6 + x0 x1 at 0 - drawn in the creature's CURRENT facing
(A on pre-onset walk ticks, B from the onset tick); draw position = 2D vector:
smoothstep tween along the walk axis A + lunge offset along the attack facing
B. Cross-lane windows are 2 A-tiles x 3 B-tiles [back | creature | arc], sized
so every opaque pixel is in-bounds by construction ([2,2,29,29] contract) and
both candidate strike tiles (NEAR = T0+B, TRUE arc = T1+B) are visible with
grid lines; degenerate lanes use the banked v8 3-tile axis window.

Sheet rows per pair section (1 column = 1 tick):

- Per lane: RULER (absolute tick indices + phase labels) + Z1/Z2 rows of the
  16 ticks onset-2 .. onset+13 over the lane window.
- ONSET 2X: per lane, onset-1 | onset | onset+1 (the fN@A | w0@B | a0@B seam),
  cropped to the 2x2-tile [back|creature]x[T0|T1] sub-window (the onset event
  never reaches the arc column; the crop is recorded in the manifest).
- RELEASE 2X: per lane, onset+4 | onset+5 (the a0 -> k0 event), FULL window so
  the arc-side grid line and both candidate tiles stay visible.
- FILM: the banked eleven-column static strip, both facings (identity anchor).

Every creature cell is recorded in a machine-readable manifest consumed by
tools/cross_seam_metrics.py for composition-purity, in-bounds, and tick-math
verification. Layout is fixed; regeneration is byte-identical. Banked tools
are imported unmodified. Optional APNG aids (cross-lanes-<pair>.apng: the four
cross lanes side by side, full t00..t33, exact 1/60 s per-frame delay, 4x NN)
are never blocking; the degenerate lanes are v8's CONTROL, already animated in
the banked v8 aids.
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
    MARGIN_LEFT,
    MARGIN_TOP,
    TILE,
    Sprite,
    draw_floor_tile,
    load_reference,
    sprite_from_png,
)
from make_grammar_timeline import (  # noqa: E402
    IDLE_PRE_TICKS,
    PHASE_LABELS,
    apng_delays,
    canvas_pixels,
    encode_apng,
    walk_frame_index,
)
import make_seam_timeline as seam  # noqa: E402
from make_seam_timeline import (  # noqa: E402
    ONSET_TICKS,
    POSE_DIRS,
    STRIP,
    TOTAL_TICKS,
    draw_text,
    default_dirs,
    pose_filename,
    tween_position,
)
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
FACINGS = seam.FACINGS
PAIRS = ("DR", "RD")
PAIR_AXES = {"DR": ("down", "right"), "RD": ("right", "down")}
CROSS_LANES = ("EARLY", "MID", "LATE", "CONTROL")
SECTION_LANES = CROSS_LANES + ("DEGEN",)
DEGEN_ONSET = ONSET_TICKS["CONTROL"]
ARRIVAL_TICK = seam.ARRIVAL_TICK
LANE_PRE_TICKS = 2
LANE_SPAN = 16
TWOX_SCALE = 2
APNG_SCALE = 4
CONTRACT_BOUNDS = (2, 29)  # opaque-pixel bounds of the export contract


def lane_axes(pair: str, lane: str) -> tuple[str, str]:
    """(walk_facing, attack_facing) for one lane of one pair section."""
    walk, attack = PAIR_AXES[pair]
    if lane == "DEGEN":
        return walk, walk
    return walk, attack


def lane_onset(lane: str) -> int:
    return DEGEN_ONSET if lane == "DEGEN" else ONSET_TICKS[lane]


def window_spec(walk_facing: str, attack_facing: str) -> dict:
    """The lane's uniform window. Cross lanes: 2 A-tiles x 3 B-tiles
    [back | creature | arc]; degenerate lanes: the banked v8 3-tile axis
    window. Tile spans are window-coordinate pixel ranges (inclusive)."""
    if walk_facing == attack_facing:
        if walk_facing == "down":
            return {
                "kind": "degen", "w": TILE, "h": 3 * TILE,
                "a_axis": "y", "b_axis": "y",
                "true_arc_a_span": [2 * TILE, 3 * TILE - 1],
                "near_a_span": None, "grid_line_b": 2 * TILE,
            }
        return {
            "kind": "degen", "w": 3 * TILE, "h": TILE,
            "a_axis": "x", "b_axis": "x",
            "true_arc_a_span": [2 * TILE, 3 * TILE - 1],
            "near_a_span": None, "grid_line_b": 2 * TILE,
        }
    if walk_facing == "down":  # DR: A = y (down), B = x (right)
        return {
            "kind": "cross", "w": 3 * TILE, "h": 2 * TILE,
            "a_axis": "y", "b_axis": "x",
            "true_arc_a_span": [TILE, 2 * TILE - 1],
            "near_a_span": [0, TILE - 1], "grid_line_b": 2 * TILE,
        }
    return {  # RD: A = x (right), B = y (down)
        "kind": "cross", "w": 2 * TILE, "h": 3 * TILE,
        "a_axis": "x", "b_axis": "y",
        "true_arc_a_span": [TILE, 2 * TILE - 1],
        "near_a_span": [0, TILE - 1], "grid_line_b": 2 * TILE,
    }


def onset_crop(walk_facing: str, attack_facing: str) -> tuple[int, int]:
    """The onset-strip sub-window (origin-preserving crop): cross lanes drop
    the arc column/row (2x2 tiles); degenerate lanes use the banked v8
    2-tile [from | landing] crop."""
    if walk_facing == attack_facing:
        return (TILE, 2 * TILE) if walk_facing == "down" else (2 * TILE, TILE)
    return (2 * TILE, 2 * TILE)


def draw_vector(
    walk_facing: str, attack_facing: str, a_px: int, offset_px: int
) -> tuple[int, int]:
    """Canvas-origin draw position in window coordinates: tween along A,
    tile-centered along B (baseline TILE for cross lanes), + offset along B."""
    if walk_facing == attack_facing:
        if walk_facing == "down":
            return (0, a_px + offset_px)
        return (a_px + offset_px, 0)
    if walk_facing == "down":
        return (TILE + offset_px, a_px)
    return (a_px, TILE + offset_px)


def lane_tick(
    tick: int, onset: int, walk_facing: str, attack_facing: str, reference: dict
) -> dict:
    """Pose + facing + 2D position for one absolute tick of one lane - a pure
    function of the pinned constants, the pre-registered onset tick, the pair
    axes, and the declared drawing model."""
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    step = timing["step_frames"]["value"]

    a_px = tween_position(tick - 1, step) if tick >= 1 else 0
    if tick < onset:
        if tick < IDLE_PRE_TICKS:
            phase, pose, facing, offset = "idle_pre", "idle", walk_facing, 0
        else:
            phase = "walk"
            pose = f"f{walk_frame_index(tick - 1, step)}"
            facing, offset = walk_facing, 0
    else:
        into = tick - onset
        facing = attack_facing
        if into < windup:
            phase = "windup"
            pose = seam.WINDUP_INBETWEEN if into == 0 else seam.WINDUP_POSE
            offset = lunge["windup_px"]
        elif into < windup + active:
            phase, pose, offset = "active", "k0", lunge["active_px"]
        elif into < windup + active + recovery:
            rec = into - windup - active
            phase = "recovery"
            if rec == 0:
                pose = seam.SETTLE_INBETWEEN
            elif rec == recovery - 1:
                pose = seam.RISE_INBETWEEN
            else:
                pose = seam.RECOVERY_POSE
            offset = 0
        else:
            phase, pose, offset = "idle_post", "idle", 0
    x, y = draw_vector(walk_facing, attack_facing, a_px, offset)
    return {
        "tick": tick, "phase": phase, "pose": pose, "pose_facing": facing,
        "a_px": a_px, "offset_px": offset, "draw": [x, y],
    }


def build_plan(reference: dict) -> dict:
    """The ten-lane 2D tick plan. Every lane runs t00..t33; the sheet rows
    show onset-2 .. onset+13 per lane; the jump tables are sliced by
    tools/cross_seam_metrics.py."""
    timing = reference["attack_timing"]["values"]
    step = timing["step_frames"]["value"]
    pairs: dict[str, dict] = {}
    for pair in PAIRS:
        walk, attack = PAIR_AXES[pair]
        lanes: dict[str, dict] = {}
        for lane in SECTION_LANES:
            lane_walk, lane_attack = lane_axes(pair, lane)
            onset = lane_onset(lane)
            ticks = [
                lane_tick(t, onset, lane_walk, lane_attack, reference)
                for t in range(TOTAL_TICKS)
            ]
            lanes[lane] = {
                "onset_tick": onset,
                "rem_after_onset": max(0, step - (onset - 1)),
                "arrival_tick": ARRIVAL_TICK,
                "walk_facing": lane_walk,
                "attack_facing": lane_attack,
                "window": window_spec(lane_walk, lane_attack),
                "onset_crop": list(onset_crop(lane_walk, lane_attack)),
                "ticks": ticks,
                "sheet_ticks": ticks[
                    onset - LANE_PRE_TICKS: onset - LANE_PRE_TICKS + LANE_SPAN
                ],
            }
        pairs[pair] = {
            "walk_facing": walk, "attack_facing": attack, "lanes": lanes,
        }
    return {
        "constants": {
            "windup_frames": timing["windup_frames"]["value"],
            "active_frames": timing["active_frames"]["value"],
            "recovery_frames": timing["recovery_frames"]["value"],
            "step_frames": step,
            "windup_px": reference["feedback_states"]["lunge_offset"]["windup_px"],
            "active_px": reference["feedback_states"]["lunge_offset"]["active_px"],
            "arrival_tick": ARRIVAL_TICK,
            "onset_ticks": {**ONSET_TICKS, "DEGEN": DEGEN_ONSET},
            "pair_axes": {pair: list(PAIR_AXES[pair]) for pair in PAIRS},
        },
        "pairs": pairs,
    }


def onset_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """onset-1 | onset | onset+1 - the fN@A | w0@B | a0@B seam region."""
    data = plan["pairs"][pair]["lanes"][lane]
    onset = data["onset_tick"]
    return [data["ticks"][onset - 1], data["ticks"][onset], data["ticks"][onset + 1]]


def release_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """onset+4 | onset+5 - the a0 -> k0 release event."""
    data = plan["pairs"][pair]["lanes"][lane]
    onset = data["onset_tick"]
    return [data["ticks"][onset + 4], data["ticks"][onset + 5]]


def load_poses(dirs: dict[str, Path]) -> dict[str, dict[str, Sprite]]:
    return {
        facing: {
            pose: sprite_from_png(dirs[POSE_DIRS[pose]] / pose_filename(pose, facing))
            for pose in STRIP
        }
        for facing in FACINGS
    }


def compose_cell(
    zone: dict, width: int, height: int, sprite: Sprite, dx: int, dy: int
) -> Rgba8Canvas:
    """One 1x window cell: grid-lined floor tiles filling the window, the
    sprite canvas blitted at the integer draw vector."""
    cv = Rgba8Canvas(width, height, BG)
    for ty in range(height // TILE):
        for tx in range(width // TILE):
            draw_floor_tile(cv, tx * TILE, ty * TILE, zone)
    base.blit_sprite(cv, sprite, dx, dy)
    return cv


class CrossSeamSheet:
    """Deterministic sheet builder that records every creature cell."""

    def __init__(self, dirs: dict[str, Path], reference: dict):
        self.dirs = dirs
        self.reference = reference
        self.plan = build_plan(reference)
        self.poses = load_poses(dirs)
        self.cells: list[dict] = []

    # -- geometry -----------------------------------------------------------

    def lane_row_width(self, pair: str, lane: str) -> int:
        window = self.plan["pairs"][pair]["lanes"][lane]["window"]
        return LANE_SPAN * (window["w"] + GUTTER)

    def onset_row_width(self, pair: str) -> int:
        total = 0
        for lane in SECTION_LANES:
            crop_w, _ = self.plan["pairs"][pair]["lanes"][lane]["onset_crop"]
            total += 3 * (crop_w * TWOX_SCALE + GUTTER)
        return total + (len(SECTION_LANES) - 1) * GUTTER

    def release_row_width(self, pair: str) -> int:
        total = 0
        for lane in SECTION_LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += 2 * (window["w"] * TWOX_SCALE + GUTTER)
        return total + (len(SECTION_LANES) - 1) * GUTTER

    def sheet_width(self) -> int:
        widths = [11 * (TILE + GUTTER)]
        for pair in PAIRS:
            widths.append(self.onset_row_width(pair))
            widths.append(self.release_row_width(pair))
            for lane in SECTION_LANES:
                widths.append(self.lane_row_width(pair, lane))
        return MARGIN_LEFT + max(widths) + MARGIN_TOP

    def section_height(self, pair: str) -> int:
        total = 8 + GUTTER  # section header
        for lane in SECTION_LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += 8 + 16 + GUTTER + 2 * (window["h"] + GUTTER)
        onset_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["onset_crop"][1]
            for lane in SECTION_LANES
        ) * TWOX_SCALE
        release_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["window"]["h"]
            for lane in SECTION_LANES
        ) * TWOX_SCALE
        total += 8 + 8 + GUTTER + onset_h + GUTTER
        total += 8 + 8 + GUTTER + release_h + GUTTER
        return total

    def film_height(self) -> int:
        return len(FACINGS) * (8 + 8 + GUTTER + 2 * (TILE + GUTTER))

    # -- cells --------------------------------------------------------------

    def record(self, **cell) -> None:
        self.cells.append(cell)

    def window_cell(
        self, cv: Rgba8Canvas, x: int, y: int, zone_key: str, tick: dict, *,
        section: str, pair: str, lane: str, width: int, height: int,
        scale: int = 1,
    ) -> None:
        zone = self.reference["zones"][zone_key]
        sprite = self.poses[tick["pose_facing"]][tick["pose"]]
        dx, dy = tick["draw"]
        composed = compose_cell(zone, width, height, sprite, dx, dy)
        if scale == 1:
            for px, py, rgb in canvas_pixels(composed):
                cv.put(x + px, y + py, (*rgb, 255))
        else:
            cv.blit_scaled(canvas_pixels(composed), x, y, scale)
        self.record(
            section=section, pair=pair, lane=lane, zone=zone_key,
            tick=tick["tick"], phase=tick["phase"], pose=tick["pose"],
            pose_facing=tick["pose_facing"], window_w=width, window_h=height,
            draw=[dx, dy], scale=scale,
            rect=[x, y, width * scale, height * scale],
        )

    # -- rows ---------------------------------------------------------------

    def ruler(self, cv, y: int, ticks: list[dict], step_w: int) -> None:
        previous_phase = None
        for index, tick in enumerate(ticks):
            x = MARGIN_LEFT + index * step_w
            draw_text(cv, x, y, f"T{tick['tick']:02d}")
            if tick["phase"] != previous_phase:
                draw_text(cv, x, y - 8, PHASE_LABELS[tick["phase"]])
                previous_phase = tick["phase"]

    def lane_rows(self, cv, y: int, pair: str, lane: str) -> int:
        data = self.plan["pairs"][pair]["lanes"][lane]
        ticks = data["sheet_ticks"]
        window = data["window"]
        step_w = window["w"] + GUTTER
        label = f"{lane} ONSET T{data['onset_tick']:02d} REM {data['rem_after_onset']}"
        if lane == "DEGEN":
            label = f"DEGEN {data['walk_facing'][0].upper()} " + label[6:]
        draw_text(cv, MARGIN_LEFT, y, label)
        y += 8
        self.ruler(cv, y + 8, ticks, step_w)
        y += 16 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + window["h"] // 2 - 2, f"{zone_label} {lane[0]}")
            for index, tick in enumerate(ticks):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, tick,
                    section="lane", pair=pair, lane=lane,
                    width=window["w"], height=window["h"],
                )
            y += window["h"] + GUTTER
        return y

    def strip_row(self, cv, y: int, pair: str, section: str, label: str,
                  strip_of, crop: bool) -> int:
        row_h = 0
        for lane in SECTION_LANES:
            data = self.plan["pairs"][pair]["lanes"][lane]
            h = data["onset_crop"][1] if crop else data["window"]["h"]
            row_h = max(row_h, h * TWOX_SCALE)
        draw_text(cv, MARGIN_LEFT, y, label)
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + row_h // 2 - 2, f"{section.upper()[:3]} 2X")
        x = MARGIN_LEFT
        for lane in SECTION_LANES:
            data = self.plan["pairs"][pair]["lanes"][lane]
            if crop:
                w, h = data["onset_crop"]
            else:
                w, h = data["window"]["w"], data["window"]["h"]
            for tick in strip_of(self.plan, pair, lane):
                draw_text(cv, x, labels_y, f"{lane[0]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section=section, pair=pair, lane=lane,
                    width=w, height=h, scale=TWOX_SCALE,
                )
                x += w * TWOX_SCALE + GUTTER
            x += GUTTER
        return y + row_h + GUTTER

    def film_rows(self, cv, y: int, facing: str) -> int:
        draw_text(cv, MARGIN_LEFT, y, f"FILM {facing.upper()}")
        y += 8
        step_w = TILE + GUTTER
        for index, pose in enumerate(STRIP):
            draw_text(cv, MARGIN_LEFT + index * step_w, y, pose.upper())
        y += 8 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} FILM")
            for index, pose in enumerate(STRIP):
                tick = {
                    "tick": index, "phase": pose, "pose": pose,
                    "pose_facing": facing, "a_px": 0, "offset_px": 0,
                    "draw": [0, 0],
                }
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, tick,
                    section="film", pair="STATIC", lane=facing.upper(),
                    width=TILE, height=TILE,
                )
            y += TILE + GUTTER
        return y

    # -- assembly -----------------------------------------------------------

    def build(self) -> Rgba8Canvas:
        self.cells = []
        width = self.sheet_width()
        height = (
            MARGIN_TOP
            + sum(self.section_height(pair) + GUTTER for pair in PAIRS)
            + self.film_height()
            + MARGIN_TOP
        )
        cv = Rgba8Canvas(width, height, BG)
        y = MARGIN_TOP
        for pair in PAIRS:
            walk, attack = PAIR_AXES[pair]
            draw_text(
                cv, 2, y,
                f"PAIR {pair} WALK {walk.upper()} ATTACK {attack.upper()}",
            )
            y += 8 + GUTTER
            for lane in SECTION_LANES:
                y = self.lane_rows(cv, y, pair, lane)
            y = self.strip_row(cv, y, pair, "onset", "ONSET SEAM 2X FN W0 A0",
                               onset_strip, crop=True)
            y = self.strip_row(cv, y, pair, "release", "RELEASE 2X A0 K0",
                               release_strip, crop=False)
            y += GUTTER
        for facing in FACINGS:
            y = self.film_rows(cv, y, facing)
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: CrossSeamSheet, pair: str) -> list[Rgba8Canvas]:
    """Per tick t00..t33: the four CROSS lanes side by side over their full
    windows (the degenerate lane is v8's CONTROL, animated in the banked v8
    aids)."""
    zone = sheet.reference["zones"]["zone_1"]
    window = sheet.plan["pairs"][pair]["lanes"]["EARLY"]["window"]
    frames = []
    for t in range(TOTAL_TICKS):
        frame = Rgba8Canvas(
            (window["w"] * len(CROSS_LANES) + GUTTER * (len(CROSS_LANES) - 1))
            * APNG_SCALE,
            window["h"] * APNG_SCALE, BG,
        )
        for index, lane in enumerate(CROSS_LANES):
            tick = sheet.plan["pairs"][pair]["lanes"][lane]["ticks"][t]
            pane = compose_cell(
                zone, window["w"], window["h"],
                sheet.poses[tick["pose_facing"]][tick["pose"]],
                tick["draw"][0], tick["draw"][1],
            )
            draw_text(pane, 2, 2, lane[0])
            frame.blit_scaled(
                canvas_pixels(pane),
                (window["w"] + GUTTER) * APNG_SCALE * index, 0, APNG_SCALE,
            )
        frames.append(frame)
    return frames


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = default_dirs()
    for key, value in defaults.items():
        flag = "--" + key.replace("_dir", "-exports").replace("_", "-")
        parser.add_argument(flag, dest=key, type=Path, default=value)
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "manifests" / "render-reference.json"
    )
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v9" / "cross-seam-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write cross-lanes-<pair>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    sheet = CrossSeamSheet(dirs, reference)
    canvas = sheet.build()
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for pair in PAIRS:
            frames = build_apng_frames(sheet, pair)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"cross-lanes-{pair.lower()}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
