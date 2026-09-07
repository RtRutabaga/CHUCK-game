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
