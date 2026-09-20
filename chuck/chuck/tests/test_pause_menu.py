"""Pause menu, controls, volume, fullscreen, and saved second words."""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.systems import save_code
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.opening_cutscene_scene import OpeningCutsceneScene
from src.scenes.pause_scene import CONTROLS, MAIN, PauseScene
from src.scenes.title_scene import TitleScene
from src.scenes.world_scene import WorldScene
from src.systems.save import SaveRecord
from src.systems.settings import DEFAULT_LEVEL, LEVELS, SettingsStore


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def _key(game, key) -> None:
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0,
                                         unicode="", scancode=0))
    game._handle_events()


def _press(game, action) -> None:
    game.input._actions_just_pressed.add(action)
    game.scenes.update(0.0)
    game.input._actions_just_pressed.clear()


def test_escape_pauses_play_and_cutscenes_and_nothing_quits() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        game.running = True
        _key(game, pygame.K_ESCAPE)
        pause = game.scenes.current
        assert isinstance(pause, PauseScene) and pause.page == "main"
        assert game.running, "Esc quit the game"
        # The world under it is frozen: only the top scene updates.
        before = (world.player.x, world.player.y, world._world_time)
        for _ in range(30):
            game.scenes.update(1 / 30)
        assert (world.player.x, world.player.y, world._world_time) == before
        # Esc again resumes.
        _key(game, pygame.K_ESCAPE)
        assert game.scenes.current is world

        cutscene = OpeningCutsceneScene(game)
        game.scenes.replace(cutscene)
        _key(game, pygame.K_ESCAPE)
        assert isinstance(game.scenes.current, PauseScene)
        assert game.running
        elapsed = cutscene.elapsed
        game.scenes.update(1.0)
        assert cutscene.elapsed == elapsed
    finally:
        game._shutdown()
        directory.cleanup()


def test_every_cutscene_pauses_rather_than_quits() -> None:
    import importlib
    import inspect
    import pkgutil

    import src.scenes as scenes

    for info in pkgutil.iter_modules(scenes.__path__):
        if not info.name.endswith("_cutscene_scene"):
            continue
        module = importlib.import_module(f"src.scenes.{info.name}")
        source = inspect.getsource(module)
        assert "self.game.quit()" not in source, info.name
        classes = [c for c in vars(module).values() if inspect.isclass(c)
                   and c.__module__ == module.__name__
                   and c.__name__.endswith("CutsceneScene")]
        assert classes and all(c.pausable for c in classes), info.name
    assert WorldScene.pausable
    assert not TitleScene.pausable and not DialogueScene.pausable


def test_the_menu_does_what_it_says() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        assert game.pause()
        pause = game.scenes.current
        assert list(MAIN) == ["RESUME", "CONTROLS", "VOLUME", "SAVE GAME",
                              "FULLSCREEN", "QUIT TO TITLE"]
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for page in ("main", "controls", "volume", "confirm", "save", "load"):
            pause._goto(page)
            pause.draw(surface)       # every page draws in the pixel font

        pause._goto("main")
        _press(game, "interact")                  # RESUME
        assert game.scenes.current is world

        game.pause()
        pause = game.scenes.current
        pause.selected = MAIN.index("CONTROLS")
        _press(game, "interact")
        assert pause.page == "controls"
        _press(game, "interact")                  # back
        assert pause.page == "main"

        # Quit asks first, and the caret never starts on YES. Which
        # option leads depends on whether there is a code to copy, so
        # the answers are found by name rather than by position.
        pause.selected = MAIN.index("QUIT TO TITLE")
        _press(game, "interact")
        assert pause.page == "confirm"
        assert pause.options[pause.selected] != "YES"
        first = pause.selected
        _press(game, "move_down")
        assert pause.selected != first, "the warning should still navigate"
        pause.selected = pause.options.index("NO")
        _press(game, "interact")                  # NO
        assert pause.page == "main" and game.scenes.current is pause
        pause.selected = MAIN.index("QUIT TO TITLE")
        _press(game, "interact")
        pause.selected = pause.options.index("YES")
        _press(game, "interact")                  # YES
        assert isinstance(game.scenes.current, TitleScene)
        assert len(game.scenes._stack) == 1
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_controls_page_lists_every_bound_key_and_the_title_opens_it():
    from src.core.input import KEY_BINDINGS

    listed = " ".join(keys for _action, keys in CONTROLS)
    for key in KEY_BINDINGS:
        name = pygame.key.name(key).upper()
        name = {"UP": "ARROW", "DOWN": "ARROW", "LEFT": "ARROW",
                "RIGHT": "ARROW", "RETURN": "ENTER"}.get(name, name)
        assert name in listed, name
    directory, game = _game()
    try:
        game.scenes.replace(TitleScene(game))
        title = game.scenes.current
        assert "CONTROLS" in title.options
        title._selected = title.options.index("CONTROLS")
        _press(game, "interact")
        page = game.scenes.current
        assert isinstance(page, PauseScene) and page.page == "controls"
        _key(game, pygame.K_ESCAPE)
        assert game.scenes.current is title
    finally:
        game._shutdown()
        directory.cleanup()


