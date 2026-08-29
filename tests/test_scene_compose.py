"""v32 SCENE-EXP unit tests - small fixtures only (<= 4x4 tiles, <= 12
ticks for units; ONE full-cycle pipeline fixture, the test_runtime_extract
precedent). The committed-evidence regeneration guard lives in
tests/test_track_recompose.py (SLOW tier).

Covers: the two anchored-manifest loaders (shape law + content-pin
anchoring), the engine notch/lunge/kit-color laws, participant
intersection, draw order (derived faction passes + declared tiebreak),
ring placement, the tile layer (floor/wall/transition/void + census), the
M-parameter window formula, the sheet-dimension hard cap, and the scene
pipeline on a tmpdir bundle including its typed STOP branches.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import track_recompose as tr  # noqa: E402
from make_contact_sheet import load_reference  # noqa: E402

PALETTE = REPO / "manifests" / "zone-palette-district.json"
BG = (16, 16, 16, 255)
FLOOR = (36, 30, 20, 255)
WALL = (176, 140, 88, 255)
GOLD = (235, 190, 90, 255)
NOTCH = (20, 14, 12, 255)
RING = (255, 255, 255, 255)


def reference() -> dict:
    return load_reference(REPO / "manifests" / "render-reference.json")


def merged_reference() -> dict:
    return tr.load_zone_palette(reference(), PALETTE)


def scene_ref() -> dict:
    return tr.load_scene_reference(tr.SCENE_REFERENCE_FILE)


def canvas_px(cv, x: int, y: int) -> tuple[int, ...]:
    offset = (y * cv.width + x) * 4
    return tuple(cv._pixels[offset:offset + 4])


def tiny_zone_map(rows: list[str], transitions=()) -> dict:
    """Loader-output-shaped map for draw units (the loader itself is
    tested against files)."""
    return {
        "rows": rows,
        "cols": len(rows[0]),
        "row_count": len(rows),
        "tile_size": 32,
        "transition_tiles": list(transitions),
    }


def record(**overrides) -> dict:
    base = {
        "tile_x": 0, "tile_y": 0, "px": 0.0, "py": 0.0,
        "facing": [1, 0], "tween_left": 0, "tween_total": 0,
        "attack_state": "idle", "current_action": None, "state_frames": 0,
        "hp": 50, "iframes": 0, "possessed": False,
    }
    base.update(overrides)
    return base


def kit_constants() -> dict:
    return {
        # FIXTURE constants: a legally-shaped SHORT striker cycle (w0, a0,
        # k0, s0, x0 = 5 ticks) keeps the fast-tier pipeline unit tiny;
        # the mapping never validates fixture constants against pinned
        # values (the test_runtime_extract precedent uses its own too).
        "striker": {"step_frames": 13, "windup_frames": 2,
                    "active_frames": 1, "recovery_frames": 2},
        "blocker": {"step_frames": 19, "windup_frames": 8,
                    "active_frames": 4, "recovery_frames": 12},
        "rusher": {"step_frames": 16, "windup_frames": 20,
                   "active_frames": 6, "recovery_frames": 0},
    }


def attack_states(constants: dict) -> list[tuple[str, int]]:
    walk = []
    for state, key in (("windup", "windup_frames"),
                       ("active", "active_frames"),
                       ("recovery", "recovery_frames")):
        for left in range(constants[key], 0, -1):
            walk.append((state, left))
    return walk


def scene_track(neighbor_px: float = 66.0, first_frame: int = 100) -> dict:
    """RUNTIME v1 fixture: possessed striker runs one complete attack cycle
    (idle head/tail); a pack blocker neighbor (facing UP - the class a
    sprite refuses and a primitive draws); a far human rusher (omitted
    every tick)."""
    cycle = attack_states(kit_constants()["striker"])
    states = [("idle", 0)] + cycle + [("idle", 0)]
    ticks = []
    frame = first_frame
    for state, left in states:
        subject = record(
            px=100.0, py=50.0, facing=[1, 0], possessed=True,
            attack_state=state, state_frames=left,
            current_action=None if state == "idle" else "attack",
        )
        neighbor = record(px=neighbor_px, py=50.0, facing=[0, -1])
        far = record(px=4000.0, py=4000.0, facing=[1, 0])
        ticks.append({
            "frame": frame,
            "creatures": {
                "striker_1": subject, "blocker_1": neighbor,
                "rusher_1": far,
            },
            "masks": {"1": 0},
        })
        frame += 1
    return {
        "schema_version": "1",
        "class": "RUNTIME",
        "tick_ms": 16.666666,
        "zone": "district",
        "view": {"origin_px": [0, 0], "width": 960, "height": 540},
        "constants": kit_constants(),
        "creatures": [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
            {"name": "blocker_1", "faction": "pack", "kit": "blocker"},
            {"name": "rusher_1", "faction": "human", "kit": "rusher"},
        ],
        "ticks": ticks,
        "provenance": {
            "class": "RUNTIME",
            "producer": "tests/test_scene_compose.py fixture",
            "bundle_id": "fixture-bundle",
            "statement": "hand-built v1 fixture; never evidence",
        },
    }


def write_fixture_bundle(root: Path, track: dict) -> Path:
    """A verified-shape evidence bundle in a tmpdir root (the
    test_runtime_extract pattern)."""
    bundle = root / "fixture-bundle"
    (bundle / "tracks").mkdir(parents=True)
    track_path = bundle / "tracks" / "t.json"
    track_path.write_text(
        json.dumps(track, indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    digest = tr.file_sha256(track_path)
    (bundle / "tracks" / "t.json.sha256").write_text(
        f"{digest}  t.json\n", encoding="utf-8"
    )
    last = track["ticks"][-1]["frame"]
    (bundle / "manifest.json").write_text(
        json.dumps({
            "bundle_id": "fixture-bundle", "fingerprint_md5": "f" * 32,
            "ticks_executed": last + 10, "members": {},
        }), encoding="utf-8",
    )
    (bundle / "verification.json").write_text(
        json.dumps({
            "bundle_id": "fixture-bundle", "verdict": "PASS", "runs": 2,
            "fingerprint_at_verification": "f" * 32,
        }), encoding="utf-8",
    )
    return track_path


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(
        json.dumps(payload, indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return path


class ZoneMapLoader(unittest.TestCase):
    def test_production_map_loads(self) -> None:
        zone_map = tr.load_zone_map(tr.ZONE_MAP_DISTRICT)
        self.assertEqual(44, zone_map["cols"])
        self.assertEqual(26, zone_map["row_count"])
        self.assertEqual(32, zone_map["tile_size"])
        self.assertEqual([(0, 13), (42, 13)], zone_map["transition_tiles"])

    def test_anchoring_bound_to_the_frozen_v32_era_content_pin(self) -> None:
        """The zone-map manifest is a FROZEN v32-era banked input: the v32
        scene-exp manifest byte-pins this file and the standing scene check
        recomposes the banked artifacts from it. Its anchoring therefore
        binds to the district.json content it was derived from (sha below,
        at game ad7f6a1e5700481c0ed455970790e66d89501358) - NOT to the live
        runtime-baseline pin, which moves with upstream zone development
        (owner-ratified retarget, 2026-08-29: game 005eab3 rethemed ZONE 2
        to descent floor -1, invalidating live-equality)."""
        manifest = json.loads(
            tr.ZONE_MAP_DISTRICT.read_text(encoding="utf-8")
        )
        self.assertEqual(
            "9774cdd04ebaf6e1a429a1aceb26ca8b7ddd13f97f3086ff862d22ee305cd5f4",
            manifest["anchoring"]["source_sha256_lf"],
        )
        self.assertEqual(
            "data/zones/district.json", manifest["anchoring"]["source_file"]
        )

    def _refuses(self, payload: dict, needle: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(Path(tmp) / "map.json", payload)
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_zone_map(path)
            self.assertIn(needle, str(ctx.exception))

    def test_bad_glyph_refuses(self) -> None:
        self._refuses(
            {"tile_size": 32, "tiles": ["#.", ".X"], "transitions": []},
            "zone-map-invalid: unknown tile glyphs",
        )

    def test_ragged_rows_refuse(self) -> None:
        self._refuses(
            {"tile_size": 32, "tiles": ["#.", "."], "transitions": []},
            "ragged",
        )

    def test_wrong_tile_size_refuses(self) -> None:
        self._refuses(
            {"tile_size": 16, "tiles": ["#.", ".."], "transitions": []},
            "tile_size",
        )

    def test_transition_on_wall_refuses(self) -> None:
        self._refuses(
            {"tile_size": 32, "tiles": ["#.", ".."],
             "transitions": [{"at": [0, 0]}]},
            "sits on a wall glyph",
        )

    def test_transition_outside_map_refuses(self) -> None:
        self._refuses(
            {"tile_size": 32, "tiles": ["#.", ".."],
             "transitions": [{"at": [5, 0]}]},
            "outside the map",
        )


class SceneReferenceLoader(unittest.TestCase):
    def test_production_reference_matches_render_reference(self) -> None:
        loaded = scene_ref()
        tr._assert_scene_reference_consistent(loaded, reference())
        self.assertEqual([235, 120, 40], loaded["kit_body"]["striker"])
        self.assertEqual([190, 80, 35], loaded["kit_body"]["blocker"])
        self.assertEqual([225, 170, 90], loaded["kit_body"]["lobber"])
        self.assertEqual([205, 198, 180], loaded["kit_body"]["rusher_hater"])
        self.assertEqual([205, 198, 180], loaded["default_body_rgb"])

    def test_anchoring_bound_to_runtime_baseline_content_pin(self) -> None:
        manifest = json.loads(
            tr.SCENE_REFERENCE_FILE.read_text(encoding="utf-8")
        )
        baseline = json.loads(
            (REPO / "manifests" / "runtime-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        pin = next(
            f["sha256_lf"] for f in baseline["source_files"]
            if f["path"] == "src/app/renderer.rb"
        )
        self.assertEqual(pin, manifest["anchoring"]["source_sha256_lf"])
        self.assertEqual(
            "src/app/renderer.rb", manifest["anchoring"]["source_file"]
        )

    def test_missing_kit_body_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(
                Path(tmp) / "ref.json",
                {"default_body_rgb": [1, 2, 3], "body_size": 28,
                 "notch": {"size": 6, "rgb": [20, 14, 12]},
                 "lunge": {"windup_px": -3, "active_px": 6}},
            )
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_scene_reference(path)
            self.assertIn("kit_body", str(ctx.exception))

    def test_bad_rgb_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(
                Path(tmp) / "ref.json",
                {"kit_body": {"striker": [235, 120]},
                 "default_body_rgb": [1, 2, 3], "body_size": 28,
                 "notch": {"size": 6, "rgb": [20, 14, 12]},
                 "lunge": {"windup_px": -3, "active_px": 6}},
            )
            with self.assertRaises(tr.RecomposeError) as ctx:
                tr.load_scene_reference(path)
            self.assertIn("RGB triple", str(ctx.exception))

    def test_mismatch_with_render_reference_stops(self) -> None:
        loaded = scene_ref()
        loaded["body_size"] = 27
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr._assert_scene_reference_consistent(loaded, reference())
        self.assertIn("scene-reference-mismatch", str(ctx.exception))


class NotchGeometry(unittest.TestCase):
    """The engine's three-branch facing-notch law (renderer.rb:863-877) is
    total over integer facings - all four cardinals, diagonals, and the
    degenerate zero vector draw mechanically."""

    def setUp(self) -> None:
        self.ref = scene_ref()

    def draw(self, facing: list[int]):
        from png_writer import Rgba8Canvas

        cv = Rgba8Canvas(40, 40, BG)
        tr.draw_primitive_creature(cv, 4, 4, facing, [235, 120, 40], self.ref)
        return cv

    def test_down_notch_bottom_center(self) -> None:
        cv = self.draw([0, 1])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 14, 4 + 25))
        self.assertEqual((235, 120, 40, 255), canvas_px(cv, 4 + 14, 4 + 4))

    def test_up_notch_top_center(self) -> None:
        cv = self.draw([0, -1])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 14, 4 + 2))
        self.assertEqual((235, 120, 40, 255), canvas_px(cv, 4 + 14, 4 + 25))

    def test_right_notch_right_center(self) -> None:
        cv = self.draw([1, 0])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 25, 4 + 14))
        self.assertEqual((235, 120, 40, 255), canvas_px(cv, 4 + 2, 4 + 14))

    def test_left_notch_left_center(self) -> None:
        cv = self.draw([-1, 0])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 2, 4 + 14))
        self.assertEqual((235, 120, 40, 255), canvas_px(cv, 4 + 25, 4 + 14))

    def test_diagonal_corner_notch(self) -> None:
        cv = self.draw([1, 1])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 25, 4 + 25))
        self.assertEqual((235, 120, 40, 255), canvas_px(cv, 4 + 2, 4 + 2))

    def test_zero_facing_draws_top_center(self) -> None:
        cv = self.draw([0, 0])
        self.assertEqual(NOTCH, canvas_px(cv, 4 + 14, 4 + 2))


class LungeLaw(unittest.TestCase):
    """The engine's draw-only lunge law (renderer.rb:879-888): pack only,
    special-suppressed, windup/active along facing."""

    def setUp(self) -> None:
        self.ref = scene_ref()

    def test_pack_windup_sinks_back(self) -> None:
        r = record(attack_state="windup", state_frames=3,
                   current_action="attack", facing=[1, 0])
        self.assertEqual((-3, 0), tr.scene_lunge(r, "pack", self.ref))

    def test_pack_active_lunges_forward(self) -> None:
        r = record(attack_state="active", state_frames=2,
                   current_action="attack", facing=[0, 1])
        self.assertEqual((0, 6), tr.scene_lunge(r, "pack", self.ref))

    def test_special_is_suppressed(self) -> None:
        r = record(attack_state="active", state_frames=2,
                   current_action="special", facing=[1, 0])
        self.assertEqual((0, 0), tr.scene_lunge(r, "pack", self.ref))

    def test_human_never_lunges(self) -> None:
        r = record(attack_state="active", state_frames=2,
                   current_action="attack", facing=[1, 0])
        self.assertEqual((0, 0), tr.scene_lunge(r, "human", self.ref))

    def test_idle_and_recovery_zero(self) -> None:
        self.assertEqual(
            (0, 0), tr.scene_lunge(record(), "pack", self.ref)
        )
        r = record(attack_state="recovery", state_frames=4,
                   current_action="attack")
        self.assertEqual((0, 0), tr.scene_lunge(r, "pack", self.ref))


class KitColors(unittest.TestCase):
    def test_pinned_kits_map(self) -> None:
        ref = scene_ref()
        self.assertEqual([235, 120, 40], tr.scene_body_rgb("striker", ref))
        self.assertEqual([190, 80, 35], tr.scene_body_rgb("blocker", ref))
        self.assertEqual([225, 170, 90], tr.scene_body_rgb("lobber", ref))
        self.assertEqual(
            [205, 198, 180], tr.scene_body_rgb("rusher_hater", ref)
        )

    def test_unlisted_kit_defaults_to_human_body(self) -> None:
        ref = scene_ref()
        self.assertEqual([205, 198, 180], tr.scene_body_rgb("rusher", ref))
        self.assertEqual([205, 198, 180], tr.scene_body_rgb("unknown", ref))


class ParticipantIntersection(unittest.TestCase):
    VIEW = {"origin_px": [0, 0], "width": 64, "height": 64}

    def entries(self, tick_creatures: dict, roster: list[dict]):
        tick = {"frame": 1, "creatures": tick_creatures, "masks": {"1": 0}}
        kit_by_name = {c["name"]: c["kit"] for c in roster}
        faction_by_name = {c["name"]: c["faction"] for c in roster}
        constants = {**kit_constants()["striker"],
                     "windup_px": -3, "active_px": 6}
        return tr.scene_tick_entries(
            tick, self.VIEW, scene_ref(), kit_by_name, faction_by_name,
            "striker_1", constants,
        )

    ROSTER = [
        {"name": "striker_1", "faction": "pack", "kit": "striker"},
        {"name": "n_1", "faction": "human", "kit": "rusher"},
    ]

    def test_inside_is_drawn(self) -> None:
        drawn, omitted = self.entries(
            {"striker_1": record(px=16.0, py=16.0, possessed=True),
             "n_1": record(px=20.0, py=20.0)},
            self.ROSTER,
        )
        self.assertEqual(2, len(drawn))
        self.assertEqual([], omitted)

    def test_outside_is_omitted(self) -> None:
        drawn, omitted = self.entries(
            {"striker_1": record(px=16.0, py=16.0, possessed=True),
             "n_1": record(px=200.0, py=20.0)},
            self.ROSTER,
        )
        self.assertEqual(["n_1"], omitted)

    def test_edge_touch_is_exclusive(self) -> None:
        drawn, omitted = self.entries(
            {"striker_1": record(px=16.0, py=16.0, possessed=True),
             "n_1": record(px=64.0, py=20.0)},
            self.ROSTER,
        )
        self.assertEqual(["n_1"], omitted)
        drawn, omitted = self.entries(
            {"striker_1": record(px=16.0, py=16.0, possessed=True),
             "n_1": record(px=63.0, py=20.0)},
            self.ROSTER,
        )
        self.assertEqual([], omitted)

    def test_lunge_moves_a_neighbor_into_the_window(self) -> None:
        roster = [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
            {"name": "p_1", "faction": "pack", "kit": "blocker"},
        ]
        base = {"striker_1": record(px=16.0, py=16.0, possessed=True)}
        idle = dict(base, p_1=record(px=64.0, py=20.0))
        drawn, omitted = self.entries(idle, roster)
        self.assertEqual(["p_1"], omitted)
        windup = dict(
            base,
            p_1=record(px=64.0, py=20.0, facing=[1, 0],
                       attack_state="windup", state_frames=3,
                       current_action="attack"),
        )
        drawn, omitted = self.entries(windup, roster)
        self.assertEqual([], omitted)
        self.assertEqual(61, drawn[-1]["wx"])


class DrawOrder(unittest.TestCase):
    VIEW = {"origin_px": [0, 0], "width": 96, "height": 96}

    def test_humans_before_pack_then_y_then_name(self) -> None:
        roster = [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
            {"name": "h_b", "faction": "human", "kit": "rusher"},
            {"name": "h_a", "faction": "human", "kit": "rusher"},
            {"name": "p_1", "faction": "pack", "kit": "blocker"},
        ]
        tick = {
            "frame": 1,
            "creatures": {
                "striker_1": record(px=10.0, py=10.0, possessed=True),
                "h_b": record(px=40.0, py=20.0),
                "h_a": record(px=50.0, py=20.0),
                "p_1": record(px=20.0, py=5.0),
            },
            "masks": {"1": 0},
        }
        kit_by_name = {c["name"]: c["kit"] for c in roster}
        faction_by_name = {c["name"]: c["faction"] for c in roster}
        constants = {**kit_constants()["striker"],
                     "windup_px": -3, "active_px": 6}
        drawn, _ = tr.scene_tick_entries(
            tick, self.VIEW, scene_ref(), kit_by_name, faction_by_name,
            "striker_1", constants,
        )
        self.assertEqual(["h_a", "h_b", "p_1", "striker_1"],
                         [e["name"] for e in drawn])

    def test_unknown_faction_refuses_typed(self) -> None:
        roster = [
            {"name": "striker_1", "faction": "pack", "kit": "striker"},
            {"name": "x_1", "faction": "ghost", "kit": "rusher"},
        ]
        tick = {
            "frame": 1,
            "creatures": {
                "striker_1": record(px=10.0, py=10.0, possessed=True),
                "x_1": record(px=20.0, py=20.0),
            },
            "masks": {"1": 0},
        }
        kit_by_name = {c["name"]: c["kit"] for c in roster}
        faction_by_name = {c["name"]: c["faction"] for c in roster}
        constants = {**kit_constants()["striker"],
                     "windup_px": -3, "active_px": 6}
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.scene_tick_entries(
                tick, self.VIEW, scene_ref(), kit_by_name, faction_by_name,
                "striker_1", constants,
            )
        self.assertIn("scene-unknown-faction", str(ctx.exception))

    def test_later_neighbor_draws_over_earlier(self) -> None:
        from png_writer import Rgba8Canvas

        base = Rgba8Canvas(96, 96, BG)
        entries = [
            {"name": "a", "kind": "neighbor", "faction": "human",
             "kit": "rusher", "wx": 10, "wy": 10, "facing": [1, 0],
             "decision": None},
            {"name": "b", "kind": "neighbor", "faction": "human",
             "kit": "rusher_hater", "wx": 20, "wy": 20, "facing": [1, 0],
             "decision": None},
        ]
        cv = tr.scene_cell(
            base, entries, self.VIEW, {}, merged_reference(), scene_ref()
        )
        # overlap zone: both bodies cover (24, 24); b drew later
        self.assertEqual((205, 198, 180, 255), canvas_px(cv, 24, 24))
        # a's exclusive zone
        self.assertEqual((205, 198, 180, 255), canvas_px(cv, 12, 12))

    def test_subject_ring_and_sprite_draw_at_slot(self) -> None:
        from png_writer import Rgba8Canvas

        poses = tr.load_poses(tr.default_dirs())
        base = Rgba8Canvas(96, 96, BG)
        entries = [
            {"name": "n", "kind": "neighbor", "faction": "pack",
             "kit": "blocker", "wx": 32, "wy": 32, "facing": [0, 1],
             "decision": None},
            {"name": "s", "kind": "subject", "faction": "pack",
             "kit": "striker", "wx": 32, "wy": 32, "facing": [1, 0],
             "decision": {"pose": "idle", "pose_facing": "right",
                          "offset_px": 0}},
        ]
        cv = tr.scene_cell(
            base, entries, self.VIEW, poses, merged_reference(), scene_ref()
        )
        # the banked draw_ring convention: 3px band outside the sprite's
        # opaque body box [2,2,29,29] -> ring rows at wy+2-3 = 31
        self.assertEqual(RING, canvas_px(cv, 32 + 15, 31))
        self.assertEqual(RING, canvas_px(cv, 31, 32 + 15))


class TileLayer(unittest.TestCase):
    def test_floor_wall_transition_void_pixels_and_census(self) -> None:
        zone_map = tiny_zone_map(["#.", ".."], transitions=[(1, 0)])
        view = {"origin_px": [-32, -32], "width": 128, "height": 128}
        zone = merged_reference()["zones"]["district"]
        cv, census = tr.scene_tile_base(view, zone_map, zone)
        self.assertEqual(
            {"floor": 2, "wall": 1, "transition": 1, "void": 12}, census
        )
        self.assertEqual(BG, canvas_px(cv, 0, 0))          # void
        self.assertEqual(WALL, canvas_px(cv, 40, 40))       # wall (0,0)
        self.assertEqual(GOLD, canvas_px(cv, 80, 48))       # transition core
        self.assertEqual(FLOOR, canvas_px(cv, 40, 72))      # floor body
        # the banked draw_floor_tile grid edge (top/left of each floor tile)
        self.assertEqual((46, 38, 26, 255), canvas_px(cv, 40, 64))

    def test_unaligned_window_refuses(self) -> None:
        zone_map = tiny_zone_map(["#.", ".."])
        zone = merged_reference()["zones"]["district"]
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.scene_tile_base(
                {"origin_px": [-30, -32], "width": 128, "height": 128},
                zone_map, zone,
            )
        self.assertIn("scene-window-unaligned", str(ctx.exception))


class SceneWindowFormula(unittest.TestCase):
    def setUp(self) -> None:
        self.track = scene_track()
        self.merged = merged_reference()
        entries = tr.subject_decision_entries(
            self.track, self.merged, "striker_1"
        )
        constants = tr.mapping_constants(self.track, "striker", self.merged)
        self.span = tr.derive_span(entries, constants)
        self.assertIsNotNone(self.span)

    def test_margin_one_equals_the_banked_v31_formula(self) -> None:
        first, last = self.span
        self.assertEqual(
            tr.derive_window(
                self.track, "striker_1", first, last, self.merged
            ),
            tr.scene_window(
                self.track, "striker_1", first, last, self.merged,
                margin_tiles=1,
            ),
        )

    def test_margin_four_expands_three_tiles_each_side(self) -> None:
        first, last = self.span
        one = tr.scene_window(
            self.track, "striker_1", first, last, self.merged, margin_tiles=1
        )
        four = tr.scene_window(
            self.track, "striker_1", first, last, self.merged, margin_tiles=4
        )
        self.assertEqual(one["origin_px"][0] - 96, four["origin_px"][0])
        self.assertEqual(one["origin_px"][1] - 96, four["origin_px"][1])
        self.assertEqual(one["width"] + 192, four["width"])
        self.assertEqual(one["height"] + 192, four["height"])
        self.assertEqual(0, four["origin_px"][0] % 32)
        self.assertEqual(0, four["width"] % 32)


class SheetDims(unittest.TestCase):
    def test_dims_formula(self) -> None:
        view = {"origin_px": [0, 0], "width": 64, "height": 64}
        width, height = tr.scene_sheet_dims(view, 8, "SPAN 1 TO 2")
        self.assertEqual(4 + 8 * 70 + 6, width)
        self.assertEqual(36 + (64 + 8 + 6) + 10, height)

    def test_oversize_sheet_stops_typed(self) -> None:
        view = {"origin_px": [0, 0], "width": 4090, "height": 64}
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.assert_scene_sheet_dims(view, 8, "SPAN 1 TO 2")
        self.assertIn("scene-sheet-dims", str(ctx.exception))


class PasteEquivalence(unittest.TestCase):
    """_paste_canvas_scaled must be byte-identical to the banked
    blit_scaled(canvas_pixels(...)) path for fully-opaque frames (the only
    class the scene builders feed it)."""

    def test_paste_matches_the_banked_blit_at_both_scales(self) -> None:
        from make_grammar_timeline import canvas_pixels
        from png_writer import Rgba8Canvas

        frame = Rgba8Canvas(16, 12, (7, 7, 7, 255))
        for x in range(16):
            for y in range(12):
                frame.put(x, y, ((x * 13) % 256, (y * 29) % 256, 99, 255))
        for scale in (1, 3):
            banked = Rgba8Canvas(80, 60, BG)
            banked.blit_scaled(canvas_pixels(frame), 5, 7, scale)
            fast = Rgba8Canvas(80, 60, BG)
            tr._paste_canvas_scaled(fast, frame, 5, 7, scale)
            self.assertEqual(banked.encode(), fast.encode(), f"scale {scale}")


class ScenePipeline(unittest.TestCase):
    """End-to-end on a tmpdir evidence bundle: the whole pre-registered
    pipeline behind the LIVE intake gate (the test_runtime_extract
    RuntimePipeline precedent; ONE real composition in the fast tier)."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.track = scene_track()
        self.track_path = write_fixture_bundle(self.root, self.track)
        self.out = self.root / "out"
        self.reference = reference()

    def make(self, **overrides):
        kwargs = {
            "out_dir": self.out,
            "evidence_root": self.root,
            "expected_span": (100, 106),
        }
        kwargs.update(overrides)
        return tr.make_scene_artifacts(
            self.track_path, self.reference, tr.default_dirs(), **kwargs
        )

    def test_pipeline_produces_the_scene_bundle(self) -> None:
        merged = tr.load_zone_palette(self.reference, PALETTE)
        entries = tr.subject_decision_entries(
            self.track, merged, "striker_1"
        )
        banked = write_json(
            self.root / "banked-decisions.json", {"entries": entries}
        )
        manifest = self.make(banked_decisions=banked)
        self.assertEqual("SCENE-EXP", manifest["artifact_class"])
        self.assertEqual(tr.MAPPING_ID, manifest["mapping_id"])
        self.assertEqual(
            tr.SCENE_COMPOSITION_ID, manifest["scene_composition_id"]
        )
        self.assertEqual(tr.SCENE_EXP_DISCLOSURE, manifest["disclosure"])
        self.assertEqual(
            7,
            manifest["subject_decisions_equality"]["entries_compared"],
        )
        self.assertEqual([100, 106], manifest["span_frames"])
        self.assertTrue(manifest["span_equality"]["equal"])
        self.assertTrue(manifest["determinism"]["double_build_identical"])
        self.assertEqual(7, manifest["ticks"])
        self.assertLess(manifest["sheet_dims"][0], tr.SCENE_MAX_SHEET_DIM)
        self.assertLess(manifest["sheet_dims"][1], tr.SCENE_MAX_SHEET_DIM)
        for name, digest in manifest["artifacts"].items():
            path = self.out / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(digest, tr.file_sha256(path), name)
        participants = json.loads(
            (self.out / tr.SCENE_PARTICIPANTS.name).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(7, participants["totals"]["neighbor_draw_events"])
        self.assertEqual(
            7, participants["totals"]["neighbor_omission_events"]
        )
        self.assertEqual(
            1, participants["totals"]["neighbors_drawn_at_least_once"]
        )
        self.assertEqual([], participants["findings"])
        self.assertEqual(
            7, participants["per_creature"]["blocker_1"]["ticks_drawn"]
        )
        self.assertEqual(
            7, participants["per_creature"]["rusher_1"]["ticks_omitted"]
        )
        self.assertGreater(participants["tile_census"]["void"], 0)

    def test_span_regression_stops_before_any_write(self) -> None:
        with self.assertRaises(tr.RecomposeError) as ctx:
            self.make(expected_span=(100, 105))
        self.assertIn("scene-span-regression", str(ctx.exception))
        self.assertFalse((self.out / tr.SCENE_PARTICIPANTS.name).exists())

    def test_subject_decision_drift_stops_after_the_capture(self) -> None:
        merged = tr.load_zone_palette(self.reference, PALETTE)
        entries = tr.subject_decision_entries(
            self.track, merged, "striker_1"
        )
        entries[3]["decision"]["pose"] = "x0"  # tamper one banked decision
        banked = write_json(
            self.root / "banked-decisions.json", {"entries": entries}
        )
        with self.assertRaises(tr.RecomposeError) as ctx:
            self.make(banked_decisions=banked)
        self.assertIn("scene-subject-decision-drift", str(ctx.exception))
        self.assertTrue((self.out / tr.SCENE_PARTICIPANTS.name).is_file())
        self.assertFalse((self.out / tr.SCENE_SHEET.name).exists())

    def test_zero_neighbors_is_a_typed_finding_not_a_stop(self) -> None:
        track = scene_track(neighbor_px=4200.0)
        root = self.root / "zero"
        root.mkdir()
        track_path = write_fixture_bundle(root, track)
        out = root / "out"
        manifest = tr.make_scene_artifacts(
            track_path, self.reference, tr.default_dirs(), out_dir=out,
            evidence_root=root, expected_span=(100, 106),
        )
        self.assertEqual(["scene-zero-participants"], manifest["findings"])
        self.assertEqual(
            0, manifest["participants_summary"]["neighbor_draw_events"]
        )
        self.assertTrue((out / tr.SCENE_SHEET.name).is_file())

    def test_runtime_track_outside_a_bundle_refuses_at_the_gate(self) -> None:
        loose = self.root / "loose.json"
        write_json(loose, self.track)
        with self.assertRaises(tr.RecomposeError) as ctx:
            tr.make_scene_artifacts(
                loose, self.reference, tr.default_dirs(),
                out_dir=self.out, evidence_root=self.root,
            )
        self.assertIn(
            "runtime-intake-not-established", str(ctx.exception)
        )


if __name__ == "__main__":
    unittest.main()
