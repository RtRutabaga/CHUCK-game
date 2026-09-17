"""Where a count stops being a number.

A save code is twelve characters, so the cigarette total gets thirteen
bits and the death count nine. Past those, a number has to do something,
and every option but one is a lie: wrapping round to nothing, or sitting
at 8191 as though Chuck had put exactly that many away.

So it stops being a number and becomes "a lot".

    Cigarettes: a lot          Past counting. Worth it.
    Deaths: a lot              We stopped counting.

Which is the honest answer, and the funnier one. A rat who has smoked
eight thousand cigarettes does not know how many he has smoked. The
ceiling is no longer a clamp to apologise for in a comment; it is the
top of the scale, and the scale ends in a shrug.

Both limits are reachable only by farming -- loose cigarettes respawn
with their map, and dying five hundred times takes some doing -- so in
an ordinary playthrough neither is ever seen. That is the point. "A lot"
is the game noticing that somebody has gone well past what it was
counting for.

The limits live here rather than in `save_code` because they are a rule
about Chuck, not about the wire format. The format is sized to them, and
a test holds the two together.
"""

from __future__ import annotations


A_LOT = "a lot"

# Thirteen bits and nine, the two counter fields of a save code.
CIGARETTE_LIMIT = (1 << 13) - 1      # 8191
DEATH_LIMIT = (1 << 9) - 1           # 511


def a_lot(value: int, limit: int) -> bool:
    """Whether this count has gone past what the game will put a number to."""
    return value >= limit


def figure(value: int, limit: int, prefix: str = "") -> str:
    """The count as it is written, which past the limit is not a count.

    The prefix (the HUD's "x") goes with the number. "x a lot" is not a
    thing anybody says, so at the limit the phrase stands on its own.
    """
    if a_lot(value, limit):
        return A_LOT
    return f"{prefix}{value}"
