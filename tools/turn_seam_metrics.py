#!/usr/bin/env python3
"""Deterministic pure-turn seam metrics and validator (sprint 10).

Measures and machine-checks the pre-registered calibration-v10 bars
(reviews/calibration-v10/rationale.md). Zero new frames: every number is
computed from banked export bytes and pinned constants.

Conventions (fixed in the rationale before any number existed): window
coordinates x right / y down, canvas-origin; A = the first walk axis
positive in the walk direction, B = the direction turned to; pose deltas are
100*XOR/union on canvas-aligned export bytes (position-independent - the
draw vector never enters the comparison); squared displacement = dA^2 +
dB^2, exact integer; degenerate lanes carry the full along-axis delta in dA
with dB = 0 by construction.

Failure grouping (fixed in the rationale): INTEGRITY failures mean the
toolchain or frozen-state law is broken - the sprint stops until fixed;
MEASUREMENT failures (the M1 compound-cut band) are banked evidence feeding
the affected lane's sub-verdict. The body-binding table is report-only,
never a failure. `--check` exits nonzero on any failure of either group.

INTEGRITY: zero new exports (banked 26-pin checker + no calibration-v9/v10
exports dirs); jump tables complete (t01..t21 consecutive rows, 10 lanes);
the anchor map - context rows == the banked v9 context_deltas on all four
fields, frame-identical turn cuts == their own context pair, f3 == idle
byte-copy per facing, wrap/restart/walk-boundary rows == the banked v1
motion-metrics pairs, cross-lane pose-pair consistency, DEGEN prefix ==
CONTROL prefix; tick math exact (walk mapping, facing rule, commit ticks,
wrap structure, tween deltas per axis, REM, pose strip restricted to
idle/f0..f3); in-window by construction (lane windows, turn crops, wrap
strips, context/film tiles); determinism + purity (sheet/metrics/APNGs
byte-identical across independent builds and equal to committed bytes;
every creature cell dual-verified); category law - every numeric bar
compares within one facing-category (the v9 category-error lesson is
structural here: no cross-category dominance bar exists).

MEASUREMENT: M1 - per turn lane, the turn cut's pose delta <= the free-turn
context band max (live only for MID's compound f0@A -> f1@B cut; the
frame-identical cuts satisfy it by anchor equality).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_turn_timeline as timeline  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from seam_metrics import check_export_pins  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

TWEEN_DELTAS = (1, 1, 2, 3, 4, 3, 4, 3, 4, 3, 2, 1, 1)
EXPECTED_REM = {"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0}
FRAME_IDENTICAL_CUTS = {"EARLY": "f0", "LATE": "f2", "CONTROL": "f3"}
CONTEXT_FIELDS = (
    "popping_pct", "recolored_px", "silhouette_changed_px", "union_px",
)
TABLE_START = 1   # rows cover t01->t02 .. t20->t21
TABLE_END = 21
V1_PAIR_KEYS = {
    ("idle", "f0"): "f3->f0",  # f3 is the idle byte-copy (anchor 3)
    ("f0", "f1"): "f0->f1",
    ("f1", "f2"): "f1->f2",
    ("f2", "f3"): "f2->f3",
    ("f3", "f0"): "f3->f0",
}

CONVENTIONS = {
    "axes": (
        "window coordinates: x right, y down, canvas-origin; A = first walk "
        "axis positive in the walk direction; B = the direction turned to; "
        "degenerate lanes carry the full along-axis delta in dA with dB 0 "
        "by construction"
    ),
    "pose_delta": (
        "100*XOR/union on canvas-aligned export bytes (position-independent); "
        "0.0 only for identical pose AND facing"
    ),
    "squared": "dA^2 + dB^2, exact integer - no scalarized pose+position metric",
    "tiles": (
        "T0 = the A step's origin tile; T1 = its committed/landing tile (one "
        "tile along A); T2 = T1+B (the B step's landing); the T0/T1 grid "
        "line is the boundary the strafing body crosses"
    ),
    "turn_cut": (
        "pose(turn-1)@A -> pose(turn)@B; REM = 13 - (turn - 1) advances "
        "remain after the turn tick's own advance"
    ),
    "category_law": (
        "every numeric bar compares within ONE facing-category (v9 "
        "category-error lesson): turn cuts and contexts against each other; "
        "same-facing rows against banked walk-cycle values; no raw "
        "cross-category dominance bar exists"
    ),
}

DRAWING_MODEL = (
    "banked v1 walk mapping f0x4/f1x3/f2x3/f3x3 over each step's 13 "
    "advances; step-commit ticks draw the standing pose (t01 idle@A; "
    "CONTROL t15 idle@B); a mid-tween re-face swaps the FACING of the drawn "
    "walk frame from the turn tick on while the frame INDEX continues from "
    "step progress; the B step's frames restart at f0; draw position = 2D "
    "tween, no offset anywhere (lunge_offset [0,0] outside attacks - "
    "engine fact at the pin)"
)


class TurnMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- frames --------------------------------------------------------------------


def load_frames(dirs: dict[str, Path]) -> dict[str, dict[str, dict]]:
    return {
        facing: {
            pose: load_opaque(
                dirs[timeline.POSE_DIRS[pose]]
                / timeline.pose_filename(pose, facing)
            )
            for pose in timeline.WALK_POSES
        }
        for facing in timeline.FACINGS
    }


# -- jump tables -----------------------------------------------------------------


def axis_delta(window: dict, delta: tuple[int, int]) -> tuple[int, int]:
    """(dA, dB) from a window delta (dx, dy) under the lane's axes."""
    dx, dy = delta
    d_a = dy if window["a_axis"] == "y" else dx
    if window["kind"] == "degen":
        return d_a, 0
    d_b = dy if window["b_axis"] == "y" else dx
    return d_a, d_b


