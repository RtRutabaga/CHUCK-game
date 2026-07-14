"""Input handling.

Responsibilities:
    * Translate raw pygame events/keys into named game actions
      (e.g. "move_up", "interact") so gameplay code never touches
      keycodes directly.
    * Track pressed / just-pressed state per action.

Keeping this abstraction from day one makes rebindable controls and
gamepad support cheap to add later.
"""

import pygame

# Default bindings. Multiple keys may map to one action.
# TODO: Load from a user settings file when a settings screen exists.
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


class InputManager:
    """Tracks input state and exposes it as named actions."""

    def __init__(self) -> None:
        self._actions_down: set[str] = set()
        self._actions_just_pressed: set[str] = set()

    def begin_frame(self) -> None:
        """Clear one-frame state. Call once per frame, BEFORE pumping
        events, so 'just pressed' survives until gameplay reads it."""
        self._actions_just_pressed.clear()

    def process_event(self, event: pygame.event.Event) -> None:
        """Record a single pygame event (called by Game._handle_events)."""
        if event.type == pygame.KEYDOWN:
            action = KEY_BINDINGS.get(event.key)
            if action and action not in self._actions_down:
                self._actions_down.add(action)
                self._actions_just_pressed.add(action)
        elif event.type == pygame.KEYUP:
            action = KEY_BINDINGS.get(event.key)
            if action:
                self._actions_down.discard(action)
        # TODO: Gamepad events map into the same action names here.

    # ------------------------------------------------------------------
    # Queries used by gameplay code
    # ------------------------------------------------------------------
    def is_down(self, action: str) -> bool:
        """Return True while any key bound to `action` is held."""
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
