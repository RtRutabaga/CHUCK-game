"""Snow that falls only where the ground is snowy.

The city's rain is screen-space: it falls everywhere because the whole
map is a rained-on city. This cannot be, because the snow is standing
in a desert. A fragment of a frozen world has landed in Chult and the
weather came with it, so the weather has to stop at the fragment's
edge -- and where it stops is exactly where the fragment is, which
turns out to be the clearest possible way of showing a player what they
are looking at.

So each flake is tested against the ground it is currently over, and
drawn only if that ground is snow. Nothing is precomputed: the mask is
the map itself, so a snow fragment of any shape gets the right weather
without anybody describing its outline twice.
"""

from __future__ import annotations

import pygame

from src.core import config


# The terrain this weather belongs to. A flake over anything else is
# simply not drawn -- it is still falling, it is just falling somewhere
# it does not exist.
SNOW_TERRAIN = frozenset({"❄", "❅"})

# Generous, because most of these are thrown away. Every flake over
# ground that is not snow is culled, so on a map where the fragment is
# a fifth of the screen only a fifth of them are ever drawn -- a count
# that looks like weather in the abstract came out as a light dusting.
FLAKE_COUNT = 420
# Brighter than the ground it falls on, which the ground's own palette
# is chosen to allow. Two depths, so a still frame still has depth.
_NEAR = (255, 255, 255)
_FAR = (232, 240, 250)


class SnowFall:
    """Deterministic flakes, masked to the snow they belong to."""

    def __init__(self) -> None:
        self.elapsed = 0.0
        # Two depths: the near ones bigger, faster and blown harder, so
        # a still image of it still has some depth in it.
        self.flakes = tuple(
            (
                (index * 61 + 13) % (config.NATIVE_WIDTH + 40) - 20,
                (index * 97 + 29) % (config.NATIVE_HEIGHT + 40) - 20,
                14 + (index * 7) % 22,          # fall speed
                1 if index % 3 else 2,          # size
                (index % 5) - 2,                # drift
            )
            for index in range(FLAKE_COUNT)
        )

    def update(self, dt: float) -> None:
        self.elapsed += max(0.0, dt)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int],
             tilemap) -> None:
        ox, oy = camera_offset
        ts = config.TILE_SIZE
        width, height = surface.get_size()
        span_y = height + 40
        span_x = width + 40
        layer = pygame.Surface((width, height), pygame.SRCALPHA)

        for x, y, speed, size, drift in self.flakes:
            screen_y = (y + self.elapsed * speed) % span_y - 20
            screen_x = (x + self.elapsed * speed * drift * 0.12) % span_x - 20
            # The tile this flake is over right now. Screen to world is
            # just the camera offset; the map does the rest.
            col = int((screen_x + ox) // ts)
            row = int((screen_y + oy) // ts)
            if tilemap.terrain_at(col, row) not in SNOW_TERRAIN:
                continue
            colour = _NEAR if size > 1 else _FAR
            pygame.draw.rect(layer, colour,
                             (round(screen_x), round(screen_y), size, size))
        surface.blit(layer, (0, 0))
