#!/usr/bin/env python3
"""Verification + selection toolchain for the v15 DEF-1 remedy candidates.

Consumes the six variant exports (exports/remedy-v15/) plus banked bytes and
banked modules only — every imported tools/ module is hash-pinned in
reviews/remedy-v15/remedy-manifest.json and re-verified by ``--check`` and
the tests. Nothing banked is edited; the banked k0 stays the pinned history.

Machine bars (INTEGRITY; reviews/remedy-v15/rationale.md, fixed before any
variant existed):

- diff declaration per variant: alpha plane byte-identical to the banked k0
  (silhouette invariance by construction — every banked XOR/mass/bbox bar
  stays literally valid); RGB differs at EXACTLY the declared recolor set;
  every color inside the frozen 5-color ramp; the set disjoint from the
  translated eye pixels and feet caps;
- eye integrity per variant: accent clusters equal the banked k0 accent set
  minus the gape band — on down that means the two SEPARATE 2x2 eye
  clusters at the v2-banked translated positions (the un-merge, machine
  proved); on right the eye cluster and feet caps unchanged;
- the v14 audit re-run per variant: interior holes (= 0), accent-cluster
  table, color histogram, and the two k0-adjacent cut localizations via the
  banked ``cut_changes`` (silhouette clusters must equal the banked k0's —
  the alpha-identity corollary, asserted);
- context contrast for the lane colors (shade #8c3818, outline #401c10)
  against the pinned zone palettes and the body — context for the
  perceptual read, never a bar.

Selection artifacts (the pinned v14 viewing protocol, restated in the
manifest): four comparison strips (per facing x zone, four stream-rows —
INCUMBENT, KS, KO, KR — over the pre-registered window T05–T12 at 8x NN,
both zone palettes) and twenty-four side-by-side APNGs (per lane x facing,
full 21-tick stream, incumbent pane + variant pane per frame, real 1/60 s
and slowed 6/60 s, 4x and 8x pre-scaled). All SYNTHETIC/EXP-labeled in
filename, manifest, and pixels.

``--check`` verifies: committed masks/specs/report/strips/APNGs regenerate
byte-identically; module hash pins; the 26 banked export pins AND the
remedy-v15 release's own pins; exports/remedy-v15 contains exactly the six
declared PNGs + release.json; no exports/calibration-* addition; the
machine bars recomputed live.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import pose_integrity_metrics as pim  # noqa: E402  (banked v14 audit, unmodified)
import remedy_masks as rm  # noqa: E402  (this sprint's derivation tool)
import track_recompose as tr  # noqa: E402  (banked v13 consumer, unmodified)
from feedback_metrics import contrast_ratio  # noqa: E402  (banked)
from make_contact_sheet import GUTTER, load_reference, sprite_from_png  # noqa: E402
from make_grammar_timeline import (  # noqa: E402  (banked encoder + delays)
    apng_delays,
    canvas_pixels,
    encode_apng,
)
from make_seam_timeline import draw_text, default_dirs  # noqa: E402  (banked)
from png_reader import read_rgba  # noqa: E402  (banked)
from png_writer import Rgba8Canvas  # noqa: E402  (banked)
from seam_metrics import RELEASE_IDS, check_export_pins  # noqa: E402  (banked)

CANVAS = 32
FACINGS = rm.FACINGS
LANES = rm.LANES
LANE_LABELS = {"ks": "KS SHADE", "ko": "KO OUTLINE", "kr": "KR TWO TONE"}
LANE_SHORT = {"ks": "KS", "ko": "KO", "kr": "KR"}
STRIP_WINDOW = (5, 12)     # pre-registered comparison window T05..T12
STRIP_SCALE = 8
APNG_SCALES = (4, 8)
RIGHT_STRIP_COLUMNS = 5    # keeps the right strip under the png_reader cap
MARGIN_LEFT = 8
BG = (12, 10, 14, 255)
BANNER = "SYNTHETIC REMEDY EXP CANDIDATES ZERO ADJUDICATION"
PROTOCOL_LINE = "PROTOCOL 100 PCT ZOOM NO FIT 8X NN PRESCALED"

REVIEW_DIR = ROOT / "reviews" / rm.RELEASE_ID
REPORT_PATH = REVIEW_DIR / "remedy-report.json"
MANIFEST_PATH = REVIEW_DIR / "remedy-manifest.json"
RELEASE_PATH = rm.EXPORT_DIR / "release.json"

# Every tools/ module this sprint imports (directly or transitively): the
# banked v14 audit's full pin list plus this sprint's two new modules.
MODULE_SOURCE_FILES = tuple(pim.MODULE_SOURCE_FILES) + (
    "tools/pixel_spec.py",
    "tools/asset_gate.py",
    "tools/audio_metrics.py",
    "tools/remedy_masks.py",
    "tools/remedy_metrics.py",
)


class RemedyMetricsError(ValueError):
    """A deterministic verification failure."""


# -- variant access ---------------------------------------------------------------


def variant_ids() -> list[str]:
    return [
        rm.variant_asset_id(facing, lane) for facing in FACINGS for lane in LANES
    ]


def load_variant_raw(facing: str, lane: str) -> bytes:
    path = rm.EXPORT_DIR / f"{rm.variant_asset_id(facing, lane)}.png"
    width, height, raw = read_rgba(path)
    if (width, height) != (CANVAS, CANVAS):
        raise RemedyMetricsError(f"{path.name}: expected {CANVAS}x{CANVAS}")
    return raw


def rgb_hex(raw: bytes, x: int, y: int) -> str:
    offset = (y * CANVAS + x) * 4
    return f"#{raw[offset]:02x}{raw[offset + 1]:02x}{raw[offset + 2]:02x}"


# -- (a) diff-declaration verifier ---------------------------------------------------


def alpha_plane(raw: bytes) -> bytes:
    return bytes(raw[3::4])


def diff_report(
    base_raw: bytes, variant_raw: bytes, declared: dict[tuple[int, int], str]
) -> dict:
    """Machine verdicts for one variant against the banked base bytes."""
    alpha_identical = alpha_plane(base_raw) == alpha_plane(variant_raw)
    changed = set()
    for y in range(CANVAS):
        for x in range(CANVAS):
            offset = (y * CANVAS + x) * 4
            if base_raw[offset + 3] != 255 or variant_raw[offset + 3] != 255:
                continue
            if base_raw[offset:offset + 3] != variant_raw[offset:offset + 3]:
                changed.add((x, y))
    declared_set = set(declared)
    colors_ok = True
    ramp = set(rm.RAMP.values())
    for cell in sorted(declared_set):
        actual = rgb_hex(variant_raw, cell[0], cell[1])
        if actual != declared[cell] or actual not in ramp:
            colors_ok = False
    return {
        "alpha_identical": alpha_identical,
        "declared_diff_px": len(declared_set),
        "changed_px": len(changed),
        "diff_set_matches_declaration": changed == declared_set,
        "declared_colors_applied_within_ramp": colors_ok,
        "undeclared_changes": [list(c) for c in sorted(changed - declared_set)],
        "missing_declared_changes": [
            list(c) for c in sorted(declared_set - changed)
        ],
    }


# -- (b) eye-integrity check ---------------------------------------------------------


def cluster_signature(clusters: list[dict]) -> set[tuple[int, tuple[int, ...]]]:
    return {(c["area"], tuple(c["bbox"])) for c in clusters}


def expected_accent_signature(masks: dict, facing: str) -> set:
    """Banked k0 accent minus the gape band, clustered by the banked logic."""
    facts = masks["facings"][facing]
    cells = {tuple(c) for c in facts["translated_eye_pixels"]} | {
        tuple(c) for c in facts["feet_pixels"]
    }
    return {
        (s["area"], tuple(s["bbox"]))
        for s in (
            pim.cluster_summary(component)
            for component in pim.cluster_cells(cells)
        )
    }


EYE_CLUSTERS_DOWN = {(4, (12, 11, 13, 12)), (4, (18, 11, 19, 12))}
EYE_CLUSTER_RIGHT = (4, (22, 11, 23, 12))


def eye_integrity(masks: dict, facing: str, variant_raw: bytes) -> dict:
    actual = cluster_signature(pim.accent_clusters(variant_raw))
    expected = expected_accent_signature(masks, facing)
    if facing == "down":
        eyes_ok = EYE_CLUSTERS_DOWN <= actual
    else:
        eyes_ok = EYE_CLUSTER_RIGHT in actual
    return {
        "accent_clusters_equal_expected": actual == expected,
        "eye_clusters_present_and_separate": eyes_ok,
        "pass": actual == expected and eyes_ok,
    }


# -- (c) the v14 audit re-run per variant --------------------------------------------


def lane_contrast(reference: dict) -> dict:
    body = tuple(reference["primitive_body"]["body_rgb"])
    colors = {
        "accent_incumbent": tuple(pim.ACCENT_RGB),
        "shade": (0x8C, 0x38, 0x18),
        "outline": (0x40, 0x1C, 0x10),
    }
    table: dict[str, dict] = {}
    for name, rgb in colors.items():
        entry: dict[str, dict] = {}
        for zone_key in ("zone_1", "zone_2"):
            zone = reference["zones"][zone_key]
            for surface in ("floor", "grid"):
                other = tuple(zone[surface])
                distance = sum((a - b) ** 2 for a, b in zip(rgb, other)) ** 0.5
                entry[f"vs_{zone_key}_{surface}"] = {
                    "contrast_ratio": contrast_ratio(rgb, other),
                    "rgb_distance": round(distance, 1),
                }
        entry["vs_body"] = {
            "contrast_ratio": contrast_ratio(rgb, body),
            "rgb_distance": round(
                sum((a - b) ** 2 for a, b in zip(rgb, body)) ** 0.5, 1
            ),
        }
        table[name] = entry
    return table


def strip_pixels(cut: dict) -> dict:
    return {
        key: value
        for key, value in cut.items()
        if key in ("silhouette_px", "recolor_px", "silhouette_clusters",
                   "recolor_clusters")
    }


def variant_entry(
    dirs: dict[str, Path], masks: dict, facing: str, lane: str
) -> dict:
    base_raw = rm.load_banked_raw(dirs, "k0", facing)
    a0_raw = rm.load_banked_raw(dirs, "a0", facing)
    s0_raw = rm.load_banked_raw(dirs, "s0", facing)
    variant_raw = load_variant_raw(facing, lane)
    declared = rm.recolor_map(masks, facing, lane)
    eyes_feet = {tuple(c) for c in masks["facings"][facing]["translated_eye_pixels"]}
    eyes_feet |= {tuple(c) for c in masks["facings"][facing]["feet_pixels"]}
    banked_in = pim.cut_changes(a0_raw, base_raw)
    banked_out = pim.cut_changes(base_raw, s0_raw)
    cut_in = pim.cut_changes(a0_raw, variant_raw)
    cut_out = pim.cut_changes(variant_raw, s0_raw)
    report = pim.pose_report(variant_raw)
    return {
        "facing": facing,
        "lane": lane,
        "diff": diff_report(base_raw, variant_raw, declared),
        "declared_disjoint_from_eyes_and_feet": not (
            set(declared) & eyes_feet
        ),
        "eye_integrity": eye_integrity(masks, facing, variant_raw),
        "interior_holes": report["interior_holes"],
        "accent_clusters": report["accent_clusters"],
        "color_histogram": report["color_histogram"],
        "mass": report["mass"],
        "bbox": report["bbox"],
        "cuts": {
            "a0_to_k0": {
                **strip_pixels(cut_in),
                "silhouette_equals_banked": (
                    cut_in["silhouette_clusters"]
                    == banked_in["silhouette_clusters"]
                ),
            },
            "k0_to_s0": {
                **strip_pixels(cut_out),
                "silhouette_equals_banked": (
                    cut_out["silhouette_clusters"]
                    == banked_out["silhouette_clusters"]
                ),
            },
        },
    }


def build_report(dirs: dict[str, Path], reference: dict, masks: dict) -> dict:
    variants = {}
    for facing in FACINGS:
        for lane in LANES:
            variants[rm.variant_asset_id(facing, lane)] = variant_entry(
                dirs, masks, facing, lane
            )
    incumbent = {}
    for facing in FACINGS:
        report = pim.pose_report(rm.load_banked_raw(dirs, "k0", facing))
        incumbent[facing] = {
            "accent_clusters": report["accent_clusters"],
            "interior_holes": report["interior_holes"],
            "color_histogram": report["color_histogram"],
        }
    entries = list(variants.values())
    bars = {
        "alpha_identity_all": all(
            e["diff"]["alpha_identical"] for e in entries
        ),
        "diff_declaration_all": all(
            e["diff"]["diff_set_matches_declaration"]
            and e["diff"]["declared_colors_applied_within_ramp"]
            and e["declared_disjoint_from_eyes_and_feet"]
            for e in entries
        ),
        "eye_integrity_all": all(e["eye_integrity"]["pass"] for e in entries),
        "interior_holes_zero_all": all(
            e["interior_holes"] == [] for e in entries
        ),
        "silhouette_cuts_equal_banked_all": all(
            e["cuts"]["a0_to_k0"]["silhouette_equals_banked"]
            and e["cuts"]["k0_to_s0"]["silhouette_equals_banked"]
            for e in entries
        ),
        "variant_count": len(entries),
    }
    return {
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tools/remedy_metrics.py --make-artifacts",
            "statement": (
                "deterministic measurement over banked export bytes and the "
                "six additive remedy candidates; NOT runtime evidence; "
                "selection is adjudicated in reviews/remedy-v15/verdict.md "
                "under the pre-registered decision rule"
            ),
        },
        "masks_sha256": hashlib.sha256(rm.MASKS_PATH.read_bytes()).hexdigest(),
        "lane_contrast": lane_contrast(reference),
        "incumbent": incumbent,
        "variants": variants,
        "machine_bars": bars,
    }


def report_bytes(report: dict) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")


# -- (d) selection artifacts ---------------------------------------------------------


def load_sprites(dirs: dict[str, Path]) -> dict:
    """Banked pose sprites plus the six variant sprites."""
    poses = tr.load_poses(dirs)
    variants = {
        (facing, lane): sprite_from_png(
            rm.EXPORT_DIR / f"{rm.variant_asset_id(facing, lane)}.png"
        )
        for facing in FACINGS
        for lane in LANES
    }
    return {"poses": poses, "variants": variants}


def stream_window(reference: dict, facing: str) -> list[dict]:
    lo, hi = STRIP_WINDOW
    return [
        entry
        for entry in pim.audit_stream(reference, facing)
        if lo <= entry["tick"] <= hi
    ]


def strip_rows(facing: str) -> int:
    ticks = STRIP_WINDOW[1] - STRIP_WINDOW[0] + 1
    columns = ticks if facing == "down" else RIGHT_STRIP_COLUMNS
    return (ticks + columns - 1) // columns


def build_strip(
    reference: dict, sprites: dict, facing: str, zone_key: str
) -> Rgba8Canvas:
    """Four aligned stream-rows (incumbent + three lanes) over one zone."""
    zone = reference["zones"][zone_key]
    window = stream_window(reference, facing)
    cell_w, cell_h = (v * STRIP_SCALE for v in pim.window_size(facing))
    columns = len(window) if facing == "down" else RIGHT_STRIP_COLUMNS
    chunk_rows = strip_rows(facing)
    row_pitch = 24 + cell_h + GUTTER
    width = MARGIN_LEFT + columns * (cell_w + GUTTER) + GUTTER
    height = 26 + 4 * chunk_rows * row_pitch
    cv = Rgba8Canvas(width, height, BG)
    draw_text(cv, 2, 2, BANNER)
    draw_text(
        cv, 2, 10,
        f"{PROTOCOL_LINE}  {facing.upper()} "
        + zone_key.upper().replace("_", " ")
        + f"  TICKS T{STRIP_WINDOW[0]:02d} TO T{STRIP_WINDOW[1]:02d}",
    )
    streams: list[tuple[str, object]] = [("INCUMBENT", None)] + [
        (LANE_LABELS[lane], sprites["variants"][(facing, lane)]) for lane in LANES
    ]
    for stream_index, (label, variant_sprite) in enumerate(streams):
        for index, entry in enumerate(window):
            chunk, col = divmod(index, columns)
            row = stream_index * chunk_rows + chunk
            x = MARGIN_LEFT + col * (cell_w + GUTTER)
            y = 26 + row * row_pitch
            if col == 0:
                draw_text(cv, x, y, label)
            draw_text(cv, x, y + 8, f"T{entry['tick']:02d} {entry['pose'].upper()}")
            sprite = sprites["poses"][facing][entry["pose"]]
            if entry["pose"] == "k0" and variant_sprite is not None:
                sprite = variant_sprite
            pane = pim.compose_tick(zone, facing, sprite, entry["offset_px"])
            cv.blit_scaled(canvas_pixels(pane), x, y + 16, STRIP_SCALE)
    return cv


def build_apng_frames(
    reference: dict, sprites: dict, facing: str, lane: str, scale: int, tag: str
) -> list[Rgba8Canvas]:
    """Side-by-side incumbent + variant panes per tick, zone_1, pre-scaled."""
    zone = reference["zones"]["zone_1"]
    win_w, win_h = pim.window_size(facing)
    frames = []
    for entry in pim.audit_stream(reference, facing):
        pose = entry["pose"]
        base_sprite = sprites["poses"][facing][pose]
        variant_sprite = (
            sprites["variants"][(facing, lane)] if pose == "k0" else base_sprite
        )
        pane_a = pim.compose_tick(zone, facing, base_sprite, entry["offset_px"])
        pane_b = pim.compose_tick(zone, facing, variant_sprite, entry["offset_px"])
        if facing == "down":
            frame = Rgba8Canvas(
                win_w * scale * 2 + GUTTER, win_h * scale + 28, BG
            )
            frame.blit_scaled(canvas_pixels(pane_a), 0, 28, scale)
            frame.blit_scaled(
                canvas_pixels(pane_b), win_w * scale + GUTTER, 28, scale
            )
            draw_text(frame, 2, 18, "INCUMBENT")
            draw_text(frame, win_w * scale + GUTTER + 2, 18, LANE_SHORT[lane])
        else:
            frame = Rgba8Canvas(
                win_w * scale, win_h * scale * 2 + GUTTER + 28, BG
            )
            frame.blit_scaled(canvas_pixels(pane_a), 0, 28, scale)
            frame.blit_scaled(
                canvas_pixels(pane_b), 0, win_h * scale + GUTTER + 28, scale
            )
            draw_text(frame, 2, 18, f"TOP INCUMBENT BOTTOM {LANE_SHORT[lane]}")
        draw_text(frame, 2, 2, "SYNTHETIC REMEDY EXP")
        draw_text(
            frame, 2, 10,
            f"T{entry['tick']:02d} {pose.upper()} {tag} {scale}X",
        )
        frames.append(frame)
    return frames


def artifact_names() -> dict[str, dict]:
    artifacts: dict[str, dict] = {}
    for facing in FACINGS:
        for zone_key in ("zone_1", "zone_2"):
            zone_tag = zone_key.replace("zone_", "z")
            artifacts[
                f"synthetic-remedy-strip-{facing}-{zone_tag}-8x.png"
            ] = {"kind": "strip", "facing": facing, "zone": zone_key}
    for lane in LANES:
        for facing in FACINGS:
            for scale in APNG_SCALES:
                artifacts[
                    f"synthetic-remedy-{lane}-{facing}-{scale}x.apng"
                ] = {
                    "kind": "apng", "facing": facing, "lane": lane,
                    "scale": scale, "speed": "real",
                }
                artifacts[
                    f"synthetic-remedy-{lane}-{facing}-slow6-{scale}x.apng"
                ] = {
                    "kind": "apng", "facing": facing, "lane": lane,
                    "scale": scale, "speed": "slow6",
                }
    return artifacts


def build_artifact(reference: dict, sprites: dict, params: dict) -> bytes:
    if params["kind"] == "strip":
        return build_strip(
            reference, sprites, params["facing"], params["zone"]
        ).encode()
    tag = "REAL 1 60" if params["speed"] == "real" else "SLOW 6 60"
    frames = build_apng_frames(
        reference, sprites, params["facing"], params["lane"], params["scale"], tag
    )
    delays = (
        apng_delays(len(frames))
        if params["speed"] == "real"
        else pim.slow_delays(len(frames))
    )
    return encode_apng(frames, delays)


# -- manifest + generation -----------------------------------------------------------


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


def declared_recolor_serialized(masks: dict) -> dict:
    serialized = {}
    for facing in FACINGS:
        for lane in LANES:
            recolor = rm.recolor_map(masks, facing, lane)
            serialized[rm.variant_asset_id(facing, lane)] = [
                [x, y, color] for (x, y), color in sorted(recolor.items())
            ]
    return serialized


def viewing_protocol() -> dict:
    protocol = pim.viewing_protocol()
    protocol["strip_window"] = (
        f"pre-registered comparison window T{STRIP_WINDOW[0]:02d}..T"
        f"{STRIP_WINDOW[1]:02d} (a0 context, a0->k0 cut, 4-tick k0 hold, "
        "k0->s0 cut, r0 context); the banked v14 strips carry the "
        "full-sequence incumbent context"
    )
    protocol["apng_layout"] = (
        "side-by-side incumbent + variant panes per frame (down horizontal, "
        "right vertical), full 21-tick stream, zone_1"
    )
    return protocol


def make_artifacts(dirs: dict[str, Path], reference: dict) -> dict:
    if not rm.MASKS_PATH.is_file():
        raise RemedyMetricsError("missing gape-masks.json; run remedy_masks first")
    masks = json.loads(rm.MASKS_PATH.read_text(encoding="utf-8"))
    sprites = load_sprites(dirs)
    report = build_report(dirs, reference, masks)
    report_a = report_bytes(report)
    report_b = report_bytes(build_report(dirs, reference, masks))
    payloads: dict[str, bytes] = {}
    deterministic = report_a == report_b
    for name, params in artifact_names().items():
        first = build_artifact(reference, sprites, params)
        second = build_artifact(reference, sprites, params)
        deterministic = deterministic and first == second
        payloads[name] = first
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_bytes(report_a)
    for name, payload in payloads.items():
        (REVIEW_DIR / name).write_bytes(payload)
    manifest = {
        "generated_by": "tools/remedy_metrics.py --make-artifacts",
        "repo_commit_at_generation": repo_commit(),
        "provenance": {
            "class": "SYNTHETIC",
            "statement": (
                "verification tables + controlled selection artifacts for "
                "the six additive DEF-1 remedy candidates, composed from "
                "banked export bytes and the candidate exports only; NOT "
                "runtime evidence; the banked k0 stays the pinned history"
            ),
        },
        "module_source_sha256": module_hashes(),
        "release": {
            "release_id": rm.RELEASE_ID,
            "release_json_sha256": (
                file_sha256(RELEASE_PATH) if RELEASE_PATH.is_file() else None
            ),
        },
        "masks_sha256": report["masks_sha256"],
        "declared_recolor": declared_recolor_serialized(masks),
        "viewing_protocol": viewing_protocol(),
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


# -- release + directory guards ------------------------------------------------------


def check_release(root: Path) -> list[str]:
    """The remedy release's own pin checker (gate-schema facts)."""
    failures: list[str] = []
    if not RELEASE_PATH.is_file():
        return [f"missing {RELEASE_PATH}"]
    manifest = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    if manifest.get("release_id") != rm.RELEASE_ID:
        failures.append("release_id != remedy-v15")
    exports = manifest.get("exports", [])
    if [e.get("asset_id") for e in exports] != variant_ids():
        failures.append("release exports do not list exactly the six variants")
    for entry in exports:
        path = root / entry["path"]
        if not path.is_file():
            failures.append(f"{entry['path']}: missing export")
        elif file_sha256(path) != entry["sha256"]:
            failures.append(f"{entry['path']}: sha256 differs from the release pin")
        if entry.get("provenance", {}).get("origin") != "procedural":
            failures.append(f"{entry.get('asset_id')}: origin must be procedural")
    for entry in manifest.get("source", {}).get("files", []):
        path = root / entry["path"]
        if not path.is_file():
            failures.append(f"{entry['path']}: missing source")
        elif file_sha256(path) != entry["sha256"]:
            failures.append(f"{entry['path']}: sha256 differs from the release pin")
    toolchain = manifest.get("toolchain", {})
    if toolchain.get("exporter_path") != rm.EXPORTER:
        failures.append("toolchain.exporter_path must be tools/export_assets.py")
    elif file_sha256(root / rm.EXPORTER) != toolchain.get("exporter_sha256"):
        failures.append("exporter pin differs from the live tools/export_assets.py")
    expected_files = {f"{asset_id}.png" for asset_id in variant_ids()}
    expected_files.add("release.json")
    on_disk = {p.name for p in rm.EXPORT_DIR.iterdir()}
    if on_disk != expected_files:
        failures.append(
            f"exports/{rm.RELEASE_ID} contents {sorted(on_disk)} != "
            f"expected {sorted(expected_files)}"
        )
    return failures


