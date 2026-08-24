#!/usr/bin/env python3
"""Pre-commit fast-tier test gate: every test module except the SLOW list.

The stage partition (v19 decision brief 1, option iii; owner-ratified
2026-08-24; pre-registered in reviews/impl-v20/rationale.md): the
pre-commit hook proves the fast tier — ALL tests/test_*.py MINUS the
nine determinism-re-proof modules pinned below — while the pre-push
gate keeps running the byte-identical full suite under coverage
(bin/full_gate.py). New test modules default INTO the fast tier; there
is no allow-list to rot.

Failure contract (all typed, all exit nonzero; the critical line
prints last so a 30-line output tail still carries the verdict):
  stale-slow-entry   a SLOW entry is missing on disk (list rot)
  empty-fast-tier    derivation found no fast modules
  test-failure       a module's unittest run exited nonzero
  zero-tests         a module ran but collected nothing
  unparsed-output    a green run whose test count could not be read
  budget-exceeded    fast-tier wall-clock crossed the assertion

This file lives in bin/, not tools/: .coveragerc measures source=tools
with a hard fail_under floor at push, and the gate runner must never
count against the floor it is adjacent to.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]

# The nine pure determinism-re-proof modules (reviews/cadence-v19/
# measurements.json: 2963s of the 3149s module sum). Pinned by
# tests/test_fast_gate.py against the pre-registered split; edits here
# go red without a matching fixture-test edit.
SLOW_MODULES = (
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

# Wall-clock assertion for the whole fast tier. Reasoning pinned in
# reviews/impl-v20/rationale.md: measured tier 185.85s, session noise
# +/-3-6%, logic growth ~5-15s/sprint; a smuggled determinism-class
# suite (~500s+) trips this, ambient noise never plausibly does.
FAST_TIER_BUDGET_S = 600.0

OUTPUT_TAIL_LINES = 30
RAN_LINE = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)


def derive_fast_modules(
    tests_dir: Path, slow: Sequence[str]
) -> tuple[list[str], list[str]]:
    """Return (fast module stems, typed derivation failures)."""
    failures = [
        f"stale-slow-entry: {tests_dir / (name + '.py')}"
        for name in slow
        if not (tests_dir / (name + ".py")).is_file()
    ]
    slow_set = set(slow)
    fast = sorted(
        path.stem
        for path in tests_dir.glob("test_*.py")
        if path.stem not in slow_set
    )
    if not fast:
        failures.append("empty-fast-tier")
    return fast, failures


def check_budget(elapsed_s: float, budget_s: float) -> list[str]:
    """Typed failure when the tier's wall-clock crosses the assertion."""
    if elapsed_s > budget_s:
        return [f"budget-exceeded: fast tier {elapsed_s:.1f}s > budget {budget_s:.0f}s"]
    return []


def run_module(
    module: str, tests_dir: Path, python: str
) -> tuple[int, int | None, str]:
    """Run one module via unittest discover; return (rc, tests_ran, output)."""
    proc = subprocess.run(
        [
            python,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(tests_dir),
            "-p",
            f"{module}.py",
            "-v",
        ],
        cwd=ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    match = RAN_LINE.search(output)
    tests_ran = int(match.group(1)) if match else None
    return proc.returncode, tests_ran, output


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fast-tier test gate (fixture flags exist for tests;"
        " the pinned swarmforge.toml invocation passes none)."
    )
    parser.add_argument("--tests-dir", type=Path, default=ROOT / "tests")
    parser.add_argument("--budget", type=float, default=FAST_TIER_BUDGET_S)
    parser.add_argument(
        "--slow",
        action="append",
        default=None,
        help="Override a SLOW-list entry (repeatable; fixture tests only).",
    )
    args = parser.parse_args(argv)
    slow = tuple(args.slow) if args.slow is not None else SLOW_MODULES

    fast, failures = derive_fast_modules(args.tests_dir, slow)
    if failures:
        for line in failures:
            print(line)
        print(f"fast gate FAILED: {len(failures)} failure(s)")
        return 1

    total_tests = 0
    started = time.monotonic()
    for module in fast:
        rc, tests_ran, output = run_module(module, args.tests_dir, sys.executable)
        if rc != 0:
            tail = "\n".join(output.splitlines()[-OUTPUT_TAIL_LINES:])
            print(f"--- {module} output tail ---")
            print(tail)
            failures.append(f"test-failure: {module} (rc={rc})")
        elif tests_ran is None:
            failures.append(f"unparsed-output: {module}")
        elif tests_ran == 0:
            failures.append(f"zero-tests: {module} (ran 0 tests)")
        else:
            total_tests += tests_ran
    elapsed = time.monotonic() - started
    failures.extend(check_budget(elapsed, args.budget))

    if failures:
        for line in failures:
            print(line)
        print(f"fast gate FAILED: {len(failures)} failure(s)")
        return 1
    print(
        f"fast gate OK: {len(fast)} module(s), {total_tests} test(s),"
        f" {elapsed:.1f}s (budget {args.budget:.0f}s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
