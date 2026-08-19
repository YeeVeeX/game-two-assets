from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_seam_timeline as timeline
import seam_metrics
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


class SyntheticSeamFixture(unittest.TestCase):
    """Distinct rects per pose so every cell is attributable byte-for-byte.

    a0 and k0 rects are disjoint (release pose delta 100) while walk/w0
    rects overlap heavily, so the release-salience mechanism is exercised in
    its passing direction on synthetic bytes too.
    """

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

    def sheet(self) -> timeline.SeamTimelineSheet:
        return timeline.SeamTimelineSheet(self.dirs, self.reference)


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = load_reference()
        self.plan = timeline.build_plan(self.reference)

    def test_onset_ticks_are_the_pre_registered_classes(self) -> None:
        self.assertEqual(
            {"EARLY": 3, "MID": 6, "LATE": 10, "CONTROL": 15},
            self.plan["constants"]["onset_ticks"],
        )

    def test_rem_after_onset_matches_the_class_table(self) -> None:
        rem = {
            lane: self.plan["lanes"][lane]["rem_after_onset"]
            for lane in timeline.LANES
        }
        self.assertEqual({"EARLY": 11, "MID": 8, "LATE": 4, "CONTROL": 0}, rem)

    def test_arrival_is_absolute_tick_14_in_every_lane(self) -> None:
        for lane in timeline.LANES:
            data = self.plan["lanes"][lane]
            self.assertEqual(14, data["arrival_tick"])
        self.assertEqual(32, timeline.tween_position(13, 13))
        self.assertEqual(31, timeline.tween_position(12, 13))

    def test_attack_grammar_is_the_banked_v7_winner_in_every_lane(self) -> None:
        for lane in timeline.LANES:
            ticks = self.plan["lanes"][lane]["ticks"]
            windup = [t["pose"] for t in ticks if t["phase"] == "windup"]
            active = [t["pose"] for t in ticks if t["phase"] == "active"]
            recovery = [t["pose"] for t in ticks if t["phase"] == "recovery"]
            self.assertEqual(["w0"] + ["a0"] * 4, windup, lane)
            self.assertEqual(["k0"] * 4, active, lane)
            self.assertEqual(["s0"] + ["r0"] * 6 + ["x0"], recovery, lane)

    def test_positions_are_tween_plus_state_offset(self) -> None:
        step = self.plan["constants"]["step_frames"]
        for lane in timeline.LANES:
            for tick in self.plan["lanes"][lane]["ticks"]:
                base = timeline.tween_position(max(tick["tick"] - 1, 0), step)
                self.assertEqual(
                    base + tick["offset_px"], tick["axis_px"],
                    f"{lane}/t{tick['tick']}",
                )

    def test_early_onset_seam_cuts_a_true_walk_frame(self) -> None:
        """The pre-registered EARLY adjustment: onset-1 is f0, never idle."""
        ticks = self.plan["lanes"]["EARLY"]["ticks"]
        onset = self.plan["lanes"]["EARLY"]["onset_tick"]
        self.assertEqual("f0", ticks[onset - 1]["pose"])
        self.assertEqual("w0", ticks[onset]["pose"])
        self.assertEqual(-1, ticks[onset]["axis_px"])

    def test_control_lane_is_the_banked_grammar_timeline(self) -> None:
        ticks = self.plan["lanes"]["CONTROL"]["ticks"]
        self.assertEqual(("f3", 32), (ticks[14]["pose"], ticks[14]["axis_px"]))
        self.assertEqual(("w0", 29), (ticks[15]["pose"], ticks[15]["axis_px"]))
        self.assertEqual(("k0", 38), (ticks[20]["pose"], ticks[20]["axis_px"]))
        self.assertEqual(("s0", 32), (ticks[24]["pose"], ticks[24]["axis_px"]))
        self.assertEqual(("x0", 32), (ticks[31]["pose"], ticks[31]["axis_px"]))
        self.assertEqual(("idle", 32), (ticks[32]["pose"], ticks[32]["axis_px"]))

    def test_walk_poses_follow_the_banked_frame_mapping(self) -> None:
        ticks = self.plan["lanes"]["CONTROL"]["ticks"]
        walk = [t["pose"] for t in ticks if t["phase"] == "walk"]
        self.assertEqual(
            ["f0"] * 4 + ["f1"] * 3 + ["f2"] * 3 + ["f3"] * 3, walk
        )

    def test_sheet_ticks_span_onset_minus_2_through_onset_plus_13(self) -> None:
        for lane in timeline.LANES:
            data = self.plan["lanes"][lane]
            span = [t["tick"] for t in data["sheet_ticks"]]
            onset = data["onset_tick"]
            self.assertEqual(list(range(onset - 2, onset + 14)), span)

    def test_no_negative_axis_puts_opaque_pixels_out_of_bounds(self) -> None:
        """Creature pixels start at row/col 2; the deepest excursion is -1."""
        for lane in timeline.LANES:
            for tick in self.plan["lanes"][lane]["ticks"]:
                self.assertGreaterEqual(tick["axis_px"] + 2, 0)

    def test_onset_and_release_strips_pick_the_seam_ticks(self) -> None:
        for lane in timeline.LANES:
            onset = self.plan["lanes"][lane]["onset_tick"]
            strip = [t["tick"] for t in timeline.onset_strip(self.plan, lane)]
            self.assertEqual([onset - 1, onset, onset + 1], strip)
            release = [t["tick"] for t in timeline.release_strip(self.plan, lane)]
            self.assertEqual([onset + 4, onset + 5], release)
            poses = [t["pose"] for t in timeline.release_strip(self.plan, lane)]
            self.assertEqual(["a0", "k0"], poses)


