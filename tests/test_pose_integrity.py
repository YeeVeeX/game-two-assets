"""Tests for tools/pose_integrity_metrics.py — the v14 attack-read defect
audit (characterization only; fixes nothing, adjudicates nothing).

Pre-registered bars (reviews/defect-audit-v14/rationale.md, committed before
any artifact existed):

- the interior-hole detector proven in BOTH directions on synthetic fixtures
  (finds planted holes with exact count/area/bbox; stays silent on solid,
  concave-open, channel-to-edge, and edge-touching fixtures; the
  4-connectivity convention asserted explicitly — a diagonally-sealed ring
  encloses);
- hole-delta logic flags appear/disappear transitions and ignores stable
  holes;
- cut-change localization reports silhouette and recolor clusters with exact
  bboxes (machine-derived, no hardcoded region rectangles);
- accent clustering finds every planted accent blob with exact centroids;
- the audited tick stream derives its poses via the banked v13
  ``select_pose`` and its ordered classes equal the pre-registered cut
  sequence for both facings;
- 22/22 banked sprites analyzed; report + playback artifacts deterministic;
- banked modules untouched (manifest hash pins; pre-bank skip pattern) and
  the 26 banked export pins byte-verified.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import pose_integrity_metrics as pim
import track_recompose as tr
from anticipation_metrics import ACCENT_RGB
from make_contact_sheet import load_reference
from make_seam_timeline import STRIP, default_dirs
from seam_metrics import check_export_pins

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = load_reference(ROOT / "manifests" / "render-reference.json")
DIRS = default_dirs()

BODY = (200, 100, 40)


def make_raw(rows: list[str], colors: dict[str, tuple[int, int, int]]) -> bytes:
    """A 32x32 RGBA canvas from a character grid ('.' = transparent);
    rows shorter than 32 are padded transparent, grids shorter too."""
    raw = bytearray(32 * 32 * 4)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == ".":
                continue
            r, g, b = colors[char]
            offset = (y * 32 + x) * 4
            raw[offset:offset + 4] = bytes((r, g, b, 255))
    return bytes(raw)


class InteriorHoleDetector(unittest.TestCase):
    """Both directions: planted holes found exactly; hole-free stays silent."""

    def test_ring_encloses_one_hole(self) -> None:
        rows = [
            "........",
            ".XXXXX..",
            ".X...X..",
            ".X.X.X..",
            ".X...X..",
            ".XXXXX..",
        ]
        holes = pim.interior_holes(make_raw(rows, {"X": BODY}))
        self.assertEqual(1, len(holes))
        self.assertEqual(8, holes[0]["area"])  # 3x3 cavity minus the 1 island
        self.assertEqual([2, 2, 4, 4], holes[0]["bbox"])
        self.assertEqual([2, 4], holes[0]["row_band"])

    def test_solid_block_has_no_holes(self) -> None:
        rows = ["XXXX"] * 4
        self.assertEqual([], pim.interior_holes(make_raw(rows, {"X": BODY})))

    def test_concave_open_shape_has_no_holes(self) -> None:
        rows = [
            "XXXXX",
            "X....",
            "X.XXX",
            "X....",
            "XXXXX",
        ]
        self.assertEqual([], pim.interior_holes(make_raw(rows, {"X": BODY})))

    def test_one_px_channel_to_edge_is_exterior(self) -> None:
        rows = [
            ".XXXXX",
            ".X...X",
            ".X.XXX",  # channel exits through the ring at row 2? no — sealed
            ".X...X",
            ".XXXXX",
        ]
        # Break the ring: open a channel from the cavity to the canvas edge.
        rows[2] = ".X...."  # row 2 now runs transparent to the right edge
        self.assertEqual([], pim.interior_holes(make_raw(rows, {"X": BODY})))

    def test_diagonally_sealed_ring_encloses(self) -> None:
        # The declared 4-connectivity convention: transparency cannot pass
        # between two opaque cells that touch only diagonally.
        rows = [
            "........",
            "..XX....",
            ".X..X...",
            "..XX....",
        ]
        holes = pim.interior_holes(make_raw(rows, {"X": BODY}))
        self.assertEqual(1, len(holes))
        self.assertEqual(2, holes[0]["area"])
        self.assertEqual([2, 2, 3, 2], holes[0]["bbox"])

    def test_edge_touching_transparency_is_never_a_hole(self) -> None:
        # Fully transparent canvas + one opaque block: the transparent field
        # touches the border everywhere, so nothing is interior.
        rows = ["....", ".XX.", ".XX.", "...."]
        self.assertEqual([], pim.interior_holes(make_raw(rows, {"X": BODY})))

    def test_two_holes_reported_separately(self) -> None:
        rows = [
            "XXXXXXX",
            "X.X.X.X".replace(" ", ""),
            "XXXXXXX",
        ]
        holes = pim.interior_holes(make_raw(rows, {"X": BODY}))
        self.assertEqual(3, len(holes))
        self.assertEqual([1, 1, 1, 1], holes[0]["bbox"])
        self.assertEqual([3, 1, 3, 1], holes[1]["bbox"])
        self.assertEqual([5, 1, 5, 1], holes[2]["bbox"])


class HoleDeltas(unittest.TestCase):
    RING = [
        "XXXXX",
        "X...X",
        "XXXXX",
    ]
    SOLID = ["XXXXX", "XXXXX", "XXXXX"]

    def test_appear_and_disappear_flagged(self) -> None:
        solid = pim.interior_holes(make_raw(self.SOLID, {"X": BODY}))
        ring = pim.interior_holes(make_raw(self.RING, {"X": BODY}))
        deltas = pim.hole_deltas(solid, ring)
        self.assertEqual(1, len(deltas["appear"]))
        self.assertEqual([], deltas["disappear"])
        self.assertEqual([], deltas["stable"])
        deltas = pim.hole_deltas(ring, solid)
        self.assertEqual([], deltas["appear"])
        self.assertEqual(1, len(deltas["disappear"]))

    def test_stable_hole_ignored_by_the_candidate_class(self) -> None:
        ring_a = pim.interior_holes(make_raw(self.RING, {"X": BODY}))
        ring_b = pim.interior_holes(make_raw(self.RING, {"X": (10, 10, 10)}))
        deltas = pim.hole_deltas(ring_a, ring_b)
        self.assertEqual([], deltas["appear"])
        self.assertEqual([], deltas["disappear"])
        self.assertEqual(1, len(deltas["stable"]))


class CutChangeLocalization(unittest.TestCase):
    def test_silhouette_and_recolor_clusters(self) -> None:
        base = [
            "XXXX",
            "XXXX",
            "XXXX",
        ]
        changed = [
            "XXXX",
            "XAAX",
            "XXXX",
            ".XX.",  # new silhouette row below
        ]
        raw_a = make_raw(base, {"X": BODY})
        raw_b = make_raw(changed, {"X": BODY, "A": (1, 2, 3)})
        changes = pim.cut_changes(raw_a, raw_b)
        self.assertEqual(2, changes["recolor_px"])
        self.assertEqual(1, len(changes["recolor_clusters"]))
        self.assertEqual([1, 1, 2, 1], changes["recolor_clusters"][0]["bbox"])
        self.assertEqual(2, changes["silhouette_px"])
        self.assertEqual(1, len(changes["silhouette_clusters"]))
        self.assertEqual([1, 3, 2, 3], changes["silhouette_clusters"][0]["bbox"])

    def test_identical_frames_report_no_changes(self) -> None:
        raw = make_raw(["XX", "XX"], {"X": BODY})
        changes = pim.cut_changes(raw, raw)
        self.assertEqual(0, changes["silhouette_px"])
        self.assertEqual(0, changes["recolor_px"])
        self.assertEqual([], changes["silhouette_clusters"])
        self.assertEqual([], changes["recolor_clusters"])


class AccentClusters(unittest.TestCase):
    def test_two_blobs_with_centroids(self) -> None:
        rows = [
            "AA..A",
            "AA..A",
        ]
        clusters = pim.accent_clusters(make_raw(rows, {"A": ACCENT_RGB}))
        self.assertEqual(2, len(clusters))
        self.assertEqual(4, clusters[0]["area"])
        self.assertEqual([0.5, 0.5], clusters[0]["centroid"])
        self.assertEqual(2, clusters[1]["area"])
        self.assertEqual([4.0, 0.5], clusters[1]["centroid"])

    def test_non_accent_colors_ignored(self) -> None:
        clusters = pim.accent_clusters(make_raw(["XX"], {"X": BODY}))
        self.assertEqual([], clusters)


class AuditStream(unittest.TestCase):
    """The stream is the declared mapping (banked select_pose, unmodified)."""

    def test_classes_match_the_preregistered_sequence(self) -> None:
        for facing in pim.FACINGS:
            stream = pim.audit_stream(REFERENCE, facing)
            self.assertEqual(pim.SEQUENCE, pim.stream_classes(stream))

    def test_tick_counts_and_offsets_follow_the_pinned_constants(self) -> None:
        constants = pim.audit_constants(REFERENCE)
        for facing in pim.FACINGS:
            stream = pim.audit_stream(REFERENCE, facing)
            self.assertEqual(
                pim.IDLE_PRE_TICKS + constants["windup_frames"]
                + constants["active_frames"] + constants["recovery_frames"]
                + pim.IDLE_POST_TICKS,
                len(stream),
            )
            for entry in stream:
                pose = entry["pose"]
                if pose in ("w0", "a0"):
                    self.assertEqual(constants["windup_px"], entry["offset_px"])
                elif pose == "k0":
                    self.assertEqual(constants["active_px"], entry["offset_px"])
                else:
                    self.assertEqual(0, entry["offset_px"])

    def test_stream_poses_equal_banked_select_pose(self) -> None:
        constants = pim.audit_constants(REFERENCE)
        for facing in pim.FACINGS:
            records = pim.attack_records(constants, facing)
            stream = pim.audit_stream(REFERENCE, facing)
            for record, entry in zip(records, stream):
                pose, pose_facing, offset = tr.select_pose(record, constants)
                self.assertEqual((pose, facing, offset),
                                 (entry["pose"], pose_facing, entry["offset_px"]))

    def test_cuts_are_the_seven_preregistered_boundaries(self) -> None:
        for facing in pim.FACINGS:
            cuts = pim.stream_cuts(pim.audit_stream(REFERENCE, facing))
            self.assertEqual(
                [("idle", "w0"), ("w0", "a0"), ("a0", "k0"), ("k0", "s0"),
                 ("s0", "r0"), ("r0", "x0"), ("x0", "idle")],
                [(c["from_pose"], c["to_pose"]) for c in cuts],
            )


class RealSetReport(unittest.TestCase):
    """Structure + determinism over the banked 22-sprite set."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.report = pim.build_report(REFERENCE, DIRS)

    def test_full_coverage(self) -> None:
        self.assertEqual(len(STRIP) * 2, self.report["coverage"]["sprites_analyzed"])
        self.assertEqual(22, self.report["coverage"]["expected"])
        for facing in pim.FACINGS:
            self.assertEqual(sorted(STRIP), sorted(self.report["poses"][facing]))
            for pose in STRIP:
                entry = self.report["poses"][facing][pose]
                for field in ("mass", "bbox", "color_histogram",
                              "interior_holes", "accent_clusters"):
                    self.assertIn(field, entry)

    def test_sequence_sections_cover_both_facings(self) -> None:
        for facing in pim.FACINGS:
            section = self.report["sequence"][facing]
            self.assertEqual(7, len(section["cuts"]))
            for cut in section["cuts"]:
                for field in ("silhouette_clusters", "recolor_clusters",
                              "holes", "accent_px_from", "accent_px_to"):
                    self.assertIn(field, cut)

    def test_report_deterministic(self) -> None:
        again = pim.build_report(REFERENCE, DIRS)
        self.assertEqual(pim.report_bytes(self.report), pim.report_bytes(again))

    def test_provenance_is_synthetic_and_non_adjudicating(self) -> None:
        provenance = self.report["provenance"]
        self.assertEqual("SYNTHETIC", provenance["class"])
        self.assertIn("ZERO register items", provenance["statement"])


