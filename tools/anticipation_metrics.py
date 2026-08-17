#!/usr/bin/env python3
"""Deterministic windup-anticipation metrics: coil poses and flash-accent survival.

Measures the numbers behind the calibration-v3 anticipation rubric:

- anticipation poses: mass, bbox, feet-contact row, centroid, mass drift
  versus the frozen idle; silhouette delta (100 * XOR / union) versus the
  idle, every walk frame, AND the frozen strike key — the walk-side minimum
  is the confusability floor, the a0-vs-k0 delta is the separately
  pre-registered strike-distinctness value, and the maximum of all deltas is
  checked against the cross-facing identity ceiling; head-region share of
  the a0-vs-idle change
- flash-accent exploration: for every strip frame (idle, walks, a0, k0),
  the count of pixels whose original color is the frozen ramp accent — the
  pixels the ACC sheet row redraws over the pinned crimson flash — plus the
  WCAG contrast of accent against the flash fill (sheet-level exploration
  only; phase-0 exports may not assume it)
- bbox-ring breathing extended to the anticipation pose (metrics only, an
  integration record): idle->a0 and a0->k0 max edge shifts

`--check` enforces the four hard sprint-3 contract lines and exits nonzero
on violation: a0 feet-contact row within +-1px of the idle baseline,
walk-side confusability floor >= 25%, a0-vs-k0 distinctness >= 25%, and
every a0 delta below the cross-facing identity ceiling.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from feedback_metrics import contrast_ratio, ring_rects  # noqa: E402
from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402

FACINGS = ("down", "right")
FRAME_COUNT = 4
FEET_TOLERANCE_PX = 1
WALK_CONFUSABILITY_FLOOR_PCT = 25.0
STRIKE_DISTINCTNESS_FLOOR_PCT = 25.0
HEAD_REGION_MAX_ROW = 15
# The frozen ramp accent #140e0c (eyes/feet caps). A test ties this constant
# byte-for-byte to the calibration-v0 idle spec palette entry "k".
ACCENT_RGB = (20, 14, 12)

STRIP = ("idle", "f0", "f1", "f2", "f3", "a0", "k0")


class AnticipationMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


def anticipation_metrics(
    a0: dict[tuple[int, int], tuple[int, int, int]],
    idle: dict[tuple[int, int], tuple[int, int, int]],
    walks: list[dict[tuple[int, int], tuple[int, int, int]]],
    k0: dict[tuple[int, int], tuple[int, int, int]],
) -> dict:
    idle_stats = frame_stats(idle)
    stats = frame_stats(a0)
    stats["mass_drift_vs_idle_pct"] = round(
        100 * (stats["mass"] - idle_stats["mass"]) / idle_stats["mass"], 2
    )
    stats["feet_row_delta_vs_idle"] = stats["feet_row"] - idle_stats["feet_row"]

    deltas = []
    comparisons = [
        ("idle", idle),
        *[(f"f{index}", walk) for index, walk in enumerate(walks)],
        ("k0", k0),
    ]
    for name, frame in comparisons:
        report = pair_stats(frame, a0)
        report["vs"] = name
        deltas.append(report)
    walk_side = [d["popping_pct"] for d in deltas if d["vs"] != "k0"]
    strike = next(d["popping_pct"] for d in deltas if d["vs"] == "k0")

    a0_keys, idle_keys = set(a0), set(idle)
    changed = a0_keys ^ idle_keys
    head_changed = sum(1 for _, y in changed if y <= HEAD_REGION_MAX_ROW)
    head_share = round(100 * head_changed / len(changed), 2) if changed else 0.0

    return {
        "pose": stats,
        "deltas": deltas,
        "walk_confusability_floor_pct": min(walk_side),
        "strike_distinctness_pct": strike,
        "max_delta_pct": max([*walk_side, strike]),
        "head_region_share_vs_idle_pct": head_share,
    }


def accent_metrics(
    frames: dict[str, dict[tuple[int, int], tuple[int, int, int]]],
    flash_rgb: tuple[int, int, int],
) -> dict:
    """Flash-accent survival: pixels the ACC row redraws over the crimson."""
    per_frame = {}
    for name, pixels in frames.items():
        surviving = sum(1 for rgb in pixels.values() if rgb == ACCENT_RGB)
        per_frame[name] = {
            "surviving_accent_px": surviving,
            "accent_share_of_mass_pct": round(100 * surviving / len(pixels), 2),
        }
    return {
        "accent_rgb": list(ACCENT_RGB),
        "flash_rgb": list(flash_rgb),
        "contrast_accent_vs_flash": contrast_ratio(ACCENT_RGB, flash_rgb),
        "frames": per_frame,
    }


def ring_breathing(
    frames: dict[str, dict[tuple[int, int], tuple[int, int, int]]], reference: dict
) -> dict:
    """Bbox-ring edge shifts across the attack grammar (integration record)."""
    rects = {
        name: ring_rects(frames[name], reference)["bbox_ring"]
        for name in ("idle", "a0", "k0")
    }
    def max_edge(a: str, b: str) -> int:
        return max(abs(p - q) for p, q in zip(rects[a], rects[b]))
    return {
        "bbox_ring_rects": {name: list(rect) for name, rect in rects.items()},
        "idle_to_a0_max_edge_px": max_edge("idle", "a0"),
        "a0_to_k0_max_edge_px": max_edge("a0", "k0"),
    }


def load_frames(
    anticipation_dir: Path, attack_dir: Path, walk_dir: Path, idle_dir: Path, facing: str
) -> dict[str, dict[tuple[int, int], tuple[int, int, int]]]:
    frames = {"idle": load_opaque(idle_dir / f"player_1_lane_b_idle_{facing}.png")}
    for index in range(FRAME_COUNT):
        frames[f"f{index}"] = load_opaque(
            walk_dir / f"player_1_lane_b_walk_{facing}_f{index}.png"
        )
    frames["a0"] = load_opaque(
        anticipation_dir / f"player_1_lane_b_attack_{facing}_a0.png"
    )
    frames["k0"] = load_opaque(attack_dir / f"player_1_lane_b_attack_{facing}_k0.png")
    return frames


def build_report(
    anticipation_dir: Path,
    attack_dir: Path,
    walk_dir: Path,
    idle_dir: Path,
    reference: dict,
) -> dict:
    flash_rgb = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
    anticipation = {}
    accents = {}
    rings = {}
    for facing in FACINGS:
        frames = load_frames(anticipation_dir, attack_dir, walk_dir, idle_dir, facing)
        walks = [frames[f"f{index}"] for index in range(FRAME_COUNT)]
        anticipation[facing] = anticipation_metrics(
            frames["a0"], frames["idle"], walks, frames["k0"]
        )
        accents[facing] = accent_metrics(frames, flash_rgb)
        rings[facing] = ring_breathing(frames, reference)
    idle_down = load_opaque(idle_dir / "player_1_lane_b_idle_down.png")
    idle_right = load_opaque(idle_dir / "player_1_lane_b_idle_right.png")
    return {
        "generated_by": "tools/anticipation_metrics.py",
        "anticipation": anticipation,
        "flash_accent": accents,
        "rings": rings,
        "reference": {"idle_cross_facing": pair_stats(idle_down, idle_right)},
    }


def check_report(report: dict) -> list[str]:
    """The four hard sprint-3 anticipation-contract lines."""
    failures: list[str] = []
    ceiling = report["reference"]["idle_cross_facing"]["popping_pct"]
    for facing, metrics in report["anticipation"].items():
        feet_delta = abs(metrics["pose"]["feet_row_delta_vs_idle"])
        if feet_delta > FEET_TOLERANCE_PX:
            failures.append(
                f"{facing}: a0 feet-contact row drifts {feet_delta}px from idle "
                f"(tolerance {FEET_TOLERANCE_PX}px)"
            )
        floor = metrics["walk_confusability_floor_pct"]
        if floor < WALK_CONFUSABILITY_FLOOR_PCT:
            failures.append(
                f"{facing}: walk-side confusability floor {floor}% is below "
                f"{WALK_CONFUSABILITY_FLOOR_PCT}% (windup confusable with idle/walk)"
            )
        strike = metrics["strike_distinctness_pct"]
        if strike < STRIKE_DISTINCTNESS_FLOOR_PCT:
            failures.append(
                f"{facing}: a0-vs-k0 distinctness {strike}% is below "
                f"{STRIKE_DISTINCTNESS_FLOOR_PCT}% (windup confusable with strike)"
            )
        peak = metrics["max_delta_pct"]
        if peak >= ceiling:
            failures.append(
                f"{facing}: a0 delta {peak}% reaches the cross-facing identity "
                f"ceiling {ceiling}% (identity change, not state change)"
            )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        default=ROOT / "reviews" / "calibration-v3" / "anticipation-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    try:
        report = build_report(
            args.anticipation_exports, args.attack_exports, args.walk_exports,
            args.idle_exports, reference,
        )
    except (AnticipationMetricsError, ValueError) as exc:
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
        print(
            "checks passed: a0 feet stability, walk confusability floor, "
            "strike distinctness, identity ceiling"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
