#!/usr/bin/env python3
"""Ingest the game-two-audio handoff/audio-v1 package as a gate-valid release.

Conversion-only lane (reviews/audio-v1/rationale.md): the seven owner-performed
24-bit 48 kHz mono originals are copied byte-exact into sources/audio-v1/, then
converted to PCM16 by the pinned twin-hash law

    s16 = clamp(round(s24 / 2^23 * 32767), -32768, 32767)   # round-half-even

and written as canonical Python-wave-module WAVs whose bytes MUST reproduce the
handoff manifest's evaluation-twin sha256 per file. Any mismatch is a hard STOP:
no divergent conversion ever ships. Zero audio-content edits: no gain, no trim,
no fade, no resample, no synthesis.

Stages (source-commit honesty, same law as make_release.py):
  --stage sources   verify the handoff package, copy originals + manifest
  --stage release   require sources/tools/manifests committed clean, convert,
                    write exports/audio-v1/*.wav + release.json
  --stage all       both (tests and tmp roots)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import subprocess
import sys
import wave
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from audio_metrics import (  # noqa: E402
    ENGINE_RATE_HZ,
    KB_LUFS_TARGETS,
    KB_TARGET_REF,
    WavError,
    integrated_lufs,
    read_wav,
    sample_peak_dbfs,
)

RELEASE_ID = "audio-v1"
EXPORTER = "tools/ingest_audio.py"
DEFAULT_HANDOFF = ROOT.parent / "game-two-audio" / "handoff" / "audio-v1"
HANDOFF_MANIFEST_MD5 = "4ec54531b6c9bda71acbe57252e01194"
HANDOFF_COMMIT = "cfef3117b48ae35831ffb5834aec25885b0a7149"
CONVERSION_LAW = (
    "s16 = clamp(round(s24 / 8388608.0 * 32767.0), -32768, 32767) with IEEE-754 "
    "float64 arithmetic and Python round-half-even, written as a canonical "
    "Python-wave-module PCM16 mono 48000 Hz WAV (44-byte RIFF/WAVE/fmt/data "
    "header, little-endian, no ancillary chunks); export bytes must equal the "
    "handoff manifest's evaluation-twin sha256 (whole-file hash)"
)
PROVENANCE = {
    "origin": "human",
    "author": "project owner (in-house performance; owner VST instruments)",
    "created": "2026-08-18",
    "rights": "private-project",
    "method": (
        "in-house owner performance: owner VST instruments driven by MIDI "
        "compositions authored in game-two-audio data/audio_listen/fixtures.json, "
        "rendered through REAPER 7.79 on 2026-08-18 (no third-party audio, no "
        "sample packs); ingested unmodified from handoff/audio-v1 - "
        "conversion-only 24->16 per the pinned twin-hash law, zero content edits"
    ),
    "upstream": {
        "repository": "game-two-audio",
        "handoff_path": "handoff/audio-v1",
        "handoff_commit": HANDOFF_COMMIT,
        "handoff_manifest_md5": HANDOFF_MANIFEST_MD5,
    },
}


class IngestError(RuntimeError):
    """A handoff-verification or conversion-law violation (hard STOP)."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def convert_pcm24_to_pcm16(samples24: tuple[int, ...]) -> bytes:
    """The pinned conversion law; returns canonical PCM16 WAV bytes."""
    scaled = [
        max(-32768, min(32767, round(v / 8388608.0 * 32767.0))) for v in samples24
    ]
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(ENGINE_RATE_HZ)
        writer.writeframes(struct.pack(f"<{len(scaled)}h", *scaled))
    return buffer.getvalue()


def load_handoff(handoff_dir: Path) -> tuple[dict, bytes]:
    """Read and verify the handoff manifest against its pinned md5."""
    manifest_path = handoff_dir / "manifest.json"
    try:
        raw = manifest_path.read_bytes()
    except OSError as exc:
        raise IngestError(f"cannot read handoff manifest: {exc}") from exc
    digest = hashlib.md5(raw).hexdigest()
    if digest != HANDOFF_MANIFEST_MD5:
        raise IngestError(
            f"handoff manifest md5 {digest} != pinned {HANDOFF_MANIFEST_MD5}; "
            "STOP - do not ingest, mail game-two-audio"
        )
    return json.loads(raw.decode("utf-8")), raw


def verify_original(handoff_dir: Path, asset: dict) -> bytes:
    data = (handoff_dir / asset["file"]).read_bytes()
    if sha256_bytes(data) != asset["sha256"]:
        raise IngestError(
            f"{asset['id']}: original sha256 differs from the handoff manifest; STOP"
        )
    return data


def stage_sources(root: Path, handoff_dir: Path) -> None:
    manifest, raw = load_handoff(handoff_dir)
    source_dir = root / "sources" / RELEASE_ID
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "handoff-manifest.json").write_bytes(raw)
    for asset in manifest["assets"]:
        data = verify_original(handoff_dir, asset)
        (source_dir / asset["file"]).write_bytes(data)
    print(f"staged {len(manifest['assets'])} originals + manifest under {source_dir}")


def _git_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(key, None)
    return env


def source_commit(root: Path) -> str:
    """HEAD commit, required to have sources/, tools/, manifests/ committed clean."""
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, env=_git_env(),
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--",
             "sources", "tools", "manifests"],
            check=True, capture_output=True, text=True, env=_git_env(),
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IngestError(f"git failed: {exc}") from exc
    if dirty:
        raise IngestError(
            "sources/, tools/, or manifests/ differ from HEAD; commit them first:\n"
            + dirty
        )
    return head


