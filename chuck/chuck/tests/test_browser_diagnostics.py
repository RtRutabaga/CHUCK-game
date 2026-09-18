"""Timing reports must not disguise stalls or count hidden-tab time."""

from types import SimpleNamespace
from src.core.browser_diagnostics import FrameReporter, browser_reporter


def test_reports_real_intervals_including_stalls():
    messages = []
    time = [0.0]
    reporter = FrameReporter(messages.append, lambda: time[0])
    reporter.frame("docks")
    for _ in range(240):
        time[0] += 1 / 60
        reporter.frame("docks")
    time[0] += 1.1
    reporter.frame("docks")
    assert len(messages) == 1
    assert "47.3 fps" in messages[0]
    assert "p95 16.7 ms" in messages[0]
    assert "max 1100.0 ms" in messages[0]


def test_hidden_time_and_map_change_start_fresh_samples():
    messages = []
    time = [0.0]
    reporter = FrameReporter(messages.append, lambda: time[0])
    reporter.frame("docks")
    time[0] = 2
    reporter.frame("docks")
    reporter.frame("docks", visible=False)
    time[0] = 200
    reporter.frame("docks")
    assert not reporter.intervals
    time[0] = 202
    reporter.frame("docks")
    reporter.frame("sewer")
    assert not reporter.intervals
    assert not messages


def test_diagnostics_are_explicitly_opt_in():
    for search in ("", "?diagnostics=0", "?otherdiagnostics=1"):
        window = SimpleNamespace(location=SimpleNamespace(search=search))
        assert browser_reporter(window) is None


if __name__ == "__main__":
    for name, test in sorted(globals().copy().items()):
        if name.startswith("test_") and callable(test):
            test()
            print(f"PASS {name}")
