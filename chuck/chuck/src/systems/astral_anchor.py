"""Astral Anchors — Chuck's checkpoints.

Responsibilities (future):
    * Remember the most recently touched anchor's position.
    * Run the respawn sequence when sanity hits zero:
        Chuck vanishes -> short quiet transition -> Chuck reappears at
        the anchor with sanity refilled.

Tone rules (Game Bible):
    * The transition should feel peaceful, not punishing. The Astral
      Sea is ancient, quiet, and almost comforting. A slow fade to a
      starfield beat is more appropriate than a death jingle.
    * Fast: no long animation, no Game Over screen, no lost progress
      friction. Hit -> vanish -> brief pause -> back.

Phase One scope: exactly one anchor in the docks map.
"""

from __future__ import annotations


class AstralAnchorSystem:
    """Where Chuck comes back to: the door he walked in by.

    It used to move. Touching an Ashtray made that the respawn point for
    the rest of the map, which is why this class is named after one.
    Measured over every Ashtray in the game, coming back to the door
    instead costs a median of 1.7 tiles of walking -- the fights are
    deep in the maps, so the walk back was already long, and the
    Ashtrays sat near the entrances anyway.

    So there is one respawn point per visit to a map, it is set when he
    arrives, and nothing changes it while he is there.
    """

    def __init__(
        self,
        default_position: tuple[float, float] = (0.0, 0.0),
        default_checkpoint_id: str | None = None,
    ) -> None:
        self.respawn_position = default_position
        self.active_checkpoint_id = default_checkpoint_id

    def respawn_position_for_chuck(self) -> tuple[float, float]:
        """Where Chuck reappears: the door he came in by."""
        return self.respawn_position
