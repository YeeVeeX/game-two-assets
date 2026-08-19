#!/usr/bin/env python3
"""Tick-accurate pure-turn timeline sheet (sprint 10, calibration-v10).

Measurement sprint: ZERO new frames, zero exports, no attack anywhere. The
engine legally re-faces a mid-tween creature on any controller tick
(controllers.rb L51-52 unconditional face on the move path; creature.rb face
L142-144; grid_walker.rb L36 refuses the step while moving?, L90-97 tween is
facing-blind with no snap; renderer.rb L520-531 reads facing live at every
draw - all verified at the pinned commit). Holding B while walking A
re-faces mid-tween, the tween finishes along A (a strafe segment), and the B
step begins at arrival (B commits at t14's controller for moving lanes; at
t15 for CONTROL). Ten pre-registered lanes render the class from frozen
banked bytes only:

- Pair DR (walk DOWN, turn RIGHT) and pair RD (walk RIGHT, turn DOWN), each
  at the four banked onset ticks reused as TURN ticks: EARLY t03 (REM 11),
  MID t06 (REM 8), LATE t10 (REM 4), CONTROL t15 (arrival+1, REM 0).
- DEGEN lanes (DR section: two-step walk DOWN; RD section: two-step walk
  RIGHT): the uncut twin of every same-facing row, wrap included.

Drawing model (pre-registered in reviews/calibration-v10/rationale.md): the
banked v1 walk mapping f0x4/f1x3/f2x3/f3x3 over each step's 13 advances;
step-commit ticks draw the standing pose (banked t01 idle precedent; CONTROL
t15 draws idle@B); a mid-tween re-face swaps the FACING of the drawn walk
frame from the turn tick on while the frame INDEX continues from step
progress; the B step's frames restart at f0. Draw position = 2D tween, no
offset anywhere (lunge_offset is [0,0] outside attacks - engine fact).

Sheet rows per pair section (1 column = 1 tick, t01..t21):

- Per lane: label + RULER (absolute ticks + phase labels) + Z1/Z2 rows over
  the lane window (turn lanes: 2x2 tiles [T0,T0+B | T1,T2]; degenerate
  lanes: the banked 3-tile axis window).
- TURN 3X: per turn lane, turn-1 | turn | turn+1, cropped to the A-tile pair
  at B-column 0 (the turn event never leaves it; crop recorded in the
  manifest).
- WRAP 2X: per lane, t13..t16 (CONTROL t14..t17) - the arrival wrap and the
  B-step restart, FULL window.
- CONTEXT 2X: the rendered stationary yardstick - [fN@A | fN@B] for
  f0..f3 + idle over one tile.
- FILM: the walk-pose identity strip (idle f0..f3), both facings, both
  zones.

Every creature cell is recorded in a machine-readable manifest consumed by
tools/turn_seam_metrics.py for composition-purity, in-bounds, and tick-math
verification. Layout is fixed; regeneration is byte-identical. Banked tools
are imported unmodified. Optional APNG aids (turn-lanes-<pair>.apng: the
four turn lanes side by side, full t00..t29, exact 1/60 s per-tick delay,
4x NN) are never blocking; the degenerate lanes' motion is the banked v1
walk, already animated in the banked v1 previews.
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
    load_reference,
    sprite_from_png,
)
from make_cross_seam_timeline import compose_cell  # noqa: E402
from make_grammar_timeline import (  # noqa: E402
    IDLE_PRE_TICKS,
    apng_delays,
    canvas_pixels,
    encode_apng,
    walk_frame_index,
)
from make_seam_timeline import (  # noqa: E402
    FACINGS,
    draw_text,
    default_dirs,
    pose_filename,
    tween_position,
)
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
PAIRS = ("DR", "RD")
PAIR_AXES = {"DR": ("down", "right"), "RD": ("right", "down")}
TURN_LANES = ("EARLY", "MID", "LATE", "CONTROL")
SECTION_LANES = TURN_LANES + ("DEGEN",)
TURN_TICKS = {"EARLY": 3, "MID": 6, "LATE": 10, "CONTROL": 15}
WALK_POSES = ("idle", "f0", "f1", "f2", "f3")  # the restricted strip: no attack
POSE_DIRS = {
    "idle": "idle_dir",
    "f0": "walk_dir", "f1": "walk_dir", "f2": "walk_dir", "f3": "walk_dir",
}
ARRIVAL_TICK = IDLE_PRE_TICKS - 1 + 13  # walk tick 13 draws at t14
TOTAL_TICKS = 30            # t00..t29 (CONTROL's B step arrives t28)
SHEET_START = 1             # lane rows show t01..t21
SHEET_SPAN = 21
WRAP_TICKS = 4              # wrap strips show 4 ticks from t13 (CONTROL t14)
TWOX_SCALE = 2
TURN_ZOOM_SCALE = 3
APNG_SCALE = 4
CONTRACT_BOUNDS = (2, 29)   # opaque-pixel bounds of the export contract
PHASE_LABELS = {
    "idle_pre": "PRE", "walk_a": "WALK A", "strafe": "STRAFE B",
    "turn_stand": "STAND B", "walk_b": "WALK B",
    "walk_1": "STEP 1", "walk_2": "STEP 2", "idle_post": "POST",
}


def lane_axes(pair: str, lane: str) -> tuple[str, str]:
    """(walk_facing, turn_facing) for one lane of one pair section."""
    walk, turn = PAIR_AXES[pair]
    if lane == "DEGEN":
        return walk, walk
    return walk, turn


def window_spec(walk_facing: str, turn_facing: str) -> dict:
    """Turn lanes: 2x2 tiles - the creature walks T0->T1 along A then
    T1->T2 along B; all four grid cells visible. Degenerate lanes: the
    banked 3-tile axis window (two steps along one axis). Tile spans are
    window-coordinate pixel ranges (inclusive) on the A axis."""
    if walk_facing == turn_facing:
        if walk_facing == "down":
            return {
                "kind": "degen", "w": TILE, "h": 3 * TILE,
                "a_axis": "y", "b_axis": "y",
                "t0_a_span": [0, TILE - 1],
                "t1_a_span": [TILE, 2 * TILE - 1],
                "t2_a_span": [2 * TILE, 3 * TILE - 1],
            }
        return {
            "kind": "degen", "w": 3 * TILE, "h": TILE,
            "a_axis": "x", "b_axis": "x",
            "t0_a_span": [0, TILE - 1],
            "t1_a_span": [TILE, 2 * TILE - 1],
            "t2_a_span": [2 * TILE, 3 * TILE - 1],
        }
    if walk_facing == "down":  # DR: A = y (down), B = x (right)
        return {
            "kind": "turn", "w": 2 * TILE, "h": 2 * TILE,
            "a_axis": "y", "b_axis": "x",
            "t0_a_span": [0, TILE - 1],
            "t1_a_span": [TILE, 2 * TILE - 1],
            "t2_a_span": [TILE, 2 * TILE - 1],
        }
    return {  # RD: A = x (right), B = y (down)
        "kind": "turn", "w": 2 * TILE, "h": 2 * TILE,
        "a_axis": "x", "b_axis": "y",
        "t0_a_span": [0, TILE - 1],
        "t1_a_span": [TILE, 2 * TILE - 1],
        "t2_a_span": [TILE, 2 * TILE - 1],
    }


def turn_crop(walk_facing: str, turn_facing: str) -> tuple[int, int] | None:
    """The 3x turn-zoom sub-window (origin-preserving crop): the A-tile pair
    at B-column 0 - every turn-1|turn|turn+1 draw stays inside it (asserted
    in-bounds by the validator). Degenerate lanes have no turn."""
    if walk_facing == turn_facing:
        return None
    if walk_facing == "down":
        return (TILE, 2 * TILE)
    return (2 * TILE, TILE)


def draw_vector(
    walk_facing: str, turn_facing: str, a_px: int, b_px: int
) -> tuple[int, int]:
    """Canvas-origin draw position in window coordinates: A-step tween along
    A, B-step tween along B; degenerate lanes carry one along-axis total."""
    if walk_facing == turn_facing:
        total = a_px + b_px
        return (0, total) if walk_facing == "down" else (total, 0)
    if walk_facing == "down":
        return (b_px, a_px)
    return (a_px, b_px)


def lane_tick(
    tick: int, turn: int | None, walk_facing: str, turn_facing: str, step: int
) -> dict:
    """Pose + facing + 2D position for one absolute tick of one lane - a
    pure function of the pinned constants, the pre-registered turn tick, the
    pair axes, and the declared drawing model (rationale, drawing-model
    section). turn=None is the degenerate two-step lane."""
    a_px = tween_position(tick - 1, step)
    commit_b = ARRIVAL_TICK + 1 if turn == ARRIVAL_TICK + 1 else ARRIVAL_TICK
    b_px = tween_position(tick - commit_b, step)
    if turn is None:  # DEGEN: continuous second step along A, facing A
        facing = walk_facing
        if tick < IDLE_PRE_TICKS:
            phase, pose = "idle_pre", "idle"
        elif tick <= ARRIVAL_TICK:
            phase, pose = "walk_1", f"f{walk_frame_index(tick - 1, step)}"
        elif tick <= ARRIVAL_TICK + step:
            phase = "walk_2"
            pose = f"f{walk_frame_index(tick - ARRIVAL_TICK, step)}"
        else:
            phase, pose = "idle_post", "idle"
    else:
        facing = walk_facing if tick < turn else turn_facing
        if tick < IDLE_PRE_TICKS:
            phase, pose = "idle_pre", "idle"
        elif tick <= ARRIVAL_TICK:
            phase = "walk_a" if tick < turn else "strafe"
            pose = f"f{walk_frame_index(tick - 1, step)}"
        elif tick == turn and turn == ARRIVAL_TICK + 1:
            phase, pose = "turn_stand", "idle"  # commit tick draws standing
        elif tick <= commit_b + step:
            phase = "walk_b"
            pose = f"f{walk_frame_index(tick - commit_b, step)}"
        else:
            phase, pose = "idle_post", "idle"
    x, y = draw_vector(walk_facing, turn_facing, a_px, b_px)
    return {
        "tick": tick, "phase": phase, "pose": pose, "pose_facing": facing,
        "a_px": a_px, "b_px": b_px, "draw": [x, y],
    }


def build_plan(reference: dict) -> dict:
    """The ten-lane pure-turn tick plan. Every lane runs t00..t29; the sheet
    rows show t01..t21; the jump tables are sliced by
    tools/turn_seam_metrics.py."""
    step = reference["attack_timing"]["values"]["step_frames"]["value"]
    pairs: dict[str, dict] = {}
    for pair in PAIRS:
        walk, turn_f = PAIR_AXES[pair]
        lanes: dict[str, dict] = {}
        for lane in SECTION_LANES:
            lane_walk, lane_turn = lane_axes(pair, lane)
            turn = None if lane == "DEGEN" else TURN_TICKS[lane]
            ticks = [
                lane_tick(t, turn, lane_walk, lane_turn, step)
                for t in range(TOTAL_TICKS)
            ]
            commit_b = (
                ARRIVAL_TICK + 1
                if turn == ARRIVAL_TICK + 1
                else ARRIVAL_TICK
            )
            lanes[lane] = {
                "turn_tick": turn,
                "rem_after_turn": (
                    None if turn is None else max(0, step - (turn - 1))
                ),
                "arrival_tick": ARRIVAL_TICK,
                "b_commit_tick": commit_b,
                "first_b_advance_tick": commit_b + 1,
                "walk_facing": lane_walk,
                "turn_facing": lane_turn,
                "window": window_spec(lane_walk, lane_turn),
                "turn_crop": (
                    None
                    if turn_crop(lane_walk, lane_turn) is None
                    else list(turn_crop(lane_walk, lane_turn))
                ),
                "ticks": ticks,
                "sheet_ticks": ticks[SHEET_START:SHEET_START + SHEET_SPAN],
            }
        pairs[pair] = {
            "walk_facing": walk, "turn_facing": turn_f, "lanes": lanes,
        }
    return {
        "constants": {
            "step_frames": step,
            "arrival_tick": ARRIVAL_TICK,
            "turn_ticks": dict(TURN_TICKS),
            "pair_axes": {pair: list(PAIR_AXES[pair]) for pair in PAIRS},
            "idle_pre_ticks": IDLE_PRE_TICKS,
            "total_ticks": TOTAL_TICKS,
            "sheet_span": [SHEET_START, SHEET_START + SHEET_SPAN - 1],
        },
        "pairs": pairs,
    }


def turn_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """turn-1 | turn | turn+1 - the fN@A | fN'@B seam region (turn lanes)."""
    data = plan["pairs"][pair]["lanes"][lane]
    turn = data["turn_tick"]
    return [data["ticks"][turn - 1], data["ticks"][turn], data["ticks"][turn + 1]]


