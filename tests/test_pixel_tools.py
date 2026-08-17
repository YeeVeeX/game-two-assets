from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from pixel_spec import ANCHOR, PixelSpec, SpecError, load_spec, load_spec_dir
from png_reader import inspect_png, read_rgba
from png_writer import Rgba8Canvas

REPO = Path(__file__).resolve().parents[1]
ASEPRITE = Path("C:/tools/aseprite/build/bin/aseprite.exe")


def valid_spec_dict() -> dict:
    grid = ["." * 32 for _ in range(32)]
    grid[4] = "..bbbb" + "." * 26
    grid[5] = "..bkkb" + "." * 26
    grid[6] = "..bbbb" + "." * 26
    return {
        "asset_id": "player_1_lane_a_idle_down",
        "kind": "creature",
        "anchor": list(ANCHOR),
        "palette": {"b": "#eb7828", "k": "#140e0c"},
        "grid": grid,
    }


def write_spec(directory: Path, spec: dict, name: str | None = None) -> Path:
    path = directory / f"{name or spec['asset_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec), encoding="utf-8")
    return path


class PixelSpecTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def load(self, spec: dict) -> PixelSpec:
        return load_spec(write_spec(self.dir, spec))

    def test_valid_spec_loads_with_derived_properties(self) -> None:
        spec = self.load(valid_spec_dict())
        self.assertEqual("player_1_lane_a_idle_down", spec.asset_id)
        self.assertEqual((2, 4, 5, 6), spec.bbox)
        self.assertEqual(("#140e0c", "#eb7828"), spec.used_colors)
        self.assertEqual((235, 120, 40, 255), spec.rgba(2, 4))
        self.assertEqual((0, 0, 0, 0), spec.rgba(0, 0))
        pixels = spec.opaque_pixels()
        self.assertEqual((2, 4, (235, 120, 40)), pixels[0])
        self.assertEqual(12, len(pixels))

    def test_rejects_structural_failures(self) -> None:
        cases = [
            ({"asset_id": "Bad Id"}, "asset_id"),
            ({"kind": "tile"}, "kind must be creature"),
            ({"anchor": [0, 0]}, "anchor must be"),
            ({"palette": {}}, "palette must be a non-empty object"),
            ({"palette": {"bb": "#eb7828"}}, "single character"),
            ({"palette": {".": "#eb7828"}}, "single character"),
            ({"palette": {"b": "#EB7828"}}, "lowercase #rrggbb"),
            ({"palette": {"b": "#eb7828", "k": "#eb7828"}}, "unique"),
        ]
        for override, message in cases:
            with self.subTest(override=override):
                spec = valid_spec_dict() | override
                if "palette" in override:
                    spec["grid"] = ["." * 32] * 32
                with self.assertRaisesRegex(SpecError, message):
                    self.load(spec)

    def test_rejects_more_than_eight_colors(self) -> None:
        spec = valid_spec_dict()
        spec["palette"] = {
            chr(ord("a") + i): f"#{i:02x}{i:02x}{i:02x}" for i in range(9)
        }
        with self.assertRaisesRegex(SpecError, "exceeds 8"):
            self.load(spec)

    def test_rejects_grid_failures(self) -> None:
        spec = valid_spec_dict()
        spec["grid"] = ["." * 32] * 31
        with self.assertRaisesRegex(SpecError, "exactly 32 rows"):
            self.load(spec)

        spec = valid_spec_dict()
        spec["grid"][0] = "." * 31
        with self.assertRaisesRegex(SpecError, "32-character string"):
            self.load(spec)

        spec = valid_spec_dict()
        spec["grid"][4] = "..bxbb" + "." * 26
        with self.assertRaisesRegex(SpecError, "undeclared palette key"):
            self.load(spec)

    def test_rejects_occupancy_failures(self) -> None:
        spec = valid_spec_dict()
        spec["grid"] = ["." * 32] * 32
        with self.assertRaisesRegex(SpecError, "fully transparent"):
            self.load(spec)

        spec = valid_spec_dict()
        spec["grid"][1] = "..b" + "." * 29  # row 1 < top bound 2
        with self.assertRaisesRegex(SpecError, "exceeds"):
            self.load(spec)

        spec = valid_spec_dict()
        spec["grid"][5] = "..bbbb" + "." * 26  # 'k' declared but unused
        with self.assertRaisesRegex(SpecError, "unused keys"):
            self.load(spec)

    def test_rejects_unreadable_and_non_object_json(self) -> None:
        path = self.dir / "broken.json"
        path.write_text("[1, 2", encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "cannot read spec JSON"):
            load_spec(path)
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "root must be an object"):
            load_spec(path)

    def test_load_spec_dir_sorts_and_rejects_duplicates_and_empty(self) -> None:
        first = valid_spec_dict()
        second = valid_spec_dict() | {"asset_id": "player_1_lane_b_idle_down"}
        write_spec(self.dir, second)
        write_spec(self.dir, first)
        specs = load_spec_dir(self.dir)
        self.assertEqual(
            ["player_1_lane_a_idle_down", "player_1_lane_b_idle_down"],
            [spec.asset_id for spec in specs],
        )

        write_spec(self.dir, first, name="duplicate")
        with self.assertRaisesRegex(SpecError, "duplicate asset_id"):
            load_spec_dir(self.dir)

        empty = self.dir / "empty"
        empty.mkdir()
        with self.assertRaisesRegex(SpecError, "no specs found"):
            load_spec_dir(empty)


class PngWriterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "out.png"

    def test_roundtrips_through_strict_reader(self) -> None:
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(2, 2, 28, 28, (235, 120, 40, 255))
        canvas.save(self.path)
        info = inspect_png(self.path)
        self.assertEqual((32, 32), (info.width, info.height))
        self.assertEqual(frozenset({"#eb7828"}), info.opaque_colors)
        self.assertEqual((2, 2, 29, 29), info.bbox)

    def test_put_ignores_transparent_and_out_of_bounds(self) -> None:
        canvas = Rgba8Canvas(4, 4, fill=(1, 2, 3, 255))
        canvas.put(0, 0, (9, 9, 9, 0))
        canvas.put(-1, 0, (9, 9, 9, 255))
        canvas.put(0, 4, (9, 9, 9, 255))
        self.assertEqual((1, 2, 3, 255), canvas.get(0, 0))

    def test_blit_scaled_nearest_neighbor(self) -> None:
        canvas = Rgba8Canvas(8, 8)
        canvas.blit_scaled([(1, 1, (10, 20, 30))], 0, 0, 2)
        for x, y in ((2, 2), (3, 2), (2, 3), (3, 3)):
            self.assertEqual((10, 20, 30, 255), canvas.get(x, y))
        self.assertEqual((0, 0, 0, 0), canvas.get(1, 1))
        with self.assertRaises(ValueError):
            canvas.blit_scaled([], 0, 0, 0)

    def test_rejects_empty_canvas(self) -> None:
        with self.assertRaises(ValueError):
            Rgba8Canvas(0, 4)

    def test_encoding_is_deterministic(self) -> None:
        one = Rgba8Canvas(16, 16, fill=(5, 6, 7, 255)).encode()
        two = Rgba8Canvas(16, 16, fill=(5, 6, 7, 255)).encode()
        self.assertEqual(one, two)

    def test_read_rgba_exposes_pixels(self) -> None:
        canvas = Rgba8Canvas(2, 1)
        canvas.put(1, 0, (7, 8, 9, 255))
        canvas.save(self.path)
        width, height, raw = read_rgba(self.path)
        self.assertEqual((2, 1), (width, height))
        self.assertEqual(bytes((0, 0, 0, 0, 7, 8, 9, 255)), raw)


