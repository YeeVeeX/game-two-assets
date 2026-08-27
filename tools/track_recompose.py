#!/usr/bin/env python3
"""Reference consumer for the DRAFT state-track schema (sprint 13).

The repo-side half of the banked runtime-replay-capture design
(docs/replay-capture-design.md section 6.1): parse and validate a per-tick
state track against the DRAFT schema (docs/state-track-schema.md), map each
tick's engine state onto banked frame selection under the DECLARED
INTEGRATION MAPPING, and compose native-scale frames, a contact sheet and an
exact-1/60s APNG from banked export bytes only. ZERO new pixels; zero
exports; zero adjudication — no artifact this tool produces answers any
lettered register item, and every synthetic artifact is labeled SYNTHETIC in
its filename, its manifest, and its pixels.

The mapping (`declared-integration-mapping-v1`) is composed of banked pieces
imported unmodified (the corner_metrics import discipline):

- walk: the banked v1 mapping f0x4/f1x3/f2x3/f3x3 via ``walk_frame_index``
  over the step's advances, k = tween_total - tween_left; commit ticks
  (tween_left == tween_total) and completed steps (tween_left == 0) draw the
  standing pose (f3 is the idle byte-copy, banked law);
- attack: the banked lane-B timeline (v7 winner, carried v9) —
  w0 | a0x4 | k0x4 | s0 | r0x6 | x0 over windup/active/recovery, indexed by
  into_phase = pinned_phase_frames - state_frames; lunge offsets
  windup_px/active_px along facing (render-reference, value-anchored to
  renderer.rb lunge_offset at the pin); attack pose priority over walk
  frames (the banked moving-recovery finding);
- facing: [0,1]=down, [1,0]=right; anything else is a typed refusal (no
  mirrored or diagonal banked row exists);
- position: draw = round_half_up(px/py) - view origin + lunge along facing;
- composition/encoding: the banked v9 ``compose_cell``, the banked
  ``Rgba8Canvas`` writer, the banked ``encode_apng`` at exact 1/60 s.

The mapping is VERSION-PINNED in every artifact (mapping id + repo commit +
SHA-256 of every imported mapping-source module) so a future mapping
revision can never silently re-ground an old artifact (design section 6.1,
council-adopted duty).

``--check`` runs the full self-verification: schema validation of the
committed demo track, the two equivalence proofs (byte half: every Model-A
lane cell of the committed v10/v11 sheets recomposed byte-identically from
mechanically derived tracks — 672 cells; plan half: the mapping's decision
stream equals the banked v9 lane_tick outputs — 340 records), double-build
determinism against the committed demo bytes, banked-module hash pins, and
the standing zero-new-exports guard.

Schema v1 (v30 adaptation): the game seat pinned the schema at tool-spec
time (s84 T2 delivery; spec section 5 at game-two ``2627ed0``) and this
consumer adapted to the pin per draft-1's own resolution rule — draft-1
validation law is UNCHANGED, dispatched by ``schema_version``. v1 deltas:
per-kit ``constants`` map covering exactly the roster's kits (selection
rule: ``constants[creature.kit]``; the lunge px pair dropped from tracks —
draw offsets stay mapping-side via render-reference); UNION roster (per-tick
presence maps; absence = death/despawn/not-yet-spawned — information, not
noise); ``possessed`` boolean per record; per-tick ``masks`` required;
windowed frame domain 1..ticks_executed (frame 0 is constructor state);
``provenance.bundle_id`` required (a track never self-certifies). RUNTIME
tracks are admitted ONLY through ``verify_runtime_intake`` — the design
section 5 evidence gate over ``evidence/replay/<bundle-id>/`` (manifest +
PASS verification receipt with runs >= 2 + sidecar-matched track bytes);
synthetic/fixture tracks are never runtime evidence (v13 law carried).
``--decisions`` emits the TEXT decision stream (validation verdict + pose /
typed-refusal statistics); it composes zero pixels.

v31 RUNTIME-EXP extraction (pre-registered in
``reviews/runtime-recompose-v31/rationale.md``): ``--make-runtime-artifacts``
renders ONE intaken RUNTIME track's possessed creature over a declared
sub-window as EXP-class instrument-readiness artifacts - subject law
(exactly one stable possessed holder), striker kit gate, longest
refusal-free span containing a complete attack cycle, whole-TILE padded
bounding-box window, additive district palette merged OPT-IN from
``manifests/zone-palette-district.json`` (``load_zone_palette``; the plain
reference keeps the banked-zones-only refusal), double-build determinism,
and the RUNTIME-EXP disclosure in pixels, filenames, and manifest. Every
artifact answers ZERO register items. ``--decisions --creature`` emits the
per-creature TEXT decision stream (the subject filter).
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_corner_timeline as v11  # noqa: E402  (banked, imported unmodified)
import make_cross_seam_timeline as v9  # noqa: E402  (banked, imported unmodified)
import make_turn_timeline as v10  # noqa: E402  (banked, imported unmodified)
from make_contact_sheet import GUTTER, TILE, load_reference  # noqa: E402
from make_cross_seam_timeline import compose_cell  # noqa: E402
from make_grammar_timeline import (  # noqa: E402
    apng_delays,
    canvas_pixels,
    encode_apng,
    round_half_up,
    walk_frame_index,
)
from make_seam_timeline import (  # noqa: E402
    POSE_DIRS,
    STRIP,
    default_dirs,
    draw_text,
    pose_filename,
)
from png_reader import read_rgba  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from seam_metrics import check_export_pins  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

MAPPING_ID = "declared-integration-mapping-v1"
SCHEMA_VERSION = "draft-1"  # this repo's proposal; the demo bundle stays draft-1
SCHEMA_V1 = "1"  # pinned by the game seat at tool-spec time (s84, spec section 5)
SUPPORTED_SCHEMA_VERSIONS = (SCHEMA_VERSION, SCHEMA_V1)
TRACK_CLASSES = ("SYNTHETIC", "RUNTIME")
ATTACK_STATES = ("idle", "windup", "active", "recovery")
FACING_NAMES = {(0, 1): "down", (1, 0): "right"}
DEMO_DIR = ROOT / "reviews" / "recompose-v13"
DEMO_TRACK = DEMO_DIR / "synthetic-demo-track.json"
DEMO_SHEET = DEMO_DIR / "synthetic-demo-sheet.png"
DEMO_APNG = DEMO_DIR / "synthetic-demo.apng"
DEMO_MANIFEST = DEMO_DIR / "recompose-manifest.json"
STALE_EXPORT_DIRS = (
    "calibration-v9", "calibration-v10", "calibration-v11", "recompose-v13",
)
# Every module the mapping imports its behavior from (hash-pinned per run).
MAPPING_SOURCE_FILES = (
    "tools/track_recompose.py",
    "tools/make_turn_timeline.py",
    "tools/make_corner_timeline.py",
    "tools/make_cross_seam_timeline.py",
    "tools/make_grammar_timeline.py",
    "tools/make_seam_timeline.py",
    "tools/make_contact_sheet.py",
    "tools/png_writer.py",
    "tools/png_reader.py",
)
APNG_SCALE = 4
V11_MODEL_A_LANES = ("CORNER", "CONTROL", "DEGEN")
# f3 is the idle byte-copy (banked law): pose labels compare at byte-class.
BYTE_CLASS = {"f3": "idle"}

# -- v31 RUNTIME-EXP single-creature instrument constants ----------------------
# Pre-registered in reviews/runtime-recompose-v31/rationale.md: extraction,
# span, window, palette route, disclosure strings. EXP-class: every artifact
# answers ZERO register items and says so in pixels, filename, and manifest.
RUNTIME_DIR = ROOT / "reviews" / "runtime-recompose-v31"
RUNTIME_MANIFEST = RUNTIME_DIR / "runtime-exp-manifest.json"
RUNTIME_SHEET = RUNTIME_DIR / "runtime-exp-attack-sheet.png"
RUNTIME_APNG_NATIVE = RUNTIME_DIR / "runtime-exp-attack-native.apng"
RUNTIME_APNG_ZOOM = RUNTIME_DIR / "runtime-exp-attack-zoom4.apng"
RUNTIME_DECISIONS = RUNTIME_DIR / "decisions-subject.json"
DISTRICT_PALETTE = ROOT / "manifests" / "zone-palette-district.json"
ZONE_ENTRY_KEYS = ("floor", "grid", "wall", "motif", "transition")
RUNTIME_EXP_DISCLOSURE = (
    "RUNTIME-EXP: captured state is real; frame selection is the "
    "proposal's (declared-integration-mapping-v1); single-creature window, "
    "neighbors omitted; not the live camera; answers ZERO register items."
)
SHEET_BANNER_1 = (
    "RUNTIME EXP  CAPTURED STATE IS REAL  FRAME SELECTION IS THE PROPOSAL"
)
SHEET_BANNER_2 = (
    "DECLARED INTEGRATION MAPPING 1  SINGLE CREATURE WINDOW  "
    "NEIGHBORS OMITTED  NOT THE GAME CAMERA"
)
SHEET_FOOTER = "ANSWERS ZERO REGISTER ITEMS"
APNG_HEADER_1 = "RUNTIME EXP  MAPPING 1"
APNG_HEADER_2 = "ANSWERS ZERO REGISTER ITEMS"
SHEET_CELLS_PER_ROW = 10

REQUIRED_TOP = (
    "schema_version", "class", "tick_ms", "zone", "view", "constants",
    "creatures", "ticks", "provenance",
)
REQUIRED_CONSTANTS = (
    "step_frames", "windup_frames", "active_frames", "recovery_frames",
    "windup_px", "active_px",
)
REQUIRED_RECORD = (
    "tile_x", "tile_y", "px", "py", "facing", "tween_left", "tween_total",
    "attack_state", "current_action", "state_frames", "hp", "iframes",
)
REQUIRED_RECORD_V1 = REQUIRED_RECORD + ("possessed",)
REQUIRED_KIT_CONSTANTS = (
    "step_frames", "windup_frames", "active_frames", "recovery_frames",
)
EVIDENCE_REPLAY = ROOT / "evidence" / "replay"


class RecomposeError(ValueError):
    """Unreadable, schema-violating, or unmappable track input."""


# -- schema validation (loud, typed) -------------------------------------------


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value) -> bool:
    return _is_int(value) or isinstance(value, float)


def validate_track(track: dict) -> list[str]:
    """Typed violations (empty == valid). Every message is prefixed with its
    refusal class so downstream tooling can sort refusals mechanically.
    Dispatches on schema_version: draft-1 law unchanged; v1 = the s84 pin
    (per-kit constants, union roster, possessed, masks, 1-based frames,
    provenance.bundle_id)."""
    errors: list[str] = []
    if not isinstance(track, dict):
        return ["bad-type: track root must be an object"]
    for field in REQUIRED_TOP:
        if field not in track:
            errors.append(f"missing-field: track.{field}")
    if errors:
        return errors
    if not isinstance(track["schema_version"], str) or not track["schema_version"]:
        return ["bad-type: track.schema_version must be a non-empty string"]
    if track["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS:
        return [
            f"bad-enum: track.schema_version {track['schema_version']!r} not "
            f"in {SUPPORTED_SCHEMA_VERSIONS} (validation law dispatches on "
            "the version; an unknown version has no law to validate under)"
        ]
    v1 = track["schema_version"] == SCHEMA_V1
    if track["class"] not in TRACK_CLASSES:
        errors.append(
            f"bad-enum: track.class {track['class']!r} not in {TRACK_CLASSES}"
        )
    if not _is_number(track["tick_ms"]) or track["tick_ms"] <= 0:
        errors.append("bad-type: track.tick_ms must be a positive number")
    view = track["view"]
    if (
        not isinstance(view, dict)
        or not isinstance(view.get("origin_px"), list)
        or len(view["origin_px"]) != 2
        or not all(_is_int(v) for v in view["origin_px"])
        or not _is_int(view.get("width"))
        or not _is_int(view.get("height"))
        or view.get("width", 0) < TILE
        or view.get("height", 0) < TILE
    ):
        errors.append(
            "bad-type: track.view needs integer origin_px [x, y] and "
            f"integer width/height >= {TILE}"
        )
    constants = track["constants"]
    if not isinstance(constants, dict):
        errors.append("bad-type: track.constants must be an object")
        constants = {}
    if v1:
        for kit, kit_constants in sorted(constants.items()):
            if not isinstance(kit_constants, dict):
                errors.append(f"bad-type: track.constants.{kit} must be an object")
                continue
            for field in REQUIRED_KIT_CONSTANTS:
                if field not in kit_constants:
                    errors.append(f"missing-field: track.constants.{kit}.{field}")
                elif not _is_int(kit_constants[field]):
                    errors.append(
                        f"bad-type: track.constants.{kit}.{field} must be "
                        "an integer"
                    )
    else:
        for field in REQUIRED_CONSTANTS:
            if field not in constants:
                errors.append(f"missing-field: track.constants.{field}")
            elif not _is_int(constants[field]):
                errors.append(f"bad-type: track.constants.{field} must be an integer")
    creatures = track["creatures"]
    if (
        not isinstance(creatures, list)
        or not creatures
        or not all(
            isinstance(c, dict) and isinstance(c.get("name"), str) and c["name"]
            for c in creatures
        )
    ):
        errors.append(
            "bad-type: track.creatures must be a non-empty list of "
            "{name, faction, kit} objects"
        )
        names: list[str] = []
    else:
        names = [c["name"] for c in creatures]
        if len(set(names)) != len(names):
            errors.append("duplicate-id: creature names must be unique")
        for creature in creatures:
            for field in ("faction", "kit"):
                if not isinstance(creature.get(field), str) or not creature[field]:
                    errors.append(
                        f"missing-field: creature {creature['name']!r} "
                        f"needs a non-empty {field}"
                    )
    kit_by_name = {
        c["name"]: c["kit"]
        for c in (creatures if isinstance(creatures, list) else [])
        if isinstance(c, dict) and isinstance(c.get("name"), str)
        and isinstance(c.get("kit"), str)
    }
    if v1:
        declared_kits = set(kit_by_name.values())
        for kit in sorted(declared_kits - set(constants)):
            errors.append(
                f"missing-field: track.constants.{kit} (per-kit law: "
                "constants cover exactly the roster's kits)"
            )
        for kit in sorted(set(constants) - declared_kits):
            errors.append(
                f"roster-mismatch: track.constants covers kit {kit!r} absent "
                "from the roster (per-kit law: exactly the roster's kits)"
            )
    provenance = track["provenance"]
    if not isinstance(provenance, dict) or provenance.get("class") != track["class"]:
        errors.append(
            "provenance-mismatch: track.provenance.class must equal track.class"
        )
    if v1 and isinstance(provenance, dict):
        bundle_id = provenance.get("bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id:
            errors.append(
                "missing-field: track.provenance.bundle_id (a track never "
                "self-certifies — s84 pin, item 1)"
            )
    ticks = track["ticks"]
    if not isinstance(ticks, list) or not ticks:
        errors.append("bad-type: track.ticks must be a non-empty list")
        return errors
    observed: set[str] = set()
    for index, tick in enumerate(ticks):
        label = f"ticks[{index}]"
        if not isinstance(tick, dict):
            errors.append(f"bad-type: {label} must be an object")
            continue
        frame = tick.get("frame")
        if not _is_int(frame):
            errors.append(f"bad-type: {label}.frame must be an integer")
        elif index == 0 and v1 and frame < 1:
            errors.append(
                f"out-of-range: {label}.frame {frame} < 1 (frame 0 is "
                "constructor state — no tick produced it; s84 pin, item 8)"
            )
        elif index > 0 and _is_int(ticks[index - 1].get("frame")) and (
            frame != ticks[index - 1]["frame"] + 1
        ):
            errors.append(
                f"non-consecutive: {label}.frame {frame} does not follow "
                f"{ticks[index - 1]['frame']}"
            )
        if v1:
            if "masks" not in tick:
                errors.append(
                    f"missing-field: {label}.masks (v1 records carry the "
                    "consumed masks — s84 pin, item 4)"
                )
            elif not isinstance(tick["masks"], dict):
                errors.append(f"bad-type: {label}.masks must be an object")
            else:
                for seat, value in sorted(tick["masks"].items()):
                    if not _is_int(value):
                        errors.append(
                            f"bad-type: {label}.masks[{seat}] must be an integer"
                        )
        records = tick.get("creatures")
        if not isinstance(records, dict):
            errors.append(f"missing-field: {label}.creatures")
            continue
        if v1:
            undeclared = sorted(set(records) - set(names))
            if names and undeclared:
                errors.append(
                    f"roster-mismatch: {label}.creatures names {undeclared} "
                    "not in the declared union roster"
                )
            observed.update(records)
        elif names and sorted(records) != sorted(names):
            errors.append(
                f"roster-mismatch: {label}.creatures keys {sorted(records)} "
                f"!= declared {sorted(names)}"
            )
        for name, record in records.items():
            if v1:
                record_constants = constants.get(kit_by_name.get(name), {})
                if not isinstance(record_constants, dict):
                    record_constants = {}
            else:
                record_constants = constants
            errors.extend(
                validate_record(
                    record, record_constants,
                    f"{label}.creatures[{name}]", v1=v1,
                )
            )
    if v1:
        for name in sorted(set(names) - observed):
            errors.append(
                f"roster-mismatch: creature {name!r} declared in the union "
                "roster but present in zero ticks (union = creatures "
                "observed in the window; s84 pin, item 5)"
            )
    return errors


def validate_record(
    record: dict, constants: dict, label: str, v1: bool = False
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"bad-type: {label} must be an object"]
    required = REQUIRED_RECORD_V1 if v1 else REQUIRED_RECORD
    for field in required:
        if field not in record:
            errors.append(f"missing-field: {label}.{field}")
    if errors:
        return errors
    if v1 and not isinstance(record["possessed"], bool):
        errors.append(f"bad-type: {label}.possessed must be a boolean")
    for field in ("tile_x", "tile_y", "tween_left", "tween_total", "hp", "iframes"):
        if not _is_int(record[field]):
            errors.append(f"bad-type: {label}.{field} must be an integer")
    for field in ("px", "py"):
        if not _is_number(record[field]):
            errors.append(f"bad-type: {label}.{field} must be a number")
    facing = record["facing"]
    if (
        not isinstance(facing, list) or len(facing) != 2
        or not all(_is_int(v) for v in facing)
    ):
        errors.append(f"bad-type: {label}.facing must be [int, int]")
    if record["attack_state"] not in ATTACK_STATES:
        errors.append(
            f"bad-enum: {label}.attack_state {record['attack_state']!r} "
            f"not in {ATTACK_STATES}"
        )
    if not (
        record["current_action"] is None
        or (isinstance(record["current_action"], str) and record["current_action"])
    ):
        errors.append(f"bad-type: {label}.current_action must be null or a string")
    if not _is_int(record["state_frames"]):
        errors.append(f"bad-type: {label}.state_frames must be an integer")
    if errors:
        return errors
    if record["tween_left"] < 0 or record["tween_total"] < 0:
        errors.append(f"out-of-range: {label}.tween_left/tween_total must be >= 0")
    if record["tween_left"] > record["tween_total"]:
        errors.append(
            f"out-of-range: {label}.tween_left {record['tween_left']} > "
            f"tween_total {record['tween_total']}"
        )
    if record["iframes"] < 0:
        errors.append(f"out-of-range: {label}.iframes must be >= 0")
    state = record["attack_state"]
    frames_left = record["state_frames"]
    if state == "idle":
        if frames_left != 0:
            errors.append(
                f"out-of-range: {label}.state_frames must be 0 when idle"
            )
        if record["current_action"] is not None:
            errors.append(
                f"state-mismatch: {label}.current_action must be null when idle"
            )
    else:
        pinned = phase_frames(constants).get(state)
        if record["current_action"] is None:
            errors.append(
                f"state-mismatch: {label}.current_action required when "
                f"attack_state is {state!r}"
            )
        if pinned is not None and not (1 <= frames_left <= pinned):
            errors.append(
                f"out-of-range: {label}.state_frames {frames_left} outside "
                f"[1, {pinned}] for {state}"
            )
    return errors


def phase_frames(constants: dict) -> dict[str, int]:
    return {
        "windup": constants.get("windup_frames"),
        "active": constants.get("active_frames"),
        "recovery": constants.get("recovery_frames"),
    }


def lunge_constants(reference: dict) -> dict[str, int]:
    """The mapping-side lunge px pair. v1 dropped windup_px/active_px from
    track constants (s84 pin, item 3): they are DRAW OFFSETS, not timing —
    this repo's render-reference pin stays their source of law."""
    lunge = reference["feedback_states"]["lunge_offset"]
    return {"windup_px": lunge["windup_px"], "active_px": lunge["active_px"]}


