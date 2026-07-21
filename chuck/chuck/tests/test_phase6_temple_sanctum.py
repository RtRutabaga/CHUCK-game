"""Temple Map 9 — the final chamber, structurally (session 130).

The temple's widest hall: a long paved processional between guardian
colonnades to the western dais where the adventurers' battle will be
staged in a later slice. Its east door is the room's ONLY threshold —
per the phase contract there is no way forward; the scripted Fireball
(later) is the only exit. Session 132 added the battle's skeletons:
the only conventional enemies, pressed against the fighter's line.
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


MAP_NAME = "temple_sanctum"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_sanctum_is_the_widest_hall_with_one_threshold_and_no_exit() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 48)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_temple_8") == 1
    assert kinds.count("anchor:temple_9_anchor") == 1
    # No onward boundary: the Fireball is a later slice, and there is
    # no way forward on foot. The battle's skeletons (sessions 132-133)
    # are the room's only conventional enemies: three press the
    # fighter's line, twenty-four more line the north and south fringes.
    assert not any(kind.startswith("boundary:") for kind in kinds)
    assert kinds.count("skeleton") == 27
    assert not any(kind in {
        "rat", "zombie", "raptor", "massive_dinosaur", "snake",
    } for kind in kinds)
    arches = [kind for kind, _c, _r in tilemap.prop_tiles
              if kind.startswith("temple_arch_")]
    assert arches == ["temple_arch_ew"]  # the single east door
    assert sum(row.count("i") for row in tilemap._grid) == 14
    assert sum(row.count("ø") for row in tilemap._grid) == 6
    assert sum(row.count("≡") for row in tilemap._grid) == 138

    # Fully connected from the arrival, Ashtray included.
    walkable = {(c, r) for r in range(tilemap.height_tiles)
                for c in range(tilemap.width_tiles)
                if not tilemap.is_solid(c, r)}
    reached = {(56, 23)}
    frontier = deque([(56, 23)])
    while frontier:
        col, row = frontier.popleft()
        for nxt in ((col - 1, row), (col + 1, row),
                    (col, row - 1), (col, row + 1)):
            if nxt in walkable and nxt not in reached:
                reached.add(nxt)
                frontier.append(nxt)
    assert reached == walkable
    assert (52, 27) in reached


def test_maps_8_and_9_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        scene._arrival_fade_t = None
        scene.player.x = 3 * config.TILE_SIZE + 3
        scene.player.y = 25 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "temple_9"
        assert scene._player_tile() == (56, 23)
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no transition bounce

        scene.player.x = 59 * config.TILE_SIZE + 3
        scene.player.y = 23 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_gauntlet"
        assert game.active_checkpoint_id == "temple_8_return"
        assert scene._player_tile() == (6, 25)
        scene.update(0.0)
        assert scene.map_name == "temple_gauntlet"
    finally:
        game._shutdown()


def test_temple_9_checkpoint_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_9"]
    assert entry.display_name == "Temple 9"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_temple_8"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["temple_9_anchor"]
    assert anchor_entry.position == (820.0, 437.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        scene._arrival_fade_t = None
        # The entrance lines are the tableau suite's concern.
        scene._pending_entrance_dialogue = None
        anchor, = scene.anchors
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 52
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_9_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == MAP_NAME
        assert resumed.active_checkpoint_id == "temple_9_anchor"
        assert scene.sanity.current == 52
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_sanctum_uses_temple_art_music_and_has_no_walk_exit_forward() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "temple.png"
    assert AREA_MUSIC[MAP_NAME] == "boss_battle.wav"  # the boss theme
    assert AREA_WALK_EXITS[(MAP_NAME, "Δ")].destination == "temple_gauntlet"
    assert AREA_WALK_EXITS[(MAP_NAME, "»")].destination == "temple_gauntlet"
    # There is deliberately NO other exit binding: the Fireball is the
    # only way onward, and it does not exist yet.
    assert (MAP_NAME, "∇") not in AREA_WALK_EXITS
    assert (MAP_NAME, "«") not in AREA_WALK_EXITS
    assert (MAP_NAME, "⌂") not in AREA_WALK_EXITS


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
    print("All temple sanctum tests passed.")


if __name__ == "__main__":
    _run_all()
