#!/usr/bin/env python3
"""Tick-accurate walk->attack onset-seam timeline sheet (sprint 8, calibration-v8).

Measurement sprint: ZERO new frames. The engine legally starts an attack
mid-walk (creature.rb start_attack has no moving? guard; the walk tween
continues under the attack — verified at the pinned commit), so the banked
f3-arrival onset (t14->t15) is only one member of a class. Four pre-registered
onset lanes render the class from frozen banked bytes only:

- EARLY   onset t03 (walk tick 2,  REM 11): active fires mid-tween; the
          recovery overlap reaches recovery tick 3 (arrival t14).
- MID     onset t06 (walk tick 5,  REM 8):  arrival lands on active tick 4.
- LATE    onset t10 (walk tick 9,  REM 4):  arrival lands on windup tick 5.
- CONTROL onset t15 (arrival + 1,  REM 0):  the banked seam, regenerated from
          banked machinery — the regression anchor.

Drawing model (pre-registered in reviews/calibration-v8/rationale.md): the
banked v7-winner grammar — windup w0 x1 + a0 x4 at -3, active k0 x4 at +6,
recovery s0 x1 + r0 x6 + x0 x1 at 0; walk frames per the banked v1 mapping on
pre-onset ticks only; draw position = smoothstep tween position + state
offset. Recovery-overlap ticks draw s0/r0 on the moving base under this
declared model (the recovery-walk priority question stays a carried finding).

Sheet rows per facing (1 column = 1 tick):

- Per lane (EARLY, MID, LATE, CONTROL): RULER (absolute tick indices +
  phase labels) + Z1/Z2 rows of the 16 ticks onset-2 .. onset+13 over
  3-tile windows [from | landing | arc] (win_px = axis; the arc tile keeps
  the k0 boundary crossing visible; EARLY's w0@-1 excursion stays in-bounds
  because creature pixels start at row/col 2).
- ONSET 2X: per lane, onset-1 | onset | onset+1 (the fN | w0 | a0 seam).
- RELEASE 2X: per lane, onset+4 | onset+5 (the a0 -> k0 event).
- FILM: the banked eleven-column static strip (identity/context anchor).

Every creature cell is recorded in a machine-readable manifest consumed by
tools/seam_metrics.py for composition-purity and tick-math verification.
Layout is fixed; regeneration is byte-identical. Banked tools are imported
unmodified. Optional APNG aids (four lanes side by side, full t00..t33,
exact 1/60 s per-frame delay, 4x NN) are never blocking.
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
from make_grammar_timeline import (  # noqa: E402
    IDLE_PRE_TICKS,
    PHASE_LABELS,
    apng_delays,
    canvas_pixels,
    cell_size,
    compose_window,
    encode_apng,
    round_half_up,
    smoothstep,
    walk_frame_index,
)
import make_grammar_timeline as grammar  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
SEAM_FONT = {
    **grammar.FONT,
    "Y": ("101", "101", "010", "010", "010"),
}
FACINGS = ("down", "right")
LANES = ("EARLY", "MID", "LATE", "CONTROL")
ONSET_TICKS = {"EARLY": 3, "MID": 6, "LATE": 10, "CONTROL": 15}
WINDUP_INBETWEEN = "w0"    # banked v6, windup tick 1
SETTLE_INBETWEEN = "s0"    # banked v6, recovery tick 1
RISE_INBETWEEN = "x0"      # banked v7, recovery tick 8
WINDUP_POSE = "a0"         # banked v4 winner
RECOVERY_POSE = "r0"       # banked v5 winner
STRIP = ("idle", "f0", "f1", "f2", "f3", "a0", "k0", "r0", "w0", "s0", "x0")
LANE_PRE_TICKS = 2         # lane rows start at onset-2
LANE_SPAN = 16             # onset-2 .. onset+13
WINDOW_TILES = 3           # [from | landing | arc]
TOTAL_TICKS = 34           # t00..t33 (CONTROL's idle tail ends at t33)
ARRIVAL_TICK = IDLE_PRE_TICKS - 1 + 13  # walk tick 13 draws at t14
ONSET_WINDOW_TILES = 2     # onset-strip crop: [from | landing] holds every onset pose
TWOX_SCALE = 2
APNG_SCALE = 4


def draw_text(cv: Rgba8Canvas, x: int, y: int, text: str) -> None:
    """The banked 3x5 glyph renderer over the seam-extended font table."""
    from make_contact_sheet import LABEL

    for index, char in enumerate(text):
        glyph = SEAM_FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.put(x + index * 4 + gx, y + gy, LABEL)

POSE_DIRS = {
    "idle": "idle_dir",
    "f0": "walk_dir", "f1": "walk_dir", "f2": "walk_dir", "f3": "walk_dir",
    "a0": "anticipation_dir",
    "k0": "attack_dir",
    "r0": "recovery_dir",
    "w0": "transition_dir", "s0": "transition_dir",
    "x0": "rise_dir",
}


def pose_filename(pose: str, facing: str) -> str:
    if pose == "idle":
        return f"player_1_lane_b_idle_{facing}.png"
    if pose.startswith("f"):
        return f"player_1_lane_b_walk_{facing}_{pose}.png"
    return f"player_1_lane_b_attack_{facing}_{pose}.png"


def tween_position(step_ticks_done: int, step: int) -> int:
    """The pinned runtime tween at integer review positions."""
    if step_ticks_done <= 0:
        return 0
    if step_ticks_done >= step:
        return TILE
    return round_half_up(TILE * smoothstep(step_ticks_done / step))


def lane_tick(tick: int, onset: int, reference: dict) -> dict:
    """Pose + position for one absolute tick of one lane — a pure function
    of the pinned constants, the pre-registered onset tick, and the declared
    drawing model."""
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    step = timing["step_frames"]["value"]

    axis = tween_position(tick - 1, step) if tick >= 1 else 0
    if tick < onset:
        if tick < IDLE_PRE_TICKS:
            return {"tick": tick, "phase": "idle_pre", "pose": "idle",
                    "axis_px": axis, "offset_px": 0}
        walk_tick = tick - 1
        pose = f"f{walk_frame_index(walk_tick, step)}"
        return {"tick": tick, "phase": "walk", "pose": pose,
                "axis_px": axis, "offset_px": 0}
    into = tick - onset
    if into < windup:
        pose = WINDUP_INBETWEEN if into == 0 else WINDUP_POSE
        return {"tick": tick, "phase": "windup", "pose": pose,
                "axis_px": axis + lunge["windup_px"],
                "offset_px": lunge["windup_px"]}
    if into < windup + active:
        return {"tick": tick, "phase": "active", "pose": "k0",
                "axis_px": axis + lunge["active_px"],
                "offset_px": lunge["active_px"]}
    if into < windup + active + recovery:
        rec = into - windup - active
        if rec == 0:
            pose = SETTLE_INBETWEEN
        elif rec == recovery - 1:
            pose = RISE_INBETWEEN
        else:
            pose = RECOVERY_POSE
        return {"tick": tick, "phase": "recovery", "pose": pose,
                "axis_px": axis, "offset_px": 0}
    return {"tick": tick, "phase": "idle_post", "pose": "idle",
            "axis_px": axis, "offset_px": 0}


def build_plan(reference: dict) -> dict:
    """The four-lane tick plan. Every lane runs t00..t33; the sheet rows show
    onset-2 .. onset+13 per lane; the jump tables are sliced by
    tools/seam_metrics.py."""
    timing = reference["attack_timing"]["values"]
    lanes: dict[str, dict] = {}
    for lane in LANES:
        onset = ONSET_TICKS[lane]
        ticks = [lane_tick(t, onset, reference) for t in range(TOTAL_TICKS)]
        lanes[lane] = {
            "onset_tick": onset,
            "rem_after_onset": max(0, timing["step_frames"]["value"] - (onset - 1)),
            "arrival_tick": ARRIVAL_TICK,
            "ticks": ticks,
            "sheet_ticks": ticks[onset - LANE_PRE_TICKS: onset - LANE_PRE_TICKS + LANE_SPAN],
        }
    return {
        "constants": {
            "windup_frames": timing["windup_frames"]["value"],
            "active_frames": timing["active_frames"]["value"],
            "recovery_frames": timing["recovery_frames"]["value"],
            "step_frames": timing["step_frames"]["value"],
            "windup_px": reference["feedback_states"]["lunge_offset"]["windup_px"],
            "active_px": reference["feedback_states"]["lunge_offset"]["active_px"],
            "arrival_tick": ARRIVAL_TICK,
            "onset_ticks": dict(ONSET_TICKS),
        },
        "lanes": lanes,
    }


def onset_strip(plan: dict, lane: str) -> list[dict]:
    """onset-1 | onset | onset+1 — the fN | w0 | a0 seam region."""
    onset = plan["lanes"][lane]["onset_tick"]
    ticks = plan["lanes"][lane]["ticks"]
    return [ticks[onset - 1], ticks[onset], ticks[onset + 1]]


def release_strip(plan: dict, lane: str) -> list[dict]:
    """onset+4 | onset+5 — the a0 -> k0 release event."""
    onset = plan["lanes"][lane]["onset_tick"]
    ticks = plan["lanes"][lane]["ticks"]
    return [ticks[onset + 4], ticks[onset + 5]]


def load_poses(dirs: dict[str, Path], facing: str) -> dict[str, Sprite]:
    return {
        pose: sprite_from_png(dirs[POSE_DIRS[pose]] / pose_filename(pose, facing))
        for pose in STRIP
    }


class SeamTimelineSheet:
    """Deterministic sheet builder that records every creature cell."""

    def __init__(self, dirs: dict[str, Path], reference: dict):
        self.dirs = dirs
        self.reference = reference
        self.plan = build_plan(reference)
        self.poses = {facing: load_poses(dirs, facing) for facing in FACINGS}
        self.cells: list[dict] = []

    # -- geometry -----------------------------------------------------------

    def sheet_width(self) -> int:
        lane_w = LANE_SPAN * (cell_size("right", WINDOW_TILES)[0] + GUTTER)
        onset_w = (
            len(LANES) * 3 * (cell_size("right", ONSET_WINDOW_TILES, TWOX_SCALE)[0] + GUTTER)
            + (len(LANES) - 1) * GUTTER
        )
        release_w = (
            len(LANES) * 2 * (cell_size("right", WINDOW_TILES, TWOX_SCALE)[0] + GUTTER)
            + (len(LANES) - 1) * GUTTER
        )
        widest = max(lane_w, onset_w, release_w)
        return MARGIN_LEFT + widest + MARGIN_TOP

    def facing_height(self, facing: str) -> int:
        header = 8 + GUTTER
        ruler = 16 + GUTTER
        h1 = cell_size(facing, WINDOW_TILES)[1]
        h2_onset = cell_size(facing, ONSET_WINDOW_TILES, TWOX_SCALE)[1]
        h2_release = cell_size(facing, WINDOW_TILES, TWOX_SCALE)[1]
        total = header
        total += len(LANES) * (8 + ruler + 2 * (h1 + GUTTER))   # lane label+ruler+Z1/Z2
        total += 8 + 8 + GUTTER + h2_onset + GUTTER             # ONSET 2X
        total += 8 + 8 + GUTTER + h2_release + GUTTER           # RELEASE 2X
        total += 8 + GUTTER + 2 * (TILE + GUTTER)               # FILM
        return total

    # -- cells --------------------------------------------------------------

    def record(self, **cell) -> None:
        self.cells.append(cell)

    def window_cell(
        self, cv: Rgba8Canvas, x: int, y: int, zone_key: str, facing: str,
        tiles: int, pose: str, win_px: int, *,
        section: str, lane: str, tick: int, phase: str, scale: int = 1,
    ) -> None:
        zone = self.reference["zones"][zone_key]
        composed = compose_window(zone, facing, tiles, self.poses[facing][pose], win_px)
        w, h = cell_size(facing, tiles, scale)
        if scale == 1:
            for px, py, rgb in canvas_pixels(composed):
                cv.put(x + px, y + py, (*rgb, 255))
        else:
            cv.blit_scaled(canvas_pixels(composed), x, y, scale)
        self.record(
            section=section, facing=facing, zone=zone_key, lane=lane,
            tick=tick, phase=phase, pose=pose, window_tiles=tiles,
            win_px=win_px, scale=scale, rect=[x, y, w, h],
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

    def lane_rows(self, cv, y: int, facing: str, lane: str) -> int:
        ticks = self.plan["lanes"][lane]["sheet_ticks"]
        w, h = cell_size(facing, WINDOW_TILES)
        step_w = w + GUTTER
        draw_text(cv, MARGIN_LEFT, y, f"{lane} ONSET T{ONSET_TICKS[lane]:02d}")
        y += 8
        self.ruler(cv, y + 8, ticks, step_w)
        y += 16 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + h // 2 - 2, f"{zone_label} {lane[0]}")
            for index, tick in enumerate(ticks):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, facing,
                    WINDOW_TILES, tick["pose"], tick["axis_px"],
                    section="lane", lane=lane, tick=tick["tick"],
                    phase=tick["phase"],
                )
            y += h + GUTTER
        return y

    def strip_row(self, cv, y: int, facing: str, section: str, label: str,
                  strip_of, tiles: int) -> int:
        w, h = cell_size(facing, tiles, TWOX_SCALE)
        step_w = w + GUTTER
        draw_text(cv, MARGIN_LEFT, y, label)
        y += 8
        x = MARGIN_LEFT
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + h // 2 - 2, f"{section.upper()[:3]} 2X")
        for lane in LANES:
            for tick in strip_of(self.plan, lane):
                draw_text(cv, x, labels_y, f"{lane[0]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", facing, tiles,
                    tick["pose"], tick["axis_px"],
                    section=section, lane=lane, tick=tick["tick"],
                    phase=tick["phase"], scale=TWOX_SCALE,
                )
                x += step_w
            x += GUTTER
        return y + h + GUTTER

    def film_rows(self, cv, y: int, facing: str) -> int:
        step_w = TILE + GUTTER
        for index, pose in enumerate(STRIP):
            draw_text(cv, MARGIN_LEFT + index * step_w, y, pose.upper())
        y += 8 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(cv, 2, y + TILE // 2 - 2, f"{zone_label} FILM")
            for index, pose in enumerate(STRIP):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, facing, 1,
                    pose, 0,
                    section="film", lane="STATIC", tick=index, phase=pose,
                )
            y += TILE + GUTTER
        return y

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
            for lane in LANES:
                y = self.lane_rows(cv, y, facing, lane)
            y = self.strip_row(cv, y, facing, "onset", "ONSET SEAM 2X FN W0 A0",
                               onset_strip, ONSET_WINDOW_TILES)
            y = self.strip_row(cv, y, facing, "release", "RELEASE 2X A0 K0",
                               release_strip, WINDOW_TILES)
            y = self.film_rows(cv, y, facing) + GUTTER
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: SeamTimelineSheet, facing: str) -> list[Rgba8Canvas]:
    """Per tick t00..t33: the four lanes side by side over 3-tile windows."""
    zone = sheet.reference["zones"]["zone_1"]
    frames = []
    for t in range(TOTAL_TICKS):
        panes = []
        for lane in LANES:
            tick = sheet.plan["lanes"][lane]["ticks"][t]
            pane = compose_window(
                zone, facing, WINDOW_TILES, sheet.poses[facing][tick["pose"]],
                tick["axis_px"],
            )
            draw_text(pane, 2, 2, lane[0])
            panes.append(pane)
        if facing == "down":
            frame = Rgba8Canvas(
                (TILE * len(LANES) + GUTTER * (len(LANES) - 1)) * APNG_SCALE,
                TILE * WINDOW_TILES * APNG_SCALE, BG,
            )
            offsets = [((TILE + GUTTER) * APNG_SCALE * i, 0) for i in range(len(LANES))]
        else:
            frame = Rgba8Canvas(
                TILE * WINDOW_TILES * APNG_SCALE,
                (TILE * len(LANES) + GUTTER * (len(LANES) - 1)) * APNG_SCALE, BG,
            )
            offsets = [(0, (TILE + GUTTER) * APNG_SCALE * i) for i in range(len(LANES))]
        for pane, (ox, oy) in zip(panes, offsets):
            frame.blit_scaled(canvas_pixels(pane), ox, oy, APNG_SCALE)
        frames.append(frame)
    return frames


def default_dirs() -> dict[str, Path]:
    return {
        "rise_dir": ROOT / "exports" / "calibration-v7",
        "transition_dir": ROOT / "exports" / "calibration-v6",
        "recovery_dir": ROOT / "exports" / "calibration-v5",
        "anticipation_dir": ROOT / "exports" / "calibration-v3",
        "attack_dir": ROOT / "exports" / "calibration-v2",
        "walk_dir": ROOT / "exports" / "calibration-v1",
        "idle_dir": ROOT / "exports" / "calibration-v0",
    }


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
        default=ROOT / "reviews" / "calibration-v8" / "seam-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write seam-lanes-<facing>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    sheet = SeamTimelineSheet(dirs, reference)
    canvas = sheet.build()
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for facing in FACINGS:
            frames = build_apng_frames(sheet, facing)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"seam-lanes-{facing}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
