"""Phase 12's exit: Chuck steps out of the table map into a desert.

The same shape as the Douglas fir crossing at the end of Phase 11, and
deliberately so -- these are the two ends of the same kind of journey.
The portal surface swells until it is the whole screen, the light
drains out of it, and what fades up is somewhere with no trees in it at
all: low dunes under a bleached sky, heat standing on the horizon, and
Chuck walking out of nothing into the middle of it.

Then it holds, and goes to white rather than to black, because the last
one went to black and the difference is the point: he has come out of a
cabin at night into the middle of a day.

The boundary is the same too. Phase 12 ends with no playable desert, so
this records the crossing as a progress flag against the save that
still points at the cabin, and hands back to the title. Continue
returns to the cabin rather than to a region that has not been built.

No words. Sanity carries into the save unchanged.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.planar_portal import portal_colour
from src.scenes.scene import Scene
from src.systems.cabin_progress import DESERT_TRANSITION_FLAG


SWELL_END = 2.4         # the portal opens until it is the whole screen
DRAIN_END = 3.4         # ...and the colour drains out of it to white
DESERT_IN = 5.0         # the desert has faded up
WALK_START = 5.4        # ...and only then does anything move in it
WALK_END = 8.6          # Chuck stops
HOLD_END = 12.6         # the tableau holds, wordless
FADE_END = 14.0         # to white, and out of the phase

_SAND = (214, 178, 122)
_SAND_LIT = (236, 206, 156)
_SAND_SHADE = (176, 138, 90)
_FAR_DUNE = (206, 176, 134)
_HAZE = (232, 218, 196)
_SKY_HIGH = (150, 186, 214)
_SKY_LOW = (226, 222, 206)
_ROCK = (150, 116, 82)
_ROCK_DARK = (110, 82, 58)

_HORIZON = 96
_GROUND_Y = 150
# Where Chuck arrives, and where he stops. He walks out of the middle of
# it rather than in from an edge: there is no edge to come in from.
_ARRIVE_X = 150
_WALK = 34


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class DesertArrivalCutsceneScene(Scene):
    """Portal, whiteout, desert, one rat. Ends Phase 12."""

    def __init__(self, game, sanity: int | None = None) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self._sanity = sanity
        self._frames: dict[str, pygame.Surface] = {}
        self._handed_off = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._frames = {
            "right": pygame.transform.flip(grid[2][0], True, False),
            "down": grid[0][0],
        }
        # The cabin, its lightshow and its music all stop at the table.
        self.game.audio.stop_music(fade_ms=900)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < SWELL_END:
            return "swell"
        if self.elapsed < DRAIN_END:
            return "drain"
        if self.elapsed < DESERT_IN:
            return "arrive"
        if self.elapsed < WALK_START:
            return "still"
        if self.elapsed < WALK_END:
            return "walking"
        if self.elapsed < HOLD_END:
            return "hold"
        return "fade_out"

    @property
    def walk_progress(self) -> float:
        """0 where he arrives, 1 at the spot he stops on."""
        if self.elapsed <= WALK_START:
            return 0.0
        return _ease((self.elapsed - WALK_START) / (WALK_END - WALK_START))

    @property
    def chuck_position(self) -> tuple[int, int]:
        x = _ARRIVE_X + round(self.walk_progress * _WALK)
        return x, _GROUND_Y - config.CHUCK_FRAME_H

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed < FADE_END or self._handed_off:
            return
        self._handed_off = True
        # Phase 12 ends here. Record the crossing and write it into the
        # save that still points at the cabin, so Continue comes back to
        # the table rather than to a desert that does not exist yet.
        self.game.progress.enable(DESERT_TRANSITION_FLAG)
        active = self.game.active_checkpoint_id
        if active is not None and self._sanity is not None:
            definition = self.game.checkpoints.definition(active)
            if definition.saveable:
                self.game.checkpoints.activate_checkpoint(
                    active, sanity=self._sanity
                )
        from src.scenes.title_scene import TitleScene

        self.game.scenes.replace(TitleScene(self.game))

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < DRAIN_END:
            self._draw_portal(surface)
            return
        self._draw_desert(surface)
        if self.elapsed >= WALK_START:
            self._draw_chuck(surface)
        if self.elapsed < DESERT_IN:
            self._white(surface, 1.0 - _ease(
                (self.elapsed - DRAIN_END) / (DESERT_IN - DRAIN_END)))
        elif self.elapsed >= HOLD_END:
            self._white(surface, (self.elapsed - HOLD_END)
                        / (FADE_END - HOLD_END))

    def _white(self, surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((252, 248, 238))
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # The crossing: the table's own surface, opened until it is all there
    # is, then drained of its colour.
    # ------------------------------------------------------------------
    def _draw_portal(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.fill((10, 10, 14))
        grow = _ease(self.elapsed / SWELL_END)
        half_w = 8 + grow * width * 0.62
        half_h = 12 + grow * height * 0.72
        phase = self.elapsed * 2.2
        # Past the swell the colour is washed out toward the white the
        # desert fades up from, so the two are one continuous light.
        drain = 0.0 if self.elapsed < SWELL_END else _clamp01(
            (self.elapsed - SWELL_END) / (DRAIN_END - SWELL_END))
        centre = (width // 2, height // 2)
        # A coarser step as it grows: at full screen this is thousands of
        # points, and it is a blur of light by then in any case.
        step = 1 + int(grow * 2)
        # It stays the table's own oval until it is most of the way
        # open, then the edge softens outward past the corners. Held at
        # the rim throughout it grew into an octagon with black in the
        # corners, because a screen has corners and an ellipse does not.
        cutoff = 0.94 + max(0.0, grow - 0.55) / 0.45 * 1.2
        for y in range(-int(half_h), int(half_h), step):
            for x in range(-int(half_w), int(half_w), step):
                nx, ny = x / half_w, y / half_h
                if math.hypot(nx, ny) >= cutoff:
                    continue
                colour = portal_colour(nx, ny, phase, 0.85)
                if drain:
                    colour = tuple(
                        round(c + (252 - c) * drain) for c in colour
                    )
                pygame.draw.rect(
                    surface, colour,
                    (centre[0] + x, centre[1] + y, step, step))

    # ------------------------------------------------------------------
    # Somewhere with no trees in it.
    # ------------------------------------------------------------------
    def _draw_desert(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        for y in range(_HORIZON):
            blend = y / _HORIZON
            surface.fill(
                tuple(round(a + (b - a) * blend)
                      for a, b in zip(_SKY_HIGH, _SKY_LOW)),
                (0, y, width, 1),
            )
        # The haze the horizon stands in: what says heat rather than cold.
        pygame.draw.rect(surface, _HAZE, (0, _HORIZON - 6, width, 8))

        # Far dunes, then near ones, each a shallow arc rather than a
        # peak: this is old sand, not a sea of dramatic ridges.
        for index, (top, colour) in enumerate((
            (_HORIZON - 4, _FAR_DUNE), (_HORIZON + 6, _SAND_SHADE),
        )):
            points = [(0, height), (0, top + 8)]
            for x in range(0, width + 16, 16):
                sway = math.sin(x / 46.0 + index * 2.1) * (5 - index * 2)
                points.append((x, round(top + sway)))
            points.append((width, height))
            pygame.draw.polygon(surface, colour, points)

        pygame.draw.rect(surface, _SAND, (0, _HORIZON + 18, width,
                                          height - _HORIZON - 18))
        # Wind ripples, running the way the dunes do.
        for index in range(70):
            x = (index * 53 + 11) % width
            y = _HORIZON + 22 + (index * 17) % (height - _HORIZON - 24)
            run = 4 + (index % 3) * 3
            shade = _SAND_LIT if index % 2 else _SAND_SHADE
            pygame.draw.line(surface, shade, (x, y), (x + run, y))
        # A few stones, and the shadows that prove the sun is overhead.
        for x, y, size in ((44, 132, 5), (232, 124, 4), (96, 160, 3),
                           (274, 148, 6)):
            pygame.draw.ellipse(surface, _ROCK_DARK,
                                (x - 1, y + size - 2, size * 2 + 4, 3))
            pygame.draw.ellipse(surface, _ROCK, (x, y, size * 2, size))
            pygame.draw.ellipse(surface, _SAND_LIT,
                                (x + 1, y, size, size // 2 + 1))

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get(
            "right" if self.phase == "walking" else "down"
        )
        if frame is None:
            return
        x, y = self.chuck_position
        # His shadow, directly under him: nothing else out here casts one
        # sideways, and it is what stops him floating on the sand.
        pygame.draw.ellipse(
            surface, _SAND_SHADE,
            (x + 1, _GROUND_Y - 3, config.CHUCK_FRAME_W - 2, 4))
        surface.blit(frame, (x, y))
