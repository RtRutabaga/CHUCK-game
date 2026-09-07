"""The final encounter's clock: what the heroes say, and when.

The phase document scripts five conversations across this fight and
says two things about how they should play. They happen automatically,
and gameplay keeps moving between them. So this owns a timer rather
than a trigger volume: Chuck survives for a stretch, the camera cuts to
the three of them, they say the next thing, and he goes back to
surviving. He is never asked to walk anywhere to advance it, because
walking anywhere in that room is not something he is reliably able to
do.

The other instruction is that the world should get worse as it goes --
"the environment should become increasingly unstable around Chuck" --
and the honest reading of that here is that the rift wins ground. From
the midpoint on, every beat takes another column of the arena: the
floor immediately west of the tear breaks through to Astral Sea, the
same way the sanctum's floor does when the Sea seals that room. It is
the identical mechanism, applied to a moving edge instead of a fixed
band, and it means the space Chuck has to dodge in shrinks each time
the heroes speak.

What it must never do is take the ground out from under him, or from
under the three of them: they are *holding* this, and a hero swallowed
by the thing he is closing would read as a bug rather than as a cost.
So Chuck's own tile is skipped and the heroes' footing is protected --
each one's whole 3x3, so that what is left when the tear stops moving
is a shelf the three of them are standing on rather than three separate
islands. That is the right picture anyway, and it is also the only one
the horde pressing them can walk up to; see `footing` for why that
distinction turned out to matter.

And when the last thing has been said, the collision itself arrives:
the desert is overwhelmed by fragments of everywhere, in large sections
that change faster and faster. That is the document's own description
and it comes with the document's own warning attached -- readability
must not be spent on spectacle. So the churn only ever writes *floors*.
Nothing it does can kill Chuck, block him, or take a route away; what
changes is what he is standing on, several tiles at a time, quicker
every few seconds. The arena's rule was that the worlds are underfoot
and the danger is above them, and the ending is that rule at its limit.

Dying resets all of it. The room heals, the clock goes back to zero and
the conversation starts again from the beat after the entrance, the
same way the sanctum's breach re-arms.
"""

from __future__ import annotations

import math

from src.core import config


# How long Chuck survives between one conversation and the next, and
# which conversation it is. The document's own order: the early
# exchange, the midpoint, the wizard asking for another minute, and
# then finding it.
#
# Long enough to be a stretch of play rather than a pause between
# cutscenes -- the instruction is to keep gameplay moving between
# dialogue moments, and four beats back to back would make the room a
# conversation with fighting in the gaps rather than the other way
# round.
BEATS: tuple[tuple[float, str], ...] = (
    (15.0, "trio_early"),
    (17.0, "trio_midpoint"),
    (17.0, "trio_climax"),
    (13.0, "trio_found_it"),
    # ...and then it works. These two are the resolution: the heroes
    # realising it is taking, and then realising what else is caught in
    # it. The last line of the second one is the trigger for everything
    # after this map.
    #
    # They are more than twice as long as the four before them, and the
    # gap is the point. Up to here the room is a conversation with
    # fighting in the gaps; from here it is a fight with two lines in
    # it. The dragon arrives on the beat before these, and at the old
    # lengths it got two crossings and no time on the ground at all --
    # the whole back half of the encounter went past before its own
    # hazard had finished introducing itself.
    (40.0, "trio_resolution"),
    (32.0, "trio_caught"),
)

# The first beat that costs ground. The early exchange is talk; from
# the midpoint on, the document wants the room getting worse.
FIRST_ADVANCE = 1
# ...and the beat it stops costing ground at, which is the one where
# the collision arrives. From there the rift is being *closed*: taking
# more of the arena after "It's working" would be the room saying the
# opposite of what the heroes are saying over the top of it.
CHURN_FROM = 4
# How many columns of shore the rift takes each time.
ADVANCE_COLUMNS = 1
# Per-tile delay as the break spreads away from Chuck's row, so it
# arrives as a wave rather than as a whole column blinking out.
ADVANCE_STEP = config.BREACH_STEP
# ...and how many rows either side of him land at once, so it cannot be
# outrun along the edge.
ADVANCE_INSTANT = config.BREACH_INSTANT_RADIUS

