"""The sanctum battle in motion (session 132).

The tableau's combatants now fight: the beholder's eye rays cycle
through the three adventurers' lanes, the ranger's arrows and the
wizard's bolts streak west at the beholder, and the fighter's slash
pulses where the skeletons press him. Every attack is a timed hazard
Chuck must dodge — none of it is aimed at him, and none of it can be
influenced by him. Survival is the only objective in this room.
"""

from __future__ import annotations

from src.core import config
from src.entities.battle_actor import BattleActor
from src.entities.entity import Entity
from src.world import collision

# Per-kind projectile tuning: (speed, damage, width, height, max_travel).
# Rays dissipate at range so the hall's east half stays survivable;
# arrows and bolts die against the west wall behind the beholder.
_PROJECTILES = {
    "ray": (config.BATTLE_RAY_SPEED, config.BATTLE_RAY_SANITY_DAMAGE,
            config.BATTLE_RAY_HITBOX_LONG, config.BATTLE_RAY_HITBOX_SHORT,
            config.BATTLE_RAY_RANGE),
    "arrow": (config.BATTLE_ARROW_SPEED, config.BATTLE_ARROW_SANITY_DAMAGE,
              7, 2, None),
    "bolt": (config.BATTLE_BOLT_SPEED, config.BATTLE_BOLT_SANITY_DAMAGE,
             5, 5, None),
}

_COLORS = {
    # Beholder-iris red, weathered arrow wood, staff-gem teal.
    "ray": ((198, 54, 46), (255, 172, 148)),
    "arrow": ((112, 80, 46), (226, 222, 210)),
    "bolt": ((118, 214, 190), (224, 250, 242)),
}


class BattleProjectile(Entity):
    """One shot crossing the sanctum: an eye ray, arrow, or bolt."""

    def __init__(self, center_x: float, center_y: float,
                 direction: int, kind: str) -> None:
        if kind not in _PROJECTILES:
            raise ValueError(f"Unknown battle projectile {kind!r}")
        speed, damage, width, height, max_travel = _PROJECTILES[kind]
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self.kind = kind
        self.direction = 1 if direction >= 0 else -1
        self.speed = speed
        self.damage = damage
        self._travel_left = max_travel

    def update(self, dt: float, tilemap) -> None:
        dx = self.direction * self.speed * dt
        new_x, new_y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, 0.0, tilemap
        )
        blocked = abs(new_x - (self.x + dx)) > 1e-4
        self.x, self.y = new_x, new_y
        if blocked:
            self.alive = False
        if self._travel_left is not None:
            self._travel_left -= abs(dx)
            if self._travel_left <= 0.0:
                self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        body, bright = _COLORS[self.kind]
        rect = pygame.Rect(
            round(self.x) - ox, round(self.y) - oy, self.width, self.height
        )
        pygame.draw.rect(surface, body, rect)
        if self.kind == "bolt":
            pygame.draw.rect(
                surface, bright,
                (rect.x + 1, rect.y + 1, self.width - 2, self.height - 2))
            return
        # Rays and arrows carry a bright leading edge showing their flight.
        tip_x = rect.right - 2 if self.direction > 0 else rect.x
        pygame.draw.rect(surface, bright, (tip_x, rect.y, 2, self.height))


class BattleChoreographer:
    """The fixed attack cadences of a battle Chuck cannot influence."""

    def __init__(self, actors: list[BattleActor]) -> None:
        by_kind = {actor.kind: actor for actor in actors}
        self._beholder = by_kind["beholder"]
        self._fighter = by_kind["fighter"]
        self._wizard = by_kind["wizard"]
        self._ranger = by_kind["ranger"]
        # Eye rays cycle the adventurers' lanes in a fixed, learnable order.
        self._ray_lanes = [
            self._ranger.center_y, self._fighter.center_y,
            self._wizard.center_y,
        ]
        self._ray_lane = 0
        # Staggered opening beats so the room never fires all at once.
        self._ray_timer = 1.2
        self._arrow_timer = 0.6
        self._bolt_timer = 1.8
        self._slash_timer = 0.9
        self._slash_active = 0.0

    def update(self, dt: float) -> list[BattleProjectile]:
        shots: list[BattleProjectile] = []

        self._ray_timer -= dt
        while self._ray_timer <= 0.0:
            self._ray_timer += config.BATTLE_RAY_INTERVAL
            lane_y = self._ray_lanes[self._ray_lane]
            self._ray_lane = (self._ray_lane + 1) % len(self._ray_lanes)
            shots.append(BattleProjectile(
                self._beholder.center_x + self._beholder.width / 2 + 6,
                lane_y, 1, "ray"))
            self._beholder.attack_flash = config.BATTLE_ATTACK_FLASH

        self._arrow_timer -= dt
        while self._arrow_timer <= 0.0:
            self._arrow_timer += config.BATTLE_ARROW_INTERVAL
            shots.append(BattleProjectile(
                self._ranger.center_x - 8, self._ranger.center_y,
                -1, "arrow"))
            self._ranger.attack_flash = config.BATTLE_ATTACK_FLASH

        self._bolt_timer -= dt
        while self._bolt_timer <= 0.0:
            self._bolt_timer += config.BATTLE_BOLT_INTERVAL
            shots.append(BattleProjectile(
                self._wizard.center_x - 8, self._wizard.center_y,
                -1, "bolt"))
            self._wizard.attack_flash = config.BATTLE_ATTACK_FLASH

        self._slash_timer -= dt
        if self._slash_timer <= 0.0:
            self._slash_timer += config.BATTLE_SLASH_INTERVAL
            self._slash_active = config.BATTLE_SLASH_ACTIVE
            self._fighter.attack_flash = config.BATTLE_ATTACK_FLASH
        elif self._slash_active > 0.0:
            self._slash_active = max(0.0, self._slash_active - dt)

        return shots

    def slash_hitbox(self):
        """The fighter's sword arc, west toward the pressing skeletons."""
        if self._slash_active <= 0.0:
            return None
        import pygame

        return pygame.Rect(
            int(self._fighter.x) - 14, int(self._fighter.y) - 2, 14, 12
        )
