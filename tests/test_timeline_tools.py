from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_grammar_timeline as timeline
import timeline_metrics
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


class SyntheticTimelineFixture(unittest.TestCase):
    """Distinct rects per pose so every cell is attributable byte-for-byte."""

    POSE_X = {"idle": 10, "f0": 11, "f1": 12, "f2": 13, "f3": 10, "a0": 14, "k0": 16}

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.anticipation = self.root / "anticipation"
        self.attack = self.root / "attack"
        self.walks = self.root / "walks"
        self.idles = self.root / "idles"
        for facing in timeline.FACINGS:
            write_rect(
                self.idles / f"player_1_lane_b_idle_{facing}.png",
                self.POSE_X["idle"], 23,
            )
            for index in range(4):
                write_rect(
                    self.walks / f"player_1_lane_b_walk_{facing}_f{index}.png",
                    self.POSE_X[f"f{index}"], 23,
                )
            write_rect(
                self.anticipation / f"player_1_lane_b_attack_{facing}_a0.png",
                self.POSE_X["a0"], 25, 6, 3,
            )
            write_rect(
                self.attack / f"player_1_lane_b_attack_{facing}_k0.png",
                self.POSE_X["k0"], 21, 8, 6,
            )
        self.reference = load_reference()

    def sheet(self) -> timeline.TimelineSheet:
        return timeline.TimelineSheet(
            self.anticipation, self.attack, self.walks, self.idles, self.reference
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

    def test_offsets_and_positions_are_the_pinned_draw_values(self) -> None:
        for tick in self.plan["ticks"]:
            if tick["phase"] == "windup":
                self.assertEqual(-3, tick["offset_px"])
                self.assertEqual(29, tick["axis_px"])
            elif tick["phase"] == "active":
                self.assertEqual(6, tick["offset_px"])
                self.assertEqual(38, tick["axis_px"])
            elif tick["phase"] in ("recovery", "idle_post"):
                self.assertEqual(0, tick["offset_px"])
                self.assertEqual(32, tick["axis_px"])

    def test_timelines_differ_only_in_windup_pose(self) -> None:
        for tick in self.plan["ticks"]:
            if tick["phase"] == "windup":
                self.assertEqual(("idle", "a0"), (tick["pose_a"], tick["pose_b"]))
            else:
                self.assertEqual(tick["pose_a"], tick["pose_b"])

    def test_walk_positions_follow_smoothstep_monotonically(self) -> None:
        walk = [t for t in self.plan["ticks"] if t["phase"] == "walk"]
        positions = [t["axis_px"] for t in walk]
        self.assertEqual(32, positions[-1])
        self.assertEqual(sorted(positions), positions)
        deltas = [b - a for a, b in zip([0] + positions, positions)]
        self.assertEqual(4, max(deltas))
        self.assertTrue(all(d >= 0 for d in deltas))

    def test_walk_frame_convention_distributes_4_3_3_3(self) -> None:
        walk = [t for t in self.plan["ticks"] if t["phase"] == "walk"]
        poses = [t["pose_a"] for t in walk]
        self.assertEqual(["f0"] * 4 + ["f1"] * 3 + ["f2"] * 3 + ["f3"] * 3, poses)

    def test_attack_ticks_overlap_approach_at_arrival(self) -> None:
        self.assertEqual(14, self.plan["arrival_tick"])
        self.assertEqual(14, self.plan["approach_ticks"][-1]["tick"])
        self.assertEqual(14, self.plan["attack_ticks"][0]["tick"])
        self.assertEqual(20, len(self.plan["attack_ticks"]))

    def test_exp_plan_holds_ten_windup_ticks(self) -> None:
        exp = timeline.build_exp_plan(self.reference)
        windup = [t for t in exp["ticks"] if t["phase"] == "windup"]
        self.assertEqual(10, len(windup))
        self.assertTrue(all(t["pose_b"] == "a0" for t in windup))
        self.assertEqual(26, len(exp["ticks"]))

    def test_round_half_up_is_floor_plus_half(self) -> None:
        self.assertEqual(1, timeline.round_half_up(0.5))
        self.assertEqual(1, timeline.round_half_up(1.49))
        self.assertEqual(0, timeline.round_half_up(-0.5))
        self.assertEqual(32, timeline.round_half_up(32.0))

    def test_flicker_pattern_is_three_on_three_off(self) -> None:
        pattern = [timeline.flicker_on(t, 3) for t in range(12)]
        self.assertEqual(
            [True] * 3 + [False] * 3 + [True] * 3 + [False] * 3, pattern
        )


class SheetTest(SyntheticTimelineFixture):
    def test_sheet_is_deterministic(self) -> None:
        self.assertEqual(
            self.sheet().build().encode(), self.sheet().build().encode()
        )

    def test_sheet_geometry_is_fixed(self) -> None:
        canvas = self.sheet().build()
        self.assertEqual(1460, canvas.width)
        self.assertEqual(1516, canvas.height)

    def test_windup_cells_blit_the_pose_at_minus_three(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        windup_b = [
            c for c in sheet.cells
            if c["section"] == "attack" and c["timeline"] == "B"
            and c["phase"] == "windup" and c["facing"] == "down"
            and c["zone"] == "zone_1"
        ]
        self.assertEqual(5, len(windup_b))
        cell = windup_b[0]
        x0, y0 = cell["rect"][0], cell["rect"][1]
        # synthetic a0 rect at (14, 25), win_px -3 -> body pixel at (14, 22)
        self.assertEqual(BODY, canvas.get(x0 + 14, y0 + 25 - 3))
        # timeline A windup holds the idle rect at (10, 23) -> (10, 20)
        windup_a = [
            c for c in sheet.cells
            if c["section"] == "attack" and c["timeline"] == "A"
            and c["phase"] == "windup" and c["facing"] == "down"
            and c["zone"] == "zone_1"
        ][0]
        ax0, ay0 = windup_a["rect"][0], windup_a["rect"][1]
        self.assertEqual(BODY, canvas.get(ax0 + 10, ay0 + 23 - 3))

    def test_flicker_rows_apply_pinned_treatments_per_tick(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        flash = tuple(self.reference["feedback_states"]["hurt_flash"]["pack_rgb"])
        acc_cells = [
            c for c in sheet.cells
            if c["section"] == "flicker" and c["timeline"] == "ACC"
            and c["facing"] == "down"
        ]
        self.assertEqual(12, len(acc_cells))
        on = [c for c in acc_cells if c["phase"] == "on"]
        off = [c for c in acc_cells if c["phase"] == "off"]
        self.assertEqual(6, len(on))
        self.assertEqual(6, len(off))
        # ON tick: crimson body, accent redrawn on top (11, 24)
        x0, y0 = on[0]["rect"][0], on[0]["rect"][1]
        self.assertEqual((*flash, 255), canvas.get(x0 + 10, y0 + 23))
        self.assertEqual(ACCENT, canvas.get(x0 + 11, y0 + 24))
        # OFF tick: the normal sprite
        x1, y1 = off[0]["rect"][0], off[0]["rect"][1]
        self.assertEqual(BODY, canvas.get(x1 + 10, y1 + 23))

    def test_grammar_row_matches_v3_static_cells(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        grammar = [
            c for c in sheet.cells
            if c["section"] == "grammar" and c["facing"] == "down"
        ]
        self.assertEqual(
            ["idle", "f1", "a0", "wind", "k0", "lunge"],
            [c["phase"] for c in grammar],
        )
        wind = grammar[3]
        x0, y0 = wind["rect"][0], wind["rect"][1]
        # tell_cell: sprite at half (16) + offset (-3); a0 pixel row 25 -> 38
        self.assertEqual(BODY, canvas.get(x0 + 14, y0 + 16 - 3 + 25))


class ValidatorTest(SyntheticTimelineFixture):
    def dirs(self) -> dict[str, Path]:
        return {
            "anticipation_dir": self.anticipation,
            "attack_dir": self.attack,
            "walk_dir": self.walks,
            "idle_dir": self.idles,
        }

    def test_purity_passes_on_a_fresh_build(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        result = timeline_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertEqual([], result["failures"])
        self.assertEqual(len(sheet.cells), result["cells_checked"])

    def test_purity_catches_a_repainted_cell(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        cell = next(c for c in sheet.cells if c["section"] == "attack")
        x0, y0 = cell["rect"][0], cell["rect"][1]
        canvas.put(x0 + 5, y0 + 5, (1, 2, 3, 255))
        result = timeline_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertTrue(
            any("region mismatch" in failure for failure in result["failures"])
        )

    def test_purity_catches_export_byte_drift(self) -> None:
        sheet = self.sheet()
        canvas = sheet.build()
        # the sheet was composed from the old bytes; drift the export afterwards
        write_rect(
            self.anticipation / "player_1_lane_b_attack_down_a0.png", 15, 25, 6, 3
        )
        result = timeline_metrics.check_purity(canvas, sheet, self.dirs())
        self.assertTrue(result["failures"])

    def test_tick_math_passes_and_catches_pin_drift(self) -> None:
        sheet = self.sheet()
        sheet.build()
        self.assertEqual(
            [], timeline_metrics.check_tick_math(sheet, self.reference)
        )
        tampered = json.loads(json.dumps(self.reference))
        tampered["attack_timing"]["values"]["windup_frames"]["value"] = 6
        failures = timeline_metrics.check_tick_math(sheet, tampered)
        self.assertTrue(any("windup cells rendered" in f for f in failures))
        tampered = json.loads(json.dumps(self.reference))
        tampered["feedback_states"]["lunge_offset"]["active_px"] = 7
        failures = timeline_metrics.check_tick_math(sheet, tampered)
        self.assertTrue(any("active offset" in f for f in failures))

    def test_export_pins_verify_and_fail_on_mismatch(self) -> None:
        import hashlib

        pins = {}
        for pose, (dir_key, name) in timeline_metrics.POSE_FILES.items():
            for facing in timeline.FACINGS:
                file = self.dirs()[dir_key] / name.format(facing=facing)
                pins[file.name] = hashlib.sha256(file.read_bytes()).hexdigest()
        result = timeline_metrics.check_export_pins(self.dirs(), pins)
        self.assertEqual([], result["failures"])
        self.assertEqual(14, result["verified"])
        pins["player_1_lane_b_idle_down.png"] = "0" * 64
        result = timeline_metrics.check_export_pins(self.dirs(), pins)
        self.assertTrue(any("sha256" in f for f in result["failures"]))
        del pins["player_1_lane_b_idle_down.png"]
        result = timeline_metrics.check_export_pins(self.dirs(), pins)
        self.assertTrue(any("no banked release pin" in f for f in result["failures"]))

    def test_report_is_deterministic_and_checkable(self) -> None:
        reports = [
            timeline_metrics.build_report(
                self.anticipation, self.attack, self.walks, self.idles,
                self.reference, verify_pins=False,
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
        # pins were skipped, so the full check must flag exactly that
        failures = timeline_metrics.check_report(report)
        self.assertEqual(1, len(failures))
        self.assertIn("skipped", failures[0])

    def test_displacement_profile_reports_the_nine_px_release(self) -> None:
        plan = timeline.build_plan(self.reference)
        profile = timeline_metrics.displacement_profile(plan)
        jumps = timeline_metrics.jump_magnitudes(profile)
        self.assertEqual(-3, jumps["windup_entry_px"])
        self.assertEqual(9, jumps["release_px"])
        self.assertEqual(-6, jumps["recovery_return_px"])
        self.assertEqual(4, jumps["max_walk_delta_px"])
        self.assertEqual(2.25, jumps["release_vs_max_walk_ratio"])

    def test_durations_ms_derive_from_the_default_tick(self) -> None:
        plan = timeline.build_plan(self.reference)
        durations = timeline_metrics.durations_ms(plan["constants"])
        self.assertEqual(83.3, durations["windup_ms"])
        self.assertEqual(66.7, durations["active_ms"])
        self.assertEqual(133.3, durations["recovery_ms"])
        self.assertEqual(166.7, durations["exp_windup_ms"])


class ApngTest(SyntheticTimelineFixture):
    def test_apng_is_deterministic_and_structured(self) -> None:
        sheet = self.sheet()
        frames = timeline.build_apng_frames(sheet, "down")
        delays = timeline.apng_delays(len(frames))
        payload = timeline.encode_apng(frames, delays)
        again = timeline.encode_apng(
            timeline.build_apng_frames(sheet, "down"), delays
        )
        self.assertEqual(payload, again)
        self.assertEqual(34, len(frames))
        self.assertEqual((280, 384), (frames[0].width, frames[0].height))
        self.assertTrue(payload.startswith(b"\x89PNG\r\n\x1a\n"))
        # acTL: 34 frames, infinite loop
        actl_at = payload.index(b"acTL") + 4
        frames_count, plays = struct.unpack(">II", payload[actl_at : actl_at + 8])
        self.assertEqual((34, 0), (frames_count, plays))
        # first fcTL delay = 1/60, last = 30/60
        fctl_positions = []
        offset = 0
        while True:
            index = payload.find(b"fcTL", offset)
            if index < 0:
                break
            fctl_positions.append(index)
            offset = index + 4
        self.assertEqual(34, len(fctl_positions))
        first = struct.unpack(
            ">IIIIIHHBB", payload[fctl_positions[0] + 4 : fctl_positions[0] + 30]
        )
        last = struct.unpack(
            ">IIIIIHHBB", payload[fctl_positions[-1] + 4 : fctl_positions[-1] + 30]
        )
        self.assertEqual((1, 60), (first[5], first[6]))
        self.assertEqual((30, 60), (last[5], last[6]))
        self.assertEqual(33, payload.count(b"fdAT"))

    def test_apng_first_frame_decodes_to_frame_zero(self) -> None:
        sheet = self.sheet()
        frames = timeline.build_apng_frames(sheet, "right")
        payload = timeline.encode_apng(frames, timeline.apng_delays(len(frames)))
        self.assertEqual((384, 280), (frames[0].width, frames[0].height))
        idat_at = payload.index(b"IDAT") + 4
        length = struct.unpack(">I", payload[idat_at - 8 : idat_at - 4])[0]
        raw = zlib.decompress(payload[idat_at : idat_at + length])
        stride = frames[0].width * 4 + 1
        self.assertEqual(stride * frames[0].height, len(raw))
        # spot pixel: row 0 filter byte + first pixel equals the canvas
        self.assertEqual(0, raw[0])
        self.assertEqual(bytes(frames[0].get(0, 0)), bytes(raw[1:5]))

    def test_apng_rejects_mismatched_inputs(self) -> None:
        with self.assertRaises(ValueError):
            timeline.encode_apng([], [])
        frames = [Rgba8Canvas(4, 4), Rgba8Canvas(5, 4)]
        with self.assertRaises(ValueError):
            timeline.encode_apng(frames, [(1, 60), (1, 60)])
        with self.assertRaises(ValueError):
            timeline.encode_apng([Rgba8Canvas(4, 4)], [])


class RealArtifactsTest(unittest.TestCase):
    """The real banked exports drive the sheet; committed artifacts stay stable."""

    def setUp(self) -> None:
        if not (REPO / "exports" / "calibration-v3"
                / "player_1_lane_b_attack_down_a0.png").is_file():
            self.skipTest("banked exports not present")
        self.reference = load_reference()

    def test_real_build_passes_the_full_check(self) -> None:
        report = timeline_metrics.build_report(
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            self.reference,
            sheet_path=REPO / "reviews" / "calibration-v4" / "timeline-sheet.png",
        )
        failures = timeline_metrics.check_report(report)
        self.assertEqual([], failures)
        self.assertEqual(28, report["export_pins"]["verified"] * 2)

    def test_banked_timeline_sheet_regenerates_byte_identical(self) -> None:
        sheet_path = REPO / "reviews" / "calibration-v4" / "timeline-sheet.png"
        if not sheet_path.is_file():
            self.skipTest("calibration-v4 sheet not banked yet")
        built = timeline.TimelineSheet(
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            self.reference,
        ).build()
        self.assertEqual(sheet_path.read_bytes(), built.encode())

    def test_banked_apng_aids_regenerate_byte_identical(self) -> None:
        apng_dir = REPO / "reviews" / "calibration-v4"
        if not (apng_dir / "timeline-ab-down.apng").is_file():
            self.skipTest("calibration-v4 apng aids not banked yet")
        sheet = timeline.TimelineSheet(
            REPO / "exports" / "calibration-v3", REPO / "exports" / "calibration-v2",
            REPO / "exports" / "calibration-v1", REPO / "exports" / "calibration-v0",
            self.reference,
        )
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
            status = timeline.main(
                ["--out", str(out), "--apng-dir", temp]
            )
            self.assertEqual(0, status)
            self.assertTrue(out.is_file())
            for facing in timeline.FACINGS:
                self.assertTrue((Path(temp) / f"timeline-ab-{facing}.apng").is_file())

    def test_metrics_main_checks_the_real_chain_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            sheet_path = Path(temp) / "sheet.png"
            apng_dir = Path(temp) / "aids"
            status = timeline.main(
                ["--out", str(sheet_path), "--apng-dir", str(apng_dir)]
            )
            self.assertEqual(0, status)
            out = Path(temp) / "metrics.json"
            status = timeline_metrics.main(
                ["--sheet", str(sheet_path), "--apng-dir", str(apng_dir),
                 "--out", str(out), "--check"]
            )
            self.assertEqual(0, status)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(report["sheet"]["committed_matches"])
            self.assertTrue(report["apng"]["down"]["committed_matches"])
            # corrupting the committed sheet must fail the determinism bar
            payload = bytearray(sheet_path.read_bytes())
            payload[-20] ^= 0xFF
            sheet_path.write_bytes(bytes(payload))
            status = timeline_metrics.main(
                ["--sheet", str(sheet_path), "--out", str(out), "--check"]
            )
            self.assertEqual(1, status)

    def test_metrics_main_reports_missing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            status = timeline_metrics.main(
                ["--idle-exports", str(Path(temp) / "missing"),
                 "--out", str(Path(temp) / "r.json")]
            )
            self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
