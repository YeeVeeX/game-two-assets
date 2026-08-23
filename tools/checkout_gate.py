#!/usr/bin/env python3
"""Clean-checkout proof for the asset gate (v18; closes the C3 caveat).

The v17 readiness register's C3 row carries its own caveat: "banked
gate runs execute on the maintained working tree; no banked artifact
records a from-scratch-clone run." This tool is that run, scripted and
both-directions:

- PRIMARY (zero network): ``git clone --no-hardlinks`` from THIS repo's
  own ``.git`` (committed HEAD only) into a fresh temp dir with
  ``GIT_LFS_SKIP_SMUDGE=1``, then exactly one ``git lfs pull`` from the
  local origin (file-path remote — the source repo's ``.git/lfs`` object
  store), then the CLONE's own ``tools/asset_gate.py`` run with the
  invoking interpreter. PASS = exit 0.
- NEGATIVE CONTROL (mandatory, clone-only): tamper the CLONE's
  ``manifests/runtime-baseline.json`` — the first ``sha256_lf`` hex
  literal replaced by 64 zeros via SURGICAL byte replacement (never
  re-serialize the manifest: the v17 json.dumps array-explosion trap),
  chosen because ``sha256_lf`` mismatch is the HARD failure class (a
  tampered ``game_commit`` only WARNS under the parallel-session law).
  PASS = nonzero exit AND the output names the violation. The original
  bytes are restored afterwards.
- SECONDARY (best-effort, network surface): fresh venv +
  ``pip install -r requirements-dev.txt`` + gate re-run with the fresh
  interpreter. Venv/pip failure records SKIPPED with the reason — never
  an overall fail. A secondary that RUNS the gate and fails is its own
  typed outcome (``SECONDARY-FAIL``) surfaced for session judgment.

Externals statement (carried into every report): the gate contracts
against live externals BY DESIGN — the sibling game-two checkout
(read-only), the pinned Aseprite binary, an invoking interpreter.
"Clean checkout" means a from-scratch clone of committed HEAD, never a
hermetic environment.

Write law: this tool writes ONLY under its temp dir (removed at exit)
and the explicitly passed ``--report`` path. It never touches the
source repo, the game repo, or any banked artifact. It is never wired
into hooks. Deliberately UNPINNED (v17 verdict: maintenance tools are
test-carried, not hash-carried).

Overall verdict vocabulary: ``PASS`` / ``FAIL`` /
``PASS-WITH-SECONDARY-FAIL`` (primary + negative control decide;
secondary PASS/SKIPPED never changes the verdict).

Pre-registration: ``reviews/maturity-v18/rationale.md`` (protocol A).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
DEFAULT_GAME_ROOT = ROOT.parent / "game-two"
DEFAULT_ASEPRITE = Path("C:/tools/aseprite/build/bin/aseprite.exe")
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
VIOLATION_NEEDLE = "sha256_lf does not match"
SUBPROCESS_TIMEOUT_S = 900
ZERO_SHA = "0" * 64


class CheckoutGateError(RuntimeError):
    """A deterministic proof-harness failure (not a gate verdict)."""


def _scrubbed_env(**extra: str) -> dict[str, str]:
    """Hook-injected GIT_* overrides break nested git (the banked
    make_release/remedy_masks pattern); scrub them for every child."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(extra)
    return env


def _run(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=str(cwd) if cwd else None,
        env=env or _scrubbed_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=SUBPROCESS_TIMEOUT_S,
    )


def _force_rmtree(path: Path) -> None:
    """Windows git object files are read-only; chmod then retry."""

    def _onexc(func: Any, target: str, _exc: Any) -> None:
        os.chmod(target, stat.S_IWRITE)
        func(target)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_onexc)
    else:  # pragma: no cover - 3.12 is the repo interpreter
        shutil.rmtree(path, onerror=lambda f, t, e: _onexc(f, t, e))


def is_lfs_pointer(head_bytes: bytes) -> bool:
    """True when file content starts with the LFS pointer signature."""
    return head_bytes.startswith(LFS_POINTER_PREFIX)


