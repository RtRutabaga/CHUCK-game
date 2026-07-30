"""The sanctum battle in motion (sessions 132, 134).

A desperate, overwhelming fight Chuck only has to survive. The
beholder's eye rays cycle the adventurers' lanes; the ranger whirls,
loosing a rotating spray of arrows in every direction; the wizard hurls
fans of bolts; the fighter's slash pulses where the skeletons press him;
and the beholder occasionally charges a screen-shaking cone of force
east across the hall. None of it is aimed at Chuck and none of it can be
influenced by him — but the air is thick with stray death. Survival is
the only objective in this room.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.core import config
from src.entities.battle_actor import BattleActor
from src.entities.entity import Entity
from src.world import collision

# Per-kind projectile tuning: (speed, damage, width, height, max_travel).
# Rays dissipate at range so the hall's east half stays survivable;
# arrows spray everywhere and die on whatever masonry they meet.
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


@dataclass
class BattleTick:
    """What one frame of the battle emitted into the world."""

    projectiles: list = field(default_factory=list)
    cones: list = field(default_factory=list)


class BattleProjectile(Entity):
    """One shot crossing the sanctum: an eye ray, arrow, or bolt.

    Direction is a free vector (dx, dy); rays and bolts fire flat, but
    the ranger's arrows fly at any angle as she spins.
    """

    def __init__(self, center_x: float, center_y: float,
                 dir_x: float, dir_y: float, kind: str) -> None:
        if kind not in _PROJECTILES:
            raise ValueError(f"Unknown battle projectile {kind!r}")
        speed, damage, width, height, max_travel = _PROJECTILES[kind]
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self.kind = kind
        mag = math.hypot(dir_x, dir_y) or 1.0
        self._ux, self._uy = dir_x / mag, dir_y / mag
        self.vx = self._ux * speed
        self.vy = self._uy * speed
        self.damage = damage
        self._travel_left = max_travel

    @property
    def direction(self) -> int:
        """Coarse east/west sign, for the flat rays and bolts."""
        return 1 if self.vx >= 0 else -1

    def update(self, dt: float, tilemap) -> None:
        dx, dy = self.vx * dt, self.vy * dt
        new_x, new_y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, tilemap
        )
        if (abs(new_x - (self.x + dx)) > 1e-4
                or abs(new_y - (self.y + dy)) > 1e-4):
            self.alive = False  # struck masonry
        self.x, self.y = new_x, new_y
        if self._travel_left is not None:
            self._travel_left -= math.hypot(dx, dy)
            if self._travel_left <= 0.0:
                self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        body, bright = _COLORS[self.kind]
        if self.kind == "arrow":
            # An oriented streak along the flight path, bright at the tip.
            cx = self.x + self.width / 2 - ox
            cy = self.y + self.height / 2 - oy
            tail = (cx - self._ux * 6, cy - self._uy * 6)
            pygame.draw.line(surface, body, tail, (cx, cy), 2)
            pygame.draw.line(surface, bright,
                             (cx - self._ux, cy - self._uy), (cx, cy), 2)
            return
        rect = pygame.Rect(
            round(self.x) - ox, round(self.y) - oy, self.width, self.height
        )
        pygame.draw.rect(surface, body, rect)
        if self.kind == "bolt":
            pygame.draw.rect(
                surface, bright,
                (rect.x + 1, rect.y + 1, self.width - 2, self.height - 2))
            return
        # The ray carries a bright leading edge showing its flight.
        tip_x = rect.right - 2 if self.direction > 0 else rect.x
        pygame.draw.rect(surface, bright, (tip_x, rect.y, 2, self.height))


class BeholderCone:
    """A charged wedge of force the beholder looses east across the hall.

    A bright telegraph (charging) warns where the blast will fall, then
    a brief lethal active window. On detonation the scene shakes the
    screen and booms. The wedge opens east — toward Chuck's half — from
    the beholder's eye, so he must be clear of it when it fires.
    """

    def __init__(self, apex_x: float, apex_y: float) -> None:
        self.apex_x = apex_x
        self.apex_y = apex_y
        self.state = "charging"
        self._charge_left = config.BATTLE_CONE_CHARGE
        self._active_left = config.BATTLE_CONE_ACTIVE
        self.alive = True
        self.just_activated = False

    @property
    def active(self) -> bool:
        return self.state == "active"

    def update(self, dt: float) -> None:
        self.just_activated = False
        if self.state == "charging":
            self._charge_left -= dt
            if self._charge_left <= 0.0:
                self.state = "active"
                self.just_activated = True
        elif self.state == "active":
            self._active_left -= dt
            if self._active_left <= 0.0:
                self.alive = False

    def contains(self, box) -> bool:
        """True if a hitbox lies within the live wedge."""
        if not self.active:
            return False
        dx = box.centerx - self.apex_x
        dy = box.centery - self.apex_y
        if dx <= 0.0:
            return False  # the wedge opens strictly east
        if math.hypot(dx, dy) > config.BATTLE_CONE_RANGE:
            return False
        return abs(math.atan2(dy, dx)) <= config.BATTLE_CONE_HALF_ANGLE

    def _polygon(self, ox: int, oy: int) -> list[tuple[float, float]]:
        half = config.BATTLE_CONE_HALF_ANGLE
        rng = config.BATTLE_CONE_RANGE
        pts = [(self.apex_x - ox, self.apex_y - oy)]
        steps = 8
        for i in range(steps + 1):
            angle = -half + (2 * half) * i / steps
            pts.append((self.apex_x + math.cos(angle) * rng - ox,
                        self.apex_y + math.sin(angle) * rng - oy))
        return pts

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pts = self._polygon(ox, oy)
        if self.active:
            frac = max(0.0, self._active_left / config.BATTLE_CONE_ACTIVE)
            fill = (236, 96, 72, int(70 + 150 * frac))
            pygame.draw.polygon(overlay, fill, pts)
            pygame.draw.polygon(overlay, (255, 210, 150, 220), pts, 2)
        else:
            # Telegraph: a pulsing wedge so the danger can be fled.
            elapsed = config.BATTLE_CONE_CHARGE - self._charge_left
            pulse = 0.5 + 0.5 * math.sin(elapsed * 16.0)
            pygame.draw.polygon(overlay, (206, 74, 122,
                                          int(28 + 44 * pulse)), pts)
            pygame.draw.polygon(overlay, (244, 150, 184,
                                          int(120 + 90 * pulse)), pts, 1)
        surface.blit(overlay, (0, 0))


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
        self._ray_timer = 1.0
        self._arrow_timer = 0.4
        self._bolt_timer = 1.4
        self._slash_timer = 0.9
        self._slash_active = 0.0
        self._cone_timer = 3.2  # the first blast comes a few seconds in
        self._spray_angle = 0.0  # the ranger's whirling aim

    def update(self, dt: float) -> BattleTick:
        tick = BattleTick()

        # The ranger whirls continuously, arrows or no arrows.
        self._ranger.spin = (self._ranger.spin
                             + config.BATTLE_RANGER_SPIN_SPEED * dt) % math.tau

        self._ray_timer -= dt
        while self._ray_timer <= 0.0:
            self._ray_timer += config.BATTLE_RAY_INTERVAL
            lane_y = self._ray_lanes[self._ray_lane]
            self._ray_lane = (self._ray_lane + 1) % len(self._ray_lanes)
            tick.projectiles.append(BattleProjectile(
                self._beholder.center_x + self._beholder.width / 2 + 6,
                lane_y, 1.0, 0.0, "ray"))
            self._beholder.attack_flash = config.BATTLE_ATTACK_FLASH

        self._arrow_timer -= dt
        while self._arrow_timer <= 0.0:
            self._arrow_timer += config.BATTLE_ARROW_INTERVAL
            self._spray_angle += config.BATTLE_ARROW_SPIN_STEP
            for k in range(config.BATTLE_ARROW_FAN):
                offset = (k - (config.BATTLE_ARROW_FAN - 1) / 2.0)
                angle = self._spray_angle + offset * config.BATTLE_ARROW_FAN_SPREAD
                tick.projectiles.append(BattleProjectile(
                    self._ranger.center_x, self._ranger.center_y,
                    math.cos(angle), math.sin(angle), "arrow"))
            self._ranger.attack_flash = config.BATTLE_ATTACK_FLASH

        self._bolt_timer -= dt
        while self._bolt_timer <= 0.0:
            self._bolt_timer += config.BATTLE_BOLT_INTERVAL
            for k in range(config.BATTLE_BOLT_FAN):
                offset = (k - (config.BATTLE_BOLT_FAN - 1) / 2.0)
                angle = math.pi + offset * config.BATTLE_BOLT_FAN_SPREAD
                tick.projectiles.append(BattleProjectile(
                    self._wizard.center_x, self._wizard.center_y,
                    math.cos(angle), math.sin(angle), "bolt"))
            self._wizard.attack_flash = config.BATTLE_ATTACK_FLASH

        self._slash_timer -= dt
        if self._slash_timer <= 0.0:
            self._slash_timer += config.BATTLE_SLASH_INTERVAL
            self._slash_active = config.BATTLE_SLASH_ACTIVE
            self._fighter.attack_flash = config.BATTLE_ATTACK_FLASH
        elif self._slash_active > 0.0:
            self._slash_active = max(0.0, self._slash_active - dt)

        self._cone_timer -= dt
        if self._cone_timer <= 0.0:
            self._cone_timer += config.BATTLE_CONE_INTERVAL
            tick.cones.append(BeholderCone(
                self._beholder.center_x + self._beholder.width / 2,
                self._beholder.center_y))
            self._beholder.attack_flash = config.BATTLE_ATTACK_FLASH

        return tick

    def slash_hitbox(self):
        """The fighter's sword arc, west toward the pressing skeletons."""
        if self._slash_active <= 0.0:
            return None
        import pygame

        return pygame.Rect(
            int(self._fighter.x) - 14, int(self._fighter.y) - 2, 14, 12
        )


