"""The opening: a rat wakes up on the Waterdeep docks.

The return-to-Waterdeep cutscene ends the long walk with Chuck on the
quay at midday, looking around and lighting one. This is the same shot
at the other end of the game, and it is built to rhyme with it: the same
low quayside vantage, the same posts along the edge and the same boat on
the water -- but evening, in the opening docks' own colours, and with the
thing the other one has no room for, which is how he got there. He was
asleep. Beside Bobert, in Bobert's barrel, who is still asleep and will
be for the whole game.

Fade in on the two of them snoring. Chuck stirs, gets up, looks left and
right at a harbour he does not seem surprised by, and lights a
cigarette. Fade out, and the fade clears onto the same docks, playable,
with Chuck on the plank beside the barrel where he woke.

No words. He does not get a line here either. Interact skips it.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene
from src.world.tileset_layout import DOCKS, TILE_PX, art_index


FADE_IN_END = 2.6
STIR = 5.4              # a twitch; the breathing stops
WAKE = 6.4              # up, facing us, the thousand-yard stare
LOOK_LEFT = 7.6
LOOK_RIGHT = 8.7
FACE_LEFT = 9.8
LIGHTER = 10.6
LIT = 11.2
DRAG = 12.2
HOLD_END = 15.6
FADE_END = 17.6

MUSIC_START = 0.2

# The opening docks' evening, taken from docks.png: its planks and water,
# and a dusk over them that the water's star flecks suggest.
_SKY_TOP = (20, 22, 44)
_SKY_LOW = (92, 70, 98)
_SKY_GLOW = (170, 104, 92)
_STAR = (210, 214, 236)
_WATER = (36, 52, 84)
_WATER_LIT = (52, 72, 110)
_WATER_FLECK = (118, 140, 176)
_DOCK_PLANK = (150, 112, 74)
_DOCK_SEAM = (108, 76, 46)
_GULL = (190, 192, 204)
_Z = (214, 214, 226)

_HORIZON = 62
_QUAY_Y = 108
_POST_XS = (30, 88, 236, 290)
_POST_BASE_Y = _QUAY_Y + 5
_MOORED_POST = 88
_BOAT_X, _BOAT_Y = 48, 82
_LAMP_X = 262

# Bobert's barrel, and Chuck asleep against its left side and then
# standing where he lay.
_BARREL_X, _BARREL_BASE = 170, 142
_SLEEP_X, _SLEEP_BASE = 150, 142
_CHUCK_X, _CHUCK_Y = 154, 128


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


class OpeningCutsceneScene(Scene):
    """Evening on the docks; Chuck wakes beside Bobert. Starts the game."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self._frames: dict[str, pygame.Surface] = {}
        self._unlit: pygame.Surface | None = None
        self._asleep: tuple[pygame.Surface, ...] = ()
        self._barrel: pygame.Surface | None = None
        self._planks: list[pygame.Surface] = []
        self._plank_info: tuple[int, int] = (1, 1)
        self._post: pygame.Surface | None = None
        self._boat: pygame.Surface | None = None
        self._lamp: pygame.Surface | None = None
        self._handed_off = False

    # ------------------------------------------------------------------
    def on_enter(self) -> None:
        assets = self.game.assets
        grid = assets.sheet(config.CHUCK_SHEET, config.CHUCK_FRAME_W,
                            config.CHUCK_FRAME_H)
        self._frames = {
            "left": grid[2][0],
            "right": pygame.transform.flip(grid[2][0], True, False),
            "down": grid[0][0],
        }
        # The profile frame has the cigarette in it already; before he
        # lights it, it is not there.
        self._unlit = grid[2][0].copy()
        self._unlit.set_at((0, 7), (0, 0, 0, 0))
        self._unlit.set_at((1, 7), (0, 0, 0, 0))
        self._asleep = tuple(assets.sheet("chuck/chuck_asleep.png", 16, 9)[0])
        self._barrel = self._image("objects/bobert_barrel.png")
        self._post = self._image("objects/harbour_bollard.png")
        self._lamp = self._image("objects/waterdeep_lamp.png")
        boat = self._image("objects/harbour_rowboat.png")
        if boat is not None:
            # The hull only; the line is drawn to this view's post.
            self._boat = boat.subsurface(
                (0, 22, boat.get_width(), boat.get_height() - 22)).copy()
        try:
            rows = assets.tileset(DOCKS.sheet, TILE_PX)
        except (FileNotFoundError, pygame.error):
            rows = None
        if rows is not None:
            for index, (name, variants, frames) in enumerate(DOCKS.order):
                if name == "planks":
                    self._planks = rows[index][: variants * frames]
                    self._plank_info = (variants, frames)
        self.game.audio.stop_music(fade_ms=400)

    def _image(self, path: str):
        try:
            return self.game.assets.image(path)
        except (FileNotFoundError, pygame.error):
            return None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    # ------------------------------------------------------------------
    @property
    def phase(self) -> str:
        if self.elapsed < WAKE:
            return "asleep"
        if self.elapsed < LIT:
            return "waking"
        if self.elapsed < HOLD_END:
            return "smoking"
        return "fading"

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= LIT

    def update(self, dt: float) -> None:
        if (self.elapsed < HOLD_END
                and self.game.input.was_pressed("interact")):
            # Skip to the fade rather than cutting: the game should still
            # arrive out of black, not out of nowhere.
            self.elapsed = HOLD_END
        previous = self.elapsed
        self.elapsed += dt
        self._play_cues(previous, self.elapsed)
        if self.elapsed < FADE_END or self._handed_off:
            return
        self._handed_off = True
        world = self.game.checkpoints.new_game()
        # Up out of the same black this faded into.
        if world is not None:
            world._arrival_fade_t = 0.0
            world._arrival_fade_from = (0, 0, 0)

    def _play_cues(self, previous: float, current: float) -> None:
        cues = (
            (WAKE, "footstep_wood_1"),
            (LOOK_RIGHT, "footstep_wood_2"),
            (LIGHTER, "lighter"),
        )
        if previous < MUSIC_START <= current:
            self.game.audio.play_music("waterdeep_docks.wav")
        for cue_time, sound in cues:
            if previous < cue_time <= current:
                self.game.audio.play_sfx(sound)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_sky_and_water(surface)
        if self._boat is not None:
            surface.blit(self._boat, (_BOAT_X, _BOAT_Y))
        self._draw_quay(surface)
        self._draw_moorings(surface)
        if self._lamp is not None:
            surface.blit(self._lamp, (_LAMP_X, _POST_BASE_Y + 2
                                      - self._lamp.get_height()))
        self._draw_bobert_and_chuck(surface)
        if self.elapsed < FADE_IN_END:
            self._black(surface, 1.0 - self.elapsed / FADE_IN_END)
        if self.elapsed >= HOLD_END:
            self._black(surface, (self.elapsed - HOLD_END)
                        / (FADE_END - HOLD_END))

    def _black(self, surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    def _draw_sky_and_water(self, surface: pygame.Surface) -> None:
        width, _height = surface.get_size()
        for y in range(_HORIZON):
            t = y / max(1, _HORIZON - 1)
            if t < 0.7:
                a, b, k = _SKY_TOP, _SKY_LOW, t / 0.7
            else:
                a, b, k = _SKY_LOW, _SKY_GLOW, (t - 0.7) / 0.3
            surface.fill(tuple(round(a[i] + (b[i] - a[i]) * k)
                               for i in range(3)), (0, y, width, 1))
        # The first stars, in the dark top of the sky only.
        for index in range(18):
            x = (index * 53 + 17) % width
            y = (index * 29) % (_HORIZON // 2)
            if (index + int(self.elapsed * 1.3)) % 7:
                surface.set_at((x, y), _STAR)
        pygame.draw.rect(surface, _WATER,
                         (0, _HORIZON, width, _QUAY_Y - _HORIZON))
        for index in range(16):
            wave_y = _HORIZON + 3 + (index * 3) % (_QUAY_Y - _HORIZON - 4)
            run = (index * 41 + int(self.elapsed * 6)) % width
            colour = _WATER_FLECK if index % 5 == 0 else _WATER_LIT
            pygame.draw.rect(surface, colour, (run, wave_y, 11, 1))
        # One late gull heading home.
        gx = int(40 + (self.elapsed * 9) % (width + 40)) - 20
        gy = 24 + round(math.sin(self.elapsed * 0.8) * 2)
        pygame.draw.line(surface, _GULL, (gx - 3, gy), (gx, gy - 2))
        pygame.draw.line(surface, _GULL, (gx, gy - 2), (gx + 3, gy))

    def _draw_quay(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        tile = config.TILE_SIZE
        if self._planks:
            variants, frames = self._plank_info
            for row, y in enumerate(range(_QUAY_Y, height, tile)):
                for col, x in enumerate(range(0, width, tile)):
                    surface.blit(self._planks[art_index(col, row, variants,
                                                        frames, 0.0)], (x, y))
        else:
            pygame.draw.rect(surface, _DOCK_PLANK,
                             (0, _QUAY_Y, width, height - _QUAY_Y))
        pygame.draw.rect(surface, _DOCK_SEAM, (0, _QUAY_Y, width, 2))

    def _draw_moorings(self, surface: pygame.Surface) -> None:
        if self._post is not None:
            post_w, post_h = self._post.get_size()
            for x in _POST_XS:
                surface.blit(self._post,
                             (x - post_w // 2, _POST_BASE_Y - post_h))
        if self._boat is None:
            return
        bow = (_BOAT_X + 9, _BOAT_Y + 5)
        post = (_MOORED_POST - 1, _POST_BASE_Y - 8)
        for step in range(19):
            t = step / 18
            x = bow[0] + (post[0] - bow[0]) * t
            y = bow[1] + (post[1] - bow[1]) * t + math.sin(t * math.pi) * 3
            surface.set_at((round(x), round(y)), (184, 149, 91))

    def _draw_bobert_and_chuck(self, surface: pygame.Surface) -> None:
        if self._barrel is not None:
            surface.blit(self._barrel, (_BARREL_X, _BARREL_BASE
                                        - self._barrel.get_height()))
        # Bobert snores all the way through, a Z every couple of seconds.
        self._draw_zs(surface, (_BARREL_X + 13, _BARREL_BASE - 28), 2.1, 4)
        if self.elapsed < WAKE:
            self._draw_asleep(surface)
            return
        facing = self._facing()
        frame = self._frames.get(facing)
        if frame is None:
            return
        if facing == "left" and not self.cigarette_lit \
                and self._unlit is not None:
            frame = self._unlit
        surface.blit(frame, (_CHUCK_X, _CHUCK_Y))
        if self.elapsed >= LIGHTER and facing == "left":
            self._draw_smoke(surface)

    def _draw_asleep(self, surface: pygame.Surface) -> None:
        if not self._asleep:
            return
        breathing = self.elapsed < STIR
        index = int(self.elapsed / 1.1) % 2 if breathing else 0
        frame = self._asleep[index]
        x = _SLEEP_X
        if STIR <= self.elapsed < STIR + 0.25:
            x += 1                                  # the twitch
        surface.blit(frame, (x, _SLEEP_BASE - frame.get_height()))
        if breathing:
            self._draw_zs(surface, (_SLEEP_X + 4, _SLEEP_BASE - 11), 1.6, 3)

    def _draw_zs(self, surface, origin, period: float, size: int) -> None:
        """Z's drifting up and to the right, one per period, fading."""
        ox, oy = origin
        for offset in (0.0, period / 2):
            t = ((self.elapsed + offset) % period) / period
            x = round(ox + t * 8)
            y = round(oy - t * 12)
            if t > 0.8:
                continue
            for i in range(size + 1):
                surface.set_at((x + i, y), _Z)
                surface.set_at((x + i, y + size), _Z)
                surface.set_at((x + size - i, y + i), _Z)

    def _facing(self) -> str:
        if self.elapsed < LOOK_LEFT:
            return "down"
        if self.elapsed < LOOK_RIGHT:
            return "left"
        if self.elapsed < FACE_LEFT:
            return "right"
        return "left"

    def _draw_smoke(self, surface: pygame.Surface) -> None:
        mouth = (_CHUCK_X, _CHUCK_Y + 7)
        if LIGHTER <= self.elapsed < LIT:
            # The lighter's flame, flickering at the end of the cigarette.
            flicker = int(self.elapsed * 20) % 2
            surface.set_at((mouth[0] - 1, mouth[1] - 1 - flicker),
                           (255, 214, 120))
            surface.set_at((mouth[0] - 1, mouth[1] - flicker),
                           (255, 150, 60))
            return
        if self.elapsed >= DRAG and int(self.elapsed * 2) % 3 == 0:
            surface.set_at(mouth, (255, 190, 110))      # the drag
        for puff in range(3):
            t = ((self.elapsed - LIT) * 0.5 + puff / 3) % 1.0
            x = round(mouth[0] - t * 5 + math.sin(t * 6 + puff) * 1.5)
            y = round(mouth[1] - 2 - t * 14)
            shade = 150 + round(60 * (1 - t))
            if t < 0.85:
                surface.set_at((x, y), (shade, shade, shade - 6))
