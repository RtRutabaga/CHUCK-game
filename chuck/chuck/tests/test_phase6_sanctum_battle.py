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
    skeletons = {(int(x // ts), int(y // ts))
                 for kind, (x, y) in tilemap.object_spawns
                 if kind == "skeleton"}
    fighter = next((int(x // ts), int(y // ts))
                   for kind, (x, y) in tilemap.object_spawns
                   if kind == "battle:fighter")
    beholder = next((int(x // ts), int(y // ts))
                    for kind, (x, y) in tilemap.object_spawns
                    if kind == "battle:beholder")
    # Three stand in the fighter's rows, between him and the beholder.
    pressing = {(13, 20), (13, 26), (15, 18)}
    assert pressing <= skeletons
    for col, row in pressing:
        assert beholder[0] <= col <= fighter[0], (col, row)


def test_wall_skeletons_line_the_fringes_and_spare_the_sight_line() -> None:
    tilemap = TileMap(config.MAPS_DIR / "temple_sanctum.txt")
    ts = config.TILE_SIZE
    skeletons = [(int(x // ts), int(y // ts))
                 for kind, (x, y) in tilemap.object_spawns
                 if kind == "skeleton"]
    assert len(skeletons) == 27
    # All stay west of the seal, so they never wall off the aisle Chuck
    # enters by, and never end up on the battle's east side.
    assert all(col < config.BREACH_COLS[0] for col, _row in skeletons)
    fringe = [(c, r) for c, r in skeletons if r <= 8 or r >= 40]
    assert len(fringe) == 24  # the wall lines
    # The central sight-line to the beholder and trio stays clear: no
    # wall skeleton stands across the rows where the fight is fought.
    assert not any(14 <= r <= 30 for c, r in fringe)
    # They line BOTH walls, herding Chuck away from either fringe.
    assert any(r <= 8 for _c, r in fringe)
    assert any(r >= 40 for _c, r in fringe)


def test_entrance_cuts_the_camera_to_the_battle_then_back_to_chuck() -> None:
    import pygame

    from src.scenes.dialogue_scene import DialogueScene

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        scene._arrival_fade_t = None
        scene.player.x = 3 * config.TILE_SIZE + 3
        scene.player.y = 25 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_sanctum"
        scene._arrival_fade_t = None
        scene.update(0.01)  # consume entrance dialogue -> establishing shot
        assert isinstance(game.scenes.current, DialogueScene)

        ox, oy = scene.camera.offset
        view = pygame.Rect(ox, oy, config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
        # Every combatant is framed; the trio's feet clear the dialogue
        # panel (the bottom ~46px), so their lines land on them.
        panel_top = config.NATIVE_HEIGHT - 46
        for actor in scene.battle_actors:
            box = pygame.Rect(int(actor.x), int(actor.y),
                              actor.width, actor.height)
            assert view.colliderect(box), actor.kind
            if actor.kind != "beholder":
                assert (actor.y + actor.height) - oy <= panel_top, actor.kind
        # The camera has LEFT Chuck at the far-east door: he is off-screen.
        player = pygame.Rect(int(scene.player.x), int(scene.player.y),
                             scene.player.width, scene.player.height)
        assert not view.colliderect(player)

        # Play through the lines; the camera returns to Chuck.
        for _ in range(6):
            game.input.begin_frame()
            game.input._actions_just_pressed.add("interact")
            game.scenes.update(0.01)
            game.scenes.update(0.3)
        assert game.scenes.current is scene
        scene.update(0.01)
        ox, oy = scene.camera.offset
        view = pygame.Rect(ox, oy, config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
        player = pygame.Rect(int(scene.player.x), int(scene.player.y),
                             scene.player.width, scene.player.height)
        assert view.colliderect(player)
    finally:
        game._shutdown()


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
        assert len(scene.undead) == 27  # every skeleton re-forms
    finally:
        game._shutdown()


def _walk_to(scene, col: int, row: int) -> None:
    scene.player.x = col * config.TILE_SIZE + 3
    scene.player.y = row * config.TILE_SIZE + 4


def test_the_astral_sea_seals_the_hall_behind_chuck() -> None:
    from collections import deque

    from src.world.collision import FALL_HAZARD_TERRAIN

    game = Game()
    try:
        scene = _sanctum_scene(game)
        assert scene.breach is not None and not scene.breach.triggered
        # Walking the aisle to the trigger column breaks reality open.
        _walk_to(scene, config.BREACH_TRIGGER_COL, 23)
        scene.update(0.01)
        assert scene.breach.triggered
        for _ in range(40):
            scene.update(0.05)  # the cascade reaches both walls
        barrier = [(col, row)
                   for col in config.BREACH_COLS
                   for row in range(scene.tilemap.height_tiles)
                   if scene.tilemap.terrain_at(col, row) == "V"]
        assert len(barrier) >= 60  # a band, not a scatter
        # On foot (fall hazards lethal), the east door is unreachable:
        # Chuck is sealed in with the battle.
        tilemap = scene.tilemap
        start = scene._player_tile()
        reached = {start}
        frontier = deque([start])
        while frontier:
            col, row = frontier.popleft()
            for nxt in ((col - 1, row), (col + 1, row),
                        (col, row - 1), (col, row + 1)):
                c, r = nxt
                if nxt in reached or tilemap.is_solid(c, r):
                    continue
                if tilemap.terrain_at(c, r) in FALL_HAZARD_TERRAIN:
                    continue
                reached.add(nxt)
                frontier.append(nxt)
        assert (56, 23) not in reached  # the arrival aisle is cut off
        # ...and a single jump cannot cross: the band is two tiles thick
        # everywhere it landed, so any hop lands in the Astral Sea.
        for col, row in barrier:
            partner = (config.BREACH_COLS[0]
                       if col == config.BREACH_COLS[1]
                       else config.BREACH_COLS[1])
            assert (scene.tilemap.terrain_at(partner, row) == "V"
                    or scene.tilemap.is_solid(partner, row)), (col, row)
        # The battle stays in sight: every actor is west of the seal.
        assert all(a.x < config.BREACH_COLS[0] * config.TILE_SIZE
                   for a in scene.battle_actors)
    finally:
        game._shutdown()


def test_the_breach_never_breaks_through_under_chuck() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        # Chuck parked ON the barrier line when the trigger is forced:
        # his tile must wait for him to move, never dropping him.
        _walk_to(scene, config.BREACH_COLS[0], 23)
        scene.breach.trigger((config.BREACH_TRIGGER_COL, 23))
        for _ in range(40):
            scene.breach.update(0.05, scene.player.hitbox)
        col, row = scene._player_tile()
        assert scene.tilemap.terrain_at(col, row) != "V"
        # The moment he steps off, reality takes the tile.
        _walk_to(scene, config.BREACH_TRIGGER_COL, 23)
        scene.breach.update(0.05, scene.player.hitbox)
        assert scene.tilemap.terrain_at(col, row) == "V"
    finally:
        game._shutdown()


def test_death_heals_the_breach_and_rearms_it() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        before = {(col, row): scene.tilemap.terrain_at(col, row)
                  for col in config.BREACH_COLS
                  for row in range(scene.tilemap.height_tiles)}
        _walk_to(scene, config.BREACH_TRIGGER_COL, 23)
        scene.update(0.01)
        for _ in range(40):
            scene.update(0.05)
        assert any(scene.tilemap.terrain_at(c, r) == "V"
                   for (c, r) in before)
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        after = {(col, row): scene.tilemap.terrain_at(col, row)
                 for (col, row) in before}
        assert after == before  # the floor healed with the room
        assert not scene.breach.triggered  # and the trigger re-armed
    finally:
        game._shutdown()


def test_no_breach_while_chuck_stays_out_of_sight() -> None:
    game = Game()
    try:
        scene = _sanctum_scene(game)
        for _ in range(20):
            scene.update(0.05)  # lingering at the arrival changes nothing
        assert not scene.breach.triggered
        assert all(scene.tilemap.terrain_at(col, row) != "V"
                   for col in config.BREACH_COLS
                   for row in range(scene.tilemap.height_tiles))
    finally:
        game._shutdown()


def test_the_battle_exists_only_in_the_sanctum() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        assert scene.battle is None
        assert scene.battle_projectiles == []
        assert scene.breach is None
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
