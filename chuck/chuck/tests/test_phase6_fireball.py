"""The scripted Fireball (session 135).

Once Chuck has been sealed into the sanctum battle (the Astral breach
triggered) and survived for BATTLE_FIREBALL_DELAY, the wizard casts
Fireball: a scripted flash and shake that cuts Chuck to roughly half
Sanity and throws him into the collapsed rubble map. The player cannot
prevent or hasten it; death before it lands simply restarts the clock.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game


def _seal_chuck_in(scene):
    """Walk Chuck west so the breach seals him into the battle."""
    scene._arrival_fade_t = None
    scene._pending_entrance_dialogue = None
    scene.player.x, scene.player.y = 26 * config.TILE_SIZE, 23 * config.TILE_SIZE
    scene.update(0.01)
    assert scene.breach.triggered


def _survive_until_fireball(scene, cap=4000):
    """Advance, ignoring the barrage, until the Fireball is cast."""
    for i in range(cap):
        scene.sanity.current = scene.sanity.maximum
        scene.update(0.05)
        if scene._fireball_t is not None:
            return i
    raise AssertionError("the Fireball never fired")


def test_the_wizard_casts_fireball_only_after_surviving_sealed_in() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        _seal_chuck_in(scene)
        # Well before the delay, no Fireball yet.
        pre = int((config.BATTLE_FIREBALL_DELAY - 2.0) / 0.05)
        for _ in range(pre):
            scene.sanity.current = scene.sanity.maximum
            scene.update(0.05)
        assert scene._fireball_t is None
        assert scene.map_name == "temple_sanctum"
        # It fires close to the authored delay (measured from the seal).
        extra = 0
        while scene._fireball_t is None and extra < 400:
            scene.sanity.current = scene.sanity.maximum
            scene.update(0.05)
            extra += 1
        assert scene._fireball_t is not None
        elapsed = (pre + extra) * 0.05
        assert abs(elapsed - config.BATTLE_FIREBALL_DELAY) < 0.4, elapsed
    finally:
        game._shutdown()


def test_no_fireball_until_chuck_is_sealed_in() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        scene._arrival_fade_t = None
        scene._pending_entrance_dialogue = None
        # Park Chuck at the arrival (east of the breach trigger): the
        # survival clock never starts, so the Fireball never comes.
        for _ in range(int((config.BATTLE_FIREBALL_DELAY + 5.0) / 0.05)):
            scene.sanity.current = scene.sanity.maximum
            scene.update(0.05)
        assert not scene.breach.triggered
        assert scene._fireball_t is None
        assert scene.map_name == "temple_sanctum"
    finally:
        game._shutdown()


def test_the_adventurers_argue_before_the_cast() -> None:
    from src.scenes.dialogue_scene import DialogueScene
    from src.ui.bitmap_font import GLYPH_ORDER

    lines = ["Wait, I know those sigils, you can't cast that here!",
             "... we're too close to an astral rip, we don't know what "
             "will happen",
             "I have to try, we're out of options!",
             "......", "FIREBALL!!"]
    from src.systems.dialogue import DialogueSystem
    assert DialogueSystem().get("fireball_cast") == lines
    for line in lines:
        assert set(line) <= set(GLYPH_ORDER), line

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        _seal_chuck_in(scene)
        # At the brink of the delay: the argument opens, no blast yet.
        scene._survival_t = config.BATTLE_FIREBALL_DELAY
        scene.update(0.05)
        assert isinstance(game.scenes.current, DialogueScene)
        assert scene._fireball_t is None
        # Advance through all five lines back to the world.
        for _ in range(14):
            game.input.begin_frame()
            game.input._actions_just_pressed.add("interact")
            game.scenes.update(0.01)
            game.scenes.update(0.3)
            if game.scenes.current is scene:
                break
        assert game.scenes.current is scene
        # "FIREBALL!!" said, the blast now lands.
        scene.update(0.01)
        assert scene._fireball_t is not None
    finally:
        game._shutdown()


def test_fireball_halves_sanity_and_throws_chuck_into_the_rubble() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        _seal_chuck_in(scene)
        _survive_until_fireball(scene)
        # The blast shakes the screen the instant it is cast.
        assert scene.camera._shake > 0.0
        half = int(scene.sanity.maximum * config.FIREBALL_SANITY_FRACTION)
        for _ in range(int(config.FIREBALL_DURATION / 0.05) + 5):
            scene.update(0.05)
            if scene.map_name == "temple_rubble":
                break
        assert scene.map_name == "temple_rubble"
        assert game.active_checkpoint_id == "temple_rubble"
        assert scene._player_tile() == (23, 5)  # the from_fireball arrival
        assert scene.sanity.current == half  # cut to half by the blast
        # The rubble has no battle of its own.
        assert scene.battle is None
    finally:
        game._shutdown()


def test_the_blast_never_heals_a_low_chuck() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        _seal_chuck_in(scene)
        _survive_until_fireball(scene)
        scene.sanity.current = 12  # barely hanging on when it lands
        for _ in range(int(config.FIREBALL_DURATION / 0.05) + 5):
            scene.update(0.05)
            if scene.map_name == "temple_rubble":
                break
        assert scene.sanity.current == 12  # the explosion cannot restore
    finally:
        game._shutdown()


def test_death_before_the_fireball_restarts_the_survival_clock() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_9")
        _seal_chuck_in(scene)
        for _ in range(int((config.BATTLE_FIREBALL_DELAY - 3.0) / 0.05)):
            scene.sanity.current = scene.sanity.maximum
            scene.update(0.05)
        assert scene._survival_t > 0.0
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # Respawn re-armed the room: breach re-sealed, clock reset.
        assert not scene.breach.triggered
        assert scene._survival_t == 0.0
        assert scene._fireball_t is None
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
    print("All fireball tests passed.")


if __name__ == "__main__":
    _run_all()
