#!/usr/bin/env python3
"""Deterministic audio-v1 analysis sheet (inspection, not taste).

One row per export: mechanical id, min/max waveform envelope decoded from the
shipped PCM16 export (amplitude against FULL SCALE - no normalization, so
quiet files look quiet), and the measured numbers verbatim from
reviews/audio-v1/audio-metrics.json (duration/frames, integrated LUFS vs the
pre-registered KB section-7 band, sample peak vs the handoff's declared peak).
Layout is fixed; regeneration is byte-identical.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from audio_metrics import PEAK_CROSSCHECK_TOLERANCE_DB, read_wav  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402

WAVE_W = 512
WAVE_H = 56
MARGIN = 10
TEXT_X = MARGIN + WAVE_W + 14
TEXT_SCALE = 2
LINE_H = 6 * TEXT_SCALE
ROW_H = WAVE_H + 22
HEADER_H = 34
SHEET_W = 1010

BG = (16, 16, 16, 255)
BOX = (58, 58, 58, 255)
AXIS = (70, 70, 70, 255)
WAVEFORM = (235, 120, 40, 255)  # player_1 baseline accent
LABEL = (200, 200, 200, 255)
VALUE = (150, 150, 150, 255)
FLAG_IN = (110, 200, 120, 255)
FLAG_OUT = (235, 170, 80, 255)
FLAG_NA = (120, 120, 120, 255)

# Minimal 3x5 glyphs (generic mechanical labels only; repo sheet convention).
FONT = {
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("011", "100", "101", "101", "011"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "P": ("110", "101", "110", "100", "100"),
    "Q": ("010", "101", "101", "110", "011"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("110", "001", "010", "100", "111"),
    "3": ("111", "001", "011", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "110", "001", "110"),
    "6": ("011", "100", "110", "101", "010"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("010", "101", "010", "101", "010"),
    "9": ("010", "101", "011", "001", "110"),
    ".": ("000", "000", "000", "000", "010"),
    "-": ("000", "000", "111", "000", "000"),
    "_": ("000", "000", "000", "000", "111"),
    "/": ("001", "001", "010", "100", "100"),
    ":": ("000", "010", "000", "010", "000"),
    "+": ("000", "010", "111", "010", "000"),
    " ": ("000", "000", "000", "000", "000"),
}


def draw_text(
    cv: Rgba8Canvas,
    x: int,
    y: int,
    text: str,
    color: tuple[int, int, int, int] = VALUE,
    scale: int = TEXT_SCALE,
) -> int:
    """Draw 3x5 glyphs at an integer scale; returns the x after the text."""
    for index, char in enumerate(text):
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.fill_rect(
                        x + (index * 4 + gx) * scale, y + gy * scale, scale, scale, color
                    )
    return x + len(text) * 4 * scale


def fmt(value: float | int | None) -> str:
    """Exact textual form of a stored metrics number (trailing zeros trimmed)."""
    if value is None:
        return "NULL"
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def envelope_columns(samples: tuple[int, ...], width: int) -> list[tuple[int, int]]:
    """Min/max sample per pixel column (no smoothing, no normalization)."""
    total = len(samples)
    columns = []
    for c in range(width):
        lo = c * total // width
        hi = max(lo + 1, (c + 1) * total // width)
        window = samples[lo:hi]
        columns.append((min(window), max(window)))
    return columns


def draw_waveform(cv: Rgba8Canvas, x: int, y: int, samples: tuple[int, ...]) -> None:
    half = WAVE_H // 2 - 1
    center = y + WAVE_H // 2
    cv.fill_rect(x - 1, y - 1, WAVE_W + 2, 1, BOX)
    cv.fill_rect(x - 1, y + WAVE_H, WAVE_W + 2, 1, BOX)
    cv.fill_rect(x - 1, y - 1, 1, WAVE_H + 2, BOX)
    cv.fill_rect(x + WAVE_W, y - 1, 1, WAVE_H + 2, BOX)
    cv.fill_rect(x, center, WAVE_W, 1, AXIS)
    for c, (low, high) in enumerate(envelope_columns(samples, WAVE_W)):
        y_top = center - round(high * half / 32768)
        y_bottom = center - round(low * half / 32768)
        cv.fill_rect(x + c, y_top, 1, y_bottom - y_top + 1, WAVEFORM)


def lufs_line(record: dict) -> tuple[str, str, tuple[int, int, int, int]]:
    lufs = record["lufs_integrated"]
    band = record["kb_target_lufs"]
    if lufs is None:
        return ("LUFS NULL UNDER 400MS BLOCK", "N/A", FLAG_NA)
    if band is None:
        return (f"LUFS {fmt(lufs)}  TGT NONE IN KB", "REPORT ONLY", FLAG_NA)
    text = f"LUFS {fmt(lufs)}  TGT {fmt(band[0])}..{fmt(band[1])}"
    if record["kb_in_band"]:
        return (text, "IN BAND", FLAG_IN)
    direction = "BELOW" if lufs < band[0] else "ABOVE"
    return (text, f"{direction} BAND", FLAG_OUT)


def peak_line(record: dict) -> tuple[str, str, tuple[int, int, int, int]]:
    measured = record["source_sample_peak_dbfs"]
    declared = record["declared_peak_dbfs"]
    text = (
        f"PEAK {fmt(record['sample_peak_dbfs'])}  "
        f"SRC24 {fmt(measured)}  DECL {fmt(declared)}"
    )
    if abs(measured - declared) <= PEAK_CROSSCHECK_TOLERANCE_DB:
        return (text, "MATCH", FLAG_IN)
    return (text, "DISAGREE", FLAG_OUT)


def build_sheet(root: Path, metrics_path: Path) -> Rgba8Canvas:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    files = metrics["files"]
    height = HEADER_H + len(files) * ROW_H + MARGIN
    cv = Rgba8Canvas(SHEET_W, height, BG)
    draw_text(cv, MARGIN, MARGIN, "AUDIO-V1 EXPORT ANALYSIS", LABEL)
    draw_text(
        cv,
        MARGIN,
        MARGIN + LINE_H,
        "PCM16 MONO 48KHZ  METER BS1770-4  AMPLITUDE AT FULL SCALE - NO NORMALIZATION",
        VALUE,
    )
    for index, record in enumerate(files):
        top = HEADER_H + index * ROW_H
        wav = read_wav(root / record["export_path"])
        label = record["asset_id"].upper()
        draw_text(cv, MARGIN, top, label, LABEL)
        draw_text(
            cv,
            MARGIN + (len(label) + 2) * 4 * TEXT_SCALE,
            top,
            f"DUR {fmt(record['dur_s'])}S  FR {record['frames']}",
            VALUE,
        )
        draw_waveform(cv, MARGIN, top + LINE_H + 2, wav.samples)
        text_top = top + LINE_H + 2
        lufs_text, lufs_flag, lufs_color = lufs_line(record)
        end = draw_text(cv, TEXT_X, text_top, lufs_text, VALUE)
        draw_text(cv, end + 8, text_top, lufs_flag, lufs_color)
        peak_text, peak_flag, peak_color = peak_line(record)
        end = draw_text(cv, TEXT_X, text_top + LINE_H + 4, peak_text, VALUE)
        draw_text(cv, end + 8, text_top + LINE_H + 4, peak_flag, peak_color)
        draw_text(
            cv,
            TEXT_X,
            text_top + 2 * (LINE_H + 4),
            f"TWIN {record['evaluation_twin_sha256'][:16].upper()}  REPRO {'YES' if record['reproduces_evaluation_twin'] else 'NO'}",
            VALUE,
        )
    return cv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--metrics", type=Path, default=Path("reviews/audio-v1/audio-metrics.json")
    )
    parser.add_argument(
        "--out", type=Path, default=Path("reviews/audio-v1/audio-sheet.png")
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    canvas = build_sheet(root, root / args.metrics)
    out_path = root / args.out
    canvas.save(out_path)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
