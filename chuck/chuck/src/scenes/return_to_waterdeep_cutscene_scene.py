"""Phase 13's exit: the worlds come apart and Chuck goes home.

The wizard's answer to "where's he going" is "where he belongs", and
this is that sentence happening. The heroes finish; the collision lets
go; and everything that had been jammed into one place snaps back to
wherever it came from, with a rat in the middle of it who was never
supposed to be there.

It is built as the last of the game's repeated world-transition
sequences and it quotes all of them on purpose. The whiteout is the
table portal's. The rushing bands are the fall to Chult seen sideways.
The Astral Sea between them is the same Sea that has been the seam of
every crossing since the pantry. What is new is only the direction:
every other one of these took him somewhere. This one takes him back.

The fragments separating is the thing to get right, and the way to get
it right is to make them *leave* rather than to make them busy. Bands
of each world stream past, and one by one they thin out and stop
coming, until there is nothing rushing at all -- and what is left when
the noise stops is planks, and water, and gulls. He is standing on the
Waterdeep docks.

Then it holds, and the white clears onto the same docks as a playable
midday place. Phase 14 begins without making Chuck leave Waterdeep and
come back again through a title screen.

No words. He does not get a line here either.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene
from src.systems.checkpoints import WATERDEEP_RETURN_FLAG
from src.world.tileset_layout import DOCKS_MIDDAY, TILE_PX, art_index


BLAST_END = 1.6         # the rift lets go: white, and a shove
STREAM_START = 1.2      # ...and the worlds start going past
THINNING = 7.0          # they begin leaving, one at a time
STREAM_END = 12.0       # the last band is gone
DOCKS_IN = 13.6         # planks, water, gulls
LOOK_START = 14.6       # he checks: left, right, down
CIGARETTE_START = 17.0
DRAG_START = 18.4
HOLD_END = 21.0
FADE_END = 22.6

MUSIC_START = 0.4

# One band per world, in the order the walk east met them, so the
# sequence reads as the journey being played backwards and put away.
# (colour, pale streak, how long it keeps coming)
_BANDS = (
    ((186, 202, 224), (232, 240, 250), 11.2),   # the frozen shelf
    ((128, 126, 122), (168, 166, 160), 10.4),   # the courtyard
    ((96, 72, 46), (140, 108, 70), 9.6),        # the ship's deck
    ((58, 35, 30), (178, 45, 12), 8.8),         # Phlegethos
    ((46, 74, 60), (128, 96, 176), 8.0),        # the Feywild
    ((37, 44, 28), (56, 96, 52), 7.2),          # Chult
    ((64, 66, 74), (156, 158, 166), 6.4),       # the modern city
    # The desert goes last, and it goes before the rush ends: a
    # band still running when the sequence is over is a world
    # that never left.
    ((214, 178, 122), (236, 206, 156), 11.8),   # the desert
)

_SEA = (14, 16, 42)
_STAR = (226, 232, 255)

# The quay is drawn from the same midday dock sheet the map he lands on
# uses -- he arrives on the planks beside Bobert's barrel, and a cutscene
# quay of cut stone was a different dock from the one the fade clears to.
# The flat colours are only the headless fallback.
_DOCK_TERRAIN = "planks"
_DOCK_PLANK = (174, 132, 82)
_DOCK_PLANK_LIT = (190, 150, 98)
_DOCK_SEAM = (126, 88, 50)
_WATER = (46, 74, 96)
_WATER_LIT = (86, 122, 142)
_SKY = (150, 166, 186)
_SKY_LOW = (198, 202, 206)
_GULL = (238, 240, 244)

_HORIZON = 62
_QUAY_Y = 108
_CHUCK_X = 148
_CHUCK_Y = 132

# The harbour dressing at the quay edge, in this view's terms: the posts
# stand along the far edge of the planks where the dock meets the water,
# and a rowboat lies on the water beyond one of them. Looking north from
# the quay, the boat shows its near side and its inside and the line runs
# down from its bow, over the edge, to the post -- the same boat and the
# same posts the map has, at the map's own scale.
_POST_XS = (34, 92, 214, 276)
_POST_BASE_Y = _QUAY_Y + 5          # just in from the edge
_MOORED_POST = 92
_BOAT_X, _BOAT_Y = 52, 82           # top-left of the hull's crop


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class ReturnToWaterdeepCutsceneScene(Scene):
    """Blast, streaming worlds, and the docks. Ends Phase 13."""

    pausable = True

    def __init__(self, game, sanity: int | None = None) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self._sanity = sanity
        self._frames: dict[str, pygame.Surface] = {}
        self._unlit: pygame.Surface | None = None
        self._planks: list[pygame.Surface] = []
        self._plank_info: tuple[int, int] = (1, 1)
        self._post: pygame.Surface | None = None
        self._boat: pygame.Surface | None = None
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
        self._unlit = grid[2][0].copy()
        self._unlit.set_at((0, 7), (0, 0, 0, 0))
        self._unlit.set_at((1, 7), (0, 0, 0, 0))
        self._load_planks()
        self._load_harbour()
        self.game.audio.stop_music(fade_ms=600)

    def _load_harbour(self) -> None:
        """The map's own mooring post and midday rowboat sprites."""
        try:
            self._post = self.game.assets.image("objects/harbour_bollard.png")
            boat = self.game.assets.image(
                "objects/harbour_rowboat_midday.png")
        except (FileNotFoundError, pygame.error):
            return
        # The hull only: the sprite's own mooring line runs up the screen to
        # a post south of the boat, and here the post is south of it the
        # other way round -- below it on the screen. The line is drawn
        # fresh instead.
        self._boat = boat.subsurface((0, 22, boat.get_width(),
                                      boat.get_height() - 22)).copy()

    def _load_planks(self) -> None:
        """The dock's own plank tiles, from the midday sheet."""
        try:
            rows = self.game.assets.tileset(DOCKS_MIDDAY.sheet, TILE_PX)
        except (FileNotFoundError, pygame.error):
            return
        for index, (name, variants, frames) in enumerate(DOCKS_MIDDAY.order):
            if name == _DOCK_TERRAIN:
                self._planks = rows[index][: variants * frames]
                self._plank_info = (variants, frames)
                return

    # ------------------------------------------------------------------
    @property
    def phase(self) -> str:
        if self.elapsed < BLAST_END:
            return "blast"
        if self.elapsed < STREAM_END:
            return "streaming"
        if self.elapsed < DOCKS_IN:
            return "arriving"
        if self.elapsed < HOLD_END:
            return "docks"
        return "fading"

    @property
    def bands_left(self) -> int:
        """How many worlds are still going past.

        They leave one at a time rather than all at once. All of them
        stopping together is a effect being switched off; them thinning
        out is a thing ending.
        """
        return sum(1 for _c, _s, until in _BANDS if self.elapsed < until)

    @property
    def cigarette_lit(self) -> bool:
        return self.elapsed >= DRAG_START

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += dt
        self._play_cues(previous, self.elapsed)
        if self.elapsed < FADE_END or self._handed_off:
            return
        self._handed_off = True
        # Phase 14 begins here. Bank the crossing before the shared loader
        # rebuilds Waterdeep so state-driven daylight is selected on its
        # first frame. This crossing is not itself a save point; the docks'
        # existing Ashtray still owns durable Continue state.
        self.game.progress.enable(WATERDEEP_RETURN_FLAG)
        self.game.checkpoints.load_checkpoint(
            "waterdeep_finale",
            progress_flags=self.game.progress.flags,
            sanity=self._sanity,
        )

    def _play_cues(self, previous: float, current: float) -> None:
        if previous < MUSIC_START <= current:
            self.game.audio.play_music("desert_arrival.wav", loop=False)
        cues = (
            (0.05, "vanish"),
            (STREAM_START, "portal_hum"),
            (STREAM_END, "portal_collapse"),
            (LOOK_START, "footstep_wood_1"),
            (CIGARETTE_START + 1.4, "lighter"),
        )
        for cue_time, sound in cues:
            if previous < cue_time <= current:
                self.game.audio.play_sfx(sound)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.elapsed < STREAM_END:
            self._draw_stream(surface)
        else:
            self._draw_docks(surface)
            if self.elapsed >= LOOK_START:
                self._draw_chuck(surface)
        if self.elapsed < BLAST_END:
            self._white(surface, 1.0 - _ease(self.elapsed / BLAST_END))
        elif STREAM_END <= self.elapsed < DOCKS_IN:
            # The last of the rush washes out into the quay. Bounded at
            # both ends: written as "before the docks arrive" alone, it
            # covered the whole streaming sequence in white, because
            # everything before STREAM_END clamps to nothing faded.
            self._white(surface, 1.0 - _ease(
                (self.elapsed - STREAM_END) / (DOCKS_IN - STREAM_END)))
        if self.elapsed >= HOLD_END:
            self._white(surface, (self.elapsed - HOLD_END)
                        / (FADE_END - HOLD_END))

    def _white(self, surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((250, 250, 252))
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    def _draw_stream(self, surface: pygame.Surface) -> None:
        """The worlds going past, and then not.

        Horizontal bands on the Astral Sea, each moving at its own
        speed. A band stops being drawn when its world has finished
        leaving, and the gap it leaves fills with Sea -- so the screen
        empties out over the sequence instead of staying busy to the
        end.
        """
        surface.fill(_SEA)
        width, height = surface.get_size()
        for index in range(46):
            star_x = (index * 97 + int(self.elapsed * 40)) % width
            star_y = (index * 61) % height
            surface.set_at((star_x, star_y), _STAR)

        band_h = height // len(_BANDS)
        for index, (colour, streak, until) in enumerate(_BANDS):
            if self.elapsed >= until:
                continue
            # Each band fades as its world finishes leaving rather than
            # blinking out: a fragment that vanishes on one frame reads
            # as a draw error.
            leaving = _clamp01((until - self.elapsed) / 1.6)
            top = index * band_h
            depth = max(3, round(band_h * leaving))
            speed = 240 + index * 55
            shift = int(self.elapsed * speed)
            band = pygame.Surface((width, depth))
            band.fill(colour)
            for streak_i in range(7):
                sx = (streak_i * 61 + shift) % (width + 40) - 20
                pygame.draw.rect(band, streak,
                                 (sx, (streak_i * 3) % max(1, depth - 2),
                                  26, max(1, depth // 4)))
            surface.blit(band, (0, top + (band_h - depth) // 2))

    def _draw_docks(self, surface: pygame.Surface) -> None:
        """Planks, water, gulls. Waterdeep, from the quayside."""
        width, height = surface.get_size()
        for y in range(_HORIZON):
            blend = y / max(1, _HORIZON)
            surface.fill(
                tuple(round(_SKY[i] + (_SKY_LOW[i] - _SKY[i]) * blend)
                      for i in range(3)),
                (0, y, width, 1),
            )
        pygame.draw.rect(surface, _WATER,
                         (0, _HORIZON, width, _QUAY_Y - _HORIZON))
        for index in range(14):
            wave_y = _HORIZON + 3 + (index * 3) % (_QUAY_Y - _HORIZON - 4)
            run = (index * 37 + int(self.elapsed * 7)) % width
            pygame.draw.rect(surface, _WATER_LIT, (run, wave_y, 13, 1))

        if self._boat is not None:
            surface.blit(self._boat, (_BOAT_X, _BOAT_Y))
        self._draw_quay(surface)

        # Two gulls, because the quiet needs something moving in it.
        for index, (base_x, base_y, speed) in enumerate(
                ((70, 26, 11.0), (216, 40, 7.0))):
            gx = int(base_x + math.sin(self.elapsed * 0.6 + index) * 26)
            gy = int(base_y + math.sin(self.elapsed * speed * 0.1 + index) * 3)
            pygame.draw.line(surface, _GULL, (gx - 3, gy), (gx, gy - 2))
            pygame.draw.line(surface, _GULL, (gx, gy - 2), (gx + 3, gy))

    def _draw_quay(self, surface: pygame.Surface) -> None:
        """The dock's planks, tile for tile, from the quay's edge down.

        Variants are picked by the same rule the map uses, so the boards
        do not repeat in a visible stripe. A dark lip along the top edge
        is the side of the dock where it drops to the water.
        """
        width, height = surface.get_size()
        tile = config.TILE_SIZE
        if self._planks:
            variants, frames = self._plank_info
            for row, y in enumerate(range(_QUAY_Y, height, tile)):
                for col, x in enumerate(range(0, width, tile)):
                    art = self._planks[art_index(col, row, variants, frames,
                                                 self.elapsed)]
                    surface.blit(art, (x, y))
        else:
            pygame.draw.rect(surface, _DOCK_PLANK,
                             (0, _QUAY_Y, width, height - _QUAY_Y))
            for y in range(_QUAY_Y + 4, height, 4):
                pygame.draw.line(surface, _DOCK_SEAM, (0, y), (width, y))
            pygame.draw.rect(surface, _DOCK_PLANK_LIT, (0, _QUAY_Y, width, 1))
        pygame.draw.rect(surface, _DOCK_SEAM, (0, _QUAY_Y, width, 2))
        self._draw_moorings(surface)

    def _draw_moorings(self, surface: pygame.Surface) -> None:
        """Posts along the quay edge, and the boat tied to one of them."""
        if self._post is not None:
            post_w, post_h = self._post.get_size()
            for x in _POST_XS:
                surface.blit(self._post,
                             (x - post_w // 2, _POST_BASE_Y - post_h))
        if self._boat is None:
            return
        # The bow ring, in the cropped hull's coordinates (the sprite's
        # (9, 27) less the 22 rows cropped off its top).
        bow = (_BOAT_X + 9, _BOAT_Y + 5)
        post = (_MOORED_POST - 1, _POST_BASE_Y - 8)
        steps = 18
        for step in range(steps + 1):
            t = step / steps
            x = bow[0] + (post[0] - bow[0]) * t
            y = bow[1] + (post[1] - bow[1]) * t + math.sin(t * math.pi) * 3
            surface.set_at((round(x), round(y)), (184, 149, 91))

    # ------------------------------------------------------------------
    def _facing(self) -> str:
        """He checks where he is: left, right, and then down at himself."""
        since = self.elapsed - LOOK_START
        if since < 0.9:
            return "left"
        if since < 1.8:
            return "right"
        return "down"

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        facing = self._facing()
        frame = self._frames.get(facing)
        if frame is None:
            return
        if (facing == "left" and self.elapsed < CIGARETTE_START
                and self._unlit is not None):
            frame = self._unlit
        surface.blit(frame, (_CHUCK_X, _CHUCK_Y))
        if self.cigarette_lit:
            surface.set_at((_CHUCK_X + 1, _CHUCK_Y + 7), (242, 146, 66))
            wisp = int((self.elapsed - DRAG_START) * 6) % 4
            surface.set_at((_CHUCK_X, _CHUCK_Y + 5 - wisp), (198, 198, 188))
