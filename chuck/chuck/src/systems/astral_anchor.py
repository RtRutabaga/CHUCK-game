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
    """Tracks the active local respawn point. Owned by the WorldScene."""

    def __init__(
        self,
        default_position: tuple[float, float] = (0.0, 0.0),
        default_checkpoint_id: str | None = None,
    ) -> None:
        # Where Chuck returns if he has never touched an anchor —
        # by default, where he woke up (Bobert's barrel).
        self.respawn_position = default_position
        self.active_checkpoint_id = default_checkpoint_id

    def activate(
        self,
        position: tuple[float, float],
        checkpoint_id: str | None = None,
    ) -> None:
        """Set a new active anchor (called when Chuck touches one).

        TODO: Small activation effect + sound, once effects exist.
        """
        self.respawn_position = position
        self.active_checkpoint_id = checkpoint_id

    def respawn_position_for_chuck(self) -> tuple[float, float]:
        """Return where Chuck should reappear."""
        return self.respawn_position

    # The AstralAnchor entity lives in src/entities/anchor.py; the
    # WorldScene calls activate() when Chuck touches one.
