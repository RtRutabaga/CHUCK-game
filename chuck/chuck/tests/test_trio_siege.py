"""The orcs' siege in the final encounter: archers, catapult, dragon."""

import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.battle_hazards import BattleProjectile
from src.entities.red_dragon import RedDragonFlyby
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems import orc_siege
from src.systems.orc_siege import (
    ARCHER_POSTS, ARCHERS_AT, CATAPULT_AFTER_BEAT, CATAPULT_FROM,
    CATAPULT_POST, ROCK_DAMAGE, Catapult, OrcSiege, RollingRock)
from src.systems.trio_encounter import BEATS, CHURN_FROM
from src.world import collision
from src.world.tilemap import TileMap

TS = config.TILE_SIZE
CLEAR_OF_IT = (46 * TS, 26 * TS)


def _open_floor(tilemap, col: int, row: int) -> bool:
    if not (0 <= col < tilemap.width_tiles and 0 <= row < tilemap.height_tiles):
        return True          # off the map edge, where they step in from
    if row in (0, tilemap.height_tiles - 1):
        return True          # the rim they step over
    return (not tilemap.is_solid(col, row)
            and tilemap.terrain_at(col, row)
            not in collision.FALL_HAZARD_TERRAIN)


def test_every_march_is_over_open_floor() -> None:
    tilemap = TileMap(config.MAPS_DIR / "desert_trio.txt")
    for entry, post in ARCHER_POSTS + ((CATAPULT_FROM, CATAPULT_POST),):
        assert entry[0] == post[0], (entry, post)   # straight lines
        step = 1 if post[1] > entry[1] else -1
        for row in range(entry[1], post[1] + step, step):
            assert _open_floor(tilemap, entry[0], row), (entry, row)
        assert not tilemap.is_solid(*post) and \
            tilemap.terrain_at(*post) not in collision.FALL_HAZARD_TERRAIN


def test_the_conversation_makes_room_for_it() -> None:
    talk = [delay for delay, _ in BEATS[:CHURN_FROM]]
    # Longer than the 62 seconds it was before the siege.
    assert sum(talk) >= 80.0, talk
    # The archers are in before the first exchange, and the catapult
    # has most of a beat to shoot in before the dragon.
    assert ARCHERS_AT < BEATS[0][0]
    assert CATAPULT_AFTER_BEAT < CHURN_FROM - 1


def test_a_rolling_rock_hurts_and_the_catapult_is_in_the_way() -> None:
    rock = RollingRock((100.0, 100.0), (300.0, 100.0))
    box = pygame.Rect(96, 96, 8, 8)
    siege = OrcSiege.__new__(OrcSiege)
    siege.rocks = [rock]
    siege.catapult = None
    assert siege.damage_for(box) == ROCK_DAMAGE
    assert siege.damage_for(pygame.Rect(400, 400, 8, 8)) == 0
    catapult = Catapult()
    catapult.x, catapult.y = 200.0, 200.0
    siege.catapult = catapult
    assert siege.blocks(pygame.Rect(196, 196, 8, 8))
    catapult.wreck()
    assert not siege.blocks(pygame.Rect(196, 196, 8, 8))
    assert all(not operator.alive for operator in catapult.operators)


def test_a_dragon_pass_can_be_sent_down_a_row_without_landing() -> None:
    tilemap = TileMap(config.MAPS_DIR / "desert_trio.txt")
    dragon = RedDragonFlyby(tilemap, first_pass=0.1)
    dragon.aim_row = 41
    dragon.update(0.2, (10, 20), (160.0, 320.0))
    assert dragon.phase == "flying" and dragon.row == 41
    assert dragon.aim_row is None and dragon._land_at is None


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        "desert_trio", progress_flags=set(DESERT_ENTRY_FLAGS))
    world._arrival_fade_t = None
    return directory, game, world


def test_archers_then_catapult_then_the_dragon_burns_it() -> None:
    directory, game, world = _world()
    step = 1 / 20
    clock = 0.0
    beats = 0
    seen: dict[str, float] = {}
    arrows_at_heroes = 0
    try:
        heroes = [(a.center_x, a.center_y) for a in world.battle_actors
                  if a.kind in ("fighter", "wizard", "ranger")]
        while clock < 100.0 and "wrecked" not in seen:
            if isinstance(game.scenes.current, DialogueScene):
                # beat0 is the entrance; beat1 is the early exchange.
                seen.setdefault(f"beat{beats}", clock)
                beats += 1
                game.scenes.pop()
                continue
            world.sanity.current = world.sanity.maximum
            world.player.x, world.player.y = CLEAR_OF_IT
            before = set(map(id, world.battle_projectiles))
            world.update(step)
            clock += step
            siege = world.siege
            for shot in world.battle_projectiles:
                if id(shot) in before or shot.kind != "orc_arrow":
                    continue
                # Aimed at one of the three: spent at about the distance
                # to one of them along its heading.
                start = (shot.x + shot.width / 2, shot.y + shot.height / 2)
                speed = math.hypot(shot.vx, shot.vy)
                end = (start[0] + shot.vx / speed * (shot._travel_left + 6),
                       start[1] + shot.vy / speed * (shot._travel_left + 6))
                assert min(math.dist(end, (hx, hy - 12))
                           for hx, hy in heroes) < TS, (start, end)
                arrows_at_heroes += 1
            if siege.archers and all(a.posted for a in siege.archers):
                seen.setdefault("posted", clock)
            if siege.catapult is not None:
                seen.setdefault("catapult", clock)
                if siege.catapult.shots:
                    seen.setdefault("rock", clock)
                if siege.catapult.wrecked:
                    seen.setdefault("wrecked", clock)
                    assert world.red_dragon.passes == 1
                    assert world.red_dragon.row == CATAPULT_POST[1]
                    assert world.red_dragon._land_at is None
            if siege.rocks:
                seen.setdefault("rolling", clock)
            # The siege's orcs are orcs in Chuck's way, like the horde.
            for body in siege.bodies:
                assert body in world.horde_orcs
        assert seen["posted"] < seen["beat1"], seen
        assert arrows_at_heroes >= 10, arrows_at_heroes
        assert seen["beat2"] < seen["catapult"] < seen["beat3"], seen
        assert seen["catapult"] < seen["rock"] < seen["rolling"] < seen["beat4"]
        assert seen["beat4"] < seen["wrecked"] < seen["beat4"] + 12.0, seen
        assert world.siege.catapult.shots >= 6
        assert all(not o.alive for o in world.siege.catapult.operators)
        assert world.siege.catapult not in world.horde_orcs
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_death_rebuilds_the_siege() -> None:
    directory, game, world = _world()
    try:
        first = world.siege
        first.catapult = Catapult()
        world._reset_enemies()
        assert world.siege is not first
        assert world.siege.catapult is None and not world.siege.archers
    finally:
        game._shutdown()
        directory.cleanup()


def test_orc_arrows_are_their_own_kind() -> None:
    shot = BattleProjectile(0.0, 0.0, 1.0, 0.0, "orc_arrow")
    assert shot.damage == config.BATTLE_ORC_ARROW_SANITY_DAMAGE
    assert config.BATTLE_ORC_ARROW_SPEED < config.BATTLE_ARROW_SPEED
    assert orc_siege.ARCHER_INTERVAL > 1.0