def lane_jump_table(
    pair: str, lane: str, plan: dict, frames: dict[str, dict[str, dict]]
) -> list[dict]:
    data = plan["pairs"][pair]["lanes"][lane]
    ticks = data["ticks"]
    window = data["window"]
    rows = []
    for before, after in zip(
        ticks[TABLE_START:TABLE_END], ticks[TABLE_START + 1:TABLE_END + 1]
    ):
        same = (
            before["pose"] == after["pose"]
            and before["pose_facing"] == after["pose_facing"]
        )
        delta = (
            0.0
            if same
            else pair_stats(
                frames[before["pose_facing"]][before["pose"]],
                frames[after["pose_facing"]][after["pose"]],
            )["popping_pct"]
        )
        dx = after["draw"][0] - before["draw"][0]
        dy = after["draw"][1] - before["draw"][1]
        d_a, d_b = axis_delta(window, (dx, dy))
        rows.append(
            {
                "from_tick": before["tick"],
                "to_tick": after["tick"],
                "pose_from": before["pose"],
                "pose_from_facing": before["pose_facing"],
                "pose_to": after["pose"],
                "pose_to_facing": after["pose_facing"],
                "pose_delta_pct": delta,
                "delta_a_px": d_a,
                "delta_b_px": d_b,
                "delta_window_px": [dx, dy],
                "squared_px": d_a * d_a + d_b * d_b,
                "phase_to": after["phase"],
            }
        )
    return rows


def turn_cut_row(pair: str, lane: str, plan: dict, table: list[dict]) -> dict | None:
    turn = plan["pairs"][pair]["lanes"][lane]["turn_tick"]
    if turn is None:
        return None
    return next(r for r in table if r["to_tick"] == turn)


# -- context + anchors -------------------------------------------------------------


def context_deltas(frames: dict[str, dict[str, dict]]) -> dict:
    context = {"idle": pair_stats(frames["down"]["idle"], frames["right"]["idle"])}
    for index in range(4):
        pose = f"f{index}"
        context[pose] = pair_stats(frames["down"][pose], frames["right"][pose])
    return context


