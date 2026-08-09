"""Phase 11 City Day 6: the collision, and the way out of the phase.

Three worlds at once -- the daytime street, a patch of Chult grown
through the plaza, and a block of Douglas fir forest at night inside the
damaged northern building. Everything here is spectacle to route around
rather than fight, and the phase document is explicit that the chaos
must not create unavoidable damage at the Ashtray or the arrival.

That is the test worth having: a clear route from the arrival to the
portal that never crosses a police lane nor comes within the dinosaur's
notice. This covers the ground and the standing cast; the fleeing
businesspeople and the spinning officer are their own pass.
"""

from collections import Counter, deque
import math
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
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "modern_city_day_6"
DAY_5 = "modern_city_day_5"
CHULT_GROUND, CHULT_DENSE, FIR = "ᵹ", "ᵺ", "ᶂ"
LANES = {"police:right": (1, 0), "police:left": (-1, 0),
         "police:up": (0, -1), "police:down": (0, 1)}


def _markers(tilemap):
    result = {}
    ts = config.TILE_SIZE
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((int(x // ts), int(y // ts)))
    return result


def _lane_tiles(tilemap, markers):
    covered = set()
    for kind, step in LANES.items():
        for col, row in markers.get(kind, ()):
            for distance in range(1, 80):
                point = (col + step[0] * distance, row + step[1] * distance)
                if not (0 <= point[0] < tilemap.width_tiles
                        and 0 <= point[1] < tilemap.height_tiles):
                    break
                if tilemap.is_solid(*point):
                    break
                covered.add(point)
    return covered


def _flood(tilemap, start, *, avoid=frozenset()):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            for point in (step, land):
                x, y = point
                if not (0 <= x < tilemap.width_tiles
                        and 0 <= y < tilemap.height_tiles):
                    continue
                if point in found or tilemap.is_solid(x, y):
                    continue
                if tilemap.terrain_at(x, y) == "V" or point in avoid:
                    continue
                if point is land and tilemap.terrain_at(*step) != "V":
                    continue
                found.add(point)
                queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def test_three_worlds_are_visible_at_once() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (80, 60)
    assert MAP_TILESET[MAP_NAME] == "city_day"

    used = Counter(char for row in tilemap._grid for char in row)
    # The city, the jungle grown through it, and the forest at night.
    for material in ("#", "▤", ".", ",", "=", "V"):
        assert used[material] > 0, material
    assert used[CHULT_GROUND] > 200, used[CHULT_GROUND]
    assert used[CHULT_DENSE] > 20, used[CHULT_DENSE]
    assert used[FIR] == 9, used[FIR]

    # The Chult patch is genuinely Chult art, not a recoloured city tile.
    sheet = tileset_for(MAP_NAME)
    assert sheet.char_to_terrain[CHULT_GROUND] == "chult_ground"
    assert sheet.char_to_terrain[CHULT_DENSE] == "chult_dense"
    assert sheet.char_to_terrain[FIR] == "doug_fir_block"
    assert not TILE_DEFS[CHULT_GROUND].solid
    assert TILE_DEFS[CHULT_DENSE].solid and TILE_DEFS[FIR].solid

    # The most visibly damaged city map: more void than every street map.
    def density(name):
        other = TileMap(config.MAPS_DIR / f"{name}.txt")
        total = other.width_tiles * other.height_tiles
        return sum(row.count("V") for row in other._grid) / total

    here = density(MAP_NAME)
    for name in ("modern_city_day_1", "modern_city_day_2",
                 "modern_city_day_3", "modern_city_day_4"):
        assert here > density(name), name


def test_the_chaos_never_traps_the_ashtray_or_the_arrival() -> None:
    """The phase document's hard requirement for this map."""
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_day_5"][0]
    anchor = markers["anchor:modern_city_day_6_anchor"][0]
    portal = markers["choice:doug_fir_portal"][0]
    dinosaur = markers["massive_dinosaur"][0]

    hazard = set(_lane_tiles(tilemap, markers))
    notice = config.DINOSAUR_NOTICE_RANGE / config.TILE_SIZE
    hazard |= {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if math.dist((col, row), dinosaur) <= notice
    }
    assert anchor not in hazard and start not in hazard

    assert portal in _flood(tilemap, start)
    clear = _flood(tilemap, start, avoid=hazard)
    assert portal in clear, "the portal cannot be reached safely"
    assert anchor in clear, "the Ashtray cannot be reached safely"


def test_the_tableau_is_one_animal_over_one_person() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)

    assert kinds["massive_dinosaur"] == 1, "the dinosaur is not a boss fight"
    assert kinds["npc:prone_businessman"] == 1
    assert kinds["raptor"] == 3
    dinosaur = markers["massive_dinosaur"][0]
    prone = markers["npc:prone_businessman"][0]
    assert math.dist(dinosaur, prone) <= 3, math.dist(dinosaur, prone)

    # The whole tableau stands in the jungle, not on the pavement.
    for point in [dinosaur, prone, *markers["raptor"]]:
        assert tilemap.terrain_at(*point) == CHULT_GROUND, point

    directory, game, world = _game_and_world()
    try:
        assert len(world.dinosaurs) == 1 and len(world.raptors) == 3
        prone_npc = next(npc for npc in world.npcs
                         if npc.npc_id == "prone_businessman")
        # He is scenery: one restrained line, no sequence.
        lines = world.dialogue.get("prone_businessman")
        assert len(lines) == 1 and len(lines[0]) <= 8, lines
        assert prone_npc is not None
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_portal_asks_and_the_beholder_theme_returns() -> None:
    choice = ChoiceSystem().get("doug_fir_portal")
    assert choice.prompt == "Enter planar portal?"
    yes, no = choice.options
    assert (yes.label, no.label) == ("YES", "NO")
    # NO closes with no further text; YES is wired by the exit pass.
    assert no.goto is None and no.dialogue is None and no.action is None

    # The phase's one deliberate music switch.
    assert AREA_MUSIC[MAP_NAME] == "boss_battle.wav"
    assert AREA_MUSIC[DAY_5] == "city_day.wav"
    assert (config.MUSIC_DIR / "boss_battle.wav").is_file()

    onward = AREA_WALK_EXITS[(DAY_5, "⮟")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_day_5")
    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Day 6", MAP_NAME)
    assert CHECKPOINT_BY_ID["modern_city_day_6_anchor"].saveable


def test_the_collision_draws_and_respawns_clear_of_the_animals() -> None:
    directory, game, world = _game_and_world("modern_city_day_6_anchor")
    try:
        assert world.city_rain is not None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        anchor = (world.anchors[0].x, world.anchors[0].y)
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == anchor
        for beast in world.dinosaurs + world.raptors:
            assert math.dist((beast.x, beast.y),
                             (world.player.x, world.player.y)) > (
                config.DINOSAUR_NOTICE_RANGE)
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
    print("All City Day 6 tests passed.")


if __name__ == "__main__":
    _run_all()
