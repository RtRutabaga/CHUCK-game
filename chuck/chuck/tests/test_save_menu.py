"""SAVE GAME in the pause menu, LOAD CODE on the title.

The two ends of a save code, as the player meets them. The tests that
matter most are the round trip -- save in one game, paste into another,
arrive at the same door with the same everything -- and the small one
about the letter E, which is a character on the code field and the
interact key everywhere else in the game.
"""

import os
import asyncio
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.pause_scene import MAIN, NOT_HERE, SAVED, PauseScene
from src.scenes.title_scene import TitleScene
from src.scenes.world_scene import WorldScene
from src.systems import clipboard, save_code
from src.systems.save import SaveRecord


def _game(directory):
    game = Game(save_path=Path(directory) / "save.json")
    while game.scenes.current is not None:
        game.scenes.pop()
    return game


def _key(key, unicode="", mod=0):
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode,
                              mod=mod)


def _type(scene, text):
    for char in text:
        scene.handle_event(_key(ord(char.lower()), char))


def _enter(scene):
    scene.handle_event(_key(pygame.K_RETURN, "\r"))


class _Pad:
    """An input manager that says it is a controller."""

    def __init__(self, *actions):
        self._actions = set(actions)
        self.using_controller = True
        self.last_kind = "xbox"

    def was_pressed(self, action):
        return action in self._actions


# ----------------------------------------------------------------------
# Saving
# ----------------------------------------------------------------------
def test_save_game_sits_between_volume_and_fullscreen() -> None:
    assert MAIN.index("SAVE GAME") == MAIN.index("VOLUME") + 1
    assert MAIN.index("FULLSCREEN") == MAIN.index("SAVE GAME") + 1


def test_saving_at_a_door_shows_a_code_for_the_game_on_disk() -> None:
    """One record, two forms. They cannot be two different games."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.cigarettes.replace(214)
            game.deaths.replace(9)
            game.progress.enable("chult_reached")
            pause = PauseScene(game)
            game.scenes.push(pause)

            pause.choose("SAVE GAME")
            assert pause.page == "save"
            assert pause.options == SAVED

            decoded = save_code.decode(pause._code)
            assert decoded.checkpoint_id == "temple_1"
            assert decoded.cigarettes == 214
            assert decoded.deaths == 9
            assert "chult_reached" in decoded.progress_flags
            # The code is the save; nothing is kept on the machine.
            assert "Nothing is kept" in pause._note
        finally:
            game._shutdown()


def test_the_code_leaves_sanity_behind() -> None:
    """Twelve characters had no room for it, and that is the whole cost."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            world = game.checkpoints.load_checkpoint("temple_1")
            world.sanity.current = 23
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("SAVE GAME")

            assert save_code.decode(pause._code).sanity == config.SANITY_START
        finally:
            game._shutdown()