def check_context_anchor(context: dict, v9_metrics_path: Path) -> list[str]:
    """Anchor 1: fresh context rows == the banked v9 context_deltas on all
    four fields, exactly."""
    if not v9_metrics_path.is_file():
        return [f"missing banked v9 metrics {v9_metrics_path}"]
    banked = json.loads(v9_metrics_path.read_text(encoding="utf-8"))[
        "context_deltas"
    ]
    failures = []
    for pose, want in banked.items():
        for field in CONTEXT_FIELDS:
            if context[pose][field] != want[field]:
                failures.append(
                    f"context {pose}.{field} {context[pose][field]} != "
                    f"banked v9 {want[field]}"
                )
    return failures


def check_bytecopy(frames: dict[str, dict[str, dict]]) -> list[str]:
    """Anchor 3: f3 is the idle byte-copy, both facings (banked release
    note made law)."""
    return [
        f"f3@{facing} pixels differ from idle@{facing} (byte-copy law)"
        for facing in timeline.FACINGS
        if frames[facing]["f3"] != frames[facing]["idle"]
    ]


def check_cut_anchors(report_tables: dict, context: dict, plan: dict) -> list[str]:
    """Anchor 2: frame-identical turn cuts == their own context pair.
    MID is asserted NOT frame-identical (its compound cut is the sprint's
    novel number)."""
    failures = []
    for pair in timeline.PAIRS:
        for lane, pose in FRAME_IDENTICAL_CUTS.items():
            cut = report_tables[pair][lane]["turn_cut"]
            want = context[pose]["popping_pct"]
            if cut["pose_delta_pct"] != want:
                failures.append(
                    f"{pair}/{lane}: frame-identical cut "
                    f"{cut['pose_delta_pct']} != context {pose} {want}"
                )
        mid = report_tables[pair]["MID"]["turn_cut"]
        if (mid["pose_from"], mid["pose_to"]) != ("f0", "f1"):
            failures.append(
                f"{pair}/MID: cut poses {mid['pose_from']}->{mid['pose_to']} "
                "!= the pre-registered compound f0->f1"
            )
    return failures


def load_v1_pairs(v1_metrics_path: Path) -> dict[str, dict[str, float]] | None:
    if not v1_metrics_path.is_file():
        return None
    banked = json.loads(v1_metrics_path.read_text(encoding="utf-8"))["facings"]
    return {
        facing: {p["pair"]: p["popping_pct"] for p in banked[facing]["pairs"]}
        for facing in timeline.FACINGS
    }


def check_walk_pair_anchors(
    report_tables: dict, plan: dict, v1_metrics_path: Path
) -> list[str]:
    """Anchors 4-6: every same-facing non-zero row == the banked v1
    motion-metrics pair for its facing (wrap, restart, and walk-cycle
    boundaries); zero rows only for identical pose+facing; the ONLY
    cross-facing rows are the turn cuts."""
    pairs = load_v1_pairs(v1_metrics_path)
    if pairs is None:
        return [f"missing banked v1 metrics {v1_metrics_path}"]
    failures = []
    for pair in timeline.PAIRS:
        for lane in timeline.SECTION_LANES:
            turn = plan["pairs"][pair]["lanes"][lane]["turn_tick"]
            for row in report_tables[pair][lane]["rows"]:
                tag = f"{pair}/{lane} t{row['from_tick']:02d}->t{row['to_tick']:02d}"
                cross = row["pose_from_facing"] != row["pose_to_facing"]
                if cross:
                    if turn is None or row["to_tick"] != turn:
                        failures.append(f"{tag}: unexpected cross-facing row")
                    continue
                if row["pose_from"] == row["pose_to"]:
                    if row["pose_delta_pct"] != 0.0:
                        failures.append(f"{tag}: identical pose pair delta != 0")
                    continue
                key = (row["pose_from"], row["pose_to"])
                banked_key = V1_PAIR_KEYS.get(key)
                if banked_key is None:
                    failures.append(f"{tag}: unexpected same-facing pair {key}")
                    continue
                want = pairs[row["pose_from_facing"]][banked_key]
                if row["pose_delta_pct"] != want:
                    failures.append(
                        f"{tag}: {key[0]}->{key[1]}@{row['pose_from_facing']} "
                        f"{row['pose_delta_pct']} != banked v1 {want}"
                    )
    return failures


