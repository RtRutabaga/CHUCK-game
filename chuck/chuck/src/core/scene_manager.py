"""Scene management.

Responsibilities:
    * Maintain a stack of Scene objects.
    * Route events, updates, and draw calls to the active (top) scene.
    * Provide push/pop/replace so scenes can transition without knowing
      about each other.

A stack (rather than a single current scene) is used so that later
features — a dialogue box, a pause overlay, the Astral Sea transition —
can be pushed on top of the world scene and popped off without tearing
the world down.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.core.game import Game
    from src.scenes.scene import Scene


class SceneManager:
    """Owns the scene stack. One instance, owned by Game."""

    def __init__(self, game: "Game") -> None:
        self.game = game
        self._stack: list["Scene"] = []

    # ------------------------------------------------------------------
    # Stack operations
    # ------------------------------------------------------------------
    def push(self, scene: "Scene") -> None:
        """Put a scene on top of the stack and notify it."""
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> None:
        """Remove the top scene and notify it."""
        if self._stack:
            self._stack.pop().on_exit()

    def replace(self, scene: "Scene") -> None:
        """Swap the top scene for a new one."""
        self.pop()
        self.push(scene)

    @property
    def current(self) -> "Scene | None":
        """The active scene, or None if the stack is empty."""
        return self._stack[-1] if self._stack else None

    # ------------------------------------------------------------------
    # Routing (called by Game each frame)
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """Forward an event to the active scene."""
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        """Update the active (top) scene only.

        The world deliberately freezes under an overlay: a conversation
        is a held breath, and no cat should ruin it. Revisit if an
        overlay ever wants ambient motion beneath it.
        """
        if self.current:
            self.current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the whole stack bottom-up, so overlays (a dialogue box)
        composite over the frozen world beneath them."""
        for scene in self._stack:
            scene.draw(surface)
