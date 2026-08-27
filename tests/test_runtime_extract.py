"""Tests for the v31 RUNTIME-EXP single-creature extraction of
tools/track_recompose.py.

Pre-registered protocols (reviews/runtime-recompose-v31/rationale.md,
committed cells-NULL BEFORE this module existed), covered branch by branch:

- the additive zone-palette loader (OPT-IN merge; collisions and malformed
  entries refuse typed; the PLAIN reference keeps the banked-zones-only
  refusal law - the banked v30 ``unmapped-zone`` test is the other half);
- the committed district palette file: five-key convention shape, values
  byte-equal to the banked zone_2 corroboration entry, anchoring block
  bound to the runtime-baseline CONTENT pin (sha256_lf);
- subject law (exactly one stable possessed holder; typed refusals for
  zero/multiple/moving possession) + the striker kit gate;
- the per-creature decision stream (mapped + typed-refusal entries);
- the span policy (complete attack cycle w0..x0 returning to idle;
  longest; tie -> earliest; refusals split runs) and the window formula
  (whole-TILE outward rounding + one TILE margin);
- sub-track extraction (validates as v1; verbatim records; provenance
  binds to the source bundle; RUNTIME admission still refused without the
  verified intake context - the refusal is never weakened);
- the full pipeline on a tmpdir evidence bundle (double-build
  determinism, manifest fields, disclosure verbatim, EXP filenames) and
  the pre-registered STOP branches (kit gate; no-clean-attack-cycle banks
  the TEXT capture with zero composed artifacts).

Small fixtures only - the committed-evidence regeneration guard lives in
the SLOW tier (tests/test_track_recompose.py RuntimeArtifactGuards).
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import track_recompose as tr
from make_contact_sheet import load_reference

REPO = Path(__file__).resolve().parents[1]
PALETTE = REPO / "manifests" / "zone-palette-district.json"


def reference() -> dict:
    return load_reference(REPO / "manifests" / "render-reference.json")


def striker_constants() -> dict:
    return {
        "striker": {"step_frames": 13, "windup_frames": 5,
                    "active_frames": 4, "recovery_frames": 8},
    }


def subject_record(**overrides) -> dict:
    base = {
        "tile_x": 3, "tile_y": 1, "px": 100.0, "py": 50.0,
        "facing": [1, 0], "tween_left": 0, "tween_total": 0,
        "attack_state": "idle", "current_action": None, "state_frames": 0,
        "hp": 80, "iframes": 0, "possessed": True,
    }
    base.update(overrides)
    return base


def attack_states(constants: dict) -> list[tuple[str, int]]:
    """(attack_state, state_frames) walk of one complete cycle."""
    walk = []
    for state, key in (("windup", "windup_frames"), ("active", "active_frames"),
                       ("recovery", "recovery_frames")):
        for left in range(constants[key], 0, -1):
            walk.append((state, left))
    return walk


def runtime_attack_track(
    idle_head: int = 2, idle_tail: int = 2, first_frame: int = 100,
    complete: bool = True,
) -> dict:
    """RUNTIME v1 striker fixture: idle head, one attack cycle (optionally
    truncated mid-recovery -> never reaches x0), idle tail."""
    cycle = attack_states(striker_constants()["striker"])
    if not complete:
        cycle = cycle[:-2]  # recovery interrupted before x0
    ticks = []
    frame = first_frame
    states: list[tuple[str, int]] = [("idle", 0)] * idle_head
    states += cycle
    states += [("idle", 0)] * idle_tail
    for state, left in states:
        record = subject_record(
            attack_state=state, state_frames=left,
            current_action=None if state == "idle" else "attack",
        )
        ticks.append({
            "frame": frame,
            "creatures": {"striker_1": record},
            "masks": {"1": 0},
        })
        frame += 1
    return {
        "schema_version": "1",
        "class": "RUNTIME",
        "tick_ms": 16.666666,
        "zone": "district",
        "view": {"origin_px": [0, 0], "width": 960, "height": 540},
        "constants": striker_constants(),
        "creatures": [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
        ],
        "ticks": ticks,
        "provenance": {
            "class": "RUNTIME",
            "producer": "tests/test_runtime_extract.py fixture",
            "bundle_id": "fixture-bundle",
            "statement": "hand-built v1 fixture; never evidence",
        },
    }


def write_fixture_bundle(root: Path, track: dict) -> Path:
    """A verified-shape evidence bundle in a tmpdir root (the
    IntakeGateFailDirections PASS-direction pattern)."""
    bundle = root / "fixture-bundle"
    (bundle / "tracks").mkdir(parents=True)
    track_path = bundle / "tracks" / "t.json"
    track_path.write_text(
        json.dumps(track, indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    digest = tr.file_sha256(track_path)
    (bundle / "tracks" / "t.json.sha256").write_text(
        f"{digest}  t.json\n", encoding="utf-8"
    )
    last = track["ticks"][-1]["frame"]
    (bundle / "manifest.json").write_text(
        json.dumps({
            "bundle_id": "fixture-bundle", "fingerprint_md5": "f" * 32,
            "ticks_executed": last + 10, "members": {},
        }), encoding="utf-8",
    )
    (bundle / "verification.json").write_text(
        json.dumps({
            "bundle_id": "fixture-bundle", "verdict": "PASS", "runs": 2,
            "fingerprint_at_verification": "f" * 32,
        }), encoding="utf-8",
    )
    return track_path


class ZonePaletteLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = reference()

    def test_merge_is_additive_and_opt_in(self) -> None:
        merged = tr.load_zone_palette(self.reference, PALETTE)
        self.assertIn("district", merged["zones"])
        self.assertNotIn("district", self.reference["zones"])  # deep copy
        for key in ("zone_1", "zone_2"):
            self.assertEqual(
                self.reference["zones"][key], merged["zones"][key]
            )

    def test_collision_with_banked_zone_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "palette.json"
            path.write_text(json.dumps({
                "zones": {"zone_1": {
                    key: [0, 0, 0] for key in tr.ZONE_ENTRY_KEYS
                }},
            }), encoding="utf-8")
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_zone_palette(self.reference, path)
            self.assertIn("zone-palette-collision", str(ctx.exception))

    def test_missing_key_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "palette.json"
            entry = {key: [1, 2, 3] for key in tr.ZONE_ENTRY_KEYS}
            del entry["motif"]
            path.write_text(
                json.dumps({"zones": {"other": entry}}), encoding="utf-8"
            )
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_zone_palette(self.reference, path)
            self.assertIn("zone-palette-invalid", str(ctx.exception))

    def test_non_triple_value_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "palette.json"
            entry = {key: [1, 2, 3] for key in tr.ZONE_ENTRY_KEYS}
            entry["floor"] = [1, 2]
            path.write_text(
                json.dumps({"zones": {"other": entry}}), encoding="utf-8"
            )
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_zone_palette(self.reference, path)
            self.assertIn("zone-palette-invalid", str(ctx.exception))

    def test_empty_palette_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "palette.json"
            path.write_text(json.dumps({"zones": {}}), encoding="utf-8")
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_zone_palette(self.reference, path)
            self.assertIn("zone-palette-invalid", str(ctx.exception))

    def test_plain_reference_still_refuses_district(self) -> None:
        """The refusal law is NOT weakened: without the opt-in merge the
        district zone stays unmapped (the banked v30 test is the other
        half of this proof)."""
        track = runtime_attack_track()
        track["class"] = "SYNTHETIC"
        track["provenance"]["class"] = "SYNTHETIC"
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.recompose_track(
                track, tr.load_poses(tr.default_dirs()), self.reference
            )
        self.assertIn("unmapped-zone", str(ctx.exception))


class DistrictPaletteFile(unittest.TestCase):
    """The committed palette file: convention shape + content anchoring."""

    def setUp(self) -> None:
        self.payload = json.loads(PALETTE.read_text(encoding="utf-8"))

    def test_five_key_convention_shape(self) -> None:
        district = self.payload["zones"]["district"]
        self.assertEqual(sorted(tr.ZONE_ENTRY_KEYS), sorted(district))

    def test_values_equal_the_banked_zone_2_corroboration(self) -> None:
        """zone_2 was captured from data/zones/district.json (display_name
        'ZONE 2'); the derived district entry must be byte-equal to it."""
        self.assertEqual(
            reference()["zones"]["zone_2"],
            self.payload["zones"]["district"],
        )

    def test_anchoring_is_bound_to_the_runtime_baseline_content_pin(self) -> None:
        baseline = json.loads(
            (REPO / "manifests" / "runtime-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        pinned = {
            entry["path"]: entry["sha256_lf"]
            for entry in baseline["source_files"]
        }
        anchoring = self.payload["anchoring"]
        self.assertEqual(
            pinned["data/zones/district.json"], anchoring["source_sha256_lf"]
        )
        self.assertEqual("data/zones/district.json", anchoring["source_file"])
        for key in tr.ZONE_ENTRY_KEYS:
            self.assertIn(key, anchoring["value_citations"])


class SubjectLaw(unittest.TestCase):
    def test_single_stable_holder_returned_with_kit(self) -> None:
        self.assertEqual(
            ("striker_1", "striker"), tr.subject_of(runtime_attack_track())
        )

    def test_zero_possessed_tick_refuses(self) -> None:
        track = runtime_attack_track()
        track["ticks"][1]["creatures"]["striker_1"]["possessed"] = False
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.subject_of(track)
        self.assertIn("unsupported-subject", str(ctx.exception))
        self.assertIn("0 possessed", str(ctx.exception))

    def test_multiple_possessed_tick_refuses(self) -> None:
        track = runtime_attack_track()
        track["creatures"].append(
            {"name": "striker_2", "faction": "pack", "kit": "striker"}
        )
        for tick in track["ticks"]:
            tick["creatures"]["striker_2"] = subject_record()
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.subject_of(track)
        self.assertIn("2 possessed", str(ctx.exception))

    def test_moving_possession_refuses(self) -> None:
        track = runtime_attack_track()
        track["creatures"].append(
            {"name": "striker_2", "faction": "pack", "kit": "striker"}
        )
        for index, tick in enumerate(track["ticks"]):
            hand_off = index >= len(track["ticks"]) // 2
            tick["creatures"]["striker_1"]["possessed"] = not hand_off
            tick["creatures"]["striker_2"] = subject_record(
                possessed=hand_off
            )
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.subject_of(track)
        self.assertIn("possession moves between", str(ctx.exception))


class SubjectDecisionEntries(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = reference()

    def test_mapped_entries_carry_the_decision(self) -> None:
        track = runtime_attack_track()
        entries = tr.subject_decision_entries(
            track, self.reference, "striker_1"
        )
        self.assertEqual(len(track["ticks"]), len(entries))
        self.assertEqual("idle", entries[0]["decision"]["pose"])
        self.assertEqual("w0", entries[2]["decision"]["pose"])
        lunge = self.reference["feedback_states"]["lunge_offset"]
        self.assertEqual(
            lunge["windup_px"], entries[2]["decision"]["offset_px"]
        )

    def test_refusal_entries_are_typed(self) -> None:
        track = runtime_attack_track()
        track["ticks"][0]["creatures"]["striker_1"]["facing"] = [0, -1]
        entries = tr.subject_decision_entries(
            track, self.reference, "striker_1"
        )
        self.assertEqual(
            "unrenderable-facing", entries[0]["refusal"]["class"]
        )
        self.assertIn("decision", entries[1])

    def test_unknown_creature_refuses(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.subject_decision_entries(
                runtime_attack_track(), self.reference, "ghost_1"
            )
        self.assertIn("unsupported-subject", str(ctx.exception))


class SpanPolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = reference()
        self.constants = tr.mapping_constants(
            runtime_attack_track(), "striker", self.reference
        )

    def entries(self, track: dict) -> list[dict]:
        return tr.subject_decision_entries(track, self.reference, "striker_1")

    def test_striker_cycle_poses_are_the_banked_timeline(self) -> None:
        self.assertEqual(
            ["w0", "a0", "a0", "a0", "a0", "k0", "k0", "k0", "k0",
             "s0", "r0", "r0", "r0", "r0", "r0", "r0", "x0"],
            tr.attack_cycle_poses(self.constants),
        )

    def test_full_cycle_with_idle_tail_qualifies(self) -> None:
        track = runtime_attack_track(first_frame=100)
        span = tr.derive_span(self.entries(track), self.constants)
        self.assertEqual((100, 100 + len(track["ticks"]) - 1), span)

    def test_incomplete_cycle_returns_none(self) -> None:
        track = runtime_attack_track(complete=False)
        self.assertIsNone(
            tr.derive_span(self.entries(track), self.constants)
        )

    def test_cycle_without_idle_return_returns_none(self) -> None:
        track = runtime_attack_track(idle_tail=0)
        self.assertIsNone(
            tr.derive_span(self.entries(track), self.constants)
        )

    def test_refusal_splits_the_run(self) -> None:
        """A refusal on the LAST idle tick strips the idle return from the
        cycle's run - the cycle no longer qualifies."""
        track = runtime_attack_track(idle_tail=1)
        track["ticks"][-1]["creatures"]["striker_1"]["facing"] = [0, -1]
        self.assertIsNone(
            tr.derive_span(self.entries(track), self.constants)
        )

    def test_longest_qualifying_span_wins(self) -> None:
        """Two qualifying runs split by one refusal tick: the longer
        (later) run wins."""
        short = runtime_attack_track(idle_head=1, idle_tail=1,
                                     first_frame=100)
        barrier = runtime_attack_track(idle_head=0, idle_tail=0,
                                       first_frame=120)
        long = runtime_attack_track(idle_head=4, idle_tail=4,
                                    first_frame=121)
        ticks = short["ticks"]
        barrier_tick = barrier["ticks"][0]
        barrier_tick["creatures"]["striker_1"]["facing"] = [0, -1]
        ticks.append(barrier_tick)
        ticks.extend(long["ticks"])
        track = runtime_attack_track()
        track["ticks"] = ticks
        span = tr.derive_span(self.entries(track), self.constants)
        self.assertEqual((121, 121 + len(long["ticks"]) - 1), span)

    def test_equal_lengths_tie_breaks_earliest(self) -> None:
        first = runtime_attack_track(idle_head=1, idle_tail=1,
                                     first_frame=100)
        barrier = runtime_attack_track(idle_head=0, idle_tail=0,
                                       first_frame=119)
        second = runtime_attack_track(idle_head=1, idle_tail=1,
                                      first_frame=120)
        barrier_tick = barrier["ticks"][0]
        barrier_tick["creatures"]["striker_1"]["facing"] = [0, -1]
        ticks = first["ticks"] + [barrier_tick] + second["ticks"]
        track = runtime_attack_track()
        track["ticks"] = ticks
        span = tr.derive_span(self.entries(track), self.constants)
        self.assertEqual((100, 100 + len(first["ticks"]) - 1), span)


