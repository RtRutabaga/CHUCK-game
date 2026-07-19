"""Phase 4 zombie/skeleton durability, pursuit, contact, and reset."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.player import Player
from src.entities.undead import UndeadEnemy
from src.scenes.world_scene import WorldScene
from src.systems.combat import scratch_first_target
from src.world.tilemap import TileMap


class StillInput:
    def was_pressed(self, _action):
        return False

    def movement_vector(self):
        return (0.0, 0.0)


def _map(text: str) -> TileMap:
    file = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    )
    file.write(text)
    file.close()
    return TileMap(Path(file.name))


def test_undead_are_human_scale_and_take_many_scratches() -> None:
    zombie = UndeadEnemy(32, 32, "zombie")
    skeleton = UndeadEnemy(32, 32, "skeleton")
    assert config.UNDEAD_FRAME_W == config.NPC_FRAME_W
    assert config.UNDEAD_FRAME_H == config.NPC_FRAME_H
    assert (zombie.width, zombie.height) == (
        config.NPC_HITBOX_W, config.NPC_HITBOX_H
    )
    assert zombie.max_scratches == 8 and skeleton.max_scratches == 6

    attack = pygame.Rect(0, 0, 64, 64)
    for _ in range(zombie.max_scratches - 1):
        assert scratch_first_target(attack, [zombie])
        assert zombie.alive
    assert scratch_first_target(attack, [zombie])
    assert not zombie.alive


def test_undead_pursue_slowly_and_respect_jungle_collision() -> None:
    tilemap = _map("#######\n#..#..#\n#######\n")
    player = Player(72, 20, StillInput())
    zombie = UndeadEnemy(24, 24, "zombie")
    zombie.tilemap = tilemap
    start = zombie.x
    zombie.update(1.0, player)
    assert zombie.x > start
    zombie.update(10.0, player)
    assert zombie.x + zombie.width <= 3 * config.TILE_SIZE


def test_undead_never_cross_fall_hazards() -> None:
    """Session 127: fall hazards are walkable for Chuck (the fall system
    owns the consequence) but enemies have no fall choreography — their
    movement treats spikes, Astral cells, and sky as walls, so a
    skeleton can never stroll across a spike pit toward Chuck."""
    for hazard in ("♠", "V"):
        tilemap = _map("#######\n#." + hazard + "..#\n#######\n")
        player = Player(72, 20, StillInput())
        skeleton = UndeadEnemy(20, 24, "skeleton")
        skeleton.tilemap = tilemap
        start = skeleton.x
        skeleton.update(1.0, player)
        assert skeleton.x >= start  # pursuit engaged eastward
        skeleton.update(10.0, player)
        # Stopped flush against the hazard column, never on or past it.
        assert skeleton.x + skeleton.width <= 2 * config.TILE_SIZE + 0.01


def test_chult_encounter_is_spaced_and_avoidable() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    spawns = [
        (kind, int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE))
        for kind, (cx, cy) in tilemap.object_spawns
        if kind in {"zombie", "skeleton"}
    ]
    assert [kind for kind, _col, _row in spawns].count("zombie") == 2
    assert [kind for kind, _col, _row in spawns].count("skeleton") == 2
    for _kind, col, row in spawns:
        # Every encounter sits in a broad clearing, never a mandatory choke.
        open_neighbors = sum(
            not tilemap.is_solid(col + dx, row + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        )
        assert open_neighbors >= 3


def test_chult_undead_damage_and_reset_with_respawn() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "chult_jungle"))
        scene = game.scenes.current
        assert len(scene.undead) == 4
        original = list(scene.undead)
        enemy = scene.undead[0]
        enemy.speed = 0.0
        scene.player.x, scene.player.y = enemy.x, enemy.y
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == before - enemy.damage

        for target in scene.undead:
            target.alive = False
        scene.undead = []
        scene._begin_respawn()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert len(scene.undead) == 4
        assert all(enemy.alive for enemy in scene.undead)
        assert all(new is not old for new in scene.undead for old in original)
    finally:
        game._shutdown()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Chult undead tests passed.")


if __name__ == "__main__":
    _run_all()
