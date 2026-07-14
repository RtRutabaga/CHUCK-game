"""Phase 2 scratch attack and ordinary-rat tutorial tests."""

import pygame

from src.core import config
from src.entities.player import Player
from src.entities.rat import SewerRat
from src.systems.combat import scratch_first_target
from src.world.tilemap import TileMap


class FakeInput:
    def __init__(self):
        self.pressed = set()

    def was_pressed(self, action):
        return action in self.pressed

    def movement_vector(self):
        return (0.0, 0.0)


def test_f_starts_a_brief_stationary_scratch() -> None:
    controls = FakeInput()
    player = Player(20, 20, controls)
    player.facing = "down"
    controls.pressed.add("scratch")
    player.update(0.01)
    assert player.scratch_just_started and player.scratching
    assert not player.moving
    assert player.scratch_hitbox().top == player.hitbox.bottom
    early = player.scratch_progress
    controls.pressed.clear()
    player.update(0.08)
    assert player.scratch_progress > early


def test_one_swipe_defeats_only_one_rat() -> None:
    first = SewerRat(24, 36)
    second = SewerRat(24, 36)
    hit = pygame.Rect(16, 28, 16, 16)
    assert scratch_first_target(hit, [first, second])
    assert not first.alive and second.alive


def test_rat_is_smaller_than_chuck_and_dies_in_one_hit() -> None:
    rat = SewerRat(20, 20)
    assert config.RAT_FRAME_W < config.CHUCK_FRAME_W
    assert config.RAT_FRAME_H < config.CHUCK_FRAME_H
    assert rat.width < config.PLAYER_HITBOX_W
    rat.on_scratched()
    assert not rat.alive


def test_sewer_has_three_rats_in_a_one_tile_choke_after_gap() -> None:
    m = TileMap(config.MAPS_DIR / "sewer.txt")
    rats = [(int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
            for kind, (x, y) in m.object_spawns if kind == "rat"]
    assert rats == [(10, 22), (10, 23), (10, 24)]
    for col, row in rats:
        assert not m.is_solid(col, row)
        assert m.is_solid(col - 1, row) and m.is_solid(col + 1, row)


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All combat tests passed.")


if __name__ == "__main__":
    _run_all()
