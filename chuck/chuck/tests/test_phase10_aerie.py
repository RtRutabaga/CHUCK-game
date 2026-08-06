"""Phase 10's open Aerie, griffon hazard, and rope boundary."""

from collections import Counter, deque
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.core.game import Game
from src.entities.choice_trigger import ChoiceTrigger
from src.entities.massive_dinosaur import MassiveDinosaur
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.choice import ChoiceSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "zephyros_aerie"


def _markers(tilemap):
    size = config.TILE_SIZE
    return {
        kind: (int(x // size), int(y // size))
        for kind, (x, y) in tilemap.object_spawns
    }


def _reachable(tilemap, start):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in reached or tilemap.is_solid(*point):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_aerie_is_a_vast_open_platform_with_four_giant_nests() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (60, 46)
    assert MAP_TILESET[MAP_NAME] == "tower"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert kinds["arrival:from_exterior"] == 1
    assert kinds["anchor:zephyros_aerie_anchor"] == 1
    assert kinds["choice:zephyros_rope"] == 1
    assert kinds["griffon"] == 1
    assert props["griffon_nest"] == 4
    assert props["aerie_rope"] == 1
    assert sum(row.count("~") for row in tilemap._grid) > 800

    nest = Image.open(
        config.SPRITES_DIR / "objects" / "griffon_nest.png"
    )
    assert nest.size[0] >= 7 * config.TILE_SIZE
    assert nest.size[1] >= 4 * config.TILE_SIZE


def test_aerie_floor_has_a_rounded_profile_not_a_square_footprint() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")

    def platform_width(row):
        return sum(char != "~" for char in tilemap._grid[row])

    # The ellipse is broad through its middle and tapers sharply at both
    # ends. The short southern entry neck does not flatten the round body.
    assert platform_width(23) > 50
    assert platform_width(5) < 20
    assert platform_width(41) < 25
    assert tilemap.terrain_at(2, 3) == "~"
    assert tilemap.terrain_at(57, 42) == "~"


def test_arrival_anchor_rope_and_return_are_connected_around_the_hole() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    points = _markers(tilemap)
    arrival = points["arrival:from_exterior"]
    reached = _reachable(tilemap, arrival)
    assert points["anchor:zephyros_aerie_anchor"] in reached
    assert points["choice:zephyros_rope"] in reached
    return_tiles = {
        (col, row) for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "⇓"
    }
    assert len(return_tiles) == 3 and return_tiles <= reached

    # The near-black tower interior is a true, solid floor opening, not blue
    # sky paint or walkable stone. Its south lip is the safe rope approach,
    # and the rope is visibly based on solid stone rather than in the void.
    assert tilemap.terrain_at(30, 22) == "●"
    assert tilemap.is_solid(30, 22)
    assert tilemap.terrain_at(29, 27) == "℞"
    assert tilemap.is_solid(29, 27)
    assert points["choice:zephyros_rope"] == (29, 28)


def test_arch_and_aerie_use_normal_reversible_map_transitions() -> None:
    inward = AREA_WALK_EXITS[("zephyros_tower_exterior", "Ƶ")]
    assert inward.destination == MAP_NAME
    assert inward.arrival == "from_exterior" and inward.facing == "up"
    outward = AREA_WALK_EXITS[(MAP_NAME, "⇓")]
    assert outward.destination == "zephyros_tower_exterior"
    assert outward.arrival == "from_aerie" and outward.facing == "down"


def test_rope_prompt_is_exact_walk_triggered_and_starts_intro() -> None:
    choice = ChoiceSystem().get("zephyros_rope")
    assert choice.prompt == "Climb down the rope?"
    assert [option.label for option in choice.options] == ["YES", "NO"]
    assert choice.options[0].action == "zephyros_intro"
    assert choice.options[0].dialogue is None
    assert choice.options[0].goto is None
    assert choice.options[1].dialogue is None
    assert choice.options[1].goto is None
    assert choice.options[1].action is None
    trigger = ChoiceTrigger(0, 0, "zephyros_rope")
    assert trigger.walk_triggered
    assert (trigger.width, trigger.height) == (
        2 * config.TILE_SIZE, config.TILE_SIZE,
    )


def test_griffon_reuses_the_slow_massive_hazard_and_is_easy_to_outrun() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("zephyros_3")
        assert len(scene.dinosaurs) == 1
        griffon = scene.dinosaurs[0]
        assert isinstance(griffon, MassiveDinosaur)
        assert griffon.variant == "griffon"
        assert griffon.speed == config.DINOSAUR_SPEED < config.PLAYER_SPEED / 4
        assert griffon.damage == config.DINOSAUR_SANITY_DAMAGE
        assert griffon.max_scratches == config.DINOSAUR_SCRATCHES
        assert math.dist(
            (scene.player.x, scene.player.y), (griffon.x, griffon.y)
        ) > config.DINOSAUR_NOTICE_RANGE

        sheet = Image.open(config.SPRITES_DIR / "hazards" / "griffon.png")
        assert sheet.size == (
            config.DINOSAUR_FRAME_W * 3, config.DINOSAUR_FRAME_H * 2,
        )
    finally:
        game._shutdown()


def test_aerie_checkpoint_uses_shared_save_respawn_and_development_loader() -> None:
    entry = CHECKPOINT_BY_ID["zephyros_3"]
    anchor = CHECKPOINT_BY_ID["zephyros_aerie_anchor"]
    assert entry.map_name == MAP_NAME and entry.runtime_entry
    assert anchor.map_name == MAP_NAME and anchor.saveable
    assert not anchor.development_visible

    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            scene = game.checkpoints.load_checkpoint("zephyros_3", sanity=21)
            assert scene.map_name == MAP_NAME and scene.sanity.current == 21
            ashtray, = scene.anchors
            scene.player.x, scene.player.y = ashtray.x, ashtray.y
            scene.update(0.01)
            assert game.active_checkpoint_id == "zephyros_aerie_anchor"
            assert game.saves.load().checkpoint_id == "zephyros_aerie_anchor"
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
    print("All Phase 10 Aerie tests passed.")


if __name__ == "__main__":
    _run_all()
