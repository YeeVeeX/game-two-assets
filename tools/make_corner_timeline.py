#!/usr/bin/env python3
"""Corner-turn + settle-hold remedy timeline sheet (sprint 11, calibration-v11).

Measurement sprint: ZERO new frames, zero exports, no attack anywhere. Two
threads fall out of the banked v10 verdict, both composition-only:

- CORNER (the v10 next-hypothesis): B pressed exactly at t14, the ARRIVAL
  tick. Derived at the live pin: step A commits at t01's controller, its 13
  advances land at t02..t14 tick_body (world.rb L687-688 runs tick_body
  BEFORE the controller loop L692-699), so at t14's controller moving? is
  already false (grid_walker.rb L32, L36) and a same-tick B press faces
  (controllers.rb L51-52; creature.rb L142-144) AND commits (L56) on that
  tick. commit_dash sets no pixel position, so t14 draws the A-arrival in
  facing B and the first B advance lands at t15. Turn = commit = arrival:
  REM 0, no stand beat, no strafe segment.
- REM_EARLY / REM_MID (EXP-class): the banked v10 recommendation - "when
  facing is perpendicular to travel, select the settle frame instead of
  cycling the gait" - rendered as a DECLARED-MODEL VARIANT at v10's two
  failing turn ticks. Never a production lane, never a runtime claim.
- CONTROL and DEGEN re-render v10's lanes VERBATIM (the same banked
  lane_tick called with the same arguments) as the toolchain-regression bar.

Drawing models (pre-registered in reviews/calibration-v11/rationale.md):
Model A is the v10 walk model unchanged (banked v1 mapping f0x4/f1x3/f2x3/
f3x3 over each step's 13 advances; commit ticks draw the standing pose; a
mid-tween re-face swaps the FACING while the frame INDEX continues from step
progress; f3 is the idle byte-copy, so the corner tick's two candidate rules
agree byte-for-byte). Model B adds ONE clause: on a REMEDY lane every strafe
tick (turn tick through arrival) draws f3 in facing B at the tween position
instead of the cycling walk frame. Draw position = 2D tween, no offset
anywhere (lunge_offset is [0,0] outside attacks - renderer.rb L560-569).

Sheet rows per pair section (1 column = 1 tick, t01..t21):

- Per lane: label + RULER + Z1/Z2 rows over the lane window (turn lanes
  2x2 tiles; DEGEN the banked 3-tile axis window).
- CUT 3X: CORNER t13|t14|t15|t16, REMEDY turn-1|turn|turn+1, CONTROL
  t14|t15|t16 - cropped to the A-tile pair at B-column 0.
- WRAP 2X: per lane t13..t16 (CONTROL t14..t17), FULL window.
- CMP 2X bands: CORNER beside CONTROL (t12..t18, tick for tick) and REM_MID
  beside the BANKED v10 MID lane (t05..t15) - the v10 lane is composed
  in-process from the banked v10 plan; it is an aid, not a new measurement.
- CONTEXT 2X: the rendered stationary yardstick [fN@A | fN@B].
- FILM: the walk-pose identity strip, both facings, both zones.

Every creature cell is recorded in a machine-readable manifest consumed by
tools/corner_metrics.py for composition-purity, in-bounds and tick-math
verification. Layout is fixed; regeneration is byte-identical. Banked tools
are imported unmodified (make_turn_timeline and its ancestors); optional APNG
aids (corner-lanes-<pair>.apng: CORNER | REM_EARLY | REM_MID | banked MID |
CONTROL side by side, exact 1/60 s delays) are never blocking.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_turn_timeline as v10  # noqa: E402  (banked, imported unmodified)
from make_contact_sheet import GUTTER, MARGIN_LEFT, MARGIN_TOP, TILE  # noqa: E402
from make_turn_timeline import (  # noqa: E402
    APNG_SCALE,
    ARRIVAL_TICK,
    BG,
    FACINGS,
    PAIR_AXES,
    PAIRS,
    SHEET_SPAN,
    SHEET_START,
    TOTAL_TICKS,
    TURN_ZOOM_SCALE,
    TWOX_SCALE,
    WALK_POSES,
    WRAP_TICKS,
    apng_delays,
    canvas_pixels,
    compose_cell,
    default_dirs,
    draw_text,
    encode_apng,
    load_reference,
)
from png_writer import Rgba8Canvas  # noqa: E402

LANES = ("CORNER", "REM_EARLY", "REM_MID", "CONTROL", "DEGEN")
LANE_TURN = {
    "CORNER": ARRIVAL_TICK,        # 14 - turn == commit == arrival
    "REM_EARLY": 3,
    "REM_MID": 6,
    "CONTROL": ARRIVAL_TICK + 1,   # 15 - the v10 anchor lane
    "DEGEN": None,
}
LANE_MODEL = {
    "CORNER": "A", "REM_EARLY": "B", "REM_MID": "B",
    "CONTROL": "A", "DEGEN": "A",
}
LANE_CODE = {
    "CORNER": "C", "REM_EARLY": "E", "REM_MID": "M",
    "CONTROL": "K", "DEGEN": "D",
}
LANE_LABEL = {
    "CORNER": "CORNER TURN T14 REM 0 LANDING TICK",
    "REM_EARLY": "REM EARLY SETTLE HOLD T03 REM 11 EXP",
    "REM_MID": "REM MID SETTLE HOLD T06 REM 8 EXP",
    "CONTROL": "CONTROL TURN T15 REM 0 BANKED ANCHOR",
    "DEGEN": "DEGEN UNCUT 2 STEP BANKED ANCHOR",
}
HOLD_POSE = "f3"                   # the settle/standing byte-copy (Model B)
HOLD_PHASE = "strafe_hold"
CORNER_PHASE = "turn_arrive"
ZOOM_TICKS = {
    "CORNER": (13, 14, 15, 16),    # the corner event plus its restart
    "REM_EARLY": (2, 3, 4),
    "REM_MID": (5, 6, 7),
    "CONTROL": (14, 15, 16),
    "DEGEN": None,
}
PHASE_LABELS = dict(v10.PHASE_LABELS) | {
    CORNER_PHASE: "TURN ARR", HOLD_PHASE: "HOLD B",
}
CMP_BANDS = (
    {
        "key": "corner_control",
        "title": "CMP 2X CORNER BESIDE CONTROL TICK FOR TICK",
        "ticks": tuple(range(12, 19)),
        "rows": (("CORNER", "v11", "CORNER"), ("CONTROL", "v11", "CONTROL")),
    },
    {
        "key": "remedy_banked",
        "title": "CMP 2X REM MID SETTLE HOLD BESIDE BANKED MID CYCLING",
        "ticks": tuple(range(5, 16)),
        "rows": (("REM MID", "v11", "REM_MID"), ("BANKED MID", "v10", "MID")),
    },
)
APNG_PANES = (
    ("C", "v11", "CORNER"), ("E", "v11", "REM_EARLY"),
    ("M", "v11", "REM_MID"), ("B", "v10", "MID"), ("K", "v11", "CONTROL"),
)


def lane_axes(pair: str, lane: str) -> tuple[str, str]:
    """(walk_facing, turn_facing) for one lane of one pair section."""
    walk, turn = PAIR_AXES[pair]
    return (walk, walk) if lane == "DEGEN" else (walk, turn)


def lane_tick(
    tick: int, turn: int | None, model: str,
    walk_facing: str, turn_facing: str, step: int,
) -> dict:
    """One absolute tick of one lane. Model-A lanes are the banked v10
    function VERBATIM (so CONTROL/DEGEN reproduce v10 bit for bit and the
    corner lane inherits the verified arrival handoff); Model B substitutes
    the held settle pose on strafe ticks only, which is the sprint's single
    new declared clause."""
    base = v10.lane_tick(tick, turn, walk_facing, turn_facing, step)
    if base["phase"] != "strafe":
        return base
    if model == "B":
        return dict(base, pose=HOLD_POSE, phase=HOLD_PHASE)
    if turn == ARRIVAL_TICK:  # CORNER: the one B-facing tick IS the arrival
        return dict(base, phase=CORNER_PHASE)
    return base


def build_plan(reference: dict) -> dict:
    """The ten-lane plan: a pure function of the pinned constants, the
    pre-registered turn ticks, the pair axes and the two declared models."""
    step = reference["attack_timing"]["values"]["step_frames"]["value"]
    pairs: dict[str, dict] = {}
    for pair in PAIRS:
        walk, turn_f = PAIR_AXES[pair]
        lanes: dict[str, dict] = {}
        for lane in LANES:
            lane_walk, lane_turn = lane_axes(pair, lane)
            turn = LANE_TURN[lane]
            model = LANE_MODEL[lane]
            ticks = [
                lane_tick(t, turn, model, lane_walk, lane_turn, step)
                for t in range(TOTAL_TICKS)
            ]
            commit_b = ARRIVAL_TICK + 1 if turn == ARRIVAL_TICK + 1 else ARRIVAL_TICK
            b_facing_in_a = sum(
                1 for t in ticks
                if t["tick"] <= ARRIVAL_TICK and t["pose_facing"] == lane_turn
                and lane_turn != lane_walk
            )
            lanes[lane] = {
                "model": model,
                "turn_tick": turn,
                "rem_after_turn": None if turn is None else max(0, step - (turn - 1)),
                "b_facing_ticks_in_a_step": None if turn is None else b_facing_in_a,
                "hold_ticks": [
                    t["tick"] for t in ticks if t["phase"] == HOLD_PHASE
                ],
                "corner_ticks": [
                    t["tick"] for t in ticks if t["phase"] == CORNER_PHASE
                ],
                "arrival_tick": ARRIVAL_TICK,
                "b_commit_tick": commit_b,
                "first_b_advance_tick": commit_b + 1,
                "walk_facing": lane_walk,
                "turn_facing": lane_turn,
                "window": v10.window_spec(lane_walk, lane_turn),
                "turn_crop": (
                    None
                    if v10.turn_crop(lane_walk, lane_turn) is None
                    else list(v10.turn_crop(lane_walk, lane_turn))
                ),
                "zoom_ticks": (
                    None if ZOOM_TICKS[lane] is None else list(ZOOM_TICKS[lane])
                ),
                "ticks": ticks,
                "sheet_ticks": ticks[SHEET_START:SHEET_START + SHEET_SPAN],
            }
        pairs[pair] = {"walk_facing": walk, "turn_facing": turn_f, "lanes": lanes}
    return {
        "constants": {
            "step_frames": step,
            "arrival_tick": ARRIVAL_TICK,
            "turn_ticks": {k: v for k, v in LANE_TURN.items() if v is not None},
            "lane_models": dict(LANE_MODEL),
            "hold_pose": HOLD_POSE,
            "pair_axes": {pair: list(PAIR_AXES[pair]) for pair in PAIRS},
            "idle_pre_ticks": v10.IDLE_PRE_TICKS,
            "total_ticks": TOTAL_TICKS,
            "sheet_span": [SHEET_START, SHEET_START + SHEET_SPAN - 1],
            "zoom_ticks": {
                lane: (None if t is None else list(t))
                for lane, t in ZOOM_TICKS.items()
            },
            "comparison_bands": [
                {
                    "key": band["key"], "ticks": list(band["ticks"]),
                    "rows": [list(row) for row in band["rows"]],
                }
                for band in CMP_BANDS
            ],
        },
        "pairs": pairs,
    }


def zoom_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """The lane's declared cut-zoom ticks (CORNER carries four)."""
    data = plan["pairs"][pair]["lanes"][lane]
    return [data["ticks"][t] for t in data["zoom_ticks"]]


