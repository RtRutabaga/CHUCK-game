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
    "ship_hammock": "objects/ship_hammock.png",
    "ship_captain_bed": "objects/ship_captain_bed.png",
    "ship_captain_rug": "objects/ship_captain_rug.png",
    "ship_round_table": "objects/ship_round_table.png",
    "ship_mast_sail": "objects/ship_mast_sail.png",
    "ship_helm": "objects/ship_helm.png",
    "ship_bowsprit": "objects/ship_bowsprit.png",
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
    "skull_stake": "objects/skull_stake.png",
    "temple_arch_ns": "objects/temple_arch_ns.png",
    "temple_arch_ew": "objects/temple_arch_ew.png",
    "temple_gate": "objects/temple_gate.png",
    "temple_skull": "objects/temple_skull.png",
    "temple_monument": (
        "objects/temple_monument_1.png",
        "objects/temple_monument_2.png",
    ),
    "temple_serpent_monument": (
        "objects/temple_serpent_monument_1.png",
        "objects/temple_serpent_monument_2.png",
    ),
    # Temple interior dressing (mute, y-sorted; the temple's version of
    # the docks' stall and the jungle's trees). Tuples vary by position.
    "temple_idol": (
        "objects/temple_idol_1.png",
        "objects/temple_idol_2.png",
    ),
    "temple_stela": (
        "objects/temple_stela_1.png",
        "objects/temple_stela_2.png",
    ),
    "temple_urn": (
        "objects/temple_urn_1.png",
        "objects/temple_urn_2.png",
        "objects/temple_urn_3.png",
    ),
    "temple_column": (
        "objects/temple_column_1.png",
        "objects/temple_column_2.png",
    ),
    "temple_rubble_block": tuple(
        f"objects/temple_rubble_block_{i + 1}.png" for i in range(12)
    ),
    "phlegethos_statue": (
        "objects/phlegethos_statue_1.png",
        "objects/phlegethos_statue_2.png",
    ),
    "phlegethos_rubble": tuple(
        f"objects/phlegethos_rubble_{i + 1}.png" for i in range(10)
    ),
    "phlegethos_lava_fall": "objects/phlegethos_lava_fall.png",
    # Chult's rounded tree/shrub silhouettes, washed with a subtle violet
    # sheen, plus one deliberately ordinary oak so the region reads as a
    # wood rather than a field of blocks (Phase 9 vegetation pass).
    "feywild_grove_tree": (
        "objects/feywild_grove_tree_1.png",
        "objects/feywild_grove_tree_2.png",
        "objects/feywild_grove_tree_3.png",
    ),
    "feywild_shrub": (
        "objects/feywild_shrub_1.png",
        "objects/feywild_shrub_2.png",
        "objects/feywild_shrub_3.png",
    ),
    "feywild_oak": (
        "objects/feywild_oak_1.png",
        "objects/feywild_oak_2.png",
        "objects/feywild_oak_3.png",
    ),
    # The redcap camp's gear, all of it gnome-sized and therefore enormous
    # next to Chuck: kicked-off boots, a cooking pot, a planted sickle he
    # can walk under, and crude hide shelters.
    "redcap_boot": (
        "objects/redcap_boot_1.png",
        "objects/redcap_boot_2.png",
        "objects/redcap_boot_3.png",
    ),
    "redcap_shelter": (
        "objects/redcap_shelter_1.png",
        "objects/redcap_shelter_2.png",
    ),
    "redcap_cauldron": "objects/redcap_cauldron.png",
    "redcap_sickle": "objects/redcap_sickle.png",
    "feywild_tree": (
        "objects/feywild_tree_1.png",
        "objects/feywild_tree_2.png",
        "objects/feywild_tree_3.png",
    ),
    "feywild_spiral": (
        "objects/feywild_spiral_1.png",
        "objects/feywild_spiral_2.png",
        "objects/feywild_spiral_3.png",
    ),
    "feywild_mushroom": (
        "objects/feywild_mushroom_1.png",
        "objects/feywild_mushroom_2.png",
        "objects/feywild_mushroom_3.png",
    ),
    "cloud_staircase": "objects/cloud_staircase.png",
    "cloud_tower_arch": "objects/cloud_tower_arch.png",
    "griffon_nest": "objects/griffon_nest.png",
    "aerie_rope": "objects/aerie_rope.png",
    "city_bottles": (
        "objects/city_bottles_1.png",
        "objects/city_bottles_2.png",
    ),
    "city_sewer_entrance": "objects/city_sewer_entrance.png",
    "city_bus_stop": "objects/city_bus_stop.png",
    "city_planar_portal": "objects/city_planar_portal_1.png",
    "tahuya_fir": (
        "objects/tahuya_fir_1.png",
        "objects/tahuya_fir_2.png",
        "objects/tahuya_fir_3.png",
    ),
    "tahuya_mushroom_light": "objects/tahuya_mushroom_light_1.png",
    "tahuya_firepit": "objects/tahuya_firepit_1.png",
    "tahuya_ufo": "objects/tahuya_ufo.png",
    "tahuya_firewood_shed": "objects/tahuya_firewood_shed.png",
    "tahuya_cabin": "objects/tahuya_cabin.png",
    "cabin_big_couch": "objects/cabin_big_couch.png",
    "cabin_couch": "objects/cabin_couch.png",
    "cabin_chair": "objects/cabin_chair.png",
    "cabin_table": "objects/cabin_table.png",
    "cabin_table_awakened": "objects/cabin_table_awakened_1.png",
    "cabin_connector_shelf": "objects/cabin_connector_shelf.png",
    "cabin_mini_fridge": "objects/cabin_mini_fridge.png",
    "cabin_closed_door_west": "objects/cabin_closed_door_west.png",
    "cabin_kitchen": "objects/cabin_kitchen.png",
    "cabin_woodstove": "objects/cabin_woodstove_1.png",
    "cabin_wood_storage": "objects/cabin_wood_storage.png",
    "fey_table_leg": (
        "objects/fey_table_leg_1.png",
        "objects/fey_table_leg_2.png",
    ),
    "fey_chair_leg": (
        "objects/fey_chair_leg_1.png",
        "objects/fey_chair_leg_2.png",
    ),
    "fey_plate": "objects/fey_plate.png",
    "fey_teacup": "objects/fey_teacup.png",
    "fey_napkin": "objects/fey_napkin.png",
    "fey_crumbs": (
        "objects/fey_crumbs_1.png",
        "objects/fey_crumbs_2.png",
        "objects/fey_crumbs_3.png",
    ),
}

