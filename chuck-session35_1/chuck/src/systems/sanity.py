"""Sanity — Chuck's version of health (Game Bible core mechanic).

Responsibilities (future):
    * Track current/max sanity.
    * Lose sanity when Chuck takes damage; restore it from cigarettes.
    * Announce (via callback or event) when sanity reaches zero so the
      WorldScene can run the quiet disappear -> Astral Anchor respawn.

Tone rules that shape implementation (Game Bible):
    * Reaching zero is NOT a failure state. No game-over screen, no
      dramatic animation. Chuck quietly disappears and returns at the
      most recent Astral Anchor. Death is an accepted part of his
      existence — the system should treat it matter-of-factly.
"""

from __future__ import annotations

from typing import Callable

from src.core import config


class SanitySystem:
    """Tracks Chuck's sanity. Owned by the WorldScene."""

    def __init__(
        self,
        on_depleted: Callable[[], None] | None = None,
        start: int | None = None,
    ) -> None:
        self.maximum = config.SANITY_MAX
        self.current = config.SANITY_START if start is None else start
        self._on_depleted = on_depleted
        self._hurt_cooldown = 0.0

    @property
    def fraction(self) -> float:
        """Current sanity as 0.0..1.0 (what the HUD meter shows)."""
        return self.current / self.maximum

    def update(self, dt: float) -> None:
        """Tick the invulnerability window. Call once per frame."""
        if self._hurt_cooldown > 0.0:
            self._hurt_cooldown = max(0.0, self._hurt_cooldown - dt)

    @property
    def is_invulnerable(self) -> bool:
        """True during the brief window after a hit."""
        return self._hurt_cooldown > 0.0

    def damage(self, amount: int) -> bool:
        """Reduce sanity, respecting invulnerability frames.

        Returns True if the hit landed (so the caller can trigger
        feedback like Chuck's blink). At zero, fires the depletion hook.
        """
        if self.is_invulnerable:
            return False
        self.current = max(0, self.current - amount)
        self._hurt_cooldown = config.HURT_COOLDOWN
        if self.current == 0 and self._on_depleted:
            self._on_depleted()
        return True

    def restore(self, amount: int) -> None:
        """Increase sanity, clamping at the maximum."""
        self.current = min(self.maximum, self.current + amount)

    def refill(self) -> None:
        """Reset to full — used after respawning at an Astral Anchor."""
        self.current = self.maximum
