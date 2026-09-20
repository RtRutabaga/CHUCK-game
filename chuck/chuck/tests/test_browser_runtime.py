"""Browser frame scheduling and audio path compatibility."""

import asyncio
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock, call
import json
import tempfile

from src.core import config
from src.core.game import Game
from src.core.runtime import audio_path
from src.systems.audio import AudioSystem
from tools.build_web import MOBILE_SHELL, finalize_web_artifact


def test_browser_clipboard_polls_completion_and_times_out():
    from src.systems.clipboard import copy_browser
    from unittest.mock import AsyncMock
    import platform
    window = Mock()
    bridge = window.CHUCKClipboard
    bridge.beginCopy.return_value = 7
    with patch("sys.platform", "emscripten"), \
            patch.object(platform, "window", window, create=True), \
            patch("src.systems.clipboard.asyncio.sleep", new_callable=AsyncMock):
        bridge.copyStatus.side_effect = ["pending", "copied"]
        assert asyncio.run(copy_browser("TEST-CODE")) is True
        bridge.finishCopy.assert_called_with(7)
        bridge.copyStatus.side_effect = None
        bridge.copyStatus.return_value = "pending"
        assert asyncio.run(copy_browser("TEST-CODE")) is False
        bridge.copyStatus.return_value = "blocked"
        assert asyncio.run(copy_browser("TEST-CODE")) is False


def test_browser_crash_remains_readable_after_sdl_shutdown():
    from src.core.browser_diagnostics import show_browser_crash
    window = Mock()
    show_browser_crash(window, "ValueError: missing captain marker")
    panel = window.document.createElement.return_value
    assert "ValueError: missing captain marker" in panel.textContent
    assert "save code" in panel.textContent
    window.document.body.appendChild.assert_called_once_with(panel)


def test_browser_artifact_is_ready_for_github_pages():
    with tempfile.TemporaryDirectory() as folder:
        web = Path(folder)
        page = web / "index.html"
        page.write_text('<canvas id=canvas></canvas> fopen("browser-app.apk")',
                        encoding="utf-8")
        (web / "browser-app.apk").write_bytes(b"first game build")

        finalize_web_artifact(web)

        assert (web / ".nojekyll").is_file()
        assert "image-rendering: pixelated" in page.read_text(encoding="utf-8")
        first = next(web.glob("browser-app-*.apk"))
        assert first.read_bytes() == b"first game build"
        assert first.name in page.read_text(encoding="utf-8")
        page.write_text('fopen("browser-app.apk")', encoding="utf-8")
        (web / "browser-app.apk").write_bytes(b"updated game build")
        finalize_web_artifact(web)
        updated = next(p for p in web.glob("browser-app-*.apk") if p != first)
        assert updated.name in page.read_text(encoding="utf-8")
        assert first.name not in page.read_text(encoding="utf-8")


def test_the_desktop_page_points_phones_at_the_touch_shell():
    """A link, and one that knows not to appear inside the shell.

    Nothing detects a device, so the desktop page carries the only sign
    that `/mobile/` exists. It is a link rather than a redirect because
    user-agent sniffing would have to be right about the Xbox browser,
    and being wrong there drops a controller player into a touch shell.

    The catch it has to survive: `/mobile/` iframes this very page. A
    link left alone would sit inside the touch shell offering to take
    the player to the touch shell, and tapping it would nest another.
    """
    with tempfile.TemporaryDirectory() as folder:
        web = Path(folder)
        page = web / "index.html"
        page.write_text('<canvas id=canvas></canvas> fopen("browser-app.apk")',
                        encoding="utf-8")
        (web / "browser-app.apk").write_bytes(b"game")

        finalize_web_artifact(web)

        html = page.read_text(encoding="utf-8")
        assert 'href="mobile/"' in html, "no way to reach the touch shell"
        assert "window.top !== window.self" in html, (
            "the link does not remove itself inside a frame, so it would "
            "appear inside /mobile/ and offer to nest another shell")
        assert "mobile=1" in html, (
            "the link ignores the marker the shell puts on the iframe URL")
        # The shell must still be asking for it, or the check above is
        # guarding against nothing.
        assert "?mobile=1" in MOBILE_SHELL


def test_the_page_claims_playback_audio_so_silent_mode_stops_muting_it():
    """Why a phone with the ring switch on heard nothing.

    iOS mutes Web Audio under the silent switch, because by default a
    page's sound is filed as "ambient" -- incidental, the kind of thing
    silent mode is for. Declaring the AudioSession type "playback" says
    this is the main content, as a music or video app does, and the
    switch stops applying. The same build was always audible on a PC and
    on the Xbox, which is how we know the mixer was never the problem.
    """
    with tempfile.TemporaryDirectory() as folder:
        web = Path(folder)
        page = web / "index.html"
        page.write_text('<canvas id=canvas></canvas> fopen("browser-app.apk")',
                        encoding="utf-8")
        (web / "browser-app.apk").write_bytes(b"game")

        finalize_web_artifact(web)

        html = page.read_text(encoding="utf-8")
        assert "navigator.audioSession" in html, (
            "the page no longer declares an audio session, so iOS will "
            "mute it under the ring/silent switch")
        assert '"playback"' in html
        # It has to be declared before the wasm build boots and makes an
        # audio context, so it must come first of the injected scripts.
        assert html.index("audioSession") < html.index("CHUCKClipboard")


def test_the_shell_can_go_full_screen_or_say_why_it_cannot():
    """Full screen on Android; Add to Home Screen on iPhone.

    Safari on iPhone has no Fullscreen API, so the button would sit there
    doing nothing. It is removed instead, and the panel's note about the
    home screen -- the only way to lose the browser bars on iOS -- is
    shown in its place.
    """
    assert 'id="fullscreen"' in MOBILE_SHELL
    assert "requestFullscreen" in MOBILE_SHELL
    assert "fullscreen.remove()" in MOBILE_SHELL, (
        "the full-screen button no longer removes itself where the "
        "browser has no Fullscreen API, so iPhone gets a dead button")
    assert "Add to Home Screen" in MOBILE_SHELL, (
        "the shell no longer tells an iPhone player how to lose the bars")
    # The orientation lock must not be able to undo the full screen it
    # was just given: it is refused outright on desktop, and a throw
    # there would escape before the await above had settled.
    assert "try{await screen.orientation.lock('landscape')}catch" in MOBILE_SHELL, (
        "screen.orientation.lock is not guarded by its own try/catch")


def test_the_shell_is_installable_to_the_home_screen():
    """The iPhone route to a chrome-free landscape game."""
    with tempfile.TemporaryDirectory() as folder:
        web = Path(folder)
        (web / "index.html").write_text('fopen("browser-app.apk")',
                                        encoding="utf-8")
        (web / "browser-app.apk").write_bytes(b"game")

        finalize_web_artifact(web)

        manifest = web / "mobile" / "manifest.webmanifest"
        assert manifest.is_file(), "no web app manifest beside the shell"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data["display"] == "fullscreen"
        assert data["orientation"] == "landscape"
        # Relative, because the site is served from a repository
        # subpath, not a domain root.
        assert data["start_url"].startswith(".")
        assert 'rel="manifest"' in MOBILE_SHELL
        assert 'name="apple-mobile-web-app-capable"' in MOBILE_SHELL, (
            "iOS needs this to launch without browser bars")


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
