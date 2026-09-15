"""The red dragon that crosses the final encounter, and what it leaves.

The blue dragon on the frozen map is a fixed thing that breathes down a
lane: you learn where the lane is and you time it. This one is the same
animal doing the opposite. It comes in off one side of the arena, flies
across it, and the ground under its track catches fire behind it. So
instead of a hazard that is always in the same place and sometimes
lethal, this is a hazard that is always lethal and never in the same
place twice.

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

## And then it comes down

Every pass now stops part way across. The dragon comes down in the
arena, spits balls of fire that roll along the floor, climbs, and
finishes the crossing -- so a pass lays half its stripe, lands, and
lays the rest.

That is a different hazard from the stripe and it has to be, or the
back half of the encounter is the front half again with a longer clock.
The stripe is a line drawn once, across the whole room, that Chuck
steps out of; the rolling fire is a handful of slow objects coming at
him from one point, which he has to move *between*. One is a wall and
the other is traffic, and having to switch between reading them is most
of what makes the last minute of this feel like the last minute.

They escalate, because there is no reason for the third landing to be
the first one again. Each time it comes down the fan is one ball wider,
the balls are faster, and the volleys are closer together -- and by the
last of them the fire is quicker than Chuck is, so outrunning it stops
working and stepping through the gaps is all that is left.

Nothing about any of it can be fought and nothing about it ends. There
is no health, no scratching it, and no arrangement of the room that
makes it stop coming -- it is the blue dragon's contract, in motion.
"""

from __future__ import annotations

import math

import pygame

from src.core import config


SPRITE = "hazards/red_dragon.png"
FRAME_W, FRAME_H = 128, 96
FLY_FRAMES = 6
BREATH_FRAMES = 6
LANDED_FRAMES = 2
SPIT_FRAMES = 2
TOTAL_FRAMES = FLY_FRAMES + BREATH_FRAMES + LANDED_FRAMES + SPIT_FRAMES

# How fast it crosses, and how far above its own track it is drawn. The
# altitude is what makes the shadow separate from the animal, and the
# shadow is what tells a player on the ground where the thing actually
# is: while it is up there the sprite's position on screen is not where
# it will burn.
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
PASS_GAP = 2.2
FIRST_PASS = 2.0
# The lane has to fit inside the arena wherever it aims, so the row it
# picks is clamped this far from the top and bottom.
ROW_MARGIN = 4

# ---------------------------------------------------------------------
# Coming down
# ---------------------------------------------------------------------
# Every pass ends on the ground part way across, and then finishes.
#
# It was every *second* pass at first, so that the plain crossings kept
# happening -- and what that bought was two landings in the whole
# encounter, which is one step of escalation and no curve at all. The
# thing that makes this work instead is that a landing pass is not an
# alternative to a crossing: it flies in laying its stripe, sets down,
# spits, climbs, and lays the rest of the stripe on its way out. Both
# hazards, every time, and four landings instead of two.
LAND_EVERY = 1
# How far short of him it puts itself down, in tiles. Landing on top of
# him would be a fan of rolling fire at point-blank range, which is not
# a dodge, it is an announcement.
LAND_STANDOFF = 7
# How long the descent and the climb take. Long enough to be a move
# rather than a teleport, short enough not to be an interlude.
DESCENT = 0.9
CLIMB = 0.9
# How long it stays down. Two or three volleys' worth.
LANDED_TIME = 6.2
# How far from the arena's own edges it will put itself down, in tiles.
# A dragon landing with half of itself off the map is a dragon that
# looks placed rather than arrived.
LAND_MARGIN = 7

# The rolling fire, and how it gets worse. Everything here is indexed
# by how many times it has already come down, so the third landing is
# nothing like the first.
BALL_RADIUS = 7.0
BALL_SPEED = 56.0
BALL_SPEED_STEP = 12.0
BALL_LIFE = 5.5
BALL_DAMAGE = 20
# How wide a stretch of Astral a ball will roll across, in tiles. The
# arena's cracks are narrower than this; the rift and the band coming in
# from the west are far wider.
CRACK_REACH = 7
FAN_FIRST = 3
FAN_STEP = 1
FAN_SPREAD = 0.40
VOLLEY_FIRST = 1.1
VOLLEY_INTERVAL = 1.9
VOLLEY_STEP = 0.38

