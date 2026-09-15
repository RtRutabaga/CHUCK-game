"""The title screen: Chuck, leaning on his own name, having a smoke.

This is the one scene drawn at twice the game's resolution. Everything
else is 320x180 scaled up four times, which is exactly right for a
one-foot rat in a large world and exactly wrong for the one moment he
is meant to be looked at. So the title asks for a 640x360 canvas
(`canvas_size`), the game scales that up twice instead of four times,
and Chuck gets enough pixels for a face.

He is not a still picture. He leans, his tail sways, he blinks, and
every so often he lifts the cigarette, takes a long drag -- the ember
brightens while he does -- lowers it, and lets the smoke out. A thin
thread of smoke comes off the ember the whole time. The timeline is a
pure function of time since the scene opened, so the same moment
always looks the same.

No subtitle. The name and the rat are the whole of it.
"""

from __future__ import annotations

import json
import math
import random

import pygame

from src.core import config
from src.scenes.scene import Scene


TITLE_DIR = "title"

# Wizards of the Coast's Fan Content Policy notice. CHUCK uses places and
# creatures from Dungeons & Dragons; free fan content is permitted under
# the policy as long as it says so. The pixel font has no copyright sign,
# so it is written "(c)".
FAN_CONTENT_NOTICE = (
    "CHUCK is unofficial Fan Content permitted under the Fan Content Policy.",
    "Not approved/endorsed by Wizards. Portions of the materials used are",
    "property of Wizards of the Coast. (c)Wizards of the Coast LLC.",
)
TITLE_MUSIC = "title.wav"

# The smoking cycle, in seconds: resting (varied, so it never becomes a
# metronome), the lift, the drag, and the lowering.
REST_TIMES = (3.2, 4.6, 2.7, 5.1)
RAISE_TIME = 0.55
DRAG_TIME = 1.25
LOWER_TIME = 0.6
BLINK_EVERY = 3.7
BLINK_TIME = 0.14
TAIL_STEP = 0.42


def chuck_pose(t: float) -> tuple[float, str]:
    """How far the cigarette is raised (0..1), and which part of the cycle.

    Returns ``(raise, phase)`` where phase is one of ``rest``, ``raise``,
    ``drag`` and ``lower``.
    """
    cycle = [(rest, RAISE_TIME, DRAG_TIME, LOWER_TIME) for rest in REST_TIMES]
    total = sum(sum(parts) for parts in cycle)
    t %= total
    for rest, lift, drag, lower in cycle:
        if t < rest:
            return 0.0, "rest"
        t -= rest
        if t < lift:
            return t / lift, "raise"
        t -= lift
        if t < drag:
            return 1.0, "drag"
        t -= drag
        if t < lower:
            return 1.0 - t / lower, "lower"
        t -= lower
    return 0.0, "rest"


def is_blinking(t: float) -> bool:
    return (t % BLINK_EVERY) > BLINK_EVERY - BLINK_TIME


class _Smoke:
    """Pixel smoke: squares that rise, drift, grow and thin out."""

    __slots__ = ("x", "y", "vx", "vy", "age", "life", "grow", "wobble",
                 "alpha")

    def __init__(self, x, y, vx, vy, life, grow, wobble, alpha) -> None:
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.age = 0.0
        self.life = life
        self.grow = grow
        self.wobble = wobble
        self.alpha = alpha


