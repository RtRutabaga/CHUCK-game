"""Contained Phase 3 falling-cutscene handoff.

This scene owns presentation after the successful pantry sky fall. It removes
normal world control and establishes the native-scale sky/cloud language. The
authored long descent and final Phase 4 endpoint are deliberately later slices.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene


SKY_TOP = (28, 139, 156)
SKY_BOTTOM = (43, 166, 166)
CLOUD = (208, 234, 218)
CLOUD_SHADE = (151, 204, 197)


class FallingCutsceneScene(Scene):
    """An input-free, open-ended first shot of Chuck's long descent."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        # x, y, width, speed: two restrained parallax layers.
        self.clouds = [
            [18.0, 154.0, 42, 18.0],
            [210.0, 118.0, 64, 24.0],
            [92.0, 52.0, 38, 14.0],
            [262.0, 20.0, 48, 12.0],
        ]
        self._chuck = None

    def on_enter(self) -> None:
        self._chuck = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )[0][0]
        # The warm tavern cue ends at the authored cut from gameplay.
        self.game.audio.stop_music(fade_ms=350)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        self.elapsed += dt
        for cloud in self.clouds:
            cloud[1] -= cloud[3] * dt
            if cloud[1] < -18:
                cloud[1] += config.NATIVE_HEIGHT + 36

    def draw(self, surface: pygame.Surface) -> None:
        # A simple vertical teal grade, quantized into native-pixel bands.
        for y in range(config.NATIVE_HEIGHT):
            t = y / max(1, config.NATIVE_HEIGHT - 1)
            color = tuple(
                round(a + (b - a) * t) for a, b in zip(SKY_TOP, SKY_BOTTOM)
            )
            pygame.draw.line(surface, color, (0, y), (config.NATIVE_WIDTH, y))

        for index, (x, y, width, _speed) in enumerate(self.clouds):
            self._draw_cloud(surface, round(x), round(y), width, index % 2)

        if self._chuck is not None:
            # Continue from the tiny end of the gameplay fall, then reframe
            # Chuck at readable cutscene scale without squash or panic.
            intro = min(1.0, self.elapsed / 0.45)
            scale = 0.25 + intro * 0.75
            width = max(2, round(config.CHUCK_FRAME_W * scale))
            height = max(3, round(config.CHUCK_FRAME_H * scale))
            frame = pygame.transform.scale(self._chuck, (width, height))
            sway = round(math.sin(self.elapsed * 1.7))
            draw_x = config.NATIVE_WIDTH // 2 - width // 2 + sway
            draw_y = 78 - height // 2
            surface.blit(frame, (draw_x, draw_y))

        # Restrained letterbox bars make the scene read as authored presentation.
        pygame.draw.rect(surface, (20, 31, 39), (0, 0, config.NATIVE_WIDTH, 7))
        pygame.draw.rect(
            surface, (20, 31, 39),
            (0, config.NATIVE_HEIGHT - 7, config.NATIVE_WIDTH, 7),
        )

    @staticmethod
    def _draw_cloud(
        surface: pygame.Surface, x: int, y: int, width: int, layer: int
    ) -> None:
        height = 8 if layer == 0 else 11
        shade = CLOUD_SHADE if layer == 0 else (165, 213, 204)
        pygame.draw.rect(surface, shade, (x, y + 4, width, height - 2))
        pygame.draw.rect(surface, CLOUD, (x + 5, y + 2, width - 10, height - 1))
        pygame.draw.rect(surface, CLOUD, (x + width // 3, y, width // 3, height))
