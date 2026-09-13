"""Pantry shelves whose jars Chuck can scratch down and break.

The Waterdeep pantry's two storage shelves keep standing forever — the
furniture is human-scale and solid — but their JARS are the breakable:
one scratch at a shelf's base rattles every jar off it in a burst of
glazed ceramic shards, and a full cigarette carton spills out onto safe
floor beside the shelf. Afterwards the shelf simply stands bare (the
dedicated empty sprite), still solid, still mute.

Unlike a temple urn the entity never dies: it outlives its debris pass
so the emptied shelf keeps drawing. The scene supplies the carton's
drop position because only the map knows which neighboring board is
safe — the left shelf stands directly above an Astral fall tile, and a
carton must never land where collecting it kills you.

Map reload rebuilds the shelves fully stocked, matching the
return-to-checkpoint lifecycle of every other breakable.
"""

from __future__ import annotations

import math

from src.core import config
from src.entities.breakable_urn import BreakableUrn
from src.entities.entity import Entity


class PantryJar(BreakableUrn):
    EXAMINE_LINE = "examine_pantry_jar"

    """One round floor jar (the map's 'z' tiles): the temple urn's whole
    scratch-break lifecycle, restyled — a big-bellied tan vessel that
    shatters into cream crockery shards and spills a carton where it
    stood. Its tile clears to walkable board through the same on_break
    callback the temple's floor urns use."""

    FRAGMENTS = (
        (-12, -4, 2, 2, (182, 142, 88)),
        (-8, 8, 2, 1, (150, 112, 66)),
        (-4, -11, 1, 3, (204, 168, 110)),
        (3, -13, 2, 2, (182, 142, 88)),
        (9, -7, 1, 2, (112, 82, 48)),
        (13, 4, 2, 2, (204, 168, 110)),
        (6, 11, 2, 1, (150, 112, 66)),
        (-7, 12, 1, 2, (112, 82, 48)),
    )

    def __init__(self, col: int, row: int, on_break=None) -> None:
        super().__init__(col, row, wall_mounted=False, on_break=on_break)
        self._sprite_path = "objects/grain_sack.png"


# Glazed ceramic shards, matching the jar colors on the stocked sprite.
_FRAGMENTS = (
    (-12, -4, 2, 2, (240, 180, 80)),
    (-8, 8, 2, 1, (128, 126, 130)),
    (-4, -11, 1, 3, (242, 146, 66)),
    (3, -13, 2, 2, (240, 180, 80)),
    (9, -7, 1, 2, (176, 156, 116)),
    (13, 4, 2, 2, (128, 126, 130)),
    (6, 11, 2, 1, (242, 146, 66)),
    (-7, 12, 1, 2, (176, 156, 116)),
)


class PantryJarShelf(Entity):
    """One solid shelf; a scratch breaks its jars and spills a carton."""

    def __init__(self, col: int, row: int,
                 drop: tuple[float, float]) -> None:
        ts = config.TILE_SIZE
        center_x = col * ts + ts / 2
        bottom = (row + 1) * ts
        # Footprint: the shelf's base tile, so a scratch from any
        # adjacent walkable board reaches it.
        super().__init__(col * ts + 1, bottom - 14, ts - 2, 14)
        self._center_x = center_x
        self._bottom = bottom
        self._drop = drop
        self._stocked_image = None
        self._empty_image = None
        self.intact = True
        self._break_time = 0.0
        self._drop_pending = False

    @property
    def dialogue_id(self) -> str:
        """The shelf stays, so it always has something to say."""
        return "examine_jar_shelf" if self.intact else "examine_jar_shelf_empty"

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """The footprint, padded a little, for the interact probe."""
        pad = 3
        return (int(self.x) - pad, int(self.y) - pad,
                int(self.width) + pad * 2, int(self.height) + pad * 2)

    def load_sprite(self, assets) -> None:
        self._stocked_image = assets.image("objects/pantry_shelf.png")
        self._empty_image = assets.image("objects/pantry_shelf_empty.png")

    @property
    def hitbox(self):
        """An emptied shelf stops consuming scratches immediately."""
        if self.intact:
            return super().hitbox
        import pygame
        return pygame.Rect(0, 0, 0, 0)

    @property
    def sort_y(self) -> float:
        """Depth key: the tile's bottom edge, same rule as the old prop."""
        return float(self._bottom)

    def on_scratched(self) -> None:
        if not self.intact:
            return
        self.intact = False
        self._break_time = 0.0
        self._drop_pending = True

    def take_drop_position(self) -> tuple[float, float] | None:
        """Return the spilled carton position exactly once."""
        if not self._drop_pending:
            return None
        self._drop_pending = False
        return self._drop

    def create_pickup(self, drop: tuple[float, float], assets):
        """The reward the jars conceal: a full carton."""
        from src.entities.pickup import CigaretteCarton

        pickup = CigaretteCarton(*drop)
        pickup.load_sprite(assets)
        return pickup

    def update(self, dt: float) -> None:
        """Advance the shard burst; the shelf itself never goes away."""
        if not self.intact and self._break_time < config.BREAKABLE_GRASS_DURATION:
            self._break_time += dt

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        cx, bottom = self._center_x, self._bottom
        image = self._stocked_image if self.intact else self._empty_image
        if image is not None:
            w, h = image.get_size()
            surface.blit(image, (int(cx - w / 2) - ox,
                                 int(bottom - h) - oy))
        elif self.intact:
            pygame.draw.rect(surface, (150, 112, 66),
                             pygame.Rect(int(cx - 8) - ox,
                                         int(bottom - 24) - oy, 16, 24))

        if self.intact or self._break_time >= config.BREAKABLE_GRASS_DURATION:
            return
        progress = self._break_time / config.BREAKABLE_GRASS_DURATION
        cy = bottom - 12
        arc = math.sin(progress * math.pi) * 6.0
        for dx, dy, w, h, color in _FRAGMENTS:
            x = int(cx + dx * progress - w / 2) - ox
            y = int(cy + dy * progress - arc - h / 2) - oy
            pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h))
