"""Tests for tools/track_recompose.py — the reference consumer for the DRAFT
state-track schema (sprint 13).

Pre-registered bars (reviews/recompose-v13/rationale.md, committed before any
artifact existed):

- schema validation exercised in BOTH directions (a valid synthetic track
  passes; bad type / missing field / unknown facing / out-of-range state all
  refuse loudly with typed messages);
- THE EQUIVALENCE BAR — byte half: tracks derived mechanically from the
  banked Model-A lane plans recompose byte-identically to the committed
  v10/v11 sheet lane cells (420 + 252 = 672 cells, zero tolerance); plan
  half: the mapping's decision stream equals the banked v9 lane_tick outputs
  (340 records, f3/idle compared at byte-class per the banked byte-copy law);
- determinism: in-process double builds byte-identical; committed demo
  artifacts equal fresh recompositions (pre-bank guard: skips until the demo
  is banked);
- banked-modules-unmodified: the committed manifest pins every
  mapping-source module by SHA-256 and the live files must match (pre-bank
  guard: skips until the manifest is banked);
- SYNTHETIC labeling: the demo track, manifest, and artifacts carry the
  SYNTHETIC class and the zero-adjudication statement.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import make_corner_timeline as v11
import make_cross_seam_timeline as v9
import make_turn_timeline as v10
import track_recompose as tr
from make_contact_sheet import load_reference

REPO = Path(__file__).resolve().parents[1]


def reference() -> dict:
    return load_reference(REPO / "manifests" / "render-reference.json")


def valid_track() -> dict:
    return tr.build_demo_track(reference())


class ValidateTrackPassDirection(unittest.TestCase):
    def test_demo_track_is_valid(self) -> None:
        self.assertEqual([], tr.validate_track(valid_track()))

    def test_demo_track_is_synthetic_with_provenance(self) -> None:
        track = valid_track()
        self.assertEqual("SYNTHETIC", track["class"])
        self.assertEqual("SYNTHETIC", track["provenance"]["class"])
        self.assertIn("ZERO register items", track["provenance"]["statement"])

    def test_demo_covers_all_banked_pose_classes(self) -> None:
        track = valid_track()
        poses = set()
        constants = track["constants"]
        for tick in track["ticks"]:
            pose, _, _ = tr.select_pose(
                tick["creatures"]["player_1"], constants
            )
            poses.add(pose)
        self.assertEqual(
            {"idle", "f0", "f1", "f2", "f3", "a0", "k0", "r0", "w0", "s0", "x0"},
            poses,
        )


class ValidateTrackFailDirections(unittest.TestCase):
    def check(self, mutate, needle: str) -> None:
        track = copy.deepcopy(valid_track())
        mutate(track)
        errors = tr.validate_track(track)
        self.assertTrue(
            any(needle in e for e in errors),
            f"expected a {needle!r} refusal, got: {errors[:4]}",
        )

    def test_missing_top_level_field(self) -> None:
        self.check(lambda t: t.pop("view"), "missing-field: track.view")

    def test_bad_class_enum(self) -> None:
        self.check(lambda t: t.update(clas_=None, **{"class": "REAL"}), "bad-enum")

    def test_provenance_class_mismatch(self) -> None:
        def mutate(t):
            t["provenance"]["class"] = "RUNTIME"
        self.check(mutate, "provenance-mismatch")

    def test_missing_record_field(self) -> None:
        def mutate(t):
            del t["ticks"][5]["creatures"]["player_1"]["tween_left"]
        self.check(mutate, "missing-field")

    def test_bad_record_type(self) -> None:
        def mutate(t):
            t["ticks"][5]["creatures"]["player_1"]["tween_left"] = "three"
        self.check(mutate, "bad-type")

    def test_bad_attack_state_enum(self) -> None:
        def mutate(t):
            t["ticks"][5]["creatures"]["player_1"]["attack_state"] = "swinging"
        self.check(mutate, "bad-enum")

    def test_tween_left_over_total(self) -> None:
        def mutate(t):
            record = t["ticks"][5]["creatures"]["player_1"]
            record["tween_left"] = record["tween_total"] + 1
        self.check(mutate, "out-of-range")

    def test_state_frames_out_of_phase_range(self) -> None:
        def mutate(t):
            record = t["ticks"][31]["creatures"]["player_1"]
            self.assertNotEqual("idle", record["attack_state"])
            record["state_frames"] = 99
        self.check(mutate, "out-of-range")

    def test_idle_with_action_rejected(self) -> None:
        def mutate(t):
            record = t["ticks"][5]["creatures"]["player_1"]
            record["attack_state"] = "idle"
            record["state_frames"] = 0
            record["current_action"] = "attack"
        self.check(mutate, "state-mismatch")

    def test_non_consecutive_frames(self) -> None:
        def mutate(t):
            t["ticks"][7]["frame"] = 99
        self.check(mutate, "non-consecutive")

    def test_roster_mismatch(self) -> None:
        def mutate(t):
            tick = t["ticks"][3]
            tick["creatures"]["player_2"] = tick["creatures"]["player_1"]
        self.check(mutate, "roster-mismatch")

    def test_unknown_facing_refused_at_mapping_time(self) -> None:
        record = valid_track()["ticks"][5]["creatures"]["player_1"]
        record["facing"] = [0, -1]
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.select_pose(record, valid_track()["constants"])
        self.assertIn("unrenderable-facing", str(ctx.exception))

    def test_unmapped_tween_class_refused(self) -> None:
        track = valid_track()
        record = track["ticks"][5]["creatures"]["player_1"]
        record["tween_total"] = 18   # a diagonal/dash-class duration
        record["tween_left"] = 9
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.select_pose(record, track["constants"])
        self.assertIn("unmapped-tween-class", str(ctx.exception))


class MappingUnitTests(unittest.TestCase):
    """The declared mapping clause by clause, on hand-built records."""

    def setUp(self) -> None:
        self.constants = tr.walk_constants(reference())

    def record(self, **overrides) -> dict:
        base = {
            "tile_x": 0, "tile_y": 0, "px": 0.0, "py": 0.0,
            "facing": [0, 1], "tween_left": 0, "tween_total": 0,
            "attack_state": "idle", "current_action": None,
            "state_frames": 0, "hp": 80, "iframes": 0,
        }
        base.update(overrides)
        return base

    def test_walk_mapping_is_the_banked_distribution(self) -> None:
        seen = []
        for k in range(1, 13):
            record = self.record(tween_left=13 - k, tween_total=13)
            pose, facing, offset = tr.select_pose(record, self.constants)
            seen.append(pose)
            self.assertEqual(("down", 0), (facing, offset))
        self.assertEqual(
            ["f0"] * 4 + ["f1"] * 3 + ["f2"] * 3 + ["f3"] * 2, seen
        )

    def test_commit_and_settle_ticks_draw_standing(self) -> None:
        for tween in ((13, 13), (0, 13), (0, 0)):
            record = self.record(tween_left=tween[0], tween_total=tween[1])
            self.assertEqual(
                "idle", tr.select_pose(record, self.constants)[0]
            )

    def test_attack_timeline_is_the_banked_lane_b_grammar(self) -> None:
        poses = []
        offsets = []
        for state, pinned in (("windup", 5), ("active", 4), ("recovery", 8)):
            for left in range(pinned, 0, -1):
                record = self.record(
                    attack_state=state, state_frames=left,
                    current_action="attack", facing=[1, 0],
                )
                pose, _, offset = tr.select_pose(record, self.constants)
                poses.append(pose)
                offsets.append(offset)
        self.assertEqual(
            ["w0", "a0", "a0", "a0", "a0"]
            + ["k0"] * 4
            + ["s0", "r0", "r0", "r0", "r0", "r0", "r0", "x0"],
            poses,
        )
        self.assertEqual([-3] * 5 + [6] * 4 + [0] * 8, offsets)

    def test_attack_pose_priority_over_walk(self) -> None:
        record = self.record(
            attack_state="windup", state_frames=5, current_action="attack",
            tween_left=7, tween_total=13, facing=[1, 0],
        )
        self.assertEqual("w0", tr.select_pose(record, self.constants)[0])

    def test_draw_vector_rounds_and_offsets_along_facing(self) -> None:
        record = self.record(px=18.499, py=32.5, facing=[1, 0])
        view = {"origin_px": [0, 0], "width": 96, "height": 64}
        self.assertEqual((18 + 6, 33), tr.draw_vector(record, view, 6))


class EquivalenceByteBar(unittest.TestCase):
    """THE hard bar: mechanically derived tracks recompose the committed
    banked lane cells byte-for-byte (all covered cells, zero tolerance)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = reference()
        cls.dirs = tr.default_dirs()

    def test_v10_lane_cells_byte_identical(self) -> None:
        sheet = v10.TurnTimelineSheet(self.dirs, self.reference)
        sheet.build()
        result = tr.check_sheet_equivalence(
            sheet, REPO / "reviews" / "calibration-v10" / "turn-sheet.png",
            v10.SECTION_LANES, self.reference, expected_cells=420,
        )
        self.assertEqual(420, result["cells_checked"])
        self.assertEqual([], result["failures"])

    def test_v11_model_a_lane_cells_byte_identical(self) -> None:
        sheet = v11.CornerTimelineSheet(self.dirs, self.reference)
        sheet.build()
        result = tr.check_sheet_equivalence(
            sheet, REPO / "reviews" / "calibration-v11" / "corner-sheet.png",
            tr.V11_MODEL_A_LANES, self.reference, expected_cells=252,
        )
        self.assertEqual(252, result["cells_checked"])
        self.assertEqual([], result["failures"])

    def test_equivalence_detects_a_broken_mapping(self) -> None:
        """FAIL direction: corrupting one derived record breaks byte
        equality (the bar is live, not vacuously green)."""
        sheet = v10.TurnTimelineSheet(self.dirs, self.reference)
        sheet.build()
        constants = tr.walk_constants(self.reference)
        cell = next(
            c for c in sheet.cells
            if c["section"] == "lane" and c["lane"] == "EARLY"
            and c["tick"] == 7 and c["zone"] == "zone_1"
        )
        data = sheet.plan["pairs"][cell["pair"]]["lanes"]["EARLY"]
        record = tr.track_record_from_walk_lane(
            data["ticks"][7], data["b_commit_tick"], constants["step_frames"]
        )
        record["tween_left"] += 2  # wrong state -> wrong frame -> wrong bytes
        pose, facing, offset = tr.select_pose(record, constants)
        view = {"origin_px": [0, 0], "width": cell["window_w"],
                "height": cell["window_h"]}
        dx, dy = tr.draw_vector(record, view, offset)
        mine = tr.compose_cell(
            self.reference["zones"]["zone_1"],
            cell["window_w"], cell["window_h"],
            sheet.poses[facing][pose], dx, dy,
        )
        from png_reader import read_rgba

        width, _, raw = read_rgba(
            REPO / "reviews" / "calibration-v10" / "turn-sheet.png"
        )
        x0, y0 = cell["rect"][0], cell["rect"][1]
        same = all(
            raw[((y0 + py) * width + x0) * 4:
                ((y0 + py) * width + x0 + cell["window_w"]) * 4]
            == bytes(
                mine._pixels[py * cell["window_w"] * 4:
                             (py + 1) * cell["window_w"] * 4]
            )
            for py in range(cell["window_h"])
        )
        self.assertFalse(same)


