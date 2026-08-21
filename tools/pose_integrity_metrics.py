#!/usr/bin/env python3
"""Deterministic pose-integrity audit over banked export bytes (sprint 14).

The owner reported a candidate defect in the v13 demo APNG ("the head losing
a piece inside it when it does the attack movement"). This tool CHARACTERIZES
the defect class over banked bytes only — it fixes nothing, exports nothing,
adjudicates nothing:

- interior-hole detection per pose per facing: flood-fill the transparent
  field from OUTSIDE the 32x32 canvas (1px border ring, 4-connected); any
  transparent region unreachable from outside is an interior hole (count,
  area, bbox, canvas-row band);
- hole DELTAS across the banked attack sequence idle -> w0 -> a0 -> k0 ->
  s0 -> r0 -> x0 -> idle per facing (a hole present in one pose and absent
  in its neighbors is the candidate class; a hole stable across all poses
  is art, not defect);
- consecutive-pair change localization in sprite-local 32x32 space:
  4-connected clusters per cut in two classes — silhouette (opaque in
  exactly one; the banked XOR class) and recolor (opaque in both, RGB
  differs; the class every banked cut metric is blind to by construction).
  Localization is REPORTING, not a bar — no hardcoded region rectangles;
- accent-pixel table: 4-connected clusters of the frozen ramp accent
  (anticipation_metrics.ACCENT_RGB) per pose per facing, with centroids —
  eyes, feet caps, and the k0 gape marker fall out mechanically;
- context contrast reporting: WCAG contrast + RGB distance of the accent
  color against the pinned zone floor/grid palettes and the body color.

The audited tick stream is derived via the banked v13 consumer's
``select_pose`` (imported unmodified) over mechanically built attack-state
records, so the stream is BY CONSTRUCTION the declared integration mapping
that produced the demo APNG the owner watched. Playback artifacts (per-tick
8x strips over both zone palettes; APNGs at exact 1/60 s and a slowed 6/60 s
variant, 4x and 8x pre-scaled integer NN) compose banked export bytes via
the banked compositor/encoder and carry SYNTHETIC/EXP labels in filename,
manifest, and pixels.

``--check`` verifies: committed artifacts regenerate byte-identically,
module hash pins (banked modules unmodified), the 26 banked export pins,
the zero-new-exports guard, 22/22 sprite coverage, and the pre-registered
cut-sequence consistency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import deque
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import track_recompose as tr  # noqa: E402  (banked v13 consumer, unmodified)
from anticipation_metrics import ACCENT_RGB  # noqa: E402  (banked)
from feedback_metrics import contrast_ratio  # noqa: E402  (banked)
from make_contact_sheet import GUTTER, TILE, load_reference  # noqa: E402
from make_cross_seam_timeline import compose_cell  # noqa: E402  (banked v9)
from make_grammar_timeline import (  # noqa: E402  (banked encoder + delays)
    APNG_LAST_DELAY,
    APNG_TICK_DELAY,
    apng_delays,
    canvas_pixels,
    encode_apng,
)
from make_seam_timeline import (  # noqa: E402  (banked pose IO + font)
    POSE_DIRS,
    STRIP,
    default_dirs,
    draw_text,
    pose_filename,
)
from png_reader import read_rgba  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from seam_metrics import check_export_pins  # noqa: E402

CANVAS = 32
FACINGS = ("down", "right")
FACING_VECTORS = {"down": (0, 1), "right": (1, 0)}
# The pre-registered cut sequence (rationale; the audit's machine bar).
SEQUENCE = ("idle", "w0", "a0", "k0", "s0", "r0", "x0", "idle")
IDLE_PRE_TICKS = 2
IDLE_POST_TICKS = 2
WINDOW_TILES = 3           # [approach | creature | lunge room] along facing
BASE_TILE_INDEX = 1        # the creature's home tile inside the window
SLOW_TICK_DELAY = (6, 60)  # declared slowed variant: 6x slower, integer ticks
STRIP_SCALE = 8
APNG_SCALES = (4, 8)
STRIP_MAX_WIDTH = 4000     # keep committed strips under the png_reader cap
MARGIN_LEFT = 8
BG = (12, 10, 14, 255)

AUDIT_DIR = ROOT / "reviews" / "defect-audit-v14"
REPORT_PATH = AUDIT_DIR / "pose-integrity-report.json"
MANIFEST_PATH = AUDIT_DIR / "defect-manifest.json"

BANNER = "SYNTHETIC AUDIT EXP BANKED BYTES ZERO ADJUDICATION"
PROTOCOL_LINE = "PROTOCOL 100 PCT ZOOM NO FIT 8X NN PRESCALED"

# Every tools/ module this audit imports (directly or transitively) — all
# hash-pinned in the manifest and re-verified by --check and the tests.
MODULE_SOURCE_FILES = (
    "tools/pose_integrity_metrics.py",
    "tools/track_recompose.py",
    "tools/make_turn_timeline.py",
    "tools/make_corner_timeline.py",
    "tools/make_cross_seam_timeline.py",
    "tools/make_grammar_timeline.py",
    "tools/make_seam_timeline.py",
    "tools/make_contact_sheet.py",
    "tools/make_feedback_sheet.py",
    "tools/make_anticipation_sheet.py",
    "tools/make_motion_sheet.py",
    "tools/anticipation_metrics.py",
    "tools/feedback_metrics.py",
    "tools/motion_metrics.py",
    "tools/seam_metrics.py",
    "tools/timeline_metrics.py",
    "tools/png_reader.py",
    "tools/png_writer.py",
)


class AuditError(ValueError):
    """A deterministic audit failure."""


# -- pixel primitives (pure functions over raw RGBA bytes) ---------------------


def load_pose_raw(dirs: dict[str, Path], pose: str, facing: str) -> bytes:
    path = dirs[POSE_DIRS[pose]] / pose_filename(pose, facing)
    width, height, raw = read_rgba(path)
    if (width, height) != (CANVAS, CANVAS):
        raise AuditError(f"{path.name}: expected {CANVAS}x{CANVAS}")
    return raw


def is_opaque(raw: bytes, x: int, y: int) -> bool:
    return raw[(y * CANVAS + x) * 4 + 3] == 255


def rgb_at(raw: bytes, x: int, y: int) -> tuple[int, int, int]:
    offset = (y * CANVAS + x) * 4
    return (raw[offset], raw[offset + 1], raw[offset + 2])


def cluster_cells(cells: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """4-connected components of a cell set, deterministic order."""
    components: list[list[tuple[int, int]]] = []
    seen: set[tuple[int, int]] = set()
    for cell in sorted(cells):
        if cell in seen:
            continue
        queue = deque([cell])
        seen.add(cell)
        component = []
        while queue:
            cx, cy = queue.popleft()
            component.append((cx, cy))
            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if (nx, ny) in cells and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        components.append(sorted(component))
    return components


def cluster_summary(component: list[tuple[int, int]]) -> dict:
    xs = [x for x, _ in component]
    ys = [y for _, y in component]
    return {
        "area": len(component),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "row_band": [min(ys), max(ys)],
    }


def interior_holes(raw: bytes) -> list[dict]:
    """Transparent regions unreachable from outside the canvas.

    Flood-fill over non-opaque cells from a 1px border ring (4-connected);
    the convention is fixed in the rationale: a diagonally-sealed enclosure
    counts as interior; any transparent path to the border makes a region
    exterior; alpha 255 is opaque, anything else is transparent.
    """
    size = CANVAS + 2  # border ring coordinates: grid[-1..CANVAS] shifted +1
    reachable = [[False] * size for _ in range(size)]
    queue = deque([(0, 0)])
    reachable[0][0] = True
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 <= nx < size and 0 <= ny < size) or reachable[ny][nx]:
                continue
            ix, iy = nx - 1, ny - 1
            if 0 <= ix < CANVAS and 0 <= iy < CANVAS and is_opaque(raw, ix, iy):
                continue
            reachable[ny][nx] = True
            queue.append((nx, ny))
    unreachable = {
        (x, y)
        for y in range(CANVAS)
        for x in range(CANVAS)
        if not is_opaque(raw, x, y) and not reachable[y + 1][x + 1]
    }
    return [
        {**cluster_summary(component), "pixels": component}
        for component in cluster_cells(unreachable)
    ]


def accent_clusters(raw: bytes) -> list[dict]:
    cells = {
        (x, y)
        for y in range(CANVAS)
        for x in range(CANVAS)
        if is_opaque(raw, x, y) and rgb_at(raw, x, y) == ACCENT_RGB
    }
    out = []
    for component in cluster_cells(cells):
        summary = cluster_summary(component)
        summary["centroid"] = [
            round(sum(x for x, _ in component) / len(component), 2),
            round(sum(y for _, y in component) / len(component), 2),
        ]
        out.append(summary)
    return out


def pose_report(raw: bytes) -> dict:
    opaque = [
        (x, y) for y in range(CANVAS) for x in range(CANVAS) if is_opaque(raw, x, y)
    ]
    histogram: dict[str, int] = {}
    for x, y in opaque:
        r, g, b = rgb_at(raw, x, y)
        histogram[f"#{r:02x}{g:02x}{b:02x}"] = (
            histogram.get(f"#{r:02x}{g:02x}{b:02x}", 0) + 1
        )
    xs = [x for x, _ in opaque]
    ys = [y for _, y in opaque]
    holes = interior_holes(raw)
    return {
        "mass": len(opaque),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "color_histogram": dict(sorted(histogram.items())),
        "interior_holes": [
            {k: v for k, v in hole.items() if k != "pixels"} for hole in holes
        ],
        "accent_clusters": accent_clusters(raw),
    }


def cut_changes(raw_a: bytes, raw_b: bytes) -> dict:
    """Changed-pixel clusters between two canvases, sprite-local space."""
    silhouette: set[tuple[int, int]] = set()
    recolor: set[tuple[int, int]] = set()
    for y in range(CANVAS):
        for x in range(CANVAS):
            a, b = is_opaque(raw_a, x, y), is_opaque(raw_b, x, y)
            if a != b:
                silhouette.add((x, y))
            elif a and rgb_at(raw_a, x, y) != rgb_at(raw_b, x, y):
                recolor.add((x, y))
    return {
        "silhouette_px": len(silhouette),
        "recolor_px": len(recolor),
        "silhouette_clusters": [
            cluster_summary(c) for c in cluster_cells(silhouette)
        ],
        "recolor_clusters": [cluster_summary(c) for c in cluster_cells(recolor)],
    }


def hole_deltas(holes_a: list[dict], holes_b: list[dict]) -> dict:
    """Match holes across a cut by pixel-set overlap (appear/disappear/stable)."""
    pixels_a = [set(h["pixels"]) for h in holes_a]
    pixels_b = [set(h["pixels"]) for h in holes_b]
    stable_a = {
        i for i, pa in enumerate(pixels_a) if any(pa & pb for pb in pixels_b)
    }
    stable_b = {
        j for j, pb in enumerate(pixels_b) if any(pb & pa for pa in pixels_a)
    }

    def strip(hole: dict) -> dict:
        return {k: v for k, v in hole.items() if k != "pixels"}

    return {
        "appear": [strip(h) for j, h in enumerate(holes_b) if j not in stable_b],
        "disappear": [strip(h) for i, h in enumerate(holes_a) if i not in stable_a],
        "stable": [strip(holes_b[j]) for j in sorted(stable_b)],
    }


# -- the audited stream (derived via the banked v13 mapping) --------------------


def audit_constants(reference: dict) -> dict:
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    return {
        "step_frames": timing["step_frames"]["value"],
        "windup_frames": timing["windup_frames"]["value"],
        "active_frames": timing["active_frames"]["value"],
        "recovery_frames": timing["recovery_frames"]["value"],
        "windup_px": lunge["windup_px"],
        "active_px": lunge["active_px"],
    }


def attack_records(constants: dict, facing: str) -> list[dict]:
    """Mechanical per-tick attack-state records: idle context, then the
    pinned windup/active/recovery countdowns, then idle context."""
    fx, fy = FACING_VECTORS[facing]

    def record(state: str, frames_left: int) -> dict:
        return {
            "tile_x": 0, "tile_y": 0, "px": 0.0, "py": 0.0,
            "facing": [fx, fy],
            "tween_left": 0, "tween_total": 0,
            "attack_state": state,
            "current_action": None if state == "idle" else "attack",
            "state_frames": frames_left,
            "hp": 80, "iframes": 0,
        }

    records = [record("idle", 0)] * IDLE_PRE_TICKS
    records = list(records)
    for state, total in (
        ("windup", constants["windup_frames"]),
        ("active", constants["active_frames"]),
        ("recovery", constants["recovery_frames"]),
    ):
        for left in range(total, 0, -1):
            records.append(record(state, left))
    records.extend(record("idle", 0) for _ in range(IDLE_POST_TICKS))
    return records


def audit_stream(reference: dict, facing: str) -> list[dict]:
    """(tick, pose, offset_px) per tick, poses chosen by the banked v13
    ``select_pose`` — the declared integration mapping, unmodified."""
    constants = audit_constants(reference)
    stream = []
    for tick, record in enumerate(attack_records(constants, facing)):
        pose, pose_facing, offset = tr.select_pose(record, constants)
        if pose_facing != facing:
            raise AuditError(f"facing drift at tick {tick}")
        stream.append({"tick": tick, "pose": pose, "offset_px": offset})
    return stream


def stream_classes(stream: list[dict]) -> tuple[str, ...]:
    classes: list[str] = []
    for entry in stream:
        if not classes or classes[-1] != entry["pose"]:
            classes.append(entry["pose"])
    return tuple(classes)


def stream_cuts(stream: list[dict]) -> list[dict]:
    cuts = []
    for previous, entry in zip(stream, stream[1:]):
        if previous["pose"] != entry["pose"]:
            cuts.append(
                {
                    "from_pose": previous["pose"], "to_pose": entry["pose"],
                    "from_tick": previous["tick"], "to_tick": entry["tick"],
                    "offset_from": previous["offset_px"],
                    "offset_to": entry["offset_px"],
                }
            )
    return cuts


# -- the report ------------------------------------------------------------------


def context_contrast(reference: dict) -> dict:
    body = tuple(reference["primitive_body"]["body_rgb"])
    table = {}
    for zone_key in ("zone_1", "zone_2"):
        zone = reference["zones"][zone_key]
        for surface in ("floor", "grid"):
            rgb = tuple(zone[surface])
            distance = sum((a - b) ** 2 for a, b in zip(ACCENT_RGB, rgb)) ** 0.5
            table[f"accent_vs_{zone_key}_{surface}"] = {
                "contrast_ratio": contrast_ratio(ACCENT_RGB, rgb),
                "rgb_distance": round(distance, 1),
            }
    table["accent_vs_body"] = {
        "contrast_ratio": contrast_ratio(ACCENT_RGB, body),
        "rgb_distance": round(
            sum((a - b) ** 2 for a, b in zip(ACCENT_RGB, body)) ** 0.5, 1
        ),
    }
    return table


def build_report(reference: dict, dirs: dict[str, Path]) -> dict:
    poses: dict[str, dict] = {}
    raws: dict[str, dict[str, bytes]] = {}
    for facing in FACINGS:
        raws[facing] = {pose: load_pose_raw(dirs, pose, facing) for pose in STRIP}
        poses[facing] = {
            pose: pose_report(raws[facing][pose]) for pose in STRIP
        }
    sequence: dict[str, dict] = {}
    for facing in FACINGS:
        stream = audit_stream(reference, facing)
        classes = stream_classes(stream)
        if classes != SEQUENCE:
            raise AuditError(
                f"stream classes {classes} != pre-registered {SEQUENCE}"
            )
        cuts = []
        for cut in stream_cuts(stream):
            raw_from = raws[facing][cut["from_pose"]]
            raw_to = raws[facing][cut["to_pose"]]
            entry = dict(cut)
            entry.update(cut_changes(raw_from, raw_to))
            entry["holes"] = hole_deltas(
                interior_holes(raw_from), interior_holes(raw_to)
            )
            entry["accent_px_from"] = sum(
                c["area"] for c in poses[facing][cut["from_pose"]]["accent_clusters"]
            )
            entry["accent_px_to"] = sum(
                c["area"] for c in poses[facing][cut["to_pose"]]["accent_clusters"]
            )
            cuts.append(entry)
        sequence[facing] = {"stream": stream, "cuts": cuts}
    analyzed = sum(len(v) for v in poses.values())
    return {
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tools/pose_integrity_metrics.py --make-audit",
            "statement": (
                "deterministic measurement over banked export bytes; NOT "
                "runtime evidence; answers ZERO register items; fixes nothing"
            ),
        },
        "accent_rgb": list(ACCENT_RGB),
        "context_contrast": context_contrast(reference),
        "constants": audit_constants(reference),
        "sequence_classes": list(SEQUENCE),
        "coverage": {"sprites_analyzed": analyzed, "expected": len(STRIP) * 2},
        "poses": poses,
        "sequence": sequence,
    }


def report_bytes(report: dict) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")


# -- playback artifacts ----------------------------------------------------------


def window_size(facing: str) -> tuple[int, int]:
    if facing == "down":
        return TILE, WINDOW_TILES * TILE
    return WINDOW_TILES * TILE, TILE


def compose_tick(
    zone: dict, facing: str, sprite, offset_px: int
) -> Rgba8Canvas:
    """One 1x window: creature at its home tile plus the lunge offset."""
    width, height = window_size(facing)
    fx, fy = FACING_VECTORS[facing]
    dx = BASE_TILE_INDEX * TILE * fx + offset_px * fx
    dy = BASE_TILE_INDEX * TILE * fy + offset_px * fy
    return compose_cell(zone, width, height, sprite, dx, dy)


def strip_columns(facing: str) -> int:
    cell_w = window_size(facing)[0] * STRIP_SCALE
    return max(1, (STRIP_MAX_WIDTH - MARGIN_LEFT) // (cell_w + GUTTER))


def build_strip(
    reference: dict, poses: dict, facing: str, zone_key: str
) -> Rgba8Canvas:
    """Per-tick 8x NN strip over one zone palette, chunked into rows."""
    zone = reference["zones"][zone_key]
    stream = audit_stream(reference, facing)
    cell_w, cell_h = (v * STRIP_SCALE for v in window_size(facing))
    columns = strip_columns(facing)
    rows = (len(stream) + columns - 1) // columns
    width = MARGIN_LEFT + columns * (cell_w + GUTTER) + GUTTER
    height = 26 + rows * (16 + cell_h + GUTTER)
    cv = Rgba8Canvas(width, height, BG)
    draw_text(cv, 2, 2, BANNER)
    draw_text(
        cv, 2, 10,
        f"{PROTOCOL_LINE}  {facing.upper()} "
        + zone_key.upper().replace("_", " "),
    )
    for index, entry in enumerate(stream):
        row, col = divmod(index, columns)
        x = MARGIN_LEFT + col * (cell_w + GUTTER)
        y = 26 + row * (16 + cell_h + GUTTER)
        draw_text(cv, x, y, f"T{entry['tick']:02d} {entry['pose'].upper()}")
        pane = compose_tick(zone, facing, poses[facing][entry["pose"]],
                            entry["offset_px"])
        cv.blit_scaled(canvas_pixels(pane), x, y + 8, STRIP_SCALE)
    return cv


def build_apng_frames(
    reference: dict, poses: dict, facing: str, scale: int, tag: str
) -> list[Rgba8Canvas]:
    """Pre-scaled integer-NN frames over zone_1 with a drawn label band."""
    zone = reference["zones"]["zone_1"]
    frames = []
    for entry in audit_stream(reference, facing):
        pane = compose_tick(zone, facing, poses[facing][entry["pose"]],
                            entry["offset_px"])
        width, height = window_size(facing)
        frame = Rgba8Canvas(width * scale, height * scale + 20, BG)
        frame.blit_scaled(canvas_pixels(pane), 0, 20, scale)
        draw_text(frame, 2, 2, "SYNTHETIC AUDIT EXP")
        draw_text(
            frame, 2, 10,
            f"T{entry['tick']:02d} {entry['pose'].upper()} {tag} {scale}X",
        )
        frames.append(frame)
    return frames


def slow_delays(count: int) -> list[tuple[int, int]]:
    """Declared slowed delay list: 6/60 s per tick, banked final hold."""
    return [SLOW_TICK_DELAY] * (count - 1) + [APNG_LAST_DELAY]


def artifact_names() -> dict[str, dict]:
    """Every playback artifact: name -> build parameters."""
    artifacts: dict[str, dict] = {}
    for facing in FACINGS:
        for zone_key in ("zone_1", "zone_2"):
            zone_tag = zone_key.replace("zone_", "z")
            artifacts[f"synthetic-audit-strip-{facing}-{zone_tag}-8x.png"] = {
                "kind": "strip", "facing": facing, "zone": zone_key,
            }
        for scale in APNG_SCALES:
            artifacts[f"synthetic-audit-attack-{facing}-{scale}x.apng"] = {
                "kind": "apng", "facing": facing, "scale": scale,
                "speed": "real",
            }
            artifacts[f"synthetic-audit-attack-slow6-{facing}-{scale}x.apng"] = {
                "kind": "apng", "facing": facing, "scale": scale,
                "speed": "slow6",
            }
    return artifacts


def build_artifact(reference: dict, poses: dict, params: dict) -> bytes:
    if params["kind"] == "strip":
        return build_strip(reference, poses, params["facing"], params["zone"]).encode()
    tag = "REAL 1 60" if params["speed"] == "real" else "SLOW 6 60"
    frames = build_apng_frames(
        reference, poses, params["facing"], params["scale"], tag
    )
    delays = (
        apng_delays(len(frames))
        if params["speed"] == "real"
        else slow_delays(len(frames))
    )
    return encode_apng(frames, delays)


# -- manifest + generation -------------------------------------------------------


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


def viewing_protocol() -> dict:
    ticks = IDLE_PRE_TICKS + 5 + 4 + 8 + IDLE_POST_TICKS
    return {
        "statement": (
            "view at 100% viewer zoom with fit-to-window OFF; all scaling is "
            "pre-baked integer nearest-neighbor (4x and 8x); percepts "
            "reproducible only under resampled viewing are viewer-domain by "
            "the pre-registered taxonomy"
        ),
        "strip_scale": STRIP_SCALE,
        "apng_scales": list(APNG_SCALES),
        "apng_real_delays": (
            f"exact {APNG_TICK_DELAY[0]}/{APNG_TICK_DELAY[1]} s per tick x "
            f"{ticks - 1} + {APNG_LAST_DELAY[0]}/{APNG_LAST_DELAY[1]} s final "
            "hold (banked apng_delays)"
        ),
        "apng_slow_delays": (
            f"{SLOW_TICK_DELAY[0]}/{SLOW_TICK_DELAY[1]} s per tick x "
            f"{ticks - 1} + {APNG_LAST_DELAY[0]}/{APNG_LAST_DELAY[1]} s final "
            "hold (slowed 6x, integer tick multiple)"
        ),
        "apng_zone": "zone_1",
        "strip_zones": ["zone_1", "zone_2"],
    }


def make_audit(reference: dict, dirs: dict[str, Path]) -> dict:
    poses = tr.load_poses(dirs)
    report = build_report(reference, dirs)
    report_a = report_bytes(report)
    report_b = report_bytes(build_report(reference, dirs))
    payloads: dict[str, bytes] = {}
    deterministic = report_a == report_b
    for name, params in artifact_names().items():
        first = build_artifact(reference, poses, params)
        second = build_artifact(reference, poses, params)
        deterministic = deterministic and first == second
        payloads[name] = first
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_bytes(report_a)
    for name, payload in payloads.items():
        (AUDIT_DIR / name).write_bytes(payload)
    manifest = {
        "generated_by": "tools/pose_integrity_metrics.py --make-audit",
        "repo_commit_at_generation": repo_commit(),
        "provenance": {
            "class": "SYNTHETIC",
            "statement": (
                "controlled playback + inspection artifacts composed from "
                "banked export bytes only; NOT runtime evidence; answers "
                "ZERO register items; fixes nothing"
            ),
        },
        "module_source_sha256": module_hashes(),
        "audit": {
            "mapping_id": tr.MAPPING_ID,
            "sequence_classes": list(SEQUENCE),
            "tick_count": IDLE_PRE_TICKS + 5 + 4 + 8 + IDLE_POST_TICKS,
            "constants": audit_constants(reference),
            "window_tiles": WINDOW_TILES,
            "base_tile_index": BASE_TILE_INDEX,
        },
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


# -- --check ---------------------------------------------------------------------


def run_check(reference: dict, dirs: dict[str, Path]) -> int:
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
            if rel == "tools/pose_integrity_metrics.py":
                continue  # self-pin recorded at generation; git history carries it
            if rel not in pinned:
                failures.append(f"manifest is missing the {rel} pin")
            elif live.get(rel) != pinned[rel]:
                failures.append(
                    f"module drift: {rel} sha256 differs from the manifest pin "
                    "(banked modules must stay unmodified)"
                )
        poses = tr.load_poses(dirs)
        fresh_report = report_bytes(build_report(reference, dirs))
        if not REPORT_PATH.is_file() or fresh_report != REPORT_PATH.read_bytes():
            failures.append(
                "committed pose-integrity-report.json differs from a fresh build"
            )
        for name, params in artifact_names().items():
            path = AUDIT_DIR / name
            if not path.is_file():
                failures.append(f"missing committed artifact {name}")
                continue
            if build_artifact(reference, poses, params) != path.read_bytes():
                failures.append(f"{name} differs from a fresh build")
        for name, digest in manifest.get("artifacts", {}).items():
            path = AUDIT_DIR / name
            if not path.is_file() or file_sha256(path) != digest:
                failures.append(f"manifest artifact pin mismatch: {name}")
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if (
            REPORT_PATH.is_file()
        ) else {}
        coverage = report.get("coverage", {})
        if coverage.get("sprites_analyzed") != len(STRIP) * 2:
            failures.append(
                f"coverage {coverage.get('sprites_analyzed')} != {len(STRIP) * 2}"
            )
        if tuple(report.get("sequence_classes", ())) != SEQUENCE:
            failures.append("report sequence_classes != pre-registered SEQUENCE")

    exports = check_export_pins(ROOT / "exports")
    failures.extend(exports["failures"])
    if (ROOT / "exports" / "defect-audit-v14").exists():
        failures.append("exports/defect-audit-v14 exists - this sprint banks no exports")

    for failure in failures:
        print(f"CHECK FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        "checks passed: committed report + strips + APNGs regenerate "
        "byte-identically; module hash pins; "
        f"{exports['verified']} banked export pins; zero-new-exports; "
        f"coverage {len(STRIP) * 2}/22; sequence consistency"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = default_dirs()
    for key, value in defaults.items():
        flag = "--" + key.replace("_dir", "-exports").replace("_", "-")
        parser.add_argument(flag, dest=key, type=Path, default=value)
    parser.add_argument(
        "--reference", type=Path,
        default=ROOT / "manifests" / "render-reference.json",
    )
    parser.add_argument("--make-audit", action="store_true",
                        help="generate the audit report + playback artifacts")
    parser.add_argument("--check", action="store_true",
                        help="full self-verification (see module docstring)")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        if args.make_audit:
            manifest = make_audit(reference, dirs)
            if not manifest["determinism"]["double_build_identical"]:
                print("audit builds are not byte-identical", file=sys.stderr)
                return 1
            print(f"wrote {REPORT_PATH}")
            print(f"wrote {MANIFEST_PATH} (+ {len(artifact_names())} artifacts)")
            return 0
        if args.check:
            return run_check(reference, dirs)
    except (AuditError, tr.RecomposeError, ValueError, OSError) as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
