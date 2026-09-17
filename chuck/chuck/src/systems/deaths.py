"""How many times Chuck has died this playthrough.

A tally, not a ledger. The cigarette count rewinds on death because
what Chuck gathered past the checkpoint is lost with him; a death is
the one thing that cannot be lost that way, so this only ever goes up.
NEW GAME zeroes it and CONTINUE restores the saved value, exactly like
the cigarettes -- which also means deaths since the last save are not
on disk yet, the same as everything else since the last save.

Two kinds of death count. The ordinary one, when Sanity runs out or
Chuck drops into the Astral and quietly stops being there. And the
three cutscenes where the same thing happens to him on screen -- the
fall to Chult, the fall into Hell, and the landing in the modern city
-- each of which plays that exact vanish and return. Cutscenes where he
survives, which is most of them, count nothing.
"""

from __future__ import annotations


class DeathCounter:
    """A count of Chuck's deaths across the whole run."""

    def __init__(self) -> None:
        self.total = 0

    def record(self) -> None:
        self.total += 1

    def replace(self, total: int) -> None:
        """Set the absolute total (NEW GAME reset / CONTINUE restore)."""
        if total < 0:
            raise ValueError("a death count cannot be negative")
        self.total = total
