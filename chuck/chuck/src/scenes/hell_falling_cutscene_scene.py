"""Phase 7's input-free fall from the pirate ship into the Nine Hells.

The timing deliberately echoes the completed fall-to-Chult presentation and
reuses its music. This scene stops on an arrived tableau: Phase 8 can replace
that boundary with playable content without Phase 7 inventing its first map.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.reality_blocks import RealityBlockField
from src.scenes.scene import Scene


HELL_MUSIC_START = 4.0
HELL_GROUND_APPROACH = 26.2
HELL_IMPACT_TIME = 29.0
HELL_ARRIVAL_TIME = 31.0
HELL_GROUND_Y = 132


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def _mix_color(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(
        round(start + (end - start) * amount)
        for start, end in zip(first, second)
    )


class HellFallingCutsceneScene(Scene):
    """A long volcanic descent ending at the stable Phase 8 boundary."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.sanity = sanity
        self.elapsed = 0.0
        self._music_started = False
        self._impact_sounded = False
        self._chuck_frame: pygame.Surface | None = None
        self._terrain = RealityBlockField(0, 0)
        # x, y, width, height, upward speed. Different sizes and offsets keep
        # the fall from becoming another aligned tile stream.
        self.fragments = [
            [18.0, 164.0, 48, 32, 22.0],
            [226.0, 116.0, 64, 32, 29.0],
            [105.0, 42.0, 32, 48, 18.0],
            [278.0, 14.0, 48, 48, 25.0],
            [-12.0, 75.0, 64, 32, 31.0],
            [160.0, 192.0, 48, 32, 35.0],
            [67.0, 129.0, 32, 32, 26.0],
        ]

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET,
            config.CHUCK_FRAME_W,
            config.CHUCK_FRAME_H,
        )
        self._chuck_frame = grid[0][0]
        self.game.audio.stop_music(fade_ms=350)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < HELL_GROUND_APPROACH:
            return "fall"
        if self.elapsed < HELL_IMPACT_TIME:
            return "approach"
        if self.elapsed < HELL_ARRIVAL_TIME:
            return "impact"
        return "arrived"

    @property
    def arrived(self) -> bool:
        return self.elapsed >= HELL_ARRIVAL_TIME

    def update(self, dt: float) -> None:
        if self.arrived:
            return
        previous = self.elapsed
        self.elapsed = min(HELL_ARRIVAL_TIME, self.elapsed + dt)
        self._terrain.age = self.elapsed

        if previous < HELL_MUSIC_START <= self.elapsed:
            self._music_started = True
            self.game.audio.play_music("fall_to_chult.wav", loop=False)
        if previous < HELL_IMPACT_TIME <= self.elapsed:
            self._impact_sounded = True
            self.game.audio.play_sfx("hurt")

        span = config.NATIVE_HEIGHT + 72
        for fragment in self.fragments:
            fragment[1] = (
                (fragment[1] - fragment[4] * dt + 40) % span
            ) - 40

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_void(surface)
        if self.elapsed < HELL_IMPACT_TIME:
            self._draw_fragments(surface)
        self._draw_ground(surface)
        self._draw_chuck(surface)
        pygame.draw.rect(surface, (17, 12, 15), (0, 0, config.NATIVE_WIDTH, 7))
        pygame.draw.rect(
            surface,
            (17, 12, 15),
            (0, config.NATIVE_HEIGHT - 7, config.NATIVE_WIDTH, 7),
        )

    def _draw_void(self, surface: pygame.Surface) -> None:
        heat = _ease(self.elapsed / HELL_IMPACT_TIME)
        top = _mix_color((17, 12, 20), (45, 13, 13), heat)
        bottom = _mix_color((43, 16, 21), (105, 27, 12), heat)
        for y in range(config.NATIVE_HEIGHT):
            amount = y / max(1, config.NATIVE_HEIGHT - 1)
            pygame.draw.line(
                surface,
                _mix_color(top, bottom, amount),
                (0, y),
                (config.NATIVE_WIDTH, y),
            )
        # Thin rising sparks create depth without modern particle effects.
        for index in range(22):
            x = (index * 47 + 19) % config.NATIVE_WIDTH
            y = (
                index * 31 - round(self.elapsed * (11 + index % 5))
            ) % config.NATIVE_HEIGHT
            color = (242, 91, 20) if index % 3 else (255, 161, 41)
            pygame.draw.rect(surface, color, (x, y, 1, 2))

    def _draw_fragments(self, surface: pygame.Surface) -> None:
        for seed, (x, y, width, height, _speed) in enumerate(self.fragments):
            image = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
            self._terrain._draw_hell(image, image.get_rect(), seed + 13)
            sway = round(math.sin(self.elapsed * 0.7 + seed) * 2)
            surface.blit(image, (round(x) + sway, round(y)))

    def _ground_top(self) -> int:
        if self.elapsed < HELL_GROUND_APPROACH:
            return config.NATIVE_HEIGHT + 18
        progress = _ease(
            (self.elapsed - HELL_GROUND_APPROACH)
            / (HELL_IMPACT_TIME - HELL_GROUND_APPROACH)
        )
        return round(
            config.NATIVE_HEIGHT + 18
            + (HELL_GROUND_Y - config.NATIVE_HEIGHT - 18) * progress
        )

    def _draw_ground(self, surface: pygame.Surface) -> None:
        top = self._ground_top()
        if top >= config.NATIVE_HEIGHT:
            return
        height = config.NATIVE_HEIGHT - top
        ground = pygame.Surface((config.NATIVE_WIDTH, height), pygame.SRCALPHA)
        self._terrain._draw_hell(ground, ground.get_rect(), seed=29)
        surface.blit(ground, (0, top))

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        frame = self._chuck_frame
        if frame is None:
            return
        intro = _ease(self.elapsed / 0.5)
        scale = 0.3 + intro * 0.7
        width = max(2, round(frame.get_width() * scale))
        height = max(3, round(frame.get_height() * scale))
        frame = pygame.transform.scale(frame, (width, height))

        base_y = 78 - height // 2
        landing_y = HELL_GROUND_Y - height
        landing = _ease(
            (self.elapsed - HELL_GROUND_APPROACH)
            / (HELL_IMPACT_TIME - HELL_GROUND_APPROACH)
        )
        jolt = 2 if HELL_IMPACT_TIME <= self.elapsed < HELL_IMPACT_TIME + 0.1 else 0
        x = config.NATIVE_WIDTH // 2 - width // 2
        if self.elapsed < HELL_GROUND_APPROACH:
            x += round(math.sin(self.elapsed * 1.6) * 2)
        y = round(base_y + (landing_y - base_y) * landing) + jolt
        surface.blit(frame, (x, y))