class WindowFormula(unittest.TestCase):
    def test_hand_computed_window_with_lunge(self) -> None:
        """Idle at (100, 50) then active (+6 along +x): world draw xs are
        {100, 106}, ys {50}. x0 = floor(100/32)*32 - 32 = 64;
        x1 = ceil((106+32)/32)*32 + 32 = 192; y0 = floor(50/32)*32 - 32 = 0;
        y1 = ceil((50+32)/32)*32 + 32 = 128."""
        track = runtime_attack_track(idle_head=1, idle_tail=0)
        track["ticks"] = track["ticks"][:2]
        cycle_tick = track["ticks"][1]
        cycle_tick["creatures"]["striker_1"].update(
            attack_state="active", state_frames=4, current_action="attack",
        )
        view = tr.derive_window(
            track, "striker_1", track["ticks"][0]["frame"],
            track["ticks"][1]["frame"], reference(),
        )
        self.assertEqual(
            {"origin_px": [64, 0], "width": 128, "height": 128}, view
        )

    def test_window_is_tile_aligned_with_margin(self) -> None:
        track = runtime_attack_track()
        first = track["ticks"][0]["frame"]
        last = track["ticks"][-1]["frame"]
        view = tr.derive_window(track, "striker_1", first, last, reference())
        self.assertEqual(0, view["origin_px"][0] % tr.TILE)
        self.assertEqual(0, view["origin_px"][1] % tr.TILE)
        self.assertEqual(0, view["width"] % tr.TILE)
        self.assertEqual(0, view["height"] % tr.TILE)
        # subject at (100, 50) +- lunge: >= 1 TILE margin each side
        self.assertLessEqual(view["origin_px"][0], 100 - 3 - tr.TILE)
        self.assertLessEqual(view["origin_px"][1], 50 - tr.TILE)