_ANIMATED_SPRITES = {
    "phlegethos_lava_fall": (
        "objects/phlegethos_lava_fall.png",
        "objects/phlegethos_lava_fall_2.png",
        "objects/phlegethos_lava_fall_3.png",
        "objects/phlegethos_lava_fall_4.png",
    ),
    "city_planar_portal": tuple(
        f"objects/city_planar_portal_{index + 1}.png" for index in range(12)
    ),
    "tahuya_mushroom_light": tuple(
        f"objects/tahuya_mushroom_light_{index + 1}.png"
        for index in range(8)
    ),
    "tahuya_firepit": tuple(
        f"objects/tahuya_firepit_{index + 1}.png" for index in range(6)
    ),
    "cabin_table_awakened": tuple(
        f"objects/cabin_table_awakened_{index + 1}.png"
        for index in range(8)
    ),
    "cabin_woodstove": tuple(
        f"objects/cabin_woodstove_{index + 1}.png" for index in range(6)
    ),
}
_PROP_FRAME_TIME = 0.14

# Props that respond to the interact key with a line of dialogue
# (ids live in data/dialogue/). Everything else stays mute scenery.
PROP_DIALOGUE = {
    "bobert_barrel": "bobert_sleeping",  # he does not wake up
    "herod_sign": "herod_sign",
    "house_door": "closed_door",
    "cabin_closed_door_west": "closed_door",
    "cheese": "cheese",
    "fey_teacup": "fey_tea_warm",
    "fey_plate": "fey_set_for_one",
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
        animated = _ANIMATED_SPRITES.get(kind)
        if animated is not None:
            self._frames = tuple(assets.image(path) for path in animated)
            # The real cabin's colour-changing path lights do not pulse in
            # lockstep.  Their authored map position gives each one a stable
            # phase, so the offsets survive reloads without save-state noise.
            phase = (
                (col * 31 + row * 17) % len(self._frames)
                if kind == "tahuya_mushroom_light" else 0
            )
            self._animation_t = phase * _PROP_FRAME_TIME
            self._image = self._frames[phase]
        else:
            self._frames = ()
            self._animation_t = 0.0
            sprite = _SPRITES[kind]
            if isinstance(sprite, tuple):
                # Stable spatial variation: authored trees keep their
                # silhouette between runs without requiring separate chars.
                sprite = sprite[(col * 31 + row * 17) % len(sprite)]
            self._image = assets.image(sprite)
        w, h = self._image.get_size()
        # Horizontally centered on the tile, bottom edges aligned.
        self._draw_x = col * ts + (ts - w) // 2
        self._draw_y = (row + 1) * ts - h
        self._bottom = (row + 1) * ts
        self._size = (w, h)
        self.floor_layer = kind == "ship_captain_rug"
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

    def update(self, dt: float) -> None:
        """Advance the small set of authored animated scenery props."""
        if not self._frames:
            return
        self._animation_t += dt
        frame = int(self._animation_t / _PROP_FRAME_TIME) % len(self._frames)
        self._image = self._frames[frame]