def check_cross_lane_consistency(report_tables: dict) -> list[str]:
    """Anchor 7: every repetition of the same pose-pair@facing carries the
    identical delta (pose deltas are pure byte-pair functions)."""
    seen: dict[tuple, tuple[float, str]] = {}
    failures = []
    for pair in timeline.PAIRS:
        for lane in timeline.SECTION_LANES:
            for row in report_tables[pair][lane]["rows"]:
                key = (
                    row["pose_from"], row["pose_from_facing"],
                    row["pose_to"], row["pose_to_facing"],
                )
                tag = f"{pair}/{lane} t{row['from_tick']:02d}"
                if key in seen:
                    want, where = seen[key]
                    if row["pose_delta_pct"] != want:
                        failures.append(
                            f"{tag}: {key} delta {row['pose_delta_pct']} != "
                            f"{want} at {where}"
                        )
                else:
                    seen[key] = (row["pose_delta_pct"], tag)
    return failures


def check_degen_prefix(report_tables: dict) -> list[str]:
    """Anchor 8: DEGEN rows t01..t14 == the same pair's CONTROL rows (both
    are the identical uncut walk @A to arrival), row for row."""
    failures = []
    for pair in timeline.PAIRS:
        control = [
            r for r in report_tables[pair]["CONTROL"]["rows"] if r["to_tick"] <= 14
        ]
        degen = [
            r for r in report_tables[pair]["DEGEN"]["rows"] if r["to_tick"] <= 14
        ]
        if len(control) != len(degen):
            failures.append(f"{pair}: DEGEN/CONTROL prefix row counts differ")
            continue
        for mine, want in zip(degen, control):
            tag = f"{pair}/DEGEN t{want['from_tick']:02d}->t{want['to_tick']:02d}"
            for field in (
                "from_tick", "to_tick", "pose_from", "pose_to",
                "pose_from_facing", "pose_to_facing", "pose_delta_pct",
                "delta_a_px", "delta_b_px",
            ):
                if mine[field] != want[field]:
                    failures.append(
                        f"{tag}: {field} {mine[field]} != CONTROL {want[field]}"
                    )
    return failures


# -- measurement (M1) --------------------------------------------------------------


def band_report(report_tables: dict, context: dict) -> dict:
    """M1: per turn lane the cut sits at or below the free-turn context band
    max (the largest facing swap the walk system can draw). Live only for
    MID's compound cut; frame-identical cuts satisfy it by anchor
    equality."""
    band_max = max(stats["popping_pct"] for stats in context.values())
    band_min = min(stats["popping_pct"] for stats in context.values())
    cuts = {}
    for pair in timeline.PAIRS:
        for lane in timeline.TURN_LANES:
            cut = report_tables[pair][lane]["turn_cut"]
            cuts[f"{pair}/{lane}"] = {
                "pose_from": cut["pose_from"],
                "pose_to": cut["pose_to"],
                "pose_delta_pct": cut["pose_delta_pct"],
                "within_band": cut["pose_delta_pct"] <= band_max,
            }
    return {"band_max": band_max, "band_min": band_min, "cuts": cuts}


def check_band(band: dict) -> list[str]:
    return [
        f"{key}: turn cut {cut['pose_delta_pct']} exceeds the free-turn "
        f"context band max {band['band_max']}"
        for key, cut in band["cuts"].items()
        if not cut["within_band"]
    ]


# -- body-tile binding (report-only) -------------------------------------------------


