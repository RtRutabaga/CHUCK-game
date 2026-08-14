"""Phase 2 scratch attack and ordinary-rat tutorial tests."""

import pygame
import tempfile
from pathlib import Path

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


def _map(text: str) -> TileMap:
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                    encoding="utf-8")
    f.write(text)
    f.close()
    return TileMap(Path(f.name))


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


def test_scratch_hits_a_small_enemy_overlapping_chuck() -> None:
    player = Player(20, 20, FakeInput())
    player.facing = "right"
    trapped_rat = SewerRat(player.hitbox.centerx, player.hitbox.centery)

    # The rat is inside Chuck and therefore behind the ordinary forward paw
    # reach.  This is the contact-pursuit case that used to pin the player.
    assert not player.scratch_hitbox().colliderect(trapped_rat.hitbox)
    assert scratch_first_target(
        player.scratch_hitbox(),
        [trapped_rat],
        overlap_box=player.hitbox,
        overlap_targets=[trapped_rat],
    )
    assert not trapped_rat.alive


def test_overlapping_enemy_takes_priority_without_hitting_two_targets() -> None:
    player = Player(20, 20, FakeInput())
    player.facing = "right"
    trapped_rat = SewerRat(player.hitbox.centerx, player.hitbox.centery)
    forward_rat = SewerRat(
        player.scratch_hitbox().centerx,
        player.scratch_hitbox().centery,
    )

    assert scratch_first_target(
        player.scratch_hitbox(),
        [forward_rat, trapped_rat],
        overlap_box=player.hitbox,
        overlap_targets=[trapped_rat, forward_rat],
    )
    assert not trapped_rat.alive
    assert forward_rat.alive


def test_rat_is_smaller_than_chuck_and_dies_in_one_hit() -> None:
    rat = SewerRat(20, 20)
    assert config.RAT_FRAME_W < config.CHUCK_FRAME_W
    assert config.RAT_FRAME_H < config.CHUCK_FRAME_H
    assert rat.width < config.PLAYER_HITBOX_W
    rat.on_scratched()
    assert not rat.alive


def test_rat_short_patrol_reverses_at_its_home_range() -> None:
    rat = SewerRat(40, 24)
    rat.configure_patrol(_map("#####\n#ddd#\n#####\n"))
    assert rat.patrolling
    start = rat.x
    rat.update(1.0)
    assert rat.x == start + config.RAT_PATROL_RANGE
    rat.update(0.25)
    assert rat.x < start + config.RAT_PATROL_RANGE


def test_rat_stays_put_beside_objects_fall_zones_or_other_rats() -> None:
    cases = [
        (_map("#####\n##dO#\n#####\n"), set()),
        (_map("#####\n#ddV#\n#####\n"), set()),
        (_map("#####\n#ddd#\n#####\n"), {(1, 1)}),
    ]
    for tilemap, blocked_spawns in cases:
        rat = SewerRat(40, 24)
        rat.configure_patrol(tilemap, blocked_spawns)
        start = rat.x
        rat.update(1.0)
        assert not rat.patrolling and rat.x == start


def test_attack_chase_rat_notices_pursues_and_respects_walls() -> None:
    class Target:
        x = 52
        y = 21
        width = config.PLAYER_HITBOX_W
        height = config.PLAYER_HITBOX_H

    rat = SewerRat(24, 24)
    rat.configure_attack_chase(_map("#####\n#ddd#\n#####\n"))
    start = rat.x
    rat.update(0.25, Target())
    assert rat.attack_chase_enabled and not rat.patrolling
    assert rat.x > start

    rat = SewerRat(24, 24)
    rat.configure_attack_chase(_map("#####\n#d#d#\n#####\n"))
    rat.update(1.0, Target())
    assert rat.x + rat.width <= 2 * config.TILE_SIZE

    far_target = Target()
    far_target.x = rat.x + config.HOLD_RAT_NOTICE_RANGE + 20
    before = (rat.x, rat.y)
    rat.update(0.25, far_target)
    assert (rat.x, rat.y) == before


def test_sewer_has_three_rats_in_a_one_tile_choke_after_gap() -> None:
    m = TileMap(config.MAPS_DIR / "sewer.txt")
    rats = [(int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
            for kind, (x, y) in m.object_spawns if kind == "rat"]
    choke_rats = [(col, row) for col, row in rats
                  if row in config.SEWER_RAT_ROWS]
    assert choke_rats == [(config.SEWER_RAT_COL, row)
                          for row in config.SEWER_RAT_ROWS]
    for col, row in choke_rats:
        assert not m.is_solid(col, row)
        assert m.is_solid(col - 1, row) and m.is_solid(col + 1, row)


def test_sewer_has_spaced_rats_through_the_late_astral_maze() -> None:
    m = TileMap(config.MAPS_DIR / "sewer.txt")
    rats = [(int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
            for kind, (x, y) in m.object_spawns if kind == "rat"]
    maze_rats = [(col, row) for col, row in rats
                 if row > max(config.SEWER_RAT_ROWS)]
    assert maze_rats == [(26, 43), (17, 52), (8, 61), (14, 68)]
    for col, row in maze_rats:
        assert m.terrain_at(col, row) == "d"
        assert not m.is_solid(col, row)


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
