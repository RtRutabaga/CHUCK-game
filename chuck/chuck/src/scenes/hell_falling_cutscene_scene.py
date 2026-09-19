"""Phase 7's input-free fall from the pirate ship into the Nine Hells.

The timing deliberately echoes the completed fall-to-Chult presentation and
reuses its music. Chuck falls through open heated air toward a distant
volcano; terrain appears only when the ground approaches. The scene then
reuses his established quiet death/return, look-around, and cigarette drag
before holding at the stable Phase 8 boundary.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.reality_blocks import HELL_BASALT_COLORS, HELL_LAVA_COLORS
from src.scenes.falling_cutscene_scene import (
    FallingCutsceneScene,
    MUSIC_START as CHULT_MUSIC_START,
    GROUND_APPROACH as CHULT_GROUND_APPROACH,
    IMPACT_TIME as CHULT_IMPACT_TIME,
    VANISH_TIME as CHULT_VANISH_TIME,
    RESPAWN_TIME as CHULT_RESPAWN_TIME,
    LOOK_START as CHULT_LOOK_START,
    CIGARETTE_START as CHULT_CIGARETTE_START,
    CIGARETTE_SEATED as CHULT_CIGARETTE_SEATED,
    DRAG_START as CHULT_DRAG_START,
    COMPLETE_TIME as CHULT_COMPLETE_TIME,
    CHULT_FADE_OUT_START,
    CHULT_HANDOFF_TIME,
)
from src.scenes.scene import Scene


HELL_MUSIC_START = CHULT_MUSIC_START
HELL_GROUND_APPROACH = CHULT_GROUND_APPROACH
HELL_IMPACT_TIME = CHULT_IMPACT_TIME
HELL_VANISH_TIME = CHULT_VANISH_TIME
HELL_RESPAWN_TIME = CHULT_RESPAWN_TIME
# The distant volcano climbs into view as Chuck falls: empty air, then its
# peak, then its full slopes. A slow rise (it is far away) that nonetheless
# makes the descent unmistakable while Chuck holds center screen.
VOLCANO_REVEAL_DELAY = 2.5   # seconds of empty sky before the peak appears
VOLCANO_RISE = 132           # how far it climbs from below the frame to full
VOLCANO_PEAK_Y = 55          # its crown, once fully revealed
VOLCANO_BASE_Y = 182         # its foot, flush past the bottom letterbox
HELL_LOOK_START = CHULT_LOOK_START
HELL_CIGARETTE_START = CHULT_CIGARETTE_START
HELL_CIGARETTE_SEATED = CHULT_CIGARETTE_SEATED
HELL_DRAG_START = CHULT_DRAG_START
HELL_ARRIVAL_TIME = CHULT_COMPLETE_TIME
# The tableau completes, then a fade hands Chuck off to playable
# Phlegethos (the start of Phase 8).
HELL_FADE_OUT_START = CHULT_FADE_OUT_START
HELL_HANDOFF_TIME = CHULT_HANDOFF_TIME
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

    pausable = True

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.sanity = sanity
        self.elapsed = 0.0
        self._handed_off = False
        self._frames: dict[str, pygame.Surface] = {}
        self._left_without_cigarette: pygame.Surface | None = None

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET,
            config.CHUCK_FRAME_W,
            config.CHUCK_FRAME_H,
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
        self.game.audio.stop_music(fade_ms=350)

    @property
    def phase(self) -> str:
        if self.elapsed < HELL_GROUND_APPROACH:
            return "fall"
        if self.elapsed < HELL_IMPACT_TIME:
            return "approach"
        if self.elapsed < HELL_VANISH_TIME:
            return "impact"
        if self.elapsed < HELL_RESPAWN_TIME:
            return "vanished"
        if self.elapsed < HELL_LOOK_START:
            return "return"
        if self.elapsed < HELL_CIGARETTE_START:
            return "look"
        if self.elapsed < HELL_CIGARETTE_SEATED:
            return "cigarette"
        if self.elapsed < HELL_ARRIVAL_TIME:
            return "smoke"
        return "arrived"

    @property
    def arrived(self) -> bool:
        return self.elapsed >= HELL_ARRIVAL_TIME

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= HELL_CIGARETTE_SEATED

    def update(self, dt: float) -> None:
        if self._handed_off:
            return
        previous = self.elapsed
        self.elapsed = min(HELL_HANDOFF_TIME, self.elapsed + dt)
        if previous < HELL_MUSIC_START <= self.elapsed:
            self.game.audio.play_music("fall_to_chult.wav", loop=False)
        if previous < HELL_IMPACT_TIME <= self.elapsed:
            self.game.audio.play_sfx("hurt")
        if previous < HELL_VANISH_TIME <= self.elapsed:
            self.game.audio.play_sfx("vanish")
            # He dies on the basalt, and it counts.
            self.game.deaths.record()
        if previous < HELL_RESPAWN_TIME <= self.elapsed:
            self.game.audio.play_sfx("respawn")
        if previous < HELL_HANDOFF_TIME <= self.elapsed:
            # The fade completes: Phase 8 begins on the Phlegethos ground.
            self._handed_off = True
            self.game.checkpoints.load_checkpoint(
                "phlegethos_arrival", sanity=self.sanity,
                progress_flags=set(self.game.progress.flags))

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_void(surface)
        self._draw_volcano(surface)
        self._draw_ground(surface)
        self._draw_chuck(surface)
        pygame.draw.rect(surface, (17, 12, 15), (0, 0, config.NATIVE_WIDTH, 7))
        pygame.draw.rect(
            surface,
            (17, 12, 15),
            (0, config.NATIVE_HEIGHT - 7, config.NATIVE_WIDTH, 7),
        )
        if self.elapsed >= HELL_FADE_OUT_START:
            frac = _clamp01(
                (self.elapsed - HELL_FADE_OUT_START)
                / (HELL_HANDOFF_TIME - HELL_FADE_OUT_START)
            )
            fade = pygame.Surface(surface.get_size())
            fade.set_alpha(round(255 * frac))
            surface.blit(fade, (0, 0))

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
        for index in range(22):
            x = (index * 47 + 19) % config.NATIVE_WIDTH
            y = (
                index * 31 - round(self.elapsed * (11 + index % 5))
            ) % config.NATIVE_HEIGHT
            color = (242, 91, 20) if index % 3 else (255, 161, 41)
            pygame.draw.rect(surface, color, (x, y, 1, 2))

    def _volcano_offset(self) -> int:
        """How far the volcano is pushed below its full position right now.

        Large early (the volcano is off the bottom of the frame — empty
        air), easing to zero as Chuck falls so the peak rises into view and
        then the whole mountain, its foot flush against the bottom."""
        reveal = _ease(_clamp01(
            (self.elapsed - VOLCANO_REVEAL_DELAY)
            / (HELL_GROUND_APPROACH - VOLCANO_REVEAL_DELAY)
        ))
        return round((1.0 - reveal) * VOLCANO_RISE)

    def _draw_volcano(self, surface: pygame.Surface) -> None:
        """A distant landmark that climbs into view as Chuck descends."""
        oy = self._volcano_offset()
        peak = VOLCANO_PEAK_Y
        base = VOLCANO_BASE_Y

        def shifted(points):
            return tuple((x, y + oy) for x, y in points)

        pygame.draw.polygon(surface, (34, 23, 25), shifted((
            (14, base), (56, 140), (90, 122), (118, 96), (142, 84),
            (158, peak + 11), (174, peak), (191, peak + 12),
            (210, 90), (240, 112), (268, 138), (311, base),
        )))
        pygame.draw.polygon(surface, (51, 28, 27), shifted((
            (56, base), (111, 111), (148, 90), (174, peak + 8),
            (202, 94), (272, base),
        )))
        # A broad dark crater lip and narrow lava scars establish scale
        # while keeping the mountain a distant silhouette.
        pygame.draw.polygon(surface, (20, 18, 20), shifted((
            (154, peak + 11), (174, peak + 5), (194, peak + 13),
            (185, peak + 18), (163, peak + 18),
        )))
        pygame.draw.line(surface, HELL_LAVA_COLORS[2],
                         (174, peak + 17 + oy), (164, 112 + oy), 2)
        pygame.draw.line(surface, HELL_LAVA_COLORS[1],
                         (164, 112 + oy), (151, base + oy), 1)
        pygame.draw.line(surface, HELL_LAVA_COLORS[1],
                         (185, peak + 17 + oy), (207, 122 + oy), 1)
        smoke_age = self.elapsed * 0.7
        for index in range(5):
            rise = (smoke_age * (6 + index) + index * 13) % 54
            x = 174 + round(math.sin(smoke_age + index) * (4 + index))
            y = peak + oy - 2 - round(rise)
            pygame.draw.rect(
                surface,
                (47 + index * 3, 35, 37),
                (x - 5 - index, y, 10 + index * 2, 4),
            )

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
        ground = pygame.Surface((config.NATIVE_WIDTH, height))
        self._draw_basalt_ground(ground)
        surface.blit(ground, (0, top))

    @staticmethod
    def _draw_basalt_ground(surface: pygame.Surface) -> None:
        """A mostly solid landing plane with only sparse molten fissures."""
        surface.fill(HELL_BASALT_COLORS[1])
        width, height = surface.get_size()
        for row, y in enumerate(range(2, height, 11)):
            offset = -7 if row % 2 else 0
            for col, x in enumerate(range(offset, width, 22)):
                shade = HELL_BASALT_COLORS[2 + (row + col) % 2]
                pygame.draw.polygon(
                    surface,
                    shade,
                    (
                        (x + 2, y),
                        (min(x + 20, width - 1), y + 1),
                        (min(x + 18, width - 1), min(y + 9, height - 1)),
                        (max(x + 1, 0), min(y + 8, height - 1)),
                    ),
                )
                pygame.draw.line(
                    surface,
                    HELL_BASALT_COLORS[0],
                    (max(x + 3, 0), min(y + 5, height - 1)),
                    (min(x + 10, width - 1), min(y + 7, height - 1)),
                    1,
                )
        pygame.draw.line(
            surface,
            HELL_BASALT_COLORS[0],
            (0, 0),
            (width, 0),
            2,
        )

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        if self.elapsed < HELL_IMPACT_TIME:
            self._draw_falling_chuck(surface)
            return
        self._draw_tableau_chuck(surface)

    def _draw_falling_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get("down")
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
        x = (
            config.NATIVE_WIDTH // 2 - width // 2
            + round(math.sin(self.elapsed * 1.6) * 2)
        )
        y = round(base_y + (landing_y - base_y) * landing)
        surface.blit(frame, (x, y))

    def _draw_tableau_chuck(self, surface: pygame.Surface) -> None:
        chuck_x = config.NATIVE_WIDTH // 2 - config.CHUCK_FRAME_W // 2
        chuck_y = HELL_GROUND_Y - config.CHUCK_FRAME_H
        jolt = 2 if self.elapsed < HELL_IMPACT_TIME + 0.1 else 0
        phase = self.phase
        if phase == "impact":
            frame = self._frames.get("down")
            if frame is not None:
                surface.blit(frame, (chuck_x, chuck_y + jolt))
        elif phase == "vanished":
            FallingCutsceneScene._draw_astral_blip(
                surface,
                chuck_x + 6,
                HELL_GROUND_Y - 7,
                self.elapsed - HELL_VANISH_TIME,
                returning=False,
            )
        elif phase == "return":
            progress = _clamp01(
                (self.elapsed - HELL_RESPAWN_TIME)
                / (HELL_LOOK_START - HELL_RESPAWN_TIME)
            )
            FallingCutsceneScene._draw_astral_blip(
                surface,
                chuck_x + 6,
                HELL_GROUND_Y - 7,
                progress,
                returning=True,
            )
            if int(progress * 8) % 2 == 1 or progress > 0.8:
                frame = self._frames.get("down")
                if frame is not None:
                    surface.blit(frame, (chuck_x, chuck_y))
        else:
            facing = self._facing_for_tableau()
            frame = self._frame_for_tableau(facing)
            if frame is not None:
                surface.blit(frame, (chuck_x, chuck_y))
        if phase == "cigarette":
            self._draw_cigarette_insert(surface, chuck_x, chuck_y)
        elif phase in {"smoke", "arrived"}:
            self._draw_drag(surface, chuck_x, chuck_y)

    def _facing_for_tableau(self) -> str:
        if self.elapsed < HELL_LOOK_START + 0.7:
            return "left"
        if self.elapsed < HELL_LOOK_START + 1.45:
            return "right"
        if self.elapsed < HELL_CIGARETTE_START:
            return "down"
        return "left"

    def _frame_for_tableau(self, facing: str) -> pygame.Surface | None:
        if facing == "left" and self.elapsed < HELL_CIGARETTE_SEATED:
            return self._left_without_cigarette
        if facing == "right" and self.elapsed < HELL_CIGARETTE_SEATED:
            if self._left_without_cigarette is None:
                return None
            return pygame.transform.flip(
                self._left_without_cigarette,
                True,
                False,
            )
        return self._frames.get(facing)

    def _draw_cigarette_insert(
        self,
        surface: pygame.Surface,
        chuck_x: int,
        chuck_y: int,
    ) -> None:
        progress = _ease(
            (self.elapsed - HELL_CIGARETTE_START)
            / (HELL_CIGARETTE_SEATED - HELL_CIGARETTE_START)
        )
        start = (chuck_x + 7, chuck_y + 10)
        end = (chuck_x - 1, chuck_y + 7)
        x = round(start[0] + (end[0] - start[0]) * progress)
        y = round(start[1] + (end[1] - start[1]) * progress)
        pygame.draw.line(surface, config.COLOR_CIG_PAPER, (x, y), (x + 2, y))
        pygame.draw.rect(surface, config.COLOR_CIG_EMBER, (x - 1, y, 1, 1))

    def _draw_drag(
        self,
        surface: pygame.Surface,
        chuck_x: int,
        chuck_y: int,
    ) -> None:
        ember = (
            (255, 184, 86)
            if int(self.elapsed * 6) % 2
            else config.COLOR_CIG_EMBER
        )
        pygame.draw.rect(surface, ember, (chuck_x - 1, chuck_y + 7, 1, 1))
        smoke_age = max(0.0, self.elapsed - HELL_DRAG_START)
        if smoke_age <= 0.0:
            return
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for index in range(4):
            age = (smoke_age - index * 0.38) % 1.7
            rise = round(age * 7)
            drift = round(math.sin(age * 3.0 + index) * 2)
            alpha = max(0, round(100 * (1.0 - age / 1.7)))
            pygame.draw.rect(
                layer,
                (178, 187, 177, alpha),
                (chuck_x - 1 + drift, chuck_y + 5 - rise, 2, 2),
            )
        surface.blit(layer, (0, 0))
