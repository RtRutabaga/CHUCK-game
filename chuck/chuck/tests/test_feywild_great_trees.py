"""The Feywild's great trees.

One per map on the maps with room, eleven tiles across and fourteen
tall. The placement rules are the ones the spots were chosen by, checked
against the shipped maps so a later edit to a map cannot quietly put a
crown over a marker or a trunk across a path. And because a tree this
tall can hide somebody completely, it thins out while anybody is
standing behind it -- which is tested with an enemy as well as Chuck.
"""

from collections import deque
import importlib
import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image

from src.core import config
from src.core.game import Game
from src.entities.prop import SEE_THROUGH_SOLID_BASE
from src.world.tilemap import MARKER_DEFS, TILE_DEFS, TileMap

sys.path.insert(0, "tools")
from feywild_great_tree_dressing import (  # noqa: E402
    GREAT_TREE, GREAT_TREE_ROOTS, GREAT_TREES_BY_MAP, footprint,
)


GROUND = set(".,'☼")
EXITS = set("⇧⇩←→")
CHECKPOINT_FOR = {"feywild_rootways": "feywild_4"}


def _rows(map_name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{map_name}.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if not line.startswith(";")]


def _solid(char: str) -> bool:
    marker = MARKER_DEFS.get(char)
    return TILE_DEFS[marker.under if marker else char].solid


def _regions(rows: list[str]) -> dict[tuple[int, int], int]:
    open_cells = {(x, y) for y, line in enumerate(rows)
                  for x, char in enumerate(line) if not _solid(char)}
    labels: dict[tuple[int, int], int] = {}
    label = 0
    for cell in open_cells:
        if cell in labels:
            continue
        labels[cell] = label
        queue = deque([cell])
        while queue:
            x, y = queue.popleft()
            for spot in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if spot in open_cells and spot not in labels:
                    labels[spot] = label
                    queue.append(spot)
        label += 1
    return labels


def test_the_tree_is_the_size_of_a_landmark() -> None:
    """Eleven tiles by fourteen, and several times any other Feywild tree."""
    objects = config.SPRITES_DIR / "objects"
    for variant in (1, 2, 3):
        with Image.open(objects / f"feywild_great_tree_{variant}.png") as tree:
            assert tree.size == (config.TILE_SIZE * 11, config.TILE_SIZE * 14)
    with Image.open(objects / "feywild_tree_1.png") as ordinary, \
            Image.open(objects / "feywild_great_tree_1.png") as great:
        assert great.height > ordinary.height * 3.5
        assert great.width > ordinary.width * 3.5


def test_one_great_tree_per_map_where_it_was_planted() -> None:
    for map_name, (col, row) in GREAT_TREES_BY_MAP.items():
        tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        trees = [(c, r) for kind, c, r in tilemap.prop_tiles
                 if kind == "feywild_great_tree"]
        assert trees == [(col, row)], (map_name, trees)
        rows = _rows(map_name)
        for x, y in footprint(col, row):
            assert rows[y][x] in (GREAT_TREE, GREAT_TREE_ROOTS), (map_name, x, y)
            assert tilemap.is_solid(x, y)


def test_there_is_room_to_walk_all_the_way_round_it() -> None:
    for map_name, (col, row) in GREAT_TREES_BY_MAP.items():
        rows = _rows(map_name)
        trunk = set(footprint(col, row))
        for x in range(col - 4, col + 5):
            for y in range(row - 3, row + 3):
                if (x, y) in trunk:
                    continue
                assert rows[y][x] in GROUND, (map_name, x, y, rows[y][x])


def test_nothing_that_matters_stands_under_the_crown() -> None:
    """No enemy, arrival, breakable or exit under fourteen tiles
    of leaves -- even thinned out, that is where a player loses it."""
    for map_name, (col, row) in GREAT_TREES_BY_MAP.items():
        rows = _rows(map_name)
        for x in range(col - 5, col + 6):
            for y in range(max(0, row - 13), row + 1):
                char = rows[y][x]
                assert char not in MARKER_DEFS and char not in EXITS, \
                    (map_name, x, y, char)


def test_a_trunk_cuts_nothing_off() -> None:
    """Take the tree away and every piece of ground is still one piece."""
    for map_name, (col, row) in GREAT_TREES_BY_MAP.items():
        rows = _rows(map_name)
        without = [list(line) for line in rows]
        for x, y in footprint(col, row):
            without[y][x] = "."
        before = _regions(["".join(line) for line in without])
        after = _regions(rows)
        pieces: dict[int, set[int]] = {}
        for cell, label in after.items():
            pieces.setdefault(before[cell], set()).add(label)
        split = {k: v for k, v in pieces.items() if len(v) > 1}
        assert not split, (map_name, split)


def test_regenerating_a_map_keeps_its_tree() -> None:
    """Planted from the generators as well as into the shipped files."""
    for map_name, (col, row) in GREAT_TREES_BY_MAP.items():
        module = importlib.import_module(f"generate_{map_name}")
        grid = module.build()
        assert grid[row][col] == GREAT_TREE, map_name


def test_the_crown_thins_while_anybody_is_behind_it() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("feywild_4")
        tree = next(prop for prop in scene.props if prop.see_through)
        col, row = GREAT_TREES_BY_MAP["feywild_rootways"]
        ts = config.TILE_SIZE

        def hold(x_tile, y_tile, seconds):
            for _ in range(round(seconds * 60)):
                scene.player.x = x_tile * ts + 4
                scene.player.y = y_tile * ts + 5
                scene.update(1 / 60)

        hold(col - 2, row - 3, 0.6)          # behind the trunk
        assert tree.veil == 1.0
        hold(col - 2, row + 2, 0.6)          # in front of it
        assert tree.veil == 0.0

        # An enemy behind it counts too.
        class Walker:
            hitbox = pygame.Rect((col - 1) * ts, (row - 4) * ts, 10, 8)
            sort_y = (row - 4) * ts + 8

        tree.update_veil([Walker()], 1.0)
        assert tree.veil == 1.0

        # Thinned above, solid at the roots.
        thin = tree._thinned_image(6)
        width, height = thin.get_size()
        crown = [(x, 90) for x in range(0, width, 3)
                 if tree._image.get_at((x, 90)).a == 255]
        assert crown and all(thin.get_at(p).a < 128 for p in crown)
        base_y = height - SEE_THROUGH_SOLID_BASE + 20
        roots = [(x, base_y) for x in range(0, width, 3)
                 if tree._image.get_at((x, base_y)).a == 255]
        assert roots and all(thin.get_at(p).a == 255 for p in roots)
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
    print("All great tree tests passed.")


if __name__ == "__main__":
    _run_all()
