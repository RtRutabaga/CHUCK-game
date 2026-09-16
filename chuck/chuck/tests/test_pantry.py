"""Phase 3 pantry layout, materials, transition, and Astral retry tests."""

import os
from collections import Counter, deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.falling_cutscene_scene import (
    CANOPY_START, CIGARETTE_START, COMPLETE_TIME, IMPACT_TIME, LOOK_START,
    MUSIC_START, RESPAWN_TIME, VANISH_TIME, FallingCutsceneScene,
)
from src.scenes.world_scene import WorldScene
from src.world.tilemap import TileMap
from src.world.tileset_layout import PANTRY


def _place_on_tile(scene: WorldScene, col: int, row: int) -> None:
    ts = config.TILE_SIZE
    scene.player.x = col * ts + (ts - scene.player.width) / 2
    scene.player.y = row * ts + (ts - scene.player.height) / 2


def test_sky_cloud_tiles_have_stable_nonrepeating_variants() -> None:
    assert PANTRY.info()["sky_cloud"] == (12, 2)
    sheet = pygame.image.load(config.TILESETS_DIR / "pantry.png")
    sky_row = 3 * config.TILE_SIZE
    first_frames = []
    for variant in range(12):
        x = variant * 2 * config.TILE_SIZE
        cell = sheet.subsurface((x, sky_row, config.TILE_SIZE, config.TILE_SIZE))
        first_frames.append(pygame.image.tobytes(cell, "RGBA"))
    assert len(set(first_frames)) >= 10


