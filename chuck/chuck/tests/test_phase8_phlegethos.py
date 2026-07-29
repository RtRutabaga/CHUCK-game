"""Phase 8 --- Phlegethos, the Nine Hells overworld (arrival slice).

Chuck lands from the Nine Hells fall onto a cracked-basalt clearing
scarred by lava. Lava is a walkable, lethal fall hazard (like the Astral
Sea); a worn stone path winds from his landing past the Ashtray toward
the way onward. The infernal enemies, lava-island jumps, the fortress
climax, the dedicated soundtrack, and the Feywild-river ending are later
slices; here we just get Chuck onto the ground.
"""

from collections import deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.fall import fall_zone_kind
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC

MAP_NAME = "phlegethos_arrival"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_arrival_is_a_basalt_clearing_scarred_by_lava() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (44, 30)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_hell") == 1
    assert kinds.count("anchor:phlegethos_anchor") == 1
    assert kinds.count("boundary:phlegethos_2") == 1  # the way onward
    lava = sum(row.count("≋") for row in tilemap._grid)
    path = sum(row.count("≡") for row in tilemap._grid)
    assert lava >= 40, lava
    assert path >= 60, path
    # No enemies yet (they are later slices).
    assert not any(k in {"rat", "zombie", "skeleton", "raptor",
                         "massive_dinosaur", "snake"} for k in kinds)


def test_lava_is_a_lethal_walkable_fall_hazard() -> None:
    import pygame

    # Lava underfoot triggers the (shared) Astral fall; airborne is safe.
    ts = config.TILE_SIZE
    box = pygame.Rect(5 * ts, 5 * ts, 8, 8)

    class _Lava:
        def terrain_at(self, c, r):
            return "≋"

    assert fall_zone_kind(_Lava(), box, airborne=False) == "astral"
    assert fall_zone_kind(_Lava(), box, airborne=True) is None
    # Lava is not solid (Chuck can walk onto it and fall in)...
    assert not TILE_DEFS["≋"].solid
    # ...but enemies treat it as a wall, like every other fall hazard.
    assert "≋" in collision.FALL_HAZARD_TERRAIN


def test_arrival_reaches_the_ashtray_and_the_way_onward_on_foot() -> None:
    tilemap = _map()
    ts = config.TILE_SIZE
    pts = {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
           for kind, (x, y) in tilemap.object_spawns}
    start = pts["from_hell"]
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nc, nr in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if (nc, nr) in reached:
                continue
            # On foot the lava is impassable (a lethal fall).
            if tilemap.is_solid(nc, nr) or tilemap.terrain_at(nc, nr) == "≋":
                continue
            reached.add((nc, nr))
            frontier.append((nc, nr))
    assert pts["phlegethos_anchor"] in reached
    assert pts["phlegethos_2"] in reached


def test_phlegethos_uses_its_own_tileset_and_placeholder_music() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "phlegethos.png"
    assert tileset.info()["lava"][1] >= 2  # lava is animated
    assert AREA_MUSIC[MAP_NAME] == "chult.wav"  # placeholder for now


def test_phlegethos_checkpoints_are_registered() -> None:
    entry = CHECKPOINT_BY_ID["phlegethos_arrival"]
    assert entry.display_name == "Phlegethos 1"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_hell"
    assert entry.runtime_entry and entry.fade_in
    anchor = CHECKPOINT_BY_ID["phlegethos_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.saveable and not anchor.development_visible


def test_phlegethos_loads_and_places_chuck_on_the_landing() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_arrival")
        assert scene.map_name == MAP_NAME
        assert len(scene.anchors) == 1
        assert scene._player_tile() == (22, 27)  # the from_hell landing
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
    print("All Phlegethos arrival tests passed.")


if __name__ == "__main__":
    _run_all()
