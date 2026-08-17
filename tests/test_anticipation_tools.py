from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import anticipation_metrics
import make_anticipation_sheet
import make_motion_sheet
from make_contact_sheet import Sprite
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


class SyntheticAnticipationFixture(unittest.TestCase):
    """Idles per facing at distinct columns (nonzero cross-facing ceiling),
    walk frames jittering around the idle, coil and strike clearly displaced
    from the walk band and from each other."""

    IDLE_X = {"down": 10, "right": 18}
    COIL_X = {"down": 12, "right": 20}
    ATTACK_X = {"down": 12, "right": 16}

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.anticipation = self.root / "anticipation"
        self.attack = self.root / "attack"
        self.walks = self.root / "walks"
        self.idles = self.root / "idles"
        for facing in anticipation_metrics.FACINGS:
            ix = self.IDLE_X[facing]
            write_rect(self.idles / f"player_1_lane_b_idle_{facing}.png", ix, 24)
            positions = [(ix, 24), (ix, 23), (ix + 1, 24), (ix + 1, 23)]
            for index, (x, y) in enumerate(positions):
                write_rect(self.walks / f"player_1_lane_b_walk_{facing}_f{index}.png", x, y)
            write_rect(
                self.anticipation / f"player_1_lane_b_attack_{facing}_a0.png",
                self.COIL_X[facing], 25, width=6, height=3,
            )
            write_rect(
                self.attack / f"player_1_lane_b_attack_{facing}_k0.png",
                self.ATTACK_X[facing], 22, width=8, height=6,
            )
        self.reference = json.loads(
            (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
        )

    def build(self) -> dict:
        return anticipation_metrics.build_report(
            self.anticipation, self.attack, self.walks, self.idles, self.reference
        )


class AnticipationMetricsTest(SyntheticAnticipationFixture):
    def test_pose_delta_and_floor_numbers_are_exact(self) -> None:
        report = self.build()
        down = report["anticipation"]["down"]
        self.assertEqual(18, down["pose"]["mass"])
        self.assertEqual([12, 25, 17, 27], down["pose"]["bbox"])
        self.assertEqual(27, down["pose"]["feet_row"])
        self.assertEqual(0, down["pose"]["feet_row_delta_vs_idle"])
        # idle 4x4 at (10,24) vs coil 6x3 at (12,25): overlap x 12-13, y 25-27
        # (6 shared px), union 16 + 18 - 6 = 28, changed 22
        vs_idle = down["deltas"][0]
        self.assertEqual("idle", vs_idle["vs"])
        self.assertEqual(22, vs_idle["silhouette_changed_px"])
        self.assertEqual(28, vs_idle["union_px"])
        self.assertEqual(78.57, vs_idle["popping_pct"])
        # six comparisons: idle, f0-f3, k0 — k0 is not part of the walk floor
        self.assertEqual(
            ["idle", "f0", "f1", "f2", "f3", "k0"], [d["vs"] for d in down["deltas"]]
        )
        walk_pcts = [d["popping_pct"] for d in down["deltas"][:5]]
        self.assertEqual(min(walk_pcts), down["walk_confusability_floor_pct"])
        self.assertEqual(down["deltas"][5]["popping_pct"], down["strike_distinctness_pct"])
        self.assertEqual(
            max([*walk_pcts, down["strike_distinctness_pct"]]), down["max_delta_pct"]
        )
        # coil sits entirely below the head region on both sides
        self.assertEqual(0.0, down["head_region_share_vs_idle_pct"])
        self.assertEqual(100.0, report["reference"]["idle_cross_facing"]["popping_pct"])

    def test_accent_metrics_count_original_accent_pixels(self) -> None:
        report = self.build()
        accents = report["flash_accent"]["down"]
        self.assertEqual([20, 14, 12], accents["accent_rgb"])
        self.assertEqual([200, 30, 30], accents["flash_rgb"])
        # every synthetic frame carries exactly one accent pixel
        for name in anticipation_metrics.STRIP:
            self.assertEqual(1, accents["frames"][name]["surviving_accent_px"])
        self.assertEqual(
            round(100 / 18, 2), accents["frames"]["a0"]["accent_share_of_mass_pct"]
        )
        # contrast is a pure function of the two pinned colors
        expected = anticipation_metrics.contrast_ratio((20, 14, 12), (200, 30, 30))
        self.assertEqual(expected, accents["contrast_accent_vs_flash"])

    def test_accent_constant_is_the_frozen_ramp_accent(self) -> None:
        """Mechanical tie: ACCENT_RGB equals the v0 idle spec palette 'k'."""
        spec = load_spec(
            REPO / "sources" / "calibration-v0" / "specs" / "player_1_lane_b_idle_down.json"
        )
        color = spec.palette["k"]
        rgb = (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
        self.assertEqual(rgb, anticipation_metrics.ACCENT_RGB)

    def test_ring_breathing_includes_the_coil(self) -> None:
        rings = self.build()["rings"]["down"]
        # idle bbox (10,24,13,27) -> coil bbox (12,25,17,27): +expand 3 on both
        self.assertEqual([7, 21, 16, 30], rings["bbox_ring_rects"]["idle"])
        self.assertEqual([9, 22, 20, 30], rings["bbox_ring_rects"]["a0"])
        self.assertEqual(4, rings["idle_to_a0_max_edge_px"])
        self.assertEqual(3, rings["a0_to_k0_max_edge_px"])

    def test_check_passes_and_output_is_deterministic(self) -> None:
        report = self.build()
        self.assertEqual([], anticipation_metrics.check_report(report))
        outs = []
        for name in ("one.json", "two.json"):
            out = self.root / name
            status = anticipation_metrics.main(
                ["--anticipation-exports", str(self.anticipation),
                 "--attack-exports", str(self.attack), "--walk-exports", str(self.walks),
                 "--idle-exports", str(self.idles),
                 "--reference", str(REPO / "manifests" / "render-reference.json"),
                 "--out", str(out), "--check"]
            )
            self.assertEqual(0, status)
            outs.append(out.read_bytes())
        self.assertEqual(outs[0], outs[1])

    def test_check_fails_on_feet_drift(self) -> None:
        write_rect(
            self.anticipation / "player_1_lane_b_attack_down_a0.png", 14, 18, 6, 3
        )
        failures = anticipation_metrics.check_report(self.build())
        self.assertTrue(any("feet-contact row drifts 7px" in f for f in failures))

    def test_check_fails_on_walk_confusable_coil(self) -> None:
        write_rect(self.anticipation / "player_1_lane_b_attack_down_a0.png", 10, 24)
        failures = anticipation_metrics.check_report(self.build())
        self.assertTrue(any("walk-side confusability floor" in f for f in failures))

    def test_check_fails_on_strike_confusable_coil(self) -> None:
        write_rect(
            self.anticipation / "player_1_lane_b_attack_down_a0.png", 12, 22, 8, 6
        )
        failures = anticipation_metrics.check_report(self.build())
        self.assertTrue(any("a0-vs-k0 distinctness" in f for f in failures))

    def test_check_fails_at_identity_ceiling(self) -> None:
        # fully disjoint from every frozen frame: all deltas 100% = ceiling
        write_rect(self.anticipation / "player_1_lane_b_attack_down_a0.png", 24, 25, 4, 3)
        failures = anticipation_metrics.check_report(self.build())
        self.assertTrue(any("identity" in f for f in failures))

    def test_main_reports_missing_inputs(self) -> None:
        status = anticipation_metrics.main(
            ["--anticipation-exports", str(self.root / "missing"),
             "--attack-exports", str(self.attack), "--walk-exports", str(self.walks),
             "--idle-exports", str(self.idles),
             "--reference", str(REPO / "manifests" / "render-reference.json"),
             "--out", str(self.root / "r.json")]
        )
        self.assertEqual(1, status)


class AnticipationSheetTest(SyntheticAnticipationFixture):
    def build_sheet(self) -> Rgba8Canvas:
        return make_anticipation_sheet.build_sheet(
            self.anticipation, self.attack, self.walks, self.idles, self.reference
        )

    def test_sheet_is_deterministic(self) -> None:
        self.assertEqual(self.build_sheet().encode(), self.build_sheet().encode())

    def test_accent_flash_sprite_redraws_only_original_accents(self) -> None:
        flash = tuple(self.reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        sprite = Sprite(((4, 4, BODY[:3]), (5, 4, ACCENT[:3]), (6, 4, (140, 56, 24))))
        result = make_anticipation_sheet.accent_flash_sprite(sprite, flash)
        colors = {(x, y): rgb for x, y, rgb in result.pixels}
        self.assertEqual(flash, colors[(4, 4)])
        self.assertEqual(ACCENT[:3], colors[(5, 4)])  # original accent survives
        self.assertEqual(flash, colors[(6, 4)])  # every other ramp color flashes

    def test_film_flash_acc_and_grammar_rows_compose_pinned_pixels(self) -> None:
        sheet = self.build_sheet()
        zone1 = self.reference["zones"]["zone_1"]
        flash = tuple(self.reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        x0 = make_anticipation_sheet.MARGIN_LEFT
        step = 32 + make_anticipation_sheet.GUTTER
        film_y = make_anticipation_sheet.MARGIN_TOP + 8 + make_anticipation_sheet.GUTTER

        # FILM: floor background + idle body pixel; A0 column shows the coil
        self.assertEqual((*zone1["floor"], 255), sheet.get(x0 + 20, film_y + 4))
        self.assertEqual(BODY, sheet.get(x0 + 10, film_y + 24))
        self.assertEqual(BODY, sheet.get(x0 + 5 * step + 14, film_y + 25))
        self.assertEqual(BODY, sheet.get(x0 + 6 * step + 12, film_y + 22))
        # FLASH: full replacement recolors even the accent pixel to crimson
        flash_y = film_y + step
        self.assertEqual((*flash, 255), sheet.get(x0 + 5 * step + 14, flash_y + 25))
        self.assertEqual((*flash, 255), sheet.get(x0 + 5 * step + 13, flash_y + 26))
        # ACC: crimson fill with the original accent pixel redrawn on top
        acc_y = flash_y + step
        self.assertEqual((*flash, 255), sheet.get(x0 + 5 * step + 14, acc_y + 25))
        self.assertEqual(ACCENT, sheet.get(x0 + 5 * step + 13, acc_y + 26))

        # GRAMMAR (down): windup cell holds the coil at -3px, lunge k0 at +6px
        grammar_y = film_y + 6 * step
        half = 16
        a0_x = x0 + 2 * step
        self.assertEqual(BODY, sheet.get(a0_x + 14, grammar_y + half + 25))
        wind_x = x0 + 3 * step
        self.assertEqual(BODY, sheet.get(wind_x + 14, grammar_y + half - 3 + 25))
        lunge_x = x0 + 5 * step
        self.assertEqual(BODY, sheet.get(lunge_x + 12, grammar_y + half + 6 + 22))

    def test_diff_row_categorizes_coil_changes(self) -> None:
        sheet = self.build_sheet()
        x0 = make_anticipation_sheet.MARGIN_LEFT
        step = 32 + make_anticipation_sheet.GUTTER
        film_y = make_anticipation_sheet.MARGIN_TOP + 8 + make_anticipation_sheet.GUTTER
        diff_y = film_y + 6 * step + 64 + make_anticipation_sheet.GUTTER
        # idle-only pixel (10, 24) reads as removed at 2x in the IDLE diff cell
        self.assertEqual(
            make_motion_sheet.DIFF_REMOVED, sheet.get(x0 + 20, diff_y + 48)
        )
        # coil-only pixel (17, 27) reads as added
        self.assertEqual(
            make_motion_sheet.DIFF_ADDED, sheet.get(x0 + 34, diff_y + 54)
        )
        # k0 diff cell is the sixth: k0-only pixel (12, 22) reads as removed
        k0_x = x0 + 5 * (64 + make_anticipation_sheet.GUTTER)
        self.assertEqual(
            make_motion_sheet.DIFF_REMOVED, sheet.get(k0_x + 24, diff_y + 44)
        )

    def test_main_writes_sheet(self) -> None:
        out = self.root / "sheet.png"
        status = make_anticipation_sheet.main(
            ["--anticipation-exports", str(self.anticipation),
             "--attack-exports", str(self.attack), "--walk-exports", str(self.walks),
             "--idle-exports", str(self.idles),
             "--reference", str(REPO / "manifests" / "render-reference.json"),
             "--out", str(out)]
        )
        self.assertEqual(0, status)
        info = inspect_png(out)
        self.assertEqual(984, info.width)
        self.assertGreater(info.height, 800)


class RealArtifactsTest(unittest.TestCase):
    """The real v3 poses satisfy the hard checks; banked artifacts stay stable."""

    def test_real_anticipation_exports_pass_checks(self) -> None:
        anticipation = REPO / "exports" / "calibration-v3"
        if not (anticipation / "player_1_lane_b_attack_down_a0.png").is_file():
            self.skipTest("calibration-v3 exports not present")
        reference = json.loads(
            (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
        )
        report = anticipation_metrics.build_report(
            anticipation, REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            reference,
        )
        self.assertEqual([], anticipation_metrics.check_report(report))

    def test_anticipation_specs_preserve_frozen_head_blocks(self) -> None:
        """Machine-verify the declared derivation: the head block is the frozen
        idle head, rigidly translated — down (0,+4) rows 4-14, right (-2,+3)
        rows 4-9 (dx applied as a 2-column left shift of the row string)."""
        down_idle = load_spec(
            REPO / "sources" / "calibration-v0" / "specs" / "player_1_lane_b_idle_down.json"
        )
        down_a0 = load_spec(
            REPO / "sources" / "calibration-v3" / "specs"
            / "player_1_lane_b_attack_down_a0.json"
        )
        for row in range(4, 15):
            self.assertEqual(
                down_idle.grid[row], down_a0.grid[row + 4],
                f"down: idle row {row} not preserved at (0,+4)",
            )
        right_idle = load_spec(
            REPO / "sources" / "calibration-v0" / "specs" / "player_1_lane_b_idle_right.json"
        )
        right_a0 = load_spec(
            REPO / "sources" / "calibration-v3" / "specs"
            / "player_1_lane_b_attack_right_a0.json"
        )
        for row in range(4, 10):
            self.assertEqual(
                right_idle.grid[row][2:] + "..", right_a0.grid[row + 3],
                f"right: idle row {row} not preserved at (-2,+3)",
            )
        # the frozen ramp is unchanged in both facings
        self.assertEqual(down_idle.palette, down_a0.palette)
        self.assertEqual(right_idle.palette, right_a0.palette)

    def test_banked_anticipation_sheet_regenerates_byte_identical(self) -> None:
        sheet_path = REPO / "reviews" / "calibration-v3" / "anticipation-sheet.png"
        if not sheet_path.is_file():
            self.skipTest("calibration-v3 sheet not banked yet")
        reference = json.loads(
            (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
        )
        built = make_anticipation_sheet.build_sheet(
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            reference,
        )
        self.assertEqual(sheet_path.read_bytes(), built.encode())


if __name__ == "__main__":
    unittest.main()
