"""Chuck's long, two-scale ascent to Zephyros' tower.

The first shot stays close enough to read Chuck against an overwhelming wall;
the tower cannot possibly fit in that frame. A cloud-white scale cut then
reveals the complete tower from so far away that Chuck is no longer visible,
and holds while every stair is visibly drawn upward into the Aerie.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene


CLOSE_CLIMB_END = 8.5
SCALE_CUT_MID = 9.0
WIDE_START = 9.5
RETRACT_START = 10.5
RETRACT_END = 17.0
FADE_START = 18.3
CUTSCENE_END = 19.5

_STONE = (202, 200, 194)
_STONE_LIGHT = (232, 227, 211)
_STONE_DARK = (139, 143, 158)
_MORTAR = (116, 121, 141)
_SHADOW = (74, 73, 99)
_SKY = (116, 190, 226)
_CLOUD = (241, 248, 246)
_CLOUD_SHADE = (187, 216, 230)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class TowerArrivalCutsceneScene(Scene):
    """Input-free ascent from the Feywild to the exterior platform."""

    pausable = True

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

    @property
    def phase(self) -> str:
        if self.elapsed < CLOSE_CLIMB_END:
            return "close_climb"
        if self.elapsed < WIDE_START:
            return "scale_cut"
        if self.elapsed < RETRACT_END:
            return "wide_retraction"
        return "wide_hold"

    @property
    def chuck_visible(self) -> bool:
        """Chuck exists only in the readable close-scale composition."""
        return self.elapsed < SCALE_CUT_MID

    def update(self, dt: float) -> None:
        self.elapsed = min(CUTSCENE_END, self.elapsed + dt)
        if self.elapsed >= CUTSCENE_END and not self._handed_off:
            self._handed_off = True
            self.game.checkpoints.load_checkpoint(
                "zephyros_2", sanity=self._sanity,
                progress_flags=set(self.game.progress.flags),
            )

    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < SCALE_CUT_MID:
            self._draw_close_ascent(surface)
        else:
            self._draw_distant_tower(surface)

        # Clouds provide a soft but unmistakable cut between incompatible
        # scales, rather than pretending one camera could zoom this far.
        if CLOSE_CLIMB_END <= self.elapsed < WIDE_START:
            distance = abs(self.elapsed - SCALE_CUT_MID)
            amount = 1.0 - distance / (WIDE_START - SCALE_CUT_MID)
            self._white(surface, amount)

        pygame.draw.rect(surface, (20, 35, 57), (0, 0, 320, 7))
        pygame.draw.rect(surface, (20, 35, 57), (0, 173, 320, 7))
        if self.elapsed >= FADE_START:
            amount = (self.elapsed - FADE_START) / (
                CUTSCENE_END - FADE_START
            )
            self._black(surface, amount)

    # ------------------------------------------------------------------
    # Close scale: the wall is the world. No tower edge or sky can fit.
    # ------------------------------------------------------------------
    def _draw_close_ascent(self, surface: pygame.Surface) -> None:
        surface.fill(_STONE)
        pygame.draw.rect(surface, _STONE_LIGHT, (0, 0, 24, 180))
        pygame.draw.rect(surface, _STONE_DARK, (288, 0, 32, 180))

        # Giant blocks make Chuck's one-foot height legible without UI.
        course_h = 32
        for row, y in enumerate(range(7, 180, course_h)):
            pygame.draw.line(surface, _MORTAR, (0, y), (320, y), 3)
            offset = 34 if row % 2 else 91
            for x in range(offset, 320, 104):
                pygame.draw.line(surface, _MORTAR,
                                 (x, y), (x - 3, y + course_h - 3), 2)
        for x, y in ((46, 23), (154, 52), (261, 116), (83, 151)):
            pygame.draw.rect(surface, (213, 175, 77), (x, y, 3, 3))

        progress = _ease(self.elapsed / CLOSE_CLIMB_END)
        for index in range(17):
            t = index / 16
            x = round(25 + 238 * t)
            y = round(166 - 139 * t)
            width = round(49 - 16 * t)
            bob = round(math.sin(self.elapsed * 1.8 + index) * 1.5)
            pygame.draw.ellipse(surface, _CLOUD_SHADE,
                                (x - 5, y + 4 + bob, width + 10, 9))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x, y + bob, width, 8))

        if self._chuck is not None:
            x = round(31 + 224 * progress)
            y = round(151 - 130 * progress)
            bob = -1 if int(self.elapsed * 7) % 2 else 0
            surface.blit(self._chuck, (x, y + bob))

    # ------------------------------------------------------------------
    # Distant scale: complete tower, no visible Chuck, long retraction.
    # ------------------------------------------------------------------
    def _draw_distant_tower(self, surface: pygame.Surface) -> None:
        surface.fill(_SKY)
        self._draw_clouds(surface)
        pygame.draw.ellipse(surface, _CLOUD_SHADE, (92, 153, 139, 19))
        pygame.draw.ellipse(surface, _CLOUD, (99, 148, 125, 20))

        # A complete, needle-like tower fits from roof to cloud foundation.
        pygame.draw.rect(surface, _SHADOW, (124, 31, 74, 133))
        pygame.draw.polygon(surface, _STONE_DARK,
                            ((129, 28), (192, 28), (198, 163), (122, 163)))
        pygame.draw.polygon(surface, _STONE,
                            ((134, 28), (187, 28), (191, 163), (129, 163)))
        pygame.draw.polygon(surface, _STONE_LIGHT,
                            ((136, 28), (150, 28), (148, 163), (132, 163)))
        for y in range(42, 161, 14):
            pygame.draw.line(surface, _MORTAR, (132, y), (190, y), 1)
        for row, y in enumerate(range(42, 154, 28)):
            x = 159 if row % 2 else 145
            pygame.draw.line(surface, _MORTAR, (x, y), (x, y + 14))

        # High Aerie opening receives the staircase.
        pygame.draw.rect(surface, (20, 20, 34), (130, 59, 13, 22))
        pygame.draw.circle(surface, (20, 20, 34), (136, 59), 6)
        pygame.draw.polygon(surface, (50, 51, 126),
                            ((115, 30), (159, 3), (207, 30)))
        pygame.draw.polygon(surface, (76, 69, 158),
                            ((126, 27), (160, 7), (192, 27)))
        pygame.draw.rect(surface, (214, 171, 67), (112, 27, 98, 4))
        for x, y in ((145, 15), (166, 19), (181, 25)):
            surface.set_at((x, y), (247, 220, 105))

        for x, y, width, _progress in self._wide_step_layout():
            bob = round(math.sin(self.elapsed * 2.0 + x) * 1.0)
            pygame.draw.ellipse(surface, _CLOUD_SHADE,
                                (x - 3, y + 3 + bob, width + 6, 7))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x, y + bob, width, 6))

    def _wide_step_layout(self) -> list[tuple[int, int, int, float]]:
        """Return the distant stairs as they stream into the Aerie opening."""
        if self.elapsed <= RETRACT_START:
            progress = 0.0
        else:
            progress = _clamp01(
                (self.elapsed - RETRACT_START) / (RETRACT_END - RETRACT_START)
            )
        layout = []
        steps = 24
        entry_x, entry_y = 133, 66
        for index in range(steps):
            t = index / (steps - 1)
            base_x = 27 + 104 * t + math.sin(t * math.pi * 5) * 8
            base_y = 164 - 99 * t
            delay = t * 0.18
            local = _clamp01((progress - delay) / (1.0 - delay))
            local = _ease(local)
            if local >= 0.985:
                continue
            x = round(base_x + (entry_x - base_x) * local)
            y = round(base_y + (entry_y - base_y) * local)
            width = max(7, round((25 - 8 * t) * (1.0 - local * 0.55)))
            layout.append((x, y, width, local))
        return layout

    def _draw_clouds(self, surface: pygame.Surface) -> None:
        drift = self.elapsed * 2.0
        for index, (x, y, width) in enumerate(
            ((10, 39, 42), (62, 111, 53), (226, 57, 47), (256, 140, 66))
        ):
            x = int((x + drift * (0.35 + index * 0.06)) % 370 - 25)
            pygame.draw.ellipse(surface, (197, 225, 236),
                                (x, y + 5, width, 11))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x + 5, y, width // 2, 13))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x + width // 3, y + 2, width // 2, 12))

    @staticmethod
    def _white(surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((241, 248, 246))
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    @staticmethod
    def _black(surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))
