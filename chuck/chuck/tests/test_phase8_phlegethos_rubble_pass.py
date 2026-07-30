"""Phase 8's east-west rubble pass between the lava lake and fortress."""

from collections import deque
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.massive_dinosaur import MassiveDinosaur
from src.entities.undead import UndeadEnemy
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "phlegethos_rubble_pass"
LAKE = "phlegethos_lake"
FORTRESS = "phlegethos_fortress_approach"


def _points(tilemap: TileMap, prefix: str) -> dict[str, tuple[int, int]]:
    ts = config.TILE_SIZE
    return {
        kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
        for kind, (x, y) in tilemap.object_spawns
        if kind.startswith(prefix)
    }


def test_rubble_pass_is_a_dark_east_west_route_with_a_lava_fall() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 34)
    assert MAP_TILESET[MAP_NAME] == "phlegethos"
    assert AREA_MUSIC[MAP_NAME] == "phlegethos.wav"

    terrain = "".join(tilemap._grid)
    assert terrain.count("þ") >= 100
    assert terrain.count("≋") >= 90
    assert terrain.count("ƒ") == 1
    assert TILE_DEFS["þ"].solid and TILE_DEFS["ƒ"].solid
    props = [kind for kind, _col, _row in tilemap.prop_tiles]
    assert props.count("phlegethos_rubble") >= 100
    assert props.count("phlegethos_lava_fall") == 1
    assert props.count("temple_urn") == 3

    # The route begins at the west edge and leaves through the east edge,
    # breaking the region's prior south-to-north cadence.
    west = next(
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "«"
    )
    east_cells = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "›"
    }
    assert west[0] == 1
    assert east_cells == {(62, 5), (62, 6), (62, 7)}
    east = (62, 6)

    # Arrival, Ashtray, and exit connect without crossing molten terrain or
    # rubble. The path changes rows repeatedly rather than forming a corridor.
    points = _points(tilemap, ("arrival:", "anchor:"))
    start = points["from_phlegethos_3"]
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
            if tilemap.terrain_at(*point) == "≋":
                continue
            reached.add(point)
            frontier.append(point)
    assert points["phlegethos_rubble_anchor"] in reached
    assert points["from_phlegethos_fortress"] in reached
    assert east in reached and west in reached
    path_rows = {
        row for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "≡"
    }
    assert len(path_rows) >= 15


def test_only_one_delayed_lemure_and_one_optional_horned_devil_spawn() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    spawns = tilemap.object_spawns
    kinds = [kind for kind, _position in spawns]
    enemy_kinds = {
        "lemure", "horned_devil", "fire_snake", "zombie", "skeleton",
        "spined_devil:up", "spined_devil:down",
        "spined_devil:left", "spined_devil:right",
        "flameskull:h", "flameskull:v",
    }
    assert [kind for kind in kinds if kind in enemy_kinds] == [
        "lemure", "horned_devil"
    ]

    by_kind = dict(spawns)
    arrival = by_kind["arrival:from_phlegethos_3"]
    assert math.dist(arrival, by_kind["lemure"]) > config.UNDEAD_NOTICE_RANGE
    assert math.dist(
        arrival, by_kind["horned_devil"]
    ) > config.DINOSAUR_NOTICE_RANGE

    # The horned devil's lava-side pocket stays beyond notice range from the
    # required paved route, so it reads as a threat without becoming a gate.
    ts = config.TILE_SIZE
    paved_centers = [
        (col * ts + ts / 2, row * ts + ts / 2)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "≡"
    ]
    assert min(
        math.dist(by_kind["horned_devil"], point)
        for point in paved_centers
    ) > config.DINOSAUR_NOTICE_RANGE

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        assert len(scene.undead) == 1
        assert isinstance(scene.undead[0], UndeadEnemy)
        assert scene.undead[0].kind == "lemure"
        assert len(scene.dinosaurs) == 1
        assert isinstance(scene.dinosaurs[0], MassiveDinosaur)
        assert scene.dinosaurs[0].variant == "horned_devil"
    finally:
        game._shutdown()


def test_rubble_pass_checkpoint_and_both_connections_use_shared_loading() -> None:
    entry = CHECKPOINT_BY_ID[MAP_NAME]
    anchor = CHECKPOINT_BY_ID["phlegethos_rubble_anchor"]
    fortress = CHECKPOINT_BY_ID[FORTRESS]
    assert entry.display_name == "Phlegethos 4"
    assert entry.runtime_entry and entry.development_visible
    assert anchor.map_name == MAP_NAME and anchor.saveable
    assert fortress.display_name == "Phlegethos 5"

    assert AREA_WALK_EXITS[(LAKE, "∇")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "«")].destination == LAKE
    assert AREA_WALK_EXITS[(MAP_NAME, "›")].destination == FORTRESS
    assert AREA_WALK_EXITS[(FORTRESS, "Δ")].destination == MAP_NAME

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(LAKE)
        scene._arrival_fade_t = None
        onward = next(
            (col, row)
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
            if scene.tilemap.terrain_at(col, row) == "∇"
        )
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME

        east = (62, 6)
        scene.player.x = east[0] * config.TILE_SIZE + 3
        scene.player.y = east[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == FORTRESS
        assert game.active_checkpoint_id == FORTRESS

        scene._pending_entrance_dialogue = None
        back = next(
            (col, row)
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
            if scene.tilemap.terrain_at(col, row) == "Δ"
        )
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "phlegethos_rubble_return"
    finally:
        game._shutdown()


def test_the_cliff_lava_fall_animates_through_authored_frames() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        fall = next(
            prop for prop in scene.props
            if prop.kind == "phlegethos_lava_fall"
        )
        assert len(fall._frames) == 4
        assert len({frame.get_view("1").raw for frame in fall._frames}) == 4
        first = fall._image
        fall.update(0.15)
        assert fall._image is fall._frames[1]
        assert fall._image is not first
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
    print("All Phase 8 rubble-pass tests passed.")


if __name__ == "__main__":
    _run_all()
