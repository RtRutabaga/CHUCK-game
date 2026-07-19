"""The overall-game cigarette ledger — Chuck's coin counter.

Every cigarette Chuck has ever picked up, across the whole game: loose
cigarettes bank one each, a carton banks exactly
config.CARTON_CIGARETTE_COUNT (the contract carried since session 110).
The total lives on Game (so it survives map walks and Astral respawns,
like coins surviving a lost life), persists through the save slot, and
resets only with NEW GAME. Displayed quietly in the HUD's top-right
corner. No spending exists yet — the ledger only accumulates.
"""

from __future__ import annotations


class CigaretteLedger:
    """A monotonically growing count of cigarettes collected."""

    def __init__(self) -> None:
        self.total = 0

    def add(self, count: int) -> None:
        if count < 0:
            raise ValueError("the ledger only accumulates")
        self.total += count

    def replace(self, total: int) -> None:
        """Set the absolute total (NEW GAME reset / CONTINUE restore)."""
        if total < 0:
            raise ValueError("a cigarette total cannot be negative")
        self.total = total
