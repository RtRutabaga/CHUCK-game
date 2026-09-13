"""The fighter's and the knights' swords, and the return's quiet docks.

The fighter holds a sword and swings it on every stroke his battle calls,
toward whatever he is cutting at. The collided desert's knights carry one
too and swing it when Chuck is within reach. And the tutorial hints are
the opening's: back on the docks at the end, nothing tells Chuck which
keys to press.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities import sword
from src.entities.battle_actor import BattleActor
from src.entities.undead import KNIGHT_SWING_REACH, UndeadEnemy


def _blade_pixels(surface) -> int:
    colours = {sword.BLADE, sword.BLADE_LIT}
    return sum(1 for x in range(surface.get_width())
               for y in range(surface.get_height())
               if tuple(surface.get_at((x, y)))[:3] in colours)


def test_every_stroke_the_fighter_is_given_starts_a_swing() -> None:
    fighter = BattleActor(40, 40, "fighter")
    fighter.update(0.1)
    assert fighter.swing_t == 0.0
    fighter.attack_flash = config.BATTLE_ATTACK_FLASH
    fighter.update(1 / 60)
    assert fighter.swing_t > 0.0
    # It outlasts the flash, so the cut is seen.
    assert sword.SWING_DURATION > config.BATTLE_ATTACK_FLASH
    fighter.swing_toward(80)
    assert fighter.swing_dir == 1
    fighter.swing_toward(0)
    assert fighter.swing_dir == -1


def test_the_fighter_is_drawn_holding_a_sword_resting_and_swinging() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        for swing_t in (0.0, sword.SWING_DURATION / 2):
            fighter = BattleActor(40, 50, "fighter")
            fighter.load_sprite(game.assets)
            fighter.swing_t = swing_t
            surface = pygame.Surface((80, 80))
            surface.fill((0, 0, 0))
            fighter.draw(surface, (0, 0))
            assert _blade_pixels(surface) >= 8, swing_t
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_horde_battle_aims_the_fighter_at_what_reached_him() -> None:
    from src.entities.battle_hazards import CollisionBattleChoreographer

    class Orc:
        def __init__(self, x, y):
            self.center_x, self.center_y = x, y

    class Horde:
        def __init__(self, orc):
            self.orc = orc

        def nearest_to(self, x, y):
            return self.orc

        def cut_down(self, rect):
            pass

    actors = [BattleActor(100, 100, kind)
              for kind in ("fighter", "wizard", "ranger")]
    fighter = actors[0]
    battle = CollisionBattleChoreographer(actors, Horde(Orc(115, 100)))
    battle.update(1 / 60)
    assert fighter.attack_flash > 0.0 and fighter.swing_dir == 1


def test_a_knight_swings_only_when_chuck_is_in_reach() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        world = game.checkpoints.load_checkpoint("desert_east_5")
        knight = next(u for u in world.undead if u.kind == "knight")
        player = world.player
        player.x = knight.x + KNIGHT_SWING_REACH * 3
        player.y = knight.y
        knight.update(1 / 60, player)
        assert knight.swing_t == 0.0
        player.x = knight.x + 10
        knight.update(1 / 60, player)
        assert knight.swing_t > 0.0

        knight.load_sprites(game.assets)
        for facing in ("down", "left", "right", "up"):
            knight.facing = facing
            surface = pygame.Surface((400, 400))
            surface.fill((0, 0, 0))
            knight.draw(surface, (int(knight.x) - 200, int(knight.y) - 200))
            assert _blade_pixels(surface) >= 4, facing
        # Other pursuers stay empty-handed.
        orc = UndeadEnemy(40, 40, "orc")
        orc.update(1 / 60, player)
        assert orc.swing_t == 0.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_tutorial_hints_are_the_openings_and_not_the_returns() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_start")
        assert opening.map_name == "waterdeep_docks"
        assert opening._hint is not None
        game.progress.enable("waterdeep_returned")
        finale = game.checkpoints.load_checkpoint(
            "waterdeep_finale", progress_flags=game.progress.flags)
        assert finale.map_name == "waterdeep_docks"
        assert finale._hint is None
    finally:
        game._shutdown()
        directory.cleanup()
