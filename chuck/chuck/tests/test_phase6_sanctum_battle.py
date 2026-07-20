"""The sanctum battle in motion (session 132).

The tableau fights: beholder eye rays cycle the adventurers' three
lanes and dissipate at range, ranger arrows and wizard bolts streak
west at the beholder, the fighter's slash pulses where three skeletons
press him. Every attack is a timed hazard Chuck must dodge; he cannot
influence the battle, and survival is the room's only objective.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.battle_hazards import BattleChoreographer, BattleProjectile
from src.scenes.dialogue_scene import DialogueScene
from src.world.tilemap import TileMap


def _sanctum_scene(game):
    scene = game.checkpoints.load_checkpoint("temple_9")
    scene._arrival_fade_t = None
    scene._pending_entrance_dialogue = None  # the tableau suite's concern
    return scene


def test_three_skeletons_press_the_fighters_line() -> None:
    tilemap = TileMap(config.MAPS_DIR / "temple_sanctum.txt")
    ts = config.TILE_SIZE
    skeletons = sorted(
        (int(x // ts), int(y // ts))
        for kind, (x, y) in tilemap.object_spawns if kind == "skeleton")
    assert skeletons == [(13, 20), (13, 26), (15, 18)]
    fighter = next((int(x // ts), int(y // ts))
                   for kind, (x, y) in tilemap.object_spawns
                   if kind == "battle:fighter")
    beholder = next((int(x // ts), int(y // ts))
                    for kind, (x, y) in tilemap.object_spawns
                    if kind == "battle:beholder")
    # They press the fighter from the west: between him and the beholder.
    for col, row in skeletons:
        assert beholder[0] <= col <= fighter[0], (col, row)


def test_the_choreographer_fires_every_attack_on_cadence() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        assert scene.battle is not None
        seen: set[str] = set()
        slash_seen = False
        # Park Chuck at the arrival, far outside every hazard.
        for _ in range(int(6.0 / 0.05)):
            scene.update(0.05)
            seen.update(s.kind for s in scene.battle_projectiles)
            slash_seen = slash_seen or (
                scene.battle.slash_hitbox() is not None)
        assert seen == {"ray", "arrow", "bolt"}
        assert slash_seen
        # Rays fly east from the beholder; arrows and bolts fly west.
        directions = {s.kind: s.direction for s in scene.battle_projectiles}
        for kind, expected in (("ray", 1), ("arrow", -1), ("bolt", -1)):
            if kind in directions:
                assert directions[kind] == expected, kind
        # The arrival aisle stays survivable: rays dissipate at range,
        # long before the east door where Chuck walks in.
        assert all(s.x < 40 * config.TILE_SIZE
                   for s in scene.battle_projectiles)
    finally:
        game._shutdown()


def test_projectiles_die_on_masonry_and_at_range() -> None:
    tilemap = TileMap(config.MAPS_DIR / "temple_sanctum.txt")
    ts = config.TILE_SIZE
    arrow = BattleProjectile(9 * ts, 15 * ts + 8, -1, "arrow")
    for _ in range(200):
        arrow.update(0.05, tilemap)
        if not arrow.alive:
            break
    assert not arrow.alive  # the west wall stopped it
    assert arrow.x > 4 * ts  # inside the hall, not out of bounds
    ray = BattleProjectile(13 * ts, 23 * ts + 8, 1, "ray")
    traveled_from = ray.x
    for _ in range(400):
        ray.update(0.05, tilemap)
        if not ray.alive:
            break
    assert not ray.alive
    # It dissipated at its authored range on open floor, not at a wall.
    assert (ray.x - traveled_from) <= config.BATTLE_RAY_RANGE + ts


def test_a_hit_costs_sanity_once_and_spends_the_shot() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        before = scene.sanity.current
        shot = BattleProjectile(
            scene.player.hitbox.centerx, scene.player.hitbox.centery,
            1, "ray")
        scene.battle_projectiles.append(shot)
        scene.update(0.01)
        assert scene.sanity.current == before - config.BATTLE_RAY_SANITY_DAMAGE
        assert not shot.alive
        assert shot not in scene.battle_projectiles
        # Invulnerability frames: an immediate second shot cannot land.
        second = BattleProjectile(
            scene.player.hitbox.centerx, scene.player.hitbox.centery,
            1, "bolt")
        scene.battle_projectiles.append(second)
        scene.update(0.01)
        assert scene.sanity.current == before - config.BATTLE_RAY_SANITY_DAMAGE
    finally:
        game._shutdown()


def test_the_fighters_slash_reaches_west_and_wounds_chuck() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        fighter = next(a for a in scene.battle_actors if a.kind == "fighter")
        choreo = BattleChoreographer(scene.battle_actors)
        choreo._slash_timer = 0.0
        choreo.update(0.01)
        zone = choreo.slash_hitbox()
        assert zone is not None
        assert zone.right <= int(fighter.x)  # the arc sweeps west
        assert fighter.attack_flash > 0.0
        # A slash landing on Chuck costs sanity through the scene.
        scene.battle._slash_timer = 0.0
        scene.battle.update(0.01)
        live = scene.battle.slash_hitbox()
        scene.player.x = live.centerx - scene.player.width / 2
        scene.player.y = live.centery - scene.player.height / 2
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == (
            before - config.BATTLE_SLASH_SANITY_DAMAGE)
    finally:
        game._shutdown()


def test_death_resets_the_battle_with_the_room() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        for _ in range(60):
            scene.update(0.05)
        assert scene.battle_projectiles  # the air is full of shots
        old_battle = scene.battle
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert scene.battle_projectiles == []
        assert scene.battle is not old_battle  # cadences restart
        assert len(scene.undead) == 3  # the skeletons re-press the line
    finally:
        game._shutdown()


def test_the_battle_exists_only_in_the_sanctum() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        assert scene.battle is None
        assert scene.battle_projectiles == []
    finally:
        game._shutdown()


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
    print("All sanctum battle tests passed.")


if __name__ == "__main__":
    _run_all()
