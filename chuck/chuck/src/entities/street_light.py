"""The pools the city's lamps put on the pavement after dark.

The sprite is the lamp; this is the light. They are separate because
they belong to different things: a lamp post stands on a tile whichever
city you are in, and whether it is *lit* is a fact about the map. The
night blocks get this field and the day blocks do not, which is the
whole of the difference between the two cities as far as the street
furniture is concerned.

How it is drawn matters more than it sounds. The light is added to the
screen rather than blended onto it -- an additive blit adds the source
channels and ignores alpha entirely -- so every pool carries its
brightness in its colour rather than in its transparency. Drawn the
obvious way, white on low alpha, each pool added 255 to everything
underneath and the street came back as a row of white discs.

There is no darkening pass here either, and that is deliberate. The
night city already draws with its own night sheet; multiplying it down
first and lighting it back up would be re-lighting a room that is
already lit, and what came out of trying it was a street darker
everywhere except directly under the lamps -- which reads as fog, not
as night. So the pools only ever add.
"""

from __future__ import annotations

import math

import pygame

from src.core import config


# How far the light reaches, and how hard it is at the centre. A lamp
# lights a stretch of pavement and the near half of a lane, not a
# building: much past three tiles and the pools join into one wash and
# the street stops having lit and unlit parts at all.
GLOW_RADIUS = 54
GLOW_PEAK = 118
# Sodium. The night city's palette is cold blues, so the one warm thing
# in it should be the only warm thing in it.
GLOW_COLOUR = (255, 196, 112)

# The lamp head sits at the top of a 56px sprite standing on its tile,
# and the pool belongs under the head rather than under the post -- the
# arm reaches out over the road, and light that fell on the post's own
# tile would be light coming from the wrong place.
HEAD_OFFSET = (7, -6)

# A very slow, very shallow breath. Sodium lamps do not flicker, but a
# perfectly constant pool on a scrolling street reads as a decal stuck
# to the camera; a couple of percent is enough to stop that without
# anybody noticing a pulse.
BREATH_HZ = 0.21
BREATH_DEPTH = 0.05


class StreetLightField:
    """Every lit lamp on one night map, and the light they throw.

    Built once from the map's own streetlight tiles, so nothing here can
    disagree with where the posts are standing. It has no update worth
    the name and no state a save needs to know about: the lamps were on
    when Chuck got here and they will be on when he leaves.
    """

    def __init__(self, tiles) -> None:
        ts = config.TILE_SIZE
        self.centres = tuple(
            (col * ts + ts / 2 + HEAD_OFFSET[0],
             row * ts + ts / 2 + HEAD_OFFSET[1])
            for col, row in tiles
        )
        self._elapsed = 0.0
        self._glow = self._build_glow()

    def __len__(self) -> int:
        return len(self.centres)

    @staticmethod
    def _build_glow() -> pygame.Surface:
        """One soft round pool in grey, built once and tinted on use.

        Squared falloff rather than linear: a linear pool has a visible
        rim where it stops, and a rim is the one thing light does not
        have.
        """
        size = GLOW_RADIUS * 2
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for step in range(GLOW_RADIUS, 0, -1):
            fade = step / GLOW_RADIUS
            value = int(GLOW_PEAK * (1.0 - fade) ** 2)
            if value <= 0:
                continue
            pygame.draw.circle(glow, (value, value, value, 255),
                               (GLOW_RADIUS, GLOW_RADIUS), step)
        return glow

    def update(self, dt: float) -> None:
        self._elapsed += dt

    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        width, height = surface.get_size()
        level = 1.0 - BREATH_DEPTH * (
            1.0 + math.sin(self._elapsed * BREATH_HZ * math.tau)
        ) / 2.0
        pool = self._glow.copy()
        pool.fill(
            (*(round(channel * level) for channel in GLOW_COLOUR), 255),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        for centre_x, centre_y in self.centres:
            left = round(centre_x - ox - GLOW_RADIUS)
            top = round(centre_y - oy - GLOW_RADIUS)
            # Culled, because a map has a dozen of these and only two or
            # three are ever on screen.
            if left > width or top > height:
                continue
            if left + GLOW_RADIUS * 2 < 0 or top + GLOW_RADIUS * 2 < 0:
                continue
            surface.blit(pool, (left, top), special_flags=pygame.BLEND_ADD)
