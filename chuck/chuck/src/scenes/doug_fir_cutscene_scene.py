"""Phase 11's exit: Chuck steps out of a Douglas fir at night.

The city's last map holds a block of forest that is plainly somewhere
else. Stepping into it plays this: black, then a Pacific Northwest
stand at night fading up in side view, then Chuck walking out of the
trunk of the largest fir as if the tree were a doorway -- because on
this map it was one. The tableau holds long enough to read, then goes
back to black.

Phase 12 now continues directly from that completed boundary.  Once the
fade reaches black, the scene selects the authored Tahuya exterior entry
through the same checkpoint loader used by Continue and the development
menu.  The first physical Ashtray on the grounds is still the point that
persists the crossing to disk.

No words. Sanity carries into the save unchanged.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.planar_portal import portal_colour
from src.scenes.scene import Scene


FADE_IN_END = 2.6       # the forest resolves out of black
WALK_START = 3.0        # ...and only then does anything move in it
WALK_END = 6.2          # Chuck clears the trunk and stops
HOLD_END = 10.4         # the stand holds, wordless
FADE_END = 11.6         # back to black, and out of the phase

DOUG_FIR_FLAG = "doug_fir_transition_completed"

_NIGHT_TOP = (10, 16, 30)
_NIGHT_LOW = (22, 34, 44)
_MOON = (226, 236, 226)
_TRUNK = (36, 28, 22)
_TRUNK_LIT = (62, 52, 40)
_NEEDLE = (10, 30, 26)
_NEEDLE_LIT = (26, 54, 44)
_NEEDLE_FAR = (14, 26, 32)
_GROUND = (20, 26, 22)
_GROUND_LIT = (34, 44, 34)
_FERN = (24, 48, 38)
_DOORWAY = (5, 6, 10)

# The doorway tree: tall, wide, and centre-left so Chuck walks into
# open ground rather than out of frame.
_HERO_X = 108
_HERO_HALF = 30
_GROUND_Y = 138


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class DougFirCutsceneScene(Scene):
    """Forest at night, one rat, no dialogue; hands into Phase 12."""

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
        right = pygame.transform.flip(grid[2][0], True, False)
        self._frames = {"right": right, "down": grid[0][0]}
        # The city, the rain and the Beholder theme all stop at the
        # trunk. What is on the other side is quiet.
        self.game.audio.stop_music(fade_ms=600)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    @property
    def phase(self) -> str:
        if self.elapsed < FADE_IN_END:
            return "fade_in"
        if self.elapsed < WALK_START:
            return "still"
        if self.elapsed < WALK_END:
            return "walking"
        if self.elapsed < HOLD_END:
            return "hold"
        return "fade_out"

    @property
    def walk_progress(self) -> float:
        """0 at the trunk, 1 at the spot he stops on."""
        if self.elapsed <= WALK_START:
            return 0.0
        return _ease((self.elapsed - WALK_START) / (WALK_END - WALK_START))

    @property
    def chuck_position(self) -> tuple[int, int]:
        """Top-left of the sprite: starts centred in the trunk's dark."""
        x = (_HERO_X - config.CHUCK_FRAME_W // 2
             + round(self.walk_progress * 52))
        return x, _GROUND_Y - config.CHUCK_FRAME_H

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed < FADE_END or self._handed_off:
            return
        self._handed_off = True
        # Phase 11 ends here.  Record the crossing, then use the shared
        # checkpoint path to enter the playable cabin grounds with the
        # running Sanity value intact.  The nearby Ashtray owns persistence.
        self.game.progress.enable(DOUG_FIR_FLAG)
        flags = set(self.game.progress.flags)
        self.game.checkpoints.load_checkpoint(
            "tahuya_exterior", progress_flags=flags, sanity=self._sanity
        )

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_forest(surface)
        if self.elapsed >= WALK_START:
            self._draw_chuck(surface)
        if self.elapsed < FADE_IN_END:
            self._black(surface, 1.0 - _ease(self.elapsed / FADE_IN_END))
        elif self.elapsed >= HOLD_END:
            self._black(
                surface, (self.elapsed - HOLD_END) / (FADE_END - HOLD_END)
            )

    def _black(self, surface: pygame.Surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # A stand of Douglas fir at night, in side view.
    # ------------------------------------------------------------------
    def _draw_forest(self, surface: pygame.Surface) -> None:
        width, height = config.NATIVE_WIDTH, config.NATIVE_HEIGHT
        for y in range(height):
            blend = min(1.0, y / max(1, _GROUND_Y))
            surface.fill(
                tuple(
                    round(top + (low - top) * blend)
                    for top, low in zip(_NIGHT_TOP, _NIGHT_LOW)
                ),
                (0, y, width, 1),
            )
        for index in range(46):
            x = (index * 97 + 13) % width
            y = (index * 41 + 7) % (_GROUND_Y - 60)
            if abs(x - 262) < 24 and y < 42:
                continue     # nothing twinkles inside the moon's glare
            surface.set_at((x, y), (150, 168, 176))
        pygame.draw.circle(surface, _MOON, (262, 24), 9)
        pygame.draw.circle(surface, _NIGHT_TOP, (257, 21), 8)

        # The far stand: overlapping silhouettes with no detail at all,
        # so the depth comes from mass rather than from drawn trees.
        for index in range(13):
            x = index * 27 - 8
            self._draw_fir(surface, x, 20, 30 + (index * 37) % 34,
                           colour=_NEEDLE_FAR, trunk=False)

        pygame.draw.rect(surface, _GROUND,
                         (0, _GROUND_Y, width, height - _GROUND_Y))
        for index in range(80):
            x = (index * 53 + 11) % width
            y = _GROUND_Y + 2 + (index * 17) % (height - _GROUND_Y - 3)
            pygame.draw.line(surface, _GROUND_LIT if index % 3 else _FERN,
                             (x, y), (x + 3, y))

        # The near trees, then the hero fir with the doorway in it.
        for x, half, top in ((26, 26, 14), (208, 24, 8), (296, 22, 24)):
            self._draw_fir(surface, x, half, top)
        self._draw_fir(surface, _HERO_X, _HERO_HALF, 2, hero=True)

    def _draw_fir(self, surface, x: int, base_half: int, top: int,
                  *, hero: bool = False, colour=_NEEDLE,
                  trunk: bool = True) -> None:
        """One conifer: stacked skirts widening to a heavy base."""
        trunk_w = 9 if hero else 4
        span = _GROUND_Y - 4 - top
        if span < 20:
            return
        if trunk:
            pygame.draw.rect(
                surface, _TRUNK,
                (x - trunk_w // 2, top + 12, trunk_w, _GROUND_Y - top - 12))
            pygame.draw.line(surface, _TRUNK_LIT,
                             (x + trunk_w // 2, top + 12),
                             (x + trunk_w // 2, _GROUND_Y - 1))
        layers = 9
        depth = round(span / layers * 2.3)
        for step in range(layers):
            reach = step / (layers - 1)
            apex = top + round(reach * (span - depth))
            half = max(2, round(base_half * (0.16 + 0.84 * reach)))
            pygame.draw.polygon(surface, colour, (
                (x - half, apex + depth), (x, apex), (x + half, apex + depth),
            ))
            if trunk:
                # Moonlight is off to the right, so that flank catches it.
                pygame.draw.line(surface, _NEEDLE_LIT,
                                 (x + 1, apex + 2),
                                 (x + half - 2, apex + depth - 1))
        if not hero:
            return
        # The doorway. It is simply the dark inside a tree, which is why
        # it needs no effect on it -- but it breathes a pixel so it does
        # not read as a shape painted on the bark.
        # The base of the doorway tree stands clear of its own skirts,
        # so the dark below reads as an opening in bark rather than a
        # shape floating in the branches.
        pygame.draw.rect(surface, _TRUNK,
                         (x - 11, _GROUND_Y - 26, 22, 26))
        pygame.draw.rect(surface, _TRUNK_LIT,
                         (x + 8, _GROUND_Y - 26, 3, 26))
        for step in range(6):
            bark = _GROUND_Y - 24 + step * 4
            pygame.draw.line(surface, (26, 20, 16),
                             (x - 9, bark), (x - 9 + (step % 3) * 3, bark))
        self._draw_doorway(surface)

    def _draw_doorway(self, surface) -> None:
        """The way through the hero fir, drawn on its own so it can be
        laid over Chuck while he is still standing in it.

        It is the same surface as the oval in the wrecked city block --
        grey with light suspended in it, turning slowly -- rather than
        the flat black it used to be. A hole cut in a tree is a hole; a
        planar portal is the thing Chuck just walked out of, and the two
        openings are the same crossing seen from either side of it.
        """
        breath = round(0.5 + 0.5 * math.sin(self.elapsed * 1.6))
        half_w = 8 + breath
        half_h = 13
        centre_y = _GROUND_Y - half_h
        phase = self.elapsed * 2.2

        pygame.draw.ellipse(
            surface, _DOORWAY,
            (_HERO_X - half_w - 1, centre_y - half_h - 1,
             (half_w + 1) * 2, (half_h + 1) * 2))
        for y in range(-half_h, half_h):
            for x in range(-half_w, half_w):
                nx, ny = (x + 0.5) / half_w, (y + 0.5) / half_h
                if math.hypot(nx, ny) >= 0.94:
                    continue
                # Pushed further from grey than the city oval is. That
                # one is sixty pixels across and can afford to be
                # subtle; this one is twenty and goes flat if it tries.
                surface.set_at((_HERO_X + x, centre_y + y),
                               portal_colour(nx, ny, phase, 0.85))
        # The rim, and one highlight travelling round it, which is what
        # lets the eye see the surface turn at this size.
        pygame.draw.ellipse(
            surface, (104, 102, 114),
            (_HERO_X - half_w, centre_y - half_h, half_w * 2, half_h * 2), 1)
        mote = phase * 0.8
        pygame.draw.circle(
            surface, (224, 222, 230),
            (round(_HERO_X + math.cos(mote) * half_w * 0.7),
             round(centre_y + math.sin(mote) * half_h * 0.7)), 1)

    # ------------------------------------------------------------------
    def _draw_chuck(self, surface: pygame.Surface) -> None:
        frame = self._frames.get(
            "right" if self.phase == "walking" else "down"
        )
        if frame is None:
            return
        x, y = self.chuck_position
        surface.blit(frame, (x, y))
        # He starts inside the tree, so the hollow is drawn again over
        # the top of him: he slides out of the dark rather than popping
        # into existence beside a hole.
        self._draw_doorway(surface)
