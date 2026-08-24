"""The look of a planar portal, in one place.

There are two of them in the game and they have to be recognisably the
same thing: the oval standing in the wrecked block on City Day 6, and
the opening in the Douglas fir at the end of the phase. One is a
pre-rendered prop and the other is drawn live inside a cutscene, so
without a shared definition the only thing keeping them in step would
be somebody remembering to edit both.

What makes a portal read as a portal here is the colour, not the shape:
grey with light suspended in it, moving in broad slow lobes rather than
in bands or rays. Two counter-turning fields do that -- one sweeping
round the opening, one drifting across it -- so the surface never
repeats a pattern the eye can lock onto.
"""

from __future__ import annotations

import math


GRAY = (142, 140, 150)
PALETTE = (
    (126, 170, 188),   # rain blue
    (168, 132, 184),   # muted violet
    (188, 146, 158),   # dusty rose
    (144, 184, 164),   # mineral green
)
# How far the colour is allowed to come up out of the grey. Past about
# half, the portal stops being smoke with light in it and turns into a
# lava lamp.
COLOUR_STRENGTH = 0.52


def blend(first, second, amount):
    return tuple(round(a + (b - a) * amount)
                 for a, b in zip(first, second))


def portal_colour(nx: float, ny: float, phase: float,
                  strength: float = COLOUR_STRENGTH):
    """The colour of one point inside a portal.

    `nx`/`ny` are the point's position within the opening, each running
    -1 to 1 from its centre, so the same surface can be laid into an
    oval of any size. `phase` is the animation, in radians.

    `strength` exists because the two portals are very different sizes.
    The lobes are the same shape in both, but across twenty pixels
    rather than sixty they cover too few of them to be told apart, and
    the whole opening flattens into one grey. A small portal has to
    push its colour further to look like the same surface.
    """
    distance = math.hypot(nx, ny)
    angle = math.atan2(ny, nx)
    field = (
        math.sin(angle * 3.0 + distance * 6.0 - phase)
        + math.sin(nx * 4.0 - ny * 3.0 + phase * 0.65)
    ) * 0.5
    position = (field + 1.0) * 1.5
    first = int(math.floor(position)) % len(PALETTE)
    second = (first + 1) % len(PALETTE)
    colour = blend(PALETTE[first], PALETTE[second],
                   position - math.floor(position))
    colour = blend(GRAY, colour, strength)
    return blend(colour, (220, 218, 224), max(0.0, 1.0 - distance) * 0.18)