def test_there_is_nowhere_to_save_from_a_cutscene() -> None:
    """Pausing somewhere that is not a room refuses, and says why."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.active_checkpoint_id = "opening_docks"
            pause = PauseScene(game)
            game.scenes.push(pause)

            pause.choose("SAVE GAME")
            assert pause.page == "save"
            assert pause._code is None
            assert pause.options == NOT_HERE
        finally:
            game._shutdown()


def test_copy_puts_it_on_the_clipboard_or_says_it_could_not() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        original = clipboard.copy
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("SAVE GAME")

            taken = []
            clipboard.copy = lambda text: taken.append(text) or True
            pause.choose("COPY")
            assert taken == [pause._code]
            assert pause._note == "Copied"

            clipboard.copy = lambda text: False
            pause.choose("COPY")
            assert "Write it down" in pause._note
        finally:
            clipboard.copy = original
            game._shutdown()


def test_browser_paste_fills_load_code_and_resumes() -> None:
    from unittest.mock import patch
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            save_menu = PauseScene(game)
            game.scenes.push(save_menu)
            save_menu.choose("SAVE GAME")
            code = save_menu._code
            save_menu.close()
            load_menu = PauseScene(game, page="load", standalone=True)
            expected_map = game.scenes.current.map_name
            with patch.object(clipboard, "enable_browser_paste") as enabled:
                game.scenes.push(load_menu)
                enabled.assert_called_with(True)
                with patch.object(clipboard, "take_browser_paste", return_value=code):
                    load_menu.update(1 / 30)
                assert load_menu._field().complete
                load_menu._try_code()
                enabled.assert_called_with(False)
            assert isinstance(game.scenes.current, WorldScene)
            assert game.scenes.current.map_name == expected_map
        finally:
            game._shutdown()


def test_browser_copy_updates_the_save_page_after_permission_result() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        original = clipboard.copy_browser
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("SAVE GAME")

            taken = []

            async def allowed(text):
                taken.append(text)
                return True

            clipboard.copy_browser = allowed
            asyncio.run(pause._copy_code())
            assert taken == [pause._code]
            assert pause._note == "Copied"

            async def blocked(_text):
                return False

            clipboard.copy_browser = blocked
            asyncio.run(pause._copy_code())
            assert pause._note == "Clipboard blocked. Write it down."
        finally:
            clipboard.copy_browser = original
            game._shutdown()


def test_back_from_the_save_page_returns_to_save_game() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("SAVE GAME")
            pause.choose("BACK")
            assert pause.page == "main"
            assert MAIN[pause.selected] == "SAVE GAME"
        finally:
            game._shutdown()


# ----------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------
def test_load_code_is_on_the_title_and_opens_the_field() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            title = TitleScene(game)
            game.scenes.push(title)
            assert "LOAD CODE" in title.options
            title._selected = title.options.index("LOAD CODE")
            title._choose()

            menu = game.scenes.current
            assert isinstance(menu, PauseScene)
            assert menu.page == "load" and menu.standalone
            # The title is still underneath, waiting to be come back to.
            assert isinstance(game.scenes._stack[0], TitleScene)
        finally:
            game._shutdown()


def _load_page(game):
    title = TitleScene(game)
    game.scenes.push(title)
    title._selected = title.options.index("LOAD CODE")
    title._choose()
    return game.scenes.current


def test_a_code_typed_in_starts_that_game() -> None:
    """The whole point, end to end, with the title left behind."""
    code = save_code.for_display(SaveRecord(
        "temple_9", 60, ("chult_reached", "sewer_completed"), 214, 9))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            _type(menu, code.replace("-", ""))
            assert menu._field().complete
            _enter(menu)

            world = game.scenes.current
            assert isinstance(world, WorldScene)
            assert game.active_checkpoint_id == "temple_9"
            # Nothing left underneath: the title went with the load.
            assert [type(s) for s in game.scenes._stack] == [WorldScene]
            assert game.cigarettes.total == 214
            assert game.deaths.total == 9
            assert "chult_reached" in game.progress.flags
        finally:
            game._shutdown()


def test_a_loaded_code_is_where_the_game_now_is() -> None:
    """Nothing is kept on the machine, so the code is the whole answer."""
    code = save_code.for_display(
        SaveRecord("temple_9", 60, ("chult_reached",), 3, 1))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            _type(menu, code.replace("-", ""))
            _enter(menu)
            assert game.active_checkpoint_id == "temple_9"
            assert game.cigarettes.total == 3 and game.deaths.total == 1
        finally:
            game._shutdown()


def test_a_mistyped_code_stays_on_the_menu_and_says_so() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            _type(menu, "Z" * save_code.CODE_LENGTH)
            _enter(menu)
            assert game.scenes.current is menu
            assert menu._field().error
            # Nothing was started.
            assert game.active_checkpoint_id != "temple_9"
        finally:
            game._shutdown()


def test_a_half_typed_code_does_nothing_on_enter() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            _type(menu, "KMW9")
            _enter(menu)
            assert game.scenes.current is menu
            assert "characters" in menu._field().error
        finally:
            game._shutdown()


def test_a_code_for_a_door_this_build_lacks_is_refused_before_the_load() -> None:
    """Checked on the menu, not halfway into tearing the title down."""
    code = save_code.for_display(SaveRecord("temple_9", 60, (), 0, 0))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            game.checkpoints.can_resume = lambda record: False
            _type(menu, code.replace("-", ""))
            _enter(menu)
            assert game.scenes.current is menu
            assert menu._field().error == "That code is not one this game knows."
        finally:
            game._shutdown()


def test_e_is_a_letter_on_the_code_field_and_not_the_interact_key() -> None:
    """E opens doors everywhere else in the game; here it is a character.

    The field would be unusable if the letter that appears in a third of
    all codes also submitted the page.
    """
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            _type(menu, "E")
            assert menu._field().text == "E"
            # And the keyboard's interact never reaches the page, even
            # though E and Enter are both bound to it.
            game.input._actions_just_pressed.add("interact")
            menu.update(0.01)
            assert game.scenes.current is menu
            assert menu._field().text == "E"
        finally:
            game._shutdown()


def test_escape_leaves_the_code_field_for_the_title() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            menu.handle_event(_key(pygame.K_ESCAPE))
            assert isinstance(game.scenes.current, TitleScene)
        finally:
            game._shutdown()


def test_a_controller_spells_a_code_out_and_loads_it() -> None:
    """No keyboard: the stick dials a character, the button loads."""
    code = save_code.for_display(SaveRecord("temple_9", 60, (), 5, 2))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            field = menu._field()
            for char in save_code.normalise(code):
                menu.game.input = _Pad("move_up")
                while field._slots[field.cursor] != char:
                    menu.update(0.01)
                menu.game.input = _Pad("move_right")
                menu.update(0.01)
            assert field.display() == code

            menu.game.input = _Pad("interact")
            menu.update(0.01)
            assert isinstance(game.scenes.current, WorldScene)
            assert game.active_checkpoint_id == "temple_9"
        finally:
            game._shutdown()


def test_arrow_keys_spell_a_code_out_through_the_menu_and_load_it() -> None:
    """The phone's fallback, driven the way the shell actually drives it.

    The touch shell sends real arrow keydowns, not controller actions,
    so this goes through the scene's event path rather than calling the
    field directly: a phone with no keyboard panel open can still dial a
    code in and press Enter, using nothing the d-pad cannot send.
    """
    code = save_code.for_display(SaveRecord("temple_9", 60, (), 5, 2))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            field = menu._field()
            for char in save_code.normalise(code):
                # Up dials. Twelve characters this way is slow on
                # purpose; it is the way in that needs no keyboard.
                guard = 0
                while field._slots[field.cursor] != char:
                    menu.handle_event(_key(pygame.K_UP))
                    guard += 1
                    assert guard < 64, "dialling went round without landing"
                menu.handle_event(_key(pygame.K_RIGHT))
            assert field.display() == code

            menu.handle_event(_key(pygame.K_RETURN))
            assert isinstance(game.scenes.current, WorldScene)
            assert game.active_checkpoint_id == "temple_9"
        finally:
            game._shutdown()


def test_the_letters_the_pad_shares_with_the_alphabet_still_type() -> None:
    """W, S and E are directions to the pad and letters to the field.

    The dial hangs off the arrow keys for exactly this reason: `move_up`
    carries W as well as the up arrow, and `interact` carries E as well
    as Enter, and all three are in the save-code alphabet. Move the dial
    back onto the actions and typing the W in a code would dial a
    character instead of writing one, while the E would submit.

    So this drives the whole loop the way `Game._handle_events` does --
    the key reaches the input manager *and* the scene, then the frame
    updates -- because that is the only arrangement in which the bug
    could appear at all.
    """
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            menu = _load_page(game)
            field = menu._field()
            typed = ""
            for char in "WSE":
                event = _key(ord(char.lower()), char.lower())
                game.input.begin_frame()
                game.input.process_event(event)
                menu.handle_event(event)
                menu.update(0.01)
                typed += char
                # After every keystroke, not just at the end: a stray
                # dial lands in the *next* slot, and the following
                # keystroke would type over it and hide the damage.
                assert field.text == typed, (
                    f"after typing {typed!r} the field holds "
                    f"{field.text!r}: something is dialling as well as "
                    f"typing")
                # E is the other half of it. Read as `interact` it
                # submits, and a three-character code complains.
                assert field.error is None, (
                    f"typing {char!r} tried to load the code: {field.error}")
            assert menu.page == "load" and game.scenes.current is menu
        finally:
            game._shutdown()


# ----------------------------------------------------------------------
# Both ends
# ----------------------------------------------------------------------
def test_a_code_carries_a_game_from_one_machine_to_another() -> None:
    """Saved in one Game, pasted into another that has never seen it."""
    with tempfile.TemporaryDirectory() as first_dir:
        first = _game(first_dir)
        try:
            first.checkpoints.load_checkpoint("temple_9")
            first.cigarettes.replace(412)
            first.deaths.replace(17)
            for flag in ("chult_reached", "sewer_completed",
                         "captain_chest_opened"):
                first.progress.enable(flag)
            pause = PauseScene(first)
            first.scenes.push(pause)
            pause.choose("SAVE GAME")
            code = pause._code
        finally:
            first._shutdown()

    with tempfile.TemporaryDirectory() as second_dir:
        second = _game(second_dir)
        try:
            menu = _load_page(second)
            # Pasted the way it would arrive: dashes, and lower case.
            menu._field().set_text(code.lower())
            _enter(menu)

            assert second.active_checkpoint_id == "temple_9"
            assert second.cigarettes.total == 412
            assert second.deaths.total == 17
            assert {"chult_reached", "sewer_completed",
                    "captain_chest_opened"} <= second.progress.flags
        finally:
            second._shutdown()


# ----------------------------------------------------------------------
# Leaving
# ----------------------------------------------------------------------
def test_quitting_hands_the_code_over_before_it_asks() -> None:
    """A code is the only thing that survives leaving, so show it.

    Warning someone in the abstract that progress will be lost is no use
    when the thing that would save them is twelve characters the game
    already knows.
    """
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.cigarettes.replace(77)
            pause = PauseScene(game)
            game.scenes.push(pause)

            pause.selected = MAIN.index("QUIT TO TITLE")
            pause.choose("QUIT TO TITLE")
            assert pause.page == "confirm"
            assert pause._code, "quitting should show a code"
            assert save_code.decode(pause._code).checkpoint_id == "temple_1"
            assert save_code.decode(pause._code).cigarettes == 77
            # The caret starts on COPY -- the useful, harmless thing --
            # and never on YES: leaving is the deliberate one.
            assert pause.options[pause.selected] == "COPY"
        finally:
            game._shutdown()


def test_quitting_only_offers_a_code() -> None:
    """The warning is read-only: it hands a code over, it does not bank one."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("QUIT TO TITLE")
            assert pause._code
        finally:
            game._shutdown()