def mapping_constants(track: dict, kit: str, reference: dict | None = None) -> dict:
    """Flat select_pose constants for ONE creature under either schema.
    draft-1 tracks carry them flat (px pair included); v1 tracks carry
    per-kit ``*_frames`` (selection rule: ``constants[creature.kit]``) and
    the px pair rides the mapping side. The mapping SEMANTICS are untouched
    — only the constants source dispatches."""
    if track["schema_version"] != SCHEMA_V1:
        return track["constants"]
    if reference is None:
        raise RecomposeError(
            "missing-reference: v1 mapping constants need the render "
            "reference for the mapping-side lunge px pair"
        )
    return {**track["constants"][kit], **lunge_constants(reference)}


# -- the declared mapping -------------------------------------------------------


def facing_name(facing: list[int]) -> str:
    name = FACING_NAMES.get(tuple(facing))
    if name is None:
        raise RecomposeError(
            f"unrenderable-facing: {facing} has no banked row (banked set is "
            "down/right; mirrored and diagonal rows are separate, unrequested "
            "asset decisions)"
        )
    return name


def select_pose(record: dict, constants: dict) -> tuple[str, str, int]:
    """(pose, facing_name, lunge_offset_px) for one validated record — the
    declared mapping, one clause per banked law (module docstring)."""
    facing = facing_name(record["facing"])
    state = record["attack_state"]
    if state != "idle":
        if record["current_action"] != "attack":
            raise RecomposeError(
                f"unmapped-action-class: current_action "
                f"{record['current_action']!r} has no banked timeline (the "
                "banked lane-B evidence covers the basic attack only; the "
                "engine also suppresses the lunge for specials — "
                "renderer.rb:633 at the pin — so mapping them would be a "
                "silent guess twice over)"
            )
        pinned = phase_frames(constants)[state]
        into = pinned - record["state_frames"]
        if state == "windup":
            pose = v9.seam.WINDUP_INBETWEEN if into == 0 else v9.seam.WINDUP_POSE
            return pose, facing, constants["windup_px"]
        if state == "active":
            return "k0", facing, constants["active_px"]
        if into == 0:
            return v9.seam.SETTLE_INBETWEEN, facing, 0
        if into == pinned - 1:
            return v9.seam.RISE_INBETWEEN, facing, 0
        return v9.seam.RECOVERY_POSE, facing, 0
    total = record["tween_total"]
    left = record["tween_left"]
    if total == 0 or left == 0 or left == total:
        return "idle", facing, 0
    if total != constants["step_frames"]:
        raise RecomposeError(
            f"unmapped-tween-class: tween_total {total} != step_frames "
            f"{constants['step_frames']} while moving (dash/knockback classes "
            "have no banked frame-selection evidence; the mapping refuses "
            "rather than guesses)"
        )
    return f"f{walk_frame_index(total - left, total)}", facing, 0


