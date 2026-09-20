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

A phone is the third case. The touch shell puts its own buttons on
screen -- JUMP, SCRATCH, INSPECT / TALK -- and telling that player to
press E or SPACE names keys they do not have. So the labels become the
words already printed on the buttons under their thumb.

That is the whole of the difference, and it is the reason this belongs
here: one module decides how a control is named, so the tutorial hints,
the title prompt, the controls page and every menu footer follow from
one change rather than five. Nothing about the game itself differs --
see `runtime.touch_host`.
"""

from __future__ import annotations

from src.core import config
from src.core.runtime import touch_host

# Button labels by controller kind, for the positions the game uses.
PAD_LABELS = {
    "xbox": {"interact": "B", "jump": "A", "scratch": "X",
             "pause": "Y", "back": "A"},
    "playstation": {"interact": "CIRCLE", "jump": "CROSS",
                    "scratch": "SQUARE", "pause": "TRIANGLE",
                    "back": "CROSS"},
    "switch": {"interact": "A", "jump": "B", "scratch": "Y",
               "pause": "X", "back": "B"},
}
KEY_LABELS = {"interact": "E", "jump": "SPACE", "scratch": "F",
              "pause": "ESC", "back": "ESC"}
# What the touch shell's buttons actually say, so a hint names the thing
# the player can see. Back is the pause button: the shell sends Escape
# from it, and Escape is what every page reads as "go back".
# The pause button is the one control whose face is a symbol rather
# than a word, so it is the one that has to say where it is.
TOUCH_LABELS = {"interact": "INSPECT", "jump": "JUMP", "scratch": "SCRATCH",
                "pause": "PAUSE, TOP RIGHT", "back": "PAUSE"}

PAD_MOVE = "LEFT STICK / D-PAD"
KEY_MOVE = "WASD / ARROW KEYS"
# Worth saying, because it is the one thing about the pad a player
# cannot see: the corners hold two directions at once.
TOUCH_MOVE = "THE PAD, CORNERS TOO"

# The tutorial hints, as templates for a controller. The keyboard keeps
# the exact lines in config.
_PAD_HINTS = {
    config.HINT_INTERACT: "Press {interact} to interact",
    config.HINT_JUMP: "Press {jump} to jump",
    config.HINT_SCRATCH: "Press {scratch} to scratch",
    config.HINT_PAUSE: "Press {pause} to pause",
}

# The same lines for a thumb. "Tap", because that is what is being done.
#
# The pause hint is empty on purpose, which means no hint at all. On a
# keyboard the line has to exist because nothing on screen says ESC
# pauses; on a phone the pause button is sitting in the corner the whole
# time, so the line would be teaching a player to tap something already
# in front of them. An empty hint draws nothing -- see
# `TutorialHint.draw`.
_TOUCH_HINTS = {
    config.HINT_INTERACT: "Tap INSPECT to interact",
    config.HINT_JUMP: "Tap JUMP to jump",
    config.HINT_SCRATCH: "Tap SCRATCH to scratch",
    config.HINT_PAUSE: "",
}

def _on_pad(input_manager) -> bool:
    return input_manager is not None and input_manager.using_controller


def label(input_manager, action: str) -> str:
    """The key or button for an action, on whatever is in the hands.

    A controller wins over the touch shell, because a phone with a pad
    paired to it is being played with the pad.
    """
    if _on_pad(input_manager):
        return PAD_LABELS.get(input_manager.last_kind,
                              PAD_LABELS["xbox"])[action]
    if touch_host():
        return TOUCH_LABELS[action]
    return KEY_LABELS[action]


def move_label(input_manager) -> str:
    if _on_pad(input_manager):
        return PAD_MOVE
    return TOUCH_MOVE if touch_host() else KEY_MOVE


def hint(input_manager, text: str) -> str:
    """A tutorial hint, naming the control the player actually has.

    An empty return means the hint should not be shown at all on this
    device, which is how the phone drops the pause hint.
    """
    if _on_pad(input_manager):
        template = _PAD_HINTS.get(text)
        if template is None:
            return text
        return template.format(**{action: label(input_manager, action)
                                  for action in KEY_LABELS})
    if touch_host():
        return _TOUCH_HINTS.get(text, text)
    return text


def title_prompt(input_manager) -> str:
    if _on_pad(input_manager):
        return f"D-PAD / STICK   {label(input_manager, 'interact')}"
    if touch_host():
        return "PAD UP / DOWN   INSPECT"
    return "UP / DOWN   E / ENTER"


def back_footer(input_manager) -> str:
    if _on_pad(input_manager):
        return (f"{label(input_manager, 'interact')} / "
                f"{label(input_manager, 'back')}: BACK")
    if touch_host():
        return "INSPECT, OR THE PAUSE BUTTON: BACK"
    return "E / ESC: BACK"