# Beats per second of the wing, and how fast the flame flickers.
WING_HZ = 7.0
FLICKER_HZ = 11.0
# ...and how fast a ball appears to roll, in radians per pixel it
# travels. It is drawn as a bright core orbiting inside a darker
# sphere, which is the cheapest thing that reads as rolling rather than
# as sliding.
ROLL_RATE = 0.09

SHADOW = (24, 18, 22, 90)
GLOW_COLOUR = (255, 158, 54)
FIRE_DEEP = (206, 62, 22)
FIRE = (255, 148, 40)
FIRE_CORE = (255, 240, 176)
EMBER = (138, 52, 34)

# What standing in the stripe costs. The most expensive touch in the
# phase, and deliberately so: this one is avoidable in a way that a
# stray arrow in a crowded room is not.
SANITY_DAMAGE = 26


class FlameBall:
    """One ball of fire rolling across the floor.

    It goes in a straight line at a fixed speed and it does not steer.
    That is the point of it: a thing that chased him would be a second
    dragon, and what this room wants is a moving obstacle whose whole
    future he can read the moment it leaves the mouth.

    It dies on anything it cannot roll over -- a wall, or the edge of
    the Astral Sea -- because a ball of fire sitting in the middle of a
    tear in the world is a bug, and because the holes in that floor are
    the one thing a player is already reading.

    ...but a crack is not the Sea. The arena is scattered with narrow
    Astral cracks, and stopping at every one of them meant that from
    most places the dragon comes down, most of a volley went out on the
    first gap between it and Chuck. So it rolls across a crack and
    carries on the far side, and only goes out where there is nothing
    but Sea ahead of it: the rift, and the band coming in from the west.
    """

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 speed: float) -> None:
        length = math.hypot(dx, dy) or 1.0
        self.x, self.y = x, y
        self.vx, self.vy = dx / length * speed, dy / length * speed
        self.travelled = 0.0
        self.age = 0.0
        self.alive = True

    @property
    def hitbox(self) -> pygame.Rect:
        radius = BALL_RADIUS
        return pygame.Rect(round(self.x - radius), round(self.y - radius),
                           round(radius * 2), round(radius * 2))

    def update(self, dt: float, tilemap) -> None:
        if not self.alive:
            return
        self.age += dt
        if self.age >= BALL_LIFE:
            self.alive = False
            return
        step_x, step_y = self.vx * dt, self.vy * dt
        self.x += step_x
        self.y += step_y
        self.travelled += math.hypot(step_x, step_y)
        col = int(self.x) // config.TILE_SIZE
        row = int(self.y) // config.TILE_SIZE
        if not (0 <= col < tilemap.width_tiles
                and 0 <= row < tilemap.height_tiles):
            self.alive = False
            return
        if tilemap.is_solid(col, row):
            self.alive = False
        elif (tilemap.terrain_at(col, row) == "V"
                and self._open_sea_ahead(tilemap)):
            self.alive = False

    def _open_sea_ahead(self, tilemap) -> bool:
        """Is it rolling out over the Sea rather than across a crack?

        Looked for along its own heading: if there is floor within
        CRACK_REACH of it, it is on a crack and will reach the far side.
        """
        speed = math.hypot(self.vx, self.vy) or 1.0
        ux, uy = self.vx / speed, self.vy / speed
        ts = config.TILE_SIZE
        reach = CRACK_REACH * ts
        along = ts / 2
        while along <= reach:
            col = int(self.x + ux * along) // ts
            row = int(self.y + uy * along) // ts
            if not (0 <= col < tilemap.width_tiles
                    and 0 <= row < tilemap.height_tiles):
                return True
            if tilemap.is_solid(col, row):
                return True
            if tilemap.terrain_at(col, row) != "V":
                return False
            along += ts / 2
        return True

    def draw(self, surface: pygame.Surface,
             camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        x, y = self.x - ox, self.y - oy
        # Guttering out over the last of its life rather than vanishing
        # mid-floor: a ball that blinks off is a ball a player will
        # assume they can wait out.
        left = min(1.0, (BALL_LIFE - self.age) / 0.8)
        radius = BALL_RADIUS * left
        if radius < 1.0:
            return
        pygame.draw.circle(surface, FIRE_DEEP, (round(x), round(y)),
                           round(radius))
        pygame.draw.circle(surface, FIRE, (round(x), round(y)),
                           max(1, round(radius * 0.68)))
        # The core orbits as it travels, which is what says rolling.
        spin = self.travelled * ROLL_RATE
        offset = radius * 0.34
        pygame.draw.circle(
            surface, FIRE_CORE,
            (round(x + math.cos(spin) * offset),
             round(y + math.sin(spin) * offset)),
            max(1, round(radius * 0.36)))


class RedDragonFlyby:
    """One red dragon: its crossings, its landings, and its fire.

    Deliberately not an `Entity` and deliberately not an `UndeadEnemy`:
    it has no hitbox worth colliding with, no health, and no death. What
    the world needs from it is a rectangle list and two draw calls --
    three, once it started landing, because a dragon on the floor has to
    sort with everything else on the floor.
    """

    def __init__(self, tilemap, *, first_pass: float = FIRST_PASS) -> None:
        self._tilemap = tilemap
        self._frames: tuple = ()
        self.passes = 0
        self.landings = 0
        # waiting | flying | landing | landed | leaving
        self.phase = "waiting"
        self.row = 0
        self.direction = 1          # +1 travelling east, -1 west
        self.x = 0.0
        self._wait = first_pass
        self._phase_t = 0.0
        self._land_at: float | None = None
        self._volley = 0.0
        self._since_drop = 0.0
        self._elapsed = 0.0
        # A row for the next pass to take instead of Chuck's, and no
        # landing on it: the final encounter sends its first pass down
        # the orcs' catapult. None means the ordinary pass at him.
        self.aim_row: int | None = None
        # [x, y, age] per patch of burning floor, oldest first.
        self.fires: list[list] = []
        self.balls: list[FlameBall] = []

    def load_sprites(self, assets) -> None:
        self._frames = tuple(assets.sheet(SPRITE, FRAME_W, FRAME_H)[0])

    # ------------------------------------------------------------------
    # Where it is
    # ------------------------------------------------------------------
    @property
    def track_y(self) -> float:
        """The centre of the burning stripe, in world pixels."""
        return (self.row + 0.5) * config.TILE_SIZE

    @property
    def _span(self) -> float:
        return self._tilemap.width_tiles * config.TILE_SIZE

    @property
    def present(self) -> bool:
        """Is it anywhere on the map?"""
        return self.phase != "waiting"

    @property
    def flying(self) -> bool:
        """Up there and crossing. The stripe only exists while so."""
        return self.phase in ("flying", "leaving")

    @property
    def on_the_ground(self) -> bool:
        return self.phase == "landed"

    @property
    def altitude(self) -> float:
        """How far above its own track the sprite is drawn.

        Interpolated through the descent and the climb, so the animal
        visibly comes down to the floor and goes back up rather than
        snapping between two heights.
        """
        if self.phase == "landing":
            return ALTITUDE * max(0.0, 1.0 - self._phase_t / DESCENT)
        if self.phase == "landed":
            return 0.0
        if self.phase == "leaving":
            return ALTITUDE * min(1.0, self._phase_t / CLIMB)
        return ALTITUDE

    @property
    def sort_y(self) -> float:
        """Its feet, for the stretch where it has any on the ground."""
        return self.track_y + FRAME_H * 0.22

    # ------------------------------------------------------------------
    # The pass
    # ------------------------------------------------------------------
    def begin(self, row: int, land_col: int | None = None,
              land: bool = True) -> None:
        """Send it across at `row`, from whichever side it did not last."""
        top = ROW_MARGIN
        bottom = self._tilemap.height_tiles - 1 - ROW_MARGIN
        self.row = max(top, min(bottom, int(row)))
        # Alternating sides, so two passes running never come from the
        # same place: a hazard that always arrives from the west is a
        # hazard you can stand on the west side of.
        self.direction = 1 if self.passes % 2 == 0 else -1
        self.x = -FRAME_W if self.direction > 0 else self._span + FRAME_W
        self.phase = "flying"
        self.passes += 1
        self._since_drop = 0.0
        self._land_at = None
        if land and self.passes % LAND_EVERY == 0:
            self._land_at = self._landing_spot(land_col)

    def _landing_spot(self, land_col: int | None) -> float:
        """Where this pass will stop, in world pixels.

        Short of him rather than on him, on ground rather than on the
        Sea, and inside the arena's own margins. All three of those are
        failures I would rather not ship: a landing on his tile puts a
        fan of rolling fire at point-blank range, a landing on the
        Astral is a dragon standing on a hole with its fire dying the
        instant it leaves the mouth, and a landing at the map's edge is
        an animal that looks placed rather than arrived.
        """
        ts = config.TILE_SIZE
        if land_col is None:
            land_col = self._tilemap.width_tiles // 2
        wanted = int(land_col) - LAND_STANDOFF * self.direction
        low = LAND_MARGIN
        high = self._tilemap.width_tiles - 1 - LAND_MARGIN
        col = max(low, min(high, wanted))
        # By the time it starts coming down the western half of this
        # arena is Astral Sea, so "inside the map" is not the same
        # question as "on the floor". Walk out from the wanted column
        # until there is something to stand on.
        for reach in range(0, self._tilemap.width_tiles):
            for candidate in (col + reach, col - reach):
                if not low <= candidate <= high:
                    continue
                if self._burnable((candidate + 0.5) * ts, self.track_y):
                    return (candidate + 0.5) * ts
        return (col + 0.5) * ts

    def update(self, dt: float, player_tile: tuple[int, int] | None = None,
               player_pos: tuple[float, float] | None = None) -> None:
        self._elapsed += dt
        for fire in self.fires:
            fire[2] += dt
        self.fires = [fire for fire in self.fires if fire[2] < LIFE]
        for ball in self.balls:
            ball.update(dt, self._tilemap)
        self.balls = [ball for ball in self.balls if ball.alive]

        if self.phase == "waiting":
            self._wait -= dt
            if self._wait <= 0.0 and self.aim_row is not None:
                # A row somebody else chose, flown straight across.
                row, self.aim_row = self.aim_row, None
                self.begin(row, land=False)
            elif self._wait <= 0.0:
                # Aimed at wherever he is standing *now*, and then
                # fixed. Re-aiming in flight would be a dragon chasing
                # a rat, which is both unfair and beneath it.
                self.begin(
                    player_tile[1] if player_tile is not None
                    else self._tilemap.height_tiles // 2,
                    player_tile[0] if player_tile is not None else None,
                )
            return

        if self.phase == "landing":
            self._phase_t += dt
            if self._phase_t >= DESCENT:
                self.phase = "landed"
                self._phase_t = 0.0
                self.landings += 1
                self._volley = VOLLEY_FIRST
            return

        if self.phase == "landed":
            self._phase_t += dt
            self._volley -= dt
            if self._volley <= 0.0:
                self._volley += self.volley_interval
                self.spit(player_pos)
            if self._phase_t >= LANDED_TIME:
                self.phase = "leaving"
                self._phase_t = 0.0
            return

        if self.phase == "leaving":
            self._phase_t += dt
            if self._phase_t >= CLIMB:
                self.phase = "flying"
            # It is already moving as it climbs, which is why this falls
            # through into the crossing below rather than returning.

        before = self.x
        self.x += SPEED * self.direction * dt
        self._lay_fire(before, self.x)
        if self._land_at is not None and self._reached(before, self.x):
            self.x = self._land_at
            self.phase = "landing"
            self._phase_t = 0.0
            self._land_at = None
            return
        if (self.direction > 0 and self.x > self._span + FRAME_W) or \
                (self.direction < 0 and self.x < -FRAME_W):
            self.phase = "waiting"
            self._wait = PASS_GAP

    def _reached(self, before: float, after: float) -> bool:
        target = self._land_at
        if target is None:
            return False
        return (before < target <= after) if self.direction > 0 \
            else (after <= target < before)

    # ------------------------------------------------------------------
    # The fire
    # ------------------------------------------------------------------
    @property
    def volley_interval(self) -> float:
        """Closer together every time it comes down."""
        return max(0.55, VOLLEY_INTERVAL - VOLLEY_STEP * (self.landings - 1))

    @property
    def fan(self) -> int:
        """Wider every time it comes down."""
        return FAN_FIRST + FAN_STEP * max(0, self.landings - 1)

    @property
    def ball_speed(self) -> float:
        """Faster every time it comes down.

        By the third landing this is past Chuck's own walking speed,
        which is the moment outrunning the fire stops working and
        stepping between the balls is the only thing left. That is the
        escalation stated as a number rather than as a feeling: the
        hazard does not get bigger, it gets past him.
        """
        return BALL_SPEED + BALL_SPEED_STEP * max(0, self.landings - 1)

    def spit(self, player_pos: tuple[float, float] | None) -> int:
        """A fan of rolling fire, aimed where he is. Returns how many."""
        mouth_x = self.x - FRAME_W * 0.32 * self.direction
        mouth_y = self.track_y
        if player_pos is None:
            aim = (-float(self.direction), 0.0)
        else:
            aim = (player_pos[0] - mouth_x, player_pos[1] - mouth_y)
        if abs(aim[0]) < 1e-6 and abs(aim[1]) < 1e-6:
            aim = (-float(self.direction), 0.0)
        base = math.atan2(aim[1], aim[0])
        count = self.fan
        for index in range(count):
            offset = (index - (count - 1) / 2.0) * FAN_SPREAD
            angle = base + offset
            self.balls.append(FlameBall(
                mouth_x, mouth_y,
                math.cos(angle), math.sin(angle), self.ball_speed,
            ))
        return count

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

    @property
    def ball_rects(self) -> list[pygame.Rect]:
        return [ball.hitbox for ball in self.balls if ball.alive]

    def burns(self, box: pygame.Rect) -> bool:
        """Is anything of the dragon's burning this box right now?"""
        return any(box.colliderect(rect)
                   for rect in self.lethal_rects + self.ball_rects)

    def damage_for(self, box: pygame.Rect) -> int:
        """What touching it costs, or nothing.

        The stripe hurts more than a ball. The stripe is a wall he chose
        to stand in; a ball is one of four things that came at him while
        he was dealing with the other three. Both are avoidable and only
        one of them is avoidable at leisure.
        """
        if any(box.colliderect(rect) for rect in self.lethal_rects):
            return SANITY_DAMAGE
        if any(box.colliderect(rect) for rect in self.ball_rects):
            return BALL_DAMAGE
        return 0

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    @property
    def frame_index(self) -> int:
        beat = int(self._elapsed * WING_HZ) % FLY_FRAMES
        if self.phase == "landed":
            base = FLY_FRAMES + BREATH_FRAMES
            # Spitting for the moment either side of a volley, idling
            # between: the animal is visibly the cause of the thing
            # rolling at him rather than a statue with fire near it.
            if self._volley > self.volley_interval - 0.45:
                return (base + LANDED_FRAMES
                        + int(self._elapsed * 9) % SPIT_FRAMES)
            return base + int(self._elapsed * 2) % LANDED_FRAMES
        if self.phase in ("landing", "leaving"):
            # Wings out and working: it is holding itself up.
            return beat
        # It breathes for the whole crossing: the pass *is* the attack,
        # and a dragon that only opened its mouth over part of the room
        # would leave a stripe with a hole in it that nothing on screen
        # explained.
        return FLY_FRAMES + beat if self.phase == "flying" else beat

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
        """The trail, the rolling fire, and the shadow, under everyone.

        Drawn as rectangles the trail was three perfectly straight bands
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

        # The rolling fire, over the stripe and under everybody: it is
        # on the floor, and a ball drawn over Chuck is a ball he cannot
        # see himself standing beside.
        for ball in self.balls:
            ball.draw(surface, camera_offset)

        if self.present:
            # The shadow, on the ground the animal is above rather than
            # under the sprite. It is the only thing on screen that says
            # where the thing actually is, and therefore where the fire
            # is about to be -- and it tightens as the dragon comes
            # down, which is what makes a descent read as a descent.
            close = 1.0 - self.altitude / ALTITUDE
            width = round(88 - 26 * close)
            height = round(26 - 8 * close)
            shadow = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, SHADOW, shadow.get_rect())
            surface.blit(shadow, (round(self.x - width / 2 - ox),
                                  round(self.track_y - height / 2 - oy)))

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
        """The animal itself.

        Called from over the top of the world while it is in the air,
        and from inside the world's own y-sort once it is on the floor.
        The world decides which; see `on_the_ground`. A landed dragon
        drawn over everything hides Chuck behind eight tiles of red,
        which is exactly the thing this room is not allowed to do.
        """
        if not self.present or not self._frames:
            return
        ox, oy = camera_offset
        image = self._frames[self.frame_index]
        if self.direction > 0:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, (round(self.x - FRAME_W / 2 - ox),
                             round(self.track_y - FRAME_H / 2
                                   - self.altitude - oy)))
