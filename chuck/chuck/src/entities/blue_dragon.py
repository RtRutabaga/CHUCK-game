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

The animal itself is a sprite rather than the dozen polygons it used to
be drawn from. There is exactly one of these in the game and it is the
one thing on its map that cannot be fought, so it is worth walking up
to look at -- see tools/generate_blue_dragon_sprite.py. All this class
draws is the lane.
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

ARC = (206, 232, 255)
ARC_CORE = (255, 255, 255)
GLOW = (120, 186, 246)

# The sheet: four frames of wing beat, then two of the breath.
SPRITE = "hazards/blue_dragon.png"
FRAME_W, FRAME_H = 128, 96
IDLE_FRAMES = 4
BREATH_FRAMES = 2
# How far into the wind-up it opens its jaw. The lane is already
# glowing by then; this is the half of the telegraph you can read
# without looking at the ground.
GAPE_AT = 0.55


class BlueDragon(Entity):
    """A fixed hazard that breathes lightning down a lane. Unkillable.

    Deliberately not an UndeadEnemy: giving it that class would give it
    scratches and a death, and a player who can see a health bar will
    try to empty it. It has neither.
    """

    # The size of its own sprite. It never moves, so the box is only
    # ever used for drawing order and for finding its mouth -- eight
    # tiles by six, which is nearly twice the massive Chult dinosaur
    # and about nine times Chuck. A dragon that is not obviously the
    # biggest thing in the game is not obviously a dragon.
    WIDTH = FRAME_W
    HEIGHT = FRAME_H
    # Where the mouth sits in the frame, as a fraction of the height.
    # Taken from the sprite rather than guessed: the lane has to leave
    # the head, and a bolt out of the chest is a bolt from nowhere.
    # Measured on the *breathing* pose, which drops its head -- the lane
    # is one fixed rectangle in every stage, so if the two disagree it
    # should be the idle one that is slightly off, not the one the bolt
    # actually comes out of.
    MOUTH_Y = 0.39
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
        # Both grew with the animal. A nine-tile bolt out of a dragon
        # eight tiles long is a spark; the reach has to be the length of
        # something worth running from.
        self.reach = config.TILE_SIZE * 14
        self.lane = config.TILE_SIZE * 4
        self._frames: tuple = ()

    def load_sprites(self, assets) -> None:
        self._frames = tuple(
            assets.sheet(SPRITE, FRAME_W, FRAME_H)[0]
        )

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
        mouth_y = self.y + self.HEIGHT * self.MOUTH_Y
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
    @property
    def frame_index(self) -> int:
        """Which frame of the sheet this instant wants.

        The jaw opens part way through the wind-up rather than at the
        bolt. The lane is already glowing by then, but a player looking
        at the dragon instead of at the ground gets the same warning --
        and a telegraph only one of those two ever sees is half a
        telegraph.
        """
        if self.stage == "breathing":
            return IDLE_FRAMES + int(self.elapsed * 16) % BREATH_FRAMES
        if self.stage == "winding" and self.warning >= GAPE_AT:
            return IDLE_FRAMES
        return int(self.elapsed * 4.0) % IDLE_FRAMES

    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset

        # The lane first, under the animal: a faint charge while it
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
            # Forked arcs down the lane rather than a filled bar, so it
            # reads as lightning and not as a coloured wall.
            for index in range(4):
                offset = (index - 1.5) * (sh / 4.4)
                self._arc(surface, lane, offset, index)

        if not self._frames:
            return
        image = self._frames[self.frame_index]
        if self.facing == "right":
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, (round(self.x - ox), round(self.y - oy)))

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
        pygame.draw.lines(surface, ARC, False, points, 4)
        pygame.draw.lines(surface, ARC_CORE, False, points, 2)
