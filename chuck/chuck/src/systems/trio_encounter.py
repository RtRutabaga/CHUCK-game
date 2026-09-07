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
So Chuck's own tile is skipped and the heroes' footing is protected,
which leaves them standing on islands by the end -- which is the right
picture anyway.

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
)

# The first beat that costs ground. The early exchange is talk; from
# the midpoint on, the document wants the room getting worse.
FIRST_ADVANCE = 1
# How many columns of shore the rift takes each time.
ADVANCE_COLUMNS = 1
# Per-tile delay as the break spreads away from Chuck's row, so it
# arrives as a wave rather than as a whole column blinking out.
ADVANCE_STEP = config.BREACH_STEP
# ...and how many rows either side of him land at once, so it cannot be
# outrun along the edge.
ADVANCE_INSTANT = config.BREACH_INSTANT_RADIUS

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


class TrioEncounter:
    """The beat clock and the advancing rift, for one visit to the room."""

    def __init__(self, tilemap, protected: set[tuple[int, int]]) -> None:
        self._tilemap = tilemap
        self._protected = set(protected)
        self._elapsed = 0.0
        self._next = 0
        self._pending: list[list] = []          # [delay, col, row]
        self._restore: list[tuple[int, int, str]] = []
        self.flashes: list[list] = []           # [col, row, age]
        self.advances = 0

    # ------------------------------------------------------------------
    @property
    def beats_played(self) -> int:
        return self._next

    @property
    def finished(self) -> bool:
        """Every scripted beat has been spoken."""
        return self._next >= len(BEATS)

    def update(self, dt: float, player_tile: tuple[int, int] | None = None,
               player_hitbox=None) -> str | None:
        """Advance the clock. Returns a dialogue id when one is due."""
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
        if self._next > FIRST_ADVANCE and player_tile is not None:
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
            if player_hitbox is not None and cell.colliderect(player_hitbox):
                remaining.append(entry)  # never open under Chuck
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