def _verify_staged_source(source_dir: Path, asset: dict) -> None:
    path = source_dir / asset["file"]
    if not path.is_file():
        raise IngestError(f"{asset['id']}: missing staged source {path}")
    if sha256_bytes(path.read_bytes()) != asset["sha256"]:
        raise IngestError(f"{asset['id']}: staged source differs from the handoff manifest")


def build_release(root: Path, commit: str) -> dict:
    """Convert every staged source and emit the release manifest."""
    source_dir = root / "sources" / RELEASE_ID
    export_dir = root / "exports" / RELEASE_ID
    manifest_copy = source_dir / "handoff-manifest.json"
    raw = manifest_copy.read_bytes()
    if hashlib.md5(raw).hexdigest() != HANDOFF_MANIFEST_MD5:
        raise IngestError("staged handoff-manifest.json md5 differs from the pin; STOP")
    manifest = json.loads(raw.decode("utf-8"))

    source_files = [
        {
            "path": f"sources/{RELEASE_ID}/handoff-manifest.json",
            "sha256": sha256_bytes(raw),
        }
    ]
    exports = []
    export_dir.mkdir(parents=True, exist_ok=True)
    for asset in manifest["assets"]:
        asset_id = asset["id"]
        _verify_staged_source(source_dir, asset)
        source_path = source_dir / asset["file"]
        source_files.append(
            {"path": f"sources/{RELEASE_ID}/{asset['file']}", "sha256": asset["sha256"]}
        )
        source_info = read_wav(source_path)
        if (source_info.sample_rate_hz, source_info.channels, source_info.bit_depth) != (
            ENGINE_RATE_HZ, 1, 24,
        ):
            raise IngestError(f"{asset_id}: source is not PCM24 mono 48 kHz")
        if source_info.frames != asset["frames"]:
            raise IngestError(
                f"{asset_id}: source frames {source_info.frames} != manifest {asset['frames']}"
            )
        wav16 = convert_pcm24_to_pcm16(source_info.samples)
        export_sha = sha256_bytes(wav16)
        twin_sha = asset["evaluation_twin"]["sha256"]
        if export_sha != twin_sha:
            raise IngestError(
                f"{asset_id}: conversion does not reproduce the evaluation twin "
                f"({export_sha} != {twin_sha}); STOP - bank the sources lane and "
                "mail game-two-audio for their exact conversion spec"
            )
        export_path = export_dir / f"{asset_id}.wav"
        export_path.write_bytes(wav16)
        export_info = read_wav(export_path)
        if export_info.frames != asset["frames"]:
            raise IngestError(f"{asset_id}: export frame count drifted")

        lufs = integrated_lufs(export_info)
        row_label, band = KB_LUFS_TARGETS.get(asset_id, (None, None))
        exports.append(
            {
                "asset_id": asset_id,
                "kind": "audio",
                "path": f"exports/{RELEASE_ID}/{asset_id}.wav",
                "sha256": export_sha,
                "format": {
                    "container": "wav",
                    "codec": "pcm_s16le",
                    "sample_rate_hz": ENGINE_RATE_HZ,
                    "channels": 1,
                    "bit_depth": 16,
                },
                "frames": asset["frames"],
                "dur_s": asset["dur_s"],
                "role": asset["role"],
                "level_band": asset["level_band"],
                "loudness": {
                    "lufs_integrated": None if lufs is None else round(lufs, 4),
                    "sample_peak_dbfs": round(sample_peak_dbfs(export_info), 4),
                    "kb_target_lufs": list(band) if band else None,
                    "kb_target_ref": f"{KB_TARGET_REF}: {row_label}" if row_label else None,
                },
                "conversion": {
                    "law": CONVERSION_LAW,
                    "evaluation_twin_sha256": twin_sha,
                    "reproduces_evaluation_twin": True,
                },
                "source": {
                    "path": f"sources/{RELEASE_ID}/{asset['file']}",
                    "sha256": asset["sha256"],
                    "source_revision": asset["source_revision"],
                    "twin_pinned_commit": asset["evaluation_twin"]["pinned_commit"],
                },
                "provenance": json.loads(json.dumps(PROVENANCE)),
            }
        )

    baseline = json.loads(
        (root / "manifests" / "runtime-baseline.json").read_text(encoding="utf-8")
    )
    return {
        "contract_version": 1,
        "release_id": RELEASE_ID,
        "source": {"commit": commit, "files": source_files},
        "target": {
            "game_commit": baseline["game_commit"],
            "runtime_baseline": "manifests/runtime-baseline.json",
        },
        "toolchain": {
            "baseline": "manifests/toolchain-baseline.json",
            "exporter_path": EXPORTER,
            "exporter_sha256": hashlib.sha256(
                (root / EXPORTER).read_bytes()
            ).hexdigest(),
        },
        "exports": exports,
    }


def stage_release(root: Path, commit: str | None) -> None:
    resolved = commit or source_commit(root)
    release = build_release(root, resolved)
    out_path = root / "exports" / RELEASE_ID / "release.json"
    out_path.write_text(
        json.dumps(release, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"wrote {out_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--handoff", type=Path, default=DEFAULT_HANDOFF)
    parser.add_argument(
        "--stage", choices=("sources", "release", "all"), required=True
    )
    parser.add_argument("--commit", help="override source commit (tests only)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.stage in ("sources", "all"):
            stage_sources(root, args.handoff.resolve())
        if args.stage in ("release", "all"):
            stage_release(root, args.commit)
    except (IngestError, WavError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"ingest refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
