"""Fall-zone rules, kept separate from scene choreography."""

from src.core import config


def touches_astral_fall_zone(tilemap, player_box, airborne: bool) -> bool:
    """True when Chuck's footprint center is over Astral material on foot."""
    if airborne:
        return False
    cx = player_box.x + player_box.width / 2
    cy = player_box.y + player_box.height / 2
    return tilemap.terrain_at(
        int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE)
    ) == "V"