class ArtifactDeterminism(unittest.TestCase):
    """One strip and one APNG double-build byte-identically (the full set is
    covered by --check against committed bytes)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.poses = tr.load_poses(DIRS)

    def test_strip_double_build(self) -> None:
        params = {"kind": "strip", "facing": "down", "zone": "zone_1"}
        first = pim.build_artifact(REFERENCE, self.poses, params)
        second = pim.build_artifact(REFERENCE, self.poses, params)
        self.assertEqual(first, second)

    def test_apng_double_build_and_delays(self) -> None:
        params = {"kind": "apng", "facing": "down", "scale": 4, "speed": "slow6"}
        first = pim.build_artifact(REFERENCE, self.poses, params)
        second = pim.build_artifact(REFERENCE, self.poses, params)
        self.assertEqual(first, second)
        delays = pim.slow_delays(5)
        self.assertEqual([(6, 60)] * 4 + [(30, 60)], delays)


class BankedUntouchedGuards(unittest.TestCase):
    def test_banked_export_pins_verify(self) -> None:
        result = check_export_pins(ROOT / "exports")
        self.assertEqual([], result["failures"])
        self.assertEqual(26, result["verified"])

    def test_no_audit_export_directory(self) -> None:
        self.assertFalse((ROOT / "exports" / "defect-audit-v14").exists())


class CommittedBundleGuards(unittest.TestCase):
    """Committed-artifact guards; each skips until the audit is banked
    (the v10/v11/v13 pre-bank artifact-guard pattern)."""

    def setUp(self) -> None:
        if not pim.MANIFEST_PATH.is_file():
            self.skipTest("audit bundle not banked yet")
        self.manifest = json.loads(pim.MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_completeness(self) -> None:
        self.assertEqual("SYNTHETIC", self.manifest["provenance"]["class"])
        self.assertTrue(self.manifest["repo_commit_at_generation"])
        self.assertTrue(self.manifest["determinism"]["double_build_identical"])
        self.assertEqual(tr.MAPPING_ID, self.manifest["audit"]["mapping_id"])
        self.assertEqual(list(pim.SEQUENCE),
                         self.manifest["audit"]["sequence_classes"])
        self.assertIn("viewing_protocol", self.manifest)
        for field in ("apng_real_delays", "apng_slow_delays", "statement"):
            self.assertIn(field, self.manifest["viewing_protocol"])

    def test_module_hash_pins_match_live_files(self) -> None:
        live = pim.module_hashes()
        pinned = self.manifest["module_source_sha256"]
        for rel in pim.MODULE_SOURCE_FILES:
            self.assertIn(rel, pinned)
            if rel == "tools/pose_integrity_metrics.py":
                continue  # self-pin is generation-time identity
            self.assertEqual(pinned[rel], live[rel], rel)

    def test_committed_artifact_hashes_match(self) -> None:
        for name, digest in self.manifest["artifacts"].items():
            path = pim.AUDIT_DIR / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(digest, pim.file_sha256(path), name)

    def test_artifact_filenames_carry_the_synthetic_label(self) -> None:
        for name in self.manifest["artifacts"]:
            if name.endswith(".json"):
                continue
            self.assertTrue(name.startswith("synthetic-"), name)

    def test_committed_report_regenerates_byte_identically(self) -> None:
        fresh = pim.report_bytes(pim.build_report(REFERENCE, DIRS))
        self.assertEqual(fresh, pim.REPORT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
