"""Chuck ascends the Cloud Staircase to Zephyros' tower.

The first Phase 10 transition is a short, input-free side-view tableau. The
cloud stair pulls itself back into the tower behind Chuck before the game
returns to the ordinary top-down exterior platform.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene


CLIMB_END = 7.2
HOLD_END = 8.2
CUTSCENE_END = 9.2


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class TowerArrivalCutsceneScene(Scene):
    """Side-view climb from the Feywild into the cloud-borne tower."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self._sanity = sanity
        self._chuck: pygame.Surface | None = None
        self._handed_off = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._chuck = grid[1][0]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        self.elapsed = min(CUTSCENE_END, self.elapsed + dt)
        if self.elapsed >= CUTSCENE_END and not self._handed_off:
            self._handed_off = True
            self.game.checkpoints.load_checkpoint(
                "zephyros_2", sanity=self._sanity
            )

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((116, 190, 226))
        self._draw_clouds(surface)
        self._draw_tower(surface)
        self._draw_staircase(surface)
        self._draw_chuck(surface)

        pygame.draw.rect(surface, (20, 35, 57), (0, 0, 320, 7))
        pygame.draw.rect(surface, (20, 35, 57), (0, 173, 320, 7))
        if self.elapsed >= HOLD_END:
            fade = (self.elapsed - HOLD_END) / (CUTSCENE_END - HOLD_END)
            overlay = pygame.Surface(surface.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(round(255 * _clamp01(fade)))
            surface.blit(overlay, (0, 0))

    def _draw_clouds(self, surface: pygame.Surface) -> None:
        drift = self.elapsed * 3.0
        clouds = ((22, 35, 38), (92, 112, 54), (248, 61, 44), (8, 151, 63))
        for index, (x, y, width) in enumerate(clouds):
            x = int((x + drift * (0.45 + index * 0.08)) % 370 - 25)
            shade = (197, 225, 236)
            light = (235, 245, 246)
            pygame.draw.ellipse(surface, shade, (x, y + 5, width, 11))
            pygame.draw.ellipse(surface, light, (x + 5, y, width // 2, 13))
            pygame.draw.ellipse(surface, light, (x + width // 3, y + 2,
                                                 width // 2, 12))

    def _draw_tower(self, surface: pygame.Surface) -> None:
        # Zephyros' pale, absurdly tall tower: narrow walls and a crooked
        # wizard-hat roof preserve the broad silhouette of the supplied ref.
        pygame.draw.rect(surface, (99, 88, 108), (208, 33, 67, 147))
        pygame.draw.rect(surface, (224, 218, 205), (213, 31, 57, 149))
        pygame.draw.rect(surface, (244, 239, 220), (217, 31, 18, 149))
        for y in range(44, 172, 16):
            pygame.draw.line(surface, (173, 167, 164), (214, y), (269, y), 1)
        for y in range(52, 170, 32):
            pygame.draw.line(surface, (186, 180, 176), (242, y), (242, y + 8))
        # High arched entry receiving the last stair.
        pygame.draw.rect(surface, (31, 28, 44), (211, 72, 13, 25))
        pygame.draw.circle(surface, (31, 28, 44), (217, 72), 6)
        pygame.draw.polygon(surface, (51, 54, 132),
                            [(199, 32), (243, 4), (284, 32)])
        pygame.draw.polygon(surface, (78, 71, 163),
                            [(207, 29), (244, 8), (270, 29)])
        pygame.draw.rect(surface, (213, 170, 67), (196, 29, 91, 4))
        for x, y in ((230, 18), (251, 21), (264, 27)):
            surface.set_at((x, y), (245, 218, 104))

    def _draw_staircase(self, surface: pygame.Surface) -> None:
        progress = _ease(self.elapsed / CLIMB_END)
        steps = 18
        # Lower steps vanish one by one as the cloud stair retracts upward.
        first_visible = min(steps - 1, int(progress * (steps - 1)))
        for index in range(first_visible, steps):
            t = index / (steps - 1)
            x = round(48 + 164 * t)
            y = round(157 - 74 * t)
            width = round(28 - 12 * t)
            bob = round(math.sin(self.elapsed * 2.1 + index) * 1.5)
            pygame.draw.ellipse(surface, (187, 216, 230),
                                (x - 3, y + 3 + bob, width + 6, 7))
            pygame.draw.ellipse(surface, (241, 248, 246),
                                (x, y + bob, width, 7))

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        if self._chuck is None:
            return
        progress = _ease(min(self.elapsed, CLIMB_END) / CLIMB_END)
        x = round(53 + 155 * progress)
        y = round(145 - 75 * progress)
        bob = -1 if int(self.elapsed * 7) % 2 else 0
        surface.blit(self._chuck, (x, y + bob))
