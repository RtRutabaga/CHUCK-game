"""Phase 8's input-free escape from Hell into the Feywild.

Chuck is swept through a river caught between collided worlds. Infernal
basalt gives way to impossible Feywild growth, the current carries him over
a short waterfall, and he washes onto a quiet bank. The scene fades to black
and hands Chuck to the first playable Feywild riverbank.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene


FADE_IN_END = 2.8
MUSIC_START = 1.8
FEYWILD_GROW_START = 3.8
WATERFALL_START = 12.0
WATERFALL_END = 15.2
CALM_START = WATERFALL_END
SHORE_START = 20.0
ASHORE_TIME = 22.8
PRONE_END = 26.2
RISE_END = 29.8
FADE_OUT_START = 32.5
CUTSCENE_END = 35.0

_BASALT = (43, 30, 30)
_BASALT_LIGHT = (67, 42, 34)
_MOSS = (24, 66, 55)
_FEYWILD_GROUND = (22, 59, 55)
_DEEP_WATER = (10, 48, 78)
_WATER = (19, 119, 143)
_WATER_LIGHT = (83, 229, 206)
_FOAM = (191, 246, 226)
_LEAF_DARK = (15, 65, 48)
_LEAF = (38, 139, 76)
_LEAF_LIGHT = (85, 195, 96)
_MAGIC_BLUE = (75, 190, 255)
_MAGIC_VIOLET = (188, 83, 246)
_MAGIC_PINK = (244, 111, 193)
_GLOW_GOLD = (244, 211, 88)
_FLOWER = (
    _MAGIC_PINK, _GLOW_GOLD, (112, 151, 255), _MAGIC_VIOLET,
)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def _mix(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(
        round(start + (end - start) * amount)
        for start, end in zip(first, second)
    )


class FeywildRiverCutsceneScene(Scene):
    """Rushing river escape ending at a held, non-playable boundary."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.sanity = sanity
        self.elapsed = 0.0
        self._frames: dict[str, pygame.Surface] = {}
        self._handoff_started = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET,
            config.CHUCK_FRAME_W,
            config.CHUCK_FRAME_H,
        )
        self._frames = {
            "down": grid[0][0],
            "left": grid[2][0],
        }
        self.game.audio.stop_music(fade_ms=300)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < WATERFALL_START:
            return "rush"
        if self.elapsed < WATERFALL_END:
            return "waterfall"
        if self.elapsed < SHORE_START:
            return "calm"
        if self.elapsed < ASHORE_TIME:
            return "washing_ashore"
        if self.elapsed < PRONE_END:
            return "prone"
        if self.elapsed < RISE_END:
            return "rising"
        return "standing"

    @property
    def complete(self) -> bool:
        return self.elapsed >= CUTSCENE_END

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed = min(CUTSCENE_END, self.elapsed + dt)
        if previous < MUSIC_START <= self.elapsed:
            self.game.audio.play_music("fall_to_chult.wav", loop=False)
        if previous < WATERFALL_START <= self.elapsed:
            self.game.audio.play_sfx("jump")
        if previous < ASHORE_TIME <= self.elapsed:
            self.game.audio.play_sfx("chime")
        if self.elapsed >= CUTSCENE_END and not self._handoff_started:
            self._handoff_started = True
            self.game.checkpoints.load_checkpoint(
                "feywild_riverbank", sanity=self.sanity
            )

    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed >= SHORE_START:
            self._draw_quiet_bank(surface)
            self._draw_shore_chuck(surface)
        else:
            self._draw_moving_river(surface)
            self._draw_carried_chuck(surface)

        # Match the established cinematic letterbox without obscuring the
        # native-resolution composition.
        pygame.draw.rect(surface, (8, 19, 20), (0, 0, config.NATIVE_WIDTH, 7))
        pygame.draw.rect(
            surface,
            (8, 19, 20),
            (0, config.NATIVE_HEIGHT - 7, config.NATIVE_WIDTH, 7),
        )
        if self.elapsed < FADE_IN_END:
            self._draw_fade(
                surface, 1.0 - self.elapsed / FADE_IN_END
            )
        if self.elapsed >= FADE_OUT_START:
            self._draw_fade(
                surface,
                (self.elapsed - FADE_OUT_START)
                / (CUTSCENE_END - FADE_OUT_START),
            )

    def _draw_moving_river(self, surface: pygame.Surface) -> None:
        wild = _ease(
            (self.elapsed - FEYWILD_GROW_START)
            / (WATERFALL_START - FEYWILD_GROW_START)
        )
        calm = _ease(
            (self.elapsed - CALM_START) / (SHORE_START - CALM_START)
        )
        land = _mix(_BASALT, _FEYWILD_GROUND, wild)
        surface.fill(land)

        center = config.NATIVE_WIDTH // 2
        width = round(116 + calm * 34)
        river = (
            (center - width // 2, 0),
            (center + width // 2, 0),
            (center + width // 2 + round(math.sin(self.elapsed) * 6),
             config.NATIVE_HEIGHT),
            (center - width // 2 + round(math.sin(self.elapsed) * 6),
             config.NATIVE_HEIGHT),
        )
        pygame.draw.polygon(surface, _DEEP_WATER, river)
        pygame.draw.line(
            surface, _mix(_BASALT_LIGHT, _MOSS, wild),
            river[0], river[3], 3,
        )
        pygame.draw.line(
            surface, _mix(_BASALT_LIGHT, _MOSS, wild),
            river[1], river[2], 3,
        )

        speed = 116.0 * (1.0 - calm) + 35.0 * calm
        scroll = self.elapsed * speed
        for index in range(17):
            y = round((index * 17 - scroll) % 210) - 15
            x = center - width // 2 + 9 + (index * 37 % max(12, width - 26))
            length = 8 + index % 4 * 4
            color = _WATER_LIGHT if index % 3 else _WATER
            pygame.draw.line(surface, color, (x, y), (x + length, y), 2)

        self._draw_banks(surface, wild, scroll, center, width)
        if self.phase == "waterfall":
            self._draw_waterfall(surface, center, width)

    def _draw_banks(
        self,
        surface: pygame.Surface,
        wild: float,
        scroll: float,
        center: int,
        river_width: int,
    ) -> None:
        # The same deterministic objects recycle toward the camera. Their
        # density and color transform the basalt gorge into lush Feywild.
        for index in range(26):
            y = round((index * 31 - scroll * 0.72) % 230) - 25
            side = -1 if index % 2 == 0 else 1
            edge = center + side * (river_width // 2 + 8)
            distance = 18 + (index * 29 % 74)
            x = edge + side * distance
            if wild < 0.55:
                shade = _mix(_BASALT_LIGHT, _MOSS, wild)
                pygame.draw.polygon(
                    surface,
                    shade,
                    ((x - 7, y + 3), (x - 2, y - 5),
                     (x + 8, y - 2), (x + 6, y + 6)),
                )
            if wild <= 0.15:
                continue
            leaf = _mix(_MOSS, _LEAF, wild)
            pygame.draw.line(surface, _LEAF_DARK, (x, y + 7), (x, y - 5), 2)
            pygame.draw.ellipse(surface, leaf, (x - 9, y - 4, 10, 6))
            pygame.draw.ellipse(surface, leaf, (x, y - 7, 11, 7))
            pygame.draw.ellipse(surface, leaf, (x - 5, y - 11, 10, 8))
            if wild > 0.48:
                pygame.draw.ellipse(
                    surface, _mix(leaf, _LEAF_LIGHT, wild),
                    (x - side * 3, y - 8, 6, 4),
                )
            if wild > 0.62 and index % 3 == 0:
                flower = _FLOWER[(index // 3) % len(_FLOWER)]
                self._draw_glow(surface, x + side * 7, y - 4, flower, 5)
                pygame.draw.rect(
                    surface, flower, (x + side * 7, y - 4, 2, 2),
                )
            if wild > 0.74 and index % 7 == 0:
                self._draw_spiral_plant(
                    surface, x - side * 5, y + 4, side,
                    _MAGIC_BLUE if index % 2 else _MAGIC_VIOLET,
                )
            if wild > 0.82 and index % 8 == 2:
                self._draw_mushroom(surface, x, y + 5, index)

        if wild > 0.45:
            root_color = _mix((61, 42, 30), (85, 71, 40), wild)
            for index in range(5):
                y = round((index * 53 - scroll * 0.48) % 230) - 20
                side = -1 if index % 2 else 1
                edge = center + side * river_width // 2
                pygame.draw.line(
                    surface, root_color,
                    (edge + side * 3, y),
                    (edge + side * (27 + index * 4), y + 13),
                    4,
                )
                if wild > 0.78:
                    pygame.draw.line(
                        surface, _mix(root_color, _MAGIC_VIOLET, 0.35),
                        (edge + side * 5, y - 1),
                        (edge + side * (25 + index * 4), y + 11),
                        1,
                    )

    def _draw_waterfall(
        self,
        surface: pygame.Surface,
        center: int,
        width: int,
    ) -> None:
        progress = _clamp01(
            (self.elapsed - WATERFALL_START)
            / (WATERFALL_END - WATERFALL_START)
        )
        lip_y = round(
            config.NATIVE_HEIGHT + 12
            - _ease(min(1.0, progress * 1.7)) * 104
        )
        pygame.draw.rect(
            surface, _FOAM,
            (center - width // 2, lip_y, width, 4),
        )
        if progress > 0.43:
            plunge = _ease((progress - 0.43) / 0.57)
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((25, 107, 125, round(210 * plunge)))
            surface.blit(overlay, (0, 0))
            for x in range(8, config.NATIVE_WIDTH, 17):
                length = 12 + x % 23
                pygame.draw.line(
                    surface, _WATER_LIGHT,
                    (x, -3), (x - 2, length), 1,
                )

    def _draw_carried_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get("down")
        if frame is None:
            return
        x = config.NATIVE_WIDTH // 2 - frame.get_width() // 2
        y = 82 - frame.get_height() // 2
        if self.phase == "rush":
            x += round(math.sin(self.elapsed * 4.4) * 7)
            y += round(math.sin(self.elapsed * 7.1) * 2)
            angle = math.sin(self.elapsed * 3.1) * 18
        elif self.phase == "waterfall":
            progress = _clamp01(
                (self.elapsed - WATERFALL_START)
                / (WATERFALL_END - WATERFALL_START)
            )
            y += round(_ease(progress) * 28)
            angle = progress * 270
        else:
            x += round(math.sin(self.elapsed * 1.8) * 3)
            angle = math.sin(self.elapsed * 1.5) * 6
        image = pygame.transform.rotate(frame, angle)
        surface.blit(image, (x, y))

    def _draw_quiet_bank(self, surface: pygame.Surface) -> None:
        surface.fill((20, 55, 52))
        shore_x = 184
        pygame.draw.rect(surface, _DEEP_WATER, (0, 0, shore_x, 180))
        pygame.draw.polygon(
            surface, (35, 87, 61),
            ((shore_x - 13, 0), (shore_x + 4, 36), (shore_x - 7, 76),
             (shore_x + 9, 112), (shore_x - 4, 180), (320, 180),
             (320, 0)),
        )
        for y in range(10, 180, 18):
            x = 24 + (y * 7) % 118
            pygame.draw.line(surface, _WATER, (x, y), (x + 14, y), 1)
        for index in range(28):
            x = 192 + (index * 37 % 120)
            y = 10 + (index * 29 % 155)
            pygame.draw.ellipse(
                surface, _LEAF if index % 3 else _LEAF_DARK,
                (x - 6, y - 3, 12, 7),
            )
            if index % 3 == 0:
                color = _FLOWER[index % len(_FLOWER)]
                self._draw_glow(surface, x + 5, y - 2, color, 5)
                pygame.draw.rect(
                    surface, color, (x + 5, y - 2, 2, 2),
                )
            if index % 9 == 1:
                self._draw_mushroom(surface, x - 3, y + 5, index)
        for x, y, side, color in (
            (214, 43, 1, _MAGIC_BLUE),
            (292, 77, -1, _MAGIC_VIOLET),
            (244, 145, 1, _MAGIC_PINK),
        ):
            self._draw_spiral_plant(surface, x, y, side, color)
        # Human-scale roots frame the tiny rat without turning this endpoint
        # into a playable map.
        pygame.draw.line(surface, (91, 70, 42), (317, 23), (218, 57), 7)
        pygame.draw.line(surface, (72, 58, 36), (315, 150), (231, 129), 5)
        pygame.draw.line(surface, (111, 73, 77), (316, 24), (220, 56), 1)

    def _draw_shore_chuck(self, surface: pygame.Surface) -> None:
        """Show the whole landing: waterborne, prone, then slowly upright."""
        left = self._frames.get("left")
        down = self._frames.get("down")
        if left is None or down is None:
            return
        prone_x, prone_y = 205, 108
        if self.phase == "washing_ashore":
            wash = _ease(
                (self.elapsed - SHORE_START)
                / (ASHORE_TIME - SHORE_START)
            )
            x = round(142 + wash * (prone_x - 142))
            y = round(96 + wash * (prone_y - 96))
            angle = round(18 + wash * 72)
            image = pygame.transform.rotate(left, angle)
            surface.blit(image, (x, y))
            return
        if self.phase == "prone":
            image = pygame.transform.rotate(left, 90)
            surface.blit(image, (prone_x, prone_y))
            return
        if self.phase == "rising":
            rise = _ease(
                (self.elapsed - PRONE_END) / (RISE_END - PRONE_END)
            )
            if rise < 0.48:
                image = pygame.transform.rotate(
                    left, round(90 - rise / 0.48 * 48)
                )
            else:
                upright = _ease((rise - 0.48) / 0.52)
                height = max(
                    6,
                    round(down.get_height() * (0.55 + 0.45 * upright)),
                )
                image = pygame.transform.scale(
                    down, (down.get_width(), height)
                )
            surface.blit(
                image,
                (prone_x + 3, prone_y + left.get_height() - image.get_height()),
            )
            return
        surface.blit(
            down,
            (prone_x + 3, prone_y + left.get_height() - down.get_height()),
        )

    @staticmethod
    def _draw_glow(
        surface: pygame.Surface,
        x: int,
        y: int,
        color: tuple[int, int, int],
        radius: int,
    ) -> None:
        glow = pygame.Surface((radius * 2 + 1, radius * 2 + 1), pygame.SRCALPHA)
        pygame.draw.circle(
            glow, (*color, 28), (radius, radius), radius
        )
        pygame.draw.circle(
            glow, (*color, 50), (radius, radius), max(1, radius // 2)
        )
        surface.blit(glow, (x - radius, y - radius))

    @classmethod
    def _draw_spiral_plant(
        cls,
        surface: pygame.Surface,
        x: int,
        y: int,
        side: int,
        color: tuple[int, int, int],
    ) -> None:
        pygame.draw.line(surface, _LEAF_DARK, (x, y + 7), (x, y - 6), 2)
        points = []
        for step in range(13):
            angle = step * 0.82
            radius = 7 - step * 0.45
            points.append((
                round(x + side * math.cos(angle) * radius),
                round(y - 7 + math.sin(angle) * radius),
            ))
        cls._draw_glow(surface, x, y - 7, color, 8)
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 2)
        pygame.draw.ellipse(surface, _LEAF, (x - 7, y + 1, 7, 4))
        pygame.draw.ellipse(surface, _LEAF_LIGHT, (x + 1, y - 1, 7, 4))

    @staticmethod
    def _draw_mushroom(
        surface: pygame.Surface,
        x: int,
        y: int,
        seed: int,
    ) -> None:
        cap = _MAGIC_PINK if seed % 2 else _MAGIC_VIOLET
        pygame.draw.rect(surface, (205, 190, 151), (x, y, 2, 5))
        pygame.draw.ellipse(surface, cap, (x - 4, y - 3, 10, 5))
        pygame.draw.rect(surface, _FOAM, (x - 1, y - 1, 1, 1))

    @staticmethod
    def _draw_fade(surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, round(255 * _clamp01(amount))))
        surface.blit(overlay, (0, 0))
