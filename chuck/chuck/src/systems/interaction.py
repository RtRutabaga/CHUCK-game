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


def _centre(rect) -> tuple[float, float]:
    x, y, w, h = _bounds(rect)
    return (x + w / 2.0, y + h / 2.0)


def _nearest(candidates, player_box):
    """Of several things in reach, the one Chuck is closest to.

    Big props overlap small ones -- the cabin's map table is nine tiles
    wide and its interaction zone swallows the fridge standing at the
    end of it -- so first-in-the-list is the wrong answer. Comparing
    centres rather than edges is what separates them: Chuck is inside
    both zones at once, so edge distance is zero for each.
    """
    if not candidates:
        return None
    px, py = _centre(player_box)
    return min(
        candidates,
        key=lambda target: (
            (_centre(target.interaction_bounds())[0] - px) ** 2
            + (_centre(target.interaction_bounds())[1] - py) ** 2
        ),
    )


def find_target(probe, player_box, npcs, props):
    """The thing Chuck would talk to right now, or None.

    NPCs take precedence over environmental targets (a person standing by
    a sign answers first); mute targets are skipped. Within either
    group, the nearest thing answers.
    """
    reachable = [npc for npc in npcs if in_reach(npc, probe, player_box)]
    if reachable:
        return _nearest(reachable, player_box)
    reachable = [
        prop for prop in props
        if (prop.dialogue_id is not None
            or getattr(prop, "choice_id", None) is not None
            or callable(getattr(prop, "interact", None)))
        and in_reach(prop, probe, player_box)
    ]
    return _nearest(reachable, player_box)
