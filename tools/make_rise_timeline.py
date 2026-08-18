#!/usr/bin/env python3
"""Tick-accurate completion-rise A/B timeline sheet (sprint 7, calibration-v7).

Extends the banked v6 transition protocol to the ready-again boundary —
r0->idle at t31->t32, the grammar's one remaining un-smoothed pose-only
discontinuity (37.09/37.64 at 0px, banked v5/v6). Timelines share the
v6-banked winner grammar everywhere except recovery tick 8, so that tick is
the only variable:

- timeline A (incumbent): the v6-banked winner grammar UNMODIFIED - w0 on
  windup tick 1 (t15, at -3), a0 held t16-t19, k0 held t20-t23 at +6, s0 on
  recovery tick 1 (t24, at 0), r0 held t25-t31. The ready-again boundary is
  the banked single-tick full swap.
- timeline B (candidate): identical except t31, where x0 (the rise
  breakdown) occupies recovery tick 8 - recovery = s0 x1 + r0 x6 + x0 x1.
  In-betweens consume pinned ticks, never add them.

The a0->k0 release boundary (t19->t20, +9px) and the banked w0/s0 transition
ticks (t15, t24) are IDENTICAL in both timelines - machine-compared by
tools/rise_metrics.py and additionally subsumed by tick-identity. The
boundary under test is a PURE pose swap: t31 and t32 both draw at position
32 (recovery else-branch and idle are both offset 0).

Sheet rows per facing (1 column = 1 tick, no cadence compression):

- RULER:    phase labels + per-tick indices (both row groups)
- APPROACH: idle_pre + the 13-tick walk step (identical in A/B, one row per
            zone)
- ATTACK:   Z1 A/B then Z2 A/B stacked (t14-t33), both zone palettes - t31
            is the only differing column
- 2X:       the four boundary-region ticks of timeline B - t30 (last held
            r0), t31 (x0), t32 (arrival idle), t33 (held idle) - at 2x
- RISE 4X:  the X | M | Y triplet at its real timeline offsets - r0@0 (t30)
            | x0@0 (t31) | idle@0 (t32) - at 4x nearest-neighbor
- FILM:     static strip idle | f0-f3 | a0 | k0 | r0 | w0 | s0 | x0 over
            both zone palettes (eleven columns)
- DIFF:     x0 vs its endpoints (r0, idle) plus the declared ambiguity
            diagnostics (s0, w0) at 2x (banked diff_pixels - derived, not a
            creature cell)
- GRAMMAR:  ten static cells via the banked tell_cell - idle | f1 | w0@-3 |
            a0 | a0@-3 | k0 | k0@+6 | s0@0 | r0@0 | x0@0 (x0 inserted at its
            timeline position after r0)

Every creature cell is recorded in a machine-readable manifest consumed by
tools/rise_metrics.py for composition-purity and tick-math verification.
Layout is fixed; regeneration is byte-identical. Banked tools are imported
unmodified. Optional APNG viewing aids (A | B side by side, 4x
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
TIMELINES = ("A", "B")
WINDUP_INBETWEEN = "w0"    # banked v6, windup tick 1, BOTH timelines
SETTLE_INBETWEEN = "s0"    # banked v6, recovery tick 1, BOTH timelines
RISE_INBETWEEN = "x0"      # timeline B, recovery tick 8 only
WINDUP_POSE = "a0"         # the banked v4 winner, held in both timelines
RECOVERY_POSE = "r0"       # the banked v5 winner, held in both timelines
STRIP = ("idle", "f0", "f1", "f2", "f3", "a0", "k0", "r0", "w0", "s0", "x0")
DIFF_PAIRS = (
    ("x0", "r0"), ("x0", "idle"), ("x0", "s0"), ("x0", "w0"),
)
TWOX_SCALE = 2
FOURX_SCALE = 4
APNG_SCALE = 4

draw_text = _draw_text_font


def build_plan(reference: dict) -> dict:
    """The tick plan: a pure function of the pinned constants.

    Timeline A is the v6-banked winner grammar (w0/s0 on their banked
    transition ticks in BOTH timelines); poses are identical across A/B
    outside recovery tick 8 - the isolation that makes the comparison
    decidable.
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
    for index in range(windup):
        pose = WINDUP_INBETWEEN if index == 0 else WINDUP_POSE
        add("windup", shared(pose), TILE + lunge["windup_px"], lunge["windup_px"])
    for _ in range(active):
        add("active", shared("k0"), TILE + lunge["active_px"], lunge["active_px"])
    for index in range(recovery):
        if index == 0:
            poses = shared(SETTLE_INBETWEEN)
        elif index == recovery - 1:
            poses = {"A": RECOVERY_POSE, "B": RISE_INBETWEEN}
        else:
            poses = shared(RECOVERY_POSE)
        add("recovery", poses, TILE, 0)
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