# The other front, and the one that decides where the fight happens.
#
# Chuck arrives on the west rim and everything worth watching is
# twenty-five tiles east of him, which means the safest thing he can do
# is stand in the doorway and let the encounter happen at a distance.
# That is a room with a corner in it, and a room with a corner in it is
# not an encounter -- it is a cutscene with a survival timer.
#
# So the Astral comes in behind him as well. It starts after the first
# exchange, takes a column every couple of seconds, and stops well
# short of the heroes: what is left when it is done is a band about a
# screen and a half across with the trio at one end of it and nothing
# but Sea at the other. He cannot retreat out of the fight because
# there is no longer anywhere behind the fight to retreat to.
#
# It is the sanctum breach's fiction, said again: the way out closes
# behind him and there is no walking away. The difference is that this
# one keeps coming.
ENCROACH_FROM = 1           # the beat it starts after -- the rift's own
ENCROACH_START = 1          # the first column it takes, inside the rim
ENCROACH_INTERVAL = 1.8     # seconds per column
# ...and where it stops. Set by the horde rather than by taste: the
# westmost cell orcs come in from is column 28, and a spawn ring inside
# the Sea would be a horde that drowned on the way to the fight.
ENCROACH_LIMIT = 26
# How far past a tile the front has to have got before it will open
# that tile under Chuck's feet.
#
# The rule everywhere else in this room is that the Sea never opens
# where he is standing -- it queues the tile and takes it when he moves,
# so the front pushes him rather than dropping him. That is right for
# the rift, which comes at him from in front, and it strands him when it
# comes from behind: a player who plants himself in the doorway and
# ignores forty-five seconds of visible Sea ends up on a single tile
# with the fight happening thirty tiles away and nothing to do but wait
# for the dragon to find him.
#
# So the front gets to finish. It goes round him, gives him a few
# seconds, and then the Sea closes over the spot as well. Standing still
# is a death rather than a stalemate, which is both the better failure
# and the honest one -- the west end of the arena is *gone*, and he was
# standing in it.
ENCROACH_GRACE = 3


def encroach_lag(row: int) -> int:
    """How many columns behind the front this row is.

    Taking a whole column at a time gave a perfectly straight vertical
    edge sweeping the map, and a perfectly straight edge does not read
    as the Astral Sea -- it reads as the end of the level. The rift on
    the other side is ragged because it follows a shore that was drawn
    that way; this one has to be given a shore.

    Two sines rather than anything modular. A lag of `row % n` is a
    repeating sawtooth, which is the same problem in a different
    costume: an edge with a period in it is still an edge somebody
    drew.
    """
    wobble = math.sin(row * 0.47) + 0.55 * math.sin(row * 1.13 + 1.7)
    return max(0, min(4, int(round(2.0 + 1.7 * wobble))))

# Ground the rift is allowed to take. Everything else on the map --
# the rim, a marker's tile, anything a later edit adds -- stays.
EDIBLE = frozenset({".", ",", "⟁", "⌖", "=", "≡", "ᛗ", "ᛟ", "·",
                    "⌼", "⌽", "❄", "≋"})


# The floors the collision can write. Every one of them is walkable,
# and that is the whole safety argument: a churn that could write lava
# or Sea would be a room where the ground kills you at random, which is
# not survivable and not what the document is asking for.
CHURN_FLOORS = (".", "⌖", "=", "ᛗ", "ᛟ", "·", "⌼", "⌽", "❄")

# How often a section changes, at the start and at the end, and how
# long it takes to get from one to the other. It builds toward the
# heroes succeeding, so it accelerates; the floor is a floor because
# below it the map stops reading as a place and starts reading as
# static.
CHURN_FIRST = 2.2
CHURN_FASTEST = 0.55
CHURN_RAMP = 40.0

# How big a section is. Large, because the document says large: a churn
# that repaints one tile at a time is a shimmer, and what is wanted is
# whole pieces of somewhere else arriving.
CHURN_MIN = (9, 7)
CHURN_MAX = (18, 13)
# How long the arriving section is outlined, so the eye can catch it.
CHURN_FLASH = 0.35


