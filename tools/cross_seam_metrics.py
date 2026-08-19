#!/usr/bin/env python3
"""Deterministic cross-facing onset-seam metrics and validator (sprint 9).

Measures and machine-checks the pre-registered calibration-v9 bars
(reviews/calibration-v9/rationale.md). Zero new frames: every number is
computed from banked export bytes and pinned constants.

Conventions (fixed in the rationale before any number existed): window
coordinates x right / y down, canvas-origin; A = walk axis positive in the
walk direction, B = attack facing positive toward the arc tile; w0 IS windup
tick 1 and draws at the windup offset; pose deltas are 100*XOR/union on
canvas-aligned export bytes (position-independent); squared displacement =
dA^2 + dB^2, exact integer; degenerate lanes carry the full along-axis delta
in dA with dB-perpendicular 0 by construction.

Failure grouping (fixed in the rationale): INTEGRITY failures mean the
toolchain or frozen-state law is broken - the sprint stops until fixed;
MEASUREMENT failures (release-salience dominance) are banked evidence feeding
the affected lane's sub-verdict. The anchoring-overlap table is report-only,
never a failure. `--check` exits nonzero on any failure of either group.

1. zero new exports (INTEGRITY) - the banked v8 checker (26 pinned PNGs over
   seven releases) plus: no exports/calibration-v9 directory exists;
2. 2D seam jump tables - per pair, per lane: pose delta AND (dA, dB) +
   window (dx, dy) + squared magnitude for every consecutive tick pair from
   onset-2 through onset+10 (EARLY: onset+12);
3. degenerate regression (INTEGRITY, hard) - DEGEN lane tables machine-equal
   to the committed reviews/calibration-v8/seam-metrics.json CONTROL rows:
   pose names, pose delta, dA == the v8 scalar, dB == 0, row for row;
4. release salience (MEASUREMENT) - per lane the a0->k0 row strictly largest
   pose delta AND strictly largest squared displacement, both axes separately;
5. anchoring-overlap table (report-only) - per lane per active tick:
   B-crossing depth past the arc-side grid line, body A-extent overlap with
   the TRUE arc tile and the NEAR tile, crossing-pixel bind counts;
6. cross-facing context deltas (INTEGRITY) - fN(A)<->fN(B) reported and
   idle<->idle reproduces the banked 44.44 exactly;
7. tick math (INTEGRITY) - grammar composition, offsets along B only from
   onset, walk facings A before onset / attack facings B after, tween deltas
   1,1,2,3,4,3,4,3,4,3,2,1,1, REM + arrival-phase per class, r0 hold = 6;
8. determinism + purity (INTEGRITY) - sheet (and any APNG aid) byte-identical
   across two independent builds and equal to committed bytes; every creature
   cell dual-verified (2D region reconstruction + direct export-byte
   equality);
9. in-window by construction (INTEGRITY) - every draw vector + the
   [2,2,29,29] contract bounds proven inside the window dims from the plan
   (never relying on put() clipping), for lane windows and strip crops; both
   candidate strike tiles inside every lane window by construction.
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

import make_cross_seam_timeline as timeline  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from seam_metrics import check_export_pins, table_range  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

TWEEN_DELTAS = (1, 1, 2, 3, 4, 3, 4, 3, 4, 3, 2, 1, 1)
CROSSING_CANVAS_B = 26  # canvas-B >= 26 crosses the grid line at the +6 offset
EXPECTED_REM = {"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0, "DEGEN": 0}
ARRIVAL_PHASE = {
    "EARLY": ("recovery", 3), "MID": ("active", 4), "LATE": ("windup", 5),
    "CONTROL": ("pre-onset", 0), "DEGEN": ("pre-onset", 0),
}
V8_CONTROL_FACING = {"DR": "down", "RD": "right"}
IDLE_CROSS_REFERENCE = 44.44

CONVENTIONS = {
    "axes": (
        "window coordinates: x right, y down, canvas-origin; A = walk axis "
        "positive in the walk direction; B = attack facing positive toward "
        "the arc tile; degenerate lanes carry the full along-axis delta in "
        "dA with dB-perpendicular 0 by construction"
    ),
    "w0": "w0 IS windup tick 1 and draws at the windup offset (-3 along B)",
    "pose_delta": (
        "100*XOR/union on canvas-aligned export bytes (position-independent); "
        "0.0 only for identical pose AND facing"
    ),
    "squared": "dA^2 + dB^2, exact integer - no scalarized pose+position metric",
    "tiles": (
        "T0 = step origin tile; T1 = committed tile (one tile along A); TRUE "
        "arc = T1+B (front1 at the committed tile); NEAR = T0+B; the arc-side "
        "grid line is the shared boundary at window-B 64"
    ),
}


class CrossSeamMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- frames --------------------------------------------------------------------


def load_frames(dirs: dict[str, Path]) -> dict[str, dict[str, dict]]:
    return {
        facing: {
            pose: load_opaque(
                dirs[timeline.POSE_DIRS[pose]]
                / timeline.pose_filename(pose, facing)
            )
            for pose in timeline.STRIP
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
    onset = data["onset_tick"]
    ticks = data["ticks"]
    window = data["window"]
    start, end = table_range(lane, onset)
    rows = []
    for before, after in zip(ticks[start:end], ticks[start + 1:end + 1]):
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


def release_salience(table: list[dict], onset: int) -> dict:
    """The a0->k0 row against BOTH axes separately (pose delta and squared
    displacement) - strict dominance is a MEASUREMENT bar cross-facing: the
    onset cut is unmeasured and may legitimately exceed the release pose
    delta (pre-registered; a red here feeds the lane's sub-verdict)."""
    release = next(
        r for r in table if r["from_tick"] == onset + 4 and r["to_tick"] == onset + 5
    )
    others = [r for r in table if r is not release]
    max_other_pose = max(r["pose_delta_pct"] for r in others)
    max_other_squared = max(r["squared_px"] for r in others)
    return {
        "release_row": release,
        "max_other_pose_delta_pct": max_other_pose,
        "max_other_squared_px": max_other_squared,
        "pose_axis_strictly_dominant": release["pose_delta_pct"] > max_other_pose,
        "squared_axis_strictly_dominant": release["squared_px"] > max_other_squared,
    }


# -- anchoring -------------------------------------------------------------------


def span_overlap(lo: int, hi: int, span: list[int] | None) -> int:
    """Inclusive-extent overlap length in px (0 when span is None)."""
    if span is None:
        return 0
    return max(0, min(hi, span[1]) - max(lo, span[0]) + 1)


def anchoring_rows(
    pair: str, lane: str, plan: dict, frames: dict[str, dict[str, dict]]
) -> list[dict]:
    """Per active tick: B-crossing depth past the arc-side grid line, body
    A-extent overlap with the TRUE arc tile and NEAR tile, and where the
    crossing pixels themselves land. Report-only - the rubric judges bind
    quality; no pass/fail px bar exists (pre-registered)."""
    data = plan["pairs"][pair]["lanes"][lane]
    window = data["window"]
    facing = data["attack_facing"]
    pixels = frames[facing]["k0"]
    stats = frame_stats(pixels)
    b_index = 1 if window["b_axis"] == "y" else 0
    a_index = 1 if window["a_axis"] == "y" else 0
    bbox = stats["bbox"]  # [x0, y0, x1, y1]
    bbox_a = (bbox[a_index], bbox[a_index + 2])
    bbox_b1 = bbox[b_index + 2]
    crossing = [p for p in pixels if p[b_index] >= CROSSING_CANVAS_B]
    grid_line = window["grid_line_b"]
    true_span = window["true_arc_a_span"]
    near_span = window["near_a_span"]
    rows = []
    for tick in data["ticks"]:
        if tick["phase"] != "active":
            continue
        draw_a = tick["draw"][a_index]
        draw_b = tick["draw"][b_index]
        body_lo, body_hi = draw_a + bbox_a[0], draw_a + bbox_a[1]
        in_true = sum(
            1 for p in crossing if true_span[0] <= draw_a + p[a_index] <= true_span[1]
        )
        in_near = (
            None
            if near_span is None
            else sum(
                1
                for p in crossing
                if near_span[0] <= draw_a + p[a_index] <= near_span[1]
            )
        )
        rows.append(
            {
                "tick": tick["tick"],
                "a_px": tick["a_px"],
                "crossing_depth_px": draw_b + bbox_b1 - (grid_line - 1),
                "body_a_extent": [body_lo, body_hi],
                "body_overlap_true_px": span_overlap(body_lo, body_hi, true_span),
                "body_overlap_near_px": (
                    None
                    if near_span is None
                    else span_overlap(body_lo, body_hi, near_span)
                ),
                "crossing_px_total": len(crossing),
                "crossing_px_true": in_true,
                "crossing_px_near": in_near,
            }
        )
    return rows


# -- overlap arithmetic ----------------------------------------------------------


def overlap_report(pair: str, lane: str, plan: dict) -> dict:
    """Where the arrival tick (absolute t14) lands per lane - the
    pre-registered class definitions, recomputed (v8 arithmetic unchanged)."""
    data = plan["pairs"][pair]["lanes"][lane]
    onset = data["onset_tick"]
    arrival = data["arrival_tick"]
    ticks = data["ticks"]
    if arrival < onset:
        arrival_phase, phase_index = "pre-onset", 0
    else:
        tick = ticks[arrival]
        arrival_phase = tick["phase"]
        phase_start = {
            "windup": onset, "active": onset + 5, "recovery": onset + 9,
        }[arrival_phase]
        phase_index = arrival - phase_start + 1
    moving = {"windup": 0, "active": 0, "recovery": 0}
    for tick in ticks[onset:]:
        if tick["phase"] in moving and tick["tick"] < arrival:
            moving[tick["phase"]] += 1
    return {
        "onset_tick": onset,
        "rem_after_onset": data["rem_after_onset"],
        "arrival_tick": arrival,
        "arrival_phase": arrival_phase,
        "arrival_phase_tick": phase_index,
        "moving_base_ticks_before_arrival": moving,
    }


# -- checks ----------------------------------------------------------------------


def check_salience(report: dict) -> list[str]:
    failures: list[str] = []
    for pair, lanes in report["seam_tables"].items():
        for lane, data in lanes.items():
            sal = data["release_salience"]
            if not sal["pose_axis_strictly_dominant"]:
                failures.append(
                    f"{pair}/{lane}: release pose delta "
                    f"{sal['release_row']['pose_delta_pct']} does not strictly "
                    f"dominate {sal['max_other_pose_delta_pct']}"
                )
            if not sal["squared_axis_strictly_dominant"]:
                failures.append(
                    f"{pair}/{lane}: release squared displacement "
                    f"{sal['release_row']['squared_px']} does not strictly "
                    f"dominate {sal['max_other_squared_px']}"
                )
    return failures


def check_degenerate_regression(report: dict, v8_metrics_path: Path) -> list[str]:
    failures: list[str] = []
    if not v8_metrics_path.is_file():
        return [f"missing banked v8 metrics {v8_metrics_path}"]
    v8 = json.loads(v8_metrics_path.read_text(encoding="utf-8"))
    for pair, facing in V8_CONTROL_FACING.items():
        banked = v8["seam_tables"][facing]["CONTROL"]["rows"]
        mine = report["seam_tables"][pair]["DEGEN"]["rows"]
        if len(banked) != len(mine):
            failures.append(
                f"{pair}/DEGEN: {len(mine)} rows != banked v8 {len(banked)}"
            )
            continue
        for row, want in zip(mine, banked):
            key = f"{pair}/DEGEN row ({want['from_tick']},{want['to_tick']})"
            if (row["from_tick"], row["to_tick"]) != (
                want["from_tick"], want["to_tick"],
            ):
                failures.append(f"{key}: tick span mismatch")
                continue
            if (row["pose_from"], row["pose_to"]) != (
                want["pose_from"], want["pose_to"],
            ):
                failures.append(f"{key}: poses {row['pose_from']}->{row['pose_to']}"
                                f" != banked {want['pose_from']}->{want['pose_to']}")
            if (
                row["pose_from_facing"] != facing
                or row["pose_to_facing"] != facing
            ):
                failures.append(f"{key}: facing != {facing}")
            if row["pose_delta_pct"] != want["pose_delta_pct"]:
                failures.append(
                    f"{key}: pose delta {row['pose_delta_pct']} != banked "
                    f"{want['pose_delta_pct']}"
                )
            if row["delta_a_px"] != want["position_delta_px"]:
                failures.append(
                    f"{key}: dA {row['delta_a_px']} != banked "
                    f"{want['position_delta_px']}"
                )
            if row["delta_b_px"] != 0:
                failures.append(f"{key}: dB {row['delta_b_px']} != 0")
    return failures


def check_context(report: dict) -> list[str]:
    idle = report["context_deltas"]["idle"]["popping_pct"]
    if idle != IDLE_CROSS_REFERENCE:
        return [
            f"idle<->idle cross-facing delta {idle} != banked "
            f"{IDLE_CROSS_REFERENCE}"
        ]
    return []


def check_overlaps(report: dict) -> list[str]:
    failures: list[str] = []
    for pair, lanes in report["overlap"].items():
        for lane, data in lanes.items():
            want_phase, want_index = ARRIVAL_PHASE[lane]
            if data["rem_after_onset"] != EXPECTED_REM[lane]:
                failures.append(
                    f"{pair}/{lane}: REM {data['rem_after_onset']} != "
                    f"pre-registered {EXPECTED_REM[lane]}"
                )
            if (data["arrival_phase"], data["arrival_phase_tick"]) != (
                want_phase, want_index,
            ):
                failures.append(
                    f"{pair}/{lane}: arrival lands in {data['arrival_phase']} "
                    f"tick {data['arrival_phase_tick']}, pre-registered "
                    f"{want_phase} tick {want_index}"
                )
    return failures


def check_tick_math(plan: dict, constants: dict) -> list[str]:
    failures: list[str] = []
    step = constants["step_frames"]
    positions = [timeline.tween_position(k, step) for k in range(step + 1)]
    deltas = tuple(b - a for a, b in zip(positions, positions[1:]))
    if deltas != TWEEN_DELTAS:
        failures.append(f"tween deltas {deltas} != pinned {TWEEN_DELTAS}")
    if positions[-1] != TILE:
        failures.append(f"tween arrival {positions[-1]} != {TILE}")
    for pair, section in plan["pairs"].items():
        for lane, data in section["lanes"].items():
            tag = f"{pair}/{lane}"
            onset = data["onset_tick"]
            ticks = data["ticks"]
            walk_facing = data["walk_facing"]
            attack_facing = data["attack_facing"]
            windup = [t for t in ticks if t["phase"] == "windup"]
            active = [t for t in ticks if t["phase"] == "active"]
            recovery = [t for t in ticks if t["phase"] == "recovery"]
            if [t["pose"] for t in windup] != ["w0"] + ["a0"] * 4:
                failures.append(f"{tag}: windup poses {[t['pose'] for t in windup]}")
            if [t["pose"] for t in active] != ["k0"] * 4:
                failures.append(f"{tag}: active poses {[t['pose'] for t in active]}")
            if [t["pose"] for t in recovery] != ["s0"] + ["r0"] * 6 + ["x0"]:
                failures.append(
                    f"{tag}: recovery poses {[t['pose'] for t in recovery]}"
                )
            if [t["tick"] for t in windup] != list(range(onset, onset + 5)):
                failures.append(f"{tag}: windup ticks not onset..onset+4")
            bad_offsets = (
                [t for t in windup if t["offset_px"] != constants["windup_px"]]
                + [t for t in active if t["offset_px"] != constants["active_px"]]
                + [t for t in recovery if t["offset_px"] != 0]
            )
            if bad_offsets:
                failures.append(f"{tag}: state offsets differ from pinned lunge")
            for tick in ticks:
                expected_a = timeline.tween_position(max(tick["tick"] - 1, 0), step)
                if tick["a_px"] != expected_a:
                    failures.append(
                        f"{tag}/t{tick['tick']:02d}: a_px {tick['a_px']} != "
                        f"tween {expected_a}"
                    )
                expected_draw = list(
                    timeline.draw_vector(
                        walk_facing, attack_facing, expected_a, tick["offset_px"]
                    )
                )
                if tick["draw"] != expected_draw:
                    failures.append(
                        f"{tag}/t{tick['tick']:02d}: draw {tick['draw']} != "
                        f"tween+offset {expected_draw}"
                    )
                expected_facing = (
                    walk_facing if tick["tick"] < onset else attack_facing
                )
                if tick["pose_facing"] != expected_facing:
                    failures.append(
                        f"{tag}/t{tick['tick']:02d}: facing "
                        f"{tick['pose_facing']} != {expected_facing}"
                    )
                if tick["phase"] == "walk":
                    want = f"f{timeline.walk_frame_index(tick['tick'] - 1, step)}"
                    if tick["pose"] != want:
                        failures.append(
                            f"{tag}/t{tick['tick']:02d}: walk pose "
                            f"{tick['pose']} != {want}"
                        )
    return failures


def check_bounds(plan: dict) -> list[str]:
    """Every opaque pixel in-window BY CONSTRUCTION: the [2,2,29,29] contract
    bound added to every draw vector must land inside the lane window (and
    inside the onset-strip crop for its three ticks) - proven from the plan,
    never from put() clipping. Both candidate strike tiles must sit inside
    the window."""
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
            crop_w, crop_h = data["onset_crop"]
            onset = data["onset_tick"]
            for tick in data["ticks"][onset - 1: onset + 2]:
                dx, dy = tick["draw"]
                if (
                    dx + lo < 0 or dx + hi >= crop_w
                    or dy + lo < 0 or dy + hi >= crop_h
                ):
                    failures.append(
                        f"{tag}/t{tick['tick']:02d}: contract bounds escape "
                        f"onset crop {crop_w}x{crop_h}"
                    )
            for span in (window["true_arc_a_span"], window["near_a_span"]):
                if span is None:
                    continue
                a_max = h if window["a_axis"] == "y" else w
                if span[0] < 0 or span[1] >= a_max:
                    failures.append(f"{tag}: tile span {span} outside window")
            b_max = h if window["b_axis"] == "y" else w
            if not 0 < window["grid_line_b"] < b_max:
                failures.append(
                    f"{tag}: arc grid line {window['grid_line_b']} not inside "
                    f"window"
                )
    return failures


# -- composition purity ----------------------------------------------------------


def reconstruct_cell(sheet: timeline.CrossSeamSheet, cell: dict) -> Rgba8Canvas:
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
    canvas: Rgba8Canvas, sheet: timeline.CrossSeamSheet, dirs: dict[str, Path]
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
    v8_metrics_path: Path | None = None,
) -> dict:
    frames = load_frames(dirs)
    sheet = timeline.CrossSeamSheet(dirs, reference)
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.CrossSeamSheet(dirs, reference).build().encode()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    seam_tables: dict[str, dict] = {}
    anchoring: dict[str, dict] = {}
    overlap: dict[str, dict] = {}
    for pair in timeline.PAIRS:
        seam_tables[pair] = {}
        anchoring[pair] = {}
        overlap[pair] = {}
        for lane in timeline.SECTION_LANES:
            rows = lane_jump_table(pair, lane, sheet.plan, frames)
            seam_tables[pair][lane] = {
                "rows": rows,
                "release_salience": release_salience(
                    rows, sheet.plan["pairs"][pair]["lanes"][lane]["onset_tick"]
                ),
            }
            anchoring[pair][lane] = anchoring_rows(pair, lane, sheet.plan, frames)
            overlap[pair][lane] = overlap_report(pair, lane, sheet.plan)

    context = {"idle": pair_stats(frames["down"]["idle"], frames["right"]["idle"])}
    for index in range(4):
        pose = f"f{index}"
        context[pose] = pair_stats(frames["down"][pose], frames["right"][pose])

    onset_cuts = {
        pair: {
            lane: next(
                r
                for r in seam_tables[pair][lane]["rows"]
                if r["to_tick"]
                == sheet.plan["pairs"][pair]["lanes"][lane]["onset_tick"]
            )
            for lane in timeline.SECTION_LANES
        }
        for pair in timeline.PAIRS
    }

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
            target = apng_dir / f"cross-lanes-{pair.lower()}.apng"
            apng[pair] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames_list),
            }

    exports = check_export_pins(exports_root or ROOT / "exports")
    v9_dir = (exports_root or ROOT / "exports") / "calibration-v9"
    if v9_dir.exists():
        exports["failures"].append(
            "exports/calibration-v9 exists - this sprint banks no exports"
        )

    constants = sheet.plan["constants"]
    return {
        "generated_by": "tools/cross_seam_metrics.py",
        "constants": constants,
        "conventions": CONVENTIONS,
        "tick_ms": TICK_MS,
        "drawing_model": (
            "attack_state != :idle draws the banked v7-winner grammar pose in "
            "the creature's CURRENT facing at 2D tween + offset*facing; facing "
            "is held at B from the onset tick (the modeled input); "
            "recovery-overlap ticks draw s0/r0 on the moving base under this "
            "declared model (recovery-walk priority stays a carried finding)"
        ),
        "seam_tables": seam_tables,
        "onset_cuts": onset_cuts,
        "anchoring": anchoring,
        "context_deltas": context,
        "overlap": overlap,
        "tick_math_failures": check_tick_math(sheet.plan, constants),
        "bounds_failures": check_bounds(sheet.plan),
        "degenerate_regression_failures": check_degenerate_regression(
            {"seam_tables": seam_tables},
            v8_metrics_path
            or ROOT / "reviews" / "calibration-v8" / "seam-metrics.json",
        ),
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
    integrity.extend(report["degenerate_regression_failures"])
    integrity.extend(check_context(report))
    integrity.extend(check_overlaps(report))
    integrity.extend(report["tick_math_failures"])
    integrity.extend(report["bounds_failures"])
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
    return {"integrity": integrity, "measurement": check_salience(report)}


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
        default=ROOT / "reviews" / "calibration-v9" / "cross-seam-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v9" / "cross-seam-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        report = build_report(
            dirs, reference, sheet_path=args.sheet, apng_dir=args.apng_dir
        )
    except (CrossSeamMetricsError, ValueError, OSError) as exc:
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
            "checks passed: zero-new-exports + banked pins, 2D jump tables, "
            "degenerate regression, release salience, context deltas, overlap "
            "arithmetic, tick math, in-bounds by construction, "
            "byte-determinism, composition purity"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
