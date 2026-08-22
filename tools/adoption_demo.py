#!/usr/bin/env python3
"""Adoption-record demo proof for the v16 sprint (reviews/adoption-v16/).

The owner ratified the v15 K-S selection ("Approved, proceed" at v15
close; docs/selection-register.md carries the entry). The selection
evidence lives in audit-geometry strips and side-by-side APNGs — nobody
had yet seen the artifact class the defect was SIGHTED in (the v13 demo
APNG) with the selected bytes in it. This module produces exactly that,
under two machine bars fixed in reviews/adoption-v16/rationale.md BEFORE
any artifact existed:

- **incumbent-reproduction bar:** this module rebuilds the v13 demo
  through its own code path using the banked ``track_recompose`` builder
  functions unmodified, and the result must equal the committed
  reviews/recompose-v13/synthetic-demo.apng bytes exactly — proof the
  harness IS the sighting pipeline;
- **swap-purity bar:** the K-S build runs the SAME code path with only
  the attack directory substituted (a staged temp dir holding the
  remedy-v15 K-S exports under the banked k0 filenames — a dirs-level
  seam; no pinned module is touched). Clause A: in-process 4x pane
  buffers differ ONLY at ticks whose mapped pose is k0, and each
  differing frame's changed-pixel set equals the right-facing gape mask
  transformed by that tick's draw vector and the pane transform. Clause
  B: the staged files byte-equal the release-pinned K-S exports, and
  every changed pane pixel carries shade #8c3818 in the K-S build and
  accent #140e0c in the incumbent build.

Artifacts (SYNTHETIC/EXP-labeled in filename, manifest, and pixels): the
K-S demo APNG at 4x and 8x, real 1/60 s and slowed 6/60 s; the
side-by-side incumbent/K-S variant of the same matrix; one 8x NN strip of
the demo attack window (T27–T47, two aligned streams, fixed viewport
crop). 8x variants use this module's scale-parameterized mirror of the
banked pane builder, whose 4x output is machine-asserted byte-identical
to the banked builder's. ZERO new pixels; zero exports; zero
adjudication; the banked k0 stays the pinned history every banked
artifact regenerates from.

``--check`` verifies: the incumbent-reproduction bar, the swap-purity
bar, committed artifacts regenerate byte-identically, module hash pins
(the v13+v14+v15 lattice + this module), the 26 banked export pins, the
remedy-v15 release pins, directory guards, and zero exports/ additions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import pose_integrity_metrics as pim  # noqa: E402  (banked v14 audit, unmodified)
import remedy_masks as rm  # noqa: E402  (banked v15 derivation, unmodified)
import remedy_metrics as rmx  # noqa: E402  (banked v15 metrics, unmodified)
import track_recompose as tr  # noqa: E402  (banked v13 consumer, unmodified)
from make_contact_sheet import GUTTER, load_reference  # noqa: E402  (banked)
from make_grammar_timeline import (  # noqa: E402  (banked encoder + delays)
    apng_delays,
    canvas_pixels,
    encode_apng,
)
from make_seam_timeline import default_dirs, draw_text  # noqa: E402  (banked)
from make_turn_timeline import BG as PANE_BG  # noqa: E402  (banked)
from png_writer import Rgba8Canvas  # noqa: E402  (banked)
from seam_metrics import check_export_pins  # noqa: E402  (banked)

CANVAS = 32
PANE_LABEL_BAND = 10           # the banked build_demo_apng_frames label band
DEMO_SCALE = tr.APNG_SCALE     # 4 — the banked demo pane scale
SCALES = (4, 8)
SHADE_RGB = (0x8C, 0x38, 0x18)
ACCENT_RGB_T = (0x14, 0x0E, 0x0C)
KS_LANE = "ks"
STRIP_WINDOW = (27, 47)        # pre-registered demo attack window
STRIP_SCALE = 8
STRIP_CROP_X = (24, 96)       # fixed viewport crop, declared in the rationale
STRIP_COLUMNS = 7
MARGIN_LEFT = 8
BG = (12, 10, 14, 255)
BANNER = "SYNTHETIC ADOPTION EXP DEMO CONTEXT ZERO NEW PIXELS"
PROTOCOL_LINE = "PROTOCOL 100 PCT ZOOM NO FIT 8X NN PRESCALED"
STREAM_LABELS = ("INCUMBENT", "KS SELECTED")

REVIEW_DIR = ROOT / "reviews" / "adoption-v16"
REPORT_PATH = REVIEW_DIR / "adoption-report.json"
MANIFEST_PATH = REVIEW_DIR / "adoption-manifest.json"

# The v13+v14+v15 pin lattice (rmx.MODULE_SOURCE_FILES is the v15 manifest
# pin set, which itself extends the v14 set, which covers the v13 set) plus
# this module.
MODULE_SOURCE_FILES = tuple(rmx.MODULE_SOURCE_FILES) + (
    "tools/adoption_demo.py",
)


class AdoptionDemoError(ValueError):
    """A deterministic verification failure."""


# -- the two build paths (banked functions, dirs-level seam) --------------------


def ks_export_path(facing: str) -> Path:
    return rm.EXPORT_DIR / f"{rm.variant_asset_id(facing, KS_LANE)}.png"


def release_pinned_sha(facing: str) -> str:
    """The K-S export sha256 as pinned by the committed release manifest."""
    manifest = json.loads(
        (rm.EXPORT_DIR / "release.json").read_text(encoding="utf-8")
    )
    asset_id = rm.variant_asset_id(facing, KS_LANE)
    for entry in manifest["exports"]:
        if entry["asset_id"] == asset_id:
            return entry["sha256"]
    raise AdoptionDemoError(f"release.json has no entry for {asset_id}")


def stage_ks_attack_dir(staging_root: Path) -> Path:
    """Copy the release-pinned K-S exports under the banked k0 filenames
    into a temp directory (the dirs-level seam; nothing in the repo moves).
    Clause B's source-identity assertion happens here."""
    staged = staging_root / "ks-attack-dir"
    staged.mkdir(parents=True, exist_ok=True)
    for facing in ("down", "right"):
        source = ks_export_path(facing)
        payload = source.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        pinned = release_pinned_sha(facing)
        if digest != pinned:
            raise AdoptionDemoError(
                f"{source.name}: sha256 {digest[:16]}… != release pin "
                f"{pinned[:16]}… — refusing to stage a non-release byte"
            )
        target = staged / tr.pose_filename("k0", facing)
        target.write_bytes(payload)
    return staged


