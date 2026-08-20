"""Phase 12's authored Cabin interior and reversible thresholds."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET, TAHUYA, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "tahuya_cabin_interior"


def _markers(tilemap):
    return {
        kind: (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
    }


def _flood(tilemap, start):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in found or tilemap.is_solid(x, y):
                continue
            found.add(point)
            queue.append(point)
    return found


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def test_interior_matches_the_authored_long_cabin_layout() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (21, 33)
    assert MAP_TILESET[MAP_NAME] == "tahuya"
    assert tileset_for(MAP_NAME) is TAHUYA
    assert AREA_MUSIC[MAP_NAME] == "cabin.wav"

    terrain = Counter(char for row in tilemap._grid for char in row)
    assert terrain["Ħ"] > terrain["Ŀ"] > 0
    assert terrain["Ƃ"] == 0
    assert terrain["ć"] >= 2 * 21 + 2 * 31 - 4
    assert tilemap.terrain_at(10, 0) == "Ƣ"
    assert tilemap.terrain_at(10, 32) == "Ɯ"

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props == {
        "cabin_big_couch": 1,
        "cabin_couch": 1,
        "cabin_chair": 2,
        "cabin_table": 1,
        "cabin_kitchen": 1,
        "cabin_woodstove": 1,
    }
    positions = {
        kind: (col, row) for kind, col, row in tilemap.prop_tiles
        if kind != "cabin_chair"
    }
    assert positions["cabin_big_couch"] == (5, 5)
    assert positions["cabin_couch"] == (16, 5)
    assert positions["cabin_table"] == (5, 11)
    assert positions["cabin_kitchen"] == (5, 29)
    assert positions["cabin_woodstove"] == (16, 25)
    # The southeast room is a complete enclosed section, not a prop-sized box.
    assert all(tilemap.terrain_at(x, 26) == "ć" for x in range(14, 20))
    assert all(tilemap.terrain_at(x, 31) == "ć" for x in range(14, 20))
    assert all(tilemap.terrain_at(14, y) == "ć" for y in range(26, 32))
    assert all(tilemap.terrain_at(19, y) == "ć" for y in range(26, 32))
    assert all(tilemap.terrain_at(x, y) == "Ħ"
               for y in range(27, 31) for x in range(15, 19))


def test_all_interior_routes_and_the_ashtray_are_reachable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    front = markers["arrival:from_front_door"]
    back = markers["arrival:from_back_door"]
    anchor = markers["anchor:tahuya_interior_anchor"]
    reachable = _flood(tilemap, front)
    assert back in reachable
    assert anchor in reachable
    assert (10, 0) in reachable and (10, 32) in reachable
    assert not any(kind.startswith(("rat", "raccoon", "zombie", "skeleton"))
                   for kind, _position in tilemap.object_spawns)


def test_front_and_back_thresholds_are_reversible_and_aligned() -> None:
    assert not TILE_DEFS["Ɛ"].solid and not TILE_DEFS["Ɣ"].solid
    assert not TILE_DEFS["Ɯ"].solid and not TILE_DEFS["Ƣ"].solid
    front_in = AREA_WALK_EXITS[("tahuya_cabin_exterior", "Ɛ")]
    front_out = AREA_WALK_EXITS[(MAP_NAME, "Ɯ")]
    back_in = AREA_WALK_EXITS[("tahuya_cabin_exterior", "Ɣ")]
    back_out = AREA_WALK_EXITS[(MAP_NAME, "Ƣ")]
    assert (front_in.destination, front_in.arrival, front_in.facing) == (
        MAP_NAME, "from_front_door", "up"
    )
    assert (front_out.destination, front_out.arrival, front_out.facing) == (
        "tahuya_cabin_exterior", "from_cabin_front", "down"
    )
    assert (back_in.destination, back_in.arrival, back_in.facing) == (
        MAP_NAME, "from_back_door", "down"
    )
    assert (back_out.destination, back_out.arrival, back_out.facing) == (
        "tahuya_cabin_exterior", "from_cabin_back", "up"
    )


def test_shared_loader_and_interior_ashtray_persist() -> None:
    entry = CHECKPOINT_BY_ID["tahuya_interior"]
    anchor = CHECKPOINT_BY_ID["tahuya_interior_anchor"]
    assert entry.display_name == "Cabin Interior"
    assert entry.runtime_entry and not entry.saveable
    assert anchor.saveable and not anchor.development_visible

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior", sanity=73)
        assert world.map_name == MAP_NAME
        assert world.player.facing == "up"
        assert world.sanity.current == 73
        assert game.checkpoints.saves.load() is None
        stove = next(prop for prop in world.props
                     if prop.kind == "cabin_woodstove")
        assert stove._size == (72, 82)
        assert len(stove._frames) == 6

        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", sanity=world.sanity.current
        )
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_interior_anchor"
        continued = game.checkpoints.continue_game()
        assert continued.map_name == MAP_NAME
        assert game.active_checkpoint_id == "tahuya_interior_anchor"

        back = game.checkpoints.load_checkpoint("tahuya_interior_back_entry")
        assert back.player.facing == "down"
        assert game.active_checkpoint_id == "tahuya_interior_back_entry"
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
    print("All Cabin interior tests passed.")


if __name__ == "__main__":
    _run_all()
