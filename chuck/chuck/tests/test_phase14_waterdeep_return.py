"""Phase 14's first slice: the same Waterdeep docks, returned to at midday."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import WATERDEEP_RETURN_FLAG
from src.world.tileset_layout import DOCKS, DOCKS_MIDDAY, tileset_for


def _cell(sheet: pygame.Surface, row: int, col: int) -> pygame.Surface:
    return sheet.subsurface(pygame.Rect(col * 16, row * 16, 16, 16))


def _rgb(cell: pygame.Surface) -> list[tuple[int, int, int]]:
    width, height = cell.get_size()
    return [
        cell.get_at((x, y))[:3]
        for y in range(height)
        for x in range(width)
    ]


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
        assert finale.tilemap._grid == opening.tilemap._grid
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
