#!/usr/bin/env python3
"""Validate game-two asset release manifests and native PNG exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from png_reader import PngError, PngInfo, inspect_png

ROOT = Path(__file__).resolve().parents[1]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
RELEASE_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
ASSET_ID_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPORT_KINDS = frozenset({"creature", "tile", "fx", "ui"})
ORIGIN_KINDS = frozenset({"human", "procedural", "ai_reconstruction"})
AI_PROVENANCE_FIELDS = (
    "provider",
    "model",
    "prompt",
    "seed",
    "terms_url",
    "terms_retrieved_at",
    "concept_path",
)


class AssetGateError(ValueError):
    """A deterministic asset-contract violation."""


def sha256_file(path: Path, *, normalize_lf: bool = False) -> str:
    data = path.read_bytes()
    if normalize_lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AssetGateError(f"cannot read JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AssetGateError("JSON root must be an object")
    return value


def _safe_path(root: Path, raw_path: Any, required_prefix: str) -> Path:
    if not isinstance(raw_path, str) or "\\" in raw_path:
        raise AssetGateError("path must be a forward-slash relative string")
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise AssetGateError("path must stay inside the repository")
    if relative.parts[0] != required_prefix:
        raise AssetGateError(f"path must be under {required_prefix}/")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise AssetGateError("path escapes the repository")
    return resolved


def _as_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{label} must be an object")
    return {}


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _valid_commit(value: Any) -> bool:
    return isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None


def _required_provenance_errors(provenance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("author", "created", "rights"):
        value = provenance.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"provenance.{key} must be a non-empty string")
    return errors


def _ai_provenance_errors(provenance: dict[str, Any]) -> list[str]:
    missing = [key for key in AI_PROVENANCE_FIELDS if provenance.get(key) in (None, "")]
    return [f"AI reconstruction requires provenance.{key}" for key in missing]


def _validate_provenance(provenance: Any) -> list[str]:
    if not isinstance(provenance, dict):
        return ["provenance must be an object"]
    errors = _required_provenance_errors(provenance)
    origin = provenance.get("origin")
    if origin not in ORIGIN_KINDS:
        errors.append("provenance.origin must be human, procedural, or ai_reconstruction")
    created = provenance.get("created")
    if isinstance(created, str) and DATE_RE.fullmatch(created) is None:
        errors.append("provenance.created must use YYYY-MM-DD")
    if origin == "ai_reconstruction":
        errors.extend(_ai_provenance_errors(provenance))
    return errors


def _validate_release_header(manifest: dict[str, Any], errors: list[str]) -> str:
    if manifest.get("contract_version") != 1:
        errors.append("contract_version must be 1")
    release_id = manifest.get("release_id")
    if isinstance(release_id, str) and RELEASE_RE.fullmatch(release_id):
        return release_id
    errors.append("release_id must use lowercase generic words, digits, '-' or '_'")
    return "invalid"


def _validate_source_entry(
    entry: Any, index: int, root: Path, errors: list[str]
) -> None:
    label = f"source.files[{index}]"
    source = _as_object(entry, label, errors)
    if not source:
        return
    digest = source.get("sha256")
    if not _valid_sha256(digest):
        errors.append(f"{label}.sha256 must be lowercase SHA-256")
    try:
        path = _safe_path(root, source.get("path"), "sources")
    except AssetGateError as exc:
        errors.append(f"{label}.path: {exc}")
        return
    if not path.is_file():
        errors.append(f"{label}.path does not exist")
    elif digest != sha256_file(path):
        errors.append(f"{label}.sha256 does not match the source file")


def _validate_source(manifest: dict[str, Any], root: Path, errors: list[str]) -> None:
    source = _as_object(manifest.get("source"), "source", errors)
    if not _valid_commit(source.get("commit")):
        errors.append("source.commit must be a full lowercase 40-hex Git commit")
    source_files = source.get("files")
    if not isinstance(source_files, list) or not source_files:
        errors.append("source.files must contain at least one source file")
        return
    for index, entry in enumerate(source_files):
        _validate_source_entry(entry, index, root, errors)


def _validate_target(manifest: dict[str, Any], errors: list[str]) -> None:
    target = _as_object(manifest.get("target"), "target", errors)
    if not _valid_commit(target.get("game_commit")):
        errors.append("target.game_commit must be a full lowercase 40-hex Git commit")
    if target.get("runtime_baseline") != "manifests/runtime-baseline.json":
        errors.append("target.runtime_baseline must name manifests/runtime-baseline.json")


def _validate_toolchain(
    manifest: dict[str, Any], root: Path, errors: list[str]
) -> None:
    toolchain = _as_object(manifest.get("toolchain"), "toolchain", errors)
    if toolchain.get("baseline") != "manifests/toolchain-baseline.json":
        errors.append("toolchain.baseline must name manifests/toolchain-baseline.json")
    digest = toolchain.get("exporter_sha256")
    if not _valid_sha256(digest):
        errors.append("toolchain.exporter_sha256 must be lowercase SHA-256")
    try:
        path = _safe_path(root, toolchain.get("exporter_path"), "tools")
    except AssetGateError as exc:
        errors.append(f"toolchain.exporter_path: {exc}")
        return
    if not path.is_file():
        errors.append("toolchain.exporter_path does not exist")
    elif digest != sha256_file(path):
        errors.append("toolchain.exporter_sha256 does not match the exporter")


def _validate_asset_id(
    entry: dict[str, Any], label: str, seen_ids: set[str], errors: list[str]
) -> str:
    asset_id = entry.get("asset_id")
    if not isinstance(asset_id, str) or ASSET_ID_RE.fullmatch(asset_id) is None:
        errors.append(f"{label}.asset_id must be lowercase generic snake_case")
        return "invalid"
    if asset_id in seen_ids:
        errors.append(f"{label}.asset_id is duplicated")
    seen_ids.add(asset_id)
    return asset_id


def _validate_export_path(
    entry: dict[str, Any],
    label: str,
    release_id: str,
    asset_id: str,
    seen_paths: set[str],
    errors: list[str],
) -> Any:
    raw_path = entry.get("path")
    expected = f"exports/{release_id}/{asset_id}.png"
    if raw_path != expected:
        errors.append(f"{label}.path must be {expected}")
    if isinstance(raw_path, str):
        if raw_path in seen_paths:
            errors.append(f"{label}.path is duplicated")
        seen_paths.add(raw_path)
    return raw_path


def _validate_export_shape(
    entry: dict[str, Any], label: str, errors: list[str]
) -> tuple[Any, Any, Any]:
    kind = entry.get("kind")
    width = entry.get("width")
    height = entry.get("height")
    if kind not in EXPORT_KINDS:
        errors.append(f"{label}.kind must be creature, tile, fx, or ui")
    if not isinstance(width, int) or not isinstance(height, int):
        errors.append(f"{label}.width and height must be integers")
    if kind in {"creature", "tile"} and (width, height) != (32, 32):
        errors.append(f"{label} {kind} exports must be 32x32")
    if kind == "creature" and entry.get("anchor") != [16, 30]:
        errors.append(f"{label}.anchor must be [16, 30]")
    return kind, width, height


def _validate_palette(entry: dict[str, Any], label: str, errors: list[str]) -> set[str]:
    palette = entry.get("palette")
    if not isinstance(palette, list) or not 1 <= len(palette) <= 8:
        errors.append(f"{label}.palette must contain 1-8 declared colors")
        return set()
    palette_set = set(palette)
    valid_colors = all(
        isinstance(color, str) and COLOR_RE.fullmatch(color) is not None for color in palette
    )
    if len(palette_set) != len(palette) or not valid_colors:
        errors.append(f"{label}.palette colors must be unique lowercase #rrggbb")
    return palette_set


def _validate_creature_info(info: PngInfo, label: str, errors: list[str]) -> None:
    if info.bbox is None:
        errors.append(f"{label} creature cannot be fully transparent")
        return
    left, top, right, bottom = info.bbox
    if not (2 <= left <= right <= 29 and 2 <= top <= bottom <= 29):
        errors.append(f"{label} creature bbox {info.bbox} exceeds [2, 2, 29, 29]")


def _validate_png_info(
    info: PngInfo,
    label: str,
    kind: Any,
    width: Any,
    height: Any,
    palette: set[str],
    errors: list[str],
) -> None:
    if (info.width, info.height) != (width, height):
        errors.append(f"{label} PNG is {info.width}x{info.height}, not {width}x{height}")
    if not info.alpha_values.issubset({0, 255}):
        errors.append(f"{label} PNG alpha must be binary (0 or 255)")
    undeclared = info.opaque_colors - palette
    if undeclared:
        errors.append(f"{label} PNG uses undeclared colors: {sorted(undeclared)}")
    if kind == "creature":
        _validate_creature_info(info, label, errors)


def _validate_export_file(
    entry: dict[str, Any],
    label: str,
    root: Path,
    raw_path: Any,
    shape: tuple[Any, Any, Any],
    palette: set[str],
    errors: list[str],
) -> None:
    digest = entry.get("sha256")
    if not _valid_sha256(digest):
        errors.append(f"{label}.sha256 must be lowercase SHA-256")
    try:
        path = _safe_path(root, raw_path, "exports")
    except AssetGateError as exc:
        errors.append(f"{label}.path: {exc}")
        return
    if not path.is_file():
        errors.append(f"{label}.path does not exist")
        return
    if digest != sha256_file(path):
        errors.append(f"{label}.sha256 does not match the export")
    try:
        info = inspect_png(path)
    except (PngError, OSError) as exc:
        errors.append(f"{label}.path: {exc}")
        return
    _validate_png_info(info, label, *shape, palette, errors)


def _validate_export_entry(
    entry: Any,
    index: int,
    root: Path,
    release_id: str,
    seen_ids: set[str],
    seen_paths: set[str],
    errors: list[str],
) -> None:
    label = f"exports[{index}]"
    export = _as_object(entry, label, errors)
    if not export:
        return
    asset_id = _validate_asset_id(export, label, seen_ids, errors)
    raw_path = _validate_export_path(
        export, label, release_id, asset_id, seen_paths, errors
    )
    shape = _validate_export_shape(export, label, errors)
    palette = _validate_palette(export, label, errors)
    errors.extend(f"{label}.{error}" for error in _validate_provenance(export.get("provenance")))
    _validate_export_file(export, label, root, raw_path, shape, palette, errors)


def _validate_exports(
    manifest: dict[str, Any], root: Path, release_id: str, errors: list[str]
) -> None:
    exports = manifest.get("exports")
    if not isinstance(exports, list) or not exports:
        errors.append("exports must contain at least one asset")
        return
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, entry in enumerate(exports):
        _validate_export_entry(
            entry, index, root, release_id, seen_ids, seen_paths, errors
        )


def validate_release(manifest_path: Path, root: Path = ROOT) -> list[str]:
    try:
        manifest = _load_json(manifest_path)
    except AssetGateError as exc:
        return [f"{manifest_path}: {exc}"]
    errors: list[str] = []
    release_id = _validate_release_header(manifest, errors)
    _validate_source(manifest, root, errors)
    _validate_target(manifest, errors)
    _validate_toolchain(manifest, root, errors)
    _validate_exports(manifest, root, release_id, errors)
    return [f"{manifest_path}: {error}" for error in errors]


def _validate_baseline_shape(baseline: dict[str, Any], errors: list[str]) -> None:
    if baseline.get("contract_version") != 1:
        errors.append("contract_version must be 1")
    if not _valid_commit(baseline.get("game_commit")):
        errors.append("game_commit must be a full lowercase 40-hex Git commit")
    grid = baseline.get("grid")
    valid_grid = isinstance(grid, dict) and (
        grid.get("tile_width"), grid.get("tile_height")
    ) == (32, 32)
    if not valid_grid:
        errors.append("grid must preserve the 32x32 runtime tile contract")
    colors = baseline.get("role_colors")
    valid_colors = isinstance(colors, dict) and all(
        isinstance(value, str) and COLOR_RE.fullmatch(value) is not None
        for value in colors.values()
    )
    if not valid_colors:
        errors.append("role_colors must contain lowercase #rrggbb values")


def _game_head(game_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(game_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AssetGateError(f"cannot read game Git commit: {exc}") from exc


def _validate_game_source(
    entry: Any, index: int, game_root: Path, errors: list[str]
) -> None:
    label = f"source_files[{index}]"
    source = _as_object(entry, label, errors)
    if not source:
        return
    path = game_root / str(source.get("path", ""))
    if not path.is_file():
        errors.append(f"{label}.path does not exist in game-two")
    elif source.get("sha256_lf") != sha256_file(path, normalize_lf=True):
        errors.append(f"{label}.sha256_lf does not match game-two")


def _validate_game_baseline(
    baseline: dict[str, Any], game_root: Path, errors: list[str]
) -> None:
    try:
        actual_commit = _game_head(game_root)
    except AssetGateError as exc:
        errors.append(str(exc))
    else:
        if actual_commit != baseline.get("game_commit"):
            errors.append(
                f"game HEAD is {actual_commit}; baseline pins {baseline.get('game_commit')}"
            )
    source_files = baseline.get("source_files")
    if not isinstance(source_files, list):
        errors.append("source_files must be a list")
        return
    for index, entry in enumerate(source_files):
        _validate_game_source(entry, index, game_root, errors)


def validate_runtime_baseline(root: Path = ROOT, game_root: Path | None = None) -> list[str]:
    baseline_path = root / "manifests" / "runtime-baseline.json"
    try:
        baseline = _load_json(baseline_path)
    except AssetGateError as exc:
        return [f"{baseline_path}: {exc}"]
    errors: list[str] = []
    _validate_baseline_shape(baseline, errors)
    if game_root is not None:
        _validate_game_baseline(baseline, game_root, errors)
    return [f"{baseline_path}: {error}" for error in errors]


def _aseprite_version(executable: Path) -> str:
    try:
        return subprocess.run(
            [str(executable), "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AssetGateError(f"cannot execute Aseprite: {exc}") from exc


def _validate_toolchain_shape(
    baseline: dict[str, Any], errors: list[str]
) -> tuple[Any, Any]:
    if baseline.get("contract_version") != 1:
        errors.append("contract_version must be 1")
    aseprite = _as_object(baseline.get("aseprite"), "aseprite", errors)
    expected_hash = aseprite.get("executable_sha256")
    expected_version = aseprite.get("version_output")
    if not _valid_sha256(expected_hash):
        errors.append("aseprite.executable_sha256 must be lowercase SHA-256")
    if not isinstance(expected_version, str) or not expected_version:
        errors.append("aseprite.version_output must be a non-empty string")
    return expected_hash, expected_version


def _validate_aseprite_executable(
    executable: Path, expected_hash: Any, expected_version: Any, errors: list[str]
) -> None:
    if not executable.is_file():
        errors.append("Aseprite executable does not exist")
        return
    if sha256_file(executable) != expected_hash:
        errors.append("Aseprite executable hash does not match the toolchain pin")
    try:
        actual_version = _aseprite_version(executable)
    except AssetGateError as exc:
        errors.append(str(exc))
        return
    if actual_version != expected_version:
        errors.append(f"Aseprite version is {actual_version!r}; expected {expected_version!r}")


def validate_toolchain_baseline(
    root: Path = ROOT, aseprite_path: Path | None = None
) -> list[str]:
    baseline_path = root / "manifests" / "toolchain-baseline.json"
    try:
        baseline = _load_json(baseline_path)
    except AssetGateError as exc:
        return [f"{baseline_path}: {exc}"]
    errors: list[str] = []
    expected_hash, expected_version = _validate_toolchain_shape(baseline, errors)
    if aseprite_path is not None:
        _validate_aseprite_executable(
            aseprite_path, expected_hash, expected_version, errors
        )
    return [f"{baseline_path}: {error}" for error in errors]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="asset repository root")
    parser.add_argument(
        "--manifest",
        action="append",
        type=Path,
        help="release manifest to validate; defaults to exports/**/release.json",
    )
    parser.add_argument(
        "--game-root",
        type=Path,
        help="also verify the pinned runtime baseline against this game-two checkout",
    )
    parser.add_argument(
        "--aseprite",
        type=Path,
        help="also verify this Aseprite executable against the pinned toolchain",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    manifests = args.manifest or sorted(root.glob("exports/**/release.json"))
    errors = validate_runtime_baseline(root, args.game_root)
    errors.extend(validate_toolchain_baseline(root, args.aseprite))
    for manifest in manifests:
        errors.extend(validate_release(manifest.resolve(), root))
    if not errors:
        return 0
    print(f"Asset gate failed with {len(errors)} violation(s):", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
