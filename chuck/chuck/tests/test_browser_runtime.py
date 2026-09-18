"""Browser frame scheduling and audio path compatibility."""

import asyncio
from pathlib import Path
from unittest.mock import patch

from src.core import config
from src.core.game import Game
from src.core.runtime import audio_path


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
