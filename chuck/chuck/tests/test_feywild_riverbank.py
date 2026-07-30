"""The first playable Feywild riverbank and its shared checkpoint entry."""

from collections import deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC


MAP_NAME = "feywild_riverbank"


def _markers(tilemap: TileMap) -> dict[str, tuple[int, int]]:
    ts = config.TILE_SIZE
    return {
        kind: (int(x // ts), int(y // ts))
        for kind, (x, y) in tilemap.object_spawns
    }


def test_riverbank_is_a_peaceful_winding_feywild_arrival() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (52, 36)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] is None

    terrain = "".join(tilemap._grid)
    assert terrain.count("~") >= 300
    assert terrain.count(",") >= 60
    assert terrain.count("'") >= 100
    assert TILE_DEFS["~"].solid

    markers = _markers(tilemap)
    assert set(markers) == {
        "arrival:from_river",
        "arrival:from_feywild_2",
        "anchor:feywild_anchor",
        "boundary:feywild_deeper",
    }
    assert markers["arrival:from_river"][0] < 20
    assert markers["boundary:feywild_deeper"][0] > 40

    enemy_kinds = {
        "rat", "zombie", "skeleton", "lemure", "horned_devil",
        "fire_snake", "raptor", "massive_dinosaur",
    }
    assert not (set(markers) & enemy_kinds)

    prop_kinds = [kind for kind, _col, _row in tilemap.prop_tiles]
    assert prop_kinds.count("feywild_tree") >= 4
    assert prop_kinds.count("feywild_spiral") >= 4
    assert prop_kinds.count("feywild_mushroom") >= 4


def test_arrival_anchor_and_deeper_boundary_are_walkably_connected() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_river"]
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if point in reached or tilemap.is_solid(*point):
                continue
            reached.add(point)
            frontier.append(point)

    assert markers["anchor:feywild_anchor"] in reached
    assert markers["boundary:feywild_deeper"] in reached


def test_feywild_entry_and_ashtray_use_the_shared_checkpoint_system() -> None:
    entry = CHECKPOINT_BY_ID[MAP_NAME]
    anchor = CHECKPOINT_BY_ID["feywild_anchor"]
    assert entry.display_name == "Feywild 1"
    assert entry.runtime_entry and entry.development_visible
    assert entry.arrival == "from_river"
    assert anchor.display_name == "Feywild Ashtray"
    assert anchor.map_name == MAP_NAME and anchor.saveable
    assert "feywild_reached" in entry.required_flags

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME, sanity=58)
        assert scene.map_name == MAP_NAME
        assert scene.sanity.current == 58
        assert game.active_checkpoint_id == MAP_NAME
        assert game.progress.has("feywild_reached")
        assert len(scene.anchors) == 1
        assert not scene.anchors[0].lit
        assert scene.undead == []
        assert scene.dinosaurs == []
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
    print("All Feywild riverbank tests passed.")


if __name__ == "__main__":
    _run_all()
