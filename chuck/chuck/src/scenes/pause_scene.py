"""The pause menu, and the controls and volume pages it opens.

Esc during play (or during a cutscene) pushes this over the frozen scene
beneath it. The scene manager only updates the top scene, so nothing
under the menu moves while it is open, and the music is paused with it.

    RESUME
    CONTROLS         the keys, on their own page
    VOLUME           music and sound, as two sliders
    SAVE GAME        writes the slot, and shows the code for it
    FULLSCREEN: ON/OFF   (F11 does the same thing anywhere)
    QUIT TO TITLE    asks first -- anything unsaved is lost

The title screen opens two of these pages on their own through the same
scene -- controls (`page="controls"`) and the code field
(`page="load"`), both `standalone=True` -- so there is one list of
controls and one code field in the game rather than two of each that
drift apart.

The two code pages are the whole of the save UI:

    save    the code for the game as it stands, with COPY
    load    a field to type or paste one into, and nothing else on the
            page -- see the note on `update` about why it has no menu
"""

from __future__ import annotations

import asyncio
import pygame
import sys

from src.core import config
from src.scenes.scene import Scene
from src.core.runtime import touch_host
from src.systems import clipboard, save_code
from src.systems.checkpoints import is_save_point
from src.systems.settings import LEVELS
from src.ui import prompts
from src.ui.code_entry import CodeEntry

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


# The line under the controls. It used to name the Ashtrays; with those
# gone it names what replaced them, which is the thing a player who has
# opened this page is most likely looking for.
CONTROLS_NOTE = "SAVE GAME gives you a code."


def controls_rows(input_manager) -> tuple[tuple[str, str], ...]:
    """The controls page for whatever the player last used."""
    if input_manager is None or not input_manager.using_controller:
        if touch_host():
            # No FULLSCREEN row: the browser owns that, and on a phone
            # it is the home screen rather than a key. See the shell.
            label = prompts.label
            return (
                ("MOVE", prompts.TOUCH_MOVE),
                ("TALK / EXAMINE", label(input_manager, "interact")),
                ("JUMP", label(input_manager, "jump")),
                ("SCRATCH", label(input_manager, "scratch")),
                ("PAUSE", label(input_manager, "pause")),
            )
        return CONTROLS[:-1] if sys.platform == "emscripten" else CONTROLS
    label = prompts.label
    rows = (
        ("MOVE", prompts.PAD_MOVE),
        ("TALK / EXAMINE", label(input_manager, "interact")),
        ("JUMP", label(input_manager, "jump")),
        ("SCRATCH", label(input_manager, "scratch")),
        ("PAUSE", label(input_manager, "pause")),
        ("FULLSCREEN", "F11 (KEYBOARD)"),
    )
    return rows[:-1] if sys.platform == "emscripten" else rows

MAIN = ("RESUME", "CONTROLS", "VOLUME", "SAVE GAME", "FULLSCREEN",
        "QUIT TO TITLE")


def main_options() -> tuple[str, ...]:
    """SDL owns desktop fullscreen; browser chrome owns web fullscreen."""
    if sys.platform == "emscripten":
        return tuple(option for option in MAIN if option != "FULLSCREEN")
    return MAIN

VOLUME = ("MUSIC", "SOUND", "BACK")
CONFIRM = ("NO", "YES")
# With a code on screen there is something to do besides answer. The
# page exists to put it in the player's hands, and a hand-typed code is
# a poor substitute for a copied one -- especially on a phone, where
# there is nothing to write on.
CONFIRM_WITH_CODE = ("COPY", "NO", "YES")
SAVED = ("COPY", "BACK")
NOT_HERE = ("BACK",)

# Why a save can be refused. Only reachable by pausing somewhere that
# is not a room -- mid-cutscene, mid-fall -- because ordinary play
# always stands on the door it came in by.
NO_SAVE_HERE = ("There is nowhere to save from here.",
                "Walk into a room and try again.")

# Leaving from somewhere that cannot be written down -- mid-cutscene,
# mid-fall. There is no code to hand over, so say so plainly.
QUIT_WITHOUT_A_CODE = ("No code from here.",
                       "Everything since your last is lost.")

