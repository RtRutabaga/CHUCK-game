"""Phase 14's first slice: the same Waterdeep docks, returned to at midday."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.fisherman import FishermanNPC
from src.systems.checkpoints import WATERDEEP_RETURN_FLAG
from src.systems.waterdeep_finale import (
    DOCKED_SHIP_TILE, FISHERMAN_TILE, RETURN_TOWNSFOLK,
)
from src.world.tilemap import TileMap
from src.world.tileset_layout import DOCKS, DOCKS_MIDDAY, tileset_for


def _game() -> tuple[tempfile.TemporaryDirectory, Game]:
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def _cell(sheet: pygame.Surface, row: int, col: int) -> pygame.Surface:
    return sheet.subsurface(pygame.Rect(col * 16, row * 16, 16, 16))


def _rgb(cell: pygame.Surface) -> list[tuple[int, int, int]]:
    width, height = cell.get_size()
    return [
        cell.get_at((x, y))[:3]
        for y in range(height)
        for x in range(width)
    ]


def test_he_comes_back_to_the_board_he_left_from() -> None:
    """Beside Bobert, on the tile the game opened on.

    The phase is about recognising the place, and there is no stronger
    way to say "you are back" than standing him on the exact plank he
    started from with Bobert still asleep beside him and everything
    else louder and brighter. So the finale carries no position of its
    own: it lands on the map's own player marker, which is the one the
    opening uses, and the two cannot drift apart.

    It also fixes something worse than a preference. The explicit
    position it used to carry was tile (2, 13) -- open harbour. Water is
    solid on this map, so the return was putting Chuck inside a solid
    tile seven tiles off the end of the pier, which is why this test
    checks the ground under him rather than only the distance.
    """
    ts = config.TILE_SIZE
    landed = {}
    for checkpoint, flags in (("waterdeep_start", set()),
                              ("waterdeep_finale", {WATERDEEP_RETURN_FLAG})):
        directory, game = _game()
        try:
            for flag in flags:
                game.progress.enable(flag)
            world = game.checkpoints.load_checkpoint(
                checkpoint, progress_flags=set(flags))
            tile = (int(world.player.x) // ts, int(world.player.y) // ts)
            landed[checkpoint] = tile
            # On the dock, not in the harbour.
            assert not world.tilemap.is_solid(*tile), (checkpoint, tile)
            assert world.tilemap.terrain_at(*tile) == "=", (checkpoint, tile)

            barrel = next(
                (col, row) for kind, col, row in world.tilemap.prop_tiles
                if kind == "bobert_barrel"
            )
            reach = max(abs(tile[0] - barrel[0]), abs(tile[1] - barrel[1]))
            assert reach <= 1, (checkpoint, tile, barrel)
        finally:
            game._shutdown()
            directory.cleanup()

    # The same board, which is the point rather than a coincidence.
    assert landed["waterdeep_finale"] == landed["waterdeep_start"], landed


def test_return_state_selects_midday_art_without_duplicating_the_map() -> None:
    assert tileset_for("waterdeep_docks") is DOCKS
    assert tileset_for(
        "waterdeep_docks", waterdeep_returned=True
    ) is DOCKS_MIDDAY
    assert DOCKS.order == DOCKS_MIDDAY.order
    assert DOCKS.char_to_terrain == DOCKS_MIDDAY.char_to_terrain

    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_start")
        assert opening.tilemap.map_path.name == "waterdeep_docks.txt"
        assert opening.tilemap._tileset.sheet == "docks.png"

        finale = game.checkpoints.load_checkpoint(
            "waterdeep_finale", progress_flags={WATERDEEP_RETURN_FLAG}
        )
        assert finale.tilemap.map_path == opening.tilemap.map_path
        # The long-established sewer completion opens the tavern door at
        # runtime. Apart from that legitimate progression swap, both states
        # still parse the same authored environment.
        opening_after_sewer = [row.replace("D", "v")
                               for row in opening.tilemap._grid]
        assert finale.tilemap._grid == opening_after_sewer
        assert finale.tilemap._tileset.sheet == "docks_midday.png"
    finally:
        game._shutdown()
        directory.cleanup()


def test_midday_water_is_teal_and_the_whole_city_is_brighter() -> None:
    opening = pygame.image.load(str(config.TILESETS_DIR / DOCKS.sheet))
    midday = pygame.image.load(str(config.TILESETS_DIR / DOCKS_MIDDAY.sheet))
    water_row = next(
        index for index, (name, _variants, _frames) in enumerate(DOCKS.order)
        if name == "water"
    )
    opening_water = _rgb(_cell(opening, water_row, 0))
    midday_water = _rgb(_cell(midday, water_row, 0))

    opening_average = tuple(
        sum(pixel[channel] for pixel in opening_water) / len(opening_water)
        for channel in range(3)
    )
    midday_average = tuple(
        sum(pixel[channel] for pixel in midday_water) / len(midday_water)
        for channel in range(3)
    )
    assert midday_average[1] > midday_average[0] * 2.5
    assert midday_average[2] > midday_average[0] * 2.5
    assert midday_average[1] > opening_average[1] + 30

    opening_luma = sum(sum(pixel) for pixel in _rgb(opening))
    midday_luma = sum(sum(pixel) for pixel in _rgb(midday))
    assert midday_luma > opening_luma * 1.12


def test_midday_wall_keeps_torch_fixtures_but_extinguishes_flames() -> None:
    opening = pygame.image.load(str(config.TILESETS_DIR / DOCKS.sheet))
    midday = pygame.image.load(str(config.TILESETS_DIR / DOCKS_MIDDAY.sheet))
    torch_row = next(
        index for index, (name, _variants, _frames) in enumerate(DOCKS.order)
        if name == "castle_torch"
    )
    opening_a = _rgb(_cell(opening, torch_row, 0))
    opening_b = _rgb(_cell(opening, torch_row, 1))
    midday_a = _rgb(_cell(midday, torch_row, 0))
    midday_b = _rgb(_cell(midday, torch_row, 1))

    assert opening_a != opening_b, "opening torch should still flicker"
    assert midday_a == midday_b, "an extinguished fixture must not flicker"
    assert len(set(midday_a)) >= 4, "the dark metal fixture disappeared"
    assert not any(r > 220 and r > b * 1.5 for r, _g, b in midday_a)


def test_return_population_is_state_gated_and_noticeably_busier() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_start")
        opening_count = len(opening.npcs)
        assert not any(
            prop.kind == "waterdeep_docked_ship" for prop in opening.props
        )
        assert not any(isinstance(npc, FishermanNPC) for npc in opening.npcs)
        assert not any(
            npc.dialogue_id in {"return_dock_worker", "market_browser"}
            for npc in opening.npcs
        )

        finale = game.checkpoints.load_checkpoint("waterdeep_finale")
        ships = [
            prop for prop in finale.props
            if prop.kind == "waterdeep_docked_ship"
        ]
        fishermen = [npc for npc in finale.npcs
                     if isinstance(npc, FishermanNPC)]
        assert len(ships) == 1
        assert ships[0]._size == (224, 152)
        assert len(fishermen) == 1
        assert len(finale.npcs) == opening_count + 1 + len(RETURN_TOWNSFOLK)
        assert sum(n.dialogue_id == "return_dock_worker"
                   for n in finale.npcs) == 2
        assert sum(n.dialogue_id == "market_browser"
                   for n in finale.npcs) == 3
        assert finale.dialogue.get("return_dock_worker") == ["Busy today."]
        assert finale.dialogue.get("market_browser") == [
            "They don't sell anything in your size."
        ]
        assert finale.dialogue.get("fisherman") == ["They're not biting."]
    finally:
        game._shutdown()
        directory.cleanup()


def test_finale_dressing_uses_safe_authored_ground() -> None:
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    ship_col, ship_row = DOCKED_SHIP_TILE
    assert tilemap.terrain_at(ship_col, ship_row) == "~"

    assert tilemap.terrain_at(*FISHERMAN_TILE) == "="
    assert not tilemap.is_solid(*FISHERMAN_TILE)
    for spawn in RETURN_TOWNSFOLK:
        assert tilemap.terrain_at(*spawn.tile) == ","
        assert not tilemap.is_solid(*spawn.tile)


def test_fisherman_returns_to_his_fishing_idle_after_interaction() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_finale")
        fisherman = next(
            npc for npc in scene.npcs if isinstance(npc, FishermanNPC)
        )
        idle_before = fisherman._idle_t
        fisherman.interact(scene.player)
        assert fisherman.facing != "right"
        fisherman.update(0.81)
        assert fisherman.facing == "right"
        assert fisherman._idle_t > idle_before
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All Phase 14 Waterdeep-return tests passed.")


if __name__ == "__main__":
    _run_all()
