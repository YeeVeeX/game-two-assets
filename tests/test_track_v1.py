"""Tests for the schema-v1 adaptation of tools/track_recompose.py (v30).

The s84 T2 delivery pinned schema v1 (spec section 5 at game-two 2627ed0);
draft-1's own resolution rule orders the consumer to adapt. Covered here,
branch by branch:

- v1 validation law: per-kit constants map + exact roster-kit coverage,
  ``possessed`` boolean, per-tick ``masks``, UNION roster semantics (both
  gap directions legal; undeclared or never-observed names refuse),
  1-based frame domain, ``provenance.bundle_id``;
- schema dispatch: draft-1 law untouched (the banked draft-1 test file is
  the other half of that proof and is unedited); unknown versions refuse;
- per-creature mapping-constants resolution (kit selection rule; the lunge
  px pair rides the mapping side in v1 — dropped from track constants);
- the design-section-5 intake gate (``verify_runtime_intake``) FAIL
  directions on tmpdir fixtures and PASS direction on the committed
  evidence bundle;
- RUNTIME admission: lifted ONLY through the verified intake context;
  synthetic/fixture tracks never pass as evidence (v13 law carried);
- the TEXT decision stream over both committed reference tracks — the
  machine half of the v30 parser verdict (mail-claimed presence gaps
  reproduced from bytes).
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import track_recompose as tr
from make_contact_sheet import load_reference

REPO = Path(__file__).resolve().parents[1]
BUNDLE = REPO / "evidence" / "replay" / "20260826T175326Z_p1_42"


def reference() -> dict:
    return load_reference(REPO / "manifests" / "render-reference.json")


def kit_constants() -> dict:
    return {
        "striker": {"step_frames": 13, "windup_frames": 5,
                    "active_frames": 4, "recovery_frames": 8},
        "rusher": {"step_frames": 16, "windup_frames": 20,
                   "active_frames": 6, "recovery_frames": 0},
    }


def v1_record(**overrides) -> dict:
    base = {
        "tile_x": 0, "tile_y": 0, "px": 4.0, "py": 32.0,
        "facing": [0, 1], "tween_left": 0, "tween_total": 0,
        "attack_state": "idle", "current_action": None, "state_frames": 0,
        "hp": 80, "iframes": 0, "possessed": False,
    }
    base.update(overrides)
    return base


def v1_track() -> dict:
    """Union-roster fixture with BOTH gap directions: rusher_1 dies after
    frame 11 (death), rusher_2 first appears at frame 13 (join)."""
    rosters = {
        10: ("striker_1", "rusher_1"),
        11: ("striker_1", "rusher_1"),
        12: ("striker_1",),
        13: ("striker_1", "rusher_2"),
    }
    ticks = []
    for frame, names in rosters.items():
        ticks.append({
            "frame": frame,
            "creatures": {
                name: v1_record(possessed=(name == "striker_1"))
                for name in names
            },
            "masks": {"1": 0},
        })
    return {
        "schema_version": "1",
        "class": "SYNTHETIC",
        "tick_ms": 16.67,
        "zone": "zone_1",
        "view": {"origin_px": [0, 0], "width": 96, "height": 64},
        "constants": kit_constants(),
        "creatures": [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
            {"name": "rusher_1", "faction": "human", "kit": "rusher"},
            {"name": "rusher_2", "faction": "human", "kit": "rusher"},
        ],
        "ticks": ticks,
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tests/test_track_v1.py fixture",
            "bundle_id": "fixture-not-a-bundle",
            "statement": "hand-built v1 fixture; never evidence",
        },
    }


class V1ValidationPassDirection(unittest.TestCase):
    def test_union_fixture_with_both_gap_directions_is_valid(self) -> None:
        self.assertEqual([], tr.validate_track(v1_track()))

    def test_per_kit_state_frames_range_uses_the_creatures_kit(self) -> None:
        """A rusher windup at state_frames 15 is legal under its OWN kit
        (windup_frames 20) — the striker law (5) would have refused it."""
        track = v1_track()
        track["ticks"][0]["creatures"]["rusher_1"].update(
            attack_state="windup", state_frames=15, current_action="attack",
        )
        self.assertEqual([], tr.validate_track(track))


class V1ValidationFailDirections(unittest.TestCase):
    def check(self, mutate, needle: str) -> None:
        track = v1_track()
        mutate(track)
        errors = tr.validate_track(track)
        self.assertTrue(
            any(needle in e for e in errors),
            f"expected a {needle!r} refusal, got: {errors[:4]}",
        )

    def test_unknown_schema_version_refused(self) -> None:
        self.check(
            lambda t: t.update(schema_version="2"),
            "bad-enum: track.schema_version",
        )

    def test_non_string_schema_version_refused(self) -> None:
        track = v1_track()
        track["schema_version"] = 1
        self.assertEqual(
            ["bad-type: track.schema_version must be a non-empty string"],
            tr.validate_track(track),
        )

    def test_kit_constants_missing_field(self) -> None:
        self.check(
            lambda t: t["constants"]["striker"].pop("windup_frames"),
            "missing-field: track.constants.striker.windup_frames",
        )

    def test_kit_constants_bad_type(self) -> None:
        self.check(
            lambda t: t["constants"]["rusher"].update(step_frames="16"),
            "bad-type: track.constants.rusher.step_frames",
        )

    def test_kit_constants_not_an_object(self) -> None:
        self.check(
            lambda t: t["constants"].update(striker=13),
            "bad-type: track.constants.striker must be an object",
        )

    def test_roster_kit_without_constants_entry(self) -> None:
        self.check(
            lambda t: t["constants"].pop("rusher"),
            "missing-field: track.constants.rusher",
        )

    def test_constants_kit_absent_from_roster(self) -> None:
        self.check(
            lambda t: t["constants"].update(lobber=kit_constants()["striker"]),
            "roster-mismatch: track.constants covers kit 'lobber'",
        )

    def test_missing_possessed(self) -> None:
        self.check(
            lambda t: t["ticks"][0]["creatures"]["striker_1"].pop("possessed"),
            "missing-field: ticks[0].creatures[striker_1].possessed",
        )

    def test_non_bool_possessed(self) -> None:
        self.check(
            lambda t: t["ticks"][0]["creatures"]["striker_1"].update(possessed=1),
            "bad-type: ticks[0].creatures[striker_1].possessed",
        )

    def test_missing_masks(self) -> None:
        self.check(lambda t: t["ticks"][1].pop("masks"), "missing-field: ticks[1].masks")

    def test_non_object_masks(self) -> None:
        self.check(
            lambda t: t["ticks"][1].update(masks=[0]),
            "bad-type: ticks[1].masks must be an object",
        )

    def test_non_int_mask_value(self) -> None:
        self.check(
            lambda t: t["ticks"][1]["masks"].update({"1": "0"}),
            "bad-type: ticks[1].masks[1]",
        )

    def test_frame_zero_refused(self) -> None:
        def mutate(t):
            for offset, tick in enumerate(t["ticks"]):
                tick["frame"] = offset  # window now starts at frame 0
        self.check(mutate, "out-of-range: ticks[0].frame 0 < 1")

    def test_non_consecutive_frames_still_refused_in_v1(self) -> None:
        self.check(
            lambda t: t["ticks"][2].update(frame=99),
            "non-consecutive",
        )

    def test_undeclared_creature_refused(self) -> None:
        def mutate(t):
            tick = t["ticks"][0]
            tick["creatures"]["ghost_1"] = v1_record()
        self.check(mutate, "roster-mismatch: ticks[0].creatures names ['ghost_1']")

    def test_declared_but_never_observed_refused(self) -> None:
        def mutate(t):
            t["creatures"].append(
                {"name": "rusher_3", "faction": "human", "kit": "rusher"}
            )
        self.check(mutate, "roster-mismatch: creature 'rusher_3' declared")

    def test_missing_bundle_id_refused(self) -> None:
        self.check(
            lambda t: t["provenance"].pop("bundle_id"),
            "missing-field: track.provenance.bundle_id",
        )

    def test_draft1_flat_constants_law_unchanged(self) -> None:
        """Dispatch proof: a draft-1 track still validates under the flat
        constants law (missing flat field refuses; per-kit map refuses)."""
        track = tr.build_demo_track(reference())
        flat = dict(track["constants"])
        del track["constants"]["step_frames"]
        errors = tr.validate_track(track)
        self.assertTrue(
            any("missing-field: track.constants.step_frames" in e for e in errors)
        )
        track["constants"] = {"striker": flat}
        errors = tr.validate_track(track)
        self.assertTrue(errors, "per-kit map must not validate as draft-1")


class MappingConstantsResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = reference()

    def test_draft1_passthrough(self) -> None:
        track = tr.build_demo_track(self.reference)
        self.assertIs(track["constants"], tr.mapping_constants(track, "striker"))

    def test_v1_merges_kit_frames_with_mapping_side_lunge(self) -> None:
        track = v1_track()
        resolved = tr.mapping_constants(track, "rusher", self.reference)
        self.assertEqual(16, resolved["step_frames"])
        self.assertEqual(20, resolved["windup_frames"])
        lunge = self.reference["feedback_states"]["lunge_offset"]
        self.assertEqual(lunge["windup_px"], resolved["windup_px"])
        self.assertEqual(lunge["active_px"], resolved["active_px"])

    def test_v1_without_reference_refuses(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.mapping_constants(v1_track(), "striker")
        self.assertIn("missing-reference", str(ctx.exception))

    def test_select_pose_walks_a_16_tick_rusher_step(self) -> None:
        """The banked declared convention (walk_frame_index) distributes the
        four walk frames across the creature's OWN step duration."""
        from make_grammar_timeline import walk_frame_index

        track = v1_track()
        constants = tr.mapping_constants(track, "rusher", self.reference)
        record = v1_record(tween_left=8, tween_total=16)
        pose, facing, offset = tr.select_pose(record, constants)
        self.assertEqual(f"f{walk_frame_index(8, 16)}", pose)
        self.assertEqual(("down", 0), (facing, offset))

    def test_select_pose_striker_timeline_unchanged_under_v1(self) -> None:
        track = v1_track()
        constants = tr.mapping_constants(track, "striker", self.reference)
        record = v1_record(
            attack_state="active", state_frames=4,
            current_action="attack", facing=[1, 0],
        )
        pose, facing, offset = tr.select_pose(record, constants)
        self.assertEqual(("k0", "right"), (pose, facing))
        self.assertEqual(
            self.reference["feedback_states"]["lunge_offset"]["active_px"],
            offset,
        )


