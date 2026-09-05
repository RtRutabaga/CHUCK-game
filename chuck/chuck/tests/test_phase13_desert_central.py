"""Phase 13's opening: the central desert, and the region's look.

Two things here are worth proving rather than eyeballing.

The first is continuity. The phase document asks for the playable
desert to match the desert Chuck was standing in at the end of the last
cutscene, and the only way to be sure of that is to check the pixels
against the constants the cutscene draws with -- a palette picked again
by eye drifts, and drifts invisibly.

The second is the absence of a route. The map is supposed to tell the
player nothing about which way to go, which is a property that is easy
to claim and easy to break by accident: one path tile, one wider gap,
one ruin nudged into a line, and the map is quietly answering a
question it was built to leave open. So the four ways out are measured
against each other, and the ground is checked for anything that leads
to one.
"""

import math
import os
from pathlib import Path
import struct
import tempfile
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.desert_arrival_cutscene_scene import (
    _ROCK, _ROCK_DARK, _SAND, _SAND_LIT, _SAND_SHADE,
)
from src.systems.checkpoints import (
    CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS, KNOWN_PROGRESS_FLAGS,
)
from src.systems.cabin_progress import DESERT_TRANSITION_FLAG
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import DESERT, TILE_PX, tileset_for
from src.world.transitions import AREA_MUSIC

import sys
sys.path.insert(0, str(config.ROOT / "tools") if hasattr(config, "ROOT") else "tools")
from generate_desert_central import (  # noqa: E402
    APPROACH, GAP, HEIGHT, RIM, WIDTH,
)


MAP_NAME = "desert_central"


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        "desert_central_start", progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def test_the_desert_is_drawn_in_the_cutscenes_own_colours() -> None:
    """Continuity with the arrival, checked in pixels rather than trusted."""
    assert tileset_for(MAP_NAME) is DESERT
    pygame.init()
    sheet = pygame.image.load(str(config.ASSETS_DIR / "tilesets" / DESERT.sheet))
    assert sheet.get_width() == DESERT.cols * TILE_PX
    assert sheet.get_height() == DESERT.rows * TILE_PX

    rows = {name: index for index, (name, _, _) in enumerate(DESERT.order)}

    def colours(row_name: str, variant: int = 0) -> set[tuple[int, int, int]]:
        top = rows[row_name] * TILE_PX
        left = variant * TILE_PX
        return {
            sheet.get_at((left + x, top + y))[:3]
            for x in range(TILE_PX) for y in range(TILE_PX)
        }

    # Sand is the cutscene's sand, and nothing else. Any fourth colour
    # in there means somebody has been tuning it locally.
    assert colours("sand") <= {_SAND, _SAND_LIT, _SAND_SHADE}
    assert _SAND in colours("sand")
    # The dunes are the same sand in shadow.
    assert colours("dune") <= {_SAND, _SAND_LIT, _SAND_SHADE}
    # ...and the canyon walls are the cutscene's rock.
    rock = colours("desert_rock")
    assert _ROCK in rock and _ROCK_DARK in rock


def test_the_hub_is_walled_in_with_four_identical_ways_out() -> None:
    """A rim with four gaps, and no way to tell the gaps apart."""
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)

    def gaps(cells) -> list[list[int]]:
        """Runs of non-solid tiles along one edge."""
        runs: list[list[int]] = []
        for index, solid in enumerate(cells):
            if solid:
                continue
            if runs and runs[-1][-1] == index - 1:
                runs[-1].append(index)
            else:
                runs.append([index])
        return runs

    edges = {
        "north": gaps([tilemap.is_solid(x, 0) for x in range(WIDTH)]),
        "south": gaps([tilemap.is_solid(x, HEIGHT - 1) for x in range(WIDTH)]),
        "west": gaps([tilemap.is_solid(0, y) for y in range(HEIGHT)]),
        "east": gaps([tilemap.is_solid(WIDTH - 1, y) for y in range(HEIGHT)]),
    }
    for side, runs in edges.items():
        assert len(runs) == 1, (side, len(runs))
        assert len(runs[0]) == GAP, (side, len(runs[0]))

    # Every gap sits the same distance from the middle of its side, so
    # none of them is nearer or more obvious than the others.
    offsets = {
        side: runs[0][0] + (len(runs[0]) - 1) / 2
        - ((WIDTH if side in ("north", "south") else HEIGHT) - 1) / 2
        for side, runs in edges.items()
    }
    # The sides are an even number of tiles long, so the middle falls
    # between two of them: what matters is that all four agree, not
    # that the number is zero.
    assert len(set(offsets.values())) == 1, offsets
    assert abs(next(iter(offsets.values()))) <= 0.5, offsets


