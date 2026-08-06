"""Zephyros casually throws Chuck into a city-fractured sky.

Phase 10 slice 4 uses two honest scales.  First the complete tower fits in a
distant side view, making Chuck only a two-pixel dot in Zephyros' tiny hand.
Then a closer flight shot follows Chuck horizontally before gravity gradually
pulls him down.  Exact Astral fall-hazard tiles mingle with authored concrete
and office fragments until Chuck strikes one.  That impact is the stable
boundary before slice 5's rainy modern-city descent.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from src.core import config
from src.scenes.scene import Scene
from src.world.tileset_layout import ANIM_FPS, SEWER, TILE_PX


MUSIC_START = 0.9
THROW_RELEASE = 2.5
TOWER_SHOT_END = 6.2
ASTRAL_START = 7.5
CITY_START = 13.5
DESCENT_START = 16.0
COLLISION_START = 25.5
COLLISION_TIME = 27.0
CUTSCENE_END = 28.2

_SKY = (112, 183, 222)
_SKY_DEEP = (68, 131, 180)
_CLOUD = (236, 244, 242)
_CLOUD_SHADE = (188, 216, 229)
_STONE = (191, 194, 201)
_STONE_LIGHT = (224, 221, 210)
_STONE_DARK = (105, 111, 134)
_PURPLE = (69, 53, 123)
_GOLD = (216, 176, 70)
_CONCRETE = (103, 110, 122)
_CONCRETE_LIGHT = (146, 151, 157)
_CONCRETE_DARK = (58, 64, 76)
_WINDOW = (39, 72, 102)
_WINDOW_LIGHT = (204, 190, 119)
_SEAM = (104, 66, 170)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


@dataclass(frozen=True)
class FlightFragment:
    kind: str
    width: int
    height: int
    y: int
    speed: float
    delay: float
    offset: int


class ZephyrosLaunchCutsceneScene(Scene):
    """Input-free throw and horizontal inter-world flight."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self.sanity = sanity
        self._chuck: pygame.Surface | None = None
        self._astral_frames: tuple[pygame.Surface, ...] = ()
        self._music_started = False
        self._arrival_started = False
        self.fragments = (
            FlightFragment("astral", 48, 32, 17, 43.0, ASTRAL_START, 7),
            FlightFragment("astral", 32, 48, 118, 51.0, ASTRAL_START + 1.2, 41),
            FlightFragment("astral", 64, 32, 64, 47.0, ASTRAL_START + 2.5, 113),
            FlightFragment("astral", 32, 32, 145, 55.0, ASTRAL_START + 4.1, 171),
            FlightFragment("office", 72, 48, 20, 49.0, CITY_START, 24),
            FlightFragment("concrete", 54, 38, 127, 45.0, CITY_START + 1.4, 96),
            FlightFragment("office", 48, 72, 74, 53.0, CITY_START + 2.7, 164),
            FlightFragment("concrete", 76, 42, 6, 46.0, CITY_START + 4.0, 222),
            FlightFragment("office", 64, 54, 116, 52.0, CITY_START + 5.0, 283),
        )

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._chuck = pygame.transform.flip(grid[2][0], True, False)
        row_index = next(
            index
            for index, (name, _variants, _frames) in enumerate(SEWER.order)
            if name == "astral_void"
        )
        variants, frames = SEWER.info()["astral_void"]
        row = self.game.assets.tileset(SEWER.sheet, TILE_PX)[row_index]
        self._astral_frames = tuple(row[:variants * frames])
        self.game.audio.stop_music(fade_ms=650)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < TOWER_SHOT_END:
            return "tower_throw"
        if self.elapsed < DESCENT_START:
            return "horizontal_flight"
        if self.elapsed < COLLISION_TIME:
            return "descending_flight"
        return "city_fragment_collision"

    @property
    def complete(self) -> bool:
        return self.elapsed >= CUTSCENE_END

    @property
    def visible_fragment_kinds(self) -> set[str]:
        return {
            fragment.kind
            for fragment in self.fragments
            if self.elapsed >= fragment.delay
        }

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed = min(CUTSCENE_END, self.elapsed + max(0.0, dt))
        if previous < MUSIC_START <= self.elapsed and not self._music_started:
            self._music_started = True
            self.game.audio.play_music("fall_to_chult.wav", loop=False)
        if previous < CUTSCENE_END <= self.elapsed and not self._arrival_started:
            from src.scenes.modern_city_arrival_cutscene_scene import (
                ModernCityArrivalCutsceneScene,
            )
            self._arrival_started = True
            self.game.scenes.replace(
                ModernCityArrivalCutsceneScene(self.game, sanity=self.sanity)
            )

    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < TOWER_SHOT_END:
            self._draw_tower_throw(surface)
        else:
            self._draw_flight(surface)

        pygame.draw.rect(surface, (16, 27, 47), (0, 0, 320, 7))
        pygame.draw.rect(surface, (16, 27, 47), (0, 173, 320, 7))

    # ------------------------------------------------------------------
    # Whole tower: Chuck is too distant to be more than a moving dot.
    # ------------------------------------------------------------------
    def _draw_tower_throw(self, surface: pygame.Surface) -> None:
        surface.fill(_SKY)
        self._draw_cloud_field(surface, speed=3.0)
        pygame.draw.ellipse(surface, _CLOUD_SHADE, (19, 148, 150, 24))
        pygame.draw.ellipse(surface, _CLOUD, (28, 143, 132, 25))

        # The same tall, needle-like language as the arrival wide shot.
        pygame.draw.polygon(surface, _STONE_DARK,
                            ((51, 31), (111, 31), (121, 159), (39, 159)))
        pygame.draw.polygon(surface, _STONE,
                            ((57, 29), (106, 29), (114, 159), (46, 159)))
        pygame.draw.polygon(surface, _STONE_LIGHT,
                            ((59, 29), (72, 29), (68, 159), (49, 159)))
        for y in range(45, 158, 15):
            pygame.draw.line(surface, _STONE_DARK, (49, y), (112, y), 1)
        pygame.draw.polygon(surface, _PURPLE,
                            ((35, 31), (81, 3), (128, 31)))
        pygame.draw.polygon(surface, (91, 74, 157),
                            ((49, 28), (82, 8), (114, 28)))
        pygame.draw.rect(surface, _GOLD, (32, 28, 99, 4))

        # The Aerie slit, one tiny palm, and a tiny Chuck preserve honest scale.
        pygame.draw.rect(surface, (20, 22, 36), (48, 53, 18, 28))
        pygame.draw.circle(surface, (20, 22, 36), (57, 53), 9)
        hand_turn = _ease((self.elapsed - 1.0) / (THROW_RELEASE - 1.0))
        palm_x = round(61 + 10 * hand_turn)
        palm_y = round(60 - 4 * hand_turn)
        pygame.draw.ellipse(surface, (130, 142, 163),
                            (palm_x, palm_y, 17, 7))

        if self.elapsed < THROW_RELEASE:
            dot_x, dot_y = palm_x + 10, palm_y - 1
        else:
            flight = _ease(
                (self.elapsed - THROW_RELEASE)
                / (TOWER_SHOT_END - THROW_RELEASE)
            )
            dot_x = round(palm_x + 10 + 255 * flight)
            dot_y = round(palm_y - 1 - 31 * math.sin(flight * math.pi * 0.68))
        pygame.draw.rect(surface, (101, 62, 145), (dot_x, dot_y, 2, 2))

    # ------------------------------------------------------------------
    # Close flight: horizontal first, then a slow gravitational descent.
    # ------------------------------------------------------------------
    def _draw_flight(self, surface: pygame.Surface) -> None:
        surface.fill(_SKY)
        self._draw_cloud_field(surface, speed=18.0)
        for index, fragment in enumerate(self.fragments):
            if self.elapsed < fragment.delay:
                continue
            x = self._fragment_x(fragment)
            image = pygame.Surface(
                (fragment.width, fragment.height), pygame.SRCALPHA
            )
            if fragment.kind == "astral":
                self._draw_astral(image, index)
            elif fragment.kind == "office":
                self._draw_office_fragment(image, index)
            else:
                self._draw_concrete_fragment(image, index)
            surface.blit(image, (round(x), fragment.y))

        if self.elapsed >= COLLISION_START:
            self._draw_collision_fragment(surface)
        self._draw_flying_chuck(surface)

        if COLLISION_TIME <= self.elapsed < COLLISION_TIME + 0.34:
            amount = 1.0 - (self.elapsed - COLLISION_TIME) / 0.34
            overlay = pygame.Surface(surface.get_size())
            overlay.fill((235, 232, 216))
            overlay.set_alpha(round(180 * amount))
            surface.blit(overlay, (0, 0))

    def chuck_position(self) -> tuple[int, int]:
        local = max(0.0, self.elapsed - TOWER_SHOT_END)
        entry = _ease(local / 2.2)
        x = round(-16 + 128 * entry)
        if self.elapsed < DESCENT_START:
            y = 48 + round(math.sin(local * 1.2) * 2)
        else:
            fall = _ease(
                (self.elapsed - DESCENT_START)
                / (COLLISION_TIME - DESCENT_START)
            )
            y = round(48 + 50 * fall)
        return x, y

    def _draw_flying_chuck(self, surface: pygame.Surface) -> None:
        if self._chuck is None:
            return
        x, y = self.chuck_position()
        tilt = -18 if self.elapsed < DESCENT_START else round(
            -18 + 38 * _ease(
                (self.elapsed - DESCENT_START)
                / (COLLISION_TIME - DESCENT_START)
            )
        )
        frame = pygame.transform.rotate(self._chuck, tilt)
        surface.blit(frame, (x, y))

    def _fragment_x(self, fragment: FlightFragment) -> float:
        age = max(0.0, self.elapsed - fragment.delay)
        start = config.NATIVE_WIDTH + fragment.offset
        distance = start + fragment.width + 28
        return start - (age * fragment.speed % distance)

    def _draw_astral(self, surface: pygame.Surface, seed: int) -> None:
        if not self._astral_frames:
            surface.fill((12, 13, 35))
            return
        variants, frames = SEWER.info()["astral_void"]
        frame = int(self.elapsed * ANIM_FPS) % frames
        for row in range(math.ceil(surface.get_height() / TILE_PX)):
            for col in range(math.ceil(surface.get_width() / TILE_PX)):
                variant = (col * 31 + row * 17 + seed) % variants
                surface.blit(
                    self._astral_frames[variant * frames + frame],
                    (col * TILE_PX, row * TILE_PX),
                )

    def _draw_office_fragment(self, surface: pygame.Surface, seed: int) -> None:
        surface.fill(_CONCRETE_DARK)
        pygame.draw.polygon(
            surface, _CONCRETE,
            ((3, 0), (surface.get_width() - 1, 4),
             (surface.get_width() - 5, surface.get_height() - 1),
             (0, surface.get_height() - 7)),
        )
        for row, y in enumerate(range(7, surface.get_height() - 5, 13)):
            for col, x in enumerate(range(8, surface.get_width() - 7, 15)):
                color = _WINDOW_LIGHT if (row + col + seed) % 4 == 0 else _WINDOW
                pygame.draw.rect(surface, color, (x, y, 8, 6))
                pygame.draw.line(surface, _CONCRETE_LIGHT,
                                 (x - 2, y + 8), (x + 10, y + 8), 1)
        self._draw_fragment_seam(surface, seed)

    def _draw_concrete_fragment(self, surface: pygame.Surface, seed: int) -> None:
        surface.fill((0, 0, 0, 0))
        points = (
            (0, 5 + seed % 6),
            (surface.get_width() - 8, 0),
            (surface.get_width() - 1, surface.get_height() // 2),
            (surface.get_width() - 11, surface.get_height() - 1),
            (7, surface.get_height() - 5),
        )
        pygame.draw.polygon(surface, _CONCRETE, points)
        pygame.draw.line(surface, _CONCRETE_LIGHT,
                         points[0], points[1], 2)
        for index in range(3):
            x = 10 + (seed * 13 + index * 17) % max(12, surface.get_width() - 18)
            y = 8 + index * 8
            pygame.draw.line(surface, _CONCRETE_DARK,
                             (x, y), (x + 7, y + 5), 2)
        self._draw_fragment_seam(surface, seed)

    def _draw_fragment_seam(self, surface: pygame.Surface, seed: int) -> None:
        points = []
        for y in range(0, surface.get_height() + 1, 8):
            x = 2 + (seed * 11 + y * 3) % 6
            points.append((x, min(y, surface.get_height() - 1)))
        if len(points) > 1:
            pygame.draw.lines(surface, _SEAM, False, points, 2)

    def _draw_collision_fragment(self, surface: pygame.Surface) -> None:
        approach = _ease(
            (self.elapsed - COLLISION_START)
            / (COLLISION_TIME - COLLISION_START)
        )
        x = round(337 + (119 - 337) * approach)
        y = 76
        pygame.draw.polygon(surface, _CONCRETE_DARK,
                            ((x, y + 7), (x + 70, y), (x + 76, y + 67),
                             (x + 8, y + 72), (x - 5, y + 40)))
        pygame.draw.polygon(surface, _CONCRETE,
                            ((x + 4, y + 9), (x + 65, y + 4),
                             (x + 69, y + 61), (x + 10, y + 65)))
        for wx in (x + 14, x + 37):
            for wy in (y + 18, y + 38):
                pygame.draw.rect(surface, _WINDOW, (wx, wy, 14, 9))
        pygame.draw.line(surface, _SEAM,
                         (x + 5, y + 10), (x + 9, y + 64), 2)
        if self.elapsed >= COLLISION_TIME:
            hit_x, hit_y = self.chuck_position()
            for radius, color in ((10, (235, 232, 216)), (6, _GOLD), (3, (255, 255, 244))):
                pygame.draw.circle(surface, color, (hit_x + 9, hit_y + 7), radius, 1)

    def _draw_cloud_field(self, surface: pygame.Surface, *, speed: float) -> None:
        scroll = self.elapsed * speed
        for index, (base_x, y, width) in enumerate(
            ((7, 30, 46), (85, 116, 61), (181, 42, 55), (271, 139, 66))
        ):
            x = round((base_x - scroll * (0.7 + index * 0.08)) % 390) - 40
            pygame.draw.ellipse(surface, _CLOUD_SHADE,
                                (x, y + 5, width, 11))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x + 5, y, width // 2, 13))
            pygame.draw.ellipse(surface, _CLOUD,
                                (x + width // 3, y + 2, width // 2, 12))
