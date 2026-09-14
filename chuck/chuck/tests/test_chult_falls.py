"""Chult Falls: the hidden map off Chult 4's western pocket."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.captain_chest import CaptainChest
from src.entities.player import Player
from src.systems.checkpoints import CHECKPOINT_BY_ID, KNOWN_PROGRESS_FLAGS
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

from tests.test_phase5_respite import StillInput


def _map(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _find(tilemap: TileMap, char: str) -> list[tuple[int, int]]:
    return [(col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) == char]


def _arrival(tilemap: TileMap, name: str) -> tuple[int, int]:
    (x, y), = [center for kind, center in tilemap.object_spawns
               if kind == f"arrival:{name}"]
    return int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)


def _flood(tilemap: TileMap, start, jump: bool = False) -> set:
    """Walkable tiles from start; with jump, one stream tile is cleared."""
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = (col + dx, row + dy)
            if not (0 <= point[0] < tilemap.width_tiles
                    and 0 <= point[1] < tilemap.height_tiles):
                continue
            if not tilemap.is_solid(*point):
                if point not in reached:
                    reached.add(point)
                    frontier.append(point)
            elif jump and tilemap.terrain_at(*point) == "≈":
                land = (point[0] + dx, point[1] + dy)
                if (0 <= land[0] < tilemap.width_tiles
                        and 0 <= land[1] < tilemap.height_tiles
                        and not tilemap.is_solid(*land)
                        and land not in reached):
                    reached.add(land)
                    frontier.append(land)
    return reached


def _place(scene, col: int, row: int) -> None:
    scene.player.x = col * config.TILE_SIZE + (
        config.TILE_SIZE - scene.player.width) / 2
    scene.player.y = row * config.TILE_SIZE + (
        config.TILE_SIZE - scene.player.height) / 2


def test_chult_4_west_wall_hides_a_way_through_under_jungle_art() -> None:
    respite = _map("chult_respite")
    exits = _find(respite, "ꝏ")
    assert exits == [(0, 30)]
    assert _find(respite, "Ꝓ") == [(1, 30), (2, 30)]
    # Walkable, but drawn over Chuck as the same dense jungle as the wall
    # above and below it -- the only tell is one tile of trail at its mouth.
    for char in ("ꝏ", "Ꝓ"):
        assert not TILE_DEFS[char].solid and TILE_DEFS[char].overhead
        assert tileset_for("chult_respite").overhead_char_to_terrain[char] \
            == "dense_jungle"
    assert respite.terrain_at(3, 30) == "'"
    assert respite.is_solid(0, 29) and respite.is_solid(0, 31)
    # It opens off the side pocket, which Chuck can walk to from Chult 4's
    # own arrival.
    arrival = _arrival(respite, "from_chult_3")
    assert (0, 30) in _flood(respite, arrival, jump=True)
    assert _arrival(respite, "from_chult_falls") == (4, 30)


def test_the_hidden_way_runs_both_ways_to_named_arrivals() -> None:
    assert AREA_WALK_EXITS[("chult_respite", "ꝏ")].destination == "chult_falls"
    assert AREA_WALK_EXITS[("chult_falls", "ð")].destination == "chult_respite"
    assert CHECKPOINT_BY_ID["chult_falls"].runtime_entry
    assert not CHECKPOINT_BY_ID["chult_4_from_falls"].development_visible
    assert AREA_MUSIC["chult_falls"] == "chult.wav"
    assert tileset_for("chult_falls") is tileset_for("chult_respite")

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_4")
        _place(scene, 0, 30)
        scene.update(0.0)
        assert scene.map_name == "chult_falls"
        assert game.active_checkpoint_id == "chult_falls"
        assert scene._player_tile() == _arrival(scene.tilemap, "from_chult_respite")
        scene.update(0.0)
        assert scene.map_name == "chult_falls"

        exit_col, exit_row = _find(scene.tilemap, "ð")[0]
        _place(scene, exit_col, exit_row)
        scene.update(0.0)
        assert scene.map_name == "chult_respite"
        assert game.active_checkpoint_id == "chult_4_from_falls"
        assert scene._player_tile() == (4, 30)
        scene.update(0.0)
        assert scene.map_name == "chult_respite"
    finally:
        game._shutdown()


def test_falls_pool_and_river_out_of_it_to_the_south_edge() -> None:
    falls = _map("chult_falls")
    assert (falls.width_tiles, falls.height_tiles) == (48, 40)
    assert _find(falls, "Ꝙ") == [(24, 9)]
    assert TILE_DEFS["Ꝙ"].prop == "chult_falls"
    # The pool is at the fall's foot, right under the anchor.
    assert falls.terrain_at(24, 10) == "≈"
    water = set(_find(falls, "≈")) | set(_find(falls, "Ꝝ"))
    start = (24, 10)
    reached = {start}
    frontier = deque(reached)
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in water and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert reached == water
    assert any(row == falls.height_tiles - 1 for _col, row in water)
    # Chult 4's stream tile, and a river the width of one jump.
    assert tileset_for("chult_falls").char_to_terrain["≈"] == "jungle_stream"
    for row in range(17, falls.height_tiles):
        assert sum(1 for col, r in water if r == row) <= 2, row
    assert _find(falls, "Ꝛ") and _find(falls, "Ꝝ")


def test_chest_is_across_the_river_and_takes_the_jump() -> None:
    falls = _map("chult_falls")
    arrival = _arrival(falls, "from_chult_respite")
    (chest,) = _find(falls, "Ꝟ")
    beside = {(chest[0] + dx, chest[1] + dy)
              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    assert not beside & _flood(falls, arrival)
    assert beside & _flood(falls, arrival, jump=True)
    assert chest[0] < 24  # the west bank

    # The jump itself, the committed one, over the river at row 22.
    assert falls.terrain_at(26, 22) == "≈"
    controls = StillInput()
    controls.movement = (-1.0, 0.0)
    player = Player(27 * config.TILE_SIZE + 3,
                    22 * config.TILE_SIZE + 4, controls)
    player.tilemap = falls
    player.facing = "left"
    player.update(0.2)
    assert player.x >= 27 * config.TILE_SIZE - 1
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert player.x < 26 * config.TILE_SIZE


def test_falls_chest_is_the_ruin_chest_twin_with_its_own_flags() -> None:
    tile = TILE_DEFS["Ꝟ"]
    assert tile.solid and tile.prop == "chult_falls_chest"
    for flag in ("chult_falls_chest_opened",
                 "chult_falls_chest_carton_collected"):
        assert flag in KNOWN_PROGRESS_FLAGS

    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_falls")
        chests = [p for p in scene.props if isinstance(p, CaptainChest)]
        assert len(chests) == 1
        chest = chests[0]
        assert chest.kind == "chult_falls_chest"
        assert chest.progress_flag == "chult_falls_chest_opened"
        assert chest.interact(None) == "examine_chult_falls_chest"
        chest.on_scratched()
        chest.update(CaptainChest.opening_duration)
        assert chest.opened
        assert game.progress.has("chult_falls_chest_opened")
        assert not game.progress.has("desert_ruin_chest_opened")
        assert not game.progress.has("captain_chest_opened")
        drop = chest.take_drop_position()
        carton = chest.create_pickup(drop, game.assets)
        assert carton.progress_flag == "chult_falls_chest_carton_collected"
        assert chest.interact(None) == "examine_chult_falls_chest_open"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_falls_move() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_falls")
        falls = [p for p in scene.props if p.kind == "chult_falls"]
        assert len(falls) == 1
        assert len(falls[0]._frames) == 4
    finally:
        game._shutdown()


def test_a_tortle_minds_the_chest_and_wants_chuck_gone() -> None:
    from src.systems.dialogue import DialogueSystem

    dialogue = DialogueSystem()
    assert dialogue.get("tortle") == ["Piss off!"]
    assert dialogue.get("tortle_repeat") == ["I said scram!"]

    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_falls")
        (tortle,) = [npc for npc in scene.npcs if npc.npc_id == "tortle"]
        (chest,) = _find(scene.tilemap, "Ꝟ")
        tile = (int(tortle.x + tortle.width / 2) // config.TILE_SIZE,
                int(tortle.y + tortle.height / 2) // config.TILE_SIZE)
        assert abs(tile[0] - chest[0]) <= 2 and tile[1] == chest[1]
        # His sheet is shell-wide, and all three facings load.
        assert tortle.frame_width == 24
        assert set(tortle._frames) == {"down", "up", "left", "right"}
        assert tortle._frames["down"].get_size() == (24, config.NPC_FRAME_H)
        assert tortle.interaction_bounds()[2] == 24 + 6

        assert tortle.interact(scene.player) == "tortle"
        assert scene._second_word(tortle, "tortle") == "tortle"
        assert scene._second_word(tortle, "tortle") == "tortle_repeat"
        assert scene._second_word(tortle, "tortle") == "tortle_repeat"
    finally:
        game._shutdown()
        directory.cleanup()