class WorldChurn:
    """Fragments of everywhere, arriving in large sections, faster.

    Deliberately incapable of hurting anyone. It picks a rectangle,
    repaints every walkable floor tile in it to one world's floor, and
    leaves everything else exactly as it was -- the rift, the lava
    veins, the heroes' footing, anything a marker stands on. So the
    ground under Chuck changes constantly and the map he is solving
    never does.

    Sections are chosen from a fixed sequence rather than at random.
    The map is generated once and read many times, and a sequence that
    differs per run is a sequence nobody can tell is working.
    """

    def __init__(self, tilemap, protected: set[tuple[int, int]]) -> None:
        self._tilemap = tilemap
        self._protected = set(protected)
        self._restore: dict[tuple[int, int], str] = {}
        self._elapsed = 0.0
        self._timer = CHURN_FIRST
        self.sections = 0
        self.flashes: list[list] = []       # [left, top, w, h, age]

    @property
    def interval(self) -> float:
        """Seconds between sections, shrinking as the heroes close in."""
        along = min(1.0, self._elapsed / CHURN_RAMP)
        return CHURN_FIRST + (CHURN_FASTEST - CHURN_FIRST) * along

    def update(self, dt: float) -> int:
        """Run the collision. Returns how many tiles changed this frame."""
        self._elapsed += dt
        for flash in self.flashes:
            flash[4] += dt
        self.flashes = [f for f in self.flashes if f[4] < CHURN_FLASH]
        self._timer -= dt
        if self._timer > 0.0:
            return 0
        self._timer += self.interval
        return self._arrive()

    def _arrive(self) -> int:
        """One section of somewhere else lands on the arena."""
        width, height = self._tilemap.width_tiles, self._tilemap.height_tiles
        index = self.sections
        self.sections += 1
        # A fixed walk over the map rather than a random one, so the
        # sequence is the same every time the encounter is played.
        span_w = CHURN_MIN[0] + (index * 5) % (CHURN_MAX[0] - CHURN_MIN[0])
        span_h = CHURN_MIN[1] + (index * 3) % (CHURN_MAX[1] - CHURN_MIN[1])
        left = 1 + (index * 13) % max(1, width - span_w - 2)
        top = 1 + (index * 7) % max(1, height - span_h - 2)
        floor = CHURN_FLOORS[index % len(CHURN_FLOORS)]

        changed = 0
        for row in range(top, min(height - 1, top + span_h)):
            for col in range(left, min(width - 1, left + span_w)):
                if (col, row) in self._protected:
                    continue
                here = self._tilemap.terrain_at(col, row)
                if here not in CHURN_FLOORS or here == floor:
                    continue
                self._restore.setdefault((col, row), here)
                self._tilemap.set_terrain(col, row, floor)
                changed += 1
        if changed:
            self.flashes.append([left, top, span_w, span_h, 0.0])
        return changed

    def restore(self) -> None:
        for (col, row), char in self._restore.items():
            self._tilemap.set_terrain(col, row, char)
        self._restore = {}
        self.flashes = []
        self._elapsed = 0.0
        self._timer = CHURN_FIRST
        self.sections = 0

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """An outline round each arriving section, for a third of a second.

        Only an outline. Filled, it washed the section it was announcing
        and the thing a player most needs to keep track of in this room
        is where their own feet are.
        """
        import pygame

        ox, oy = camera_offset
        ts = config.TILE_SIZE
        for left, top, span_w, span_h, age in self.flashes:
            fade = 1.0 - age / CHURN_FLASH
            colour = (round(170 + 70 * fade), round(180 + 60 * fade), 255)
            pygame.draw.rect(
                surface, colour,
                (left * ts - ox, top * ts - oy, span_w * ts, span_h * ts),
                max(1, round(3 * fade)))