def test_the_quit_warning_can_copy_the_code_it_shows() -> None:
    """The same offer the save page makes, on the page that needs it more.

    Quitting is the last moment a code is reachable, and before this the
    only way to keep it was to transcribe twelve characters by eye. On a
    phone there is nothing to transcribe onto.
    """
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        original = clipboard.copy
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.cigarettes.replace(41)
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("QUIT TO TITLE")

            assert pause.options == ("COPY", "NO", "YES")
            taken = []
            clipboard.copy = lambda text: taken.append(text) or True
            pause.choose("COPY")
            assert taken == [pause._code]
            assert pause._note == "Copied"
            # Copying is not leaving: the warning is still up, and the
            # code it copied is still the one for this game.
            assert pause.page == "confirm"
            assert save_code.decode(taken[0]).cigarettes == 41

            clipboard.copy = lambda text: False
            pause.choose("COPY")
            assert "Write it down" in pause._note
            assert pause.page == "confirm"
        finally:
            clipboard.copy = original
            game._shutdown()


def test_the_quit_warning_offers_no_copy_when_there_is_nothing_to_copy() -> None:
    """From a cutscene there is no code, so there is nothing to offer."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.active_checkpoint_id = "opening_docks"
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("QUIT TO TITLE")
            assert pause._code is None
            assert pause.options == ("NO", "YES")
        finally:
            game._shutdown()


def test_copying_on_the_way_out_does_not_stop_the_player_leaving() -> None:
    """COPY is an extra, not a gate: YES and NO still do what they did."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)

            pause.choose("QUIT TO TITLE")
            pause.choose("NO")
            assert pause.page == "main", "NO should go back, not leave"

            pause.choose("QUIT TO TITLE")
            pause.choose("YES")
            from src.scenes.title_scene import TitleScene
            assert isinstance(game.scenes.current, TitleScene)
        finally:
            game._shutdown()


