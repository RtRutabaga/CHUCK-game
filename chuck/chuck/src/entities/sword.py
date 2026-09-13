"""A sword, drawn and swung.

Shared by the adventuring fighter and the collided desert's knights. The
blade is drawn at runtime rather than baked into their sprites, because
a sword that only ever points one way is a stick they are holding: it
has to come up, come round and come down, and a sprite frame cannot do
that without a sheet of them per angle.

Angles are screen angles: 0 points east and positive turns clockwise
(y grows downward), so -pi/2 is straight up.
"""

from __future__ import annotations

import math

BLADE = (206, 212, 222)
BLADE_LIT = (244, 248, 252)
BLADE_DARK = (120, 126, 138)
GUARD = (176, 140, 62)
GRIP = (88, 56, 34)
TRAIL = (236, 242, 250)

BLADE_LENGTH = 11
SWING_DURATION = 0.32


def _plot(surface, x: float, y: float, colour) -> None:
    ix, iy = round(x), round(y)
    if 0 <= ix < surface.get_width() and 0 <= iy < surface.get_height():
        surface.set_at((ix, iy), colour)


def draw_sword(surface, hilt: tuple[float, float], angle: float,
               length: int = BLADE_LENGTH) -> None:
    """Grip behind the hand, a crossguard across it, the blade ahead."""
    hx, hy = hilt
    dx, dy = math.cos(angle), math.sin(angle)
    # Perpendicular, for the crossguard and the blade's lit edge.
    px, py = -dy, dx
    for step in range(1, 4):
        _plot(surface, hx - dx * step, hy - dy * step, GRIP)
    for offset in (-2, -1, 0, 1, 2):
        _plot(surface, hx + px * offset, hy + py * offset, GUARD)
    for step in range(1, length + 1):
        x, y = hx + dx * step, hy + dy * step
        colour = BLADE if step < length else BLADE_LIT
        _plot(surface, x, y, colour)
        # A second pixel of blade on one side, lit on its upper edge, so
        # the blade has a width at every angle rather than being a line.
        if step < length - 1:
            side = BLADE_LIT if py < 0 else BLADE_DARK
            _plot(surface, x + px, y + py, side)


def swing_angle(progress: float, start: float, end: float) -> float:
    """Where the blade is, eased: slow wind-up, fast cut, slow finish."""
    t = max(0.0, min(1.0, progress))
    eased = t * t * (3.0 - 2.0 * t)
    return start + (end - start) * eased


def draw_trail(surface, hilt: tuple[float, float], start: float,
               current: float, length: int = BLADE_LENGTH) -> None:
    """The pale arc the tip has just cut through."""
    if abs(current - start) < 0.2:
        return
    hx, hy = hilt
    steps = max(3, int(abs(current - start) * length))
    for index in range(steps):
        a = start + (current - start) * index / steps
        # Fades toward the start of the arc, and only the outer third of
        # the blade leaves a mark.
        if index % 2 and index < steps * 0.5:
            continue
        for reach in (length - 1, length):
            _plot(surface, hx + math.cos(a) * reach,
                  hy + math.sin(a) * reach, TRAIL)


# A downward cut toward one side, as (rest, start, end) screen angles for
# a swing to the east. The west one is the mirror image.
_EAST_CUT = (-1.25, -2.2, 0.55)


def _mirror(angle: float) -> float:
    return math.pi - angle


def cut_angles(direction: str) -> tuple[float, float, float]:
    """(resting, wind-up, finish) angles for a cut toward a direction."""
    if direction == "right":
        return _EAST_CUT
    if direction == "left":
        return tuple(_mirror(a) for a in _EAST_CUT)
    if direction == "down":
        return (-1.1, -2.0, 1.9)
    # Up: held out to the right, raised and brought round over the head.
    return (-1.1, 0.3, -3.6)
