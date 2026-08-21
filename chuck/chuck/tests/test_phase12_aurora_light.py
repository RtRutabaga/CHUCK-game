"""The awakened cabin's light: the projector, and the stove under it.

Waking the table map turns the cabin lights off. What is left is a
Northern Lights projector sweeping broad soft bands across the room in
slowly cycling colours, a held scatter of blue stars behind them, and
the woodstove throwing a dim orange pool that stays orange while
everything else changes colour.

The tests worth having are the ones about *when* it is on and how it
composites. Every layer carries its brightness in its colour channels
rather than its alpha, because an additive blit adds the source
channels and ignores alpha -- drawn the obvious way, white on low
alpha, each band added 255 to everything beneath it and the room came
out as saturated tartan.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.aurora_light import AuroraLight, PALETTE, ROOM_TINT
from src.systems.cabin_progress import (
    CABIN_ENTITY_FLAGS, COUNTER_MAP_AWAKENED_FLAG,
)


INTERIOR = "tahuya_cabin_interior"
AWAKE = set(CABIN_ENTITY_FLAGS) | {COUNTER_MAP_AWAKENED_FLAG}


def _world(flags=frozenset(), checkpoint="tahuya_interior"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(flags)
    )
    world._arrival_fade_t = None
    return directory, game, world


def test_the_lights_only_go_out_once_the_table_has_woken() -> None:
    directory, game, world = _world()
    try:
        assert world.map_name == INTERIOR
        assert world.aurora is None, "the cabin is lit until the map wakes"
    finally:
        game._shutdown()
        directory.cleanup()

    directory, game, world = _world(AWAKE)
    try:
        assert world.aurora is not None
        assert world.aurora.stove_position is not None
    finally:
        game._shutdown()
        directory.cleanup()

    # ...and it is the cabin's light, not a global one.
    directory, game, world = _world(AWAKE, checkpoint="tahuya_exterior")
    try:
        assert world.aurora is None
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_projector_walks_its_palette_instead_of_switching() -> None:
    aurora = AuroraLight(None)
    seen = []
    for step in range(240):
        aurora.update(0.25)
        seen.append(aurora.colour_for(0))

    # It gets all the way round the palette, passing through every
    # colour in it rather than sitting between two of them...
    assert len(set(seen)) > 100, len(set(seen))
    for colour in PALETTE:
        assert min(max(abs(a - b) for a, b in zip(colour, shade))
                   for shade in seen) <= 6, colour
    # ...and never jumps: one shade slides into the next.
    for before, after in zip(seen, seen[1:]):
        assert max(abs(a - b) for a, b in zip(before, after)) <= 12, (
            before, after
        )
    # The three layers are never all on the same colour at once.
    assert len({aurora.colour_for(index) for index in range(3)}) == 3


def test_the_room_goes_dark_and_the_light_is_added_back() -> None:
    directory, game, world = _world(AWAKE)
    try:
        aurora = world.aurora
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        surface.fill((200, 200, 200))
        aurora.update(1.0)
        aurora.draw(surface, (0, 0))

        # A flat grey room comes out much darker than it went in...
        pixels = [surface.get_at((x, y))[:3]
                  for x in range(0, config.NATIVE_WIDTH, 7)
                  for y in range(0, config.NATIVE_HEIGHT, 5)]
        average = sum(sum(pixel) for pixel in pixels) / (3 * len(pixels))
        assert average < 120, average
        assert max(ROOM_TINT) < 128, ROOM_TINT

        # ...but not uniformly: the bands are light landing on some of it.
        levels = [sum(pixel) for pixel in pixels]
        assert max(levels) - min(levels) > 80, (min(levels), max(levels))
        # Nothing is blown out to white, which is what happens when the
        # layers carry their brightness in alpha instead of in colour.
        assert not any(all(channel > 250 for channel in pixel)
                       for pixel in pixels)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_stove_stays_orange_while_the_room_changes_colour() -> None:
    directory, game, world = _world(AWAKE)
    try:
        aurora = world.aurora
        stove = aurora.stove_position
        assert stove is not None

        warmth = []
        for moment in (0.0, 6.0, 13.0):
            surface = pygame.Surface(
                (config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
            )
            surface.fill((0, 0, 0))
            aurora.elapsed = moment
            aurora.draw(surface, (round(stove[0] - config.NATIVE_WIDTH / 2),
                                  round(stove[1] - config.NATIVE_HEIGHT / 2)))
            red, green, blue = surface.get_at(
                (config.NATIVE_WIDTH // 2, config.NATIVE_HEIGHT // 2)
            )[:3]
            warmth.append((red, green, blue))

        for red, green, blue in warmth:
            assert red > green > blue, (red, green, blue)
            # Dim: a fire in a dark room, not a floodlight.
            assert red < 210, red
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
    print("All aurora light tests passed.")


if __name__ == "__main__":
    _run_all()
