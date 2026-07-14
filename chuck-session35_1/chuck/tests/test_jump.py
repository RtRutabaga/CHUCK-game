"""Phase 2 jump: committed movement and Astral-only clearance."""

import tempfile
from pathlib import Path

from src.core import config
from src.entities.player import Player
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


def test_walking_cannot_enter_astral_void() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n#V#\n#.#\n###\n")
    controls.movement_vector = lambda: (0.0, 1.0)
    player.update(0.2)
    assert player.y == 2 * config.TILE_SIZE - player.height


def test_jump_does_not_clear_normal_walls() -> None:
    controls = FakeInput()
    player = Player(19.0, 20.0, controls)
    player.tilemap = _map("###\n#.#\n###\n#.#\n###\n")
    player.facing = "down"
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert player.y == 2 * config.TILE_SIZE - player.height


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
