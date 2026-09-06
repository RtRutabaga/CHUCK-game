"""Phase 13's blue dragon, and the lightning it breathes.

The phase document is unusually firm about what this is not. It cannot
be defeated, it must not be built as a boss fight, and the player's job
is to survive the hazard and keep going. So the dragon is not an enemy
in the game's sense at all: it has no health, it does not pursue, it
cannot be scratched, and nothing about it ends. It is weather with a
temper -- a fixed thing on the map that periodically makes a stretch of
ground lethal and then stops.

That makes the whole design one number: how long the ground is unsafe
against how long it is safe. Chuck is slow, so the safe window has to
be long enough to cross the breath and the warning long enough to see
it coming. The bolt itself is short, because a long one would be a wall
rather than a thing to time.

    idle -> the dragon stands, wings shifting
    winding -> it draws breath, and the strike lights up faintly
    breathing -> the strike is lethal
    spent -> a pause, so two breaths never run together

The strike is a rectangle out of the dragon's mouth. A cone would be
prettier and much harder to read at sixteen pixels a tile; the player
has to know exactly where the edge is, because the edge is the whole
mechanic.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.entity import Entity


# One full cycle, in seconds. The safe stretch is deliberately most of
# it: this is an obstacle to time, not a fight to win.
WIND_UP = 1.15          # the warning
BREATH = 0.75           # the lethal part
SPENT = 2.30            # the pause afterwards
CYCLE = WIND_UP + BREATH + SPENT

BODY = (58, 104, 168)
BODY_DARK = (34, 66, 116)
BODY_LIT = (96, 152, 208)
HORN = (206, 214, 226)
EYE = (238, 244, 120)
ARC = (206, 232, 255)
ARC_CORE = (255, 255, 255)
GLOW = (120, 186, 246)


class BlueDragon(Entity):
    """A fixed hazard that breathes lightning down a lane. Unkillable.

    Deliberately not an UndeadEnemy: giving it that class would give it
    scratches and a death, and a player who can see a health bar will
    try to empty it. It has neither.
    """

    # Wide enough to read as an animal rather than a prop, and it never
    # moves, so the hitbox is only ever used for drawing order.
    WIDTH = 48
    HEIGHT = 34
    damage = config.KNIGHT_SANITY_DAMAGE

    def __init__(self, center_x: float, center_y: float,
                 facing: str = "left", phase: float = 0.0) -> None:
        if facing not in ("left", "right"):
            raise ValueError(f"Unknown dragon facing {facing!r}")
        super().__init__(center_x - self.WIDTH / 2,
                         center_y - self.HEIGHT / 2,
                         self.WIDTH, self.HEIGHT)
        self.facing = facing
        # Two dragons on one map should not breathe in unison, so each
        # starts somewhere different in the cycle.
        self.elapsed = phase % CYCLE
        self.reach = config.TILE_SIZE * 9
        self.lane = config.TILE_SIZE * 3

    # ------------------------------------------------------------------
    @property
    def stage(self) -> str:
        if self.elapsed < WIND_UP:
            return "winding"
        if self.elapsed < WIND_UP + BREATH:
            return "breathing"
        return "spent"

    @property
    def warning(self) -> float:
        """0 at the start of the wind-up, 1 the instant before the bolt."""
        if self.stage != "winding":
            return 1.0 if self.stage == "breathing" else 0.0
        return self.elapsed / WIND_UP

    @property
    def strike(self) -> tuple[float, float, float, float]:
        """The lane the breath covers: (x, y, w, h), always the same.

        The same rectangle whether it is lit or not, so that the warning
        shows exactly the ground the bolt will take. A telegraph that
        does not match its strike is worse than no telegraph.
        """
        mouth_y = self.y + self.HEIGHT * 0.42
        top = mouth_y - self.lane / 2
        if self.facing == "left":
            return (self.x - self.reach, top, self.reach, self.lane)
        return (self.x + self.WIDTH, top, self.reach, self.lane)

    @property
    def lethal(self) -> bool:
        return self.stage == "breathing"

    @property
    def sort_y(self) -> float:
        return float(self.y + self.HEIGHT)

    def update(self, dt: float) -> None:
        self.elapsed = (self.elapsed + max(0.0, dt)) % CYCLE

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        x, y = self.x - ox, self.y - oy
        flip = self.facing == "right"

        def px(value: float) -> float:
            """Mirror a body-space x for a right-facing dragon."""
            return (self.WIDTH - value) if flip else value

        # The lane first, under everything: a faint charge while it
        # winds up, the bolt itself while it breathes.
        sx, sy, sw, sh = self.strike
        lane = pygame.Rect(round(sx - ox), round(sy - oy),
                           round(sw), round(sh))
        if self.stage == "winding":
            layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = round(30 + 70 * self.warning)
            pygame.draw.rect(layer, (*GLOW, alpha), lane)
            surface.blit(layer, (0, 0))
        elif self.stage == "breathing":
            pygame.draw.rect(surface, GLOW, lane)
            # Three forked arcs down the lane rather than a filled bar,
            # so it reads as lightning and not as a coloured wall.
            for index in range(3):
                offset = (index - 1) * (sh / 3.2)
                self._arc(surface, lane, offset, index)

        # Haunches, body, tail.
        pygame.draw.ellipse(surface, BODY_DARK,
                            (x + px(10) - (18 if flip else 0), y + 14, 18, 16))
        pygame.draw.ellipse(surface, BODY,
                            (x + px(12) - (16 if flip else 0), y + 12, 16, 14))
        tail = [(px(40), 22), (px(48), 16), (px(46), 26), (px(38), 26)]
        pygame.draw.polygon(surface, BODY_DARK,
                            [(x + tx, y + ty) for tx, ty in tail])

        # Wing: one big folded triangle, shifting slowly so the thing
        # is alive even when it is doing nothing.
        lift = math.sin(self.elapsed * 1.6) * 2.0
        wing = [(px(16), 12), (px(30), 2 + lift), (px(34), 16)]
        pygame.draw.polygon(surface, BODY_LIT,
                            [(x + wx, y + wy) for wx, wy in wing])
        pygame.draw.polygon(surface, BODY_DARK,
                            [(x + wx, y + wy) for wx, wy in wing], 1)

        # Neck and head, dipped while it breathes.
        dip = 3 if self.lethal else 0
        neck = [(px(14), 16), (px(8), 6 + dip), (px(2), 12 + dip),
                (px(12), 22)]
        pygame.draw.polygon(surface, BODY,
                            [(x + nx, y + ny) for nx, ny in neck])
        head = pygame.Rect(x + px(9 if not flip else 1), y + 6 + dip, 8, 7)
        pygame.draw.rect(surface, BODY_DARK, head)
        pygame.draw.rect(surface, BODY, head.inflate(-2, -2))
        pygame.draw.polygon(surface, HORN, [
            (x + px(8), y + 6 + dip), (x + px(12), y + 1 + dip),
            (x + px(11), y + 7 + dip)])
        surface.set_at((round(x + px(5)), round(y + 9 + dip)), EYE)

        # Legs, so it is standing on the snow rather than hovering.
        for leg in (px(16), px(26)):
            pygame.draw.rect(surface, BODY_DARK,
                             (x + leg - 1, y + 26, 3, 7))

    def _arc(self, surface, lane: pygame.Rect, offset: float,
             seed: int) -> None:
        """One jagged bolt down the lane."""
        steps = 8
        points = []
        for step in range(steps + 1):
            along = step / steps
            jitter = math.sin(along * 9.0 + seed * 2.1
                              + self.elapsed * 40.0) * (lane.height / 5)
            points.append((
                lane.left + along * lane.width,
                lane.centery + offset + jitter,
            ))
        if self.facing == "left":
            points.reverse()
        pygame.draw.lines(surface, ARC, False, points, 3)
        pygame.draw.lines(surface, ARC_CORE, False, points, 1)
