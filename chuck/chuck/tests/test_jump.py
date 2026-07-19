"""Phase 2 jump: committed movement and Astral-only clearance."""

import tempfile
from pathlib import Path

from src.core import config
from src.entities.player import Player
from src.systems.fall import fall_zone_kind, touches_astral_fall_zone
from src.world.tilemap import TileMap


class FakeInput:
    def __init__(self):
        self.press_jump = False

    def was_pressed(self, action):
        pressed = action == "jump" and self.press_jump
        self.press_jump = False
        return pressed

    def movement_vector(self):
        return (0.0, 0.0)


def _map(text: str) -> TileMap:
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                    encoding="utf-8")
    f.write(text)
    f.close()
    return TileMap(Path(f.name))


def test_jump_clears_one_astral_tile() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n#V#\n#.#\n###\n")
    player.facing = "down"
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert player.y > 3 * config.TILE_SIZE, player.y


def test_jump_start_is_a_one_frame_event() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    controls.press_jump = True
    player.update(0.01)
    assert player.jumping and player.jump_just_started
    player.update(0.01)
    assert player.jumping and not player.jump_just_started


def test_walking_into_astral_void_triggers_fall_zone() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n#V#\n#.#\n###\n")
    controls.movement_vector = lambda: (0.0, 1.0)
    player.update(0.2)
    assert player.y > 2 * config.TILE_SIZE - player.height
    assert touches_astral_fall_zone(player.tilemap, player.hitbox, airborne=False)


def test_airborne_chuck_is_safe_over_astral_void() -> None:
    controls = FakeInput()
    player = Player(19.0, 32.0, controls)
    player.tilemap = _map("###\n#.#\n#V#\n#.#\n###\n")
    assert not touches_astral_fall_zone(
        player.tilemap, player.hitbox, airborne=True
    )


def test_sky_and_astral_are_distinct_fall_materials() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    tilemap = _map("###\n#s#\n#V#\n###\n")
    assert fall_zone_kind(tilemap, player.hitbox, airborne=False) == "sky"
    player.y += config.TILE_SIZE
    assert fall_zone_kind(tilemap, player.hitbox, airborne=False) == "astral"
    assert fall_zone_kind(tilemap, player.hitbox, airborne=True) is None


def test_jump_does_not_clear_normal_walls() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n###\n#.#\n###\n")
    player.facing = "down"
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert player.y == 2 * config.TILE_SIZE - player.height


def test_jump_clears_one_jungle_stream_tile_but_walking_does_not() -> None:
    controls = FakeInput()
    controls.movement_vector = lambda: (0.0, 1.0)
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n#≈#\n#.#\n###\n")
    player.facing = "down"
    player.update(0.2)
    assert player.y == 2 * config.TILE_SIZE - player.height

    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert player.y > 3 * config.TILE_SIZE


def test_jump_clears_one_temple_spike_band_walking_means_falling() -> None:
    # Session 124: spikes are Astral-style fall hazards — walking is no
    # longer stopped by them, it walks Chuck into the fall; only the
    # committed jump crosses safely.
    from src.systems.fall import fall_zone_kind

    controls = FakeInput()
    controls.movement_vector = lambda: (0.0, -1.0)
    player = Player(19.0, 3 * config.TILE_SIZE + 4, controls)
    player.tilemap = _map("###\n#.#\n#♠#\n#.#\n###\n")
    player.facing = "up"
    player.update(0.2)  # one stride carries him onto the band
    assert player.y < 3 * config.TILE_SIZE  # nothing blocks the walk...
    assert fall_zone_kind(player.tilemap, player.hitbox,
                          airborne=False) == "astral"  # ...but it is death

    player = Player(19.0, 3 * config.TILE_SIZE + 4, controls)
    player.tilemap = _map("###\n#.#\n#♠#\n#.#\n###\n")
    player.facing = "up"
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert player.y < 2 * config.TILE_SIZE
    assert fall_zone_kind(player.tilemap, player.hitbox,
                          airborne=False) is None  # landed on safe floor


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
    print("All jump tests passed.")


if __name__ == "__main__":
    _run_all()