def demo_dirs(attack_dir: Path | None = None) -> dict[str, Path]:
    dirs = default_dirs()
    if attack_dir is not None:
        dirs = {**dirs, "attack_dir": attack_dir}
    return dirs


def build_demo(reference: dict, attack_dir: Path | None = None) -> dict:
    """One demo build through the banked v13 code path. Returns the track,
    the in-process 4x pane frames, the decisions, and the encoded APNG."""
    dirs = demo_dirs(attack_dir)
    track = tr.build_demo_track(reference)
    poses = tr.load_poses(dirs)
    frames = tr.build_demo_apng_frames(track, poses, reference)
    _, decisions = tr.recompose_track(track, poses, reference, "zone_1")
    apng = encode_apng(frames, apng_delays(len(frames)))
    return {
        "track": track,
        "poses": poses,
        "frames": frames,
        "decisions": decisions,
        "apng": apng,
    }


def track_bytes(track: dict) -> bytes:
    return (json.dumps(track, indent=2, sort_keys=True) + "\n").encode("ascii")


# -- incumbent-reproduction bar --------------------------------------------------


def incumbent_reproduction(build: dict) -> dict:
    """The pre-registered bar: this harness's incumbent build must equal
    the committed v13 demo bytes exactly."""
    committed_apng = tr.DEMO_APNG.read_bytes()
    committed_track = tr.DEMO_TRACK.read_bytes()
    fresh_track = track_bytes(build["track"])
    return {
        "committed_apng_sha256": hashlib.sha256(committed_apng).hexdigest(),
        "rebuilt_apng_sha256": hashlib.sha256(build["apng"]).hexdigest(),
        "apng_byte_identical": build["apng"] == committed_apng,
        "committed_track_sha256": hashlib.sha256(committed_track).hexdigest(),
        "rebuilt_track_sha256": hashlib.sha256(fresh_track).hexdigest(),
        "track_byte_identical": fresh_track == committed_track,
    }


