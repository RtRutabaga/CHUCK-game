"""Small reusable combat rules for Chuck's scratch."""

from src.systems.interaction import rects_overlap


def scratch_first_target(attack_box, targets) -> bool:
    """Defeat the first living target in reach; one swipe hits one target."""
    for target in targets:
        if target.alive and rects_overlap(attack_box, target.hitbox):
            target.on_scratched()
            return True
    return False
