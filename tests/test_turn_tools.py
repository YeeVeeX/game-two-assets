from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_turn_timeline as timeline
import turn_seam_metrics as metrics
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


def load_reference() -> dict:
    return json.loads(
        (REPO / "manifests" / "render-reference.json").read_text(encoding="utf-8")
    )


def real_dirs() -> dict[str, Path]:
    return timeline.default_dirs()


class SyntheticTurnFixture(unittest.TestCase):
    """Distinct rects per pose, IDENTICAL across facings, f3 == idle (the
    byte-copy law holds on synthetic bytes), so every cell is attributable
    byte-for-byte AND the anchor bars are exercised in their FAILING
    direction on synthetic bytes: context deltas collapse to 0 (the banked
    v9 equality fires), walk-cycle boundaries differ from the banked v1
    numbers (the walk-pair anchor fires), and MID's compound cut exceeds
    the collapsed band max 0.0 (M1 fires) - the banked test pattern."""

    POSE_RECT = {
        "idle": (10, 23), "f0": (11, 23), "f1": (12, 23), "f2": (13, 23),
        "f3": (10, 23),
    }

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dirs = {
            "rise_dir": self.root / "rise",
            "transition_dir": self.root / "transition",
            "recovery_dir": self.root / "recovery",
            "anticipation_dir": self.root / "anticipation",
            "attack_dir": self.root / "attack",
            "walk_dir": self.root / "walks",
            "idle_dir": self.root / "idles",
        }
        for facing in timeline.FACINGS:
            for pose, (x, y) in self.POSE_RECT.items():
                write_rect(
                    self.dirs[timeline.POSE_DIRS[pose]]
                    / timeline.pose_filename(pose, facing),
                    x, y,
                )
        self.reference = load_reference()

    def sheet(self) -> timeline.TurnTimelineSheet:
        return timeline.TurnTimelineSheet(self.dirs, self.reference)


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = load_reference()
        self.plan = timeline.build_plan(self.reference)

    def test_pair_axes_are_the_pre_registered_lane_set(self) -> None:
        self.assertEqual(
            {"DR": ["down", "right"], "RD": ["right", "down"]},
            self.plan["constants"]["pair_axes"],
        )
        for pair, walk in (("DR", "down"), ("RD", "right")):
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]
            self.assertEqual(walk, degen["walk_facing"])
            self.assertEqual(walk, degen["turn_facing"])
            self.assertIsNone(degen["turn_tick"])

    def test_turn_ticks_and_rem_match_the_class_table(self) -> None:
        for pair in timeline.PAIRS:
            rem = {
                lane: self.plan["pairs"][pair]["lanes"][lane]["rem_after_turn"]
                for lane in timeline.TURN_LANES
            }
            self.assertEqual(
                {"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0}, rem
            )
            turns = {
                lane: self.plan["pairs"][pair]["lanes"][lane]["turn_tick"]
                for lane in timeline.TURN_LANES
            }
            self.assertEqual(
                {"EARLY": 3, "MID": 6, "LATE": 10, "CONTROL": 15}, turns
            )

    def test_commit_and_first_advance_follow_the_verified_handoff(self) -> None:
        """B commits at t14's controller for moving lanes (arrival tick),
        at t15 for CONTROL; the first B advance is one tick later."""
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                data = self.plan["pairs"][pair]["lanes"][lane]
                self.assertEqual(14, data["arrival_tick"])
                want = 15 if lane == "CONTROL" else 14
                self.assertEqual(want, data["b_commit_tick"], f"{pair}/{lane}")
                self.assertEqual(want + 1, data["first_b_advance_tick"])

    def test_tween_positions_are_the_pinned_sequence(self) -> None:
        control = self.plan["pairs"]["DR"]["lanes"]["CONTROL"]["ticks"]
        self.assertEqual(
            [0, 0, 1, 2, 4, 7, 11, 14, 18, 21, 25, 28, 30, 31, 32],
            [t["a_px"] for t in control[:15]],
        )

    def test_walk_mapping_is_the_banked_v1_distribution(self) -> None:
        control = self.plan["pairs"]["DR"]["lanes"]["CONTROL"]["ticks"]
        self.assertEqual(
            ["f0"] * 4 + ["f1"] * 3 + ["f2"] * 3 + ["f3"] * 3,
            [t["pose"] for t in control[2:15]],
        )

    def test_facing_swaps_at_the_turn_tick_and_nowhere_else(self) -> None:
        for pair in timeline.PAIRS:
            walk, turn_facing = timeline.PAIR_AXES[pair]
            for lane in timeline.TURN_LANES:
                data = self.plan["pairs"][pair]["lanes"][lane]
                turn = data["turn_tick"]
                for tick in data["ticks"]:
                    want = walk if tick["tick"] < turn else turn_facing
                    self.assertEqual(
                        want, tick["pose_facing"],
                        f"{pair}/{lane}/t{tick['tick']}",
                    )
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]
            self.assertEqual(
                {walk}, {t["pose_facing"] for t in degen["ticks"]}
            )

    def test_turn_cut_poses_are_forced_by_the_mapping(self) -> None:
        """EARLY cuts f0->f0, MID the f0->f1 compound, LATE f2->f2,
        CONTROL f3->idle (the commit tick draws the standing pose)."""
        for pair in timeline.PAIRS:
            lanes = self.plan["pairs"][pair]["lanes"]
            for lane, want in (
                ("EARLY", ("f0", "f0")), ("MID", ("f0", "f1")),
                ("LATE", ("f2", "f2")), ("CONTROL", ("f3", "idle")),
            ):
                turn = lanes[lane]["turn_tick"]
                before = lanes[lane]["ticks"][turn - 1]
                after = lanes[lane]["ticks"][turn]
                self.assertEqual(want, (before["pose"], after["pose"]), lane)

    def test_draw_vectors_are_tween_along_a_then_along_b(self) -> None:
        # The pre-registered key vectors from the rationale, spot-checked.
        dr = self.plan["pairs"]["DR"]["lanes"]
        self.assertEqual([0, 1], dr["EARLY"]["ticks"][2]["draw"])    # f0@A
        self.assertEqual([0, 2], dr["EARLY"]["ticks"][3]["draw"])    # f0@B turn
        self.assertEqual([0, 32], dr["EARLY"]["ticks"][14]["draw"])  # arrival
        self.assertEqual([1, 32], dr["EARLY"]["ticks"][15]["draw"])  # wrap
        self.assertEqual([0, 11], dr["MID"]["ticks"][6]["draw"])
        self.assertEqual([0, 25], dr["LATE"]["ticks"][10]["draw"])
        self.assertEqual([0, 32], dr["CONTROL"]["ticks"][15]["draw"])  # stand
        self.assertEqual([1, 32], dr["CONTROL"]["ticks"][16]["draw"])  # restart
        self.assertEqual([0, 33], dr["DEGEN"]["ticks"][15]["draw"])    # step 2
        rd = self.plan["pairs"]["RD"]["lanes"]
        self.assertEqual([2, 0], rd["EARLY"]["ticks"][3]["draw"])
        self.assertEqual([32, 1], rd["EARLY"]["ticks"][15]["draw"])
        self.assertEqual([32, 1], rd["CONTROL"]["ticks"][16]["draw"])
        self.assertEqual([33, 0], rd["DEGEN"]["ticks"][15]["draw"])

    def test_control_stand_tick_draws_idle_in_the_new_facing(self) -> None:
        for pair in timeline.PAIRS:
            _, turn_facing = timeline.PAIR_AXES[pair]
            stand = self.plan["pairs"][pair]["lanes"]["CONTROL"]["ticks"][15]
            self.assertEqual("turn_stand", stand["phase"])
            self.assertEqual("idle", stand["pose"])
            self.assertEqual(turn_facing, stand["pose_facing"])

    def test_no_attack_pose_anywhere(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                for tick in self.plan["pairs"][pair]["lanes"][lane]["ticks"]:
                    self.assertIn(tick["pose"], timeline.WALK_POSES)

    def test_windows_hold_every_opaque_pixel_by_construction(self) -> None:
        self.assertEqual([], metrics.check_bounds(self.plan))

    def test_turn_windows_are_two_by_two_tiles_with_declared_spans(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.TURN_LANES:
                window = self.plan["pairs"][pair]["lanes"][lane]["window"]
                self.assertEqual("turn", window["kind"])
                self.assertEqual(64, window["w"])
                self.assertEqual(64, window["h"])
                self.assertEqual([0, 31], window["t0_a_span"])
                self.assertEqual([32, 63], window["t1_a_span"])
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]["window"]
            self.assertEqual("degen", degen["kind"])
            self.assertEqual([64, 95], degen["t2_a_span"])

    def test_sheet_ticks_span_t01_through_t21(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                span = [
                    t["tick"]
                    for t in self.plan["pairs"][pair]["lanes"][lane]["sheet_ticks"]
                ]
                self.assertEqual(list(range(1, 22)), span)

    def test_turn_and_wrap_strips_pick_the_seam_ticks(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.TURN_LANES:
                turn = self.plan["pairs"][pair]["lanes"][lane]["turn_tick"]
                strip = [
                    t["tick"] for t in timeline.turn_strip(self.plan, pair, lane)
                ]
                self.assertEqual([turn - 1, turn, turn + 1], strip)
            for lane in timeline.SECTION_LANES:
                start = 14 if lane == "CONTROL" else 13
                wrap = [
                    t["tick"] for t in timeline.wrap_strip(self.plan, pair, lane)
                ]
                self.assertEqual(list(range(start, start + 4)), wrap)

    def test_turn_crops_hold_the_turn_event(self) -> None:
        for pair, want in (("DR", [32, 64]), ("RD", [64, 32])):
            for lane in timeline.TURN_LANES:
                crop = self.plan["pairs"][pair]["lanes"][lane]["turn_crop"]
                self.assertEqual(want, crop)
            self.assertIsNone(
                self.plan["pairs"][pair]["lanes"]["DEGEN"]["turn_crop"]
            )


class SheetTest(SyntheticTurnFixture):
    def test_sheet_is_deterministic(self) -> None:
        self.assertEqual(
            self.sheet().build().encode(), self.sheet().build().encode()
        )

    def test_sheet_geometry_is_fixed(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        self.assertEqual(sheet.sheet_width(), canvas.width)

    def test_cell_manifest_covers_every_creature_cell(self) -> None:
        sheet = self.sheet()
        sheet.build()
        sections = {c["section"] for c in sheet.cells}
        self.assertEqual({"lane", "turn", "wrap", "context", "film"}, sections)
        lanes = [c for c in sheet.cells if c["section"] == "lane"]
        # 2 pairs x 5 lanes x 2 zones x 21 columns
        self.assertEqual(2 * 5 * 2 * 21, len(lanes))
        turn = [c for c in sheet.cells if c["section"] == "turn"]
        self.assertEqual(2 * 4 * 3, len(turn))
        wrap = [c for c in sheet.cells if c["section"] == "wrap"]
        self.assertEqual(2 * 5 * 4, len(wrap))
        context = [c for c in sheet.cells if c["section"] == "context"]
        self.assertEqual(2 * 5 * 2, len(context))
        film = [c for c in sheet.cells if c["section"] == "film"]
        self.assertEqual(2 * 2 * len(timeline.WALK_POSES), len(film))
        self.assertEqual(524, len(sheet.cells))

    def test_lane_cells_draw_at_the_plan_positions(self) -> None:
        sheet = self.sheet()
        sheet.build()
        plan = sheet.plan
        for cell in sheet.cells:
            if cell["section"] != "lane":
                continue
            tick = plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]["ticks"][
                cell["tick"]
            ]
            self.assertEqual(tick["draw"], cell["draw"])
            self.assertEqual(tick["pose"], cell["pose"])
            self.assertEqual(tick["pose_facing"], cell["pose_facing"])
            window = plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]["window"]
            self.assertEqual(window["w"], cell["window_w"])
            self.assertEqual(window["h"], cell["window_h"])

    def test_turn_cells_use_the_crop_and_wrap_cells_the_full_window(self) -> None:
        sheet = self.sheet()
        sheet.build()
        plan = sheet.plan
        for cell in sheet.cells:
            if cell["section"] == "turn":
                data = plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]
                self.assertEqual(
                    data["turn_crop"], [cell["window_w"], cell["window_h"]]
                )
                self.assertEqual(timeline.TURN_ZOOM_SCALE, cell["scale"])
            if cell["section"] == "wrap":
                data = plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]
                self.assertEqual(data["window"]["w"], cell["window_w"])
                self.assertEqual(data["window"]["h"], cell["window_h"])
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])
            if cell["section"] == "context":
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])
                self.assertEqual([0, 0], cell["draw"])

    def test_context_row_renders_both_facings_per_pose(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for pair in timeline.PAIRS:
            walk, turn_facing = timeline.PAIR_AXES[pair]
            cells = [
                c for c in sheet.cells
                if c["section"] == "context" and c["pair"] == pair
            ]
            self.assertEqual(
                [walk, turn_facing] * 5, [c["pose_facing"] for c in cells]
            )
            self.assertEqual(
                ["f0", "f0", "f1", "f1", "f2", "f2", "f3", "f3",
                 "idle", "idle"],
                [c["pose"] for c in cells],
            )

    def test_film_rows_carry_the_walk_strip_per_facing(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for facing in timeline.FACINGS:
            for zone in ("zone_1", "zone_2"):
                film = [
                    c for c in sheet.cells
                    if c["section"] == "film" and c["pose_facing"] == facing
                    and c["zone"] == zone
                ]
                self.assertEqual(
                    list(timeline.WALK_POSES), [c["pose"] for c in film]
                )

    def test_apng_frames_show_four_turn_lanes_for_all_30_ticks(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for pair in timeline.PAIRS:
            frames = timeline.build_apng_frames(sheet, pair)
            self.assertEqual(timeline.TOTAL_TICKS, len(frames))
            sizes = {(f.width, f.height) for f in frames}
            self.assertEqual(1, len(sizes))


class ValidatorTest(SyntheticTurnFixture):
    def build_report(self, **kwargs) -> dict:
        return metrics.build_report(
            self.dirs, self.reference,
            exports_root=kwargs.pop("exports_root", REPO / "exports"),
            **kwargs,
        )

    def test_purity_passes_on_a_fresh_build(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        result = metrics.check_purity(canvas, sheet, self.dirs)
        self.assertEqual([], result["failures"])
        self.assertEqual(524, result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(c for c in sheet.cells if c["section"] == "lane")
        canvas.put(cell["rect"][0] + 8, cell["rect"][1] + 8, (1, 2, 3, 255))
        result = metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        write_rect(
            self.dirs["walk_dir"] / timeline.pose_filename("f2", "down"), 5, 5
        )
        result = metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_tick_math_passes_on_the_pinned_plan(self) -> None:
        plan = timeline.build_plan(self.reference)
        self.assertEqual([], metrics.check_tick_math(plan))

    def test_tick_math_catches_pose_facing_and_position_drift(self) -> None:
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["MID"]["ticks"][6]["pose"] = "f3"
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("pose/phase" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["EARLY"]["ticks"][8]["draw"][1] += 1
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("draw" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["RD"]["lanes"]["LATE"]["ticks"][12]["pose_facing"] = "right"
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("facing" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["RD"]["lanes"]["CONTROL"]["ticks"][15]["pose"] = "f0"
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("CONTROL" in f and "t15" in f for f in failures))

    def test_bounds_check_catches_an_escaping_draw(self) -> None:
        plan = timeline.build_plan(self.reference)
        self.assertEqual([], metrics.check_bounds(plan))
        plan["pairs"]["DR"]["lanes"]["EARLY"]["ticks"][8]["draw"][0] = 70
        self.assertTrue(metrics.check_bounds(plan))

    def test_jump_tables_span_t01_through_t21(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                rows = report["turn_tables"][pair][lane]["rows"]
                self.assertEqual(20, len(rows), f"{pair}/{lane}")
                self.assertEqual(1, rows[0]["from_tick"])
                self.assertEqual(21, rows[-1]["to_tick"])

    def test_jump_rows_carry_vector_deltas_and_exact_squares(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                for row in report["turn_tables"][pair][lane]["rows"]:
                    dx, dy = row["delta_window_px"]
                    self.assertEqual(row["squared_px"], dx * dx + dy * dy)
                    self.assertEqual(
                        row["squared_px"],
                        row["delta_a_px"] ** 2 + row["delta_b_px"] ** 2,
                    )

    def test_wrap_rows_carry_the_pre_registered_pivot_vectors(self) -> None:
        """Moving lanes pivot (dA,dB) = (0,1) at t14->t15; CONTROL stands
        (0,0) then restarts (0,1); DEGEN wraps along-axis (1,0)."""
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in ("EARLY", "MID", "LATE"):
                rows = report["turn_tables"][pair][lane]["rows"]
                wrap = next(r for r in rows if r["from_tick"] == 14)
                self.assertEqual(("f3", "f0"), (wrap["pose_from"], wrap["pose_to"]))
                self.assertEqual((0, 1), (wrap["delta_a_px"], wrap["delta_b_px"]))
            control = report["turn_tables"][pair]["CONTROL"]["rows"]
            stand = next(r for r in control if r["from_tick"] == 14)
            self.assertEqual(("f3", "idle"), (stand["pose_from"], stand["pose_to"]))
            self.assertEqual((0, 0), (stand["delta_a_px"], stand["delta_b_px"]))
            restart = next(r for r in control if r["from_tick"] == 15)
            self.assertEqual(("idle", "f0"), (restart["pose_from"], restart["pose_to"]))
            self.assertEqual((0, 1), (restart["delta_a_px"], restart["delta_b_px"]))
            degen = report["turn_tables"][pair]["DEGEN"]["rows"]
            wrap = next(r for r in degen if r["from_tick"] == 14)
            self.assertEqual(("f3", "f0"), (wrap["pose_from"], wrap["pose_to"]))
            self.assertEqual((1, 0), (wrap["delta_a_px"], wrap["delta_b_px"]))

    def test_turn_cut_extraction_matches_the_turn_tick(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.TURN_LANES:
                cut = report["turn_tables"][pair][lane]["turn_cut"]
                self.assertEqual(timeline.TURN_TICKS[lane], cut["to_tick"])
                self.assertNotEqual(
                    cut["pose_from_facing"], cut["pose_to_facing"]
                )
            self.assertIsNone(report["turn_tables"][pair]["DEGEN"]["turn_cut"])

    def test_context_anchor_fires_on_synthetic_bytes(self) -> None:
        """Identical rects across facings collapse every context to 0, so
        the banked-v9 equality bar must fire (failing-direction)."""
        report = self.build_report()
        self.assertEqual(0.0, report["context_deltas"]["idle"]["popping_pct"])
        self.assertTrue(report["context_anchor_failures"])

    def test_walk_pair_anchor_fires_on_synthetic_bytes(self) -> None:
        report = self.build_report()
        self.assertTrue(report["walk_pair_anchor_failures"])

    def test_band_fires_on_synthetic_bytes(self) -> None:
        """The collapsed band max is 0.0 while MID's compound cut is
        nonzero - M1 must fire (failing-direction)."""
        report = self.build_report()
        self.assertEqual(0.0, report["band"]["band_max"])
        failures = metrics.check_band(report["band"])
        self.assertTrue(any("MID" in f for f in failures))

    def test_bytecopy_holds_on_synthetic_and_catches_drift(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["bytecopy_failures"])
        write_rect(
            self.dirs["walk_dir"] / timeline.pose_filename("f3", "down"), 20, 4
        )
        report = self.build_report()
        self.assertTrue(report["bytecopy_failures"])

    def test_cut_anchors_hold_on_synthetic_bytes(self) -> None:
        """Frame-identical cuts equal their (collapsed) context on synthetic
        bytes - the equality mechanism's passing direction."""
        report = self.build_report()
        self.assertEqual([], report["cut_anchor_failures"])

    def test_cut_anchor_catches_a_mismatch(self) -> None:
        report = self.build_report()
        tables = report["turn_tables"]
        tables["DR"]["EARLY"]["turn_cut"]["pose_delta_pct"] = 99.9
        failures = metrics.check_cut_anchors(
            tables, report["context_deltas"], None
        )
        self.assertTrue(any("DR/EARLY" in f for f in failures))

    def test_consistency_catches_a_diverging_repeat(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["consistency_failures"])
        tables = report["turn_tables"]
        tables["RD"]["DEGEN"]["rows"][4]["pose_delta_pct"] = 77.7
        self.assertTrue(metrics.check_cross_lane_consistency(tables))

    def test_degen_prefix_equality_holds_and_catches_drift(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["degen_prefix_failures"])
        tables = report["turn_tables"]
        tables["DR"]["DEGEN"]["rows"][3]["delta_a_px"] = 9
        self.assertTrue(metrics.check_degen_prefix(tables))

    def test_binding_rows_cover_exactly_the_strafe_ticks(self) -> None:
        report = self.build_report()
        want = {"EARLY": 12, "MID": 9, "LATE": 5, "CONTROL": 0}
        for pair in timeline.PAIRS:
            for lane, count in want.items():
                data = report["binding"][pair][lane]
                self.assertEqual(count, len(data["rows"]), f"{pair}/{lane}")
                self.assertEqual(count, data["summary"]["strafe_ticks"])
                for row in data["rows"]:
                    lo, hi = row["body_a_extent"]
                    self.assertLessEqual(lo, hi)
                    self.assertEqual(
                        row["majority_tile"],
                        "T1"
                        if row["body_overlap_t1_px"] > row["body_overlap_t0_px"]
                        else "T0",
                    )

    def test_export_pins_verify_the_banked_chain_and_flag_new_dirs(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["export_pins"]["failures"])
        self.assertEqual(26, report["export_pins"]["verified"])
        import shutil

        fake_root = self.root / "exports"
        shutil.copytree(REPO / "exports", fake_root)
        (fake_root / "calibration-v10").mkdir()
        report = self.build_report(exports_root=fake_root)
        self.assertTrue(
            any("calibration-v10" in f for f in report["export_pins"]["failures"])
        )

    def test_check_report_groups_integrity_and_measurement(self) -> None:
        report = self.build_report()
        grouped = metrics.check_report(report)
        self.assertEqual({"integrity", "measurement"}, set(grouped))
        # Synthetic bytes: the context + walk-pair anchors fire (expected
        # integrity reds) and M1 fires (measurement); nothing structural.
        self.assertTrue(grouped["integrity"])
        self.assertTrue(grouped["measurement"])
        self.assertEqual([], report["tick_math_failures"])
        self.assertEqual([], report["bounds_failures"])
        self.assertEqual([], report["purity"]["failures"])
        self.assertEqual([], report["consistency_failures"])
        self.assertEqual([], report["degen_prefix_failures"])

    def test_report_is_deterministic(self) -> None:
        first = self.build_report()
        second = self.build_report()
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertTrue(first["sheet"]["deterministic"])


class RealArtifactsTest(unittest.TestCase):
    """The real banked exports drive the sheet; committed artifacts stay
    stable. MID's compound-cut numbers are UNMEASURED before this sprint's
    artifacts exist - these tests assert committed-artifact consistency and
    the pre-known banked values only, never an assumed compound answer."""

    METRICS_PATH = REPO / "reviews" / "calibration-v10" / "turn-metrics.json"
    SHEET_PATH = REPO / "reviews" / "calibration-v10" / "turn-sheet.png"

    def setUp(self) -> None:
        if not (REPO / "exports" / "calibration-v1"
                / "player_1_lane_b_walk_down_f0.png").is_file():
            self.skipTest("banked exports not present")
        self.reference = load_reference()

    def test_real_build_passes_every_integrity_bar(self) -> None:
        report = metrics.build_report(
            real_dirs(), self.reference, sheet_path=self.SHEET_PATH
        )
        grouped = metrics.check_report(report)
        self.assertEqual([], grouped["integrity"])
        self.assertEqual(26, report["export_pins"]["verified"])

    def test_context_reproduces_the_banked_v9_numbers(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        context = report["context_deltas"]
        self.assertEqual(53.64, context["f0"]["popping_pct"])
        self.assertEqual(45.0, context["f1"]["popping_pct"])
        self.assertEqual(36.45, context["f2"]["popping_pct"])
        self.assertEqual(44.44, context["f3"]["popping_pct"])
        self.assertEqual(44.44, context["idle"]["popping_pct"])
        self.assertEqual([], report["context_anchor_failures"])

    def test_frame_identical_cuts_equal_their_banked_contexts(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        for pair in timeline.PAIRS:
            tables = report["turn_tables"][pair]
            self.assertEqual(
                53.64, tables["EARLY"]["turn_cut"]["pose_delta_pct"]
            )
            self.assertEqual(
                36.45, tables["LATE"]["turn_cut"]["pose_delta_pct"]
            )
            self.assertEqual(
                44.44, tables["CONTROL"]["turn_cut"]["pose_delta_pct"]
            )

    def test_wrap_and_restart_rows_equal_the_banked_v1_wrap(self) -> None:
        """f3 is the idle byte-copy, so the wrap (f3->f0@B) and CONTROL's
        restart (idle->f0@B) both equal the banked v1 f3->f0 pair: right
        10.29 (DR turns right), down 15.87 (RD turns down)."""
        report = metrics.build_report(real_dirs(), self.reference)
        expected = {"DR": 10.29, "RD": 15.87}
        for pair, want in expected.items():
            for lane in ("EARLY", "MID", "LATE"):
                rows = report["turn_tables"][pair][lane]["rows"]
                wrap = next(r for r in rows if r["from_tick"] == 14)
                self.assertEqual(want, wrap["pose_delta_pct"], f"{pair}/{lane}")
            control = report["turn_tables"][pair]["CONTROL"]["rows"]
            restart = next(r for r in control if r["from_tick"] == 15)
            self.assertEqual(want, restart["pose_delta_pct"], pair)

    def test_mid_compound_cut_is_reported_not_assumed(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        for pair in timeline.PAIRS:
            cut = report["turn_tables"][pair]["MID"]["turn_cut"]
            self.assertEqual(("f0", "f1"), (cut["pose_from"], cut["pose_to"]))
            self.assertGreater(cut["pose_delta_pct"], 0.0)

    def test_binding_summaries_match_the_pre_registered_arithmetic(self) -> None:
        """EARLY strafes ~5 T0-majority ticks before the flip; MID 2;
        LATE/CONTROL 0 - the rationale's hand table, recomputed from real
        frame bboxes."""
        report = metrics.build_report(real_dirs(), self.reference)
        for pair in timeline.PAIRS:
            summaries = {
                lane: report["binding"][pair][lane]["summary"]
                for lane in timeline.TURN_LANES
            }
            self.assertEqual(5, summaries["EARLY"]["t0_majority_ticks"], pair)
            self.assertEqual(8, summaries["EARLY"]["first_t1_majority_tick"])
            self.assertEqual(2, summaries["MID"]["t0_majority_ticks"], pair)
            self.assertEqual(0, summaries["LATE"]["t0_majority_ticks"], pair)
            self.assertEqual(0, summaries["CONTROL"]["strafe_ticks"], pair)

    def test_committed_metrics_match_a_fresh_report(self) -> None:
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v10 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        report = metrics.build_report(
            real_dirs(), self.reference,
            sheet_path=self.SHEET_PATH,
            apng_dir=REPO / "reviews" / "calibration-v10",
        )
        self.assertEqual(committed, json.loads(json.dumps(report)))

    def test_banked_sheet_regenerates_byte_identical(self) -> None:
        if not self.SHEET_PATH.is_file():
            self.skipTest("calibration-v10 sheet not banked yet")
        sheet = timeline.TurnTimelineSheet(real_dirs(), self.reference)
        self.assertEqual(self.SHEET_PATH.read_bytes(), sheet.build().encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        apng_dir = REPO / "reviews" / "calibration-v10"
        targets = [
            apng_dir / f"turn-lanes-{pair.lower()}.apng"
            for pair in timeline.PAIRS
        ]
        if not all(t.is_file() for t in targets):
            self.skipTest("calibration-v10 apng aids not banked yet")
        sheet = timeline.TurnTimelineSheet(real_dirs(), self.reference)
        sheet.build()
        for pair, target in zip(timeline.PAIRS, targets):
            frames = timeline.build_apng_frames(sheet, pair)
            payload = timeline.encode_apng(
                frames, timeline.apng_delays(len(frames))
            )
            self.assertEqual(target.read_bytes(), payload)

    def test_sheet_main_writes_sheet_and_apng_aids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "sheet.png"
            status = timeline.main(["--out", str(out), "--apng-dir", temp])
            self.assertEqual(0, status)
            self.assertTrue(out.is_file())
            for pair in timeline.PAIRS:
                self.assertTrue(
                    (Path(temp) / f"turn-lanes-{pair.lower()}.apng").is_file()
                )

    def test_metrics_main_matches_the_committed_check_outcome(self) -> None:
        """The --check exit reflects the committed measurement outcome: the
        integrity bars must be green on real bytes; M1 carries whatever the
        committed metrics banked (pre-registered split)."""
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v10 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        committed_reds = len(metrics.check_band(committed["band"]))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "turn-metrics.json"
            status = metrics.main(["--out", str(out), "--check"])
            report = json.loads(out.read_text(encoding="utf-8"))
            grouped = metrics.check_report(report)
            self.assertEqual([], grouped["integrity"])
            self.assertEqual(committed_reds, len(grouped["measurement"]))
            self.assertEqual(0 if committed_reds == 0 else 1, status)

    def test_metrics_main_reports_missing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            status = metrics.main(
                ["--idle-exports", str(Path(temp) / "nowhere"),
                 "--out", str(Path(temp) / "out.json")]
            )
            self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
