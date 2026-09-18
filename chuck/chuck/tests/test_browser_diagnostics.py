"""Timing reports must not disguise stalls or count hidden-tab time."""

from types import SimpleNamespace
from src.core.browser_diagnostics import (
    FrameReporter, PadWatch, browser_reporter)


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


class _Pad:
    """A gamepad that reports exactly the buttons it is told to."""

    def __init__(self, buttons, hats=()):
        self._buttons = buttons
        self._hats = hats

    def get_name(self):
        return "Test Pad"

    def get_numbuttons(self):
        return len(self._buttons)

    def get_numhats(self):
        return len(self._hats)

    def get_numaxes(self):
        return 4

    def get_button(self, index):
        return self._buttons[index]

    def get_hat(self, index):
        return self._hats[index]

    def get_init(self):
        return True


class _Input:
    def __init__(self, *down):
        self._down = set(down)

    def is_down(self, action):
        return action in self._down


def _watch(messages, pad):
    watch = PadWatch(messages.append)
    watch._pad = lambda: pad
    return watch


def test_a_button_reports_which_action_it_reached() -> None:
    messages = []
    pad = _Pad([False, False, False, False])
    watch = _watch(messages, pad)
    game = SimpleNamespace(input=_Input())
    watch.poll(game)
    assert "Test Pad" in messages[0] and "4 buttons" in messages[0]

    pad._buttons[1] = True
    game = SimpleNamespace(input=_Input("jump", "back"))
    watch.poll(game)
    assert "button 1 down" in messages[1]
    assert "reached: jump, back" in messages[1]


def test_a_button_that_reaches_nothing_says_so() -> None:
    """The Xbox case: a press arrives and no action fires."""
    messages = []
    pad = _Pad([False, False])
    watch = _watch(messages, pad)
    watch.poll(SimpleNamespace(input=_Input()))
    pad._buttons[0] = True
    watch.poll(SimpleNamespace(input=_Input()))
    assert "button 0 down" in messages[-1]
    assert "reached: nothing" in messages[-1]


def test_a_held_button_is_reported_once() -> None:
    messages = []
    pad = _Pad([True])
    watch = _watch(messages, pad)
    game = SimpleNamespace(input=_Input("interact"))
    for _ in range(5):
        watch.poll(game)
    assert sum("button 0 down" in m for m in messages) == 1


def test_no_pad_is_not_an_error() -> None:
    messages = []
    watch = PadWatch(messages.append)
    watch._pad = lambda: None
    watch.poll(SimpleNamespace(input=_Input()))
    assert messages == []


def test_diagnostics_are_explicitly_opt_in():
    for search in ("", "?diagnostics=0", "?otherdiagnostics=1"):
        window = SimpleNamespace(location=SimpleNamespace(search=search))
        assert browser_reporter(window) is None


if __name__ == "__main__":
    for name, test in sorted(globals().copy().items()):
        if name.startswith("test_") and callable(test):
            test()
            print(f"PASS {name}")
