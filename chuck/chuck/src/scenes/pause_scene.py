"""The pause menu, and the controls and volume pages it opens.

Esc during play (or during a cutscene) pushes this over the frozen scene
beneath it. The scene manager only updates the top scene, so nothing
under the menu moves while it is open, and the music is paused with it.

    RESUME
    CONTROLS         the keys, on their own page
    VOLUME           music and sound, as two sliders
    FULLSCREEN: ON/OFF   (F11 does the same thing anywhere)
    QUIT TO TITLE    asks first -- anything since the last Ashtray is lost

The title screen opens the controls page on its own through the same
scene (`PauseScene(game, page="controls", standalone=True)`), so there is
one list of controls in the game rather than two that drift apart.
"""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene
from src.systems.settings import LEVELS

# What the controls page says. One row per action, in the order a player
# needs them.
CONTROLS = (
    ("MOVE", "WASD / ARROW KEYS"),
    ("TALK / EXAMINE", "E / ENTER"),
    ("JUMP", "SPACE"),
    ("SCRATCH", "F"),
    ("PAUSE", "ESC"),
    ("FULLSCREEN", "F11"),
)
CONTROLS_NOTE = "Ashtrays save your progress."

MAIN = ("RESUME", "CONTROLS", "VOLUME", "FULLSCREEN", "QUIT TO TITLE")
VOLUME = ("MUSIC", "SOUND", "BACK")
CONFIRM = ("NO", "YES")

PANEL = (24, 22, 30)
BORDER = (120, 116, 130)
DIM = 150
TITLE_TINT = (246, 214, 140)
BAR = (70, 66, 80)
BAR_FILL = (232, 196, 120)


