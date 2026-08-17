#!/usr/bin/env python3
"""Deterministic feedback-state metrics: attack tells, hurt flash, ring variants.

Measures the numbers behind the calibration-v2 feedback rubric:

- attack poses: mass, bbox, feet-contact row, centroid, mass drift versus the
  frozen idle; silhouette delta (100 * XOR / union) versus the idle AND every
  walk frame — the minimum is the confusability floor, the maximum is checked
  against the cross-facing identity ceiling; head-region share of the
  pose-vs-idle change
- hurt flash: WCAG contrast of the pinned flash color against both zone
  palettes; RGB distance from the flash to telegraph edge/core, transition
  gold, and the role base color
- possession ring: per frame and per variant (current SIZE geometry versus
  the bbox-fit exploration variant): ring rect, visible ring margin,
  margin-to-body dominance ratio; bbox-ring breathing across the walk cycle

`--check` enforces the hard sprint-2 contract lines and exits nonzero on
violation: attack feet-contact row within +-1px of the idle baseline,
confusability floor >= 25%, and every attack delta below the cross-facing
identity ceiling.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402

FACINGS = ("down", "right")
FRAME_COUNT = 4
FEET_TOLERANCE_PX = 1
CONFUSABILITY_FLOOR_PCT = 25.0
HEAD_REGION_MAX_ROW = 15


class FeedbackMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.x relative luminance of an sRGB color."""
    channels = []
    for value in rgb:
        c = value / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return round(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5, 1)


def attack_metrics(
    attack: dict[tuple[int, int], tuple[int, int, int]],
    idle: dict[tuple[int, int], tuple[int, int, int]],
    walks: list[dict[tuple[int, int], tuple[int, int, int]]],
) -> dict:
    idle_stats = frame_stats(idle)
    stats = frame_stats(attack)
    stats["mass_drift_vs_idle_pct"] = round(
        100 * (stats["mass"] - idle_stats["mass"]) / idle_stats["mass"], 2
    )
    stats["feet_row_delta_vs_idle"] = stats["feet_row"] - idle_stats["feet_row"]

    deltas = []
    for name, frame in [("idle", idle), *[(f"f{i}", w) for i, w in enumerate(walks)]]:
        report = pair_stats(frame, attack)
        report["vs"] = name
        deltas.append(report)

    attack_keys, idle_keys = set(attack), set(idle)
    changed = attack_keys ^ idle_keys
    head_changed = sum(1 for _, y in changed if y <= HEAD_REGION_MAX_ROW)
    head_share = round(100 * head_changed / len(changed), 2) if changed else 0.0

    return {
        "pose": stats,
        "deltas": deltas,
        "confusability_floor_pct": min(d["popping_pct"] for d in deltas),
        "max_delta_pct": max(d["popping_pct"] for d in deltas),
        "head_region_share_vs_idle_pct": head_share,
    }


def flash_metrics(reference: dict) -> dict:
    flash = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
    zones = reference["zones"]
    telegraph = reference["telegraph"]
    role_base = tuple(reference["primitive_body"]["body_rgb"])
    contrast = {}
    for zone_name, zone in sorted(zones.items()):
        contrast[zone_name] = {
            "floor": contrast_ratio(flash, tuple(zone["floor"])),
            "wall": contrast_ratio(flash, tuple(zone["wall"])),
        }
    gold = tuple(zones["zone_1"]["transition"])
    return {
        "rgb": list(flash),
        "contrast": contrast,
        "rgb_distance": {
            "telegraph_edge": rgb_distance(flash, tuple(telegraph["edge_rgb"])),
            "telegraph_core": rgb_distance(flash, tuple(telegraph["core_rgb"])),
            "transition_gold": rgb_distance(flash, gold),
            "role_base": rgb_distance(flash, role_base),
        },
    }


def ring_rects(
    pixels: dict[tuple[int, int], tuple[int, int, int]], reference: dict
) -> dict[str, tuple[int, int, int, int]]:
    """Inclusive (left, top, right, bottom) ring rects for both variants."""
    body = reference["primitive_body"]
    expand = reference["possession_ring"]["expand"]
    ox, oy = body["tile_offset"]
    size = body["size"]
    xs = [x for x, _ in pixels]
    ys = [y for _, y in pixels]
    return {
        "size_ring": (ox - expand, oy - expand, ox + size - 1 + expand, oy + size - 1 + expand),
        "bbox_ring": (min(xs) - expand, min(ys) - expand, max(xs) + expand, max(ys) + expand),
    }


