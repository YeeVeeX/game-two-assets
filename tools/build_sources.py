#!/usr/bin/env python3
"""Build native .aseprite sources from pixel specs via headless Aseprite.

Chain: sources/<release>/specs/*.json -> tools/aseprite_build.lua -> sources/<release>/*.aseprite
The generated Lua data chunk is deterministic (sorted, fixed formatting) so the
same spec always drives Aseprite identically.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from pixel_spec import PixelSpec, SpecError, load_spec_dir  # noqa: E402

DEFAULT_ASEPRITE = Path("C:/tools/aseprite/build/bin/aseprite.exe")
BUILDER = TOOLS / "aseprite_build.lua"


class BuildError(RuntimeError):
    """Aseprite source build failure."""


def lua_data_chunk(spec: PixelSpec) -> str:
    """Deterministic Lua chunk carrying the spec's opaque pixels."""
    lines = ["return {", "  width = 32,", "  height = 32,", "  pixels = {"]
    for x, y, (r, g, b) in spec.opaque_pixels():
        lines.append(f"    {{{x}, {y}, {r}, {g}, {b}}},")
    lines.extend(["  },", "}", ""])
    return "\n".join(lines)


def run_aseprite(aseprite: Path, arguments: list[str]) -> None:
    command = [str(aseprite), "-b", *arguments]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise BuildError(f"cannot execute aseprite: {exc}") from exc
    if result.returncode != 0:
        raise BuildError(
            f"aseprite failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )


def build_source(spec: PixelSpec, out_path: Path, aseprite: Path) -> None:
    """Build one .aseprite from one spec."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        data = Path(scratch) / f"{spec.asset_id}.lua"
        data.write_text(lua_data_chunk(spec), encoding="utf-8", newline="\n")
        run_aseprite(
            aseprite,
            [
                "--script-param", f"data={data}",
                "--script-param", f"out={out_path}",
                "--script", str(BUILDER),
            ],
        )
    if not out_path.is_file():
        raise BuildError(f"aseprite did not write {out_path}")


def build_all(spec_dir: Path, out_dir: Path, aseprite: Path) -> list[Path]:
    specs = load_spec_dir(spec_dir)
    written = []
    for spec in specs:
        out_path = out_dir / f"{spec.asset_id}.aseprite"
        build_source(spec, out_path, aseprite)
        written.append(out_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--specs", type=Path, default=ROOT / "sources" / "calibration-v0" / "specs"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "sources" / "calibration-v0"
    )
    parser.add_argument("--aseprite", type=Path, default=DEFAULT_ASEPRITE)
    args = parser.parse_args(argv)
    try:
        written = build_all(args.specs.resolve(), args.out.resolve(), args.aseprite)
    except (SpecError, BuildError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    for path in written:
        printable = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        print(f"built {printable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
