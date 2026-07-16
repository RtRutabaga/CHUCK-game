"""Phase 5 Chult Map 2 foundation and shared checkpoint contract."""

from collections import deque
import os
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC


def _map(name: str = "chult_cog") -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def test_chult_map_2_is_substantially_larger_than_map_1() -> None:
    first = _map("chult_jungle")
    second = _map()
    assert (second.width_tiles, second.height_tiles) == (80, 80)
    assert second.width_tiles * second.height_tiles > (
        first.width_tiles * first.height_tiles * 1.5
    )


def test_chult_map_2_walkable_space_is_one_connected_exploration_area() -> None:
    tilemap = _map()
    walkable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
    }
    start = next(iter(walkable))
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in walkable and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert reached == walkable
    # Southern, central, and northern authored zones remain connected.
    assert {(40, 70), (40, 40), (40, 10)} <= reached


def test_chult_2_checkpoint_uses_the_shared_loader_definition() -> None:
    checkpoint = CHECKPOINT_BY_ID["chult_2"]
    assert checkpoint.display_name == "Chult 2"
    assert checkpoint.map_name == "chult_cog"
    assert checkpoint.arrival == "from_chult_1"
    assert checkpoint.facing == "up"
    assert checkpoint.runtime_entry
    assert checkpoint.development_visible
    assert checkpoint.required_flags == {
        "sewer_completed", "chult_reached"
    }
    arrivals = dict(
        (kind.removeprefix("arrival:"), position)
        for kind, position in _map().object_spawns
        if kind.startswith("arrival:")
    )
    assert arrivals["from_chult_1"] == (648.0, 1224.0)


def test_chult_map_2_reuses_the_chult_visual_and_audio_language() -> None:
    assert tileset_for("chult_cog") is tileset_for("chult_jungle")
    assert AREA_MUSIC["chult_cog"] == AREA_MUSIC["chult_jungle"]
    grass = [kind for kind, _ in _map().object_spawns
             if kind == "breakable_grass"]
    assert len(grass) == 10


def test_sailing_cog_is_one_oversized_solid_landmark() -> None:
    tilemap = _map()
    cogs = [entry for entry in tilemap.prop_tiles
            if entry[0] == "sailing_cog"]
    assert cogs == [("sailing_cog", 40, 64)]
    assert tilemap.terrain_at(40, 64) == ";"
    assert TILE_DEFS[";"].solid and TILE_DEFS[";"].under == "#"
    footprint = {
        59: range(40, 45),
        60: range(36, 47),
        61: range(34, 48),
        62: range(34, 48),
        63: range(35, 48),
        64: range(36, 47),
    }
    for row, columns in footprint.items():
        for col in columns:
            assert tilemap.is_solid(col, row)

    image = pygame.image.load(
        config.SPRITES_DIR / "objects" / "sailing_cog.png"
    )
    assert image.get_size() == (224, 152)
    assert image.get_width() >= config.CHUCK_FRAME_W * 18
    assert image.get_height() >= config.CHUCK_FRAME_H * 10
    mask = pygame.mask.from_surface(image)
    # The broad reference-style sail dominates the upper silhouette, while
    # the southwest hull begins at a sharp prow and recedes below it.
    assert sum(mask.get_at((x, 40)) for x in range(224)) >= 125
    assert mask.get_at((7, 96))
    assert not mask.get_at((7, 125))
    # The sail's lower overlap is foreground sail cloth, not deck planking.
    assert image.get_at((140, 74))[:3] == (191, 177, 128)
    # The exposed lower mast is painted over the deck, visibly anchoring the
    # sail assembly to the ship instead of letting deck planks erase it.
    assert image.get_at((115, 100))[:3] == (146, 102, 56)


def test_astral_sea_scatter_reuses_fall_tiles_without_blocking_progress() -> None:
    tilemap = _map()
    astral = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "V"
    }
    assert len(astral) == 24
    assert all(58 <= row <= 65 and 27 <= col <= 51
               for col, row in astral)
    assert not TILE_DEFS["V"].solid
    assert tileset_for("chult_cog").char_to_terrain["V"] == "astral_void"

    # Astral fragments pressure the ship approach, but neither side is a
    # mandatory fall crossing on the route deeper into the map.
    start = (40, 76)
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if (point not in reached and not tilemap.is_solid(*point)
                    and tilemap.terrain_at(*point) != "V"):
                reached.add(point)
                frontier.append(point)
    assert (40, 40) in reached


def test_phase_4_boundary_enters_chult_2_without_a_transition_bounce() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_anchor")
        scene.player.x = 31 * config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_W
        ) / 2
        scene.player.y = config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_H
        ) / 2
        scene.update(0.0)
        assert scene.map_name == "chult_cog"
        assert game.active_checkpoint_id == "chult_2"
        assert scene.player.facing == "up"
        assert scene._player_tile() == (40, 76)
        scene.update(0.0)
        assert scene.map_name == "chult_cog"
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 Chult Map 2 tests passed.")


if __name__ == "__main__":
    _run_all()
