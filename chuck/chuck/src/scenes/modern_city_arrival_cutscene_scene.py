"""Rainy descent, impact, and quiet return at the modern-city Ashtray."""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.city_rain import CityRain
from src.scenes.falling_cutscene_scene import FallingCutsceneScene
from src.scenes.scene import Scene


DESCENT_END = 8.2
IMPACT_TIME = 10.0
VANISH_TIME = 10.15
RESPAWN_TIME = 12.1
LOOK_START = 13.0
CIGARETTE_START = 16.0
CIGARETTE_SEATED = 17.0
DRAG_START = 17.1
FADE_OUT_START = 20.3
HANDOFF_TIME = FADE_OUT_START + config.AREA_FADE_DURATION
SIDEWALK_Y = 137


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class ModernCityArrivalCutsceneScene(Scene):
    """Input-free close flight through rain and established death/return."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self.starting_sanity = sanity
        self.sanity = sanity
        self.rain = CityRain()
        self._frames: dict[str, pygame.Surface] = {}
        self._left_without_cigarette: pygame.Surface | None = None
        self._handed_off = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._frames = {
            "down": grid[0][0],
            "up": grid[1][0],
            "left": grid[2][0],
            "right": pygame.transform.flip(grid[2][0], True, False),
        }
        self._left_without_cigarette = grid[2][0].copy()
        self._left_without_cigarette.set_at((0, 7), (0, 0, 0, 0))
        self._left_without_cigarette.set_at((1, 7), (0, 0, 0, 0))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < DESCENT_END:
            return "diagonal_descent"
        if self.elapsed < IMPACT_TIME:
            return "vertical_fall"
        if self.elapsed < VANISH_TIME:
            return "impact"
        if self.elapsed < RESPAWN_TIME:
            return "vanished"
        if self.elapsed < LOOK_START:
            return "return"
        if self.elapsed < CIGARETTE_START:
            return "look"
        if self.elapsed < CIGARETTE_SEATED:
            return "cigarette"
        return "smoke"

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= CIGARETTE_SEATED

    def chuck_position(self) -> tuple[int, int]:
        diagonal = _ease(self.elapsed / DESCENT_END)
        x = round(22 + 172 * diagonal)
        y = round(17 + 67 * diagonal + math.sin(self.elapsed * 2.0) * 2)
        if self.elapsed >= DESCENT_END:
            fall = _ease(
                (self.elapsed - DESCENT_END) / (IMPACT_TIME - DESCENT_END)
            )
            x = round(194 + 7 * (1.0 - fall))
            y = round(84 + (SIDEWALK_Y - config.CHUCK_FRAME_H - 84) * fall)
        return x, y

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += max(0.0, dt)
        self.rain.update(dt)
        cues = (
            (IMPACT_TIME, "hurt"),
            (VANISH_TIME, "vanish"),
            (RESPAWN_TIME, "respawn"),
        )
        for cue_time, sound in cues:
            if previous < cue_time <= self.elapsed:
                self.game.audio.play_sfx(sound)
        if previous < IMPACT_TIME <= self.elapsed:
            self.sanity = 0
        if previous < RESPAWN_TIME <= self.elapsed:
            self.sanity = config.SANITY_MAX
        if previous < HANDOFF_TIME <= self.elapsed and not self._handed_off:
            self._handed_off = True
            self.game.checkpoints.activate_checkpoint(
                "modern_city_anchor", config.SANITY_MAX
            )
            self.game.checkpoints.load_checkpoint(
                "modern_city_anchor", sanity=config.SANITY_MAX
            )

    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < IMPACT_TIME:
            self._draw_city_canyon(surface)
            self._draw_flying_chuck(surface)
        else:
            self._draw_sidewalk_tableau(surface)
        self.rain.draw(surface)
        pygame.draw.rect(surface, (8, 11, 18), (0, 0, 320, 7))
        pygame.draw.rect(surface, (8, 11, 18), (0, 173, 320, 7))
        if self.elapsed >= FADE_OUT_START:
            fade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = round(255 * _clamp01(
                (self.elapsed - FADE_OUT_START) / config.AREA_FADE_DURATION
            ))
            fade.fill((0, 0, 0, alpha))
            surface.blit(fade, (0, 0))

    def _draw_city_canyon(self, surface: pygame.Surface) -> None:
        surface.fill((28, 39, 55))
        # Passing concrete and window faces form a steep street canyon.
        for side in (-1, 1):
            if side < 0:
                points = ((0, 0), (105, 0), (78, 180), (0, 180))
                x0, x1 = 8, 74
            else:
                points = ((222, 0), (320, 0), (320, 180), (246, 180))
                x0, x1 = 247, 310
            pygame.draw.polygon(surface, (48, 52, 62), points)
            for row, y in enumerate(range(14, 165, 24)):
                for col, x in enumerate(range(x0, x1, 18)):
                    lit = (row * 3 + col * 5 + side) % 7 == 0
                    color = (188, 166, 93) if lit else (31, 68, 88)
                    pygame.draw.rect(surface, color, (x, y, 10, 8))
            pygame.draw.line(surface, (99, 105, 116), points[1], points[2], 2)
        horizon = round(138 - 18 * _ease(self.elapsed / DESCENT_END))
        pygame.draw.rect(surface, (17, 22, 30), (78, horizon, 168, 180 - horizon))
        for x in range(86, 243, 18):
            pygame.draw.line(surface, (68, 74, 83), (160, horizon), (x, 180), 1)

    def _draw_flying_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get("down")
        if frame is None:
            return
        x, y = self.chuck_position()
        tilt = round(-31 + 42 * _ease(self.elapsed / IMPACT_TIME))
        surface.blit(pygame.transform.rotate(frame, tilt), (x, y))

    def _draw_sidewalk_tableau(self, surface: pygame.Surface) -> None:
        surface.fill((25, 30, 38))
        pygame.draw.rect(surface, (53, 57, 66), (0, 28, 320, 109))
        for y in range(31, 132, 16):
            pygame.draw.line(surface, (39, 43, 51), (0, y), (319, y), 1)
        for row, y in enumerate(range(31, 132, 16)):
            offset = 14 if row % 2 else 0
            for x in range(offset, 320, 32):
                pygame.draw.line(surface, (73, 76, 82), (x, y), (x, y + 15), 1)
        pygame.draw.rect(surface, (104, 105, 104), (0, 137, 320, 8))
        pygame.draw.rect(surface, (19, 23, 31), (0, 145, 320, 35))
        pygame.draw.line(surface, (125, 145, 154), (0, 146), (319, 146), 1)

        # The first city Ashtray is present throughout the fixed tableau.
        anchor_x, anchor_y = 181, 130
        pygame.draw.rect(surface, (42, 40, 49), (anchor_x, anchor_y, 9, 5))
        pygame.draw.rect(surface, (116, 102, 120), (anchor_x + 1, anchor_y, 7, 1))
        pygame.draw.rect(surface, (204, 112, 62), (anchor_x + 6, anchor_y, 1, 1))

        chuck_x = 199
        chuck_y = SIDEWALK_Y - config.CHUCK_FRAME_H
        if self.phase == "impact":
            self._blit(self._frames.get("down"), surface, chuck_x, chuck_y)
        elif self.phase == "vanished":
            FallingCutsceneScene._draw_astral_blip(
                surface, chuck_x + 6, SIDEWALK_Y - 7,
                self.elapsed - VANISH_TIME, returning=False,
            )
        elif self.phase == "return":
            progress = _clamp01(
                (self.elapsed - RESPAWN_TIME) / (LOOK_START - RESPAWN_TIME)
            )
            FallingCutsceneScene._draw_astral_blip(
                surface, chuck_x + 6, SIDEWALK_Y - 7,
                progress, returning=True,
            )
            if int(progress * 8) % 2 == 1 or progress > 0.8:
                self._blit(self._frames.get("down"), surface, chuck_x, chuck_y)
        else:
            facing = self._facing()
            frame = self._frame(facing)
            self._blit(frame, surface, chuck_x, chuck_y)
            if self.phase == "cigarette":
                self._draw_cigarette_insert(surface, chuck_x, chuck_y)
            elif self.phase == "smoke":
                self._draw_drag(surface, chuck_x, chuck_y)

    @staticmethod
    def _blit(frame, surface: pygame.Surface, x: int, y: int) -> None:
        if frame is not None:
            surface.blit(frame, (x, y))

    def _facing(self) -> str:
        if self.elapsed < LOOK_START + 0.7:
            return "left"
        if self.elapsed < LOOK_START + 1.45:
            return "right"
        if self.elapsed < CIGARETTE_START:
            return "down"
        return "left"

    def _frame(self, facing: str) -> pygame.Surface | None:
        if facing == "left" and self.elapsed < CIGARETTE_SEATED:
            return self._left_without_cigarette
        if facing == "right" and self.elapsed < CIGARETTE_SEATED:
            if self._left_without_cigarette is None:
                return None
            return pygame.transform.flip(self._left_without_cigarette, True, False)
        return self._frames.get(facing)

    def _draw_cigarette_insert(
        self, surface: pygame.Surface, chuck_x: int, chuck_y: int
    ) -> None:
        progress = _ease(
            (self.elapsed - CIGARETTE_START)
            / (CIGARETTE_SEATED - CIGARETTE_START)
        )
        x = round(chuck_x + 7 - 8 * progress)
        y = round(chuck_y + 10 - 3 * progress)
        pygame.draw.line(surface, config.COLOR_CIG_PAPER, (x, y), (x + 2, y), 1)
        pygame.draw.rect(surface, config.COLOR_CIG_EMBER, (x - 1, y, 1, 1))

    def _draw_drag(
        self, surface: pygame.Surface, chuck_x: int, chuck_y: int
    ) -> None:
        ember = (255, 184, 86) if int(self.elapsed * 6) % 2 else config.COLOR_CIG_EMBER
        pygame.draw.rect(surface, ember, (chuck_x - 1, chuck_y + 7, 1, 1))
        smoke_age = max(0.0, self.elapsed - DRAG_START)
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for index in range(4):
            age = (smoke_age - index * 0.38) % 1.7
            rise = round(age * 7)
            drift = round(math.sin(age * 3.0 + index) * 2)
            alpha = max(0, round(100 * (1.0 - age / 1.7)))
            pygame.draw.rect(
                layer, (178, 187, 177, alpha),
                (chuck_x - 1 + drift, chuck_y + 5 - rise, 2, 2),
            )
        surface.blit(layer, (0, 0))
