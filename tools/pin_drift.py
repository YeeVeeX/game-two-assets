#!/usr/bin/env python3
"""Read-only pin-drift verifier: the re-pin protocol's MECHANICAL half.

v17 measured the cadence live: game-two's held seat lands ~3
commits/hour, three pinned-file hops routed in one session, the
14-constant re-verify lived in a throwaway temp script, and a
json.dumps array-explosion trap was hit on the manifest. This tool
banks that mechanical half permanently so every future hop costs
minutes and zero re-derivation.

What it computes, all read-only (``git rev-parse``/``show``/``diff``
against the game checkout; it writes NOTHING anywhere — proven by a
byte-hash fixture test):

1. Per pinned file (``manifests/runtime-baseline.json`` source_files):
   blob identity at the old pin vs the new commit; for drifted files
   the ``--numstat`` +/- counts and the recomputed ``sha256_lf`` over
   LF-normalized COMMITTED bytes (the manifest's cross-platform law).
2. The derived-constant battery: every needle is built AT CALL TIME
   from ``manifests/render-reference.json`` values (the guard's
   derive-don't-duplicate law — zero pinned values hardcoded here) and
   checked against the renderer/creature blobs at the NEW commit.
   Verified on every run: identical blobs double as a continuous
   needle self-test. Zone-palette JSONs carry no needle battery; their
   drift routes by diff class alone.
3. attack_timing ALWAYS re-verified at the new commit — its source
   (``data/balance/combat.json``) is commit-anchored, NOT in the pin
   set, so it can move while all five pinned blobs stay identical.
4. Exact old/new manifest line pairs (the literal baseline lines) for
   the session to apply via the edit tool as SURGICAL replacements —
   never a re-serialization.
5. ONE routing line per the pre-registered decidable-class table
   (``reviews/maturity-v18/rationale.md``, protocol B):

   - all pinned blobs identical + attack_timing green
     -> ``mechanical re-pin`` (game_commit line only);
   - every drifted file additive-only (numstat deletions == 0: git's
     line-diff model counts an in-place mutation as +1/-1, so zero
     deletions mechanically guarantees pure appends/insertions) + all
     constants green + attack_timing green
     -> ``approve-by-default candidate`` — the session applies the
     protocol; the tool decides nothing, and the route line carries the
     session's REMAINING duties (read the diff, apply the pairs, commit
     the re-pin alone, mail the note) so the candidate class never
     reads as pre-vetted (council adoption, v18 gate);
   - ANY deletion, ANY constant/attack_timing failure, or any other
     surprise -> ``SESSION JUDGMENT REQUIRED`` + the quoted clause.

The quoted clause (owner-extended protocol, project MEMORY 2026-08-21):
"semantic-preserving refactors + additive features in a pinned file
that move NO render-reference.json constant join the approve-by-default
class - only draw-value moves or true removals still stop for owner
review." Deletions are NOT mechanically decidable as
removals-vs-refactors; that hop is exactly the session's judgment, and
this tool never attempts it. It never prints "approved".

Exit codes: 0 = analysis complete (WHATEVER the route — this is an
advisor, never a gate; it is never wired into hooks); 2 = analysis
failure (bad args, git failure, malformed baseline/reference). Never
exit 1: nothing may mistake it for a pass/fail gate. Deliberately
UNPINNED (v17 verdict: maintenance tools are test-carried, not
hash-carried).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
DEFAULT_GAME_ROOT = ROOT.parent / "game-two"
DEFAULT_BASELINE = ROOT / "manifests" / "runtime-baseline.json"
DEFAULT_REFERENCE = ROOT / "manifests" / "render-reference.json"

PROTOCOL_CLAUSE = (
    '"semantic-preserving refactors + additive features in a pinned file '
    "that move NO render-reference.json constant join the approve-by-default "
    "class - only draw-value moves or true removals still stop for owner "
    'review." (owner-extended re-pin protocol, project MEMORY 2026-08-21)'
)

ROUTE_NONE = "ROUTE: no re-pin due (the new commit IS the pinned commit)"
ROUTE_MECHANICAL = (
    "ROUTE: mechanical re-pin (identity drift only; all pinned blobs "
    "byte-identical; game_commit line is the only manifest edit)"
)
ROUTE_CANDIDATE = (
    "ROUTE: approve-by-default candidate (additive-only + constants green + "
    "attack_timing green) - the session applies the protocol; this tool "
    "decides nothing. Session duties remain: read the diff, apply the "
    "manifest pairs via the edit tool, commit the re-pin ALONE, mail the "
    "dev-seat note"
)
ROUTE_JUDGMENT = "ROUTE: SESSION JUDGMENT REQUIRED: "


class PinDriftError(RuntimeError):
    """A deterministic analysis failure (bad input, git failure)."""


@dataclass(frozen=True)
class ConstantCheck:
    name: str
    file_role: str  # "renderer" | "creature"
    kind: str  # "substring" | "regex"
    pattern: str


def _git_env() -> dict[str, str]:
    """Scrub hook-injected git overrides (the banked repo pattern)."""
    env = dict(os.environ)
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(key, None)
    return env


def _git_text(game_root: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(game_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_git_env(),
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PinDriftError(f"git {' '.join(arguments)} failed: {exc}") from exc


def _git_bytes(game_root: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(game_root), *arguments],
            check=True,
            capture_output=True,
            env=_git_env(),
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PinDriftError(f"git {' '.join(arguments)} failed: {exc}") from exc


def _blob_id(game_root: Path, commit: str, path: str) -> str:
    return _git_text(game_root, "rev-parse", f"{commit}:{path}").strip()


def sha256_lf(blob: bytes) -> str:
    """LF-normalized SHA-256 (the manifest's cross-platform hash law)."""
    return hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PinDriftError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PinDriftError(f"{path}: JSON root must be an object")
    return value


def _gosu_color(alpha: int, rgb: list[int]) -> str:
    r, g, b = rgb
    return f"Gosu::Color.new({alpha}, {r}, {g}, {b})"


def derive_constant_checks(reference: dict[str, Any]) -> list[ConstantCheck]:
    """Build every needle from render-reference.json values at call
    time. A missing path is a typed analysis failure, never a silent
    skip."""
    try:
        pb = reference["primitive_body"]
        tg = reference["telegraph"]
        ring = reference["possession_ring"]
        fs = reference["feedback_states"]
        hurt = fs["hurt_flash"]
        dim = fs["ally_dim"]
        lunge = fs["lunge_offset"]
        swell = fs["telegraph_swell"]
        checks = [
            ConstantCheck(
                "body_striker", "renderer", "substring",
                _gosu_color(255, pb["body_rgb"]),
            ),
            ConstantCheck(
                "body_human", "renderer", "substring",
                _gosu_color(255, tg["body_rgb"]),
            ),
            ConstantCheck(
                "hurt_pack", "renderer", "substring",
                _gosu_color(255, hurt["pack_rgb"]),
            ),
            ConstantCheck(
                "hurt_human", "renderer", "substring",
                _gosu_color(255, hurt["human_rgb"]),
            ),
            ConstantCheck(
                "hurt_flicker_period", "renderer", "substring",
                f"(world.frame / {hurt['flicker_period_frames']}).even?",
            ),
            ConstantCheck(
                "ally_dim", "renderer", "substring",
                _gosu_color(dim["alpha"], dim["rgb"]),
            ),
            ConstantCheck(
                "telegraph_edge", "renderer", "substring",
                _gosu_color(255, tg["edge_rgb"]),
            ),
            ConstantCheck(
                "telegraph_core", "renderer", "substring",
                _gosu_color(255, tg["core_rgb"]),
            ),
            ConstantCheck(
                "telegraph_swell", "renderer", "regex",
                rf"(?m)^\s*swell = {swell['swell_px']}$",
            ),
            ConstantCheck(
                "telegraph_edge_rect", "renderer", "substring",
                "x - swell / 2, y - swell / 2, SIZE + swell, SIZE + swell, "
                "TELEGRAPH_EDGE",
            ),
            ConstantCheck(
                "telegraph_core_rect", "renderer", "substring",
                f"x - {swell['core_expand_px']}, y - {swell['core_expand_px']}, "
                f"SIZE + {2 * swell['core_expand_px']}, "
                f"SIZE + {2 * swell['core_expand_px']}, TELEGRAPH_CORE",
            ),
            ConstantCheck(
                "telegraph_inner_inset_rect", "renderer", "substring",
                f"x + {swell['inner_body_inset_px']}, "
                f"y + {swell['inner_body_inset_px']}, "
                f"SIZE - {2 * swell['inner_body_inset_px']}, "
                f"SIZE - {2 * swell['inner_body_inset_px']}, HUMAN_BODY",
            ),
            ConstantCheck(
                "ring_color", "renderer", "substring",
                _gosu_color(255, ring["rgb"]),
            ),
            ConstantCheck(
                "ring_expand_rect", "renderer", "substring",
                f"x - {ring['expand']}, y - {ring['expand']}, "
                f"SIZE + {2 * ring['expand']}, SIZE + {2 * ring['expand']}, "
                "POSSESSED_RING",
            ),
            ConstantCheck(
                "notch_color", "renderer", "substring",
                _gosu_color(255, pb["notch_rgb"]),
            ),
            ConstantCheck(
                "notch_size", "renderer", "regex",
                rf"(?m)^\s*n = {pb['notch_size']}$",
            ),
            ConstantCheck(
                "lunge_windup", "renderer", "substring",
                f"when :windup then [{lunge['windup_px']} * fx, "
                f"{lunge['windup_px']} * fy]",
            ),
            ConstantCheck(
                "lunge_active", "renderer", "substring",
                f"when :active then [{lunge['active_px']} * fx, "
                f"{lunge['active_px']} * fy]",
            ),
            ConstantCheck(
                "creature_size", "creature", "regex",
                rf"(?m)^\s*SIZE = {pb['size']}$",
            ),
        ]
    except (KeyError, TypeError, IndexError, ValueError) as exc:
        raise PinDriftError(f"reference-missing: {exc!r}") from exc
    return checks


def check_swell_consistency(reference: dict[str, Any]) -> bool:
    """JSON-internal law: edge_expand_px * 2 == swell_px."""
    try:
        swell = reference["feedback_states"]["telegraph_swell"]
        return swell["edge_expand_px"] * 2 == swell["swell_px"]
    except (KeyError, TypeError) as exc:
        raise PinDriftError(f"reference-missing: {exc!r}") from exc


def _constant_ok(check: ConstantCheck, blob_text: str) -> bool:
    if check.kind == "regex":
        return re.search(check.pattern, blob_text) is not None
    return check.pattern in blob_text


def _role_paths(source_files: list[dict[str, Any]]) -> dict[str, str]:
    """Map renderer/creature roles to pinned paths by basename."""
    roles: dict[str, str] = {}
    for entry in source_files:
        name = Path(str(entry.get("path", ""))).name
        if name == "renderer.rb":
            roles["renderer"] = str(entry["path"])
        elif name == "creature.rb":
            roles["creature"] = str(entry["path"])
    if "renderer" not in roles or "creature" not in roles:
        raise PinDriftError(
            "baseline source_files must pin renderer.rb and creature.rb"
        )
    return roles


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    current = document
    for part in pointer.strip("/").split("/"):
        try:
            current = current[part]
        except (KeyError, TypeError) as exc:
            raise PinDriftError(f"json-pointer missing: {pointer}") from exc
    return current


def _numstat(
    game_root: Path, old: str, new: str, path: str
) -> tuple[int | None, int | None]:
    out = _git_text(game_root, "diff", "--numstat", old, new, "--", path).strip()
    if not out:
        return (0, 0)
    added_raw, deleted_raw, *_ = out.split("\t")
    added = int(added_raw) if added_raw.isdigit() else None
    deleted = int(deleted_raw) if deleted_raw.isdigit() else None
    return (added, deleted)


def analyze(
    game_root: Path,
    baseline_path: Path,
    reference_path: Path,
    new_commit: str | None = None,
) -> dict[str, Any]:
    """Full read-only drift analysis; returns the report dict."""
    baseline = _load_json(baseline_path)
    reference = _load_json(reference_path)
    old_commit = str(baseline.get("game_commit", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", old_commit):
        raise PinDriftError("baseline game_commit must be 40-hex")
    source_files = baseline.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        raise PinDriftError("baseline source_files must be a non-empty list")
    if new_commit is None:
        new_commit = _git_text(game_root, "rev-parse", "HEAD").strip()
    else:
        new_commit = _git_text(game_root, "rev-parse", new_commit).strip()

    files: list[dict[str, Any]] = []
    for entry in source_files:
        path = str(entry.get("path", ""))
        old_blob = _blob_id(game_root, old_commit, path)
        new_blob = _blob_id(game_root, new_commit, path)
        record: dict[str, Any] = {
            "path": path,
            "pinned_sha256_lf": entry.get("sha256_lf"),
            "identical": old_blob == new_blob,
        }
        if old_blob != new_blob:
            added, deleted = _numstat(game_root, old_commit, new_commit, path)
            record["added"] = added
            record["deleted"] = deleted
            record["additive_only"] = deleted == 0 and added is not None
            record["new_sha256_lf"] = sha256_lf(
                _git_bytes(game_root, "show", f"{new_commit}:{path}")
            )
        files.append(record)

    roles = _role_paths(source_files)
    blob_cache = {
        role: _git_bytes(game_root, "show", f"{new_commit}:{path}").decode(
            "utf-8", errors="replace"
        )
        for role, path in roles.items()
    }
    constant_results = [
        {
            "name": check.name,
            "file": roles[check.file_role],
            "ok": _constant_ok(check, blob_cache[check.file_role]),
        }
        for check in derive_constant_checks(reference)
    ]
    constant_results.append(
        {
            "name": "swell_edge_consistency",
            "file": str(reference_path),
            "ok": check_swell_consistency(reference),
        }
    )

    timing = reference.get("attack_timing", {})
    timing_file = str(timing.get("source_file", ""))
    if not timing_file:
        raise PinDriftError("reference attack_timing.source_file missing")
    timing_doc = json.loads(
        _git_bytes(game_root, "show", f"{new_commit}:{timing_file}").decode(
            "utf-8", errors="replace"
        )
    )
    timing_results = []
    for name, spec in timing.get("values", {}).items():
        actual = _resolve_json_pointer(timing_doc, str(spec["json_pointer"]))
        timing_results.append(
            {
                "name": name,
                "pointer": str(spec["json_pointer"]),
                "expected": spec["value"],
                "actual": actual,
                "ok": actual == spec["value"],
            }
        )

    drifted = [record for record in files if not record["identical"]]
    constants_green = all(result["ok"] for result in constant_results)
    timing_green = all(result["ok"] for result in timing_results)
    judgment_reasons: list[str] = []
    if not constants_green:
        judgment_reasons.append("derived-constant check failed")
    if not timing_green:
        judgment_reasons.append("attack_timing value moved")
    for record in drifted:
        if not record.get("additive_only"):
            judgment_reasons.append(
                f"non-additive diff in pinned file {record['path']} "
                f"(+{record.get('added')}/-{record.get('deleted')})"
            )
    if new_commit == old_commit and not judgment_reasons:
        route = ROUTE_NONE
    elif judgment_reasons:
        route = (
            ROUTE_JUDGMENT
            + "; ".join(judgment_reasons)
            + " - the protocol clause governs: "
            + PROTOCOL_CLAUSE
        )
    elif not drifted:
        route = ROUTE_MECHANICAL
    else:
        route = ROUTE_CANDIDATE

    return {
        "old_commit": old_commit,
        "new_commit": new_commit,
        "files": files,
        "constants": constant_results,
        "attack_timing": timing_results,
        "route": route,
    }


def manifest_line_pairs(
    baseline_text: str, analysis: dict[str, Any]
) -> list[tuple[str, str]]:
    """Exact (old line, new line) pairs as they appear in the baseline
    text — surgical edit-tool replacements; this tool applies none."""
    pairs: list[tuple[str, str]] = []
    if analysis["new_commit"] != analysis["old_commit"]:
        for line in baseline_text.splitlines():
            if analysis["old_commit"] in line:
                pairs.append(
                    (line, line.replace(analysis["old_commit"], analysis["new_commit"]))
                )
    for record in analysis["files"]:
        if record["identical"] or "new_sha256_lf" not in record:
            continue
        pinned = str(record["pinned_sha256_lf"])
        for line in baseline_text.splitlines():
            if pinned in line:
                pairs.append((line, line.replace(pinned, record["new_sha256_lf"])))
    return pairs


def render_report(analysis: dict[str, Any], baseline_text: str) -> str:
    lines = [
        "pin-drift report (read-only; this tool writes nothing)",
        f"  pinned commit : {analysis['old_commit']}",
        f"  new commit    : {analysis['new_commit']}",
    ]
    for record in analysis["files"]:
        if record["identical"]:
            lines.append(f"  [identical] {record['path']}")
        else:
            shape = f"+{record.get('added')}/-{record.get('deleted')}"
            klass = (
                "additive-only"
                if record.get("additive_only")
                else "NOT additive-only"
            )
            lines.append(f"  [drifted]   {record['path']}  {shape}  {klass}")
            lines.append(f"              new sha256_lf: {record['new_sha256_lf']}")
    failed_constants = [c for c in analysis["constants"] if not c["ok"]]
    total = len(analysis["constants"])
    if failed_constants:
        for constant in failed_constants:
            lines.append(
                f"  FAIL constant {constant['name']}: pattern not found in "
                f"{constant['file']}@{analysis['new_commit'][:12]}"
            )
        lines.append(
            f"constants (derived from render-reference.json): "
            f"{total - len(failed_constants)}/{total} OK"
        )
    else:
        lines.append(
            f"constants (derived from render-reference.json): {total}/{total} "
            f"OK at {analysis['new_commit'][:12]}"
        )
    timing_bits = []
    for result in analysis["attack_timing"]:
        mark = "OK" if result["ok"] else f"FAIL (now {result['actual']})"
        timing_bits.append(f"{result['name']}={result['expected']} {mark}")
    lines.append("attack_timing: " + ", ".join(timing_bits))
    pairs = manifest_line_pairs(baseline_text, analysis)
    if pairs:
        lines.append(
            "manifest line pairs (surgical edit-tool replacements; never "
            "re-serialize the manifest):"
        )
        for old_line, new_line in pairs:
            lines.append(f"  OLD |{old_line}")
            lines.append(f"  NEW |{new_line}")
    lines.append(analysis["route"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only pin-drift verifier (the re-pin protocol's mechanical "
            "half); advisor only, never a gate, writes nothing."
        )
    )
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument(
        "--new-commit",
        default=None,
        help="candidate commit (default: the game root's HEAD)",
    )
    args = parser.parse_args(argv)
    try:
        analysis = analyze(
            args.game_root, args.baseline, args.reference, args.new_commit
        )
        baseline_text = args.baseline.read_text(encoding="utf-8")
    except (PinDriftError, OSError, json.JSONDecodeError) as exc:
        print(f"pin-drift ANALYSIS FAILURE: {exc}")
        return 2
    print(render_report(analysis, baseline_text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
