#!/usr/bin/env python3
"""Tests for the v17 exports-tree guard + readiness-register shape.

Guard tests prove both directions on synthetic fixture trees (valid tree
passes; planted stray dir / stray top-level file / missing release.json
each fail), prove the whitelist is derived from the banked exporter
constants (no literal duplication), and assert the LIVE tree clean — the
suite is the guard's continuous enforcement (no hook rewiring).

Register-shape tests activate post-bank (skip-guarded before
docs/integration-readiness.md exists) and enforce the pre-registered
status-only law: six contract-condition rows, each with a status and a
carrier citation; the banned-verb scan; watch items; the advisory-class
header; the verbatim upstream ruling quotes; no lore-class words.
"""

from __future__ import annotations

import contextlib
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import exports_guard as xg  # noqa: E402
import ingest_audio  # noqa: E402
import remedy_masks  # noqa: E402
import seam_metrics  # noqa: E402


def build_valid_tree(base: Path) -> Path:
    """A synthetic exports/ tree satisfying the guard's tree law."""
    exports = base / "exports"
    exports.mkdir()
    (exports / ".gitkeep").write_bytes(b"")
    for release_id in xg.release_whitelist():
        release_dir = exports / release_id
        release_dir.mkdir()
        (release_dir / "release.json").write_text("{}", encoding="utf-8")
    return exports


class ExportsTreeGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="exports-guard-")
        self.exports = build_valid_tree(Path(self._tmp))
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

    def test_valid_synthetic_tree_passes(self) -> None:
        self.assertEqual(xg.check_exports_tree(self.exports), [])

    def test_planted_stray_directory_fails(self) -> None:
        (self.exports / "rogue-v99").mkdir()
        self.assertEqual(
            xg.check_exports_tree(self.exports), ["stray-dir: rogue-v99"]
        )

    def test_planted_top_level_file_fails(self) -> None:
        (self.exports / "stray.png").write_bytes(b"not a release")
        self.assertEqual(
            xg.check_exports_tree(self.exports), ["stray-file: stray.png"]
        )

    def test_missing_release_manifest_fails(self) -> None:
        victim = remedy_masks.RELEASE_ID
        (self.exports / victim / "release.json").unlink()
        self.assertEqual(
            xg.check_exports_tree(self.exports),
            [f"missing-release-manifest: {victim}"],
        )

    def test_whitelisted_name_present_as_plain_file_fails(self) -> None:
        victim = ingest_audio.RELEASE_ID
        shutil.rmtree(self.exports / victim)
        (self.exports / victim).write_bytes(b"not a directory")
        self.assertEqual(
            xg.check_exports_tree(self.exports), [f"stray-file: {victim}"]
        )

    def test_missing_exports_root_is_a_typed_failure(self) -> None:
        missing = Path(self._tmp) / "nope"
        failures = xg.check_exports_tree(missing)
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0].startswith("missing-exports-root: "))

    def test_cli_reports_failures_with_exit_1(self) -> None:
        (self.exports / "rogue-v99").mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            exit_code = xg.main(["--exports-root", str(self.exports)])
        self.assertEqual(exit_code, 1)
        self.assertIn("stray-dir: rogue-v99", captured.getvalue())


class WhitelistDerivation(unittest.TestCase):
    def test_whitelist_equals_the_banked_constants(self) -> None:
        self.assertEqual(
            xg.release_whitelist(),
            frozenset(seam_metrics.RELEASE_IDS)
            | {remedy_masks.RELEASE_ID, ingest_audio.RELEASE_ID},
        )

    def test_no_release_id_duplicated_as_a_literal(self) -> None:
        source = Path(xg.__file__).read_text(encoding="utf-8")
        for release_id in xg.release_whitelist():
            self.assertNotIn(release_id, source)

    def test_top_level_allowance_is_exactly_the_hygiene_file(self) -> None:
        self.assertEqual(xg.ALLOWED_TOP_FILES, frozenset({".gitkeep"}))


