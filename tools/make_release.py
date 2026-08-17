#!/usr/bin/env python3
"""Emit exports/<release>/release.json with pinned commits and full hash chain.

Reads the frozen pixel specs, native sources, and exports; records SHA-256 for
every file plus the source/game commits. Refuses to write when the working
tree state under sources/ or tools/ differs from HEAD, so the recorded source
commit is always honest.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from asset_gate import sha256_file  # noqa: E402
from pixel_spec import load_spec_dir  # noqa: E402

RELEASE_ID = "calibration-v0"
EXPORTER = "tools/export_assets.py"
PROVENANCE = {
    "origin": "procedural",
    "author": "dev agent (pi session, sprint 0)",
    "created": "2026-08-17",
    "rights": "private-project",
    "method": (
        "authored as reviewable pixel-grid specs (sources/calibration-v0/specs), "
        "built into native Aseprite sources via tools/aseprite_build.lua, exported "
        "deterministically via tools/export_assets.py and verified pixel-for-pixel "
        "against the specs"
    ),
}


def _idle_copy_note(facing: str) -> str:
    return (
        f"pass frame: the calibration-v0 player_1_lane_b_idle_{facing} spec copied "
        "forward verbatim as walk frame f3; export bytes match the calibration-v0 "
        "idle export"
    )


# Per-release provenance registry. Every entry is frozen once its release is
# banked; new sprints append a new release id instead of editing older ones.
RELEASES: dict[str, dict] = {
    "calibration-v0": {"provenance": PROVENANCE, "asset_notes": {}},
    "calibration-v1": {
        "provenance": {
            "origin": "procedural",
            "author": "dev agent (pi session, sprint 1)",
            "created": "2026-08-17",
            "rights": "private-project",
            "method": (
                "authored as reviewable pixel-grid specs derived from the frozen "
                "calibration-v0 lane-B idle poses (sources/calibration-v1/specs), "
                "built into native Aseprite sources via tools/aseprite_build.lua, "
                "exported deterministically via tools/export_assets.py and verified "
                "pixel-for-pixel against the specs"
            ),
        },
        "asset_notes": {
            "player_1_lane_b_walk_down_f3": _idle_copy_note("down"),
            "player_1_lane_b_walk_right_f3": _idle_copy_note("right"),
        },
    },
    "calibration-v2": {
        "provenance": {
            "origin": "procedural",
            "author": "dev agent (pi session, sprint 2)",
            "created": "2026-08-17",
            "rights": "private-project",
            "method": (
                "authored as reviewable pixel-grid specs derived from the frozen "
                "calibration-v0 lane-B idle poses and measured against the frozen "
                "calibration-v1 walk frames (sources/calibration-v2/specs), built "
                "into native Aseprite sources via tools/aseprite_build.lua, exported "
                "deterministically via tools/export_assets.py and verified "
                "pixel-for-pixel against the specs"
            ),
        },
        "asset_notes": {
            "player_1_lane_b_attack_down_k0": (
                "attack-key tell pose: dome and eye rows copied byte-exact from the "
                "frozen calibration-v0 idle_down spec and rigidly lowered 2px; "
                "open-jaw accent recolor and braced 2px-wider stance carry the "
                "state; the lunge displacement is the pinned draw-only renderer "
                "offset, never pose pixels"
            ),
            "player_1_lane_b_attack_right_k0": (
                "attack-key tell pose: dome and eye rows copied byte-exact from the "
                "frozen calibration-v0 idle_right spec and rigidly lowered 3px; "
                "open-jaw accent recolor at the snout, crouched body, and forward "
                "foreleg carry the state; the lunge displacement is the pinned "
                "draw-only renderer offset, never pose pixels"
            ),
        },
    },
    "calibration-v3": {
        "provenance": {
            "origin": "procedural",
            "author": "dev agent (pi session, sprint 3)",
            "created": "2026-08-17",
            "rights": "private-project",
            "method": (
                "authored as reviewable pixel-grid specs derived from the frozen "
                "calibration-v0 lane-B idle poses and measured against the frozen "
                "calibration-v1 walk frames and calibration-v2 attack keys "
                "(sources/calibration-v3/specs), built into native Aseprite sources "
                "via tools/aseprite_build.lua, exported deterministically via "
                "tools/export_assets.py and verified pixel-for-pixel against the "
                "specs"
            ),
        },
        "asset_notes": {
            "player_1_lane_b_attack_down_a0": (
                "anticipation coil pose: head block (dome, eyes, and taper rows) "
                "copied byte-exact from the frozen calibration-v0 idle_down spec "
                "and rigidly translated (0,+4); haunch bulge widens the lower "
                "torso to 12 columns and the legs fold to a 3-row crouch at the "
                "idle columns; the jaw stays closed (the gape is the strike "
                "marker); the -3px windup displacement is the pinned draw-only "
                "renderer offset, never pose pixels"
            ),
            "player_1_lane_b_attack_right_a0": (
                "anticipation coil pose: dome and eye rows copied byte-exact from "
                "the frozen calibration-v0 idle_right spec and rigidly translated "
                "(-2,+3) - retracted back and down; body compressed to a low slab "
                "with a rear haunch ridge, the oss tail marker kept, and the legs "
                "gathered 1px inward and folded to a 3-row crouch; the snout stays "
                "closed (the gape is the strike marker); the -3px windup "
                "displacement is the pinned draw-only renderer offset, never pose "
                "pixels"
            ),
        },
    },
    "calibration-v5": {
        "provenance": {
            "origin": "procedural",
            "author": "dev agent (pi session, sprint 5)",
            "created": "2026-08-18",
            "rights": "private-project",
            "method": (
                "authored as reviewable pixel-grid specs derived from the frozen "
                "calibration-v0 lane-B idle poses and measured against the frozen "
                "calibration-v1 walk frames, calibration-v2 attack keys, and "
                "calibration-v3 anticipation coils (sources/calibration-v5/specs), "
                "built into native Aseprite sources via tools/aseprite_build.lua, "
                "exported deterministically via tools/export_assets.py and verified "
                "pixel-for-pixel against the specs"
            ),
        },
        "asset_notes": {
            "player_1_lane_b_attack_down_r0": (
                "follow-through settle pose: head block (dome, eyes, and taper "
                "rows) copied byte-exact from the frozen calibration-v0 idle_down "
                "spec and rigidly translated (+2,+3) - slumped down and off the "
                "strike axis (the lateral axis is virgin for down states); low "
                "13-14-wide slab sagged toward the shaded side with mass pooled "
                "at the base; legs asymmetric mid-return (left planted at the "
                "idle columns, right still at the k0 splay column); the jaw stays "
                "closed (the gape is the strike marker); recovery draws at the "
                "pinned offset 0 (renderer lunge_offset else-branch), never pose "
                "pixels"
            ),
            "player_1_lane_b_attack_right_r0": (
                "follow-through overshoot pose: dome and eye rows copied "
                "byte-exact from the frozen calibration-v0 idle_right spec and "
                "rigidly translated (+1,+4) - dipped forward and down (the +x "
                "head axis is virgin: the coil retracts -2, the strike and every "
                "walk hold the idle head columns); back line slopes toward the "
                "front, oss tail marker kept and raised 2 rows (weight tipped "
                "forward); legs carried 1px forward of idle (rear 11-13, front "
                "19-21, between the idle stance and the k0 reach); the snout "
                "stays closed (the gape is the strike marker); recovery draws at "
                "the pinned offset 0, never pose pixels"
            ),
        },
    },
}


class ReleaseError(RuntimeError):
    """Refuse to emit a manifest that would lie about provenance."""


def _git_env() -> dict[str, str]:
    """Child git env without hook-injected index/dir overrides.

    Pathspec commits export an absolute GIT_INDEX_FILE (and hooks may export
    GIT_DIR/GIT_WORK_TREE); any nested git run against another repository must
    scrub them or it operates on the parent's temporary index.
    """
    env = dict(os.environ)
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(key, None)
    return env


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True, capture_output=True, text=True, env=_git_env(),
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseError(f"git failed: {exc}") from exc


def source_commit(root: Path) -> str:
    """HEAD commit, required to have sources/ and tools/ committed clean."""
    head = _git(root, "rev-parse", "HEAD")
    dirty = _git(root, "status", "--porcelain", "--", "sources", "tools", "manifests")
    if dirty:
        raise ReleaseError(
            "sources/, tools/, or manifests/ differ from HEAD; commit them first:\n" + dirty
        )
    return head


def game_commit(root: Path) -> str:
    baseline = json.loads(
        (root / "manifests" / "runtime-baseline.json").read_text(encoding="utf-8")
    )
    return baseline["game_commit"]


def build_manifest(root: Path, commit: str, release_id: str) -> dict:
    if release_id not in RELEASES:
        known = ", ".join(sorted(RELEASES))
        raise ReleaseError(f"unknown release id {release_id!r}; registry has: {known}")
    release = RELEASES[release_id]
    spec_dir = root / "sources" / release_id / "specs"
    source_dir = root / "sources" / release_id
    export_dir = root / "exports" / release_id
    specs = load_spec_dir(spec_dir)

    source_files = []
    for spec in specs:
        spec_path = spec_dir / f"{spec.asset_id}.json"
        ase_path = source_dir / f"{spec.asset_id}.aseprite"
        if not ase_path.is_file():
            raise ReleaseError(f"missing native source {ase_path}")
        source_files.append(
            {"path": f"sources/{release_id}/specs/{spec.asset_id}.json",
             "sha256": sha256_file(spec_path)}
        )
        source_files.append(
            {"path": f"sources/{release_id}/{spec.asset_id}.aseprite",
             "sha256": sha256_file(ase_path)}
        )

    exports = []
    for spec in specs:
        png_path = export_dir / f"{spec.asset_id}.png"
        if not png_path.is_file():
            raise ReleaseError(f"missing export {png_path}")
        provenance = dict(release["provenance"])
        note = release["asset_notes"].get(spec.asset_id)
        if note:
            provenance["note"] = note
        exports.append(
            {
                "asset_id": spec.asset_id,
                "kind": "creature",
                "path": f"exports/{release_id}/{spec.asset_id}.png",
                "sha256": sha256_file(png_path),
                "width": 32,
                "height": 32,
                "anchor": [16, 30],
                "palette": list(spec.used_colors),
                "provenance": provenance,
            }
        )

    return {
        "contract_version": 1,
        "release_id": release_id,
        "source": {"commit": commit, "files": source_files},
        "target": {
            "game_commit": game_commit(root),
            "runtime_baseline": "manifests/runtime-baseline.json",
        },
        "toolchain": {
            "baseline": "manifests/toolchain-baseline.json",
            "exporter_path": EXPORTER,
            "exporter_sha256": sha256_file(root / EXPORTER),
        },
        "exports": exports,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--release", required=True, choices=sorted(RELEASES),
        help="release id from the provenance registry",
    )
    parser.add_argument("--commit", help="override source commit (tests only)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        commit = args.commit or source_commit(root)
        manifest = build_manifest(root, commit, args.release)
    except ReleaseError as exc:
        print(f"release refused: {exc}", file=sys.stderr)
        return 1
    out_path = root / "exports" / args.release / "release.json"
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