# -- swap-purity bar --------------------------------------------------------------


def gape_mask_right() -> list[tuple[int, int]]:
    masks = json.loads(rm.MASKS_PATH.read_text(encoding="utf-8"))
    return [tuple(c) for c in masks["facings"]["right"]["gape_pixels"]]


def expected_block_cells(
    draw: list[int], scale: int, band: int
) -> set[tuple[int, int]]:
    """The gape mask transformed by the draw vector and the pane transform:
    gape cell (gx, gy) -> the scale x scale pane block at
    ((dx + gx) * scale, band + (dy + gy) * scale)."""
    dx, dy = draw
    cells: set[tuple[int, int]] = set()
    for gx, gy in gape_mask_right():
        base_x = (dx + gx) * scale
        base_y = band + (dy + gy) * scale
        for oy in range(scale):
            for ox in range(scale):
                cells.add((base_x + ox, base_y + oy))
    return cells


def frame_diff_cells(a: Rgba8Canvas, b: Rgba8Canvas) -> set[tuple[int, int]]:
    if (a.width, a.height) != (b.width, b.height):
        raise AdoptionDemoError("pane geometry differs between builds")
    diffs: set[tuple[int, int]] = set()
    pa, pb = a._pixels, b._pixels
    for y in range(a.height):
        row = y * a.width * 4
        if pa[row: row + a.width * 4] == pb[row: row + a.width * 4]:
            continue
        for x in range(a.width):
            offset = row + x * 4
            if pa[offset: offset + 4] != pb[offset: offset + 4]:
                diffs.add((x, y))
    return diffs


def frame_rgb(cv: Rgba8Canvas, x: int, y: int) -> tuple[int, int, int]:
    offset = (y * cv.width + x) * 4
    return tuple(cv._pixels[offset: offset + 3])


def swap_purity(
    incumbent: dict, substituted: dict, scale: int = DEMO_SCALE,
    band: int = PANE_LABEL_BAND,
) -> dict:
    """Clauses A and B over the two builds' in-process pane buffers."""
    frames_a, frames_b = incumbent["frames"], substituted["frames"]
    decisions = incumbent["decisions"]
    if len(frames_a) != len(frames_b) or len(frames_a) != len(decisions):
        raise AdoptionDemoError("frame/decision counts differ between builds")
    if [d["pose"] for d in decisions] != [
        d["pose"] for d in substituted["decisions"]
    ]:
        raise AdoptionDemoError("decision streams differ between builds")
    k0_ticks = [
        d["frame"] for d in decisions if d["pose"] == "k0"
    ]
    table = []
    clean = True
    for tick, (frame_a, frame_b, decision) in enumerate(
        zip(frames_a, frames_b, decisions)
    ):
        diffs = frame_diff_cells(frame_a, frame_b)
        if decision["pose"] != "k0":
            if diffs:
                clean = False
                table.append(
                    {"tick": tick, "pose": decision["pose"],
                     "changed_px": len(diffs), "expected_px": 0,
                     "sets_equal": False}
                )
            continue
        expected = expected_block_cells(decision["draw"], scale, band)
        colors_ok = all(
            frame_rgb(frame_b, x, y) == SHADE_RGB
            and frame_rgb(frame_a, x, y) == ACCENT_RGB_T
            for x, y in diffs
        )
        entry = {
            "tick": tick,
            "pose": "k0",
            "draw": decision["draw"],
            "changed_px": len(diffs),
            "expected_px": len(expected),
            "sets_equal": diffs == expected,
            "substituted_all_shade_and_incumbent_all_accent": colors_ok,
        }
        clean = clean and entry["sets_equal"] and colors_ok
        table.append(entry)
    window = range(29, 46)  # the v14-cited attack window, ticks 29..45
    stream_ok = (
        len(k0_ticks) == 4
        and k0_ticks == list(range(k0_ticks[0], k0_ticks[0] + 4))
        and all(t in window for t in k0_ticks)
    )
    return {
        "k0_ticks": k0_ticks,
        "k0_stream_consistent_with_v14_window": stream_ok,
        "frames_compared": len(frames_a),
        "per_tick": table,
        "pass": clean and stream_ok and len(table) == len(k0_ticks),
    }


