"""Phase 9 Map 11 --- the Mushroom Underways.

The recovery map, straight after the displacer beast. Its requirement is
a mood rather than a mechanic, so these tests guard the mood: nothing
here pursues Chuck, the walk really does alternate shade and open
clearing instead of running exposed the whole way, and every side
chamber and fungal tuft can actually be found.
"""

from collections import deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import FEYWILD, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "feywild_mushroom_underways"
MEADOW = "feywild_displacer_meadow"
SHADE, POOL = "ᛥ", "ᛞ"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    ts = config.TILE_SIZE
    return (int(position[0] // ts), int(position[1] // ts))


def _points(tilemap):
    return {kind.split(":", 1)[1]: _tile(pos)
            for kind, pos in tilemap.object_spawns
            if kind.startswith(("arrival:", "boundary:"))}


def _flood(tilemap, start):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in reached or tilemap.is_solid(x, y):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_nothing_in_the_underways_pursues_chuck() -> None:
    """The whole point of the map: it is somewhere to stop running."""
    tilemap = _map()
    kinds = {kind for kind, _pos in tilemap.object_spawns}
    for hostile in ("redcap", "thorn_mite", "displacer_beast",
                    "massive_dinosaur", "rat", "snake", "skeleton", "zombie"):
        assert hostile not in kinds, hostile
    assert not any(kind.startswith(("spitting_orchid:", "lantern_moth:",
                                    "flameskull:", "spined_devil:"))
                   for kind in kinds)

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_11")
        scene._arrival_fade_t = None
        assert not scene.rats and not scene.redcaps
        assert not scene.dinosaurs and not scene.snakes
        assert not scene.undead and not scene.flameskulls
        assert not scene.hazards
        # A while spent standing still costs nothing at all.
        scene.sanity.current = scene.sanity.maximum
        for _ in range(60):
            scene.update(0.05)
        assert scene.sanity.current == scene.sanity.maximum
    finally:
        game._shutdown()


def test_the_walk_alternates_canopy_shade_and_open_clearing() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (70, 46)
    # Shade is ordinary ground, only darker; a pool is solid, to walk
    # around and look at rather than through.
    assert not TILE_DEFS[SHADE].solid and TILE_DEFS[POOL].solid
    assert FEYWILD.char_to_terrain[SHADE] == "fey_cap_shade"
    assert FEYWILD.char_to_terrain[POOL] == "fey_glow_pool"
    # Both animate, so the shade drifts with spores and the pools shimmer.
    art = dict((name, (v, f)) for name, v, f in FEYWILD.order)
    assert art["fey_cap_shade"][1] > 1 and art["fey_glow_pool"][1] > 1

    points = _points(tilemap)
    walk = _flood(tilemap, points["from_feywild_10"])

    shaded = sum(1 for col, row in walk
                 if tilemap.terrain_at(col, row) == SHADE)
    assert shaded >= 300, shaded
    # Neither mode dominates: the map is weather, not a tunnel.
    assert shaded * 3 >= len(walk), (shaded, len(walk))
    assert shaded * 3 <= len(walk) * 2, (shaded, len(walk))
    assert sum(row.count(POOL) for row in tilemap._grid) >= 40


def test_the_side_chambers_and_tufts_are_optional_but_findable() -> None:
    tilemap = _map()
    points = _points(tilemap)
    walk = _flood(tilemap, points["from_feywild_10"])
    tufts = {_tile(pos) for kind, pos in tilemap.object_spawns
             if kind == "breakable_grass"}
    assert len(tufts) >= 6
    assert tufts <= walk

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_11")
        scene._arrival_fade_t = None
        assert len(scene.breakables) == len(tufts)
        # A tuft opens to a cigarette, exactly as grass does elsewhere.
        tuft = scene.breakables[0]
        revealed = len(scene.pickups)
        scene.player.x = tuft.x - scene.player.width
        scene.player.y = tuft.y + 3
        scene.player.facing = "right"
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        assert not tuft.intact
        assert len(scene.pickups) == revealed + 1
    finally:
        game._shutdown()


def test_underways_checkpoints_music_and_the_meadow_connection() -> None:
    entry = CHECKPOINT_BY_ID["feywild_11"]
    assert entry.display_name == "Feywild 11" and entry.runtime_entry
    assert entry.map_name == MAP_NAME and entry.arrival == "from_feywild_10"
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_WALK_EXITS[(MEADOW, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == MEADOW

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_10")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_11"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MEADOW
        assert game.active_checkpoint_id == "feywild_10_return"
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
    print("All Mushroom Underways tests passed.")


if __name__ == "__main__":
    _run_all()
