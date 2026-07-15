"""Native-resolution title menu for starting or resuming CHUCK."""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene


class TitleScene(Scene):
    """Circa-1994 title screen: two real options and one gated dev option."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._font = game.assets.bitmap_font()
        self._selected = 0
        self._continue_available = game.checkpoints.can_continue

    @property
    def options(self) -> tuple[str, ...]:
        options = ["NEW GAME", "CONTINUE"]
        if config.ENABLE_DEV_CHECKPOINT_SELECTOR:
            options.append("DEV CHECKPOINTS")
        return tuple(options)

    @property
    def continue_available(self) -> bool:
        return self._continue_available

    def on_enter(self) -> None:
        self.game.audio.stop_music(fade_ms=250)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        del dt
        if self.game.input.was_pressed("move_up"):
            self._move(-1)
        elif self.game.input.was_pressed("move_down"):
            self._move(1)
        elif self.game.input.was_pressed("interact"):
            self._choose()

    def _enabled(self, index: int) -> bool:
        return index != 1 or self._continue_available

    def _move(self, direction: int) -> None:
        count = len(self.options)
        for _ in range(count):
            self._selected = (self._selected + direction) % count
            if self._enabled(self._selected):
                self.game.audio.play_sfx("interact")
                return

    def _choose(self) -> None:
        if not self._enabled(self._selected):
            return
        self.game.audio.play_sfx("interact")
        if self._selected == 0:
            self.game.checkpoints.new_game()
        elif self._selected == 1:
            self.game.checkpoints.continue_game()
        else:
            from src.scenes.checkpoint_select_scene import CheckpointSelectScene
            self.game.scenes.replace(CheckpointSelectScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((13, 16, 35))
        # A small, still Astral horizon: atmosphere without a modern menu skin.
        pygame.draw.rect(surface, (25, 29, 61), (0, 117, 320, 63))
        pygame.draw.line(surface, (75, 71, 111), (0, 117), (320, 117), 1)
        for x, y in ((19, 23), (52, 69), (94, 31), (140, 78), (181, 20),
                     (226, 60), (274, 29), (305, 83), (31, 103), (251, 99)):
            pygame.draw.rect(surface, config.COLOR_STAR, (x, y, 1, 1))

        title = self._font.render("CHUCK")
        title = pygame.transform.scale(title, (title.get_width() * 3,
                                                title.get_height() * 3))
        surface.blit(title, ((surface.get_width() - title.get_width()) // 2, 28))
        subtitle = self._font.render("A SMALL RAT IN A LARGE WORLD")
        surface.blit(subtitle, ((surface.get_width() - subtitle.get_width()) // 2,
                                64))

        y = 91
        for index, label in enumerate(self.options):
            caret = ">" if index == self._selected else " "
            rendered = self._font.render(f"{caret} {label}")
            if not self._enabled(index):
                rendered.set_alpha(70)
            surface.blit(rendered, (98, y + index * 15))

        prompt = self._font.render("UP / DOWN   E / ENTER")
        surface.blit(prompt, ((320 - prompt.get_width()) // 2, 158))
