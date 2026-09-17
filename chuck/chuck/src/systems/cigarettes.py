"""The overall-game cigarette ledger — Chuck's coin counter.

Every cigarette Chuck has ever picked up, across the whole game: loose
cigarettes bank one each, a carton banks exactly
config.CARTON_CIGARETTE_COUNT. The count is continuous for the entire
run — cutscene handoffs and dev jumps never reset it; only NEW GAME
does (and CONTINUE restores the saved total).

Death rewinds it: whenever a respawn point is established (entering a
map) the ledger commits, and the quiet Astral
respawn rolls the total back to that committed value — whatever Chuck
gathered past the checkpoint is lost with him, like the run since a
save never happened. Displayed quietly in the HUD's top-right corner.
No spending exists yet — the ledger only accumulates.
"""

from __future__ import annotations


class CigaretteLedger:
    """A cigarette count with checkpoint commit/rollback semantics."""

    def __init__(self) -> None:
        self.total = 0
        self.checkpoint_total = 0

    def add(self, count: int) -> None:
        if count < 0:
            raise ValueError("the ledger only accumulates")
        self.total += count

    def commit(self) -> None:
        """Bank the current total as the respawn-point value."""
        self.checkpoint_total = self.total

    def rollback(self) -> None:
        """Death: return to the last committed value."""
        self.total = self.checkpoint_total

    def replace(self, total: int) -> None:
        """Set the absolute total (NEW GAME reset / CONTINUE restore)."""
        if total < 0:
            raise ValueError("a cigarette total cannot be negative")
        self.total = total
        self.checkpoint_total = total
