#!/usr/bin/env python3
"""Deterministic corner-turn + settle-hold metrics and validator (sprint 11).

Measures and machine-checks the pre-registered calibration-v11 bars
(reviews/calibration-v11/rationale.md). Zero new frames: every number is
computed from banked export bytes and pinned constants.

Conventions (fixed in the rationale before any number existed): window
coordinates x right / y down, canvas-origin; A = the first walk axis positive
in the walk direction, B = the direction turned to; pose deltas are
100*XOR/union on canvas-aligned export bytes (position-independent - the draw
vector never enters the comparison); squared displacement = dA^2 + dB^2,
exact integer; degenerate lanes carry the full along-axis delta in dA with
dB = 0 by construction.

Failure grouping (fixed in the rationale): INTEGRITY failures mean the
toolchain or frozen-state law is broken - the sprint stops until fixed;
MEASUREMENT failures (M1, the remedy turn-and-settle band) are banked
evidence feeding the affected lane's sub-verdict. Binding tables are
report-only, never a failure. `--check` exits nonzero on any failure of
either group.

INTEGRITY: zero new exports (banked 26-pin checker + no calibration-v9/v10/
v11 exports dirs); jump tables complete (t01..t21, 10 lanes); the anchor map
- context rows == the banked v9 context_deltas on all four fields, f3 == idle
byte-copy, the CORNER cut == the f3/idle context exactly, Model-B hold
structure (every held tick draws f3@B, every held row 0.0), the two remedy
cuts equal each other within a pair, wrap/restart/walk-boundary rows == the
banked v1 motion-metrics pairs, cross-lane consistency, DEGEN prefix ==
CONTROL prefix; THE HARD REGRESSION BAR - CONTROL and DEGEN rows == the
committed calibration-v10 turn-metrics rows field for field, plus plan-level
identity and the cross-version lane webs (the corner lane is provably a
splice of two banked v10 lanes; Model B touches strafe ticks ONLY); tick math
exact per lane class; in-window by construction (lane windows, cut-zoom
crops, wrap strips, comparison bands); determinism + purity (sheet/metrics/
APNGs byte-identical across independent builds and equal to committed bytes;
every creature cell dual-verified); category law - every numeric bar compares
within one facing-category.

MEASUREMENT: M1 - the two novel remedy cuts (f0@down->f3@right,
f0@right->f3@down) <= the free-turn context band max (53.64). The CORNER cut
satisfies the band by anchor equality, so M1's live subjects are exactly the
remedy numbers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import make_corner_timeline as timeline  # noqa: E402
import make_turn_timeline as v10  # noqa: E402  (banked, imported unmodified)
import turn_seam_metrics as v10m  # noqa: E402  (banked, imported unmodified)
from make_contact_sheet import TILE, load_reference  # noqa: E402
from png_writer import Rgba8Canvas  # noqa: E402
from seam_metrics import check_export_pins  # noqa: E402
from timeline_metrics import TICK_MS  # noqa: E402

PAIRS = timeline.PAIRS
LANES = timeline.LANES
CUT_LANES = ("CORNER", "REM_EARLY", "REM_MID", "CONTROL")
REMEDY_LANES = ("REM_EARLY", "REM_MID")
V10_ANCHOR_LANES = ("CONTROL", "DEGEN")
EXPECTED_REM = {"CORNER": 0, "REM_EARLY": 11, "REM_MID": 8, "CONTROL": 0}
EXPECTED_B_FACING_IN_A = {
    "CORNER": 1, "REM_EARLY": 12, "REM_MID": 9, "CONTROL": 0,
}
EXPECTED_HOLD_TICKS = {
    "CORNER": [], "REM_EARLY": list(range(3, 15)),
    "REM_MID": list(range(6, 15)), "CONTROL": [], "DEGEN": [],
}
EXPECTED_CORNER_TICKS = {
    "CORNER": [14], "REM_EARLY": [], "REM_MID": [],
    "CONTROL": [], "DEGEN": [],
}
# The v10 lane each v11 lane is spliced from (anchor 11, cross-version webs).
V10_PREFIX_SOURCE = {"CORNER": "CONTROL", "REM_EARLY": "EARLY", "REM_MID": "MID"}
V10_SUFFIX_SOURCE = {"CORNER": "EARLY", "REM_EARLY": "EARLY", "REM_MID": "MID"}
PREFIX_LAST_TICK = {"CORNER": 13, "REM_EARLY": 2, "REM_MID": 5}
SUFFIX_FIRST_TICK = 14          # rows from the wrap on (from_tick >= 14)
ROW_FIELDS = (
    "from_tick", "to_tick", "pose_from", "pose_from_facing", "pose_to",
    "pose_to_facing", "pose_delta_pct", "delta_a_px", "delta_b_px",
    "delta_window_px", "squared_px", "phase_to",
)
TICK_FIELDS = ("tick", "phase", "pose", "pose_facing", "a_px", "b_px", "draw")
TICK_FIELDS_NO_POSE = ("tick", "pose_facing", "a_px", "b_px", "draw")
STALE_EXPORT_DIRS = ("calibration-v9", "calibration-v10", "calibration-v11")

CONVENTIONS = dict(v10m.CONVENTIONS) | {
    "rem": (
        "REM = 13 - (turn - 1) advances remain after the turn tick's own "
        "advance; CORNER carries REM 0 with ONE B-facing tick inside the A "
        "step (the arrival tick), CONTROL REM 0 with ZERO - both numbers are "
        "reported so the formula is never asked to carry that distinction"
    ),
    "phases": (
        "v10's phase vocabulary unchanged for Model-A lanes plus two v11 "
        "labels: turn_arrive (CORNER's t14 - turn, commit and arrival in one "
        "tick) and strafe_hold (a Model-B held tick)"
    ),
    "exp_class": (
        "REM_EARLY/REM_MID are EXP-class declared-model variants previewing "
        "an ENGINE frame-selection recommendation - never a production lane, "
        "never a runtime claim, never a rescue of v10's banked reds"
    ),
}

DRAWING_MODEL = (
    "Model A (v10, unchanged): banked v1 walk mapping f0x4/f1x3/f2x3/f3x3 "
    "over each step's 13 advances; commit ticks draw the standing pose; a "
    "mid-tween re-face swaps the FACING while the frame INDEX continues from "
    "step progress; the B step restarts at f0; f3 is the idle byte-copy, so "
    "the corner tick's arrival rule and commit rule agree byte for byte; "
    "draw position = 2D tween, no offset anywhere (lunge_offset [0,0] "
    "outside attacks - engine fact at the pin). Model B (NEW, EXP-class): on "
    "a REMEDY lane every strafe tick (turn tick through arrival) draws f3 in "
    "facing B at the tween position instead of the cycling walk frame; "
    "everything else is Model A untouched."
)


class CornerMetricsError(ValueError):
    """Unreadable or contract-violating metric input."""


# -- jump tables ---------------------------------------------------------------


def lane_tables(plan: dict, frames: dict) -> dict:
    """Consecutive-pair rows per lane, built by the BANKED v10 row builder so
    the regression comparison runs through the identical code path."""
    tables: dict[str, dict] = {}
    for pair in PAIRS:
        tables[pair] = {}
        for lane in LANES:
            rows = v10m.lane_jump_table(pair, lane, plan, frames)
            tables[pair][lane] = {
                "rows": rows,
                "turn_cut": v10m.turn_cut_row(pair, lane, plan, rows),
            }
    return tables


# -- anchors -------------------------------------------------------------------


def check_corner_cut_anchor(tables: dict, context: dict) -> list[str]:
    """Anchor 3: the CORNER cut is frame-identical (f3@A->f3@B) and f3 is the
    idle byte-copy, so it must equal the f3 context AND the idle context
    exactly."""
    failures = []
    for pair in PAIRS:
        cut = tables[pair]["CORNER"]["turn_cut"]
        if (cut["pose_from"], cut["pose_to"]) != ("f3", "f3"):
            failures.append(
                f"{pair}/CORNER: cut poses {cut['pose_from']}->{cut['pose_to']}"
                " != the pre-registered frame-identical f3->f3"
            )
        if cut["to_tick"] != v10.ARRIVAL_TICK:
            failures.append(
                f"{pair}/CORNER: cut lands at t{cut['to_tick']:02d} != the "
                f"arrival tick t{v10.ARRIVAL_TICK:02d}"
            )
        for pose in ("f3", "idle"):
            want = context[pose]["popping_pct"]
            if cut["pose_delta_pct"] != want:
                failures.append(
                    f"{pair}/CORNER: cut {cut['pose_delta_pct']} != {pose} "
                    f"context {want}"
                )
        if (cut["delta_a_px"], cut["delta_b_px"]) != (1, 0):
            failures.append(
                f"{pair}/CORNER: cut displacement "
                f"({cut['delta_a_px']},{cut['delta_b_px']}) != the "
                "pre-registered last tween pixel (1,0)"
            )
    return failures


def check_hold_structure(plan: dict, tables: dict) -> list[str]:
    """Anchor 4: every Model-B held tick draws f3 in facing B, the held ticks
    are exactly the pre-registered set, and every held ROW is 0.0."""
    failures = []
    for pair in PAIRS:
        for lane in LANES:
            data = plan["pairs"][pair]["lanes"][lane]
            if data["hold_ticks"] != EXPECTED_HOLD_TICKS[lane]:
                failures.append(
                    f"{pair}/{lane}: hold ticks {data['hold_ticks']} != "
                    f"pre-registered {EXPECTED_HOLD_TICKS[lane]}"
                )
            if data["corner_ticks"] != EXPECTED_CORNER_TICKS[lane]:
                failures.append(
                    f"{pair}/{lane}: corner ticks {data['corner_ticks']} != "
                    f"pre-registered {EXPECTED_CORNER_TICKS[lane]}"
                )
            for tick in data["ticks"]:
                if tick["phase"] != timeline.HOLD_PHASE:
                    continue
                if tick["pose"] != timeline.HOLD_POSE:
                    failures.append(
                        f"{pair}/{lane}/t{tick['tick']:02d}: held pose "
                        f"{tick['pose']} != {timeline.HOLD_POSE}"
                    )
                if tick["pose_facing"] != data["turn_facing"]:
                    failures.append(
                        f"{pair}/{lane}/t{tick['tick']:02d}: held facing "
                        f"{tick['pose_facing']} != B {data['turn_facing']}"
                    )
            holds = set(data["hold_ticks"])
            for row in tables[pair][lane]["rows"]:
                if row["from_tick"] in holds and row["to_tick"] in holds:
                    if row["pose_delta_pct"] != 0.0:
                        failures.append(
                            f"{pair}/{lane} t{row['from_tick']:02d}->"
                            f"t{row['to_tick']:02d}: held row "
                            f"{row['pose_delta_pct']} != 0.0"
                        )
    return failures


def check_remedy_cut_anchor(tables: dict) -> list[str]:
    """Anchor 5: both remedy classes cut f0@A->f3@B, so the two lanes share
    ONE number per pair; the displacement contexts are the pre-registered
    (1,0) and (4,0)."""
    want_displacement = {"REM_EARLY": (1, 0), "REM_MID": (4, 0)}
    failures = []
    for pair in PAIRS:
        numbers = {}
        for lane in REMEDY_LANES:
            cut = tables[pair][lane]["turn_cut"]
            if (cut["pose_from"], cut["pose_to"]) != ("f0", timeline.HOLD_POSE):
                failures.append(
                    f"{pair}/{lane}: cut poses {cut['pose_from']}->"
                    f"{cut['pose_to']} != the pre-registered f0->"
                    f"{timeline.HOLD_POSE}"
                )
            if cut["pose_from_facing"] == cut["pose_to_facing"]:
                failures.append(f"{pair}/{lane}: remedy cut is not cross-facing")
            got = (cut["delta_a_px"], cut["delta_b_px"])
            if got != want_displacement[lane]:
                failures.append(
                    f"{pair}/{lane}: cut displacement {got} != "
                    f"{want_displacement[lane]}"
                )
            numbers[lane] = cut["pose_delta_pct"]
        if len(set(numbers.values())) != 1:
            failures.append(f"{pair}: remedy cut numbers differ {numbers}")
    return failures


def check_walk_pair_anchors(
    tables: dict, plan: dict, v1_metrics_path: Path
) -> list[str]:
    """Anchors 6-7: every same-facing non-zero row == the banked v1
    motion-metrics pair for its facing (wrap, restart, walk-cycle
    boundaries); zero rows only for identical pose+facing; the ONLY
    cross-facing row in a lane is its turn cut. The banked v10 checker is
    bound to v10's lane names, so v11 re-implements the ITERATION and imports
    the banked anchor data."""
    banked = v10m.load_v1_pairs(v1_metrics_path)
    if banked is None:
        return [f"missing banked v1 metrics {v1_metrics_path}"]
    failures = []
    for pair in PAIRS:
        for lane in LANES:
            turn = plan["pairs"][pair]["lanes"][lane]["turn_tick"]
            for row in tables[pair][lane]["rows"]:
                tag = f"{pair}/{lane} t{row['from_tick']:02d}->t{row['to_tick']:02d}"
                if row["pose_from_facing"] != row["pose_to_facing"]:
                    if turn is None or row["to_tick"] != turn:
                        failures.append(f"{tag}: unexpected cross-facing row")
                    continue
                if row["pose_from"] == row["pose_to"]:
                    if row["pose_delta_pct"] != 0.0:
                        failures.append(f"{tag}: identical pose pair delta != 0")
                    continue
                key = (row["pose_from"], row["pose_to"])
                banked_key = v10m.V1_PAIR_KEYS.get(key)
                if banked_key is None:
                    failures.append(f"{tag}: unexpected same-facing pair {key}")
                    continue
                want = banked[row["pose_from_facing"]][banked_key]
                if row["pose_delta_pct"] != want:
                    failures.append(
                        f"{tag}: {key[0]}->{key[1]}@{row['pose_from_facing']} "
                        f"{row['pose_delta_pct']} != banked v1 {want}"
                    )
    return failures


def check_cross_lane_consistency(tables: dict) -> list[str]:
    """Anchor 8: every repetition of the same pose-pair@facing carries the
    identical delta (pose deltas are pure byte-pair functions)."""
    seen: dict[tuple, tuple[float, str]] = {}
    failures = []
    for pair in PAIRS:
        for lane in LANES:
            for row in tables[pair][lane]["rows"]:
                key = (
                    row["pose_from"], row["pose_from_facing"],
                    row["pose_to"], row["pose_to_facing"],
                )
                tag = f"{pair}/{lane} t{row['from_tick']:02d}"
                if key in seen:
                    want, where = seen[key]
                    if row["pose_delta_pct"] != want:
                        failures.append(
                            f"{tag}: {key} delta {row['pose_delta_pct']} != "
                            f"{want} at {where}"
                        )
                else:
                    seen[key] = (row["pose_delta_pct"], tag)
    return failures


# -- the hard v10 regression bar (anchors 10-11) --------------------------------


def load_v10_metrics(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def compare_rows(
    tag: str, mine: list[dict], banked: list[dict], keep
) -> list[str]:
    got = [r for r in mine if keep(r)]
    want = [r for r in banked if keep(r)]
    if len(got) != len(want) or not got:
        return [f"{tag}: row counts {len(got)} vs banked {len(want)} (or empty)"]
    failures = []
    for a, b in zip(got, want):
        for field in ROW_FIELDS:
            if a[field] != b[field]:
                failures.append(
                    f"{tag} t{b['from_tick']:02d}->t{b['to_tick']:02d}: "
                    f"{field} {a[field]} != banked v10 {b[field]}"
                )
    return failures


def check_v10_row_regression(tables: dict, v10_metrics_path: Path) -> list[str]:
    """Anchor 10/11 at row level: CONTROL and DEGEN reproduce the committed
    v10 rows field for field (the hard toolchain-regression bar), and every
    v11 lane's pre-turn / wrap+B-walk rows equal the banked v10 lane they are
    spliced from."""
    banked = load_v10_metrics(v10_metrics_path)
    if banked is None:
        return [f"missing committed v10 metrics {v10_metrics_path}"]
    tables10 = banked["turn_tables"]
    failures = []
    for pair in PAIRS:
        for lane in V10_ANCHOR_LANES:
            failures.extend(
                compare_rows(
                    f"{pair}/{lane} == v10", tables[pair][lane]["rows"],
                    tables10[pair][lane]["rows"], lambda r: True,
                )
            )
        for lane, source in V10_PREFIX_SOURCE.items():
            last = PREFIX_LAST_TICK[lane]
            failures.extend(
                compare_rows(
                    f"{pair}/{lane} prefix == v10 {source}",
                    tables[pair][lane]["rows"], tables10[pair][source]["rows"],
                    lambda r, last=last: r["to_tick"] <= last,
                )
            )
        for lane, source in V10_SUFFIX_SOURCE.items():
            failures.extend(
                compare_rows(
                    f"{pair}/{lane} wrap+walkB == v10 {source}",
                    tables[pair][lane]["rows"], tables10[pair][source]["rows"],
                    lambda r: r["from_tick"] >= SUFFIX_FIRST_TICK,
                )
            )
    return failures


def compare_ticks(
    tag: str, mine: list[dict], banked: list[dict], fields, keep
) -> list[str]:
    failures = []
    for a, b in zip(mine, banked):
        if not keep(b):
            continue
        for field in fields:
            if a[field] != b[field]:
                failures.append(
                    f"{tag} t{b['tick']:02d}: {field} {a[field]} != "
                    f"banked v10 {b[field]}"
                )
    return failures


def check_v10_plan_identity(plan: dict, v10_plan: dict) -> list[str]:
    """Anchor 10/11 at plan level: CONTROL and DEGEN tick dicts are identical
    to v10's; the CORNER lane is a provable SPLICE of two banked v10 lanes
    (CONTROL up to t13, EARLY from t14 with the phase relabelled); and Model
    B touches strafe ticks ONLY (held ticks keep v10's facing and position;
    every other tick is v10 verbatim)."""
    failures = []
    for pair in PAIRS:
        mine = plan["pairs"][pair]["lanes"]
        banked = v10_plan["pairs"][pair]["lanes"]
        for lane in V10_ANCHOR_LANES:
            failures.extend(
                compare_ticks(
                    f"{pair}/{lane} plan == v10", mine[lane]["ticks"],
                    banked[lane]["ticks"], TICK_FIELDS, lambda t: True,
                )
            )
        failures.extend(
            compare_ticks(
                f"{pair}/CORNER plan prefix == v10 CONTROL",
                mine["CORNER"]["ticks"], banked["CONTROL"]["ticks"],
                TICK_FIELDS, lambda t: t["tick"] <= 13,
            )
        )
        failures.extend(
            compare_ticks(
                f"{pair}/CORNER plan suffix == v10 EARLY",
                mine["CORNER"]["ticks"], banked["EARLY"]["ticks"],
                TICK_FIELDS, lambda t: t["tick"] >= 15,
            )
        )
        failures.extend(  # the corner tick itself: v10's EARLY t14 but relabelled
            compare_ticks(
                f"{pair}/CORNER plan arrival == v10 EARLY",
                mine["CORNER"]["ticks"], banked["EARLY"]["ticks"],
                ("tick", "pose", "pose_facing", "a_px", "b_px", "draw"),
                lambda t: t["tick"] == 14,
            )
        )
        for lane, source in (("REM_EARLY", "EARLY"), ("REM_MID", "MID")):
            holds = set(mine[lane]["hold_ticks"])
            failures.extend(
                compare_ticks(
                    f"{pair}/{lane} plan outside hold == v10 {source}",
                    mine[lane]["ticks"], banked[source]["ticks"],
                    TICK_FIELDS, lambda t, h=holds: t["tick"] not in h,
                )
            )
            failures.extend(
                compare_ticks(
                    f"{pair}/{lane} hold geometry == v10 {source}",
                    mine[lane]["ticks"], banked[source]["ticks"],
                    TICK_FIELDS_NO_POSE, lambda t, h=holds: t["tick"] in h,
                )
            )
    return failures


def check_binding_regression(binding: dict, v10_metrics_path: Path) -> list[str]:
    """Anchor 11's last clause: the remedy does NOT move the body - every
    remedy binding row's a_px equals the banked v10 row's at the same tick."""
    banked = load_v10_metrics(v10_metrics_path)
    if banked is None:
        return [f"missing committed v10 metrics {v10_metrics_path}"]
    failures = []
    for pair in PAIRS:
        for lane, source in (("REM_EARLY", "EARLY"), ("REM_MID", "MID")):
            mine = {r["tick"]: r["a_px"] for r in binding[pair][lane]["rows"]}
            want = {
                r["tick"]: r["a_px"]
                for r in banked["binding"][pair][source]["rows"]
            }
            if set(mine) != set(want):
                failures.append(
                    f"{pair}/{lane}: reported ticks {sorted(mine)} != banked "
                    f"v10 {source} {sorted(want)}"
                )
                continue
            for tick, a_px in want.items():
                if mine[tick] != a_px:
                    failures.append(
                        f"{pair}/{lane} t{tick:02d}: a_px {mine[tick]} != "
                        f"banked v10 {a_px}"
                    )
    return failures


# -- measurement (M1) ----------------------------------------------------------


def band_report(tables: dict, context: dict) -> dict:
    """M1: every turn cut at or below the free-turn context band max. The
    CORNER and CONTROL cuts satisfy it by anchor equality; the LIVE subjects
    are the two novel remedy cuts."""
    band_max = max(stats["popping_pct"] for stats in context.values())
    band_min = min(stats["popping_pct"] for stats in context.values())
    cuts = {}
    for pair in PAIRS:
        for lane in CUT_LANES:
            cut = tables[pair][lane]["turn_cut"]
            cuts[f"{pair}/{lane}"] = {
                "pose_from": cut["pose_from"],
                "pose_to": cut["pose_to"],
                "pose_delta_pct": cut["pose_delta_pct"],
                "within_band": cut["pose_delta_pct"] <= band_max,
                "measurement_subject": lane in REMEDY_LANES,
            }
    return {"band_max": band_max, "band_min": band_min, "cuts": cuts}


# -- binding (report-only) -----------------------------------------------------


def binding_for(pair: str, lane: str, plan: dict, frames: dict) -> list[dict]:
    """Binding rows for the lane's DECLARED reported tick set (Model-B held
    ticks; CORNER's single arrival tick). The banked v10 geometry function is
    reused verbatim through a phase-relabelled view of the lane - no
    duplicated overlap arithmetic."""
    data = plan["pairs"][pair]["lanes"][lane]
    reported = set(data["hold_ticks"]) | set(data["corner_ticks"])
    view = dict(data)
    view["ticks"] = [
        dict(tick, phase="strafe")
        for tick in data["ticks"] if tick["tick"] in reported
    ]
    shim = {"pairs": {pair: {"lanes": {lane: view}}}}
    return v10m.binding_rows(pair, lane, shim, frames)


# -- structural checks ---------------------------------------------------------


def check_tick_math(plan: dict) -> list[str]:
    """Bar 4: the whole plan re-derived independently from the pinned
    constants and the two declared models."""
    failures: list[str] = []
    step = plan["constants"]["step_frames"]
    positions = [v10.tween_position(k, step) for k in range(step + 1)]
    deltas = tuple(b - a for a, b in zip(positions, positions[1:]))
    if deltas != v10m.TWEEN_DELTAS:
        failures.append(f"tween deltas {deltas} != pinned {v10m.TWEEN_DELTAS}")
    if positions[-1] != TILE:
        failures.append(f"tween arrival {positions[-1]} != {TILE}")
    for pair, section in plan["pairs"].items():
        for lane, data in section["lanes"].items():
            tag = f"{pair}/{lane}"
            turn = data["turn_tick"]
            walk_facing = data["walk_facing"]
            turn_facing = data["turn_facing"]
            commit_b = data["b_commit_tick"]
            if turn != timeline.LANE_TURN[lane]:
                failures.append(
                    f"{tag}: turn tick {turn} != pre-registered "
                    f"{timeline.LANE_TURN[lane]}"
                )
            if data["model"] != timeline.LANE_MODEL[lane]:
                failures.append(f"{tag}: model {data['model']} != pre-registered")
            if lane == "DEGEN":
                if turn is not None or walk_facing != turn_facing:
                    failures.append(f"{tag}: degenerate lane carries a turn")
            else:
                if data["rem_after_turn"] != EXPECTED_REM[lane]:
                    failures.append(
                        f"{tag}: REM {data['rem_after_turn']} != "
                        f"pre-registered {EXPECTED_REM[lane]}"
                    )
                if data["b_facing_ticks_in_a_step"] != EXPECTED_B_FACING_IN_A[lane]:
                    failures.append(
                        f"{tag}: B-facing ticks in the A step "
                        f"{data['b_facing_ticks_in_a_step']} != pre-registered "
                        f"{EXPECTED_B_FACING_IN_A[lane]}"
                    )
                want_commit = 15 if lane == "CONTROL" else 14
                if commit_b != want_commit:
                    failures.append(
                        f"{tag}: B commit tick {commit_b} != {want_commit}"
                    )
                if data["first_b_advance_tick"] != want_commit + 1:
                    failures.append(f"{tag}: first B advance tick wrong")
            if data["arrival_tick"] != 14:
                failures.append(f"{tag}: arrival tick != 14")
            for tick in data["ticks"]:
                t = tick["tick"]
                expected_a = v10.tween_position(t - 1, step)
                expected_b = v10.tween_position(t - commit_b, step)
                if (tick["a_px"], tick["b_px"]) != (expected_a, expected_b):
                    failures.append(
                        f"{tag}/t{t:02d}: tween ({tick['a_px']},{tick['b_px']})"
                        f" != ({expected_a},{expected_b})"
                    )
                expected_draw = list(
                    v10.draw_vector(walk_facing, turn_facing, expected_a, expected_b)
                )
                if tick["draw"] != expected_draw:
                    failures.append(
                        f"{tag}/t{t:02d}: draw {tick['draw']} != {expected_draw}"
                    )
                expected_facing = (
                    walk_facing if turn is None or t < turn else turn_facing
                )
                if tick["pose_facing"] != expected_facing:
                    failures.append(
                        f"{tag}/t{t:02d}: facing {tick['pose_facing']} != "
                        f"{expected_facing}"
                    )
                if tick["pose"] not in v10.WALK_POSES:
                    failures.append(f"{tag}/t{t:02d}: pose outside walk strip")
                want_pose, want_phase = expected_pose_phase(
                    lane, data, t, step, commit_b
                )
                if (tick["pose"], tick["phase"]) != (want_pose, want_phase):
                    failures.append(
                        f"{tag}/t{t:02d}: pose/phase "
                        f"({tick['pose']},{tick['phase']}) != "
                        f"({want_pose},{want_phase})"
                    )
    return failures


def expected_pose_phase(
    lane: str, data: dict, t: int, step: int, commit_b: int
) -> tuple[str, str]:
    """The declared models, re-derived per tick from the lane class."""
    turn = data["turn_tick"]
    if t < v10.IDLE_PRE_TICKS:
        return "idle", "idle_pre"
    if t <= 14:
        walk_pose = f"f{v10.walk_frame_index(t - 1, step)}"
        if turn is None:
            return walk_pose, "walk_1"
        if t < turn:
            return walk_pose, "walk_a"
        if data["model"] == "B":                     # Model B substitution
            return timeline.HOLD_POSE, timeline.HOLD_PHASE
        return walk_pose, timeline.CORNER_PHASE      # CORNER's arrival tick
    if lane == "CONTROL" and t == 15:
        return "idle", "turn_stand"
    if t <= commit_b + step:
        return (
            f"f{v10.walk_frame_index(t - commit_b, step)}",
            "walk_2" if turn is None else "walk_b",
        )
    return "idle", "idle_post"


def check_bounds(plan: dict, v10_plan: dict) -> list[str]:
    """Bar 5: in-window BY CONSTRUCTION - the banked per-tick/window/turn-crop
    check plus v11's declared zoom strips (CORNER carries four ticks) and both
    comparison bands (full windows; the banked row is checked in its own
    plan)."""
    failures = list(v10m.check_bounds(plan))
    failures.extend(f"v10 comparison plan: {f}" for f in v10m.check_bounds(v10_plan))
    lo, hi = v10.CONTRACT_BOUNDS
    for pair, section in plan["pairs"].items():
        for lane, data in section["lanes"].items():
            if data["zoom_ticks"] is None:
                continue
            crop_w, crop_h = data["turn_crop"]
            for t in data["zoom_ticks"]:
                dx, dy = data["ticks"][t]["draw"]
                if (
                    dx + lo < 0 or dx + hi >= crop_w
                    or dy + lo < 0 or dy + hi >= crop_h
                ):
                    failures.append(
                        f"{pair}/{lane}/t{t:02d}: contract bounds escape the "
                        f"declared zoom crop {crop_w}x{crop_h}"
                    )
    return failures


# -- report --------------------------------------------------------------------


def build_report(
    dirs: dict[str, Path],
    reference: dict,
    sheet_path: Path | None = None,
    apng_dir: Path | None = None,
    exports_root: Path | None = None,
    v9_metrics_path: Path | None = None,
    v1_metrics_path: Path | None = None,
    v10_metrics_path: Path | None = None,
) -> dict:
    frames = v10m.load_frames(dirs)
    sheet = timeline.CornerTimelineSheet(dirs, reference)
    canvas = sheet.build()
    encoded = canvas.encode()
    second = timeline.CornerTimelineSheet(dirs, reference).build().encode()

    committed = None
    if sheet_path is not None and sheet_path.is_file():
        committed = sheet_path.read_bytes() == encoded

    tables = lane_tables(sheet.plan, frames)
    binding: dict[str, dict] = {}
    for pair in PAIRS:
        binding[pair] = {}
        for lane in ("CORNER",) + REMEDY_LANES:
            rows = binding_for(pair, lane, sheet.plan, frames)
            binding[pair][lane] = {
                "rows": rows, "summary": v10m.binding_summary(rows),
            }

    context = v10m.context_deltas(frames)
    band = band_report(tables, context)

    apng = {}
    if apng_dir is not None:
        for pair in PAIRS:
            frames_list = timeline.build_apng_frames(sheet, pair)
            payload = timeline.encode_apng(
                frames_list, timeline.apng_delays(len(frames_list))
            )
            again = timeline.encode_apng(
                timeline.build_apng_frames(sheet, pair),
                timeline.apng_delays(len(frames_list)),
            )
            target = apng_dir / f"corner-lanes-{pair.lower()}.apng"
            apng[pair] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "deterministic": payload == again,
                "committed_matches": (
                    target.read_bytes() == payload if target.is_file() else None
                ),
                "frames": len(frames_list),
            }

    root = exports_root or ROOT / "exports"
    exports = check_export_pins(root)
    for stale in STALE_EXPORT_DIRS:
        if (root / stale).exists():
            exports["failures"].append(
                f"exports/{stale} exists - this sprint banks no exports"
            )

    v10_metrics = (
        v10_metrics_path
        or ROOT / "reviews" / "calibration-v10" / "turn-metrics.json"
    )
    return {
        "generated_by": "tools/corner_metrics.py",
        "constants": sheet.plan["constants"],
        "conventions": CONVENTIONS,
        "drawing_model": DRAWING_MODEL,
        "tick_ms": TICK_MS,
        "lane_tables": tables,
        "context_deltas": context,
        "band": band,
        "binding": binding,
        "context_anchor_failures": v10m.check_context_anchor(
            context,
            v9_metrics_path
            or ROOT / "reviews" / "calibration-v9" / "cross-seam-metrics.json",
        ),
        "bytecopy_failures": v10m.check_bytecopy(frames),
        "corner_cut_anchor_failures": check_corner_cut_anchor(tables, context),
        "hold_structure_failures": check_hold_structure(sheet.plan, tables),
        "remedy_cut_anchor_failures": check_remedy_cut_anchor(tables),
        "walk_pair_anchor_failures": check_walk_pair_anchors(
            tables, sheet.plan,
            v1_metrics_path
            or ROOT / "reviews" / "calibration-v1" / "motion-metrics.json",
        ),
        "consistency_failures": check_cross_lane_consistency(tables),
        "degen_prefix_failures": v10m.check_degen_prefix(tables),
        "v10_row_regression_failures": check_v10_row_regression(
            tables, v10_metrics
        ),
        "v10_plan_identity_failures": check_v10_plan_identity(
            sheet.plan, sheet.v10_plan
        ),
        "binding_regression_failures": check_binding_regression(
            binding, v10_metrics
        ),
        "tick_math_failures": check_tick_math(sheet.plan),
        "bounds_failures": check_bounds(sheet.plan, sheet.v10_plan),
        "sheet": {
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "deterministic": encoded == second,
            "committed_matches": committed,
            "cells": len(sheet.cells),
        },
        "apng": apng,
        "purity": v10m.check_purity(canvas, sheet, dirs),
        "export_pins": exports,
    }


INTEGRITY_KEYS = (
    "context_anchor_failures", "bytecopy_failures",
    "corner_cut_anchor_failures", "hold_structure_failures",
    "remedy_cut_anchor_failures", "walk_pair_anchor_failures",
    "consistency_failures", "degen_prefix_failures",
    "v10_row_regression_failures", "v10_plan_identity_failures",
    "binding_regression_failures", "tick_math_failures", "bounds_failures",
)


def check_report(report: dict) -> dict[str, list[str]]:
    """INTEGRITY failures stop the sprint; MEASUREMENT failures are banked
    evidence for the affected lane's sub-verdict (pre-registered split)."""
    integrity: list[str] = []
    for key in INTEGRITY_KEYS:
        integrity.extend(report[key])
    if not report["sheet"]["deterministic"]:
        integrity.append("sheet builds are not byte-identical across two runs")
    if report["sheet"]["committed_matches"] is False:
        integrity.append("committed sheet bytes differ from a fresh build")
    for pair, aid in report["apng"].items():
        if not aid["deterministic"]:
            integrity.append(f"apng {pair}: builds not byte-identical")
        if aid["committed_matches"] is False:
            integrity.append(f"apng {pair}: committed bytes differ from fresh build")
    integrity.extend(report["purity"]["failures"])
    integrity.extend(report["export_pins"]["failures"])
    return {"integrity": integrity, "measurement": v10m.check_band(report["band"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = timeline.default_dirs()
    for key, value in defaults.items():
        flag = "--" + key.replace("_dir", "-exports").replace("_", "-")
        parser.add_argument(flag, dest=key, type=Path, default=value)
    parser.add_argument(
        "--reference", type=Path,
        default=ROOT / "manifests" / "render-reference.json",
    )
    parser.add_argument(
        "--sheet", type=Path,
        default=ROOT / "reviews" / "calibration-v11" / "corner-sheet.png",
    )
    parser.add_argument("--apng-dir", type=Path, default=None)
    parser.add_argument(
        "--out", type=Path,
        default=ROOT / "reviews" / "calibration-v11" / "corner-metrics.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reference = load_reference(args.reference)
    dirs = {key: getattr(args, key) for key in defaults}
    try:
        report = build_report(
            dirs, reference, sheet_path=args.sheet, apng_dir=args.apng_dir
        )
    except (CornerMetricsError, ValueError, OSError) as exc:
        print(f"metrics failed: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"wrote {args.out}")
    if args.check:
        failures = check_report(report)
        for failure in failures["integrity"]:
            print(f"INTEGRITY FAIL: {failure}", file=sys.stderr)
        for failure in failures["measurement"]:
            print(f"MEASUREMENT FAIL: {failure}", file=sys.stderr)
        if failures["integrity"] or failures["measurement"]:
            return 1
        print(
            "checks passed: zero-new-exports + banked pins, jump tables, "
            "anchor map (context, byte-copy, corner cut, hold structure, "
            "remedy cuts, walk pairs, consistency, degen prefix), the v10 "
            "regression bar (rows, plan identity, binding), remedy band, "
            "tick math, in-bounds by construction, byte-determinism, "
            "composition purity"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