class BuildAndExportLiveTest(unittest.TestCase):
    """Real Aseprite round-trip: spec -> .aseprite -> PNG -> pixel verification."""

    def setUp(self) -> None:
        if not ASEPRITE.is_file():
            self.skipTest("real Aseprite executable is unavailable")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec_dir = self.root / "specs"
        write_spec(self.spec_dir, valid_spec_dict())

    def test_full_chain_builds_exports_and_verifies(self) -> None:
        import build_sources
        import export_assets

        sources = self.root / "sources"
        exports = self.root / "exports"
        built = build_sources.build_all(self.spec_dir, sources, ASEPRITE)
        self.assertEqual(1, len(built))
        self.assertTrue(built[0].is_file())

        written = export_assets.export_release(self.spec_dir, sources, exports, ASEPRITE)
        self.assertEqual(1, len(written))
        info = inspect_png(written[0])
        self.assertEqual(frozenset({"#eb7828", "#140e0c"}), info.opaque_colors)
        self.assertEqual((2, 4, 5, 6), info.bbox)

        # determinism: exporting again produces identical bytes
        first = written[0].read_bytes()
        export_assets.export_release(self.spec_dir, sources, exports, ASEPRITE)
        self.assertEqual(first, written[0].read_bytes())

    def test_exporter_rejects_pixel_drift(self) -> None:
        import export_assets

        spec = load_spec(self.spec_dir / "player_1_lane_a_idle_down.json")
        drifted = self.root / "drifted.png"
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(2, 4, 4, 3, (235, 120, 40, 255))  # wrong: no accent color
        canvas.save(drifted)
        with self.assertRaisesRegex(export_assets.ExportError, "!= spec colors"):
            export_assets.verify_against_spec(drifted, spec)

        wrong_size = self.root / "wrong-size.png"
        Rgba8Canvas(16, 16, fill=(1, 1, 1, 255)).save(wrong_size)
        with self.assertRaisesRegex(export_assets.ExportError, "not 32x32"):
            export_assets.verify_against_spec(wrong_size, spec)

    def test_bbox_drift_is_rejected(self) -> None:
        import export_assets

        spec = load_spec(self.spec_dir / "player_1_lane_a_idle_down.json")
        shifted = self.root / "shifted.png"
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(3, 4, 4, 3, (235, 120, 40, 255))
        canvas.fill_rect(4, 5, 2, 1, (20, 14, 12, 255))
        canvas.save(shifted)
        with self.assertRaisesRegex(export_assets.ExportError, "bbox"):
            export_assets.verify_against_spec(shifted, spec)

    def test_export_errors_on_missing_source_or_bad_executable(self) -> None:
        import build_sources
        import export_assets

        with self.assertRaisesRegex(export_assets.ExportError, "missing native source"):
            export_assets.export_png(self.root / "nope.aseprite", self.root / "o.png", ASEPRITE)

        spec = load_spec(self.spec_dir / "player_1_lane_a_idle_down.json")
        with self.assertRaisesRegex(build_sources.BuildError, "cannot execute"):
            build_sources.build_source(spec, self.root / "x.aseprite", self.root / "missing.exe")

    def test_lua_data_chunk_is_deterministic_and_complete(self) -> None:
        import build_sources

        spec = load_spec(self.spec_dir / "player_1_lane_a_idle_down.json")
        chunk = build_sources.lua_data_chunk(spec)
        self.assertEqual(chunk, build_sources.lua_data_chunk(spec))
        self.assertIn("{2, 4, 235, 120, 40},", chunk)
        self.assertIn("{4, 5, 20, 14, 12},", chunk)
        self.assertEqual(12, chunk.count("},") - 1)  # 12 pixels + closing table

    def test_build_main_reports_failure_for_missing_specs(self) -> None:
        import build_sources

        status = build_sources.main(
            ["--specs", str(self.root / "missing"), "--out", str(self.root)]
        )
        self.assertEqual(1, status)

    def test_export_main_reports_failure_for_missing_sources(self) -> None:
        import export_assets

        status = export_assets.main(
            [
                "--specs", str(self.spec_dir),
                "--sources", str(self.root / "nowhere"),
                "--out", str(self.root / "exports"),
                "--aseprite", str(ASEPRITE),
            ]
        )
        self.assertEqual(1, status)


class ContactSheetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        import make_contact_sheet

        self.tool = make_contact_sheet
        self.reference = self.tool.load_reference(
            REPO / "manifests" / "render-reference.json"
        )
        self.exports = self.root / "exports"
        self.exports.mkdir()
        for _, key, _ in self.tool.COLUMNS:
            if key == "baseline":
                continue
            canvas = Rgba8Canvas(32, 32)
            canvas.fill_rect(4, 4, 20, 20, (235, 120, 40, 255))
            canvas.fill_rect(6, 6, 4, 4, (20, 14, 12, 255))
            canvas.save(self.exports / f"{key}.png")

    def test_sheet_is_deterministic_and_correctly_composed(self) -> None:
        sheet_one = self.tool.build_sheet(self.exports, self.reference)
        sheet_two = self.tool.build_sheet(self.exports, self.reference)
        self.assertEqual(sheet_one.encode(), sheet_two.encode())

        zone1 = self.reference["zones"]["zone_1"]
        # wall tile at the first MAIN cell's top-left
        x0, y0 = self.tool.MARGIN_LEFT, self.tool.MARGIN_TOP
        self.assertEqual((*zone1["wall"], 255), sheet_one.get(x0 + 5, y0 + 5))
        # gold transition center right of it
        self.assertEqual(
            (235, 190, 90, 255), sheet_one.get(x0 + 32 + 16, y0 + 16)
        )
        # baseline body pixel on the floor tile below
        self.assertEqual((235, 120, 40, 255), sheet_one.get(x0 + 16, y0 + 32 + 16))
        # telegraph swatch bone center
        self.assertEqual(
            (205, 198, 180, 255), sheet_one.get(x0 + 32 + 16, y0 + 32 + 16)
        )

    def test_ring_row_carries_possession_ring(self) -> None:
        sheet = self.tool.build_sheet(self.exports, self.reference)
        ring_y = self.tool.MARGIN_TOP + (64 + self.tool.GUTTER)
        # ring pixel: 3px outside the 28x28 body at tile offset (2,2)
        self.assertEqual(
            (255, 255, 255, 255),
            sheet.get(self.tool.MARGIN_LEFT + 1, ring_y + 32 + 16),
        )

    def test_primitive_sprite_notch_faces_correctly(self) -> None:
        down = self.tool.primitive_sprite(self.reference, "down")
        right = self.tool.primitive_sprite(self.reference, "right")
        down_notch = {(x, y) for x, y, rgb in down.pixels if rgb == (20, 14, 12)}
        right_notch = {(x, y) for x, y, rgb in right.pixels if rgb == (20, 14, 12)}
        self.assertIn((16, 29), down_notch)
        self.assertIn((29, 16), right_notch)
        self.assertNotIn((29, 16), down_notch)

    def test_sprite_from_png_rejects_wrong_size(self) -> None:
        bad = self.root / "bad.png"
        Rgba8Canvas(16, 16, fill=(1, 1, 1, 255)).save(bad)
        with self.assertRaisesRegex(ValueError, "expects 32x32"):
            self.tool.sprite_from_png(bad)

    def test_main_writes_sheet(self) -> None:
        out = self.root / "sheet.png"
        status = self.tool.main(
            [
                "--exports", str(self.exports),
                "--reference", str(REPO / "manifests" / "render-reference.json"),
                "--out", str(out),
            ]
        )
        self.assertEqual(0, status)
        info = inspect_png(out)
        self.assertGreater(info.width, 600)


