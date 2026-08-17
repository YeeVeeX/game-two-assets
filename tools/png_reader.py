"""Minimal native-RGBA PNG inspector used by the asset gate."""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
BYTES_PER_PIXEL = 4


class PngError(ValueError):
    """A malformed PNG or unsupported export format."""


@dataclass(frozen=True)
class PngInfo:
    width: int
    height: int
    opaque_colors: frozenset[str]
    alpha_values: frozenset[int]
    bbox: tuple[int, int, int, int] | None


def _read_chunk(data: bytes, offset: int) -> tuple[bytes, bytes, int]:
    if offset + 12 > len(data):
        raise PngError("truncated PNG chunk")
    length = struct.unpack(">I", data[offset : offset + 4])[0]
    kind = data[offset + 4 : offset + 8]
    chunk_end = offset + 12 + length
    if chunk_end > len(data):
        raise PngError("PNG chunk exceeds file length")
    payload = data[offset + 8 : offset + 8 + length]
    expected_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
    actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    if actual_crc != expected_crc:
        raise PngError(f"invalid {kind.decode('ascii', 'replace')} chunk CRC")
    return kind, payload, chunk_end


def _apply_chunk(
    kind: bytes, payload: bytes, header: bytes | None, compressed: bytearray
) -> tuple[bytes | None, bool]:
    if kind == b"IHDR":
        if header is not None or len(payload) != 13:
            raise PngError("invalid or duplicate IHDR chunk")
        return payload, False
    if kind == b"IDAT":
        compressed.extend(payload)
        return header, False
    if kind == b"acTL":
        raise PngError("animated PNG is not allowed")
    if kind == b"IEND":
        if payload:
            raise PngError("invalid IEND chunk")
        return header, True
    return header, False


def _collect_image_chunks(data: bytes) -> tuple[bytes, bytes]:
    if not data.startswith(PNG_SIGNATURE):
        raise PngError("not a PNG file")
    offset = len(PNG_SIGNATURE)
    header: bytes | None = None
    compressed = bytearray()
    ended = False

    while offset < len(data) and not ended:
        kind, payload, offset = _read_chunk(data, offset)
        header, ended = _apply_chunk(kind, payload, header, compressed)

    if header is None or not compressed or not ended:
        raise PngError("PNG requires IHDR, IDAT, and IEND chunks")
    if offset != len(data):
        raise PngError("trailing bytes after IEND")
    return header, bytes(compressed)


def _decode_header(header: bytes) -> tuple[int, int]:
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if not (1 <= width <= 4096 and 1 <= height <= 4096):
        raise PngError("PNG dimensions are outside the supported range")
    if (bit_depth, color_type) != (8, 6):
        raise PngError("export must be 8-bit RGBA PNG (color type 6)")
    if (compression, filter_method, interlace) != (0, 0, 0):
        raise PngError("PNG must use standard compression/filtering and no interlace")
    return width, height


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distances = (
        (abs(estimate - left), left),
        (abs(estimate - up), up),
        (abs(estimate - upper_left), upper_left),
    )
    return min(distances, key=lambda pair: pair[0])[1]


def _predictor(filter_type: int, left: int, up: int, upper_left: int) -> int:
    if filter_type == 0:
        return 0
    if filter_type == 1:
        return left
    if filter_type == 2:
        return up
    if filter_type == 3:
        return (left + up) // 2
    if filter_type == 4:
        return _paeth(left, up, upper_left)
    raise PngError(f"unsupported PNG row filter {filter_type}")


def _decode_row(encoded: bytes, previous: bytes, filter_type: int) -> bytearray:
    decoded = bytearray(len(encoded))
    for index, value in enumerate(encoded):
        left = decoded[index - BYTES_PER_PIXEL] if index >= BYTES_PER_PIXEL else 0
        up = previous[index]
        upper_left = previous[index - BYTES_PER_PIXEL] if index >= BYTES_PER_PIXEL else 0
        decoded[index] = (value + _predictor(filter_type, left, up, upper_left)) & 0xFF
    return decoded


def _decode_pixels(compressed: bytes, width: int, height: int) -> bytes:
    stride = width * BYTES_PER_PIXEL
    try:
        raw = zlib.decompress(compressed)
    except zlib.error as exc:
        raise PngError(f"invalid PNG image data: {exc}") from exc
    expected_size = height * (stride + 1)
    if len(raw) != expected_size:
        raise PngError(f"decoded PNG has {len(raw)} bytes; expected {expected_size}")

    previous = bytes(stride)
    pixels = bytearray()
    for row_number in range(height):
        cursor = row_number * (stride + 1)
        filter_type = raw[cursor]
        encoded = raw[cursor + 1 : cursor + 1 + stride]
        previous = _decode_row(encoded, previous, filter_type)
        pixels.extend(previous)
    return bytes(pixels)


def _bounding_box(occupied: list[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    if not occupied:
        return None
    xs, ys = zip(*occupied, strict=True)
    return min(xs), min(ys), max(xs), max(ys)


def _summarize(pixels: bytes, width: int, height: int) -> PngInfo:
    alpha_values: set[int] = set()
    opaque_colors: set[str] = set()
    occupied: list[tuple[int, int]] = []
    for index in range(0, len(pixels), BYTES_PER_PIXEL):
        red, green, blue, alpha = pixels[index : index + BYTES_PER_PIXEL]
        alpha_values.add(alpha)
        pixel_number = index // BYTES_PER_PIXEL
        if alpha:
            occupied.append((pixel_number % width, pixel_number // width))
        if alpha == 255:
            opaque_colors.add(f"#{red:02x}{green:02x}{blue:02x}")
    return PngInfo(
        width=width,
        height=height,
        opaque_colors=frozenset(opaque_colors),
        alpha_values=frozenset(alpha_values),
        bbox=_bounding_box(occupied),
    )


def inspect_png(path: Path) -> PngInfo:
    header, compressed = _collect_image_chunks(path.read_bytes())
    width, height = _decode_header(header)
    return _summarize(_decode_pixels(compressed, width, height), width, height)


def read_rgba(path: Path) -> tuple[int, int, bytes]:
    """Decode a strict RGBA8 PNG to (width, height, raw RGBA bytes)."""
    header, compressed = _collect_image_chunks(path.read_bytes())
    width, height = _decode_header(header)
    return width, height, _decode_pixels(compressed, width, height)
