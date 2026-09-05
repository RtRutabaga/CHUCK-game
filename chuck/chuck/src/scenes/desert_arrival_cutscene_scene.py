"""Phase 12's exit: Chuck steps out of the table map into a desert.

The same shape as the Douglas fir crossing at the end of Phase 11, and
deliberately so -- these are the two ends of the same kind of journey.
The portal surface swells until it is the whole screen, the light drains
out of it, and what fades up is somewhere with no trees in it at all:
low dunes under a bleached sky, heat standing on the horizon.

He does not simply appear there. The crossing has another mouth, and it
is standing in the sand waiting: an upright oval of the same moving
colour, which he walks out of. Then it collapses -- pulled into its own
middle and gone, leaving the desert with nothing in it to explain him.
Only once he is alone in it does he take out a cigarette and light it,
which is what Chuck does after every arrival that has not killed him.

Then it holds, and goes to white rather than to black, because the last
one went to black and the difference is the point: he has come out of a
cabin at night into the middle of a day.

Then it hands off into the desert. It used to end at the title instead:
Phase 12 closed with no playable region on the far side, so the only
honest thing it could do was record the crossing and let Continue come
back to the cabin. Phase 13 built the far side, so the crossing goes
where it always meant to go -- through the same shared checkpoint path
the Douglas fir crossing uses, with Sanity carried through intact and
the desert's own Ashtray owning persistence from there.

No words.
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
DESERT_IN = 5.0         # the desert has faded up, the far mouth standing in it
WALK_START = 5.8        # ...and only then does anything come out of it
WALK_END = 8.6          # Chuck stops, clear of the portal
COLLAPSE_START = 9.2    # the mouth begins to fall into itself
COLLAPSE_END = 10.8     # ...and there is nothing there at all
LOOK_START = 11.2       # he takes the place in: left, right, down
CIGARETTE_START = 13.6  # and then does what he always does
CIGARETTE_SEATED = 15.0
DRAG_START = 15.4
HOLD_END = 20.0         # the tableau holds, wordless
FADE_END = 21.6         # to white, and out of the phase

MUSIC_START = 3.6       # under the whiteout, so the desert arrives on it

# Where the crossing comes out. The hub's own runtime entry rather than
# a position authored twice: the map decides where its start is.
DESERT_ENTRY_CHECKPOINT = "desert_central_start"

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
# Where the far mouth stands, and where Chuck walks out to. He arrives
# in the middle of it rather than in from an edge: there is no edge to
# come in from, which is the whole reason the portal has to be shown.
_PORTAL_X = 132
_PORTAL_HALF_W = 17
_PORTAL_HEIGHT = 58
_ARRIVE_X = 126
_WALK = 40


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class DesertArrivalCutsceneScene(Scene):
    """Portal, whiteout, desert, one rat, one cigarette. Ends Phase 12."""

    def __init__(self, game, sanity: int | None = None) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self._sanity = sanity
        self._frames: dict[str, pygame.Surface] = {}
        self._unlit: pygame.Surface | None = None
        self._handed_off = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._frames = {
            "left": grid[2][0],
            "right": pygame.transform.flip(grid[2][0], True, False),
            "down": grid[0][0],
        }
        # The profile art already carries Chuck's usual cigarette. Keep a
        # clean copy so this scene can show him actually taking it out,
        # exactly as the fall into Chult does.
        self._unlit = grid[2][0].copy()
        self._unlit.set_at((0, 7), (0, 0, 0, 0))
        self._unlit.set_at((1, 7), (0, 0, 0, 0))
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
        if self.elapsed < COLLAPSE_END:
            return "collapse"
        if self.elapsed < CIGARETTE_START:
            return "look"
        if self.elapsed < CIGARETTE_SEATED:
            return "cigarette"
        if self.elapsed < HOLD_END:
            return "smoke"
        return "fade_out"

    @property
    def walk_progress(self) -> float:
        """0 where he steps out of the mouth, 1 at the spot he stops on."""
        if self.elapsed <= WALK_START:
            return 0.0
        return _ease((self.elapsed - WALK_START) / (WALK_END - WALK_START))

    @property
    def chuck_position(self) -> tuple[int, int]:
        x = _ARRIVE_X + round(self.walk_progress * _WALK)
        return x, _GROUND_Y - config.CHUCK_FRAME_H

    @property
    def portal_scale(self) -> float:
        """1 while it stands there, falling to 0 as it eats itself."""
        if self.elapsed < COLLAPSE_START:
            return 1.0
        return 1.0 - _ease(
            (self.elapsed - COLLAPSE_START) / (COLLAPSE_END - COLLAPSE_START)
        )

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= CIGARETTE_SEATED

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += dt
        self._play_cues(previous, self.elapsed)
        if self.elapsed < FADE_END or self._handed_off:
            return
        self._handed_off = True
        # Phase 12 ends and Phase 13 begins here. Record the crossing,
        # then walk out into the desert through the same shared
        # checkpoint path the Douglas fir crossing uses, with the
        # running Sanity value intact. The desert's Ashtray owns
        # persistence from this point; nothing is written here.
        self.game.progress.enable(DESERT_TRANSITION_FLAG)
        self.game.checkpoints.load_checkpoint(
            DESERT_ENTRY_CHECKPOINT,
            progress_flags=set(self.game.progress.flags),
            sanity=self._sanity,
        )

    def _play_cues(self, previous: float, current: float) -> None:
        """One short cue and a handful of quiet noises.

        Everything here is deliberately under the music. The loudest
        thing in the scene is a portal folding up, and that is a soft
        inward sound rather than a bang: nothing is being destroyed,
        something is being closed.
        """
        if previous < MUSIC_START <= current:
            self.game.audio.play_music("desert_arrival.wav", loop=False)
        cues = (
            (DESERT_IN, "portal_hum"),
            # Two steps out of the mouth and one as he settles. Sand is
            # a dry surface; the stone taps are the closest thing to it.
            (WALK_START + 0.35, "footstep_stone_1"),
            (WALK_START + 1.15, "footstep_stone_2"),
            (WALK_END - 0.4, "footstep_stone_1"),
            (COLLAPSE_START, "portal_collapse"),
            (CIGARETTE_SEATED, "lighter"),
        )
        for cue_time, sound in cues:
            if previous < cue_time <= current:
                self.game.audio.play_sfx(sound)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < DRAIN_END:
            self._draw_portal(surface)
            return
        self._draw_desert(surface)
        if self.portal_scale > 0.0:
            self._draw_far_mouth(surface)
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
    # The far mouth: the same crossing seen from the other end, standing
    # upright in the sand because there is no table out here to lie on.
    # ------------------------------------------------------------------
    def _draw_far_mouth(self, surface: pygame.Surface) -> None:
        scale = self.portal_scale
        # It closes by being pulled into its own middle, so the width
        # goes first and the height follows: a sheet drawn through a
        # ring rather than a picture shrinking evenly to a dot.
        half_w = max(1.0, _PORTAL_HALF_W * scale ** 1.7)
        half_h = max(1.0, _PORTAL_HEIGHT / 2.0 * scale ** 0.85)
        centre_x = _PORTAL_X
        centre_y = _GROUND_Y - _PORTAL_HEIGHT / 2.0
        phase = self.elapsed * 2.2
        # The last of it flares as it goes: everything that was spread
        # across the mouth ends up in the same few pixels.
        flare = 0.0 if scale > 0.28 else (0.28 - scale) / 0.28

        # The pool of light it throws on the sand in front of it.
        if scale > 0.05:
            glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.ellipse(
                glow, (150, 170, 200, round(52 * scale)),
                (centre_x - half_w * 1.9, _GROUND_Y - 7,
                 half_w * 3.8, 13))
            surface.blit(glow, (0, 0))

        for y in range(-int(half_h) - 1, int(half_h) + 1):
            for x in range(-int(half_w) - 1, int(half_w) + 1):
                nx, ny = x / half_w, y / half_h
                if math.hypot(nx, ny) >= 1.0:
                    continue
                colour = portal_colour(nx, ny, phase, 0.85)
                if flare:
                    colour = tuple(
                        round(c + (255 - c) * flare) for c in colour)
                surface.set_at(
                    (centre_x + x, round(centre_y) + y), colour)

        # A thin rim, so it reads as an opening with an edge rather than
        # a coloured smear on the sand.
        if half_w > 2 and half_h > 2:
            pygame.draw.ellipse(
                surface, (226, 232, 244),
                (centre_x - half_w, centre_y - half_h,
                 half_w * 2, half_h * 2), 1)

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

    # ------------------------------------------------------------------
    def _facing(self) -> str:
        """Walk out, then take the place in before settling."""
        if self.elapsed < LOOK_START + 0.7:
            return "right"
        if self.elapsed < LOOK_START + 1.4:
            return "down"
        if self.elapsed < LOOK_START + 2.1:
            return "right"
        # ...and in profile well before he reaches for the cigarette:
        # the whole gesture is drawn against the side of his head, and
        # played against the front-facing frame it floats beside his ear.
        return "left"

    def _frame_for(self, facing: str) -> pygame.Surface | None:
        """The profile art, with or without the cigarette already in it."""
        if self._unlit is not None and self.elapsed < CIGARETTE_SEATED:
            if facing == "left":
                return self._unlit
            if facing == "right":
                return pygame.transform.flip(self._unlit, True, False)
        return self._frames.get(facing)

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        facing = self._facing()
        frame = self._frame_for(facing)
        if frame is None:
            return
        x, y = self.chuck_position
        # He comes out of the mouth rather than being placed beside it:
        # opaque only once he is clear of the opening.
        emerging = _clamp01((self.elapsed - WALK_START) / 0.9)
        if emerging < 1.0:
            frame = frame.copy()
            frame.set_alpha(round(255 * emerging))
        # His shadow, directly under him: nothing else out here casts one
        # sideways, and it is what stops him floating on the sand.
        shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(
            shadow, (*_SAND_SHADE, round(255 * emerging)),
            (x + 1, _GROUND_Y - 3, config.CHUCK_FRAME_W - 2, 4))
        surface.blit(shadow, (0, 0))
        surface.blit(frame, (x, y))

        if self.phase == "cigarette":
            self._draw_cigarette_insert(surface, x, y)
        elif self.elapsed >= CIGARETTE_SEATED:
            self._draw_drag(surface, x, y)

    def _draw_cigarette_insert(self, surface, chuck_x: int, chuck_y: int) -> None:
        """Taking it out and putting it in, the Chult landing's gesture."""
        progress = _ease((self.elapsed - CIGARETTE_START)
                         / (CIGARETTE_SEATED - CIGARETTE_START))
        start = (chuck_x + 7, chuck_y + 10)
        end = (chuck_x - 1, chuck_y + 7)
        x = round(start[0] + (end[0] - start[0]) * progress)
        y = round(start[1] + (end[1] - start[1]) * progress)
        pygame.draw.line(surface, config.COLOR_CIG_PAPER, (x, y), (x + 2, y), 1)

    def _draw_drag(self, surface, chuck_x: int, chuck_y: int) -> None:
        # The flare of the light itself, then the steady ember.
        since = self.elapsed - CIGARETTE_SEATED
        if since < 0.28:
            pygame.draw.rect(surface, (255, 226, 150),
                             (chuck_x - 2, chuck_y + 6, 3, 3))
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
            alpha = max(0, round(90 * (1.0 - age / 1.7)))
            pygame.draw.rect(layer, (198, 200, 188, alpha),
                             (chuck_x - 1 + drift, chuck_y + 5 - rise, 2, 2))
        surface.blit(layer, (0, 0))
