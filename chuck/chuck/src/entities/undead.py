"""Simple, durable Chultan undead built on the existing enemy lifecycle."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.entities.player import Player
    from src.world.tilemap import TileMap


_STATS = {
    "zombie": (
        config.ZOMBIE_SPEED,
        config.ZOMBIE_SANITY_DAMAGE,
        config.ZOMBIE_SCRATCHES,
    ),
    "skeleton": (
        config.SKELETON_SPEED,
        config.SKELETON_SANITY_DAMAGE,
        config.SKELETON_SCRATCHES,
    ),
    # Phase 13's desert orc. Not undead either, and the same role again:
    # the phase document is explicit that it should be built on this
    # architecture rather than given a combat system of its own.
    "orc": (
        config.ORC_SPEED,
        config.ORC_SANITY_DAMAGE,
        config.ORC_SCRATCHES,
    ),
    # Phase 13's armoured knight, out of the medieval fragment. The
    # same role again, at the far end of its range: slow and very hard
    # to shift, which is what armour is for.
    "knight": (
        config.KNIGHT_SPEED,
        config.KNIGHT_SANITY_DAMAGE,
        config.KNIGHT_SCRATCHES,
    ),
    # Phlegethos (Phase 8): the lemure is a third undead kind, identical in
    # behaviour to the Chultan pair but slower and far more durable.
    "lemure": (
        config.LEMURE_SPEED,
        config.LEMURE_SANITY_DAMAGE,
        config.LEMURE_SCRATCHES,
    ),
    # The modern sewer (Phase 11): not undead at all, but the same role --
    # durable, dangerous to touch, straightforward in pursuit. The upright
    # 16x30 frame suits a top-down crocodile better than it suits a person.
    "crocodile": (
        config.CROCODILE_SPEED,
        config.CROCODILE_SANITY_DAMAGE,
        config.CROCODILE_SCRATCHES,
    ),
    # The daytime city (Phase 11). Animal Control officers are this role
    # too; their net lives in the subclass, not here.
    "animal_control": (
        config.ANIMAL_CONTROL_SPEED,
        config.ANIMAL_CONTROL_SANITY_DAMAGE,
        config.ANIMAL_CONTROL_SCRATCHES,
    ),
}


class UndeadEnemy(Entity):
    """A human-scale pursuer that is possible, but inefficient, to fight."""

    def __init__(self, center_x: float, center_y: float, kind: str) -> None:
        if kind not in _STATS:
            raise ValueError(f"Unknown undead kind {kind!r}")
        super().__init__(
            center_x - config.UNDEAD_HITBOX_W / 2,
            center_y - config.UNDEAD_HITBOX_H / 2,
            config.UNDEAD_HITBOX_W,
            config.UNDEAD_HITBOX_H,
        )
        self.kind = kind
        self.speed, self.damage, self.max_scratches = _STATS[kind]
        self.scratches_remaining = self.max_scratches
        self.facing = "down"
        self.tilemap: "TileMap | None" = None
        self._frames: dict[str, object] = {}

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        down, up, left = assets.sheet(
            f"hazards/{self.kind}.png",
            config.UNDEAD_FRAME_W,
            config.UNDEAD_FRAME_H,
        )[0]
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def update(self, dt: float, target: "Player | None" = None) -> None:
        if target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0 or distance > config.UNDEAD_NOTICE_RANGE:
            return
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = self.speed * dt / distance
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height,
            dx * step, dy * step, self.tilemap,
            extra_solid_terrain=(collision.LARGE_ACTOR_PASSAGE_TERRAIN
                                 | collision.FALL_HAZARD_TERRAIN),
        )

    def on_scratched(self) -> None:
        self.scratches_remaining -= 1
        if self.scratches_remaining <= 0:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is not None:
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            color = {
                "zombie": (73, 100, 62),
                "lemure": (176, 146, 132),
            }.get(self.kind, (194, 191, 158))
            pygame.draw.rect(surface, color,
                             (int(self.x) - ox, int(self.y) - 22 - oy, 12, 30))