def binding_rows(
    pair: str, lane: str, plan: dict, frames: dict[str, dict[str, dict]]
) -> list[dict]:
    """Per strafe tick: the drawn frame's body extent along A, overlap px
    with T0's and T1's A-spans, and the majority tile (ties -> T0, the tile
    being left - declared). Report-only; the rubric judges bind quality."""
    data = plan["pairs"][pair]["lanes"][lane]
    window = data["window"]
    a_index = 1 if window["a_axis"] == "y" else 0
    t0_span = window["t0_a_span"]
    t1_span = window["t1_a_span"]
    rows = []
    for tick in data["ticks"]:
        if tick["phase"] != "strafe":
            continue
        stats = frame_stats(frames[tick["pose_facing"]][tick["pose"]])
        bbox = stats["bbox"]  # [x0, y0, x1, y1]
        lo = tick["a_px"] + bbox[a_index]
        hi = tick["a_px"] + bbox[a_index + 2]
        in_t0 = max(0, min(hi, t0_span[1]) - max(lo, t0_span[0]) + 1)
        in_t1 = max(0, min(hi, t1_span[1]) - max(lo, t1_span[0]) + 1)
        rows.append(
            {
                "tick": tick["tick"],
                "pose": tick["pose"],
                "pose_facing": tick["pose_facing"],
                "a_px": tick["a_px"],
                "body_a_extent": [lo, hi],
                "body_overlap_t0_px": in_t0,
                "body_overlap_t1_px": in_t1,
                "majority_tile": "T1" if in_t1 > in_t0 else "T0",
            }
        )
    return rows


def binding_summary(rows: list[dict]) -> dict:
    t0_run = 0
    longest_t0_run = 0
    crossover = None
    for row in rows:
        if row["majority_tile"] == "T0":
            t0_run += 1
            longest_t0_run = max(longest_t0_run, t0_run)
        else:
            if crossover is None:
                crossover = row["tick"]
            t0_run = 0
    return {
        "strafe_ticks": len(rows),
        "t0_majority_ticks": sum(1 for r in rows if r["majority_tile"] == "T0"),
        "longest_t0_majority_run": longest_t0_run,
        "first_t1_majority_tick": crossover,
    }


# -- structural checks ----------------------------------------------------------