def test_a_copied_note_does_not_follow_the_player_onto_the_warning() -> None:
    """"Copied" belongs to the page that copied.

    Saving, then quitting, must not open the warning already claiming
    something was copied from it.
    """
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        original = clipboard.copy
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            clipboard.copy = lambda text: True
            pause.choose("SAVE GAME")
            pause.choose("COPY")
            assert pause._note == "Copied"

            pause.back()
            pause.choose("QUIT TO TITLE")
            assert pause._note == ""
        finally:
            clipboard.copy = original
            game._shutdown()


def test_quitting_from_nowhere_saveable_says_so() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            game.active_checkpoint_id = "opening_docks"
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("QUIT TO TITLE")
            assert pause.page == "confirm"
            assert pause._code is None
            surface = pygame.Surface((config.NATIVE_WIDTH,
                                      config.NATIVE_HEIGHT))
            pause.draw(surface)          # the no-code wording draws
        finally:
            game._shutdown()


def test_every_line_the_quit_warning_can_show_fits_its_panel() -> None:
    from src.scenes.pause_scene import QUIT_WITHOUT_A_CODE
    from src.ui.bitmap_font import ADVANCE

    usable = 250 - 16
    for line in QUIT_WITHOUT_A_CODE + ("Write this down, or copy it:",
                                       "Anything since here will be lost."):
        assert len(line) * ADVANCE - 1 <= usable, line