class InfernalBattleChoreographer:
    """The trio's ongoing fight with the Pit Fiend.

    This shares the established battle actor/projectile path while changing
    the targets: the ranger now fires directly at the Pit Fiend, the wizard
    drives magic into it, and the fighter holds the lesser devils nearby.
    Chuck remains an observer navigating stray fire.
    """

    def __init__(self, actors: list[BattleActor]) -> None:
        by_kind = {actor.kind: actor for actor in actors}
        self._pit_fiend = by_kind["pit_fiend"]
        self._fighter = by_kind["fighter"]
        self._wizard = by_kind["wizard"]
        self._ranger = by_kind["ranger"]
        self._arrow_timer = 0.35
        self._bolt_timer = 0.8
        self._fiend_timer = 1.4
        self._fighter_timer = 0.5
        self._fiend_target = 0

    @staticmethod
    def _toward(source: BattleActor, target: BattleActor) -> tuple[float, float]:
        return (
            target.center_x - source.center_x,
            target.center_y - source.center_y,
        )

    def update(self, dt: float) -> BattleTick:
        tick = BattleTick()

        self._arrow_timer -= dt
        while self._arrow_timer <= 0.0:
            self._arrow_timer += 0.58
            dx, dy = self._toward(self._ranger, self._pit_fiend)
            tick.projectiles.append(BattleProjectile(
                self._ranger.center_x, self._ranger.center_y,
                dx, dy, "arrow",
            ))
            self._ranger.attack_flash = config.BATTLE_ATTACK_FLASH

        self._bolt_timer -= dt
        while self._bolt_timer <= 0.0:
            self._bolt_timer += 1.1
            dx, dy = self._toward(self._wizard, self._pit_fiend)
            for spread in (-0.16, 0.0, 0.16):
                angle = math.atan2(dy, dx) + spread
                tick.projectiles.append(BattleProjectile(
                    self._wizard.center_x, self._wizard.center_y,
                    math.cos(angle), math.sin(angle), "bolt",
                ))
            self._wizard.attack_flash = config.BATTLE_ATTACK_FLASH

        self._fighter_timer -= dt
        if self._fighter_timer <= 0.0:
            self._fighter_timer += 1.25
            self._fighter.attack_flash = config.BATTLE_ATTACK_FLASH

        self._fiend_timer -= dt
        while self._fiend_timer <= 0.0:
            self._fiend_timer += 1.7
            targets = (self._fighter, self._wizard, self._ranger)
            target = targets[self._fiend_target]
            self._fiend_target = (self._fiend_target + 1) % len(targets)
            dx, dy = self._toward(self._pit_fiend, target)
            tick.projectiles.append(BattleProjectile(
                self._pit_fiend.center_x, self._pit_fiend.center_y,
                dx, dy, "ray",
            ))
            self._pit_fiend.attack_flash = config.BATTLE_ATTACK_FLASH

        return tick

    def slash_hitbox(self):
        # The fighter's engagement is part of the distant tableau. Unlike
        # the cramped sanctum slash, it does not create an invisible hazard.
        return None


