"""Finding what Chuck can interact with.

One rule, one place. Both the interact key and the tutorial hint ask
this module "is there anything in reach?" — so the hint can never
promise an interaction the key won't deliver, or vice versa.

The rule (unchanged from when it was inline in the WorldScene): a
target is in reach if Chuck's facing probe touches it OR he's standing
on it. NPCs answer before environmental targets such as props and
map-authored choice zones.

Pure math on (x, y, w, h) tuples — no pygame, so it's unit-testable
headless. Callers pass rects; pygame.Rect exposes .x/.y/.width/.height
and so satisfies _bounds() unchanged.
"""

from __future__ import annotations

from typing import Protocol


class Interactable(Protocol):
    """Anything Chuck can talk to: NPCs, and props with a line."""

    def interaction_bounds(self) -> tuple[int, int, int, int]: ...


def _bounds(rect) -> tuple[float, float, float, float]:
    """(x, y, w, h) from a pygame.Rect or any tuple-shaped rect."""
    if isinstance(rect, tuple):
        return rect
    return (rect.x, rect.y, rect.width, rect.height)


def rects_overlap(a, b) -> bool:
    ax, ay, aw, ah = _bounds(a)
    bx, by, bw, bh = _bounds(b)
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def in_reach(target: Interactable, probe, player_box) -> bool:
    """True if Chuck faces the target or is standing on it."""
    zone = target.interaction_bounds()
    return rects_overlap(probe, zone) or rects_overlap(player_box, zone)


def find_target(probe, player_box, npcs, props):
    """The thing Chuck would talk to right now, or None.

    NPCs take precedence over environmental targets (a person standing by
    a sign answers first); mute targets are skipped.
    """
    for npc in npcs:
        if in_reach(npc, probe, player_box):
            return npc
    for prop in props:
        has_something_to_say = (
            prop.dialogue_id is not None
            or getattr(prop, "choice_id", None) is not None
        )
        if not has_something_to_say:
            continue  # mute scenery
        if in_reach(prop, probe, player_box):
            return prop
    return None
