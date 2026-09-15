"""The orcs' siege on the trio: archers, then a catapult, then the dragon.

The horde charges the fighter and the ranger. This is the rest of the
orc army doing what an army does to people it cannot reach: standing
off and shooting at them.

In order, on the encounter's own clock:

    a few seconds in, orc archers march in from the north and south
    edges, take up posts well back from the heroes, and loose arrows
    at them. The arrows are aimed at the three of them, not at Chuck,
    but they cross the arena to get there and a rat in the way is hit.

    after the midpoint exchange, two orcs push a catapult in from the
    south edge. It lobs rocks at the heroes; each one comes down short
    of them -- its shadow on the floor marks where -- and rolls the rest
    of the way. Rolling rock is the thing for Chuck to dodge.

    and when the dragon arrives, its first pass is flown down the
    catapult's row rather than Chuck's. The stripe of fire takes out
    the catapult and the orcs working it, and from then on the dragon
    hunts Chuck the way it always has. Its fire burns archers too,
    because it does not care whose side anybody is on.

Nothing here is aimed at Chuck, and nothing here can be stopped by him.
It is more of the room he is surviving. A death rebuilds the lot, the
same way it rebuilds the horde.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from src.core import config
from src.entities.battle_hazards import BattleProjectile
from src.entities.undead import UndeadEnemy

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.entities.battle_actor import BattleActor


TS = config.TILE_SIZE

# ---------------------------------------------------------------------
# Archers
# ---------------------------------------------------------------------
# How long after the entrance before they come.
ARCHERS_AT = 5.0
# Where each one comes in, and where it stands. Straight lines down from
# the north edge and up from the south edge, over open floor the whole
# way (a test walks every one of them), to posts a long bowshot back
# from the heroes.
ARCHER_POSTS: tuple[tuple[tuple[int, int], tuple[int, int]], ...] = (
    ((38, -1), (38, 5)),
    ((44, -1), (44, 8)),
    ((50, -1), (50, 4)),
    ((39, 52), (39, 44)),
    ((36, 52), (36, 47)),
)
# Each one steps out a moment after the last, so they arrive as a file.
ARCHER_STAGGER = 0.8
ARCHER_MARCH_SPEED = 30.0
# One arrow each, every this many seconds, staggered across the line.
ARCHER_INTERVAL = 2.8
ARCHER_FIRST_SHOT = 0.6

# ---------------------------------------------------------------------
# The catapult
# ---------------------------------------------------------------------
CATAPULT_SHEET = "hazards/orc_catapult.png"
CATAPULT_FRAME = (56, 44)
# It comes after this beat of the conversation has been spoken, and
# this long after it.
CATAPULT_AFTER_BEAT = 2
CATAPULT_DELAY = 3.0
# Pushed in from below the south edge to its emplacement.
CATAPULT_FROM = (32, 53)
CATAPULT_POST = (32, 41)
CATAPULT_PUSH_SPEED = 26.0
# The shot cycle: loose, hold the arm up, reload.
CATAPULT_FIRST_SHOT = 1.5
CATAPULT_INTERVAL = 3.4
LOOSE_TIME = 0.12
RELOAD_TIME = 1.3
# ...and how long the wreck smoulders before the dragon's work is done.
WRECK_SMOKE = 6.0

# The rock: its flight, where it comes down, and its roll.
ROCK_FLIGHT = 1.25
ROCK_ARC = 70.0
# Where along the line to the hero it lands, cycled so no two shots in a
# row come down in the same place.
ROCK_LANDINGS = (0.42, 0.58, 0.34, 0.5, 0.64)
ROCK_SPREAD = (0.0, 1.6, -1.6, 0.8, -0.8)     # tiles, across the line
ROCK_ROLL_SPEED = 62.0
ROCK_RADIUS = 6.0
ROCK_LIFE = 9.0
ROCK_DAMAGE = 15
# How close to the hero it gets before it has spent itself against the
# line they are holding.
ROCK_STOP_SHORT = 14.0

ROCK_DARK = (92, 86, 78)
ROCK = (138, 130, 118)
ROCK_LIT = (184, 176, 158)
SHADOW = (24, 20, 18, 110)
DUST = (196, 180, 140)
SMOKE = (70, 66, 64)


def _centre(cell: tuple[int, int]) -> tuple[float, float]:
    return ((cell[0] + 0.5) * TS, (cell[1] + 0.5) * TS)


class OrcArcher(UndeadEnemy):
    """An orc with a bow, who walks to a post and shoots at the heroes."""

    def __init__(self, entry: tuple[int, int], post: tuple[int, int],
                 delay: float, shot_offset: float) -> None:
        x, y = _centre(entry)
        super().__init__(x, y, "orc")
        self._post = _centre(post)
        self._delay = delay
        self._shot = ARCHER_FIRST_SHOT + shot_offset
        self.shots = 0
        self.facing = "down" if post[1] > entry[1] else "up"

    def load_sprites(self, assets: "AssetManager") -> None:
        down, up, left = assets.sheet(
            "hazards/orc_archer.png", config.UNDEAD_FRAME_W,
            config.UNDEAD_FRAME_H)[0]
        self._frames = {"down": down, "up": up, "left": left,
                        "right": pygame.transform.flip(left, True, False)}

    @property
    def centre(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def posted(self) -> bool:
        return math.dist(self.centre, self._post) < 0.5

    def update(self, dt: float, _player=None) -> None:
        """Walk to the post. Shooting is the siege's job."""
        if self._delay > 0.0:
            self._delay -= dt
            return
        if self.posted:
            return
        cx, cy = self.centre
        dx, dy = self._post[0] - cx, self._post[1] - cy
        distance = math.hypot(dx, dy)
        step = min(distance, ARCHER_MARCH_SPEED * dt)
        self.x += dx / distance * step
        self.y += dy / distance * step

    @property
    def on_the_map(self) -> bool:
        """Has it stepped out yet? Waiting archers are off the map."""
        return self._delay <= 0.0

    def aim(self, target: "BattleActor", dt: float):
        """An arrow at the target when one is due, or None."""
        if not self.posted:
            return None
        self._shot -= dt
        if self._shot > 0.0:
            return None
        self._shot += ARCHER_INTERVAL
        cx, cy = self.centre
        dx, dy = target.center_x - cx, target.center_y - cy
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        # Loosed from the bow, at chest height, and spent at the hero.
        shot = BattleProjectile(cx, cy - 12, dx, dy, "orc_arrow")
        shot._travel_left = max(8.0, math.hypot(dx, dy) - 6.0)
        self.shots += 1
        return shot