class ExtractSubjectTrack(unittest.TestCase):
    def setUp(self) -> None:
        self.track = runtime_attack_track()
        self.first = self.track["ticks"][2]["frame"]
        self.last = self.track["ticks"][-1]["frame"]
        self.view = {"origin_px": [64, 0], "width": 128, "height": 128}
        self.sub = tr.extract_subject_track(
            self.track, "striker_1", self.first, self.last, self.view,
            "a" * 64,
        )

    def test_extracted_track_validates_as_v1(self) -> None:
        self.assertEqual([], tr.validate_track(self.sub))

    def test_single_creature_roster_and_kit_constants(self) -> None:
        self.assertEqual(1, len(self.sub["creatures"]))
        self.assertEqual(["striker"], sorted(self.sub["constants"]))
        self.assertEqual(
            self.track["constants"]["striker"],
            self.sub["constants"]["striker"],
        )

    def test_records_and_masks_copied_verbatim(self) -> None:
        for tick in self.sub["ticks"]:
            source = next(
                t for t in self.track["ticks"] if t["frame"] == tick["frame"]
            )
            self.assertEqual(
                source["creatures"]["striker_1"],
                tick["creatures"]["striker_1"],
            )
            self.assertEqual(source["masks"], tick["masks"])
        self.assertEqual(
            self.last - self.first + 1, len(self.sub["ticks"])
        )

    def test_provenance_binds_to_source_bundle_and_protocol(self) -> None:
        provenance = self.sub["provenance"]
        self.assertEqual("RUNTIME", provenance["class"])
        self.assertEqual("fixture-bundle", provenance["bundle_id"])
        self.assertEqual("a" * 64, provenance["source_track_sha256"])
        self.assertEqual(
            [self.first, self.last],
            provenance["extraction"]["span_frames"],
        )
        self.assertEqual(tr.RUNTIME_EXP_DISCLOSURE, provenance["statement"])

    def test_extracted_runtime_track_still_needs_the_intake_gate(self) -> None:
        """The refusal is never weakened: extraction output without the
        verified intake context refuses with the SAME class."""
        merged = tr.load_zone_palette(reference(), PALETTE)
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.recompose_track(
                self.sub, tr.load_poses(tr.default_dirs()), merged,
                intake=None,
            )
        self.assertIn(
            "runtime-intake-not-established", str(ctx.exception)
        )


