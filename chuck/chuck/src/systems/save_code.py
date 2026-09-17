"""A whole save, as twelve characters the player can carry.

    K6PT-6EX1-BV41

Fifty-five bits of game and one check character, written in Crockford
base32. That alphabet drops I, L, O and U, so there is no squinting at a
screenshot wondering whether a character is a one or an ell, and it is
case-insensitive, so it does not matter how it comes back. All
thirty-two of its characters are already in the bitmap font.

    entry     8   a slot in SAVE_ENTRIES: the door he came in by
    flags    25   one bit per SAVE_FLAGS entry
    cigs     13   clamped, see below
    deaths    9   clamped
                  -- fifty-five bits, exactly eleven characters --
    check     1 character

Eleven and twenty-five are the floor. A hundred and forty-seven doors
need eight bits however they are written, and the twenty-five progress
flags are independent of each other -- they gate the captain, the cabin
and the cartons, and none of them can be derived from where Chuck is
standing. Everything else has been cut to the bone to get here:

    sanity     dropped. A code resumes at a door with a fresh
               sixty, the same as walking in. The local save still
               carries the exact figure; see below.
    version    dropped. It lives in the check constant instead, so a
               later format refuses most of today's codes as mistyped
               rather than naming the version they came from.
    check      one character instead of two.

The two registries this is written against are frozen -- see
`save_registry`. A code is positions in those tuples, so reordering one
silently changes what every code in the wild means.

On the one check character
--------------------------

Reed-Solomon parity over GF(32), weighted by position, so that the
weighted sum of the twelve characters comes out zero:

    any one wrong character          always caught
    any two characters swapped       always caught
    two or more wrong characters     one in 32 gets through

The first two are guarantees -- one wrong symbol leaves the syndrome
equal to that symbol's error times a non-zero weight, and a swap leaves
it equal to the difference times the difference of two distinct weights.
They are the mistakes a player actually makes when retyping. Everything
worse falls back to one chance in thirty-two, which is the price of the
character that would otherwise be spent on it.

This is not security and does not pretend to be. Fifty-five bits with a
five-bit check, and the mask below shipping inside the game, means a
determined player can work out how to edit a code. That is a deliberate
trade for a code short enough to write on the back of a hand: CHUCK is
single-player, the save is the player's own, and a save the player can
edit is a save the player can carry.

The word is masked with a fixed keystream before it is written out, so a
code looks like a code rather than like its own field layout. Masking is
symbol-wise, so it cannot turn one wrong character into two: both
guarantees above survive it.

What a code does not carry
--------------------------

`spoken` -- who has already introduced themselves -- and now `sanity`
as well. Both are in the local save file, which stays the primary way a
game resumes on a machine that has one. A code is the portable form, and
it carries the things that would be a loss to redo: where Chuck is, what
he has done, what he has collected, and how many times he has died.
"""

from __future__ import annotations

from dataclasses import replace

from src.core import config
from src.systems import save_registry as registry
from src.systems.save import SaveRecord


CODE_VERSION = 1

# (name, bits), most significant first. The order is part of the format.
LAYOUT: tuple[tuple[str, int], ...] = (
    ("entry", 8),
    ("flags", 25),
    ("cigarettes", 13),
    ("deaths", 9),
)
PAYLOAD_BITS = sum(width for _name, width in LAYOUT)

# Crockford base32: no I, L, O or U.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
# What a player might type instead, because the shapes are the shapes.
# U is not among them: Crockford leaves it out of the alphabet on
# purpose, so a U in a code is a wrong character rather than a near miss.
ALIASES = {"I": "1", "L": "1", "O": "0"}

BITS_PER_SYMBOL = 5
MESSAGE_SYMBOLS = PAYLOAD_BITS // BITS_PER_SYMBOL      # 11, exactly
PARITY_SYMBOLS = 1
CODE_LENGTH = MESSAGE_SYMBOLS + PARITY_SYMBOLS         # 12
GROUP = 4

MAX_CIGARETTES = (1 << 13) - 1
MAX_DEATHS = (1 << 9) - 1


class SaveCodeError(ValueError):
    """A code that cannot be read, with a line to show the player."""


# ----------------------------------------------------------------------
# GF(32), for the check character
# ----------------------------------------------------------------------
# x^5 + x^2 + 1. Addition is XOR; multiplication goes round the log
# tables, which is quite fast enough for twelve symbols once a menu.
_MODULUS = 0b100101


def _tables() -> tuple[list[int], list[int]]:
    exp, log, value = [0] * 62, [0] * 32, 1
    for power in range(31):
        exp[power] = exp[power + 31] = value
        log[value] = power
        value <<= 1
        if value & 0b100000:
            value ^= _MODULUS
    return exp, log


_EXP, _LOG = _tables()