class LiveTreeClean(unittest.TestCase):
    """The suite is the guard's continuous enforcement on the live tree."""

    def test_live_tree_shape_clean(self) -> None:
        self.assertEqual(xg.check_exports_tree(xg.EXPORTS_ROOT), [])

    def test_live_check_cli_exits_0(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            exit_code = xg.main(["--check"])
        self.assertEqual(exit_code, 0)
        self.assertIn("exports guard OK", captured.getvalue())


class ReadinessRegisterShape(unittest.TestCase):
    """Post-bank shape law for docs/integration-readiness.md."""

    REGISTER = ROOT / "docs" / "integration-readiness.md"

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.REGISTER.is_file():
            raise unittest.SkipTest("readiness register not banked yet")
        cls.text = cls.REGISTER.read_text(encoding="utf-8")

    def condition_blocks(self) -> list[str]:
        parts = re.split(r"^### ", self.text, flags=re.MULTILINE)
        return [part for part in parts if re.match(r"C\d ", part)]

    def test_all_six_contract_conditions_present_once(self) -> None:
        headings = re.findall(r"^### C(\d) ", self.text, flags=re.MULTILINE)
        self.assertEqual(headings, ["1", "2", "3", "4", "5", "6"])

    def test_every_condition_row_carries_status_and_carrier(self) -> None:
        blocks = self.condition_blocks()
        self.assertEqual(len(blocks), 6)
        for block in blocks:
            self.assertIn("**Status:**", block)
            self.assertIn("**Carrier:**", block)

    def test_every_carrier_cites_a_real_location_class(self) -> None:
        citation = re.compile(
            r"(docs/|reviews/|manifests/|exports/|tools/|done/from-game-two-)"
        )
        for block in self.condition_blocks():
            carrier_lines = [
                line
                for line in block.splitlines()
                if line.strip().startswith("**Carrier:**")
            ]
            self.assertEqual(len(carrier_lines), 1, block[:60])
            self.assertRegex(carrier_lines[0], citation)

    def test_banned_verb_scan(self) -> None:
        for pattern in (
            r"\bwill\b",
            r"\bschedul\w*\b",
            r"\bpropos\w*\b",
            r"\bshould\s+integrate\b",
        ):
            self.assertIsNone(
                re.search(pattern, self.text, flags=re.IGNORECASE), pattern
            )

    def test_no_lore_class_words(self) -> None:
        for pattern in (r"\blore\b", r"\bstory\b", r"\bnarrative\b"):
            self.assertIsNone(
                re.search(pattern, self.text, flags=re.IGNORECASE), pattern
            )

    def test_advisory_class_header_present(self) -> None:
        head = self.text[:1200]
        self.assertIn("advisory", head)
        self.assertIn("the hub decides", head)
        self.assertIn("parking-lot", head)

    def test_condition_kernels_quote_the_contract(self) -> None:
        for kernel in (
            "fun verdict",
            "least bad",
            "clean checkout",
            "provenance and rights",
            "native scale",
            "integration design",
        ):
            self.assertIn(kernel, self.text)

    def test_watch_items_present(self) -> None:
        for kernel in (
            "shade double-duty",
            "protocol-vs",
            "at-speed",
            "DEF-3",
        ):
            self.assertIn(kernel, self.text)

    def test_upstream_rulings_quoted_verbatim(self) -> None:
        for quote in (
            "I agree with you, defer, maybe revisit later if needed",
            "yes please!",
            "v17 and v18 are both CLOSED",
            "Approved, proceed",
            "No asset action until the game pins its new frame",
        ):
            self.assertIn(quote, self.text)

    def test_non_claims_section_present(self) -> None:
        self.assertIn("## Non-claims", self.text)
        self.assertIn("no integration ask", self.text)

    def test_mechanical_affordance_row_present(self) -> None:
        self.assertIn("stage_ks_attack_dir", self.text)
        self.assertIn("adoption_demo", self.text)


if __name__ == "__main__":
    unittest.main()
