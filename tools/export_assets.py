#!/usr/bin/env python3
"""Deterministic Aseprite export: native .aseprite sources -> 32x32 RGBA8 PNGs.

Every export is verified pixel-for-pixel against its pixel spec after Aseprite
writes it, so a silent Aseprite behavior change can never ship drifted pixels.
This file is the release manifest's pinned exporter.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from pixel_spec import PixelSpec, SpecError, load_spec_dir  # noqa: E402
from png_reader import PngError, inspect_png  # noqa: E402

DEFAULT_ASEPRITE = Path("C:/tools/aseprite/build/bin/aseprite.exe")


class ExportError(RuntimeError):
    """Aseprite export failure or spec mismatch."""


def export_png(source: Path, out_path: Path, aseprite: Path) -> None:
    """Export one .aseprite to PNG via headless Aseprite CLI."""
    if not source.is_file():
        raise ExportError(f"missing native source {source}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    command = [str(aseprite), "-b", str(source), "--save-as", str(out_path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise ExportError(f"cannot execute aseprite: {exc}") from exc
    if result.returncode != 0:
        raise ExportError(
            f"aseprite failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )
    if not out_path.is_file():
        raise ExportError(f"aseprite did not write {out_path}")


def verify_against_spec(png_path: Path, spec: PixelSpec) -> None:
    """Fail loudly unless the exported PNG matches the spec exactly."""
    try:
        info = inspect_png(png_path)
    except (PngError, OSError) as exc:
        raise ExportError(f"{png_path.name}: unreadable export: {exc}") from exc
    if (info.width, info.height) != (32, 32):
        raise ExportError(f"{png_path.name}: export is {info.width}x{info.height}, not 32x32")
    if not info.alpha_values.issubset({0, 255}):
        raise ExportError(f"{png_path.name}: export alpha is not binary")
    expected_colors = frozenset(spec.used_colors)
    if info.opaque_colors != expected_colors:
        raise ExportError(
            f"{png_path.name}: export colors {sorted(info.opaque_colors)} "
            f"!= spec colors {sorted(expected_colors)}"
        )
    if info.bbox != spec.bbox:
        raise ExportError(f"{png_path.name}: export bbox {info.bbox} != spec bbox {spec.bbox}")


def export_release(
    spec_dir: Path, source_dir: Path, out_dir: Path, aseprite: Path
) -> list[Path]:
    """Export every spec's .aseprite source and verify each result."""
    specs = load_spec_dir(spec_dir)
    written = []
    for spec in specs:
        source = source_dir / f"{spec.asset_id}.aseprite"
        out_path = out_dir / f"{spec.asset_id}.png"
        export_png(source, out_path, aseprite)
        verify_against_spec(out_path, spec)
        written.append(out_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--specs", type=Path, default=ROOT / "sources" / "calibration-v0" / "specs"
    )
    parser.add_argument(
        "--sources", type=Path, default=ROOT / "sources" / "calibration-v0"
    )
    parser.add_argument("--out", type=Path, default=ROOT / "exports" / "calibration-v0")
    parser.add_argument("--aseprite", type=Path, default=DEFAULT_ASEPRITE)
    args = parser.parse_args(argv)
    try:
        written = export_release(args.specs, args.sources, args.out, args.aseprite)
    except (SpecError, ExportError) as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(f"exported {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
