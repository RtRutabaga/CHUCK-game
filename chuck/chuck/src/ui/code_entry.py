"""A field for typing a save code into.

    K6PT-6EX1-BV..-....
                ^

Sixteen slots in groups of four, a caret under the one being filled,
and a dot for every slot still waiting, so the player can see how much
is left. The game had no text input at all before this -- the pause and
title menus are fixed lists of options -- so this is the whole of it,
kept in one widget that owns no scene and no game.

Three ways in, because the field has to work wherever the game is:

    keyboard   type it; backspace, arrows, Ctrl-V all behave
    paste      the usual way a code arrives, especially in a browser
    pad        up and down dial a slot through the alphabet

The pad is the slow one and it is meant to be. It is there so that a
player on a controller is not locked out of loading a game, not because
anybody should want to enter sixteen characters that way.

The field is forgiving on the way in: lower case, missing dashes, a
letter O where a zero belongs -- `save_code.normalise` settles all of
it. What it will not do is accept a character that is not in the
alphabet at all. A refused keystroke does nothing and says so by not
appearing, which is the clearest thing a text field can do.
"""

from __future__ import annotations

import pygame

from src.systems import clipboard
from src.systems.save import SaveRecord
from src.systems.save_code import (
    ALPHABET, CODE_LENGTH, GROUP, SaveCodeError, decode, normalise,
)
from src.ui.bitmap_font import ADVANCE

# An unfilled slot, and the mark between groups. Both are in the pixel
# font, and neither is in the alphabet, so nothing on screen can be read
# back as part of the code.
BLANK = "."
SEPARATOR = "-"
CARET_BLINK = 0.53


