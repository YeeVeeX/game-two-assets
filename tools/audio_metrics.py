#!/usr/bin/env python3
"""Deterministic audio metrics + validator for the audio-v1 release lane.

Strict RIFF/WAVE PCM reader, ITU-R BS.1770-4 integrated loudness (48 kHz
K-weighting, 400 ms blocks, 75% overlap, -70 LKFS absolute + -10 LU relative
gating), and sample-peak measurement. REPORT-ONLY: nothing here ever modifies
audio bytes; the twin-hash conversion law makes gain edits impossible anyway.

`--check` validates the banked release against the pre-registered pass bars
(reviews/audio-v1/rationale.md sections 4 and 8) and writes
reviews/audio-v1/audio-metrics.json. Failures are grouped INTEGRITY
(stops the sprint) vs MEASUREMENT (banked evidence, routed findings).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENGINE_RATE_HZ = 48000
BAR_FRAMES = 96000  # one bar at 120 bpm 4/4 @ 48 kHz (handoff bar-exact law)
BLOCK_SAMPLES = 19200  # 400 ms gating block @ 48 kHz
STEP_SAMPLES = 4800  # 75% overlap -> 100 ms step
ABSOLUTE_GATE_LUFS = -70.0
RELATIVE_GATE_LU = -10.0
LOUDNESS_OFFSET = -0.691

# BS.1770-4 K-weighting biquads for 48 kHz input (published coefficients).
STAGE1_B = (1.53512485958697, -2.69169618940638, 1.19839281085285)
STAGE1_A = (1.0, -1.69065929318241, 0.73248077421585)
STAGE2_B = (1.0, -2.0, 1.0)
STAGE2_A = (1.0, -1.99004745483398, 0.99007225036621)

# Pre-registered KB targets (music-production/game-audio-pipeline.md section 7).
# asset_id -> (kb_row_label, (low, high) integrated-LUFS band) or (None, None)
# where section 7 has no row for the role (report-only, never invented).
KB_LUFS_TARGETS: dict[str, tuple[str | None, tuple[float, float] | None]] = {
    "mstem_calm_6s": ("Music (exploration)", (-18.0, -16.0)),
    "mstem_combat_6s": ("Music (combat)", (-16.0, -14.0)),
    "msfx_drone_4s": ("Ambient/drone", (-24.0, -20.0)),
    "msfx_stinger_2s": ("Sound effects", (-14.0, -10.0)),
    "msfx_swarmpip_4s": (None, None),  # stacked-texture role: no KB row
    "mui_confirm_200ms": ("UI sounds", (-16.0, -12.0)),
    "mui_ping_1200ms": ("UI sounds", (-16.0, -12.0)),
}
KB_TARGET_REF = "music-production/game-audio-pipeline.md section 7 (LUFS Targets for Game Audio)"
PEAK_CROSSCHECK_TOLERANCE_DB = 0.05  # pre-registered (rationale section 4)


class WavError(ValueError):
    """A malformed or unsupported WAV file."""


@dataclass(frozen=True)
class WavInfo:
    """Decoded PCM WAV: format facts plus integer samples."""

    sample_rate_hz: int
    channels: int
    bit_depth: int
    frames: int
    samples: tuple[int, ...]

    @property
    def full_scale(self) -> int:
        return 1 << (self.bit_depth - 1)


def _walk_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise WavError("not a RIFF/WAVE file")
    declared = struct.unpack("<I", data[4:8])[0]
    if declared + 8 != len(data):
        raise WavError(f"RIFF size {declared} does not match file size {len(data)}")
    chunks: list[tuple[bytes, bytes]] = []
    pos = 12
    while pos < len(data):
        if pos + 8 > len(data):
            raise WavError("truncated chunk header")
        kind = data[pos : pos + 4]
        size = struct.unpack("<I", data[pos + 4 : pos + 8])[0]
        body = data[pos + 8 : pos + 8 + size]
        if len(body) != size:
            raise WavError(f"truncated {kind!r} chunk")
        chunks.append((kind, body))
        pos += 8 + size + (size % 2)  # chunks are word-aligned
    return chunks


def _decode_samples(raw: bytes, bit_depth: int) -> tuple[int, ...]:
    if bit_depth == 16:
        return struct.unpack(f"<{len(raw) // 2}h", raw)
    values = []
    for i in range(0, len(raw), 3):
        v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
        if v >= 1 << 23:
            v -= 1 << 24
        values.append(v)
    return tuple(values)


def read_wav(path: Path) -> WavInfo:
    """Strict mono PCM 16/24-bit reader; rejects everything else loudly."""
    chunks = _walk_chunks(path.read_bytes())
    fmts = [body for kind, body in chunks if kind == b"fmt "]
    datas = [body for kind, body in chunks if kind == b"data"]
    if len(fmts) != 1 or len(datas) != 1:
        raise WavError("expected exactly one fmt chunk and one data chunk")
    if len(fmts[0]) < 16:
        raise WavError("fmt chunk shorter than 16 bytes")
    tag, channels, rate, _, block_align, bits = struct.unpack("<HHIIHH", fmts[0][:16])
    if tag != 1:
        raise WavError(f"unsupported WAV format tag {tag} (PCM only)")
    if channels != 1:
        raise WavError(f"unsupported channel count {channels} (mono only)")
    if bits not in (16, 24):
        raise WavError(f"unsupported bit depth {bits} (16 or 24 only)")
    if block_align != channels * bits // 8:
        raise WavError(f"block align {block_align} inconsistent with format")
    if len(datas[0]) % block_align:
        raise WavError("data chunk is not a whole number of frames")
    samples = _decode_samples(datas[0], bits)
    return WavInfo(rate, channels, bits, len(samples), samples)


def sample_peak_dbfs(info: WavInfo) -> float:
    peak = max(abs(s) for s in info.samples) if info.samples else 0
    if peak == 0:
        return -math.inf
    return 20.0 * math.log10(peak / info.full_scale)


def _biquad(
    samples: list[float], b: tuple[float, float, float], a: tuple[float, float, float]
) -> list[float]:
    out = [0.0] * len(samples)
    x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b
    _, a1, a2 = a
    for i, x0 in enumerate(samples):
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        out[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return out


def _block_mean_squares(weighted: list[float]) -> list[float]:
    """Mean square of each 400 ms block at 75% overlap (prefix-sum, exact order)."""
    if len(weighted) < BLOCK_SAMPLES:
        return []
    squares = [v * v for v in weighted]
    prefix = [0.0] * (len(squares) + 1)
    for i, v in enumerate(squares):
        prefix[i + 1] = prefix[i] + v
    blocks = []
    start = 0
    while start + BLOCK_SAMPLES <= len(squares):
        blocks.append((prefix[start + BLOCK_SAMPLES] - prefix[start]) / BLOCK_SAMPLES)
        start += STEP_SAMPLES
    return blocks


def _loudness(mean_square: float) -> float:
    if mean_square <= 0.0:
        return -math.inf
    return LOUDNESS_OFFSET + 10.0 * math.log10(mean_square)


def integrated_lufs(info: WavInfo) -> float | None:
    """BS.1770-4 gated integrated loudness; None below one 400 ms block."""
    if info.sample_rate_hz != ENGINE_RATE_HZ:
        raise WavError(f"meter is pinned to {ENGINE_RATE_HZ} Hz input")
    if info.frames < BLOCK_SAMPLES:
        return None
    scale = float(info.full_scale)
    normalized = [s / scale for s in info.samples]
    weighted = _biquad(_biquad(normalized, STAGE1_B, STAGE1_A), STAGE2_B, STAGE2_A)
    blocks = _block_mean_squares(weighted)
    above_absolute = [z for z in blocks if _loudness(z) > ABSOLUTE_GATE_LUFS]
    if not above_absolute:
        return None
    relative_gate = _loudness(sum(above_absolute) / len(above_absolute)) + RELATIVE_GATE_LU
    surviving = [z for z in above_absolute if _loudness(z) > relative_gate]
    if not surviving:
        return None
    return _loudness(sum(surviving) / len(surviving))


# --- meter self-validation (pre-registered vectors V1-V6) ---------------------


def _sine_pcm16(freq: float, amplitude: float, seconds: float) -> WavInfo:
    frames = int(round(seconds * ENGINE_RATE_HZ))
    scale = 32768.0
    samples = tuple(
        max(-32768, min(32767, round(amplitude * scale * math.sin(2.0 * math.pi * freq * n / ENGINE_RATE_HZ))))
        for n in range(frames)
    )
    return WavInfo(ENGINE_RATE_HZ, 1, 16, frames, samples)


def _analytic_sine_lufs(amplitude: float, freq: float) -> float:
    """Independent expectation: direct transfer-function evaluation (rationale 4)."""

    def mag2(b: tuple[float, float, float], a: tuple[float, float, float]) -> float:
        import cmath

        z = cmath.exp(-2j * math.pi * freq / ENGINE_RATE_HZ)
        return abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)) ** 2

    mean_square = (amplitude**2 / 2.0) * mag2(STAGE1_B, STAGE1_A) * mag2(STAGE2_B, STAGE2_A)
    return LOUDNESS_OFFSET + 10.0 * math.log10(mean_square)


def meter_validation_failures() -> list[str]:
    """Run vectors V1-V6; returns pre-registered-tolerance violations."""
    failures: list[str] = []
    v1 = _sine_pcm16(997.0, 0.5, 5.0)
    v2 = _sine_pcm16(997.0, 0.25, 5.0)
    m1, m2 = integrated_lufs(v1), integrated_lufs(v2)
    e1, e2 = _analytic_sine_lufs(0.5, 997.0), _analytic_sine_lufs(0.25, 997.0)
    if m1 is None or abs(m1 - e1) > 0.05:
        failures.append(f"V1: measured {m1} vs expected {e1:.4f} (tol 0.05)")
    if m2 is None or abs(m2 - e2) > 0.05:
        failures.append(f"V2: measured {m2} vs expected {e2:.4f} (tol 0.05)")
    if m1 is not None and m2 is not None and abs((m2 - m1) - (-6.0206)) > 0.02:
        failures.append(f"V2 delta: {m2 - m1:.4f} vs -6.0206 (tol 0.02)")
    sine = _sine_pcm16(997.0, 0.1, 3.0)
    padded = WavInfo(
        ENGINE_RATE_HZ, 1, 16, sine.frames * 2, sine.samples + (0,) * sine.frames
    )
    m_sine, m_padded = integrated_lufs(sine), integrated_lufs(padded)
    if m_sine is None or m_padded is None or abs(m_padded - m_sine) > 0.30:
        failures.append(f"V3 gating: sine {m_sine} vs sine+silence {m_padded} (tol 0.30)")
    frames = 4 * ENGINE_RATE_HZ
    silence = WavInfo(ENGINE_RATE_HZ, 1, 16, frames, (0,) * frames)
    if integrated_lufs(silence) is not None:
        failures.append("V4a: digital silence must gate out to None")
    dc = WavInfo(ENGINE_RATE_HZ, 1, 16, frames, (16384,) * frames)
    dc_lufs = integrated_lufs(dc)
    if dc_lufs is None or dc_lufs > -25.0:
        failures.append(
            f"V4b: DC must read far below the unweighted level (got {dc_lufs}; "
            "only the onset step transient may gate in)"
        )
    spike = WavInfo(ENGINE_RATE_HZ, 1, 16, 4800, (0,) * 4799 + (32767,))
    if abs(sample_peak_dbfs(spike) - 20.0 * math.log10(32767 / 32768)) > 0.001:
        failures.append("V5: sample peak of +32767 spike out of tolerance")
    half = _sine_pcm16(997.0, 0.5, 1.0)
    if abs(sample_peak_dbfs(half) - (-6.0206)) > 0.01:
        failures.append(f"V6: sample peak {sample_peak_dbfs(half):.4f} vs -6.0206 (tol 0.01)")
    return failures


# --- release validation (--check) ---------------------------------------------


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _round(value: float | None, digits: int = 4) -> float | None:
    return None if value is None else round(value, digits)


def measure_release(
    root: Path,
    release_path: Path,
    handoff_manifest_path: Path,
) -> tuple[dict, list[str], list[str]]:
    """Measure every export; returns (metrics document, integrity, measurement)."""
    integrity: list[str] = []
    measurement: list[str] = []
    release = _load_json(release_path)
    manifest = _load_json(handoff_manifest_path)
    by_id = {asset["id"]: asset for asset in manifest.get("assets", [])}

    integrity.extend(f"meter validation: {failure}" for failure in meter_validation_failures())

    files = []
    for entry in release.get("exports", []):
        asset_id = entry.get("asset_id", "?")
        declared = by_id.get(asset_id)
        if declared is None:
            integrity.append(f"{asset_id}: not present in the handoff manifest")
            continue
        export_path = root / entry["path"]
        source_path = root / entry["source"]["path"]
        record: dict = {"asset_id": asset_id}
        try:
            export = read_wav(export_path)
            source = read_wav(source_path)
        except (OSError, WavError) as exc:
            integrity.append(f"{asset_id}: {exc}")
            continue

        export_sha = hashlib.sha256(export_path.read_bytes()).hexdigest()
        source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        twin_sha = declared["evaluation_twin"]["sha256"]
        if source_sha != declared["sha256"]:
            integrity.append(f"{asset_id}: source sha256 differs from the handoff original")
        if export_sha != twin_sha:
            integrity.append(f"{asset_id}: export bytes do not reproduce the evaluation twin")
        if entry.get("sha256") != export_sha:
            integrity.append(f"{asset_id}: release sha256 differs from the export file")
        if not (export.frames == source.frames == declared["frames"]):
            integrity.append(
                f"{asset_id}: frame counts differ (export {export.frames}, "
                f"source {source.frames}, manifest {declared['frames']})"
            )
        if (export.sample_rate_hz, export.channels, export.bit_depth) != (ENGINE_RATE_HZ, 1, 16):
            integrity.append(f"{asset_id}: export is not PCM16 mono 48 kHz")
        if (source.sample_rate_hz, source.channels, source.bit_depth) != (ENGINE_RATE_HZ, 1, 24):
            integrity.append(f"{asset_id}: source is not PCM24 mono 48 kHz")
        if abs(declared["dur_s"] * ENGINE_RATE_HZ - declared["frames"]) > 1e-6:
            integrity.append(f"{asset_id}: manifest dur_s and frames disagree")
        if asset_id.startswith("mstem_") and declared["frames"] % BAR_FRAMES:
            integrity.append(f"{asset_id}: stem is not bar-exact (frames % {BAR_FRAMES})")

        source_peak = sample_peak_dbfs(source)
        export_peak = sample_peak_dbfs(export)
        declared_peak = declared["peak_dbfs"]
        if abs(source_peak - declared_peak) > PEAK_CROSSCHECK_TOLERANCE_DB:
            integrity.append(
                f"{asset_id}: source sample peak {source_peak:.4f} dBFS vs declared "
                f"{declared_peak} (tol {PEAK_CROSSCHECK_TOLERANCE_DB})"
            )

        lufs = integrated_lufs(export)
        row_label, band = KB_LUFS_TARGETS.get(asset_id, (None, None))
        in_band: bool | None = None
        if band is not None and lufs is not None:
            in_band = band[0] <= lufs <= band[1]
            if not in_band:
                direction = "below" if lufs < band[0] else "above"
                measurement.append(
                    f"{asset_id}: integrated {lufs:.2f} LUFS is {direction} the KB band "
                    f"[{band[0]}, {band[1]}] ({row_label}) - routed finding, never gain-rescued"
                )
        record.update(
            {
                "role": declared["role"],
                "level_band": declared["level_band"],
                "frames": export.frames,
                "dur_s": declared["dur_s"],
                "export_path": entry["path"],
                "export_sha256": export_sha,
                "source_path": entry["source"]["path"],
                "source_sha256": source_sha,
                "evaluation_twin_sha256": twin_sha,
                "reproduces_evaluation_twin": export_sha == twin_sha,
                "lufs_integrated": _round(lufs),
                "lufs_note": (
                    None
                    if export.frames >= BLOCK_SAMPLES
                    else "undefined: shorter than one 400 ms gating block"
                ),
                "kb_target_row": row_label,
                "kb_target_lufs": list(band) if band else None,
                "kb_in_band": in_band,
                "sample_peak_dbfs": _round(export_peak),
                "source_sample_peak_dbfs": _round(source_peak),
                "declared_peak_dbfs": declared_peak,
                "declared_rms_dbfs": declared["rms_dbfs"],
            }
        )
        files.append(record)

    document = {
        "_what": (
            "audio-v1 deterministic metrics: BS.1770-4 integrated LUFS (report-only) "
            "+ sample peak per export, conversion/consistency verdicts, KB section-7 "
            "target conformance. Pass bars pre-registered in reviews/audio-v1/rationale.md."
        ),
        "engine_rate_hz": ENGINE_RATE_HZ,
        "meter": "ITU-R BS.1770-4 (48 kHz K-weighting, 400 ms blocks, 75% overlap, gated)",
        "kb_target_ref": KB_TARGET_REF,
        "peak_crosscheck_tolerance_db": PEAK_CROSSCHECK_TOLERANCE_DB,
        "meter_validation": "vectors V1-V6 passed" if not any(
            failure.startswith("meter validation") for failure in integrity
        ) else "FAILED",
        "files": files,
        "integrity_failures": integrity,
        "measurement_failures": measurement,
    }
    return document, integrity, measurement


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--release", type=Path, default=Path("exports/audio-v1/release.json")
    )
    parser.add_argument(
        "--handoff-manifest",
        type=Path,
        default=Path("sources/audio-v1/handoff-manifest.json"),
    )
    parser.add_argument(
        "--out", type=Path, default=Path("reviews/audio-v1/audio-metrics.json")
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero on INTEGRITY or MEASUREMENT failures",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    document, integrity, measurement = measure_release(
        root, root / args.release, root / args.handoff_manifest
    )
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"wrote {out_path}")
    for failure in integrity:
        print(f"INTEGRITY: {failure}", file=sys.stderr)
    for failure in measurement:
        print(f"MEASUREMENT: {failure}", file=sys.stderr)
    if args.check and (integrity or measurement):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
