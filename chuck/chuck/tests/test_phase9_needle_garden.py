"""Phase 9 Needle Garden map, orchid cadence, and checkpoint coverage."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.core.game import Game
from src.entities.spitting_orchid import OrchidSeed, SpittingOrchid
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_needle_garden"
VECTORS = {
    "up": (0, -1), "down": (0, 1),
    "left": (-1, 0), "right": (1, 0),
}


def _markers(tilemap: TileMap) -> dict[str, tuple[int, int]]:
    size = config.TILE_SIZE
    return {
        kind: (int(x // size), int(y // size))
        for kind, (x, y) in tilemap.object_spawns
    }


def _blocks(tilemap: TileMap, col: int, row: int) -> bool:
    """What bounds a lane: solid ground, or a needle bed. Chuck can push
    through the beds at a cost, but seeds stop at them and the safe route
    goes round them."""
    return tilemap.is_solid(col, row) or tilemap.terrain_at(col, row) == "✿"


def _ray(
    tilemap: TileMap, start: tuple[int, int], direction: str,
) -> list[tuple[int, int]]:
    dx, dy = VECTORS[direction]
    col, row = start
    cells = []
    while True:
        col += dx
        row += dy
        if _blocks(tilemap, col, row):
            return cells
        cells.append((col, row))


def _reachable(
    tilemap: TileMap,
    start: tuple[int, int],
    blocked: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    blocked = blocked or set()
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if point in reached or point in blocked:
                continue
            if _blocks(tilemap, *point):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_needle_garden_content_and_cardinal_lanes() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (72, 50)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_5"] == 1
    assert kinds["boundary:feywild_7"] == 1
    assert kinds["arrival:from_feywild_7"] == 1
    assert kinds["breakable_grass"] == 2
    orchids = [
        (kind.split(":", 1)[1], position)
        for kind, position in _tile_markers(tilemap)
        if kind.startswith("spitting_orchid:")
    ]
    assert Counter(direction for direction, _position in orchids) == {
        "down": 1, "left": 1, "right": 2,
    }
    assert sum(row.count("✿") for row in tilemap._grid) > 200
    assert sum(row.count("☼") for row in tilemap._grid) == 3
    assert not any(
        kind in {
            "rat", "snake", "zombie", "skeleton", "lemure", "raptor",
            "redcap", "massive_dinosaur", "horned_devil", "fire_snake",
        }
        for kind in kinds
    )

    rays = [
        _ray(tilemap, position, direction)
        for direction, position in orchids
    ]
    assert sorted(map(len, rays)) == [3, 38, 38, 55]


def _tile_markers(tilemap: TileMap):
    size = config.TILE_SIZE
    return [
        (kind, (int(x // size), int(y // size)))
        for kind, (x, y) in tilemap.object_spawns
    ]


def test_late_crossing_has_a_pollen_bypass() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    orchid_markers = [
        (kind.split(":", 1)[1], position)
        for kind, position in _tile_markers(tilemap)
        if kind.startswith("spitting_orchid:")
    ]
    late_rays = {
        cell
        for direction, position in orchid_markers
        if position in {(20, 34), (44, 32)}
        for cell in _ray(tilemap, position, direction)
    }
    # From the choice point below the firing row, the lower route still reaches
    # the final clearing even when the dangerous crossing is treated as solid.
    reached = _reachable(tilemap, (34, 35), late_rays)
    assert (56, 43) in reached
    assert {(40, 39), (41, 39), (42, 39)} <= reached
    # The first two lessons occur before any pollen tile.
    pollen_tiles = {
        (col, row)
        for row, terrain_row in enumerate(tilemap._grid)
        for col, char in enumerate(terrain_row)
        if char == "☼"
    }
    assert pollen_tiles and min(row for _col, row in pollen_tiles) > 28
    assert all(
        tilemap.terrain_at(col, row) != "☼"
        for direction, position in orchid_markers[:2]
        for col, row in _ray(tilemap, position, direction)
    )


def test_orchids_are_stationary_staggered_and_telegraph_shots() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_6")
        orchids = scene.spitting_orchids
        assert len(orchids) == 4
        assert all(isinstance(orchid, SpittingOrchid) for orchid in orchids)
        home = [(orchid.x, orchid.y) for orchid in orchids]
        cadences = sorted(
            round(orchid._time_until_shot - 0.65, 2)
            for orchid in orchids
        )
        assert cadences == [0.0, 0.6, 1.2, 1.8]

        orchid = orchids[0]
        orchid._time_until_shot = config.ORCHID_WINDUP_TIME + 0.01
        assert orchid.windup_stage == 0
        orchid._time_until_shot = config.ORCHID_WINDUP_TIME
        assert orchid.windup_stage == 1
        orchid._time_until_shot = config.ORCHID_FLASH_TIME
        assert orchid.windup_stage == 2

        for _ in range(60):
            scene.update(0.05)
        assert [(orchid.x, orchid.y) for orchid in orchids] == home
        assert scene.orchid_seeds
        assert all(isinstance(seed, OrchidSeed) for seed in scene.orchid_seeds)
    finally:
        game._shutdown()


def test_seed_damage_collision_and_solid_terrain_stop() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_6")
        scene._arrival_fade_t = None
        scene.orchid_seeds = []
        seed = OrchidSeed(
            scene.player.hitbox.centerx,
            scene.player.hitbox.centery,
            "right",
        )
        scene.orchid_seeds.append(seed)
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == (
            before - config.ORCHID_SEED_SANITY_DAMAGE
        )
        assert seed not in scene.orchid_seeds

        tilemap = scene.tilemap
        stopped = OrchidSeed(7 * 16 - 5, 12 * 16 + 8, "right")
        for _ in range(20):
            stopped.update(0.05, tilemap)
            if not stopped.alive:
                break
        assert not stopped.alive
    finally:
        game._shutdown()


def test_orchid_sprite_contains_three_readable_windup_stages() -> None:
    path = config.SPRITES_DIR / "hazards" / "spitting_orchid.png"
    with Image.open(path) as image:
        assert image.size == (
            config.ORCHID_FRAME_W * 3,
            config.ORCHID_FRAME_H * 3,
        )
        stages = [
            image.crop((
                0, stage * config.ORCHID_FRAME_H,
                config.ORCHID_FRAME_W, (stage + 1) * config.ORCHID_FRAME_H,
            )).tobytes()
            for stage in range(3)
        ]
        assert len(set(stages)) == 3


def test_tea_table_and_needle_garden_transition_both_ways() -> None:
    forward = AREA_WALK_EXITS[("feywild_tea_table", "⇩")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "⇧")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_5"
    assert backward.destination == "feywild_tea_table"
    assert backward.arrival == "from_feywild_6"
    # The garden's east boundary now carries on into the Moonmoth Fen.
    onward = AREA_WALK_EXITS[(MAP_NAME, "→")]
    assert onward.destination == "feywild_moonmoth_fen"
    assert onward.arrival == "from_feywild_6"

    entry = CHECKPOINT_BY_ID["feywild_6"]
    previous_return = CHECKPOINT_BY_ID["feywild_5_return"]
    future_return = CHECKPOINT_BY_ID["feywild_6_return"]
    assert entry.display_name == "Feywild 6" and entry.runtime_entry
    assert previous_return.arrival == "from_feywild_6"
    assert future_return.arrival == "from_feywild_7"

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_5")
        forward_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "⇩"
        )
        scene.player.x = forward_tile[0] * config.TILE_SIZE + 3
        scene.player.y = forward_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_6"

        return_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "⇧"
        )
        scene.player.x = return_tile[0] * config.TILE_SIZE + 3
        scene.player.y = return_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "feywild_tea_table"
        assert game.active_checkpoint_id == "feywild_5_return"
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
    print("All Phase 9 Needle Garden tests passed.")


if __name__ == "__main__":
    _run_all()
