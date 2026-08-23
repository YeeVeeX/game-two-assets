#!/usr/bin/env python3
"""Tests for the v18 maturity tools: pin_drift + checkout_gate.

FIXTURES ONLY — no live-drift assertions anywhere in this file
(test_asset_gate's live-pin tests are the ONE suite surface that reds
on upstream drift; this file never doubles that failure surface). A
synthetic game git repo (GIT_* scrubbed — hooks export GIT_INDEX_FILE
and break nested git otherwise) carries a five-commit chain exercising
all four pre-registered pin_drift routing classes:

- identity drift            -> mechanical re-pin line
- additive-only, all green  -> approve-by-default CANDIDATE line
- moved constant            -> MUST NOT recommend approve
- deletion in a pinned file -> SESSION JUDGMENT + the quoted clause

plus the attack_timing-moved-while-blobs-identical case (combat.json is
commit-anchored, not pinned) and the READ-ONLY proof: every file under
the fixture tree (including .git) byte-hashed before/after a full
pin_drift run, required identical.

checkout_gate is covered by pure-function tests (surgical tamper,
pointer detection, violation naming, verdict logic, command shape)
WITHOUT running a full clone in the suite — the live both-directions
run is the banked v18 artifact, not a suite surface.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import checkout_gate  # noqa: E402
import pin_drift  # noqa: E402

REFERENCE_FIXTURE = {
    "primitive_body": {
        "size": 20,
        "body_rgb": [1, 2, 3],
        "notch_rgb": [4, 5, 6],
        "notch_size": 4,
    },
    "telegraph": {
        "edge_rgb": [7, 8, 9],
        "core_rgb": [10, 11, 12],
        "body_rgb": [13, 14, 15],
    },
    "possession_ring": {"rgb": [255, 255, 255], "expand": 2},
    "feedback_states": {
        "hurt_flash": {
            "pack_rgb": [16, 17, 18],
            "human_rgb": [19, 20, 21],
            "flicker_period_frames": 3,
        },
        "ally_dim": {"rgb": [22, 23, 24], "alpha": 99},
        "lunge_offset": {"windup_px": -2, "active_px": 5},
        "telegraph_swell": {
            "swell_px": 6,
            "edge_expand_px": 3,
            "core_expand_px": 1,
            "inner_body_inset_px": 2,
        },
    },
    "attack_timing": {
        "source_file": "data/balance/combat.json",
        "values": {
            "windup_frames": {
                "json_pointer": "/kits/striker/attack/windup_frames",
                "value": 5,
            },
            "active_frames": {
                "json_pointer": "/kits/striker/attack/active_frames",
                "value": 4,
            },
            "recovery_frames": {
                "json_pointer": "/kits/striker/attack/recovery_frames",
                "value": 8,
            },
            "step_frames": {
                "json_pointer": "/kits/striker/step_frames",
                "value": 13,
            },
        },
    },
}

RENDERER_FIXTURE = """\
module Render
  class Renderer
    HUMAN_BODY = Gosu::Color.new(255, 13, 14, 15)
    KIT_BODY = Hash.new(HUMAN_BODY).merge(
      striker: Gosu::Color.new(255, 1, 2, 3),
    )
    POSSESSED_RING = Gosu::Color.new(255, 255, 255, 255)
    ALLY_DIM       = Gosu::Color.new(99, 22, 23, 24)
    PACK_HURT      = Gosu::Color.new(255, 16, 17, 18)
    HUMAN_HURT     = Gosu::Color.new(255, 19, 20, 21)
    TELEGRAPH_EDGE = Gosu::Color.new(255, 7, 8, 9)
    TELEGRAPH_CORE = Gosu::Color.new(255, 10, 11, 12)
    NOTCH          = Gosu::Color.new(255, 4, 5, 6)

    def draw_creature(c)
      Gosu.draw_rect(x - 2, y - 2, SIZE + 4, SIZE + 4, POSSESSED_RING)
      if c.telegraphing?
        swell = 6
        Gosu.draw_rect(x - swell / 2, y - swell / 2, SIZE + swell, SIZE + swell, TELEGRAPH_EDGE)
        Gosu.draw_rect(x - 1, y - 1, SIZE + 2, SIZE + 2, TELEGRAPH_CORE)
        Gosu.draw_rect(x + 2, y + 2, SIZE - 4, SIZE - 4, HUMAN_BODY)
      end
      PACK_HURT if c.iframes? && (world.frame / 3).even?
    end

    def draw_facing_notch(c, x, y)
      n = 4
      Gosu.draw_rect(x, y, n, n, NOTCH)
    end

    def lunge_offset(c)
      case c.attack_state
      when :windup then [-2 * fx, -2 * fy]
      when :active then [5 * fx, 5 * fy]
      else [0, 0]
      end
    end
  end