class IntakeGateFailDirections(unittest.TestCase):
    """verify_runtime_intake on tmpdir fixtures — every refusal is the
    runtime-intake-not-established class with the reason named."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.bundle = self.root / "fixture-bundle"
        (self.bundle / "tracks").mkdir(parents=True)
        self.track_path = self.bundle / "tracks" / "t.json"
        self.track_path.write_text('{"fixture": true}\n', encoding="utf-8")
        digest = tr.file_sha256(self.track_path)
        (self.bundle / "tracks" / "t.json.sha256").write_text(
            f"{digest}  t.json\n", encoding="utf-8"
        )
        self.manifest = {
            "bundle_id": "fixture-bundle", "fingerprint_md5": "f" * 32,
            "ticks_executed": 100, "members": {},
        }
        self.verification = {
            "bundle_id": "fixture-bundle", "verdict": "PASS", "runs": 2,
            "fingerprint_at_verification": "f" * 32,
        }

    def write_bundle(self) -> None:
        (self.bundle / "manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )
        (self.bundle / "verification.json").write_text(
            json.dumps(self.verification), encoding="utf-8"
        )

    def expect_refusal(self, needle: str) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.verify_runtime_intake(self.track_path, evidence_root=self.root)
        message = str(ctx.exception)
        self.assertIn("runtime-intake-not-established", message)
        self.assertIn(needle, message)

    def test_outside_evidence_root_refused(self) -> None:
        self.write_bundle()
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.verify_runtime_intake(
                self.track_path, evidence_root=self.root / "elsewhere"
            )
        self.assertIn("outside the evidence intake root", str(ctx.exception))

    def test_missing_manifest_refused(self) -> None:
        (self.bundle / "verification.json").write_text(
            json.dumps(self.verification), encoding="utf-8"
        )
        self.expect_refusal("manifest.json missing")

    def test_failed_verdict_refused(self) -> None:
        self.verification["verdict"] = "RED"
        self.write_bundle()
        self.expect_refusal("verdict 'RED'")

    def test_single_run_refused(self) -> None:
        self.verification["runs"] = 1
        self.write_bundle()
        self.expect_refusal("runs 1 < 2")

    def test_non_int_runs_refused(self) -> None:
        self.verification["runs"] = "2"
        self.write_bundle()
        self.expect_refusal("runs '2' < 2")

    def test_bundle_id_mismatch_refused(self) -> None:
        self.verification["bundle_id"] = "other-bundle"
        self.write_bundle()
        self.expect_refusal("verification bundle_id")

    def test_fingerprint_mismatch_refused(self) -> None:
        self.verification["fingerprint_at_verification"] = "0" * 32
        self.write_bundle()
        self.expect_refusal("fingerprint mismatch")

    def test_missing_sidecar_refused(self) -> None:
        self.write_bundle()
        (self.bundle / "tracks" / "t.json.sha256").unlink()
        self.expect_refusal("sidecar t.json.sha256 missing")

    def test_sidecar_hash_mismatch_refused(self) -> None:
        self.write_bundle()
        (self.bundle / "tracks" / "t.json.sha256").write_text(
            ("0" * 64) + "  t.json\n", encoding="utf-8"
        )
        self.expect_refusal("!= sidecar")

    def test_unusable_ticks_executed_refused(self) -> None:
        self.manifest["ticks_executed"] = 0
        self.write_bundle()
        self.expect_refusal("ticks_executed 0")

    def test_happy_path_returns_context(self) -> None:
        self.write_bundle()
        context = tr.verify_runtime_intake(
            self.track_path, evidence_root=self.root
        )
        self.assertEqual("fixture-bundle", context["bundle_id"])
        self.assertEqual(100, context["ticks_executed"])
        self.assertEqual(
            tr.file_sha256(self.track_path), context["track_sha256"]
        )


class RuntimeAdmission(unittest.TestCase):
    def intake(self, **overrides) -> dict:
        base = {
            "bundle_id": "fixture-not-a-bundle", "ticks_executed": 100,
            "manifest": {}, "verification": {"verdict": "PASS", "runs": 2},
            "track_sha256": "0" * 64, "bundle_dir": "x",
        }
        base.update(overrides)
        return base

    def runtime_track(self) -> dict:
        track = v1_track()
        track["class"] = "RUNTIME"
        track["provenance"]["class"] = "RUNTIME"
        return track

    def test_synthetic_needs_no_intake(self) -> None:
        self.assertIsNone(tr.require_runtime_admission(v1_track(), None))

    def test_runtime_without_intake_refused(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.require_runtime_admission(self.runtime_track(), None)
        self.assertIn("runtime-intake-not-established", str(ctx.exception))

    def test_draft1_runtime_refused_even_with_intake(self) -> None:
        track = tr.build_demo_track(reference())
        track["class"] = "RUNTIME"
        track["provenance"]["class"] = "RUNTIME"
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.require_runtime_admission(track, self.intake())
        self.assertIn("runtime-intake-not-established", str(ctx.exception))

    def test_bundle_id_mismatch_refused(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.require_runtime_admission(
                self.runtime_track(), self.intake(bundle_id="other")
            )
        self.assertIn("provenance-mismatch", str(ctx.exception))

    def test_window_outside_domain_refused(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.require_runtime_admission(
                self.runtime_track(), self.intake(ticks_executed=12)
            )
        self.assertIn("out-of-range: window 10..13 outside 1..12",
                      str(ctx.exception))

    def test_admitted_with_matching_context(self) -> None:
        self.assertIsNone(
            tr.require_runtime_admission(self.runtime_track(), self.intake())
        )


class DecisionStreamFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = reference()

    def test_union_gaps_reported_as_information(self) -> None:
        stats = tr.decision_stream(v1_track(), self.reference)
        self.assertEqual(["rusher_1", "rusher_2"], stats["presence_gaps"])
        self.assertEqual(
            {"first_frame": 10, "last_frame": 11, "ticks_present": 2,
             "possessed_ticks": 0, "kit": "rusher"},
            stats["presence"]["rusher_1"],
        )
        self.assertEqual(
            {"first_frame": 13, "last_frame": 13, "ticks_present": 1,
             "possessed_ticks": 0, "kit": "rusher"},
            stats["presence"]["rusher_2"],
        )
        self.assertEqual(7, stats["decisions"])
        self.assertEqual(7, stats["mapped"])
        self.assertEqual({"idle/down": 7}, stats["pose_counts"])
        self.assertEqual({"1": 4}, stats["possessed_ticks_histogram"])

    def test_typed_refusals_are_counted_not_raised(self) -> None:
        track = v1_track()
        track["ticks"][0]["creatures"]["striker_1"]["facing"] = [0, -1]
        stats = tr.decision_stream(track, self.reference)
        self.assertEqual(1, stats["refused"])
        self.assertEqual(
            1, stats["refusal_counts"]["unrenderable-facing"]["count"]
        )
        self.assertIn(
            "frame 10 striker_1",
            stats["refusal_counts"]["unrenderable-facing"]["first_example"],
        )

    def test_invalid_track_raises(self) -> None:
        track = v1_track()
        del track["ticks"][0]["creatures"]["striker_1"]["possessed"]
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.decision_stream(track, self.reference)
        self.assertIn("invalid track", str(ctx.exception))

    def test_runtime_fixture_without_intake_refused(self) -> None:
        track = v1_track()
        track["class"] = "RUNTIME"
        track["provenance"]["class"] = "RUNTIME"
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.decision_stream(track, self.reference)
        self.assertIn("runtime-intake-not-established", str(ctx.exception))


class RecomposeTrackV1(unittest.TestCase):
    def test_unbanked_zone_refuses_typed(self) -> None:
        track = v1_track()
        track["zone"] = "district"
        track["creatures"] = [track["creatures"][0]]
        track["constants"] = {"striker": track["constants"]["striker"]}
        for tick in track["ticks"]:
            tick["creatures"] = {"striker_1": tick["creatures"]["striker_1"]}
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.recompose_track(
                track, tr.load_poses(tr.default_dirs()), reference()
            )
        self.assertIn("unmapped-zone", str(ctx.exception))

    def test_v1_single_creature_synthetic_composes_on_banked_zone(self) -> None:
        """The v1 path drives the banked composition end-to-end on a banked
        palette — per-kit constants resolved, mapping semantics unchanged."""
        track = v1_track()
        track["creatures"] = [track["creatures"][0]]
        track["constants"] = {"striker": track["constants"]["striker"]}
        for tick in track["ticks"]:
            tick["creatures"] = {"striker_1": tick["creatures"]["striker_1"]}
        frames, decisions = tr.recompose_track(
            track, tr.load_poses(tr.default_dirs()), reference()
        )
        self.assertEqual(4, len(frames))
        self.assertEqual(
            ["idle"] * 4, [d["pose"] for d in decisions]
        )


class CommittedEvidenceIntegration(unittest.TestCase):
    """The committed bundle is real intaken evidence — the gate and the
    stream must hold against its bytes (mail claims reproduced, not trusted)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = reference()
        cls.stats = {}
        for name in ("reference-attack-window", "reference-roster-gaps-window"):
            path = BUNDLE / "tracks" / f"{name}.json"
            track = json.loads(path.read_text(encoding="utf-8"))
            intake = tr.verify_runtime_intake(path)
            cls.stats[name] = tr.decision_stream(track, cls.reference, intake)

    def test_attack_window_accepted_roster_stable(self) -> None:
        stats = self.stats["reference-attack-window"]
        self.assertEqual([420, 560], stats["window_frames"])
        self.assertEqual(141, stats["ticks"])
        self.assertEqual(18, stats["declared_creatures"])
        self.assertEqual([], stats["presence_gaps"])
        self.assertEqual({"1": 141}, stats["possessed_ticks_histogram"])
        self.assertEqual(
            "20260826T175326Z_p1_42", stats["intake"]["bundle_id"]
        )

    def test_attack_window_covers_all_four_attack_states(self) -> None:
        """All four attack_states appear (mail claim) and the attack poses
        of the banked timeline show up in the mapped stream."""
        poses = set()
        for key in self.stats["reference-attack-window"]["pose_counts"]:
            poses.add(key.split("/")[0])
        self.assertLessEqual({"w0", "a0", "k0", "s0", "r0", "x0"}, poses)

    def test_gaps_window_union_gaps_match_the_mailed_claims(self) -> None:
        """The four machine-verified gap claims in the s84 mail, reproduced
        from the intaken bytes: deaths (rusher1 last 615, rusher0 last 688)
        and joins (rusher15 first 916, rusher16 first 989)."""
        stats = self.stats["reference-roster-gaps-window"]
        self.assertEqual([561, 1100], stats["window_frames"])
        self.assertEqual(540, stats["ticks"])
        self.assertEqual(20, stats["declared_creatures"])
        self.assertEqual(
            ["rusher0", "rusher1", "rusher15", "rusher16"],
            stats["presence_gaps"],
        )
        presence = stats["presence"]
        self.assertEqual(615, presence["rusher1"]["last_frame"])
        self.assertEqual(688, presence["rusher0"]["last_frame"])
        self.assertEqual(916, presence["rusher15"]["first_frame"])
        self.assertEqual(989, presence["rusher16"]["first_frame"])
        self.assertEqual(561, presence["rusher1"]["first_frame"])
        self.assertEqual({"1": 540}, stats["possessed_ticks_histogram"])

    def test_every_refusal_is_a_banked_lawful_class(self) -> None:
        lawful = {
            "unrenderable-facing", "unmapped-tween-class",
            "unmapped-action-class",
        }
        for name, stats in self.stats.items():
            self.assertLessEqual(
                set(stats["refusal_counts"]), lawful,
                f"{name} produced a refusal outside the banked classes",
            )
            self.assertEqual(
                stats["decisions"], stats["mapped"] + stats["refused"],
                f"{name} decision accounting must balance",
            )


