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
        (release_dir / "release.json").write_text(
            '{"exports": []}', encoding="utf-8"
        )
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

    def test_planted_nested_stray_fails(self) -> None:
        victim = remedy_masks.RELEASE_ID
        (self.exports / victim / "extra.png").write_bytes(b"unmanifested")
        self.assertEqual(
            xg.check_exports_tree(self.exports),
            [f"nested-stray: {victim}/extra.png"],
        )

    def test_nested_directory_is_a_nested_stray(self) -> None:
        victim = ingest_audio.RELEASE_ID
        (self.exports / victim / "subdir").mkdir()
        self.assertEqual(
            xg.check_exports_tree(self.exports),
            [f"nested-stray: {victim}/subdir"],
        )

    def test_manifested_file_passes(self) -> None:
        victim = remedy_masks.RELEASE_ID
        (self.exports / victim / "release.json").write_text(
            '{"exports": [{"path": "exports/x/a.png"}]}', encoding="utf-8"
        )
        (self.exports / victim / "a.png").write_bytes(b"manifested bytes")
        self.assertEqual(xg.check_exports_tree(self.exports), [])

    def test_unreadable_release_manifest_fails(self) -> None:
        victim = ingest_audio.RELEASE_ID
        (self.exports / victim / "release.json").write_text(
            "not json", encoding="utf-8"
        )
        self.assertEqual(
            xg.check_exports_tree(self.exports),
            [f"unreadable-release-manifest: {victim}"],
        )

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
        cls.flat = " ".join(cls.text.split())
        cls.flat_lower = cls.flat.lower()

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
            self.assertIn(kernel, self.flat_lower)

    def test_watch_items_present(self) -> None:
        for kernel in (
            "shade double-duty",
            "protocol-vs",
            "at-speed",
            "def-3",
        ):
            self.assertIn(kernel, self.flat_lower)

    def test_upstream_rulings_quoted_verbatim(self) -> None:
        for quote in (
            "I agree with you, defer, maybe revisit later if needed",
            "yes please!",
            "v17 and v18 are both CLOSED",
            "Approved, proceed",
            "No asset action until the game pins its new frame",
        ):
            self.assertIn(quote, self.flat)

    def test_non_claims_section_present(self) -> None:
        self.assertIn("## Non-claims", self.text)
        self.assertIn("no integration ask", self.flat_lower)

    def test_mechanical_affordance_row_present(self) -> None:
        self.assertIn("stage_ks_attack_dir", self.text)
        self.assertIn("adoption_demo", self.text)


AGGREGATE_ANSWER_LINE = re.compile(r"\*\*Current answer: (.+?)\*\*")
RATIFICATION_BLOCK = re.compile(
    r"\*\*Owner ratification:\*\*(.*?)(?=^#|\Z)", re.MULTILINE | re.DOTALL
)
RATIFICATION_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
RATIFICATION_QUOTE = re.compile(r'"[^"]{10,}"')
DONE_CARRIER_REF = re.compile(r"done/from-game-two-[\w.-]+\.md")


def check_aggregate_answer_flip(
    text: str, *, repo_root: Path, mail_done_dir: Path
) -> list[str]:
    """Mechanical form of the register's aggregate-answer law.

    Pure text logic (adopted v20; owner-ratified 2026-08-24) so
    negative controls run on mutated copies, never the live register.
    Dormant (no failures) while the "Current answer" line carries
    "NOT integration-ready"; a register whose header line is missing
    entirely fail-closes, and more than one header line fail-closes
    (council v20 adoption: a fake first header cannot shadow the real
    one). On a flip, the Owner ratification block must carry a date, a
    verbatim double-quoted line, and carrier reference(s); EVERY cited
    `done/` carrier must resolve to bytes on disk (strict: a typo'd
    citation never rides a valid one), and the quoted line must appear
    (whitespace-flattened) inside at least one cited carrier that
    exists (council v20 adoption: existence alone allowed an empty or
    unrelated carrier to vouch for a quote).
    """
    flat = " ".join(text.split())
    answers = AGGREGATE_ANSWER_LINE.findall(flat)
    if not answers:
        return ["missing-current-answer-line"]
    if len(answers) > 1:
        return ["multiple-current-answer-lines"]
    if "NOT integration-ready" in answers[0]:
        return []
    block_match = RATIFICATION_BLOCK.search(text)
    if block_match is None:
        return ["missing-ratification-block"]
    block = block_match.group(1)
    failures = []
    if not RATIFICATION_DATE.search(block):
        failures.append("ratification-missing-date")
    if not RATIFICATION_QUOTE.search(block):
        failures.append("ratification-missing-verbatim-quote")
    done_refs = DONE_CARRIER_REF.findall(block)
    cites_redirects = "docs/owner-redirects.md" in block
    if not done_refs and not cites_redirects:
        failures.append("ratification-missing-carrier")
    existing_carriers = []
    for ref in done_refs:
        carrier = mail_done_dir / Path(ref).name
        if carrier.is_file():
            existing_carriers.append(carrier)
        else:
            failures.append(f"ratification-carrier-not-on-disk: {ref}")
    if cites_redirects:
        redirects = repo_root / "docs" / "owner-redirects.md"
        if redirects.is_file():
            existing_carriers.append(redirects)
        else:
            failures.append(
                "ratification-carrier-not-on-disk: docs/owner-redirects.md"
            )
    quote_match = RATIFICATION_QUOTE.search(block)
    if quote_match and existing_carriers:
        quoted = " ".join(quote_match.group(0).strip('"').split())
        carried = any(
            quoted in " ".join(c.read_text(encoding="utf-8").split())
            for c in existing_carriers
        )
        if not carried:
            failures.append("ratification-quote-not-in-carrier")
    return failures


