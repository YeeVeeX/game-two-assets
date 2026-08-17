"""Deterministic non-interlaced RGBA8 PNG writer (no timestamps, no ancillary chunks)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"
BYTES_PER_PIXEL = 4


class Rgba8Canvas:
    """A mutable RGBA8 pixel surface with hard-alpha compositing."""

    def __init__(self, width: int, height: int, fill: tuple[int, int, int, int] = (0, 0, 0, 0)):
        if width < 1 or height < 1:
            raise ValueError("canvas dimensions must be positive")
        self.width = width
        self.height = height
        self._pixels = bytearray(bytes(fill) * (width * height))

    def put(self, x: int, y: int, rgba: tuple[int, int, int, int]) -> None:
        """Set one pixel; alpha 0 writes are ignored (hard alpha, no blending)."""
        if rgba[3] == 0:
            return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        offset = (y * self.width + x) * BYTES_PER_PIXEL
        self._pixels[offset : offset + BYTES_PER_PIXEL] = bytes(rgba)

    def fill_rect(self, x: int, y: int, w: int, h: int, rgba: tuple[int, int, int, int]) -> None:
        for py in range(y, y + h):
            for px in range(x, x + w):
                self.put(px, py, rgba)

    def blit_scaled(
        self,
        pixels: list[tuple[int, int, tuple[int, int, int]]],
        dest_x: int,
        dest_y: int,
        scale: int,
    ) -> None:
        """Nearest-neighbor blit of opaque (x, y, rgb) pixels at an integer scale."""
        if scale < 1:
            raise ValueError("scale must be a positive integer")
        for sx, sy, (r, g, b) in pixels:
            self.fill_rect(dest_x + sx * scale, dest_y + sy * scale, scale, scale, (r, g, b, 255))

    def get(self, x: int, y: int) -> tuple[int, int, int, int]:
        offset = (y * self.width + x) * BYTES_PER_PIXEL
        return tuple(self._pixels[offset : offset + BYTES_PER_PIXEL])  # type: ignore[return-value]

    def encode(self) -> bytes:
        """Encode as a minimal deterministic PNG: IHDR, one IDAT, IEND."""
        stride = self.width * BYTES_PER_PIXEL
        raw = bytearray()
        for y in range(self.height):
            raw.append(0)  # filter type 0 on every row: deterministic, simple
            raw.extend(self._pixels[y * stride : (y + 1) * stride])
        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0)
        return (
            SIGNATURE
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
            + _chunk(b"IEND", b"")
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.encode())


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)
