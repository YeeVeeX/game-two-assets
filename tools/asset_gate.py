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

from audio_metrics import WavError, read_wav
from png_reader import PngError, PngInfo, inspect_png

ROOT = Path(__file__).resolve().parents[1]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MD5_RE = re.compile(r"^[0-9a-f]{32}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
RELEASE_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
ASSET_ID_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPORT_KINDS = frozenset({"creature", "tile", "fx", "ui"})
ORIGIN_KINDS = frozenset({"human", "procedural", "ai_reconstruction"})
AUDIO_RATE_HZ = 48000
AUDIO_BAR_FRAMES = 96000  # one bar at 120 bpm 4/4 @ 48 kHz (handoff bar-exact law)
AUDIO_FORMAT = {
    "container": "wav",
    "codec": "pcm_s16le",
    "sample_rate_hz": AUDIO_RATE_HZ,
    "channels": 1,
    "bit_depth": 16,
}
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
    if export.get("kind") == "audio":
        _validate_audio_export_entry(
            export, label, root, release_id, seen_ids, seen_paths, errors
        )
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


# --- audio releases (additive kind; docs/asset-contract.md "Audio contract v1") ---


def _validate_audio_shape(entry: dict[str, Any], label: str, errors: list[str]) -> None:
    """Format facts, frame count, duration consistency, bar-exact stems."""
    if entry.get("format") != AUDIO_FORMAT:
        errors.append(f"{label}.format must be exactly {json.dumps(AUDIO_FORMAT, sort_keys=True)}")
    frames = entry.get("frames")
    if not isinstance(frames, int) or frames <= 0:
        errors.append(f"{label}.frames must be a positive integer")
        return
    dur_s = entry.get("dur_s")
    if not isinstance(dur_s, (int, float)) or abs(dur_s * AUDIO_RATE_HZ - frames) > 1e-6:
        errors.append(f"{label}.dur_s must equal frames/{AUDIO_RATE_HZ}")
    asset_id = entry.get("asset_id")
    if isinstance(asset_id, str) and asset_id.startswith("mstem_"):
        if frames % AUDIO_BAR_FRAMES:
            errors.append(
                f"{label} music stem must be bar-exact (frames % {AUDIO_BAR_FRAMES} == 0)"
            )


def _validate_audio_loudness(entry: dict[str, Any], label: str, errors: list[str]) -> None:
    """Report-only loudness fields must exist and be typed; no gain law here."""
    loudness = entry.get("loudness")
    if not isinstance(loudness, dict):
        errors.append(f"{label}.loudness must be an object")
        return
    peak = loudness.get("sample_peak_dbfs")
    if not isinstance(peak, (int, float)) or peak > 0:
        errors.append(f"{label}.loudness.sample_peak_dbfs must be a number <= 0")
    lufs = loudness.get("lufs_integrated")
    if lufs is not None and not isinstance(lufs, (int, float)):
        errors.append(f"{label}.loudness.lufs_integrated must be a number or null")


def _validate_audio_conversion(
    entry: dict[str, Any], label: str, errors: list[str]
) -> None:
    """The twin-hash law: export bytes ARE the pinned PCM16 evaluation twin."""
    conversion = entry.get("conversion")
    if not isinstance(conversion, dict):
        errors.append(f"{label}.conversion must be an object")
        return
    law = conversion.get("law")
    if not isinstance(law, str) or not law.strip():
        errors.append(f"{label}.conversion.law must be a non-empty string")
    twin = conversion.get("evaluation_twin_sha256")
    if not _valid_sha256(twin):
        errors.append(f"{label}.conversion.evaluation_twin_sha256 must be lowercase SHA-256")
    elif twin != entry.get("sha256"):
        errors.append(
            f"{label}.conversion export sha256 must equal the evaluation-twin sha256 "
            "(conversion law)"
        )
    if conversion.get("reproduces_evaluation_twin") is not True:
        errors.append(f"{label}.conversion.reproduces_evaluation_twin must be true")


def _validate_audio_source(
    entry: dict[str, Any], label: str, root: Path, errors: list[str]
) -> None:
    source = entry.get("source")
    if not isinstance(source, dict):
        errors.append(f"{label}.source must be an object")
        return
    digest = source.get("sha256")
    if not _valid_sha256(digest):
        errors.append(f"{label}.source.sha256 must be lowercase SHA-256")
    for key in ("source_revision", "twin_pinned_commit"):
        value = source.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.source.{key} must be a non-empty string")
    try:
        path = _safe_path(root, source.get("path"), "sources")
    except AssetGateError as exc:
        errors.append(f"{label}.source.path: {exc}")
        return
    if not path.is_file():
        errors.append(f"{label}.source.path does not exist")
    elif digest != sha256_file(path):
        errors.append(f"{label}.source.sha256 does not match the source file")


def _validate_audio_provenance(entry: dict[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}.{error}" for error in _validate_provenance(entry.get("provenance")))
    provenance = entry.get("provenance")
    if not isinstance(provenance, dict):
        return
    method = provenance.get("method")
    if not isinstance(method, str) or not method.strip():
        errors.append(f"{label}.provenance.method must be a non-empty string")
    upstream = provenance.get("upstream")
    if not isinstance(upstream, dict):
        errors.append(f"{label}.provenance.upstream must be an object")
        return
    repository = upstream.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        errors.append(f"{label}.provenance.upstream.repository must be a non-empty string")
    if not _valid_commit(upstream.get("handoff_commit")):
        errors.append(
            f"{label}.provenance.upstream.handoff_commit must be a full lowercase "
            "40-hex Git commit"
        )
    md5_digest = upstream.get("handoff_manifest_md5")
    if not isinstance(md5_digest, str) or MD5_RE.fullmatch(md5_digest) is None:
        errors.append(
            f"{label}.provenance.upstream.handoff_manifest_md5 must be lowercase MD5"
        )


def _validate_audio_file(
    entry: dict[str, Any], label: str, root: Path, raw_path: Any, errors: list[str]
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
        info = read_wav(path)
    except (WavError, OSError) as exc:
        errors.append(f"{label}.path: {exc}")
        return
    if (info.sample_rate_hz, info.channels, info.bit_depth) != (AUDIO_RATE_HZ, 1, 16):
        errors.append(f"{label} WAV must be PCM16 mono {AUDIO_RATE_HZ} Hz")
    if info.frames != entry.get("frames"):
        errors.append(
            f"{label} WAV has {info.frames} frames; manifest declares {entry.get('frames')}"
        )


def _validate_audio_export_entry(
    export: dict[str, Any],
    label: str,
    root: Path,
    release_id: str,
    seen_ids: set[str],
    seen_paths: set[str],
    errors: list[str],
) -> None:
    """Additive audio-kind law; visual entries never reach this path."""
    asset_id = _validate_asset_id(export, label, seen_ids, errors)
    raw_path = export.get("path")
    expected = f"exports/{release_id}/{asset_id}.wav"
    if raw_path != expected:
        errors.append(f"{label}.path must be {expected}")
    if isinstance(raw_path, str):
        if raw_path in seen_paths:
            errors.append(f"{label}.path is duplicated")
        seen_paths.add(raw_path)
    for key in ("role", "level_band"):
        value = export.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{key} must be a non-empty string")
    _validate_audio_shape(export, label, errors)
    _validate_audio_loudness(export, label, errors)
    _validate_audio_conversion(export, label, errors)
    _validate_audio_source(export, label, root, errors)
    _validate_audio_provenance(export, label, errors)
    _validate_audio_file(export, label, root, raw_path, errors)


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


def _game_head_lf_sha256(game_root: Path, path: str) -> str | None:
    """LF-normalized SHA-256 of a file's committed content at the game HEAD."""
    try:
        blob = subprocess.run(
            ["git", "-C", str(game_root), "show", f"HEAD:{path}"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()


def _validate_game_source(
    entry: Any, index: int, game_root: Path, errors: list[str], warnings: list[str]
) -> None:
    """Committed HEAD content decides compatibility; worktree state only warns.

    Parallel-session law (owner directive 2026-08-18): the sibling game-two
    checkout is another agent's live workbench, so its uncommitted edits must
    never fail this gate. Content drift in COMMITTED history remains a hard
    failure requiring owner review.
    """
    label = f"source_files[{index}]"
    source = _as_object(entry, label, errors)
    if not source:
        return
    rel = str(source.get("path", ""))
    head_sha = _game_head_lf_sha256(game_root, rel)
    if head_sha is None:
        errors.append(f"{label}.path does not exist at game-two HEAD")
        return
    if source.get("sha256_lf") != head_sha:
        errors.append(f"{label}.sha256_lf does not match game-two")
        return
    worktree = game_root / rel
    if not worktree.is_file():
        warnings.append(
            f"{label} ({rel}): missing from the game-two worktree "
            "(HEAD content still matches the pin)"
        )
    elif sha256_file(worktree, normalize_lf=True) != head_sha:
        warnings.append(
            f"{label} ({rel}): worktree differs from HEAD "
            "(parallel session mid-edit; committed content still matches the pin)"
        )


def _validate_game_baseline(
    baseline: dict[str, Any], game_root: Path, errors: list[str], warnings: list[str]
) -> None:
    try:
        actual_commit = _game_head(game_root)
    except AssetGateError as exc:
        errors.append(str(exc))
    else:
        if actual_commit != baseline.get("game_commit"):
            warnings.append(
                f"game HEAD is {actual_commit}; baseline pins "
                f"{baseline.get('game_commit')} (commit-identity drift; content "
                "below decides - re-pin at the next sprint checkpoint)"
            )
    source_files = baseline.get("source_files")
    if not isinstance(source_files, list):
        errors.append("source_files must be a list")
        return
    for index, entry in enumerate(source_files):
        _validate_game_source(entry, index, game_root, errors, warnings)


def validate_runtime_baseline_report(
    root: Path = ROOT, game_root: Path | None = None
) -> tuple[list[str], list[str]]:
    """Full report: (blocking errors, non-blocking parallel-session warnings)."""
    baseline_path = root / "manifests" / "runtime-baseline.json"
    try:
        baseline = _load_json(baseline_path)
    except AssetGateError as exc:
        return [f"{baseline_path}: {exc}"], []
    errors: list[str] = []
    warnings: list[str] = []
    _validate_baseline_shape(baseline, errors)
    if game_root is not None:
        _validate_game_baseline(baseline, game_root, errors, warnings)
    return (
        [f"{baseline_path}: {error}" for error in errors],
        [f"{baseline_path}: {warning}" for warning in warnings],
    )


def validate_runtime_baseline(root: Path = ROOT, game_root: Path | None = None) -> list[str]:
    return validate_runtime_baseline_report(root, game_root)[0]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    manifests = args.manifest or sorted(root.glob("exports/**/release.json"))
    errors, warnings = validate_runtime_baseline_report(root, args.game_root)
    errors.extend(validate_toolchain_baseline(root, args.aseprite))
    for manifest in manifests:
        errors.extend(validate_release(manifest.resolve(), root))
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if not errors:
        return 0
    print(f"Asset gate failed with {len(errors)} violation(s):", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
