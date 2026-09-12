"""The Feywild's root walls, redrawn to read as roots.

The old tile was four parallel diagonal bands; tiled into a wall it
became one even stripe and read as bark shingles or a brown rug. The new
one is a tangle of curved strands that only leave a tile at fixed points
on its edges, so the tangle carries on across the whole wall -- and the
test that matters is that it actually does, for every pair of variants
that can end up next to each other.
"""

import importlib
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import FEYWILD, TILE_PX

sys.path.insert(0, "tools")
from feywild_root_dressing import (  # noqa: E402
    KNOT_SPACING, ROOT_FACE, ROOT_FAMILY, ROOT_KNOT, ROOT_KNOT_FACE,
    ROOT_MAPS,
)


# The root colours in the tile: bark, its lit side, its rim, the grain.
ROOT_COLOURS = {(82, 55, 45), (125, 83, 55), (56, 38, 36), (42, 31, 34)}


def _sheet_row(name: str) -> list:
    pygame.display.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))
    sheet = pygame.image.load(str(config.ASSETS_DIR / "tilesets"
                                  / FEYWILD.sheet))
    order = [entry[0] for entry in FEYWILD.order]
    row = order.index(name)
    variants = FEYWILD.order[row][1]
    return [sheet.subsurface((v * TILE_PX, row * TILE_PX, TILE_PX, TILE_PX))
            for v in range(variants)]


def _is_root(tile, x, y) -> bool:
    return tuple(tile.get_at((x, y)))[:3] in ROOT_COLOURS


def _rows(map_name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{map_name}.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if not line.startswith(";")]


def test_the_tangle_carries_on_into_every_neighbour() -> None:
    """Every variant against every variant, left-right and top-bottom:
    wherever a root runs off one tile's edge, one runs on into the next."""
    tiles = _sheet_row("fey_root_wall")
    assert len(tiles) >= 8
    last = TILE_PX - 1
    for a in tiles:
        for b in tiles:
            across = [_is_root(a, last, y) for y in range(TILE_PX)]
            onward = [_is_root(b, 0, y) for y in range(TILE_PX)]
            mismatches = sum(x != y for x, y in zip(across, onward))
            assert mismatches <= 2, (across, onward)
            down = [_is_root(a, x, last) for x in range(TILE_PX)]
            below = [_is_root(b, x, 0) for x in range(TILE_PX)]
            assert sum(x != y for x, y in zip(down, below)) <= 2


def test_it_is_not_stripes_any_more() -> None:
    """No two variants alike, and plenty of both root and hollow in each."""
    tiles = _sheet_row("fey_root_wall")
    seen = set()
    for tile in tiles:
        picture = pygame.image.tobytes(tile, "RGB")
        assert picture not in seen
        seen.add(picture)
        root = sum(_is_root(tile, x, y) for x in range(16) for y in range(16))
        assert 90 < root < 250, root


def test_walls_have_a_front_face_where_they_stop_above_open_ground() -> None:
    for map_name in ROOT_MAPS:
        rows = _rows(map_name)
        for r, line in enumerate(rows):
            for c, char in enumerate(line):
                if char not in ROOT_FAMILY:
                    continue
                below = rows[r + 1][c] if r + 1 < len(rows) else None
                faces = char in (ROOT_FACE, ROOT_KNOT_FACE)
                assert faces == (below not in ROOT_FAMILY), \
                    (map_name, c, r, char, below)


def test_knots_stand_on_a_run_and_are_spaced_out() -> None:
    total = 0
    for map_name in ROOT_MAPS:
        rows = _rows(map_name)
        knots = [(c, r) for r, line in enumerate(rows)
                 for c, char in enumerate(line)
                 if char in (ROOT_KNOT, ROOT_KNOT_FACE)]
        total += len(knots)
        for c, r in knots:
            assert rows[r][c - 1] in ROOT_FAMILY and rows[r][c + 1] in ROOT_FAMILY
        for index, (c, r) in enumerate(knots):
            for oc, orow in knots[index + 1:]:
                assert max(abs(c - oc), abs(r - orow)) >= KNOT_SPACING
    assert total >= 10, total


def test_every_piece_of_root_wall_is_still_wall() -> None:
    for char in ROOT_FAMILY:
        assert TILE_DEFS[char].solid, char
    for map_name in ROOT_MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        rows = _rows(map_name)
        for r, line in enumerate(rows):
            for c, char in enumerate(line):
                if char in ROOT_FAMILY:
                    assert tilemap.is_solid(c, r), (map_name, c, r)


def test_regenerating_a_map_keeps_its_dressing() -> None:
    for map_name in ROOT_MAPS:
        grid = importlib.import_module(f"generate_{map_name}").build()
        chars = {char for line in grid for char in line}
        assert ROOT_FACE in chars, map_name


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
    print("All root wall tests passed.")


if __name__ == "__main__":
    _run_all()
