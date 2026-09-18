"""Opt-in browser timing reports; no gameplay changes or network telemetry."""

import math
from time import perf_counter


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


def browser_reporter(window):
    """Enable only for an explicit ?diagnostics=1 preview URL."""
    if "diagnostics=1" not in str(window.location.search).lstrip("?").split("&"):
        return None
    reporter = FrameReporter(window.console.info)
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

    return report
