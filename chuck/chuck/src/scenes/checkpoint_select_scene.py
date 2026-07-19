"""Temporary development-only menu over the shared checkpoint registry."""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene


class CheckpointSelectScene(Scene):
    """Loads authored test entries through CheckpointLoader.load_checkpoint.

    The registry outgrew one screen (session 125), so entries page in
    screenfuls of two six-row columns: up/down walk the whole list and
    the page follows the selection, while left/right leap a full page.
    Small side arrows show when more pages exist in that direction.
    """

    PAGE_SIZE = 12  # two columns of six rows per screen

    def __init__(self, game) -> None:
        super().__init__(game)
        if not config.ENABLE_DEV_CHECKPOINT_SELECTOR:
            raise RuntimeError("Development checkpoint selector is disabled")
        self._font = game.assets.bitmap_font()
        self.checkpoints = game.checkpoints.development_checkpoints
        self._selected = 0

    @property
    def page(self) -> int:
        """The page holding the selection — paging follows the caret."""
        return self._selected // self.PAGE_SIZE

    @property
    def pages(self) -> int:
        return (len(self.checkpoints) + self.PAGE_SIZE - 1) // self.PAGE_SIZE

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.title_scene import TitleScene
            self.game.scenes.replace(TitleScene(self.game))

    def update(self, dt: float) -> None:
        del dt
        count = len(self.checkpoints)
        if self.game.input.was_pressed("move_up"):
            self._selected = (self._selected - 1) % count
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("move_down"):
            self._selected = (self._selected + 1) % count
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("move_right"):
            self._selected = (self._selected + self.PAGE_SIZE) % (
                self.pages * self.PAGE_SIZE
            )
            self._selected = min(self._selected, count - 1)
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("move_left"):
            self._selected = (self._selected - self.PAGE_SIZE) % (
                self.pages * self.PAGE_SIZE
            )
            self._selected = min(self._selected, count - 1)
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("interact"):
            checkpoint = self.checkpoints[self._selected]
            self.game.audio.play_sfx("interact")
            self.game.checkpoints.load_checkpoint(checkpoint.checkpoint_id)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 31))
        pygame.draw.rect(surface, (30, 28, 43), (22, 18, 276, 144))
        pygame.draw.rect(surface, config.COLOR_DIALOGUE_BORDER,
                         (22, 18, 276, 144), 1)
        heading = self._font.render("DEVELOPMENT CHECKPOINTS")
        surface.blit(heading, ((320 - heading.get_width()) // 2, 29))
        note = self._font.render("USES THE REAL CHECKPOINT LOADER")
        note.set_alpha(120)
        surface.blit(note, ((320 - note.get_width()) // 2, 44))

        rows_per_column = 6
        start = self.page * self.PAGE_SIZE
        for slot, checkpoint in enumerate(
                self.checkpoints[start:start + self.PAGE_SIZE]):
            index = start + slot
            caret = ">" if index == self._selected else " "
            label = self._font.render(f"{caret} {checkpoint.display_name}")
            column, row = divmod(slot, rows_per_column)
            surface.blit(label, (42 + column * 124, 64 + row * 13))

        # Side arrows whenever another page exists in that direction.
        arrow = config.COLOR_DIALOGUE_TEXT
        if self.page > 0:
            pygame.draw.polygon(surface, arrow,
                                ((32, 104), (38, 98), (38, 110)))
        if self.page < self.pages - 1:
            pygame.draw.polygon(surface, arrow,
                                ((288, 104), (282, 98), (282, 110)))
        if self.pages > 1:
            pager = self._font.render(
                f"PAGE {self.page + 1} OF {self.pages}")
            pager.set_alpha(140)
            surface.blit(pager, (42, 148))

        back = self._font.render("ESC BACK")
        back.set_alpha(140)
        surface.blit(back, (245, 148))
