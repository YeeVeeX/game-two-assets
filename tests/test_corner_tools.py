from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import corner_metrics as metrics
import make_corner_timeline as timeline
import make_turn_timeline as v10
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


class SyntheticCornerFixture(unittest.TestCase):
    """Distinct rects per pose, IDENTICAL across facings, f3 == idle (the
    byte-copy law holds on synthetic bytes), so every cell is attributable
    byte-for-byte AND the anchor bars are exercised in their FAILING
    direction on synthetic bytes: context deltas collapse to 0 (the banked v9
    equality fires), walk-cycle boundaries differ from the banked v1 numbers
    (the walk-pair anchor fires), the committed-v10 row values no longer match
    (the regression bar fires), and the remedy cut exceeds the collapsed band
    max 0.0 (M1 fires) - the banked test pattern."""

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
                    self.dirs[v10.POSE_DIRS[pose]] / v10.pose_filename(pose, facing),
                    x, y,
                )
        self.reference = load_reference()

    def sheet(self) -> timeline.CornerTimelineSheet:
        return timeline.CornerTimelineSheet(self.dirs, self.reference)


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = load_reference()
        self.plan = timeline.build_plan(self.reference)

    def test_lane_set_is_the_pre_registered_five(self) -> None:
        self.assertEqual(
            ("CORNER", "REM_EARLY", "REM_MID", "CONTROL", "DEGEN"), timeline.LANES
        )
        for pair in timeline.PAIRS:
            self.assertEqual(
                list(timeline.LANES), list(self.plan["pairs"][pair]["lanes"])
            )

    def test_turn_ticks_rem_and_b_facing_counts(self) -> None:
        """CORNER turns ON the arrival tick: REM 0 with exactly ONE B-facing
        tick inside the A step; CONTROL is REM 0 with zero."""
        for pair in timeline.PAIRS:
            lanes = self.plan["pairs"][pair]["lanes"]
            self.assertEqual(
                {"CORNER": 14, "REM_EARLY": 3, "REM_MID": 6, "CONTROL": 15},
                {
                    lane: lanes[lane]["turn_tick"]
                    for lane in metrics.CUT_LANES
                },
            )
            self.assertEqual(
                {"CORNER": 0, "REM_EARLY": 11, "REM_MID": 8, "CONTROL": 0},
                {
                    lane: lanes[lane]["rem_after_turn"]
                    for lane in metrics.CUT_LANES
                },
            )
            self.assertEqual(
                {"CORNER": 1, "REM_EARLY": 12, "REM_MID": 9, "CONTROL": 0},
                {
                    lane: lanes[lane]["b_facing_ticks_in_a_step"]
                    for lane in metrics.CUT_LANES
                },
            )
            self.assertIsNone(lanes["DEGEN"]["turn_tick"])

    def test_corner_commits_b_on_the_arrival_tick(self) -> None:
        """The derived engine handoff: turn == commit == arrival == t14, first
        B advance t15 (CONTROL pays the extra stand tick)."""
        for pair in timeline.PAIRS:
            lanes = self.plan["pairs"][pair]["lanes"]
            for lane in timeline.LANES:
                self.assertEqual(14, lanes[lane]["arrival_tick"])
                want = 15 if lane == "CONTROL" else 14
                self.assertEqual(want, lanes[lane]["b_commit_tick"], lane)
                self.assertEqual(want + 1, lanes[lane]["first_b_advance_tick"])

    def test_hold_and_corner_tick_sets_are_pre_registered(self) -> None:
        for pair in timeline.PAIRS:
            lanes = self.plan["pairs"][pair]["lanes"]
            self.assertEqual(list(range(3, 15)), lanes["REM_EARLY"]["hold_ticks"])
            self.assertEqual(list(range(6, 15)), lanes["REM_MID"]["hold_ticks"])
            self.assertEqual([], lanes["CORNER"]["hold_ticks"])
            self.assertEqual([14], lanes["CORNER"]["corner_ticks"])
            for lane in ("CONTROL", "DEGEN"):
                self.assertEqual([], lanes[lane]["hold_ticks"])
                self.assertEqual([], lanes[lane]["corner_ticks"])

    def test_settle_hold_draws_f3_in_facing_b_on_every_held_tick(self) -> None:
        for pair in timeline.PAIRS:
            _, turn_facing = timeline.PAIR_AXES[pair]
            for lane in ("REM_EARLY", "REM_MID"):
                data = self.plan["pairs"][pair]["lanes"][lane]
                held = [t for t in data["ticks"] if t["tick"] in data["hold_ticks"]]
                self.assertEqual(
                    {("f3", turn_facing, "strafe_hold")},
                    {(t["pose"], t["pose_facing"], t["phase"]) for t in held},
                )

    def test_corner_tick_draws_f3_in_facing_b_at_the_arrival_position(self) -> None:
        for pair in timeline.PAIRS:
            _, turn_facing = timeline.PAIR_AXES[pair]
            tick = self.plan["pairs"][pair]["lanes"]["CORNER"]["ticks"][14]
            self.assertEqual(("f3", turn_facing, "turn_arrive"),
                             (tick["pose"], tick["pose_facing"], tick["phase"]))
            self.assertEqual(32, tick["a_px"])
            self.assertEqual(0, tick["b_px"])

    def test_tween_positions_and_walk_mapping_are_the_pinned_sequence(self) -> None:
        corner = self.plan["pairs"]["DR"]["lanes"]["CORNER"]["ticks"]
        self.assertEqual(
            [0, 0, 1, 2, 4, 7, 11, 14, 18, 21, 25, 28, 30, 31, 32],
            [t["a_px"] for t in corner[:15]],
        )
        self.assertEqual(
            ["f0"] * 4 + ["f1"] * 3 + ["f2"] * 3 + ["f3"] * 3,
            [t["pose"] for t in corner[2:15]],
        )

    def test_facing_swaps_at_the_turn_tick_and_nowhere_else(self) -> None:
        for pair in timeline.PAIRS:
            walk, turn_facing = timeline.PAIR_AXES[pair]
            for lane in metrics.CUT_LANES:
                data = self.plan["pairs"][pair]["lanes"][lane]
                turn = data["turn_tick"]
                for tick in data["ticks"]:
                    want = walk if tick["tick"] < turn else turn_facing
                    self.assertEqual(
                        want, tick["pose_facing"],
                        f"{pair}/{lane}/t{tick['tick']}",
                    )
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]
            self.assertEqual({walk}, {t["pose_facing"] for t in degen["ticks"]})

    def test_cut_poses_are_forced_by_the_two_models(self) -> None:
        """CORNER cuts f3->f3 (frame-identical, f3 is the idle byte-copy);
        both remedy classes cut f0->f3; CONTROL cuts f3->idle."""
        for pair in timeline.PAIRS:
            lanes = self.plan["pairs"][pair]["lanes"]
            for lane, want in (
                ("CORNER", ("f3", "f3")), ("REM_EARLY", ("f0", "f3")),
                ("REM_MID", ("f0", "f3")), ("CONTROL", ("f3", "idle")),
            ):
                turn = lanes[lane]["turn_tick"]
                before = lanes[lane]["ticks"][turn - 1]
                after = lanes[lane]["ticks"][turn]
                self.assertEqual(want, (before["pose"], after["pose"]), lane)

    def test_draw_vectors_are_tween_along_a_then_along_b(self) -> None:
        # The pre-registered key vectors from the rationale, spot-checked.
        dr = self.plan["pairs"]["DR"]["lanes"]
        self.assertEqual([0, 31], dr["CORNER"]["ticks"][13]["draw"])   # f3@A
        self.assertEqual([0, 32], dr["CORNER"]["ticks"][14]["draw"])   # f3@B turn
        self.assertEqual([1, 32], dr["CORNER"]["ticks"][15]["draw"])   # wrap
        self.assertEqual([0, 2], dr["REM_EARLY"]["ticks"][3]["draw"])  # hold start
        self.assertEqual([0, 11], dr["REM_MID"]["ticks"][6]["draw"])
        self.assertEqual([0, 32], dr["CONTROL"]["ticks"][15]["draw"])  # stand
        self.assertEqual([0, 33], dr["DEGEN"]["ticks"][15]["draw"])    # step 2
        rd = self.plan["pairs"]["RD"]["lanes"]
        self.assertEqual([31, 0], rd["CORNER"]["ticks"][13]["draw"])
        self.assertEqual([32, 0], rd["CORNER"]["ticks"][14]["draw"])
        self.assertEqual([32, 1], rd["CORNER"]["ticks"][15]["draw"])
        self.assertEqual([2, 0], rd["REM_EARLY"]["ticks"][3]["draw"])
        self.assertEqual([33, 0], rd["DEGEN"]["ticks"][15]["draw"])

    def test_no_attack_pose_anywhere(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.LANES:
                for tick in self.plan["pairs"][pair]["lanes"][lane]["ticks"]:
                    self.assertIn(tick["pose"], v10.WALK_POSES)

    def test_windows_hold_every_opaque_pixel_by_construction(self) -> None:
        self.assertEqual(
            [], metrics.check_bounds(self.plan, v10.build_plan(self.reference))
        )

    def test_zoom_strips_and_wrap_strips_pick_the_declared_ticks(self) -> None:
        for pair in timeline.PAIRS:
            self.assertEqual(
                [13, 14, 15, 16],
                [t["tick"] for t in timeline.zoom_strip(self.plan, pair, "CORNER")],
            )
            self.assertEqual(
                [2, 3, 4],
                [t["tick"] for t in timeline.zoom_strip(self.plan, pair, "REM_EARLY")],
            )
            self.assertEqual(
                [5, 6, 7],
                [t["tick"] for t in timeline.zoom_strip(self.plan, pair, "REM_MID")],
            )
            self.assertIsNone(
                self.plan["pairs"][pair]["lanes"]["DEGEN"]["zoom_ticks"]
            )
            for lane in timeline.LANES:
                start = 14 if lane == "CONTROL" else 13
                self.assertEqual(
                    list(range(start, start + 4)),
                    [t["tick"] for t in timeline.wrap_strip(self.plan, pair, lane)],
                )

    def test_windows_and_crops_match_the_lane_kinds(self) -> None:
        for pair, crop in (("DR", [32, 64]), ("RD", [64, 32])):
            for lane in metrics.CUT_LANES:
                window = self.plan["pairs"][pair]["lanes"][lane]["window"]
                self.assertEqual("turn", window["kind"])
                self.assertEqual((64, 64), (window["w"], window["h"]))
                self.assertEqual([0, 31], window["t0_a_span"])
                self.assertEqual([32, 63], window["t1_a_span"])
                self.assertEqual(
                    crop, self.plan["pairs"][pair]["lanes"][lane]["turn_crop"]
                )
            degen = self.plan["pairs"][pair]["lanes"]["DEGEN"]["window"]
            self.assertEqual("degen", degen["kind"])
            self.assertEqual([64, 95], degen["t2_a_span"])

    def test_sheet_ticks_span_t01_through_t21(self) -> None:
        for pair in timeline.PAIRS:
            for lane in timeline.LANES:
                self.assertEqual(
                    list(range(1, 22)),
                    [
                        t["tick"]
                        for t in self.plan["pairs"][pair]["lanes"][lane]["sheet_ticks"]
                    ],
                )

    def test_control_and_degen_ticks_are_the_banked_v10_lanes(self) -> None:
        """The hard regression bar at plan level: v11's anchor lanes are the
        banked v10 lanes, tick dict for tick dict."""
        banked = v10.build_plan(self.reference)
        for pair in timeline.PAIRS:
            for lane in ("CONTROL", "DEGEN"):
                self.assertEqual(
                    banked["pairs"][pair]["lanes"][lane]["ticks"],
                    self.plan["pairs"][pair]["lanes"][lane]["ticks"],
                    f"{pair}/{lane}",
                )

    def test_plan_identity_web_passes_and_catches_drift(self) -> None:
        banked = v10.build_plan(self.reference)
        self.assertEqual([], metrics.check_v10_plan_identity(self.plan, banked))
        broken = timeline.build_plan(self.reference)
        broken["pairs"]["DR"]["lanes"]["REM_MID"]["ticks"][4]["pose"] = "f2"
        failures = metrics.check_v10_plan_identity(broken, banked)
        self.assertTrue(any("outside hold" in f for f in failures))
        broken = timeline.build_plan(self.reference)
        broken["pairs"]["RD"]["lanes"]["REM_EARLY"]["ticks"][8]["a_px"] = 99
        failures = metrics.check_v10_plan_identity(broken, banked)
        self.assertTrue(any("hold geometry" in f for f in failures))
        broken = timeline.build_plan(self.reference)
        broken["pairs"]["DR"]["lanes"]["CORNER"]["ticks"][16]["draw"] = [9, 9]
        failures = metrics.check_v10_plan_identity(broken, banked)
        self.assertTrue(any("CORNER plan suffix" in f for f in failures))


class SheetTest(SyntheticCornerFixture):
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
        self.assertEqual(
            {"lane", "cut", "wrap", "cmp", "context", "film"},
            {c["section"] for c in sheet.cells},
        )
        counts = {
            section: len([c for c in sheet.cells if c["section"] == section])
            for section in ("lane", "cut", "wrap", "cmp", "context", "film")
        }
        self.assertEqual(2 * 5 * 2 * 21, counts["lane"])
        self.assertEqual(2 * (4 + 3 + 3 + 3), counts["cut"])
        self.assertEqual(2 * 5 * 4, counts["wrap"])
        self.assertEqual(2 * (2 * 7 + 2 * 11), counts["cmp"])
        self.assertEqual(2 * 5 * 2, counts["context"])
        self.assertEqual(2 * 2 * len(v10.WALK_POSES), counts["film"])
        self.assertEqual(598, len(sheet.cells))

    def test_comparison_bands_pair_the_two_treatments(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for pair in timeline.PAIRS:
            cmp_cells = [
                c for c in sheet.cells
                if c["section"] == "cmp" and c["pair"] == pair
            ]
            lanes = [c["lane"] for c in cmp_cells]
            self.assertEqual(7, lanes.count("CORNER"))
            self.assertEqual(7, lanes.count("CONTROL"))
            self.assertEqual(11, lanes.count("REM_MID"))
            self.assertEqual(11, lanes.count("V10_MID"))
            banked = [c for c in cmp_cells if c["lane"] == "V10_MID"]
            self.assertEqual(list(range(5, 16)), [c["tick"] for c in banked])
            # the banked row carries v10's CYCLING poses, not the held frame
            self.assertNotEqual({"f3"}, {c["pose"] for c in banked})

    def test_lane_cells_draw_at_the_plan_positions(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for cell in sheet.cells:
            if cell["section"] != "lane":
                continue
            tick = sheet.plan["pairs"][cell["pair"]]["lanes"][cell["lane"]][
                "ticks"
            ][cell["tick"]]
            self.assertEqual(tick["draw"], cell["draw"])
            self.assertEqual(tick["pose"], cell["pose"])
            self.assertEqual(tick["pose_facing"], cell["pose_facing"])

    def test_cut_cells_use_the_crop_and_wrap_cells_the_full_window(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for cell in sheet.cells:
            data = None
            if cell["section"] in ("cut", "wrap"):
                data = sheet.plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]
            if cell["section"] == "cut":
                self.assertEqual(
                    data["turn_crop"], [cell["window_w"], cell["window_h"]]
                )
                self.assertEqual(timeline.TURN_ZOOM_SCALE, cell["scale"])
            if cell["section"] == "wrap":
                self.assertEqual(data["window"]["w"], cell["window_w"])
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])
            if cell["section"] in ("cmp", "context"):
                self.assertEqual(timeline.TWOX_SCALE, cell["scale"])

    def test_apng_frames_show_five_panes_for_all_30_ticks(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for pair in timeline.PAIRS:
            frames = timeline.build_apng_frames(sheet, pair)
            self.assertEqual(timeline.TOTAL_TICKS, len(frames))
            self.assertEqual(1, len({(f.width, f.height) for f in frames}))
            self.assertEqual(
                (64 * 5 + 6 * 4) * timeline.APNG_SCALE, frames[0].width
            )


class ValidatorTest(SyntheticCornerFixture):
    def build_report(self, **kwargs) -> dict:
        return metrics.build_report(
            self.dirs, self.reference,
            exports_root=kwargs.pop("exports_root", REPO / "exports"),
            **kwargs,
        )

    def test_purity_passes_on_a_fresh_build(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        result = metrics.v10m.check_purity(canvas, sheet, self.dirs)
        self.assertEqual([], result["failures"])
        self.assertEqual(598, result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(c for c in sheet.cells if c["section"] == "cmp")
        canvas.put(cell["rect"][0] + 8, cell["rect"][1] + 8, (1, 2, 3, 255))
        self.assertTrue(
            metrics.v10m.check_purity(canvas, sheet, self.dirs)["failures"]
        )

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        write_rect(self.dirs["walk_dir"] / v10.pose_filename("f2", "down"), 5, 5)
        self.assertTrue(
            metrics.v10m.check_purity(canvas, sheet, self.dirs)["failures"]
        )

    def test_tick_math_passes_on_the_pinned_plan(self) -> None:
        self.assertEqual(
            [], metrics.check_tick_math(timeline.build_plan(self.reference))
        )

    def test_tick_math_catches_model_pose_facing_and_position_drift(self) -> None:
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["REM_MID"]["ticks"][8]["pose"] = "f1"
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("pose/phase" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["CORNER"]["ticks"][14]["phase"] = "strafe"
        failures = metrics.check_tick_math(plan)
        self.assertTrue(any("turn_arrive" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["RD"]["lanes"]["CORNER"]["ticks"][8]["draw"][0] += 1
        self.assertTrue(any("draw" in f for f in metrics.check_tick_math(plan)))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["RD"]["lanes"]["REM_EARLY"]["ticks"][12]["pose_facing"] = "right"
        self.assertTrue(any("facing" in f for f in metrics.check_tick_math(plan)))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["CORNER"]["turn_tick"] = 13
        self.assertTrue(any("turn tick" in f for f in metrics.check_tick_math(plan)))

    def test_bounds_check_catches_an_escaping_draw(self) -> None:
        plan = timeline.build_plan(self.reference)
        banked = v10.build_plan(self.reference)
        self.assertEqual([], metrics.check_bounds(plan, banked))
        plan["pairs"]["DR"]["lanes"]["CORNER"]["ticks"][16]["draw"][0] = 70
        self.assertTrue(metrics.check_bounds(plan, banked))

    def test_jump_tables_span_t01_through_t21_with_exact_squares(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in timeline.LANES:
                rows = report["lane_tables"][pair][lane]["rows"]
                self.assertEqual(20, len(rows), f"{pair}/{lane}")
                self.assertEqual(1, rows[0]["from_tick"])
                self.assertEqual(21, rows[-1]["to_tick"])
                for row in rows:
                    dx, dy = row["delta_window_px"]
                    self.assertEqual(row["squared_px"], dx * dx + dy * dy)
                    self.assertEqual(
                        row["squared_px"],
                        row["delta_a_px"] ** 2 + row["delta_b_px"] ** 2,
                    )

    def test_corner_cut_and_wrap_rows_carry_the_pre_registered_vectors(self) -> None:
        """The corner cut rides the last tween pixel (1,0) at t13->t14 and the
        wrap pivots (0,1) at t14->t15 - no stand beat anywhere."""
        report = self.build_report()
        for pair in timeline.PAIRS:
            rows = report["lane_tables"][pair]["CORNER"]["rows"]
            cut = next(r for r in rows if r["to_tick"] == 14)
            self.assertEqual(("f3", "f3"), (cut["pose_from"], cut["pose_to"]))
            self.assertNotEqual(cut["pose_from_facing"], cut["pose_to_facing"])
            self.assertEqual((1, 0), (cut["delta_a_px"], cut["delta_b_px"]))
            wrap = next(r for r in rows if r["from_tick"] == 14)
            self.assertEqual(("f3", "f0"), (wrap["pose_from"], wrap["pose_to"]))
            self.assertEqual((0, 1), (wrap["delta_a_px"], wrap["delta_b_px"]))
            for lane in metrics.REMEDY_LANES:
                lane_rows = report["lane_tables"][pair][lane]["rows"]
                wrap = next(r for r in lane_rows if r["from_tick"] == 14)
                self.assertEqual(
                    ("f3", "f0"), (wrap["pose_from"], wrap["pose_to"])
                )
                self.assertEqual((0, 1), (wrap["delta_a_px"], wrap["delta_b_px"]))

    def test_hold_rows_are_zero_by_construction(self) -> None:
        report = self.build_report()
        for pair in timeline.PAIRS:
            for lane in metrics.REMEDY_LANES:
                holds = set(range(timeline.LANE_TURN[lane], 15))
                rows = [
                    r for r in report["lane_tables"][pair][lane]["rows"]
                    if r["from_tick"] in holds and r["to_tick"] in holds
                ]
                self.assertTrue(rows)
                self.assertEqual({0.0}, {r["pose_delta_pct"] for r in rows})

    def test_hold_structure_check_catches_a_broken_hold(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["hold_structure_failures"])
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["REM_MID"]["ticks"][8]["pose"] = "f1"
        failures = metrics.check_hold_structure(
            plan, report["lane_tables"]
        )
        self.assertTrue(any("held pose" in f for f in failures))
        plan = timeline.build_plan(self.reference)
        plan["pairs"]["DR"]["lanes"]["REM_EARLY"]["hold_ticks"] = [3, 4]
        failures = metrics.check_hold_structure(plan, report["lane_tables"])
        self.assertTrue(any("hold ticks" in f for f in failures))

    def test_corner_cut_anchor_holds_on_synthetic_and_catches_a_mismatch(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["corner_cut_anchor_failures"])
        tables = report["lane_tables"]
        tables["DR"]["CORNER"]["turn_cut"]["pose_delta_pct"] = 99.9
        failures = metrics.check_corner_cut_anchor(tables, report["context_deltas"])
        self.assertTrue(any("DR/CORNER" in f for f in failures))

    def test_remedy_cut_anchor_holds_and_catches_divergence(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["remedy_cut_anchor_failures"])
        tables = report["lane_tables"]
        tables["RD"]["REM_MID"]["turn_cut"]["pose_delta_pct"] = 12.5
        failures = metrics.check_remedy_cut_anchor(tables)
        self.assertTrue(any("differ" in f for f in failures))

    def test_context_and_walk_pair_anchors_fire_on_synthetic_bytes(self) -> None:
        report = self.build_report()
        self.assertEqual(0.0, report["context_deltas"]["idle"]["popping_pct"])
        self.assertTrue(report["context_anchor_failures"])
        self.assertTrue(report["walk_pair_anchor_failures"])

    def test_band_fires_on_synthetic_bytes(self) -> None:
        """The collapsed band max is 0.0 while the remedy cut is nonzero - M1
        must fire (failing-direction), and its live subjects are flagged."""
        report = self.build_report()
        self.assertEqual(0.0, report["band"]["band_max"])
        failures = metrics.v10m.check_band(report["band"])
        self.assertTrue(any("REM_" in f for f in failures))
        subjects = {
            key for key, cut in report["band"]["cuts"].items()
            if cut["measurement_subject"]
        }
        self.assertEqual(
            {"DR/REM_EARLY", "DR/REM_MID", "RD/REM_EARLY", "RD/REM_MID"},
            subjects,
        )

    def test_bytecopy_holds_on_synthetic_and_catches_drift(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["bytecopy_failures"])
        write_rect(self.dirs["walk_dir"] / v10.pose_filename("f3", "down"), 20, 4)
        self.assertTrue(self.build_report()["bytecopy_failures"])

    def test_consistency_and_degen_prefix_hold_and_catch_drift(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["consistency_failures"])
        self.assertEqual([], report["degen_prefix_failures"])
        tables = report["lane_tables"]
        tables["RD"]["DEGEN"]["rows"][4]["pose_delta_pct"] = 77.7
        self.assertTrue(metrics.check_cross_lane_consistency(tables))
        tables["DR"]["DEGEN"]["rows"][3]["delta_a_px"] = 9
        self.assertTrue(metrics.v10m.check_degen_prefix(tables))

    def test_v10_row_regression_fires_on_synthetic_bytes(self) -> None:
        """Synthetic pose deltas cannot equal the committed v10 numbers, so
        the hard regression bar must fire (failing-direction)."""
        report = self.build_report()
        failures = report["v10_row_regression_failures"]
        self.assertTrue(any("CONTROL == v10" in f for f in failures))
        self.assertTrue(any("pose_delta_pct" in f for f in failures))

    def test_v10_plan_identity_and_binding_regression_pass_on_synthetic(self) -> None:
        """Plan geometry and body positions are byte-independent, so both
        pass even on synthetic bytes (passing-direction)."""
        report = self.build_report()
        self.assertEqual([], report["v10_plan_identity_failures"])
        self.assertEqual([], report["binding_regression_failures"])

    def test_binding_regression_catches_a_moved_body(self) -> None:
        report = self.build_report()
        binding = report["binding"]
        binding["DR"]["REM_MID"]["rows"][0]["a_px"] = 99
        self.assertTrue(
            metrics.check_binding_regression(
                binding, REPO / "reviews" / "calibration-v10" / "turn-metrics.json"
            )
        )

    def test_binding_rows_cover_the_declared_tick_sets(self) -> None:
        report = self.build_report()
        want = {"CORNER": 1, "REM_EARLY": 12, "REM_MID": 9}
        for pair in timeline.PAIRS:
            for lane, count in want.items():
                data = report["binding"][pair][lane]
                self.assertEqual(count, len(data["rows"]), f"{pair}/{lane}")
                self.assertEqual(count, data["summary"]["strafe_ticks"])
                for row in data["rows"]:
                    lo, hi = row["body_a_extent"]
                    self.assertLessEqual(lo, hi)

    def test_corner_tick_binds_the_landing_tile_by_arithmetic(self) -> None:
        """At the corner tick a_px is 32: the body sits wholly inside T1's
        span, so T0 overlap is zero on any frame bbox."""
        report = self.build_report()
        for pair in timeline.PAIRS:
            row = report["binding"][pair]["CORNER"]["rows"][0]
            self.assertEqual(14, row["tick"])
            self.assertEqual(0, row["body_overlap_t0_px"])
            self.assertEqual("T1", row["majority_tile"])

    def test_export_pins_verify_the_banked_chain_and_flag_new_dirs(self) -> None:
        report = self.build_report()
        self.assertEqual([], report["export_pins"]["failures"])
        self.assertEqual(26, report["export_pins"]["verified"])
        import shutil

        fake_root = self.root / "exports"
        shutil.copytree(REPO / "exports", fake_root)
        (fake_root / "calibration-v11").mkdir()
        report = self.build_report(exports_root=fake_root)
        self.assertTrue(
            any("calibration-v11" in f for f in report["export_pins"]["failures"])
        )

    def test_check_report_groups_integrity_and_measurement(self) -> None:
        report = self.build_report()
        grouped = metrics.check_report(report)
        self.assertEqual({"integrity", "measurement"}, set(grouped))
        # Synthetic bytes: context/walk-pair/v10-row anchors fire (expected
        # integrity reds) and M1 fires (measurement); nothing structural.
        self.assertTrue(grouped["integrity"])
        self.assertTrue(grouped["measurement"])
        for key in (
            "tick_math_failures", "bounds_failures", "consistency_failures",
            "degen_prefix_failures", "hold_structure_failures",
            "corner_cut_anchor_failures", "remedy_cut_anchor_failures",
            "v10_plan_identity_failures", "binding_regression_failures",
        ):
            self.assertEqual([], report[key], key)
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
    stable. The remedy cut numbers are UNMEASURED before this sprint's
    artifacts exist - these tests assert committed-artifact consistency, the
    pre-known banked values and structural facts only, never an assumed
    remedy answer."""

    METRICS_PATH = REPO / "reviews" / "calibration-v11" / "corner-metrics.json"
    SHEET_PATH = REPO / "reviews" / "calibration-v11" / "corner-sheet.png"
    APNG_DIR = REPO / "reviews" / "calibration-v11"

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

    def test_corner_cut_equals_the_banked_f3_context(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        for pair in timeline.PAIRS:
            cut = report["lane_tables"][pair]["CORNER"]["turn_cut"]
            self.assertEqual(44.44, cut["pose_delta_pct"], pair)
        self.assertEqual([], report["corner_cut_anchor_failures"])

    def test_wrap_rows_equal_the_banked_v1_wrap(self) -> None:
        """f3 is the idle byte-copy, so every wrap (f3->f0@B) equals the
        banked v1 f3->f0 pair: right 10.29 (DR), down 15.87 (RD)."""
        report = metrics.build_report(real_dirs(), self.reference)
        for pair, want in (("DR", 10.29), ("RD", 15.87)):
            for lane in ("CORNER",) + metrics.REMEDY_LANES:
                rows = report["lane_tables"][pair][lane]["rows"]
                wrap = next(r for r in rows if r["from_tick"] == 14)
                self.assertEqual(want, wrap["pose_delta_pct"], f"{pair}/{lane}")

    def test_remedy_cut_is_reported_not_assumed(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        for pair in timeline.PAIRS:
            numbers = set()
            for lane in metrics.REMEDY_LANES:
                cut = report["lane_tables"][pair][lane]["turn_cut"]
                self.assertEqual(("f0", "f3"), (cut["pose_from"], cut["pose_to"]))
                self.assertGreater(cut["pose_delta_pct"], 0.0)
                numbers.add(cut["pose_delta_pct"])
            self.assertEqual(1, len(numbers), pair)

    def test_the_v10_regression_bar_is_green_on_real_bytes(self) -> None:
        report = metrics.build_report(real_dirs(), self.reference)
        self.assertEqual([], report["v10_row_regression_failures"])
        self.assertEqual([], report["v10_plan_identity_failures"])
        self.assertEqual([], report["binding_regression_failures"])

    def test_committed_metrics_match_a_fresh_report(self) -> None:
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v11 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        report = metrics.build_report(
            real_dirs(), self.reference,
            sheet_path=self.SHEET_PATH, apng_dir=self.APNG_DIR,
        )
        self.assertEqual(committed, json.loads(json.dumps(report)))

    def test_banked_sheet_regenerates_byte_identical(self) -> None:
        if not self.SHEET_PATH.is_file():
            self.skipTest("calibration-v11 sheet not banked yet")
        sheet = timeline.CornerTimelineSheet(real_dirs(), self.reference)
        self.assertEqual(self.SHEET_PATH.read_bytes(), sheet.build().encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        targets = [
            self.APNG_DIR / f"corner-lanes-{pair.lower()}.apng"
            for pair in timeline.PAIRS
        ]
        if not all(t.is_file() for t in targets):
            self.skipTest("calibration-v11 apng aids not banked yet")
        sheet = timeline.CornerTimelineSheet(real_dirs(), self.reference)
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
            self.assertEqual(
                0, timeline.main(["--out", str(out), "--apng-dir", temp])
            )
            self.assertTrue(out.is_file())
            for pair in timeline.PAIRS:
                self.assertTrue(
                    (Path(temp) / f"corner-lanes-{pair.lower()}.apng").is_file()
                )

    def test_metrics_main_matches_the_committed_check_outcome(self) -> None:
        if not self.METRICS_PATH.is_file():
            self.skipTest("calibration-v11 metrics not banked yet")
        committed = json.loads(self.METRICS_PATH.read_text(encoding="utf-8"))
        committed_reds = len(metrics.v10m.check_band(committed["band"]))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "corner-metrics.json"
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
