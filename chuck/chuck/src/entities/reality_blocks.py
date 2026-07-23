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

# Shared semantic palettes keep the procedural Hell terrain readable at the
# native resolution and make its top-down material balance testable.
HELL_BASALT_COLORS = (
    (28, 22, 23),
    (42, 28, 27),
    (58, 35, 30),
    (76, 43, 32),
)
HELL_LAVA_COLORS = (
    (112, 28, 13),
    (178, 45, 12),
    (235, 83, 15),
    (255, 157, 31),
)


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
        """Draw a bird's-eye volcanic hellscape of basalt over moving lava."""
        import pygame

        # Lava is the ground plane, visible through the gaps between irregular
        # basalt plates. Slow highlight drift suggests flow without making the
        # terrain itself slide separately from its east-west screen motion.
        phase = int(self.age * 4) + seed * 5
        pygame.draw.rect(surface, HELL_LAVA_COLORS[0], rect)
        for y in range(rect.top + 2, rect.bottom, 6):
            offset = (phase + y * 3) % 9
            for x in range(rect.left - 6 + offset, rect.right, 12):
                pygame.draw.line(
                    surface,
                    HELL_LAVA_COLORS[2],
                    (x, y),
                    (min(x + 5, rect.right - 1), y),
                    1,
                )
                if (x + y + seed) % 3 == 0:
                    surface.set_at(
                        (min(x + 2, rect.right - 1), y),
                        HELL_LAVA_COLORS[3],
                    )

        # Build irregular staggered bands rather than a shared square lattice.
        # The seed changes the band heights, starting offsets, slab widths,
        # and gaps for every fragment, while remaining stable between frames.
        row = 0
        band_top = rect.top - (seed * 3 % 5)
        while band_top < rect.bottom:
            band_value = seed * 43 + row * 71
            band_height = 9 + band_value % 7
            col = 0
            cursor_x = rect.left - (band_value % 8)
            while cursor_x < rect.right:
                value = seed * 97 + row * 53 + col * 37
                slab_width = 8 + value % 9
                gap_left = 1 + (value // 7) % 4
                top_inset = 1 + (value // 13) % 3

                # A few absent plates create larger lava pools. Never remove
                # adjacent cells in these small fragments, preserving a clear
                # majority of traversable-looking basalt terrain.
                if value % 7 == 0 and (row + col) % 2:
                    cursor_x += slab_width
                    col += 1
                    continue
                left = max(rect.left, cursor_x + gap_left)
                top = max(rect.top, band_top + top_inset)
                right = min(
                    cursor_x + slab_width + (value // 19) % 3,
                    rect.right,
                )
                bottom = min(
                    band_top + band_height + (value // 23) % 3,
                    rect.bottom,
                )
                if right - left < 4 or bottom - top < 4:
                    cursor_x += slab_width
                    col += 1
                    continue

                plate = pygame.Rect(
                    left,
                    top,
                    right - left,
                    bottom - top,
                )
                notch = 2 + value % 2
                points = (
                    (plate.left + notch, plate.top),
                    (plate.right - 1, plate.top),
                    (plate.right - 1, plate.bottom - notch),
                    (plate.right - notch, plate.bottom - 1),
                    (plate.left, plate.bottom - 1),
                    (plate.left, plate.top + notch),
                )
                pygame.draw.polygon(surface, HELL_BASALT_COLORS[0], points)

                inner = tuple(
                    (
                        min(max(x, plate.left + 1), plate.right - 2),
                        min(max(y, plate.top + 1), plate.bottom - 2),
                    )
                    for x, y in points
                )
                pygame.draw.polygon(
                    surface,
                    HELL_BASALT_COLORS[2 + value % 2],
                    inner,
                )

                # Short angular fissures read as cracked rock from above.
                center_x = plate.centerx
                center_y = plate.centery
                fissure = (
                    (plate.left + 2, center_y - 1),
                    (center_x - 1, center_y),
                    (center_x + 1, center_y + 2),
                    (plate.right - 2, center_y + 1),
                )
                pygame.draw.lines(
                    surface,
                    HELL_BASALT_COLORS[0],
                    False,
                    fissure,
                    1,
                )
                if value % 4 == 0:
                    surface.set_at(
                        (center_x, center_y + 1),
                        HELL_LAVA_COLORS[2],
                    )
                cursor_x += slab_width
                col += 1
            band_top += band_height
            row += 1

        # Pinprick vents sit in the final terrain layer so the hottest lava
        # remains readable after the plates cover the flowing ground plane.
        for vent in range(max(2, rect.width // 16)):
            vx = rect.left + 3 + (
                seed * 7 + vent * 17 + phase
            ) % max(1, rect.width - 6)
            vy = rect.top + 3 + (
                seed * 11 + vent * 13
            ) % max(1, rect.height - 6)
            surface.set_at((vx, vy), HELL_LAVA_COLORS[3])
            surface.set_at((max(rect.left, vx - 1), vy), HELL_LAVA_COLORS[2])

        # A dark cut edge keeps each foreign-world fragment distinct against
        # the bright ocean without implying a side-facing wall or flame row.
        pygame.draw.rect(surface, HELL_BASALT_COLORS[0], rect, 1)
