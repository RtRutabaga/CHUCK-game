"""Where Chuck comes back to.

One respawn point per visit to a map: the door he walked in by. It is
set when he arrives and nothing moves it while he is in there.

It used to move. Touching an Ashtray made that spot the respawn point
for the rest of the map, and the Ashtrays are gone -- the save is a
code written from the menu now, and the door is both the save point and
the place he reappears. Measured over every Ashtray there was, coming
back to the door instead costs a median of 1.7 tiles of walking: the
fights are deep in the maps, so the walk back was already long, and the
Ashtrays sat near the entrances anyway.

Tone rules (Game Bible), which have not changed with any of it:
    * The transition should feel peaceful, not punishing. The Astral
      Sea is ancient, quiet, and almost comforting. A slow fade to a
      starfield beat is more appropriate than a death jingle.
    * Fast: no long animation, no Game Over screen, no lost progress
      friction. Hit -> vanish -> brief pause -> back.
"""

from __future__ import annotations


class RespawnPoint:
    """The door Chuck came in by, held for as long as he is in the map."""

    def __init__(
        self,
        position: tuple[float, float] = (0.0, 0.0),
        checkpoint_id: str | None = None,
    ) -> None:
        self.position = position
        self.checkpoint_id = checkpoint_id

    def position_for_chuck(self) -> tuple[float, float]:
        """Where Chuck reappears: the door he came in by."""
        return self.position
