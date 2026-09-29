"""Small reusable combat rules for Chuck's scratch, and for backing off."""

import math

from src.systems.interaction import rects_overlap


def moved_away(old_position, player, enemy) -> bool:
    """Whether Chuck's move did not carry him further into an enemy.

    Touching an enemy stops Chuck walking *through* a body, which is
    what makes one a thing in the world rather than a decal. It must
    never stop him walking *out* of one. Cancelling the whole move on
    contact did both: a pursuer that caught up stood in him and pinned
    him there, and since it had caught him once it would catch him
    again, which is the difference between an enemy and a cage.

    So only the closing half of the move is refused. Retreating and
    sliding along a body are allowed -- anything that does not shorten
    the distance between the two centres. Chuck is faster than every
    pursuer in the game, so being able to leave is the whole of being
    able to escape; he does not need to be pushed, only let go.

    Animal Control is the exception, and is excluded by its caller
    rather than here: cornering Chuck is their entire purpose.
    """
    old_x, old_y = old_position
    enemy_x = enemy.x + enemy.width / 2
    enemy_y = enemy.y + enemy.height / 2
    before = math.hypot(
        (old_x + player.width / 2) - enemy_x,
        (old_y + player.height / 2) - enemy_y,
    )
    after = math.hypot(
        (player.x + player.width / 2) - enemy_x,
        (player.y + player.height / 2) - enemy_y,
    )
    return after >= before


def scratch_first_target(
    attack_box,
    targets,
    *,
    overlap_box=None,
    overlap_targets=(),
) -> bool:
    """Scratch one target, prioritizing an enemy occupying Chuck's space.

    ``attack_box`` remains the ordinary forward paw reach.  The optional
    overlap pass exists for small pursuers that can get inside that reach and
    pin Chuck against collision; it deliberately receives its own target list
    so overlapping scenery does not become scratchable by accident.
    """
    if overlap_box is not None:
        for target in overlap_targets:
            if target.alive and rects_overlap(overlap_box, target.hitbox):
                target.on_scratched()
                return True
    for target in targets:
        if target.alive and rects_overlap(attack_box, target.hitbox):
            target.on_scratched()
            return True
    return False