# The quit warning's panel, sized to what it has to hold: the code, a
# line about what is lost, the options a font-line apart, and a line of
# feedback under them. The numbers live here rather than inline so the
# test that checks they still fit reads the same ones the drawing uses
# -- add a fourth option without growing the height and it will say so.
CONFIRM_HEIGHT = 128
CONFIRM_MENU_TOP = 72
CONFIRM_HEIGHT_NO_CODE = 106
CONFIRM_MENU_TOP_NO_CODE = 74
FOOTER_MARGIN = 6

PANEL = (24, 22, 30)
BORDER = (120, 116, 130)
DIM = 150
TITLE_TINT = (246, 214, 140)
BAR = (70, 66, 80)
BAR_FILL = (232, 196, 120)
WRONG_TINT = (230, 120, 110)


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
        # The save page: the code for this game, and a word about where
        # it went. The load page: the field. Built when the page opens.
        self._code: str | None = None
        self._note = ""
        self._entry: CodeEntry | None = None
        self._copy_task = None

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
        clipboard.enable_browser_paste(self.page == "load")
        self.game.audio.play_sfx("interact")
        if not self.standalone and self.game.audio.enabled:
            pygame.mixer.music.pause()
            self._music_paused = True

    def on_exit(self) -> None:
        clipboard.enable_browser_paste(False)
        if self._music_paused and self.game.audio.enabled:
            pygame.mixer.music.unpause()
        self._music_paused = False

    @property
    def options(self) -> tuple[str, ...]:
        if self.page == "main":
            return main_options()
        if self.page == "volume":
            return VOLUME
        if self.page == "confirm":
            return CONFIRM_WITH_CODE if self._code else CONFIRM
        if self.page == "save":
            return SAVED if self._code else NOT_HERE
        # The load page has no option list at all; see `update`.
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
            return
        if self.page == "load":
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN, pygame.K_KP_ENTER):
                self._try_code()
                return
            # Everything else is a character. E is a letter here, not
            # the interact key.
            self._field().handle_event(event)

    def back(self) -> None:
        """Esc: one page up, or close the menu from the top page."""
        self.game.audio.play_sfx("interact")
        if self.page == "main" or self.standalone:
            self.close()
        else:
            self._goto("main", main_options().index(
                {"controls": "CONTROLS", "volume": "VOLUME",
                 "save": "SAVE GAME",
                 "confirm": "QUIT TO TITLE"}.get(self.page, "RESUME")))

    def close(self) -> None:
        if self.game.scenes.current is self:
            self.game.scenes.pop()

    def _goto(self, page: str, selected: int = 0) -> None:
        self.page = page
        clipboard.enable_browser_paste(page == "load")
        self.selected = selected

    def update(self, dt: float) -> None:
        pressed = self.game.input.was_pressed
        if pressed("back"):
            # A controller's back button (Esc arrives through handle_event).
            self.back()
            return
        if self.page == "controls":
            if pressed("interact"):
                self.back()
            return
        if self.page == "load":
            self._update_load(pressed, dt)
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
            elif option == "SAVE GAME":
                self._save_now()
            elif option == "FULLSCREEN":
                self.game.set_fullscreen(not self.game.settings.fullscreen)
            elif option == "QUIT TO TITLE":
                self._code = self._code_here()
                # A "Copied" from the save page belongs to the save
                # page; this one starts with nothing to report.
                self._note = ""
                self._goto("confirm")
        elif self.page == "volume":
            if option == "BACK":
                self.back()
            else:
                # E on a slider steps it up, wrapping to silent at the top.
                self._nudge(1, wrap=True)
        elif self.page == "confirm":
            if option == "COPY":
                self._copy_now()
            elif option == "YES":
                self.quit_to_title()
            else:
                self.back()
        elif self.page == "save":
            if option == "COPY":
                self._copy_now()
            else:
                self.back()

    def _copy_now(self) -> None:
        """Hand the shown code to the clipboard, and say what happened.

        Both pages that show a code can do this, and they do it the same
        way: saving offers it because a code is the save, and quitting
        offers it because a code is the only thing that survives
        leaving. One implementation, so the second cannot quietly drift
        into behaving differently from the first.

        The browser settles its clipboard promise in JavaScript, so
        there the copy is a task and the note arrives later; a second
        press while one is in flight is ignored rather than queued.
        """
        if sys.platform == "emscripten":
            if self._copy_task is not None and not self._copy_task.done():
                return
            self._note = ""
            self._copy_task = asyncio.create_task(self._copy_code())
        else:
            self._note = (
                "Copied" if clipboard.copy(self._code or "")
                else "No clipboard here. Write it down."
            )

    async def _copy_code(self) -> None:
        copied = await clipboard.copy_browser(self._code or "")
        self._note = (
            "Copied" if copied else "Clipboard blocked. Write it down."
        )

    # ------------------------------------------------------------------
    # Saving, and the code that comes of it
    # ------------------------------------------------------------------
    def _code_here(self) -> str | None:
        """The code for the game as it stands, or None if not somewhere.

        Read-only: it writes nothing. The quit warning uses it to show a
        player what they are about to walk away from.
        """
        checkpoint_id = self.game.active_checkpoint_id
        if not is_save_point(checkpoint_id):
            return None
        record = self.game.checkpoints.current_record(
            checkpoint_id, self._sanity())
        return save_code.for_display(record)

    def _save_now(self) -> None:
        """Bank the save point, show the code, and say what it means.

        There is nothing else: the code is the save. Nothing is written
        to this machine, so a player who does not keep it has not saved.
        """
        self._code, self._note = None, ""
        checkpoint_id = self.game.active_checkpoint_id
        if not is_save_point(checkpoint_id):
            self._goto("save")
            return
        record = self.game.checkpoints.save_here(
            checkpoint_id, self._sanity())
        self._code = save_code.for_display(record)
        self._note = "This code is the save. Nothing is kept for you."
        self._goto("save")

    def _sanity(self) -> int:
        """Chuck's sanity in the scene underneath, or a starting figure.

        A code does not carry sanity at all; the slot on disk does, and
        it is the scene below that knows the number.
        """
        stack = self.game.scenes._stack
        below = stack[:stack.index(self)] if self in stack else []
        for scene in reversed(below):
            sanity = getattr(scene, "sanity", None)
            if sanity is not None:
                return sanity.current
        return config.SANITY_START

    # ------------------------------------------------------------------
    # Loading a code
    # ------------------------------------------------------------------
    def _field(self) -> CodeEntry:
        if self._entry is None:
            self._entry = CodeEntry()
        return self._entry

    def _update_load(self, pressed, dt: float) -> None:
        """The one page with no menu on it.

        A list of options would need somewhere to put the focus, and
        every key that moved it is a key the player might be trying to
        type. So the field is the page: keys go into it, Enter loads,
        and Esc leaves. A controller has no keys to conflict with, so
        there the stick dials a character and the interact button loads.
        """
        field = self._field()
        pasted = clipboard.take_browser_paste()
        if pasted is not None and not field.set_text(pasted):
            field.error = "That is not a save code."
        field.update(dt)
        if not self.game.input.using_controller:
            return
        if pressed("interact"):
            self._try_code()
        else:
            field.handle_pad(self.game.input)

    def _try_code(self) -> None:
        """Read the field, and load it if it names a game we have.

        Everything is checked before anything is torn down: a code for a
        door this build does not have is refused on the menu, not
        halfway into a load.
        """
        field = self._field()
        record = field.decode()
        if record is None:
            self.game.audio.play_sfx("interact")
            return
        checkpoints = self.game.checkpoints
        if not checkpoints.can_resume(record):
            field.error = "That code is not one this game knows."
            self.game.audio.play_sfx("interact")
            return
        self.game.audio.play_sfx("interact")
        self.close()
        checkpoints.resume_from(record)

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
                           rect.bottom - hint.get_height() - FOOTER_MARGIN))

    def _draw_main(self, canvas) -> None:
        rect = self._panel(canvas, 150, 117, "PAUSED")
        self._menu(canvas, rect, [self.label(o) for o in self.options], rect.y + 26)

    def _draw_controls(self, canvas) -> None:
        rect = self._panel(canvas, 230, 146, "CONTROLS")
        line = self._font.get_height() + 5
        rows = controls_rows(self.game.input)
        for index, (action, keys) in enumerate(rows):
            y = rect.y + 26 + index * line
            canvas.blit(self._text(action, alpha=200), (rect.x + 14, y))
            key_text = self._text(keys, TITLE_TINT)
            canvas.blit(key_text, (rect.right - 14 - key_text.get_width(), y))
        note = self._text(CONTROLS_NOTE, alpha=190)
        canvas.blit(note, (rect.centerx - note.get_width() // 2,
                           rect.y + 26 + len(rows) * line + 3))
        self._footer(canvas, rect, prompts.back_footer(self.game.input))

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

    def _draw_save(self, canvas) -> None:
        rect = self._panel(canvas, 250, 108, "SAVE GAME")
        if not self._code:
            for index, line in enumerate(NO_SAVE_HERE):
                text = self._text(line, alpha=200)
                canvas.blit(text, (rect.centerx - text.get_width() // 2,
                                   rect.y + 26 + index * 11))
        else:
            label = self._text("Write this down, or copy it:", alpha=180)
            canvas.blit(label, (rect.centerx - label.get_width() // 2,
                                rect.y + 24))
            # The one thing on screen the player has to transcribe, so
            # it is drawn at twice the size of everything round it.
            code = self._big(self._code, TITLE_TINT)
            canvas.blit(code, (rect.centerx - code.get_width() // 2,
                               rect.y + 38))
        self._menu(canvas, rect, self.options, rect.y + 62)
        self._footer(canvas, rect, self._note or prompts.back_footer(
            self.game.input))

    def _draw_load(self, canvas) -> None:
        rect = self._panel(canvas, 250, 100, "LOAD CODE")
        field = self._field()
        label = self._text("Enter your save code:", alpha=180)
        canvas.blit(label, (rect.centerx - label.get_width() // 2,
                            rect.y + 24))
        strip = pygame.Surface((field.width(), field.height(self._font)),
                               pygame.SRCALPHA)
        field.draw(strip, self._font, 0, 0, tint=TITLE_TINT)
        strip = pygame.transform.scale(
            strip, (strip.get_width() * 2, strip.get_height() * 2))
        canvas.blit(strip, (rect.centerx - strip.get_width() // 2,
                            rect.y + 40))
        if field.error:
            wrong = self._text(field.error, WRONG_TINT)
            canvas.blit(wrong, (rect.centerx - wrong.get_width() // 2,
                                rect.y + 66))
        self._footer(canvas, rect, self._load_footer())

    def _load_footer(self) -> str:
        if self.game.input.using_controller:
            return (f"{prompts.PAD_MOVE}: SPELL   "
                    f"{prompts.label(self.game.input, 'interact')}: LOAD")
        if touch_host():
            # The shell puts a field and a LOAD button at the top of the
            # screen; the pad dials for anyone who closes it.
            return "TYPE ABOVE, OR DIAL WITH THE PAD."
        return "CTRL-V PASTES.  ENTER LOADS.  ESC: BACK."

    def _big(self, text: str, tint=None):
        image = self._text(text, tint)
        return pygame.transform.scale(
            image, (image.get_width() * 2, image.get_height() * 2))

    def _draw_confirm(self, canvas) -> None:
        """The way out, with the code in the player's hands first.

        A code is the only thing that survives leaving, so quitting shows
        it rather than warning about it in the abstract. Nothing is
        written here; the player is being given something to copy.
        """
        # The code case carries a third option and a line of feedback,
        # and the panel has to be tall enough for both: the options are
        # a 13px line apart, so three of them no longer fit the height
        # two used to need.
        rect = self._panel(
            canvas, 250,
            CONFIRM_HEIGHT if self._code else CONFIRM_HEIGHT_NO_CODE,
            "QUIT TO TITLE?")
        if self._code:
            label = self._text("Write this down, or copy it:", alpha=190)
            canvas.blit(label, (rect.centerx - label.get_width() // 2,
                                rect.y + 22))
            code = self._big(self._code, TITLE_TINT)
            canvas.blit(code, (rect.centerx - code.get_width() // 2,
                               rect.y + 34))
            lines, top = ("Anything since here will be lost.",), 56
            menu_top = CONFIRM_MENU_TOP
        else:
            # No code to make room for, and one line more to fit.
            lines, top = QUIT_WITHOUT_A_CODE, 34
            menu_top = CONFIRM_MENU_TOP_NO_CODE
        for index, line in enumerate(lines):
            text = self._text(line, alpha=200)
            canvas.blit(text, (rect.centerx - text.get_width() // 2,
                               rect.y + top + index * 11))
        line_h = self._font.get_height() + 4
        for index, option in enumerate(self.options):
            caret = ">" if index == self.selected else " "
            text = self._text(f"{caret} {option}",
                              alpha=255 if index == self.selected else 190)
            canvas.blit(text, (rect.x + 96, rect.y + menu_top + index * line_h))
        if self._note:
            self._footer(canvas, rect, self._note)