class TitleScene(Scene):
    """Title menu over Chuck's portrait: two real options, one dev option."""

    canvas_size = (config.NATIVE_WIDTH * 2, config.NATIVE_HEIGHT * 2)

    def __init__(self, game) -> None:
        super().__init__(game)
        self._font = game.assets.bitmap_font()
        self._selected = 0
        self._continue_available = game.checkpoints.can_continue
        self._time = 0.0
        self._canvas = None
        self._smoke: list[_Smoke] = []
        self._wisp_timer = 0.0
        self._last_phase = "rest"
        self._random = random.Random(1994)

        meta_path = config.SPRITES_DIR / TITLE_DIR / "title.json"
        self._meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self._chuck_origin = tuple(self._meta["chuck_origin"])
        self._logo_origin = tuple(self._meta["logo"]["origin"])
        self._arms = self._meta["arm_frames"]
        self._images_loaded = False

    # ------------------------------------------------------------------
    @property
    def options(self) -> tuple[str, ...]:
        options = ["NEW GAME", "CONTINUE", "CONTROLS"]
        if config.ENABLE_DEV_CHECKPOINT_SELECTOR:
            options.append("DEV CHECKPOINTS")
        return tuple(options)

    @property
    def continue_available(self) -> bool:
        return self._continue_available

    def on_enter(self) -> None:
        # Very quiet space ambience under the portrait; the trim in
        # config keeps it well below every area theme.
        self.game.audio.play_music(TITLE_MUSIC)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        self._time += dt
        self._update_smoke(dt)
        if self.game.input.was_pressed("move_up"):
            self._move(-1)
        elif self.game.input.was_pressed("move_down"):
            self._move(1)
        elif self.game.input.was_pressed("interact"):
            self._choose()

    def _enabled(self, index: int) -> bool:
        return index != 1 or self._continue_available

    def _move(self, direction: int) -> None:
        count = len(self.options)
        for _ in range(count):
            self._selected = (self._selected + direction) % count
            if self._enabled(self._selected):
                self.game.audio.play_sfx("interact")
                return

    def _choose(self) -> None:
        if not self._enabled(self._selected):
            return
        self.game.audio.play_sfx("interact")
        choice = self.options[self._selected]
        if choice == "NEW GAME":
            # A new game opens on Chuck waking up beside Bobert; the
            # cutscene starts the game itself when it fades out.
            from src.scenes.opening_cutscene_scene import OpeningCutsceneScene
            self.game.scenes.replace(OpeningCutsceneScene(self.game))
        elif choice == "CONTINUE":
            self.game.checkpoints.continue_game()
        elif choice == "CONTROLS":
            # The pause menu's own controls page, opened on its own.
            from src.scenes.pause_scene import PauseScene
            self.game.scenes.push(
                PauseScene(self.game, page="controls", standalone=True))
        else:
            from src.scenes.checkpoint_select_scene import CheckpointSelectScene
            self.game.scenes.replace(CheckpointSelectScene(self.game))

    # ------------------------------------------------------------------
    # Chuck
    # ------------------------------------------------------------------
    def _arm_frame(self, amount: float) -> int:
        return min(len(self._arms) - 1, round(amount * (len(self._arms) - 1)))

    def ember_position(self) -> tuple[float, float]:
        amount, _phase = chuck_pose(self._time)
        ex, ey = self._arms[self._arm_frame(amount)]["ember"]
        return self._chuck_origin[0] + ex, self._chuck_origin[1] + ey

    def mouth_position(self) -> tuple[float, float]:
        mx, my = self._arms[0]["mouth"]
        return self._chuck_origin[0] + mx, self._chuck_origin[1] + my

    def _update_smoke(self, dt: float) -> None:
        amount, phase = chuck_pose(self._time)
        rng = self._random

        # A thread off the ember, always -- thinner during the drag,
        # when the smoke is going into Chuck rather than off the end.
        self._wisp_timer -= dt
        while self._wisp_timer <= 0.0:
            self._wisp_timer += 0.1 if phase == "drag" else 0.045
            ex, ey = self.ember_position()
            self._smoke.append(_Smoke(
                # Leaning away from his face as it rises: straight up,
                # the thread went through his whiskers.
                ex - 1, ey - 2, rng.uniform(-7.0, -3.0),
                rng.uniform(-17.0, -13.0), rng.uniform(2.6, 3.4),
                rng.uniform(0.9, 1.5), rng.uniform(0, math.tau), 190))

        # The exhale: once per cycle, the moment the arm starts down.
        if phase == "lower" and self._last_phase != "lower":
            mx, my = self.mouth_position()
            for index in range(26):
                self._smoke.append(_Smoke(
                    mx - 3 - index * 0.5, my + rng.uniform(-3, 2),
                    rng.uniform(-30.0, -10.0), rng.uniform(-14.0, -3.0),
                    rng.uniform(1.8, 2.8), rng.uniform(2.0, 3.2),
                    rng.uniform(0, math.tau), 210))
        self._last_phase = phase

        alive = []
        for puff in self._smoke:
            puff.age += dt
            if puff.age >= puff.life:
                continue
            puff.vx *= 0.985
            puff.vy *= 0.992
            puff.x += (puff.vx + math.sin(puff.age * 2.6 + puff.wobble) * 4.0) * dt
            puff.y += puff.vy * dt
            alive.append(puff)
        self._smoke = alive

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if self._images_loaded:
            return
        image = self.game.assets.image
        self._background = image(f"{TITLE_DIR}/background.png")
        self._logo = image(f"{TITLE_DIR}/logo.png")
        self._body = image(f"{TITLE_DIR}/chuck_body.png")
        self._body_blink = image(f"{TITLE_DIR}/chuck_body_blink.png")
        self._tails = [image(f"{TITLE_DIR}/chuck_tail_{index}.png")
                       for index in range(self._meta["tail_frames"])]
        self._arm_images = [image(f"{TITLE_DIR}/chuck_arm_{index}.png")
                            for index in range(len(self._arms))]
        self._images_loaded = True

    def draw(self, surface: pygame.Surface) -> None:
        self._load()
        if surface.get_size() == self.canvas_size:
            self._draw_canvas(surface)
            return
        if self._canvas is None:
            self._canvas = pygame.Surface(self.canvas_size)
        self._draw_canvas(self._canvas)
        pygame.transform.scale(self._canvas, surface.get_size(), surface)

    def _draw_canvas(self, canvas: pygame.Surface) -> None:
        t = self._time
        canvas.blit(self._background, (0, 0))
        self._draw_twinkles(canvas, t)
        canvas.blit(self._logo, self._logo_origin)

        amount, phase = chuck_pose(t)
        tail_count = len(self._tails)
        step = int(t / TAIL_STEP)
        cycle = step % (tail_count * 2 - 2) if tail_count > 1 else 0
        tail = cycle if cycle < tail_count else tail_count * 2 - 2 - cycle
        canvas.blit(self._tails[tail], self._chuck_origin)
        body = self._body_blink if is_blinking(t) else self._body
        canvas.blit(body, self._chuck_origin)
        canvas.blit(self._arm_images[self._arm_frame(amount)],
                    self._chuck_origin)
        self._draw_ember(canvas, t, phase)
        self._draw_smoke(canvas)
        self._draw_menu(canvas)

    def _draw_twinkles(self, canvas: pygame.Surface, t: float) -> None:
        for x, y, arm, phase in self._meta["sparkles"]:
            level = 0.5 + 0.5 * math.sin(t * 1.7 + phase)
            if level < 0.55:
                # Dim: cover the baked sparkle's arms so it shrinks to
                # its core, which is what a twinkle is.
                for step in range(2, arm + 1):
                    for sx, sy in ((step, 0), (-step, 0), (0, step),
                                   (0, -step)):
                        px, py = x + sx, y + sy
                        if 0 <= px < canvas.get_width() \
                                and 0 <= py < canvas.get_height():
                            canvas.set_at((px, py),
                                          self._background.get_at(
                                              (px + (4 if sx else 0),
                                               py + (4 if sy else 0))))
            elif level > 0.92:
                for sx, sy in ((arm + 1, 0), (-arm - 1, 0), (0, arm + 1),
                               (0, -arm - 1)):
                    px, py = x + sx, y + sy
                    if 0 <= px < canvas.get_width() \
                            and 0 <= py < canvas.get_height():
                        canvas.set_at((px, py), (150, 170, 240))

    def _draw_ember(self, canvas: pygame.Surface, t: float, phase: str) -> None:
        ex, ey = self.ember_position()
        x, y = round(ex), round(ey)
        if phase == "drag":
            heat = 1.0
        else:
            heat = 0.45 + 0.2 * math.sin(t * 9.0) * math.sin(t * 3.1)
        glow = pygame.Surface((9, 9), pygame.SRCALPHA)
        strength = round(90 * heat)
        pygame.draw.rect(glow, (strength, round(strength * 0.45), 0), (2, 2, 5, 5))
        pygame.draw.rect(glow, (strength, round(strength * 0.6), 10), (3, 3, 3, 3))
        canvas.blit(glow, (x - 4, y - 3), special_flags=pygame.BLEND_ADD)
        core = (255, round(150 + 90 * heat), round(60 + 100 * heat))
        canvas.set_at((x, y), core)
        canvas.set_at((x, y + 1), (255, round(110 + 60 * heat), 40))

    def _draw_smoke(self, canvas: pygame.Surface) -> None:
        """Each puff a square with a thinner square round it.

        Drawn as bare one-pixel specks the smoke disappeared entirely
        into the nebula's star dust, which is the same colour and the
        same size. It needs body: a core, a soft edge, and enough of
        them close together to read as one ribbon.
        """
        for puff in self._smoke:
            progress = puff.age / puff.life
            size = max(2, round(2 + puff.grow * progress * 2.4))
            alpha = round(puff.alpha * (1.0 - progress) ** 1.3)
            if alpha <= 4:
                continue
            shade = round(214 + 24 * progress)
            colour = (shade, shade, min(255, shade + 10))
            x, y = round(puff.x), round(puff.y)
            halo = pygame.Surface((size + 2, size + 2), pygame.SRCALPHA)
            halo.fill(colour + (alpha // 3,))
            canvas.blit(halo, (x - 1, y - 1))
            core = pygame.Surface((size, size), pygame.SRCALPHA)
            core.fill(colour + (alpha,))
            canvas.blit(core, (x, y))

    def _draw_menu(self, canvas: pygame.Surface) -> None:
        scale = 2
        top = 216
        left = 262
        for index, label in enumerate(self.options):
            caret = ">" if index == self._selected else " "
            rendered = self._font.render(f"{caret} {label}")
            rendered = pygame.transform.scale(
                rendered, (rendered.get_width() * scale,
                           rendered.get_height() * scale))
            if not self._enabled(index):
                rendered.set_alpha(70)
            elif index != self._selected:
                rendered.set_alpha(215)
            canvas.blit(rendered, (left, top + index * 24))

        from src.ui import prompts

        prompt = self._font.render(prompts.title_prompt(self.game.input))
        prompt = pygame.transform.scale(
            prompt, (prompt.get_width() * scale, prompt.get_height() * scale))
        prompt.set_alpha(165)
        canvas.blit(prompt, ((canvas.get_width() - prompt.get_width()) // 2,
                             308))

        # The fan content notice, small along the bottom edge, on a
        # dark band so it reads against the nebula.
        band = pygame.Surface((canvas.get_width(), 27), pygame.SRCALPHA)
        band.fill((6, 6, 16, 170))
        canvas.blit(band, (0, canvas.get_height() - band.get_height()))
        for index, line in enumerate(FAN_CONTENT_NOTICE):
            notice = self._font.render(line)
            notice.set_alpha(205)
            canvas.blit(notice,
                        ((canvas.get_width() - notice.get_width()) // 2,
                         334 + index * 8))