# -- the scale-parameterized mirror (fidelity-asserted at 4x) ---------------------


def build_demo_frames_scaled(
    track: dict, poses: dict, reference: dict, scale: int
) -> list[Rgba8Canvas]:
    """Mirror of the banked tr.build_demo_apng_frames with the pane scale
    parameterized. At scale 4 the output MUST be byte-identical to the
    banked builder's (assert_mirror_fidelity); the 8x artifacts are then
    the banked construction at the other pre-registered protocol scale."""
    frames, _ = tr.recompose_track(track, poses, reference, "zone_1")
    view = track["view"]
    out = []
    for frame in frames:
        pane = Rgba8Canvas(
            view["width"] * scale,
            view["height"] * scale + PANE_LABEL_BAND,
            PANE_BG,
        )
        pane.blit_scaled(canvas_pixels(frame), 0, PANE_LABEL_BAND, scale)
        draw_text(pane, 2, 2, "SYNTHETIC DEMO EXP")
        out.append(pane)
    return out


def assert_mirror_fidelity(build: dict, reference: dict) -> None:
    mirrored = build_demo_frames_scaled(
        build["track"], build["poses"], reference, DEMO_SCALE
    )
    banked = build["frames"]
    if len(mirrored) != len(banked) or any(
        m._pixels != b._pixels or (m.width, m.height) != (b.width, b.height)
        for m, b in zip(mirrored, banked)
    ):
        raise AdoptionDemoError(
            "scale-mirror fidelity failed: the parameterized pane builder "
            "does not reproduce the banked 4x frames byte-identically"
        )


# -- side-by-side + strip compositions (this module's own artifact classes) ------


def compose_side_by_side(
    frames_a: list[Rgba8Canvas], frames_b: list[Rgba8Canvas],
    decisions: list[dict], scale: int, tag: str,
) -> list[Rgba8Canvas]:
    """Incumbent pane stacked over the K-S pane, drawn stream labels."""
    out = []
    for tick, (pane_a, pane_b) in enumerate(zip(frames_a, frames_b)):
        width = pane_a.width
        header = 20
        label_row = 8
        height = header + 2 * (label_row + pane_a.height) + GUTTER
        cv = Rgba8Canvas(width, height, BG)
        draw_text(cv, 2, 2, "SYNTHETIC ADOPTION EXP")
        pose = decisions[tick]["pose"].upper()
        draw_text(cv, 2, 10, f"T{tick:02d} {pose} {tag} {scale}X")
        y = header
        for label, pane in zip(STREAM_LABELS, (pane_a, pane_b)):
            draw_text(cv, 2, y, label)
            y += label_row
            cv.blit_scaled(canvas_pixels(pane), 0, y, 1)
            y += pane.height + (GUTTER if label == STREAM_LABELS[0] else 0)
        out.append(cv)
    return out


def strip_geometry(view: dict) -> tuple[int, int, int]:
    crop_w = STRIP_CROP_X[1] - STRIP_CROP_X[0]
    cell_w = crop_w * STRIP_SCALE
    cell_h = view["height"] * STRIP_SCALE
    return cell_w, cell_h, crop_w


def crop_window(frame: Rgba8Canvas, view: dict) -> list[tuple[int, int, tuple]]:
    """The declared fixed viewport crop of one composed 1x demo window."""
    x0, x1 = STRIP_CROP_X
    return [
        (x - x0, y, frame.get(x, y)[:3])
        for y in range(view["height"])
        for x in range(x0, x1)
        if frame.get(x, y)[3] == 255
    ]


