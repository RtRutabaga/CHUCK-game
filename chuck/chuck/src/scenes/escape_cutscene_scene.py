"""Phase 6's escape: Chuck crawls out of the rubble and reaches a ship.

A contained, input-free cutscene (the Phase 6 -> 7 boundary). Chuck
squeezes through the tight stone crawlspace toward a growing blade of
daylight; the light swallows the screen; he emerges into a cramped
wooden hold whose hull is set with round portholes — the sunlit sea
visible through them, but plainly an interior. The tableau holds, then
hands off to the playable deck. Sanity carries over. No words.
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
HOLD_END = 11.4        # the tableau holds wordlessly
FADE_END = 12.2        # then hand off to the ship deck

_DEEP = (8, 8, 12)
_DAYLIGHT = (250, 244, 224)
# A sunny-day sea seen through the portholes.
_SKY = (196, 224, 240)
_SEA = (96, 164, 214)
_SEA_DEEP = (66, 138, 196)
_SEA_GLINT = (214, 236, 250)
# The ship's wooden interior.
_WOOD = (120, 84, 52)
_WALL = (92, 64, 40)
_WOOD_LINE = (78, 54, 34)
_RIM = (150, 120, 66)      # brass porthole rim
_RIM_DARK = (96, 74, 38)


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
            self.game.audio.play_music("ship_shanty.wav", loop=True)
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
    # The hold: a wooden interior whose hull is set with portholes onto
    # the sunlit sea. Plainly inside a ship, the sea framed in circles.
    # ------------------------------------------------------------------
    def _draw_hold(self, surface: pygame.Surface) -> None:
        w, h = config.NATIVE_WIDTH, config.NATIVE_HEIGHT
        surface.fill(_WOOD)
        # The upper hull wall, planked, carrying the portholes.
        wall_bottom = 74
        surface.fill(_WALL, (0, 0, w, wall_bottom))
        for y in range(0, wall_bottom, 9):
            pygame.draw.line(surface, _WOOD_LINE, (0, y), (w, y))
        for cx in (58, 160, 262):
            self._draw_porthole(surface, cx, 37, 22)
        # A beam divides the hull wall from the deck below.
        pygame.draw.rect(surface, _RIM_DARK, (0, wall_bottom - 3, w, 4))
        # Plank deck, with a couple of lashed cargo crates.
        for y in range(wall_bottom + 6, h, 8):
            pygame.draw.line(surface, _WOOD_LINE, (0, y), (w, y))
        for bx in (34, 256):
            pygame.draw.rect(surface, (74, 52, 32), (bx, 104, 22, 18))
            pygame.draw.line(surface, (96, 68, 42), (bx, 112), (bx + 22, 112))
        # Chuck standing on the deck, looking up at the portholes.
        frame = self._frames.get("up")
        if frame is not None:
            scale = 2
            img = pygame.transform.scale(
                frame, (config.CHUCK_FRAME_W * scale,
                        config.CHUCK_FRAME_H * scale))
            surface.blit(img, (w // 2 - img.get_width() // 2, 128))

    def _draw_porthole(self, surface, cx: int, cy: int, r: int) -> None:
        """One round window: sunlit sea and sky over a horizon, brass rim."""
        glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        gx = r  # local center
        horizon = round(r * 0.9)
        pygame.draw.circle(glass, _SKY, (gx, gx), r)
        # The sea fills the lower part of the circle, darker toward the rim.
        for y in range(horizon, r * 2):
            shade = y / (r * 2)
            col = tuple(round(a + (b - a) * shade)
                        for a, b in zip(_SEA, _SEA_DEEP))
            pygame.draw.line(glass, col, (0, y), (r * 2, y))
        # Re-mask to the circle so the sea lines don't spill to the corners.
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (gx, gx), r)
        glass.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # A couple of moving glints on the water.
        for i in range(3):
            wx = gx + round(math.sin(self.elapsed * 0.9 + i * 2.1) * (r - 6))
            wy = horizon + 4 + i * 5
            if wy < r * 2 - 2:
                glass.set_at((wx, wy), _SEA_GLINT)
        surface.blit(glass, (cx - r, cy - r))
        # Brass rim with rivets, sitting proud of the hull.
        pygame.draw.circle(surface, _RIM, (cx, cy), r + 2, 3)
        pygame.draw.circle(surface, _RIM_DARK, (cx, cy), r + 2, 1)
        for a in range(0, 360, 45):
            rx = cx + round(math.cos(math.radians(a)) * (r + 2))
            ry = cy + round(math.sin(math.radians(a)) * (r + 2))
            surface.set_at((rx, ry), _RIM_DARK)
