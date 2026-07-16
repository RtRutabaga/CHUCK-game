"""Massive Chult dinosaur scale, slow pursuit, combat, and placement."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.massive_dinosaur import MassiveDinosaur
from src.entities.player import Player
from src.entities.raptor import Raptor
from src.entities.undead import UndeadEnemy
from src.systems.combat import scratch_first_target
from src.world.tilemap import TileMap


class StillInput:
    def was_pressed(self, _action):
        return False

    def movement_vector(self):
        return (0.0, 0.0)


def _temporary_map(text: str) -> TileMap:
    file = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    )
    file.write(text)
    file.close()
    return TileMap(Path(file.name))


def test_dinosaur_is_massive_slow_and_scratchable() -> None:
    dinosaur = MassiveDinosaur(64, 48)
    raptor = Raptor(64, 48)
    zombie = UndeadEnemy(64, 48, "zombie")
    image = pygame.image.load(
        config.SPRITES_DIR / "hazards" / "massive_dinosaur.png"
    )
    assert image.get_size() == (
        config.DINOSAUR_FRAME_W * 3, config.DINOSAUR_FRAME_H * 2
    )
    assert config.DINOSAUR_FRAME_W > config.RAPTOR_FRAME_W
    assert config.DINOSAUR_FRAME_H >= config.CHUCK_FRAME_H * 4
    assert dinosaur.width > raptor.width
    assert dinosaur.height > raptor.height
    assert dinosaur.speed < zombie.speed

    attack = pygame.Rect(0, 0, 128, 96)
    for _ in range(dinosaur.max_scratches - 1):
        assert scratch_first_target(attack, [dinosaur])
        assert dinosaur.alive
    assert scratch_first_target(attack, [dinosaur])
    assert not dinosaur.alive


def test_dinosaur_pursues_slowly_and_respects_jungle_collision() -> None:
    tilemap = _temporary_map(
        "###############\n"
        "#......#......#\n"
        "#......#......#\n"
        "#......#......#\n"
        "###############\n"
    )
    player = Player(160, 30, StillInput())
    dinosaur = MassiveDinosaur(48, 40)
    dinosaur.tilemap = tilemap
    start = dinosaur.x
    dinosaur.update(0.5, player)
    assert dinosaur.x > start and dinosaur.moving
    assert dinosaur.x - start < config.ZOMBIE_SPEED * 0.5
    dinosaur.update(20.0, player)
    assert dinosaur.x + dinosaur.width <= 7 * config.TILE_SIZE


def test_one_dinosaur_has_a_large_avoidable_northern_clearing() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_cog.txt")
    spawns = [
        (int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE))
        for kind, (cx, cy) in tilemap.object_spawns
        if kind == "massive_dinosaur"
    ]
    assert spawns == [(40, 14)]
    assert all(
        not tilemap.is_solid(col, row)
        for row in range(12, 17)
        for col in range(36, 45)
    )

    # Even treating a four-tile envelope around its enormous body as blocked,
    # the player can circle it; entering notice range is allowed and safe
    # because its pursuit is intentionally slower than a zombie.
    radius_tiles = 4.0
    excluded = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if (col - 40) ** 2 + (row - 14) ** 2 <= radius_tiles ** 2
    }
    start = (40, 76)
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if (point not in reached and point not in excluded
                    and not tilemap.is_solid(*point)):
                reached.add(point)
                frontier.append(point)
    assert (40, 4) in reached


def test_dinosaur_damage_and_reset_use_existing_enemy_lifecycle() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_2")
        assert len(scene.dinosaurs) == 1
        original = scene.dinosaurs[0]
        original.speed = 0.0
        scene.player.x, scene.player.y = original.x, original.y
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == before - original.damage

        original.alive = False
        scene.dinosaurs = []
        scene._begin_respawn()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert len(scene.dinosaurs) == 1
        assert scene.dinosaurs[0] is not original
        assert scene.dinosaurs[0].alive
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All massive Chult dinosaur tests passed.")


if __name__ == "__main__":
    _run_all()