def draw_vector(record: dict, view: dict, offset_px: int) -> tuple[int, int]:
    fx, fy = record["facing"]
    ox, oy = view["origin_px"]
    return (
        round_half_up(record["px"]) - ox + offset_px * fx,
        round_half_up(record["py"]) - oy + offset_px * fy,
    )


def load_poses(dirs: dict[str, Path]) -> dict[str, dict]:
    from make_contact_sheet import sprite_from_png

    return {
        facing: {
            pose: sprite_from_png(dirs[POSE_DIRS[pose]] / pose_filename(pose, facing))
            for pose in STRIP
        }
        for facing in ("down", "right")
    }


def recompose_tick(
    record: dict, track: dict, poses: dict, zone: dict, constants: dict
) -> tuple[Rgba8Canvas, dict]:
    """One creature's window for one tick + the decision record."""
    pose, facing, offset = select_pose(record, constants)
    dx, dy = draw_vector(record, track["view"], offset)
    view = track["view"]
    cell = compose_cell(
        zone, view["width"], view["height"], poses[facing][pose], dx, dy
    )
    decision = {
        "pose": pose, "pose_facing": facing, "offset_px": offset,
        "draw": [dx, dy],
    }
    return cell, decision


def verify_runtime_intake(
    track_path: Path, evidence_root: Path | None = None
) -> dict:
    """The design-section-5 evidence gate for one RUNTIME track file: the
    track must live inside an intaken ``evidence/replay/<bundle-id>/``
    bundle whose manifest + verification receipt are present, the receipt
    must attest PASS over >= 2 re-execution runs at the manifest's
    fingerprint, and the track bytes must match their sidecar sha256.
    Returns the intake context; raises RecomposeError
    (``runtime-intake-not-established``) on any failure. Re-execution
    itself is the game seat's attestation — this repo does not run game
    code; member hashes and receipt consistency are what verify here."""
    root = (evidence_root if evidence_root is not None else EVIDENCE_REPLAY)
    root = root.resolve()
    path = Path(track_path).resolve()
    try:
        rel = path.relative_to(root)
    except ValueError:
        raise RecomposeError(
            f"runtime-intake-not-established: {path.name} lives outside the "
            f"evidence intake root {root} (design section 5: RUNTIME tracks "
            "are admitted only from verified intaken bundles; synthetic and "
            "fixture tracks are never runtime evidence)"
        ) from None
    bundle_dir = root / rel.parts[0]
    manifest_path = bundle_dir / "manifest.json"
    verification_path = bundle_dir / "verification.json"
    for req in (manifest_path, verification_path):
        if not req.is_file():
            raise RecomposeError(
                f"runtime-intake-not-established: {req.name} missing from "
                f"bundle {bundle_dir.name}"
            )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if verification.get("verdict") != "PASS":
        raise RecomposeError(
            "runtime-intake-not-established: verification verdict "
            f"{verification.get('verdict')!r} != 'PASS' for bundle "
            f"{bundle_dir.name}"
        )
    runs = verification.get("runs")
    if not _is_int(runs) or runs < 2:
        raise RecomposeError(
            f"runtime-intake-not-established: verification runs {runs!r} < 2 "
            f"for bundle {bundle_dir.name} (double re-execution is the "
            "producer's attestation)"
        )
    if verification.get("bundle_id") != manifest.get("bundle_id"):
        raise RecomposeError(
            "runtime-intake-not-established: verification bundle_id "
            f"{verification.get('bundle_id')!r} != manifest "
            f"{manifest.get('bundle_id')!r}"
        )
    fp_manifest = manifest.get("fingerprint_md5")
    fp_verified = verification.get("fingerprint_at_verification")
    if not fp_manifest or fp_verified != fp_manifest:
        raise RecomposeError(
            "runtime-intake-not-established: fingerprint mismatch (manifest "
            f"{fp_manifest!r} vs verification {fp_verified!r})"
        )
    sidecar = path.with_name(path.name + ".sha256")
    if not sidecar.is_file():
        raise RecomposeError(
            f"runtime-intake-not-established: sidecar {sidecar.name} missing "
            "(track identity rides the sidecar sha256 — bundles are "
            "gitignored game-side; no git blob exists)"
        )
    stated = sidecar.read_text(encoding="utf-8").split()[0]
    computed = file_sha256(path)
    if stated != computed:
        raise RecomposeError(
            f"runtime-intake-not-established: {path.name} sha256 {computed} "
            f"!= sidecar {stated}"
        )
    ticks_executed = manifest.get("ticks_executed")
    if not _is_int(ticks_executed) or ticks_executed < 1:
        raise RecomposeError(
            "runtime-intake-not-established: manifest ticks_executed "
            f"{ticks_executed!r} unusable as the frame-domain bound"
        )
    return {
        "bundle_id": manifest.get("bundle_id"),
        "bundle_dir": str(bundle_dir),
        "ticks_executed": ticks_executed,
        "manifest": manifest,
        "verification": verification,
        "track_sha256": computed,
    }


def require_runtime_admission(track: dict, intake: dict | None) -> None:
    """RUNTIME tracks are admitted only as v1 evidence through the verified
    intake context; draft-1 RUNTIME stays a proposal with no emitter, and a
    track without the context refuses with the same class the v13 law
    pinned (lifted ONLY via verified evidence/replay/ bundles)."""
    if track["class"] != "RUNTIME":
        return
    if track["schema_version"] != SCHEMA_V1 or intake is None:
        raise RecomposeError(
            "runtime-intake-not-established: RUNTIME tracks are admitted "
            "only through the verified evidence/replay/ intake gate "
            "(verify_runtime_intake: manifest + PASS receipt with runs >= 2 "
            "+ sidecar-matched bytes; design section 5). draft-1 RUNTIME "
            "remains a schema proposal; synthetic and fixture tracks are "
            "never runtime evidence (v13 law)"
        )
    bundle_id = track["provenance"].get("bundle_id")
    if bundle_id != intake["bundle_id"]:
        raise RecomposeError(
            f"provenance-mismatch: track provenance.bundle_id {bundle_id!r} "
            f"!= intaken bundle {intake['bundle_id']!r}"
        )
    first = track["ticks"][0]["frame"]
    last = track["ticks"][-1]["frame"]
    if first < 1 or last > intake["ticks_executed"]:
        raise RecomposeError(
            f"out-of-range: window {first}..{last} outside 1.."
            f"{intake['ticks_executed']} (frame 0 is constructor state; "
            "records exist only for executed ticks — s84 pin, item 8)"
        )


