"""Tests for tools/adoption_demo.py — the v16 adoption record + demo proof
(reviews/adoption-v16/rationale.md, fixed before any v16 artifact existed).

Pre-registered bars covered here:

- the incumbent-reproduction bar: this module's own code path rebuilds the
  committed v13 demo APNG and track byte-exactly (runs pre-bank — it needs
  only banked bytes);
- swap purity proven in BOTH directions: the correct release-pinned K-S
  swap passes (k0 ticks 34-37, draw [38,32], 128 changed px per frame,
  shade/accent color identity); a planted off-k0 frame delta fails clause
  A; a wrong-bytes k0 substitute (K-R two-tone) fails clause B; a
  tampered staged file is refused at staging;
- scale-mirror fidelity at 4x (machine-asserted byte equality against the
  banked builder);
- determinism (report bytes, strip + side-by-side double-build);
- the v13+v14+v15 manifest pin lattice compared against live files
  (extends the v15 pin-compare test with the remedy manifest);
- register-entry shape (date + verbatim quote + carrier + reversal; no
  fiction names);
- pre-bank skip guards (committed-artifact tests skip until banked);
  post-bank: artifact files exist, hashes match the manifest, filenames
  carry the synthetic-adoption prefix, machine bars all true.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import adoption_demo as ad
import remedy_masks as rm
import track_recompose as tr
from make_contact_sheet import load_reference
from make_seam_timeline import SEAM_FONT
from png_writer import Rgba8Canvas

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = load_reference(ROOT / "manifests" / "render-reference.json")
CANVAS = 32


class _SharedBuilds:
    """Class-level fixtures: the two demo builds, built once per run."""

    _cache: dict | None = None

    @classmethod
    def builds(cls) -> dict:
        if cls._cache is None:
            tmp = tempfile.mkdtemp(prefix="adoption-v16-tests-")
            staged = ad.stage_ks_attack_dir(Path(tmp))
            incumbent = ad.build_demo(REFERENCE)
            substituted = ad.build_demo(REFERENCE, staged)
            cls._cache = {
                "staged": staged,
                "incumbent": incumbent,
                "substituted": substituted,
            }
        return cls._cache


class IncumbentReproduction(unittest.TestCase):
    """The pre-registered harness-identity bar (rationale, fixed first)."""

    def test_rebuild_equals_the_committed_v13_demo_bytes(self) -> None:
        result = ad.incumbent_reproduction(_SharedBuilds.builds()["incumbent"])
        self.assertTrue(result["apng_byte_identical"], result)
        self.assertTrue(result["track_byte_identical"], result)
        self.assertEqual(
            result["committed_apng_sha256"],
            "3cb8361a7bd4cddc070e587da023d5f3de84c3ceaeed3b311df68e40deb1392d",
        )


class SwapPurity(unittest.TestCase):

    def test_correct_swap_accepted_with_the_preregistered_values(self) -> None:
        builds = _SharedBuilds.builds()
        purity = ad.swap_purity(builds["incumbent"], builds["substituted"])
        self.assertTrue(purity["pass"], purity)
        self.assertEqual(purity["k0_ticks"], [34, 35, 36, 37])
        self.assertTrue(purity["k0_stream_consistent_with_v14_window"])
        self.assertEqual(purity["frames_compared"], 48)
        self.assertEqual(len(purity["per_tick"]), 4)
        for row in purity["per_tick"]:
            self.assertEqual(row["draw"], [38, 32])
            self.assertEqual(row["changed_px"], 128)
            self.assertTrue(row["sets_equal"])
            self.assertTrue(
                row["substituted_all_shade_and_incumbent_all_accent"]
            )

    def test_planted_off_k0_delta_fails_clause_a(self) -> None:
        builds = _SharedBuilds.builds()
        substituted = builds["substituted"]
        tampered_frames = list(substituted["frames"])
        victim = Rgba8Canvas(
            tampered_frames[10].width, tampered_frames[10].height, (0, 0, 0, 255)
        )
        victim._pixels[:] = tampered_frames[10]._pixels
        victim.put(50, 50, (255, 0, 255, 255))
        tampered_frames[10] = victim
        tampered = {**substituted, "frames": tampered_frames}
        purity = ad.swap_purity(builds["incumbent"], tampered)
        self.assertFalse(purity["pass"])
        bad = [r for r in purity["per_tick"] if r["tick"] == 10]
        self.assertEqual(len(bad), 1)
        self.assertFalse(bad[0]["sets_equal"])

    def test_wrong_bytes_substitute_fails_clause_b(self) -> None:
        """K-R shares the positional diff set; only clause B rejects it."""
        builds = _SharedBuilds.builds()
        with tempfile.TemporaryDirectory(prefix="adoption-v16-kr-") as tmp:
            staged = Path(tmp) / "kr-attack-dir"
            staged.mkdir()
            for facing in ("down", "right"):
                payload = (
                    rm.EXPORT_DIR
                    / f"{rm.variant_asset_id(facing, 'kr')}.png"
                ).read_bytes()
                (staged / tr.pose_filename("k0", facing)).write_bytes(payload)
            wrong = ad.build_demo(REFERENCE, staged)
            purity = ad.swap_purity(builds["incumbent"], wrong)
        self.assertFalse(purity["pass"])
        k0_rows = [r for r in purity["per_tick"] if r["pose"] == "k0"]
        self.assertEqual(len(k0_rows), 4)
        for row in k0_rows:
            # positional purity holds (same declared diff set) ...
            self.assertTrue(row["sets_equal"])
            # ... and the color clause is what rejects the wrong bytes.
            self.assertFalse(
                row["substituted_all_shade_and_incumbent_all_accent"]
            )

    def test_tampered_staged_source_refused_at_staging(self) -> None:
        with tempfile.TemporaryDirectory(prefix="adoption-v16-tam-") as tmp:
            root = Path(tmp)
            real = ad.ks_export_path("down").read_bytes()
            fake_export_dir = root / "fake-exports"
            fake_export_dir.mkdir()
            original_export_dir = rm.EXPORT_DIR
            try:
                for facing in ("down", "right"):
                    payload = bytearray(ad.ks_export_path(facing).read_bytes())
                    payload[-20] ^= 0xFF  # corrupt inside the IDAT stream
                    (
                        fake_export_dir
                        / f"{rm.variant_asset_id(facing, 'ks')}.png"
                    ).write_bytes(bytes(payload))
                (fake_export_dir / "release.json").write_bytes(
                    (original_export_dir / "release.json").read_bytes()
                )
                rm.EXPORT_DIR = fake_export_dir
                with self.assertRaises(ad.AdoptionDemoError):
                    ad.stage_ks_attack_dir(root)
            finally:
                rm.EXPORT_DIR = original_export_dir
            self.assertEqual(ad.ks_export_path("down").read_bytes(), real)


class ScaleMirrorFidelity(unittest.TestCase):

    def test_mirror_reproduces_the_banked_4x_frames_byte_identically(self) -> None:
        builds = _SharedBuilds.builds()
        # assert_mirror_fidelity raises on any byte difference.
        ad.assert_mirror_fidelity(builds["incumbent"], REFERENCE)

    def test_mirror_detects_a_divergence(self) -> None:
        builds = _SharedBuilds.builds()
        incumbent = builds["incumbent"]
        victim = Rgba8Canvas(
            incumbent["frames"][0].width, incumbent["frames"][0].height,
            (0, 0, 0, 255),
        )
        victim._pixels[:] = incumbent["frames"][0]._pixels
        victim.put(1, 1, (1, 2, 3, 255))
        tampered = {
            **incumbent, "frames": [victim] + incumbent["frames"][1:],
        }
        with self.assertRaises(ad.AdoptionDemoError):
            ad.assert_mirror_fidelity(tampered, REFERENCE)


class Determinism(unittest.TestCase):

    def test_report_bytes_double_build(self) -> None:
        builds = _SharedBuilds.builds()
        first = ad.report_bytes(
            ad.build_report(
                builds["incumbent"], builds["substituted"], builds["staged"]
            )
        )
        second = ad.report_bytes(
            ad.build_report(
                builds["incumbent"], builds["substituted"], builds["staged"]
            )
        )
        self.assertEqual(first, second)

    def test_strip_double_build(self) -> None:
        builds = _SharedBuilds.builds()
        params = {"kind": "strip"}
        first = ad.build_artifact(
            builds["incumbent"], builds["substituted"], REFERENCE, params
        )
        second = ad.build_artifact(
            builds["incumbent"], builds["substituted"], REFERENCE, params
        )
        self.assertEqual(first, second)

    def test_sbs_4x_real_double_build_and_frame_count(self) -> None:
        builds = _SharedBuilds.builds()
        params = {"kind": "sbs-demo", "scale": 4, "speed": "real"}
        first = ad.build_artifact(
            builds["incumbent"], builds["substituted"], REFERENCE, params
        )
        second = ad.build_artifact(
            builds["incumbent"], builds["substituted"], REFERENCE, params
        )
        self.assertEqual(first, second)
        self.assertEqual(first.count(b"fcTL"), 48)


class ArtifactMatrix(unittest.TestCase):

    def test_the_preregistered_matrix(self) -> None:
        names = ad.artifact_names()
        self.assertEqual(len(names), 9)
        apngs = [n for n in names if n.endswith(".apng")]
        strips = [n for n in names if n.endswith(".png")]
        self.assertEqual(len(apngs), 8)
        self.assertEqual(strips, ["synthetic-adoption-strip-attack-8x.png"])
        for name in names:
            self.assertTrue(name.startswith("synthetic-adoption-"), name)

    def test_drawn_labels_are_font_safe(self) -> None:
        for text in (
            ad.BANNER, ad.PROTOCOL_LINE, *ad.STREAM_LABELS,
            "SYNTHETIC ADOPTION EXP", "SYNTHETIC DEMO EXP",
            "REAL 1 60", "SLOW 6 60",
        ):
            for char in text:
                self.assertIn(char, SEAM_FONT, f"{char!r} in {text!r}")

    def test_strip_fits_the_png_reader_cap(self) -> None:
        builds = _SharedBuilds.builds()
        strip = ad.build_strip(
            builds["incumbent"], builds["substituted"], REFERENCE
        )
        self.assertLessEqual(strip.width, 4096, strip.width)
        self.assertLessEqual(strip.height, 4096, strip.height)


class PinLattice(unittest.TestCase):

    def test_v13_v14_v15_manifest_pins_match_live_files(self) -> None:
        """Extends the banked v15 pin-compare test with the v15 manifest
        itself (the deepened lattice; rationale bar 8)."""
        pins: dict[str, str] = {}
        v13 = json.loads(
            (ROOT / "reviews" / "recompose-v13" / "recompose-manifest.json")
            .read_text(encoding="utf-8")
        )
        pins.update(v13["mapping_source_sha256"])
        v14 = json.loads(
            (ROOT / "reviews" / "defect-audit-v14" / "defect-manifest.json")
            .read_text(encoding="utf-8")
        )
        pins.update(v14["module_source_sha256"])
        v15 = json.loads(
            (ROOT / "reviews" / "remedy-v15" / "remedy-manifest.json")
            .read_text(encoding="utf-8")
        )
        pins.update(v15["module_source_sha256"])
        self.assertGreaterEqual(len(pins), 23)
        for rel, pinned in sorted(pins.items()):
            live = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(live, pinned, f"pinned module drifted: {rel}")

    def test_module_pin_list_extends_the_v15_set(self) -> None:
        self.assertEqual(
            set(ad.MODULE_SOURCE_FILES),
            set(
                json.loads(
                    (ROOT / "reviews" / "remedy-v15" / "remedy-manifest.json")
                    .read_text(encoding="utf-8")
                )["module_source_sha256"]
            )
            | {"tools/adoption_demo.py"},
        )

    def test_no_exports_addition(self) -> None:
        self.assertFalse((ROOT / "exports" / "adoption-v16").exists())


class RegisterEntryShape(unittest.TestCase):
    REGISTER = ROOT / "docs" / "selection-register.md"

    def test_dated_entry_with_the_verbatim_owner_quote(self) -> None:
        text = self.REGISTER.read_text(encoding="utf-8")
        self.assertIn("2026-08-21", text)
        self.assertIn('"Approved, proceed"', text)

    def test_names_the_selected_assets_and_the_carrier(self) -> None:
        text = self.REGISTER.read_text(encoding="utf-8")
        for asset_id in (
            "player_1_lane_b_attack_down_k0_ks",
            "player_1_lane_b_attack_right_k0_ks",
        ):
            self.assertIn(asset_id, text)
        self.assertIn("reviews/remedy-v15/verdict.md", text)
        self.assertIn("exports/calibration-v2", text)

    def test_reversal_and_scope_lines_present(self) -> None:
        text = " ".join(self.REGISTER.read_text(encoding="utf-8").split())
        self.assertIn("Reversal: delete this entry", text)
        self.assertIn("no game-two integration is implied", text)


class CommittedBundleGuards(unittest.TestCase):
    """Post-bank guards; skip cleanly before the artifacts exist."""

    @classmethod
    def setUpClass(cls) -> None:
        if not ad.MANIFEST_PATH.is_file():
            raise unittest.SkipTest("adoption-v16 artifacts not banked yet")
        cls.manifest = json.loads(
            ad.MANIFEST_PATH.read_text(encoding="utf-8")
        )

    def test_manifest_provenance_and_pins(self) -> None:
        self.assertEqual(self.manifest["provenance"]["class"], "SYNTHETIC")
        pinned = self.manifest["module_source_sha256"]
        for rel in ad.MODULE_SOURCE_FILES:
            self.assertIn(rel, pinned)

    def test_committed_artifacts_exist_with_matching_hashes(self) -> None:
        for name, digest in self.manifest["artifacts"].items():
            path = ad.REVIEW_DIR / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), digest, name
            )

    def test_report_machine_bars_all_true(self) -> None:
        report = json.loads(ad.REPORT_PATH.read_text(encoding="utf-8"))
        for bar, value in report["machine_bars"].items():
            self.assertIs(value, True, bar)
        self.assertEqual(report["swap_purity"]["k0_ticks"], [34, 35, 36, 37])

    def test_every_artifact_filename_carries_the_synthetic_prefix(self) -> None:
        for name in self.manifest["artifacts"]:
            if name == ad.REPORT_PATH.name:
                continue
            self.assertTrue(name.startswith("synthetic-adoption-"), name)

    def test_double_build_recorded_identical(self) -> None:
        self.assertTrue(
            self.manifest["determinism"]["double_build_identical"]
        )
        self.assertEqual(self.manifest["determinism"]["artifact_count"], 10)

    def test_swap_source_pinned_to_the_release(self) -> None:
        swap = self.manifest["swap_source"]
        self.assertEqual(swap["release_id"], "remedy-v15")
        release = json.loads(
            (rm.EXPORT_DIR / "release.json").read_text(encoding="utf-8")
        )
        pins = {e["asset_id"]: e["sha256"] for e in release["exports"]}
        for facing in ("down", "right"):
            entry = swap["assets"][facing]
            self.assertEqual(pins[entry["asset_id"]], entry["sha256"])


if __name__ == "__main__":
    unittest.main()
