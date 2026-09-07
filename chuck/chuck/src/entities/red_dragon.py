"""The red dragon that crosses the final encounter, and what it leaves.

The blue dragon on the frozen map is a fixed thing that breathes down a
lane: you learn where the lane is and you time it. This one is the same
animal doing the opposite. It comes in off one side of the arena, flies
across it, and goes out the other -- and the ground under its track
catches fire behind it. So instead of a hazard that is always in the
same place and sometimes lethal, this is a hazard that is always lethal
and never in the same place twice.

That is the whole reason it is here. By the end of this encounter Chuck
is already dodging the ranger's arrows, threading a horde that is not
aiming at him, and standing on a floor being repainted several tiles at
a time. All three of those are things he reads *around* himself. A wall
of fire sweeping across the room is the one kind of pressure that room
did not have: something that makes standing still wrong no matter where
he is standing.

How a pass reads, in order, which is also the order it has to be built
in for the thing to be survivable:

    the dragon appears at the edge of the arena, on his row
    the ground ahead of it starts to glow -- warm, and harmless
    it passes over
    the glow behind it catches, and burning ground is lethal
    the fire dies back to embers, and then to nothing

The glow is the telegraph and it is not decoration. Fire that lit the
instant the dragon arrived would be a hazard that hits before it can be
read, and at three tiles across the lane is wide enough that "read it
as it lands" is not a thing a one-foot rat can do. So the flame leaves
the mouth ahead of the animal, takes a second to reach the floor and
catch, and Chuck's window is that second plus however long he had while
it was flying at him.

It aims at him. The row is taken from wherever he is standing when the
pass begins, and then it is fixed -- so a player who stays put is hit
and a player who moves is not, which is the definition of a dodge. It
is not tracking: once it is in the air the row it is on is the row it
is on, and the whole approach is a promise about where the fire will be.

Nothing about it can be fought and nothing about it ends. There is no
health, no scratching it, and no arrangement of the room that makes it
stop coming -- it is the blue dragon's contract, in motion.
"""

from __future__ import annotations

import math

import pygame

from src.core import config


SPRITE = "hazards/red_dragon.png"
FRAME_W, FRAME_H = 128, 96
FLY_FRAMES = 6
BREATH_FRAMES = 6

# How fast it crosses, and how far above its own track it is drawn. The
# altitude is what makes the shadow separate from the animal, and the
# shadow is what tells a player on the ground where the thing actually
# is: the sprite is up in the air and its position on screen is not
# where it will burn.
SPEED = 150.0
ALTITUDE = 46

# The burning stripe: three tiles, which is wide enough to matter and
# narrow enough to walk out of. Four was a wall and two was a crack.
LANE = config.TILE_SIZE * 3
# Where the flame meets the floor, relative to the animal, and how
# often a patch of it is laid down. Ahead, because the jet leaves the
# mouth pointing forward and down -- which is also what puts the
# warning in front of the dragon rather than under it.
DROP_AHEAD = 34.0
DROP_STEP = 10.0

# One patch's life. It glows before it burns, which is the telegraph;
# it smoulders after, which is not lethal and is only there so the
# stripe fades instead of switching off.
GLOW = 1.0
BURN = 1.9
EMBERS = 0.8
LIFE = GLOW + BURN + EMBERS

# Between passes. Long enough to be a breath rather than a barrage.
PASS_GAP = 3.0
FIRST_PASS = 2.0
# The lane has to fit inside the arena wherever it aims, so the row it
# picks is clamped this far from the top and bottom.
ROW_MARGIN = 4

# Beats per second of the wing, and how fast the flame flickers.
WING_HZ = 7.0
FLICKER_HZ = 11.0

SHADOW = (24, 18, 22, 90)
GLOW_COLOUR = (255, 158, 54)
FIRE_DEEP = (206, 62, 22)
FIRE = (255, 148, 40)
FIRE_CORE = (255, 240, 176)
EMBER = (138, 52, 34)

# What standing in it costs. The most expensive touch in the phase, and
# deliberately so: this one is avoidable in a way that a stray arrow in
# a crowded room is not.
SANITY_DAMAGE = 26


