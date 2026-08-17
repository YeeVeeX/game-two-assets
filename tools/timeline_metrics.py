#!/usr/bin/env python3
"""Deterministic timeline metrics and validator for the sprint-4 grammar sheet.

Measures and machine-checks the four pre-registered calibration-v4 bars
(reviews/calibration-v4/rationale.md):

1. compositor byte-determinism - the sheet (and any APNG aid) is SHA-256
   identical across two independent in-process builds, and the committed
   artifact bytes equal a fresh build;
2. composition purity - every creature cell equals a banked export's opaque
   pixels blitted at the computed integer offset over freshly reconstructed
   pinned-palette tiles (verified twice per cell: full-region reconstruction
   AND direct export-byte pixel equality at the recorded blit position);
3. tick math exact - rendered windup/active/recovery/walk cell counts equal
   the pinned constants; offsets exactly windup/active/rest along the facing
   axis; timelines A and B tick-for-tick identical except the windup pose;
   walk positions equal independently recomputed smoothstep values;
4. zero new creature pixels - every export consumed hashes to its banked
   release.json SHA-256.

Also reports the per-tick displacement profile (the anchoring evidence), the
derived durations at the unoverridden 16.666666 ms tick, and the flicker-row
accent survival counts. `--check` exits nonzero on any violation.
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

import make_grammar_timeline as timeline  # noqa: E402
from anticipation_metrics import ACCENT_RGB  # noqa: E402
from make_contact_sheet import TILE, load_reference, sprite_from_png  # noqa: E402
from make_feedback_sheet import tell_cell  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

TICK_MS = 16.666666  # unoverridden Gosu 1.4.6 default (see attack_timing pin)

POSE_FILES = {
    "idle": ("idle_dir", "player_1_lane_b_idle_{facing}.png"),
    "f0": ("walk_dir", "player_1_lane_b_walk_{facing}_f0.png"),
    "f1": ("walk_dir", "player_1_lane_b_walk_{facing}_f1.png"),
    "f2": ("walk_dir", "player_1_lane_b_walk_{facing}_f2.png"),
    "f3": ("walk_dir", "player_1_lane_b_walk_{facing}_f3.png"),
    "a0": ("anticipation_dir", "player_1_lane_b_attack_{facing}_a0.png"),
    "k0": ("attack_dir", "player_1_lane_b_attack_{facing}_k0.png"),
}
RELEASE_IDS = ("calibration-v0", "calibration-v1", "calibration-v2", "calibration-v3")


class TimelineMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


def displacement_profile(plan: dict) -> list[dict]:
    profile = []
    previous = None
    for tick in plan["ticks"]:
        delta = 0 if previous is None else tick["axis_px"] - previous
        profile.append(
            {
                "tick": tick["tick"],
                "phase": tick["phase"],
                "pose_a": tick["pose_a"],
                "pose_b": tick["pose_b"],
                "axis_px": tick["axis_px"],
                "offset_px": tick["offset_px"],
                "delta_px": delta,
            }
        )
        previous = tick["axis_px"]
    return profile


def jump_magnitudes(profile: list[dict]) -> dict:
    by_phase: dict[str, list[dict]] = {}
    for entry in profile:
        by_phase.setdefault(entry["phase"], []).append(entry)
    walk_deltas = [abs(e["delta_px"]) for e in by_phase["walk"]]
    return {
        "windup_entry_px": by_phase["windup"][0]["delta_px"],
        "release_px": by_phase["active"][0]["delta_px"],
        "recovery_return_px": by_phase["recovery"][0]["delta_px"],
        "max_walk_delta_px": max(walk_deltas),
        "release_vs_max_walk_ratio": round(
            abs(by_phase["active"][0]["delta_px"]) / max(walk_deltas), 2
        ),
    }


def durations_ms(constants: dict) -> dict:
    return {
        "note": "derived at the unoverridden Gosu default 16.666666 ms/tick; "
        "ticks are the contract numbers",
        "windup_ms": round(constants["windup_frames"] * TICK_MS, 1),
        "active_ms": round(constants["active_frames"] * TICK_MS, 1),
        "recovery_ms": round(constants["recovery_frames"] * TICK_MS, 1),
        "step_ms": round(constants["step_frames"] * TICK_MS, 1),
        "kb_anticipation_band_ms": [100, 200],
        "exp_windup_ms": round(timeline.EXP_WINDUP_TICKS * TICK_MS, 1),
    }


def reconstruct_cell(sheet: timeline.TimelineSheet, cell: dict) -> Rgba8Canvas:
    """Independently redraw one cell from export bytes + pinned constants."""
    w, h = cell["rect"][2], cell["rect"][3]
    temp = Rgba8Canvas(w, h, timeline.BG)
    sprite = sheet.poses[cell["facing"]][cell["pose"]]
    if cell["section"] == "grammar":
        zone = sheet.reference["zones"][cell["zone"]]
        tell_cell(temp, 0, 0, zone, cell["facing"], sprite, cell["win_px"])
        return temp
    treated = timeline.treat(sprite, cell["treatment"], sheet.flash_rgb)
    composed = timeline.compose_window(
        sheet.reference["zones"][cell["zone"]], cell["facing"],
        cell["window_tiles"], treated, cell["win_px"],
    )
    if cell["scale"] == 1:
        return composed
    temp.blit_scaled(timeline.canvas_pixels(composed), 0, 0, cell["scale"])
    return temp


def cell_blit_origin(cell: dict) -> tuple[int, int]:
    """Window-relative sprite-canvas origin for the direct export-byte check."""
    if cell["section"] == "grammar":
        half = TILE // 2
        offset = half + cell["win_px"]
    else:
        offset = cell["win_px"]
    return (0, offset) if cell["facing"] == "down" else (offset, 0)


def check_purity(
    canvas: Rgba8Canvas, sheet: timeline.TimelineSheet, dirs: dict[str, Path]
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
        treated = timeline.treat(export, cell["treatment"], sheet.flash_rgb)
        bx, by = cell_blit_origin(cell)
        scale = cell["scale"]
        pixel_ok = all(
            canvas.get(x0 + (bx + sx) * scale, y0 + (by + sy) * scale)
            == (*rgb, 255)
            for sx, sy, rgb in treated.pixels
        )
        if not pixel_ok:
            failures.append(f"export-byte mismatch: {cell_id(cell)}")
    return {"cells_checked": len(sheet.cells), "failures": failures}


def cell_id(cell: dict) -> str:
    return (
        f"{cell['section']}/{cell['facing']}/{cell['zone']}/"
        f"{cell['timeline']}/tick{cell['tick']:02d}"
    )


def check_tick_math(sheet: timeline.TimelineSheet, reference: dict) -> list[str]:
    failures: list[str] = []
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    pins = {
        "windup": (timing["windup_frames"]["value"], lunge["windup_px"]),
        "active": (timing["active_frames"]["value"], lunge["active_px"]),
        "recovery": (timing["recovery_frames"]["value"], 0),
    }
    attack_cells = [c for c in sheet.cells if c["section"] == "attack"]
    for facing in timeline.FACINGS:
        for zone in ("zone_1", "zone_2"):
            for tl in ("A", "B"):
                rows = [
                    c for c in attack_cells
                    if c["facing"] == facing and c["zone"] == zone
                    and c["timeline"] == tl
                ]
                for phase, (count, offset) in pins.items():
                    cells = [c for c in rows if c["phase"] == phase]
                    if len(cells) != count:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {len(cells)} {phase} cells "
                            f"rendered, pinned {count}"
                        )
                    bad = [c for c in cells if c["win_px"] != offset]
                    if bad:
                        failures.append(
                            f"{facing}/{zone}/{tl}: {phase} offset "
                            f"{bad[0]['win_px']} != pinned {offset}"
                        )
            a_cells = {
                c["tick"]: c for c in rows_of(attack_cells, facing, zone, "A")
            }
            b_cells = {
                c["tick"]: c for c in rows_of(attack_cells, facing, zone, "B")
            }
            if set(a_cells) != set(b_cells):
                failures.append(f"{facing}/{zone}: A/B tick sets differ")
            for tick, cell_a in a_cells.items():
                cell_b = b_cells.get(tick)
                if cell_b is None:
                    continue
                if cell_a["win_px"] != cell_b["win_px"]:
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: A/B positions differ"
                    )
                same_expected = cell_a["phase"] != "windup"
                if same_expected and cell_a["pose"] != cell_b["pose"]:
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: A/B poses differ outside windup"
                    )
                if not same_expected and (cell_a["pose"], cell_b["pose"]) != (
                    "idle", "a0",
                ):
                    failures.append(
                        f"{facing}/{zone}/tick{tick}: windup poses not idle-vs-a0"
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
    return failures


def rows_of(cells: list[dict], facing: str, zone: str, tl: str) -> list[dict]:
    return [
        c for c in cells
        if c["facing"] == facing and c["zone"] == zone and c["timeline"] == tl
    ]


def load_release_pins(exports_root: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for release_id in RELEASE_IDS:
        manifest = json.loads(
            (exports_root / release_id / "release.json").read_text(encoding="utf-8")
        )
        for export in manifest["exports"]:
            pins[Path(export["path"]).name] = export["sha256"]
    return pins


def check_export_pins(
    dirs: dict[str, Path], pins: dict[str, str]
) -> dict:
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


def flicker_metrics(sheet: timeline.TimelineSheet) -> dict:
    period = sheet.flicker_period
    pattern = [timeline.flicker_on(t, period) for t in range(timeline.FLICKER_TICKS)]
    accents = {}
    for facing in timeline.FACINGS:
        idle = sheet.poses[facing]["idle"]
        accents[facing] = sum(1 for _, _, rgb in idle.pixels if rgb == ACCENT_RGB)
    return {
        "period_frames": period,
        "on_pattern": pattern,
        "on_ticks": sum(pattern),
        "idle_surviving_accent_px": accents,
    }


def build_report(
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
        "anticipation_dir": anticipation_dir,
        "attack_dir": attack_dir,
        "walk_dir": walk_dir,
        "idle_dir": idle_dir,
    }
    sheet = timeline.TimelineSheet(
        anticipation_dir, attack_dir, walk_dir, idle_dir, reference
    )
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.TimelineSheet(
        anticipation_dir, attack_dir, walk_dir, idle_dir, reference
    ).build().encode()
    sheet_sha = hashlib.sha256(encoded).hexdigest()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    apng = {}
    if apng_dir is not None:
        for facing in timeline.FACINGS:
            frames = timeline.build_apng_frames(sheet, facing)
            payload = timeline.encode_apng(
                frames, timeline.apng_delays(len(frames))
            )
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

    profile = displacement_profile(sheet.plan)
    report = {
        "generated_by": "tools/timeline_metrics.py",
        "constants": sheet.plan["constants"],
        "durations_ms": durations_ms(sheet.plan["constants"]),
        "displacement_profile": profile,
        "jumps": jump_magnitudes(profile),
        "flicker": flicker_metrics(sheet),
        "sheet": {
            "sha256": sheet_sha,
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
    return report


def check_report(report: dict) -> list[str]:
    failures: list[str] = []
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
        default=ROOT / "reviews" / "calibration-v4" / "timeline-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v4" / "timeline-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    try:
        report = build_report(
            args.anticipation_exports, args.attack_exports, args.walk_exports,
            args.idle_exports, reference, sheet_path=args.sheet,
            apng_dir=args.apng_dir,
        )
    except (TimelineMetricsError, ValueError, OSError) as exc:
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
            "checks passed: byte-determinism, composition purity, tick math, "
            "banked export pins"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