def build_strip(
    incumbent: dict, substituted: dict, reference: dict
) -> Rgba8Canvas:
    """Two aligned 8x streams over the demo attack window T27–T47."""
    track = incumbent["track"]
    view = track["view"]
    lo, hi = STRIP_WINDOW
    window = list(range(lo, hi + 1))
    cell_w, cell_h, _ = strip_geometry(view)
    chunk_rows = (len(window) + STRIP_COLUMNS - 1) // STRIP_COLUMNS
    row_pitch = 16 + cell_h + GUTTER
    width = MARGIN_LEFT + STRIP_COLUMNS * (cell_w + GUTTER) + GUTTER
    height = 26 + 2 * chunk_rows * row_pitch
    cv = Rgba8Canvas(width, height, BG)
    draw_text(cv, 2, 2, BANNER)
    draw_text(
        cv, 2, 10,
        f"{PROTOCOL_LINE}  ZONE 1  TICKS T{lo:02d} TO T{hi:02d}",
    )
    streams = (
        (STREAM_LABELS[0], incumbent), (STREAM_LABELS[1], substituted)
    )
    frames_1x = {
        label: tr.recompose_track(
            build["track"], build["poses"], reference, "zone_1"
        )[0]
        for label, build in streams
    }
    decisions = incumbent["decisions"]
    for stream_index, (label, _) in enumerate(streams):
        for index, tick in enumerate(window):
            chunk, col = divmod(index, STRIP_COLUMNS)
            row = stream_index * chunk_rows + chunk
            x = MARGIN_LEFT + col * (cell_w + GUTTER)
            y = 26 + row * row_pitch
            if col == 0:
                draw_text(cv, x, y, label)
            pose = decisions[tick]["pose"].upper()
            draw_text(cv, x, y + 8, f"T{tick:02d} {pose}")
            cv.blit_scaled(
                crop_window(frames_1x[label][tick], view), x, y + 16,
                STRIP_SCALE,
            )
    return cv


# -- artifact matrix ---------------------------------------------------------------


def artifact_names() -> dict[str, dict]:
    artifacts: dict[str, dict] = {}
    for scale in SCALES:
        for speed in ("real", "slow6"):
            speed_tag = "" if speed == "real" else "-slow6"
            artifacts[f"synthetic-adoption-ks-demo{speed_tag}-{scale}x.apng"] = {
                "kind": "ks-demo", "scale": scale, "speed": speed,
            }
            artifacts[f"synthetic-adoption-sbs-demo{speed_tag}-{scale}x.apng"] = {
                "kind": "sbs-demo", "scale": scale, "speed": speed,
            }
    artifacts["synthetic-adoption-strip-attack-8x.png"] = {"kind": "strip"}
    return artifacts


def artifact_delays(speed: str, count: int) -> list[tuple[int, int]]:
    return apng_delays(count) if speed == "real" else pim.slow_delays(count)


def build_artifact(
    incumbent: dict, substituted: dict, reference: dict, params: dict
) -> bytes:
    if params["kind"] == "strip":
        return build_strip(incumbent, substituted, reference).encode()
    scale, speed = params["scale"], params["speed"]
    tag = "REAL 1 60" if speed == "real" else "SLOW 6 60"
    if params["kind"] == "ks-demo":
        if scale == DEMO_SCALE:
            frames = substituted["frames"]
        else:
            frames = build_demo_frames_scaled(
                substituted["track"], substituted["poses"], reference, scale
            )
        return encode_apng(frames, artifact_delays(speed, len(frames)))
    if params["kind"] == "sbs-demo":
        if scale == DEMO_SCALE:
            frames_a, frames_b = incumbent["frames"], substituted["frames"]
        else:
            frames_a = build_demo_frames_scaled(
                incumbent["track"], incumbent["poses"], reference, scale
            )
            frames_b = build_demo_frames_scaled(
                substituted["track"], substituted["poses"], reference, scale
            )
        frames = compose_side_by_side(
            frames_a, frames_b, incumbent["decisions"], scale, tag
        )
        return encode_apng(frames, artifact_delays(speed, len(frames)))
    raise AdoptionDemoError(f"unknown artifact kind {params['kind']!r}")


# -- report + manifest ---------------------------------------------------------------


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_hashes() -> dict[str, str]:
    return {rel: file_sha256(ROOT / rel) for rel in MODULE_SOURCE_FILES}