def wrap_strip(plan: dict, pair: str, lane: str) -> list[dict]:
    """Four ticks bracketing the arrival wrap: t13..t16 (CONTROL t14..t17 -
    its wrap events sit one tick later)."""
    data = plan["pairs"][pair]["lanes"][lane]
    start = 14 if data["turn_tick"] == ARRIVAL_TICK + 1 else 13
    return data["ticks"][start:start + WRAP_TICKS]


class CornerTimelineSheet(v10.TurnTimelineSheet):
    """Deterministic sheet builder that records every creature cell. The
    banked v10 builder supplies the cell recorder, the window compositor and
    the static rows unmodified; v11 overrides only the row set."""

    def __init__(self, dirs: dict[str, Path], reference: dict):
        self.dirs = dirs
        self.reference = reference
        self.plan = build_plan(reference)
        self.v10_plan = v10.build_plan(reference)  # the banked comparison lane
        self.poses = v10.load_poses(dirs)
        self.cells: list[dict] = []

    # -- sources ------------------------------------------------------------

    def source_lane(self, source: str, pair: str, lane: str) -> dict:
        plan = self.plan if source == "v11" else self.v10_plan
        return plan["pairs"][pair]["lanes"][lane]

    # -- geometry -----------------------------------------------------------

    def cut_row_width(self, pair: str) -> int:
        total = 0
        for lane in LANES:
            if ZOOM_TICKS[lane] is None:
                continue
            crop_w, _ = self.plan["pairs"][pair]["lanes"][lane]["turn_crop"]
            total += len(ZOOM_TICKS[lane]) * (crop_w * TURN_ZOOM_SCALE + GUTTER)
            total += GUTTER
        return total

    def wrap_row_width(self, pair: str) -> int:
        total = 0
        for lane in LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += WRAP_TICKS * (window["w"] * TWOX_SCALE + GUTTER) + GUTTER
        return total

    def band_width(self, pair: str, band: dict) -> int:
        width = 0
        for _, source, lane in band["rows"]:
            window = self.source_lane(source, pair, lane)["window"]
            width = max(width, window["w"] * TWOX_SCALE + GUTTER)
        return len(band["ticks"]) * width

    def band_height(self, pair: str, band: dict) -> int:
        rows = 0
        for _, source, lane in band["rows"]:
            window = self.source_lane(source, pair, lane)["window"]
            rows += window["h"] * TWOX_SCALE + GUTTER
        return 8 + 8 + GUTTER + rows

    def sheet_width(self) -> int:
        widths = [len(WALK_POSES) * (TILE + GUTTER), self.context_row_width()]
        for pair in PAIRS:
            widths.append(self.cut_row_width(pair))
            widths.append(self.wrap_row_width(pair))
            widths.extend(self.band_width(pair, band) for band in CMP_BANDS)
            widths.extend(self.lane_row_width(pair, lane) for lane in LANES)
        return MARGIN_LEFT + max(widths) + MARGIN_TOP

    def section_height(self, pair: str) -> int:
        total = 8 + GUTTER  # section header
        for lane in LANES:
            window = self.plan["pairs"][pair]["lanes"][lane]["window"]
            total += 8 + 16 + GUTTER + 2 * (window["h"] + GUTTER)
        cut_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["turn_crop"][1]
            for lane in LANES if ZOOM_TICKS[lane] is not None
        ) * TURN_ZOOM_SCALE
        wrap_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["window"]["h"]
            for lane in LANES
        ) * TWOX_SCALE
        total += 8 + 8 + GUTTER + cut_h + GUTTER
        total += 8 + 8 + GUTTER + wrap_h + GUTTER
        total += sum(self.band_height(pair, band) + GUTTER for band in CMP_BANDS)
        total += 8 + 8 + GUTTER + TILE * TWOX_SCALE + GUTTER  # context row
        return total

    # -- rows ---------------------------------------------------------------

    def ruler(self, cv, y: int, ticks: list[dict], step_w: int) -> None:
        """The v10 ruler over the v11 phase vocabulary (two added labels)."""
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
        draw_text(cv, MARGIN_LEFT, y, LANE_LABEL[lane])
        y += 8
        self.ruler(cv, y + 8, ticks, step_w)
        y += 16 + GUTTER
        for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
            draw_text(
                cv, 2, y + window["h"] // 2 - 2,
                f"{zone_label} {LANE_CODE[lane]}",
            )
            for index, tick in enumerate(ticks):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, zone_key, tick,
                    section="lane", pair=pair, lane=lane,
                    width=window["w"], height=window["h"],
                )
            y += window["h"] + GUTTER
        return y

    def cut_zoom_row(self, cv, y: int, pair: str) -> int:
        row_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["turn_crop"][1]
            for lane in LANES if ZOOM_TICKS[lane] is not None
        ) * TURN_ZOOM_SCALE
        draw_text(cv, MARGIN_LEFT, y, "CUT 3X CORNER AND SETTLE HOLD SEAMS")
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + row_h // 2 - 2, "CUT 3X")
        x = MARGIN_LEFT
        for lane in LANES:
            if ZOOM_TICKS[lane] is None:
                continue
            data = self.plan["pairs"][pair]["lanes"][lane]
            w, h = data["turn_crop"]
            for tick in zoom_strip(self.plan, pair, lane):
                draw_text(cv, x, labels_y, f"{LANE_CODE[lane]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section="cut", pair=pair, lane=lane,
                    width=w, height=h, scale=TURN_ZOOM_SCALE,
                )
                x += w * TURN_ZOOM_SCALE + GUTTER
            x += GUTTER
        return y + row_h + GUTTER

    def wrap_row(self, cv, y: int, pair: str) -> int:
        row_h = max(
            self.plan["pairs"][pair]["lanes"][lane]["window"]["h"]
            for lane in LANES
        ) * TWOX_SCALE
        draw_text(cv, MARGIN_LEFT, y, "WRAP 2X F3 TO F0 RESTART")
        y += 8
        labels_y = y
        y += 8 + GUTTER
        draw_text(cv, 2, y + row_h // 2 - 2, "WRP 2X")
        x = MARGIN_LEFT
        for lane in LANES:
            data = self.plan["pairs"][pair]["lanes"][lane]
            w, h = data["window"]["w"], data["window"]["h"]
            for tick in wrap_strip(self.plan, pair, lane):
                draw_text(cv, x, labels_y, f"{LANE_CODE[lane]}{tick['tick']:02d}")
                self.window_cell(
                    cv, x, y, "zone_1", tick,
                    section="wrap", pair=pair, lane=lane,
                    width=w, height=h, scale=TWOX_SCALE,
                )
                x += w * TWOX_SCALE + GUTTER
            x += GUTTER
        return y + row_h + GUTTER

    def comparison_band(self, cv, y: int, pair: str, band: dict) -> int:
        """Two treatments aligned tick for tick over absolute ticks. The
        BANKED row is composed from the v10 plan in-process: it is a reading
        aid for an already-banked lane, never a new measurement."""
        draw_text(cv, MARGIN_LEFT, y, band["title"])
        y += 8
        labels_y = y
        y += 8 + GUTTER
        step_w = max(
            self.source_lane(source, pair, lane)["window"]["w"] * TWOX_SCALE
            + GUTTER
            for _, source, lane in band["rows"]
        )
        for index, tick_no in enumerate(band["ticks"]):
            draw_text(cv, MARGIN_LEFT + index * step_w, labels_y, f"T{tick_no:02d}")
        for label, source, lane in band["rows"]:
            data = self.source_lane(source, pair, lane)
            window = data["window"]
            draw_text(cv, 2, y + window["h"] - 2, label[:6])
            for index, tick_no in enumerate(band["ticks"]):
                self.window_cell(
                    cv, MARGIN_LEFT + index * step_w, y, "zone_1",
                    data["ticks"][tick_no],
                    section="cmp", pair=pair,
                    lane=lane if source == "v11" else f"V10_{lane}",
                    width=window["w"], height=window["h"], scale=TWOX_SCALE,
                )
            y += window["h"] * TWOX_SCALE + GUTTER
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
            for lane in LANES:
                y = self.lane_rows(cv, y, pair, lane)
            y = self.cut_zoom_row(cv, y, pair)
            y = self.wrap_row(cv, y, pair)
            for band in CMP_BANDS:
                y = self.comparison_band(cv, y, pair, band) + GUTTER
            y = self.context_row(cv, y, pair)
            y += GUTTER
        for facing in FACINGS:
            y = self.film_rows(cv, y, facing)
        return cv


# -- APNG viewing aid (optional, never blocking) ------------------------------


def build_apng_frames(sheet: CornerTimelineSheet, pair: str) -> list[Rgba8Canvas]:
    """Per tick t00..t29: the corner lane, both settle-hold remedy lanes, the
    BANKED v10 cycling MID lane and CONTROL side by side over their full
    2x2-tile windows - the remedy beside the treatment it is meant to
    replace."""
    zone = sheet.reference["zones"]["zone_1"]
    window = sheet.plan["pairs"][pair]["lanes"]["CORNER"]["window"]
    panes = len(APNG_PANES)
    frames = []
    for t in range(TOTAL_TICKS):
        frame = Rgba8Canvas(
            (window["w"] * panes + GUTTER * (panes - 1)) * APNG_SCALE,
            window["h"] * APNG_SCALE, BG,
        )
        for index, (code, source, lane) in enumerate(APNG_PANES):
            tick = sheet.source_lane(source, pair, lane)["ticks"][t]
            pane = compose_cell(
                zone, window["w"], window["h"],
                sheet.poses[tick["pose_facing"]][tick["pose"]],
                tick["draw"][0], tick["draw"][1],
            )
            draw_text(pane, 2, 2, code)
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
        "--reference", type=Path,
        default=ROOT / "manifests" / "render-reference.json",
    )
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v11" / "corner-sheet.png",
    )
    parser.add_argument(
        "--apng-dir", type=Path, default=None,
        help="also write corner-lanes-<pair>.apng viewing aids (optional)",
    )
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    sheet = CornerTimelineSheet(dirs, reference)
    canvas = sheet.build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out)
    print(f"wrote {args.out}")
    if args.apng_dir is not None:
        args.apng_dir.mkdir(parents=True, exist_ok=True)
        for pair in PAIRS:
            frames = build_apng_frames(sheet, pair)
            payload = encode_apng(frames, apng_delays(len(frames)))
            target = args.apng_dir / f"corner-lanes-{pair.lower()}.apng"
            target.write_bytes(payload)
            print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
