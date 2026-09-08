"""Phase 9 Giant Tea Table exploration, scale routes, and checkpoint wiring."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.core.game import Game
from src.entities.prop import PROP_DIALOGUE
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.dialogue import DialogueSystem
from src.world import collision
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_tea_table"
TABLE_CHARS = frozenset({"▤", "◍", "◉", "☕", "⌁", "⁙"})


def _markers(tilemap: TileMap) -> dict[str, tuple[int, int]]:
    size = config.TILE_SIZE
    return {
        kind: (int(x // size), int(y // size))
        for kind, (x, y) in tilemap.object_spawns
    }


def _reachable(
    tilemap: TileMap,
    start: tuple[int, int],
    *,
    large_actor: bool = False,
) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            terrain = tilemap.terrain_at(*point)
            if point in reached or tilemap.is_solid(*point):
                continue
            if large_actor and terrain in collision.LARGE_ACTOR_PASSAGE_TERRAIN:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_tea_table_is_a_large_enemy_free_scale_respite() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (72, 52)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_4"] == 1
    assert kinds["anchor:feywild_5_anchor"] == 1
    assert kinds["boundary:feywild_6"] == 1
    assert kinds["arrival:from_feywild_6"] == 1
    assert kinds["breakable_grass"] == 4
    assert not any(
        kind in {
            "rat", "snake", "zombie", "skeleton", "lemure", "raptor",
            "redcap", "massive_dinosaur", "horned_devil", "fire_snake",
        }
        for kind in kinds
    )

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    # Two legs, and both of them at the front. A leg is seventy pixels
    # of sprite drawn upward from the bottom of its tile, so the far
    # pair that used to stand four rows behind these ones stacked into
    # one continuous post with a joint halfway up it -- a pillar, not a
    # table. The pair that reads is the pair holding up the edge the
    # camera can see.
    assert props["fey_table_leg"] == 2
    assert {
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "fey_table_leg"
    } == {(21, 32), (52, 32)}
    # And nothing stands loose in the western aisle. There were three
    # chair legs out there, each on its own in open ground with no seat
    # over it and no second leg near enough to belong to the same
    # chair, which is a fence post rather than furniture.
    assert "fey_chair_leg" not in props
    assert props["fey_plate"] == 3
    assert props["fey_teacup"] == 3
    assert props["fey_napkin"] == 3
    assert props["fey_crumbs"] == 6
    assert sum(
        tilemap.terrain_at(col, row) in TABLE_CHARS
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
    ) > 600


def test_the_shadow_is_the_whole_of_the_table_edge() -> None:
    """One unbroken field of shade, with nothing framing it.

    There was a wooden lip drawn round the ring of the shadow, and from
    above at this distance a thin border round a dark rectangle is a
    picture frame rather than the edge of a table. Taking it off costs
    nothing, which is the point of asserting it here: the shadow itself
    was always the tile too low for anything bigger than Chuck, so the
    scale gate this whole map is built on is where it always was.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    for row in range(29, 39):
        for col in range(18, 56):
            char = tilemap.terrain_at(col, row)
            assert char in {"░", "♜"}, (col, row, char)
            # Chuck walks it; nothing larger does; and the legs
            # standing in it are the only solid thing under there.
            assert tilemap.is_solid(col, row) == (char == "♜")
    assert "░" in collision.LARGE_ACTOR_PASSAGE_TERRAIN
    assert not any(name.startswith("fey_table_apron")
                   for name in tileset_for(MAP_NAME).info())


