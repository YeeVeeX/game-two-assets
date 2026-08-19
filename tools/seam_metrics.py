#!/usr/bin/env python3
"""Deterministic walk->attack onset-seam metrics and validator (sprint 8).

Measures and machine-checks the pre-registered calibration-v8 bars
(reviews/calibration-v8/rationale.md). Zero new frames: every number is
computed from banked export bytes and pinned constants.

1. zero new exports - exports/ contains exactly the pinned PNGs of the seven
   banked releases (26 files), each SHA-256-verified against its release.json
   pin; no exports/calibration-v8 directory exists;
2. seam jump tables - per onset class, per facing: pose delta (100*XOR/union
   on export bytes) AND position delta (tween + state offset, independently
   recomputed smoothstep) for every consecutive tick pair from onset-2
   through onset+9 (EARLY: onset+12, covering its recovery overlap);
3. CONTROL regression (hard) - CONTROL's onset row is f3->w0 at the banked
   16.48 (down) / 19.69 (right) at -3px, and its shared boundary rows equal
   the committed reviews/calibration-v7/timeline-metrics.json timeline-B
   values exactly;
4. release salience - in every lane, both facings, the a0->k0 row is STRICTLY
   the largest pose delta AND STRICTLY the largest absolute position delta in
   that lane's table (dominance on both axes separately, no combined metric);
5. tick math - per lane: windup 5 (w0 x1 + a0 x4) at -3, active 4 (k0) at +6,
   recovery 8 (s0 x1 + r0 x6 + x0 x1) at 0, walk frames per the banked
   mapping at recomputed smoothstep positions, per-tick tween deltas exactly
   1,1,2,3,4,3,4,3,4,3,2,1,1, REM per class 11/8/4/0 with the arrival tick
   landing in the pre-registered phase (rec 3 / act 4 / wind 5 / pre-onset);
6. determinism + purity - sheet (and any APNG aid) byte-identical across two
   independent in-process builds and equal to committed bytes; every creature
   cell dual-verified against banked export bytes at the computed offsets.

`--check` exits nonzero on any violation.
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

import make_seam_timeline as timeline  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from motion_metrics import load_opaque, pair_stats  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

RELEASE_IDS = (
    "calibration-v0", "calibration-v1", "calibration-v2", "calibration-v3",
    "calibration-v5", "calibration-v6", "calibration-v7",
)
EXPECTED_EXPORT_COUNT = 26
TWEEN_DELTAS = (1, 1, 2, 3, 4, 3, 4, 3, 4, 3, 2, 1, 1)
CONTROL_ONSET = {"down": {"pose": 16.48, "position": -3},
                 "right": {"pose": 19.69, "position": -3}}
V7_SHARED_ROWS = ((13, 14), (14, 15), (15, 16), (19, 20), (23, 24), (24, 25))
ARRIVAL_PHASE = {
    "EARLY": ("recovery", 3), "MID": ("active", 4), "LATE": ("windup", 5),
    "CONTROL": ("pre-onset", 0),
}
EXPECTED_REM = {"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0}


class SeamMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- frames --------------------------------------------------------------------


def load_frames(dirs: dict[str, Path], facing: str) -> dict[str, dict]:
    return {
        pose: load_opaque(
            dirs[timeline.POSE_DIRS[pose]] / timeline.pose_filename(pose, facing)
        )
        for pose in timeline.STRIP
    }


# -- jump tables ------------------------------------------------------------------


def table_range(lane: str, onset: int) -> tuple[int, int]:
    """Pre-registered table span: onset-2 .. onset+10 (EARLY: onset+12), so
    every lane's table ends on the s0->r0 seam row and EARLY covers its
    recovery overlap plus one settled hold tick."""
    end = onset + (12 if lane == "EARLY" else 10)
    return onset - 2, end


def lane_jump_table(
    lane: str, plan: dict, frames: dict[str, dict]
) -> list[dict]:
    onset = plan["lanes"][lane]["onset_tick"]
    ticks = plan["lanes"][lane]["ticks"]
    start, end = table_range(lane, onset)
    rows = []
    for before, after in zip(ticks[start:end], ticks[start + 1:end + 1]):
        delta = (
            0.0
            if before["pose"] == after["pose"]
            else pair_stats(frames[before["pose"]], frames[after["pose"]])["popping_pct"]
        )
        rows.append(
            {
                "from_tick": before["tick"],
                "to_tick": after["tick"],
                "pose_from": before["pose"],
                "pose_to": after["pose"],
                "pose_delta_pct": delta,
                "position_delta_px": after["axis_px"] - before["axis_px"],
                "phase_to": after["phase"],
            }
        )
    return rows


def release_salience(table: list[dict], onset: int) -> dict:
    """The a0->k0 row must strictly dominate BOTH axes within the lane table
    (pose delta and absolute position delta reported separately - the banked
    v6 council correction: no invented combined metric)."""
    release = next(
        r for r in table if r["from_tick"] == onset + 4 and r["to_tick"] == onset + 5
    )
    others = [r for r in table if r is not release]
    max_other_pose = max(r["pose_delta_pct"] for r in others)
    max_other_position = max(abs(r["position_delta_px"]) for r in others)
    return {
        "release_row": release,
        "max_other_pose_delta_pct": max_other_pose,
        "max_other_abs_position_delta_px": max_other_position,
        "pose_axis_strictly_dominant": release["pose_delta_pct"] > max_other_pose,
        "position_axis_strictly_dominant": (
            abs(release["position_delta_px"]) > max_other_position
        ),
    }


# -- overlap arithmetic --------------------------------------------------------


def overlap_report(lane: str, plan: dict) -> dict:
    """Where the arrival tick (absolute t14) lands, and how many ticks of each
    attack phase draw on a still-moving base - the pre-registered class
    definitions, recomputed."""
    data = plan["lanes"][lane]
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


def check_tables(report: dict) -> list[str]:
    failures: list[str] = []
    for facing, lanes in report["seam_tables"].items():
        for lane, data in lanes.items():
            sal = data["release_salience"]
            if not sal["pose_axis_strictly_dominant"]:
                failures.append(
                    f"{facing}/{lane}: release pose delta "
                    f"{sal['release_row']['pose_delta_pct']} does not strictly "
                    f"dominate {sal['max_other_pose_delta_pct']}"
                )
            if not sal["position_axis_strictly_dominant"]:
                failures.append(
                    f"{facing}/{lane}: release position delta "
                    f"{sal['release_row']['position_delta_px']} does not strictly "
                    f"dominate {sal['max_other_abs_position_delta_px']}"
                )
    return failures


def check_control_regression(report: dict, v7_metrics_path: Path) -> list[str]:
    failures: list[str] = []
    for facing, expected in CONTROL_ONSET.items():
        table = report["seam_tables"][facing]["CONTROL"]["rows"]
        onset_row = next(r for r in table if (r["from_tick"], r["to_tick"]) == (14, 15))
        if (onset_row["pose_delta_pct"], onset_row["position_delta_px"]) != (
            expected["pose"], expected["position"],
        ):
            failures.append(
                f"{facing}/CONTROL onset row {onset_row['pose_delta_pct']}%/"
                f"{onset_row['position_delta_px']}px != banked "
                f"{expected['pose']}%/{expected['position']}px"
            )
    if not v7_metrics_path.is_file():
        failures.append(f"missing banked v7 metrics {v7_metrics_path}")
        return failures
    v7 = json.loads(v7_metrics_path.read_text(encoding="utf-8"))
    for facing in timeline.FACINGS:
        banked = {
            (row["from_tick"], row["to_tick"]): row
            for row in v7["boundaries"][facing]["B"]["boundary_rows"]
        }
        table = {
            (r["from_tick"], r["to_tick"]): r
            for r in report["seam_tables"][facing]["CONTROL"]["rows"]
        }
        for pair in V7_SHARED_ROWS:
            if pair not in banked:
                continue  # (13,14) is not a banked v7 boundary row
            if pair not in table:
                failures.append(f"{facing}/CONTROL: banked row {pair} missing")
                continue
            row, want = table[pair], banked[pair]
            if (
                row["pose_delta_pct"] != want["pose_delta_pct"]
                or row["position_delta_px"] != want["position_delta_px"]
            ):
                failures.append(
                    f"{facing}/CONTROL row {pair}: "
                    f"{row['pose_delta_pct']}%/{row['position_delta_px']}px != "
                    f"banked v7 {want['pose_delta_pct']}%/"
                    f"{want['position_delta_px']}px"
                )
    return failures


def check_overlaps(report: dict) -> list[str]:
    failures: list[str] = []
    for lane, data in report["overlap"].items():
        want_phase, want_index = ARRIVAL_PHASE[lane]
        if data["rem_after_onset"] != EXPECTED_REM[lane]:
            failures.append(
                f"{lane}: REM {data['rem_after_onset']} != "
                f"pre-registered {EXPECTED_REM[lane]}"
            )
        if (data["arrival_phase"], data["arrival_phase_tick"]) != (
            want_phase, want_index,
        ):
            failures.append(
                f"{lane}: arrival lands in {data['arrival_phase']} tick "
                f"{data['arrival_phase_tick']}, pre-registered {want_phase} "
                f"tick {want_index}"
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
    for lane, data in plan["lanes"].items():
        onset = data["onset_tick"]
        ticks = data["ticks"]
        windup = [t for t in ticks if t["phase"] == "windup"]
        active = [t for t in ticks if t["phase"] == "active"]
        recovery = [t for t in ticks if t["phase"] == "recovery"]
        if [t["pose"] for t in windup] != ["w0"] + ["a0"] * 4:
            failures.append(f"{lane}: windup poses {[t['pose'] for t in windup]}")
        if [t["pose"] for t in active] != ["k0"] * 4:
            failures.append(f"{lane}: active poses {[t['pose'] for t in active]}")
        if [t["pose"] for t in recovery] != ["s0"] + ["r0"] * 6 + ["x0"]:
            failures.append(f"{lane}: recovery poses {[t['pose'] for t in recovery]}")
        if [t["tick"] for t in windup] != list(range(onset, onset + 5)):
            failures.append(f"{lane}: windup ticks not onset..onset+4")
        bad_offsets = (
            [t for t in windup if t["offset_px"] != constants["windup_px"]]
            + [t for t in active if t["offset_px"] != constants["active_px"]]
            + [t for t in recovery if t["offset_px"] != 0]
        )
        if bad_offsets:
            failures.append(f"{lane}: state offsets differ from pinned lunge values")
        for tick in ticks:
            expected_axis = (
                timeline.tween_position(max(tick["tick"] - 1, 0), step)
                + tick["offset_px"]
            )
            if tick["axis_px"] != expected_axis:
                failures.append(
                    f"{lane}/t{tick['tick']:02d}: axis {tick['axis_px']} != "
                    f"tween+offset {expected_axis}"
                )
        for tick in ticks:
            if tick["phase"] == "walk":
                want = f"f{timeline.walk_frame_index(tick['tick'] - 1, step)}"
                if tick["pose"] != want:
                    failures.append(
                        f"{lane}/t{tick['tick']:02d}: walk pose {tick['pose']} != {want}"
                    )
    return failures


# -- composition purity ----------------------------------------------------------


def reconstruct_cell(sheet: timeline.SeamTimelineSheet, cell: dict) -> Rgba8Canvas:
    composed = timeline.compose_window(
        sheet.reference["zones"][cell["zone"]], cell["facing"],
        cell["window_tiles"], sheet.poses[cell["facing"]][cell["pose"]],
        cell["win_px"],
    )
    if cell["scale"] == 1:
        return composed
    temp = Rgba8Canvas(cell["rect"][2], cell["rect"][3], timeline.BG)
    temp.blit_scaled(timeline.canvas_pixels(composed), 0, 0, cell["scale"])
    return temp


def check_purity(
    canvas: Rgba8Canvas, sheet: timeline.SeamTimelineSheet, dirs: dict[str, Path]
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
            / timeline.pose_filename(cell["pose"], cell["facing"])
        )
        offset = cell["win_px"]
        bx, by = (0, offset) if cell["facing"] == "down" else (offset, 0)
        scale = cell["scale"]
        pixel_ok = all(
            canvas.get(x0 + (bx + sx) * scale, y0 + (by + sy) * scale) == (*rgb, 255)
            for sx, sy, rgb in export.pixels
        )
        if not pixel_ok:
            failures.append(f"export-byte mismatch: {cell_id(cell)}")
    return {"cells_checked": len(sheet.cells), "failures": failures}


def cell_id(cell: dict) -> str:
    return (
        f"{cell['section']}/{cell['facing']}/{cell['zone']}/"
        f"{cell['lane']}/tick{cell['tick']:02d}"
    )


# -- export pins + zero-new-exports ------------------------------------------------


def check_export_pins(exports_root: Path) -> dict:
    pins: dict[str, str] = {}
    for release_id in RELEASE_IDS:
        manifest_path = exports_root / release_id / "release.json"
        if not manifest_path.is_file():
            return {"verified": 0, "failures": [f"missing {manifest_path}"]}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for export in manifest["exports"]:
            pins[str(exports_root / release_id / Path(export["path"]).name)] = (
                export["sha256"]
            )
    failures: list[str] = []
    verified = 0
    for path_text, pinned in sorted(pins.items()):
        file = Path(path_text)
        if not file.is_file():
            failures.append(f"{file.name}: pinned export missing")
            continue
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        if digest != pinned:
            failures.append(
                f"{file.name}: sha256 {digest[:16]}... != banked {pinned[:16]}..."
            )
        else:
            verified += 1
    on_disk = {str(p) for p in exports_root.glob("calibration-*/*.png")}
    unpinned = sorted(on_disk - set(pins))
    if unpinned:
        failures.append(f"unpinned export files present: {unpinned}")
    if (exports_root / "calibration-v8").exists():
        failures.append("exports/calibration-v8 exists - this sprint banks no exports")
    if len(pins) != EXPECTED_EXPORT_COUNT:
        failures.append(
            f"pinned export count {len(pins)} != expected {EXPECTED_EXPORT_COUNT}"
        )
    return {"verified": verified, "pinned_total": len(pins), "failures": failures}


# -- report ------------------------------------------------------------------------


def build_report(
    dirs: dict[str, Path],
    reference: dict,
    sheet_path: Path | None = None,
    apng_dir: Path | None = None,
    exports_root: Path | None = None,
    v7_metrics_path: Path | None = None,
) -> dict:
    frames_by_facing = {
        facing: load_frames(dirs, facing) for facing in timeline.FACINGS
    }
    sheet = timeline.SeamTimelineSheet(dirs, reference)
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.SeamTimelineSheet(dirs, reference).build().encode()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    seam_tables: dict[str, dict] = {}
    for facing, frames in frames_by_facing.items():
        seam_tables[facing] = {}
        for lane in timeline.LANES:
            rows = lane_jump_table(lane, sheet.plan, frames)
            seam_tables[facing][lane] = {
                "rows": rows,
                "release_salience": release_salience(
                    rows, sheet.plan["lanes"][lane]["onset_tick"]
                ),
            }

    apng = {}
    if apng_dir is not None:
        for facing in timeline.FACINGS:
            frames = timeline.build_apng_frames(sheet, facing)
            payload = timeline.encode_apng(frames, timeline.apng_delays(len(frames)))
            again = timeline.encode_apng(
                timeline.build_apng_frames(sheet, facing),
                timeline.apng_delays(len(frames)),
            )
            target = apng_dir / f"seam-lanes-{facing}.apng"
            apng[facing] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames),
            }

    constants = sheet.plan["constants"]
    return {
        "generated_by": "tools/seam_metrics.py",
        "constants": constants,
        "tick_ms": TICK_MS,
        "drawing_model": (
            "attack_state != :idle draws the banked v7-winner grammar pose at "
            "tween+offset; recovery-overlap ticks draw s0/r0 on the moving base "
            "under this declared model (recovery-walk priority stays a carried "
            "integration finding)"
        ),
        "seam_tables": seam_tables,
        "overlap": {
            lane: overlap_report(lane, sheet.plan) for lane in timeline.LANES
        },
        "tick_math_failures": check_tick_math(sheet.plan, constants),
        "sheet": {
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "deterministic": encoded == second,
            "committed_matches": committed,
            "cells": len(sheet.cells),
        },
        "apng": apng,
        "purity": check_purity(canvas, sheet, dirs),
        "export_pins": check_export_pins(exports_root or ROOT / "exports"),
        "control_regression_failures": check_control_regression(
            {"seam_tables": seam_tables},
            v7_metrics_path
            or ROOT / "reviews" / "calibration-v7" / "timeline-metrics.json",
        ),
    }


def check_report(report: dict) -> list[str]:
    failures: list[str] = list(check_tables(report))
    failures.extend(report["control_regression_failures"])
    failures.extend(check_overlaps(report))
    failures.extend(report["tick_math_failures"])
    if not report["sheet"]["deterministic"]:
        failures.append("sheet builds are not byte-identical across two runs")
    if report["sheet"]["committed_matches"] is False:
        failures.append("committed sheet bytes differ from a fresh build")
    for facing, aid in report["apng"].items():
        if not aid["deterministic"]:
            failures.append(f"apng {facing}: builds not byte-identical")
        if aid["committed_matches"] is False:
            failures.append(f"apng {facing}: committed bytes differ from fresh build")
    failures.extend(report["purity"]["failures"])
    failures.extend(report["export_pins"]["failures"])
    return failures


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
        default=ROOT / "reviews" / "calibration-v8" / "seam-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v8" / "seam-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        report = build_report(
            dirs, reference, sheet_path=args.sheet, apng_dir=args.apng_dir
        )
    except (SeamMetricsError, ValueError, OSError) as exc:
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
        for failure in failures:
            print(f"CHECK FAIL: {failure}", file=sys.stderr)
        if failures:
            return 1
        print(
            "checks passed: zero-new-exports + banked pins, seam jump tables, "
            "CONTROL regression, release salience, overlap arithmetic, tick "
            "math, byte-determinism, composition purity"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
