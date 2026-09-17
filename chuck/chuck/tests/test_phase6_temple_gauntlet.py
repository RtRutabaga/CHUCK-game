"""Temple Map 8 — the gauntlet before the final chamber.

The temple's established defenses concentrate in one L-shaped
connector: three full-width spike bands with skeletons on the landings
and a guardian monument pair in the vertical leg, turning west into a
dart corridor seeded with single Astral cells. One door; the west
boundary stays inert until Temple Map 9.
"""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "temple_gauntlet"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_gauntlet_concentrates_the_temple_defenses() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (40, 52)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("skeleton") == 3
    assert kinds.count("dart_trap:down") == 2
    assert kinds.count("dart_trap:up") == 2
    assert kinds.count("arrival:from_temple_7") == 1
    assert kinds.count("boundary:temple_9") == 1
    assert sum(row.count("i") for row in tilemap._grid) == 9
    assert sum(row.count("♠") for row in tilemap._grid) == 21
    assert sum(row.count("V") for row in tilemap._grid) == 3
    assert sum(row.count("≡") for row in tilemap._grid) == 18


def test_gauntlet_course_is_completable_with_single_hops() -> None:
    """Walking plus single-tile hops over spikes and Astral cells must
    reach the door and the west boundary from the south arrival —
    the concentrated defenses never require a longer jump."""
    tilemap = _map()
    jumpable = {"♠", "V"}
    passable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
        or tilemap.terrain_at(col, row) in jumpable
    }
    safe = {p for p in passable
            if tilemap.terrain_at(*p) not in jumpable}
    start = (19, 46)
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            walk = (col + dc, row + dr)
            if walk in safe and walk not in reached:
                reached.add(walk)
                frontier.append(walk)
            over = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            if (over in passable
                    and tilemap.terrain_at(*over) in jumpable
                    and land in safe and land not in reached):
                reached.add(land)
                frontier.append(land)
    assert reached == safe
    assert (2, 25) in reached or (2, 25) in passable  # the boundary
    assert (19, 25) in reached                        # the door


def test_maps_7_and_8_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_7")
        scene._arrival_fade_t = None
        scene.player.x = 27 * config.TILE_SIZE + 3
        scene.player.y = 2 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "temple_8"
        assert scene._player_tile() == (19, 46)
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no transition bounce

        scene.player.x = 19 * config.TILE_SIZE + 3
        scene.player.y = 48 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_shrine"
        assert game.active_checkpoint_id == "temple_7_return"
        assert scene._player_tile() == (27, 4)
        scene.update(0.0)
        assert scene.map_name == "temple_shrine"
    finally:
        game._shutdown()


def test_temple_8_checkpoint_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_8"]
    assert entry.display_name == "Temple 8"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_temple_7"
    assert entry.runtime_entry and entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        scene._arrival_fade_t = None
        assert len(scene.undead) == 3
        assert len(scene.dart_traps) == 4
        came_in = scene.respawn.position_for_chuck()
        scene.sanity.current = 52
        # The save the menu writes, at the door he came in by.
        assert game.checkpoints.write_save("temple_8", scene.sanity.current)
        assert game.active_checkpoint_id == "temple_8"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # The door he came in by.
        assert (scene.player.x, scene.player.y) == came_in
        assert len(scene.undead) == 3 and len(scene.dart_traps) == 4
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == MAP_NAME
        assert resumed.active_checkpoint_id == "temple_8"
        assert scene.sanity.current == 52
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_gauntlet_uses_temple_art_music_and_holds_future_west_exit() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "temple.png"
    assert AREA_MUSIC[MAP_NAME] == "temple.wav"
    assert AREA_WALK_EXITS[(MAP_NAME, "Δ")].destination == "temple_shrine"
    assert AREA_WALK_EXITS[(MAP_NAME, "⌄")].destination == "temple_shrine"
    # The west boundary stays inert until Map 9 exists.
    # Session 130: the former inert west boundary now enters Map 9.
    assert AREA_WALK_EXITS[(MAP_NAME, "∇")].destination == "temple_sanctum"
    assert AREA_WALK_EXITS[(MAP_NAME, "«")].destination == "temple_sanctum"


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
    print("All temple gauntlet tests passed.")


if __name__ == "__main__":
    _run_all()
