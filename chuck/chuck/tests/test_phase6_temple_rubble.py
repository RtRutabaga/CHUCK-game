"""The rubble map (sessions 135, 138).

Where the Fireball throws Chuck: a collapsed 48x30 chamber strewn with
Astral Sea hazard blocks. He lands on the `from_fireball` arrival at the
top; the rubble ashtray sits below, and the one way out is a narrow
crawlspace mouth ('∇') in the south wall that leads to the ship deck —
all reachable on foot along the clear spine and the right-side lane.
"""

from collections import Counter, deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "temple_rubble"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_the_rubble_is_a_broken_chamber_of_astral_hazards() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 30)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_fireball") == 1
    assert kinds.count("anchor:temple_rubble_anchor") == 1
    # Numerous Astral Sea blocks, the collapsed reality of the map.
    astral = sum(row.count("V") for row in tilemap._grid)
    assert astral >= 150, astral
    # The ceiling has caved in: the chamber is choked with big broken
    # masonry blocks (and a few column drums), numerous enough to make it
    # almost impassable off the route. No torches.
    debris = Counter(kind for kind, _c, _r in tilemap.prop_tiles)
    assert debris["temple_rubble_block"] + debris["temple_column"] >= 250, debris
    assert debris["temple_rubble_block"] > debris["temple_column"]  # blocks dominate
    assert sum(row.count("i") for row in tilemap._grid) == 0  # torches removed
    # One intact paved lane ('≡') threads through it, the obvious way out.
    path = sum(row.count("≡") for row in tilemap._grid)
    assert path >= 100, path
    # No way forward yet (beyond the crawlspace), and no conventional enemies.
    assert not any(kind.startswith("boundary:") for kind in kinds)
    assert not any(kind in {
        "rat", "zombie", "skeleton", "raptor", "massive_dinosaur", "snake",
    } for kind in kinds)


def test_the_arrival_reaches_the_ashtray_on_foot() -> None:
    tilemap = _map()
    ts = config.TILE_SIZE
    points = {kind.split(":", 1)[1] if ":" in kind else kind:
              (int(x // ts), int(y // ts))
              for kind, (x, y) in tilemap.object_spawns}
    start = points["from_fireball"]
    anchor = points["temple_rubble_anchor"]
    # On foot the Astral Sea is impassable (a lethal fall hazard).
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nc, nr in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if (nc, nr) in reached:
                continue
            if tilemap.is_solid(nc, nr) or tilemap.terrain_at(nc, nr) == "V":
                continue
            reached.add((nc, nr))
            frontier.append((nc, nr))
    assert anchor in reached
    # ...and so is the crawlspace mouth, the one way out.
    crawl = next((c, r) for r in range(tilemap.height_tiles)
                 for c in range(tilemap.width_tiles)
                 if tilemap.terrain_at(c, r) == "∇")
    assert crawl in reached


def test_the_rubble_uses_temple_art_and_music() -> None:
    assert tileset_for(MAP_NAME).sheet == "temple.png"
    assert AREA_MUSIC[MAP_NAME] == "temple.wav"


def test_the_crawlspace_is_an_enter_crevice_prompt_not_a_walk_exit() -> None:
    # No walk-over exit: the way out is the "Enter crevice?" prompt.
    assert not any(m == MAP_NAME for (m, _c) in AREA_WALK_EXITS)
    tilemap = _map()
    crevice = [pos for kind, pos in tilemap.object_spawns
               if kind == "choice:crevice"]
    assert len(crevice) == 1
    # The prompt sits on the lane, just before the crawlspace mouth.
    ts = config.TILE_SIZE
    cx, cy = crevice[0]
    tile = (int(cx // ts), int(cy // ts))
    below = tilemap.terrain_at(tile[0], tile[1] + 1)
    assert below == "∇", below

    from src.systems.choice import ChoiceSystem
    choice = ChoiceSystem().get("crevice")
    assert choice.prompt == "Enter crevice?"
    labels = [o.label for o in choice.options]
    assert labels == ["YES", "NO"]
    yes = next(o for o in choice.options if o.label == "YES")
    assert yes.goto == "ship_deck"


def test_rubble_checkpoints_are_registered() -> None:
    entry = CHECKPOINT_BY_ID["temple_rubble"]
    assert entry.display_name == "Rubble 1"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_fireball"
    assert entry.runtime_entry and entry.fade_in
    anchor = CHECKPOINT_BY_ID["temple_rubble_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.position == (356.0, 389.0)
    assert anchor.saveable and not anchor.development_visible


def test_the_rubble_loads_and_places_its_anchor() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_rubble")
        assert scene.map_name == MAP_NAME
        assert len(scene.anchors) == 1
        assert scene._player_tile() == (23, 5)
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
    print("All rubble map tests passed.")


if __name__ == "__main__":
    _run_all()
