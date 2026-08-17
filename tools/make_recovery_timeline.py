#!/usr/bin/env python3
"""Tick-accurate recovery-comparison timeline sheet (sprint 5, calibration-v5).

Extends the banked v4 timeline protocol to the three-way recovery comparison
under identical pinned timing (manifests/render-reference.json
`attack_timing`, captured read-only from the pinned game commit). Every
non-recovery span uses the banked-winner grammar (a0 held at the pinned -3px
windup offset, k0 at +6px active - the v4 timeline-B result, not re-tested),
so the only variable is the recovery-span pose:

- timeline A (incumbent): recovery = idle at offset 0 - the v4-banked
  treatment whose recovery span is invisible;
- timeline R (candidate): recovery = r0 held at offset 0 for the pinned
  8 recovery ticks;
- timeline C (cheap alternative, tested honestly): recovery = a0 REUSED at
  offset 0 - the pre-registered grammar-inversion probe.

Sheet rows per facing (1 column = 1 tick, no cadence compression):

- RULER:    phase labels + per-tick indices (both row groups)
- APPROACH: idle_pre + the 13-tick walk step (identical in A/R/C, one row
            per zone)
- ATTACK:   Z1 A/R/C then Z2 A/R/C stacked (t14-t33), both zone palettes
- 2X:       the four boundary ticks of timeline R at 2x - t23 (last active),
            t24 (first recovery), t31 (last recovery), t32 (first idle):
            the two boundaries under test (release->settle, ready-again)
- FILM:     static strip idle | f0-f3 | a0 | k0 | r0 over both zone palettes
- DIFF:     r0 versus idle, every walk frame, a0, AND k0 at 2x (derived
            diagnostic via the banked diff_pixels - not a creature cell)
- GRAMMAR:  seven static cells via the banked tell_cell - idle | f1 | a0 |
            a0@-3 | k0 | k0@+6 | r0@0 (the recovery state at its pinned
            runtime draw offset)

Every creature cell is recorded in a machine-readable manifest consumed by
tools/recovery_metrics.py for composition-purity and tick-math verification.
Layout is fixed; regeneration is byte-identical. Banked tools are imported
unmodified. Optional APNG viewing aids (A | R | C stacked, 4x
nearest-neighbor, exact 1/60 s per-frame delay) are never blocking.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_contact_sheet as base  # noqa: E402
import make_motion_sheet as motion  # noqa: E402
from make_contact_sheet import (  # noqa: E402
    GUTTER,
    MARGIN_LEFT,
    MARGIN_TOP,
    TILE,
    Sprite,
    load_reference,
    sprite_from_png,
)
from make_feedback_sheet import tell_cell  # noqa: E402
from make_grammar_timeline import (  # noqa: E402
    FONT,
    IDLE_POST_TICKS,
    IDLE_PRE_TICKS,
    PHASE_LABELS,
    WALK_FRAME_COUNT,
    apng_delays,
    canvas_pixels,
    cell_size,
    compose_window,
    encode_apng,
    round_half_up,
    smoothstep,
    walk_frame_index,
)
from make_grammar_timeline import draw_text as _draw_text_font  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

BG = base.BG
FACINGS = ("down", "right")
TIMELINES = ("A", "R", "C")
RECOVERY_POSE = {"A": "idle", "R": "r0", "C": "a0"}
WINDUP_POSE = "a0"  # the banked v4 winner, held in ALL timelines
STRIP = ("idle", "f0", "f1", "f2", "f3", "a0", "k0", "r0")
DIFF_VS = ("idle", "f0", "f1", "f2", "f3", "a0", "k0")
TWOX_SCALE = 2
APNG_SCALE = 4

draw_text = _draw_text_font


def build_plan(reference: dict) -> dict:
    """The tick plan: a pure function of the pinned constants.

    Every tick carries one pose per timeline; poses are identical across
    A/R/C outside the recovery span (the isolation that makes the
    comparison decidable).
    """
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    step = timing["step_frames"]["value"]

    ticks: list[dict] = []

    def add(phase: str, poses: dict[str, str], axis_px: int, offset_px: int) -> None:
        ticks.append(
            {
                "tick": len(ticks),
                "phase": phase,
                "poses": dict(poses),
                "axis_px": axis_px,
                "offset_px": offset_px,
            }
        )

    def shared(pose: str) -> dict[str, str]:
        return {tl: pose for tl in TIMELINES}

    for _ in range(IDLE_PRE_TICKS):
        add("idle_pre", shared("idle"), 0, 0)
    for k in range(1, step + 1):
        pose = f"f{walk_frame_index(k, step)}"
        add("walk", shared(pose), round_half_up(TILE * smoothstep(k / step)), 0)
    for _ in range(windup):
        add("windup", shared(WINDUP_POSE), TILE + lunge["windup_px"], lunge["windup_px"])
    for _ in range(active):
        add("active", shared("k0"), TILE + lunge["active_px"], lunge["active_px"])
    for _ in range(recovery):
        add("recovery", dict(RECOVERY_POSE), TILE, 0)
    for _ in range(IDLE_POST_TICKS):
        add("idle_post", shared("idle"), TILE, 0)

    arrival = IDLE_PRE_TICKS + step - 1
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
        "approach_ticks": [t for t in ticks if t["tick"] <= arrival],
        "attack_ticks": [t for t in ticks if t["tick"] >= arrival],
        "arrival_tick": arrival,
    }


def boundary_ticks(plan: dict) -> list[dict]:
    """The two boundaries under test: last active, first recovery (release->
    settle), last recovery, first idle_post (the ready-again beat)."""
    ticks = plan["ticks"]
    active = [t for t in ticks if t["phase"] == "active"]
    recovery = [t for t in ticks if t["phase"] == "recovery"]
    idle_post = [t for t in ticks if t["phase"] == "idle_post"]
    return [active[-1], recovery[0], recovery[-1], idle_post[0]]


def load_poses(
    recovery_dir: Path,
    anticipation_dir: Path,
    attack_dir: Path,
    walk_dir: Path,
    idle_dir: Path,
    facing: str,
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
    poses["r0"] = sprite_from_png(
        recovery_dir / f"player_1_lane_b_attack_{facing}_r0.png"
    )
    return poses


class RecoveryTimelineSheet:
    """Deterministic sheet builder that records every creature cell."""

    def __init__(
        self,
        recovery_dir: Path,
        anticipation_dir: Path,
        attack_dir: Path,
        walk_dir: Path,
        idle_dir: Path,
        reference: dict,
    ):
        self.reference = reference
        self.plan = build_plan(reference)
        self.poses = {
            facing: load_poses(
                recovery_dir, anticipation_dir, attack_dir, walk_dir, idle_dir, facing
            )
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
        total += ruler + 6 * (h2 + GUTTER)  # attack rows: 2 zones x A/R/C
        total += ruler + cell_size(facing, 2, TWOX_SCALE)[1] + GUTTER  # 2X row
        total += 8 + GUTTER + 2 * (TILE + GUTTER)  # FILM labels + Z1/Z2 rows
        total += TILE * TWOX_SCALE + GUTTER  # DIFF row
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
        scale: int = 1,
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
            section=section, facing=facing, zone=zone_key, timeline=timeline,
            tick=tick, phase=phase, pose=pose, window_tiles=tiles, win_px=win_px,
            scale=scale, rect=[x, y, w, h],
        )

    # -- rows ---------------------------------------------------------------

    def ruler(self, cv, y: int, ticks: list[dict], step_w: int, prefix: str) -> None:
        previous_phase = None
        for index, tick in enumerate(ticks):
            x = MARGIN_LEFT + index * step_w
            draw_text(cv, x, y, f"{prefix}{tick['tick']:02d}")
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
                    tick["poses"]["A"], tick["axis_px"],
                    section="approach", timeline="ARC", tick=tick["tick"],
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
            for timeline in TIMELINES:
                draw_text(cv, 2, y + h // 2 - 2, f"{zone_label} {timeline}")
                for index, tick in enumerate(ticks):
                    self.window_cell(
                        cv, MARGIN_LEFT + index * step_w, y, zone_key, facing, 2,
                        tick["poses"][timeline], tick["axis_px"] - TILE,
                        section="attack", timeline=timeline, tick=tick["tick"],
                        phase=tick["phase"],
                    )
                y += h + GUTTER
        return y

    def twox_row(self, cv, y: int, facing: str) -> int:
        transitions = boundary_ticks(self.plan)
        w, h = cell_size(facing, 2, TWOX_SCALE)
        step_w = w + GUTTER
        for index, tick in enumerate(transitions):
            draw_text(cv, MARGIN_LEFT + index * step_w, y + 8, f"T{tick['tick']:02d}")
        y += 16 + GUTTER
        draw_text(cv, 2, y + h // 2 - 2, "2X R")
        for index, tick in enumerate(transitions):
            self.window_cell(
                cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 2,
                tick["poses"]["R"], tick["axis_px"] - TILE,
                section="twox", timeline="R", tick=tick["tick"],
                phase=tick["phase"], scale=TWOX_SCALE,
            )
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
                    section="film", timeline="STATIC", tick=index, phase=pose,
                )
            y += TILE + GUTTER
        return y

    def diff_row(self, cv, y: int, facing: str) -> int:
        """Derived diagnostic (banked diff_pixels): r0 vs each confusable.
        Not a creature cell - excluded from the purity manifest by design."""
        r0 = self.poses[facing]["r0"]
        draw_text(cv, 2, y + TILE - 2, "DIFF")
        for index, name in enumerate(DIFF_VS):
            x = MARGIN_LEFT + index * (TILE * TWOX_SCALE + GUTTER)
            cv.fill_rect(x, y, TILE * TWOX_SCALE, TILE * TWOX_SCALE, (30, 30, 30, 255))
            cv.blit_scaled(
                motion.diff_pixels(self.poses[facing][name], r0), x, y, TWOX_SCALE
            )
            draw_text(cv, x, y + TILE * TWOX_SCALE - 6, name.upper())
        return y + TILE * TWOX_SCALE + GUTTER

    def grammar_row(self, cv, y: int, facing: str) -> int:
        """The static grammar control row extended to seven cells: the v3/v4
        six plus the recovery state at its pinned runtime draw offset (0)."""
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
            ("R0", "r0", 0),
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
                tick=index, phase=label.lower(), pose=pose, window_tiles=2,
                win_px=offset, scale=1, rect=[x, y, cell_w, cell_h],
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
            y = self.twox_row(cv, y, facing)
            y = self.film_rows(cv, y, facing)
            y = self.diff_row(cv, y, facing)
            y = self.grammar_row(cv, y, facing) + GUTTER
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: RecoveryTimelineSheet, facing: str) -> list[Rgba8Canvas]:
    """Per tick: timelines A, R, C side by side over a 3-tile window, 4x NN."""
    zone = sheet.reference["zones"]["zone_1"]
    frames = []
    for tick in sheet.plan["ticks"]:
        panes = []
        for timeline in TIMELINES:
            pane = compose_window(
                zone, facing, 3, sheet.poses[facing][tick["poses"][timeline]],
                tick["axis_px"],
            )
            draw_text(pane, 2, 2, timeline)
            panes.append(pane)
        if facing == "down":
            frame = Rgba8Canvas(
                (TILE * 3 + GUTTER * 2) * APNG_SCALE, TILE * 3 * APNG_SCALE, BG
            )
            offsets = [((TILE + GUTTER) * APNG_SCALE * i, 0) for i in range(3)]
        else:
            frame = Rgba8Canvas(
                TILE * 3 * APNG_SCALE, (TILE * 3 + GUTTER * 2) * APNG_SCALE, BG
            )
            offsets = [(0, (TILE + GUTTER) * APNG_SCALE * i) for i in range(3)]
        for pane, (ox, oy) in zip(panes, offsets):
            frame.blit_scaled(canvas_pixels(pane), ox, oy, APNG_SCALE)
        frames.append(frame)
    return frames


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recovery-exports", type=Path, default=ROOT / "exports" / "calibration-v5"
    )
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
        default=ROOT / "reviews" / "calibration-v5" / "timeline-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write timeline-arc-<facing>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = RecoveryTimelineSheet(
        args.recovery_exports, args.anticipation_exports, args.attack_exports,
        args.walk_exports, args.idle_exports, reference,
    )
    canvas = sheet.build()
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for facing in FACINGS:
            frames = build_apng_frames(sheet, facing)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"timeline-arc-{facing}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
