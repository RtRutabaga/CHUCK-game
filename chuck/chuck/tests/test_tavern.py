"""Phase 3 Waterdeep tavern shell and doorway lifecycle tests."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.world_scene import WorldScene
from src.world.tilemap import TileMap


def _place_on_tile(scene: WorldScene, col: int, row: int) -> None:
    ts = config.TILE_SIZE
    scene.player.x = col * ts + (ts - scene.player.width) / 2
    scene.player.y = row * ts + (ts - scene.player.height) / 2


def test_tavern_shell_is_connected_and_readable() -> None:
    tavern = TileMap(config.MAPS_DIR / "waterdeep_tavern.txt")
    assert (tavern.width_tiles, tavern.height_tiles) == (30, 20)
    assert len(tavern.spawn_points) == 1
    assert tavern.terrain_at(14, 18) == ">"
    assert not tavern.is_solid(14, 18)

    kinds = [kind for kind, _, _ in tavern.prop_tiles]
    assert kinds.count("bar_counter") == 6
    assert kinds.count("tavern_table") == 3
    assert kinds.count("tavern_chair") == 12
    assert kinds.count("tavern_hearth") == 1
    assert kinds.count("cheese") == 4
    assert kinds.count("pantry_open") == 1
    cheese_tiles = {
        (col, row) for kind, col, row in tavern.prop_tiles if kind == "cheese"
    }
    assert cheese_tiles == {(13, 2), (14, 6), (14, 10), (14, 14)}
    assert all(not tavern.is_solid(col, row) for col, row in cheese_tiles)
    assert not tavern.is_solid(14, 1)

    occupants = {
        kind: (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tavern.object_spawns
        if kind.startswith("npc:")
    }
    assert occupants == {
        "npc:bartender": (6, 2),
        "npc:patron": (22, 10),
    }

    ts = config.TILE_SIZE
    spawn = tavern.spawn_points["player"]
    start = (int(spawn[0] // ts), int(spawn[1] // ts))
    reachable = {start}
    frontier = [start]
    while frontier:
        col, row = frontier.pop()
        for neighbor in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if neighbor not in reachable and not tavern.is_solid(*neighbor):
                reachable.add(neighbor)
                frontier.append(neighbor)
    every_walkable = {
        (col, row)
        for row in range(tavern.height_tiles)
        for col in range(tavern.width_tiles)
        if not tavern.is_solid(col, row)
    }
    assert reachable == every_walkable


def test_tavern_cheese_is_an_examinable_environmental_hook() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_tavern"))
        scene = game.scenes.current
        cheeses = [prop for prop in scene.props if prop.kind == "cheese"]
        assert len(cheeses) == 4
        assert not scene.pickups
        assert {npc.npc_id for npc in scene.npcs} == {"bartender", "patron"}
        assert all(
            frame.get_size() == (config.NPC_FRAME_W, config.NPC_FRAME_H)
            for npc in scene.npcs for frame in npc._frames.values()
        )

        cheese = cheeses[0]
        x, y, w, h = cheese.interaction_bounds()
        scene.player.x = x + (w - scene.player.width) / 2
        scene.player.y = y + (h - scene.player.height) / 2
        game.input._actions_just_pressed.add("interact")
        scene.update(0.01)
        dialogue = game.scenes.current
        assert isinstance(dialogue, DialogueScene)
        assert dialogue._lines == ["It is cheese."]
        assert len(cheeses) == 4
        assert cheese in scene.props
    finally:
        game._shutdown()


def test_open_docks_door_enters_tavern_and_returns_safely() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_docks"))
        scene = game.scenes.current
        scene.load_map("waterdeep_docks", arrival="sewer_outflow")
        scene.update(config.CLIMB_OUT_DURATION)
        assert scene._sewer_completed

        _place_on_tile(scene, 44, 17)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"
        assert scene._player_tile() == (14, 17)
        assert scene.player.facing == "up"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"

        _place_on_tile(scene, 14, 18)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_docks"
        assert scene._player_tile() == (44, 18)
        assert scene.player.facing == "down"
        assert scene._sewer_completed
        assert scene.tilemap.terrain_at(44, 17) == "v"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_docks"
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All tavern tests passed.")


if __name__ == "__main__":
    _run_all()
