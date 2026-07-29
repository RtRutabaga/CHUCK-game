"""Phlegethos spined devils and their burning tail spines (Phase 8).

A spined devil never moves. It perches beside the road and flicks spines
down an authored lane on a fixed cadence -- the temple wall-launcher
pattern, but with a visible, deliberately menacing owner. Closing to
melee is fatal: scratching one immediately defeats Chuck, so it must be
solved by timing the lane, never by fighting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager

_VECTORS = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


class FlamingSpine(Entity):
    """One thrown spine, burning out against stone."""

    damage = config.SPINE_SANITY_DAMAGE

    def __init__(self, center_x: float, center_y: float,
                 direction: str) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown spine direction {direction!r}")
        horizontal = direction in {"left", "right"}
        width = (config.SPINE_HITBOX_LONG if horizontal
                 else config.SPINE_HITBOX_SHORT)
        height = (config.SPINE_HITBOX_SHORT if horizontal
                  else config.SPINE_HITBOX_LONG)
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self.direction = direction

    def update(self, dt: float, tilemap) -> None:
        vx, vy = _VECTORS[self.direction]
        dx = vx * config.SPINE_SPEED * dt
        dy = vy * config.SPINE_SPEED * dt
        target_x, target_y = self.x + dx, self.y + dy
        new_x, new_y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, tilemap
        )
        self.x, self.y = new_x, new_y
        if abs(new_x - target_x) > 1e-4 or abs(new_y - target_y) > 1e-4:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        rect = pygame.Rect(round(self.x) - ox, round(self.y) - oy,
                           self.width, self.height)
        pygame.draw.rect(surface, (196, 70, 22), rect)
        vx, vy = _VECTORS[self.direction]
        tip_x = round(self.x + self.width / 2 + vx * self.width / 2) - ox
        tip_y = round(self.y + self.height / 2 + vy * self.height / 2) - oy
        pygame.draw.rect(surface, (255, 196, 84), (tip_x - 1, tip_y - 1, 2, 2))


class SpinedDevil(Entity):
    """A perched launcher: lethal to touch in melee, dodgeable at range."""

    # Contact still merely hurts; it is the SCRATCH that is fatal, so the
    # rule reads as "do not try to fight this" rather than "do not brush it".
    damage = config.SPINED_DEVIL_CONTACT_DAMAGE
    melee_is_fatal = True

    def __init__(self, center_x: float, center_y: float,
                 direction: str) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown spined-devil direction {direction!r}")
        super().__init__(
            center_x - config.SPINED_DEVIL_HITBOX_W / 2,
            center_y - config.SPINED_DEVIL_HITBOX_H / 2,
            config.SPINED_DEVIL_HITBOX_W,
            config.SPINED_DEVIL_HITBOX_H,
        )
        self.direction = direction
        self.facing = direction
        # Deterministic stagger so a row of devils never fires in unison.
        col = int(center_x // config.TILE_SIZE)
        row = int(center_y // config.TILE_SIZE)
        stagger = ((col * 23 + row * 11) % 100) / 100.0
        self._time_until_throw = 0.4 + stagger * config.SPINED_DEVIL_INTERVAL
        self._wing_t = 0.0
        self._frames: dict[str, object] = {}

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        down, up, left = assets.sheet(
            "hazards/spined_devil.png",
            config.SPINED_DEVIL_FRAME_W,
            config.SPINED_DEVIL_FRAME_H,
        )[0]
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def update(self, dt: float) -> "FlamingSpine | None":
        """Tick the throw cadence; returns a spine on the beat."""
        self._wing_t += dt
        self._time_until_throw -= dt
        if self._time_until_throw > 0.0:
            return None
        while self._time_until_throw <= 0.0:
            self._time_until_throw += config.SPINED_DEVIL_INTERVAL
        vx, vy = _VECTORS[self.direction]
        offset = config.TILE_SIZE / 2 + config.SPINE_HITBOX_LONG / 2
        return FlamingSpine(
            self.x + self.width / 2 + vx * offset,
            self.y + self.height / 2 + vy * offset,
            self.direction,
        )

    @property
    def sort_y(self) -> float:
        return self.y + self.height

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is None:
            pygame.draw.rect(
                surface, (150, 52, 40),
                (int(self.x) - ox, int(self.y) - 12 - oy,
                 self.width, self.height + 12))
            return
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (int(self.x + self.width / 2 - fw / 2) - ox,
             int(self.y + self.height - fh) - oy),
        )