class SiegeOperator(UndeadEnemy):
    """One of the two orcs working the catapult. Goes where it goes."""

    def __init__(self, offset: tuple[float, float]) -> None:
        super().__init__(0.0, 0.0, "orc")
        self.offset = offset

    def update(self, dt: float, _player=None) -> None:
        return

    def follow(self, x: float, y: float, facing: str) -> None:
        self.x = x + self.offset[0] - self.width / 2
        self.y = y + self.offset[1] - self.height / 2
        self.facing = facing


class LobbedRock:
    """A rock in the air, and the shadow that says where it will land."""

    def __init__(self, start, landing, roll_to) -> None:
        self.start = start
        self.landing = landing
        self.roll_to = roll_to
        self.age = 0.0
        self.alive = True

    @property
    def progress(self) -> float:
        return min(1.0, self.age / ROCK_FLIGHT)

    @property
    def position(self) -> tuple[float, float]:
        t = self.progress
        x = self.start[0] + (self.landing[0] - self.start[0]) * t
        y = self.start[1] + (self.landing[1] - self.start[1]) * t
        return x, y - math.sin(math.pi * t) * ROCK_ARC

    def update(self, dt: float) -> "RollingRock | None":
        self.age += dt
        if self.age < ROCK_FLIGHT:
            return None
        self.alive = False
        return RollingRock(self.landing, self.roll_to)

    def draw_shadow(self, surface, offset) -> None:
        t = self.progress
        width = round(6 + 10 * t)
        height = max(2, round(width * 0.4))
        shadow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (*SHADOW[:3], round(40 + 90 * t)),
                            shadow.get_rect())
        surface.blit(shadow, (round(self.landing[0] - width / 2 - offset[0]),
                              round(self.landing[1] - height / 2
                                    - offset[1])))

    def draw(self, surface, offset) -> None:
        x, y = self.position
        _draw_rock(surface, x - offset[0], y - offset[1], self.age * 9.0)


