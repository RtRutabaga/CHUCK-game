"""Text helpers.

wrap_text is a pure function (the measurer is injected) so word
wrapping is unit-testable without pygame or fonts.
"""

from __future__ import annotations

from typing import Callable


def wrap_text(
    text: str, max_width: int, measure: Callable[[str], int]
) -> list[str]:
    """Split text into lines no wider than max_width.

    measure(s) returns the pixel width of s. Words longer than
    max_width get a line of their own (never dropped, never split).
    """
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if measure(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
