"""Finite, authored undead releases for pressure-run maps."""

from __future__ import annotations

from collections import defaultdict


STAGED_UNDEAD_PREFIX = "staged_undead:"

# Crossing these rows while moving north releases the matching authored group.
# Spawns themselves remain map markers so openings and enemy origins stay in
# one inspectable source of truth.
RELEASE_ROWS: dict[str, dict[int, int]] = {
    "chult_run": {1: 27, 2: 20, 3: 13},
}

Spawn = tuple[str, tuple[float, float]]


def is_staged_undead(kind: str) -> bool:
    return kind.startswith(STAGED_UNDEAD_PREFIX)


class UndeadReleaseController:
    """Release finite marker-authored groups once, then reset on return."""

    def __init__(self, map_name: str, marker_spawns: list[Spawn]) -> None:
        self.map_name = map_name
        self._release_rows = RELEASE_ROWS.get(map_name, {})
        self._groups: dict[int, list[Spawn]] = defaultdict(list)
        self._released: set[int] = set()

        for marker_kind, position in marker_spawns:
            if not is_staged_undead(marker_kind):
                continue
            parts = marker_kind.split(":")
            if len(parts) != 3:
                raise ValueError(f"Invalid staged undead marker {marker_kind!r}")
            _prefix, group_text, enemy_kind = parts
            group = int(group_text)
            if group not in self._release_rows:
                raise ValueError(
                    f"No release row for group {group} on map {map_name!r}"
                )
            if enemy_kind not in {"zombie", "skeleton"}:
                raise ValueError(f"Invalid staged enemy {enemy_kind!r}")
            self._groups[group].append((enemy_kind, position))

    @property
    def total_count(self) -> int:
        return sum(len(spawns) for spawns in self._groups.values())

    @property
    def released_groups(self) -> frozenset[int]:
        return frozenset(self._released)

    def release_for_row(self, player_row: int) -> list[Spawn]:
        released: list[Spawn] = []
        for group, threshold in sorted(self._release_rows.items()):
            if (group in self._groups and group not in self._released
                    and player_row <= threshold):
                self._released.add(group)
                released.extend(self._groups[group])
        return released

    def reset(self) -> None:
        self._released.clear()