class RollingRock:
    """A rock rolling along the floor at the heroes. Chuck's to dodge."""

    def __init__(self, start, roll_to) -> None:
        self.x, self.y = start
        dx, dy = roll_to[0] - start[0], roll_to[1] - start[1]
        distance = math.hypot(dx, dy) or 1.0
        self.vx = dx / distance * ROCK_ROLL_SPEED
        self.vy = dy / distance * ROCK_ROLL_SPEED
        self._left = max(0.0, distance - ROCK_STOP_SHORT)
        self.travelled = 0.0
        self.age = 0.0
        self.dust = 0.35
        self.alive = True

    @property
    def hitbox(self) -> pygame.Rect:
        r = ROCK_RADIUS
        return pygame.Rect(round(self.x - r), round(self.y - r),
                           round(r * 2), round(r * 2))

    def update(self, dt: float, tilemap) -> None:
        self.age += dt
        self.dust = max(0.0, self.dust - dt)
        step = ROCK_ROLL_SPEED * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.travelled += step
        col, row = int(self.x) // TS, int(self.y) // TS
        if (self.travelled >= self._left or self.age >= ROCK_LIFE
                or not (0 <= col < tilemap.width_tiles
                        and 0 <= row < tilemap.height_tiles)
                or tilemap.is_solid(col, row)
                or tilemap.terrain_at(col, row) == "V"):
            self.alive = False

    def draw(self, surface, offset) -> None:
        x, y = self.x - offset[0], self.y - offset[1]
        if self.dust > 0.0:
            spread = (0.35 - self.dust) * 40
            for angle in (0.4, 2.0, 3.6, 5.2):
                pygame.draw.circle(
                    surface, DUST,
                    (round(x + math.cos(angle) * spread),
                     round(y + 3 + math.sin(angle) * spread * 0.4)), 2)
        _draw_rock(surface, x, y, self.travelled / ROCK_RADIUS)