def _multiply(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _divide(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("GF(32)")
    if a == 0:
        return 0
    return _EXP[(_LOG[a] - _LOG[b]) % 31]


# The format's version, spent here instead of in the code. Change it and
# yesterday's codes stop checking out, which is the whole of the version
# handling a twelve-character code can afford.
_SEED = CODE_VERSION


def _syndrome(word: list[int]) -> int:
    """The weighted sum a valid word drives to zero.

    Weighted, not plain: a plain sum is blind to two characters swapped
    round, which is exactly the mistake a player retyping makes.
    """
    total = _SEED
    for power, symbol in enumerate(word):
        total ^= _multiply(symbol, _EXP[(power + 1) % 31])
    return total


def _parity(message: list[int]) -> int:
    """The symbol that takes the syndrome of message+parity to zero."""
    return _divide(_syndrome(message), _EXP[(len(message) + 1) % 31])


# A fixed keystream, one symbol per position. See the module docstring:
# obscurity, not security. Any fixed sequence does the job; this one is
# written down so it can never quietly change.
_MASK = (17, 3, 28, 9, 22, 14, 31, 5, 11, 26, 2, 19)


def _mask(word: list[int]) -> list[int]:
    """Its own inverse."""
    return [symbol ^ _MASK[index] for index, symbol in enumerate(word)]


# ----------------------------------------------------------------------
# The code itself
# ----------------------------------------------------------------------
def _pack(record: SaveRecord) -> int:
    try:
        entry = registry.entry_index(record.checkpoint_id)
    except KeyError as exc:
        raise SaveCodeError(str(exc)) from exc

    values = {
        "entry": entry,
        "flags": registry.flags_to_bits(record.progress_flags),
        "cigarettes": max(0, min(record.cigarettes, MAX_CIGARETTES)),
        "deaths": max(0, min(record.deaths, MAX_DEATHS)),
    }
    payload = 0
    for name, width in LAYOUT:
        value = values[name]
        if not 0 <= value < (1 << width):
            raise SaveCodeError(f"{name} does not fit in {width} bits: {value}")
        payload = payload << width | value
    return payload


def encode(record: SaveRecord) -> str:
    """Pack a save into its code. Counters clamp rather than overflow.

    Clamping matters because cigarettes are farmable: loose ones respawn
    with the map, so a long enough session can push the total past what
    thirteen bits hold. Wrapping round to nothing would be worse than
    stopping. `record.sanity` is not written; see the module docstring.
    """
    payload = _pack(record)
    message = [(payload >> (BITS_PER_SYMBOL * (MESSAGE_SYMBOLS - 1 - index)))
               & 31 for index in range(MESSAGE_SYMBOLS)]
    word = _mask(message + [_parity(message)])
    text = "".join(ALPHABET[symbol] for symbol in word)
    return "-".join(text[i:i + GROUP] for i in range(0, len(text), GROUP))


def normalise(text: str) -> str:
    """Strip a code back to its characters: spaces, dashes and case go."""
    out = []
    for char in text.strip().upper():
        if char in "- \t\r\n_":
            continue
        out.append(ALIASES.get(char, char))
    return "".join(out)


def decode(text: str) -> SaveRecord:
    """Read a code, or raise SaveCodeError with something to show.

    Loud rather than quiet: a pasted code is something the player typed,
    and "that is not a code" is more use to them than a silent refusal.
    """
    cleaned = normalise(text)
    if not cleaned:
        raise SaveCodeError("Enter a save code.")
    if len(cleaned) != CODE_LENGTH:
        raise SaveCodeError(
            f"A save code is {CODE_LENGTH} characters; that one is "
            f"{len(cleaned)}.")
    word = []
    for char in cleaned:
        position = ALPHABET.find(char)
        if position < 0:
            raise SaveCodeError(f"'{char}' is not part of a save code.")
        word.append(position)

    word = _mask(word)
    if _syndrome(word):
        raise SaveCodeError("That code has a character wrong in it.")

    payload = 0
    for symbol in word[:MESSAGE_SYMBOLS]:
        payload = payload << BITS_PER_SYMBOL | symbol

    values, rest = {}, payload
    for name, width in reversed(LAYOUT):
        values[name] = rest & (1 << width) - 1
        rest >>= width
    try:
        checkpoint_id = registry.entry_id(values["entry"])
    except ValueError as exc:
        raise SaveCodeError(
            "That code is for a place this version does not have.") from exc

    return SaveRecord(
        checkpoint_id=checkpoint_id,
        # Not carried. A code resumes at the door on a fresh sixty.
        sanity=config.SANITY_START,
        progress_flags=registry.bits_to_flags(values["flags"]),
        cigarettes=values["cigarettes"],
        deaths=values["deaths"],
        spoken=(),
    )


def for_display(record: SaveRecord) -> str:
    """The code, with `spoken` dropped -- a code never carries it."""
    return encode(replace(record, spoken=()))
