"""Authored, map-local vegetation changes driven by Feywild flowers."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from src.core import config


_SWITCH_PREFIX = "flower_switch:"
_OPEN_PREFIX = "flower_open:"
_CLOSE_PREFIX = "flower_close:"


@dataclass(frozen=True)
class _Target:
    col: int
    row: int
    original: str


@dataclass
class _Group:
    opens: tuple[_Target, ...]
    closes: tuple[_Target, ...]
    active: bool = False


class ReactiveFlowerController:
    """Toggle small, inspectable vegetation groups without durable state."""

    def __init__(self, tilemap, object_spawns) -> None:
        from src.entities.reactive_flower import ReactiveFlower

        self.tilemap = tilemap
        positions: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(
            lambda: {"switch": [], "open": [], "close": []}
        )
        for kind, position in object_spawns:
            for prefix, role in (
                (_SWITCH_PREFIX, "switch"),
                (_OPEN_PREFIX, "open"),
                (_CLOSE_PREFIX, "close"),
            ):
                if kind.startswith(prefix):
                    positions[kind[len(prefix):]][role].append(position)
                    break

        self.groups: dict[str, _Group] = {}
        self.flowers: list[ReactiveFlower] = []
        for group_id, authored in sorted(positions.items()):
            if not authored["switch"]:
                raise ValueError(
                    f"Reactive flower group {group_id!r} has no switch"
                )
            if not authored["open"] or not authored["close"]:
                raise ValueError(
                    f"Reactive flower group {group_id!r} must open and "
                    "close at least one authored tile"
                )
            opens = self._targets(authored["open"], expect_solid=True)
            closes = self._targets(authored["close"], expect_solid=False)
            self.groups[group_id] = _Group(opens=opens, closes=closes)
            for center_x, center_y in authored["switch"]:
                self.flowers.append(ReactiveFlower(
                    center_x,
                    center_y,
                    group_id,
                    lambda group_id=group_id: self.trigger(group_id),
                ))

        self._pending_group: str | None = None
        self._pending_t = 0.0
        self._flash_t = 0.0
        self._flash_tiles: tuple[tuple[int, int], ...] = ()

    def _targets(
        self,
        positions: list[tuple[float, float]],
        *,
        expect_solid: bool,
    ) -> tuple[_Target, ...]:
        targets = []
        for center_x, center_y in positions:
            col = int(center_x // config.TILE_SIZE)
            row = int(center_y // config.TILE_SIZE)
            if self.tilemap.is_solid(col, row) != expect_solid:
                state = "solid" if expect_solid else "walkable"
                raise ValueError(
                    f"Reactive flower target at {(col, row)} must begin {state}"
                )
            targets.append(
                _Target(col, row, self.tilemap.terrain_at(col, row))
            )
        return tuple(targets)

    def load_sprites(self, assets) -> None:
        for flower in self.flowers:
            flower.load_sprites(assets)

    def trigger(self, group_id: str) -> bool:
        """Begin one readable change; repeated scratches cannot stack it."""
        if group_id not in self.groups:
            raise ValueError(f"Unknown reactive flower group {group_id!r}")
        if self._pending_group is not None:
            return False
        self._pending_group = group_id
        self._pending_t = config.REACTIVE_FLOWER_CHANGE_DELAY
        return True

    def update(self, dt: float, player_hitbox) -> None:
        for flower in self.flowers:
            flower.update(dt)
        self._flash_t = max(0.0, self._flash_t - dt)
        if self._pending_group is None:
            return
        self._pending_t = max(0.0, self._pending_t - dt)
        if self._pending_t > 0.0:
            return

        group = self.groups[self._pending_group]
        targets = (*group.opens, *group.closes)
        if any(
            self._tile_rect(target.col, target.row).colliderect(player_hitbox)
            for target in targets
        ):
            return

        group.active = not group.active
        for target in group.opens:
            self.tilemap.set_terrain(
                target.col,
                target.row,
                "'" if group.active else target.original,
            )
        for target in group.closes:
            self.tilemap.set_terrain(
                target.col,
                target.row,
                "#" if group.active else target.original,
            )
        for flower in self.flowers:
            if flower.group_id == self._pending_group:
                flower.set_active(group.active)
        self._flash_tiles = tuple(
            (target.col, target.row) for target in targets
        )
        self._flash_t = config.REACTIVE_FLOWER_FLASH_DURATION
        self._pending_group = None

    @staticmethod
    def _tile_rect(col: int, row: int):
        import pygame

        size = config.TILE_SIZE
        return pygame.Rect(col * size, row * size, size, size)

    def reset(self) -> None:
        """Restore the authored initial state after death or map reload."""
        for group in self.groups.values():
            for target in (*group.opens, *group.closes):
                self.tilemap.set_terrain(
                    target.col, target.row, target.original
                )
            group.active = False
        for flower in self.flowers:
            flower.reset()
        self._pending_group = None
        self._pending_t = 0.0
        self._flash_t = 0.0
        self._flash_tiles = ()

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """Brief leaf-and-light flecks make the atomic route swap readable."""
        if self._flash_t <= 0.0:
            return
        import pygame

        ox, oy = camera_offset
        progress = 1.0 - self._flash_t / config.REACTIVE_FLOWER_FLASH_DURATION
        rise = round(progress * 7)
        colors = ((83, 229, 206), (188, 83, 246), (244, 111, 193))
        size = config.TILE_SIZE
        for index, (col, row) in enumerate(self._flash_tiles):
            center_x = col * size + size // 2 - ox
            center_y = row * size + size // 2 - oy
            color = colors[index % len(colors)]
            for offset_x, offset_y in ((-5, 1), (4, -3), (1, 5)):
                pygame.draw.rect(
                    surface,
                    color,
                    (
                        center_x + offset_x,
                        center_y + offset_y - rise,
                        2,
                        2,
                    ),
                )
