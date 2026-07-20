"""The final chamber's battle tableau, first slice (session 131).

Three adventurers and the beholder stand as static presences at the
sanctum's western dais. On entering from the gauntlet, each adventurer
delivers one heroic, non-interactive line before control returns.
Chuck cannot talk to them, help them, or hurt them — combat behavior
is the next slice, and their identities are never explained.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.battle_actor import BattleActor
from src.scenes.dialogue_scene import DialogueScene
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "temple_sanctum.txt")


def test_four_actors_hold_the_western_arena() -> None:
    tilemap = _map()
    actors = {kind.split(":", 1)[1]: position
              for kind, position in tilemap.object_spawns
              if kind.startswith("battle:")}
    assert set(actors) == {"fighter", "wizard", "ranger", "beholder"}
    ts = config.TILE_SIZE
    tiles = {kind: (int(x // ts), int(y // ts))
             for kind, (x, y) in actors.items()}
    assert tiles["beholder"] == (10, 23)  # over the dais end of the aisle
    # The adventurers stand east of the beholder, facing it.
    for kind in ("fighter", "wizard", "ranger"):
        assert tiles[kind][0] > tiles["beholder"][0], kind


def test_actor_sprites_exist_at_the_authored_scales() -> None:
    pygame.init()
    for name in ("fighter", "wizard", "ranger"):
        image = pygame.image.load(
            config.SPRITES_DIR / "npcs" / f"{name}.png")
        assert image.get_size() == (16, 30), name  # human-NPC scale
    beholder = pygame.image.load(
        config.SPRITES_DIR / "npcs" / "beholder.png")
    assert beholder.get_size() == (40, 40)  # far larger than any human


def test_entrance_lines_exist_and_render() -> None:
    from src.ui.bitmap_font import GLYPH_ORDER

    lines = DialogueSystem().get("sanctum_entrance")
    assert len(lines) == 3  # one line per adventurer
    for line in lines:
        assert set(line) <= set(GLYPH_ORDER), line


def test_entering_from_the_gauntlet_plays_the_lines_once() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_8")
        scene._arrival_fade_t = None
        scene.player.x = 3 * config.TILE_SIZE + 3
        scene.player.y = 25 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_sanctum"
        assert len(scene.battle_actors) == 4
        scene._arrival_fade_t = None
        scene.update(0.01)
        overlay = game.scenes.current
        assert isinstance(overlay, DialogueScene)
        # Advance through all three lines; control returns to the world.
        for _ in range(6):
            game.input.begin_frame()
            game.input._actions_just_pressed.add("interact")
            game.scenes.update(0.01)
            game.scenes.update(0.3)
        assert game.scenes.current is scene
        # The lines were consumed: further updates stay in the world.
        scene.update(0.01)
        assert game.scenes.current is scene
    finally:
        game._shutdown()


def test_actors_are_not_interactable_and_not_enemies() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        scene._arrival_fade_t = None
        scene.update(0.01)  # (a dev jump uses the same arrival: lines play)
        if isinstance(game.scenes.current, DialogueScene):
            for _ in range(6):
                game.input.begin_frame()
                game.input._actions_just_pressed.add("interact")
                game.scenes.update(0.01)
                game.scenes.update(0.3)
        # Stand on the fighter and press E: nobody answers.
        fighter = next(a for a in scene.battle_actors
                       if a.kind == "fighter")
        scene.player.x, scene.player.y = fighter.x, fighter.y
        game.input.begin_frame()
        game.input._actions_just_pressed.add("interact")
        scene.update(0.01)
        assert game.scenes.current is scene  # no dialogue opened
        # And a scratch passes through them: they are not targets.
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        assert all(isinstance(a, BattleActor) and a.alive
                   for a in scene.battle_actors)
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
    print("All sanctum tableau tests passed.")


if __name__ == "__main__":
    _run_all()