def wrap_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """Four ticks bracketing the arrival wrap: t13..t16 (CONTROL t14..t17 -
    its wrap events sit one tick later: stand t15, restart t16)."""
    data = plan["pairs"][pair]["lanes"][lane]
    start = 14 if data["turn_tick"] == ARRIVAL_TICK + 1 else 13
    return data["ticks"][start:start + WRAP_TICKS]


def load_poses(dirs: dict[str, Path]) -> dict[str, dict[str, Sprite]]:
    return {
        facing: {
            pose: sprite_from_png(dirs[POSE_DIRS[pose]] / pose_filename(pose, facing))
            for pose in WALK_POSES
        }
        for facing in FACINGS
    }


class TurnTimelineSheet:
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
        return SHEET_SPAN * (window["w"] + GUTTER)

    def turn_row_width(self, pair: str) -> int:
        total = 0
        for lane in TURN_LANES:
            crop_w, _ = self.plan["pairs"][pair]["lanes"][lane]["turn_crop"]
            total += 3 * (crop_w * TURN_ZOOM_SCALE + GUTTER)
        return total + (len(TURN_LANES) - 1) * GUTTER

    def wrap_row_width(self, pair: str) -> int:
        total = 0
        for lane in SECTION_LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += WRAP_TICKS * (window["w"] * TWOX_SCALE + GUTTER)
        return total + (len(SECTION_LANES) - 1) * GUTTER

    def context_row_width(self) -> int:
        return len(WALK_POSES) * 2 * (TILE * TWOX_SCALE + GUTTER) + GUTTER * 4

    def sheet_width(self) -> int:
        widths = [len(WALK_POSES) * (TILE + GUTTER), self.context_row_width()]
        for pair in PAIRS:
            widths.append(self.turn_row_width(pair))
            widths.append(self.wrap_row_width(pair))
            for lane in SECTION_LANES:
                widths.append(self.lane_row_width(pair, lane))
        return MARGIN_LEFT + max(widths) + MARGIN_TOP

    def section_height(self, pair: str) -> int:
        total = 8 + GUTTER  # section header
        for lane in SECTION_LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += 8 + 16 + GUTTER + 2 * (window["h"] + GUTTER)
        turn_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["turn_crop"][1]
            for lane in TURN_LANES
        ) * TURN_ZOOM_SCALE
        wrap_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["window"]["h"]
            for lane in SECTION_LANES
        ) * TWOX_SCALE
        total += 8 + 8 + GUTTER + turn_h + GUTTER
        total += 8 + 8 + GUTTER + wrap_h + GUTTER
        total += 8 + 8 + GUTTER + TILE * TWOX_SCALE + GUTTER  # context row
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
        if lane == "DEGEN":
            label = f"DEGEN {data['walk_facing'][0].upper()} UNCUT 2 STEP"
        else:
            label = (
                f"{lane} TURN T{data['turn_tick']:02d} "
                f"REM {data['rem_after_turn']}"
            )
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

    def turn_zoom_row(self, cv, y: int, pair: str) -> int:
        row_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["turn_crop"][1]
            for lane in TURN_LANES
        ) * TURN_ZOOM_SCALE
        draw_text(cv, MARGIN_LEFT, y, "TURN SEAM 3X FN A TO FN B")
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + row_h // 2 - 2, "TRN 3X")
        x = MARGIN_LEFT
        for lane in TURN_LANES:
            data = self.plan["pairs"][pair]["lanes"][lane]
            w, h = data["turn_crop"]
            for tick in turn_strip(self.plan, pair, lane):
                draw_text(cv, x, labels_y, f"{lane[0]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section="turn", pair=pair, lane=lane,
                    width=w, height=h, scale=TURN_ZOOM_SCALE,
                )
                x += w * TURN_ZOOM_SCALE + GUTTER
            x += GUTTER
        return y + row_h + GUTTER

    def wrap_row(self, cv, y: int, pair: str) -> int:
        row_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["window"]["h"]
            for lane in SECTION_LANES
        ) * TWOX_SCALE
        draw_text(cv, MARGIN_LEFT, y, "WRAP 2X F3 TO F0 RESTART")
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + row_h // 2 - 2, "WRP 2X")
        x = MARGIN_LEFT
        for lane in SECTION_LANES:
            data = self.plan["pairs"][pair]["lanes"][lane]
            w, h = data["window"]["w"], data["window"]["h"]
            for tick in wrap_strip(self.plan, pair, lane):
                draw_text(cv, x, labels_y, f"{lane[0]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section="wrap", pair=pair, lane=lane,
                    width=w, height=h, scale=TWOX_SCALE,
                )
                x += w * TWOX_SCALE + GUTTER
            x += GUTTER
        return y + row_h + GUTTER

    def context_row(self, cv, y: int, pair: str) -> int:
        """The rendered stationary yardstick: [fN@A | fN@B] per pose."""
        walk, turn_f = PAIR_AXES[pair]
        draw_text(cv, MARGIN_LEFT, y, "CONTEXT 2X A B STATIONARY SWAP")
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + TILE - 2, "CTX 2X")
        x = MARGIN_LEFT
        for pose in ("f0", "f1", "f2", "f3", "idle"):
            for side, facing in (("A", walk), ("B", turn_f)):
                draw_text(cv, x, labels_y, f"{pose.upper()} {side}")
                tick = {
                    "tick": 0, "phase": "context", "pose": pose,
                    "pose_facing": facing, "a_px": 0, "b_px": 0,
                    "draw": [0, 0],
                }
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section="context", pair=pair, lane="CONTEXT",
                    width=TILE, height=TILE, scale=TWOX_SCALE,
                )
                x += TILE * TWOX_SCALE + GUTTER
            x += GUTTER
        return y + TILE * TWOX_SCALE + GUTTER

    def film_rows(self, cv, y: int, facing: str) -> int:
        draw_text(cv, MARGIN_LEFT, y, f"FILM {facing.upper()}")
        y += 8
        step_w = TILE + GUTTER
        for index, pose in enumerate(WALK_POSES):
            draw_text(cv, MARGIN_LEFT + index * step_w, y, pose.upper())
        y += 8 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} FILM")
            for index, pose in enumerate(WALK_POSES):
                tick = {
                    "tick": index, "phase": pose, "pose": pose,
                    "pose_facing": facing, "a_px": 0, "b_px": 0,
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
            walk, turn_f = PAIR_AXES[pair]
            draw_text(
                cv, 2, y,
                f"PAIR {pair} WALK {walk.upper()} TURN {turn_f.upper()}",
            )
            y += 8 + GUTTER
            for lane in SECTION_LANES:
                y = self.lane_rows(cv, y, pair, lane)
            y = self.turn_zoom_row(cv, y, pair)
            y = self.wrap_row(cv, y, pair)
            y = self.context_row(cv, y, pair)
            y += GUTTER
        for facing in FACINGS:
            y = self.film_rows(cv, y, facing)
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: TurnTimelineSheet, pair: str) -> list[Rgba8Canvas]:
    """Per tick t00..t29: the four TURN lanes side by side over their full
    2x2-tile windows (the degenerate lanes' motion is the banked v1 walk,
    animated in the banked v1 previews)."""
    zone = sheet.reference["zones"]["zone_1"]
    window = sheet.plan["pairs"][pair]["lanes"]["EARLY"]["window"]
    frames = []
    for t in range(TOTAL_TICKS):
        frame = Rgba8Canvas(
            (window["w"] * len(TURN_LANES) + GUTTER * (len(TURN_LANES) - 1))
            * APNG_SCALE,
            window["h"] * APNG_SCALE, BG,
        )
        for index, lane in enumerate(TURN_LANES):
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
        default=ROOT / "reviews" / "calibration-v10" / "turn-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write turn-lanes-<pair>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    sheet = TurnTimelineSheet(dirs, reference)
    canvas = sheet.build()
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for pair in PAIRS:
            frames = build_apng_frames(sheet, pair)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"turn-lanes-{pair.lower()}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
