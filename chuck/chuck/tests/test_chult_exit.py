"""Phase 4's route-deeper boundary now enters Phase 5 Chult Map 2."""

from src.core import config
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_WALK_EXITS


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "chult_jungle.txt")


def test_chult_has_one_named_deeper_boundary() -> None:
    tilemap = _map()
    boundaries = [
        (kind, position)
        for kind, position in tilemap.object_spawns
        if kind.startswith("boundary:")
    ]
    assert len(boundaries) == 1
    kind, (x, y) = boundaries[0]
    assert kind == "boundary:chult_deeper"
    col = int(x // config.TILE_SIZE)
    row = int(y // config.TILE_SIZE)
    assert (col, row) == (31, 1)
    assert tilemap.terrain_at(col, row) == '"'
    assert not tilemap.is_solid(col, row)
    assert tilemap.is_solid(col, row - 1)


def test_worn_trail_connects_the_jungle_to_the_boundary() -> None:
    tilemap = _map()
    # The three-wide track remains continuous from the existing northern
    # clearing to the canopy threshold, with no accidental choke tile.
    for row in range(1, 9):
        for col in range(30, 33):
            assert tilemap.terrain_at(col, row) in {"'", '"'}
            assert not tilemap.is_solid(col, row)
    assert not tilemap.is_solid(31, 9)


def test_boundary_art_is_part_of_the_chult_tileset() -> None:
    tileset = tileset_for("chult_jungle")
    assert tileset.char_to_terrain["'"] == "jungle_trail"
    assert tileset.overhead_char_to_terrain['"'] == "jungle_exit"


def test_deeper_boundary_targets_chult_map_2() -> None:
    exit_config = AREA_WALK_EXITS[("chult_jungle", '"')]
    assert exit_config.destination == "chult_cog"
    assert exit_config.arrival == "from_chult_1"
    assert exit_config.facing == "up"


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Chult exit tests passed.")


if __name__ == "__main__":
    _run_all()
