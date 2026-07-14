"""Chuck — the player entity.

Responsibilities:
    * Read named actions from the InputManager and move through the
      world via collision.move_and_collide (8-directional top-down
      movement — no jumping, no gravity; this is a top-down RPG per
      the Game Bible).
    * Drive animation state: idle/walk in four facings (right is the
      left frames flipped).
    * (Future) Trigger interactions when the interact action is pressed.
    * (Future) The quiet vanish animation when sanity depletes.

Character notes that shape implementation (Game Bible):
    * Chuck never emotes dramatically. The walk is a small shuffle;
      the idle is stillness. No bounce, no squash-and-stretch.
    * Chuck is ~1 foot tall. His 12x14 sprite is smaller than one 16px
      tile — scale is a core design pillar, not a cosmetic choice.
    * The hitbox (10x8) is his FOOTPRINT; the sprite is taller and is
      drawn anchored to the hitbox's bottom edge, so depth sorting and
      "walking behind things" read correctly later.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.core import config
from src.core.animation import Animation
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.input import InputManager
    from src.world.tilemap import TileMap


class Player(Entity):
    """Chuck. Quiet. Patient. Persistent."""

    def __init__(self, x: float, y: float, input_manager: "InputManager") -> None:
        super().__init__(
            x, y, width=config.PLAYER_HITBOX_W, height=config.PLAYER_HITBOX_H
        )
        self.input = input_manager
        self.speed = config.PLAYER_SPEED
        self.facing = "down"  # "up" | "down" | "left" | "right"
        self.moving = False
        # The map Chuck collides with; set by the WorldScene on spawn
        # and whenever he changes areas.
        self.tilemap: "TileMap | None" = None
        # Hidden while Chuck is between places (the respawn transit).
        self.visible = True
        # Seconds of hurt-blink remaining (set by the WorldScene on hit).
        self.hurt_blink = 0.0
        # (state, facing) -> Animation. Empty until load_sprites() is
        # called; draw() falls back to a rectangle so headless tests
        # and asset failures degrade gracefully instead of crashing.
        self._animations: dict[tuple[str, str], Animation] = {}

    # ------------------------------------------------------------------
    # Sprites
    # ------------------------------------------------------------------
    def load_sprites(self, assets: "AssetManager") -> None:
        """Build the animation table from Chuck's sprite sheet.

        Sheet layout (see tools/generate_chuck_sprites.py):
            row 0 down, row 1 up, row 2 left; cols: idle, walk1, walk2.
        Right-facing frames are the left frames mirrored.
        """
        grid = assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        rows = {"down": grid[0], "up": grid[1], "left": grid[2]}
        rows["right"] = [
            pygame.transform.flip(frame, True, False) for frame in grid[2]
        ]

        ft = config.ANIM_WALK_FRAME_TIME
        for facing, (idle, walk1, walk2) in rows.items():
            self._animations[("idle", facing)] = Animation([idle], 1.0)
            # 4-beat cycle (step, pass, step, pass) from 3 drawings —
            # reads far better than a 2-frame shuffle.
            self._animations[("walk", facing)] = Animation(
                [walk1, idle, walk2, idle], ft
            )
        self._current_key = ("idle", self.facing)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Movement and animation state."""
        if self.hurt_blink > 0.0:
            self.hurt_blink = max(0.0, self.hurt_blink - dt)

        dx, dy = self.input.movement_vector()
        self.moving = bool(dx or dy)

        if self.moving:
            self._update_facing(dx, dy)
            if self.tilemap is not None:
                self.x, self.y = collision.move_and_collide(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dx * self.speed * dt,
                    dy * self.speed * dt,
                    self.tilemap,
                )

        if self._animations:
            key = ("walk" if self.moving else "idle", self.facing)
            if key != self._current_key:
                self._current_key = key
                self._animations[key].reset()
            self._animations[key].update(dt)



    def interaction_probe(self):
        """A rect (pygame.Rect) one tile ahead of Chuck's facing.

        The WorldScene tests this against NPCs (later: signs, doors)
        when interact is pressed. Generously sized: talking to someone
        should never require pixel-perfect alignment.
        """
        import pygame

        ts = config.TILE_SIZE
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        step = {"up": (0, -ts), "down": (0, ts),
                "left": (-ts, 0), "right": (ts, 0)}[self.facing]
        return pygame.Rect(
            int(cx + step[0] - ts / 2), int(cy + step[1] - ts / 2), ts, ts
        )

    def _update_facing(self, dx: float, dy: float) -> None:
        """Pick a cardinal facing from the movement vector.

        Horizontal wins ties so diagonal walking shows the profile
        (and the cigarette).
        """
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int]) -> None:
        """Draw the current animation frame anchored at Chuck's feet.

        Skips drawing entirely while hidden (respawn transit), and
        blinks (skips alternate slices) during the hurt window —
        understated feedback, no flashes or shakes.
        """
        if not self.visible:
            return
        if self.hurt_blink > 0.0 and int(self.hurt_blink / 0.08) % 2 == 0:
            return
        ox, oy = camera_offset
        if self._animations:
            frame = self._animations[self._current_key].current_frame
            fw, fh = frame.get_size()
            # Horizontally centered on the hitbox, bottom edges aligned.
            draw_x = int(self.x + self.width / 2 - fw / 2) - ox
            draw_y = int(self.y + self.height - fh) - oy
            surface.blit(frame, (draw_x, draw_y))
        else:
            # Fallback (sprites not loaded): the old placeholder rect.
            pygame.draw.rect(
                surface,
                config.COLOR_CHUCK_PLACEHOLDER,
                pygame.Rect(
                    int(self.x) - ox, int(self.y) - oy, self.width, self.height
                ),
            )
