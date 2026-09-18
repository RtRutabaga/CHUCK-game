"""SAVE GAME in the pause menu, LOAD CODE on the title.

The two ends of a save code, as the player meets them. The tests that
matter most are the round trip -- save in one game, paste into another,
arrive at the same door with the same everything -- and the small one
about the letter E, which is a character on the code field and the
interact key everywhere else in the game.
"""

import os
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
            written = game.saves.load()
            assert decoded.checkpoint_id == written.checkpoint_id == "temple_1"
            assert decoded.cigarettes == written.cigarettes == 214
            assert decoded.deaths == written.deaths == 9
            assert set(decoded.progress_flags) == set(written.progress_flags)
            assert "Saved" in pause._note
        finally:
            game._shutdown()


def test_the_code_is_the_sanity_free_form_of_the_record_on_disk() -> None:
    """The slot keeps the exact figure; the code resumes on a fresh 60."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            world = game.checkpoints.load_checkpoint("temple_1")
            world.sanity.current = 23
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("SAVE GAME")

            assert game.saves.load().sanity == 23
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
            assert game.saves.load() is None
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
            assert pause._note == "Copied."

            clipboard.copy = lambda text: False
            pause.choose("COPY")
            assert "Write it down" in pause._note
        finally:
            clipboard.copy = original
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


def test_loading_a_code_is_what_continue_comes_back_to() -> None:
    """Otherwise CONTINUE would take them to whatever was here before."""
    code = save_code.for_display(
        SaveRecord("temple_9", 60, ("chult_reached",), 3, 1))
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.saves.write(SaveRecord("temple_1", 60, (), 0, 0))
            menu = _load_page(game)
            _type(menu, code.replace("-", ""))
            _enter(menu)
            assert game.saves.load().checkpoint_id == "temple_9"
            assert game.checkpoints.can_continue
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
            # Nothing was started and nothing was written.
            assert game.saves.load() is None
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
            assert not second.checkpoints.can_continue
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
            # NO is where the caret starts: leaving is the deliberate one.
            assert pause.selected == 0
        finally:
            game._shutdown()


def test_quitting_writes_nothing() -> None:
    """The warning is read-only. It offers a code; it does not save."""
    with tempfile.TemporaryDirectory() as directory:
        game = _game(directory)
        try:
            game.checkpoints.load_checkpoint("temple_1")
            pause = PauseScene(game)
            game.scenes.push(pause)
            pause.choose("QUIT TO TITLE")
            assert pause._code
            assert game.saves.load() is None
        finally:
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
    for line in QUIT_WITHOUT_A_CODE + ("Write this down before you go:",
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
