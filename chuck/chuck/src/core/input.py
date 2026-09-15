"""Input handling: keyboard and game controllers, as named actions.

Responsibilities:
    * Translate raw pygame events into named game actions (e.g.
      "move_up", "interact") so gameplay code never touches keycodes or
      controller buttons directly.
    * Track pressed / just-pressed state per action.
    * Know which device the player last used, and what kind of
      controller it is, so prompts on screen can name the right button.

Controllers go through SDL's game-controller layer, which lays out Xbox,
PlayStation, Switch Pro and most PC pads the same way. Buttons are read by
*position*, not by the letter printed on them (see
`use_positional_buttons`), so the layout is the same on every pad and
only the labels differ:

    left stick / D-pad   move (and menus)
    south  (Xbox A)      talk / examine / confirm
    east   (Xbox B)      jump -- and back, in menus
    west   (Xbox X)      scratch
    Start / Back         pause

The stick is read as four directions with hysteresis, the same as the
keys, so movement stays eight-way and a jump off a stick goes exactly
where a jump off the keyboard would.
"""

from __future__ import annotations

import os

import pygame

# Default bindings. Multiple keys may map to one action.
KEY_BINDINGS: dict[int, str] = {
    pygame.K_w: "move_up",
    pygame.K_UP: "move_up",
    pygame.K_s: "move_down",
    pygame.K_DOWN: "move_down",
    pygame.K_a: "move_left",
    pygame.K_LEFT: "move_left",
    pygame.K_d: "move_right",
    pygame.K_RIGHT: "move_right",
    pygame.K_e: "interact",
    pygame.K_RETURN: "interact",
    pygame.K_SPACE: "jump",
    pygame.K_f: "scratch",
}

# Controller buttons, by position. One button can mean two things: the
# east button is jump in play and back in a menu, and each scene reads
# whichever of the two it cares about.
BUTTON_BINDINGS: dict[int, tuple[str, ...]] = {
    pygame.CONTROLLER_BUTTON_DPAD_UP: ("move_up",),
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: ("move_down",),
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: ("move_left",),
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: ("move_right",),
    pygame.CONTROLLER_BUTTON_A: ("interact",),
    pygame.CONTROLLER_BUTTON_B: ("jump", "back"),
    pygame.CONTROLLER_BUTTON_X: ("scratch",),
    pygame.CONTROLLER_BUTTON_START: ("pause",),
    pygame.CONTROLLER_BUTTON_BACK: ("pause",),
}

# The left stick, as four directions. It has to pass PRESS to count and
# fall back under RELEASE to let go, so a stick resting near the edge of
# the dead zone does not flicker a direction on and off.
STICK_PRESS = 0.5
STICK_RELEASE = 0.35
_AXIS_MAX = 32767.0
STICK_AXES = {
    pygame.CONTROLLER_AXIS_LEFTX: ("move_left", "move_right"),
    pygame.CONTROLLER_AXIS_LEFTY: ("move_up", "move_down"),
}

KEYBOARD = "keyboard"
CONTROLLER = "controller"


def use_positional_buttons() -> None:
    """Ask SDL for buttons by position, before any controller opens.

    By default SDL reports a Nintendo pad's buttons by their printed
    letters, which are in the opposite places to an Xbox pad's -- so
    "A" would be the east button on one and the south button on the
    other, and the layout would move depending on what was plugged in.
    """
    os.environ.setdefault("SDL_GAMECONTROLLER_USE_BUTTON_LABELS", "0")


def controller_kind(name: str) -> str:
    """xbox, playstation or switch, from the name SDL gives the pad."""
    lowered = (name or "").lower()
    if any(word in lowered for word in ("ps3", "ps4", "ps5", "playstation",
                                        "dualshock", "dualsense", "sony")):
        return "playstation"
    if any(word in lowered for word in ("nintendo", "switch", "joy-con",
                                        "pro controller")):
        return "switch"
    return "xbox"


