"""Standing props — barrels and crates that Chuck walks behind.

A Prop is a drawable, not a full Entity: it never updates, and its
collision is the solid tile beneath it (the TileMap owns that). A few
props respond to the interact key with a single line (PROP_DIALOGUE):
Bobert snores; the sign says what signs say. He still never wakes,
never gets a name on screen, never becomes a character. Its
job is purely visual: render taller than its tile, anchored at the
tile's bottom edge, and participate in the y-sorted draw so characters
pass in front of and behind it correctly.

Scale note (Game Bible): a barrel is 19px to Chuck's 14. To Chuck,
standing at a barrel is standing at a building. Good.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config

if TYPE_CHECKING:
    from src.core.assets import AssetManager

_SPRITES = {
    "barrel": "objects/barrel.png",
    "crate": "objects/crate.png",
    "bobert_barrel": "objects/bobert_barrel.png",
    "herod_sign": "objects/herod_sign.png",
    "tavern_door": "objects/tavern_door.png",
    "tavern_open": "objects/tavern_open.png",
    "tavern_table": "objects/tavern_table.png",
    "tavern_chair": "objects/tavern_chair.png",
    "bar_counter": "objects/bar_counter.png",
    "tavern_hearth": "objects/tavern_hearth.png",
    "cheese": "objects/cheese.png",
    "pantry_door": "objects/pantry_door.png",
    "pantry_open": "objects/pantry_open.png",
    "pantry_shelf": "objects/pantry_shelf.png",
    "grain_sack": "objects/grain_sack.png",
    "chimney": "objects/chimney.png",
    "sewer_grate": "objects/sewer_grate.png",
    "house_door": "objects/house_door.png",
    "stall_post": "objects/stall_post.png",
    "stall_table": "objects/stall_table.png",
    "crate_green": "objects/crate_green.png",
    "crate_red": "objects/crate_red.png",
    "crate_orange": "objects/crate_orange.png",
    "jungle_tree": (
        "objects/jungle_tree_1.png",
        "objects/jungle_tree_2.png",
        "objects/jungle_tree_3.png",
    ),
    "jungle_shrub": (
        "objects/jungle_shrub_1.png",
        "objects/jungle_shrub_2.png",
        "objects/jungle_shrub_3.png",
    ),
    "sailing_cog": "objects/sailing_cog.png",
}

# Props that respond to the interact key with a line of dialogue
# (ids live in data/dialogue/). Everything else stays mute scenery.
PROP_DIALOGUE = {
    "bobert_barrel": "bobert_sleeping",  # he does not wake up
    "herod_sign": "herod_sign",
    "house_door": "closed_door",
    "cheese": "cheese",
}

# Props that ask a question instead of making a statement (ids live in
# data/choices/). A prop has a line or a choice, never both.
PROP_CHOICE = {
    "sewer_grate": "sewer_grate",
}


class Prop:
    """One standing object on a tile."""

    def __init__(self, kind: str, col: int, row: int,
                 assets: "AssetManager") -> None:
        if kind not in _SPRITES:
            raise ValueError(f"Unknown prop kind {kind!r}")
        self.kind = kind
        ts = config.TILE_SIZE
        sprite = _SPRITES[kind]
        if isinstance(sprite, tuple):
            # Stable spatial variation: authored trees keep their silhouette
            # between runs without requiring three separate map characters.
            sprite = sprite[(col * 31 + row * 17) % len(sprite)]
        self._image = assets.image(sprite)
        w, h = self._image.get_size()
        # Horizontally centered on the tile, bottom edges aligned.
        self._draw_x = col * ts + (ts - w) // 2
        self._draw_y = (row + 1) * ts - h
        self._bottom = (row + 1) * ts
        self._size = (w, h)
        self.dialogue_id = PROP_DIALOGUE.get(kind)
        self.choice_id = PROP_CHOICE.get(kind)
        if self.dialogue_id and self.choice_id:
            raise ValueError(f"{kind}: a prop has a line OR a choice, not both")

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """(x, y, w, h) of the interactable area: the visible sprite,
        slightly padded — same convention as NPCs. Pure math."""
        pad = 3
        w, h = self._size
        return (self._draw_x - pad, self._draw_y - pad,
                w + 2 * pad, h + 2 * pad)

    @property
    def sort_y(self) -> float:
        """Depth key: the tile's bottom edge (same rule as entity feet)."""
        return float(self._bottom)

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        surface.blit(self._image, (self._draw_x - ox, self._draw_y - oy))
