"""Game controllers: the layout, the stick, pausing, and the prompts."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.core.input import (
    CONTROLLER, KEYBOARD, STICK_PRESS, STICK_RELEASE, InputManager,
    controller_kind)
from src.scenes.pause_scene import CONTROLS, PauseScene, controls_rows
from src.ui import prompts

PAD = 7
MAX = 32767


class _FakePad:
    def quit(self):
        pass


class _BrowserButton:
    def __init__(self):
        self.pressed = False


class _BrowserValues(list):
    @property
    def length(self):
        return len(self)


class _BrowserPad:
    def __init__(self):
        self.id = "Xbox Wireless Controller"
        self.buttons = _BrowserValues(_BrowserButton() for _ in range(16))
        self.axes = _BrowserValues([0.0, 0.0])


class _BrowserNavigator:
    def __init__(self, pad):
        self.pads = _BrowserValues([pad])

    def getGamepads(self):
        return self.pads


def _manager(kind: str = "xbox") -> InputManager:
    manager = InputManager()
    manager.controllers[PAD] = _FakePad()
    manager._kinds[PAD] = kind
    return manager


def _button(manager, button, down=True):
    manager.process_event(pygame.event.Event(
        pygame.CONTROLLERBUTTONDOWN if down else pygame.CONTROLLERBUTTONUP,
        instance_id=PAD, button=button))


def _stick(manager, axis, amount):
    manager.process_event(pygame.event.Event(
        pygame.CONTROLLERAXISMOTION, instance_id=PAD, axis=axis,
        value=round(amount * MAX)))


def _key(manager, key, down=True):
    manager.process_event(pygame.event.Event(
        pygame.KEYDOWN if down else pygame.KEYUP, key=key, mod=0,
        unicode="", scancode=0))


def test_the_layout() -> None:
    manager = _manager()
    for button, actions in (
            (pygame.CONTROLLER_BUTTON_A, {"interact"}),
            (pygame.CONTROLLER_BUTTON_B, {"jump", "back"}),
            (pygame.CONTROLLER_BUTTON_X, {"scratch"}),
            (pygame.CONTROLLER_BUTTON_Y, {"pause"}),
            (pygame.CONTROLLER_BUTTON_DPAD_LEFT, {"move_left"})):
        manager.begin_frame()
        _button(manager, button)
        assert manager._actions_just_pressed == actions, button
        _button(manager, button, down=False)
        assert not manager._actions_down & actions
    # Buttons by position on every pad, not by printed letter.
    assert os.environ.get("SDL_GAMECONTROLLER_USE_BUTTON_LABELS") == "0"


def test_the_stick_is_four_directions_with_hysteresis() -> None:
    manager = _manager()
    x, y = pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_AXIS_LEFTY
    _stick(manager, x, STICK_PRESS - 0.05)
    assert manager.movement_vector() == (0.0, 0.0)     # inside the dead zone
    _stick(manager, x, STICK_PRESS + 0.05)
    assert manager.movement_vector() == (1.0, 0.0)
    assert manager.was_pressed("move_right")
    _stick(manager, x, STICK_RELEASE + 0.05)            # eased off, still held
    assert manager.is_down("move_right")
    _stick(manager, x, STICK_RELEASE - 0.05)
    assert not manager.is_down("move_right")
    # A diagonal is the keyboard's diagonal: eight-way, normalised.
    _stick(manager, x, -0.9)
    _stick(manager, y, -0.9)
    dx, dy = manager.movement_vector()
    assert dx < 0 and dy < 0 and abs(dx * dx + dy * dy - 1.0) < 1e-9
    # Straight across to the other side.
    _stick(manager, x, 0.9)
    assert manager.is_down("move_right") and not manager.is_down("move_left")


def test_every_source_has_to_let_go() -> None:
    manager = _manager()
    _key(manager, pygame.K_d)
    _button(manager, pygame.CONTROLLER_BUTTON_DPAD_RIGHT)
    _stick(manager, pygame.CONTROLLER_AXIS_LEFTX, 0.9)
    _button(manager, pygame.CONTROLLER_BUTTON_DPAD_RIGHT, down=False)
    _key(manager, pygame.K_d, down=False)
    assert manager.is_down("move_right")
    _stick(manager, pygame.CONTROLLER_AXIS_LEFTX, 0.0)
    assert not manager.is_down("move_right")


def test_browser_gamepad_fallback_maps_xbox_edge_without_sdl_events() -> None:
    manager = InputManager()
    pad = _BrowserPad()
    navigator = _BrowserNavigator(pad)
    manager.enable_browser_gamepads(navigator)

    manager.begin_frame()
    pad.buttons[0].pressed = True
    assert manager.poll_browser_gamepads() == {"interact"}
    assert manager.was_pressed("interact")
    assert manager.last_device == CONTROLLER
    assert prompts.title_prompt(manager) == "D-PAD / STICK   A"
    assert prompts.hint(manager, config.HINT_INTERACT) == \
        "Press A to interact"
    assert dict(controls_rows(manager))["MOVE"] == "LEFT STICK / D-PAD"

    manager.begin_frame()
    assert manager.poll_browser_gamepads() == set()
    assert manager.is_down("interact") and not manager.was_pressed("interact")
    pad.buttons[0].pressed = False
    manager.poll_browser_gamepads()
    assert not manager.is_down("interact")

    manager.begin_frame()
    pad.buttons[13].pressed = True
    pad.axes[0] = -0.9
    manager.poll_browser_gamepads()
    assert manager.is_down("move_down") and manager.is_down("move_left")
    pad.buttons[13].pressed = False
    pad.axes[0] = 0.0
    manager.poll_browser_gamepads()
    assert manager.movement_vector() == (0.0, 0.0)


def test_it_knows_what_was_used_last_and_what_kind_of_pad() -> None:
    assert controller_kind("PS5 Controller") == "playstation"
    assert controller_kind("DualShock 4") == "playstation"
    assert controller_kind("Nintendo Switch Pro Controller") == "switch"
    assert controller_kind("Xbox Series X Controller") == "xbox"
    assert controller_kind("") == "xbox"
    manager = _manager("playstation")
    assert manager.last_device == KEYBOARD
    _button(manager, pygame.CONTROLLER_BUTTON_A)
    assert manager.last_device == CONTROLLER
    assert manager.last_kind == "playstation"
    _key(manager, pygame.K_e)
    assert manager.last_device == KEYBOARD


def test_prompts_name_the_button_being_held() -> None:
    manager = _manager()
    # Keyboard: exactly the text the game always had.
    assert prompts.hint(manager, config.HINT_INTERACT) == config.HINT_INTERACT
    assert prompts.title_prompt(manager) == "UP / DOWN   E / ENTER"
    assert controls_rows(manager) == CONTROLS
    _button(manager, pygame.CONTROLLER_BUTTON_A)
    assert prompts.hint(manager, config.HINT_INTERACT) == \
        "Press A to interact"
    assert prompts.hint(manager, config.HINT_JUMP) == "Press B to jump"
    assert prompts.hint(manager, config.HINT_SCRATCH) == "Press X to scratch"
    assert prompts.title_prompt(manager) == "D-PAD / STICK   A"
    rows = dict(controls_rows(manager))
    assert rows["MOVE"] == "LEFT STICK / D-PAD"
    assert rows["PAUSE"] == "Y"
    manager._kinds[PAD] = "playstation"
    _button(manager, pygame.CONTROLLER_BUTTON_A)
    assert prompts.hint(manager, config.HINT_INTERACT) == \
        "Press CROSS to interact"
    assert prompts.back_footer(manager) == "CROSS / CIRCLE: BACK"
    manager._kinds[PAD] = "switch"
    _button(manager, pygame.CONTROLLER_BUTTON_A)
    # Nintendo prints B where Xbox prints A.
    assert prompts.hint(manager, config.HINT_INTERACT) == \
        "Press B to interact"
    # Every label is drawable in the pixel font.
    from src.ui.bitmap_font import GLYPH_ORDER
    for labels in prompts.PAD_LABELS.values():
        for text in labels.values():
            assert set(text) <= set(GLYPH_ORDER), text


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    game.input.controllers[PAD] = _FakePad()
    game.input._kinds[PAD] = "xbox"
    return directory, game


def _post(game, event_type, **fields):
    pygame.event.post(pygame.event.Event(event_type, **fields))
    game._handle_events()


def test_start_pauses_and_b_backs_out_and_chuck_walks_on_the_stick() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        world._arrival_fade_t = None
        game.running = True
        start = world.player.x
        _post(game, pygame.CONTROLLERAXISMOTION, instance_id=PAD,
              axis=pygame.CONTROLLER_AXIS_LEFTX, value=MAX)
        for _ in range(20):
            game.scenes.update(1 / 30)
        assert world.player.x > start, "the stick did not walk him"
        _post(game, pygame.CONTROLLERAXISMOTION, instance_id=PAD,
              axis=pygame.CONTROLLER_AXIS_LEFTX, value=0)

        _post(game, pygame.CONTROLLERBUTTONDOWN, instance_id=PAD,
              button=pygame.CONTROLLER_BUTTON_Y)
        pause = game.scenes.current
        assert isinstance(pause, PauseScene)
        pause._goto("controls")
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        pause.draw(surface)
        _post(game, pygame.CONTROLLERBUTTONDOWN, instance_id=PAD,
              button=pygame.CONTROLLER_BUTTON_B)
        game.scenes.update(0.0)
        assert pause.page == "main"
        _post(game, pygame.CONTROLLERBUTTONDOWN, instance_id=PAD,
              button=pygame.CONTROLLER_BUTTON_Y)
        assert game.scenes.current is world
        assert game.running
    finally:
        game._shutdown()
        directory.cleanup()


def test_unplugging_the_pad_in_use_pauses_and_lets_go_of_everything() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        _post(game, pygame.CONTROLLERBUTTONDOWN, instance_id=PAD,
              button=pygame.CONTROLLER_BUTTON_DPAD_RIGHT)
        assert game.input.is_down("move_right")
        _post(game, pygame.CONTROLLERDEVICEREMOVED, instance_id=PAD)
        assert isinstance(game.scenes.current, PauseScene)
        assert not game.input.is_down("move_right")
        assert game.input.last_device == KEYBOARD
        assert PAD not in game.input.controllers
    finally:
        game._shutdown()
        directory.cleanup()
