"""The horde pressing the trio in the final encounter.

The room used to have the ranger whirling on the spot, throwing arrows
in every direction at nothing at all. It was a hazard and it was legible
as a hazard, but it read as a woman having a fit rather than as a fight,
and the document's own line about this encounter is that the three of
them may also be fighting enemies or another threat while completing
whatever process is required. There was no threat. Now there is one:
orcs, out of the camp Chuck passed on his way through the region, in a
continuous stream at the two of them who are holding the line.

Three rules, and every one of them is there to make the room read:

*The horde has not noticed Chuck and never will.* Each orc is charging
the fighter or the ranger, chosen once at spawn and never revisited --
whichever of the two it came in nearest. A one-foot rat is not what an
orc pushing a line is looking at, and the moment one of them turned to
chase him the room would stop being a battle he is caught in and become
a battle he is in.

*He is still in the way.* They do not aim at him, but they are bodies
moving through the same floor, and running into one costs the same
Sanity that running into any orc in this region costs. That is the
weave: the horde's paths converge on two points, so the ground between
Chuck and anywhere is crossed by a slow, readable current.

*The heroes kill them in one.* The ranger looses a single arrow at the
nearest orc to her and it drops; anything that gets past that and
reaches the fighter is cut down by his sword. Both of those existed
already as hazards Chuck has to stay out of -- her arrows and his arc --
and the change is that they now have a reason, which is the entire
point. Nothing about the danger to Chuck got smaller. It got aimed.

The orcs are ordinary `UndeadEnemy` orcs at ORC_SPEED rather than a
faster charging variant: the phase document fixes what an orc is
(slightly faster than a zombie) and this is not the place to keep a
second definition of it. What makes the pressure work instead is where
they come in. The ring is close enough that the line is always under
someone, and a press is already joined when Chuck walks in, because he
has walked into the middle of something already happening both of the
other times he has met these three.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.undead import UndeadEnemy
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.entities.battle_actor import BattleActor
    from src.world.tilemap import TileMap


# Where they come in from: down the west of the arena at the fighter,
# and up the south rim at the ranger. Authored rather than scattered,
# and the thing that had to be checked is not that a cell is walkable --
# it is that an orc starting there *arrives*, both on the arena as it
# opens and on the arena after the rift has taken everything it is going
# to take. A test simulates every one of them, on both.
#
# That check is why there is nothing along the north rim. The Astral
# crack that runs from (48, 14) grows west with the rift and welds onto
# it, and what it leaves behind is a funnel that narrows to one tile and
# then stops -- so anything walking south down the map's east side ends
# up in a cul-de-sac four tiles from the fighter with no way to see that
# it should have gone round. The route that works is west of the crack
# and then east along the rows the heroes are standing in, and those are
# the cells written down here. The north of the arena is Chuck's to run
# around in; it is not a way in.
SPAWN_CELLS = (
    (28, 8), (32, 12), (36, 16), (40, 16), (28, 20), (32, 24), (36, 24),
    (28, 32), (32, 36), (40, 36), (28, 40),
    (46, 47), (50, 47), (54, 47), (52, 49),
)
# Coprime with the ring, so the stream comes from a different side each
# time rather than marching round it in order.
SPAWN_STRIDE = 7

# Roughly how long the longest of those approaches takes. Nothing reads
# it; it is here so the next person to move a spawn cell knows what the
# number was meant to be.
LONGEST_APPROACH = 24.0

# The press that is already on them when Chuck arrives. He has walked
# into the middle of this twice before and the room is written that way;
# an empty arena that filled up over the first twenty seconds would be
# the fight starting when he got there.
OPENING = (
    # Four already on them, so the first frame of the room is a fight
    # rather than a fight arriving...
    (52, 22), (51, 24), (52, 28), (51, 30),
    # ...and five feeding in behind, so it does not go quiet the moment
    # those four are cut down.
    (44, 20), (44, 26), (50, 20), (47, 35), (45, 38),
)


class HordeOrc(UndeadEnemy):
    """One orc, charging a hero, with no interest in Chuck at all.

    It is an ordinary desert orc in every respect but two. It ignores
    the player it is handed and steers for the actor it was given at
    spawn, with no notice range, because it noticed its target before
    Chuck was in the room. And when the straight line is blocked it
    goes round rather than standing there.

    That second part is not polish, it is the difference between this
    working and not working. Every pursuer in this game walks straight
    at what it wants, which is fine in rooms that are open and fine in
    rooms where the thing it wants is ten feet away. This arena is
    neither: it has lava veins and Astral cracks in it to begin with,
    and then it *tears* -- the rift takes a column of ground on every
    beat of the conversation and the cracks grow west with it, so a
    line that was open when Chuck walked in is a wall by the fourth
    exchange. A straight-line charge into that is a horde of orcs
    standing in a field, which is exactly the "attacking nothing"
    problem this whole change exists to fix, moved twenty tiles west.

    So: try the direct line; if it will not move, follow the obstacle,
    and keep following the same way round for a moment rather than
    reconsidering every frame, because reconsidering every frame is how
    a thing ends up vibrating in a corner. It is the oldest steering
    trick there is and it is all this needs -- these are orcs.
    """

    # Which way round it prefers once it has committed, and how long a
    # clear run has to be before it forgets. Sticky only in the *choice
    # of side*: the direct line is tried every single frame, so the
    # moment an opening appears the orc takes it instead of continuing
    # to trace the wall it was following.
    SLIDE_FORGET = 0.7
    # How much of the direct heading is kept while sliding. Without it
    # the orc circles the obstacle instead of working along it.
    SLIDE_DRIFT = 0.42
    # What counts as getting somewhere. Both are fractions of the step
    # it was trying to take, and the first is the whole reason this
    # works: `move_and_collide` resolves the axes separately, so a
    # diagonal charge into a wall still slides a fraction of a pixel
    # along it and still returns a new position. "Did it move?" is
    # therefore always yes. The question that separates walking from
    # grinding is "did it get closer?".
    CLOSER = 0.25
    ANYWHERE = 0.4

    def __init__(self, center_x: float, center_y: float,
                 target: "BattleActor") -> None:
        super().__init__(center_x, center_y, "orc")
        self.target = target
        self._sign = 0
        self._clear = 0.0

    def update(self, dt: float, _player=None) -> None:
        """Advance on the hero. The player argument is accepted and ignored.

        Taking it and doing nothing with it is deliberate: this sits in
        the same lists and the same loops as every other pursuer, and
        the one thing that is different about it belongs here rather
        than at every call site.
        """
        if self.tilemap is None:
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance <= 0.0:
            return
        ux, uy = dx / distance, dy / distance
        step = self.speed * dt

        # The direct line, first, every frame.
        landing, travelled, closed = self._probe(ux * step, uy * step)
        if travelled > step * self.ANYWHERE and closed > step * self.CLOSER:
            self._clear += dt
            if self._clear > self.SLIDE_FORGET:
                self._sign = 0
            self.x, self.y = landing
            self._face(ux, uy)
            return

        # Blocked. Follow the obstacle, the same way round as last time
        # if it is still working.
        self._clear = 0.0
        for sign in ((self._sign, -self._sign) if self._sign else (1, -1)):
            px = -uy * sign + ux * self.SLIDE_DRIFT
            py = ux * sign + uy * self.SLIDE_DRIFT
            length = math.hypot(px, py) or 1.0
            px, py = px / length, py / length
            landing, travelled, _closed = self._probe(px * step, py * step)
            if travelled > step * self.ANYWHERE:
                self._sign = sign
                self.x, self.y = landing
                self._face(px, py)
                return
        # Wedged both ways round. Forget the commitment so the next
        # frame is free to pick the other side.
        self._sign = 0

    def _probe(self, dx: float, dy: float):
        """Where a step would land, how far it goes, and how much nearer.

        Nothing is committed here. Trying a direction and then taking a
        different one has to leave the orc where it started, or a frame
        that considers three headings moves it along all three.
        """
        target = (self.target.center_x, self.target.center_y)
        before = math.dist((self.center_x, self.center_y), target)
        x, y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, self.tilemap,
            extra_solid_terrain=(collision.LARGE_ACTOR_PASSAGE_TERRAIN
                                 | collision.FALL_HAZARD_TERRAIN),
        )
        travelled = math.dist((x, y), (self.x, self.y))
        after = math.dist((x + self.width / 2, y + self.height / 2), target)
        return (x, y), travelled, before - after

    def _face(self, dx: float, dy: float) -> None:
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


class OrcHorde:
    """The stream itself: who is coming, from where, and how often.

    It owns no terrain and writes nothing, so a death in this room does
    not need it put back -- the room simply builds a new one, opening
    press and all, the same way it builds new battle cadences.
    """

    # The cap is what actually governs the size of it. The ring is far
    # enough out that most of the horde is in transit at any moment, so
    # in practice a new orc leaves the rim about when one dies at the
    # line, and the interval only sets how fast the pipeline fills.
    SPAWN_INTERVAL = 0.7
    MAX_ALIVE = 18
    FIRST_SPAWN = 1.4

    def __init__(self, tilemap: "TileMap", assets: "AssetManager | None",
                 *, fighter: "BattleActor", ranger: "BattleActor") -> None:
        self._tilemap = tilemap
        self._assets = assets
        self._fighter = fighter
        self._ranger = ranger
        self.orcs: list[HordeOrc] = []
        self._spawn_timer = self.FIRST_SPAWN
        self._next = 0
        self.spawned = 0
        self.killed = 0
        for cell in OPENING:
            self._spawn(cell)

    # ------------------------------------------------------------------
    # Spawning
    # ------------------------------------------------------------------
    def _hero_for(self, cell: tuple[int, int]) -> "BattleActor":
        """Whichever of the two it came in nearest.

        Chosen once and kept. The two of them are only six rows apart,
        so this splits the ring roughly north and south -- which is what
        makes the horde converge on the line instead of crossing over
        itself on the way there.
        """
        ts = config.TILE_SIZE
        x, y = (cell[0] + 0.5) * ts, (cell[1] + 0.5) * ts
        to_fighter = math.dist((x, y), (self._fighter.center_x,
                                        self._fighter.center_y))
        to_ranger = math.dist((x, y), (self._ranger.center_x,
                                       self._ranger.center_y))
        return self._fighter if to_fighter <= to_ranger else self._ranger

    def _spawn(self, cell: tuple[int, int]) -> HordeOrc:
        ts = config.TILE_SIZE
        orc = HordeOrc((cell[0] + 0.5) * ts, (cell[1] + 0.5) * ts,
                       self._hero_for(cell))
        orc.tilemap = self._tilemap
        if self._assets is not None:
            orc.load_sprites(self._assets)
        self.orcs.append(orc)
        self.spawned += 1
        return orc

    def update(self, dt: float, player_box=None) -> None:
        self._spawn_timer -= dt
        while self._spawn_timer <= 0.0:
            self._spawn_timer += self.SPAWN_INTERVAL
            if len(self.orcs) < self.MAX_ALIVE:
                self._spawn_next(player_box)
        for orc in self.orcs:
            orc.update(dt)
        self.orcs = [orc for orc in self.orcs if orc.alive]

    def _spawn_next(self, player_box=None) -> HordeOrc | None:
        """Take the next cell in the ring, skipping one Chuck is on.

        The ring is a long way from anywhere he has reason to be, so
        this almost never fires -- but an orc materialising on top of
        him is twenty Sanity he had no way to avoid, and "almost never"
        is not the standard the rest of this room is held to.
        """
        for _ in range(len(SPAWN_CELLS)):
            cell = SPAWN_CELLS[self._next % len(SPAWN_CELLS)]
            self._next += SPAWN_STRIDE
            if player_box is not None and self._occupied(cell, player_box):
                continue
            return self._spawn(cell)
        return None

    @staticmethod
    def _occupied(cell: tuple[int, int], player_box) -> bool:
        ts = config.TILE_SIZE
        return player_box.colliderect(
            (cell[0] * ts - ts, cell[1] * ts - ts, ts * 3, ts * 3))

    # ------------------------------------------------------------------
    # Dying
    # ------------------------------------------------------------------
    def nearest_to(self, x: float, y: float) -> HordeOrc | None:
        """The orc a hero would shoot: the closest one still standing."""
        if not self.orcs:
            return None
        return min(self.orcs,
                   key=lambda orc: math.dist((x, y),
                                             (orc.center_x, orc.center_y)))

    def cut_down(self, box) -> int:
        """Kill every orc inside a hitbox. One hit, however healthy.

        The heroes are not fighting these things the way Chuck fights
        anything -- an orc that takes eleven of his scratches takes one
        arrow or one sword stroke here, because these are the people who
        do this for a living and the room has to look like it.
        """
        killed = 0
        for orc in self.orcs:
            if orc.alive and box.colliderect(orc.hitbox):
                orc.alive = False
                killed += 1
        if killed:
            self.orcs = [orc for orc in self.orcs if orc.alive]
            self.killed += killed
        return killed

    def kill(self, orc: HordeOrc) -> bool:
        """One arrow, one orc. Used by the ranger's shots landing."""
        if not orc.alive:
            return False
        orc.alive = False
        self.orcs = [other for other in self.orcs if other.alive]
        self.killed += 1
        return True