def check_tick_math(plan: dict) -> list[str]:
    """Bar 4: the whole plan re-derived independently from the pinned
    constants and the declared model."""
    failures: list[str] = []
    step = plan["constants"]["step_frames"]
    positions = [timeline.tween_position(k, step) for k in range(step + 1)]
    deltas = tuple(b - a for a, b in zip(positions, positions[1:]))
    if deltas != TWEEN_DELTAS:
        failures.append(f"tween deltas {deltas} != pinned {TWEEN_DELTAS}")
    if positions[-1] != TILE:
        failures.append(f"tween arrival {positions[-1]} != {TILE}")
    for pair, section in plan["pairs"].items():
        for lane, data in section["lanes"].items():
            tag = f"{pair}/{lane}"
            turn = data["turn_tick"]
            walk_facing = data["walk_facing"]
            turn_facing = data["turn_facing"]
            commit_b = data["b_commit_tick"]
            if lane == "DEGEN":
                if turn is not None or walk_facing != turn_facing:
                    failures.append(f"{tag}: degenerate lane carries a turn")
            else:
                if data["rem_after_turn"] != EXPECTED_REM[lane]:
                    failures.append(
                        f"{tag}: REM {data['rem_after_turn']} != "
                        f"pre-registered {EXPECTED_REM[lane]}"
                    )
                want_commit = 15 if lane == "CONTROL" else 14
                if commit_b != want_commit:
                    failures.append(
                        f"{tag}: B commit tick {commit_b} != {want_commit}"
                    )
                if data["first_b_advance_tick"] != want_commit + 1:
                    failures.append(f"{tag}: first B advance tick wrong")
            if data["arrival_tick"] != 14:
                failures.append(f"{tag}: arrival tick != 14")
            for tick in data["ticks"]:
                t = tick["tick"]
                expected_a = timeline.tween_position(t - 1, step)
                expected_b = timeline.tween_position(t - commit_b, step)
                if (tick["a_px"], tick["b_px"]) != (expected_a, expected_b):
                    failures.append(
                        f"{tag}/t{t:02d}: tween ({tick['a_px']},{tick['b_px']})"
                        f" != ({expected_a},{expected_b})"
                    )
                expected_draw = list(
                    timeline.draw_vector(
                        walk_facing, turn_facing, expected_a, expected_b
                    )
                )
                if tick["draw"] != expected_draw:
                    failures.append(
                        f"{tag}/t{t:02d}: draw {tick['draw']} != {expected_draw}"
                    )
                if turn is None:
                    expected_facing = walk_facing
                else:
                    expected_facing = walk_facing if t < turn else turn_facing
                if tick["pose_facing"] != expected_facing:
                    failures.append(
                        f"{tag}/t{t:02d}: facing {tick['pose_facing']} != "
                        f"{expected_facing}"
                    )
                if tick["pose"] not in timeline.WALK_POSES:
                    failures.append(f"{tag}/t{t:02d}: pose outside walk strip")
                if t < timeline.IDLE_PRE_TICKS:
                    want_pose, want_phase = "idle", "idle_pre"
                elif t <= 14:
                    want_pose = f"f{timeline.walk_frame_index(t - 1, step)}"
                    if turn is None:
                        want_phase = "walk_1"
                    else:
                        want_phase = "walk_a" if t < turn else "strafe"
                elif lane == "CONTROL" and t == 15:
                    want_pose, want_phase = "idle", "turn_stand"
                elif t <= commit_b + step:
                    want_pose = f"f{timeline.walk_frame_index(t - commit_b, step)}"
                    want_phase = "walk_2" if turn is None else "walk_b"
                else:
                    want_pose, want_phase = "idle", "idle_post"
                if (tick["pose"], tick["phase"]) != (want_pose, want_phase):
                    failures.append(
                        f"{tag}/t{t:02d}: pose/phase "
                        f"({tick['pose']},{tick['phase']}) != "
                        f"({want_pose},{want_phase})"
                    )
    return failures


def check_bounds(plan: dict) -> list[str]:
    """Bar 5: every opaque pixel in-window BY CONSTRUCTION - the [2,2,29,29]
    contract bound added to every draw vector must land inside the lane
    window, the turn-zoom crop (its three ticks), and the wrap strip's full
    window - proven from the plan, never from put() clipping."""
    lo, hi = timeline.CONTRACT_BOUNDS
    failures: list[str] = []
    for pair, section in plan["pairs"].items():
        for lane, data in section["lanes"].items():
            tag = f"{pair}/{lane}"
            window = data["window"]
            w, h = window["w"], window["h"]
            for tick in data["ticks"]:
                dx, dy = tick["draw"]
                if dx + lo < 0 or dx + hi >= w or dy + lo < 0 or dy + hi >= h:
                    failures.append(
                        f"{tag}/t{tick['tick']:02d}: contract bounds escape "
                        f"window {w}x{h} at draw {tick['draw']}"
                    )
            for span_key in ("t0_a_span", "t1_a_span", "t2_a_span"):
                span = window[span_key]
                a_max = h if window["a_axis"] == "y" else w
                if span[0] < 0 or span[1] >= a_max:
                    failures.append(f"{tag}: {span_key} {span} outside window")
            if data["turn_crop"] is not None:
                crop_w, crop_h = data["turn_crop"]
                turn = data["turn_tick"]
                for tick in data["ticks"][turn - 1: turn + 2]:
                    dx, dy = tick["draw"]
                    if (
                        dx + lo < 0 or dx + hi >= crop_w
                        or dy + lo < 0 or dy + hi >= crop_h
                    ):
                        failures.append(
                            f"{tag}/t{tick['tick']:02d}: contract bounds "
                            f"escape turn crop {crop_w}x{crop_h}"
                        )
    return failures


# -- composition purity ----------------------------------------------------------


