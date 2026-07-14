"""Base class for everything that exists in the world.

An Entity has a position in world pixels, a hitbox, and update/draw
hooks. Chuck, NPCs, cigarettes, cats, and Astral Anchors are all
entities. Keeping this base minimal is deliberate — features are added
in subclasses, not here.
"""

from __future__ import annotations


class Entity:
    """A thing in the world with a position and a hitbox."""

    def __init__(self, x: float, y: float, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alive = True  # dead entities are removed by the WorldScene

    @property
    def hitbox(self):
        """Axis-aligned collision box (pygame.Rect) at the current position.

        pygame is imported lazily so entity logic stays unit-testable
        without pygame installed. (The player sprite anchors to this
        box's bottom edge — the hitbox is the FOOTPRINT.)
        """
        import pygame

        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        """Advance this entity by dt seconds. Override in subclasses."""

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """Draw this entity in screen space. Override in subclasses."""

    @property
    def sort_y(self) -> float:
        """Y value used for draw ordering (painter's algorithm).

        Entities lower on screen draw later, so Chuck correctly appears
        in front of / behind objects as he walks around them.
        """
        return self.y + self.height
