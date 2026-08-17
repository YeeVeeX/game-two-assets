#!/usr/bin/env python3
"""Run tests under branch coverage, then enforce the configured threshold."""

from __future__ import annotations

import subprocess
import sys


def run(*arguments: str) -> int:
    return subprocess.run([sys.executable, *arguments], check=False).returncode


def main() -> int:
    commands = (
        ("-m", "coverage", "erase"),
        ("-m", "coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-v"),
        ("-m", "coverage", "report"),
    )
    for command in commands:
        status = run(*command)
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