class PauseScene(Scene):
    """A menu over whatever was running. See the module docstring."""

    def __init__(self, game, *, page: str = "main",
                 standalone: bool = False) -> None:
        super().__init__(game)
        self.page = page
        # Opened for one page from somewhere that is not a game in
        # progress (the title's CONTROLS): leaving that page closes it.
        self.standalone = standalone
        self.selected = 0
        self._font = game.assets.bitmap_font()
        self._music_paused = False

    @property
    def canvas_size(self):
        """Whatever the scene underneath draws at, so it is not blurred.

        The title draws on a canvas twice the game's size; opened over
        it, the menu asks for the same canvas rather than squeezing the
        title down to the game's native size while it is up.
        """
        stack = self.game.scenes._stack
        if self in stack and stack.index(self) > 0:
            return getattr(stack[stack.index(self) - 1], "canvas_size", None)
        return None

    # ------------------------------------------------------------------
    def on_enter(self) -> None:
        self.game.audio.play_sfx("interact")
        if not self.standalone and self.game.audio.enabled:
            pygame.mixer.music.pause()
            self._music_paused = True

    def on_exit(self) -> None:
        if self._music_paused and self.game.audio.enabled:
            pygame.mixer.music.unpause()
        self._music_paused = False

    @property
    def options(self) -> tuple[str, ...]:
        if self.page == "main":
            return MAIN
        if self.page == "volume":
            return VOLUME
        if self.page == "confirm":
            return CONFIRM
        return ()

    def label(self, option: str) -> str:
        if option == "FULLSCREEN":
            return ("FULLSCREEN: ON" if self.game.settings.fullscreen
                    else "FULLSCREEN: OFF")
        return option

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def back(self) -> None:
        """Esc: one page up, or close the menu from the top page."""
        self.game.audio.play_sfx("interact")
        if self.page == "main" or self.standalone:
            self.close()
        else:
            self._goto("main", MAIN.index(
                {"controls": "CONTROLS", "volume": "VOLUME",
                 "confirm": "QUIT TO TITLE"}.get(self.page, "RESUME")))

    def close(self) -> None:
        if self.game.scenes.current is self:
            self.game.scenes.pop()

    def _goto(self, page: str, selected: int = 0) -> None:
        self.page = page
        self.selected = selected

    def update(self, dt: float) -> None:
        del dt
        pressed = self.game.input.was_pressed
        if self.page == "controls":
            if pressed("interact"):
                self.back()
            return
        options = self.options
        if pressed("move_up"):
            self.selected = (self.selected - 1) % len(options)
            self.game.audio.play_sfx("interact")
        elif pressed("move_down"):
            self.selected = (self.selected + 1) % len(options)
            self.game.audio.play_sfx("interact")
        elif self.page == "volume" and (pressed("move_left")
                                        or pressed("move_right")):
            self._nudge(1 if pressed("move_right") else -1)
        elif pressed("interact"):
            self.choose(options[self.selected])

    def choose(self, option: str) -> None:
        self.game.audio.play_sfx("interact")
        if self.page == "main":
            if option == "RESUME":
                self.close()
            elif option == "CONTROLS":
                self._goto("controls")
            elif option == "VOLUME":
                self._goto("volume")
            elif option == "FULLSCREEN":
                self.game.set_fullscreen(not self.game.settings.fullscreen)
            elif option == "QUIT TO TITLE":
                self._goto("confirm")
        elif self.page == "volume":
            if option == "BACK":
                self.back()
            else:
                # E on a slider steps it up, wrapping to silent at the top.
                self._nudge(1, wrap=True)
        elif self.page == "confirm":
            if option == "YES":
                self.quit_to_title()
            else:
                self.back()

    def _nudge(self, step: int, wrap: bool = False) -> None:
        option = VOLUME[self.selected]
        if option not in ("MUSIC", "SOUND"):
            return
        settings = self.game.settings
        current = settings.music if option == "MUSIC" else settings.sound
        value = current + step
        if wrap and value > LEVELS:
            value = 0
        value = max(0, min(LEVELS, value))
        if option == "MUSIC":
            self.game.set_volume(music=value)
        else:
            self.game.set_volume(sound=value)
            # So the player hears the level they just picked.
            self.game.audio.play_sfx("interact")

    def quit_to_title(self) -> None:
        from src.scenes.title_scene import TitleScene

        self._music_paused = False
        self.game.audio.stop_music()
        scenes = self.game.scenes
        while scenes.current is not None:
            scenes.pop()
        scenes.push(TitleScene(self.game))

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        veil = pygame.Surface(surface.get_size())
        veil.set_alpha(DIM)
        surface.blit(veil, (0, 0))
        # Drawn at the game's native size and scaled up by the canvas
        # it lands on, so it looks the same over the title's big canvas
        # as it does over play.
        canvas = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT),
                                pygame.SRCALPHA)
        getattr(self, f"_draw_{self.page}")(canvas)
        if canvas.get_size() != surface.get_size():
            canvas = pygame.transform.scale(canvas, surface.get_size())
        surface.blit(canvas, (0, 0))

    def _text(self, text: str, tint=None, alpha: int = 255):
        image = self._font.render(text)
        if tint is not None:
            image = image.copy()
            image.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        image.set_alpha(alpha)
        return image

    def _panel(self, canvas, width: int, height: int, title: str):
        rect = pygame.Rect((config.NATIVE_WIDTH - width) // 2,
                           (config.NATIVE_HEIGHT - height) // 2,
                           width, height)
        pygame.draw.rect(canvas, PANEL, rect)
        pygame.draw.rect(canvas, BORDER, rect, 1)
        heading = self._text(title, TITLE_TINT)
        canvas.blit(heading, (rect.centerx - heading.get_width() // 2,
                              rect.y + 8))
        return rect

    def _menu(self, canvas, rect, labels, top: int) -> None:
        line = self._font.get_height() + 4
        for index, label in enumerate(labels):
            caret = ">" if index == self.selected else " "
            text = self._text(f"{caret} {label}",
                              alpha=255 if index == self.selected else 190)
            canvas.blit(text, (rect.x + 16, top + index * line))

    def _footer(self, canvas, rect, text: str) -> None:
        hint = self._text(text, alpha=150)
        canvas.blit(hint, (rect.centerx - hint.get_width() // 2,
                           rect.bottom - hint.get_height() - 6))

    def _draw_main(self, canvas) -> None:
        rect = self._panel(canvas, 150, 104, "PAUSED")
        self._menu(canvas, rect, [self.label(o) for o in MAIN], rect.y + 26)

    def _draw_controls(self, canvas) -> None:
        rect = self._panel(canvas, 230, 146, "CONTROLS")
        line = self._font.get_height() + 5
        for index, (action, keys) in enumerate(CONTROLS):
            y = rect.y + 26 + index * line
            canvas.blit(self._text(action, alpha=200), (rect.x + 14, y))
            key_text = self._text(keys, TITLE_TINT)
            canvas.blit(key_text, (rect.right - 14 - key_text.get_width(), y))
        note = self._text(CONTROLS_NOTE, alpha=190)
        canvas.blit(note, (rect.centerx - note.get_width() // 2,
                           rect.y + 26 + len(CONTROLS) * line + 3))
        self._footer(canvas, rect, "E / ESC: BACK")

    def _draw_volume(self, canvas) -> None:
        rect = self._panel(canvas, 190, 96, "VOLUME")
        line = self._font.get_height() + 8
        levels = (self.game.settings.music, self.game.settings.sound)
        for index, option in enumerate(VOLUME):
            y = rect.y + 28 + index * line
            caret = ">" if index == self.selected else " "
            text = self._text(f"{caret} {option}",
                              alpha=255 if index == self.selected else 190)
            canvas.blit(text, (rect.x + 12, y))
            if index < 2:
                self._slider(canvas, rect.x + 76, y + 2, levels[index],
                             index == self.selected)
        self._footer(canvas, rect, "LEFT / RIGHT: ADJUST")

    def _slider(self, canvas, x: int, y: int, level: int,
                selected: bool) -> None:
        cell_w, gap, height = 8, 1, 5
        for step in range(LEVELS):
            colour = BAR_FILL if step < level else BAR
            cell = pygame.Rect(x + step * (cell_w + gap), y, cell_w, height)
            pygame.draw.rect(canvas, colour, cell)
        if selected:
            outline = pygame.Rect(x - 2, y - 2,
                                  LEVELS * (cell_w + gap) - gap + 4,
                                  height + 4)
            pygame.draw.rect(canvas, BORDER, outline, 1)

    def _draw_confirm(self, canvas) -> None:
        rect = self._panel(canvas, 236, 84, "QUIT TO TITLE?")
        for index, line in enumerate(("Anything since your last Ashtray",
                                      "will be lost.")):
            text = self._text(line, alpha=200)
            canvas.blit(text, (rect.centerx - text.get_width() // 2,
                               rect.y + 24 + index * 11))
        line_h = self._font.get_height() + 4
        for index, option in enumerate(CONFIRM):
            caret = ">" if index == self.selected else " "
            text = self._text(f"{caret} {option}",
                              alpha=255 if index == self.selected else 190)
            canvas.blit(text, (rect.x + 90, rect.y + 50 + index * line_h))
