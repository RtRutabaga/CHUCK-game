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
    CLOSE_CLIMB_END, CUTSCENE_END, RETRACT_END, RETRACT_START, WIDE_START,
    TowerArrivalCutsceneScene,
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
    trigger = ChoiceTrigger(0, 0, "cloud_staircase")
    assert trigger.walk_triggered
    assert (trigger.width, trigger.height) == (
        2 * config.TILE_SIZE, config.TILE_SIZE,
    )

    tilemap = TileMap(config.MAPS_DIR / "feywild_cloud_staircase.txt")
    markers = _markers(tilemap)
    prop = next(
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "cloud_staircase"
    )
    prompt = markers["choice:cloud_staircase"]
    assert prompt == (prop[0], prop[1] + 1)


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
    assert AREA_MUSIC["feywild_cloud_staircase"] == "zephyros_tower.wav"
    assert AREA_MUSIC["zephyros_tower_exterior"] == "zephyros_tower.wav"
    assert AREA_MUSIC["zephyros_aerie"] == "zephyros_tower.wav"


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


def test_ascent_uses_two_truthful_scales_and_a_long_visible_retraction() -> None:
    assert CLOSE_CLIMB_END >= 8.0
    assert RETRACT_END - RETRACT_START >= 6.0
    assert CUTSCENE_END >= 19.0

    game = Game()
    try:
        cutscene = TowerArrivalCutsceneScene(game, sanity=30)
        cutscene.on_enter()
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))

        cutscene.elapsed = 4.0
        assert cutscene.phase == "close_climb" and cutscene.chuck_visible
        cutscene.draw(surface)
        # Even the far-right background is masonry: no complete tower or sky
        # can fit while Chuck remains readable.
        assert surface.get_at((310, 90))[:3] != (116, 190, 226)

        cutscene.elapsed = WIDE_START
        assert cutscene.phase == "wide_retraction"
        assert not cutscene.chuck_visible
        initial_steps = cutscene._wide_step_layout()
        assert len(initial_steps) == 24

        cutscene.elapsed = (RETRACT_START + RETRACT_END) / 2
        moving_steps = cutscene._wide_step_layout()
        assert moving_steps
        assert any(progress > 0.0 for *_position, progress in moving_steps)
        assert min(y for _x, y, _width, _progress in moving_steps) <= 66
        cutscene.draw(surface)

        cutscene.elapsed = RETRACT_END
        assert cutscene._wide_step_layout() == []
        cutscene.draw(surface)
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
    assert arch.size == (320, 224)
    # Opaque masonry must flank and continue above the dark threshold: the
    # arch is part of the tower facade, not a portal standing in open sky.
    assert arch.getpixel((40, 8))[3] == 255
    assert arch.getpixel((280, 8))[3] == 255
    assert arch.getpixel((160, 12))[3] == 255
    assert arch.getpixel((160, 180))[:3] == (7, 9, 17)

    # The compact platform is less than half of the old broad 34x27 ellipse,
    # leaving open sky close on every side of Chuck's route.
    stone_tiles = sum(
        terrain != "~" for row in tilemap._grid for terrain in row
    )
    assert stone_tiles < 400


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


def test_the_tower_stands_on_cloud_and_the_aerie_still_on_stone() -> None:
    """The way up to Zephyros is sky all the way to his door.

    The approach platform was pale masonry hanging in mid-air, which
    reads as a piece of ground that fell off something. It is standing
    cloud now -- its own tiles, so only the approach changes and the
    Aerie inside the tower keeps the stone it is built of.
    """
    from src.world.tilemap import TILE_DEFS
    from src.world.tileset_layout import TOWER

    exterior = TileMap(config.MAPS_DIR / "zephyros_tower_exterior.txt")
    floors = {exterior.terrain_at(col, row)
              for row in range(exterior.height_tiles)
              for col in range(exterior.width_tiles)
              if not exterior.is_solid(col, row)}
    assert "ᚡ" in floors                      # the cloud he walks on
    assert "." not in floors                   # and not a tile of stone
    assert TOWER.char_to_terrain["ᚡ"] == "tower_cloud"
    assert TOWER.char_to_terrain["ᚫ"] == "tower_cloud_soft"
    assert not TILE_DEFS["ᚡ"].solid and not TILE_DEFS["ᚫ"].solid

    # The rim is one tile per side it is open on, not one tile used all
    # the way round: a shape lit the same on its far edge, its near edge
    # and both flanks has no form, and reads as a patch of cloud tiles
    # rather than as one bank with a top and an underside.
    rims = {"ᚤ": "tower_cloud_top", "ᚥ": "tower_cloud_base",
            "ᚩ": "tower_cloud_west", "ᚪ": "tower_cloud_east"}
    for char, art in rims.items():
        assert TOWER.char_to_terrain[char] == art
        assert TILE_DEFS[char].solid, char
    grid = [line for line in
            (config.MAPS_DIR / "zephyros_tower_exterior.txt")
            .read_text(encoding="utf-8").splitlines()
            if not line.startswith(";")]
    for row, line in enumerate(grid):
        for col, char in enumerate(line):
            if char not in rims:
                continue
            sky = {(0, -1): "ᚤ", (0, 1): "ᚥ",
                   (-1, 0): "ᚩ", (1, 0): "ᚪ"}
            open_sides = [want for (dcol, drow), want in sky.items()
                          if grid[row + drow][col + dcol] == "~"]
            assert open_sides, (col, row, char)
            assert char == open_sides[0], (col, row, char, open_sides)
    # ...and every tile of the platform that touches sky wears one.
    for row, line in enumerate(grid):
        for col, char in enumerate(line):
            if char not in ("ᚡ", "ᚫ"):
                continue
            assert not any(grid[row + drow][col + dcol] == "~"
                           for dcol, drow in ((0, -1), (0, 1), (-1, 0), (1, 0))),                 (col, row)
    # The rim is solid, so the platform still ends where it always did.
    walkable = sum(not exterior.is_solid(col, row)
                   for row in range(exterior.height_tiles)
                   for col in range(exterior.width_tiles))
    assert 150 < walkable < 400, walkable

    aerie = TileMap(config.MAPS_DIR / "zephyros_aerie.txt")
    assert any(aerie.terrain_at(col, row) == "."
               for row in range(aerie.height_tiles)
               for col in range(aerie.width_tiles))
    assert not any(aerie.terrain_at(col, row) in ("ᚡ", "ᚣ")
                   for row in range(aerie.height_tiles)
                   for col in range(aerie.width_tiles))