def test_volume_is_two_sliders_that_stick() -> None:
    directory, game = _game()
    try:
        assert (game.settings.music, game.settings.sound) == \
            (DEFAULT_LEVEL, DEFAULT_LEVEL)
        assert abs(game.audio.music_volume - config.AUDIO_MUSIC_VOLUME) < 1e-9
        game.checkpoints.load_checkpoint("waterdeep_start")
        game.pause()
        pause = game.scenes.current
        pause._goto("volume")
        for _ in range(3):
            _press(game, "move_left")             # music down three
        pause.selected = 1
        for _ in range(LEVELS + 5):
            _press(game, "move_right")            # sound up, clamped
        assert game.settings.music == DEFAULT_LEVEL - 3
        assert game.settings.sound == LEVELS
        assert abs(game.audio.music_volume - config.AUDIO_MUSIC_VOLUME
                   * (DEFAULT_LEVEL - 3) / DEFAULT_LEVEL) < 1e-9
        assert game.audio.sfx_volume <= 1.0
        path = game.settings_store.path
        stored = json.loads(path.read_text(encoding="utf-8"))
        assert stored["music"] == DEFAULT_LEVEL - 3
        # NEW GAME does not reset the settings.
        game.checkpoints.new_game()
        assert path.is_file()
    finally:
        game._shutdown()
        directory.cleanup()
    # ...and a new session starts with them.
    directory2 = tempfile.TemporaryDirectory()
    try:
        store = SettingsStore(Path(directory2.name) / "settings.json")
        store.path.write_text('{"music": 3, "sound": "loud", '
                              '"fullscreen": 7}', encoding="utf-8")
        loaded = store.load()
        assert (loaded.music, loaded.sound, loaded.fullscreen) == \
            (3, DEFAULT_LEVEL, False)
        store.path.write_text("not json", encoding="utf-8")
        assert store.load().music == DEFAULT_LEVEL
    finally:
        directory2.cleanup()


def test_fullscreen_toggles_from_the_menu_and_f11_and_is_remembered() -> None:
    directory, game = _game()
    try:
        game.checkpoints.load_checkpoint("waterdeep_start")
        _key(game, pygame.K_F11)
        assert game.settings.fullscreen
        game.pause()
        pause = game.scenes.current
        assert pause.label("FULLSCREEN") == "FULLSCREEN: ON"
        pause.selected = MAIN.index("FULLSCREEN")
        _press(game, "interact")
        assert not game.settings.fullscreen
        assert pause.label("FULLSCREEN") == "FULLSCREEN: OFF"
        stored = json.loads(game.settings_store.path.read_text("utf-8"))
        assert stored["fullscreen"] is False
    finally:
        game._shutdown()
        directory.cleanup()


def test_any_window_size_gets_whole_pixels_and_black_bars() -> None:
    native = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
    for size, scale in (((1280, 720), 4), ((1920, 1080), 6),
                        ((2560, 1440), 8), ((1366, 768), 4),
                        ((1280, 1024), 4)):
        frame, (x, y) = Game.present(native, size)
        assert frame.get_size() == (config.NATIVE_WIDTH * scale,
                                    config.NATIVE_HEIGHT * scale), size
        assert x == (size[0] - frame.get_width()) // 2
        assert y == (size[1] - frame.get_height()) // 2
    # Smaller than the game itself: shrunk to fit rather than cropped.
    frame, _ = Game.present(native, (200, 200))
    assert frame.get_width() <= 200 and frame.get_height() <= 200


def test_second_words_are_session_memory_that_a_code_drops() -> None:
    """Everyone introduces themselves again after resuming from a code.

    `spoken` went with the save file. It needs a positional key and
    would never fit in twelve characters, so it lives for the session
    and no longer survives a resume. The cost is one repeated hello per
    person already met, which is cosmetic.
    """
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        worker = next(n for n in scene.npcs if n.dialogue_id == "dock_worker")
        assert scene._second_word(worker, "dock_worker") == "dock_worker"
        assert game.spoken_to, "the session remembers within itself"
        code = save_code.for_display(game.checkpoints.save_here(
            "waterdeep_start", scene.sanity.current))
        assert save_code.decode(code).spoken == ()

        game.spoken_to.clear()
        continued = game.checkpoints.resume_from(save_code.decode(code))
        assert continued is not None
        again = next(n for n in continued.npcs
                     if n.dialogue_id == "dock_worker")
        assert continued._second_word(again, "dock_worker") == "dock_worker"
        # NEW GAME forgets.
        game.checkpoints.new_game()
        assert not game.spoken_to
    finally:
        game._shutdown()
        directory.cleanup()
