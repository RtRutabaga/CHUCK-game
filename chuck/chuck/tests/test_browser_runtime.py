"""Browser frame scheduling and audio path compatibility."""

import asyncio
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock, call
import tempfile

from src.core import config
from src.core.game import Game
from src.core.runtime import audio_path
from src.systems.audio import AudioSystem
from tools.build_web import finalize_web_artifact


def test_browser_artifact_is_ready_for_github_pages():
    with tempfile.TemporaryDirectory() as folder:
        web = Path(folder)
        page = web / "index.html"
        page.write_text("<canvas id=canvas></canvas>", encoding="utf-8")

        finalize_web_artifact(web)

        assert (web / ".nojekyll").is_file()
        assert "image-rendering: pixelated" in page.read_text(encoding="utf-8")


def test_browser_music_cancels_fade_before_replacing_track():
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        (directory / "next.ogg").touch()
        (directory / "next.wav").touch()
        for platform, suffix, stops in (("emscripten", ".ogg", True),
                                        ("win32", ".wav", False)):
            music = Mock()
            audio = AudioSystem.__new__(AudioSystem)
            audio.enabled = True
            audio.music_volume = 0.5
            audio._current_music = ("previous.wav", True)
            with patch("sys.platform", platform), \
                    patch.object(config, "MUSIC_DIR", directory), \
                    patch("pygame.mixer.music", music):
                audio.play_music("next.wav")
                expected = [call.stop()] if stops else []
                expected += [call.load(str(directory / ("next" + suffix))),
                             call.set_volume(0.5), call.play(-1)]
                assert music.mock_calls == expected
                audio.play_music("next.wav")
                assert music.mock_calls == expected  # Same cue keeps playing.


def test_browser_display_has_fixed_framebuffer():
    with patch("sys.platform", "emscripten"), \
            patch("pygame.display.set_mode") as mode:
        Game._open_window(True)
        mode.assert_called_once_with((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))


def test_browser_fullscreen_cannot_recreate_window():
    from src.scenes.pause_scene import main_options, controls_rows
    with patch("sys.platform", "emscripten"), \
            patch("pygame.display.set_mode") as mode:
        Game.set_fullscreen(object(), True)
        mode.assert_not_called()
        assert "FULLSCREEN" not in main_options()
        assert not any(row[0] == "FULLSCREEN" for row in controls_rows(None))


def test_browser_audio_paths_preserve_desktop_cues():
    original = Path("assets/audio/music/title.wav")
    with patch("sys.platform", "emscripten"):
        assert audio_path(original) == original.with_suffix(".ogg")
    with patch("sys.platform", "win32"):
        assert audio_path(original) == original


def test_browser_frames_yield_without_blocking_and_clamp_dt():
    events = []

    class Clock:
        def tick(self):
            # No FPS argument: sleeping to cap frames would block the host.
            return 1000

    class Probe:
        clock = Clock()
        running = False
        frames = 0

        def _handle_events(self):
            events.append("input")

        def _update(self, dt):
            assert dt == config.MAX_DT
            events.append("update")

        def _draw(self):
            events.append("draw")
            self.frames += 1
            if self.frames == 2:
                self.running = False

        def _shutdown(self):
            events.append("shutdown")

    async def host():
        events.append("host")

    async def exercise():
        await asyncio.gather(Game.run_async(Probe()), host())

    asyncio.run(exercise())
    assert events == ["input", "update", "draw", "host",
                      "input", "update", "draw", "shutdown"]


def test_browser_shutdown_on_frame_failure():
    class Probe:
        running = False
        closed = False
        clock = type("Clock", (), {"tick": lambda self: 16})()

        def _handle_events(self):
            raise ValueError("frame failure")

        def _shutdown(self):
            self.closed = True

    probe = Probe()
    try:
        asyncio.run(Game.run_async(probe))
    except ValueError:
        pass
    else:
        raise AssertionError("Frame errors must remain visible")
    assert probe.closed


if __name__ == "__main__":
    for name, test in sorted(globals().copy().items()):
        if name.startswith("test_") and callable(test):
            test()
            print(f"PASS {name}")