end
"""

CREATURE_FIXTURE = """\
module Game
  class Creature
    SIZE = 20
    FILLER_LAW = :removable
    def initialize
      @hp = 1
    end
  end
end
"""

COMBAT_FIXTURE = {
    "kits": {
        "striker": {
            "attack": {
                "windup_frames": 5,
                "active_frames": 4,
                "recovery_frames": 8,
            },
            "step_frames": 13,
        }
    }
}


def _git_env() -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env.update(
        {
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        }
    )
    return env


def _hash_tree(root: Path) -> dict[str, str]:
    """SHA-256 of every file under root, .git included (read-only proof)."""
    digests: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digests[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return digests


class PinDriftFixture(unittest.TestCase):
    """Five-commit synthetic chain; every class asserted from the same pin."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.mkdtemp(prefix="pin-drift-")
        base = Path(cls._tmp)
        cls.game = base / "game"
        (cls.game / "src" / "app").mkdir(parents=True)
        (cls.game / "src" / "game").mkdir(parents=True)
        (cls.game / "data" / "balance").mkdir(parents=True)

        cls._write("src/app/renderer.rb", RENDERER_FIXTURE)
        cls._write("src/game/creature.rb", CREATURE_FIXTURE)
        cls._write("data/display.json", '{"hud": 1}\n')
        cls._write(
            "data/balance/combat.json",
            json.dumps(COMBAT_FIXTURE, indent=2) + "\n",
        )
        cls._write("README.md", "fixture\n")
        cls._git("init", "-q")
        cls._git("add", "-A")
        cls._git("commit", "-q", "-m", "pin")
        cls.commit_pin = cls._git("rev-parse", "HEAD")

        # identity drift: an UNPINNED file moves; pinned blobs identical.
        cls._write("README.md", "fixture moved\n")
        cls._git("commit", "-q", "-am", "identity")
        cls.commit_identity = cls._git("rev-parse", "HEAD")

        # additive-only: renderer gains lines; every constant intact.
        cls._write(
            "src/app/renderer.rb",
            RENDERER_FIXTURE + "# additive comment\n# second line\n",
        )
        cls._git("commit", "-q", "-am", "additive")
        cls.commit_additive = cls._git("rev-parse", "HEAD")

        # moved constant: swell 6 -> 7 edited in place.
        cls._write(
            "src/app/renderer.rb",
            RENDERER_FIXTURE.replace("swell = 6", "swell = 7")
            + "# additive comment\n# second line\n",
        )
        cls._git("commit", "-q", "-am", "moved constant")
        cls.commit_moved = cls._git("rev-parse", "HEAD")

        # deletion: back to additive renderer, creature loses a line.
        cls._write(
            "src/app/renderer.rb",
            RENDERER_FIXTURE + "# additive comment\n# second line\n",
        )
        cls._write(
            "src/game/creature.rb",
            CREATURE_FIXTURE.replace("    FILLER_LAW = :removable\n", ""),
        )
        cls._git("commit", "-q", "-am", "deletion")
        cls.commit_deletion = cls._git("rev-parse", "HEAD")

        # attack_timing moved while every pinned blob is identical.
        cls._git("checkout", "-q", cls.commit_identity, "--", ".")
        combat = json.loads(json.dumps(COMBAT_FIXTURE))
        combat["kits"]["striker"]["attack"]["windup_frames"] = 6
        cls._write(
            "data/balance/combat.json", json.dumps(combat, indent=2) + "\n"
        )
        cls._git("commit", "-q", "-am", "timing moved")
        cls.commit_timing = cls._git("rev-parse", "HEAD")

        def lf_sha(text: str) -> str:
            return hashlib.sha256(
                text.encode("utf-8").replace(b"\r\n", b"\n")
            ).hexdigest()

        cls.baseline_path = base / "runtime-baseline.json"
        cls.baseline_path.write_text(
            json.dumps(
                {
                    "game_commit": cls.commit_pin,
                    "source_files": [
                        {
                            "path": "src/app/renderer.rb",
                            "sha256_lf": lf_sha(RENDERER_FIXTURE),
                        },
                        {
                            "path": "src/game/creature.rb",
                            "sha256_lf": lf_sha(CREATURE_FIXTURE),
                        },
                        {
                            "path": "data/display.json",
                            "sha256_lf": lf_sha('{"hud": 1}\n'),
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        cls.reference_path = base / "render-reference.json"
        cls.reference_path.write_text(
            json.dumps(REFERENCE_FIXTURE, indent=2) + "\n", encoding="utf-8"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        checkout_gate._force_rmtree(Path(cls._tmp))

    @classmethod
    def _write(cls, rel: str, text: str) -> None:
        (cls.game / rel).write_text(text, encoding="utf-8", newline="\n")

    @classmethod
    def _git(cls, *arguments: str) -> str:
        return subprocess.run(
            ["git", "-C", str(cls.game), *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=_git_env(),
        ).stdout.strip()

    def _analysis(self, new_commit: str) -> dict:
        return pin_drift.analyze(
            self.game, self.baseline_path, self.reference_path, new_commit
        )

    # --- the four pre-registered routing classes ---

    def test_identity_drift_routes_mechanical(self) -> None:
        analysis = self._analysis(self.commit_identity)
        self.assertTrue(all(f["identical"] for f in analysis["files"]))
        self.assertIn("mechanical re-pin", analysis["route"])
        self.assertNotIn("candidate", analysis["route"])

    def test_additive_only_clean_routes_candidate(self) -> None:
        analysis = self._analysis(self.commit_additive)
        renderer = analysis["files"][0]
        self.assertFalse(renderer["identical"])
        self.assertEqual((renderer["added"], renderer["deleted"]), (2, 0))
        self.assertTrue(renderer["additive_only"])
        self.assertTrue(all(c["ok"] for c in analysis["constants"]))
        self.assertIn("approve-by-default candidate", analysis["route"])
        self.assertIn("the session applies the protocol", analysis["route"])
        self.assertNotIn("approved", analysis["route"])

    def test_moved_constant_must_not_recommend_approve(self) -> None:
        analysis = self._analysis(self.commit_moved)
        failed = [c["name"] for c in analysis["constants"] if not c["ok"]]
        self.assertEqual(failed, ["telegraph_swell"])
        self.assertNotIn("approve-by-default candidate", analysis["route"])
        self.assertIn("SESSION JUDGMENT REQUIRED", analysis["route"])
        self.assertIn("derived-constant check failed", analysis["route"])

    def test_deletion_routes_session_judgment_with_clause(self) -> None:
        analysis = self._analysis(self.commit_deletion)
        creature = analysis["files"][1]
        self.assertEqual(creature["deleted"], 1)
        self.assertIn("SESSION JUDGMENT REQUIRED", analysis["route"])
        self.assertIn("non-additive diff", analysis["route"])
        # the clause is QUOTED, never summarized:
        self.assertIn(
            "only draw-value moves or true removals still stop for owner",
            analysis["route"],
        )

    def test_timing_move_blocks_even_with_identical_blobs(self) -> None:
        analysis = self._analysis(self.commit_timing)
        self.assertTrue(all(f["identical"] for f in analysis["files"]))
        windup = next(
            t for t in analysis["attack_timing"] if t["name"] == "windup_frames"
        )
        self.assertFalse(windup["ok"])
        self.assertEqual(windup["actual"], 6)
        self.assertIn("SESSION JUDGMENT REQUIRED", analysis["route"])
        self.assertIn("attack_timing value moved", analysis["route"])

    def test_pin_equals_new_commit_routes_no_re_pin(self) -> None:
        analysis = self._analysis(self.commit_pin)
        self.assertIn("no re-pin due", analysis["route"])

    # --- report + manifest pairs + CLI ---

    def test_manifest_line_pairs_are_exact_surgical_lines(self) -> None:
        analysis = self._analysis(self.commit_additive)
        baseline_text = self.baseline_path.read_text(encoding="utf-8")
        pairs = pin_drift.manifest_line_pairs(baseline_text, analysis)
        self.assertEqual(len(pairs), 2)  # game_commit + renderer sha
        old_commit_line, new_commit_line = pairs[0]
        self.assertIn(self.commit_pin, old_commit_line)
        self.assertIn(self.commit_additive, new_commit_line)
        # exact-line law: the pair differs ONLY by the replaced value.
        self.assertEqual(
            old_commit_line.replace(self.commit_pin, self.commit_additive),
            new_commit_line,
        )
        old_sha_line, new_sha_line = pairs[1]
        self.assertIn(analysis["files"][0]["pinned_sha256_lf"], old_sha_line)
        self.assertIn(analysis["files"][0]["new_sha256_lf"], new_sha_line)

    def test_render_report_names_drift_shape_and_route(self) -> None:
        analysis = self._analysis(self.commit_deletion)
        report = pin_drift.render_report(
            analysis, self.baseline_path.read_text(encoding="utf-8")
        )
        self.assertIn("[drifted]   src/game/creature.rb", report)
        self.assertIn("NOT additive-only", report)
        self.assertIn("ROUTE: SESSION JUDGMENT REQUIRED", report)
        self.assertIn("writes nothing", report)

    def test_cli_exits_0_on_any_completed_route(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            exit_code = pin_drift.main(
                [
                    "--game-root", str(self.game),
                    "--baseline", str(self.baseline_path),
                    "--reference", str(self.reference_path),
                    "--new-commit", self.commit_moved,
                ]
            )
        self.assertEqual(exit_code, 0)  # advisor, never a gate
        self.assertIn("SESSION JUDGMENT REQUIRED", captured.getvalue())

    def test_cli_analysis_failure_exits_2(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            exit_code = pin_drift.main(
                [
                    "--game-root", str(self.game),
                    "--baseline", str(self.reference_path),  # wrong file
                    "--reference", str(self.reference_path),
                ]
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("ANALYSIS FAILURE", captured.getvalue())

    # --- read-only proof (pre-registered) ---

    def test_full_run_is_read_only_by_byte_hash(self) -> None:
        before = _hash_tree(Path(self._tmp))
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = pin_drift.main(
                [
                    "--game-root", str(self.game),
                    "--baseline", str(self.baseline_path),
                    "--reference", str(self.reference_path),
                    "--new-commit", self.commit_deletion,
                ]
            )
        self.assertEqual(exit_code, 0)
        self.assertEqual(before, _hash_tree(Path(self._tmp)))

    # --- derivation law ---

    def test_needles_derive_from_reference_values(self) -> None:
        checks = pin_drift.derive_constant_checks(REFERENCE_FIXTURE)
        by_name = {check.name: check for check in checks}
        self.assertEqual(len(checks), 19)
        self.assertIn("Gosu::Color.new(255, 1, 2, 3)", by_name["body_striker"].pattern)
        self.assertIn("swell = 6", by_name["telegraph_swell"].pattern)
        self.assertIn("SIZE = 20", by_name["creature_size"].pattern)
        self.assertEqual(by_name["creature_size"].file_role, "creature")

    def test_missing_reference_path_is_a_typed_failure(self) -> None:
        broken = json.loads(json.dumps(REFERENCE_FIXTURE))
        del broken["feedback_states"]["telegraph_swell"]
        with self.assertRaises(pin_drift.PinDriftError):
            pin_drift.derive_constant_checks(broken)

    def test_constant_ok_is_false_when_needle_absent(self) -> None:
        check = pin_drift.ConstantCheck(
            "body_striker", "renderer", "substring", "Gosu::Color.new(255, 1, 2, 3)"
        )
        self.assertTrue(pin_drift._constant_ok(check, RENDERER_FIXTURE))
        self.assertFalse(
            pin_drift._constant_ok(
                check, RENDERER_FIXTURE.replace("(255, 1, 2, 3)", "(255, 9, 9, 9)")
            )
        )

    def test_swell_consistency_law(self) -> None:
        self.assertTrue(pin_drift.check_swell_consistency(REFERENCE_FIXTURE))
        broken = json.loads(json.dumps(REFERENCE_FIXTURE))
        broken["feedback_states"]["telegraph_swell"]["edge_expand_px"] = 4
        self.assertFalse(pin_drift.check_swell_consistency(broken))


class CheckoutGatePureFunctions(unittest.TestCase):
    """Pure-function coverage; the full clone run is the banked artifact,
    never a suite surface."""

    BASELINE_TEXT = (
        '{\n'
        '  "game_commit": "' + "a" * 40 + '",\n'
        '  "source_files": [\n'
        '    {\n'
        '      "path": "src/app/renderer.rb",\n'
        '      "sha256_lf": "' + "b" * 64 + '"\n'
        '    },\n'
        '    {\n'
        '      "path": "src/game/creature.rb",\n'
        '      "sha256_lf": "' + "c" * 64 + '"\n'
        '    }\n'
        '  ]\n'
        '}\n'
    )

    def test_tamper_is_surgical_first_sha_only(self) -> None:
        original = self.BASELINE_TEXT.encode("utf-8")
        tampered, replaced = checkout_gate.tamper_baseline_text(original)
        self.assertEqual(replaced, "b" * 64)
        self.assertNotEqual(tampered, original)
        self.assertEqual(tampered.count(b"\n"), original.count(b"\n"))
        parsed = json.loads(tampered.decode("utf-8"))
        self.assertEqual(parsed["source_files"][0]["sha256_lf"], "0" * 64)
        self.assertEqual(parsed["source_files"][1]["sha256_lf"], "c" * 64)
        self.assertEqual(parsed["game_commit"], "a" * 40)  # never the WARN field
        # never a re-serialization: everything but the sha is byte-identical.
        self.assertEqual(
            tampered.replace(b"0" * 64, b"b" * 64), original
        )

    def test_tamper_without_sha_field_is_a_typed_failure(self) -> None:
        with self.assertRaises(checkout_gate.CheckoutGateError):
            checkout_gate.tamper_baseline_text(b'{"game_commit": "abc"}')

    def test_lfs_pointer_detection(self) -> None:
        pointer = (
            b"version https://git-lfs.github.com/spec/v1\n"
            b"oid sha256:" + b"d" * 64 + b"\nsize 12\n"
        )
        self.assertTrue(checkout_gate.is_lfs_pointer(pointer))
        self.assertFalse(checkout_gate.is_lfs_pointer(b"\x89PNG\r\n\x1a\n"))

    def test_pointer_scan_finds_only_pointer_files(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="lfs-scan-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "sources").mkdir()
        (tmp / "sources" / "real.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 64)
        (tmp / "sources" / "pointer.wav").write_bytes(
            b"version https://git-lfs.github.com/spec/v1\noid sha256:"
            + b"e" * 64
            + b"\nsize 9\n"
        )
        (tmp / "big.bin").write_bytes(b"y" * 2048)
        self.assertEqual(
            checkout_gate.scan_lfs_pointers(tmp), ["sources/pointer.wav"]
        )

    def test_violation_naming(self) -> None:
        self.assertTrue(
            checkout_gate.violation_named(
                "- manifests/runtime-baseline.json: source_files[0].sha256_lf "
                "does not match game-two"
            )
        )
        self.assertFalse(checkout_gate.violation_named("Asset gate failed"))

    def test_overall_verdict_matrix(self) -> None:
        ok = {"verdict": "PASS"}
        bad = {"verdict": "FAIL"}
        skipped = {"status": "SKIPPED"}
        self.assertEqual(checkout_gate.overall_verdict(ok, ok, skipped), "PASS")
        self.assertEqual(
            checkout_gate.overall_verdict(ok, ok, {"status": "PASS"}), "PASS"
        )
        self.assertEqual(checkout_gate.overall_verdict(bad, ok, skipped), "FAIL")
        self.assertEqual(checkout_gate.overall_verdict(ok, bad, skipped), "FAIL")
        # a secondary that RUNS and fails is its own typed outcome:
        self.assertEqual(
            checkout_gate.overall_verdict(ok, ok, {"status": "FAIL"}),
            "PASS-WITH-SECONDARY-FAIL",
        )

    def test_gate_command_targets_the_clone_copy(self) -> None:
        command = checkout_gate._gate_command(
            Path("C:/py/python.exe"),
            Path("C:/tmp/clone"),
            Path("C:/gr/game-two"),
            Path("C:/tools/aseprite.exe"),
        )
        joined = " ".join(command)
        self.assertIn("clone", command[1])  # the CLONE's own gate copy
        self.assertIn("--root", joined)
        self.assertIn("--game-root", joined)
        self.assertIn("--aseprite", joined)

    def test_report_path_is_required(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                checkout_gate.main([])


if __name__ == "__main__":
    unittest.main()
