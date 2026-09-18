"""Button prompts that name whatever the player is holding.

Every piece of text that names a key -- the tutorial hints, the title's
prompt, the controls page, the menu footers -- asks here instead of
spelling the key out. With the keyboard last used, the answer is the
text the game always had. With a controller, it is that controller's
button: A/B/X on an Xbox pad, CROSS/CIRCLE/SQUARE on a PlayStation pad,
and Nintendo's letters on a Switch pad (which sit in different places,
so the same position gets a different letter).

PlayStation's buttons are named in words. The symbols were tried as
nine-pixel icons and read as punctuation at this resolution; the words
are in the game's own font and cannot be misread.
"""

from __future__ import annotations

from src.core import config

# Button labels by controller kind, for the positions the game uses.
PAD_LABELS = {
    "xbox": {"interact": "A", "jump": "B", "scratch": "X",
             "pause": "START", "back": "B"},
    "playstation": {"interact": "CROSS", "jump": "CIRCLE",
                    "scratch": "SQUARE", "pause": "OPTIONS",
                    "back": "CIRCLE"},
    "switch": {"interact": "B", "jump": "A", "scratch": "Y",
               "pause": "PLUS", "back": "A"},
}
KEY_LABELS = {"interact": "E", "jump": "SPACE", "scratch": "F",
              "pause": "ESC", "back": "ESC"}

PAD_MOVE = "LEFT STICK / D-PAD"
KEY_MOVE = "WASD / ARROW KEYS"

# The tutorial hints, as templates for a controller. The keyboard keeps
# the exact lines in config.
_PAD_HINTS = {
    config.HINT_INTERACT: "Press {interact} to interact",
    config.HINT_JUMP: "Press {jump} to jump",
    config.HINT_SCRATCH: "Press {scratch} to scratch",
    config.HINT_PAUSE: "Press {pause} to pause",
}

def label(input_manager, action: str) -> str:
    """The key or button for an action, on the device last used."""
    if input_manager is None or not input_manager.using_controller:
        return KEY_LABELS[action]
    return PAD_LABELS.get(input_manager.last_kind,
                          PAD_LABELS["xbox"])[action]


def move_label(input_manager) -> str:
    if input_manager is not None and input_manager.using_controller:
        return PAD_MOVE
    return KEY_MOVE


def hint(input_manager, text: str) -> str:
    """A tutorial hint, naming the button on a controller."""
    if input_manager is None or not input_manager.using_controller:
        return text
    template = _PAD_HINTS.get(text)
    if template is None:
        return text
    return template.format(**{action: label(input_manager, action)
                              for action in KEY_LABELS})


def title_prompt(input_manager) -> str:
    if input_manager is not None and input_manager.using_controller:
        return f"UP / DOWN   {label(input_manager, 'interact')}"
    return "UP / DOWN   E / ENTER"


def back_footer(input_manager) -> str:
    if input_manager is not None and input_manager.using_controller:
        return (f"{label(input_manager, 'interact')} / "
                f"{label(input_manager, 'back')}: BACK")
    return "E / ESC: BACK"