def decision_stream(
    track: dict, reference: dict, intake: dict | None = None
) -> dict:
    """Validation verdict + mapping decision statistics for one track —
    TEXT only, zero pixels composed. Every record maps to either a pose
    selection or a TYPED refusal; v1 union-roster presence gaps (deaths,
    despawns, not-yet-spawned joins) are reported as per-creature
    information, never refused. RUNTIME tracks require the verified intake
    context (design section 5)."""
    errors = validate_track(track)
    if errors:
        raise RecomposeError("invalid track:\n" + "\n".join(errors))
    require_runtime_admission(track, intake)
    kit_by_name = {c["name"]: c["kit"] for c in track["creatures"]}
    ticks = track["ticks"]
    presence: dict[str, dict] = {
        name: {
            "kit": kit_by_name[name], "first_frame": None, "last_frame": None,
            "ticks_present": 0, "possessed_ticks": 0,
        }
        for name in kit_by_name
    }
    pose_counts: dict[str, int] = {}
    refusal_counts: dict[str, dict] = {}
    possessed_histogram: dict[int, int] = {}
    masks_nonzero_ticks = 0
    decisions = 0
    for tick in ticks:
        frame = tick["frame"]
        masks = tick.get("masks")
        if isinstance(masks, dict) and any(
            _is_int(v) and v != 0 for v in masks.values()
        ):
            masks_nonzero_ticks += 1
        possessed_here = 0
        for name, record in sorted(tick["creatures"].items()):
            stat = presence[name]
            if stat["first_frame"] is None:
                stat["first_frame"] = frame
            stat["last_frame"] = frame
            stat["ticks_present"] += 1
            if record.get("possessed") is True:
                stat["possessed_ticks"] += 1
                possessed_here += 1
            decisions += 1
            try:
                constants = mapping_constants(track, kit_by_name[name], reference)
                pose, facing, _ = select_pose(record, constants)
                key = f"{pose}/{facing}"
                pose_counts[key] = pose_counts.get(key, 0) + 1
            except RecomposeError as exc:
                refusal_class = str(exc).split(":", 1)[0]
                entry = refusal_counts.setdefault(
                    refusal_class,
                    {"count": 0,
                     "first_example": f"frame {frame} {name}: {exc}"[:200]},
                )
                entry["count"] += 1
        possessed_histogram[possessed_here] = (
            possessed_histogram.get(possessed_here, 0) + 1
        )
    mapped = sum(pose_counts.values())
    gaps = sorted(
        name for name, stat in presence.items()
        if stat["ticks_present"] != len(ticks)
    )
    return {
        "mapping_id": MAPPING_ID,
        "schema_version": track["schema_version"],
        "class": track["class"],
        "zone": track["zone"],
        "window_frames": [ticks[0]["frame"], ticks[-1]["frame"]],
        "record_semantics": (
            "post-tick: a record at frame F carries world state AFTER the "
            "tick that produced F; its masks are the consumed "
            "input_log.masks[F-1] (s84 pin, item 4)"
        ),
        "ticks": len(ticks),
        "declared_creatures": len(kit_by_name),
        "decisions": decisions,
        "mapped": mapped,
        "refused": decisions - mapped,
        "pose_counts": {k: pose_counts[k] for k in sorted(pose_counts)},
        "refusal_counts": {
            k: refusal_counts[k] for k in sorted(refusal_counts)
        },
        "possessed_ticks_histogram": {
            str(k): possessed_histogram[k] for k in sorted(possessed_histogram)
        },
        "masks_nonzero_ticks": masks_nonzero_ticks,
        "presence": {name: presence[name] for name in sorted(presence)},
        "presence_gaps": gaps,
        "intake": None if intake is None else {
            "bundle_id": intake["bundle_id"],
            "track_sha256": intake["track_sha256"],
            "verification_verdict": intake["verification"]["verdict"],
            "verification_runs": intake["verification"]["runs"],
        },
    }


def recompose_track(
    track: dict, poses: dict, reference: dict, zone_key: str | None = None,
    intake: dict | None = None,
) -> tuple[list[Rgba8Canvas], list[dict]]:
    """All ticks of a single-creature track over one zone palette."""
    errors = validate_track(track)
    if errors:
        raise RecomposeError("invalid track:\n" + "\n".join(errors))
    require_runtime_admission(track, intake)
    names = [c["name"] for c in track["creatures"]]
    if len(names) != 1:
        raise RecomposeError(
            "unsupported-roster: the reference consumer composes one creature "
            f"per window (track declares {len(names)})"
        )
    zone_name = zone_key or track["zone"]
    if zone_name not in reference["zones"]:
        raise RecomposeError(
            f"unmapped-zone: no banked palette exists for zone {zone_name!r} "
            "(banked zones only; the mapping refuses rather than guesses)"
        )
    zone = reference["zones"][zone_name]
    constants = mapping_constants(
        track, track["creatures"][0]["kit"], reference
    )
    frames: list[Rgba8Canvas] = []
    decisions: list[dict] = []
    for tick in track["ticks"]:
        record = tick["creatures"][names[0]]
        cell, decision = recompose_tick(record, track, poses, zone, constants)
        decision["frame"] = tick["frame"]
        frames.append(cell)
        decisions.append(decision)
    return frames, decisions


# -- v31 RUNTIME-EXP single-creature extraction (pre-registered protocol) -------


