"""Phase 6's escape: Chuck crawls out of the rubble and reaches a ship.

A contained, input-free cutscene (the Phase 6 -> 7 boundary). Chuck
squeezes through the tight stone crawlspace toward a growing blade of
daylight; the light swallows the screen; he emerges into a cramped
wooden hold with the open sea beyond a breach in the hull. Three quiet
lines land the moment — he has reached a ship, and does not yet know it
— before the scene hands off to the playable deck. Sanity carries over.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene

CRAWL_END = 5.0        # crawling the tunnel toward the light
WHITEOUT = 5.6         # the daylight swallows the screen
SEA_MUSIC = 5.6        # the sea theme swells in as he emerges
REVEAL_IN = 6.6        # the whiteout has faded to the hold + sea
CAP1 = 6.9
CAP2 = 8.8
CAP3 = 10.9
HOLD_END = 13.6
FADE_END = 14.4        # then hand off to the ship deck

_CAPTIONS = (
    (CAP1, "Daylight, at last."),
    (CAP2, "Salt air, and the sound of the sea."),
    (CAP3, "Chuck has reached a ship. He does not yet know it."),
)

_DEEP = (8, 8, 12)
_DAYLIGHT = (250, 244, 224)
_SKY = (150, 178, 198)
_SEA = (26, 30, 64)
_SEA_GLINT = (120, 150, 200)
_WOOD = (104, 74, 46)
_WOOD_LINE = (78, 54, 34)
_HULL = (64, 46, 28)
_CAP_COLOR = (234, 230, 216)


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _ease(v: float) -> float:
    v = _clamp01(v)
    return v * v * (3.0 - 2.0 * v)


class EscapeCutsceneScene(Scene):
    """Crawl -> daylight -> the ship. Ends Phase 6."""

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
        self._frames = {"up": grid[1][0], "down": grid[0][0]}
        self.game.audio.stop_music(fade_ms=300)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += dt
        # Scraping through the tight passage.
        for cue in (1.2, 2.6, 4.0):
            if previous < cue <= self.elapsed:
                self.game.audio.play_sfx("scratch")
        if previous < SEA_MUSIC <= self.elapsed:
            self.game.audio.play_music("waterdeep_docks.wav", loop=True)
        if self.elapsed >= FADE_END and not self._handed_off:
            # Onto the playable deck, Sanity intact. Phase 6 ends here.
            self._handed_off = True
            self.game.checkpoints.load_checkpoint(
                "ship_deck", sanity=self._sanity
            )

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        t = self.elapsed
        if t < WHITEOUT:
            self._draw_crawl(surface)
            if t >= CRAWL_END:
                self._white(surface, (t - CRAWL_END) / (WHITEOUT - CRAWL_END))
        else:
            self._draw_hold(surface)
            if t < REVEAL_IN:
                self._white(surface, 1.0 - (t - WHITEOUT) / (REVEAL_IN - WHITEOUT))
            self._draw_captions(surface)
        if t >= HOLD_END:
            self._black(surface, (t - HOLD_END) / (FADE_END - HOLD_END))

    def _white(self, surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.fill(_DAYLIGHT)
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    def _black(self, surface, amount: float) -> None:
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(round(255 * _clamp01(amount)))
        surface.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # The crawl: a stone tunnel receding to a growing point of daylight.
    # ------------------------------------------------------------------
    def _draw_crawl(self, surface: pygame.Surface) -> None:
        w, h = config.NATIVE_WIDTH, config.NATIVE_HEIGHT
        surface.fill(_DEEP)
        cx, cy = w // 2, h // 2 - 8
        prog = _ease(self.elapsed / CRAWL_END)
        light_r = round(5 + prog * 42)
        # Stone rings scrolling outward from the light give forward motion.
        for i in range(10, 0, -1):
            f = ((i + self.elapsed * 2.4) % 10) / 10.0
            rw = round(f * w * 0.95) + light_r
            rh = round(f * h * 0.95) + light_r
            shade = round(14 + f * 40)
            pygame.draw.rect(surface, (shade, shade - 2, max(0, shade - 5)),
                             (cx - rw // 2, cy - rh // 2, rw, rh), 3)
        # The daylight at the tunnel's end.
        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*_DAYLIGHT, 110),
                            (cx - light_r - 8, cy - light_r - 8,
                             light_r * 2 + 16, light_r * 2 + 16))
        pygame.draw.ellipse(glow, (255, 250, 236, 255),
                            (cx - light_r, cy - light_r,
                             light_r * 2, light_r * 2))
        surface.blit(glow, (0, 0))
        # Tight-space vignette: dark stone crowds the corners.
        for corner in ((0, 0), (w, 0), (0, h), (w, h)):
            dark = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(dark, (4, 4, 6, 200), corner, 96)
            surface.blit(dark, (0, 0))
        # Chuck, back turned, crawling toward it with a low wobble.
        frame = self._frames.get("up")
        if frame is not None:
            scale = 2
            img = pygame.transform.scale(
                frame, (config.CHUCK_FRAME_W * scale,
                        config.CHUCK_FRAME_H * scale))
            wob = round(math.sin(self.elapsed * 7.0) * 3)
            duck = round(abs(math.sin(self.elapsed * 3.5)) * 2)
            surface.blit(img, (cx - img.get_width() // 2 + wob,
                               h - 46 + duck))

    # ------------------------------------------------------------------
    # The hold: wooden room, the open sea through a breach in the hull.
    # ------------------------------------------------------------------
    def _draw_hold(self, surface: pygame.Surface) -> None:
        w, h = config.NATIVE_WIDTH, config.NATIVE_HEIGHT
        surface.fill(_WOOD)
        sea_bottom = 66
        pygame.draw.rect(surface, _SKY, (0, 0, w, 12))
        pygame.draw.rect(surface, _SEA, (0, 12, w, sea_bottom - 12))
        # A slow swell of glints on the water.
        for i in range(46):
            gx = (i * 43 + round(self.elapsed * 9)) % w
            gy = 16 + (i * 17) % (sea_bottom - 20)
            if (i + round(self.elapsed * 2)) % 3 == 0:
                surface.set_at((gx, gy), _SEA_GLINT)
        # The broken hull framing the breach.
        pygame.draw.rect(surface, _HULL, (0, sea_bottom - 4, w, 8))
        for x in range(0, w, 12):
            jag = 2 if (x // 12) % 2 else 5
            pygame.draw.rect(surface, _HULL, (x, sea_bottom - 4, 6, jag))
        # Plank deck below, with a couple of cargo silhouettes.
        for y in range(sea_bottom + 6, h, 8):
            pygame.draw.line(surface, _WOOD_LINE, (0, y), (w, y))
        for bx in (40, 250):
            pygame.draw.rect(surface, (58, 40, 26), (bx, 96, 20, 18))
            pygame.draw.line(surface, (86, 60, 38), (bx, 104), (bx + 20, 104))
        # Chuck standing on the deck, looking up at the sea.
        frame = self._frames.get("up")
        if frame is not None:
            scale = 2
            img = pygame.transform.scale(
                frame, (config.CHUCK_FRAME_W * scale,
                        config.CHUCK_FRAME_H * scale))
            surface.blit(img, (w // 2 - img.get_width() // 2, 120))

    def _draw_captions(self, surface: pygame.Surface) -> None:
        text = None
        for start, line in _CAPTIONS:
            if self.elapsed >= start:
                text = (start, line)
        if text is None:
            return
        start, line = text
        alpha = round(255 * _ease((self.elapsed - start) / 0.5))
        font = self.game.assets.bitmap_font()
        img = font.render(line, False, _CAP_COLOR)
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        surface.blit(img, ((config.NATIVE_WIDTH - img.get_width()) // 2,
                           config.NATIVE_HEIGHT - 24))
