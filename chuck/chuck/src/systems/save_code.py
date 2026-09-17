"""A whole save, as sixteen characters the player can carry.

    X7B3-K9QW-2M4X-H8VN

Seventy bits of game and two check characters, written in Crockford
base32. That alphabet drops I, L, O and U, so there is no squinting at a
screenshot wondering whether a character is a one or an ell, and it is
case-insensitive, so it does not matter how it comes back. All
thirty-two of its characters are already in the bitmap font.

    version   4   which layout this is
    entry     8   a slot in SAVE_ENTRIES: the door he came in by
    sanity    7   0..100
    flags    25   one bit per SAVE_FLAGS entry
    cigs     16   clamped, see below
    deaths   10   clamped
                  -- seventy bits, exactly fourteen characters --
    check     2 characters

The two registries this is written against are frozen -- see
`save_registry`. A code is positions in those tuples, so reordering one
silently changes what every code in the wild means.

On the two check characters
---------------------------

They are Reed-Solomon parity over GF(32), computed so that both
syndromes of the sixteen-character word come out zero. Ten bits, where a
truncated hash would need thirty-two to feel as safe, because this is
not a hash and does not fail like one:

    any one wrong character          always caught
    any two wrong characters         always caught
    any two characters swapped       always caught  (two wrong characters)

Not "almost always" -- the minimum distance of the code is three, so a
word with one or two symbols altered cannot be another valid word. A
truncated hash only ever gives a probability, however many bits it is
given. For the errors a player actually makes, ten designed bits beat
thirty-two undesigned ones and cost five characters less.

Three or more wrong characters fall back to chance: one in 1024 to pass
parity, and then the version has to read as ours and the entry has to
name a door that exists, which together leave roughly one in thirty
thousand. That is the cost, and it buys a code short enough to read down
a phone line.

The word is masked with a fixed keystream before it is written out. That
is not security and cannot be -- the mask ships inside the game, and in
a browser build it sits in readable JavaScript. It is there so a code
looks like a code rather than like its own field layout, and so editing
one by hand takes more than a moment's thought. Masking is symbol-wise,
so it cannot turn one wrong character into two: every guarantee above
survives it. A single-player game whose save the player holds cannot be
made tamper-proof, and pretending otherwise only costs effort that could
go somewhere useful.
"""

from __future__ import annotations

from dataclasses import replace

from src.systems import save_registry as registry
from src.systems.save import SaveRecord


CODE_VERSION = 1

# (name, bits), most significant first. The order is part of the format.
LAYOUT: tuple[tuple[str, int], ...] = (
    ("version", 4),
    ("entry", 8),
    ("sanity", 7),
    ("flags", 25),
    ("cigarettes", 16),
    ("deaths", 10),
)
PAYLOAD_BITS = sum(width for _name, width in LAYOUT)

# Crockford base32: no I, L, O or U.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
# What a player might type instead, because the shapes are the shapes.
# U is not among them: Crockford leaves it out of the alphabet on
# purpose, so a U in a code is a wrong character rather than a near miss.
ALIASES = {"I": "1", "L": "1", "O": "0"}

BITS_PER_SYMBOL = 5
MESSAGE_SYMBOLS = PAYLOAD_BITS // BITS_PER_SYMBOL      # 14, exactly
PARITY_SYMBOLS = 2
CODE_LENGTH = MESSAGE_SYMBOLS + PARITY_SYMBOLS         # 16
GROUP = 4

MAX_CIGARETTES = (1 << 16) - 1
MAX_DEATHS = (1 << 10) - 1


class SaveCodeError(ValueError):
    """A code that cannot be read, with a line to show the player."""


# ----------------------------------------------------------------------
# GF(32), for the parity symbols
# ----------------------------------------------------------------------
# x^5 + x^2 + 1. Addition is XOR; multiplication goes round the log
# tables, which is quite fast enough for two symbols once a menu.
_MODULUS = 0b100101
_EXP: list[int] = [0] * 62
_LOG: list[int] = [0] * 32
_value = 1
for _power in range(31):
    _EXP[_power] = _value
    _EXP[_power + 31] = _value
    _LOG[_value] = _power
    _value <<= 1
    if _value & 0b100000:
        _value ^= _MODULUS


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


def _syndromes(word: list[int]) -> tuple[int, int]:
    """The two sums a valid word drives to zero."""
    plain = even = 0
    for power, symbol in enumerate(word):
        plain ^= symbol
        even ^= _multiply(symbol, _EXP[power % 31])
    return plain, even


def _parity(message: list[int]) -> tuple[int, int]:
    """The two symbols that take both syndromes of message+parity to zero."""
    plain, even = _syndromes(message)
    k = len(message)
    # p0 + p1 = plain ; p0*a^k + p1*a^(k+1) = even
    first = _divide(even ^ _multiply(plain, _EXP[(k + 1) % 31]),
                    _multiply(_EXP[k % 31], 1 ^ _EXP[1]))
    return first, first ^ plain


# A fixed keystream, one symbol per position. See the module docstring:
# obscurity, not security. Any fixed sequence does the job; this one is
# written down so it can never quietly change.
_MASK = (17, 3, 28, 9, 22, 14, 31, 5, 11, 26, 2, 19, 7, 30, 13, 24)


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
        "version": CODE_VERSION,
        "entry": entry,
        "sanity": max(0, min(record.sanity, (1 << 7) - 1)),
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
    sixteen bits hold. Wrapping round to nothing would be worse than
    stopping.
    """
    payload = _pack(record)
    message = [(payload >> (BITS_PER_SYMBOL * (MESSAGE_SYMBOLS - 1 - index)))
               & 31 for index in range(MESSAGE_SYMBOLS)]
    word = _mask(message + list(_parity(message)))
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
    if any(_syndromes(word)):
        raise SaveCodeError("That code has a character wrong in it.")

    payload = 0
    for symbol in word[:MESSAGE_SYMBOLS]:
        payload = payload << BITS_PER_SYMBOL | symbol

    values, rest = {}, payload
    for name, width in reversed(LAYOUT):
        values[name] = rest & (1 << width) - 1
        rest >>= width
    if values["version"] != CODE_VERSION:
        raise SaveCodeError(
            "That code is from a different version of the game.")
    try:
        checkpoint_id = registry.entry_id(values["entry"])
    except ValueError as exc:
        raise SaveCodeError(
            "That code is for a place this version does not have.") from exc

    return SaveRecord(
        checkpoint_id=checkpoint_id,
        sanity=values["sanity"],
        progress_flags=registry.bits_to_flags(values["flags"]),
        cigarettes=values["cigarettes"],
        deaths=values["deaths"],
        spoken=(),
    )


def for_display(record: SaveRecord) -> str:
    """The code, with `spoken` dropped -- a code never carries it."""
    return encode(replace(record, spoken=()))
