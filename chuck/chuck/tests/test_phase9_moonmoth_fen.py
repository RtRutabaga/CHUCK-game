"""Phase 9 Map 7 --- the Moonmoth Fen and its lantern moths.

A dark luminous wetland of small safe islands strung across deep water.
Every crossing is exactly one channel tile, so each is a single committed
hop on the existing jump; the fen cannot be walked. Lantern moths fill
the flameskull role as living Feywild wildlife: they weave fixed haunts,
cannot be cleared, and cost Sanity on contact.
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

MAP_NAME = "feywild_moonmoth_fen"
GARDEN = "feywild_needle_garden"

def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _is_safe(tilemap, col, row):
    """Ground Chuck may stand on. Markers resolve to their under-terrain
    in the grid, so solidity — not the authored char — is the truth."""
    return not tilemap.is_solid(col, row)


def _points(tilemap):
    ts = config.TILE_SIZE
    return {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
            for kind, (x, y) in tilemap.object_spawns
            if kind.startswith(("arrival:", "boundary:"))}


def test_the_fen_is_islands_over_water_and_cannot_be_walked() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (62, 40)
    water = sum(row.count("~") for row in tilemap._grid)
    channels = sum(row.count("≈") for row in tilemap._grid)
    assert water >= 800, water          # a genuine fen, not a pond
    assert channels >= 20, channels
    # Deep water is impassable; the channel is the established solid-but-
    # jumpable stream, so no engine change was needed for the hops.
    assert TILE_DEFS["~"].solid and TILE_DEFS["≈"].solid
    assert FEYWILD.char_to_terrain["≈"] == "fey_channel"

    pts = _points(tilemap)
    start = pts["from_feywild_6"]

    def flood(with_hops):
        seen = {start}
        frontier = deque([start])
        while frontier:
            c, r = frontier.popleft()
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                walk = (c + dc, r + dr)
                if (0 <= walk[0] < tilemap.width_tiles
                        and 0 <= walk[1] < tilemap.height_tiles
                        and _is_safe(tilemap, *walk) and walk not in seen):
                    seen.add(walk)
                    frontier.append(walk)
                if not with_hops:
                    continue
                over = (c + dc, r + dr)
                land = (c + 2 * dc, r + 2 * dr)
                if (0 <= land[0] < tilemap.width_tiles
                        and 0 <= land[1] < tilemap.height_tiles
                        and tilemap.terrain_at(*over) == "≈"
                        and _is_safe(tilemap, *land) and land not in seen):
                    seen.add(land)
                    frontier.append(land)
        return seen

    reached = flood(True)
    every_safe = {(c, r)
                  for r in range(tilemap.height_tiles)
                  for c in range(tilemap.width_tiles)
                  if _is_safe(tilemap, c, r)}
    assert reached == every_safe, sorted(every_safe - reached)[:8]
    assert pts["feywild_8"] in reached
    # The hops are mandatory: walking alone never reaches the far bank.
    assert pts["feywild_8"] not in flood(False), "the fen can be walked!"


def test_every_crossing_is_exactly_one_channel_tile() -> None:
    """A committed hop clears one tile, so no crossing may be wider."""
    tilemap = _map()
    for row in range(tilemap.height_tiles):
        for col in range(tilemap.width_tiles):
            if tilemap.terrain_at(col, row) != "≈":
                continue
            # Each channel tile is crossable on at least one axis: safe
            # ground directly opposite it, one tile away on both sides.
            crossable = any(
                _is_safe(tilemap, col - dc, row - dr)
                and _is_safe(tilemap, col + dc, row + dr)
                for dc, dr in ((1, 0), (0, 1))
            )
            assert crossable, (col, row)


def test_the_fen_offers_an_optional_island() -> None:
    tilemap = _map()
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("breakable_grass") >= 3          # cigarette grass
    ts = config.TILE_SIZE
    grass_rows = {int(y // ts) for kind, (x, y) in tilemap.object_spawns
                  if kind == "breakable_grass"}
    # The grass sits on the northern side island, off the main chain.
    assert max(grass_rows) < 16, grass_rows


def test_lantern_moths_are_the_flameskull_hazard_as_wildlife() -> None:
    from src.entities.flameskull import Flameskull

    tilemap = _map()
    haunts = [kind for kind, _pos in tilemap.object_spawns
              if kind.startswith("lantern_moth:")]
    assert len(haunts) >= 4
    assert {k.split(":", 1)[1] for k in haunts} <= {"h", "v"}
    # They fly, so their markers leave the deep water beneath untouched.
    ts = config.TILE_SIZE
    for kind, (x, y) in tilemap.object_spawns:
        if kind.startswith("lantern_moth:"):
            assert tilemap.terrain_at(int(x // ts), int(y // ts)) == "~"

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_7")
        scene._arrival_fade_t = None
        moths = scene.flameskulls
        assert moths and all(isinstance(m, Flameskull) for m in moths)
        assert all(m.variant == "lantern_moth" for m in moths)
        assert all(m.damage == config.FLAMESKULL_SANITY_DAMAGE for m in moths)

        # They weave around a fixed haunt rather than pursuing Chuck.
        moth = moths[0]
        home = moth.home
        seen = set()
        for _ in range(80):
            scene.update(0.05)
            seen.add((round(moth.x), round(moth.y)))
        assert len(seen) > 15, "a lantern moth should weave"
        assert moth.home == home
        reach = config.FLAMESKULL_RANGE + config.FLAMESKULL_WEAVE + 8
        assert all(abs(x - home[0]) <= reach for x, _y in seen)

        # Contact costs Sanity and no scratch can clear them.
        haunt = Flameskull(scene.player.hitbox.centerx,
                           scene.player.hitbox.centery, "h",
                           variant="lantern_moth")
        haunt._t = 0.0
        haunt.load_sprites(game.assets)
        scene.flameskulls.append(haunt)
        before_count = len(scene.flameskulls)
        scene.sanity.current = scene.sanity.maximum
        scene.update(0.001)
        assert scene.sanity.current == (
            scene.sanity.maximum - config.FLAMESKULL_SANITY_DAMAGE)
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.001)
        assert len(scene.flameskulls) == before_count
    finally:
        game._shutdown()


def test_fen_checkpoints_art_and_music_match_the_region() -> None:
    entry = CHECKPOINT_BY_ID["feywild_7"]
    assert entry.display_name == "Feywild 7"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_feywild_6" and entry.runtime_entry
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"  # uninterrupted region theme


def test_the_needle_garden_and_fen_connect_both_ways() -> None:
    assert AREA_WALK_EXITS[(GARDEN, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == GARDEN

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_6")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_7"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == GARDEN
        assert game.active_checkpoint_id == "feywild_6_return"
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
    print("All Moonmoth Fen tests passed.")


if __name__ == "__main__":
    _run_all()
