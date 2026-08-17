"""Load and validate native pixel-grid specs (the text source of truth).

A spec is a JSON object describing one 32x32 creature sprite as a character
grid plus a palette map. Every downstream tool (Aseprite source builder,
deterministic exporter verification, contact sheet) consumes specs through
this module so pixel truth exists in exactly one reviewable place.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
ASSET_ID_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
TRANSPARENT = "."
CANVAS = 32
BOUNDS = (2, 2, 29, 29)
ANCHOR = (16, 30)
MAX_COLORS = 8


class SpecError(ValueError):
    """A malformed or contract-violating pixel spec."""


@dataclass(frozen=True)
class PixelSpec:
    asset_id: str
    palette: dict[str, str]
    grid: tuple[str, ...]

    @property
    def used_colors(self) -> tuple[str, ...]:
        """Opaque colors actually placed on the grid, sorted."""
        used = {char for row in self.grid for char in row if char != TRANSPARENT}
        return tuple(sorted(self.palette[char] for char in used))

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """Inclusive (left, top, right, bottom) of occupied pixels."""
        xs = [x for y, row in enumerate(self.grid) for x, c in enumerate(row) if c != TRANSPARENT]
        ys = [y for y, row in enumerate(self.grid) for x, c in enumerate(row) if c != TRANSPARENT]
        return min(xs), min(ys), max(xs), max(ys)

    def rgba(self, x: int, y: int) -> tuple[int, int, int, int]:
        """Hard-alpha RGBA for one pixel."""
        char = self.grid[y][x]
        if char == TRANSPARENT:
            return (0, 0, 0, 0)
        color = self.palette[char]
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)

    def opaque_pixels(self) -> list[tuple[int, int, tuple[int, int, int]]]:
        """(x, y, (r, g, b)) for every opaque pixel, row-major order."""
        pixels: list[tuple[int, int, tuple[int, int, int]]] = []
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char != TRANSPARENT:
                    r, g, b, _ = self.rgba(x, y)
                    pixels.append((x, y, (r, g, b)))
        return pixels


def _validate_palette(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        raise SpecError("palette must be a non-empty object")
    for char, color in raw.items():
        if not isinstance(char, str) or len(char) != 1 or char == TRANSPARENT:
            raise SpecError(f"palette key {char!r} must be a single character, not '.'")
        if not isinstance(color, str) or COLOR_RE.fullmatch(color) is None:
            raise SpecError(f"palette[{char!r}] must be lowercase #rrggbb")
    colors = list(raw.values())
    if len(set(colors)) != len(colors):
        raise SpecError("palette colors must be unique")
    if len(colors) > MAX_COLORS:
        raise SpecError(f"palette exceeds {MAX_COLORS} opaque colors")
    return dict(raw)


def _validate_grid(raw: object, palette: dict[str, str]) -> tuple[str, ...]:
    if not isinstance(raw, list) or len(raw) != CANVAS:
        raise SpecError(f"grid must contain exactly {CANVAS} rows")
    for y, row in enumerate(raw):
        if not isinstance(row, str) or len(row) != CANVAS:
            raise SpecError(f"grid row {y} must be a {CANVAS}-character string")
        for x, char in enumerate(row):
            if char != TRANSPARENT and char not in palette:
                raise SpecError(f"grid[{y}][{x}] uses undeclared palette key {char!r}")
    return tuple(raw)


def _validate_occupancy(grid: tuple[str, ...], palette: dict[str, str]) -> None:
    occupied = [
        (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c != TRANSPARENT
    ]
    if not occupied:
        raise SpecError("grid cannot be fully transparent")
    left = min(x for x, _ in occupied)
    top = min(y for _, y in occupied)
    right = max(x for x, _ in occupied)
    bottom = max(y for _, y in occupied)
    min_x, min_y, max_x, max_y = BOUNDS
    if not (min_x <= left and min_y <= top and right <= max_x and bottom <= max_y):
        raise SpecError(
            f"occupied bbox ({left}, {top}, {right}, {bottom}) exceeds {list(BOUNDS)}"
        )
    used = {char for row in grid for char in row if char != TRANSPARENT}
    unused = sorted(set(palette) - used)
    if unused:
        raise SpecError(f"palette declares unused keys: {unused}")


def load_spec(path: Path) -> PixelSpec:
    """Load one spec JSON, enforcing the phase-0 creature contract."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SpecError(f"cannot read spec JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise SpecError("spec root must be an object")
    asset_id = raw.get("asset_id")
    if not isinstance(asset_id, str) or ASSET_ID_RE.fullmatch(asset_id) is None:
        raise SpecError("asset_id must be lowercase generic snake_case")
    if raw.get("kind") != "creature":
        raise SpecError("kind must be creature")
    if raw.get("anchor") != list(ANCHOR):
        raise SpecError(f"anchor must be {list(ANCHOR)}")
    palette = _validate_palette(raw.get("palette"))
    grid = _validate_grid(raw.get("grid"), palette)
    _validate_occupancy(grid, palette)
    return PixelSpec(asset_id=asset_id, palette=palette, grid=grid)


def load_spec_dir(directory: Path) -> list[PixelSpec]:
    """Load every *.json spec in a directory, sorted by filename."""
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise SpecError(f"no specs found under {directory}")
    specs = [load_spec(path) for path in paths]
    ids = [spec.asset_id for spec in specs]
    if len(set(ids)) != len(ids):
        raise SpecError("duplicate asset_id across specs")
    return specs
