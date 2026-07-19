"""Fall-zone rules, kept separate from scene choreography."""

from src.core import config


def fall_zone_kind(tilemap, player_box, airborne: bool) -> str | None:
    """Return the fall material under Chuck, or None while safely airborne."""
    if airborne:
        return None
    cx = player_box.x + player_box.width / 2
    cy = player_box.y + player_box.height / 2
    terrain = tilemap.terrain_at(
        int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE)
    )
    # Spike pits share the Astral fall exactly (session 124): lethal
    # underfoot, safe while airborne, same quiet vanish and return.
    return {"V": "astral", "s": "sky", "♠": "astral"}.get(terrain)


def touches_astral_fall_zone(tilemap, player_box, airborne: bool) -> bool:
    """True when Chuck's footprint center is over Astral material on foot."""
    return fall_zone_kind(tilemap, player_box, airborne) == "astral"
