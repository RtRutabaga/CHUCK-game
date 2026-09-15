"""Phase 3's contained fall from the Waterdeep pantry into Chult.

The sequence is deliberately authored inside one input-free scene: an almost
too-long sky descent, a violent passage through the canopy, impact, Chuck's
familiar quiet death/return, and a final cigarette drag in the jungle. The
tableau holds at the clean Phase 4 boundary; playable Chult is not built here.
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

CANOPY_START = 24.0
MUSIC_START = 4.0
GROUND_APPROACH = 26.2
IMPACT_TIME = 29.0
VANISH_TIME = 29.15
RESPAWN_TIME = 31.1
LOOK_START = 32.0
CIGARETTE_START = 35.0
CIGARETTE_SEATED = 36.0
DRAG_START = 36.1
COMPLETE_TIME = 39.0
CHULT_FADE_OUT_START = 41.0
CHULT_HANDOFF_TIME = CHULT_FADE_OUT_START + config.AREA_FADE_DURATION
GROUND_Y = 132


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def _mix_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


class FallingCutsceneScene(Scene):
    """The complete input-free Phase 3 descent and jungle endpoint."""

    pausable = True

    def __init__(self, game) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        # x, y, width, speed: enough irregular layers to sustain the long hold.
        self.clouds = [
            [18.0, 154.0, 42, 18.0],
            [210.0, 118.0, 64, 24.0],
            [92.0, 52.0, 38, 14.0],
            [262.0, 20.0, 48, 12.0],
            [-22.0, 84.0, 55, 21.0],
            [145.0, 176.0, 34, 27.0],
            [284.0, 148.0, 43, 16.0],
            [48.0, 12.0, 70, 11.0],
            [184.0, 66.0, 29, 19.0],
        ]
        self._frames: dict[str, pygame.Surface] = {}
        self._left_without_cigarette: pygame.Surface | None = None

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
        # The profile source art already carries Chuck's usual cigarette. Keep
        # a clean copy so this scene can show him actually putting it in.
        self._left_without_cigarette = grid[2][0].copy()
        self._left_without_cigarette.set_at((0, 7), (0, 0, 0, 0))
        self._left_without_cigarette.set_at((1, 7), (0, 0, 0, 0))
        self.game.audio.stop_music(fade_ms=350)

    @property
    def phase(self) -> str:
        if self.elapsed < CANOPY_START:
            return "fall"
        if self.elapsed < IMPACT_TIME:
            return "canopy"
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
        if self.elapsed < COMPLETE_TIME:
            return "smoke"
        return "complete"

    @property
    def cutscene_complete(self) -> bool:
        return self.elapsed >= COMPLETE_TIME

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= CIGARETTE_SEATED

    @property
    def fade_out_progress(self) -> float:
        return _clamp01(
            (self.elapsed - CHULT_FADE_OUT_START) / config.AREA_FADE_DURATION
        )

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += dt
        span = config.NATIVE_HEIGHT + 36
        for cloud in self.clouds:
            cloud[1] = ((cloud[1] - cloud[3] * dt + 18) % span) - 18
        self._play_cues(previous, self.elapsed)
        if previous < CHULT_HANDOFF_TIME <= self.elapsed:
            self.game.checkpoints.load_checkpoint("chult_landing")

    def _play_cues(self, previous: float, current: float) -> None:
        if previous < MUSIC_START <= current:
            self.game.audio.play_music("fall_to_chult.wav", loop=False)
        cues = (
            (CANOPY_START + 0.7, "scratch"),
            (CANOPY_START + 2.2, "scratch"),
            (IMPACT_TIME, "hurt"),
            (VANISH_TIME, "vanish"),
            (RESPAWN_TIME, "respawn"),
        )
        for cue_time, sound in cues:
            if previous < cue_time <= current:
                self.game.audio.play_sfx(sound)
        # He dies on the jungle floor: the same quiet vanish as any death.
        if previous < VANISH_TIME <= current:
            self.game.deaths.record()

    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < IMPACT_TIME:
            self._draw_sky(surface)
            if self.elapsed >= CANOPY_START:
                self._draw_canopy_approach(surface)
            self._draw_falling_chuck(surface)
        else:
            self._draw_jungle_tableau(surface)

        pygame.draw.rect(surface, (13, 22, 25), (0, 0, config.NATIVE_WIDTH, 7))
        pygame.draw.rect(
            surface, (13, 22, 25),
            (0, config.NATIVE_HEIGHT - 7, config.NATIVE_WIDTH, 7),
        )
        if self.fade_out_progress > 0.0:
            fade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            fade.fill((0, 0, 0, round(255 * self.fade_out_progress)))
            surface.blit(fade, (0, 0))

    # ------------------------------------------------------------------
    # Long sky descent
    # ------------------------------------------------------------------
    def _draw_sky(self, surface: pygame.Surface) -> None:
        dusk = _ease((self.elapsed - 17.0) / (CANOPY_START - 17.0))
        top = _mix_color(SKY_TOP, (17, 82, 83), dusk)
        bottom = _mix_color(SKY_BOTTOM, (28, 111, 91), dusk)
        for y in range(config.NATIVE_HEIGHT):
            t = y / max(1, config.NATIVE_HEIGHT - 1)
            pygame.draw.line(surface, _mix_color(top, bottom, t),
                             (0, y), (config.NATIVE_WIDTH, y))

        for index, (x, y, width, _speed) in enumerate(self.clouds):
            self._draw_cloud(surface, round(x), round(y), width, index % 2)

    def _draw_falling_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get("down")
        if frame is None:
            return
        intro = _ease(self.elapsed / 0.45)
        scale = 0.25 + intro * 0.75
        width = max(2, round(config.CHUCK_FRAME_W * scale))
        height = max(3, round(config.CHUCK_FRAME_H * scale))
        frame = pygame.transform.scale(frame, (width, height))

        sway = round(math.sin(self.elapsed * 1.7))
        base_top = 78 - height // 2
        landing_top = GROUND_Y - height
        landing = _ease((self.elapsed - GROUND_APPROACH)
                        / (IMPACT_TIME - GROUND_APPROACH))
        draw_x = config.NATIVE_WIDTH // 2 - width // 2 + sway
        draw_y = round(base_top + (landing_top - base_top) * landing)
        surface.blit(frame, (draw_x, draw_y))

    @staticmethod
    def _draw_cloud(
        surface: pygame.Surface, x: int, y: int, width: int, layer: int
    ) -> None:
        height = 8 if layer == 0 else 11
        shade = CLOUD_SHADE if layer == 0 else (165, 213, 204)
        pygame.draw.rect(surface, shade, (x, y + 4, width, height - 2))
        pygame.draw.rect(surface, CLOUD, (x + 5, y + 2, width - 10, height - 1))
        pygame.draw.rect(surface, CLOUD, (x + width // 3, y,
                                          width // 3, height))

    # ------------------------------------------------------------------
    # Canopy collision
    # ------------------------------------------------------------------
    def _draw_canopy_approach(self, surface: pygame.Surface) -> None:
        progress = _clamp01((self.elapsed - CANOPY_START)
                            / (IMPACT_TIME - CANOPY_START))
        self._draw_rushing_branches(surface, self.elapsed - CANOPY_START)
        ground_y = round(194 + (GROUND_Y - 194) * _ease(
            (self.elapsed - GROUND_APPROACH) / (IMPACT_TIME - GROUND_APPROACH)
        ))
        self._draw_jungle(surface, ground_y, progress)

    @staticmethod
    def _draw_rushing_branches(surface: pygame.Surface, t: float) -> None:
        specs = (
            (18, 0.0, 42, 74, 1), (278, 0.3, 55, 62, -1),
            (66, 0.7, 63, 48, 1), (224, 1.0, 47, 82, -1),
            (4, 1.4, 72, 57, 1), (300, 1.8, 68, 70, -1),
            (112, 2.1, 75, 50, 1), (252, 2.5, 82, 66, -1),
            (42, 2.8, 86, 72, 1), (188, 3.1, 91, 58, -1),
            (8, 3.5, 96, 80, 1), (286, 3.8, 102, 74, -1),
        )
        for x, delay, speed, length, direction in specs:
            if t < delay:
                continue
            y = round(config.NATIVE_HEIGHT + 18 - (t - delay) * speed)
            if y < -30:
                continue
            end_x = x + direction * length
            pygame.draw.line(surface, (34, 60, 34), (x, y), (end_x, y - 18), 4)
            pygame.draw.line(surface, (57, 83, 42), (x, y - 1),
                             (end_x, y - 19), 1)
            for leaf in range(3):
                lx = x + direction * (14 + leaf * 15)
                ly = y - 5 - leaf * 5
                pygame.draw.rect(surface, (31, 74, 46),
                                 (lx - 3, ly - 2, 7, 4))
        # Long vines become an increasingly dense vertical blur.
        for index, x in enumerate((31, 83, 137, 202, 246, 294)):
            delay = 1.1 + index * 0.25
            if t < delay:
                continue
            top = round(190 - (t - delay) * (54 + index * 3))
            pygame.draw.line(surface, (42, 91, 54), (x, top),
                             (x + (index % 3 - 1) * 7, top + 58), 2)

    # ------------------------------------------------------------------
    # Jungle, death, return, and cigarette
    # ------------------------------------------------------------------
    def _draw_jungle_tableau(self, surface: pygame.Surface) -> None:
        impact_age = self.elapsed - IMPACT_TIME
        jolt = 2 if 0.0 <= impact_age < 0.08 else 0
        surface.fill((10, 27, 24))
        self._draw_jungle(surface, GROUND_Y + jolt, 1.0)
        self._draw_impact_leaves(surface, impact_age, jolt)

        chuck_x = config.NATIVE_WIDTH // 2 - config.CHUCK_FRAME_W // 2
        chuck_y = GROUND_Y - config.CHUCK_FRAME_H + jolt
        phase = self.phase
        if phase == "impact":
            self._blit_chuck(surface, self._frames.get("down"), chuck_x, chuck_y)
        elif phase == "vanished":
            self._draw_astral_blip(surface, chuck_x + 6, GROUND_Y - 7,
                                   self.elapsed - VANISH_TIME, returning=False)
        elif phase == "return":
            progress = _clamp01((self.elapsed - RESPAWN_TIME)
                                / (LOOK_START - RESPAWN_TIME))
            self._draw_astral_blip(surface, chuck_x + 6, GROUND_Y - 7,
                                   progress, returning=True)
            if int(progress * 8) % 2 == 1 or progress > 0.8:
                self._blit_chuck(surface, self._frames.get("down"),
                                 chuck_x, chuck_y)
        else:
            facing = self._facing_for_tableau()
            frame = self._frame_for_tableau(facing)
            self._blit_chuck(surface, frame, chuck_x, chuck_y)
            if phase == "cigarette":
                self._draw_cigarette_insert(surface, chuck_x, chuck_y)
            elif phase in {"smoke", "complete"}:
                self._draw_drag(surface, chuck_x, chuck_y)

    def _facing_for_tableau(self) -> str:
        if self.elapsed < LOOK_START + 0.7:
            return "left"
        if self.elapsed < LOOK_START + 1.45:
            return "right"
        if self.elapsed < CIGARETTE_START:
            return "down"
        return "left"

    def _frame_for_tableau(self, facing: str) -> pygame.Surface | None:
        if facing == "left" and self.elapsed < CIGARETTE_SEATED:
            return self._left_without_cigarette
        if facing == "right" and self.elapsed < CIGARETTE_SEATED:
            if self._left_without_cigarette is None:
                return None
            return pygame.transform.flip(self._left_without_cigarette, True, False)
        return self._frames.get(facing)

    @staticmethod
    def _blit_chuck(surface, frame, x: int, y: int, alpha: int = 255) -> None:
        if frame is None:
            return
        if alpha < 255:
            frame = frame.copy()
            frame.set_alpha(alpha)
        surface.blit(frame, (x, y))

    def _draw_cigarette_insert(self, surface, chuck_x: int, chuck_y: int) -> None:
        progress = _ease((self.elapsed - CIGARETTE_START)
                         / (CIGARETTE_SEATED - CIGARETTE_START))
        start = (chuck_x + 7, chuck_y + 10)
        end = (chuck_x - 1, chuck_y + 7)
        x = round(start[0] + (end[0] - start[0]) * progress)
        y = round(start[1] + (end[1] - start[1]) * progress)
        pygame.draw.line(surface, config.COLOR_CIG_PAPER, (x, y), (x + 2, y), 1)
        pygame.draw.rect(surface, config.COLOR_CIG_EMBER, (x - 1, y, 1, 1))

    def _draw_drag(self, surface, chuck_x: int, chuck_y: int) -> None:
        ember = (255, 184, 86) if int(self.elapsed * 6) % 2 else (
            config.COLOR_CIG_EMBER
        )
        pygame.draw.rect(surface, ember, (chuck_x - 1, chuck_y + 7, 1, 1))
        smoke_age = max(0.0, self.elapsed - DRAG_START)
        if smoke_age <= 0.0:
            return
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for index in range(4):
            age = (smoke_age - index * 0.38) % 1.7
            rise = round(age * 7)
            drift = round(math.sin(age * 3.0 + index) * 2)
            alpha = max(0, round(100 * (1.0 - age / 1.7)))
            pygame.draw.rect(layer, (178, 187, 177, alpha),
                             (chuck_x - 1 + drift, chuck_y + 5 - rise, 2, 2))
        surface.blit(layer, (0, 0))

    @staticmethod
    def _draw_astral_blip(
        surface: pygame.Surface, cx: int, cy: int, progress: float,
        returning: bool,
    ) -> None:
        amount = _clamp01(progress if returning else 1.0 - progress / 1.2)
        for index in range(14):
            radius = 3 + (index * 7) % 13
            angle = index * 2.17 + progress * (1 if returning else -1)
            x = cx + round(math.cos(angle) * radius * amount)
            y = cy + round(math.sin(angle) * radius * amount)
            color = config.COLOR_STAR if index % 3 else (123, 105, 174)
            pygame.draw.rect(surface, color, (x, y, 1, 1))

    @staticmethod
    def _draw_impact_leaves(surface: pygame.Surface, age: float, jolt: int) -> None:
        if not 0.0 <= age <= 1.1:
            return
        for index in range(10):
            direction = -1 if index % 2 else 1
            x = 160 + direction * round((8 + index * 2) * age)
            y = GROUND_Y - 2 - round((10 + index % 4 * 3) * age) + jolt
            pygame.draw.rect(surface, (61, 94, 47), (x, y, 3, 2))

    @staticmethod
    def _draw_jungle(surface: pygame.Surface, ground_y: int, density: float) -> None:
        density = _clamp01(density)
        trunks = (
            (8, 13, 108), (42, 8, 76), (74, 15, 118), (112, 7, 83),
            (196, 12, 104), (232, 7, 88), (269, 15, 121), (307, 10, 91),
        )
        for index, (x, width, height) in enumerate(trunks):
            shown = round(height * density)
            top = ground_y - shown
            color = (27, 48, 32) if index % 2 else (31, 55, 35)
            pygame.draw.rect(surface, color, (x, top, width, shown + 12))
            if shown > 25:
                root = 8 + index % 3 * 4
                pygame.draw.line(surface, (45, 61, 35),
                                 (x + width // 2, ground_y - 1),
                                 (x - root, ground_y + 6), 3)

        canopy_y = max(7, ground_y - round(105 * density))
        for x, width, depth in (
            (-8, 64, 21), (45, 78, 16), (108, 58, 25),
            (154, 82, 18), (222, 62, 27), (274, 58, 20),
        ):
            pygame.draw.rect(surface, (17, 54, 34),
                             (x, canopy_y, width, depth))
            pygame.draw.rect(surface, (25, 70, 40),
                             (x + 7, canopy_y + depth - 4, width - 14, 5))

        if density > 0.45:
            for index, x in enumerate((25, 58, 101, 146, 214, 251, 295)):
                length = 25 + index % 4 * 11
                pygame.draw.line(surface, (37, 83, 48), (x, 7),
                                 (x + (index % 3 - 1) * 6, 7 + length), 2)

        if ground_y < config.NATIVE_HEIGHT:
            pygame.draw.rect(surface, (37, 44, 28),
                             (0, ground_y, config.NATIVE_WIDTH,
                              config.NATIVE_HEIGHT - ground_y))
            pygame.draw.line(surface, (65, 69, 38), (0, ground_y),
                             (config.NATIVE_WIDTH, ground_y), 2)
        for x in range(4, config.NATIVE_WIDTH, 17):
            y = ground_y + 5 + (x * 7) % max(6, config.NATIVE_HEIGHT - ground_y - 8)
            pygame.draw.rect(surface, (51, 64, 35), (x, y, 4, 2))
        # Foreground ferns crowd the landing without obscuring Chuck.
        for x, direction in ((5, 1), (37, -1), (281, 1), (315, -1)):
            base = ground_y + 24
            pygame.draw.line(surface, (31, 83, 43), (x, base),
                             (x + direction * 9, base - 24), 2)
            for leaf in range(4):
                ly = base - 5 - leaf * 5
                pygame.draw.line(surface, (43, 102, 53),
                                 (x + direction * leaf * 2, ly),
                                 (x + direction * (11 + leaf), ly - 3), 2)