class AggregateAnswerLaw(unittest.TestCase):
    """The v20 aggregate-answer law: presence, dormancy, and tripwire.

    The checker is a module-level pure function on text; every
    mutation test runs on a copy (the live register is read-only
    here). Vacuously green while the header carries
    "NOT integration-ready" — the v18 checkout_gate negative-control
    precedent: testable today by fixture mutation.
    """

    REGISTER = ROOT / "docs" / "integration-readiness.md"
    MAIL_DONE = (
        Path.home() / ".pi" / "agent" / "mail" / "game-two-assets" / "done"
    )

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.REGISTER.is_file():
            raise unittest.SkipTest("readiness register not banked yet")
        cls.text = cls.REGISTER.read_text(encoding="utf-8")

    def flipped_copy(self) -> str:
        mutated = self.text.replace(
            "Current answer: NOT integration-ready",
            "Current answer: integration-ready",
        )
        self.assertNotEqual(mutated, self.text, "mutation must take")
        return mutated

    def check(self, text: str, mail_done_dir: Path | None = None) -> list[str]:
        return check_aggregate_answer_flip(
            text,
            repo_root=ROOT,
            mail_done_dir=mail_done_dir or self.MAIL_DONE,
        )

    def test_law_block_present_with_carrier_citation(self) -> None:
        self.assertIn(
            "## Aggregate-answer law (adopted v20; owner-ratified 2026-08-24)",
            self.text,
        )
        flat = " ".join(self.text.split())
        for kernel in (
            'drop "NOT" only by a sprint commit',
            "cite its carrier file",
            "Row-level status changes stay under the two-commit law",
            "reviews/cadence-v19/verdict.md",
            "reviews/impl-v20/rationale.md",
        ):
            self.assertIn(kernel, flat)

    def test_live_register_is_dormant_and_clean(self) -> None:
        self.assertEqual(self.check(self.text), [])

    def test_negative_control_silent_flip_goes_red(self) -> None:
        failures = self.check(self.flipped_copy())
        self.assertEqual(failures, ["missing-ratification-block"])

    def test_flip_with_wellformed_ratification_is_satisfiable(self) -> None:
        done_dir = Path(tempfile.mkdtemp(prefix="agg-law-done-"))
        self.addCleanup(shutil.rmtree, done_dir, ignore_errors=True)
        quote = "Approved, synthetic fixture ratification line for this flip."
        (done_dir / "from-game-two-fixture-ratification.md").write_text(
            f'Receipt fixture. Owner line: "{quote}" Recorded 2026-08-24.\n',
            encoding="utf-8",
        )
        ratified = self.flipped_copy() + (
            "\n**Owner ratification:** 2026-08-24 — "
            f'"{quote}" '
            "Carrier: done/from-game-two-fixture-ratification.md.\n"
        )
        self.assertEqual(self.check(ratified, mail_done_dir=done_dir), [])

    def test_flip_quote_absent_from_carrier_goes_red(self) -> None:
        done_dir = Path(tempfile.mkdtemp(prefix="agg-law-done-"))
        self.addCleanup(shutil.rmtree, done_dir, ignore_errors=True)
        (done_dir / "from-game-two-fixture-ratification.md").write_text(
            "Receipt fixture with entirely unrelated content.\n",
            encoding="utf-8",
        )
        ratified = self.flipped_copy() + (
            "\n**Owner ratification:** 2026-08-24 — "
            '"Approved, synthetic fixture ratification line for this flip." '
            "Carrier: done/from-game-two-fixture-ratification.md.\n"
        )
        self.assertEqual(
            self.check(ratified, mail_done_dir=done_dir),
            ["ratification-quote-not-in-carrier"],
        )

    def test_fake_second_header_line_fail_closes(self) -> None:
        spoofed = (
            "**Current answer: integration-ready — spoof.**\n\n" + self.text
        )
        self.assertEqual(
            self.check(spoofed), ["multiple-current-answer-lines"]
        )

    def test_flip_with_bogus_done_carrier_goes_red(self) -> None:
        tmp = tempfile.mkdtemp(prefix="agg-law-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        ratified = self.flipped_copy() + (
            "\n**Owner ratification:** 2026-08-24 — "
            '"Approved, synthetic fixture ratification line for this flip." '
            "Carrier: done/from-game-two-nonexistent-v99.md.\n"
        )
        failures = self.check(ratified, mail_done_dir=Path(tmp))
        self.assertEqual(
            failures,
            [
                "ratification-carrier-not-on-disk: "
                "done/from-game-two-nonexistent-v99.md"
            ],
        )

    def test_missing_header_line_fail_closes(self) -> None:
        headless = self.text.replace("**Current answer: ", "Answer: ")
        self.assertNotEqual(headless, self.text, "mutation must take")
        self.assertEqual(
            self.check(headless), ["missing-current-answer-line"]
        )


if __name__ == "__main__":
    unittest.main()