def check_calibration_dirs(root: Path) -> list[str]:
    on_disk = {
        p.name for p in (root / "exports").glob("calibration-*") if p.is_dir()
    }
    if on_disk != set(RELEASE_IDS):
        return [
            f"exports/calibration-* dirs {sorted(on_disk)} != banked "
            f"{sorted(RELEASE_IDS)}"
        ]
    return []


# -- --check --------------------------------------------------------------------------


def run_check(dirs: dict[str, Path], reference: dict) -> int:
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
            if rel == "tools/remedy_metrics.py":
                continue  # self-pin recorded at generation; git history carries it
            if rel not in pinned:
                failures.append(f"manifest is missing the {rel} pin")
            elif live.get(rel) != pinned[rel]:
                failures.append(
                    f"module drift: {rel} sha256 differs from the manifest pin"
                )
        if rm.run_check(dirs) != 0:
            failures.append("remedy_masks --check failed (masks/specs drift)")
        masks = json.loads(rm.MASKS_PATH.read_text(encoding="utf-8"))
        sprites = load_sprites(dirs)
        fresh_report = report_bytes(build_report(dirs, reference, masks))
        if not REPORT_PATH.is_file() or fresh_report != REPORT_PATH.read_bytes():
            failures.append("committed remedy-report.json differs from a fresh build")
        else:
            bars = json.loads(fresh_report).get("machine_bars", {})
            for bar, value in bars.items():
                if bar != "variant_count" and value is not True:
                    failures.append(f"machine bar failed: {bar}")
            if bars.get("variant_count") != 6:
                failures.append("machine bar failed: variant_count != 6")
        for name, params in artifact_names().items():
            path = REVIEW_DIR / name
            if not path.is_file():
                failures.append(f"missing committed artifact {name}")
                continue
            if build_artifact(reference, sprites, params) != path.read_bytes():
                failures.append(f"{name} differs from a fresh build")
        for name, digest in manifest.get("artifacts", {}).items():
            path = REVIEW_DIR / name
            if not path.is_file() or file_sha256(path) != digest:
                failures.append(f"manifest artifact pin mismatch: {name}")

    failures.extend(check_release(ROOT))
    failures.extend(check_calibration_dirs(ROOT))
    exports = check_export_pins(ROOT / "exports")
    failures.extend(exports["failures"])

    for failure in failures:
        print(f"CHECK FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        "checks passed: committed masks + specs + report + strips + APNGs "
        "regenerate byte-identically; module hash pins; machine bars 6/6; "
        f"{exports['verified']} banked export pins; remedy release pins; "
        "directory guards"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference", type=Path,
        default=ROOT / "manifests" / "render-reference.json",
    )
    parser.add_argument("--make-artifacts", action="store_true",
                        help="generate the report + selection artifacts")
    parser.add_argument("--check", action="store_true",
                        help="full self-verification (see module docstring)")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = default_dirs()
    try:
        if args.make_artifacts:
            manifest = make_artifacts(dirs, reference)
            if not manifest["determinism"]["double_build_identical"]:
                print("artifact builds are not byte-identical", file=sys.stderr)
                return 1
            print(f"wrote {REPORT_PATH}")
            print(f"wrote {MANIFEST_PATH} (+ {len(artifact_names())} artifacts)")
            return 0
        if args.check:
            return run_check(dirs, reference)
    except (RemedyMetricsError, rm.RemedyMaskError, pim.AuditError,
            tr.RecomposeError, ValueError, OSError) as exc:
        print(f"remedy metrics failed: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
