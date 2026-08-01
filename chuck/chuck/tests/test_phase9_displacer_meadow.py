"""Phase 9 Map 10 --- the Displacer Meadow.

The phase's massive-creature encounter. The beast reuses the Chult
colossus wholesale and is never meant to be fought: the meadow's answer
is the root arches and toadstool caps threaded through it, which Chuck
walks under and the beast stops dead at.

Two promises from the phase document are tested rather than eyeballed:
the Ashtray sits in a pocket the beast physically cannot enter, and
respawning there never puts Chuck inside its notice range.
"""

from collections import deque
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world import collision
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "feywild_displacer_meadow"
HEDGE = "feywild_shifting_hedge"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    ts = config.TILE_SIZE
    return (int(position[0] // ts), int(position[1] // ts))


def _points(tilemap):
    return {kind.split(":", 1)[1]: _tile(pos)
            for kind, pos in tilemap.object_spawns
            if kind.startswith(("arrival:", "anchor:", "boundary:"))}


def _flood(tilemap, start, *, large_actor=False):
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
            if large_actor and tilemap.terrain_at(x, y) in (
                    collision.LARGE_ACTOR_PASSAGE_TERRAIN):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_the_meadow_is_crossable_and_the_beast_starts_far_off() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (74, 48)
    points = _points(tilemap)
    beast = next(_tile(pos) for kind, pos in tilemap.object_spawns
                 if kind == "displacer_beast")
    start = points["from_feywild_9"]

    walk = _flood(tilemap, start)
    assert points["feywild_11"] in walk
    assert points["feywild_10_anchor"] in walk
    assert beast in walk

    notice = config.DINOSAUR_NOTICE_RANGE / config.TILE_SIZE
    assert math.dist(start, beast) > notice * 2, math.dist(start, beast)

    # No redcaps here, and exactly one massive creature.
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("displacer_beast") == 1
    assert "redcap" not in kinds
    # The exposed route really is thick with pollen.
    assert sum(row.count("☼") for row in tilemap._grid) >= 150


def test_the_ashtray_is_somewhere_the_beast_can_never_reach() -> None:
    """The phase document's hard requirement for this map."""
    tilemap = _map()
    points = _points(tilemap)
    anchor = points["feywild_10_anchor"]
    beast = next(_tile(pos) for kind, pos in tilemap.object_spawns
                 if kind == "displacer_beast")

    prowl = _flood(tilemap, beast, large_actor=True)
    assert anchor not in prowl, "the beast can reach the Ashtray"
    caches = {_tile(pos) for kind, pos in tilemap.object_spawns
              if kind == "breakable_grass"}
    assert caches and not (caches & prowl)

    # Respawning must never drop Chuck inside its notice range.
    notice = config.DINOSAUR_NOTICE_RANGE / config.TILE_SIZE
    assert math.dist(anchor, beast) > notice, math.dist(anchor, beast)

    entry = CHECKPOINT_BY_ID["feywild_10_anchor"]
    assert _tile(entry.position) == anchor

    # At least three Chuck-scale openings, all of them beyond its reach.
    chuck = _flood(tilemap, points["from_feywild_9"])
    openings = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) in collision.LARGE_ACTOR_PASSAGE_TERRAIN
    }
    assert len(openings) >= 3, len(openings)
    assert openings <= chuck
    assert not (openings & prowl)


def test_a_displacer_beast_is_the_colossus_that_cannot_follow() -> None:
    from src.entities.massive_dinosaur import MassiveDinosaur

    # The engine rule, not just the map: root arches and toadstool caps
    # are walls to anything larger than Chuck.
    assert "≀" in collision.LARGE_ACTOR_PASSAGE_TERRAIN
    assert "ᚿ" in collision.LARGE_ACTOR_PASSAGE_TERRAIN

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_10")
        scene._arrival_fade_t = None
        assert len(scene.dinosaurs) == 1
        beast = scene.dinosaurs[0]
        assert isinstance(beast, MassiveDinosaur)
        assert beast.variant == "displacer_beast"
        assert beast.max_scratches == config.DINOSAUR_SCRATCHES
        assert beast.damage == config.DINOSAUR_SANITY_DAMAGE

        # It ignores Chuck until he is close, then comes straight at him.
        home = (beast.x, beast.y)
        scene.player.x, scene.player.y = 60.0, 400.0
        for _ in range(20):
            scene.update(0.05)
        assert (beast.x, beast.y) == home, "it noticed Chuck from too far"

        scene.player.x = beast.x - config.DINOSAUR_NOTICE_RANGE / 3
        scene.player.y = beast.y
        for _ in range(20):
            scene.update(0.05)
        assert beast.x < home[0], "it should pursue once it notices"

        # Put it against a root arch and it stops at the mouth.
        opening = next(
            (col, row)
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
            if scene.tilemap.terrain_at(col, row) == "≀"
        )
        beast.x = (opening[0] + 2) * config.TILE_SIZE
        beast.y = opening[1] * config.TILE_SIZE
        scene.player.x = (opening[0] - 2) * config.TILE_SIZE
        scene.player.y = opening[1] * config.TILE_SIZE
        for _ in range(60):
            scene.update(0.05)
        assert beast.x > (opening[0] + 0.5) * config.TILE_SIZE, (
            "the beast walked through a Chuck-sized arch")
    finally:
        game._shutdown()


def test_meadow_checkpoints_music_and_the_hedge_connection() -> None:
    entry = CHECKPOINT_BY_ID["feywild_10"]
    assert entry.display_name == "Feywild 10" and entry.runtime_entry
    assert entry.map_name == MAP_NAME and entry.arrival == "from_feywild_9"
    anchor = CHECKPOINT_BY_ID["feywild_10_anchor"]
    assert anchor.saveable and not anchor.development_visible
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_WALK_EXITS[(HEDGE, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == HEDGE

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_9")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_10"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == HEDGE
        assert game.active_checkpoint_id == "feywild_9_return"
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
    print("All Displacer Meadow tests passed.")


if __name__ == "__main__":
    _run_all()