def footing(cells: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """A hero's tile and the eight around it: the shelf he holds.

    Protecting only the tile somebody is standing on was enough while
    the only thing that had to survive the rift was the tableau. It
    stopped being enough the moment a horde had to *reach* them: the
    edge is ragged, so the rows either side of a hero get taken while
    his own does not, and what is left after four beats is three people
    on single tiles at the end of spurs one tile wide. Nothing with a
    body can walk down a corridor one tile wide, so the fighter's sword
    quietly stopped being able to hit anything and the horde piled up on
    the far bank instead -- which is the "attacking nothing" problem
    again, in the orcs' clothes this time.

    So each of them keeps the step around him as well. The generator
    already clears that 3x3 to plain desert, so this protects a shape
    that was authored rather than inventing one; the rift stops
    advancing in the three rows the heroes are standing in and keeps
    taking every other row, which leaves them on a shelf jutting into
    the tear. That is a better picture than three islands anyway -- they
    are *holding* this, and holding it needs somewhere to stand.
    """
    return {
        (col + dx, row + dy)
        for (col, row) in cells
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
    }


class TrioEncounter:
    """The beat clock and the advancing rift, for one visit to the room."""

    def __init__(self, tilemap, protected: set[tuple[int, int]]) -> None:
        self._tilemap = tilemap
        # The shelf, not the tile: the horde has to be able to reach
        # them, and a hero on a single tile is a hero nothing with a
        # body can walk up to. See `footing`.
        self._protected = footing(protected)
        self._elapsed = 0.0
        self._next = 0
        self._pending: list[list] = []          # [delay, col, row]
        self._restore: list[tuple[int, int, str]] = []
        self.flashes: list[list] = []           # [col, row, age]
        self.advances = 0
        # The western front: the last column it has taken, and the
        # clock to the next one.
        self.encroached = ENCROACH_START - 1
        self._encroach_t = 0.0

    # ------------------------------------------------------------------
    @property
    def beats_played(self) -> int:
        return self._next

    @property
    def finished(self) -> bool:
        """Every scripted beat has been spoken, resolution included.

        The last of them is the trigger: when this goes true the phase
        is over and Chuck is on his way back to Waterdeep.
        """
        return self._next >= len(BEATS)

    @property
    def collided(self) -> bool:
        """The wizard has found it: the worlds start arriving."""
        return self._next >= CHURN_FROM

    @property
    def closing_in(self) -> bool:
        """Is the Sea behind him still coming?"""
        return (self._next >= ENCROACH_FROM
                and self.encroached < ENCROACH_LIMIT)

    def update(self, dt: float, player_tile: tuple[int, int] | None = None,
               player_hitbox=None) -> str | None:
        """Advance the clock. Returns a dialogue id when one is due."""
        # The western front runs on its own clock rather than on the
        # beats. The rift takes ground when the heroes speak, because
        # that is the room answering them; this is just the way out
        # going, and it should go steadily whether or not anybody is
        # saying anything.
        if self.closing_in and player_tile is not None:
            self._encroach_t += dt
            while (self._encroach_t >= ENCROACH_INTERVAL
                   and self.encroached < ENCROACH_LIMIT):
                self._encroach_t -= ENCROACH_INTERVAL
                self.encroach(player_tile)
        self._break_through(dt, player_hitbox)
        for flash in self.flashes:
            flash[2] += dt
        self.flashes = [f for f in self.flashes
                        if f[2] < config.BREACH_FLASH]
        if self.finished:
            return None
        self._elapsed += dt
        delay, dialogue_id = BEATS[self._next]
        if self._elapsed < delay:
            return None
        self._elapsed = 0.0
        self._next += 1
        if (FIRST_ADVANCE < self._next <= CHURN_FROM
                and player_tile is not None):
            self.advance(player_tile)
        return dialogue_id

    # ------------------------------------------------------------------
    def advance(self, player_tile: tuple[int, int]) -> int:
        """Take another column of shore. Returns how many tiles are queued.

        The edge is ragged, so what is taken is found rather than
        computed: for each row, walk west from the map's east side to
        the first tile that is not already Sea, and queue that one. A
        column index would have cut a straight line down a torn edge.
        """
        _col, player_row = player_tile
        queued = 0
        for _ in range(ADVANCE_COLUMNS):
            for row in range(self._tilemap.height_tiles):
                shore = self._shore(row)
                if shore is None:
                    continue
                spread = max(0, abs(row - player_row) - ADVANCE_INSTANT)
                self._pending.append([spread * ADVANCE_STEP, shore, row])
                queued += 1
        self._pending.sort()
        self.advances += 1
        return queued

    def encroach(self, player_tile: tuple[int, int]) -> int:
        """Take the next column in from the west. Returns tiles queued.

        Queued rather than written, through the same delayed break the
        rift uses -- which is also the safety valve. `_break_through`
        refuses to open a tile Chuck is standing on and puts it back in
        the queue, so the front cannot drop him into the Sea. It pushes
        him instead, which is the entire point of it.
        """
        _col, player_row = player_tile
        self.encroached += 1
        queued = 0
        for row in range(self._tilemap.height_tiles):
            # Each row lags the front by its own fixed amount, so the
            # edge keeps a ragged shape as it travels instead of being
            # a ruled line crossing the map.
            col = self.encroached - encroach_lag(row)
            if col < ENCROACH_START:
                continue
            if (col, row) in self._protected:
                continue
            if self._tilemap.terrain_at(col, row) not in EDIBLE:
                continue
            spread = max(0, abs(row - player_row) - ADVANCE_INSTANT)
            self._pending.append([spread * ADVANCE_STEP, col, row])
            queued += 1
        self._pending.sort()
        return queued

    def _shore(self, row: int) -> int | None:
        """The westmost tile of the rift's edge in this row, if any."""
        width = self._tilemap.width_tiles
        seen_sea = False
        for col in range(width - 1, -1, -1):
            char = self._tilemap.terrain_at(col, row)
            if char == "V":
                seen_sea = True
                continue
            if not seen_sea:
                continue        # rim, or ground east of nothing
            if (col, row) in self._protected or char not in EDIBLE:
                return None     # the heroes' footing, and anything else
            if any(entry[1] == col and entry[2] == row
                   for entry in self._pending):
                return None
            return col
        return None

    def _break_through(self, dt: float, player_hitbox) -> None:
        if not self._pending:
            return
        import pygame

        remaining = []
        ts = config.TILE_SIZE
        for entry in self._pending:
            entry[0] -= dt
            _delay, col, row = entry
            if entry[0] > 0.0:
                remaining.append(entry)
                continue
            cell = pygame.Rect(col * ts, row * ts, ts, ts)
            if (player_hitbox is not None and cell.colliderect(player_hitbox)
                    and self.encroached - col < ENCROACH_GRACE):
                # Never open under Chuck -- while the front is still
                # anywhere near. Once it is well past this column it
                # takes the ground he is standing on too; see
                # ENCROACH_GRACE. The rift never meets this second test,
                # because its columns are at the far end of the map and
                # the western front stops less than half way.
                remaining.append(entry)
                continue
            old = self._tilemap.set_terrain(col, row, "V")
            self._restore.append((col, row, old))
            self.flashes.append([col, row, 0.0])
        self._pending = remaining

    def restore(self) -> None:
        """Heal the arena and put the conversation back to the start."""
        for col, row, char in reversed(self._restore):
            self._tilemap.set_terrain(col, row, char)
        self._restore = []
        self._pending = []
        self.flashes = []
        self._elapsed = 0.0
        self._next = 0
        self.advances = 0
        self.encroached = ENCROACH_START - 1
        self._encroach_t = 0.0

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """The same flash the sanctum's breach uses, for the same event."""
        import pygame

        ox, oy = camera_offset
        ts = config.TILE_SIZE
        for col, row, age in self.flashes:
            fade = 1.0 - age / config.BREACH_FLASH
            pad = round(3 * (1.0 - fade))
            colour = (round(150 + 90 * fade), round(160 + 86 * fade), 255)
            pygame.draw.rect(
                surface, colour,
                (col * ts + pad - ox, row * ts + pad - oy,
                 ts - 2 * pad, ts - 2 * pad))