class InputManager:
    """Tracks input state and exposes it as named actions."""

    def __init__(self) -> None:
        self._actions_down: set[str] = set()
        self._actions_just_pressed: set[str] = set()
        # What is holding each action down: a key, a button, a stick
        # direction. An action is released only when nothing holds it,
        # so letting go of the D-pad does not stop a held stick.
        self._sources: dict[str, set[tuple]] = {}
        self.controllers: dict[int, object] = {}
        self._kinds: dict[int, str] = {}
        self._stick: dict[tuple[int, int], int] = {}
        self.last_device = KEYBOARD
        self.last_kind = "xbox"
        # The instance id of a controller unplugged this frame, while it
        # was the device in use. Game pauses on it.
        self.lost_controller: int | None = None

    # ------------------------------------------------------------------
    # Controllers
    # ------------------------------------------------------------------
    def start_controllers(self) -> None:
        """Open every controller already plugged in. Safe to call twice."""
        try:
            from pygame._sdl2 import controller
            controller.init()
            for index in range(controller.get_count()):
                self._open(index)
        except (ImportError, pygame.error):
            pass

    def _open(self, device_index: int) -> None:
        try:
            from pygame._sdl2 import controller
            if not controller.is_controller(device_index):
                return
            pad = controller.Controller(device_index)
        except (ImportError, pygame.error):
            return
        if pad.id in self.controllers:
            return
        self.controllers[pad.id] = pad
        self._kinds[pad.id] = controller_kind(getattr(pad, "name", ""))

    def _close(self, instance_id: int) -> None:
        pad = self.controllers.pop(instance_id, None)
        self._kinds.pop(instance_id, None)
        for sources in self._sources.values():
            for source in [s for s in sources if s[1] == instance_id
                           and s[0] in ("button", "stick")]:
                sources.discard(source)
        for action, sources in self._sources.items():
            if not sources:
                self._actions_down.discard(action)
        self._stick = {key: value for key, value in self._stick.items()
                       if key[0] != instance_id}
        if pad is not None:
            try:
                pad.quit()
            except pygame.error:
                pass

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def begin_frame(self) -> None:
        """Clear one-frame state. Call once per frame, BEFORE pumping
        events, so 'just pressed' survives until gameplay reads it."""
        self._actions_just_pressed.clear()
        self.lost_controller = None

    def _hold(self, action: str, source: tuple) -> None:
        sources = self._sources.setdefault(action, set())
        if not sources and action not in self._actions_down:
            self._actions_just_pressed.add(action)
        sources.add(source)
        self._actions_down.add(action)

    def _let_go(self, action: str, source: tuple) -> None:
        sources = self._sources.setdefault(action, set())
        sources.discard(source)
        if not sources:
            self._actions_down.discard(action)

    def process_event(self, event: pygame.event.Event) -> None:
        """Record a single pygame event (called by Game._handle_events)."""
        if event.type == pygame.KEYDOWN:
            self.last_device = KEYBOARD
            action = KEY_BINDINGS.get(event.key)
            if action:
                self._hold(action, ("key", event.key))
        elif event.type == pygame.KEYUP:
            action = KEY_BINDINGS.get(event.key)
            if action:
                self._let_go(action, ("key", event.key))
        elif event.type == pygame.CONTROLLERDEVICEADDED:
            self._open(event.device_index)
        elif event.type == pygame.CONTROLLERDEVICEREMOVED:
            if (self.last_device == CONTROLLER
                    and event.instance_id in self.controllers):
                self.lost_controller = event.instance_id
            self._close(event.instance_id)
            if not self.controllers:
                self.last_device = KEYBOARD
        elif event.type == pygame.CONTROLLERBUTTONDOWN:
            self._used(event.instance_id)
            for action in BUTTON_BINDINGS.get(event.button, ()):
                self._hold(action, ("button", event.instance_id,
                                    event.button))
        elif event.type == pygame.CONTROLLERBUTTONUP:
            for action in BUTTON_BINDINGS.get(event.button, ()):
                self._let_go(action, ("button", event.instance_id,
                                      event.button))
        elif event.type == pygame.CONTROLLERAXISMOTION:
            self._stick_moved(event.instance_id, event.axis, event.value)

    def _used(self, instance_id: int) -> None:
        self.last_device = CONTROLLER
        self.last_kind = self._kinds.get(instance_id, self.last_kind)

    def _stick_moved(self, instance_id: int, axis: int, value: int) -> None:
        if axis not in STICK_AXES:
            return
        negative, positive = STICK_AXES[axis]
        amount = max(-1.0, min(1.0, value / _AXIS_MAX))
        key = (instance_id, axis)
        held = self._stick.get(key, 0)
        if held and abs(amount) >= STICK_RELEASE and (amount > 0) == (held > 0):
            return                      # still pushed the same way
        now = 0
        if amount <= -STICK_PRESS:
            now = -1
        elif amount >= STICK_PRESS:
            now = 1
        if now == held:
            return
        if held:
            self._let_go(negative if held < 0 else positive,
                         ("stick", instance_id, axis))
        if now:
            self._used(instance_id)
            self._hold(negative if now < 0 else positive,
                       ("stick", instance_id, axis))
        self._stick[key] = now

    # ------------------------------------------------------------------
    # Queries used by gameplay code
    # ------------------------------------------------------------------
    @property
    def using_controller(self) -> bool:
        return self.last_device == CONTROLLER

    def is_down(self, action: str) -> bool:
        """Return True while anything bound to `action` is held."""
        return action in self._actions_down

    def was_pressed(self, action: str) -> bool:
        """Return True only on the frame `action` was first pressed."""
        return action in self._actions_just_pressed

    def movement_vector(self) -> tuple[float, float]:
        """Current movement direction as a normalized (dx, dy) vector.

        Diagonals are normalized so Chuck doesn't walk ~41% faster
        when moving diagonally.
        """
        dx = float(self.is_down("move_right")) - float(self.is_down("move_left"))
        dy = float(self.is_down("move_down")) - float(self.is_down("move_up"))
        if dx and dy:
            dx *= 0.7071067811865476
            dy *= 0.7071067811865476
        return dx, dy
