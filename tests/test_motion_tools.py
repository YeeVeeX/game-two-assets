from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_motion_sheet
import motion_metrics
from png_reader import inspect_png
from png_writer import Rgba8Canvas

REPO = Path(__file__).resolve().parents[1]
BODY = (235, 120, 40, 255)
ACCENT = (20, 14, 12, 255)


def write_frame(path: Path, x: int, y: int, width: int = 4, height: int = 4) -> None:
    """A minimal 32x32 export: body rect at (x, y) with one accent pixel."""
    canvas = Rgba8Canvas(32, 32)
    canvas.fill_rect(x, y, width, height, BODY)
    canvas.put(x + 1, y + 1, ACCENT)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


class SyntheticCycle(unittest.TestCase):
    """Shared fixture: idle at rows 24..27, frames with known deltas."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.exports = self.root / "exports"
        self.idles = self.root / "idles"
        for facing in motion_metrics.FACINGS:
            write_frame(self.idles / f"player_1_lane_b_idle_{facing}.png", 10, 24)
            positions = [(10, 24), (10, 23), (11, 24), (11, 23)]
            for index, (x, y) in enumerate(positions):
                write_frame(
                    self.exports / f"player_1_lane_b_walk_{facing}_f{index}.png", x, y
                )


class MotionMetricsTest(SyntheticCycle):
    def test_frame_and_pair_numbers_are_exact(self) -> None:
        report = motion_metrics.build_report(self.exports, self.idles)
        down = report["facings"]["down"]

        self.assertEqual(16, down["idle"]["mass"])
        self.assertEqual(27, down["idle"]["feet_row"])
        f1 = down["frames"][1]
        self.assertEqual([10, 23, 13, 26], f1["bbox"])
        self.assertEqual(-1, f1["feet_row_delta_vs_idle"])
        self.assertEqual(0.0, f1["mass_drift_vs_idle_pct"])
        self.assertEqual([11.5, 25.5], down["frames"][0]["centroid"])

        # f0 (10,24) -> f1 (10,23): shifted up one row => XOR 8 of union 20
        pair_01 = down["pairs"][0]
        self.assertEqual("f0->f1", pair_01["pair"])
        self.assertEqual(8, pair_01["silhouette_changed_px"])
        self.assertEqual(20, pair_01["union_px"])
        self.assertEqual(40.0, pair_01["popping_pct"])
        # overlap rows keep colors except accent misalignment => 2 recolored
        self.assertEqual(2, pair_01["recolored_px"])
        # f3 (11,23) -> f0 (10,24): diagonal shift, XOR 14 of union 23
        self.assertEqual(60.87, down["pairs"][3]["popping_pct"])
        self.assertEqual(60.87, down["summary"]["max_popping_pct"])
        self.assertEqual(1, down["summary"]["max_abs_feet_row_delta"])
        self.assertIn("idle_cross_facing", report["reference"])

    def test_check_passes_within_tolerance_and_output_is_deterministic(self) -> None:
        report = motion_metrics.build_report(self.exports, self.idles)
        self.assertEqual([], motion_metrics.check_report(report))

        out_one = self.root / "one.json"
        out_two = self.root / "two.json"
        for out in (out_one, out_two):
            status = motion_metrics.main(
                ["--exports", str(self.exports), "--idle-exports", str(self.idles),
                 "--out", str(out), "--check"]
            )
            self.assertEqual(0, status)
        self.assertEqual(out_one.read_bytes(), out_two.read_bytes())
        self.assertIn("popping_pct", out_one.read_text(encoding="utf-8"))

    def test_check_fails_on_feet_drift(self) -> None:
        write_frame(self.exports / "player_1_lane_b_walk_down_f2.png", 10, 20)
        report = motion_metrics.build_report(self.exports, self.idles)
        failures = motion_metrics.check_report(report)
        self.assertEqual(1, len(failures))
        self.assertIn("feet-contact row drifts 4px", failures[0])
        status = motion_metrics.main(
            ["--exports", str(self.exports), "--idle-exports", str(self.idles),
             "--out", str(self.root / "r.json"), "--check"]
        )
        self.assertEqual(1, status)

    def test_check_fails_on_static_pair(self) -> None:
        write_frame(self.exports / "player_1_lane_b_walk_down_f1.png", 10, 24)
        write_frame(self.exports / "player_1_lane_b_walk_down_f2.png", 10, 24)
        report = motion_metrics.build_report(self.exports, self.idles)
        failures = motion_metrics.check_report(report)
        self.assertTrue(any("f1->f2 is static" in failure for failure in failures))

    def test_recolor_only_pair_is_not_static(self) -> None:
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(10, 24, 4, 4, BODY)
        canvas.put(12, 26, ACCENT)  # same silhouette as f0, accent moved
        canvas.save(self.exports / "player_1_lane_b_walk_down_f1.png")
        report = motion_metrics.build_report(self.exports, self.idles)
        pair = report["facings"]["down"]["pairs"][0]
        self.assertEqual(0, pair["silhouette_changed_px"])
        self.assertGreater(pair["recolored_px"], 0)
        self.assertEqual([], motion_metrics.check_report(report))

    def test_rejects_missing_and_wrong_size_inputs(self) -> None:
        with self.assertRaisesRegex(motion_metrics.MetricsError, "missing export"):
            motion_metrics.load_opaque(self.root / "nope.png")
        wrong = self.root / "wrong.png"
        Rgba8Canvas(16, 16, fill=(1, 1, 1, 255)).save(wrong)
        with self.assertRaisesRegex(motion_metrics.MetricsError, "expected 32x32"):
            motion_metrics.load_opaque(wrong)
        status = motion_metrics.main(
            ["--exports", str(self.root / "missing"), "--idle-exports", str(self.idles),
             "--out", str(self.root / "r.json")]
        )
        self.assertEqual(1, status)


class MotionSheetTest(SyntheticCycle):
    def setUp(self) -> None:
        super().setUp()
        self.reference = make_motion_sheet.load_reference(
            REPO / "manifests" / "render-reference.json"
        )

    def test_sheet_is_deterministic(self) -> None:
        one = make_motion_sheet.build_sheet(self.exports, self.idles, self.reference)
        two = make_motion_sheet.build_sheet(self.exports, self.idles, self.reference)
        self.assertEqual(one.encode(), two.encode())

    def test_film_walk_and_ring_rows_compose_runtime_pixels(self) -> None:
        sheet = make_motion_sheet.build_sheet(self.exports, self.idles, self.reference)
        zone1 = self.reference["zones"]["zone_1"]
        x0 = make_motion_sheet.MARGIN_LEFT
        film_y = make_motion_sheet.MARGIN_TOP + 8 + make_motion_sheet.GUTTER

        # FILM row: floor tile background and the idle control's body pixel
        self.assertEqual((*zone1["floor"], 255), sheet.get(x0 + 20, film_y + 20))
        self.assertEqual(BODY, sheet.get(x0 + 10, film_y + 24))
        # second strip cell is walk f0 at the same body position
        self.assertEqual(BODY, sheet.get(x0 + 38 + 10, film_y + 24))

        # WALK row, phase cell index 1 (phase 8, frame f1 at y offset 8):
        # f1 body starts at row 23 -> sheet row walk_y + 23 + 8
        walk_y = film_y + 32 + make_motion_sheet.GUTTER
        cell_x = x0 + (2 * 32 + make_motion_sheet.GUTTER) * 0  # down cells are 32 wide
        cell_x = x0 + (32 + make_motion_sheet.GUTTER) * 1
        self.assertEqual(BODY, sheet.get(cell_x + 10, walk_y + 23 + 8))

    def test_diff_row_categorizes_changes(self) -> None:
        before = make_motion_sheet.Sprite(((5, 5, (1, 2, 3)), (6, 5, (1, 2, 3))))
        after = make_motion_sheet.Sprite(((6, 5, (9, 9, 9)), (7, 5, (1, 2, 3))))
        pixels = {(x, y): rgb for x, y, rgb in make_motion_sheet.diff_pixels(before, after)}
        self.assertEqual(make_motion_sheet.DIFF_REMOVED[:3], pixels[(5, 5)])
        self.assertEqual(make_motion_sheet.DIFF_RECOLORED[:3], pixels[(6, 5)])
        self.assertEqual(make_motion_sheet.DIFF_ADDED[:3], pixels[(7, 5)])

    def test_main_writes_sheet(self) -> None:
        out = self.root / "sheet.png"
        status = make_motion_sheet.main(
            ["--exports", str(self.exports), "--idle-exports", str(self.idles),
             "--reference", str(REPO / "manifests" / "render-reference.json"),
             "--out", str(out)]
        )
        self.assertEqual(0, status)
        info = inspect_png(out)
        self.assertEqual(716, info.width)
        self.assertGreater(info.height, 800)


class MotionMetricsRealExportsTest(unittest.TestCase):
    """The real v1 cycle satisfies the hard motion-contract checks."""

    def test_real_release_passes_checks(self) -> None:
        exports = REPO / "exports" / "calibration-v1"
        idles = REPO / "exports" / "calibration-v0"
        if not (exports / "player_1_lane_b_walk_down_f0.png").is_file():
            self.skipTest("calibration-v1 exports not present")
        report = motion_metrics.build_report(exports, idles)
        self.assertEqual([], motion_metrics.check_report(report))
        # idle-copy pass frames: f3 must equal the idle silhouette exactly
        for facing in motion_metrics.FACINGS:
            f3 = report["facings"][facing]["frames"][3]
            idle = report["facings"][facing]["idle"]
            self.assertEqual(idle["mass"], f3["mass"])
            self.assertEqual(idle["bbox"], f3["bbox"])


if __name__ == "__main__":
    unittest.main()
