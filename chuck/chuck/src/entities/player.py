"""Chuck — the player entity.

Responsibilities:
    * Read named actions from the InputManager and move through the
      world via collision.move_and_collide (8-directional top-down
      movement plus a short committed hop; no platformer gravity).
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
        # A jump is a short committed hop in the current facing direction.
        self.jump_remaining = 0.0
        self.jump_just_started = False
        self._jump_direction = (0.0, 1.0)
        self.scratch_remaining = 0.0
        self.scratch_just_started = False
        # Set by WorldScene while Chuck drops into an Astral fall zone.
        self.fall_progress: float | None = None
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
        self.jump_just_started = False
        self.scratch_just_started = False
        if self.hurt_blink > 0.0:
            self.hurt_blink = max(0.0, self.hurt_blink - dt)

        if (
            self.input.was_pressed("jump")
            and not self.jumping
            and not self.scratching
        ):
            self.jump_remaining = config.JUMP_DURATION
            self.jump_just_started = True
            self._jump_direction = {
                "up": (0.0, -1.0),
                "down": (0.0, 1.0),
                "left": (-1.0, 0.0),
                "right": (1.0, 0.0),
            }[self.facing]

        if (
            self.input.was_pressed("scratch")
            and not self.scratching
            and not self.jumping
        ):
            self.scratch_remaining = config.SCRATCH_DURATION
            self.scratch_just_started = True

        if self.jumping:
            dx, dy = self._jump_direction
            move_speed = config.JUMP_SPEED
            ignored_terrain = frozenset({"V"})
            self.jump_remaining = max(0.0, self.jump_remaining - dt)
        elif self.scratching:
            dx, dy = (0.0, 0.0)
            move_speed = 0.0
            ignored_terrain = frozenset()
            self.scratch_remaining = max(0.0, self.scratch_remaining - dt)
        else:
            dx, dy = self.input.movement_vector()
            move_speed = self.speed
            ignored_terrain = frozenset()
        self.moving = bool(dx or dy)

        if self.moving:
            self._update_facing(dx, dy)
            if self.tilemap is not None:
                self.x, self.y = collision.move_and_collide(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dx * move_speed * dt,
                    dy * move_speed * dt,
                    self.tilemap,
                    ignored_terrain=ignored_terrain,
                )

        if self._animations:
            key = ("walk" if self.moving else "idle", self.facing)
            if key != self._current_key:
                self._current_key = key
                self._animations[key].reset()
            self._animations[key].update(dt)

    @property
    def jumping(self) -> bool:
        return self.jump_remaining > 0.0

    @property
    def scratching(self) -> bool:
        return self.scratch_remaining > 0.0

    @property
    def scratch_progress(self) -> float:
        """0..1 across the current swipe, used only by visual feedback."""
        if not self.scratching:
            return 1.0
        return 1.0 - self.scratch_remaining / config.SCRATCH_DURATION

    def scratch_hitbox(self):
        """The small forward area reached by one paw swipe."""
        reach = config.SCRATCH_REACH
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        if self.facing == "up":
            return pygame.Rect(int(cx - reach / 2), int(self.y - reach),
                               reach, reach)
        if self.facing == "down":
            return pygame.Rect(int(cx - reach / 2), int(self.y + self.height),
                               reach, reach)
        if self.facing == "left":
            return pygame.Rect(int(self.x - reach), int(cy - reach / 2),
                               reach, reach)
        return pygame.Rect(int(self.x + self.width), int(cy - reach / 2),
                           reach, reach)



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
            lift = 0
            if self.jumping:
                import math
                progress = 1.0 - self.jump_remaining / config.JUMP_DURATION
                lift = round(math.sin(progress * math.pi) * config.JUMP_HEIGHT)
            if self.fall_progress is not None:
                scale = max(0.2, 1.0 - self.fall_progress * 0.8)
                fw, fh = max(1, round(fw * scale)), max(1, round(fh * scale))
                frame = pygame.transform.scale(frame, (fw, fh))
            draw_x = int(self.x + self.width / 2 - fw / 2) - ox
            sink = (round(self.fall_progress * 5)
                    if self.fall_progress is not None else 0)
            draw_y = int(self.y + self.height - fh) - oy - lift + sink
            surface.blit(frame, (draw_x, draw_y))
        else:
            # Fallback (sprites not loaded): the old placeholder rect.
            scale = (max(0.2, 1.0 - self.fall_progress * 0.8)
                     if self.fall_progress is not None else 1.0)
            fw = max(1, round(self.width * scale))
            fh = max(1, round(self.height * scale))
            pygame.draw.rect(
                surface,
                config.COLOR_CHUCK_PLACEHOLDER,
                pygame.Rect(
                    int(self.x + self.width / 2 - fw / 2) - ox,
                    int(self.y + self.height - fh) - oy,
                    fw, fh,
                ),
            )
        if self.scratching:
            self._draw_scratch(surface, camera_offset)

    def _draw_scratch(self, surface, camera_offset: tuple[int, int]) -> None:
        """A fast fan of fading afterimages — motion, not two static lines."""
        ox, oy = camera_offset
        box = self.scratch_hitbox().move(-ox, -oy)
        progress = self.scratch_progress
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # The leading claw mark crosses the target box; four translucent
        # echoes trail it by whole native pixels and read as a compact blur.
        if self.facing in ("up", "down"):
            lead = box.left + 2 + round(progress * (box.width - 4))
            for i in range(5):
                x = lead - i * 2
                alpha = 210 - i * 38
                pygame.draw.line(layer, (226, 220, 210, alpha),
                                 (x - 2, box.top + 2),
                                 (x + 2, box.bottom - 2), 1)
                pygame.draw.line(layer, (180, 166, 190, alpha // 2),
                                 (x, box.top + 3),
                                 (x + 3, box.bottom - 3), 1)
        else:
            lead = box.top + 2 + round(progress * (box.height - 4))
            for i in range(5):
                y = lead - i * 2
                alpha = 210 - i * 38
                pygame.draw.line(layer, (226, 220, 210, alpha),
                                 (box.left + 2, y - 2),
                                 (box.right - 2, y + 2), 1)
                pygame.draw.line(layer, (180, 166, 190, alpha // 2),
                                 (box.left + 3, y),
                                 (box.right - 3, y + 3), 1)
        surface.blit(layer, (0, 0))