class DecisionsCli(unittest.TestCase):
    def test_decisions_flag_writes_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            track_path = Path(tmp) / "fixture.json"
            track_path.write_text(
                json.dumps(v1_track()), encoding="utf-8", newline="\n"
            )
            out_path = Path(tmp) / "stats.json"
            rc = tr.main(
                ["--decisions", str(track_path), "--out", str(out_path)]
            )
            self.assertEqual(0, rc)
            stats = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(["rusher_1", "rusher_2"], stats["presence_gaps"])
            self.assertIsNone(stats["intake"])

    def test_decisions_flag_refuses_runtime_outside_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            track = v1_track()
            track["class"] = "RUNTIME"
            track["provenance"]["class"] = "RUNTIME"
            track_path = Path(tmp) / "fixture.json"
            track_path.write_text(
                json.dumps(track), encoding="utf-8", newline="\n"
            )
            rc = tr.main(["--decisions", str(track_path)])
            self.assertEqual(1, rc)

    def test_track_flag_still_validates_draft1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            track_path = Path(tmp) / "demo.json"
            track_path.write_text(
                json.dumps(tr.build_demo_track(reference())),
                encoding="utf-8", newline="\n",
            )
            self.assertEqual(0, tr.main(["--track", str(track_path)]))


if __name__ == "__main__":
    unittest.main()