class CodeEntry:
    """Sixteen slots the player fills with a save code."""

    def __init__(self, length: int = CODE_LENGTH, group: int = GROUP) -> None:
        self.length = length
        self.group = group
        self._slots: list[str] = [""] * length
        self.cursor = 0
        self.error: str | None = None
        self._time = 0.0

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    @property
    def text(self) -> str:
        """What has been entered, holes and all."""
        return "".join(self._slots)

    @property
    def complete(self) -> bool:
        return all(self._slots)

    @property
    def empty(self) -> bool:
        return not any(self._slots)

    def display(self) -> str:
        """The field as it reads on screen, with its dashes and blanks."""
        out = []
        for index, slot in enumerate(self._slots):
            if index and index % self.group == 0:
                out.append(SEPARATOR)
            out.append(slot or BLANK)
        return "".join(out)

    def update(self, dt: float) -> None:
        """Only the caret's blink; the field itself is event-driven."""
        self._time += dt

    # ------------------------------------------------------------------
    # Editing
    # ------------------------------------------------------------------
    def clear(self) -> None:
        self._slots = [""] * self.length
        self.cursor = 0
        self.error = None

    def _touched(self) -> None:
        """Any edit clears a stale complaint and restarts the blink."""
        self.error = None
        self._time = 0.0

    def type_character(self, char: str) -> bool:
        """Write one character at the caret. False if it is not one of ours."""
        if not char:
            return False
        cleaned = normalise(char)
        if len(cleaned) != 1 or cleaned not in ALPHABET:
            return False
        if self.cursor >= self.length:
            return False
        self._slots[self.cursor] = cleaned
        self.cursor = min(self.cursor + 1, self.length)
        self._touched()
        return True

    def backspace(self) -> None:
        """Clear the slot behind the caret, or the one under it if it is last."""
        if self.cursor >= self.length and self._slots[self.length - 1]:
            self._slots[self.length - 1] = ""
            self.cursor = self.length - 1
        elif self.cursor > 0:
            self.cursor -= 1
            self._slots[self.cursor] = ""
        self._touched()

    def delete(self) -> None:
        """Clear the slot under the caret, leaving the caret where it is."""
        if self.cursor < self.length:
            self._slots[self.cursor] = ""
        self._touched()

    def _first_empty(self) -> int:
        """The first slot still waiting, or the last one if none are."""
        for index, slot in enumerate(self._slots):
            if not slot:
                return index
        return self.length - 1

    def move_cursor(self, step: int) -> None:
        self.cursor = max(0, min(self.cursor + step, self.length - 1))
        self._time = 0.0

    def dial(self, step: int) -> None:
        """Turn the slot under the caret through the alphabet, for a pad."""
        index = min(self.cursor, self.length - 1)
        current = self._slots[index]
        position = ALPHABET.find(current) if current else -1
        self._slots[index] = ALPHABET[(position + step) % len(ALPHABET)]
        self.cursor = index
        self._touched()

    def set_text(self, text: str) -> bool:
        """Replace the field wholesale. False if nothing usable was in it.

        This is what a paste does: a code arrives as one lump, and
        dropping it into the slots one character at a time would mean a
        code with a space in it filled the field short.
        """
        cleaned = normalise(text)
        usable = [char for char in cleaned if char in ALPHABET][:self.length]
        if not usable:
            return False
        self._slots = usable + [""] * (self.length - len(usable))
        self.cursor = min(len(usable), self.length)
        self._touched()
        return True

    def paste_from_clipboard(self) -> bool:
        """Take the clipboard's text, if there is any and it has code in it."""
        text = clipboard.paste()
        if text is None:
            self.error = "Nothing to paste."
            return False
        if not self.set_text(text):
            self.error = "That is not a save code."
            return False
        return True

    # ------------------------------------------------------------------
    # Reading it back
    # ------------------------------------------------------------------
    def decode(self) -> SaveRecord | None:
        """The save this code names, or None with `error` set to say why."""
        try:
            return decode(self.text)
        except SaveCodeError as exc:
            self.error = str(exc)
            return None

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Consume one key event. True if the field took it."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_BACKSPACE:
            self.backspace()
            return True
        if event.key == pygame.K_DELETE:
            self.delete()
            return True
        if event.key == pygame.K_LEFT:
            self.move_cursor(-1)
            return True
        if event.key == pygame.K_RIGHT:
            self.move_cursor(1)
            return True
        if event.key == pygame.K_HOME:
            self.cursor = 0
            return True
        if event.key == pygame.K_END:
            self.cursor = self._first_empty()
            return True
        # Ctrl-V, and Cmd-V for a Mac. The browser build gets its paste
        # through the same door, because the page hands the keystroke on.
        if event.key == pygame.K_v and event.mod & (pygame.KMOD_CTRL
                                                    | pygame.KMOD_META):
            self.paste_from_clipboard()
            return True
        return self.type_character(getattr(event, "unicode", ""))

    def handle_pad(self, input_manager) -> bool:
        """Dialling and stepping, for a player without a keyboard."""
        pressed = input_manager.was_pressed
        if pressed("move_up"):
            self.dial(1)
        elif pressed("move_down"):
            self.dial(-1)
        elif pressed("move_left"):
            self.move_cursor(-1)
        elif pressed("move_right"):
            self.move_cursor(1)
        else:
            return False
        return True

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def width(self) -> int:
        return len(self.display()) * ADVANCE - 1

    def caret_visible(self) -> bool:
        """Half of each blink, and always for a moment after an edit."""
        return (self._time % CARET_BLINK) * 2 < CARET_BLINK

    def caret_x(self) -> int:
        """Where the caret sits, in pixels from the field's left edge."""
        index = min(self.cursor, self.length - 1)
        return (index + index // self.group) * ADVANCE

    def height(self, font) -> int:
        """The text and the caret's own row under it."""
        return font.get_height() + 1

    def draw(self, surface, font, x: int, y: int, tint=None) -> None:
        """The slots at (x, y), with the caret blinking underneath them.

        The caret gets a row of its own below the glyphs rather than an
        underline through them: the font's bottom two rows are descender
        space, and a bar drawn in them sits inside the Q and the comma.
        """
        image = font.render(self.display())
        if tint is not None:
            image = image.copy()
            image.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(image, (x, y))
        if self.caret_visible():
            caret = pygame.Rect(x + self.caret_x(), y + font.get_height(),
                                ADVANCE - 1, 1)
            pygame.draw.rect(surface, tint or (246, 214, 140), caret)