class EquivalencePlanBar(unittest.TestCase):
    def test_attack_decision_stream_equals_banked_v9(self) -> None:
        result = tr.check_attack_plan_equivalence(reference())
        self.assertEqual(340, result["records_checked"])
        self.assertEqual([], result["failures"])

    def test_plan_bar_detects_a_shifted_timeline(self) -> None:
        """FAIL direction: an off-by-one state_frames derivation is caught."""
        ref = reference()
        plan = v9.build_plan(ref)
        lane = plan["pairs"]["DR"]["lanes"]["MID"]
        constants = tr.walk_constants(ref)
        tick = lane["ticks"][lane["onset_tick"]]
        record = tr.track_record_from_attack_lane(tick, lane, ref)
        record["state_frames"] -= 1  # off by one inside the windup
        pose, _, _ = tr.select_pose(record, constants)
        self.assertNotEqual(tick["pose"], pose)


class DemoBundleGuards(unittest.TestCase):
    """Committed-demo guards; each skips until the demo is banked
    (the v10/v11 pre-bank artifact-guard pattern)."""

    def setUp(self) -> None:
        if not tr.DEMO_MANIFEST.is_file():
            self.skipTest("demo bundle not banked yet")
        self.manifest = json.loads(tr.DEMO_MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_completeness(self) -> None:
        self.assertEqual(tr.MAPPING_ID, self.manifest["mapping_id"])
        self.assertEqual(tr.SCHEMA_VERSION, self.manifest["schema_version"])
        self.assertEqual("SYNTHETIC", self.manifest["provenance"]["class"])
        self.assertTrue(self.manifest["repo_commit_at_generation"])
        self.assertTrue(self.manifest["determinism"]["double_build_identical"])
        self.assertEqual(
            sorted(
                ["synthetic-demo-track.json", "synthetic-demo-sheet.png",
                 "synthetic-demo.apng"]
            ),
            sorted(self.manifest["artifacts"]),
        )

    def test_banked_mapping_source_modules_unmodified(self) -> None:
        live = tr.mapping_source_hashes()
        pinned = self.manifest["mapping_source_sha256"]
        self.assertEqual(sorted(tr.MAPPING_SOURCE_FILES), sorted(pinned))
        for rel, digest in pinned.items():
            self.assertEqual(
                digest, live[rel],
                f"{rel} differs from the banked manifest pin",
            )

    def test_committed_demo_regenerates_byte_identically(self) -> None:
        failures = tr.check_demo(reference(), tr.default_dirs())
        self.assertEqual([], failures)

    def test_synthetic_labels_everywhere(self) -> None:
        track = json.loads(tr.DEMO_TRACK.read_text(encoding="utf-8"))
        self.assertEqual("SYNTHETIC", track["class"])
        for name in self.manifest["artifacts"]:
            self.assertIn("synthetic-demo", name)
        statement = self.manifest["provenance"]["statement"]
        self.assertIn("NOT runtime evidence", statement)
        self.assertIn("ZERO register items", statement)


class ExportGuard(unittest.TestCase):
    def test_no_new_export_dirs_and_pins_hold(self) -> None:
        exports = tr.check_export_pins(REPO / "exports")
        self.assertEqual([], exports["failures"])
        for stale in tr.STALE_EXPORT_DIRS:
            self.assertFalse((REPO / "exports" / stale).exists())


if __name__ == "__main__":
    unittest.main()
