"""Opt-in browser timing reports; no gameplay changes or network telemetry."""

import math
from time import perf_counter


def show_browser_crash(window, details):
    """Keep a readable error after SDL closes, including on Xbox Edge."""
    panel = window.document.createElement("pre")
    panel.id = "chuck-crash"
    panel.style.cssText = (
        "position:fixed;inset:5%;z-index:2147483647;margin:0;padding:24px;"
        "background:#171322;color:white;white-space:pre-wrap;overflow:auto;"
        "font:18px/1.5 monospace;user-select:text"
    )
    panel.textContent = (
        "CHUCK stopped unexpectedly.\n"
        "Please share a photo of this message, then reload and use your save code.\n\n"
        + details
    )
    window.document.body.appendChild(panel)


class FrameReporter:
    """Report five-second samples, separating maps and scene transitions."""

    def __init__(self, emit, now=perf_counter):
        self.emit = emit
        self.now = now
        self.label = None
        self.previous = None
        self.intervals = []
        self.elapsed = 0.0

    def frame(self, label, visible=True):
        current = self.now()
        if not visible or label != self.label or self.previous is None:
            self.label = label
            self.previous = current if visible else None
            self.intervals.clear()
            self.elapsed = 0.0
            return
        interval = current - self.previous
        self.previous = current
        self.intervals.append(interval)
        self.elapsed += interval
        elapsed = self.elapsed
        if elapsed < 5:
            return
        ordered = sorted(self.intervals)
        p95 = ordered[math.ceil(len(ordered) * 0.95) - 1]
        self.emit(
            f"CHUCK timing | {label} | {len(ordered) / elapsed:.1f} fps | "
            f"p95 {p95 * 1000:.1f} ms | max {ordered[-1] * 1000:.1f} ms")
        self.intervals.clear()
        self.elapsed = 0.0


# Every named action, so a report can say which ones a button reached.
ACTIONS = ("move_up", "move_down", "move_left", "move_right",
           "interact", "jump", "scratch", "pause", "back")


class PadWatch:
    """What the browser's gamepad layer is actually delivering.

    Xbox Edge was moving the title selection with the d-pad while A did
    nothing, and the fix for that was a guess about which button the
    page receives. This turns the guess into a reading: press a button,
    and the console says which physical index went down and which of the
    game's actions -- if any -- it reached.

    Polled rather than hooked into events, so it needs no changes to the
    input path it is reporting on.
    """

    def __init__(self, emit):
        self.emit = emit
        self.down = set()
        self.hat = None
        self.described = False

    def _pad(self):
        import pygame

        try:
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                return None
            pad = pygame.joystick.Joystick(0)
            if not pad.get_init():
                pad.init()
            return pad
        except Exception:      # noqa: BLE001 - a report is never worth a crash
            return None

    def poll(self, game):
        pad = self._pad()
        if pad is None:
            return
        if not self.described:
            self.described = True
            self.emit(
                f"CHUCK pad | {pad.get_name()!r} | "
                f"{pad.get_numbuttons()} buttons, {pad.get_numhats()} hats, "
                f"{pad.get_numaxes()} axes")

        try:
            now = {index for index in range(pad.get_numbuttons())
                   if pad.get_button(index)}
        except Exception:      # noqa: BLE001
            return
        for index in sorted(now - self.down):
            reached = [name for name in ACTIONS if game.input.is_down(name)]
            self.emit(f"CHUCK pad | button {index} down | "
                      f"reached: {', '.join(reached) or 'nothing'}")
        self.down = now

        if pad.get_numhats():
            try:
                hat = pad.get_hat(0)
            except Exception:  # noqa: BLE001
                return
            if hat != self.hat and hat != (0, 0):
                reached = [name for name in ACTIONS if game.input.is_down(name)]
                self.emit(f"CHUCK pad | hat {hat} | "
                          f"reached: {', '.join(reached) or 'nothing'}")
            self.hat = hat


def browser_reporter(window):
    """Enable only for an explicit ?diagnostics=1 preview URL."""
    if "diagnostics=1" not in str(window.location.search).lstrip("?").split("&"):
        return None
    reporter = FrameReporter(window.console.info)
    pad = PadWatch(window.console.info)
    first = True

    def report(game):
        nonlocal first
        scene = game.scenes.current
        label = type(scene).__name__
        map_name = getattr(scene, "map_name", None)
        if map_name is not None:
            label += ":" + map_name
        if first:
            window.console.info(
                f"CHUCK first frame | {window.performance.now() / 1000:.2f}s "
                "since navigation (includes waiting for start gesture)")
            first = False
        reporter.frame(label, not window.document.hidden)
        pad.poll(game)

    return report
