"""Small reusable combat rules for Chuck's scratch."""

from src.systems.interaction import rects_overlap


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
