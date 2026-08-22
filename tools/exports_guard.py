#!/usr/bin/env python3
"""Global exports-tree guard (v17; closes the v15 council Q3 residue).

The v15 selection verdict carried a toolchain observation two sprints:
"the standing toolchain has no *global* stray-file guard for exports/
outside ``calibration-*``" (the v15 selection verdict, council appendix
Q3).
This module is that guard. It never builds anything and never touches a
banked module: it reads the tree shape directly under ``exports/`` and
returns typed failures.

Tree law (``check_exports_tree``):

- (a) every directory directly under ``exports/`` must be a whitelisted
  release directory, else ``stray-dir: <name>``;
- (b) every top-level file must be in the named allowance
  (``ALLOWED_TOP_FILES`` — the tracked hygiene file that keeps the tree
  present in a fresh clone), else ``stray-file: <name>``;
- (c) every whitelisted directory PRESENT on disk must carry a
  ``release.json``, else ``missing-release-manifest: <id>``. Existence
  only, by design: content pinning stays the job of
  ``seam_metrics.check_export_pins`` and the asset gate. A whitelisted id
  absent from disk is not a tree failure (the pins check owns
  calibration completeness).

Whitelist derivation law: the whitelist is DERIVED at call time from the
banked exporter release-id constants — ``seam_metrics.RELEASE_IDS``,
``remedy_masks.RELEASE_ID``, ``ingest_audio.RELEASE_ID`` — and is never
duplicated as literals in this module (test-enforced in
tests/test_exports_guard.py).

EXTENSION LAW: a future release extends the whitelist in ITS OWN
pre-registration commit-1, by adding its exporter module's release-id
constant to ``release_whitelist()`` — never by hardcoding an id here,
never retroactively. Until that commit exists, this guard going red on a
new ``exports/`` entry is the designed behavior, not a defect.

CLI: no arguments runs the tree guard alone; ``--check`` additionally
verifies the banked export pins (``seam_metrics.check_export_pins``).
Exit 0 clean / 1 with one line per typed failure.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import ingest_audio  # noqa: E402  (banked audio exporter, unmodified)
import remedy_masks  # noqa: E402  (banked v15 derivation, unmodified)
import seam_metrics  # noqa: E402  (banked metrics + pins check, unmodified)

EXPORTS_ROOT = ROOT / "exports"
ALLOWED_TOP_FILES = frozenset({".gitkeep"})
RELEASE_MANIFEST_NAME = "release.json"


def release_whitelist() -> frozenset[str]:
    """Release ids allowed directly under exports/, derived from the banked
    exporter constants at call time (see the derivation law above)."""
    return frozenset(seam_metrics.RELEASE_IDS) | {
        remedy_masks.RELEASE_ID,
        ingest_audio.RELEASE_ID,
    }


def check_exports_tree(exports_root: Path) -> list[str]:
    """Typed shape failures for the exports tree; ``[]`` means clean.

    Failure classes: ``missing-exports-root``, ``stray-dir``,
    ``stray-file``, ``missing-release-manifest`` (tree law in the module
    docstring).
    """
    if not exports_root.is_dir():
        return [f"missing-exports-root: {exports_root}"]
    whitelist = release_whitelist()
    failures: list[str] = []
    for entry in sorted(exports_root.iterdir(), key=lambda p: p.name):
        if entry.is_dir():
            if entry.name not in whitelist:
                failures.append(f"stray-dir: {entry.name}")
        elif entry.name not in ALLOWED_TOP_FILES:
            failures.append(f"stray-file: {entry.name}")
    for release_id in sorted(whitelist):
        release_dir = exports_root / release_id
        if release_dir.is_dir():
            if not (release_dir / RELEASE_MANIFEST_NAME).is_file():
                failures.append(f"missing-release-manifest: {release_id}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Global exports-tree guard (typed shape failures; "
        "whitelist derived from banked exporter constants).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="also verify the banked export pins (seam_metrics.check_export_pins)",
    )
    parser.add_argument(
        "--exports-root",
        type=Path,
        default=EXPORTS_ROOT,
        help="exports tree to guard (default: this repo's exports/)",
    )
    args = parser.parse_args(argv)

    failures = check_exports_tree(args.exports_root)
    pins_summary = ""
    if args.check:
        pins = seam_metrics.check_export_pins(args.exports_root)
        failures.extend(f"export-pin: {failure}" for failure in pins["failures"])
        pins_summary = (
            f", pins verified {pins.get('verified', 0)}"
            f"/{pins.get('pinned_total', 0)}"
        )
    if failures:
        for failure in failures:
            print(failure)
        print(f"exports guard FAILED: {len(failures)} failure(s)")
        return 1
    whitelist = release_whitelist()
    present = sum(
        1 for rid in whitelist if (args.exports_root / rid).is_dir()
    )
    print(
        f"exports guard OK: {len(whitelist)} release ids whitelisted, "
        f"{present} present{pins_summary}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
