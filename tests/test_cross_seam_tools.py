from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import cross_seam_metrics as metrics
import make_cross_seam_timeline as timeline
import make_seam_timeline as seam
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


class SyntheticCrossFixture(unittest.TestCase):
    """Distinct rects per pose, IDENTICAL across facings, so every cell is
    attributable byte-for-byte AND the release-salience mechanism exercises
    its passing direction on synthetic bytes (a0/k0 disjoint; walk/w0 rects
    overlap heavily, so the cross-facing onset cut stays small). Identical
    facings also mean the 44.44 context bar and the degenerate-regression bar
    fire on synthetic bytes - both are exercised in their FAILING direction
    (the banked v8 test pattern)."""

    POSE_RECT = {
        "idle": (10, 23), "f0": (11, 23), "f1": (12, 23), "f2": (13, 23),
        "f3": (10, 23),
        "a0": (12, 25), "k0": (22, 10), "r0": (26, 14), "w0": (10, 23),
        "s0": (24, 12), "x0": (26, 18),
    }
    POSE_SIZE = {"k0": (8, 6)}

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
                width, height = self.POSE_SIZE.get(pose, (4, 4))
                write_rect(
                    self.dirs[timeline.POSE_DIRS[pose]]
                    / timeline.pose_filename(pose, facing),
                    x, y, width, height,
                )
        self.reference = load_reference()

    def sheet(self) -> timeline.CrossSeamSheet:
        return timeline.CrossSeamSheet(self.dirs, self.reference)


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
            self.assertEqual(walk, degen["attack_facing"])

    def test_onset_ticks_and_rem_match_the_class_table(self) -> None:
        for pair in timeline.PAIRS:
            rem = {
                lane: self.plan["pairs"][pair]["lanes"][lane]["rem_after_onset"]
                for lane in timeline.SECTION_LANES
            }
            self.assertEqual(
                {"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0, "DEGEN": 0}, rem
            )
            onsets = {
                lane: self.plan["pairs"][pair]["lanes"][lane]["onset_tick"]
                for lane in timeline.SECTION_LANES
            }
            self.assertEqual(
                {"EARLY": 3, "MID": 6, "LATE": 10, "CONTROL": 15, "DEGEN": 15},
                onsets,
            )

    def test_arrival_is_absolute_tick_14_in_every_lane(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                self.assertEqual(
                    14, self.plan["pairs"][pair]["lanes"][lane]["arrival_tick"]
                )

    def test_walk_ticks_face_a_and_attack_ticks_face_b(self) -> None:
        for pair in timeline.PAIRS:
            walk, attack = timeline.PAIR_AXES[pair]
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                data = self.plan["pairs"][pair]["lanes"][lane]
                onset = data["onset_tick"]
                for tick in data["ticks"]:
                    want = walk if tick["tick"] < onset else attack
                    self.assertEqual(
                        want, tick["pose_facing"],
                        f"{pair}/{lane}/t{tick['tick']}",
                    )

    def test_attack_grammar_is_the_banked_winner_in_every_lane(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                ticks = self.plan["pairs"][pair]["lanes"][lane]["ticks"]
                windup = [t["pose"] for t in ticks if t["phase"] == "windup"]
                active = [t["pose"] for t in ticks if t["phase"] == "active"]
                recovery = [t["pose"] for t in ticks if t["phase"] == "recovery"]
                self.assertEqual(["w0"] + ["a0"] * 4, windup, f"{pair}/{lane}")
                self.assertEqual(["k0"] * 4, active, f"{pair}/{lane}")
                self.assertEqual(
                    ["s0"] + ["r0"] * 6 + ["x0"], recovery, f"{pair}/{lane}"
                )

    def test_draw_vectors_are_tween_along_a_plus_offset_along_b(self) -> None:
        # The pre-registered key vectors from the rationale, spot-checked.
        dr = self.plan["pairs"]["DR"]["lanes"]
        self.assertEqual([32, 1], dr["EARLY"]["ticks"][2]["draw"])    # f0
        self.assertEqual([29, 2], dr["EARLY"]["ticks"][3]["draw"])    # w0
        self.assertEqual([38, 18], dr["EARLY"]["ticks"][8]["draw"])   # k0
        self.assertEqual([32, 30], dr["EARLY"]["ticks"][12]["draw"])  # s0
        self.assertEqual([29, 11], dr["MID"]["ticks"][6]["draw"])
        self.assertEqual([38, 28], dr["MID"]["ticks"][11]["draw"])
        self.assertEqual([29, 25], dr["LATE"]["ticks"][10]["draw"])
        self.assertEqual([29, 32], dr["CONTROL"]["ticks"][15]["draw"])
        self.assertEqual([38, 32], dr["CONTROL"]["ticks"][20]["draw"])
        rd = self.plan["pairs"]["RD"]["lanes"]
        self.assertEqual([2, 29], rd["EARLY"]["ticks"][3]["draw"])
        self.assertEqual([18, 38], rd["EARLY"]["ticks"][8]["draw"])
        self.assertEqual([32, 29], rd["CONTROL"]["ticks"][15]["draw"])

    def test_degen_lanes_reproduce_the_v8_axis_positions(self) -> None:
        """The 2D machinery degenerated to along-facing must carry the exact
        v8 seam-plan axis positions (pure-plan equality, no bytes needed)."""
        v8_plan = seam.build_plan(self.reference)
        for pair, axis_index in (("DR", 1), ("RD", 0)):
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]["ticks"]
            control = v8_plan["lanes"]["CONTROL"]["ticks"]
            for mine, banked in zip(degen, control):
                self.assertEqual(banked["pose"], mine["pose"])
                self.assertEqual(banked["axis_px"], mine["draw"][axis_index])
                self.assertEqual(0, mine["draw"][1 - axis_index])

    def test_windows_hold_every_opaque_pixel_by_construction(self) -> None:
        self.assertEqual([], metrics.check_bounds(self.plan))

    def test_cross_windows_expose_both_candidate_strike_tiles(self) -> None:
        for pair in timeline.PAIRS:
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                window = self.plan["pairs"][pair]["lanes"][lane]["window"]
                self.assertEqual("cross", window["kind"])
                self.assertEqual([32, 63], window["true_arc_a_span"])
                self.assertEqual([0, 31], window["near_a_span"])
                self.assertEqual(64, window["grid_line_b"])
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]["window"]
            self.assertEqual("degen", degen["kind"])
            self.assertEqual([64, 95], degen["true_arc_a_span"])
            self.assertIsNone(degen["near_a_span"])

    def test_sheet_ticks_span_onset_minus_2_through_onset_plus_13(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                data = self.plan["pairs"][pair]["lanes"][lane]
                span = [t["tick"] for t in data["sheet_ticks"]]
                onset = data["onset_tick"]
                self.assertEqual(list(range(onset - 2, onset + 14)), span)

    def test_onset_and_release_strips_pick_the_seam_ticks(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                onset = self.plan["pairs"][pair]["lanes"][lane]["onset_tick"]
                strip = [
                    t["tick"] for t in timeline.onset_strip(self.plan, pair, lane)
                ]
                self.assertEqual([onset - 1, onset, onset + 1], strip)
                release = [
                    t["tick"] for t in timeline.release_strip(self.plan, pair, lane)
                ]
                self.assertEqual([onset + 4, onset + 5], release)
                poses = [
                    t["pose"] for t in timeline.release_strip(self.plan, pair, lane)
                ]
                self.assertEqual(["a0", "k0"], poses)

    def test_onset_crops_hold_the_onset_event(self) -> None:
        for pair in timeline.PAIRS:
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                crop = self.plan["pairs"][pair]["lanes"][lane]["onset_crop"]
                self.assertEqual([64, 64], crop)


class SheetTest(SyntheticCrossFixture):
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
        self.assertEqual({"lane", "onset", "release", "film"}, sections)
        lanes = [c for c in sheet.cells if c["section"] == "lane"]
        # 2 pairs x 5 lanes x 2 zones x 16 columns
        self.assertEqual(2 * 5 * 2 * 16, len(lanes))
        onset = [c for c in sheet.cells if c["section"] == "onset"]
        self.assertEqual(2 * 5 * 3, len(onset))
        release = [c for c in sheet.cells if c["section"] == "release"]
        self.assertEqual(2 * 5 * 2, len(release))
        film = [c for c in sheet.cells if c["section"] == "film"]
        self.assertEqual(2 * 2 * len(timeline.STRIP), len(film))

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

    def test_onset_strip_uses_the_crop_and_release_the_full_window(self) -> None:
        sheet = self.sheet()
        sheet.build()
        plan = sheet.plan
        for cell in sheet.cells:
            data = (
                plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]
                if cell["section"] in ("onset", "release")
                else None
            )
            if cell["section"] == "onset":
                self.assertEqual(
                    data["onset_crop"], [cell["window_w"], cell["window_h"]]
                )
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])
            if cell["section"] == "release":
                self.assertEqual(data["window"]["w"], cell["window_w"])
                self.assertEqual(data["window"]["h"], cell["window_h"])
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])

    def test_film_rows_carry_the_eleven_column_strip_per_facing(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for facing in timeline.FACINGS:
            for zone in ("zone_1", "zone_2"):
                film = [
                    c for c in sheet.cells
                    if c["section"] == "film" and c["pose_facing"] == facing
                    and c["zone"] == zone
                ]
                self.assertEqual(list(timeline.STRIP), [c["pose"] for c in film])

    def test_apng_frames_show_four_cross_lanes_for_all_34_ticks(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for pair in timeline.PAIRS:
            frames = timeline.build_apng_frames(sheet, pair)
            self.assertEqual(timeline.TOTAL_TICKS, len(frames))
            sizes = {(f.width, f.height) for f in frames}
            self.assertEqual(1, len(sizes))


class ValidatorTest(SyntheticCrossFixture):
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
        self.assertEqual(414, result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(c for c in sheet.cells if c["section"] == "lane")
        x, y = cell["rect"][0] + 8, cell["rect"][1] + 8
        canvas.put(x, y, (1, 2, 3, 255))
        result = metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        write_rect(
            self.dirs["transition_dir"] / timeline.pose_filename("w0", "down"),
            5, 5,
        )
        result = metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_tick_math_passes_on_the_pinned_plan(self) -> None:
        plan = timeline.build_plan(self.reference)
        self.assertEqual(
            [], metrics.check_tick_math(plan, plan["constants"])
        )

    def test_tick_math_catches_pose_facing_and_position_drift(self) -> None:
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["MID"]["ticks"][6]["pose"] = "a0"
        failures = metrics.check_tick_math(plan, plan["constants"])
        self.assertTrue(any("windup poses" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["EARLY"]["ticks"][8]["draw"][1] += 1
        failures = metrics.check_tick_math(plan, plan["constants"])
        self.assertTrue(any("tween+offset" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["RD"]["lanes"]["LATE"]["ticks"][12]["pose_facing"] = "right"
        failures = metrics.check_tick_math(plan, plan["constants"])
        self.assertTrue(any("facing" in f for f in failures))

    def test_bounds_check_catches_an_escaping_draw(self) -> None:
        plan = timeline.build_plan(self.reference)
        self.assertEqual([], metrics.check_bounds(plan))
        plan["pairs"]["DR"]["lanes"]["EARLY"]["ticks"][8]["draw"][0] = 70
        self.assertTrue(metrics.check_bounds(plan))

    def test_overlap_check_catches_a_wrong_arrival_phase(self) -> None:
        report = {
            "overlap": {
                pair: {
                    lane: {
                        "rem_after_onset": metrics.EXPECTED_REM[lane],
                        "arrival_phase": metrics.ARRIVAL_PHASE[lane][0],
                        "arrival_phase_tick": metrics.ARRIVAL_PHASE[lane][1],
                    }
                    for lane in timeline.SECTION_LANES
                }
                for pair in timeline.PAIRS
            }
        }
        self.assertEqual([], metrics.check_overlaps(report))
        report["overlap"]["DR"]["MID"]["arrival_phase"] = "recovery"
        self.assertTrue(metrics.check_overlaps(report))

    def test_jump_tables_span_the_pre_registered_ranges(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                rows = report["seam_tables"][pair][lane]["rows"]
                onset = timeline.lane_onset(lane)
                want = 14 if lane == "EARLY" else 12
                self.assertEqual(want, len(rows), f"{pair}/{lane}")
                self.assertEqual(onset - 2, rows[0]["from_tick"])
                pairs = [(r["pose_from"], r["pose_to"]) for r in rows]
                self.assertIn(("s0", "r0"), pairs)
                if lane == "EARLY":
                    self.assertEqual(("r0", "r0"), pairs[-1])
                else:
                    self.assertEqual(("s0", "r0"), pairs[-1])

    def test_jump_rows_carry_vector_deltas_and_exact_squares(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                for row in report["seam_tables"][pair][lane]["rows"]:
                    dx, dy = row["delta_window_px"]
                    self.assertEqual(
                        row["squared_px"], dx * dx + dy * dy, f"{pair}/{lane}"
                    )
                    self.assertEqual(
                        row["squared_px"],
                        row["delta_a_px"] ** 2 + row["delta_b_px"] ** 2,
                    )
        # The pre-registered release displacement vectors.
        for pair in timeline.PAIRS:
            expected = {"EARLY": (4, 9, 97), "MID": (3, 9, 90),
                        "LATE": (0, 9, 81), "CONTROL": (0, 9, 81)}
            for lane, (d_a, d_b, squared) in expected.items():
                sal = report["seam_tables"][pair][lane]["release_salience"]
                row = sal["release_row"]
                self.assertEqual(d_a, row["delta_a_px"], f"{pair}/{lane}")
                self.assertEqual(d_b, row["delta_b_px"], f"{pair}/{lane}")
                self.assertEqual(squared, row["squared_px"], f"{pair}/{lane}")

    def test_release_salience_dominates_both_axes_on_synthetic_bytes(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                sal = report["seam_tables"][pair][lane]["release_salience"]
                self.assertTrue(
                    sal["pose_axis_strictly_dominant"], f"{pair}/{lane}"
                )
                self.assertTrue(
                    sal["squared_axis_strictly_dominant"], f"{pair}/{lane}"
                )
        self.assertEqual([], metrics.check_salience(report))

    def test_salience_check_flags_a_non_dominant_release(self) -> None:
        report = self.build_report()
        sal = report["seam_tables"]["DR"]["MID"]["release_salience"]
        sal["pose_axis_strictly_dominant"] = False
        failures = metrics.check_salience(report)
        self.assertTrue(any("DR/MID" in f for f in failures))

    def test_anchoring_rows_are_internally_consistent(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.SECTION_LANES:
                rows = report["anchoring"][pair][lane]
                self.assertEqual(4, len(rows), f"{pair}/{lane}")
                window = timeline.window_spec(
                    *timeline.lane_axes(pair, lane)
                )
                for row in rows:
                    if window["kind"] == "cross":
                        self.assertEqual(
                            row["crossing_px_total"],
                            row["crossing_px_true"] + row["crossing_px_near"],
                        )
                    else:
                        self.assertIsNone(row["crossing_px_near"])
                        self.assertIsNone(row["body_overlap_near_px"])

    def test_cross_crossing_depth_is_tween_independent(self) -> None:
        """The pre-registered geometry: the B-offset is tween-independent, so
        a cross lane's crossing depth is constant across its active ticks."""
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                depths = {
                    row["crossing_depth_px"]
                    for row in report["anchoring"][pair][lane]
                }
                self.assertEqual(1, len(depths), f"{pair}/{lane}")

    def test_context_bar_fires_on_synthetic_bytes(self) -> None:
        """Identical rects across facings give idle<->idle = 0, so the 44.44
        reproduction bar must fire (the failing-direction exercise)."""
        report = self.build_report()
        self.assertEqual(0.0, report["context_deltas"]["idle"]["popping_pct"])
        self.assertTrue(metrics.check_context(report))

    def test_degenerate_regression_fires_on_synthetic_bytes(self) -> None:
        report = self.build_report()
        failures = metrics.check_degenerate_regression(
            report, REPO / "reviews" / "calibration-v8" / "seam-metrics.json"
        )
        # Synthetic bytes cannot reproduce the banked deltas - the bar fires.
        self.assertTrue(failures)

    def test_degenerate_regression_flags_a_missing_metrics_file(self) -> None:
        report = self.build_report()
        failures = metrics.check_degenerate_regression(
            report, self.root / "missing.json"
        )
        self.assertTrue(any("missing" in f for f in failures))

    def test_export_pins_verify_the_banked_chain_and_flag_v9(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["export_pins"]["failures"])
        self.assertEqual(26, report["export_pins"]["verified"])
        import shutil

        fake_root = self.root / "exports"
        shutil.copytree(REPO / "exports", fake_root)
        (fake_root / "calibration-v9").mkdir()
        report = self.build_report(exports_root=fake_root)
        self.assertTrue(
            any("calibration-v9" in f for f in report["export_pins"]["failures"])
        )

    def test_check_report_groups_integrity_and_measurement(self) -> None:
        report = self.build_report()
        grouped = metrics.check_report(report)
        self.assertEqual({"integrity", "measurement"}, set(grouped))
        # Synthetic bytes: measurement (salience) passes; integrity carries
        # the expected context + degenerate reds and nothing structural.
        self.assertEqual([], grouped["measurement"])
        self.assertTrue(grouped["integrity"])
        self.assertEqual([], report["tick_math_failures"])
        self.assertEqual([], report["bounds_failures"])
        self.assertEqual([], report["purity"]["failures"])

    def test_report_is_deterministic(self) -> None:
        first = self.build_report()
        second = self.build_report()
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertTrue(first["sheet"]["deterministic"])


class RealArtifactsTest(unittest.TestCase):
    """The real banked exports drive the sheet; committed artifacts stay
    stable. Cross-facing pose numbers are UNMEASURED before this sprint's
    artifacts exist - these tests assert committed-artifact consistency and
    the pre-known banked values only, never an assumed cross-facing answer."""

    METRICS_PATH = REPO / "reviews" / "calibration-v9" / "cross-seam-metrics.json"
    SHEET_PATH = REPO / "reviews" / "calibration-v9" / "cross-seam-sheet.png"

    def setUp(self) -> None:
        if not (REPO / "exports" / "calibration-v7"
                / "player_1_lane_b_attack_down_x0.png").is_file():
            self.skipTest("banked exports not present")
        self.reference = load_reference()

    def test_real_build_passes_every_integrity_bar(self) -> None:
        report = metrics.build_report(
            real_dirs(), self.reference, sheet_path=self.SHEET_PATH
        )
        grouped = metrics.check_report(report)
        self.assertEqual([], grouped["integrity"])
        self.assertEqual(26, report["export_pins"]["verified"])

    def test_degen_lanes_machine_equal_the_banked_v8_control_rows(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        self.assertEqual([], report["degenerate_regression_failures"])

    def test_context_reproduces_the_banked_cross_facing_reference(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        self.assertEqual(
            44.44, report["context_deltas"]["idle"]["popping_pct"]
        )

    def test_release_rows_carry_the_banked_pose_deltas_per_attack_facing(
        self,
    ) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        expected_pose = {"DR": 31.97, "RD": 27.18}  # banked per-facing release
        for pair, want in expected_pose.items():
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                sal = report["seam_tables"][pair][lane]["release_salience"]
                self.assertEqual(want, sal["release_row"]["pose_delta_pct"])

    def test_cross_crossing_depths_equal_the_banked_anchoring_constants(
        self,
    ) -> None:
        """DR strikes with k0-right (banked leading edge 28 -> 3px); RD with
        k0-down (banked 27 -> 2px) - the v4-banked anchoring values, now
        tween-independent by the cross geometry."""
        report = metrics.build_report(real_dirs(), self.reference)
        for pair, depth in (("DR", 3), ("RD", 2)):
            for lane in ("EARLY", "MID", "LATE", "CONTROL"):
                for row in report["anchoring"][pair][lane]:
                    self.assertEqual(depth, row["crossing_depth_px"], pair)

    def test_committed_metrics_match_a_fresh_report(self) -> None:
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v9 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        report = metrics.build_report(
            real_dirs(), self.reference,
            sheet_path=self.SHEET_PATH,
            apng_dir=REPO / "reviews" / "calibration-v9",
        )
        self.assertEqual(committed, json.loads(json.dumps(report)))

    def test_banked_sheet_regenerates_byte_identical(self) -> None:
        if not self.SHEET_PATH.is_file():
            self.skipTest("calibration-v9 sheet not banked yet")
        sheet = timeline.CrossSeamSheet(real_dirs(), self.reference)
        self.assertEqual(self.SHEET_PATH.read_bytes(), sheet.build().encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        apng_dir = REPO / "reviews" / "calibration-v9"
        targets = [
            apng_dir / f"cross-lanes-{pair.lower()}.apng"
            for pair in timeline.PAIRS
        ]
        if not all(t.is_file() for t in targets):
            self.skipTest("calibration-v9 apng aids not banked yet")
        sheet = timeline.CrossSeamSheet(real_dirs(), self.reference)
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
                    (Path(temp) / f"cross-lanes-{pair.lower()}.apng").is_file()
                )

    def test_metrics_main_matches_the_committed_check_outcome(self) -> None:
        """The --check exit reflects the committed measurement outcome: the
        integrity bars must be green on real bytes; the salience bars carry
        whatever the committed metrics banked (pre-registered split)."""
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v9 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        committed_reds = len(
            metrics.check_salience({"seam_tables": committed["seam_tables"]})
        )
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "cross-seam-metrics.json"
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