def reconstruct_cell(sheet: timeline.TurnTimelineSheet, cell: dict) -> Rgba8Canvas:
    composed = timeline.compose_cell(
        sheet.reference["zones"][cell["zone"]], cell["window_w"], cell["window_h"],
        sheet.poses[cell["pose_facing"]][cell["pose"]],
        cell["draw"][0], cell["draw"][1],
    )
    if cell["scale"] == 1:
        return composed
    temp = Rgba8Canvas(cell["rect"][2], cell["rect"][3], timeline.BG)
    temp.blit_scaled(timeline.canvas_pixels(composed), 0, 0, cell["scale"])
    return temp


def check_purity(
    canvas: Rgba8Canvas, sheet: timeline.TurnTimelineSheet, dirs: dict[str, Path]
) -> dict:
    failures: list[str] = []
    for cell in sheet.cells:
        x0, y0, w, h = cell["rect"]
        rebuilt = reconstruct_cell(sheet, cell)
        region_ok = all(
            canvas.get(x0 + px, y0 + py) == rebuilt.get(px, py)
            for py in range(h)
            for px in range(w)
        )
        if not region_ok:
            failures.append(f"region mismatch: {cell_id(cell)}")
            continue
        export = sprite_from_png(
            dirs[timeline.POSE_DIRS[cell["pose"]]]
            / timeline.pose_filename(cell["pose"], cell["pose_facing"])
        )
        dx, dy = cell["draw"]
        scale = cell["scale"]
        pixel_ok = all(
            canvas.get(x0 + (dx + sx) * scale, y0 + (dy + sy) * scale)
            == (*rgb, 255)
            for sx, sy, rgb in export.pixels
        )
        if not pixel_ok:
            failures.append(f"export-byte mismatch: {cell_id(cell)}")
    return {"cells_checked": len(sheet.cells), "failures": failures}


def cell_id(cell: dict) -> str:
    return (
        f"{cell['section']}/{cell['pair']}/{cell['lane']}/{cell['zone']}/"
        f"tick{cell['tick']:02d}"
    )


# -- report ------------------------------------------------------------------------


def build_report(
    dirs: dict[str, Path],
    reference: dict,
    sheet_path: Path | None = None,
    apng_dir: Path | None = None,
    exports_root: Path | None = None,
    v9_metrics_path: Path | None = None,
    v1_metrics_path: Path | None = None,
) -> dict:
    frames = load_frames(dirs)
    sheet = timeline.TurnTimelineSheet(dirs, reference)
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.TurnTimelineSheet(dirs, reference).build().encode()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    turn_tables: dict[str, dict] = {}
    binding: dict[str, dict] = {}
    for pair in timeline.PAIRS:
        turn_tables[pair] = {}
        binding[pair] = {}
        for lane in timeline.SECTION_LANES:
            rows = lane_jump_table(pair, lane, sheet.plan, frames)
            turn_tables[pair][lane] = {
                "rows": rows,
                "turn_cut": turn_cut_row(pair, lane, sheet.plan, rows),
            }
            if lane in timeline.TURN_LANES:
                lane_binding = binding_rows(pair, lane, sheet.plan, frames)
                binding[pair][lane] = {
                    "rows": lane_binding,
                    "summary": binding_summary(lane_binding),
                }

    context = context_deltas(frames)
    band = band_report(turn_tables, context)

    apng = {}
    if apng_dir is not None:
        for pair in timeline.PAIRS:
            frames_list = timeline.build_apng_frames(sheet, pair)
            payload = timeline.encode_apng(
                frames_list, timeline.apng_delays(len(frames_list))
            )
            again = timeline.encode_apng(
                timeline.build_apng_frames(sheet, pair),
                timeline.apng_delays(len(frames_list)),
            )
            target = apng_dir / f"turn-lanes-{pair.lower()}.apng"
            apng[pair] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames_list),
            }

    exports = check_export_pins(exports_root or ROOT / "exports")
    for stale in ("calibration-v9", "calibration-v10"):
        if ((exports_root or ROOT / "exports") / stale).exists():
            exports["failures"].append(
                f"exports/{stale} exists - this sprint banks no exports"
            )

    return {
        "generated_by": "tools/turn_seam_metrics.py",
        "constants": sheet.plan["constants"],
        "conventions": CONVENTIONS,
        "drawing_model": DRAWING_MODEL,
        "tick_ms": TICK_MS,
        "turn_tables": turn_tables,
        "context_deltas": context,
        "band": band,
        "binding": binding,
        "context_anchor_failures": check_context_anchor(
            context,
            v9_metrics_path
            or ROOT / "reviews" / "calibration-v9" / "cross-seam-metrics.json",
        ),
        "bytecopy_failures": check_bytecopy(frames),
        "cut_anchor_failures": check_cut_anchors(turn_tables, context, sheet.plan),
        "walk_pair_anchor_failures": check_walk_pair_anchors(
            turn_tables, sheet.plan,
            v1_metrics_path
            or ROOT / "reviews" / "calibration-v1" / "motion-metrics.json",
        ),
        "consistency_failures": check_cross_lane_consistency(turn_tables),
        "degen_prefix_failures": check_degen_prefix(turn_tables),
        "tick_math_failures": check_tick_math(sheet.plan),
        "bounds_failures": check_bounds(sheet.plan),
        "sheet": {
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "deterministic": encoded == second,
            "committed_matches": committed,
            "cells": len(sheet.cells),
        },
        "apng": apng,
        "purity": check_purity(canvas, sheet, dirs),
        "export_pins": exports,
    }