class MakeReleaseTest(unittest.TestCase):
    """Real git + real files: the emitted manifest must satisfy the asset gate."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        import make_release

        self.tool = make_release
        spec_dir = self.root / "sources" / "calibration-v0" / "specs"
        spec = valid_spec_dict()
        write_spec(spec_dir, spec)
        (self.root / "sources" / "calibration-v0" / f"{spec['asset_id']}.aseprite").write_bytes(
            b"native-source"
        )
        export_dir = self.root / "exports" / "calibration-v0"
        export_dir.mkdir(parents=True)
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(2, 4, 4, 3, (235, 120, 40, 255))
        canvas.fill_rect(4, 5, 2, 1, (20, 14, 12, 255))
        canvas.save(export_dir / f"{spec['asset_id']}.png")
        tools_dir = self.root / "tools"
        tools_dir.mkdir()
        (tools_dir / "export_assets.py").write_text("# exporter\n", encoding="utf-8")
        manifests = self.root / "manifests"
        manifests.mkdir()
        (manifests / "runtime-baseline.json").write_text(
            json.dumps({"game_commit": "219121d3ca2cfabfd39c3a1533b8227b52f68617"}),
            encoding="utf-8",
        )

    def _git(self, *arguments: str) -> str:
        from make_release import _git_env

        return subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True, capture_output=True, text=True, env=_git_env(),
        ).stdout.strip()

    def test_git_env_scrubs_hook_index_overrides(self) -> None:
        import os

        from make_release import _git_env

        os.environ["GIT_INDEX_FILE"] = "/tmp/poisoned-index"
        try:
            env = _git_env()
        finally:
            del os.environ["GIT_INDEX_FILE"]
        self.assertNotIn("GIT_INDEX_FILE", env)
        self.assertNotIn("GIT_DIR", env)

    def test_manifest_passes_the_asset_gate(self) -> None:
        from asset_gate import validate_release

        manifest = self.tool.build_manifest(self.root, "a" * 40, "calibration-v0")
        manifest_path = self.root / "exports" / "calibration-v0" / "release.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.assertEqual([], validate_release(manifest_path, self.root))
        self.assertEqual(
            ["#140e0c", "#eb7828"], manifest["exports"][0]["palette"]
        )

    def test_refuses_missing_files(self) -> None:
        (self.root / "exports" / "calibration-v0" / "player_1_lane_a_idle_down.png").unlink()
        with self.assertRaisesRegex(self.tool.ReleaseError, "missing export"):
            self.tool.build_manifest(self.root, "a" * 40, "calibration-v0")

        (self.root / "sources" / "calibration-v0" / "player_1_lane_a_idle_down.aseprite").unlink()
        with self.assertRaisesRegex(self.tool.ReleaseError, "missing native source"):
            self.tool.build_manifest(self.root, "a" * 40, "calibration-v0")

    def test_rejects_unknown_release_id(self) -> None:
        with self.assertRaisesRegex(self.tool.ReleaseError, "unknown release id"):
            self.tool.build_manifest(self.root, "a" * 40, "calibration-v9")

    def test_v1_registry_notes_idle_copy_provenance(self) -> None:
        spec_dir = self.root / "sources" / "calibration-v1" / "specs"
        spec = valid_spec_dict() | {"asset_id": "player_1_lane_b_walk_down_f3"}
        write_spec(spec_dir, spec)
        (self.root / "sources" / "calibration-v1" / f"{spec['asset_id']}.aseprite").write_bytes(
            b"native-source"
        )
        export_dir = self.root / "exports" / "calibration-v1"
        export_dir.mkdir(parents=True)
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(2, 4, 4, 3, (235, 120, 40, 255))
        canvas.fill_rect(4, 5, 2, 1, (20, 14, 12, 255))
        canvas.save(export_dir / f"{spec['asset_id']}.png")

        manifest = self.tool.build_manifest(self.root, "a" * 40, "calibration-v1")
        provenance = manifest["exports"][0]["provenance"]
        self.assertEqual("calibration-v1", manifest["release_id"])
        self.assertIn("copied forward verbatim", provenance["note"])
        self.assertIn("sprint 1", provenance["author"])

        from asset_gate import validate_release

        manifest_path = export_dir / "release.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.assertEqual([], validate_release(manifest_path, self.root))

    def test_source_commit_requires_clean_pinned_paths(self) -> None:
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "test")
        self._git("add", "sources", "tools", "manifests")
        self._git("commit", "-q", "-m", "sources")
        head = self._git("rev-parse", "HEAD")
        self.assertEqual(head, self.tool.source_commit(self.root))

        (self.root / "tools" / "export_assets.py").write_text("# drift\n", encoding="utf-8")
        with self.assertRaisesRegex(self.tool.ReleaseError, "differ from HEAD"):
            self.tool.source_commit(self.root)

    def test_main_writes_gate_valid_manifest(self) -> None:
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "test")
        self._git("add", "sources", "tools", "manifests")
        self._git("commit", "-q", "-m", "sources")
        status = self.tool.main(["--root", str(self.root), "--release", "calibration-v0"])
        self.assertEqual(0, status)
        manifest = json.loads(
            (self.root / "exports" / "calibration-v0" / "release.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(self._git("rev-parse", "HEAD"), manifest["source"]["commit"])

    def test_main_reports_refusal(self) -> None:
        arguments = [
            "--root", str(self.root), "--release", "calibration-v0", "--commit", "a" * 40,
        ]
        status = self.tool.main(arguments)
        self.assertEqual(0, status)
        (self.root / "exports" / "calibration-v0" / "player_1_lane_a_idle_down.png").unlink()
        status = self.tool.main(arguments)
        self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
