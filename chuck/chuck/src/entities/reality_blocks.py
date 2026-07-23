"""Moving reality fragments behind the pirate-ship plank.

These remain presentation-only wrong-map blocks, not portals or hazards. The
ship is moving through them: complete Astral and Hell chunks enter from the
east edge of the native screen, cross west, and recycle continuously.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core import config
from src.world.tileset_layout import ANIM_FPS, SEWER, TILE_PX

if TYPE_CHECKING:
    from src.core.assets import AssetManager


_OFFSCREEN_MARGIN = 12
_EAST_EDGE_INSET = 8


@dataclass(frozen=True)
class RealityBlock:
    kind: str
    width: int
    height: int
    screen_y: int
    speed: float
    delay: float
    entry_offset: int


class RealityBlockField:
    """A repeating east-to-west mix of Astral and Hell blocks."""

    def __init__(self, plank_col: int, plank_row: int) -> None:
        # Keep the authored origin available for the later kick/fall slice.
        # Motion in this pass is deliberately screen-relative, because it is
        # the ship—not the wrong-map fragments—that owns the world position.
        self.plank_origin = (plank_col, plank_row)
        ts = config.TILE_SIZE

        def block(
            kind: str,
            width_tiles: int,
            height_tiles: int,
            screen_y: int,
            speed: float,
            delay: float,
            entry_offset: int,
        ) -> RealityBlock:
            return RealityBlock(
                kind=kind,
                width=width_tiles * ts,
                height=height_tiles * ts,
                screen_y=screen_y,
                speed=speed,
                delay=delay,
                entry_offset=entry_offset,
            )

        # Alternating materials and vertically overlapping lanes make the
        # moving field feel irregular without random runtime placement. The
        # ship and plank draw above these chunks, so their uninterrupted
        # east-west travel never changes collision or blocks the route.
        self.blocks = (
            block("astral", 3, 2, 94, 54.0, 0.0, 0),
            block("hell", 2, 3, 122, 58.0, 0.6, 14),
            block("astral", 2, 2, 150, 52.0, 1.2, 5),
            block("hell", 3, 2, 101, 56.0, 1.8, 20),
            block("astral", 3, 3, 132, 55.0, 2.4, 9),
            block("hell", 2, 2, 157, 53.0, 3.0, 2),
            block("astral", 2, 3, 109, 57.0, 3.6, 17),
            block("hell", 3, 2, 143, 54.0, 4.2, 7),
        )
        self.active = False
        self.age = 0.0
        self._astral_frames: tuple[object, ...] = ()

    def load_art(self, assets: "AssetManager") -> None:
        """Load the exact animated Astral fall-hazard cells used elsewhere."""
        row_index = next(
            index
            for index, (name, _variants, _frames) in enumerate(SEWER.order)
            if name == "astral_void"
        )
        variants, frames = SEWER.info()["astral_void"]
        row = assets.tileset(SEWER.sheet, TILE_PX)[row_index]
        self._astral_frames = tuple(row[:variants * frames])

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

    def east_x(
        self,
        block: RealityBlock,
        screen_width: int = config.NATIVE_WIDTH,
    ) -> float:
        """Left edge where a recycled block begins entering from the east."""
        return screen_width - _EAST_EDGE_INSET + block.entry_offset

    def travel_distance(
        self,
        block: RealityBlock,
        screen_width: int = config.NATIVE_WIDTH,
    ) -> float:
        """Distance from the east entry point to fully clear of the west."""
        return self.east_x(block, screen_width) + block.width + _OFFSCREEN_MARGIN

    def position(
        self,
        block: RealityBlock,
        screen_width: int = config.NATIVE_WIDTH,
    ) -> tuple[float, float]:
        """Current screen-space position; motion is always directly west."""
        elapsed = max(0.0, self.age - block.delay)
        distance = self.travel_distance(block, screen_width)
        x = self.east_x(block, screen_width) - (
            elapsed * block.speed % distance
        )
        return x, float(block.screen_y)

    def draw(
        self,
        surface,
        _camera_offset: tuple[int, int] = (0, 0),
    ) -> None:
        if not self.active:
            return
        import pygame

        for index, block in enumerate(self.visible_blocks):
            x, y = self.position(block, surface.get_width())
            image = pygame.Surface(
                (block.width, block.height), pygame.SRCALPHA
            )
            if block.kind == "astral":
                self._draw_astral(image, index)
            else:
                self._draw_hell(image, image.get_rect(), index)
            surface.blit(image, (int(x), int(y)))

    def _draw_astral(self, surface, seed: int) -> None:
        """Tile the established animated Astral fall-hazard art unchanged."""
        import pygame

        if not self._astral_frames:
            pygame.draw.rect(surface, (14, 16, 38), surface.get_rect())
            return
        variants, frames = SEWER.info()["astral_void"]
        frame = int(self.age * ANIM_FPS) % frames
        cols = surface.get_width() // TILE_PX
        rows = surface.get_height() // TILE_PX
        for row in range(rows):
            for col in range(cols):
                variant = (col * 31 + row * 17 + seed) % variants
                surface.blit(
                    self._astral_frames[variant * frames + frame],
                    (col * TILE_PX, row * TILE_PX),
                )

    def _draw_hell(self, surface, rect, seed: int) -> None:
        """A block of foreign basalt with square magma seams and ember heat."""
        import pygame

        pygame.draw.rect(surface, (43, 16, 15), rect)
        phase = int(self.age * 5) + seed * 3
        for x in range(rect.left + 5 - phase % 6, rect.right, 9):
            pygame.draw.line(
                surface,
                (126, 38, 20),
                (x, rect.top),
                (x + 3, rect.bottom),
                2,
            )
        seam_y = rect.top + rect.height // 2
        pygame.draw.line(
            surface,
            (224, 72, 24),
            (rect.left, seam_y),
            (rect.right, seam_y),
            1,
        )
        for flame, fx in enumerate(range(rect.left + 2, rect.right, 7)):
            height = 2 + (phase + flame * 3) % 5
            pygame.draw.rect(
                surface,
                (205, 48, 19),
                pygame.Rect(fx, rect.top, 4, height),
            )
            pygame.draw.rect(
                surface,
                (255, 142, 31),
                pygame.Rect(fx + 1, rect.top, 2, max(1, height - 2)),
            )
        for ember in range(5):
            ex = (
                rect.left
                + (seed * 9 + ember * 13 + phase) % max(1, rect.width)
            )
            ey = (
                rect.top
                + (seed * 4 + ember * 9) % max(1, rect.height)
            )
            surface.set_at((ex, ey), (255, 162, 42))
        pygame.draw.rect(surface, (102, 31, 24), rect, 1)
