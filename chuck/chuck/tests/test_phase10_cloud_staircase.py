"""Phase 10's Cloud Staircase arrival and first tower platform."""

from collections import Counter, deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image

from src.core import config
from src.core.game import Game
from src.entities.choice_trigger import ChoiceTrigger
from src.scenes.tower_arrival_cutscene_scene import (
    CUTSCENE_END, TowerArrivalCutsceneScene,
)
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.choice import ChoiceSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


HOSTILES = {
    "rat", "snake", "zombie", "skeleton", "lemure", "raptor",
    "massive_dinosaur", "horned_devil", "fire_snake", "redcap",
    "thorn_mite", "quickling", "displacer_beast", "moonmoth",
}


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


def test_cloud_staircase_is_peaceful_reachable_and_checkpointed() -> None:
    tilemap = TileMap(config.MAPS_DIR / "feywild_cloud_staircase.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 44)
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_13"] == 1
    assert kinds["anchor:zephyros_staircase_anchor"] == 1
    assert kinds["choice:cloud_staircase"] == 1
    assert not HOSTILES & set(kinds)
    assert Counter(kind for kind, _, _ in tilemap.prop_tiles)[
        "cloud_staircase"
    ] == 1

    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_feywild_13"])
    assert markers["anchor:zephyros_staircase_anchor"] in reached
    assert markers["choice:cloud_staircase"] in reached


def test_staircase_prompt_is_exact_and_walk_triggered() -> None:
    choice = ChoiceSystem().get("cloud_staircase")
    assert choice.prompt == "Climb the cloud staircase?"
    assert [option.label for option in choice.options] == ["YES", "NO"]
    assert choice.options[0].action == "tower_arrival"
    assert choice.options[1].dialogue is None
    assert choice.options[1].goto is None
    assert choice.options[1].action is None
    assert ChoiceTrigger(0, 0, "cloud_staircase").walk_triggered


def test_route_uses_normal_transitions_and_shared_checkpoints() -> None:
    outward = AREA_WALK_EXITS[("feywild_twilight_crossroads", "←")]
    assert outward.destination == "feywild_cloud_staircase"
    assert outward.arrival == "from_feywild_13"
    back = AREA_WALK_EXITS[("feywild_cloud_staircase", "→")]
    assert back.destination == "feywild_twilight_crossroads"
    assert back.arrival == "from_feywild_tower"
    assert CHECKPOINT_BY_ID["zephyros_1"].map_name == "feywild_cloud_staircase"
    assert CHECKPOINT_BY_ID["zephyros_staircase_anchor"].saveable
    assert CHECKPOINT_BY_ID["zephyros_2"].map_name == "zephyros_tower_exterior"
    assert CHECKPOINT_BY_ID["zephyros_exterior_anchor"].saveable
    assert AREA_MUSIC["feywild_cloud_staircase"] == "feywild.wav"
    assert AREA_MUSIC["zephyros_tower_exterior"] == "feywild.wav"


def test_yes_starts_input_free_cutscene_and_preserves_sanity() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("zephyros_1", sanity=27)
        yes = scene.choices.get("cloud_staircase").options[0]
        scene._on_choice(yes)
        scene.update(0.0)
        cutscene = game.scenes.current
        assert isinstance(cutscene, TowerArrivalCutsceneScene)
        assert cutscene._sanity == 27

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        cutscene.draw(surface)
        cutscene.update(CUTSCENE_END)
        exterior = game.scenes.current
        assert exterior.map_name == "zephyros_tower_exterior"
        assert exterior.sanity.current == 27
    finally:
        game._shutdown()


def test_exterior_is_open_sky_with_giant_arch_and_one_anchor() -> None:
    tilemap = TileMap(config.MAPS_DIR / "zephyros_tower_exterior.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (44, 34)
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["arrival:from_staircase"] == 1
    assert kinds["anchor:zephyros_exterior_anchor"] == 1
    assert kinds["boundary:zephyros_aerie"] == 1
    assert not HOSTILES & set(kinds)
    assert Counter(kind for kind, _, _ in tilemap.prop_tiles)[
        "cloud_tower_arch"
    ] == 1
    assert MAP_TILESET["zephyros_tower_exterior"] == "tower"

    arch = Image.open(
        config.SPRITES_DIR / "objects" / "cloud_tower_arch.png"
    ).convert("RGBA")
    assert arch.size[0] >= 12 * config.TILE_SIZE
    # Opaque masonry must flank and continue above the dark threshold: the
    # arch is part of the tower facade, not a portal standing in open sky.
    assert arch.getpixel((24, 8))[3] == 255
    assert arch.getpixel((167, 8))[3] == 255
    assert arch.getpixel((96, 12))[3] == 255
    assert arch.getpixel((96, 100))[:3] == (7, 9, 17)


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
    print("All Phase 10 Cloud Staircase tests passed.")


if __name__ == "__main__":
    _run_all()