class SheetTest(SyntheticSeamFixture):
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
        # 2 facings x 4 lanes x 2 zones x 16 columns
        self.assertEqual(2 * 4 * 2 * 16, len(lanes))
        onset = [c for c in sheet.cells if c["section"] == "onset"]
        self.assertEqual(2 * 4 * 3, len(onset))
        release = [c for c in sheet.cells if c["section"] == "release"]
        self.assertEqual(2 * 4 * 2, len(release))
        film = [c for c in sheet.cells if c["section"] == "film"]
        self.assertEqual(2 * 2 * len(timeline.STRIP), len(film))

    def test_lane_cells_draw_at_the_plan_positions(self) -> None:
        sheet = self.sheet()
        sheet.build()
        plan = sheet.plan
        for cell in sheet.cells:
            if cell["section"] != "lane":
                continue
            tick = plan["lanes"][cell["lane"]]["ticks"][cell["tick"]]
            self.assertEqual(tick["axis_px"], cell["win_px"])
            self.assertEqual(tick["pose"], cell["pose"])
            self.assertEqual(timeline.WINDOW_TILES, cell["window_tiles"])

    def test_onset_strip_uses_the_two_tile_crop(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for cell in sheet.cells:
            if cell["section"] == "onset":
                self.assertEqual(timeline.ONSET_WINDOW_TILES, cell["window_tiles"])
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])
            if cell["section"] == "release":
                self.assertEqual(timeline.WINDOW_TILES, cell["window_tiles"])

    def test_film_rows_carry_the_eleven_column_strip(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for facing in timeline.FACINGS:
            for zone in ("zone_1", "zone_2"):
                film = [
                    c for c in sheet.cells
                    if c["section"] == "film" and c["facing"] == facing
                    and c["zone"] == zone
                ]
                self.assertEqual(list(timeline.STRIP), [c["pose"] for c in film])

    def test_apng_frames_show_four_lanes_for_all_34_ticks(self) -> None:
        sheet = self.sheet()
        sheet.build()
        frames = timeline.build_apng_frames(sheet, "down")
        self.assertEqual(timeline.TOTAL_TICKS, len(frames))
        sizes = {(f.width, f.height) for f in frames}
        self.assertEqual(1, len(sizes))


class ValidatorTest(SyntheticSeamFixture):
    def build_report(self, **kwargs) -> dict:
        return seam_metrics.build_report(
            self.dirs, self.reference,
            exports_root=kwargs.pop("exports_root", REPO / "exports"),
            **kwargs,
        )

    def test_purity_passes_on_a_fresh_build(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        result = seam_metrics.check_purity(canvas, sheet, self.dirs)
        self.assertEqual([], result["failures"])
        self.assertEqual(340, result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(c for c in sheet.cells if c["section"] == "lane")
        x, y = cell["rect"][0] + 8, cell["rect"][1] + 8
        canvas.put(x, y, (1, 2, 3, 255))
        result = seam_metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        write_rect(
            self.dirs["transition_dir"] / timeline.pose_filename("w0", "down"),
            5, 5,
        )
        result = seam_metrics.check_purity(canvas, sheet, self.dirs)
        self.assertTrue(result["failures"])

    def test_tick_math_passes_on_the_pinned_plan(self) -> None:
        plan = timeline.build_plan(self.reference)
        failures = seam_metrics.check_tick_math(
            plan, plan["constants"]
        )
        self.assertEqual([], failures)

    def test_tick_math_catches_pose_and_position_drift(self) -> None:
        plan = timeline.build_plan(self.reference)
        plan["lanes"]["MID"]["ticks"][6]["pose"] = "a0"
        failures = seam_metrics.check_tick_math(plan, plan["constants"])
        self.assertTrue(any("windup poses" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["lanes"]["EARLY"]["ticks"][8]["axis_px"] += 1
        failures = seam_metrics.check_tick_math(plan, plan["constants"])
        self.assertTrue(any("tween+offset" in f for f in failures))

    def test_overlap_check_catches_a_wrong_arrival_phase(self) -> None:
        report = {
            "overlap": {
                lane: {
                    "rem_after_onset": seam_metrics.EXPECTED_REM[lane],
                    "arrival_phase": seam_metrics.ARRIVAL_PHASE[lane][0],
                    "arrival_phase_tick": seam_metrics.ARRIVAL_PHASE[lane][1],
                }
                for lane in timeline.LANES
            }
        }
        self.assertEqual([], seam_metrics.check_overlaps(report))
        report["overlap"]["MID"]["arrival_phase"] = "recovery"
        self.assertTrue(seam_metrics.check_overlaps(report))
        report["overlap"]["MID"]["arrival_phase"] = "active"
        report["overlap"]["MID"]["rem_after_onset"] = 9
        self.assertTrue(seam_metrics.check_overlaps(report))

    def test_jump_tables_span_the_pre_registered_ranges(self) -> None:
        report = self.build_report()
        for facing in timeline.FACINGS:
            for lane in timeline.LANES:
                rows = report["seam_tables"][facing][lane]["rows"]
                onset = timeline.ONSET_TICKS[lane]
                want = 14 if lane == "EARLY" else 12
                self.assertEqual(want, len(rows), f"{facing}/{lane}")
                self.assertEqual(onset - 2, rows[0]["from_tick"])
                pairs = [(r["pose_from"], r["pose_to"]) for r in rows]
                self.assertIn(("s0", "r0"), pairs)
                if lane == "EARLY":
                    self.assertEqual(("r0", "r0"), pairs[-1])
                else:
                    self.assertEqual(("s0", "r0"), pairs[-1])

    def test_release_salience_dominates_both_axes_on_synthetic_bytes(self) -> None:
        report = self.build_report()
        for facing in timeline.FACINGS:
            for lane in timeline.LANES:
                sal = report["seam_tables"][facing][lane]["release_salience"]
                self.assertTrue(sal["pose_axis_strictly_dominant"], f"{facing}/{lane}")
                self.assertTrue(
                    sal["position_axis_strictly_dominant"], f"{facing}/{lane}"
                )
        self.assertEqual([], seam_metrics.check_tables(report))

    def test_salience_check_flags_a_non_dominant_release(self) -> None:
        report = self.build_report()
        sal = report["seam_tables"]["down"]["MID"]["release_salience"]
        sal["pose_axis_strictly_dominant"] = False
        failures = seam_metrics.check_tables(report)
        self.assertTrue(any("down/MID" in f for f in failures))

    def test_control_regression_needs_the_banked_pairs(self) -> None:
        report = self.build_report()
        failures = seam_metrics.check_control_regression(
            report, REPO / "reviews" / "calibration-v7" / "timeline-metrics.json"
        )
        # Synthetic bytes cannot reproduce the banked deltas - the bar fires.
        self.assertTrue(failures)

    def test_control_regression_flags_a_missing_metrics_file(self) -> None:
        report = self.build_report()
        failures = seam_metrics.check_control_regression(
            report, self.root / "missing.json"
        )
        self.assertTrue(any("missing" in f for f in failures))

    def test_export_pins_verify_the_banked_chain(self) -> None:
        result = seam_metrics.check_export_pins(REPO / "exports")
        self.assertEqual([], result["failures"])
        self.assertEqual(seam_metrics.EXPECTED_EXPORT_COUNT, result["verified"])

    def test_export_pins_flag_new_or_missing_exports(self) -> None:
        import shutil

        fake_root = self.root / "exports"
        shutil.copytree(REPO / "exports", fake_root)
        (fake_root / "calibration-v1" / "rogue.png").write_bytes(b"not a pin")
        result = seam_metrics.check_export_pins(fake_root)
        self.assertTrue(any("unpinned" in f for f in result["failures"]))
        (fake_root / "calibration-v1" / "rogue.png").unlink()
        (fake_root / "calibration-v8").mkdir()
        result = seam_metrics.check_export_pins(fake_root)
        self.assertTrue(any("calibration-v8" in f for f in result["failures"]))

    def test_report_is_deterministic(self) -> None:
        first = self.build_report()
        second = self.build_report()
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertTrue(first["sheet"]["deterministic"])


class RealArtifactsTest(unittest.TestCase):
    """The real banked exports drive the sheet; committed artifacts stay stable."""

    def setUp(self) -> None:
        if not (REPO / "exports" / "calibration-v7"
                / "player_1_lane_b_attack_down_x0.png").is_file():
            self.skipTest("banked exports not present")
        self.reference = load_reference()

    def test_real_build_passes_the_full_check(self) -> None:
        report = seam_metrics.build_report(
            real_dirs(), self.reference,
            sheet_path=REPO / "reviews" / "calibration-v8" / "seam-sheet.png",
        )
        failures = seam_metrics.check_report(report)
        self.assertEqual([], failures)
        self.assertEqual(26, report["export_pins"]["verified"])

    def test_control_onset_row_reproduces_the_banked_arrival_numbers(self) -> None:
        report = seam_metrics.build_report(real_dirs(), self.reference)
        for facing, want in (("down", 16.48), ("right", 19.69)):
            rows = report["seam_tables"][facing]["CONTROL"]["rows"]
            onset_row = next(
                r for r in rows if (r["from_tick"], r["to_tick"]) == (14, 15)
            )
            self.assertEqual(want, onset_row["pose_delta_pct"])
            self.assertEqual(-3, onset_row["position_delta_px"])

    def test_release_rows_carry_the_moving_base_displacements(self) -> None:
        report = seam_metrics.build_report(real_dirs(), self.reference)
        expected = {"EARLY": 13, "MID": 12, "LATE": 9, "CONTROL": 9}
        for facing in timeline.FACINGS:
            for lane, px in expected.items():
                sal = report["seam_tables"][facing][lane]["release_salience"]
                self.assertEqual(px, sal["release_row"]["position_delta_px"])
                self.assertEqual(
                    {"down": 27.18, "right": 31.97}[facing],
                    sal["release_row"]["pose_delta_pct"],
                )

    def test_mid_walk_onset_seams_exceed_the_banked_arrival_boundary(self) -> None:
        report = seam_metrics.build_report(real_dirs(), self.reference)
        banked = {"down": 16.48, "right": 19.69}
        for facing in timeline.FACINGS:
            for lane in ("EARLY", "MID", "LATE"):
                rows = report["seam_tables"][facing][lane]["rows"]
                onset = timeline.ONSET_TICKS[lane]
                row = next(
                    r for r in rows
                    if (r["from_tick"], r["to_tick"]) == (onset - 1, onset)
                )
                self.assertEqual("w0", row["pose_to"])
                self.assertGreater(row["pose_delta_pct"], banked[facing])

    def test_banked_seam_sheet_regenerates_byte_identical(self) -> None:
        sheet_path = REPO / "reviews" / "calibration-v8" / "seam-sheet.png"
        if not sheet_path.is_file():
            self.skipTest("calibration-v8 sheet not banked yet")
        sheet = timeline.SeamTimelineSheet(real_dirs(), self.reference)
        self.assertEqual(sheet_path.read_bytes(), sheet.build().encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        apng_dir = REPO / "reviews" / "calibration-v8"
        targets = [apng_dir / f"seam-lanes-{facing}.apng" for facing in timeline.FACINGS]
        if not all(t.is_file() for t in targets):
            self.skipTest("calibration-v8 apng aids not banked yet")
        sheet = timeline.SeamTimelineSheet(real_dirs(), self.reference)
        sheet.build()
        for facing, target in zip(timeline.FACINGS, targets):
            frames = timeline.build_apng_frames(sheet, facing)
            payload = timeline.encode_apng(
                frames, timeline.apng_delays(len(frames))
            )
            self.assertEqual(target.read_bytes(), payload)

    def test_committed_metrics_match_a_fresh_report(self) -> None:
        metrics_path = REPO / "reviews" / "calibration-v8" / "seam-metrics.json"
        if not metrics_path.is_file():
            self.skipTest("calibration-v8 metrics not banked yet")
        committed = json.loads(metrics_path.read_text(encoding="utf-8"))
        report = seam_metrics.build_report(
            real_dirs(), self.reference,
            sheet_path=REPO / "reviews" / "calibration-v8" / "seam-sheet.png",
            apng_dir=REPO / "reviews" / "calibration-v8",
        )
        self.assertEqual(committed, json.loads(json.dumps(report)))

    def test_sheet_main_writes_sheet_and_apng_aids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "sheet.png"
            status = timeline.main(
                ["--out", str(out), "--apng-dir", temp]
            )
            self.assertEqual(0, status)
            self.assertTrue(out.is_file())
            for facing in timeline.FACINGS:
                self.assertTrue((Path(temp) / f"seam-lanes-{facing}.apng").is_file())

    def test_metrics_main_checks_the_real_chain_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "seam-metrics.json"
            status = seam_metrics.main(["--out", str(out), "--check"])
            self.assertEqual(0, status)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual([], seam_metrics.check_report(report))

    def test_metrics_main_reports_missing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            status = seam_metrics.main(
                ["--idle-exports", str(Path(temp) / "nowhere"),
                 "--out", str(Path(temp) / "out.json")]
            )
            self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
