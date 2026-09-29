"""An enemy is a thing in the way, not a cage.

Contact used to cancel Chuck's whole move: while a body overlapped his,
every direction was refused. A pursuer that caught up therefore stood in
him and held him there, and because it had caught him once it would
catch him again -- so the first hit committed him to the fight whether
or not the fight was the point. Exploration matters more than combat
here, and running is supposed to be an answer.

Now only the closing half of a move is refused. Chuck still cannot walk
through a body; he can always walk out of one.

Animal Control is the exception, and the reason the rule is written as
an exception rather than an absence: their entire role in the day city
is to corner him, and the net that follows is a designed capture.
"""

import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core.game import Game
from src.entities.animal_control import AnimalControlOfficer
from src.entities.undead import UndeadEnemy


MAP_NAME = "modern_city_day_2"
STEP = 4.0


def _game_and_world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(MAP_NAME)
    world._arrival_fade_t = None
    return directory, game, world


def _on_top_of_chuck(world, enemy_type):
    """An enemy standing exactly where Chuck is, which is the pinned case."""
    enemy = enemy_type(world.player.x + world.player.width / 2,
                       world.player.y + world.player.height / 2)
    enemy.tilemap = world.tilemap
    return enemy


def _walk(world, enemy, dx, steps=12):
    """Try to walk, one step per frame, the way the scene does it."""
    for _ in range(steps):
        old = (world.player.x, world.player.y)
        world.player.x += dx
        world._touched_by(
            enemy, old,
            lets_go=not isinstance(enemy, AnimalControlOfficer),
        )


def test_chuck_can_walk_out_of_an_enemy_standing_on_him() -> None:
    directory, game, world = _game_and_world()
    try:
        enemy = _on_top_of_chuck(world, lambda x, y: UndeadEnemy(x, y, "zombie"))
        start = world.player.x
        _walk(world, enemy, STEP)
        assert world.player.x > start + STEP * 6, (
            "a zombie standing on Chuck still holds him in place")
    finally:
        game._shutdown()
        directory.cleanup()


def test_chuck_still_cannot_walk_through_an_enemy() -> None:
    """The other half: a body is solid, or it is a decal."""
    directory, game, world = _game_and_world()
    try:
        enemy = _on_top_of_chuck(world, lambda x, y: UndeadEnemy(x, y, "zombie"))
        # Put the zombie a little to Chuck's right, then walk into it.
        enemy.x += STEP
        start = world.player.x
        _walk(world, enemy, STEP)
        assert world.player.x <= start, (
            "Chuck pushed into a zombie instead of being stopped by it")
    finally:
        game._shutdown()
        directory.cleanup()


def test_animal_control_still_corners_him() -> None:
    directory, game, world = _game_and_world()
    try:
        officer = _on_top_of_chuck(world, AnimalControlOfficer)
        start = world.player.x
        _walk(world, officer, STEP)
        assert world.player.x == start, (
            "an Animal Control officer let Chuck walk away; the net is "
            "supposed to be the end of that chase")
    finally:
        game._shutdown()
        directory.cleanup()


def test_walking_away_still_costs_sanity() -> None:
    """Escaping is allowed. Escaping for free is not."""
    directory, game, world = _game_and_world()
    try:
        enemy = _on_top_of_chuck(world, lambda x, y: UndeadEnemy(x, y, "zombie"))
        before = world.sanity.current
        _walk(world, enemy, STEP)
        assert world.sanity.current < before, (
            "contact with a zombie stopped hurting")
    finally:
        game._shutdown()
        directory.cleanup()


def _chase(enemy, world, game, frames=90):
    """Hold right for a second and a half, through the real update loop."""
    enemy.tilemap = world.tilemap
    world.undead.append(enemy)
    game.input._hold("move_right", ("test",))
    for _ in range(frames):
        world.update(1 / 60)
    return math.hypot(world.player.x - enemy.x, world.player.y - enemy.y)


def test_a_pursuer_on_top_of_chuck_does_not_hold_him_there() -> None:
    """The whole thing, through `update`: pursuit, contact and getting out."""
    directory, game, world = _game_and_world()
    try:
        zombie = _on_top_of_chuck(
            world, lambda x, y: UndeadEnemy(x, y, "zombie"))
        gap = _chase(zombie, world, game)
        # He is faster than it, so a second and a half should be daylight.
        assert gap > 60.0, f"Chuck only got {gap:.1f}px from a zombie"
    finally:
        game._shutdown()
        directory.cleanup()


def test_an_officer_on_top_of_chuck_does_hold_him_there() -> None:
    directory, game, world = _game_and_world()
    try:
        officer = _on_top_of_chuck(world, AnimalControlOfficer)
        gap = _chase(officer, world, game)
        assert gap < 8.0, (
            f"Chuck got {gap:.1f}px from an Animal Control officer; they "
            f"are the one enemy that is supposed to corner him")
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
    print("All enemy-escape tests passed.")


if __name__ == "__main__":
    _run_all()
