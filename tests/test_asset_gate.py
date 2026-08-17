from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from asset_gate import (
    main,
    sha256_file,
    validate_release,
    validate_runtime_baseline,
    validate_toolchain_baseline,
)
from png_reader import PngError, inspect_png


def _chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def write_rgba_png(
    path: Path,
    width: int,
    height: int,
    pixels: bytes,
    *,
    filter_type: int = 0,
) -> None:
    if len(pixels) != width * height * 4:
        raise ValueError("pixel byte count does not match dimensions")
    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(filter_type)
        rows.extend(pixels[y * stride : (y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(rows), level=9))
    data += _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def creature_pixels(
    *,
    color: tuple[int, int, int] = (235, 120, 40),
    alpha: int = 255,
    left: int = 2,
) -> bytes:
    pixels = bytearray(32 * 32 * 4)
    for y in range(2, 30):
        for x in range(left, 30):
            offset = (y * 32 + x) * 4
            pixels[offset : offset + 4] = bytes((*color, alpha))
    return bytes(pixels)


class AssetGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "sources" / "calibration" / "player_1.aseprite"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"native-source-v1")
        self.source = source
        exporter = self.root / "tools" / "export_assets.py"
        exporter.parent.mkdir()
        exporter.write_text("# deterministic exporter\n", encoding="utf-8")
        self.exporter = exporter
        self.export = self.root / "exports" / "calibration-v0" / "player_1_lane_a.png"
        write_rgba_png(self.export, 32, 32, creature_pixels())
        self.manifest_path = self.export.parent / "release.json"
        self.manifest = {
            "contract_version": 1,
            "release_id": "calibration-v0",
            "source": {
                "commit": "a" * 40,
                "files": [
                    {
                        "path": "sources/calibration/player_1.aseprite",
                        "sha256": sha256_file(source),
                    }
                ],
            },
            "target": {
                "game_commit": "219121d3ca2cfabfd39c3a1533b8227b52f68617",
                "runtime_baseline": "manifests/runtime-baseline.json",
            },
            "toolchain": {
                "baseline": "manifests/toolchain-baseline.json",
                "exporter_path": "tools/export_assets.py",
                "exporter_sha256": sha256_file(exporter),
            },
            "exports": [
                {
                    "asset_id": "player_1_lane_a",
                    "kind": "creature",
                    "path": "exports/calibration-v0/player_1_lane_a.png",
                    "sha256": sha256_file(self.export),
                    "width": 32,
                    "height": 32,
                    "anchor": [16, 30],
                    "palette": ["#eb7828"],
                    "provenance": {
                        "origin": "human",
                        "author": "test",
                        "created": "2026-08-17",
                        "rights": "private-project",
                    },
                }
            ],
        }
        self._write_manifest()

    def _write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def _refresh_export_hash(self) -> None:
        self.manifest["exports"][0]["sha256"] = sha256_file(self.export)
        self._write_manifest()

    def test_valid_release_passes(self) -> None:
        self.assertEqual([], validate_release(self.manifest_path, self.root))
        info = inspect_png(self.export)
        self.assertEqual((2, 2, 29, 29), info.bbox)
        self.assertEqual(frozenset({"#eb7828"}), info.opaque_colors)

    def test_rejects_soft_alpha(self) -> None:
        write_rgba_png(self.export, 32, 32, creature_pixels(alpha=128))
        self._refresh_export_hash()
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("alpha must be binary" in error for error in errors), errors)

    def test_rejects_undeclared_color(self) -> None:
        write_rgba_png(self.export, 32, 32, creature_pixels(color=(1, 2, 3)))
        self._refresh_export_hash()
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("undeclared colors" in error for error in errors), errors)

    def test_rejects_creature_overhang_and_empty_creature(self) -> None:
        write_rgba_png(self.export, 32, 32, creature_pixels(left=1))
        self._refresh_export_hash()
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("exceeds [2, 2, 29, 29]" in error for error in errors), errors)

        write_rgba_png(self.export, 32, 32, bytes(32 * 32 * 4))
        self._refresh_export_hash()
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("cannot be fully transparent" in error for error in errors), errors)

    def test_rejects_corrupt_png_crc(self) -> None:
        data = bytearray(self.export.read_bytes())
        data[-5] ^= 0x01
        self.export.write_bytes(data)
        self._refresh_export_hash()
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("chunk CRC" in error for error in errors), errors)

    def test_reports_invalid_release_structure(self) -> None:
        self.manifest = {
            "contract_version": 2,
            "release_id": "Bad ID",
            "source": {"commit": "short", "files": []},
            "target": {},
            "toolchain": {},
            "exports": [],
        }
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        for expected in (
            "contract_version must be 1",
            "release_id must use lowercase",
            "source.commit must be",
            "source.files must contain",
            "target.game_commit must be",
            "target.runtime_baseline",
            "toolchain.baseline",
            "toolchain.exporter_sha256",
            "exports must contain",
        ):
            self.assertIn(expected, errors)

    def test_reports_source_path_and_hash_failures(self) -> None:
        source_entry = self.manifest["source"]["files"][0]
        source_entry["path"] = "../outside.aseprite"
        source_entry["sha256"] = "bad"
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("path must stay inside", errors)
        self.assertIn("sha256 must be lowercase", errors)

        source_entry["path"] = "sources/calibration/missing.aseprite"
        source_entry["sha256"] = "0" * 64
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("path does not exist", errors)

    def test_reports_export_contract_and_provenance_failures(self) -> None:
        export = self.manifest["exports"][0]
        export.update(
            {
                "asset_id": "Bad ID",
                "kind": "unknown",
                "path": "wrong\\path.png",
                "sha256": "bad",
                "width": "32",
                "height": 31,
                "anchor": [0, 0],
                "palette": ["#FFFFFF", "#FFFFFF"],
                "provenance": {
                    "origin": "ai_reconstruction",
                    "author": "",
                    "created": "yesterday",
                    "rights": "",
                },
            }
        )
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        for expected in (
            "asset_id must be lowercase",
            "kind must be creature",
            "width and height must be integers",
            "palette colors must be unique lowercase",
            "provenance.author",
            "provenance.created must use",
            "AI reconstruction requires provenance.provider",
            "path must be a forward-slash",
            "sha256 must be lowercase",
        ):
            self.assertIn(expected, errors)

    def test_reports_toolchain_exporter_failures(self) -> None:
        toolchain = self.manifest["toolchain"]
        toolchain["exporter_sha256"] = "0" * 64
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("does not match the exporter", errors)

        toolchain["exporter_path"] = "tools/missing.py"
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("exporter_path does not exist", errors)

    def test_reports_duplicate_export_identity(self) -> None:
        self.manifest["exports"].append(copy.deepcopy(self.manifest["exports"][0]))
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("asset_id is duplicated", errors)
        self.assertIn("path is duplicated", errors)

    def test_reports_export_hash_dimension_and_missing_file(self) -> None:
        export = self.manifest["exports"][0]
        export["sha256"] = "0" * 64
        export["width"] = 31
        self._write_manifest()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("sha256 does not match", errors)
        self.assertIn("exports must be 32x32", errors)
        self.assertIn("PNG is 32x32, not 31x32", errors)

        self.export.unlink()
        errors = "\n".join(validate_release(self.manifest_path, self.root))
        self.assertIn("path does not exist", errors)

    def test_rejects_malformed_json(self) -> None:
        self.manifest_path.write_text("[not-json", encoding="utf-8")
        errors = validate_release(self.manifest_path, self.root)
        self.assertTrue(any("cannot read JSON" in error for error in errors), errors)

    def test_lf_normalized_hash_is_cross_platform(self) -> None:
        path = self.root / "line-endings.txt"
        path.write_bytes(b"one\r\ntwo\r\n")
        expected = hashlib.sha256(b"one\ntwo\n").hexdigest()
        self.assertEqual(expected, sha256_file(path, normalize_lf=True))

    def test_checked_in_baselines_match_live_game_and_aseprite(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        game_root = repository_root.parent / "game-two"
        aseprite = Path("C:/tools/aseprite/build/bin/aseprite.exe")
        self.assertEqual([], validate_runtime_baseline(repository_root))
        self.assertEqual([], validate_toolchain_baseline(repository_root))
        if not game_root.is_dir():
            self.skipTest("real sibling game-two checkout is unavailable")
        self.assertEqual([], validate_runtime_baseline(repository_root, game_root))
        if not aseprite.is_file():
            self.skipTest("real Aseprite executable is unavailable")
        self.assertEqual([], validate_toolchain_baseline(repository_root, aseprite))

    def test_runtime_baseline_detects_commit_and_source_drift(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        game_root = repository_root.parent / "game-two"
        if not game_root.is_dir():
            self.skipTest("real sibling game-two checkout is unavailable")
        baseline_dir = self.root / "manifests"
        baseline_dir.mkdir()
        baseline = json.loads(
            (repository_root / "manifests" / "runtime-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        baseline["game_commit"] = "0" * 40
        baseline["source_files"][0]["sha256_lf"] = "0" * 64
        (baseline_dir / "runtime-baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )
        errors = "\n".join(validate_runtime_baseline(self.root, game_root))
        self.assertIn("game HEAD is", errors)
        self.assertIn("sha256_lf does not match", errors)

    def test_main_passes_live_baseline_and_reports_invalid_baseline(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        game_root = repository_root.parent / "game-two"
        aseprite = Path("C:/tools/aseprite/build/bin/aseprite.exe")
        args = ["--root", str(repository_root)]
        if game_root.is_dir():
            args.extend(["--game-root", str(game_root)])
        if aseprite.is_file():
            args.extend(["--aseprite", str(aseprite)])
        self.assertEqual(0, main(args))

        baseline_dir = self.root / "manifests"
        baseline_dir.mkdir()
        (baseline_dir / "runtime-baseline.json").write_text("{}", encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(1, main(["--root", str(self.root)]))
        self.assertIn("Asset gate failed", stderr.getvalue())


class PngReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.png"

    def test_decodes_all_standard_row_filters(self) -> None:
        pixel = bytes((1, 2, 3, 255))
        for filter_type in range(5):
            with self.subTest(filter_type=filter_type):
                write_rgba_png(self.path, 1, 1, pixel, filter_type=filter_type)
                info = inspect_png(self.path)
                self.assertEqual(frozenset({"#010203"}), info.opaque_colors)

    def test_rejects_unsupported_row_filter(self) -> None:
        write_rgba_png(self.path, 1, 1, bytes((1, 2, 3, 255)), filter_type=5)
        with self.assertRaisesRegex(PngError, "unsupported PNG row filter"):
            inspect_png(self.path)

    def test_rejects_non_png_apng_and_trailing_bytes(self) -> None:
        self.path.write_bytes(b"not png")
        with self.assertRaisesRegex(PngError, "not a PNG"):
            inspect_png(self.path)

        header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
        data = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
        data += _chunk(b"acTL", struct.pack(">II", 1, 0))
        data += _chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03\xff"))
        data += _chunk(b"IEND", b"")
        self.path.write_bytes(data)
        with self.assertRaisesRegex(PngError, "animated PNG"):
            inspect_png(self.path)

        write_rgba_png(self.path, 1, 1, bytes((1, 2, 3, 255)))
        self.path.write_bytes(self.path.read_bytes() + b"trailing")
        with self.assertRaisesRegex(PngError, "trailing bytes"):
            inspect_png(self.path)

    def test_rejects_wrong_color_type_and_missing_chunks(self) -> None:
        header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        data = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
        data += _chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03"))
        data += _chunk(b"IEND", b"")
        self.path.write_bytes(data)
        with self.assertRaisesRegex(PngError, "8-bit RGBA"):
            inspect_png(self.path)

        self.path.write_bytes(b"\x89PNG\r\n\x1a\n")
        with self.assertRaisesRegex(PngError, "requires IHDR"):
            inspect_png(self.path)


if __name__ == "__main__":
    unittest.main()
