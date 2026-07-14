"""Dialogue scene — an overlay pushed on top of the frozen world.

Responsibilities:
    * Play a linear sequence of lines through the DialogueBox.
    * Interact press: complete the typewriter if mid-reveal, otherwise
      advance to the next line; after the last line, pop back to the
      world.
    * Optionally end on a CHOICE: once the last line has finished
      typing, options appear; up/down moves the caret, interact picks.
      The chosen option's dialogue then plays as a normal sequence, and
      its `on_choice` callback fires (the caller decides what a YES
      means — this scene only reports it).

The world scene below keeps drawing (SceneManager draws the stack
bottom-up) but stops updating: a conversation is a held breath.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.scenes.scene import Scene
from src.systems.choice import Choice
from src.ui.choice_box import ChoiceBox
from src.ui.dialogue_box import DialogueBox

if TYPE_CHECKING:
    from src.core.game import Game


class DialogueScene(Scene):
    """One conversation, start to finish."""

    def __init__(
        self,
        game: "Game",
        lines: list[str],
        choice: Choice | None = None,
        dialogue=None,
        on_choice=None,
    ) -> None:
        """`choice` needs `dialogue` (a DialogueSystem) to look up the
        lines of whichever branch the player picks."""
        super().__init__(game)
        if not lines:
            raise ValueError("DialogueScene needs at least one line")
        if choice is not None and dialogue is None:
            raise ValueError("A choice needs a DialogueSystem to resolve it")
        self._dialogue = dialogue
        self._lines = lines
        self._index = 0
        self._box = DialogueBox(game.assets)
        self._choice = choice
        self._on_choice = on_choice
        self._selected = 0
        self._choice_box = ChoiceBox(game.assets) if choice else None

    def on_enter(self) -> None:
        self.game.audio.play_sfx("interact")
        self._box.show(self._lines[self._index])

    @property
    def choosing(self) -> bool:
        """True while the options are up and waiting for an answer."""
        return (
            self._choice is not None
            and self._index == len(self._lines) - 1
            and self._box.is_complete
        )

    def update(self, dt: float) -> None:
        self._box.update(dt)

        if self.choosing:
            self._update_choice()
            return

        if self.game.input.was_pressed("interact"):
            if not self._box.is_complete:
                self._box.complete()
            elif self._index + 1 < len(self._lines):
                self._index += 1
                self.game.audio.play_sfx("interact")
                self._box.show(self._lines[self._index])
            else:
                self.game.scenes.pop()

    def _update_choice(self) -> None:
        """Move the caret; interact commits."""
        count = len(self._choice.options)
        if self.game.input.was_pressed("move_up"):
            self._selected = (self._selected - 1) % count
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("move_down"):
            self._selected = (self._selected + 1) % count
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("interact"):
            option = self._choice.options[self._selected]
            self.game.audio.play_sfx("interact")
            if self._on_choice is not None:
                self._on_choice(option)
            if option.goto is not None:
                # A navigation choice, not a spoken one: no lines to
                # read — close now and let the world act on the goto.
                self.game.scenes.pop()
                return
            # A spoken branch becomes an ordinary conversation.
            self._lines = self._dialogue.get(option.dialogue)
            self._index = 0
            self._choice = None
            self._box.show(self._lines[0])

    def handle_event(self, event: pygame.event.Event) -> None:
        """ESC also closes the conversation (politely)."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.scenes.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Only the box: the world beneath drew itself already."""
        self._box.draw(surface)
        if self.choosing:
            self._choice_box.draw(
                surface,
                [o.label for o in self._choice.options],
                self._selected,
            )