def test_pantry_is_compact_readable_and_safely_navigable() -> None:
    pantry = TileMap(config.MAPS_DIR / "waterdeep_pantry.txt")
    assert (pantry.width_tiles, pantry.height_tiles) == (26, 18)
    terrain = Counter(ch for row in pantry._grid for ch in row)
    assert terrain["p"] > 250
    assert terrain["V"] == 30
    assert terrain["s"] == 55
    assert not pantry.is_solid(9, 10)  # Astral retains the fall-zone contract.
    assert not pantry.is_solid(11, 4)  # Sky is the successful fall route.

    props = Counter(kind for kind, _, _ in pantry.prop_tiles)
    assert props == Counter({
        "grain_sack": 4,
        "barrel": 2,
        "pantry_shelf": 2,
        "crate": 2,
        "pantry_open": 1,
        "cheese": 1,
        # Dressing that says food store without saying cheese: the one
        # cheese in the room is the hook.
        "pantry_sack_pile": 2,
        "pantry_produce_basket": 2,
    })
    cheese_tiles = {
        (col, row) for kind, col, row in pantry.prop_tiles if kind == "cheese"
    }
    assert cheese_tiles == {(11, 6)}
    # Chuck's committed hop travels only about 2.3 tiles. The cheese board is
    # four tiles from ordinary floor in every cardinal direction, so it reads
    # as tempting but remains the documented impossible pantry jump.
    assert config.JUMP_SPEED * config.JUMP_DURATION < 3 * config.TILE_SIZE
    assert all(
        pantry.terrain_at(11 + dx, 6 + dy) == "s"
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-2, 0), (2, 0), (0, -2), (0, 2))
    )

    sx, sy = pantry.spawn_points["player"]
    start = (int(sx // config.TILE_SIZE), int(sy // config.TILE_SIZE))
    seen = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for neighbor in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if (
                neighbor not in seen
                and pantry.terrain_at(*neighbor) == "p"
                and not pantry.is_solid(*neighbor)
            ):
                seen.add(neighbor)
                frontier.append(neighbor)
    safe_floor = {
        (col, row)
        for row in range(pantry.height_tiles)
        for col in range(pantry.width_tiles)
        if pantry.terrain_at(col, row) == "p" and not pantry.is_solid(col, row)
    }
    assert seen == safe_floor - cheese_tiles
    assert not (seen & cheese_tiles)


def test_pantry_doorway_is_bidirectional_without_bounce() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_tavern"))
        scene = game.scenes.current
        _place_on_tile(scene, 14, 1)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_pantry"
        assert scene._player_tile() == (13, 15)
        assert scene.player.facing == "up"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_pantry"

        _place_on_tile(scene, 13, 16)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"
        assert scene._player_tile() == (14, 2)
        assert scene.player.facing == "down"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"
    finally:
        game._shutdown()


def test_pantry_repeats_jump_hint_near_sky_blocks() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_pantry"))
        scene = game.scenes.current
        assert scene._hint is not None
        _place_on_tile(scene, 2, 15)
        assert not scene._jump_hint_visible()
        _place_on_tile(scene, 6, 6)
        assert scene.tilemap.terrain_at(8, 6) == "s"
        assert scene._jump_hint_visible()
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


def test_pantry_astral_floor_reuses_fall_and_local_retry() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_pantry"))
        scene = game.scenes.current
        spawn = (scene.player.x, scene.player.y)
        _place_on_tile(scene, 9, 10)
        scene.update(0.01)
        assert scene._fall_t == 0.0
        assert scene._fall_kind == "astral"
        assert scene.player.fall_progress == 0.0
        scene.update(config.FALL_DURATION)
        assert scene._respawn_phase == "out"
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        assert scene.map_name == "waterdeep_pantry"
        assert (scene.player.x, scene.player.y) == spawn
        assert scene.player.visible
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


def test_pantry_sky_fall_preserves_sanity_and_enters_cutscene() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_pantry"))
        world = game.scenes.current
        sanity_before = world.sanity.current
        _place_on_tile(world, 11, 4)
        world.update(0.01)
        assert world._fall_t == 0.0
        assert world._fall_kind == "sky"
        assert world.sanity.current == sanity_before

        world.update(config.FALL_DURATION)
        cutscene = game.scenes.current
        assert isinstance(cutscene, FallingCutsceneScene)
        assert world.sanity.current == sanity_before
        cloud_y = [cloud[1] for cloud in cutscene.clouds]

        game.input._actions_down.update({"move_up", "move_right"})
        cutscene.update(0.25)
        assert cutscene.elapsed == 0.25
        assert [cloud[1] for cloud in cutscene.clouds] != cloud_y
        assert not hasattr(cutscene, "player")
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


def test_falling_cutscene_completes_long_descent_and_jungle_return() -> None:
    game = Game()
    try:
        game.scenes.replace(FallingCutsceneScene(game))
        scene = game.scenes.current
        sounds = []
        music = []
        game.audio.play_sfx = sounds.append
        game.audio.play_music = lambda filename, loop=True: music.append(
            (filename, loop)
        )
        initial_clouds = [cloud[1] for cloud in scene.clouds]

        scene.update(MUSIC_START - 0.1)
        assert music == []
        scene.update(0.2)
        assert music == [("fall_to_chult.wav", False)]

        scene.update(CANOPY_START - scene.elapsed - 0.1)
        assert scene.phase == "fall"
        assert scene.elapsed > 20.0  # The open-sky hold is intentionally long.
        assert [cloud[1] for cloud in scene.clouds] != initial_clouds
        game.scenes.draw(game.native_surface)

        scene.update(1.0)
        assert scene.phase == "canopy"
        assert sounds == ["scratch"]
        game.scenes.draw(game.native_surface)

        scene.update(IMPACT_TIME - scene.elapsed)
        assert scene.phase == "impact"
        assert sounds == ["scratch", "scratch", "hurt"]
        game.scenes.draw(game.native_surface)

        scene.update(VANISH_TIME - scene.elapsed + 0.01)
        assert scene.phase == "vanished"
        assert sounds[-1] == "vanish"
        game.scenes.draw(game.native_surface)

        scene.update(RESPAWN_TIME - scene.elapsed + 0.01)
        assert scene.phase == "return"
        assert sounds[-1] == "respawn"
        game.scenes.draw(game.native_surface)

        scene.update(LOOK_START - scene.elapsed + 0.01)
        assert scene.phase == "look"
        game.scenes.draw(game.native_surface)

        scene.update(CIGARETTE_START - scene.elapsed + 0.01)
        assert scene.phase == "cigarette"
        assert not scene.cigarette_lit
        game.scenes.draw(game.native_surface)

        scene.update(COMPLETE_TIME - scene.elapsed + 0.01)
        assert scene.phase == "complete"
        assert scene.cutscene_complete and scene.cigarette_lit
        assert not hasattr(scene, "player")
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


def test_nothing_in_the_store_is_smooshed_into_anything_else() -> None:
    """The room's stores stand clear of each other and of the walls.

    Props are wider than their tile -- the shelf is 28 pixels across a
    16-pixel tile, the sack pile 30 -- so putting two of them side by
    side buries one in the other, and putting a wide one against the
    wall buries half of it in the wall. Both had happened along the
    north shelf wall and at the two sack piles.
    """
    from src.entities.prop import _SPRITES

    ts = config.TILE_SIZE
    pantry = TileMap(config.MAPS_DIR / "waterdeep_pantry.txt")
    boxes = []
    for kind, col, row in pantry.prop_tiles:
        sprite = pygame.image.load(config.SPRITES_DIR / _SPRITES[kind])
        width, height = sprite.get_size()
        boxes.append((kind, col, row, col * ts + ts // 2 - width // 2,
                      (row + 1) * ts - height, width, height))

    for kind, col, row, x, y, width, height in boxes:
        for tile_col in range(x // ts, (x + width - 1) // ts + 1):
            for tile_row in range(y // ts, row + 1):
                if (tile_col, tile_row) == (col, row):
                    continue
                if pantry.is_solid(tile_col, tile_row) and not any(
                        other[1:3] == (tile_col, tile_row) for other in boxes):
                    raise AssertionError(
                        f"{kind} at {(col, row)} is drawn into the wall at "
                        f"{(tile_col, tile_row)}")

    for index, first in enumerate(boxes):
        for second in boxes[index + 1:]:
            across = min(first[3] + first[5], second[3] + second[5])                 - max(first[3], second[3])
            down = min(first[4] + first[6], second[4] + second[6])                 - max(first[4], second[4])
            assert across <= 0 or down <= 0, (first[0], first[1:3],
                                              second[0], second[1:3])


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
    print("All pantry tests passed.")


if __name__ == "__main__":
    _run_all()