def check_report(report: dict) -> dict[str, list[str]]:
    """INTEGRITY failures stop the sprint; MEASUREMENT failures are banked
    evidence for the affected lane's sub-verdict (pre-registered split)."""
    integrity: list[str] = []
    for key in (
        "context_anchor_failures", "bytecopy_failures", "cut_anchor_failures",
        "walk_pair_anchor_failures", "consistency_failures",
        "degen_prefix_failures", "tick_math_failures", "bounds_failures",
    ):
        integrity.extend(report[key])
    if not report["sheet"]["deterministic"]:
        integrity.append("sheet builds are not byte-identical across two runs")
    if report["sheet"]["committed_matches"] is False:
        integrity.append("committed sheet bytes differ from a fresh build")
    for pair, aid in report["apng"].items():
        if not aid["deterministic"]:
            integrity.append(f"apng {pair}: builds not byte-identical")
        if aid["committed_matches"] is False:
            integrity.append(f"apng {pair}: committed bytes differ from fresh build")
    integrity.extend(report["purity"]["failures"])
    integrity.extend(report["export_pins"]["failures"])
    return {"integrity": integrity, "measurement": check_band(report["band"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = timeline.default_dirs()
    for key, value in defaults.items():
        flag = "--" + key.replace("_dir", "-exports").replace("_", "-")
        parser.add_argument(flag, dest=key, type=Path, default=value)
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "manifests" / "render-reference.json"
    )
    parser.add_argument(
        "--sheet", type=Path,
        default=ROOT / "reviews" / "calibration-v10" / "turn-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v10" / "turn-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        report = build_report(
            dirs, reference, sheet_path=args.sheet, apng_dir=args.apng_dir
        )
    except (TurnMetricsError, ValueError, OSError) as exc:
        print(f"metrics failed: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"wrote {args.out}")
    if args.check:
        failures = check_report(report)
        for failure in failures["integrity"]:
            print(f"INTEGRITY FAIL: {failure}", file=sys.stderr)
        for failure in failures["measurement"]:
            print(f"MEASUREMENT FAIL: {failure}", file=sys.stderr)
        if failures["integrity"] or failures["measurement"]:
            return 1
        print(
            "checks passed: zero-new-exports + banked pins, jump tables, "
            "anchor map (context, byte-copy, cuts, walk pairs, consistency, "
            "degen prefix), compound-cut band, tick math, in-bounds by "
            "construction, byte-determinism, composition purity"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