class InfernalAstralCorruption:
    """Timed Astral blocks that close around the fortress battle.

    The first wave is an unjumpable two-row seal behind Chuck. Later waves
    arrive from alternating sides of the upper yard. The center remains a
    deliberate survival spine until the separate Feywild-river slice exists.
    """

    _WAVE_RECTS = (
        ((4, 18, 8, 3), (36, 18, 8, 3)),
        ((6, 14, 9, 3), (33, 14, 9, 3)),
        ((3, 10, 8, 3), (37, 10, 8, 3),
         (13, 12, 4, 4), (31, 11, 4, 4)),
        # The final choke consumes the temporary central refuge. By then the
        # moving Feywild river is present: boarding it is the only answer.
        ((21, 10, 7, 13),),
    )

    def __init__(self, tilemap) -> None:
        self._tilemap = tilemap
        self.triggered = False
        self.elapsed = 0.0
        self.wave_index = 0
        self._pending: list[list] = []
        self._restore: list[tuple[int, int, str]] = []
        self._forced_cells: set[tuple[int, int]] = set()
        self.flashes: list[list] = []
        ts = config.TILE_SIZE
        self._protected = {
            (int(cx // ts), int(cy // ts))
            for _kind, (cx, cy) in tilemap.object_spawns
        }

    def trigger(self, player_tile: tuple[int, int]) -> None:
        if self.triggered:
            return
        self.triggered = True
        player_col, _player_row = player_tile
        cells = (
            (col, row)
            for row in config.INFERNAL_CORRUPTION_SEAL_ROWS
            for col in range(self._tilemap.width_tiles)
        )
        self._queue(cells, lambda col, _row: abs(col - player_col) * 0.025)

    def _queue(self, cells, delay_for, *, forced: bool = False) -> None:
        for col, row in cells:
            if (col, row) in self._protected:
                continue
            if self._tilemap.terrain_at(col, row) not in {"·", "≡"}:
                continue
            self._pending.append([delay_for(col, row), col, row])
            if forced:
                self._forced_cells.add((col, row))
        self._pending.sort()

    def _queue_wave(self, wave_index: int) -> None:
        rects = self._WAVE_RECTS[wave_index]
        cells = []
        for left, top, width, height in rects:
            for row in range(top, top + height):
                for col in range(left, left + width):
                    # This vertical spine is the readable temporary refuge.
                    if wave_index < 3 and 21 <= col <= 27:
                        continue
                    # Deterministic missing cells break the later incursions
                    # into jagged wrong-map fragments rather than clean
                    # rectangles. The initial retreat seal stays continuous.
                    if (
                        wave_index < 3
                        and (col * 7 + row * 11 + wave_index * 3) % 6 == 0
                    ):
                        continue
                    cells.append((col, row))
        self._queue(
            cells,
            lambda col, row: (abs(col - 24) + abs(row - 16)) * 0.018,
            forced=wave_index == 3,
        )

    def update(self, dt: float, player_hitbox=None) -> None:
        if not self.triggered:
            return
        self.elapsed += dt
        while (
            self.wave_index < len(config.INFERNAL_CORRUPTION_WAVE_TIMES)
            and self.elapsed >= config.INFERNAL_CORRUPTION_WAVE_TIMES[
                self.wave_index
            ]
        ):
            self._queue_wave(self.wave_index)
            self.wave_index += 1

        for flash in self.flashes:
            flash[2] += dt
        self.flashes = [f for f in self.flashes if f[2] < config.BREACH_FLASH]

        import pygame

        remaining = []
        for entry in self._pending:
            entry[0] -= dt
            _delay, col, row = entry
            if entry[0] > 0.0:
                remaining.append(entry)
                continue
            ts = config.TILE_SIZE
            cell = pygame.Rect(col * ts, row * ts, ts, ts)
            if player_hitbox is not None and cell.colliderect(player_hitbox):
                force_ready = (
                    (col, row) in self._forced_cells
                    and self.elapsed
                    >= config.INFERNAL_CORRUPTION_WAVE_TIMES[-1] + 2.5
                )
                if not force_ready:
                    remaining.append(entry)
                    continue
            old = self._tilemap.set_terrain(col, row, "V")
            self._restore.append((col, row, old))
            self.flashes.append([col, row, 0.0])
        self._pending = remaining

    def restore(self) -> None:
        for col, row, char in reversed(self._restore):
            self._tilemap.set_terrain(col, row, char)
        self.triggered = False
        self.elapsed = 0.0
        self.wave_index = 0
        self._pending = []
        self._restore = []
        self._forced_cells = set()
        self.flashes = []

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        ts = config.TILE_SIZE
        for col, row, age in self.flashes:
            fade = 1.0 - age / config.BREACH_FLASH
            pad = round(3 * (1.0 - fade))
            color = (round(150 + 90 * fade), round(160 + 86 * fade), 255)
            pygame.draw.rect(
                surface, color,
                (col * ts + pad - ox, row * ts + pad - oy,
                 ts - 2 * pad, ts - 2 * pad),
            )


@dataclass
class FeywildRiverBlock:
    x: float
    y: float

    @property
    def rect(self):
        import pygame

        return pygame.Rect(
            round(self.x), round(self.y),
            config.FEYWILD_RIVER_BLOCK_W,
            config.FEYWILD_RIVER_BLOCK_H,
        )


class FeywildRiverField:
    """Hard-edged river fragments flowing west through the Hell arena."""

    _SPACING = 144

    def __init__(self, map_width_px: int) -> None:
        self.map_width_px = map_width_px
        self.active = False
        self.time = 0.0
        self.blocks: list[FeywildRiverBlock] = []

    def activate(self) -> None:
        if self.active:
            return
        self.active = True
        # Two nearby lanes cross the central survival spine. Staggered east
        # starts make the intrusion build instead of appearing all at once.
        rows = (15, 18, 15, 18)
        self.blocks = [
            FeywildRiverBlock(
                self.map_width_px - config.FEYWILD_RIVER_BLOCK_W
                + index * self._SPACING,
                row * config.TILE_SIZE,
            )
            for index, row in enumerate(rows)
        ]

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.time += dt
        for block in self.blocks:
            block.x -= config.FEYWILD_RIVER_SPEED * dt
        for block in self.blocks:
            if block.x + config.FEYWILD_RIVER_BLOCK_W >= 0:
                continue
            rightmost = max(other.x for other in self.blocks)
            block.x = rightmost + self._SPACING

    def overlaps(self, hitbox) -> bool:
        return self.active and any(
            block.rect.colliderect(hitbox) for block in self.blocks
        )

    def reset(self) -> None:
        self.active = False
        self.time = 0.0
        self.blocks = []

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        if not self.active:
            return
        import pygame

        ox, oy = camera_offset
        deep = (18, 66, 78)
        water = (35, 132, 142)
        bright = (112, 226, 194)
        green = (44, 104, 82)
        phase = int(self.time * 8)
        for index, block in enumerate(self.blocks):
            rect = block.rect.move(-ox, -oy)
            pygame.draw.rect(surface, deep, rect)
            pygame.draw.rect(surface, green, (rect.x, rect.y, rect.w, 2))
            pygame.draw.rect(
                surface, green, (rect.x, rect.bottom - 2, rect.w, 2)
            )
            for x in range(rect.x - 8, rect.right + 8, 12):
                wave_x = x - ((phase + index * 3) % 12)
                pygame.draw.line(
                    surface, water,
                    (wave_x, rect.y + 5), (wave_x + 7, rect.y + 5), 2,
                )
                pygame.draw.line(
                    surface, bright,
                    (wave_x + 4, rect.y + 10),
                    (wave_x + 9, rect.y + 10),
                )


class AstralBreach:
    """The Astral Sea seals the hall once Chuck has seen the battle.

    When Chuck walks west of BREACH_TRIGGER_COL — into sight of the
    fight — the floor behind him breaks through to the Astral Sea in a
    two-tile-thick north-south band ('V' terrain: lethal to walk into,
    unjumpable at this thickness, uncrossable by enemies). The band
    lands instantly across the rows nearest Chuck so it cannot be
    outrun, then cascades outward to the walls with a flash per tile.
    There is no going back: only the battle, and whatever ends it.
    Restored whenever the room resets, so death re-arms the trigger.
    """

    def __init__(self, tilemap) -> None:
        self._tilemap = tilemap
        self.triggered = False
        self._pending: list[list] = []   # [delay, col, row]
        self._restore: list[tuple[int, int, str]] = []
        self.flashes: list[list] = []    # [col, row, age]

    def trigger(self, player_tile: tuple[int, int]) -> None:
        if self.triggered:
            return
        self.triggered = True
        _col, player_row = player_tile
        for col in config.BREACH_COLS:
            for row in range(self._tilemap.height_tiles):
                if self._tilemap.terrain_at(col, row) not in {"·", "≡"}:
                    continue  # walls, monuments, dressing keep their place
                spread = max(0, abs(row - player_row)
                             - config.BREACH_INSTANT_RADIUS)
                self._pending.append([spread * config.BREACH_STEP, col, row])
        self._pending.sort()

    def update(self, dt: float, player_hitbox=None) -> None:
        for flash in self.flashes:
            flash[2] += dt
        self.flashes = [f for f in self.flashes if f[2] < config.BREACH_FLASH]
        if not self._pending:
            return
        import pygame

        remaining = []
        for entry in self._pending:
            entry[0] -= dt
            _delay, col, row = entry
            if entry[0] > 0.0:
                remaining.append(entry)
                continue
            ts = config.TILE_SIZE
            cell = pygame.Rect(col * ts, row * ts, ts, ts)
            if player_hitbox is not None and cell.colliderect(player_hitbox):
                remaining.append(entry)  # never break through under Chuck
                continue
            old = self._tilemap.set_terrain(col, row, "V")
            self._restore.append((col, row, old))
            self.flashes.append([col, row, 0.0])
        self._pending = remaining

    def restore(self) -> None:
        """Heal the floor and re-arm the trigger (the room reset)."""
        for col, row, char in reversed(self._restore):
            self._tilemap.set_terrain(col, row, char)
        self._restore = []
        self._pending = []
        self.flashes = []
        self.triggered = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        ts = config.TILE_SIZE
        for col, row, age in self.flashes:
            fade = 1.0 - age / config.BREACH_FLASH
            pad = round(3 * (1.0 - fade))
            color = (round(150 + 90 * fade), round(160 + 86 * fade), 255)
            pygame.draw.rect(
                surface, color,
                (col * ts + pad - ox, row * ts + pad - oy,
                 ts - 2 * pad, ts - 2 * pad))
