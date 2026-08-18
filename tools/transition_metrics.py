#!/usr/bin/env python3
"""Deterministic transition metrics and validator for the sprint-6 sheet.

Measures and machine-checks the pre-registered calibration-v6 bars
(reviews/calibration-v6/rationale.md):

1. bridging bar on export bytes, per in-between, per facing -
   max(d(X,M), d(M,Y)) < d(X,Y): the boundary's largest single-tick
   silhouette jump strictly decreases (full decomposition reported);
2. nearest-neighbor bar - among the four grammar states {idle, a0, k0, r0},
   the in-between's two smallest deltas are exactly its two endpoints
   (deltas to every walk frame reported);
3. identity ceiling - every in-between delta < the 44.44% cross-facing
   reference; feet-contact row within +-1px of the idle baseline;
4. frozen-state protection - every consumed export hashes to its banked
   release.json SHA-256 (calibration-v0..v3, v5, v6), so the five banked
   state exports are byte-untouched and their banked floors stand by
   construction; the release boundary (a0->k0 pose pair at -3/+6) is
   machine-compared IDENTICAL in timelines A and B;
5. compositor byte-determinism - the sheet (and any APNG aid) is SHA-256
   identical across two independent in-process builds, and committed
   artifact bytes equal a fresh build;
6. composition purity - every creature cell equals a banked export's opaque
   pixels blitted at the computed integer offset over freshly reconstructed
   pinned-palette tiles (verified twice per cell); the DIFF row is a derived
   diagnostic, declared, not a creature cell;
7. tick math exact - windup = 5 cells at -3 in BOTH timelines (B: w0 x1 +
   a0 x4), active = 4 at +6 (k0, both), recovery = 8 at 0 (B: s0 x1 +
   r0 x7), walk = 13 at independently recomputed smoothstep positions;
   timelines tick-identical except the two transition ticks.

Also reports the boundary-jump table across A and B (pose delta + position
delta per boundary tick pair, sharpest-single-tick attribution) and the
derived hold durations after the tick consumption. `--check` exits nonzero
on any violation.
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

import make_transition_timeline as timeline  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from make_feedback_sheet import tell_cell  # noqa: E402
from motion_metrics import frame_stats, load_opaque, pair_stats  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

FEET_TOLERANCE_PX = 1
HEAD_REGION_MAX_ROW = 15
GRAMMAR_STATES = ("idle", "a0", "k0", "r0")
INBETWEENS = {"w0": ("idle", "a0"), "s0": ("k0", "r0")}

POSE_FILES = {
    "idle": ("idle_dir", "player_1_lane_b_idle_{facing}.png"),
    "f0": ("walk_dir", "player_1_lane_b_walk_{facing}_f0.png"),
    "f1": ("walk_dir", "player_1_lane_b_walk_{facing}_f1.png"),
    "f2": ("walk_dir", "player_1_lane_b_walk_{facing}_f2.png"),
    "f3": ("walk_dir", "player_1_lane_b_walk_{facing}_f3.png"),
    "a0": ("anticipation_dir", "player_1_lane_b_attack_{facing}_a0.png"),
    "k0": ("attack_dir", "player_1_lane_b_attack_{facing}_k0.png"),
    "r0": ("recovery_dir", "player_1_lane_b_attack_{facing}_r0.png"),
    "w0": ("transition_dir", "player_1_lane_b_attack_{facing}_w0.png"),
    "s0": ("transition_dir", "player_1_lane_b_attack_{facing}_s0.png"),
}
RELEASE_IDS = (
    "calibration-v0", "calibration-v1", "calibration-v2", "calibration-v3",
    "calibration-v5", "calibration-v6",
)


class TransitionMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- static bars (bridging, nearest-neighbor, ceiling) -------------------------


def inbetween_metrics(
    name: str,
    frames: dict[str, dict[tuple[int, int], tuple[int, int, int]]],
) -> dict:
    x_name, y_name = INBETWEENS[name]
    m = frames[name]
    idle_stats = frame_stats(frames["idle"])
    stats = frame_stats(m)
    stats["mass_drift_vs_idle_pct"] = round(
        100 * (stats["mass"] - idle_stats["mass"]) / idle_stats["mass"], 2
    )
    stats["feet_row_delta_vs_idle"] = stats["feet_row"] - idle_stats["feet_row"]

    grammar_deltas = {}
    for state in GRAMMAR_STATES:
        report = pair_stats(frames[state], m)
        grammar_deltas[state] = report["popping_pct"]
    walk_deltas = {
        f"f{index}": pair_stats(frames[f"f{index}"], m)["popping_pct"]
        for index in range(4)
    }
    d_xy = pair_stats(frames[x_name], frames[y_name])["popping_pct"]
    d_xm = grammar_deltas[x_name]
    d_my = grammar_deltas[y_name]
    ordered = sorted(grammar_deltas.items(), key=lambda kv: (kv[1], kv[0]))
    two_smallest = sorted([ordered[0][0], ordered[1][0]])

    m_keys, idle_keys = set(m), set(frames["idle"])
    changed = m_keys ^ idle_keys
    head_changed = sum(1 for _, y in changed if y <= HEAD_REGION_MAX_ROW)
    head_share = round(100 * head_changed / len(changed), 2) if changed else 0.0

    return {
        "pose": stats,
        "endpoints": [x_name, y_name],
        "bridging": {
            "d_x_m_pct": d_xm,
            "d_m_y_pct": d_my,
            "d_x_y_pct": d_xy,
            "max_leg_pct": max(d_xm, d_my),
            "passes": max(d_xm, d_my) < d_xy,
        },
        "nearest_neighbor": {
            "grammar_deltas": grammar_deltas,
            "two_smallest": two_smallest,
            "passes": two_smallest == sorted([x_name, y_name]),
        },
        "walk_deltas": walk_deltas,
        "max_delta_pct": max([*grammar_deltas.values(), *walk_deltas.values()]),
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
    """The pre-registered static bars (bridging, nearest-neighbor, ceiling,
    feet)."""
    failures: list[str] = []
    ceiling = report["reference"]["idle_cross_facing"]["popping_pct"]
    for facing, per_inbetween in report["static"].items():
        for name, metrics in per_inbetween.items():
            if name == "cross_delta_w0_s0_pct":
                continue
            x_name, y_name = metrics["endpoints"]
            bridge = metrics["bridging"]
            if not bridge["passes"]:
                failures.append(
                    f"{facing}/{name}: bridging max({bridge['d_x_m_pct']}, "
                    f"{bridge['d_m_y_pct']}) does not decrease the "
                    f"{x_name}->{y_name} jump {bridge['d_x_y_pct']}"
                )
            nn = metrics["nearest_neighbor"]
            if not nn["passes"]:
                failures.append(
                    f"{facing}/{name}: nearest neighbors {nn['two_smallest']} "
                    f"are not the endpoints {sorted([x_name, y_name])} "
                    f"(reads as a new/wrong state)"
                )
            peak = metrics["max_delta_pct"]
            if peak >= ceiling:
                failures.append(
                    f"{facing}/{name}: delta {peak}% reaches the cross-facing "
                    f"identity ceiling {ceiling}% (identity change, not bridge)"
                )
            feet_delta = abs(metrics["pose"]["feet_row_delta_vs_idle"])
            if feet_delta > FEET_TOLERANCE_PX:
                failures.append(
                    f"{facing}/{name}: feet-contact row drifts {feet_delta}px "
                    f"from idle (tolerance {FEET_TOLERANCE_PX}px)"
                )
    return failures


# -- boundary-jump table and release preservation ------------------------------


def boundary_jump_table(
    plan: dict,
    frames_by_facing: dict[str, dict[str, dict]],
) -> dict:
    """Per facing, per timeline: pose delta + position delta for every
    consecutive tick pair, the boundary rows under test, and the
    sharpest-single-tick attribution."""
    ticks = plan["ticks"]
    table: dict = {}
    for facing, frames in frames_by_facing.items():
        per_timeline = {}
        for tl in timeline.TIMELINES:
            jumps = []
            for before, after in zip(ticks, ticks[1:]):
                pose_from = before["poses"][tl]
                pose_to = after["poses"][tl]
                delta = (
                    0.0
                    if pose_from == pose_to
                    else pair_stats(frames[pose_from], frames[pose_to])["popping_pct"]
                )
                jumps.append(
                    {
                        "from_tick": before["tick"],
                        "to_tick": after["tick"],
                        "pose_from": pose_from,
                        "pose_to": pose_to,
                        "pose_delta_pct": delta,
                        "position_delta_px": after["axis_px"] - before["axis_px"],
                    }
                )
            sharpest_pose = max(jumps, key=lambda j: j["pose_delta_pct"])
            sharpest_position = max(
                jumps, key=lambda j: abs(j["position_delta_px"])
            )
            per_timeline[tl] = {
                "boundary_rows": [
                    j for j in jumps
                    if (j["from_tick"], j["to_tick"]) in
                    ((14, 15), (15, 16), (19, 20), (23, 24), (24, 25), (31, 32))
                ],
                "sharpest_pose_jump": sharpest_pose,
                "sharpest_position_jump": sharpest_position,
            }
        table[facing] = per_timeline
    return table


def release_preservation(
    plan: dict, frames_by_facing: dict[str, dict[str, dict]]
) -> dict:
    """The a0->k0 release boundary must be IDENTICAL in A and B: same poses,
    same offsets, same delta (machine-compared, never assumed)."""
    ticks = plan["ticks"]
    last_windup = [t for t in ticks if t["phase"] == "windup"][-1]
    first_active = [t for t in ticks if t["phase"] == "active"][0]
    identical = all(
        last_windup["poses"][tl] == "a0" and first_active["poses"][tl] == "k0"
        for tl in timeline.TIMELINES
    )
    per_facing = {}
    for facing, frames in frames_by_facing.items():
        deltas = {
            tl: pair_stats(
                frames[last_windup["poses"][tl]], frames[first_active["poses"][tl]]
            )["popping_pct"]
            for tl in timeline.TIMELINES
        }
        per_facing[facing] = {
            "delta_pct_per_timeline": deltas,
            "identical_across_timelines": len(set(deltas.values())) == 1,
        }
    return {
        "from_tick": last_windup["tick"],
        "to_tick": first_active["tick"],
        "pose_pair_pinned": identical,
        "position_delta_px": first_active["axis_px"] - last_windup["axis_px"],
        "per_facing": per_facing,
        "note": (
            "the release stays deliberately unsmoothed: no in-between, no "
            "offset change - the banked v4 salience (KB: the strike is the "
            "instant beat; anticipation eases in, follow-through cushions)"
        ),
    }


def check_release(release: dict) -> list[str]:
    failures = []
    if not release["pose_pair_pinned"]:
        failures.append("release boundary poses differ from the pinned a0->k0")
    if release["position_delta_px"] != 9:
        failures.append(
            f"release position step {release['position_delta_px']}px != +9px "
            f"(pinned -3 -> +6)"
        )
    for facing, data in release["per_facing"].items():
        if not data["identical_across_timelines"]:
            failures.append(
                f"{facing}: release delta differs between timelines "
                f"{data['delta_pct_per_timeline']}"
            )
    return failures


def durations_ms(constants: dict) -> dict:
    return {
        "note": "derived at the unoverridden Gosu default 16.666666 ms/tick; "
        "ticks are the contract numbers; timeline B consumes one pinned tick "
        "per boundary for the in-between (never adds ticks)",
        "windup_ms": round(constants["windup_frames"] * TICK_MS, 1),
        "active_ms": round(constants["active_frames"] * TICK_MS, 1),
        "recovery_ms": round(constants["recovery_frames"] * TICK_MS, 1),
        "step_ms": round(constants["step_frames"] * TICK_MS, 1),
        "timeline_b_holds": {
            "w0_ticks": 1,
            "a0_hold_ticks": constants["windup_frames"] - 1,
            "a0_hold_ms": round((constants["windup_frames"] - 1) * TICK_MS, 1),
            "s0_ticks": 1,
            "r0_hold_ticks": constants["recovery_frames"] - 1,
            "r0_hold_ms": round((constants["recovery_frames"] - 1) * TICK_MS, 1),
        },
    }


# -- composition purity ---------------------------------------------------------


def reconstruct_cell(
    sheet: timeline.TransitionTimelineSheet, cell: dict
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
    canvas: Rgba8Canvas, sheet: timeline.TransitionTimelineSheet,
    dirs: dict[str, Path],
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


# -- tick math -------------------------------------------------------------------


def check_tick_math(
    sheet: timeline.TransitionTimelineSheet, reference: dict
) -> list[str]:
    failures: list[str] = []
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    windup_n = timing["windup_frames"]["value"]
    recovery_n = timing["recovery_frames"]["value"]
    pose_sequences = {
        "windup": {
            "A": ["a0"] * windup_n,
            "B": ["w0"] + ["a0"] * (windup_n - 1),
        },
        "active": {
            tl: ["k0"] * timing["active_frames"]["value"]
            for tl in timeline.TIMELINES
        },
        "recovery": {
            "A": ["r0"] * recovery_n,
            "B": ["s0"] + ["r0"] * (recovery_n - 1),
        },
    }
    offsets = {
        "windup": lunge["windup_px"],
        "active": lunge["active_px"],
        "recovery": 0,
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
                for phase, sequences in pose_sequences.items():
                    cells = sorted(
                        (c for c in rows if c["phase"] == phase),
                        key=lambda c: c["tick"],
                    )
                    expected = sequences[tl]
                    if len(cells) != len(expected):
                        failures.append(
                            f"{facing}/{zone}/{tl}: {len(cells)} {phase} cells "
                            f"rendered, pinned {len(expected)}"
                        )
                        continue
                    actual = [c["pose"] for c in cells]
                    if actual != expected:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {phase} poses {actual} != "
                            f"pinned {expected}"
                        )
                    bad_offset = [
                        c for c in cells if c["win_px"] != offsets[phase]
                    ]
                    if bad_offset:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {phase} offset "
                            f"{bad_offset[0]['win_px']} != pinned {offsets[phase]}"
                        )
            tick_sets = {tl: set(cells) for tl, cells in per_timeline.items()}
            if len(set(map(frozenset, tick_sets.values()))) != 1:
                failures.append(f"{facing}/{zone}: A/B tick sets differ")
                continue
            transition = {
                t["tick"]
                for t in sheet.plan["ticks"]
                if t["poses"]["A"] != t["poses"]["B"]
            }
            for tick, cell_a in per_timeline["A"].items():
                other = per_timeline["B"].get(tick)
                if other is None:
                    continue
                if cell_a["win_px"] != other["win_px"]:
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: A/B positions differ"
                    )
                if tick not in transition and cell_a["pose"] != other["pose"]:
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: A/B poses differ outside "
                        f"the transition ticks"
                    )
                if tick in transition and cell_a["pose"] == other["pose"]:
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: transition tick shows the "
                        f"same pose in A and B"
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
        ("idle", "idle", 0), ("f1", "f1", 0),
        ("w0", "w0", lunge["windup_px"]), ("a0", "a0", 0),
        ("wind", "a0", lunge["windup_px"]), ("k0", "k0", 0),
        ("lunge", "k0", lunge["active_px"]), ("s0", "s0", 0), ("r0", "r0", 0),
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
    expected_six = [t["tick"] for t in timeline.transition_ticks(sheet.plan)]
    twox = [c for c in sheet.cells if c["section"] == "twox"]
    for facing in timeline.FACINGS:
        ticks = [c["tick"] for c in twox if c["facing"] == facing]
        if ticks != expected_six:
            failures.append(
                f"{facing}: 2X transition ticks {ticks} != {expected_six}"
            )
    fourx = [c for c in sheet.cells if c["section"] == "fourx"]
    for facing in timeline.FACINGS:
        ticks = [c["tick"] for c in fourx if c["facing"] == facing]
        if ticks != expected_six:
            failures.append(
                f"{facing}: 4X boundary ticks {ticks} != {expected_six}"
            )
        scales = {c["scale"] for c in fourx if c["facing"] == facing}
        if scales != {timeline.FOURX_SCALE}:
            failures.append(f"{facing}: 4X scale {scales} != 4")
    return failures


# -- export pins -----------------------------------------------------------------


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
    transition_dir: Path,
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
        "transition_dir": transition_dir,
        "recovery_dir": recovery_dir,
        "anticipation_dir": anticipation_dir,
        "attack_dir": attack_dir,
        "walk_dir": walk_dir,
        "idle_dir": idle_dir,
    }
    frames_by_facing = {
        facing: load_frames(dirs, facing) for facing in timeline.FACINGS
    }
    static = {}
    for facing, frames in frames_by_facing.items():
        static[facing] = {
            name: inbetween_metrics(name, frames) for name in INBETWEENS
        }
        static[facing]["cross_delta_w0_s0_pct"] = pair_stats(
            frames["w0"], frames["s0"]
        )["popping_pct"]

    sheet = timeline.TransitionTimelineSheet(
        transition_dir, recovery_dir, anticipation_dir, attack_dir, walk_dir,
        idle_dir, reference,
    )
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.TransitionTimelineSheet(
        transition_dir, recovery_dir, anticipation_dir, attack_dir, walk_dir,
        idle_dir, reference,
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
            target = apng_dir / f"timeline-ab-{facing}.apng"
            apng[facing] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames),
            }

    idle_down = frames_by_facing["down"]["idle"]
    idle_right = frames_by_facing["right"]["idle"]
    return {
        "generated_by": "tools/transition_metrics.py",
        "constants": sheet.plan["constants"],
        "durations_ms": durations_ms(sheet.plan["constants"]),
        "static": static,
        "boundaries": boundary_jump_table(sheet.plan, frames_by_facing),
        "release_preservation": release_preservation(sheet.plan, frames_by_facing),
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
    failures.extend(check_release(report["release_preservation"]))
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
        "--sheet", type=Path,
        default=ROOT / "reviews" / "calibration-v6" / "timeline-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v6" / "timeline-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    try:
        report = build_report(
            args.transition_exports, args.recovery_exports,
            args.anticipation_exports, args.attack_exports, args.walk_exports,
            args.idle_exports, reference,
            sheet_path=args.sheet, apng_dir=args.apng_dir,
        )
    except (TransitionMetricsError, ValueError, OSError) as exc:
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
            "checks passed: bridging, nearest-neighbor, ceiling, release "
            "preservation, byte-determinism, composition purity, tick math, "
            "banked export pins"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