def ring_variant_report(
    rect: tuple[int, int, int, int], mass: int
) -> dict:
    area = (rect[2] - rect[0] + 1) * (rect[3] - rect[1] + 1)
    visible = area - mass
    return {
        "rect": list(rect),
        "area_px": area,
        "visible_margin_px": visible,
        "margin_to_body_ratio": round(visible / mass, 2),
    }


def ring_metrics(
    frames: dict[str, dict[tuple[int, int], tuple[int, int, int]]], reference: dict
) -> dict:
    reports = []
    for name, pixels in frames.items():
        rects = ring_rects(pixels, reference)
        mass = len(pixels)
        reports.append(
            {
                "frame": name,
                "size_ring": ring_variant_report(rects["size_ring"], mass),
                "bbox_ring": ring_variant_report(rects["bbox_ring"], mass),
            }
        )
    walk_rects = [
        ring_rects(frames[f"f{index}"], reference)["bbox_ring"] for index in range(FRAME_COUNT)
    ]
    cycle = [*walk_rects, walk_rects[0]]
    breathing = max(
        abs(a - b) for before, after in zip(cycle, cycle[1:]) for a, b in zip(before, after)
    )
    idle_to_attack = max(
        abs(a - b)
        for a, b in zip(
            ring_rects(frames["idle"], reference)["bbox_ring"],
            ring_rects(frames["k0"], reference)["bbox_ring"],
        )
    )
    return {
        "frames": reports,
        "bbox_ring_walk_breathing_max_edge_px": breathing,
        "bbox_ring_idle_to_attack_max_edge_px": idle_to_attack,
    }


def load_frames(
    attack_dir: Path, walk_dir: Path, idle_dir: Path, facing: str
) -> dict[str, dict[tuple[int, int], tuple[int, int, int]]]:
    frames = {"idle": load_opaque(idle_dir / f"player_1_lane_b_idle_{facing}.png")}
    for index in range(FRAME_COUNT):
        frames[f"f{index}"] = load_opaque(
            walk_dir / f"player_1_lane_b_walk_{facing}_f{index}.png"
        )
    frames["k0"] = load_opaque(attack_dir / f"player_1_lane_b_attack_{facing}_k0.png")
    return frames


def build_report(
    attack_dir: Path, walk_dir: Path, idle_dir: Path, reference: dict
) -> dict:
    attack = {}
    rings = {}
    for facing in FACINGS:
        frames = load_frames(attack_dir, walk_dir, idle_dir, facing)
        walks = [frames[f"f{index}"] for index in range(FRAME_COUNT)]
        attack[facing] = attack_metrics(frames["k0"], frames["idle"], walks)
        rings[facing] = ring_metrics(frames, reference)
    idle_down = load_opaque(idle_dir / "player_1_lane_b_idle_down.png")
    idle_right = load_opaque(idle_dir / "player_1_lane_b_idle_right.png")
    return {
        "generated_by": "tools/feedback_metrics.py",
        "attack": attack,
        "flash": flash_metrics(reference),
        "rings": rings,
        "reference": {"idle_cross_facing": pair_stats(idle_down, idle_right)},
    }


def check_report(report: dict) -> list[str]:
    """The hard sprint-2 feedback-contract lines."""
    failures: list[str] = []
    ceiling = report["reference"]["idle_cross_facing"]["popping_pct"]
    for facing, metrics in report["attack"].items():
        feet_delta = abs(metrics["pose"]["feet_row_delta_vs_idle"])
        if feet_delta > FEET_TOLERANCE_PX:
            failures.append(
                f"{facing}: attack feet-contact row drifts {feet_delta}px from idle "
                f"(tolerance {FEET_TOLERANCE_PX}px)"
            )
        floor = metrics["confusability_floor_pct"]
        if floor < CONFUSABILITY_FLOOR_PCT:
            failures.append(
                f"{facing}: confusability floor {floor}% is below "
                f"{CONFUSABILITY_FLOOR_PCT}% (tell confusable with idle/walk)"
            )
        peak = metrics["max_delta_pct"]
        if peak >= ceiling:
            failures.append(
                f"{facing}: attack delta {peak}% reaches the cross-facing identity "
                f"ceiling {ceiling}% (identity change, not state change)"
            )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        default=ROOT / "reviews" / "calibration-v2" / "feedback-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    try:
        report = build_report(
            args.attack_exports, args.walk_exports, args.idle_exports, reference
        )
    except (FeedbackMetricsError, ValueError) as exc:
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
        print("checks passed: attack feet stability, confusability floor, identity ceiling")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
