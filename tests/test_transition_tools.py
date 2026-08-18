from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_transition_timeline as timeline
import transition_metrics
from pixel_spec import load_spec
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


class SyntheticTransitionFixture(unittest.TestCase):
    """Distinct rects per pose so every cell is attributable byte-for-byte."""

    POSE_X = {
        "idle": 10, "f0": 11, "f1": 12, "f2": 13, "f3": 10,
        "a0": 14, "k0": 16, "r0": 18, "w0": 20, "s0": 22,
    }
    POSE_Y = {
        "idle": 23, "f0": 23, "f1": 23, "f2": 23, "f3": 23,
        "a0": 25, "k0": 21, "r0": 24, "w0": 22, "s0": 20,
    }

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.transition = self.root / "transition"
        self.recovery = self.root / "recovery"
        self.anticipation = self.root / "anticipation"
        self.attack = self.root / "attack"
        self.walks = self.root / "walks"
        self.idles = self.root / "idles"
        for facing in timeline.FACINGS:
            write_rect(
                self.idles / f"player_1_lane_b_idle_{facing}.png",
                self.POSE_X["idle"], self.POSE_Y["idle"],
            )
            for index in range(4):
                write_rect(
                    self.walks / f"player_1_lane_b_walk_{facing}_f{index}.png",
                    self.POSE_X[f"f{index}"], self.POSE_Y[f"f{index}"],
                )
            write_rect(
                self.anticipation / f"player_1_lane_b_attack_{facing}_a0.png",
                self.POSE_X["a0"], self.POSE_Y["a0"], 6, 3,
            )
            write_rect(
                self.attack / f"player_1_lane_b_attack_{facing}_k0.png",
                self.POSE_X["k0"], self.POSE_Y["k0"], 8, 6,
            )
            write_rect(
                self.recovery / f"player_1_lane_b_attack_{facing}_r0.png",
                self.POSE_X["r0"], self.POSE_Y["r0"], 7, 4,
            )
            write_rect(
                self.transition / f"player_1_lane_b_attack_{facing}_w0.png",
                self.POSE_X["w0"], self.POSE_Y["w0"], 5, 5,
            )
            write_rect(
                self.transition / f"player_1_lane_b_attack_{facing}_s0.png",
                self.POSE_X["s0"], self.POSE_Y["s0"], 4, 6,
            )
        self.reference = load_reference()

    def dirs(self) -> dict[str, Path]:
        return {
            "transition_dir": self.transition,
            "recovery_dir": self.recovery,
            "anticipation_dir": self.anticipation,
            "attack_dir": self.attack,
            "walk_dir": self.walks,
            "idle_dir": self.idles,
        }

    def sheet(self) -> timeline.TransitionTimelineSheet:
        return timeline.TransitionTimelineSheet(
            self.transition, self.recovery, self.anticipation, self.attack,
            self.walks, self.idles, self.reference,
        )


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = load_reference()
        self.plan = timeline.build_plan(self.reference)

    def test_phase_counts_equal_pinned_constants(self) -> None:
        counts: dict[str, int] = {}
        for tick in self.plan["ticks"]:
            counts[tick["phase"]] = counts.get(tick["phase"], 0) + 1
        self.assertEqual(2, counts["idle_pre"])
        self.assertEqual(13, counts["walk"])
        self.assertEqual(5, counts["windup"])
        self.assertEqual(4, counts["active"])
        self.assertEqual(8, counts["recovery"])
        self.assertEqual(2, counts["idle_post"])
        self.assertEqual(34, len(self.plan["ticks"]))

    def test_timeline_b_windup_consumes_tick_one_with_w0(self) -> None:
        windup = [t for t in self.plan["ticks"] if t["phase"] == "windup"]
        self.assertEqual(5, len(windup))
        self.assertEqual(
            ["w0", "a0", "a0", "a0", "a0"], [t["poses"]["B"] for t in windup]
        )
        self.assertEqual(["a0"] * 5, [t["poses"]["A"] for t in windup])
        for tick in windup:
            self.assertEqual(-3, tick["offset_px"])
            self.assertEqual(29, tick["axis_px"])

    def test_timeline_b_recovery_consumes_tick_one_with_s0(self) -> None:
        recovery = [t for t in self.plan["ticks"] if t["phase"] == "recovery"]
        self.assertEqual(8, len(recovery))
        self.assertEqual(
            ["s0"] + ["r0"] * 7, [t["poses"]["B"] for t in recovery]
        )
        self.assertEqual(["r0"] * 8, [t["poses"]["A"] for t in recovery])
        for tick in recovery:
            self.assertEqual(0, tick["offset_px"])
            self.assertEqual(32, tick["axis_px"])

    def test_timelines_identical_except_the_two_transition_ticks(self) -> None:
        differing = [
            t["tick"] for t in self.plan["ticks"]
            if t["poses"]["A"] != t["poses"]["B"]
        ]
        self.assertEqual([15, 24], differing)

    def test_active_holds_k0_at_plus_six_in_both_timelines(self) -> None:
        active = [t for t in self.plan["ticks"] if t["phase"] == "active"]
        self.assertEqual(4, len(active))
        for tick in active:
            self.assertEqual({"k0"}, set(tick["poses"].values()))
            self.assertEqual(6, tick["offset_px"])
            self.assertEqual(38, tick["axis_px"])

    def test_transition_ticks_are_the_two_boundary_regions(self) -> None:
        ticks = [t["tick"] for t in timeline.transition_ticks(self.plan)]
        self.assertEqual([14, 15, 16, 23, 24, 25], ticks)

    def test_boundary_triplets_carry_x_m_y_per_boundary(self) -> None:
        triplets = timeline.boundary_triplets(self.plan)
        onset = [(t["poses"]["B"], t["offset_px"]) for t in triplets["onset"]]
        settle = [(t["poses"]["B"], t["offset_px"]) for t in triplets["settle"]]
        self.assertEqual([("f3", 0), ("w0", -3), ("a0", -3)], onset)
        self.assertEqual([("k0", 6), ("s0", 0), ("r0", 0)], settle)

    def test_walk_positions_follow_smoothstep_monotonically(self) -> None:
        walk = [t for t in self.plan["ticks"] if t["phase"] == "walk"]
        positions = [t["axis_px"] for t in walk]
        self.assertEqual(32, positions[-1])
        self.assertEqual(sorted(positions), positions)
        deltas = [b - a for a, b in zip([0] + positions, positions)]
        self.assertEqual(4, max(deltas))

    def test_attack_ticks_overlap_approach_at_arrival(self) -> None:
        self.assertEqual(14, self.plan["arrival_tick"])
        self.assertEqual(14, self.plan["approach_ticks"][-1]["tick"])
        self.assertEqual(14, self.plan["attack_ticks"][0]["tick"])
        self.assertEqual(20, len(self.plan["attack_ticks"]))


