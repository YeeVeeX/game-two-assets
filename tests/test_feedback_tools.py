from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import feedback_metrics
import make_contact_sheet
import make_feedback_sheet
import make_motion_sheet
from pixel_spec import load_spec
from png_reader import inspect_png
from png_writer import Rgba8Canvas

REPO = Path(__file__).resolve().parents[1]
BODY = (235, 120, 40, 255)
ACCENT = (20, 14, 12, 255)


def write_rect(path: Path, x: int, y: int, width: int = 4, height: int = 4) -> None:
    """A minimal 32x32 export: body rect at (x, y) with one accent pixel."""
    canvas = Rgba8Canvas(32, 32)
    canvas.fill_rect(x, y, width, height, BODY)
    canvas.put(x + 1, y + 1, ACCENT)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


class SyntheticFeedbackFixture(unittest.TestCase):
    """Idles per facing at distinct columns (nonzero cross-facing ceiling),
    walk frames jittering around the idle, attack keys clearly displaced."""

    IDLE_X = {"down": 10, "right": 18}
    ATTACK_X = {"down": 12, "right": 16}

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.attack = self.root / "attack"
        self.walks = self.root / "walks"
        self.idles = self.root / "idles"
        for facing in feedback_metrics.FACINGS:
            ix = self.IDLE_X[facing]
            write_rect(self.idles / f"player_1_lane_b_idle_{facing}.png", ix, 24)
            positions = [(ix, 24), (ix, 23), (ix + 1, 24), (ix + 1, 23)]
            for index, (x, y) in enumerate(positions):
                write_rect(self.walks / f"player_1_lane_b_walk_{facing}_f{index}.png", x, y)
            write_rect(
                self.attack / f"player_1_lane_b_attack_{facing}_k0.png",
                self.ATTACK_X[facing], 22, width=8, height=6,
            )
        self.reference = json.loads(
            (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
        )


class ColorMathTest(unittest.TestCase):
    def test_contrast_ratio_anchors(self) -> None:
        self.assertEqual(21.0, feedback_metrics.contrast_ratio((255, 255, 255), (0, 0, 0)))
        self.assertEqual(1.0, feedback_metrics.contrast_ratio((80, 80, 80), (80, 80, 80)))
        # documented WCAG threshold example: #767676 on white is ~4.54
        self.assertEqual(
            4.54, feedback_metrics.contrast_ratio((118, 118, 118), (255, 255, 255))
        )

    def test_rgb_distance_is_euclidean(self) -> None:
        self.assertEqual(5.0, feedback_metrics.rgb_distance((0, 3, 0), (4, 0, 0)))
        self.assertEqual(0.0, feedback_metrics.rgb_distance((9, 9, 9), (9, 9, 9)))


class FeedbackMetricsTest(SyntheticFeedbackFixture):
    def build(self) -> dict:
        return feedback_metrics.build_report(
            self.attack, self.walks, self.idles, self.reference
        )

    def test_attack_pose_and_delta_numbers_are_exact(self) -> None:
        report = self.build()
        down = report["attack"]["down"]
        self.assertEqual(48, down["pose"]["mass"])
        self.assertEqual([12, 22, 19, 27], down["pose"]["bbox"])
        self.assertEqual(27, down["pose"]["feet_row"])
        self.assertEqual(0, down["pose"]["feet_row_delta_vs_idle"])
        self.assertEqual(200.0, down["pose"]["mass_drift_vs_idle_pct"])
        # vs idle: rects overlap on x 12-13, y 24-27 (8 px shared of union 56)
        vs_idle = down["deltas"][0]
        self.assertEqual("idle", vs_idle["vs"])
        self.assertEqual(48, vs_idle["silhouette_changed_px"])
        self.assertEqual(56, vs_idle["union_px"])
        self.assertEqual(85.71, vs_idle["popping_pct"])
        self.assertEqual(5, len(down["deltas"]))
        self.assertLessEqual(down["confusability_floor_pct"], down["max_delta_pct"])
        # synthetic idles are disjoint across facings: ceiling is 100%
        self.assertEqual(100.0, report["reference"]["idle_cross_facing"]["popping_pct"])
        self.assertEqual(0.0, down["head_region_share_vs_idle_pct"])

    def test_head_region_share_counts_high_rows(self) -> None:
        canvas = Rgba8Canvas(32, 32)
        canvas.fill_rect(12, 22, 8, 6, BODY)
        canvas.fill_rect(12, 10, 2, 2, BODY)  # 4 px in the head region
        canvas.save(self.attack / "player_1_lane_b_attack_down_k0.png")
        report = self.build()
        down = report["attack"]["down"]
        # XOR vs idle: (52 - 8) + (16 - 8) = 52 changed, 4 in rows <= 15
        self.assertEqual(7.69, down["head_region_share_vs_idle_pct"])

    def test_flash_metrics_use_pinned_constants(self) -> None:
        flash = self.build()["flash"]
        self.assertEqual([200, 30, 30], flash["rgb"])
        self.assertEqual(47.2, flash["rgb_distance"]["telegraph_edge"])
        self.assertEqual(189.2, flash["rgb_distance"]["telegraph_core"])
        self.assertEqual(174.4, flash["rgb_distance"]["transition_gold"])
        self.assertEqual(97.1, flash["rgb_distance"]["role_base"])
        for zone in ("zone_1", "zone_2"):
            self.assertGreater(flash["contrast"][zone]["floor"], 1.0)
            self.assertGreater(flash["contrast"][zone]["wall"], 1.0)

    def test_ring_variants_and_breathing_are_exact(self) -> None:
        rings = self.build()["rings"]["down"]
        by_frame = {entry["frame"]: entry for entry in rings["frames"]}
        idle = by_frame["idle"]
        self.assertEqual([-1, -1, 32, 32], idle["size_ring"]["rect"])
        self.assertEqual(1156, idle["size_ring"]["area_px"])
        self.assertEqual(1140, idle["size_ring"]["visible_margin_px"])
        self.assertEqual(71.25, idle["size_ring"]["margin_to_body_ratio"])
        self.assertEqual([7, 21, 16, 30], idle["bbox_ring"]["rect"])
        self.assertEqual(100, idle["bbox_ring"]["area_px"])
        self.assertEqual(84, idle["bbox_ring"]["visible_margin_px"])
        self.assertEqual(5.25, idle["bbox_ring"]["margin_to_body_ratio"])
        # walk jitter is +-1px in each axis: bbox ring breathes 1px per edge
        self.assertEqual(1, rings["bbox_ring_walk_breathing_max_edge_px"])
        # idle (10,24) 4x4 -> attack (12,22) 8x6: right edge moves 6px
        self.assertEqual(6, rings["bbox_ring_idle_to_attack_max_edge_px"])
        # SIZE ring is constant across every frame by construction
        size_rects = {tuple(entry["size_ring"]["rect"]) for entry in rings["frames"]}
        self.assertEqual(1, len(size_rects))

    def test_check_passes_and_output_is_deterministic(self) -> None:
        report = self.build()
        self.assertEqual([], feedback_metrics.check_report(report))
        outs = []
        for name in ("one.json", "two.json"):
            out = self.root / name
            status = feedback_metrics.main(
                ["--attack-exports", str(self.attack), "--walk-exports", str(self.walks),
                 "--idle-exports", str(self.idles),
                 "--reference", str(REPO / "manifests" / "render-reference.json"),
                 "--out", str(out), "--check"]
            )
            self.assertEqual(0, status)
            outs.append(out.read_bytes())
        self.assertEqual(outs[0], outs[1])

    def test_check_fails_on_feet_drift(self) -> None:
        write_rect(self.attack / "player_1_lane_b_attack_down_k0.png", 12, 18, 8, 6)
        failures = feedback_metrics.check_report(self.build())
        self.assertTrue(any("feet-contact row drifts 4px" in f for f in failures))

    def test_check_fails_on_confusable_tell(self) -> None:
        write_rect(self.attack / "player_1_lane_b_attack_down_k0.png", 10, 24)
        failures = feedback_metrics.check_report(self.build())
        self.assertTrue(any("confusability floor" in f for f in failures))

    def test_check_fails_at_identity_ceiling(self) -> None:
        # fully disjoint from idle and every walk frame: delta 100% = ceiling
        write_rect(self.attack / "player_1_lane_b_attack_down_k0.png", 24, 4, 4, 4)
        write_rect(self.attack / "player_1_lane_b_attack_down_k0.png", 24, 22, 4, 6)
        failures = feedback_metrics.check_report(self.build())
        self.assertTrue(any("identity" in f for f in failures))

    def test_main_reports_missing_inputs(self) -> None:
        status = feedback_metrics.main(
            ["--attack-exports", str(self.root / "missing"),
             "--walk-exports", str(self.walks), "--idle-exports", str(self.idles),
             "--reference", str(REPO / "manifests" / "render-reference.json"),
             "--out", str(self.root / "r.json")]
        )
        self.assertEqual(1, status)


class FeedbackSheetTest(SyntheticFeedbackFixture):
    def build_sheet(self) -> Rgba8Canvas:
        return make_feedback_sheet.build_sheet(
            self.attack, self.walks, self.idles, self.reference
        )

    def test_sheet_is_deterministic(self) -> None:
        self.assertEqual(self.build_sheet().encode(), self.build_sheet().encode())

    def test_film_flash_and_tell_rows_compose_pinned_pixels(self) -> None:
        sheet = self.build_sheet()
        zone1 = self.reference["zones"]["zone_1"]
        flash = tuple(self.reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        x0 = make_feedback_sheet.MARGIN_LEFT
        step = 32 + make_feedback_sheet.GUTTER
        film_y = make_feedback_sheet.MARGIN_TOP + 8 + make_feedback_sheet.GUTTER

        # FILM: floor background + idle body pixel; K0 column shows the attack
        self.assertEqual((*zone1["floor"], 255), sheet.get(x0 + 20, film_y + 4))
        self.assertEqual(BODY, sheet.get(x0 + 10, film_y + 24))
        self.assertEqual(BODY, sheet.get(x0 + 5 * step + 12, film_y + 22))
        # FLASH: same silhouette recolored to the pinned crimson
        flash_y = film_y + step
        self.assertEqual((*flash, 255), sheet.get(x0 + 10, flash_y + 24))
        self.assertEqual((*flash, 255), sheet.get(x0 + 5 * step + 12, flash_y + 22))
        # accent pixel flashes with the body (full replacement, not a tint)
        self.assertEqual((*flash, 255), sheet.get(x0 + 11, flash_y + 25))

        # TELL (down): windup cell holds idle at -3px, lunge cell k0 at +6px
        tell_y = film_y + 4 * step
        half = 16
        windup_x = x0 + 2 * step
        self.assertEqual(BODY, sheet.get(windup_x + 10, tell_y + half - 3 + 24))
        lunge_x = x0 + 4 * step
        self.assertEqual(BODY, sheet.get(lunge_x + 12, tell_y + half + 6 + 22))

    def test_adjacency_and_ring_rows_compose_pinned_pixels(self) -> None:
        sheet = self.build_sheet()
        reference = self.reference
        zone1 = reference["zones"]["zone_1"]
        telegraph = reference["telegraph"]
        flash = tuple(reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        x0 = make_feedback_sheet.MARGIN_LEFT
        step = 32 + make_feedback_sheet.GUTTER
        film_y = make_feedback_sheet.MARGIN_TOP + 8 + make_feedback_sheet.GUTTER
        tell_h = 64  # down facing
        adj_y = film_y + 4 * step + tell_h + make_feedback_sheet.GUTTER

        # telegraph swell: edge band outside the core, core inside, bone body
        cell_y = adj_y + 32
        self.assertEqual(
            (*telegraph["edge_rgb"], 255), sheet.get(x0 - 1, cell_y + 10)
        )
        self.assertEqual((*telegraph["core_rgb"], 255), sheet.get(x0 + 1, cell_y + 1))
        self.assertEqual((*telegraph["body_rgb"], 255), sheet.get(x0 + 16, cell_y + 16))
        # flash-on idle sits in the adjacent tile
        self.assertEqual((*flash, 255), sheet.get(x0 + 32 + 10, cell_y + 24))
        # gold adjacency cell: transition slab beside the flash body
        gold_x = x0 + 2 * (64 + make_feedback_sheet.GUTTER)
        self.assertEqual((*zone1["transition"], 255), sheet.get(gold_x + 16, cell_y + 16))

        # RING S covers the near-full tile; RING B hugs the sprite bbox
        rings_y = adj_y + 64 + make_feedback_sheet.GUTTER
        ring_cell_y = rings_y + 32
        white = (255, 255, 255, 255)
        self.assertEqual(white, sheet.get(x0 + 1, ring_cell_y + 1))
        ringb_y = rings_y + 64 + make_feedback_sheet.GUTTER
        ringb_cell_y = ringb_y + 32
        self.assertEqual((*zone1["floor"], 255), sheet.get(x0 + 20, ringb_cell_y + 2))
        self.assertEqual(white, sheet.get(x0 + 8, ringb_cell_y + 22))
        self.assertEqual(BODY, sheet.get(x0 + 10, ringb_cell_y + 24))

    def test_diff_row_categorizes_attack_changes(self) -> None:
        sheet = self.build_sheet()
        x0 = make_feedback_sheet.MARGIN_LEFT
        step = 32 + make_feedback_sheet.GUTTER
        film_y = make_feedback_sheet.MARGIN_TOP + 8 + make_feedback_sheet.GUTTER
        diff_y = film_y + 4 * step + 64 + make_feedback_sheet.GUTTER \
            + 3 * (64 + make_feedback_sheet.GUTTER)
        # idle-only pixel (10, 24) reads as removed at 2x
        self.assertEqual(
            make_motion_sheet.DIFF_REMOVED, sheet.get(x0 + 20, diff_y + 48)
        )
        # attack-only pixel (19, 22) reads as added
        self.assertEqual(
            make_motion_sheet.DIFF_ADDED, sheet.get(x0 + 38, diff_y + 44)
        )

    def test_main_writes_sheet(self) -> None:
        out = self.root / "sheet.png"
        status = make_feedback_sheet.main(
            ["--attack-exports", str(self.attack), "--walk-exports", str(self.walks),
             "--idle-exports", str(self.idles),
             "--reference", str(REPO / "manifests" / "render-reference.json"),
             "--out", str(out)]
        )
        self.assertEqual(0, status)
        info = inspect_png(out)
        self.assertEqual(850, info.width)
        self.assertGreater(info.height, 1000)


class RealArtifactsTest(unittest.TestCase):
    """The real v2 poses satisfy the hard checks; banked sheets stay stable."""

    def test_real_attack_exports_pass_checks(self) -> None:
        attack = REPO / "exports" / "calibration-v2"
        if not (attack / "player_1_lane_b_attack_down_k0.png").is_file():
            self.skipTest("calibration-v2 exports not present")
        reference = json.loads(
            (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
        )
        report = feedback_metrics.build_report(
            attack, REPO / "exports" / "calibration-v1",
            REPO / "exports" / "calibration-v0", reference,
        )
        self.assertEqual([], feedback_metrics.check_report(report))

    def test_attack_specs_preserve_frozen_head_rows(self) -> None:
        """Machine-verify the declared derivation: dome and eye rows are the
        frozen idle rows, rigidly lowered (down +2, right +3)."""
        for facing, shift, rows in (("down", 2, range(4, 11)), ("right", 3, range(4, 10))):
            idle = load_spec(
                REPO / "sources" / "calibration-v0" / "specs"
                / f"player_1_lane_b_idle_{facing}.json"
            )
            attack = load_spec(
                REPO / "sources" / "calibration-v2" / "specs"
                / f"player_1_lane_b_attack_{facing}_k0.json"
            )
            for row in rows:
                self.assertEqual(
                    idle.grid[row], attack.grid[row + shift],
                    f"{facing}: idle row {row} not preserved at +{shift}",
                )

    def test_banked_sheets_regenerate_byte_identical(self) -> None:
        reference = make_contact_sheet.load_reference(
            REPO / "manifests" / "render-reference.json"
        )
        v0_sheet = REPO / "reviews" / "calibration-v0" / "contact-sheet.png"
        if v0_sheet.is_file():
            built = make_contact_sheet.build_sheet(
                REPO / "exports" / "calibration-v0", reference
            )
            self.assertEqual(v0_sheet.read_bytes(), built.encode())
        v1_sheet = REPO / "reviews" / "calibration-v1" / "motion-sheet.png"
        if v1_sheet.is_file():
            built = make_motion_sheet.build_sheet(
                REPO / "exports" / "calibration-v1",
                REPO / "exports" / "calibration-v0", reference,
            )
            self.assertEqual(v1_sheet.read_bytes(), built.encode())


if __name__ == "__main__":
    unittest.main()