def _draw_rock(surface, x: float, y: float, spin: float) -> None:
    centre = (round(x), round(y))
    radius = round(ROCK_RADIUS)
    pygame.draw.circle(surface, (30, 26, 22), centre, radius + 1)
    pygame.draw.circle(surface, ROCK_DARK, centre, radius)
    pygame.draw.circle(surface, ROCK, centre, radius - 1)
    # A lighter facet that goes round as it rolls.
    pygame.draw.circle(
        surface, ROCK_LIT,
        (round(x + math.cos(spin) * radius * 0.45),
         round(y + math.sin(spin) * radius * 0.45)), max(1, radius // 3))


class Catapult:
    """The siege engine: pushed in, loosing rocks, and then a wreck."""

    def __init__(self) -> None:
        self.x, self.y = _centre(CATAPULT_FROM)
        self._post = _centre(CATAPULT_POST)
        self.state = "pushing"          # pushing | ready | loosing | reload | wreck
        self._t = CATAPULT_FIRST_SHOT
        self._frames: tuple = ()
        self.shots = 0
        self.wrecked_for = 0.0
        self.operators = [SiegeOperator((-10.0, 12.0)),
                          SiegeOperator((10.0, 12.0))]
        self._place_operators()

    def load_sprites(self, assets) -> None:
        self._frames = tuple(assets.sheet(CATAPULT_SHEET,
                                          *CATAPULT_FRAME)[0])
        for operator in self.operators:
            operator.load_sprites(assets)

    # ------------------------------------------------------------------
    @property
    def wrecked(self) -> bool:
        return self.state == "wreck"

    @property
    def sort_y(self) -> float:
        return self.y + 4

    @property
    def body(self) -> pygame.Rect:
        """What the dragon's fire has to touch, and what Chuck bumps."""
        return pygame.Rect(round(self.x - 22), round(self.y - 10), 44, 14)

    @property
    def bucket(self) -> tuple[float, float]:
        return (self.x + 2, self.y - 30)

    def _place_operators(self) -> None:
        if self.state == "pushing":
            # Behind it, which on the way up from the south is below.
            facing = "up"
            offsets = ((-10.0, 12.0), (10.0, 12.0))
        else:
            facing = "right"
            offsets = ((-30.0, 2.0), (-20.0, 8.0))
        for operator, offset in zip(self.operators, offsets):
            operator.offset = offset
            operator.follow(self.x, self.y, facing)

    def update(self, dt: float) -> bool:
        """Advance. Returns True on the frame a rock is loosed."""
        if self.wrecked:
            self.wrecked_for += dt
            return False
        if self.state == "pushing":
            dx, dy = self._post[0] - self.x, self._post[1] - self.y
            distance = math.hypot(dx, dy)
            step = CATAPULT_PUSH_SPEED * dt
            if distance <= step:
                self.x, self.y = self._post
                self.state = "ready"
            else:
                self.x += dx / distance * step
                self.y += dy / distance * step
            self._place_operators()
            return False
        self._t -= dt
        if self.state == "ready" and self._t <= 0.0:
            self.state = "loosing"
            self._t = LOOSE_TIME
            return False
        if self.state == "loosing" and self._t <= 0.0:
            self.state = "reload"
            self._t = RELOAD_TIME
            self.shots += 1
            return True
        if self.state == "reload" and self._t <= 0.0:
            self.state = "ready"
            self._t = CATAPULT_INTERVAL - LOOSE_TIME - RELOAD_TIME
        return False

    def wreck(self) -> None:
        self.state = "wreck"
        self.wrecked_for = 0.0
        for operator in self.operators:
            operator.alive = False

    # ------------------------------------------------------------------
    @property
    def frame_index(self) -> int:
        if self.wrecked:
            return 3
        if self.state == "loosing":
            return 1
        if self.state == "reload" and self._t > RELOAD_TIME - 0.5:
            return 2
        return 0

    def draw(self, surface, offset) -> None:
        fw, fh = CATAPULT_FRAME
        left = round(self.x - fw / 2 - offset[0])
        top = round(self.y + 6 - fh - offset[1])
        if self._frames:
            surface.blit(self._frames[self.frame_index], (left, top))
        else:
            pygame.draw.rect(surface, (110, 80, 50),
                             (left + 6, top + 26, fw - 12, 12))
        if self.wrecked and self.wrecked_for < WRECK_SMOKE:
            fade = 1.0 - self.wrecked_for / WRECK_SMOKE
            for index in range(5):
                t = (self.wrecked_for * 0.8 + index / 5) % 1.0
                x = self.x - 14 + index * 7 + math.sin(t * 6 + index) * 3
                y = self.y - 8 - t * 34
                pygame.draw.circle(
                    surface, SMOKE,
                    (round(x - offset[0]), round(y - offset[1])),
                    max(1, round((2 + t * 5) * fade)))


class OrcSiege:
    """The archers, the catapult and its rocks, for one visit to the room."""

    def __init__(self, tilemap, assets: "AssetManager | None",
                 heroes: list["BattleActor"]) -> None:
        self._tilemap = tilemap
        self._assets = assets
        self._heroes = [hero for hero in heroes
                        if hero.kind in ("fighter", "wizard", "ranger")]
        self.elapsed = 0.0
        self.archers: list[OrcArcher] = []
        self.catapult: Catapult | None = None
        self._catapult_due: float | None = None
        self.lobbed: list[LobbedRock] = []
        self.rocks: list[RollingRock] = []
        self._rock_index = 0
        self._archer_target = 0

    # ------------------------------------------------------------------
    @property
    def bodies(self) -> list[UndeadEnemy]:
        """Every orc of the siege standing on the map."""
        people: list[UndeadEnemy] = [
            archer for archer in self.archers
            if archer.alive and archer.on_the_map]
        if self.catapult is not None:
            people += [operator for operator in self.catapult.operators
                       if operator.alive]
        return people

    @property
    def drawables(self) -> list:
        return [self.catapult] if self.catapult is not None else []

    def update(self, dt: float, beats_played: int) -> list[BattleProjectile]:
        """Run the siege. Returns the arrows loosed this frame."""
        self.elapsed += dt
        shots: list[BattleProjectile] = []

        if not self.archers and self.elapsed >= ARCHERS_AT:
            for index, (entry, post) in enumerate(ARCHER_POSTS):
                archer = OrcArcher(entry, post, index * ARCHER_STAGGER,
                                   index * ARCHER_INTERVAL
                                   / len(ARCHER_POSTS))
                archer.tilemap = self._tilemap
                if self._assets is not None:
                    archer.load_sprites(self._assets)
                self.archers.append(archer)
        for archer in self.archers:
            if not archer.alive:
                continue
            archer.update(dt)
            if self._heroes:
                target = self._heroes[self._archer_target
                                      % len(self._heroes)]
                shot = archer.aim(target, dt)
                if shot is not None:
                    self._archer_target += 1
                    shots.append(shot)
        self.archers = [archer for archer in self.archers if archer.alive]

        if (self.catapult is None and self._catapult_due is None
                and beats_played >= CATAPULT_AFTER_BEAT):
            self._catapult_due = CATAPULT_DELAY
        if self._catapult_due is not None and self.catapult is None:
            self._catapult_due -= dt
            if self._catapult_due <= 0.0:
                self.catapult = Catapult()
                if self._assets is not None:
                    self.catapult.load_sprites(self._assets)
        if self.catapult is not None:
            if self.catapult.update(dt) and self._heroes:
                self._loose()

        for rock in self.lobbed:
            landed = rock.update(dt)
            if landed is not None:
                self.rocks.append(landed)
        self.lobbed = [rock for rock in self.lobbed if rock.alive]
        for rock in self.rocks:
            rock.update(dt, self._tilemap)
        self.rocks = [rock for rock in self.rocks if rock.alive]
        return shots

    def _loose(self) -> None:
        """One rock at one of the heroes, landing short and rolling on."""
        index = self._rock_index
        self._rock_index += 1
        hero = self._heroes[index % len(self._heroes)]
        start = self.catapult.bucket
        ground = (self.catapult.x, self.catapult.y)
        target = (hero.center_x, hero.center_y)
        dx, dy = target[0] - ground[0], target[1] - ground[1]
        distance = math.hypot(dx, dy) or 1.0
        along = ROCK_LANDINGS[index % len(ROCK_LANDINGS)]
        across = ROCK_SPREAD[index % len(ROCK_SPREAD)] * TS
        landing = (ground[0] + dx * along - dy / distance * across,
                   ground[1] + dy * along + dx / distance * across)
        roll_to = (target[0] - dy / distance * across * 0.3,
                   target[1] + dx / distance * across * 0.3)
        self.lobbed.append(LobbedRock(start, landing, roll_to))

    # ------------------------------------------------------------------
    def burn(self, rects) -> int:
        """The dragon's fire: wreck the catapult, burn whoever is in it."""
        rects = list(rects)
        if not rects:
            return 0
        burned = 0
        if self.catapult is not None and not self.catapult.wrecked:
            body = self.catapult.body
            if any(body.colliderect(rect) for rect in rects):
                self.catapult.wreck()
                burned += 1
        for archer in self.bodies:
            if archer.alive and any(archer.hitbox.colliderect(rect)
                                    for rect in rects):
                archer.alive = False
                burned += 1
        self.archers = [archer for archer in self.archers if archer.alive]
        return burned

    @property
    def target_row(self) -> int | None:
        """The row the dragon's first pass should take, while it stands."""
        if self.catapult is None or self.catapult.wrecked \
                or self.catapult.state == "pushing":
            return None
        return int(self.catapult.y) // TS

    def blocks(self, box: pygame.Rect) -> bool:
        """Does the catapult stand in the way of this box?"""
        return (self.catapult is not None and not self.catapult.wrecked
                and box.colliderect(self.catapult.body))

    def damage_for(self, box: pygame.Rect) -> int:
        if any(box.colliderect(rock.hitbox) for rock in self.rocks):
            return ROCK_DAMAGE
        return 0

    def draw_ground(self, surface, offset) -> None:
        for rock in self.lobbed:
            rock.draw_shadow(surface, offset)
        for rock in self.rocks:
            rock.draw(surface, offset)

    def draw_air(self, surface, offset) -> None:
        for rock in self.lobbed:
            rock.draw(surface, offset)
