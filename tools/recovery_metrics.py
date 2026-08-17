#!/usr/bin/env python3
"""Deterministic recovery metrics and validator for the sprint-5 sheet.

Measures and machine-checks the pre-registered calibration-v5 bars
(reviews/calibration-v5/rationale.md):

1. static distinctness on export bytes, per facing - confusability floors
   all >= 25.0%: r0 vs idle AND every walk frame; r0 vs a0 (separately
   pre-registered - grammar inversion is THE failure mode); r0 vs k0;
   identity ceiling: every r0 delta < the 44.44% cross-facing reference;
   feet-contact row within +-1px of the idle baseline;
2. compositor byte-determinism - the sheet (and any APNG aid) is SHA-256
   identical across two independent in-process builds, and committed
   artifact bytes equal a fresh build;
3. composition purity - every creature cell equals a banked export's opaque
   pixels blitted at the computed integer offset over freshly reconstructed
   pinned-palette tiles (verified twice per cell: full-region reconstruction
   AND direct export-byte pixel equality); the DIFF row is a derived
   diagnostic, declared, not a creature cell;
4. tick math exact - recovery cells = 8 at offset 0 in ALL three timelines;
   timelines tick-identical except the recovery-span pose (A=idle, R=r0,
   C=a0); windup 5 at -3 holding a0 (the banked v4 winner) in all three;
   active 4 at +6 holding k0; walk cells = 13 at independently recomputed
   smoothstep positions;
5. export pins - every export consumed hashes to its banked release.json
   SHA-256 (calibration-v0..v3 plus the new v5).

Also reports the boundary profile (the k0->recovery -6px return and the
pose-only recovery-end->idle beat) and the derived durations against the KB
follow-through band. `--check` exits nonzero on any violation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_recovery_timeline as timeline  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from make_feedback_sheet import tell_cell  # noqa: E402
from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

FEET_TOLERANCE_PX = 1
CONFUSABILITY_FLOOR_PCT = 25.0
HEAD_REGION_MAX_ROW = 15
KB_FOLLOWTHROUGH_HOLD_MS = 150.0  # KB: "Attack follow-through: ~150ms hold"

POSE_FILES = {
    "idle": ("idle_dir", "player_1_lane_b_idle_{facing}.png"),
    "f0": ("walk_dir", "player_1_lane_b_walk_{facing}_f0.png"),
    "f1": ("walk_dir", "player_1_lane_b_walk_{facing}_f1.png"),
    "f2": ("walk_dir", "player_1_lane_b_walk_{facing}_f2.png"),
    "f3": ("walk_dir", "player_1_lane_b_walk_{facing}_f3.png"),
    "a0": ("anticipation_dir", "player_1_lane_b_attack_{facing}_a0.png"),
    "k0": ("attack_dir", "player_1_lane_b_attack_{facing}_k0.png"),
    "r0": ("recovery_dir", "player_1_lane_b_attack_{facing}_r0.png"),
}
RELEASE_IDS = (
    "calibration-v0", "calibration-v1", "calibration-v2", "calibration-v3",
    "calibration-v5",
)


class RecoveryMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- static distinctness (bar 1) ----------------------------------------------


def recovery_pose_metrics(
    r0: dict[tuple[int, int], tuple[int, int, int]],
    idle: dict[tuple[int, int], tuple[int, int, int]],
    walks: list[dict[tuple[int, int], tuple[int, int, int]]],
    a0: dict[tuple[int, int], tuple[int, int, int]],
    k0: dict[tuple[int, int], tuple[int, int, int]],
) -> dict:
    idle_stats = frame_stats(idle)
    stats = frame_stats(r0)
    stats["mass_drift_vs_idle_pct"] = round(
        100 * (stats["mass"] - idle_stats["mass"]) / idle_stats["mass"], 2
    )
    stats["feet_row_delta_vs_idle"] = stats["feet_row"] - idle_stats["feet_row"]

    deltas = []
    comparisons = [
        ("idle", idle),
        *[(f"f{index}", walk) for index, walk in enumerate(walks)],
        ("a0", a0),
        ("k0", k0),
    ]
    for name, frame in comparisons:
        report = pair_stats(frame, r0)
        report["vs"] = name
        deltas.append(report)
    walk_side = [
        d["popping_pct"] for d in deltas if d["vs"] not in ("a0", "k0")
    ]
    coil = next(d["popping_pct"] for d in deltas if d["vs"] == "a0")
    strike = next(d["popping_pct"] for d in deltas if d["vs"] == "k0")

    r0_keys, idle_keys = set(r0), set(idle)
    changed = r0_keys ^ idle_keys
    head_changed = sum(1 for _, y in changed if y <= HEAD_REGION_MAX_ROW)
    head_share = round(100 * head_changed / len(changed), 2) if changed else 0.0

    return {
        "pose": stats,
        "deltas": deltas,
        "walk_confusability_floor_pct": min(walk_side),
        "coil_distinctness_pct": coil,
        "strike_distinctness_pct": strike,
        "max_delta_pct": max([*walk_side, coil, strike]),
        "head_region_share_vs_idle_pct": head_share,
    }


def load_frames(
    dirs: dict[str, Path], facing: str
) -> dict[str, dict[tuple[int, int], tuple[int, int, int]]]:
    frames = {}
    for pose, (dir_key, name) in POSE_FILES.items():
        frames[pose] = load_opaque(dirs[dir_key] / name.format(facing=facing))
    return frames


def check_static(report: dict) -> list[str]:
    """The pre-registered static bars (floors, ceiling, feet)."""
    failures: list[str] = []
    ceiling = report["reference"]["idle_cross_facing"]["popping_pct"]
    for facing, metrics in report["static"].items():
        feet_delta = abs(metrics["pose"]["feet_row_delta_vs_idle"])
        if feet_delta > FEET_TOLERANCE_PX:
            failures.append(
                f"{facing}: r0 feet-contact row drifts {feet_delta}px from idle "
                f"(tolerance {FEET_TOLERANCE_PX}px)"
            )
        floor = metrics["walk_confusability_floor_pct"]
        if floor < CONFUSABILITY_FLOOR_PCT:
            failures.append(
                f"{facing}: walk-side confusability floor {floor}% is below "
                f"{CONFUSABILITY_FLOOR_PCT}% (recovery confusable with idle/walk)"
            )
        coil = metrics["coil_distinctness_pct"]
        if coil < CONFUSABILITY_FLOOR_PCT:
            failures.append(
                f"{facing}: r0-vs-a0 distinctness {coil}% is below "
                f"{CONFUSABILITY_FLOOR_PCT}% (grammar inversion: settle reads as coil)"
            )
        strike = metrics["strike_distinctness_pct"]
        if strike < CONFUSABILITY_FLOOR_PCT:
            failures.append(
                f"{facing}: r0-vs-k0 distinctness {strike}% is below "
                f"{CONFUSABILITY_FLOOR_PCT}% (recovery confusable with strike)"
            )
        peak = metrics["max_delta_pct"]
        if peak >= ceiling:
            failures.append(
                f"{facing}: r0 delta {peak}% reaches the cross-facing identity "
                f"ceiling {ceiling}% (identity change, not state change)"
            )
    return failures


# -- boundary profile and durations -------------------------------------------


def boundary_profile(plan: dict) -> dict:
    """The two boundaries under test, characterized from the plan."""
    ticks = plan["ticks"]
    active = [t for t in ticks if t["phase"] == "active"]
    recovery = [t for t in ticks if t["phase"] == "recovery"]
    idle_post = [t for t in ticks if t["phase"] == "idle_post"]
    release_settle = {
        "from_tick": active[-1]["tick"],
        "to_tick": recovery[0]["tick"],
        "position_delta_px": recovery[0]["axis_px"] - active[-1]["axis_px"],
        "pose_change": {
            tl: [active[-1]["poses"][tl], recovery[0]["poses"][tl]]
            for tl in timeline.TIMELINES
        },
    }
    ready_again = {
        "from_tick": recovery[-1]["tick"],
        "to_tick": idle_post[0]["tick"],
        "position_delta_px": idle_post[0]["axis_px"] - recovery[-1]["axis_px"],
        "pose_change": {
            tl: [recovery[-1]["poses"][tl], idle_post[0]["poses"][tl]]
            for tl in timeline.TIMELINES
        },
    }
    return {
        "release_to_settle": release_settle,
        "recovery_end_to_idle": ready_again,
        "note": (
            "release->settle carries a -6px return in every timeline; the "
            "ready-again beat is pose-only (position constant) and exists "
            "only where the recovery pose differs from idle (R and C)"
        ),
    }


def durations_ms(constants: dict) -> dict:
    recovery_ms = round(constants["recovery_frames"] * TICK_MS, 1)
    return {
        "note": "derived at the unoverridden Gosu default 16.666666 ms/tick; "
        "ticks are the contract numbers",
        "windup_ms": round(constants["windup_frames"] * TICK_MS, 1),
        "active_ms": round(constants["active_frames"] * TICK_MS, 1),
        "recovery_ms": recovery_ms,
        "step_ms": round(constants["step_frames"] * TICK_MS, 1),
        "kb_followthrough_hold_ms": KB_FOLLOWTHROUGH_HOLD_MS,
        "recovery_vs_kb_band_ms": round(recovery_ms - KB_FOLLOWTHROUGH_HOLD_MS, 1),
    }


# -- composition purity (bar 3) ------------------------------------------------


def reconstruct_cell(
    sheet: timeline.RecoveryTimelineSheet, cell: dict
) -> Rgba8Canvas:
    """Independently redraw one cell from export bytes + pinned constants."""
    w, h = cell["rect"][2], cell["rect"][3]
    sprite = sheet.poses[cell["facing"]][cell["pose"]]
    if cell["section"] == "grammar":
        temp = Rgba8Canvas(w, h, timeline.BG)
        zone = sheet.reference["zones"][cell["zone"]]
        tell_cell(temp, 0, 0, zone, cell["facing"], sprite, cell["win_px"])
        return temp
    composed = timeline.compose_window(
        sheet.reference["zones"][cell["zone"]], cell["facing"],
        cell["window_tiles"], sprite, cell["win_px"],
    )
    if cell["scale"] == 1:
        return composed
    temp = Rgba8Canvas(w, h, timeline.BG)
    temp.blit_scaled(timeline.canvas_pixels(composed), 0, 0, cell["scale"])
    return temp


def cell_blit_origin(cell: dict) -> tuple[int, int]:
    """Window-relative sprite-canvas origin for the direct export-byte check."""
    if cell["section"] == "grammar":
        offset = TILE // 2 + cell["win_px"]
    else:
        offset = cell["win_px"]
    return (0, offset) if cell["facing"] == "down" else (offset, 0)


def check_purity(
    canvas: Rgba8Canvas, sheet: timeline.RecoveryTimelineSheet, dirs: dict[str, Path]
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
        dir_key, name = POSE_FILES[cell["pose"]]
        export = sprite_from_png(dirs[dir_key] / name.format(facing=cell["facing"]))
        bx, by = cell_blit_origin(cell)
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
        f"{cell['timeline']}/tick{cell['tick']:02d}"
    )


# -- tick math (bar 4) ----------------------------------------------------------


def check_tick_math(
    sheet: timeline.RecoveryTimelineSheet, reference: dict
) -> list[str]:
    failures: list[str] = []
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    pins = {
        "windup": (timing["windup_frames"]["value"], lunge["windup_px"],
                   {tl: timeline.WINDUP_POSE for tl in timeline.TIMELINES}),
        "active": (timing["active_frames"]["value"], lunge["active_px"],
                   {tl: "k0" for tl in timeline.TIMELINES}),
        "recovery": (timing["recovery_frames"]["value"], 0,
                     dict(timeline.RECOVERY_POSE)),
    }
    attack_cells = [c for c in sheet.cells if c["section"] == "attack"]
    for facing in timeline.FACINGS:
        for zone in ("zone_1", "zone_2"):
            per_timeline: dict[str, dict[int, dict]] = {}
            for tl in timeline.TIMELINES:
                rows = [
                    c for c in attack_cells
                    if c["facing"] == facing and c["zone"] == zone
                    and c["timeline"] == tl
                ]
                per_timeline[tl] = {c["tick"]: c for c in rows}
                for phase, (count, offset, poses) in pins.items():
                    cells = [c for c in rows if c["phase"] == phase]
                    if len(cells) != count:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {len(cells)} {phase} cells "
                            f"rendered, pinned {count}"
                        )
                    bad_offset = [c for c in cells if c["win_px"] != offset]
                    if bad_offset:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {phase} offset "
                            f"{bad_offset[0]['win_px']} != pinned {offset}"
                        )
                    bad_pose = [c for c in cells if c["pose"] != poses[tl]]
                    if bad_pose:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {phase} pose "
                            f"{bad_pose[0]['pose']!r} != {poses[tl]!r}"
                        )
            tick_sets = {tl: set(cells) for tl, cells in per_timeline.items()}
            if len(set(map(frozenset, tick_sets.values()))) != 1:
                failures.append(f"{facing}/{zone}: A/R/C tick sets differ")
                continue
            for tick, cell_a in per_timeline["A"].items():
                for tl in ("R", "C"):
                    other = per_timeline[tl].get(tick)
                    if other is None:
                        continue
                    if cell_a["win_px"] != other["win_px"]:
                        failures.append(
                            f"{facing}/{zone}/tick{tick}: A/{tl} positions differ"
                        )
                    if cell_a["phase"] != "recovery" and (
                        cell_a["pose"] != other["pose"]
                    ):
                        failures.append(
                            f"{facing}/{zone}/tick{tick}: A/{tl} poses differ "
                            f"outside recovery"
                        )
    step = timing["step_frames"]["value"]
    approach_cells = [c for c in sheet.cells if c["section"] == "approach"]
    for facing in timeline.FACINGS:
        for zone in ("zone_1", "zone_2"):
            walk = [
                c for c in approach_cells
                if c["facing"] == facing and c["zone"] == zone
                and c["phase"] == "walk"
            ]
            if len(walk) != step:
                failures.append(
                    f"{facing}/{zone}: {len(walk)} walk cells rendered, "
                    f"pinned step_frames {step}"
                )
            for index, cell in enumerate(sorted(walk, key=lambda c: c["tick"])):
                t = (index + 1) / step
                expected = math.floor(TILE * (3 * t * t - 2 * t * t * t) + 0.5)
                if cell["win_px"] != expected:
                    failures.append(
                        f"{facing}/{zone}/walk k={index + 1}: position "
                        f"{cell['win_px']} != smoothstep {expected}"
                    )
    grammar_pins = [
        ("idle", "idle", 0), ("f1", "f1", 0), ("a0", "a0", 0),
        ("wind", "a0", lunge["windup_px"]), ("k0", "k0", 0),
        ("lunge", "k0", lunge["active_px"]), ("r0", "r0", 0),
    ]
    for facing in timeline.FACINGS:
        grammar = [
            c for c in sheet.cells
            if c["section"] == "grammar" and c["facing"] == facing
        ]
        actual = [(c["phase"], c["pose"], c["win_px"]) for c in grammar]
        if actual != grammar_pins:
            failures.append(f"{facing}: grammar row {actual} != pinned sequence")
    for facing in timeline.FACINGS:
        for zone in ("zone_1", "zone_2"):
            film = [
                c for c in sheet.cells
                if c["section"] == "film" and c["facing"] == facing
                and c["zone"] == zone
            ]
            if [c["pose"] for c in film] != list(timeline.STRIP):
                failures.append(f"{facing}/{zone}: film strip differs from contract")
    twox = [c for c in sheet.cells if c["section"] == "twox"]
    expected_boundaries = [
        t["tick"] for t in timeline.boundary_ticks(sheet.plan)
    ]
    for facing in timeline.FACINGS:
        ticks = [c["tick"] for c in twox if c["facing"] == facing]
        if ticks != expected_boundaries:
            failures.append(
                f"{facing}: 2X boundary ticks {ticks} != {expected_boundaries}"
            )
    return failures


# -- export pins (bar 5) ---------------------------------------------------------


def load_release_pins(exports_root: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for release_id in RELEASE_IDS:
        manifest = json.loads(
            (exports_root / release_id / "release.json").read_text(encoding="utf-8")
        )
        for export in manifest["exports"]:
            pins[Path(export["path"]).name] = export["sha256"]
    return pins


def check_export_pins(dirs: dict[str, Path], pins: dict[str, str]) -> dict:
    verified = 0
    failures: list[str] = []
    for pose, (dir_key, name) in POSE_FILES.items():
        for facing in timeline.FACINGS:
            file = dirs[dir_key] / name.format(facing=facing)
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            pinned = pins.get(file.name)
            if pinned is None:
                failures.append(f"{file.name}: no banked release pin found")
            elif digest != pinned:
                failures.append(
                    f"{file.name}: sha256 {digest[:16]}... != banked {pinned[:16]}..."
                )
            else:
                verified += 1
    return {"verified": verified, "failures": failures}


# -- report ----------------------------------------------------------------------


def build_report(
    recovery_dir: Path,
    anticipation_dir: Path,
    attack_dir: Path,
    walk_dir: Path,
    idle_dir: Path,
    reference: dict,
    sheet_path: Path | None = None,
    apng_dir: Path | None = None,
    verify_pins: bool = True,
    exports_root: Path | None = None,
) -> dict:
    dirs = {
        "recovery_dir": recovery_dir,
        "anticipation_dir": anticipation_dir,
        "attack_dir": attack_dir,
        "walk_dir": walk_dir,
        "idle_dir": idle_dir,
    }
    static = {}
    for facing in timeline.FACINGS:
        frames = load_frames(dirs, facing)
        static[facing] = recovery_pose_metrics(
            frames["r0"], frames["idle"],
            [frames[f"f{i}"] for i in range(4)], frames["a0"], frames["k0"],
        )
    idle_down = load_opaque(idle_dir / "player_1_lane_b_idle_down.png")
    idle_right = load_opaque(idle_dir / "player_1_lane_b_idle_right.png")

    sheet = timeline.RecoveryTimelineSheet(
        recovery_dir, anticipation_dir, attack_dir, walk_dir, idle_dir, reference
    )
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.RecoveryTimelineSheet(
        recovery_dir, anticipation_dir, attack_dir, walk_dir, idle_dir, reference
    ).build().encode()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    apng = {}
    if apng_dir is not None:
        for facing in timeline.FACINGS:
            frames = timeline.build_apng_frames(sheet, facing)
            payload = timeline.encode_apng(frames, timeline.apng_delays(len(frames)))
            again = timeline.encode_apng(
                timeline.build_apng_frames(sheet, facing),
                timeline.apng_delays(len(frames)),
            )
            target = apng_dir / f"timeline-arc-{facing}.apng"
            apng[facing] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames),
            }

    return {
        "generated_by": "tools/recovery_metrics.py",
        "constants": sheet.plan["constants"],
        "durations_ms": durations_ms(sheet.plan["constants"]),
        "static": static,
        "boundaries": boundary_profile(sheet.plan),
        "reference": {"idle_cross_facing": pair_stats(idle_down, idle_right)},
        "sheet": {
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "deterministic": encoded == second,
            "committed_matches": committed,
            "cells": len(sheet.cells),
        },
        "apng": apng,
        "purity": check_purity(canvas, sheet, dirs),
        "tick_math_failures": check_tick_math(sheet, reference),
        "export_pins": (
            check_export_pins(dirs, load_release_pins(exports_root or ROOT / "exports"))
            if verify_pins
            else {"skipped": True}
        ),
    }


def check_report(report: dict) -> list[str]:
    failures: list[str] = list(check_static(report))
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
    failures.extend(report["tick_math_failures"])
    pins = report["export_pins"]
    if pins.get("skipped"):
        failures.append("export pins were not verified (skipped)")
    else:
        failures.extend(pins["failures"])
    return failures


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
        "--sheet", type=Path,
        default=ROOT / "reviews" / "calibration-v5" / "timeline-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v5" / "timeline-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    try:
        report = build_report(
            args.recovery_exports, args.anticipation_exports, args.attack_exports,
            args.walk_exports, args.idle_exports, reference,
            sheet_path=args.sheet, apng_dir=args.apng_dir,
        )
    except (RecoveryMetricsError, ValueError, OSError) as exc:
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
            "checks passed: static distinctness, byte-determinism, composition "
            "purity, tick math, banked export pins"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