def rise_ticks(plan: dict) -> list[dict]:
    """The four boundary-region ticks: last held r0, the rise tick, the
    arrival idle, and one held idle column."""
    ticks = plan["ticks"]
    recovery = [t for t in ticks if t["phase"] == "recovery"]
    idle_post = [t for t in ticks if t["phase"] == "idle_post"]
    return [recovery[-2], recovery[-1], idle_post[0], idle_post[1]]


def rise_triplet(plan: dict) -> list[dict]:
    """The X | M | Y triplet at real timeline positions: r0 | x0 | idle."""
    return rise_ticks(plan)[:3]


def load_poses(
    rise_dir: Path,
    transition_dir: Path,
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
    for inbetween in (WINDUP_INBETWEEN, SETTLE_INBETWEEN):
        poses[inbetween] = sprite_from_png(
            transition_dir / f"player_1_lane_b_attack_{facing}_{inbetween}.png"
        )
    poses[RISE_INBETWEEN] = sprite_from_png(
        rise_dir / f"player_1_lane_b_attack_{facing}_{RISE_INBETWEEN}.png"
    )
    return poses


class RiseTimelineSheet:
    """Deterministic sheet builder that records every creature cell."""

    def __init__(
        self,
        rise_dir: Path,
        transition_dir: Path,
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
                rise_dir, transition_dir, recovery_dir, anticipation_dir,
                attack_dir, walk_dir, idle_dir, facing,
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
        total += ruler + 4 * (h2 + GUTTER)  # attack rows: 2 zones x A/B
        total += ruler + cell_size(facing, 2, TWOX_SCALE)[1] + GUTTER  # 2X row
        total += ruler + cell_size(facing, 2, FOURX_SCALE)[1] + GUTTER  # RISE 4X
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
        boundary = rise_ticks(self.plan)
        w, h = cell_size(facing, 2, TWOX_SCALE)
        step_w = w + GUTTER
        for index, tick in enumerate(boundary):
            draw_text(cv, MARGIN_LEFT + index * step_w, y + 8, f"T{tick['tick']:02d}")
        y += 16 + GUTTER
        draw_text(cv, 2, y + h // 2 - 2, "2X B")
        for index, tick in enumerate(boundary):
            self.window_cell(
                cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 2,
                tick["poses"]["B"], tick["axis_px"] - TILE,
                section="twox", timeline="B", tick=tick["tick"],
                phase=tick["phase"], scale=TWOX_SCALE,
            )
        return y + h + GUTTER

    def fourx_row(self, cv, y: int, facing: str) -> int:
        triplet = rise_triplet(self.plan)
        w, h = cell_size(facing, 2, FOURX_SCALE)
        step_w = w + GUTTER
        draw_text(cv, MARGIN_LEFT, y, "RISE 4X")
        for index, tick in enumerate(triplet):
            draw_text(
                cv, MARGIN_LEFT + index * step_w, y + 8,
                f"T{tick['tick']:02d} {tick['poses']['B'].upper()}",
            )
        y += 16 + GUTTER
        for index, tick in enumerate(triplet):
            self.window_cell(
                cv, MARGIN_LEFT + index * step_w, y, "zone_1", facing, 2,
                tick["poses"]["B"], tick["axis_px"] - TILE,
                section="fourx", timeline="B", tick=tick["tick"],
                phase=tick["phase"], scale=FOURX_SCALE,
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
        """Derived diagnostic (banked diff_pixels): x0 vs its endpoints and
        the two declared ambiguity poses. Not a creature cell - excluded from
        the purity manifest by design."""
        draw_text(cv, 2, y + TILE - 2, "DIFF")
        for index, (inbetween, other) in enumerate(DIFF_PAIRS):
            x = MARGIN_LEFT + index * (TILE * TWOX_SCALE + GUTTER)
            cv.fill_rect(x, y, TILE * TWOX_SCALE, TILE * TWOX_SCALE, (30, 30, 30, 255))
            cv.blit_scaled(
                motion.diff_pixels(
                    self.poses[facing][other], self.poses[facing][inbetween]
                ),
                x, y, TWOX_SCALE,
            )
            draw_text(
                cv, x, y + TILE * TWOX_SCALE - 6,
                f"{inbetween.upper()} {other.upper()}",
            )
        return y + TILE * TWOX_SCALE + GUTTER

    def grammar_row(self, cv, y: int, facing: str) -> int:
        """The banked static grammar control row with the in-betweens at
        their timeline positions: w0 before the coil pair (windup tick 1),
        s0 before the settle (recovery tick 1), x0 after the settle
        (recovery tick 8)."""
        zone1 = self.reference["zones"]["zone_1"]
        lunge = self.reference["feedback_states"]["lunge_offset"]
        cell_w = TILE if facing == "down" else 2 * TILE
        cell_h = 2 * TILE if facing == "down" else TILE
        cells = (
            ("IDLE", "idle", 0),
            ("F1", "f1", 0),
            ("W0", "w0", lunge["windup_px"]),
            ("A0", "a0", 0),
            ("WIND", "a0", lunge["windup_px"]),
            ("K0", "k0", 0),
            ("LUNGE", "k0", lunge["active_px"]),
            ("S0", "s0", 0),
            ("R0", "r0", 0),
            ("X0", "x0", 0),
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
            y = self.fourx_row(cv, y, facing)
            y = self.film_rows(cv, y, facing)
            y = self.diff_row(cv, y, facing)
            y = self.grammar_row(cv, y, facing) + GUTTER
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: RiseTimelineSheet, facing: str) -> list[Rgba8Canvas]:
    """Per tick: timelines A and B side by side over a 3-tile window, 4x NN."""
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
                (TILE * 2 + GUTTER) * APNG_SCALE, TILE * 3 * APNG_SCALE, BG
            )
            offsets = [(0, 0), ((TILE + GUTTER) * APNG_SCALE, 0)]
        else:
            frame = Rgba8Canvas(
                TILE * 3 * APNG_SCALE, (TILE * 2 + GUTTER) * APNG_SCALE, BG
            )
            offsets = [(0, 0), (0, (TILE + GUTTER) * APNG_SCALE)]
        for pane, (ox, oy) in zip(panes, offsets):
            frame.blit_scaled(canvas_pixels(pane), ox, oy, APNG_SCALE)
        frames.append(frame)
    return frames


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rise-exports", type=Path, default=ROOT / "exports" / "calibration-v7"
    )
    parser.add_argument(
        "--transition-exports", type=Path, default=ROOT / "exports" / "calibration-v6"
    )
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
        default=ROOT / "reviews" / "calibration-v7" / "timeline-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write timeline-ab-<facing>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    sheet = RiseTimelineSheet(
        args.rise_exports, args.transition_exports, args.recovery_exports,
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