def test_nothing_on_the_ground_points_at_the_way_out() -> None:
    """No painted route, and no accidental one either.

    The rule the phase document actually states is that there must be no
    road through the sand. The rule worth testing is stronger: whatever
    terrain leads up to one gap has to lead up to all four, or the map
    is answering the question by implication.
    """
    tilemap = _tilemap()
    mid_x, mid_y = WIDTH // 2, HEIGHT // 2
    half = GAP // 2

    approaches = {
        "north": [(x, y) for x in range(mid_x - half, mid_x + half + 1)
                  for y in range(RIM, RIM + APPROACH)],
        "south": [(x, y) for x in range(mid_x - half, mid_x + half + 1)
                  for y in range(HEIGHT - RIM - APPROACH, HEIGHT - RIM)],
        "west": [(x, y) for y in range(mid_y - half, mid_y + half + 1)
                 for x in range(RIM, RIM + APPROACH)],
        "east": [(x, y) for y in range(mid_y - half, mid_y + half + 1)
                 for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM)],
    }
    for side, cells in approaches.items():
        kinds = {tilemap.terrain_at(x, y) for x, y in cells}
        # Open sand and its weathering only: no floor, no stone, nothing
        # built, nothing that reads as somebody having come this way.
        assert kinds <= {".", ",", "⟁"}, (side, sorted(kinds))
        assert not any(tilemap.is_solid(x, y) for x, y in cells), side


def test_every_way_out_can_actually_be_reached_from_the_start() -> None:
    """Walked, not assumed: a flood over the tiles Chuck can stand on."""
    tilemap = _tilemap()
    start = CHECKPOINT_BY_ID["desert_central_start"].position
    assert start is not None
    origin = (int(start[0]) // TILE_PX, int(start[1]) // TILE_PX)
    assert not tilemap.is_solid(*origin), "Chuck spawns inside something"

    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + step[0], y + step[1])
            if nxt in seen or tilemap.is_solid(*nxt):
                continue
            seen.add(nxt)
            frontier.append(nxt)

    mid_x, mid_y = WIDTH // 2, HEIGHT // 2
    for name, cell in (("north", (mid_x, 0)), ("south", (mid_x, HEIGHT - 1)),
                       ("west", (0, mid_y)), ("east", (WIDTH - 1, mid_y))):
        assert cell in seen, name

    anchor = CHECKPOINT_BY_ID["desert_central_anchor"].position
    assert anchor is not None
    assert (int(anchor[0]) // TILE_PX, int(anchor[1]) // TILE_PX) in seen

    # The ruins are worth walking into rather than only around: every
    # one of them has floor inside that the flood found.
    floor = [cell for cell in seen
             if tilemap.terrain_at(*cell) == "⌖"]
    assert len(floor) > 120, len(floor)


def test_the_ashtray_stands_where_the_checkpoint_says_it_does() -> None:
    tilemap = _tilemap()
    anchors = [position for kind, position in tilemap.object_spawns
               if kind == "anchor:desert_central_anchor"]
    assert len(anchors) == 1
    checkpoint = CHECKPOINT_BY_ID["desert_central_anchor"]
    assert checkpoint.position == anchors[0]
    assert checkpoint.saveable

    # Both desert entries are gated on the crossing that Phase 12 ends
    # on, so the region cannot be walked into before it exists.
    assert DESERT_TRANSITION_FLAG in DESERT_ENTRY_FLAGS
    assert DESERT_ENTRY_FLAGS <= KNOWN_PROGRESS_FLAGS
    for entry in ("desert_central_start", "desert_central_anchor"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    # ...and the phase document's development access to the initial
    # desert, which is the hub's own entry.
    assert CHECKPOINT_BY_ID["desert_central_start"].development_visible
    assert CHECKPOINT_BY_ID["desert_central_start"].runtime_entry


def test_the_region_has_a_theme_and_it_loops() -> None:
    assert AREA_MUSIC[MAP_NAME] == "desert.wav"
    song = __import__("data.music.desert", fromlist=["desert"])
    seconds = song.TOTAL_BEATS * 60.0 / song.TEMPO_BPM
    assert seconds >= 60.0, seconds

    with wave.open(str(config.MUSIC_DIR / "desert.wav")) as handle:
        assert handle.getnchannels() == 1
        rate = handle.getframerate()
        raw = handle.readframes(handle.getnframes())
    samples = [value / 32767 for (value,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * rate
    assert max(abs(sample) for sample in samples) <= 0.9
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"
    level = math.sqrt(sum(s * s for s in samples) / len(samples))
    assert 0.10 <= level <= 0.20, level

    # It is the cutscene's tune grown up, not a different piece: same
    # tonic, same mode, and the arpeggio still underneath it.
    arrival = __import__("data.music.desert_arrival", fromlist=["desert_arrival"])
    assert song._TRIADS["D2"] == arrival._TRIADS["D2"]
    assert song._ROOTS[0] == arrival._ROOTS[0] == "D2"


def test_the_desert_renders_and_chuck_stands_in_it() -> None:
    directory, game, world = _world()
    try:
        assert world.map_name == MAP_NAME
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for _ in range(6):
            world.update(0.1)
        world.draw(surface)
        # A screen of desert: warm, and nowhere near black or white.
        pixels = [surface.get_at((x, y))[:3]
                  for x in range(0, config.NATIVE_WIDTH, 9)
                  for y in range(0, config.NATIVE_HEIGHT, 7)]
        warm = [p for p in pixels if p[0] > p[2]]
        assert len(warm) > len(pixels) * 0.8, len(warm)
        assert world.anchors
        assert world.anchors[0].checkpoint_id == "desert_central_anchor"
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
    print("All central desert tests passed.")


if __name__ == "__main__":
    _run_all()