def scan_lfs_pointers(tree: Path) -> list[str]:
    """Relative paths of LFS pointer files anywhere under ``tree``
    (excluding .git). Pointers are ~130 bytes; only small files can be
    pointers, so the scan stays cheap."""
    pointers: list[str] = []
    for path in sorted(tree.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            if path.stat().st_size > 1024:
                continue
            with path.open("rb") as handle:
                head = handle.read(len(LFS_POINTER_PREFIX))
        except OSError:
            continue
        if is_lfs_pointer(head):
            pointers.append(path.relative_to(tree).as_posix())
    return pointers


def tamper_baseline_text(original: bytes) -> tuple[bytes, str]:
    """Surgically replace the FIRST ``sha256_lf`` hex literal with 64
    zeros. Byte-level single replacement — the manifest is NEVER
    re-serialized (v17 array-explosion trap). Returns (tampered bytes,
    the replaced sha)."""
    marker = b'"sha256_lf": "'
    start = original.find(marker)
    if start < 0:
        raise CheckoutGateError("baseline has no sha256_lf field to tamper")
    sha_start = start + len(marker)
    sha = original[sha_start : sha_start + 64]
    if len(sha) != 64:
        raise CheckoutGateError("baseline sha256_lf literal is malformed")
    tampered = (
        original[:sha_start] + ZERO_SHA.encode("ascii") + original[sha_start + 64 :]
    )
    if tampered.count(b"\n") != original.count(b"\n"):
        raise CheckoutGateError("tamper changed the line count (not surgical)")
    return tampered, sha.decode("ascii")


def violation_named(gate_output: str) -> bool:
    """True when the gate output names the tampered-pin violation."""
    return VIOLATION_NEEDLE in gate_output


def _gate_command(python: Path, clone: Path, game_root: Path, aseprite: Path) -> list[str]:
    return [
        str(python),
        str(clone / "tools" / "asset_gate.py"),
        "--root",
        str(clone),
        "--game-root",
        str(game_root),
        "--aseprite",
        str(aseprite),
    ]


def _gate_step(
    python: Path, clone: Path, game_root: Path, aseprite: Path
) -> dict[str, Any]:
    result = _run(_gate_command(python, clone, game_root, aseprite), cwd=clone)
    return {
        "command": _gate_command(python, clone, game_root, aseprite),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _git(clone_or_repo: Path, *arguments: str) -> str:
    result = _run(["git", "-C", str(clone_or_repo), *arguments])
    if result.returncode != 0:
        raise CheckoutGateError(
            f"git {' '.join(arguments)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def overall_verdict(
    primary: dict[str, Any],
    negative: dict[str, Any],
    secondary: dict[str, Any],
) -> str:
    """PASS / FAIL / PASS-WITH-SECONDARY-FAIL (pre-registered law):
    primary exit 0 AND negative-control nonzero-naming-the-violation
    decide; secondary PASS/SKIPPED never changes the verdict."""
    both = primary.get("verdict") == "PASS" and negative.get("verdict") == "PASS"
    if not both:
        return "FAIL"
    if secondary.get("status") == "FAIL":
        return "PASS-WITH-SECONDARY-FAIL"
    return "PASS"


def _secondary_step(
    tmp: Path, clone: Path, game_root: Path, aseprite: Path
) -> dict[str, Any]:
    """Fresh venv + requirements-dev.txt + gate re-run. Best-effort:
    venv/pip failure -> SKIPPED with reason (never an overall fail)."""
    step: dict[str, Any] = {"status": "SKIPPED", "reason": None}
    venv_dir = tmp / "fresh-venv"
    created = _run([sys.executable, "-m", "venv", str(venv_dir)])
    if created.returncode != 0:
        step["reason"] = f"venv creation failed: {created.stderr.strip()[:400]}"
        return step
    venv_python = venv_dir / "Scripts" / "python.exe"
    if not venv_python.is_file():  # pragma: no cover - POSIX layout
        venv_python = venv_dir / "bin" / "python"
    pip = _run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(clone / "requirements-dev.txt"),
        ]
    )
    step["pip_exit_code"] = pip.returncode
    if pip.returncode != 0:
        step["reason"] = (
            "pip install failed (network surface, best-effort): "
            + pip.stderr.strip()[-400:]
        )
        return step
    gate = _gate_step(venv_python, clone, game_root, aseprite)
    step.update(gate)
    step["status"] = "PASS" if gate["exit_code"] == 0 else "FAIL"
    step["reason"] = None if step["status"] == "PASS" else "gate failed on fresh venv"
    return step


