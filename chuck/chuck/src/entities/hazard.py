"""Hazards — starting with the dock cat.

Responsibilities:
    * Patrol horizontally at a steady pace, turning around at anything
      solid (crates, walls, water's edge).
    * Damage Chuck's sanity on contact (the WorldScene detects overlap
      and applies damage through the SanitySystem's i-frames).

Behavior notes (Game Bible tone):
    * The cat does not chase, does not lunge, does not notice Chuck at
      all. It simply exists, enormously, on its route. Ruining Chuck's
      day is incidental. Phase One explicitly wants no pathfinding.
    * Scale: the cat's sprite (18px) and footprint (16x8) dwarf Chuck.

pygame is imported only inside load_sprites/draw so patrol logic is
unit-testable headless.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.core.animation import Animation
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.world.tilemap import TileMap


class Cat(Entity):
    """A dockside tabby. Not evil. A cat. This is worse."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - config.CAT_HITBOX_W / 2,
            center_y - config.CAT_HITBOX_H / 2,
            width=config.CAT_HITBOX_W,
            height=config.CAT_HITBOX_H,
        )
        self.speed = config.CAT_SPEED
        self.direction = -1  # -1 left, +1 right
        self.damage = config.CAT_SANITY_DAMAGE
        self.tilemap: "TileMap | None" = None
        self._walk: Animation | None = None
        self._frames_left: list = []
        self._frames_right: list = []

    # ------------------------------------------------------------------
    # Sprites
    # ------------------------------------------------------------------
    def load_sprites(self, assets: "AssetManager") -> None:
        """Slice the cat sheet; right-facing frames are mirrored."""
        import pygame

        row = assets.sheet(
            config.CAT_SHEET, config.CAT_FRAME_W, config.CAT_FRAME_H
        )[0]
        stand, walk1, walk2 = row
        self._frames_left = [walk1, stand, walk2, stand]
        self._frames_right = [
            pygame.transform.flip(f, True, False) for f in self._frames_left
        ]
        self._walk = Animation(self._frames_left, config.ANIM_WALK_FRAME_TIME)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Walk the route; turn around at anything solid."""
        if self.tilemap is None:
            return
        dx = self.direction * self.speed * dt
        intended_x = self.x + dx
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, 0.0, self.tilemap
        )
        if abs(self.x - intended_x) > 1e-6:  # blocked: about-face
            self.direction *= -1
        if self._walk is not None:
            self._walk.frames = (
                self._frames_right if self.direction > 0 else self._frames_left
            )
            self._walk.update(dt)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """Sprite anchored at the feet (like all characters)."""
        import pygame

        ox, oy = camera_offset
        if self._walk is not None:
            frame = self._walk.current_frame
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (
                    int(self.x + self.width / 2 - fw / 2) - ox,
                    int(self.y + self.height - fh) - oy,
                ),
            )
        else:  # fallback: an ominous orange slab
            pygame.draw.rect(
                surface,
                (204, 126, 58),
                pygame.Rect(
                    int(self.x) - ox, int(self.y) - oy, self.width, self.height
                ),
            )
