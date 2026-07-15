"""Temporary development-only menu over the shared checkpoint registry."""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene


class CheckpointSelectScene(Scene):
    """Loads authored test entries through CheckpointLoader.load_checkpoint."""

    def __init__(self, game) -> None:
        super().__init__(game)
        if not config.ENABLE_DEV_CHECKPOINT_SELECTOR:
            raise RuntimeError("Development checkpoint selector is disabled")
        self._font = game.assets.bitmap_font()
        self.checkpoints = game.checkpoints.development_checkpoints
        self._selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.title_scene import TitleScene
            self.game.scenes.replace(TitleScene(self.game))

    def update(self, dt: float) -> None:
        del dt
        if self.game.input.was_pressed("move_up"):
            self._selected = (self._selected - 1) % len(self.checkpoints)
            self.game.audio.play_sfx("interact")
        elif self.game.input.was_pressed("move_down"):
            self._selected = (self._selected + 1) % len(self.checkpoints)
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

        for index, checkpoint in enumerate(self.checkpoints):
            caret = ">" if index == self._selected else " "
            label = self._font.render(f"{caret} {checkpoint.display_name}")
            surface.blit(label, (72, 64 + index * 13))

        back = self._font.render("ESC BACK")
        back.set_alpha(140)
        surface.blit(back, (245, 148))
