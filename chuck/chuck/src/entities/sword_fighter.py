"""Paired wandering sword-fighters on the exterior pirate deck."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.world.tilemap import TileMap


FRAME_W = 24
FRAME_H = 30
SHANTY_BPM = 126.0


class SwordFighter(Entity):
    """One half of a paired, avoidable fencing hazard.

    The shared midpoint wanders in a slow loop while the fighters lunge and
    retreat across it on the shanty's beat. They remain ordinary collision-
    aware world entities, so masts and rails constrain the performance.
    """

    def __init__(self, center_x: float, center_y: float, role: str) -> None:
        if role not in {"a", "b"}:
            raise ValueError(f"Unknown sword-fighter role {role!r}")
        super().__init__(
            center_x - config.NPC_HITBOX_W / 2,
            center_y - config.NPC_HITBOX_H / 2,
            config.NPC_HITBOX_W,
            config.NPC_HITBOX_H,
        )
        self.role = role
        self.side = -1 if role == "a" else 1
        self.damage = config.SWORD_FIGHTER_SANITY_DAMAGE
        self.tilemap: "TileMap | None" = None
        self.facing = "right" if self.side < 0 else "left"
        self._frames: dict[str, tuple[object, ...]] = {}
        self._motion_t = 0.0
        self._pair_center = (center_x, center_y)
        self.spawn_position = (self.x, self.y)

    def bind_pair(self, other: "SwordFighter") -> None:
        center_a = (self.x + self.width / 2, self.y + self.height / 2)
        center_b = (other.x + other.width / 2, other.y + other.height / 2)
        self._pair_center = other._pair_center = (
            (center_a[0] + center_b[0]) / 2,
            (center_a[1] + center_b[1]) / 2,
        )

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        frames = assets.sheet(
            f"hazards/sword_fighter_{self.role}.png", FRAME_W, FRAME_H
        )[0]
        if len(frames) != 12:
            raise ValueError(f"Sword fighter {self.role} needs 12 frames")
        down = tuple(frames[0:4])
        up = tuple(frames[4:8])
        left = tuple(frames[8:12])
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": tuple(
                pygame.transform.flip(frame, True, False) for frame in left
            ),
        }

    @property
    def animation_frame(self) -> int:
        half_beat = (60.0 / SHANTY_BPM) / 2.0
        offset = 0 if self.role == "a" else 2
        return (int(self._motion_t / half_beat) + offset) % 4

    def update(self, dt: float) -> None:
        if self.tilemap is None:
            return
        self._motion_t += dt
        beat_phase = self._motion_t * math.tau * SHANTY_BPM / 60.0
        base_x, base_y = self._pair_center
        group_x = base_x + math.sin(self._motion_t * 0.72) * 58.0
        group_y = base_y + math.sin(self._motion_t * 0.47) * 20.0
        separation = 42.0 + math.sin(beat_phase) * 10.0
        target_x = group_x + self.side * separation / 2.0
        target_y = group_y + self.side * math.sin(beat_phase * 0.5) * 2.0
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        dx, dy = target_x - center_x, target_y - center_y
        distance = math.hypot(dx, dy)
        if distance > 0.0:
            step = min(distance, config.SWORD_FIGHTER_SPEED * dt)
            self.x, self.y = collision.move_and_collide(
                self.x, self.y, self.width, self.height,
                dx / distance * step, dy / distance * step,
                self.tilemap,
                extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
            )
        self.facing = "right" if self.side < 0 else "left"

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frames = self._frames.get(self.facing)
        if frames:
            frame = frames[self.animation_frame]
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            pygame.draw.rect(
                surface, (133, 65, 57),
                (int(self.x) - ox, int(self.y) - 22 - oy, 12, 30),
            )
