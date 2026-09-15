"""Base class for all scenes.

A Scene is one self-contained mode of the game: the world, a dialogue
overlay, the Astral Sea transition, a title screen. Scenes never talk
to each other directly — they ask the SceneManager to push/pop/replace.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.core.game import Game


class Scene:
    """Abstract base scene. Subclass and override the hooks you need."""

    # Esc opens the pause menu over this scene. Play and cutscenes pause;
    # menus, the title and the dialogue box handle Esc themselves.
    pausable = False

    def __init__(self, game: "Game") -> None:
        self.game = game

    def on_enter(self) -> None:
        """Called once when this scene becomes active (pushed)."""

    def on_exit(self) -> None:
        """Called once when this scene is removed (popped)."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """React to a single pygame event."""

    def update(self, dt: float) -> None:
        """Advance this scene's state by dt seconds."""

    def draw(self, surface: pygame.Surface) -> None:
        """Draw this scene onto the native render surface."""
