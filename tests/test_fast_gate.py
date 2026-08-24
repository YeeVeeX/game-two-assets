#!/usr/bin/env python3
"""Fixture tests for bin/fast_gate.py (the pre-commit fast-tier gate).

Every behavior is proven on synthetic temp trees — the real fast tier
is never run inside a test (the activation commit's own hook is the
live proof; reviews/impl-v20/rationale.md). The SLOW-list pin test
carries the pre-registered 12/9 split as literal ground truth so a
unilateral edit to fast_gate.SLOW_MODULES goes red here.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))

import fast_gate  # noqa: E402

PASSING_MODULE = (
    "import unittest\n"
    "class Probe(unittest.TestCase):\n"
    "    def test_ok(self):\n"
    "        self.assertTrue(True)\n"
)
FAILING_MODULE = (
    "import unittest\n"
    "class Probe(unittest.TestCase):\n"
    "    def test_boom(self):\n"
    "        self.fail('synthetic failure')\n"
)
HOLLOW_MODULE = "import unittest\n"

# The pre-registered SLOW list (reviews/impl-v20/rationale.md; the
# nine determinism-re-proof modules from reviews/cadence-v19/
# measurements.json). Duplicated here on purpose: the banked split is
# test-carried ground truth, not a mirror of the implementation.
PREREGISTERED_SLOW = (
    "test_corner_tools",
    "test_cross_seam_tools",
    "test_recovery_tools",
    "test_rise_tools",
    "test_seam_tools",
    "test_timeline_tools",
    "test_track_recompose",
    "test_transition_tools",
    "test_turn_tools",
)


def run_main(argv: list[str]) -> tuple[int, str]:
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        exit_code = fast_gate.main(argv)
    return exit_code, captured.getvalue()


class FixtureTree(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="fast-gate-")
        self.tests_dir = Path(self._tmp)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

    def write_module(self, name: str, body: str) -> None:
        (self.tests_dir / f"{name}.py").write_text(body, encoding="utf-8")


class FastListDerivation(FixtureTree):
    def test_fast_list_is_all_minus_slow(self) -> None:
        for name in ("test_a", "test_b", "test_slowx"):
            self.write_module(name, PASSING_MODULE)
        fast, failures = fast_gate.derive_fast_modules(
            self.tests_dir, ("test_slowx",)
        )
        self.assertEqual(failures, [])
        self.assertEqual(fast, ["test_a", "test_b"])

    def test_new_module_defaults_into_fast_tier(self) -> None:
        self.write_module("test_slowx", PASSING_MODULE)
        self.write_module("test_newcomer", PASSING_MODULE)
        fast, failures = fast_gate.derive_fast_modules(
            self.tests_dir, ("test_slowx",)
        )
        self.assertEqual(failures, [])
        self.assertIn("test_newcomer", fast)

    def test_stale_slow_entry_is_a_typed_failure(self) -> None:
        self.write_module("test_a", PASSING_MODULE)
        fast, failures = fast_gate.derive_fast_modules(
            self.tests_dir, ("test_gone",)
        )
        self.assertEqual(fast, ["test_a"])
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0].startswith("stale-slow-entry: "))
        self.assertIn("test_gone.py", failures[0])

    def test_empty_fast_tier_is_a_typed_failure(self) -> None:
        self.write_module("test_slowx", PASSING_MODULE)
        fast, failures = fast_gate.derive_fast_modules(
            self.tests_dir, ("test_slowx",)
        )
        self.assertEqual(fast, [])
        self.assertIn("empty-fast-tier", failures)


class SlowListPin(unittest.TestCase):
    def test_slow_list_matches_the_preregistered_split(self) -> None:
        self.assertEqual(fast_gate.SLOW_MODULES, PREREGISTERED_SLOW)

    def test_every_slow_entry_exists_on_disk(self) -> None:
        fast, failures = fast_gate.derive_fast_modules(
            ROOT / "tests", fast_gate.SLOW_MODULES
        )
        self.assertEqual(failures, [])

    def test_live_partition_covers_the_whole_glob(self) -> None:
        tests_dir = ROOT / "tests"
        fast, _ = fast_gate.derive_fast_modules(
            tests_dir, fast_gate.SLOW_MODULES
        )
        everything = sorted(p.stem for p in tests_dir.glob("test_*.py"))
        self.assertEqual(
            sorted(fast + list(fast_gate.SLOW_MODULES)), everything
        )

    def test_budget_matches_the_preregistered_assertion(self) -> None:
        self.assertEqual(fast_gate.FAST_TIER_BUDGET_S, 600.0)


class BudgetAssertion(unittest.TestCase):
    def test_within_budget_is_clean(self) -> None:
        self.assertEqual(fast_gate.check_budget(599.9, 600.0), [])

    def test_exceeding_budget_is_a_typed_failure(self) -> None:
        failures = fast_gate.check_budget(601.2, 600.0)
        self.assertEqual(len(failures), 1)
        self.assertEqual(
            failures[0], "budget-exceeded: fast tier 601.2s > budget 600s"
        )


class MainExitCodes(FixtureTree):
    def test_passing_tier_exits_0_with_the_ok_line(self) -> None:
        self.write_module("test_pass1", PASSING_MODULE)
        self.write_module("test_pass2", PASSING_MODULE)
        code, out = run_main(
            ["--tests-dir", str(self.tests_dir), "--slow", "test_pass1"]
        )
        self.assertEqual(code, 0)
        self.assertIn("fast gate OK: 1 module(s), 1 test(s)", out)

    def test_failing_test_exits_nonzero_with_typed_line(self) -> None:
        self.write_module("test_boom", FAILING_MODULE)
        self.write_module("test_slowx", PASSING_MODULE)
        code, out = run_main(
            ["--tests-dir", str(self.tests_dir), "--slow", "test_slowx"]
        )
        self.assertEqual(code, 1)
        self.assertIn("test-failure: test_boom (rc=1)", out)
        self.assertIn("synthetic failure", out)
        self.assertTrue(
            out.rstrip().endswith("fast gate FAILED: 1 failure(s)")
        )

    def test_hollow_module_exits_nonzero(self) -> None:
        # Python 3.12 unittest exits 5 ("NO TESTS RAN") on a module
        # with no tests; the gate types it as a test-failure. The
        # zero-tests guard (rc==0 path) is covered at function level.
        self.write_module("test_hollow", HOLLOW_MODULE)
        self.write_module("test_slowx", PASSING_MODULE)
        code, out = run_main(
            ["--tests-dir", str(self.tests_dir), "--slow", "test_slowx"]
        )
        self.assertEqual(code, 1)
        self.assertIn("test-failure: test_hollow (rc=5)", out)

    def test_budget_exceed_exits_nonzero_on_synthetic_input(self) -> None:
        self.write_module("test_pass1", PASSING_MODULE)
        self.write_module("test_slowx", PASSING_MODULE)
        code, out = run_main(
            [
                "--tests-dir",
                str(self.tests_dir),
                "--slow",
                "test_slowx",
                "--budget",
                "0.000001",
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("budget-exceeded: fast tier ", out)
        self.assertTrue(
            out.rstrip().endswith("fast gate FAILED: 1 failure(s)")
        )

    def test_stale_slow_entry_exits_nonzero_before_running(self) -> None:
        self.write_module("test_pass1", PASSING_MODULE)
        code, out = run_main(
            ["--tests-dir", str(self.tests_dir), "--slow", "test_gone"]
        )
        self.assertEqual(code, 1)
        self.assertIn("stale-slow-entry: ", out)
        self.assertTrue(
            out.rstrip().endswith("fast gate FAILED: 1 failure(s)")
        )

    def test_critical_line_is_last_on_failure(self) -> None:
        self.write_module("test_boom", FAILING_MODULE)
        self.write_module("test_slowx", PASSING_MODULE)
        code, out = run_main(
            ["--tests-dir", str(self.tests_dir), "--slow", "test_slowx"]
        )
        self.assertEqual(code, 1)
        lines = [line for line in out.splitlines() if line.strip()]
        self.assertTrue(lines[-1].startswith("fast gate FAILED: "))


class ZeroTestsGuard(unittest.TestCase):
    """Function-level cover for the defensive rc==0 zero-test path."""

    def test_ran_line_parses_singular_and_plural(self) -> None:
        self.assertEqual(
            fast_gate.RAN_LINE.search("Ran 1 test in 0.000s").group(1), "1"
        )
        self.assertEqual(
            fast_gate.RAN_LINE.search("Ran 27 tests in 0.4s").group(1), "27"
        )
        self.assertIsNone(fast_gate.RAN_LINE.search("no summary here"))


if __name__ == "__main__":
    unittest.main()