def test_the_legs_hold_the_table_up() -> None:
    """Butted against the underside, not standing loose beneath it.

    A leg is seventy pixels of sprite drawn upward from the bottom of
    its tile. Row 32 is the row where that puts its top a few pixels
    into the tabletop, so the leg meets what it is carrying; standing
    any further down it is a post with a gap above it, which is a leg
    holding nothing.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    legs = [(col, row) for kind, col, row in tilemap.prop_tiles
            if kind == "fey_table_leg"]
    top_of_shadow = 29
    for col, row in legs:
        reach = (row + 1) * config.TILE_SIZE - LEG_HEIGHT
        assert reach < top_of_shadow * config.TILE_SIZE, (col, row, reach)
        # ...and not so far up that it is drawn inside the tabletop.
        assert reach > (top_of_shadow - 1) * config.TILE_SIZE, (col, row)


LEG_HEIGHT = 70


def test_required_route_and_cache_depend_on_chuck_scale() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    arrival = markers["arrival:from_feywild_4"]
    exit_tile = markers["boundary:feywild_6"]
    cache = next(
        position for kind, position in _markers_with_duplicates(tilemap)
        if kind == "breakable_grass" and position == (10, 27)
    )
    chuck_reach = _reachable(tilemap, arrival)
    large_reach = _reachable(tilemap, arrival, large_actor=True)

    assert markers["anchor:feywild_5_anchor"] in chuck_reach
    assert exit_tile in chuck_reach
    assert cache in chuck_reach
    assert exit_tile not in large_reach
    assert cache not in large_reach


def _markers_with_duplicates(tilemap: TileMap):
    size = config.TILE_SIZE
    return [
        (kind, (int(x // size), int(y // size)))
        for kind, (x, y) in tilemap.object_spawns
    ]


def test_place_settings_are_human_scale_and_say_only_short_lines() -> None:
    objects = config.SPRITES_DIR / "objects"
    expected_sizes = {
        "fey_table_leg_1.png": (34, 70),
        "fey_plate.png": (52, 28),
        "fey_teacup.png": (34, 38),
        "fey_napkin.png": (42, 30),
    }
    for filename, size in expected_sizes.items():
        with Image.open(objects / filename) as image:
            assert image.size == size

    assert PROP_DIALOGUE["fey_teacup"] == "fey_tea_warm"
    assert PROP_DIALOGUE["fey_plate"] == "fey_set_for_one"
    dialogue = DialogueSystem()
    assert dialogue.get("fey_tea_warm") == ["Still warm."]
    assert dialogue.get("fey_set_for_one") == ["Set for one."]


def test_tea_table_uses_shared_checkpoint_save_respawn_and_continue() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            scene = game.checkpoints.load_checkpoint("feywild_5", sanity=58)
            assert scene.map_name == MAP_NAME
            assert not scene.redcaps and not scene.undead and not scene.raptors

            anchor = scene.anchors[0]
            scene.player.x, scene.player.y = anchor.x, anchor.y
            scene.update(0.0)
            assert anchor.lit
            assert game.active_checkpoint_id == "feywild_5_anchor"

            scene.sanity.deplete()
            scene.update(config.RESPAWN_FADE_OUT)
            scene.update(config.RESPAWN_HOLD)
            assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)

            resumed = game.checkpoints.continue_game()
            assert resumed is not None
            assert resumed.map_name == MAP_NAME
            assert resumed.sanity.current == 58
            assert resumed.anchors[0].lit
        finally:
            game._shutdown()


def test_rootways_and_tea_table_transition_both_ways() -> None:
    forward = AREA_WALK_EXITS[("feywild_rootways", "→")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "⇧")]
    onward = AREA_WALK_EXITS[(MAP_NAME, "⇩")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_4"
    assert backward.destination == "feywild_rootways"
    assert backward.arrival == "from_feywild_5"
    assert onward.destination == "feywild_needle_garden"
    assert onward.arrival == "from_feywild_5"

    entry = CHECKPOINT_BY_ID["feywild_5"]
    anchor = CHECKPOINT_BY_ID["feywild_5_anchor"]
    root_return = CHECKPOINT_BY_ID["feywild_4_return"]
    future_return = CHECKPOINT_BY_ID["feywild_5_return"]
    assert entry.display_name == "Feywild 5" and entry.runtime_entry
    assert anchor.map_name == MAP_NAME and anchor.saveable
    assert not anchor.development_visible
    assert root_return.arrival == "from_feywild_5"
    assert future_return.arrival == "from_feywild_6"


def test_world_walks_from_rootways_into_tea_table_and_back() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_4")
        forward_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "→"
        )
        scene.player.x = forward_tile[0] * config.TILE_SIZE + 3
        scene.player.y = forward_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_5"

        return_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "⇧"
        )
        scene.player.x = return_tile[0] * config.TILE_SIZE + 3
        scene.player.y = return_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "feywild_rootways"
        assert game.active_checkpoint_id == "feywild_4_return"
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
    print("All Phase 9 Giant Tea Table tests passed.")


if __name__ == "__main__":
    _run_all()
