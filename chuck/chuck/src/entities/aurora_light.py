"""The cabin's aurora projector, and the stove burning under it.

Once the table map has woken, the cabin lights go out and the room is
lit by a Northern Lights projector: broad soft bands sweeping across
everything in slowly cycling colours, a scatter of small blue stars
holding still behind them, and two warm pools that never change colour
with the rest -- the woodstove, and the lava lamp beside it.

The bands are drawn once, in grey, and tinted on the way to the screen
rather than being redrawn every frame. Sweeping them is a blit at a
moving offset, so the whole effect costs three tinted blits and a fill
per frame regardless of how many bands are in it.

Every layer here carries its brightness in its colour channels rather
than in alpha, because an additive blit adds the source channels and
ignores alpha entirely. Drawn white-on-low-alpha -- the obvious way --
each band added 255 to everything under it and the room came out as
saturated tartan.
"""

from __future__ import annotations

import math

import pygame

from src.core import config


# What the room is multiplied down to before any of the light is added
# back. Cool rather than neutral: the projector is the only source left,
# and a warm room lit by a cold one still reads cold.
ROOM_TINT = (56, 54, 74)

# The colours the projector cycles through, in order. Taken off the
# reference: magenta and violet over blue, then the green-and-red band
# that sweeps through underneath it.
PALETTE = (
    (196, 62, 178),
    (108, 66, 214),
    (54, 108, 216),
    (62, 190, 132),
    (208, 74, 96),
)
CYCLE_SECONDS = 7.0        # how long one colour holds before the next
STAR_COUNT = 90
STOVE_GLOW_RADIUS = 46
# The lamp is a lamp, not a fire: a smaller, steadier, redder pool that
# only exists at all because the room is otherwise dark.
LAMP_GLOW_RADIUS = 26


def _band_layer(width: int, height: int, spacing: int, half: int,
                slope: float, peak: int, seed: int) -> pygame.Surface:
    """One set of soft diagonal bands, in white, ready to be tinted.

    Bands have to be far apart and very faint. Drawn close together and
    bright they stop being light falling across a room and become
    tartan, which is what the first attempt at this looked like: three
    layers of hard stripes adding up to white.
    """
    layer = pygame.Surface((width, height), pygame.SRCALPHA)
    for index in range(-height * 2, width + height, spacing):
        wobble = ((index * 7 + seed * 13) % 17) - 8
        for offset in range(-half, half + 1):
            fade = 1.0 - abs(offset) / (half + 1)
            value = int(peak * fade * fade)
            if value <= 0:
                continue
            start = (index + offset, 0)
            end = (index + offset + int(height * slope) + wobble, height)
            pygame.draw.line(layer, (value, value, value, 255), start, end)
    return layer


class AuroraLight:
    """The awakened cabin's light: projector bands, stars, and the stove."""

    def __init__(self, stove_position: tuple[float, float] | None = None,
                 lamp_position: tuple[float, float] | None = None):
        self.elapsed = 0.0
        self.stove_position = stove_position
        self.lamp_position = lamp_position
        width, height = config.NATIVE_WIDTH * 2, config.NATIVE_HEIGHT
        self._layers = (
            _band_layer(width, height, 104, 30, 0.9, 78, 1),
            _band_layer(width, height, 132, 38, -0.6, 58, 2),
            _band_layer(width, height, 168, 20, 1.5, 44, 3),
        )
        # Each layer drifts at its own rate, which is what stops the
        # three of them reading as one moving texture.
        self._speeds = (11.0, -7.0, 17.0)
        self._stars = tuple(
            ((index * 61) % config.NATIVE_WIDTH,
             (index * 37) % config.NATIVE_HEIGHT,
             (index % 5))
            for index in range(STAR_COUNT)
        )
        self._glow = self._build_glow()
        self._lamp_glow = self._build_glow(LAMP_GLOW_RADIUS, 74)

    @staticmethod
    def _build_glow(radius: int = STOVE_GLOW_RADIUS,
                    peak: int = 96) -> pygame.Surface:
        """A soft round pool, built once, tinted on use."""
        size = radius * 2
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for step in range(radius, 0, -1):
            fade = step / radius
            value = int(peak * (1.0 - fade) ** 2)
            if value <= 0:
                continue
            pygame.draw.circle(glow, (value, value, value, 255),
                               (radius, radius), step)
        return glow

    def _pool(self, surface, camera_offset, glow, radius, position,
              colour, level: float) -> None:
        ox, oy = camera_offset
        pool = glow.copy()
        pool.fill((*(round(channel * level) for channel in colour), 255),
                  special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(
            pool,
            (round(position[0] - ox - radius), round(position[1] - oy - radius)),
            special_flags=pygame.BLEND_ADD,
        )

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def colour_for(self, index: int) -> tuple[int, int, int]:
        """The colour of one band layer right now.

        The palette is walked rather than jumped between, so the room
        changes colour the way a projector does -- one shade sliding
        into the next -- instead of flicking like a light switch.
        """
        position = self.elapsed / CYCLE_SECONDS + index * 1.7
        first = PALETTE[int(position) % len(PALETTE)]
        second = PALETTE[(int(position) + 1) % len(PALETTE)]
        blend = position - int(position)
        return tuple(
            round(a + (b - a) * blend) for a, b in zip(first, second)
        )

    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        width, height = surface.get_size()

        # The cabin lights are off: everything already drawn goes down
        # before any of the projector goes back on top of it.
        surface.fill(ROOM_TINT, special_flags=pygame.BLEND_MULT)

        # A held star field, behind the bands, barely moving.
        stars = pygame.Surface((width, height), pygame.SRCALPHA)
        for x, y, phase in self._stars:
            twinkle = 0.55 + 0.45 * math.sin(self.elapsed * 1.6 + phase * 1.3)
            stars.set_at((x % width, y % height),
                         (round(40 * twinkle), round(70 * twinkle),
                          round(150 * twinkle), 255))
        surface.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)

        for index, (layer, speed) in enumerate(zip(self._layers,
                                                   self._speeds)):
            tinted = layer.copy()
            tinted.fill((*self.colour_for(index), 255),
                        special_flags=pygame.BLEND_RGBA_MULT)
            offset = int(self.elapsed * speed) % config.NATIVE_WIDTH
            surface.blit(tinted, (-offset, 0), special_flags=pygame.BLEND_ADD)

        # The fire and the lamp are the two things in the room still
        # their own colour, so they are added after the bands rather
        # than tinted by them. The fire flickers; the lamp does not --
        # it swells, on the same slow beat its blobs move on.
        if self.stove_position is not None:
            flicker = 0.82 + 0.18 * math.sin(self.elapsed * 5.3)
            flicker *= 0.94 + 0.06 * math.sin(self.elapsed * 11.7)
            self._pool(surface, camera_offset, self._glow,
                       STOVE_GLOW_RADIUS, self.stove_position,
                       (255, 126, 38), flicker)
        if self.lamp_position is not None:
            swell = 0.86 + 0.14 * math.sin(self.elapsed * 0.55)
            self._pool(surface, camera_offset, self._lamp_glow,
                       LAMP_GLOW_RADIUS, self.lamp_position,
                       (250, 96, 62), swell)
