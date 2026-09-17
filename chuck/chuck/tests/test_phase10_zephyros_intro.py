"""Phase 10's rope descent, giant-scale reveal, and exact conversation."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.zephyros_intro_cutscene_scene import (
    CONVERSATION_FADE_START,
    CONVERSATION_MUSIC_START,
    DIALOGUE_START,
    FACE_ENTER_END,
    HAND_SETTLE_END,
    HAND_RISE_START,
    ROPE_DESCENT_END,
    ZephyrosIntroCutsceneScene,
)
from src.scenes.zephyros_launch_cutscene_scene import (
    ZephyrosLaunchCutsceneScene,
)
from src.systems.dialogue import DialogueSystem


EXPECTED_DIALOGUE = [
    "Hello little friend! ... Yes... YES!",
    "... The Entity said you would be coming.",
    "Now, as you know, the worlds have been shuffled. Smashed.",
    "A little bit crinkled. Most don't know. Most don't see.",
    "The typical being, you see, is like the halfling leaf inside a cigarette.",
    "They don't know whether they're still neat inside the pack...",
    "...or whether they've already been smashed together in the ashtray.",
    "But you, Chuck... You're part of the ashtray. You see.",
    "... The Entity has gone quiet.",
    "It is frightened, Chuck. Yes... Yes...",
    "Something must be done.",
    "... Oh... No.",
    "Not you. Heavens, no.",
    "You're more of a fighter than a winner, aren't you, Chuck?",
    "Not to worry. I have my best people working on it.",
    "Your role in all this...",
    "...is simply to make it through. As you always do.",
    "... Now then!",
    "I shall fling you onward!",
]
def test_rope_yes_uses_validated_action_and_preserves_sanity() -> None:
    game = Game()
    try:
        aerie = game.checkpoints.load_checkpoint("zephyros_3", sanity=37)
        choice = aerie.choices.get("zephyros_rope")
        assert choice.options[0].action == "zephyros_intro"
        assert choice.options[1].action is None
        aerie._on_choice(choice.options[0])
        aerie.update(0.0)
        intro = game.scenes.current
        assert isinstance(intro, ZephyrosIntroCutsceneScene)
        assert intro.sanity == 37
    finally:
        game._shutdown()


def test_complete_supplied_dialogue_is_data_driven_and_exact() -> None:
    assert DialogueSystem().get("zephyros_intro") == EXPECTED_DIALOGUE


def test_descent_face_blink_smile_and_reaching_hand_are_distinct_beats() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=45)
        scene.on_enter()
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))

        scene.elapsed = 3.0
        assert scene.phase == "rope_descent"
        scene.draw(surface)
        assert surface.get_at((78, 40))[:3] != surface.get_at((20, 40))[:3]

        scene.elapsed = ROPE_DESCENT_END + 1.0
        assert scene.phase == "face_reveal"
        scene.draw(surface)

        scene.elapsed = 9.55
        assert scene._blink_amount() > 0.9
        scene.draw(surface)

        scene.elapsed = HAND_RISE_START + 2.0
        assert scene.phase == "hand_rise"
        midpoint = scene.hand_position()
        scene.draw(surface)

        scene.elapsed = HAND_SETTLE_END
        assert scene.phase == "conversation"
        assert scene.hand_position()[0] < midpoint[0] - 100
        scene.draw(surface)
    finally:
        game._shutdown()


def test_exterior_cloud_is_clipped_behind_the_tower_window() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=45)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = 6.0  # cloud overlaps the opening's west edge
        scene._draw_tower_interior(surface)

        # The cloud remains visible through the blue opening but cannot paint
        # across the surrounding dark reveal or interior masonry.
        assert surface.get_at((260, 48))[:3] == (225, 237, 238)
        assert surface.get_at((253, 48))[:3] == (34, 34, 51)
        assert surface.get_at((251, 48))[:3] != (225, 237, 238)
    finally:
        game._shutdown()


def _press_interact(game, scene) -> None:
    game.input.begin_frame()
    game.input._actions_just_pressed.add("interact")
    scene.update(0.0)


def test_dialogue_uses_normal_manual_advance_then_hands_off() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=62)
        game.scenes.replace(scene)
        scene.update(DIALOGUE_START + 0.1)
        assert scene.dialogue_index == 0
        # Time alone never advances a conversation or starts the launch.
        scene.update(300.0)
        assert scene.dialogue_index == 0
        assert game.scenes.current is scene

        for expected_index in range(1, len(scene.dialogue)):
            _press_interact(game, scene)  # complete current typewriter
            _press_interact(game, scene)  # advance exactly one panel
            assert scene.dialogue_index == expected_index
        assert scene.conversation_complete
        _press_interact(game, scene)  # leave the completed conversation
        launch = game.scenes.current
        assert isinstance(launch, ZephyrosLaunchCutsceneScene)
        assert launch.sanity == 62
    finally:
        game._shutdown()


def test_non_dialogue_input_cannot_skip_the_cinematic() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=50)
        game.scenes.replace(scene)
        before = scene.elapsed
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
        assert game.scenes.current is scene
        assert scene.elapsed == before
    finally:
        game._shutdown()


def test_tower_music_fades_before_conversation_theme_begins() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=50)
        stopped = []
        played = []
        game.audio.stop_music = lambda fade_ms=0: stopped.append(fade_ms)
        game.audio.play_music = lambda name, loops=True: played.append(
            (name, loops)
        )

        scene.update(CONVERSATION_FADE_START - 0.1)
        assert stopped == [] and played == []
        scene.update(0.2)
        assert stopped == [900] and played == []
        scene.update(CONVERSATION_MUSIC_START - scene.elapsed - 0.01)
        assert played == []
        scene.update(0.02)
        assert played == [("zephyros_conversation.wav", True)]
    finally:
        game._shutdown()


def test_large_frame_still_gives_the_tower_theme_a_real_fade() -> None:
    game = Game()
    try:
        scene = ZephyrosIntroCutsceneScene(game, sanity=50)
        stopped = []
        played = []
        game.audio.stop_music = lambda fade_ms=0: stopped.append(fade_ms)
        game.audio.play_music = lambda name, loops=True: played.append(name)

        scene.update(CONVERSATION_MUSIC_START + 1.0)
        assert stopped == [900] and played == []
        scene.update(0.0)
        assert played == ["zephyros_conversation.wav"]
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
    print("All Phase 10 Zephyros introduction tests passed.")


if __name__ == "__main__":
    _run_all()