def repo_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def build_report(incumbent: dict, substituted: dict, staged: Path) -> dict:
    reproduction = incumbent_reproduction(incumbent)
    purity = swap_purity(incumbent, substituted)
    staged_pinned = all(
        hashlib.sha256(
            (staged / tr.pose_filename("k0", facing)).read_bytes()
        ).hexdigest() == release_pinned_sha(facing)
        for facing in ("down", "right")
    )
    bars = {
        "incumbent_reproduction_apng": reproduction["apng_byte_identical"],
        "incumbent_reproduction_track": reproduction["track_byte_identical"],
        "swap_purity": purity["pass"],
        "staged_source_release_pinned": staged_pinned,
    }
    return {
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tools/adoption_demo.py --make-artifacts",
            "statement": (
                "sighting-context demo proof for the owner-ratified K-S "
                "selection: the banked v13 demo pipeline re-run with only "
                "the k0 sprite substituted, gated by the "
                "incumbent-reproduction and swap-purity bars; composed from "
                "banked export bytes and the release-pinned remedy-v15 K-S "
                "exports only; NOT runtime evidence; answers ZERO register "
                "items; the banked k0 stays the pinned history"
            ),
        },
        "selected_assets": [
            rm.variant_asset_id(facing, KS_LANE) for facing in ("down", "right")
        ],
        "swap_source_sha256": {
            facing: release_pinned_sha(facing) for facing in ("down", "right")
        },
        "incumbent_reproduction": reproduction,
        "swap_purity": purity,
        "machine_bars": bars,
    }


def report_bytes(report: dict) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")


def viewing_protocol() -> dict:
    protocol = pim.viewing_protocol()
    protocol["demo_context"] = (
        "the v13 demo view (96x64 window, zone_1, 48 ticks at exact "
        "1/60 s, 4x panes with the drawn label band) is the artifact class "
        "the owner sighted DEF-1 in; the K-S demo differs from the "
        "committed v13 demo ONLY at the k0 ticks per the swap-purity bar"
    )
    protocol["strip_window"] = (
        f"demo attack window T{STRIP_WINDOW[0]:02d}..T{STRIP_WINDOW[1]:02d} "
        f"(approach tail, full attack envelope, idle return), fixed "
        f"viewport crop x in [{STRIP_CROP_X[0]}, {STRIP_CROP_X[1]}) of the "
        "identically composed demo window, two aligned streams "
        "(INCUMBENT, KS SELECTED)"
    )
    return protocol