def _repo_relative(path: Path) -> str:
    """Repo-relative posix path when inside ROOT (the committed bundle);
    absolute posix otherwise (tmpdir fixtures)."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_zone_palette(reference: dict, palette_path: Path) -> dict:
    """A DEEP-COPIED reference with an additive zone palette merged in.
    OPT-IN per call site: the plain reference keeps the banked-zones-only
    refusal law (the banked v30 ``unmapped-zone`` fixture test is the
    guard); the additive palette is admitted only where explicitly loaded.
    Existing banked zone keys never move - a collision is a typed refusal.
    Every palette value is byte-anchored in the palette file itself
    (manifests/zone-palette-district.json anchoring block)."""
    payload = json.loads(Path(palette_path).read_text(encoding="utf-8"))
    zones = payload.get("zones")
    if not isinstance(zones, dict) or not zones:
        raise RecomposeError(
            f"zone-palette-invalid: {Path(palette_path).name} carries no "
            "zones object"
        )
    merged = copy.deepcopy(reference)
    for zone_name, entry in sorted(zones.items()):
        if zone_name in merged["zones"]:
            raise RecomposeError(
                f"zone-palette-collision: zone {zone_name!r} is already "
                "banked in the render reference (the palette file is "
                "additive-only; existing entries never move)"
            )
        if not isinstance(entry, dict):
            raise RecomposeError(
                f"zone-palette-invalid: zone {zone_name!r} must be an object"
            )
        for key in ZONE_ENTRY_KEYS:
            value = entry.get(key)
            if (
                not isinstance(value, list)
                or len(value) != 3
                or not all(_is_int(v) and 0 <= v <= 255 for v in value)
            ):
                raise RecomposeError(
                    f"zone-palette-invalid: zone {zone_name!r}.{key} must be "
                    "an RGB triple (the five-key zone_1/zone_2 convention "
                    "shape)"
                )
        merged["zones"][zone_name] = {
            key: list(entry[key]) for key in ZONE_ENTRY_KEYS
        }
    return merged


def subject_of(track: dict) -> tuple[str, str]:
    """(name, kit) of the single possessed creature - the pre-registered
    subject law: exactly one ``possessed`` record per tick and ONE stable
    holder across the window; anything else is a typed refusal (no owner
    ruling exists for possession handoffs under single-subject
    extraction)."""
    kit_by_name = {c["name"]: c["kit"] for c in track["creatures"]}
    holders: set[str] = set()
    for tick in track["ticks"]:
        here = [
            name for name, record in sorted(tick["creatures"].items())
            if record.get("possessed") is True
        ]
        if len(here) != 1:
            raise RecomposeError(
                f"unsupported-subject: frame {tick['frame']} carries "
                f"{len(here)} possessed records (single-subject extraction "
                "needs exactly one per tick)"
            )
        holders.add(here[0])
    if len(holders) != 1:
        raise RecomposeError(
            f"unsupported-subject: possession moves between {sorted(holders)} "
            "inside the window (no owner ruling for possession handoffs "
            "under single-subject extraction)"
        )
    name = holders.pop()
    return name, kit_by_name[name]


def subject_decision_entries(
    track: dict, reference: dict, name: str
) -> list[dict]:
    """Per-tick decision stream for ONE creature - TEXT, zero pixels; the
    span-derivation input. Every present tick yields either the mapped
    decision or the TYPED refusal (same select_pose path as
    decision_stream; mapping semantics untouched)."""
    kit_by_name = {c["name"]: c["kit"] for c in track["creatures"]}
    if name not in kit_by_name:
        raise RecomposeError(
            f"unsupported-subject: {name!r} is not in the declared roster"
        )
    entries: list[dict] = []
    for tick in track["ticks"]:
        record = tick["creatures"].get(name)
        if record is None:
            continue
        entry: dict = {
            "frame": tick["frame"],
            "attack_state": record["attack_state"],
            "tween": [record["tween_left"], record["tween_total"]],
        }
        try:
            constants = mapping_constants(track, kit_by_name[name], reference)
            pose, facing, offset = select_pose(record, constants)
            entry["decision"] = {
                "pose": pose,
                "pose_facing": facing,
                "offset_px": offset,
                "draw": list(draw_vector(record, track["view"], offset)),
            }
        except RecomposeError as exc:
            entry["refusal"] = {
                "class": str(exc).split(":", 1)[0],
                "message": str(exc)[:200],
            }
        entries.append(entry)
    return entries


def attack_cycle_poses(constants: dict) -> list[str]:
    """The complete-cycle pose subsequence under ONE kit's constants
    (pre-registered): w0 | a0 x (wf-1) | k0 x af | s0 | r0 x (rf-2) | x0."""
    return (
        ["w0"]
        + ["a0"] * (constants["windup_frames"] - 1)
        + ["k0"] * constants["active_frames"]
        + ["s0"]
        + ["r0"] * (constants["recovery_frames"] - 2)
        + ["x0"]
    )


def span_contains_cycle(entries: list[dict], constants: dict) -> bool:
    """True iff the run's pose stream contains the complete cycle followed
    by at least one later attack_state == idle tick INSIDE the run."""
    poses = [entry["decision"]["pose"] for entry in entries]
    states = [entry["attack_state"] for entry in entries]
    target = attack_cycle_poses(constants)
    size = len(target)
    for start in range(len(poses) - size + 1):
        if poses[start:start + size] == target and any(
            state == "idle" for state in states[start + size:]
        ):
            return True
    return False


def derive_span(
    entries: list[dict], constants: dict
) -> tuple[int, int] | None:
    """The pre-registered span policy: candidate spans are maximal runs of
    consecutive frames where the subject is present AND maps refusal-free;
    a candidate qualifies iff it contains a complete attack cycle
    returning to idle; pick the LONGEST, tie -> EARLIEST. None if no
    candidate qualifies (the STOP branch)."""
    runs: list[list[dict]] = []
    current: list[dict] = []
    for entry in entries:
        if "decision" in entry and (
            not current or entry["frame"] == current[-1]["frame"] + 1
        ):
            current.append(entry)
        else:
            if current:
                runs.append(current)
            current = [entry] if "decision" in entry else []
    if current:
        runs.append(current)
    best: list[dict] | None = None
    for run in runs:
        if not span_contains_cycle(run, constants):
            continue
        if best is None or len(run) > len(best):
            best = run
    if best is None:
        return None
    return best[0]["frame"], best[-1]["frame"]


def derive_window(
    track: dict, name: str, first: int, last: int, reference: dict
) -> dict:
    """The pre-registered FIXED declared sub-window: bounding box of the
    subject's world draw vectors across the span (round_half_up(px/py) +
    lunge offset along facing, each sprite spanning TILE), rounded outward
    to the whole-TILE world grid, plus one full TILE margin per side."""
    kit_by_name = {c["name"]: c["kit"] for c in track["creatures"]}
    constants = mapping_constants(track, kit_by_name[name], reference)
    xs: list[int] = []
    ys: list[int] = []
    for tick in track["ticks"]:
        if not (first <= tick["frame"] <= last):
            continue
        record = tick["creatures"][name]
        _, _, offset = select_pose(record, constants)
        fx, fy = record["facing"]
        xs.append(round_half_up(record["px"]) + offset * fx)
        ys.append(round_half_up(record["py"]) + offset * fy)
    x0 = (min(xs) // TILE) * TILE - TILE
    y0 = (min(ys) // TILE) * TILE - TILE
    x1 = -((-(max(xs) + TILE)) // TILE) * TILE + TILE
    y1 = -((-(max(ys) + TILE)) // TILE) * TILE + TILE
    return {"origin_px": [x0, y0], "width": x1 - x0, "height": y1 - y0}


def extract_subject_track(
    track: dict, name: str, first: int, last: int, view: dict,
    source_sha256: str,
) -> dict:
    """The single-creature sub-track over the declared window: subject
    records, masks, tick_ms, zone, and roster entry copied VERBATIM;
    constants = the subject's kit entry only; provenance carries the
    source bundle_id (require_runtime_admission still binds it to the
    verified intake context) + the extraction parameters. Extraction
    changes WHAT is composed, never HOW."""
    creature = next(c for c in track["creatures"] if c["name"] == name)
    kit = creature["kit"]
    ticks = []
    for tick in track["ticks"]:
        if first <= tick["frame"] <= last:
            ticks.append(
                {
                    "frame": tick["frame"],
                    "creatures": {
                        name: copy.deepcopy(tick["creatures"][name])
                    },
                    "masks": copy.deepcopy(tick["masks"]),
                }
            )
    return {
        "schema_version": SCHEMA_V1,
        "class": "RUNTIME",
        "tick_ms": track["tick_ms"],
        "zone": track["zone"],
        "view": dict(view),
        "constants": {kit: copy.deepcopy(track["constants"][kit])},
        "creatures": [copy.deepcopy(creature)],
        "ticks": ticks,
        "provenance": {
            "class": "RUNTIME",
            "bundle_id": track["provenance"]["bundle_id"],
            "producer": "tools/track_recompose.py --make-runtime-artifacts",
            "source_track_sha256": source_sha256,
            "extraction": {
                "subject": name,
                "kit": kit,
                "span_frames": [first, last],
                "window": dict(view),
                "protocol": "reviews/runtime-recompose-v31/rationale.md",
            },
            "statement": RUNTIME_EXP_DISCLOSURE,
        },
    }


def build_runtime_sheet(
    frames: list[Rgba8Canvas], frame_numbers: list[int], view: dict
) -> Rgba8Canvas:
    """Native 1x per-tick contact sheet of the span under the RUNTIME-EXP
    disclosure banner (layout convention: 10 cells per row, banked
    GUTTER/BG/LABEL presentation constants)."""
    margin_left = 4
    header_h = 20
    label_h = 8
    per_row = SHEET_CELLS_PER_ROW
    rows = (len(frames) + per_row - 1) // per_row
    step_w = view["width"] + GUTTER
    step_h = view["height"] + label_h + GUTTER
    banner_w = 4 * max(len(SHEET_BANNER_1), len(SHEET_BANNER_2)) + 4
    width = max(
        margin_left + min(per_row, len(frames)) * step_w + GUTTER, banner_w
    )
    height = header_h + rows * step_h + 10
    cv = Rgba8Canvas(width, height, v10.BG)
    draw_text(cv, 2, 2, SHEET_BANNER_1)
    draw_text(cv, 2, 10, SHEET_BANNER_2)
    for index, frame in enumerate(frames):
        row, col = divmod(index, per_row)
        x = margin_left + col * step_w
        y = header_h + row * step_h + label_h
        draw_text(cv, x, y - 8, f"T{frame_numbers[index]}")
        for px, py, rgb in canvas_pixels(frame):
            cv.put(x + px, y + py, (*rgb, 255))
    draw_text(cv, 2, height - 8, SHEET_FOOTER)
    return cv


def build_runtime_apng_frames(
    frames: list[Rgba8Canvas], scale: int
) -> list[Rgba8Canvas]:
    """Disclosure-headed panes at native 1x or ONE integer zoom."""
    header_h = 18
    text_w = 4 * max(len(APNG_HEADER_1), len(APNG_HEADER_2)) + 4
    out = []
    for frame in frames:
        pane = Rgba8Canvas(
            max(frame.width * scale, text_w),
            frame.height * scale + header_h,
            v10.BG,
        )
        pane.blit_scaled(canvas_pixels(frame), 0, header_h, scale)
        draw_text(pane, 2, 2, APNG_HEADER_1)
        draw_text(pane, 2, 10, APNG_HEADER_2)
        out.append(pane)
    return out


def _runtime_bundle_bytes(
    track_path: Path, reference: dict, dirs: dict[str, Path],
    palette_path: Path, evidence_root: Path | None = None,
) -> dict:
    """The whole pre-registered pipeline to BYTES (no writes): intake gate
    LIVE, subject law, kit gate, decision capture, span policy, window
    formula, extraction, double-build composition. Typed refusals
    throughout; refuse-not-guess."""
    intake = verify_runtime_intake(Path(track_path), evidence_root)
    track = json.loads(Path(track_path).read_text(encoding="utf-8"))
    errors = validate_track(track)
    if errors:
        raise RecomposeError("invalid track:\n" + "\n".join(errors))
    require_runtime_admission(track, intake)
    name, kit = subject_of(track)
    if kit != "striker":
        raise RecomposeError(
            f"unsupported-subject-kit: subject {name!r} kit {kit!r} != "
            "'striker' (the banked pose set is striker art; substituting it "
            "for another kit in a RUNTIME-labeled artifact needs an owner "
            "call)"
        )
    merged = load_zone_palette(reference, palette_path)
    entries = subject_decision_entries(track, merged, name)
    constants = mapping_constants(track, kit, merged)
    span = derive_span(entries, constants)
    decisions_payload = {
        "mapping_id": MAPPING_ID,
        "schema_version": track["schema_version"],
        "class": track["class"],
        "zone": track["zone"],
        "subject": name,
        "kit": kit,
        "window_frames": [
            track["ticks"][0]["frame"], track["ticks"][-1]["frame"]
        ],
        "entries": entries,
        "mapped": sum(1 for e in entries if "decision" in e),
        "refused": sum(1 for e in entries if "refusal" in e),
        "span": None if span is None else list(span),
        "span_policy": (
            "longest contiguous refusal-free span of the subject containing "
            "a complete attack cycle (w0 through x0, returning to idle); "
            "tie -> earliest (pre-registered, "
            "reviews/runtime-recompose-v31/rationale.md)"
        ),
        "intake": {
            "bundle_id": intake["bundle_id"],
            "track_sha256": intake["track_sha256"],
            "verification_verdict": intake["verification"]["verdict"],
            "verification_runs": intake["verification"]["runs"],
        },
        "disclosure": RUNTIME_EXP_DISCLOSURE,
    }
    decisions_bytes = (
        json.dumps(decisions_payload, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    result = {
        "decisions": decisions_bytes,
        "span": span,
        "subject": (name, kit),
        "intake": intake,
        "track": track,
    }
    if span is None:
        return result
    first, last = span
    view = derive_window(track, name, first, last, merged)
    sub = extract_subject_track(
        track, name, first, last, view, intake["track_sha256"]
    )
    poses = load_poses(dirs)

    def build_once() -> tuple[bytes, bytes, bytes]:
        frames, _ = recompose_track(sub, poses, merged, intake=intake)
        sheet = build_runtime_sheet(
            frames, [t["frame"] for t in sub["ticks"]], view
        ).encode()
        native = encode_apng(
            build_runtime_apng_frames(frames, 1), apng_delays(len(frames))
        )
        zoom = encode_apng(
            build_runtime_apng_frames(frames, APNG_SCALE),
            apng_delays(len(frames)),
        )
        return sheet, native, zoom

    first_build = build_once()
    second_build = build_once()
    sheet, native, zoom = first_build
    result.update(
        {
            "view": view,
            "sheet": sheet,
            "native": native,
            "zoom": zoom,
            "deterministic": first_build == second_build,
            "sub_ticks": len(sub["ticks"]),
        }
    )
    return result


def make_runtime_artifacts(
    track_path: Path, reference: dict, dirs: dict[str, Path],
    out_dir: Path | None = None, palette_path: Path | None = None,
    evidence_root: Path | None = None,
) -> dict:
    """Generate the v31 RUNTIME-EXP artifact bundle. The decision capture
    is written BEFORE the span gate so the STOP branch banks the TEXT
    analysis with zero composed artifacts (pre-registered)."""
    out = RUNTIME_DIR if out_dir is None else Path(out_dir)
    palette = DISTRICT_PALETTE if palette_path is None else Path(palette_path)
    bundle = _runtime_bundle_bytes(
        track_path, reference, dirs, palette, evidence_root
    )
    out.mkdir(parents=True, exist_ok=True)
    (out / RUNTIME_DECISIONS.name).write_bytes(bundle["decisions"])
    if bundle["span"] is None:
        raise RecomposeError(
            "no-clean-attack-cycle: no refusal-free contiguous span of the "
            "subject contains a complete attack cycle (w0 through x0, "
            "returning to idle) - STOP branch: the banked decision capture "
            "is the sprint's TEXT finding; zero artifacts composed"
        )
    (out / RUNTIME_SHEET.name).write_bytes(bundle["sheet"])
    (out / RUNTIME_APNG_NATIVE.name).write_bytes(bundle["native"])
    (out / RUNTIME_APNG_ZOOM.name).write_bytes(bundle["zoom"])
    name, kit = bundle["subject"]
    intake = bundle["intake"]
    first, last = bundle["span"]
    track_rel = _repo_relative(Path(track_path))
    palette_rel = _repo_relative(palette)
    artifacts = {
        RUNTIME_DECISIONS.name: hashlib.sha256(
            bundle["decisions"]
        ).hexdigest(),
        RUNTIME_SHEET.name: hashlib.sha256(bundle["sheet"]).hexdigest(),
        RUNTIME_APNG_NATIVE.name: hashlib.sha256(
            bundle["native"]
        ).hexdigest(),
        RUNTIME_APNG_ZOOM.name: hashlib.sha256(bundle["zoom"]).hexdigest(),
    }
    manifest = {
        "generated_by": "tools/track_recompose.py --make-runtime-artifacts",
        "artifact_class": "RUNTIME-EXP",
        "disclosure": RUNTIME_EXP_DISCLOSURE,
        "mapping_id": MAPPING_ID,
        "schema_version": SCHEMA_V1,
        "repo_commit_at_generation": repo_commit(),
        "mapping_source_sha256": mapping_source_hashes(),
        "zone_palette": {
            "file": palette_rel,
            "sha256": file_sha256(palette),
            "zone": bundle["track"]["zone"],
        },
        "source_track": {
            "path": track_rel,
            "sha256": intake["track_sha256"],
        },
        "intake": {
            "bundle_id": intake["bundle_id"],
            "verification_verdict": intake["verification"]["verdict"],
            "verification_runs": intake["verification"]["runs"],
            "fingerprint_md5": intake["manifest"].get("fingerprint_md5"),
        },
        "subject": {"name": name, "kit": kit},
        "span_frames": [first, last],
        "ticks": bundle["sub_ticks"],
        "window": bundle["view"],
        "window_formula": (
            "bounding box of the subject's world draw vectors "
            "(round_half_up(px/py) + lunge offset along facing), each "
            "sprite spanning TILE=32; rounded outward to the whole-TILE "
            "world grid; plus one full TILE margin per side "
            "(reviews/runtime-recompose-v31/rationale.md, window policy)"
        ),
        "span_policy": (
            "longest contiguous refusal-free span of the subject containing "
            "a complete attack cycle (w0 through x0, returning to idle); "
            "tie -> earliest (pre-registered)"
        ),
        "apng": {
            "frames": bundle["sub_ticks"],
            "delay": (
                "exact 1/60 s per tick; the banked encoder holds the last "
                "frame 0.5 s before the loop restarts (v13 convention)"
            ),
            "zoom_scales": [1, APNG_SCALE],
        },
        "determinism": {
            "double_build_identical": bundle["deterministic"],
        },
        "artifacts": artifacts,
    }
    (out / RUNTIME_MANIFEST.name).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return manifest


def check_runtime_artifacts(
    reference: dict, dirs: dict[str, Path]
) -> list[str]:
    """Committed v31 RUNTIME-EXP bundle guard: regenerate from the
    committed evidence and compare bytes; verify pins and the disclosure.
    Pre-bank (no committed manifest): nothing to guard - returns []."""
    if not RUNTIME_MANIFEST.is_file():
        return []
    failures: list[str] = []
    manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("artifact_class") != "RUNTIME-EXP":
        failures.append("runtime manifest artifact_class must be RUNTIME-EXP")
    if manifest.get("disclosure") != RUNTIME_EXP_DISCLOSURE:
        failures.append(
            "runtime manifest disclosure differs from the pre-registered text"
        )
    live = mapping_source_hashes()
    pinned = manifest.get("mapping_source_sha256", {})
    for rel in MAPPING_SOURCE_FILES:
        if rel not in pinned:
            failures.append(f"runtime manifest is missing the {rel} pin")
    for rel, digest in pinned.items():
        if live.get(rel) != digest:
            failures.append(f"runtime manifest mapping-source drift: {rel}")
    try:
        bundle = _runtime_bundle_bytes(
            ROOT / manifest["source_track"]["path"], reference, dirs,
            ROOT / manifest["zone_palette"]["file"],
        )
    except RecomposeError as exc:
        failures.append(f"runtime artifact regeneration refused: {exc}")
        return failures
    if bundle["span"] is None:
        failures.append("runtime artifact regeneration found no qualifying span")
        return failures
    if not bundle["deterministic"]:
        failures.append("runtime artifact double build not byte-identical")
    for name, blob in (
        (RUNTIME_DECISIONS.name, bundle["decisions"]),
        (RUNTIME_SHEET.name, bundle["sheet"]),
        (RUNTIME_APNG_NATIVE.name, bundle["native"]),
        (RUNTIME_APNG_ZOOM.name, bundle["zoom"]),
    ):
        path = RUNTIME_DIR / name
        if not path.is_file() or path.read_bytes() != blob:
            failures.append(
                f"committed {name} differs from a fresh recomposition"
            )
        if manifest.get("artifacts", {}).get(name) != hashlib.sha256(
            blob
        ).hexdigest():
            failures.append(f"runtime manifest artifact pin mismatch: {name}")
    return failures


# -- synthetic demo -------------------------------------------------------------


def walk_state(t: int, commit: int, step: int) -> tuple[int, int]:
    """(tween_left, tween_total) at draw time for a step committed at
    ``commit``'s controller: commit tick shows (step, step); advance k lands
    at commit+k; arrival leaves (0, step)."""
    if t < commit:
        return (0, 0)
    k = min(t - commit, step)
    return (step - k, step)


def demo_record(
    px: int, py: int, tile: tuple[int, int], facing: list[int],
    tween: tuple[int, int], attack: tuple[str, int] | None,
) -> dict:
    state, frames_left = attack if attack else ("idle", 0)
    return {
        "tile_x": tile[0],
        "tile_y": tile[1],
        "px": float(px), "py": float(py),
        "facing": list(facing),
        "tween_left": tween[0], "tween_total": tween[1],
        "attack_state": state,
        "current_action": None if state == "idle" else "attack",
        "state_frames": frames_left,
        "hp": 80, "iframes": 0,
    }


def build_demo_track(reference: dict) -> dict:
    """One SYNTHETIC track: idle -> step DOWN -> boundary turn at the
    arrival tick (commit-at-arrival class) -> step RIGHT -> full attack
    cycle -> idle. A novel arrangement of banked walk/attack classes in one
    continuous sequence; never a register-item scenario, never runtime
    evidence."""
    timing = reference["attack_timing"]["values"]
    step = timing["step_frames"]["value"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    lunge = reference["feedback_states"]["lunge_offset"]
    constants = {
        "step_frames": step, "windup_frames": windup,
        "active_frames": active, "recovery_frames": recovery,
        "windup_px": lunge["windup_px"], "active_px": lunge["active_px"],
    }
    commit_a = 2                      # step DOWN commits at t02's controller
    commit_b = commit_a + step        # arrival tick t15: turn+commit (CORNER class)
    onset = commit_b + step + 1       # attack begins the tick after B arrival
    attack_ticks = windup + active + recovery
    total = onset + attack_ticks + 2  # two idle tail ticks
    down, right = [0, 1], [1, 0]
    ticks = []
    for t in range(total):
        a_left, a_total = walk_state(t, commit_a, step)
        b_left, b_total = walk_state(t, commit_b, step)
        py = v10.tween_position(min(max(t - commit_a, 0), step), step)
        px = v10.tween_position(min(max(t - commit_b, 0), step), step)
        facing = down if t < commit_b else right
        tile = (0, 0) if t < commit_a else ((0, 1) if t < commit_b else (1, 1))
        attack = None
        if onset <= t < onset + attack_ticks:
            into = t - onset
            if into < windup:
                attack = ("windup", windup - into)
            elif into < windup + active:
                attack = ("active", active - (into - windup))
            else:
                attack = ("recovery", recovery - (into - windup - active))
        tween = (b_left, b_total) if t >= commit_b else (a_left, a_total)
        ticks.append(
            {
                "frame": t,
                "creatures": {
                    "player_1": demo_record(px, py, tile, facing, tween, attack)
                },
                "masks": {"1": 0},
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "class": "SYNTHETIC",
        "tick_ms": TICK_MS,
        "zone": "zone_1",
        "view": {"origin_px": [0, 0], "width": 3 * TILE, "height": 2 * TILE},
        "constants": constants,
        "creatures": [{"name": "player_1", "faction": "pack", "kit": "striker"}],
        "ticks": ticks,
        "provenance": {
            "class": "SYNTHETIC",
            "producer": "tools/track_recompose.py --make-demo",
            "statement": (
                "synthetic declared-model state stream composed from pinned "
                "constants; NOT runtime evidence; answers ZERO register items"
            ),
        },
    }


BANNER = "SYNTHETIC DEMO EXP CLASS DECLARED MODEL ZERO ADJUDICATION"


def build_demo_sheet(track: dict, poses: dict, reference: dict) -> Rgba8Canvas:
    """Both zone rows at native 1x under a drawn SYNTHETIC banner."""
    view = track["view"]
    count = len(track["ticks"])
    margin_left, margin_top = 46, 26
    step_w = view["width"] + GUTTER
    width = margin_left + count * step_w + GUTTER
    height = margin_top + 2 * (view["height"] + GUTTER) + 16 + GUTTER
    cv = Rgba8Canvas(width, height, v10.BG)
    draw_text(cv, 2, 2, BANNER)
    # No V glyph exists in the banked font; the mapping id renders with the
    # version particle spelled as its digit.
    draw_text(
        cv, 2, 10,
        "MAPPING " + MAPPING_ID.upper().replace("-", " ").replace("V1", "1"),
    )
    y = margin_top
    for zone_label, zone_key in (("Z1", "zone_1"), ("Z2", "zone_2")):
        frames, decisions = recompose_track(track, poses, reference, zone_key)
        draw_text(cv, 2, y + view["height"] // 2 - 2, zone_label)
        for index, frame in enumerate(frames):
            x = margin_left + index * step_w
            if zone_key == "zone_1":
                draw_text(cv, x, y - 8, f"T{decisions[index]['frame']:02d}")
            for px, py, rgb in canvas_pixels(frame):
                cv.put(x + px, y + py, (*rgb, 255))
        y += view["height"] + GUTTER
    draw_text(cv, 2, y + 4, "BANKED BYTES ONLY  NOT RUNTIME  NOT AN ANSWER")
    return cv


def build_demo_apng_frames(
    track: dict, poses: dict, reference: dict
) -> list[Rgba8Canvas]:
    frames, _ = recompose_track(track, poses, reference, "zone_1")
    view = track["view"]
    out = []
    for frame in frames:
        pane = Rgba8Canvas(
            view["width"] * APNG_SCALE, view["height"] * APNG_SCALE + 10, v10.BG
        )
        pane.blit_scaled(canvas_pixels(frame), 0, 10, APNG_SCALE)
        draw_text(pane, 2, 2, "SYNTHETIC DEMO EXP")
        out.append(pane)
    return out


def repo_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mapping_source_hashes() -> dict[str, str]:
    return {rel: file_sha256(ROOT / rel) for rel in MAPPING_SOURCE_FILES}


def make_demo(reference: dict, dirs: dict[str, Path]) -> dict:
    """Generate the demo bundle deterministically (double-build proven)."""
    track = build_demo_track(reference)
    track_bytes = (
        json.dumps(track, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    poses = load_poses(dirs)
    sheet = build_demo_sheet(track, poses, reference).encode()
    sheet_again = build_demo_sheet(track, poses, reference).encode()
    frames = build_demo_apng_frames(track, poses, reference)
    apng = encode_apng(frames, apng_delays(len(frames)))
    apng_again = encode_apng(
        build_demo_apng_frames(track, poses, reference), apng_delays(len(frames))
    )
    track_again = (
        json.dumps(build_demo_track(reference), indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    deterministic = (
        sheet == sheet_again and apng == apng_again and track_bytes == track_again
    )
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_TRACK.write_bytes(track_bytes)
    DEMO_SHEET.write_bytes(sheet)
    DEMO_APNG.write_bytes(apng)
    manifest = {
        "generated_by": "tools/track_recompose.py --make-demo",
        "mapping_id": MAPPING_ID,
        "schema_version": SCHEMA_VERSION,
        "repo_commit_at_generation": repo_commit(),
        "mapping_source_sha256": mapping_source_hashes(),
        "provenance": {
            "class": "SYNTHETIC",
            "statement": (
                "synthetic declared-model demo composed from banked export "
                "bytes only; NOT runtime evidence; answers ZERO register items"
            ),
        },
        "artifacts": {
            "synthetic-demo-track.json": hashlib.sha256(track_bytes).hexdigest(),
            "synthetic-demo-sheet.png": hashlib.sha256(sheet).hexdigest(),
            "synthetic-demo.apng": hashlib.sha256(apng).hexdigest(),
        },
        "track_sha256": hashlib.sha256(track_bytes).hexdigest(),
        "determinism": {
            "double_build_identical": deterministic,
            "apng_frames": len(frames),
            "apng_delay": "exact 1/60 s per tick (banked encoder)",
        },
    }
    DEMO_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return manifest


# -- equivalence proof: tracks derived from the banked lane plans ----------------


def track_record_from_walk_lane(
    tick: dict, b_commit: int, step: int
) -> dict:
    """Engine-state record mechanically derived from one banked v10/v11
    Model-A plan tick: A commits at t01, B (when the lane has one) at
    b_commit; facing is the plan's drawn facing; px/py are the plan's draw
    vector (window-origin view)."""
    t = tick["tick"]
    if b_commit is not None and t >= b_commit:
        tween = walk_state(t, b_commit, step)
    else:
        tween = walk_state(t, 1, step)
    return {
        "tile_x": 0, "tile_y": 0,
        "px": float(tick["draw"][0]), "py": float(tick["draw"][1]),
        "facing": [0, 1] if tick["pose_facing"] == "down" else [1, 0],
        "tween_left": tween[0], "tween_total": tween[1],
        "attack_state": "idle", "current_action": None, "state_frames": 0,
        "hp": 80, "iframes": 0,
    }


def walk_constants(reference: dict) -> dict:
    timing = reference["attack_timing"]["values"]
    lunge = reference["feedback_states"]["lunge_offset"]
    return {
        "step_frames": timing["step_frames"]["value"],
        "windup_frames": timing["windup_frames"]["value"],
        "active_frames": timing["active_frames"]["value"],
        "recovery_frames": timing["recovery_frames"]["value"],
        "windup_px": lunge["windup_px"], "active_px": lunge["active_px"],
    }


def check_sheet_equivalence(
    sheet, committed_png: Path, lanes: tuple[str, ...], reference: dict,
    expected_cells: int,
) -> dict:
    """Byte half: every committed scale-1 lane cell of the named Model-A
    lanes equals the mapping's recomposition of a mechanically derived
    track record. Compared against the COMMITTED sheet bytes."""
    failures: list[str] = []
    if not committed_png.is_file():
        return {
            "cells_checked": 0, "expected_cells": expected_cells,
            "failures": [f"missing committed sheet {committed_png}"],
        }
    width, height, raw = read_rgba(committed_png)
    constants = walk_constants(reference)
    step = constants["step_frames"]
    checked = 0
    for cell in sheet.cells:
        if cell["section"] != "lane" or cell["lane"] not in lanes:
            continue
        data = sheet.plan["pairs"][cell["pair"]]["lanes"][cell["lane"]]
        tick = data["ticks"][cell["tick"]]
        record = track_record_from_walk_lane(tick, data["b_commit_tick"], step)
        track = {
            "constants": constants,
            "view": {
                "origin_px": [0, 0],
                "width": cell["window_w"], "height": cell["window_h"],
            },
        }
        pose, facing, offset = select_pose(record, constants)
        dx, dy = draw_vector(record, track["view"], offset)
        mine = compose_cell(
            reference["zones"][cell["zone"]],
            cell["window_w"], cell["window_h"],
            sheet.poses[facing][pose], dx, dy,
        )
        x0, y0 = cell["rect"][0], cell["rect"][1]
        ok = True
        for py in range(cell["window_h"]):
            row_off = ((y0 + py) * width + x0) * 4
            row = raw[row_off: row_off + cell["window_w"] * 4]
            mine_off = py * cell["window_w"] * 4
            if row != mine._pixels[mine_off: mine_off + cell["window_w"] * 4]:
                ok = False
                break
        if not ok:
            failures.append(
                f"{cell['pair']}/{cell['lane']}/{cell['zone']}/"
                f"t{cell['tick']:02d}: recomposed bytes differ from the "
                "committed sheet"
            )
        checked += 1
    if checked != expected_cells:
        failures.append(
            f"covered-cell count {checked} != expected {expected_cells}"
        )
    return {
        "cells_checked": checked, "expected_cells": expected_cells,
        "failures": failures,
    }


def track_record_from_attack_lane(tick: dict, lane: dict, reference: dict) -> dict:
    """Engine-state record mechanically derived from one banked v9 plan
    tick: the walk step commits at t01; the attack begins at the lane's
    onset; px/py are the plan's lunge-free position."""
    t = tick["tick"]
    timing = reference["attack_timing"]["values"]
    step = timing["step_frames"]["value"]
    windup = timing["windup_frames"]["value"]
    active = timing["active_frames"]["value"]
    recovery = timing["recovery_frames"]["value"]
    onset = lane["onset_tick"]
    attack_state, state_frames, action = "idle", 0, None
    if onset <= t < onset + windup + active + recovery:
        into = t - onset
        action = "attack"
        if into < windup:
            attack_state, state_frames = "windup", windup - into
        elif into < windup + active:
            attack_state, state_frames = "active", active - (into - windup)
        else:
            attack_state, state_frames = (
                "recovery", recovery - (into - windup - active)
            )
    base = v9.draw_vector(
        lane["walk_facing"], lane["attack_facing"], tick["a_px"], 0
    )
    return {
        "tile_x": 0, "tile_y": 0,
        "px": float(base[0]), "py": float(base[1]),
        "facing": [0, 1] if tick["pose_facing"] == "down" else [1, 0],
        "tween_left": walk_state(t, 1, step)[0],
        "tween_total": walk_state(t, 1, step)[1],
        "attack_state": attack_state, "current_action": action,
        "state_frames": state_frames, "hp": 80, "iframes": 0,
    }


