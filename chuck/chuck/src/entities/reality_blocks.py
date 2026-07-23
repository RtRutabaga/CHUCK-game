"""Moving reality fragments around the staged pirate-ship plank.

These are visible wrong-map blocks over the sea, not portals and not yet
hazards. Phase 7's later kick/fall sequence can choose a Hell block from this
same field; this slice deliberately leaves the plank endpoint contained.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from src.core import config


@dataclass(frozen=True)
class RealityBlock:
    kind: str
    base_x: float
    base_y: float
    width: int
    height: int
    amplitude_x: float
    amplitude_y: float
    speed: float
    phase: float
    delay: float


class RealityBlockField:
    """A deterministic mix of Astral and Hell blocks flanking the plank."""

    reveal_duration = 0.4

    def __init__(self, plank_col: int, plank_row: int) -> None:
        ts = config.TILE_SIZE
        x = plank_col * ts
        y = plank_row * ts

        def block(
            kind: str,
            dx: float,
            dy: float,
            width_tiles: int,
            height_tiles: int,
            amplitude_x: float,
            amplitude_y: float,
            speed: float,
            phase: float,
            delay: float,
        ) -> RealityBlock:
            return RealityBlock(
                kind=kind,
                base_x=x + dx * ts,
                base_y=y + dy * ts,
                width=width_tiles * ts,
                height=height_tiles * ts,
                amplitude_x=amplitude_x,
                amplitude_y=amplitude_y,
                speed=speed,
                phase=phase,
                delay=delay,
            )

        # Both materials occupy broad lanes beside the plank. Their restrained
        # oscillation never crosses its centerline, so this reveal cannot
        # become the still-unbuilt kick/fall hazard by accident.
        self.blocks = (
            block("astral", -8.2, 0.8, 3, 2, 7, 3, .72, .2, 0.0),
            block("hell", 4.2, 0.4, 2, 3, 5, 4, .62, 1.3, .2),
            block("hell", -6.5, 3.7, 2, 2, 6, 5, .55, 2.1, .5),
            block("astral", 3.1, 3.4, 3, 2, 6, 4, .68, 2.8, .8),
            block("astral", -8.7, 6.6, 2, 3, 4, 6, .58, 3.6, 1.1),
            block("hell", 5.0, 6.8, 3, 2, 7, 3, .64, 4.2, 1.4),
            block("hell", -5.7, 9.0, 3, 2, 5, 4, .52, 5.0, 1.7),
            block("astral", 3.7, 9.2, 2, 3, 4, 5, .60, 5.7, 2.0),
        )
        self.active = False
        self.age = 0.0

    def activate(self) -> None:
        if self.active:
            return
        self.active = True
        self.age = 0.0

    def update(self, dt: float) -> None:
        if self.active:
            self.age += dt

    @property
    def visible_blocks(self) -> tuple[RealityBlock, ...]:
        if not self.active:
            return ()
        return tuple(block for block in self.blocks if self.age >= block.delay)

    def position(self, block: RealityBlock) -> tuple[float, float]:
        t = max(0.0, self.age - block.delay)
        angle = t * block.speed + block.phase
        return (
            block.base_x + math.sin(angle) * block.amplitude_x,
            block.base_y + math.cos(angle * .83) * block.amplitude_y,
        )

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        if not self.active:
            return
        import pygame

        ox, oy = camera_offset
        for index, block in enumerate(self.visible_blocks):
            x, y = self.position(block)
            reveal = min(
                1.0,
                (self.age - block.delay) / self.reveal_duration,
            )
            width = max(2, int(block.width * reveal))
            left = int(x + (block.width - width) / 2) - ox
            top = int(y) - oy
            image = pygame.Surface((width, block.height), pygame.SRCALPHA)
            rect = image.get_rect()
            if block.kind == "astral":
                self._draw_astral(image, rect, index)
            else:
                self._draw_hell(image, rect, index)
            surface.blit(image, (left, top))

    def _draw_astral(self, surface, rect, seed: int) -> None:
        """Hard-edged wrong-map night blocks with stepped nebula bands."""
        import pygame

        pygame.draw.rect(surface, (10, 10, 28), rect)
        phase = int(self.age * 6) + seed * 5
        for y in range(rect.top, rect.bottom, 4):
            x = rect.left + ((y + phase) % 9) - 4
            pygame.draw.rect(surface, (35, 22, 78),
                             pygame.Rect(x, y, rect.width + 5, 2))
        for star in range(4):
            sx = rect.left + (seed * 7 + star * 11 + phase) % max(1, rect.width)
            sy = rect.top + (seed * 5 + star * 7) % max(1, rect.height)
            surface.set_at((sx, sy), (190, 205, 255))
        pygame.draw.rect(surface, (71, 45, 126), rect, 1)

    def _draw_hell(self, surface, rect, seed: int) -> None:
        """A block of foreign basalt with square magma seams and ember heat."""
        import pygame

        pygame.draw.rect(surface, (43, 16, 15), rect)
        phase = int(self.age * 5) + seed * 3
        for x in range(rect.left + 5 - phase % 6, rect.right, 9):
            pygame.draw.line(surface, (126, 38, 20),
                             (x, rect.top), (x + 3, rect.bottom), 2)
        seam_y = rect.top + rect.height // 2
        pygame.draw.line(surface, (224, 72, 24),
                         (rect.left, seam_y), (rect.right, seam_y), 1)
        # Square, flickering tongues along the foreign block's upper edge.
        for flame, fx in enumerate(range(rect.left + 2, rect.right, 7)):
            height = 2 + (phase + flame * 3) % 5
            pygame.draw.rect(
                surface, (205, 48, 19),
                pygame.Rect(fx, rect.top, 4, height),
            )
            pygame.draw.rect(
                surface, (255, 142, 31),
                pygame.Rect(fx + 1, rect.top, 2, max(1, height - 2)),
            )
        for ember in range(5):
            ex = rect.left + (seed * 9 + ember * 13 + phase) % max(1, rect.width)
            ey = rect.top + (seed * 4 + ember * 9) % max(1, rect.height)
            surface.set_at((ex, ey), (255, 162, 42))
        pygame.draw.rect(surface, (102, 31, 24), rect, 1)
