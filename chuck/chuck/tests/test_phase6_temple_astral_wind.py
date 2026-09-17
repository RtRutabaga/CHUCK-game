"""Temple arches and Map 6's narrow winding Astral-jump connector."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.fall import fall_zone_kind
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "temple_astral_wind"


def _map(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _flood(tilemap: TileMap, start: tuple[int, int], *, block_astral=False):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in reached or tilemap.is_solid(*point):
                continue
            if block_astral and tilemap.terrain_at(*point) == "V":
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_every_temple_threshold_has_one_human_scale_stone_arch() -> None:
    maps = (
        "temple_entrance", "temple_spikes", "temple_skeletons",
        "temple_darts", "temple_snakes", "temple_astral_wind",
        "temple_shrine", "temple_gauntlet",
    )
    for name in maps:
        tilemap = _map(name)
        # Every map's two thresholds carry a monument: a stone arch, or
        # (Map 1's deeper door, session 114) the monumental gate facade.
        monuments = [kind for kind, _col, _row in tilemap.prop_tiles
                     if kind.startswith("temple_arch_")
                     or kind == "temple_gate"]
        assert len(monuments) == 2
        # No threshold remains a six- or eight-tile-wide repeated doorway.
        for row in tilemap._grid:
            run = 0
            for char in row:
                run = run + 1 if char in "Δ∇⌂⌄«»£" else 0
                assert run <= 3

    ns = Image.open(config.SPRITES_DIR / "objects" / "temple_arch_ns.png")
    ew = Image.open(config.SPRITES_DIR / "objects" / "temple_arch_ew.png")
    assert ns.size == (48, 38) and ew.size == (38, 48)
    assert ns.height > config.NPC_FRAME_H and ew.height > config.NPC_FRAME_H


def test_map_6_is_a_connected_narrow_winding_route_with_eight_jump_cuts() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 60)
    assert (47, 52) in _flood(tilemap, (17, 5))

    mandatory_cuts = (
        {(col, 9) for col in range(15, 20)}
        | {(25, row) for row in range(10, 15)}
        | {(col, 19) for col in range(33, 38)}
        | {(22, row) for row in range(24, 29)}
        | {(col, 34) for col in range(8, 13)}
        | {(19, row) for row in range(39, 44)}
        | {(col, 47) for col in range(28, 33)}
        | {(39, row) for row in range(50, 55)}
    )
    actual_astral = {
        (col, row) for row, line in enumerate(tilemap._grid)
        for col, char in enumerate(line) if char == "V"
    }
    # The eight full-width mandatory cuts remain, and session 118's
    # broken-reality scatter fractures the legs around them.
    assert mandatory_cuts <= actual_astral
    scatter = actual_astral - mandatory_cuts
    assert len(scatter) == 36
    # Scatter never widens a mandatory crossing beyond the ~2.3-tile
    # committed jump: no scatter cell touches a cut cardinally.
    for col, row in scatter:
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            assert (col + dc, row + dr) not in mandatory_cuts, (col, row)
    assert (47, 52) not in _flood(tilemap, (17, 5), block_astral=True)
    assert sum(row.count("i") for row in tilemap._grid) == 27

    # Session 124: spike pits joined the trial as the same fall family —
    # two bands (the entry chamber's mixed spike/Astral trench, and one
    # after the final cut) plus singles through the leg slaloms.
    spikes = {
        (col, row) for row, line in enumerate(tilemap._grid)
        for col, char in enumerate(line) if char == "♠"
    }
    assert len(spikes) == 18

    # The whole course stays completable with walking plus SINGLE-tile
    # hops (a jump clears exactly one hazard cell — Astral or spike —
    # and lands on safe floor), and every safe cell stays reachable, so
    # the hazards can never strand Chuck or gate progress behind a
    # longer jump.
    hazards = actual_astral | spikes
    safe = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
        and (col, row) not in hazards
    }
    reached = {(17, 5)}
    frontier = deque([(17, 5)])
    while frontier:
        col, row = frontier.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            walk = (col + dc, row + dr)
            if walk in safe and walk not in reached:
                reached.add(walk)
                frontier.append(walk)
            over = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            if over in hazards and land in safe and land not in reached:
                reached.add(land)
                frontier.append(land)
    assert reached == safe
    assert (47, 52) in reached

    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_temple_5") == 1
    assert kinds.count("anchor:temple_6_anchor") == 1
    assert kinds.count("boundary:temple_7") == 1
    assert not any(kind in {
        "rat", "zombie", "skeleton", "raptor", "massive_dinosaur", "snake",
    } for kind in kinds)


def test_falling_always_centers_chuck_on_the_hazard_tile() -> None:
    """Session 126: the fall triggers when Chuck's center crosses the
    hazard, which can leave his sprite mostly over the safe neighbor.
    The choreography glides him onto the hazard tile so the sink always
    reads as dropping INTO it — from every approach direction."""
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_6")
        scene._arrival_fade_t = None
        ts = config.TILE_SIZE
        # Enter the vertical cut at (25, 12) from its WEST side: center
        # just across the tile edge, sprite mostly over safe floor.
        scene.player.x = 25 * ts - scene.player.width / 2 + 1
        scene.player.y = 12 * ts + 4
        scene.update(0.01)
        assert scene._fall_t is not None  # the fall began
        # By the end of the glide window he is centered on the hazard.
        scene.update(config.FALL_DURATION * 0.4)
        center_x = scene.player.x + scene.player.width / 2
        center_y = scene.player.y + scene.player.height / 2
        assert abs(center_x - (25 * ts + ts / 2)) < 0.6
        assert abs(center_y - (12 * ts + ts / 2)) < 0.6
    finally:
        game._shutdown()


def test_astral_cuts_use_the_existing_fall_and_airborne_rules() -> None:
    tilemap = _map()

    class Box:
        x = 15 * config.TILE_SIZE + 3
        y = 9 * config.TILE_SIZE + 4
        width = config.PLAYER_HITBOX_W
        height = config.PLAYER_HITBOX_H

    assert fall_zone_kind(tilemap, Box(), airborne=False) == "astral"
    assert fall_zone_kind(tilemap, Box(), airborne=True) is None


def test_maps_5_and_6_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_5")
        scene._arrival_fade_t = None
        scene.player.x = 17 * config.TILE_SIZE + 3
        scene.player.y = 40 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "temple_6"
        assert scene._player_tile() == (17, 5)
        scene.update(0.0)
        assert scene.map_name == MAP_NAME

        scene.player.x = 17 * config.TILE_SIZE + 3
        scene.player.y = 2 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_snakes"
        assert game.active_checkpoint_id == "temple_5_return"
        assert scene._player_tile() == (17, 35)
        scene.update(0.0)
        assert scene.map_name == "temple_snakes"
    finally:
        game._shutdown()


def test_temple_6_checkpoint_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_6"]
    assert entry.display_name == "Temple 6"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_temple_5"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["temple_6_anchor"]
    assert anchor_entry.position == (276.0, 117.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_6")
        scene._arrival_fade_t = None
        anchor, = scene.anchors
        came_in = scene.anchors_system.respawn_position_for_chuck()
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 69
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_6_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # The door he came in by, not the Ashtray he touched.
        assert (scene.player.x, scene.player.y) == came_in
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == MAP_NAME
        assert resumed.active_checkpoint_id == "temple_6_anchor"
        assert scene.sanity.current == 69
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_map_6_uses_temple_art_music_and_enters_map_7_east() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "temple.png"
    assert tileset.char_to_terrain["V"] == "astral_void"
    assert AREA_MUSIC[MAP_NAME] == "temple.wav"
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC["temple_snakes"]
    # Session 121: the former inert east boundary now enters Map 7.
    assert AREA_WALK_EXITS[(MAP_NAME, "∇")].destination == "temple_shrine"
    assert AREA_WALK_EXITS[(MAP_NAME, "»")].destination == "temple_shrine"
    assert AREA_WALK_EXITS[(MAP_NAME, "Δ")].destination == "temple_snakes"
    assert AREA_WALK_EXITS[(MAP_NAME, "⌄")].destination == "temple_snakes"


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-arch/Astral-wind tests passed.")


if __name__ == "__main__":
    _run_all()