class RedDragonFlyby:
    """One red dragon, crossing and re-crossing, and its burning trail.

    Deliberately not an `Entity` and deliberately not an `UndeadEnemy`:
    it has no hitbox worth colliding with (it is in the air), no health,
    and no death. What the world needs from it is a rectangle list and
    two draw calls.
    """

    def __init__(self, tilemap, *, first_pass: float = FIRST_PASS) -> None:
        self._tilemap = tilemap
        self._frames: tuple = ()
        self.passes = 0
        self.flying = False
        self.row = 0
        self.direction = 1          # +1 travelling east, -1 west
        self.x = 0.0
        self._wait = first_pass
        self._since_drop = 0.0
        self._elapsed = 0.0
        # [x, y, age] per patch of burning floor, oldest first.
        self.fires: list[list] = []

    def load_sprites(self, assets) -> None:
        self._frames = tuple(assets.sheet(SPRITE, FRAME_W, FRAME_H)[0])

    # ------------------------------------------------------------------
    # The pass
    # ------------------------------------------------------------------
    @property
    def track_y(self) -> float:
        """The centre of the burning stripe, in world pixels."""
        return (self.row + 0.5) * config.TILE_SIZE

    @property
    def _span(self) -> float:
        return self._tilemap.width_tiles * config.TILE_SIZE

    def begin(self, row: int) -> None:
        """Send it across at `row`, from whichever side it did not last."""
        top = ROW_MARGIN
        bottom = self._tilemap.height_tiles - 1 - ROW_MARGIN
        self.row = max(top, min(bottom, int(row)))
        # Alternating sides, so two passes running never come from the
        # same place: a hazard that always arrives from the west is a
        # hazard you can stand on the west side of.
        self.direction = 1 if self.passes % 2 == 0 else -1
        self.x = -FRAME_W if self.direction > 0 else self._span + FRAME_W
        self.flying = True
        self.passes += 1
        self._since_drop = 0.0

    def update(self, dt: float, player_tile: tuple[int, int] | None = None
               ) -> None:
        self._elapsed += dt
        for fire in self.fires:
            fire[2] += dt
        self.fires = [fire for fire in self.fires if fire[2] < LIFE]

        if not self.flying:
            self._wait -= dt
            if self._wait <= 0.0:
                # Aimed at wherever he is standing *now*, and then
                # fixed. Re-aiming in flight would be a dragon chasing
                # a rat, which is both unfair and beneath it.
                self.begin(player_tile[1] if player_tile is not None
                           else self._tilemap.height_tiles // 2)
            return

        before = self.x
        self.x += SPEED * self.direction * dt
        self._lay_fire(before, self.x)
        if (self.direction > 0 and self.x > self._span + FRAME_W) or \
                (self.direction < 0 and self.x < -FRAME_W):
            self.flying = False
            self._wait = PASS_GAP

    def _lay_fire(self, before: float, after: float) -> None:
        """Drop patches along the ground the jet has just crossed."""
        travelled = abs(after - before)
        self._since_drop += travelled
        while self._since_drop >= DROP_STEP:
            self._since_drop -= DROP_STEP
            # Back-date the drop to where it actually happened, so the
            # stripe is even however long the frame was.
            along = self._since_drop / max(travelled, 1e-6)
            x = after - (after - before) * along + DROP_AHEAD * self.direction
            if self._burnable(x, self.track_y):
                self.fires.append([x, self.track_y, 0.0])

    def _burnable(self, x: float, y: float) -> bool:
        """Is there floor here to set alight?

        Nothing catches over the rift or on the rim. Fire hanging in the
        Astral Sea would read as the hazard floating, and the Sea is
        already the most lethal thing in the room -- painting flame on
        top of it says nothing and hides the edge of it.
        """
        col = int(x) // config.TILE_SIZE
        row = int(y) // config.TILE_SIZE
        if not (0 <= col < self._tilemap.width_tiles
                and 0 <= row < self._tilemap.height_tiles):
            return False
        if self._tilemap.is_solid(col, row):
            return False
        return self._tilemap.terrain_at(col, row) != "V"

    # ------------------------------------------------------------------
    # What it costs to be under it
    # ------------------------------------------------------------------
    @staticmethod
    def _rect(fire) -> pygame.Rect:
        half = DROP_STEP
        return pygame.Rect(round(fire[0] - half), round(fire[1] - LANE / 2),
                           round(half * 2), LANE)

    @property
    def lethal_rects(self) -> list[pygame.Rect]:
        """The parts of the trail that are actually burning."""
        return [self._rect(fire) for fire in self.fires
                if GLOW <= fire[2] < GLOW + BURN]

    def burns(self, box: pygame.Rect) -> bool:
        return any(box.colliderect(rect) for rect in self.lethal_rects)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    @property
    def frame_index(self) -> int:
        beat = int(self._elapsed * WING_HZ) % FLY_FRAMES
        # It breathes for the whole crossing: the pass *is* the attack,
        # and a dragon that only opened its mouth over part of the room
        # would leave a stripe with a hole in it that nothing on screen
        # explained.
        return FLY_FRAMES + beat if self.flying else beat

    def _edge(self, x: float, share: float, sign: int) -> float:
        """Half-height of the flame at world `x`, on one side of the lane.

        Two sines of *position* rather than of the patch's index, which
        is the difference between a fire and a bar chart: neighbouring
        patches are ten pixels apart and read the same wave, so the edge
        they share is continuous, and the whole stripe ripples along its
        length instead of each segment jumping to its own height.
        """
        phase = self._elapsed * FLICKER_HZ
        wobble = (math.sin(x * 0.09 + phase + sign * 1.9)
                  + 0.6 * math.sin(x * 0.23 - phase * 0.7 + sign))
        return max(1.0, LANE * 0.5 * share + wobble * 3.4)

    def _band(self, surface, fire, share: float, colour,
              offset, alpha: int | None = None) -> None:
        """One layer of one patch, as a quad with two wavy edges."""
        ox, oy = offset
        x, y = fire[0], fire[1]
        left, right = x - DROP_STEP, x + DROP_STEP
        points = [
            (left - ox, y - self._edge(left, share, -1) - oy),
            (right - ox, y - self._edge(right, share, -1) - oy),
            (right - ox, y + self._edge(right, share, 1) - oy),
            (left - ox, y + self._edge(left, share, 1) - oy),
        ]
        pygame.draw.polygon(surface, colour if alpha is None
                            else (*colour, alpha), points)

    def draw_ground(self, surface: pygame.Surface,
                    camera_offset: tuple[int, int]) -> None:
        """The trail and the shadow, under everything that stands on them.

        Drawn as rectangles this was three perfectly straight bands
        running the width of the arena -- an orange flag rather than a
        fire, and worse than that, a hazard with an edge so clean it
        looked like interface. So every layer has a wavy top and a wavy
        bottom taken from position rather than from the patch's index,
        which is what lets neighbouring patches share an edge and the
        whole stripe ripple along its length.

        Layer by layer rather than patch by patch, and that is not
        tidiness. Drawn patch by patch, each one's outer band painted
        over the previous one's bright core, and every tongue came back
        with its right half missing -- a row of arrowheads pointing the
        way the dragon had come.

        Ragged matters because the trail has to say which stretch of
        floor is lit and which is only warm. Those are different things,
        so they have to look like different things.
        """
        ox, oy = camera_offset
        burning = [(index, fire) for index, fire in enumerate(self.fires)
                   if GLOW <= fire[2] < GLOW + BURN]

        # Embers first: they are the oldest and the dimmest, and live
        # under whatever the newer end of the trail is doing.
        for fire in self.fires:
            if fire[2] >= GLOW + BURN:
                left = (fire[2] - GLOW - BURN) / EMBERS
                self._band(surface, fire, 0.42 * (1.0 - left), EMBER,
                           camera_offset)

        for share, colour in ((1.0, FIRE_DEEP), (0.62, FIRE)):
            for _index, fire in burning:
                self._band(surface, fire, share * self._guttering(fire),
                           colour, camera_offset)
        for _index, fire in burning:
            # Which stretches have a bright core, chosen from where they
            # are rather than from how far along the list they are. By
            # index they came out evenly spaced and identically sized --
            # a row of lozenges laid down the middle of the fire, which
            # is the bar-chart problem again in a smaller font.
            seed = int(abs(math.sin(fire[0] * 12.9898)) * 43758.5)
            if seed % 5 < 2:
                continue
            # A tongue: a taper, not a block. Rectangular cores came
            # back as a row of lit windows.
            height = (LANE * (0.16 + 0.06 * (seed % 7)) * self._guttering(fire)
                      + math.sin(self._elapsed * FLICKER_HZ
                                 + fire[0] * 0.3) * 2.0)
            width = DROP_STEP * (0.7 + 0.05 * (seed % 6))
            x = fire[0] - ox + (seed % 5) - 2
            y = fire[1] - oy
            pygame.draw.polygon(surface, FIRE_CORE, (
                (x - width, y), (x, y - height),
                (x + width, y), (x, y + height)))

        # The warning, over the lot: narrow, translucent, and warm
        # rather than bright. It has to be obvious at a glance that this
        # stretch has not caught yet.
        glowing = [fire for fire in self.fires if fire[2] < GLOW]
        if glowing:
            layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            for fire in glowing:
                along = fire[2] / GLOW
                self._band(layer, fire, 0.34 + 0.5 * along, GLOW_COLOUR,
                           camera_offset, alpha=round(46 + 78 * along))
            surface.blit(layer, (0, 0))

        if self.flying:
            # The shadow, on the ground the animal is above rather than
            # under the sprite. It is the only thing on screen that says
            # where the thing actually is, and therefore where the fire
            # is about to be.
            shadow = pygame.Surface((88, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, SHADOW, shadow.get_rect())
            surface.blit(shadow, (round(self.x - 44 - ox),
                                  round(self.track_y - 13 - oy)))

    @staticmethod
    def _guttering(fire) -> float:
        """How much of its height a patch has left.

        It gutters over the last third of the burn, so a stretch of
        floor is visibly on its way out before it stops hurting -- which
        is the only warning a player gets that it is about to be safe
        again, and worth having.
        """
        along = (fire[2] - GLOW) / BURN
        return 1.0 - max(0.0, along - 0.66) / 0.34 * 0.5

    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        """The animal itself, over everything: it is in the air."""
        if not self.flying or not self._frames:
            return
        ox, oy = camera_offset
        image = self._frames[self.frame_index]
        if self.direction > 0:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, (round(self.x - FRAME_W / 2 - ox),
                             round(self.track_y - FRAME_H / 2
                                   - ALTITUDE - oy)))