def run_proof(
    *,
    report_path: Path,
    game_root: Path,
    aseprite: Path,
    python: Path,
    secondary: bool,
    source_root: Path = ROOT,
) -> dict[str, Any]:
    """Execute the full pre-registered protocol; return the report dict
    (also written to ``report_path``)."""
    source_head = _git(source_root, "rev-parse", "HEAD")
    tmp = Path(tempfile.mkdtemp(prefix="checkout-gate-"))
    try:
        clone = tmp / "clone"
        clone_result = _run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-hardlinks",
                str(source_root),
                str(clone),
            ],
            env=_scrubbed_env(GIT_LFS_SKIP_SMUDGE="1"),
        )
        if clone_result.returncode != 0:
            raise CheckoutGateError(
                f"local clone failed: {clone_result.stderr.strip()}"
            )
        clone_head = _git(clone, "rev-parse", "HEAD")
        lfs_pull = _run(["git", "-C", str(clone), "lfs", "pull"])
        pointers_left = scan_lfs_pointers(clone)

        primary = _gate_step(python, clone, game_root, aseprite)
        primary["verdict"] = "PASS" if primary["exit_code"] == 0 else "FAIL"

        baseline_path = clone / "manifests" / "runtime-baseline.json"
        original = baseline_path.read_bytes()
        tampered, replaced_sha = tamper_baseline_text(original)
        baseline_path.write_bytes(tampered)
        negative = _gate_step(python, clone, game_root, aseprite)
        baseline_path.write_bytes(original)
        named = violation_named(negative["stdout"] + negative["stderr"])
        negative["tampered_field"] = "source_files[0].sha256_lf"
        negative["replaced_sha256_lf"] = replaced_sha
        negative["violation_named"] = named
        negative["verdict"] = (
            "PASS" if negative["exit_code"] != 0 and named else "FAIL"
        )

        secondary_step: dict[str, Any] = {
            "status": "SKIPPED",
            "reason": "disabled by --no-secondary",
        }
        if secondary:
            secondary_step = _secondary_step(tmp, clone, game_root, aseprite)

        report = {
            "contract_version": 1,
            "tool": "tools/checkout_gate.py",
            "protocol": "reviews/maturity-v18/rationale.md (protocol A)",
            "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "source_repo": str(source_root),
            "source_head": source_head,
            "clone": {
                "head": clone_head,
                "head_matches_source": clone_head == source_head,
                "lfs": {
                    "skip_smudge_clone": True,
                    "lfs_pull_exit_code": lfs_pull.returncode,
                    "pointers_remaining": pointers_left,
                },
            },
            "externals": {
                "statement": (
                    "The gate contracts against live externals by design: "
                    "the sibling game-two checkout (read-only), the pinned "
                    "Aseprite binary, and an invoking Python interpreter. "
                    "Clean checkout means a from-scratch clone of committed "
                    "HEAD, never a hermetic environment."
                ),
                "game_root": str(game_root),
                "game_head_at_run": _git(game_root, "rev-parse", "HEAD"),
                "aseprite": str(aseprite),
                "primary_python": str(python),
            },
            "primary": primary,
            "negative_control": negative,
            "secondary": secondary_step,
        }
        report["overall"] = overall_verdict(primary, negative, secondary_step)
    finally:
        _force_rmtree(tmp)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Both-directions clean-checkout proof for the asset gate "
            "(local clone of committed HEAD; writes only the --report "
            "path and its own temp dir)."
        )
    )
    parser.add_argument(
        "--report", type=Path, required=True, help="JSON report output path"
    )
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--aseprite", type=Path, default=DEFAULT_ASEPRITE)
    parser.add_argument(
        "--python",
        type=Path,
        default=Path(sys.executable),
        help="interpreter for the primary gate run (default: this one)",
    )
    parser.add_argument(
        "--no-secondary",
        action="store_true",
        help="skip the fresh-venv secondary proof",
    )
    args = parser.parse_args(argv)
    try:
        report = run_proof(
            report_path=args.report.resolve(),
            game_root=args.game_root.resolve(),
            aseprite=args.aseprite,
            python=args.python,
            secondary=not args.no_secondary,
        )
    except (CheckoutGateError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"checkout gate HARNESS ERROR: {exc}")
        return 2
    lfs = report["clone"]["lfs"]
    print(
        f"clone: {report['clone']['head'][:12]} from committed HEAD "
        f"(lfs pull exit {lfs['lfs_pull_exit_code']}, "
        f"{len(lfs['pointers_remaining'])} pointer(s) remaining)"
    )
    print(
        f"primary: exit {report['primary']['exit_code']} - "
        f"{report['primary']['verdict']}"
    )
    negative = report["negative_control"]
    print(
        f"negative control: exit {negative['exit_code']}, violation "
        f"named={negative['violation_named']} - {negative['verdict']}"
    )
    secondary = report["secondary"]
    reason = f" ({secondary['reason']})" if secondary.get("reason") else ""
    print(f"secondary: {secondary['status']}{reason}")
    print(f"checkout gate {report['overall']}: report at {args.report}")
    return 0 if report["overall"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
