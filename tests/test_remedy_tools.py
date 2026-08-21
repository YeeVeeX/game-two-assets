"""Tests for tools/remedy_masks.py + tools/remedy_metrics.py — the v15
DEF-1 remedy exploration (reviews/remedy-v15/rationale.md, fixed before any
variant pixel existed).

Pre-registered bars covered here:

- mask derivation exactness: both facings, the v14 expectations (16 px down
  [12,13,19,14], 8 px right [24,13,27,14]), the subset assertion, the feet
  row law, disjointness from eyes/feet, the kr split totality;
- the diff-declaration verifier proven in BOTH directions on synthetic
  fixtures (accepts a correct variant; rejects an off-mask recolor, an
  alpha change, an out-of-ramp color);
- eye integrity proven in BOTH directions (a correct recolor of the banked
  k0 passes; a half-recolored gape or a touched eye pixel fails);
- variant specs load under the banked pixel_spec contract law and differ
  from the banked k0 grid at exactly the declared set;
- determinism (masks payload, spec bytes, strip double-build);
- pre-bank skip guards (release/artifact tests skip until banked);
- banked-untouched guards: the 26 banked export pins byte-verified and the
  v13/v14 manifest module pins compared against live files (the
  pin-compare equivalent of both banked --checks).
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import pose_integrity_metrics as pim
import remedy_masks as rm
import remedy_metrics as rmx
from make_contact_sheet import load_reference
from make_seam_timeline import default_dirs
from pixel_spec import load_spec
from seam_metrics import check_export_pins

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = load_reference(ROOT / "manifests" / "render-reference.json")
DIRS = default_dirs()
CANVAS = 32

SHADE = "#8c3818"
OUTLINE = "#401c10"
ACCENT = "#140e0c"


def masks_payload() -> dict:
    return json.loads(rm.MASKS_PATH.read_text(encoding="utf-8"))


def hex_rgb(color: str) -> tuple[int, int, int]:
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))


def apply_recolor(raw: bytes, recolor: dict[tuple[int, int], str]) -> bytes:
    """In-memory masked recolor of a raw RGBA canvas (test fixture builder)."""
    out = bytearray(raw)
    for (x, y), color in recolor.items():
        offset = (y * CANVAS + x) * 4
        assert out[offset + 3] == 255
        out[offset:offset + 3] = bytes(hex_rgb(color))
    return bytes(out)


class MaskDerivation(unittest.TestCase):
    """The pre-registered definition reproduces the v14 numbers exactly."""

    def test_derived_masks_match_the_v14_expectations(self) -> None:
        payload = rm.masks_payload(DIRS)
        down = payload["facings"]["down"]
        right = payload["facings"]["right"]
        self.assertEqual(down["gape_px"], 16)
        self.assertEqual(down["gape_bbox"], [12, 13, 19, 14])
        self.assertEqual(right["gape_px"], 8)
        self.assertEqual(right["gape_bbox"], [24, 13, 27, 14])

    def test_translated_eyes_at_the_banked_positions(self) -> None:
        payload = rm.masks_payload(DIRS)
        self.assertEqual(
            payload["facings"]["down"]["translated_eye_pixels"],
            [[12, 11], [12, 12], [13, 11], [13, 12],
             [18, 11], [18, 12], [19, 11], [19, 12]],
        )
        self.assertEqual(
            payload["facings"]["right"]["translated_eye_pixels"],
            [[22, 11], [22, 12], [23, 11], [23, 12]],
        )

    def test_gape_disjoint_from_eyes_and_feet(self) -> None:
        payload = rm.masks_payload(DIRS)
        for facing in rm.FACINGS:
            facts = payload["facings"][facing]
            gape = {tuple(c) for c in facts["gape_pixels"]}
            eyes = {tuple(c) for c in facts["translated_eye_pixels"]}
            feet = {tuple(c) for c in facts["feet_pixels"]}
            self.assertFalse(gape & eyes, facing)
            self.assertFalse(gape & feet, facing)
            self.assertTrue(all(y != rm.FEET_ROW for _, y in gape), facing)

    def test_gape_rows_covered_by_the_kr_split(self) -> None:
        payload = rm.masks_payload(DIRS)
        for facing in rm.FACINGS:
            rows = {y for _, y in
                    (tuple(c) for c in payload["facings"][facing]["gape_pixels"])}
            self.assertEqual(rows, set(rm.KR_SPLIT), facing)

    def test_masks_payload_deterministic(self) -> None:
        self.assertEqual(
            rm.masks_bytes(rm.masks_payload(DIRS)),
            rm.masks_bytes(rm.masks_payload(DIRS)),
        )

    def test_committed_masks_regenerate_byte_identically(self) -> None:
        self.assertTrue(rm.MASKS_PATH.is_file(), "gape-masks.json is bundled")
        self.assertEqual(
            rm.masks_bytes(rm.masks_payload(DIRS)), rm.MASKS_PATH.read_bytes()
        )


class RecolorMaps(unittest.TestCase):
    def test_ks_and_ko_paint_one_color_over_the_whole_mask(self) -> None:
        payload = masks_payload()
        for facing in rm.FACINGS:
            gape = {tuple(c) for c in payload["facings"][facing]["gape_pixels"]}
            ks = rm.recolor_map(payload, facing, "ks")
            ko = rm.recolor_map(payload, facing, "ko")
            self.assertEqual(set(ks), gape)
            self.assertEqual(set(ko), gape)
            self.assertEqual(set(ks.values()), {SHADE})
            self.assertEqual(set(ko.values()), {OUTLINE})

    def test_kr_splits_by_row(self) -> None:
        payload = masks_payload()
        for facing in rm.FACINGS:
            kr = rm.recolor_map(payload, facing, "kr")
            for (x, y), color in kr.items():
                self.assertEqual(color, SHADE if y == 13 else OUTLINE, (x, y))

    def test_unknown_lane_rejected(self) -> None:
        with self.assertRaises(rm.RemedyMaskError):
            rm.recolor_map(masks_payload(), "down", "kz")


class DiffDeclarationVerifier(unittest.TestCase):
    """Both directions on synthetic fixtures."""

    def setUp(self) -> None:
        raw = bytearray(CANVAS * CANVAS * 4)
        body = hex_rgb("#eb7828")
        accent = hex_rgb(ACCENT)
        for y in range(10, 20):
            for x in range(10, 20):
                offset = (y * CANVAS + x) * 4
                rgb = accent if y in (13, 14) and 12 <= x <= 15 else body
                raw[offset:offset + 4] = bytes((*rgb, 255))
        self.base = bytes(raw)
        self.declared = {
            (x, y): SHADE for y in (13, 14) for x in range(12, 16)
        }

    def test_accepts_a_correct_variant(self) -> None:
        variant = apply_recolor(self.base, self.declared)
        report = rmx.diff_report(self.base, variant, self.declared)
        self.assertTrue(report["alpha_identical"])
        self.assertTrue(report["diff_set_matches_declaration"])
        self.assertTrue(report["declared_colors_applied_within_ramp"])
        self.assertEqual(report["changed_px"], 8)

    def test_rejects_an_off_mask_recolor(self) -> None:
        variant = apply_recolor(
            self.base, {**self.declared, (11, 12): SHADE}
        )
        report = rmx.diff_report(self.base, variant, self.declared)
        self.assertFalse(report["diff_set_matches_declaration"])
        self.assertEqual(report["undeclared_changes"], [[11, 12]])

    def test_rejects_a_missing_declared_change(self) -> None:
        partial = dict(self.declared)
        del partial[(12, 13)]
        variant = apply_recolor(self.base, partial)
        report = rmx.diff_report(self.base, variant, self.declared)
        self.assertFalse(report["diff_set_matches_declaration"])
        self.assertEqual(report["missing_declared_changes"], [[12, 13]])

    def test_rejects_an_alpha_change(self) -> None:
        variant = bytearray(apply_recolor(self.base, self.declared))
        offset = (15 * CANVAS + 15) * 4
        variant[offset + 3] = 0
        report = rmx.diff_report(self.base, bytes(variant), self.declared)
        self.assertFalse(report["alpha_identical"])

    def test_rejects_an_out_of_ramp_color(self) -> None:
        rogue = {**{cell: SHADE for cell in self.declared}, (12, 13): "#123456"}
        variant = apply_recolor(self.base, rogue)
        report = rmx.diff_report(self.base, variant, self.declared)
        self.assertFalse(report["declared_colors_applied_within_ramp"])
        rogue_declared = dict(self.declared)
        rogue_declared[(12, 13)] = "#123456"
        variant2 = apply_recolor(self.base, rogue_declared)
        report2 = rmx.diff_report(self.base, variant2, rogue_declared)
        self.assertFalse(report2["declared_colors_applied_within_ramp"])


class EyeIntegrity(unittest.TestCase):
    """Both directions on the real banked bytes (in-memory recolors)."""

    def test_correct_recolors_pass_every_lane_and_facing(self) -> None:
        payload = masks_payload()
        for facing in rm.FACINGS:
            base = rm.load_banked_raw(DIRS, "k0", facing)
            for lane in rm.LANES:
                variant = apply_recolor(
                    base, rm.recolor_map(payload, facing, lane)
                )
                verdict = rmx.eye_integrity(payload, facing, variant)
                self.assertTrue(verdict["pass"], (facing, lane))

    def test_down_unmerge_is_proved(self) -> None:
        payload = masks_payload()
        base = rm.load_banked_raw(DIRS, "k0", "down")
        merged = rmx.eye_integrity(payload, "down", base)
        self.assertFalse(merged["pass"], "the incumbent merge must fail")
        variant = apply_recolor(base, rm.recolor_map(payload, "down", "ks"))
        verdict = rmx.eye_integrity(payload, "down", variant)
        self.assertTrue(verdict["eye_clusters_present_and_separate"])

    def test_half_recolored_gape_fails(self) -> None:
        payload = masks_payload()
        base = rm.load_banked_raw(DIRS, "k0", "down")
        partial = rm.recolor_map(payload, "down", "ks")
        del partial[(12, 13)]  # leftover accent pixel touching the left eye
        variant = apply_recolor(base, partial)
        self.assertFalse(rmx.eye_integrity(payload, "down", variant)["pass"])

    def test_touched_eye_pixel_fails(self) -> None:
        payload = masks_payload()
        base = rm.load_banked_raw(DIRS, "k0", "down")
        recolor = rm.recolor_map(payload, "down", "ks")
        recolor[(12, 11)] = SHADE  # an eye pixel — never in the declared set
        variant = apply_recolor(base, recolor)
        self.assertFalse(rmx.eye_integrity(payload, "down", variant)["pass"])


class VariantSpecs(unittest.TestCase):
    def test_specs_load_under_the_banked_contract_law(self) -> None:
        payload = masks_payload()
        for facing in rm.FACINGS:
            for lane in rm.LANES:
                spec = rm.variant_spec(DIRS, payload, facing, lane)
                self.assertEqual(len(spec["grid"]), CANVAS)
                self.assertEqual(
                    sorted(spec["palette"].values()),
                    sorted(rm.RAMP.values()),
                    (facing, lane),
                )

    def test_spec_grid_differs_from_banked_at_exactly_the_declared_set(self) -> None:
        payload = masks_payload()
        for facing in rm.FACINGS:
            base = rm.load_banked_raw(DIRS, "k0", facing)
            for lane in rm.LANES:
                spec = rm.variant_spec(DIRS, payload, facing, lane)
                declared = rm.recolor_map(payload, facing, lane)
                changed = set()
                for y in range(CANVAS):
                    for x in range(CANVAS):
                        offset = (y * CANVAS + x) * 4
                        opaque = base[offset + 3] == 255
                        char = spec["grid"][y][x]
                        self.assertEqual(
                            opaque, char != ".", (facing, lane, x, y)
                        )
                        if not opaque:
                            continue
                        spec_rgb = hex_rgb(spec["palette"][char])
                        base_rgb = tuple(base[offset:offset + 3])
                        if spec_rgb != base_rgb:
                            changed.add((x, y))
                            self.assertEqual(
                                spec_rgb, hex_rgb(declared[(x, y)]),
                                (facing, lane, x, y),
                            )
                self.assertEqual(changed, set(declared), (facing, lane))

    def test_spec_bytes_deterministic(self) -> None:
        payload = masks_payload()
        spec = rm.variant_spec(DIRS, payload, "down", "ks")
        self.assertEqual(rm.spec_bytes(spec), rm.spec_bytes(spec))

    def test_committed_specs_regenerate_byte_identically(self) -> None:
        if not rm.SPEC_DIR.is_dir():
            self.skipTest("variant specs not banked yet (pre-bank state)")
        payload = masks_payload()
        for asset_id, spec in sorted(rm.all_specs(DIRS, payload).items()):
            path = rm.SPEC_DIR / f"{asset_id}.json"
            self.assertTrue(path.is_file(), asset_id)
            self.assertEqual(rm.spec_bytes(spec), path.read_bytes(), asset_id)
            load_spec(path)  # the banked contract law accepts every spec


class BankedUntouchedGuards(unittest.TestCase):
    def test_banked_export_pins_verify(self) -> None:
        result = check_export_pins(ROOT / "exports")
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verified"], 26)

    def test_v13_and_v14_manifest_module_pins_match_live_files(self) -> None:
        """Pin-compare equivalent of both banked --checks (rationale bar 3)."""
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
        for rel, pinned in sorted(pins.items()):
            live = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(live, pinned, f"pinned module drifted: {rel}")

    def test_no_new_calibration_export_directory(self) -> None:
        self.assertEqual(rmx.check_calibration_dirs(ROOT), [])


class CommittedBundleGuards(unittest.TestCase):
    """Post-bank guards; skip cleanly before the release exists."""

    @classmethod
    def setUpClass(cls) -> None:
        if not rmx.RELEASE_PATH.is_file():
            raise unittest.SkipTest("remedy-v15 release not banked yet")
        cls.release = json.loads(rmx.RELEASE_PATH.read_text(encoding="utf-8"))

    def test_release_covers_exactly_the_six_variants(self) -> None:
        self.assertEqual(
            [e["asset_id"] for e in self.release["exports"]],
            rmx.variant_ids(),
        )
        self.assertEqual(rmx.check_release(ROOT), [])

    def test_alpha_identity_on_the_committed_exports(self) -> None:
        for facing in rm.FACINGS:
            base = rm.load_banked_raw(DIRS, "k0", facing)
            for lane in rm.LANES:
                variant = rmx.load_variant_raw(facing, lane)
                self.assertEqual(
                    rmx.alpha_plane(base), rmx.alpha_plane(variant),
                    (facing, lane),
                )

    def test_machine_bars_all_pass_in_the_committed_report(self) -> None:
        if not rmx.REPORT_PATH.is_file():
            self.skipTest("remedy report not banked yet")
        report = json.loads(rmx.REPORT_PATH.read_text(encoding="utf-8"))
        bars = report["machine_bars"]
        self.assertEqual(bars["variant_count"], 6)
        for bar, value in bars.items():
            if bar != "variant_count":
                self.assertIs(value, True, bar)

    def test_artifact_filenames_and_manifest_hashes(self) -> None:
        if not rmx.MANIFEST_PATH.is_file():
            self.skipTest("remedy manifest not banked yet")
        manifest = json.loads(rmx.MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["provenance"]["class"], "SYNTHETIC")
        for name, digest in manifest["artifacts"].items():
            path = rmx.REVIEW_DIR / name
            self.assertTrue(path.is_file(), name)
            if name not in ("remedy-report.json",):
                self.assertTrue(name.startswith("synthetic-remedy-"), name)
            live = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(live, digest, name)

    def test_expected_artifact_matrix(self) -> None:
        names = set(rmx.artifact_names())
        self.assertEqual(len(names), 4 + 24)
        for facing in rm.FACINGS:
            for zone in ("z1", "z2"):
                self.assertIn(
                    f"synthetic-remedy-strip-{facing}-{zone}-8x.png", names
                )


class ArtifactDeterminism(unittest.TestCase):
    """One in-process double-build (full byte-regen lives in --check)."""

    @classmethod
    def setUpClass(cls) -> None:
        if not rmx.RELEASE_PATH.is_file():
            raise unittest.SkipTest("remedy-v15 release not banked yet")
        cls.sprites = rmx.load_sprites(DIRS)

    def test_strip_double_build(self) -> None:
        first = rmx.build_strip(REFERENCE, self.sprites, "down", "zone_1")
        second = rmx.build_strip(REFERENCE, self.sprites, "down", "zone_1")
        self.assertEqual(first.encode(), second.encode())

    def test_apng_frame_count_and_deterministic_encode(self) -> None:
        frames = rmx.build_apng_frames(
            REFERENCE, self.sprites, "down", "ks", 4, "REAL 1 60"
        )
        ticks = len(pim.audit_stream(REFERENCE, "down"))
        self.assertEqual(len(frames), ticks)


if __name__ == "__main__":
    unittest.main()
