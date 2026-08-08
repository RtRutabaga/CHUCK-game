"""Phase 10 rainy modern-city descent and contained endpoint."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.modern_city_arrival_cutscene_scene import (
    CIGARETTE_SEATED,
    DESCENT_END,
    FADE_OUT_START,
    HANDOFF_TIME,
    IMPACT_TIME,
    LOOK_START,
    RESPAWN_TIME,
    VANISH_TIME,
    ModernCityArrivalCutsceneScene,
)
from src.scenes.world_scene import WorldScene
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _game_and_scene(sanity=47):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    scene = ModernCityArrivalCutsceneScene(game, sanity=sanity)
    game.scenes.replace(scene)
    return directory, game, scene


def test_close_flight_moves_diagonally_then_loses_horizontal_momentum() -> None:
    directory, game, scene = _game_and_scene()
    try:
        scene.elapsed = 0.0
        start = scene.chuck_position()
        scene.elapsed = DESCENT_END
        turn = scene.chuck_position()
        scene.elapsed = IMPACT_TIME
        impact = scene.chuck_position()
        assert turn[0] > start[0] + 160
        assert turn[1] > start[1] + 60
        assert abs(impact[0] - turn[0]) < 12
        assert impact[1] > turn[1] + 30
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = 5.0
        scene.draw(surface)
        # The old unexplained black perspective-road rectangle is gone.
        assert surface.get_at((160, 155))[:3] != (17, 22, 30)
    finally:
        game._shutdown()
        directory.cleanup()


def test_impact_uses_the_established_death_and_return_cues() -> None:
    directory, game, scene = _game_and_scene(sanity=33)
    try:
        played = []
        game.audio.play_sfx = played.append
        scene.update(IMPACT_TIME)
        assert scene.phase == "impact"
        assert scene.sanity == 0
        scene.update(VANISH_TIME - IMPACT_TIME)
        assert scene.phase == "vanished"
        scene.update(RESPAWN_TIME - VANISH_TIME)
        assert scene.phase == "return"
        assert scene.sanity == config.SANITY_MAX
        assert played == ["hurt", "vanish", "respawn"]
    finally:
        game._shutdown()
        directory.cleanup()


def test_return_looks_around_then_lights_a_cigarette_in_fixed_tableau() -> None:
    directory, game, scene = _game_and_scene()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = LOOK_START + 0.2
        assert scene.phase == "look" and scene._facing() == "left"
        scene.draw(surface)
        scene.elapsed = LOOK_START + 1.0
        assert scene._facing() == "right"
        scene.elapsed = CIGARETTE_SEATED
        assert scene.cigarette_lit and scene.phase == "smoke"
        scene.draw(surface)
        before = scene.elapsed
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
        assert scene.elapsed == before
        assert game.scenes.current is scene
    finally:
        game._shutdown()
        directory.cleanup()


def test_handoff_saves_and_loads_the_real_city_ashtray() -> None:
    directory, game, scene = _game_and_scene(sanity=19)
    try:
        scene.update(HANDOFF_TIME)
        world = game.scenes.current
        assert isinstance(world, WorldScene)
        assert world.map_name == "modern_city_arrival"
        assert game.active_checkpoint_id == "modern_city_anchor"
        assert game.progress.has("modern_city_reached")
        assert world.sanity.current == config.SANITY_MAX
        assert len(world.anchors) == 1
        assert world.anchors[0].lit
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        saved = game.saves.load()
        assert saved is not None
        assert saved.checkpoint_id == "modern_city_anchor"
        assert saved.sanity == config.SANITY_MAX
        assert "modern_city_reached" in saved.progress_flags

        # CONTINUE uses the same checkpoint definition and initialization.
        continued = game.checkpoints.continue_game()
        assert continued.map_name == "modern_city_arrival"
        assert continued.anchors[0].lit
    finally:
        game._shutdown()
        directory.cleanup()


def test_city_handoff_enters_the_rainy_phase11_start_map() -> None:
    directory, game, _scene = _game_and_scene()
    try:
        world = game.checkpoints.load_checkpoint("modern_city_1")
        assert world.map_name == "modern_city_arrival"
        assert MAP_TILESET[world.map_name] == "city"
        # The night-city theme now starts the moment Chuck lands.
        assert AREA_MUSIC[world.map_name] == "city_night.wav"
        assert AREA_WALK_EXITS[(world.map_name, "⮝")].destination == (
            "modern_city_night_2"
        )
        assert world.city_rain is not None
        assert len(world.anchors) == 1
        assert not world.npcs
        assert not world.hazards
        assert not world._enemy_spawns
        assert world.tilemap.width_tiles == 72
        assert world.tilemap.height_tiles == 54
        assert len(world.pickups) == 4
        assert CHECKPOINT_BY_ID["modern_city_anchor"].saveable
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.update(0.1)
        world.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_arrival_does_not_restart_or_replace_the_transition_cue() -> None:
    directory, game, scene = _game_and_scene()
    try:
        played = []
        stopped = []
        game.audio.play_music = lambda filename, loop=True: played.append(
            (filename, loop)
        )
        game.audio.stop_music = lambda fade_ms=0: stopped.append(fade_ms)
        scene.on_enter()
        scene.update(FADE_OUT_START - 0.1)
        assert played == [] and stopped == []
        scene.update(0.2)
        assert played == []
        assert stopped == [round(config.AREA_FADE_DURATION * 1000)]
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All Phase 10 city arrival tests passed.")


if __name__ == "__main__":
    _run_all()
