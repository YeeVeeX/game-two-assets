#!/usr/bin/env python3
"""Deterministic motion metrics for a 4-frame walk cycle against its idle.

Measures, per facing, the numbers behind the motion-coherence rubric:

- per frame: opaque mass, bbox, feet-contact row (bbox bottom), centroid,
  mass drift versus the frozen idle
- per consecutive cyclic pair (f0f1, f1f2, f2f3, f3f0): silhouette change
  (XOR pixel count), union, popping percentage (100 * XOR / union), and
  recolored-in-overlap count (a popping detector for pure palette flicker)
- reference: silhouette delta between the two idle facings (the calibration-v0
  cross-pose anchor that frame-to-frame deltas must stay well under)

`--check` enforces the two hard sprint-1 contract lines and exits nonzero on
violation: feet-contact row within +-1px of the idle baseline on every frame,
and no static consecutive pair (a dead frame in the cycle).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from png_reader import read_rgba  # noqa: E402

FACINGS = ("down", "right")
FRAME_COUNT = 4
FEET_TOLERANCE_PX = 1


class MetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


def load_opaque(path: Path) -> dict[tuple[int, int], tuple[int, int, int]]:
    if not path.is_file():
        raise MetricsError(f"missing export {path}")
    width, height, raw = read_rgba(path)
    if (width, height) != (32, 32):
        raise MetricsError(f"{path.name}: expected 32x32, got {width}x{height}")
    pixels: dict[tuple[int, int], tuple[int, int, int]] = {}
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 4
            r, g, b, a = raw[offset : offset + 4]
            if a == 255:
                pixels[(x, y)] = (r, g, b)
    if not pixels:
        raise MetricsError(f"{path.name}: fully transparent")
    return pixels


def frame_stats(pixels: dict[tuple[int, int], tuple[int, int, int]]) -> dict:
    xs = [x for x, _ in pixels]
    ys = [y for _, y in pixels]
    mass = len(pixels)
    return {
        "mass": mass,
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "feet_row": max(ys),
        "centroid": [round(sum(xs) / mass, 2), round(sum(ys) / mass, 2)],
    }


def pair_stats(
    before: dict[tuple[int, int], tuple[int, int, int]],
    after: dict[tuple[int, int], tuple[int, int, int]],
) -> dict:
    before_keys, after_keys = set(before), set(after)
    union = before_keys | after_keys
    changed = len(before_keys ^ after_keys)
    recolored = sum(
        1 for position in before_keys & after_keys if before[position] != after[position]
    )
    return {
        "silhouette_changed_px": changed,
        "union_px": len(union),
        "popping_pct": round(100 * changed / len(union), 2),
        "recolored_px": recolored,
    }


def facing_metrics(exports_dir: Path, idle_dir: Path, facing: str) -> dict:
    idle = load_opaque(idle_dir / f"player_1_lane_b_idle_{facing}.png")
    idle_stats = frame_stats(idle)
    frames = [
        load_opaque(exports_dir / f"player_1_lane_b_walk_{facing}_f{index}.png")
        for index in range(FRAME_COUNT)
    ]

    frame_reports = []
    for index, pixels in enumerate(frames):
        stats = frame_stats(pixels)
        stats["frame"] = f"f{index}"
        stats["mass_drift_vs_idle_pct"] = round(
            100 * (stats["mass"] - idle_stats["mass"]) / idle_stats["mass"], 2
        )
        stats["feet_row_delta_vs_idle"] = stats["feet_row"] - idle_stats["feet_row"]
        frame_reports.append(stats)

    pair_reports = []
    cycle = [*frames, frames[0]]
    for index in range(FRAME_COUNT):
        report = pair_stats(cycle[index], cycle[index + 1])
        report["pair"] = f"f{index}->f{(index + 1) % FRAME_COUNT}"
        pair_reports.append(report)

    return {
        "idle": idle_stats,
        "frames": frame_reports,
        "pairs": pair_reports,
        "summary": {
            "max_popping_pct": max(pair["popping_pct"] for pair in pair_reports),
            "max_abs_mass_drift_pct": max(
                abs(frame["mass_drift_vs_idle_pct"]) for frame in frame_reports
            ),
            "max_abs_feet_row_delta": max(
                abs(frame["feet_row_delta_vs_idle"]) for frame in frame_reports
            ),
        },
    }


def build_report(exports_dir: Path, idle_dir: Path) -> dict:
    facings = {
        facing: facing_metrics(exports_dir, idle_dir, facing) for facing in FACINGS
    }
    idle_down = load_opaque(idle_dir / "player_1_lane_b_idle_down.png")
    idle_right = load_opaque(idle_dir / "player_1_lane_b_idle_right.png")
    return {
        "generated_by": "tools/motion_metrics.py",
        "facings": facings,
        "reference": {"idle_cross_facing": pair_stats(idle_down, idle_right)},
    }


def check_report(report: dict) -> list[str]:
    """The two hard sprint-1 motion-contract lines."""
    failures: list[str] = []
    for facing, metrics in report["facings"].items():
        delta = metrics["summary"]["max_abs_feet_row_delta"]
        if delta > FEET_TOLERANCE_PX:
            failures.append(
                f"{facing}: feet-contact row drifts {delta}px from idle "
                f"(tolerance {FEET_TOLERANCE_PX}px)"
            )
        for pair in metrics["pairs"]:
            if pair["silhouette_changed_px"] == 0 and pair["recolored_px"] == 0:
                failures.append(f"{facing}: pair {pair['pair']} is static (dead frame)")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", type=Path, default=ROOT / "exports" / "calibration-v1")
    parser.add_argument(
        "--idle-exports", type=Path, default=ROOT / "exports" / "calibration-v0"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "reviews" / "calibration-v1" / "motion-metrics.json"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.exports, args.idle_exports)
    except MetricsError as exc:
        print(f"metrics failed: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"wrote {args.out}")
    if args.check:
        failures = check_report(report)
        for failure in failures:
            print(f"CHECK FAIL: {failure}", file=sys.stderr)
        if failures:
            return 1
        print("checks passed: feet-contact stability, no static pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