class SheetTest(SyntheticTransitionFixture):
    def test_sheet_is_deterministic(self) -> None:
        self.assertEqual(self.sheet().build().encode(), self.sheet().build().encode())

    def test_sheet_geometry_is_fixed(self) -> None:
        canvas = self.sheet().build()
        self.assertEqual(1460, canvas.width)
        self.assertEqual(2404, canvas.height)

    def test_cell_manifest_covers_every_creature_cell(self) -> None:
        sheet = self.sheet()
        sheet.build()
        by_section: dict[str, int] = {}
        for cell in sheet.cells:
            by_section[cell["section"]] = by_section.get(cell["section"], 0) + 1
        self.assertEqual(
            {"approach": 60, "attack": 160, "twox": 12, "fourx": 12,
             "film": 40, "grammar": 18},
            by_section,
        )

    def test_transition_cells_blit_the_per_timeline_pose(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        for tl, tick_pose in (("A", ("a0", "r0")), ("B", ("w0", "s0"))):
            for tick_index, pose in zip((15, 24), tick_pose):
                cells = [
                    c for c in sheet.cells
                    if c["section"] == "attack" and c["timeline"] == tl
                    and c["tick"] == tick_index and c["facing"] == "down"
                    and c["zone"] == "zone_1"
                ]
                self.assertEqual(1, len(cells))
                cell = cells[0]
                self.assertEqual(pose, cell["pose"])
                x0, y0 = cell["rect"][0], cell["rect"][1]
                self.assertEqual(
                    BODY,
                    canvas.get(
                        x0 + self.POSE_X[pose],
                        y0 + cell["win_px"] + self.POSE_Y[pose],
                    ),
                )

    def test_grammar_row_carries_nine_cells_with_inserted_inbetweens(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        grammar = [
            c for c in sheet.cells
            if c["section"] == "grammar" and c["facing"] == "down"
        ]
        self.assertEqual(
            ["idle", "f1", "w0", "a0", "wind", "k0", "lunge", "s0", "r0"],
            [c["phase"] for c in grammar],
        )
        self.assertEqual(
            [0, 0, -3, 0, -3, 0, 6, 0, 0], [c["win_px"] for c in grammar]
        )
        w0_cell = grammar[2]
        x0, y0 = w0_cell["rect"][0], w0_cell["rect"][1]
        # tell_cell: sprite at half (16) + offset (-3); w0 rect row 22 -> 35
        self.assertEqual(
            BODY, canvas.get(x0 + self.POSE_X["w0"], y0 + 16 - 3 + 22)
        )

    def test_film_rows_carry_the_ten_column_strip(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for zone in ("zone_1", "zone_2"):
            film = [
                c for c in sheet.cells
                if c["section"] == "film" and c["facing"] == "right"
                and c["zone"] == zone
            ]
            self.assertEqual(list(timeline.STRIP), [c["pose"] for c in film])
            self.assertTrue(all(c["window_tiles"] == 1 for c in film))

    def test_twox_row_shows_the_six_transition_ticks_of_timeline_b(self) -> None:
        sheet = self.sheet()
        sheet.build()
        twox = [c for c in sheet.cells if c["section"] == "twox"
                and c["facing"] == "down"]
        self.assertEqual([14, 15, 16, 23, 24, 25], [c["tick"] for c in twox])
        self.assertEqual(
            ["f3", "w0", "a0", "k0", "s0", "r0"], [c["pose"] for c in twox]
        )
        self.assertTrue(all(c["scale"] == 2 for c in twox))

    def test_fourx_strips_show_the_boundary_triplets_at_4x(self) -> None:
        sheet = self.sheet()
        sheet.build()
        fourx = [c for c in sheet.cells if c["section"] == "fourx"
                 and c["facing"] == "right"]
        self.assertEqual([14, 15, 16, 23, 24, 25], [c["tick"] for c in fourx])
        self.assertEqual(
            ["f3", "w0", "a0", "k0", "s0", "r0"], [c["pose"] for c in fourx]
        )
        self.assertTrue(all(c["scale"] == 4 for c in fourx))


class ValidatorTest(SyntheticTransitionFixture):
    def test_purity_passes_on_a_fresh_build(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        result = transition_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertEqual([], result["failures"])
        self.assertEqual(len(sheet.cells), result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(
            c for c in sheet.cells
            if c["section"] == "attack" and c["phase"] == "windup"
        )
        x0, y0 = cell["rect"][0], cell["rect"][1]
        canvas.put(x0 + 5, y0 + 5, (1, 2, 3, 255))
        result = transition_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertTrue(
            any("region mismatch" in failure for failure in result["failures"])
        )

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        write_rect(
            self.transition / "player_1_lane_b_attack_down_w0.png", 21, 22, 5, 5
        )
        result = transition_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertTrue(result["failures"])

    def test_tick_math_passes_and_catches_pin_drift(self) -> None:
        sheet = self.sheet()
        sheet.build()
        self.assertEqual(
            [], transition_metrics.check_tick_math(sheet, self.reference)
        )
        tampered = json.loads(json.dumps(self.reference))
        tampered["attack_timing"]["values"]["windup_frames"]["value"] = 6
        failures = transition_metrics.check_tick_math(sheet, tampered)
        self.assertTrue(any("windup cells" in f for f in failures))
        tampered = json.loads(json.dumps(self.reference))
        tampered["feedback_states"]["lunge_offset"]["windup_px"] = -4
        failures = transition_metrics.check_tick_math(sheet, tampered)
        self.assertTrue(any("windup offset" in f for f in failures))

    def test_tick_math_catches_a_missing_inbetween(self) -> None:
        sheet = self.sheet()
        sheet.build()
        for cell in sheet.cells:
            if (cell["section"] == "attack" and cell["timeline"] == "B"
                    and cell["tick"] == 15):
                cell["pose"] = "a0"
        failures = transition_metrics.check_tick_math(sheet, self.reference)
        self.assertTrue(any("windup poses" in f for f in failures))
        self.assertTrue(
            any("same pose in A and B" in f for f in failures)
        )

    def test_export_pins_verify_and_fail_on_mismatch(self) -> None:
        import hashlib

        pins = {}
        for pose, (dir_key, name) in transition_metrics.POSE_FILES.items():
            for facing in timeline.FACINGS:
                file = self.dirs()[dir_key] / name.format(facing=facing)
                pins[file.name] = hashlib.sha256(file.read_bytes()).hexdigest()
        result = transition_metrics.check_export_pins(self.dirs(), pins)
        self.assertEqual([], result["failures"])
        self.assertEqual(20, result["verified"])
        pins["player_1_lane_b_attack_down_w0.png"] = "0" * 64
        result = transition_metrics.check_export_pins(self.dirs(), pins)
        self.assertTrue(any("sha256" in f for f in result["failures"]))
        del pins["player_1_lane_b_attack_down_s0.png"]
        result = transition_metrics.check_export_pins(self.dirs(), pins)
        self.assertTrue(any("no banked release pin" in f for f in result["failures"]))

    def test_report_is_deterministic(self) -> None:
        reports = [
            transition_metrics.build_report(
                self.transition, self.recovery, self.anticipation, self.attack,
                self.walks, self.idles, self.reference, verify_pins=False,
            )
            for _ in range(2)
        ]
        self.assertEqual(
            json.dumps(reports[0], sort_keys=True),
            json.dumps(reports[1], sort_keys=True),
        )
        report = reports[0]
        self.assertTrue(report["sheet"]["deterministic"])
        self.assertEqual([], report["purity"]["failures"])
        self.assertEqual([], report["tick_math_failures"])
        self.assertIn(
            "export pins were not verified (skipped)",
            transition_metrics.check_report(report),
        )

    def test_boundary_jump_table_reports_the_tested_rows(self) -> None:
        report = transition_metrics.build_report(
            self.transition, self.recovery, self.anticipation, self.attack,
            self.walks, self.idles, self.reference, verify_pins=False,
        )
        for facing in timeline.FACINGS:
            for tl in timeline.TIMELINES:
                rows = report["boundaries"][facing][tl]["boundary_rows"]
                pairs = [(r["from_tick"], r["to_tick"]) for r in rows]
                self.assertEqual(
                    [(14, 15), (15, 16), (19, 20), (23, 24), (24, 25), (31, 32)],
                    pairs,
                )
            b_rows = {
                (r["from_tick"], r["to_tick"]): r
                for r in report["boundaries"][facing]["B"]["boundary_rows"]
            }
            self.assertEqual("w0", b_rows[(14, 15)]["pose_to"])
            self.assertEqual(("w0", "a0"),
                             (b_rows[(15, 16)]["pose_from"],
                              b_rows[(15, 16)]["pose_to"]))
            self.assertEqual(("k0", "s0"),
                             (b_rows[(23, 24)]["pose_from"],
                              b_rows[(23, 24)]["pose_to"]))
            self.assertEqual(-3, b_rows[(14, 15)]["position_delta_px"])
            self.assertEqual(9, b_rows[(19, 20)]["position_delta_px"])
            self.assertEqual(-6, b_rows[(23, 24)]["position_delta_px"])

    def test_release_preservation_is_machine_compared(self) -> None:
        report = transition_metrics.build_report(
            self.transition, self.recovery, self.anticipation, self.attack,
            self.walks, self.idles, self.reference, verify_pins=False,
        )
        release = report["release_preservation"]
        self.assertTrue(release["pose_pair_pinned"])
        self.assertEqual((19, 20), (release["from_tick"], release["to_tick"]))
        self.assertEqual(9, release["position_delta_px"])
        for facing in timeline.FACINGS:
            data = release["per_facing"][facing]
            self.assertTrue(data["identical_across_timelines"])
        self.assertEqual([], transition_metrics.check_release(release))
        tampered = json.loads(json.dumps(release))
        tampered["per_facing"]["down"]["identical_across_timelines"] = False
        self.assertTrue(transition_metrics.check_release(tampered))
        tampered = json.loads(json.dumps(release))
        tampered["position_delta_px"] = 3
        self.assertTrue(transition_metrics.check_release(tampered))

    def test_durations_report_the_consumed_holds(self) -> None:
        plan = timeline.build_plan(self.reference)
        durations = transition_metrics.durations_ms(plan["constants"])
        holds = durations["timeline_b_holds"]
        self.assertEqual(1, holds["w0_ticks"])
        self.assertEqual(4, holds["a0_hold_ticks"])
        self.assertEqual(66.7, holds["a0_hold_ms"])
        self.assertEqual(7, holds["r0_hold_ticks"])
        self.assertEqual(116.7, holds["r0_hold_ms"])

    def test_check_static_flags_each_pre_registered_bar(self) -> None:
        def metrics_with(**overrides) -> dict:
            metrics = {
                "pose": {"feet_row_delta_vs_idle": 0},
                "endpoints": ["idle", "a0"],
                "bridging": {
                    "d_x_m_pct": 16.0, "d_m_y_pct": 17.0, "d_x_y_pct": 31.0,
                    "max_leg_pct": 17.0, "passes": True,
                },
                "nearest_neighbor": {
                    "grammar_deltas": {}, "two_smallest": ["a0", "idle"],
                    "passes": True,
                },
                "walk_deltas": {}, "max_delta_pct": 30.0,
                "head_region_share_vs_idle_pct": 50.0,
            }
            metrics.update(overrides)
            return metrics

        def report_with(**overrides) -> dict:
            return {
                "static": {"down": {"w0": metrics_with(**overrides)}},
                "reference": {"idle_cross_facing": {"popping_pct": 44.44}},
            }

        self.assertEqual([], transition_metrics.check_static(report_with()))
        failures = transition_metrics.check_static(report_with(
            bridging={"d_x_m_pct": 32.0, "d_m_y_pct": 17.0, "d_x_y_pct": 31.0,
                      "max_leg_pct": 32.0, "passes": False},
        ))
        self.assertTrue(any("bridging" in f for f in failures))
        failures = transition_metrics.check_static(report_with(
            nearest_neighbor={"grammar_deltas": {},
                              "two_smallest": ["idle", "k0"], "passes": False},
        ))
        self.assertTrue(any("nearest neighbors" in f for f in failures))
        self.assertTrue(transition_metrics.check_static(
            report_with(max_delta_pct=44.44)
        ))
        self.assertTrue(transition_metrics.check_static(
            report_with(pose={"feet_row_delta_vs_idle": 2})
        ))


class SpecContractTest(unittest.TestCase):
    """The w0/s0 specs carry the declared byte-exact head machinery."""

    HEAD = {
        ("down", "w0"): ((4, 14), (0, 2)),
        ("down", "s0"): ((4, 14), (1, 2)),
        ("right", "w0"): ((4, 9), (-1, 2)),
        ("right", "s0"): ((4, 9), (0, 4)),
    }

    def spec_pair(self, facing: str, name: str):
        idle = load_spec(
            REPO / "sources" / "calibration-v0" / "specs"
            / f"player_1_lane_b_idle_{facing}.json"
        )
        candidate = load_spec(
            REPO / "sources" / "calibration-v6" / "specs"
            / f"player_1_lane_b_attack_{facing}_{name}.json"
        )
        return idle, candidate

    def test_head_block_is_byte_exact_at_the_declared_translation(self) -> None:
        for (facing, name), ((row0, row1), (dx, dy)) in self.HEAD.items():
            idle, candidate = self.spec_pair(facing, name)
            for y in range(row0, row1 + 1):
                for x, char in enumerate(idle.grid[y]):
                    if char == ".":
                        continue
                    self.assertEqual(
                        char, candidate.grid[y + dy][x + dx],
                        f"{facing}/{name}: head pixel ({x},{y}) not exact at "
                        f"({dx},{dy})",
                    )

    def test_ramp_is_the_frozen_five_color_palette(self) -> None:
        for facing, name in self.HEAD:
            idle, candidate = self.spec_pair(facing, name)
            self.assertEqual(idle.palette, candidate.palette)
            self.assertEqual(idle.used_colors, candidate.used_colors)

    def test_no_jaw_gape_authored(self) -> None:
        # The gape is k0's exclusive marker: a horizontal accent run wider
        # than the feet caps (3px). Neither in-between may author one.
        for facing, name in self.HEAD:
            _, candidate = self.spec_pair(facing, name)
            for y, row in enumerate(candidate.grid):
                longest = max(
                    (len(run) for run in row.split(".") for run in run.split("o")
                     if set(run) == {"k"}),
                    default=0,
                )
                self.assertLessEqual(
                    longest, 3, f"{facing}/{name}: accent run {longest} at row {y}"
                )

    def test_feet_rest_on_the_idle_contact_row(self) -> None:
        for facing, name in self.HEAD:
            idle, candidate = self.spec_pair(facing, name)
            self.assertEqual(idle.bbox[3], candidate.bbox[3])


class RealArtifactsTest(unittest.TestCase):
    """The real banked exports drive the sheet; committed artifacts stay stable."""

    def setUp(self) -> None:
        if not (REPO / "exports" / "calibration-v6"
                / "player_1_lane_b_attack_down_w0.png").is_file():
            self.skipTest("calibration-v6 exports not present")
        self.reference = load_reference()

    def build_sheet(self) -> timeline.TransitionTimelineSheet:
        return timeline.TransitionTimelineSheet(
            REPO / "exports" / "calibration-v6", REPO / "exports" / "calibration-v5",
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            self.reference,
        )

    def test_real_build_passes_the_full_check(self) -> None:
        if not (REPO / "exports" / "calibration-v6" / "release.json").is_file():
            self.skipTest("calibration-v6 release not banked yet")
        report = transition_metrics.build_report(
            REPO / "exports" / "calibration-v6", REPO / "exports" / "calibration-v5",
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            self.reference,
            sheet_path=REPO / "reviews" / "calibration-v6" / "timeline-sheet.png",
        )
        failures = transition_metrics.check_report(report)
        self.assertEqual([], failures)
        self.assertEqual(20, report["export_pins"]["verified"])

    def test_banked_transition_sheet_regenerates_byte_identical(self) -> None:
        sheet_path = REPO / "reviews" / "calibration-v6" / "timeline-sheet.png"
        if not sheet_path.is_file():
            self.skipTest("calibration-v6 sheet not banked yet")
        self.assertEqual(sheet_path.read_bytes(), self.build_sheet().build().encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        apng_dir = REPO / "reviews" / "calibration-v6"
        if not (apng_dir / "timeline-ab-down.apng").is_file():
            self.skipTest("calibration-v6 apng aids not banked yet")
        sheet = self.build_sheet()
        for facing in timeline.FACINGS:
            frames = timeline.build_apng_frames(sheet, facing)
            payload = timeline.encode_apng(frames, timeline.apng_delays(len(frames)))
            self.assertEqual(
                (apng_dir / f"timeline-ab-{facing}.apng").read_bytes(), payload,
                f"apng {facing} drifted",
            )

    def test_sheet_main_writes_sheet_and_apng_aids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "sheet.png"
            status = timeline.main(["--out", str(out), "--apng-dir", temp])
            self.assertEqual(0, status)
            self.assertTrue(out.is_file())
            for facing in timeline.FACINGS:
                self.assertTrue(
                    (Path(temp) / f"timeline-ab-{facing}.apng").is_file()
                )

    def test_metrics_main_checks_the_real_chain_end_to_end(self) -> None:
        if not (REPO / "exports" / "calibration-v6" / "release.json").is_file():
            self.skipTest("calibration-v6 release not banked yet")
        with tempfile.TemporaryDirectory() as temp:
            sheet_path = Path(temp) / "sheet.png"
            status = timeline.main(["--out", str(sheet_path)])
            self.assertEqual(0, status)
            out = Path(temp) / "metrics.json"
            status = transition_metrics.main(
                ["--sheet", str(sheet_path), "--out", str(out), "--check"]
            )
            self.assertEqual(0, status)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(report["sheet"]["committed_matches"])
            # corrupting the committed sheet must fail the determinism bar
            payload = bytearray(sheet_path.read_bytes())
            payload[-20] ^= 0xFF
            sheet_path.write_bytes(bytes(payload))
            status = transition_metrics.main(
                ["--sheet", str(sheet_path), "--out", str(out), "--check"]
            )
            self.assertEqual(1, status)

    def test_metrics_main_reports_missing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            status = transition_metrics.main(
                ["--idle-exports", str(Path(temp) / "missing"),
                 "--out", str(Path(temp) / "r.json")]
            )
            self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