def check_attack_plan_equivalence(reference: dict) -> dict:
    """Plan half: the mapping's (pose byte-class, facing, offset) stream
    equals the banked v9 lane_tick outputs for every tick of all ten
    lanes."""
    plan = v9.build_plan(reference)
    constants = walk_constants(reference)
    failures: list[str] = []
    checked = 0
    for pair in v9.PAIRS:
        for lane_name in v9.SECTION_LANES:
            lane = plan["pairs"][pair]["lanes"][lane_name]
            for tick in lane["ticks"]:
                record = track_record_from_attack_lane(tick, lane, reference)
                pose, facing, offset = select_pose(record, constants)
                want_pose = BYTE_CLASS.get(tick["pose"], tick["pose"])
                got_pose = BYTE_CLASS.get(pose, pose)
                tag = f"{pair}/{lane_name}/t{tick['tick']:02d}"
                if (got_pose, facing, offset) != (
                    want_pose, tick["pose_facing"], tick["offset_px"]
                ):
                    failures.append(
                        f"{tag}: mapping ({got_pose},{facing},{offset}) != "
                        f"banked v9 ({want_pose},{tick['pose_facing']},"
                        f"{tick['offset_px']})"
                    )
                checked += 1
    expected = len(v9.PAIRS) * len(v9.SECTION_LANES) * seam_total_ticks()
    if checked != expected:
        failures.append(f"record count {checked} != expected {expected}")
    return {"records_checked": checked, "expected": expected, "failures": failures}


