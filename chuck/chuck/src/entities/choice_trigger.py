"""Invisible map-authored interaction zones for environmental choices."""

from __future__ import annotations

from src.core import config


_TRIGGER_TILES = {
    "sewer_exit": (3, 1),
    "crevice": (2, 2),
    # A shallow base-only trigger: Chuck gets close enough to see the whole
    # stair before the climb prompt takes over the screen.
    "cloud_staircase": (2, 1),
    "zephyros_rope": (2, 1),
    "city_sewer_entrance": (4, 2),
    # Narrow: the climb prompt should fire at the ladder, not across
    # the whole chamber floor in front of it.
    "city_sewer_ladder": (2, 2),
}

# Choices that pop by simply walking into the zone — no interact press.
_WALK_TRIGGERS = {
    "crevice", "cloud_staircase", "zephyros_rope",
    "city_sewer_entrance", "city_sewer_ladder",
}


class ChoiceTrigger:
    """A non-drawing interaction target centered on a map marker."""

    dialogue_id = None

    def __init__(self, center_x: float, center_y: float, choice_id: str) -> None:
        if choice_id not in _TRIGGER_TILES:
            raise ValueError(f"Unknown choice trigger {choice_id!r}")
        width_tiles, height_tiles = _TRIGGER_TILES[choice_id]
        self.choice_id = choice_id
        self.walk_triggered = choice_id in _WALK_TRIGGERS
        self.width = width_tiles * config.TILE_SIZE
        self.height = height_tiles * config.TILE_SIZE
        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """Cover the authored feature, padded like props and NPCs."""
        pad = 3
        return (
            int(self.x) - pad,
            int(self.y) - pad,
            self.width + 2 * pad,
            self.height + 2 * pad,
        )
