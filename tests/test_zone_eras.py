"""Fast-tier guards for zone-era manifests (docs/zone-era-manifests.md).

Pre-registered in reviews/zone-era-v33/rationale.md (commit A, before
this module existed). Three duties:

- every era file ``manifests/zone-<kind>-<zone>-<era>.json``: filename
  era == prefix of ``anchoring.source_sha256_lf`` (8 hex, or 12 on the
  law's collision escalation); anchoring block complete (game_commit,
  source_file, source_sha256_lf, value_citations); schema shape loads;
- palette era instances re-derive VALUE-BY-VALUE from pinned game bytes
  (``git -C ../game-two show <game_commit>:<source_file>``) — the live
  half skips LOUDLY when the real sibling checkout is absent (the
  test_asset_gate live-test pattern; no mocks, Rule 3);
- the two grandfathered v32-era files (legacy unsuffixed names) still
  hash to the exact raw-sha256 pins the v31/v32 artifact manifests
  carry — redundant with the push-tier artifact checks BY DESIGN: a
  ~seconds fast-tier early warning vs the 3-4 h push gate.

Era anchoring binds to CONTENT (source_sha256_lf), never to the live
runtime-baseline pin (project MEMORY 2026-08-29; d7294e9 precedent) —
so nothing here reads runtime-baseline.json, and identity-only upstream
re-pins can never redden this module.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFESTS = REPO / "manifests"
GAME_ROOT = REPO.parent / "game-two"

# zone-<kind>-<zone>-<era>.json; kind is one token, zone may carry
# underscores (district_two), era is 8 lowercase hex (12 on the L2
# collision escalation).
ERA_NAME = re.compile(
    r"^zone-([a-z0-9]+)-([a-z0-9_]+)-([0-9a-f]{8}(?:[0-9a-f]{4})?)\.json$"
)

ANCHORING_REQUIRED = (
    "game_commit",
    "source_file",
    "source_sha256_lf",
    "value_citations",
)

# The exact pins the banked artifact manifests carry for the two
# grandfathered v32-era files (reviews/runtime-recompose-v31/
# runtime-exp-manifest.json and reviews/scene-recompose-v32/
# scene-exp-manifest.json, zone_map/zone_palette entries).
GRANDFATHERED_PINS = {
    "zone-map-district.json":
        "b9843cbd32993cecf94b3ee1be4cad0d88d8949ede4ae345cdcae1c3d168b082",
    "zone-palette-district.json":
        "ee2d185a2b8b5c120001751951fc787e9d863065e01eef413ea93a5017734622",
}


def sha256_lf(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def era_files() -> list[tuple[Path, re.Match]]:
    out = []
    for path in sorted(MANIFESTS.glob("zone-*.json")):
        match = ERA_NAME.match(path.name)
        if match:
            out.append((path, match))
    return out


def git_show(commit: str, source_file: str) -> bytes:
    """Committed game bytes at the era's own anchoring commit. GIT_*
    env is scrubbed: the fast gate runs under git hooks, which export
    GIT_DIR/GIT_INDEX_FILE into children (project MEMORY 2026-08-17)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(GAME_ROOT), "show", f"{commit}:{source_file}"],
        capture_output=True, check=True, env=env,
    ).stdout


class EraFileLaw(unittest.TestCase):
    def test_at_least_one_era_file_exists(self) -> None:
        """The v33 palette instance banks with this module; an empty
        glob would mean the guard guards nothing (list-rot symmetry
        with the fast gate's stale-slow-entry check)."""
        self.assertGreaterEqual(len(era_files()), 1)

    def test_filename_era_is_the_source_content_sha_prefix(self) -> None:
        for path, match in era_files():
            with self.subTest(file=path.name):
                manifest = json.loads(path.read_text(encoding="utf-8"))
                era = match.group(3)
                self.assertEqual(
                    era,
                    manifest["anchoring"]["source_sha256_lf"][: len(era)],
                )

    def test_anchoring_block_is_complete(self) -> None:
        for path, _ in era_files():
            with self.subTest(file=path.name):
                anchoring = json.loads(
                    path.read_text(encoding="utf-8")
                )["anchoring"]
                for key in ANCHORING_REQUIRED:
                    self.assertIn(key, anchoring)
                self.assertRegex(
                    anchoring["source_sha256_lf"], r"^[0-9a-f]{64}$"
                )
                self.assertRegex(anchoring["game_commit"], r"^[0-9a-f]{40}$")
                self.assertTrue(anchoring["value_citations"])

    def test_schema_shape_loads(self) -> None:
        for path, match in era_files():
            with self.subTest(file=path.name):
                manifest = json.loads(path.read_text(encoding="utf-8"))
                for key in ("contract_version", "purpose", "derived_at",
                            "anchoring"):
                    self.assertIn(key, manifest)
                if match.group(1) == "palette":
                    zone = match.group(2)
                    self.assertEqual([zone], list(manifest["zones"]))


class PaletteEraRederivation(unittest.TestCase):
    """The core L6 duty: era values byte-equal the re-derivation from
    the pinned game bytes the anchoring names."""

    def _palette_eras(self) -> list[tuple[Path, str]]:
        return [(p, m.group(2)) for p, m in era_files()
                if m.group(1) == "palette"]

    def test_values_rederive_from_pinned_game_bytes(self) -> None:
        if not GAME_ROOT.is_dir():
            self.skipTest("real sibling game-two checkout is unavailable")
        for path, zone in self._palette_eras():
            with self.subTest(file=path.name):
                manifest = json.loads(path.read_text(encoding="utf-8"))
                anchoring = manifest["anchoring"]
                shown = git_show(
                    anchoring["game_commit"], anchoring["source_file"]
                )
                self.assertEqual(
                    anchoring["source_sha256_lf"], sha256_lf(shown),
                    f"{path.name}: pinned game bytes do not hash to the "
                    "anchored source sha (banked-anchor integrity event)",
                )
                source_palette = json.loads(shown.decode("utf-8"))["palette"]
                self.assertEqual(source_palette, manifest["zones"][zone])

    def test_every_palette_key_carries_a_citation(self) -> None:
        for path, zone in self._palette_eras():
            with self.subTest(file=path.name):
                manifest = json.loads(path.read_text(encoding="utf-8"))
                citations = manifest["anchoring"]["value_citations"]
                for key in manifest["zones"][zone]:
                    self.assertIn(key, citations)


class GrandfatheredFrozenFiles(unittest.TestCase):
    def test_v32_era_files_hash_to_their_banked_pins(self) -> None:
        for name, pin in GRANDFATHERED_PINS.items():
            with self.subTest(file=name):
                digest = hashlib.sha256(
                    (MANIFESTS / name).read_bytes()
                ).hexdigest()
                self.assertEqual(
                    pin, digest,
                    f"{name}: frozen v32-era banked input no longer "
                    "matches the v31/v32 artifact-manifest pin "
                    "(banked-artifact integrity event - STOP, never "
                    "self-repair; docs/zone-era-manifests.md L1)",
                )


if __name__ == "__main__":
    unittest.main()