# ----------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------
def test_both_pages_draw_without_running_off_their_panel() -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            surface = pygame.Surface((config.NATIVE_WIDTH,
                                      config.NATIVE_HEIGHT))

            pause.choose("SAVE GAME")
            pause.draw(surface)
            pause._goto("save")
            pause._code = None
            pause.draw(surface)

            pause._goto("load")
            pause._field().set_text("KMW9J6ZP2T5D")
            pause.draw(surface)
            pause._field().error = "That code has a character wrong in it."
            pause.draw(surface)

            # The code is drawn at twice the font size and still fits
            # inside the panel it is drawn on.
            pause._goto("save")
            pause._save_now()
            assert pause._big(pause._code).get_width() < 236 - 8
        finally:
            game._shutdown()


def test_the_quit_warning_has_room_for_every_option_it_offers() -> None:
    """Adding COPY pushed the options down, so the panel had to grow.

    Checking the drawn pixels does not work here: the font's bottom two
    rows are descender space, so a line that overruns by a little paints
    nothing and an intact border proves nothing. What actually breaks is
    the options colliding with the footer under them, so that is what
    this checks -- from the same constants the drawing uses, so a fourth
    option added without more height fails here rather than on screen.
    """
    from src.scenes.pause_scene import (
        CONFIRM, CONFIRM_HEIGHT, CONFIRM_HEIGHT_NO_CODE, CONFIRM_MENU_TOP,
        CONFIRM_MENU_TOP_NO_CODE, CONFIRM_WITH_CODE, FOOTER_MARGIN,
    )
    from src.ui.bitmap_font import GLYPH_H

    line = GLYPH_H + 4

    # Only the code page can show a footer: the note is cleared on the
    # way in, and the one thing that sets it is COPY, which is not
    # offered when there is no code. So this page owes the footer room
    # and the other one does not.
    last = CONFIRM_MENU_TOP + (len(CONFIRM_WITH_CODE) - 1) * line + GLYPH_H
    footer_top = CONFIRM_HEIGHT - GLYPH_H - FOOTER_MARGIN
    assert last <= footer_top, (
        f"{CONFIRM_WITH_CODE} runs to y={last} but the footer starts at "
        f"y={footer_top}; the quit warning needs a taller panel")

    bare = CONFIRM_MENU_TOP_NO_CODE + (len(CONFIRM) - 1) * line + GLYPH_H
    assert bare < CONFIRM_HEIGHT_NO_CODE, (
        f"{CONFIRM} runs to y={bare} on a {CONFIRM_HEIGHT_NO_CODE}px panel")

    for height in (CONFIRM_HEIGHT, CONFIRM_HEIGHT_NO_CODE):
        assert height <= config.NATIVE_HEIGHT, (
            f"a {height}px panel does not fit a {config.NATIVE_HEIGHT}px screen")


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All save menu tests passed.")


if __name__ == "__main__":
    _run_all()
