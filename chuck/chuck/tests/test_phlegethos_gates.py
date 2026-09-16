"""Phlegethos's doorways: built at the temple's scale, and facing right.

Devils are not rat-sized. Every way between these maps is three tiles
wide with an arch over the middle one, the way every temple doorway is,
rather than the one-tile gaps the region shipped with.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.transitions import AREA_WALK_EXITS

MAPS = ("phlegethos_arrival", "phlegethos_road", "phlegethos_lake",
        "phlegethos_rubble_pass", "phlegethos_fractured_way",
        "phlegethos_fortress_approach")
# The threshold terrains, and the arch that goes over the middle of each.
GATES = {"∇": "⌂", "Δ": "⌄"}
ARCHES = {"⌂": "temple_arch_ns", "⌄": "temple_arch_ns",
          "«": "temple_arch_ew", "»": "temple_arch_ew"}


def _cells(tilemap, chars):
    return {(col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) in chars}


def test_every_way_between_these_maps_is_an_arch_three_tiles_wide() -> None:
    for name in MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
        arches = _cells(tilemap, ARCHES)
        assert arches, name
        for col, row in arches:
            arch = tilemap.terrain_at(col, row)
            assert TILE_DEFS[arch].prop == ARCHES[arch], (name, arch)
            # Three tiles: the arch, and its threshold either side --
            # across for a north/south gate, above and below for one
            # in a side wall.
            if arch in ("⌂", "⌄"):
                sides = [(col - 1, row), (col + 1, row)]
                wanted = {"⌂": "∇", "⌄": "Δ"}[arch]
            else:
                sides = [(col, row - 1), (col, row + 1)]
                wanted = "∇"
            for side in sides:
                assert tilemap.terrain_at(*side) == wanted, (name, side)
            # ...and every one of the three walks him through.
            for cell in [(col, row)] + sides:
                assert (name, tilemap.terrain_at(*cell)) in AREA_WALK_EXITS, \
                    (name, cell)
        # Nothing rat-sized is left: no lone threshold tile anywhere.
        for col, row in _cells(tilemap, GATES):
            neighbours = {tilemap.terrain_at(col + dx, row + dy)
                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
            assert neighbours & set(ARCHES) or neighbours & set(GATES), \
                (name, col, row)


def test_north_out_of_the_lake_is_north_into_the_pass() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_lake")
        scene._arrival_fade_t = None
        gate = next((col, row)
                    for row in range(scene.tilemap.height_tiles)
                    for col in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(col, row) == "⌂")
        scene.player.x = gate[0] * config.TILE_SIZE + 3
        scene.player.y = gate[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "phlegethos_rubble_pass"
        # Out of the pass's own south gate, still walking north.
        col, row = scene._player_tile()
        assert row >= scene.tilemap.height_tiles - 5, (col, row)
        assert scene.player.facing == "up"
        # ...and the paved lane reaches down to meet him.
        assert scene.tilemap.terrain_at(col, row - 1) == "≡"
    finally:
        game._shutdown()
