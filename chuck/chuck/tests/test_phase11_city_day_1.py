"""Phase 11 City Day 1: out of the sewer into the rainy daytime city.

The daytime city is the same city at noon, so its tileset reuses the
night sheet's draw functions under an overcast wash rather than
authoring a second set of buildings that could drift out of step. What
changes is the light, the street geometry, and who is on the pavement.

These tests cover the ladder that finally works, the daylight wash being
genuinely lighter than night, the looser avenue-and-plaza layout, the
roads that end in visible Astral damage, and the woman in the red dress
-- one of her, on a patrol long enough to make her a landmark.
"""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.choice import ChoiceSystem
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import CITY, CITY_DAY, MAP_TILESET, tileset_for


MAP_NAME = "modern_city_day_1"
SEWER_4 = "modern_city_sewer_4"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _flood(tilemap, start):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in found or tilemap.is_solid(x, y):
                continue
            if tilemap.terrain_at(x, y) == "V":
                continue
            found.add(point)
            queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_the_daytime_sheet_is_the_night_city_in_daylight() -> None:
    """Same geometry, different light: the two sheets must stay in step."""
    # The shared rows must stay in step. The day sheet also carries rows
    # the night city has no use for: puddles, and -- on City Day 6 -- the
    # Chult patch and the separately drawn planar portal.
    day_only = {"astral_void", "city_day_puddle", "chult_ground",
                "chult_dense"}
    assert [name for name, _v, _f in CITY.order if name != "astral_void"] == [
        name.replace("city_day_", "city_")
        for name, _v, _f in CITY_DAY.order
        if name not in day_only
    ]
    # Every terrain char the night city uses reads in daylight too.
    assert set(CITY.char_to_terrain) <= set(CITY_DAY.char_to_terrain)
    assert MAP_TILESET[MAP_NAME] == "city_day"
    assert tileset_for(MAP_NAME).sheet == "city_day.png"

    pygame.init()
    day = pygame.image.load(str(config.TILESETS_DIR / "city_day.png"))
    night = pygame.image.load(str(config.TILESETS_DIR / "city.png"))

    def brightness(surface, row):
        total = count = 0
        for x in range(surface.get_width()):
            for y in range(row * 16, row * 16 + 16):
                r, g, b, a = surface.get_at((x, y))
                if a:
                    total += r + g + b
                    count += 1
        return total / max(1, count)

    # The sidewalk and road rows sit at the same index in both sheets.
    for row in (5, 7):
        assert brightness(day, row) > brightness(night, row) * 1.3, row


def test_the_ladder_finally_leads_somewhere() -> None:
    choice = ChoiceSystem().get("city_sewer_ladder")
    assert choice.prompt == "Climb up ladder?"
    yes, no = choice.options
    assert yes.label == "YES" and no.label == "NO"
    assert yes.goto == MAP_NAME and yes.arrival == "from_city_sewer_4_ladder"
    # NO closes with no further text, exactly like the sewer entrance.
    assert no.goto is None and no.dialogue is None and no.action is None

    sewer = TileMap(config.MAPS_DIR / f"{SEWER_4}.txt")
    triggers = [kind for kind, _pos in sewer.object_spawns
                if kind == "choice:city_sewer_ladder"]
    assert len(triggers) == 1

    directory, game, world = _game_and_world(SEWER_4)
    try:
        world._on_choice(yes)
        world.update(0.0)
        day = game.scenes.current
        assert day.map_name == MAP_NAME
        assert day.player.facing == "up"
        assert game.active_checkpoint_id == MAP_NAME
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_avenue_is_looser_than_the_night_blocks_and_visibly_broken() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (88, 44)

    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_city_sewer_4_ladder"][0])
    assert markers["anchor:modern_city_day_1_anchor"][0] in reachable
    assert markers["boundary:modern_city_day_2"][0] in reachable

    # One broad avenue, a plaza off it, and a side street north: the open
    # ground is wide rather than the night region's tight blocks.
    assert len(reachable) > 1200, len(reachable)

    # Roads that run off the map end in visible Astral damage, never in
    # an unexplained invisible wall.
    assert all(tilemap.terrain_at(0, row) == "V" for row in range(28, 38))
    assert sum(row.count("V") for row in tilemap._grid) >= 60

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "▱", "▤", "▥", "w", ".", ",", "=", "▦", "ꞏ"):
        assert used[material] > 0, material
    # Rain reads on the ground now that it is light enough to see.
    assert used["ꞏ"] >= 4

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["cigarette"] == 4


def test_one_woman_in_a_red_dress_walks_a_long_pavement() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["patrol_npc:red_dress_woman:h"] == 1
    # No homeless man in the daytime region.
    assert not any(kind.endswith("homeless_man") for kind in kinds)
    assert sum(count for kind, count in kinds.items()
               if kind.endswith("businessman") or ":businessman:" in kind) == 3

    # Her line is everyone else's: she is a landmark, not a subplot.
    dialogue = DialogueSystem()
    assert dialogue.get("red_dress_woman") == dialogue.get("businessman")
    assert dialogue.get("red_dress_woman")[0] == "Ah! A rat!"

    directory, game, world = _game_and_world()
    try:
        woman = next(npc for npc in world.npcs
                     if npc.npc_id == "red_dress_woman")
        others = [npc for npc in world.npcs
                  if npc.npc_id == "businessman"]
        assert len(others) == 3
        # She covers more ground than the businesspeople do.
        assert woman.patrol_range > max(npc.patrol_range for npc in others)
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_is_still_raining_in_the_daytime_city() -> None:
    directory, game, world = _game_and_world("modern_city_day_1_anchor")
    try:
        assert world.city_rain is not None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        entry = CHECKPOINT_BY_ID[MAP_NAME]
        assert (entry.display_name, entry.map_name) == ("City Day 1", MAP_NAME)
        assert entry.runtime_entry
        assert CHECKPOINT_BY_ID["modern_city_day_1_anchor"].saveable

        world._arrival_fade_t = None
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All City Day 1 tests passed.")


if __name__ == "__main__":
    _run_all()