def make_artifacts(reference: dict, staging_root: Path) -> dict:
    staged = stage_ks_attack_dir(staging_root)
    incumbent = build_demo(reference)
    substituted = build_demo(reference, staged)
    assert_mirror_fidelity(incumbent, reference)
    report = build_report(incumbent, substituted, staged)
    if not all(report["machine_bars"].values()):
        raise AdoptionDemoError(
            "machine bars failed: " + json.dumps(report["machine_bars"])
        )
    report_a = report_bytes(report)
    report_b = report_bytes(build_report(incumbent, substituted, staged))
    payloads: dict[str, bytes] = {}
    deterministic = report_a == report_b
    for name, params in artifact_names().items():
        first = build_artifact(incumbent, substituted, reference, params)
        second = build_artifact(incumbent, substituted, reference, params)
        deterministic = deterministic and first == second
        payloads[name] = first
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_bytes(report_a)
    for name, payload in payloads.items():
        (REVIEW_DIR / name).write_bytes(payload)
    ticks = len(incumbent["frames"])
    manifest = {
        "generated_by": "tools/adoption_demo.py --make-artifacts",
        "repo_commit_at_generation": repo_commit(),
        "provenance": {
            "class": "SYNTHETIC",
            "statement": (
                "adoption-record demo proof composed from banked export "
                "bytes and the release-pinned remedy-v15 K-S exports only; "
                "NOT runtime evidence; the selection register entry "
                "(docs/selection-register.md) is the recorded owner "
                "decision this proof accompanies"
            ),
        },
        "module_source_sha256": module_hashes(),
        "swap_source": {
            "release_id": rm.RELEASE_ID,
            "assets": {
                facing: {
                    "asset_id": rm.variant_asset_id(facing, KS_LANE),
                    "sha256": release_pinned_sha(facing),
                }
                for facing in ("down", "right")
            },
        },
        "viewing_protocol": viewing_protocol(),
        "apng_ticks": ticks,
        "apng_delays": {
            "real": (
                f"exact 1/60 s per tick x {ticks - 1} + 30/60 s final hold "
                "(banked apng_delays)"
            ),
            "slow6": (
                f"6/60 s per tick x {ticks - 1} + 30/60 s final hold "
                "(banked slow_delays)"
            ),
        },
        "artifacts": {
            REPORT_PATH.name: hashlib.sha256(report_a).hexdigest(),
            **{
                name: hashlib.sha256(payload).hexdigest()
                for name, payload in payloads.items()
            },
        },
        "determinism": {
            "double_build_identical": deterministic,
            "artifact_count": len(payloads) + 1,
        },
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return manifest


# -- --check --------------------------------------------------------------------------


def run_check(reference: dict, staging_root: Path) -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file():
        failures.append(f"missing committed manifest {MANIFEST_PATH.name}")
    else:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if manifest.get("provenance", {}).get("class") != "SYNTHETIC":
            failures.append("manifest provenance.class must be SYNTHETIC")
        live = module_hashes()
        pinned = manifest.get("module_source_sha256", {})
        for rel in MODULE_SOURCE_FILES:
            if rel == "tools/adoption_demo.py":
                continue  # self-pin recorded at generation; git history carries it
            if rel not in pinned:
                failures.append(f"manifest is missing the {rel} pin")
            elif live.get(rel) != pinned[rel]:
                failures.append(
                    f"module drift: {rel} sha256 differs from the manifest pin"
                )
        staged = stage_ks_attack_dir(staging_root)
        incumbent = build_demo(reference)
        substituted = build_demo(reference, staged)
        try:
            assert_mirror_fidelity(incumbent, reference)
        except AdoptionDemoError as exc:
            failures.append(str(exc))
        report = build_report(incumbent, substituted, staged)
        for bar, value in report["machine_bars"].items():
            if value is not True:
                failures.append(f"machine bar failed: {bar}")
        fresh_report = report_bytes(report)
        if not REPORT_PATH.is_file() or fresh_report != REPORT_PATH.read_bytes():
            failures.append(
                "committed adoption-report.json differs from a fresh build"
            )
        for name, params in artifact_names().items():
            path = REVIEW_DIR / name
            if not path.is_file():
                failures.append(f"missing committed artifact {name}")
                continue
            fresh = build_artifact(incumbent, substituted, reference, params)
            if fresh != path.read_bytes():
                failures.append(f"{name} differs from a fresh build")
        for name, digest in manifest.get("artifacts", {}).items():
            path = REVIEW_DIR / name
            if not path.is_file() or file_sha256(path) != digest:
                failures.append(f"manifest artifact pin mismatch: {name}")

    if (ROOT / "exports" / "adoption-v16").exists():
        failures.append("exports/adoption-v16 exists - this sprint banks no exports")
    failures.extend(rmx.check_release(ROOT))
    failures.extend(rmx.check_calibration_dirs(ROOT))
    exports = check_export_pins(ROOT / "exports")
    failures.extend(exports["failures"])

    for failure in failures:
        print(f"CHECK FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        "checks passed: incumbent reproduction byte-exact vs the committed "
        "v13 demo; swap purity (clauses A + B); scale-mirror fidelity; "
        "committed report + APNGs + strip regenerate byte-identically; "
        f"module hash pins; {exports['verified']} banked export pins; "
        "remedy release pins; directory guards; zero-new-exports"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference", type=Path,
        default=ROOT / "manifests" / "render-reference.json",
    )
    parser.add_argument("--make-artifacts", action="store_true",
                        help="generate the report + adoption demo artifacts")
    parser.add_argument("--check", action="store_true",
                        help="full self-verification (see module docstring)")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    try:
        with tempfile.TemporaryDirectory(prefix="adoption-v16-") as tmp:
            staging_root = Path(tmp)
            if args.make_artifacts:
                manifest = make_artifacts(reference, staging_root)
                if not manifest["determinism"]["double_build_identical"]:
                    print("artifact builds are not byte-identical",
                          file=sys.stderr)
                    return 1
                print(f"wrote {REPORT_PATH}")
                print(
                    f"wrote {MANIFEST_PATH} (+ {len(artifact_names())} artifacts)"
                )
                return 0
            if args.check:
                return run_check(reference, staging_root)
    except (AdoptionDemoError, rm.RemedyMaskError, rmx.RemedyMetricsError,
            pim.AuditError, tr.RecomposeError, ValueError, OSError) as exc:
        print(f"adoption demo failed: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