def seam_total_ticks() -> int:
    return v9.seam.TOTAL_TICKS


# -- --check --------------------------------------------------------------------


def check_demo(reference: dict, dirs: dict[str, Path]) -> list[str]:
    """Committed-demo verification: schema, manifest pins, determinism."""
    failures: list[str] = []
    for path in (DEMO_TRACK, DEMO_SHEET, DEMO_APNG, DEMO_MANIFEST):
        if not path.is_file():
            failures.append(f"missing committed demo artifact {path.name}")
    if failures:
        return failures
    track = json.loads(DEMO_TRACK.read_text(encoding="utf-8"))
    errors = validate_track(track)
    failures.extend(f"demo track: {e}" for e in errors)
    if track.get("class") != "SYNTHETIC":
        failures.append("demo track must be SYNTHETIC-class")
    manifest = json.loads(DEMO_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("mapping_id") != MAPPING_ID:
        failures.append(
            f"manifest mapping_id {manifest.get('mapping_id')!r} != {MAPPING_ID!r}"
        )
    if manifest.get("provenance", {}).get("class") != "SYNTHETIC":
        failures.append("manifest provenance.class must be SYNTHETIC")
    live = mapping_source_hashes()
    pinned = manifest.get("mapping_source_sha256", {})
    for rel, digest in pinned.items():
        if live.get(rel) != digest:
            failures.append(
                f"mapping source drift: {rel} sha256 differs from the manifest "
                "pin (banked modules must stay unmodified)"
            )
    for rel in MAPPING_SOURCE_FILES:
        if rel not in pinned:
            failures.append(f"manifest is missing the {rel} pin")
    poses = load_poses(dirs)
    fresh_sheet = build_demo_sheet(track, poses, reference).encode()
    if fresh_sheet != DEMO_SHEET.read_bytes():
        failures.append("committed demo sheet differs from a fresh recomposition")
    frames = build_demo_apng_frames(track, poses, reference)
    fresh_apng = encode_apng(frames, apng_delays(len(frames)))
    if fresh_apng != DEMO_APNG.read_bytes():
        failures.append("committed demo APNG differs from a fresh recomposition")
    fresh_track = (
        json.dumps(build_demo_track(reference), indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    if fresh_track != DEMO_TRACK.read_bytes():
        failures.append("committed demo track differs from a fresh derivation")
    for name, digest in manifest.get("artifacts", {}).items():
        path = DEMO_DIR / name
        if not path.is_file() or file_sha256(path) != digest:
            failures.append(f"manifest artifact pin mismatch: {name}")
    return failures


def run_check(reference: dict, dirs: dict[str, Path]) -> int:
    failures: list[str] = []
    failures.extend(check_demo(reference, dirs))

    v10_sheet = v10.TurnTimelineSheet(dirs, reference)
    v10_sheet.build()
    result = check_sheet_equivalence(
        v10_sheet, ROOT / "reviews" / "calibration-v10" / "turn-sheet.png",
        v10.SECTION_LANES, reference, expected_cells=420,
    )
    failures.extend(f"v10 byte equivalence: {f}" for f in result["failures"])
    v10_cells = result["cells_checked"]

    v11_sheet = v11.CornerTimelineSheet(dirs, reference)
    v11_sheet.build()
    result = check_sheet_equivalence(
        v11_sheet, ROOT / "reviews" / "calibration-v11" / "corner-sheet.png",
        V11_MODEL_A_LANES, reference, expected_cells=252,
    )
    failures.extend(f"v11 byte equivalence: {f}" for f in result["failures"])
    v11_cells = result["cells_checked"]

    attack = check_attack_plan_equivalence(reference)
    failures.extend(f"v9 plan equivalence: {f}" for f in attack["failures"])

    exports = check_export_pins(ROOT / "exports")
    failures.extend(exports["failures"])
    for stale in STALE_EXPORT_DIRS:
        if (ROOT / "exports" / stale).exists():
            failures.append(f"exports/{stale} exists - this sprint banks no exports")

    runtime_failures = check_runtime_artifacts(reference, dirs)
    failures.extend(runtime_failures)

    for failure in failures:
        print(f"CHECK FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        "checks passed: demo schema + SYNTHETIC labels + manifest pins + "
        "determinism vs committed bytes; byte equivalence "
        f"{v10_cells} v10 + {v11_cells} v11 lane cells == committed sheets; "
        f"attack plan equivalence {attack['records_checked']} records == "
        "banked v9; banked module hash pins; zero-new-exports + banked "
        "export pins; runtime-exp artifact guard "
        + ("(banked)" if RUNTIME_MANIFEST.is_file() else "(pre-bank skip)")
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
    parser.add_argument("--track", type=Path, default=None,
                        help="validate a track file and report (no artifacts)")
    parser.add_argument("--decisions", type=Path, default=None,
                        help="decision-stream statistics for a track (TEXT "
                             "only; RUNTIME goes through the intake gate)")
    parser.add_argument("--out", type=Path, default=None,
                        help="write --decisions JSON here instead of stdout")
    parser.add_argument("--creature", type=str, default=None,
                        help="with --decisions: per-creature decision "
                             "entries for ONE named creature (TEXT; the "
                             "v31 subject filter)")
    parser.add_argument("--make-runtime-artifacts", type=Path, default=None,
                        help="generate the v31 RUNTIME-EXP single-creature "
                             "artifact bundle from an intaken evidence "
                             "track (pre-registered protocol)")
    parser.add_argument("--make-demo", action="store_true",
                        help="generate the SYNTHETIC demo bundle")
    parser.add_argument("--check", action="store_true",
                        help="full self-verification (see module docstring)")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        if args.track is not None:
            track = json.loads(args.track.read_text(encoding="utf-8"))
            errors = validate_track(track)
            for error in errors:
                print(f"INVALID: {error}", file=sys.stderr)
            if errors:
                return 1
            intake = None
            if isinstance(track, dict) and track.get("class") == "RUNTIME":
                intake = verify_runtime_intake(args.track)
            frames, decisions = recompose_track(
                track, load_poses(dirs), reference, intake=intake
            )
            print(
                f"valid {track['class']} track: {len(frames)} ticks recomposed "
                f"under {MAPPING_ID}"
            )
            return 0
        if args.decisions is not None:
            track = json.loads(args.decisions.read_text(encoding="utf-8"))
            intake = None
            if isinstance(track, dict) and track.get("class") == "RUNTIME":
                intake = verify_runtime_intake(args.decisions)
            if args.creature is not None:
                errors = validate_track(track)
                if errors:
                    raise RecomposeError(
                        "invalid track:\n" + "\n".join(errors)
                    )
                require_runtime_admission(track, intake)
                entries = subject_decision_entries(
                    track, reference, args.creature
                )
                kit_by_name = {
                    c["name"]: c["kit"] for c in track["creatures"]
                }
                stats = {
                    "mapping_id": MAPPING_ID,
                    "schema_version": track["schema_version"],
                    "class": track["class"],
                    "zone": track["zone"],
                    "subject": args.creature,
                    "kit": kit_by_name[args.creature],
                    "window_frames": [
                        track["ticks"][0]["frame"],
                        track["ticks"][-1]["frame"],
                    ],
                    "entries": entries,
                    "mapped": sum(1 for e in entries if "decision" in e),
                    "refused": sum(1 for e in entries if "refusal" in e),
                    "intake": None if intake is None else {
                        "bundle_id": intake["bundle_id"],
                        "track_sha256": intake["track_sha256"],
                        "verification_verdict": (
                            intake["verification"]["verdict"]
                        ),
                        "verification_runs": (
                            intake["verification"]["runs"]
                        ),
                    },
                }
            else:
                stats = decision_stream(track, reference, intake)
            payload = json.dumps(stats, indent=2, sort_keys=True) + "\n"
            if args.out is not None:
                args.out.write_text(payload, encoding="utf-8", newline="\n")
                print(f"wrote {args.out}")
            else:
                print(payload, end="")
            return 0
        if args.make_demo:
            manifest = make_demo(reference, dirs)
            if not manifest["determinism"]["double_build_identical"]:
                print("demo builds are not byte-identical", file=sys.stderr)
                return 1
            print(f"wrote {DEMO_TRACK}")
            print(f"wrote {DEMO_SHEET}")
            print(f"wrote {DEMO_APNG}")
            print(f"wrote {DEMO_MANIFEST}")
            return 0
        if args.make_runtime_artifacts is not None:
            manifest = make_runtime_artifacts(
                args.make_runtime_artifacts, reference, dirs
            )
            if not manifest["determinism"]["double_build_identical"]:
                print(
                    "runtime artifact builds are not byte-identical",
                    file=sys.stderr,
                )
                return 1
            for name in sorted(manifest["artifacts"]):
                print(f"wrote {RUNTIME_DIR / name}")
            print(f"wrote {RUNTIME_MANIFEST}")
            return 0
        if args.check:
            return run_check(reference, dirs)
    except (RecomposeError, ValueError, OSError) as exc:
        print(f"recompose failed: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