class RuntimePipeline(unittest.TestCase):
    """The full --make-runtime-artifacts path on a tmpdir evidence bundle."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.out = self.root / "out"

    def run_pipeline(self, track: dict) -> dict:
        track_path = write_fixture_bundle(self.root, track)
        return tr.make_runtime_artifacts(
            track_path, reference(), tr.default_dirs(),
            out_dir=self.out, palette_path=PALETTE,
            evidence_root=self.root,
        )

    def test_pipeline_produces_the_exp_bundle(self) -> None:
        track = runtime_attack_track()
        manifest = self.run_pipeline(track)
        self.assertEqual("RUNTIME-EXP", manifest["artifact_class"])
        self.assertEqual(tr.RUNTIME_EXP_DISCLOSURE, manifest["disclosure"])
        self.assertTrue(manifest["determinism"]["double_build_identical"])
        self.assertEqual(
            [track["ticks"][0]["frame"], track["ticks"][-1]["frame"]],
            manifest["span_frames"],
        )
        self.assertEqual(("striker_1", "striker"),
                         (manifest["subject"]["name"],
                          manifest["subject"]["kit"]))
        self.assertEqual([1, tr.APNG_SCALE],
                         manifest["apng"]["zoom_scales"])
        for name, digest in manifest["artifacts"].items():
            path = self.out / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(digest, tr.file_sha256(path), name)
        for name in manifest["artifacts"]:
            self.assertTrue(
                name.startswith("runtime-exp-")
                or name == "decisions-subject.json",
                name,
            )
        window = manifest["window"]
        self.assertEqual(0, window["width"] % tr.TILE)
        self.assertEqual(0, window["height"] % tr.TILE)

    def test_stop_branch_banks_the_text_capture_only(self) -> None:
        track = runtime_attack_track(complete=False)
        with self.assertRaises(tr.RecomposeError) as ctx:
            self.run_pipeline(track)
        self.assertIn("no-clean-attack-cycle", str(ctx.exception))
        self.assertTrue((self.out / "decisions-subject.json").is_file())
        self.assertFalse(
            (self.out / tr.RUNTIME_SHEET.name).exists()
        )
        self.assertFalse(
            (self.out / tr.RUNTIME_MANIFEST.name).exists()
        )
        capture = json.loads(
            (self.out / "decisions-subject.json").read_text(encoding="utf-8")
        )
        self.assertIsNone(capture["span"])
        self.assertEqual("striker_1", capture["subject"])

    def test_non_striker_subject_kit_stops(self) -> None:
        track = runtime_attack_track()
        track["creatures"][0]["kit"] = "rusher"
        track["constants"] = {
            "rusher": striker_constants()["striker"]
        }
        with self.assertRaises(tr.RecomposeError) as ctx:
            self.run_pipeline(track)
        self.assertIn("unsupported-subject-kit", str(ctx.exception))
        self.assertFalse(
            (self.out / "decisions-subject.json").exists()
        )

    def test_runtime_track_without_bundle_refuses_at_the_gate(self) -> None:
        track_path = self.root / "loose.json"
        track_path.write_text(
            json.dumps(runtime_attack_track()), encoding="utf-8",
            newline="\n",
        )
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.make_runtime_artifacts(
                track_path, reference(), tr.default_dirs(),
                out_dir=self.out, palette_path=PALETTE,
                evidence_root=self.root / "elsewhere",
            )
        self.assertIn(
            "runtime-intake-not-established", str(ctx.exception)
        )


class DecisionsCreatureCli(unittest.TestCase):
    def test_creature_filter_writes_per_tick_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            track = runtime_attack_track()
            track["class"] = "SYNTHETIC"
            track["provenance"]["class"] = "SYNTHETIC"
            track_path = Path(tmp) / "fixture.json"
            track_path.write_text(
                json.dumps(track), encoding="utf-8", newline="\n"
            )
            out_path = Path(tmp) / "subject.json"
            rc = tr.main([
                "--decisions", str(track_path),
                "--creature", "striker_1", "--out", str(out_path),
            ])
            self.assertEqual(0, rc)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual("striker_1", payload["subject"])
            self.assertEqual("striker", payload["kit"])
            self.assertEqual(len(track["ticks"]), len(payload["entries"]))
            self.assertEqual(len(track["ticks"]), payload["mapped"])
            self.assertEqual(0, payload["refused"])

    def test_unknown_creature_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            track = runtime_attack_track()
            track["class"] = "SYNTHETIC"
            track["provenance"]["class"] = "SYNTHETIC"
            track_path = Path(tmp) / "fixture.json"
            track_path.write_text(
                json.dumps(track), encoding="utf-8", newline="\n"
            )
            rc = tr.main([
                "--decisions", str(track_path), "--creature", "ghost_1",
            ])
            self.assertEqual(1, rc)


if __name__ == "__main__":
    unittest.main()
