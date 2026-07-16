"""Phase 5 raptor pursuit, combat, placement, and avoidance coverage."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
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


def test_raptor_is_large_fast_dangerous_and_scratchable() -> None:
    raptor = Raptor(40, 40)
    skeleton = UndeadEnemy(40, 40, "skeleton")
    image = pygame.image.load(config.SPRITES_DIR / "hazards" / "raptor.png")
    assert image.get_size() == (
        config.RAPTOR_FRAME_W * 3, config.RAPTOR_FRAME_H * 2
    )
    assert config.RAPTOR_FRAME_W > config.CHUCK_FRAME_W * 2
    assert config.RAPTOR_FRAME_H > config.CHUCK_FRAME_H
    assert raptor.width > config.PLAYER_HITBOX_W
    assert raptor.height > config.PLAYER_HITBOX_H
    assert skeleton.speed < raptor.speed < config.PLAYER_SPEED
    assert raptor.damage > skeleton.damage

    attack = pygame.Rect(0, 0, 80, 80)
    for _ in range(raptor.max_scratches - 1):
        assert scratch_first_target(attack, [raptor])
        assert raptor.alive
    assert scratch_first_target(attack, [raptor])
    assert not raptor.alive


def test_raptor_pursues_directly_and_respects_jungle_collision() -> None:
    tilemap = _temporary_map(
        "#########\n"
        "#...#...#\n"
        "#...#...#\n"
        "#########\n"
    )
    player = Player(104, 24, StillInput())
    raptor = Raptor(32, 32)
    raptor.tilemap = tilemap
    start = raptor.x
    raptor.update(0.25, player)
    assert raptor.x > start and raptor.moving
    raptor.update(10.0, player)
    assert raptor.x + raptor.width <= 4 * config.TILE_SIZE


def test_exactly_two_raptors_are_spaced_in_broad_avoidable_territory() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_cog.txt")
    spawns = [
        (int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE))
        for kind, (cx, cy) in tilemap.object_spawns
        if kind == "raptor"
    ]
    assert spawns == [(30, 38), (50, 38)]
    assert abs(spawns[1][0] - spawns[0][0]) >= 16
    for col, row in spawns:
        open_neighbors = sum(
            not tilemap.is_solid(col + dx, row + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        )
        assert open_neighbors == 4

    # A route from the southern entry to the northern reserve remains even
    # when each raptor's full notice radius is treated as impassable territory.
    radius_tiles = config.RAPTOR_NOTICE_RANGE / config.TILE_SIZE
    excluded = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if any((col - rx) ** 2 + (row - ry) ** 2 <= radius_tiles ** 2
               for rx, ry in spawns)
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
    assert (40, 8) in reached


def test_raptors_damage_and_rebuild_after_sanity_return() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_2")
        assert len(scene.raptors) == 2
        originals = list(scene.raptors)
        raptor = scene.raptors[0]
        raptor.speed = 0.0
        scene.player.x, scene.player.y = raptor.x, raptor.y
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == before - raptor.damage

        for target in scene.raptors:
            target.alive = False
        scene.raptors = []
        scene._begin_respawn()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert len(scene.raptors) == 2
        assert all(new is not old for new in scene.raptors for old in originals)
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 raptor tests passed.")


if __name__ == "__main__":
    _run_all()
