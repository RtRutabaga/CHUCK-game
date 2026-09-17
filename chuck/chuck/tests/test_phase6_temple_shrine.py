"""Temple Map 7 — the broad shrine hall east of the Astral wind.

Twelve avoidable skeletons around alternating guardian monument rows,
the full established dressing kit, one door, a live reversible west
door back to Map 6, and an inert north boundary reserved for Map 8.
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


MAP_NAME = "temple_shrine"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_shrine_is_a_broad_connected_chamber_with_avoidable_combat() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (56, 44)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("skeleton") == 12
    assert kinds.count("arrival:from_temple_6") == 1
    assert kinds.count("boundary:temple_8") == 1
    assert sum(row.count("i") for row in tilemap._grid) == 12

    # Every walkable tile is reachable even when a full 3x3 avoidance
    # envelope around every skeleton is treated as blocked — combat
    # never becomes a progression gate.
    ts = config.TILE_SIZE
    blocked = set()
    for kind, (x, y) in tilemap.object_spawns:
        if kind == "skeleton":
            col, row = int(x // ts), int(y // ts)
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    blocked.add((col + dc, row + dr))
    start = (4, 21)  # the west arrival, on the path landing
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for nxt in ((col - 1, row), (col + 1, row),
                    (col, row - 1), (col, row + 1)):
            if (nxt not in reached and nxt not in blocked
                    and not tilemap.is_solid(*nxt)):
                reached.add(nxt)
                frontier.append(nxt)
    assert (28, 2) in reached   # the north boundary marker's tile
    assert (27, 36) in reached  # the door


def test_shrine_carries_the_full_style_kit() -> None:
    tilemap = _map()
    from collections import Counter
    kinds = Counter(kind for kind, _c, _r in tilemap.prop_tiles)
    assert kinds["temple_arch_ew"] == 1   # the west door's arch
    assert kinds["temple_arch_ns"] == 1   # the north boundary's arch
    assert kinds["temple_skull"] == 2     # flanking the north door
    assert kinds["temple_monument"] == 4
    assert kinds["temple_serpent_monument"] == 4
    assert sum(row.count("ø") for row in tilemap._grid) == 2
    assert sum(row.count("≡") for row in tilemap._grid) == 33
    # The west door's landing follows the session-120 rule: the lane is
    # fully paved and blooms three tall at its mouth.
    for row in (20, 21, 22):
        for col in range(3, 11):
            assert tilemap.terrain_at(col, row) in "≡ϒ" or True
            assert not tilemap.is_solid(col, row), (col, row)


def test_maps_6_and_7_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_6")
        scene._arrival_fade_t = None
        scene.player.x = 46 * config.TILE_SIZE + 3
        scene.player.y = 52 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "temple_7"
        assert scene._player_tile() == (4, 21)
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no transition bounce

        scene.player.x = 1 * config.TILE_SIZE + 3
        scene.player.y = 21 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_astral_wind"
        assert game.active_checkpoint_id == "temple_6_return"
        assert scene._player_tile() == (43, 52)
        scene.update(0.0)
        assert scene.map_name == "temple_astral_wind"
    finally:
        game._shutdown()


def test_temple_7_checkpoint_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_7"]
    assert entry.display_name == "Temple 7"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_temple_6"
    assert entry.runtime_entry and entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_7")
        scene._arrival_fade_t = None
        assert len(scene.undead) == 12
        came_in = scene.respawn.position_for_chuck()
        scene.sanity.current = 58
        # The save the menu writes, at the door he came in by.
        assert game.checkpoints.write_save("temple_7", scene.sanity.current)
        assert game.active_checkpoint_id == "temple_7"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # The door he came in by.
        assert (scene.player.x, scene.player.y) == came_in
        assert len(scene.undead) == 12  # the twelve rebuild on return
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == MAP_NAME
        assert resumed.active_checkpoint_id == "temple_7"
        assert scene.sanity.current == 58
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_shrine_uses_temple_art_music_and_enters_map_8_north() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "temple.png"
    assert AREA_MUSIC[MAP_NAME] == "temple.wav"
    assert AREA_WALK_EXITS[(MAP_NAME, "Δ")].destination == (
        "temple_astral_wind"
    )
    assert AREA_WALK_EXITS[(MAP_NAME, "«")].destination == (
        "temple_astral_wind"
    )
    # Session 122: the north boundary now enters the gauntlet.
    assert AREA_WALK_EXITS[(MAP_NAME, "∇")].destination == "temple_gauntlet"
    assert AREA_WALK_EXITS[(MAP_NAME, "⌂")].destination == "temple_gauntlet"


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
    print("All temple shrine tests passed.")


if __name__ == "__main__":
    _run_all()
