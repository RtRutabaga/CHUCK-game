"""A whole save, as twenty-one characters the player can carry.

    X7B3K-9QW2M-4XH8V-NP2RT-C

Seventy bits of game plus a thirty-two bit checksum, written in
Crockford base32. That alphabet drops I, L, O and U, so there is no
squinting at a screenshot wondering whether a character is a one or an
ell, and it is case-insensitive, so it does not matter how it comes
back. All thirty-two of its characters are already in the bitmap font.

    version   4   which layout this is
    entry     8   a slot in SAVE_ENTRIES: the door he came in by
    sanity    7   0..100
    flags    25   one bit per SAVE_FLAGS entry
    cigs     16   clamped, see below
    deaths   10   clamped
    check    32   truncated HMAC

The two registries this is written against are frozen -- see
`save_registry`. A code is positions in those tuples, so reordering one
silently changes what every code in the wild means.

On the checksum: the key ships inside the game, and in a browser build
it sits in readable JavaScript. This is not security and cannot be. It
is here so that a mistyped code says "that is not a code" instead of
loading a game with one wrong bit in it, and so that editing a code by
hand takes more than a moment's thought. A single-player game whose save
the player holds cannot be made tamper-proof, and pretending otherwise
only costs effort that could go somewhere useful.
"""

from __future__ import annotations

from dataclasses import replace
import hmac
import hashlib

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
CHECK_BITS = 32
TOTAL_BITS = PAYLOAD_BITS + CHECK_BITS

# Crockford base32: no I, L, O or U.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
# What a player might type instead, because the shapes are the shapes.
# U is not among them: Crockford leaves it out of the alphabet on
# purpose, so a U in a code is a wrong character rather than a near miss.
ALIASES = {"I": "1", "L": "1", "O": "0"}
CODE_LENGTH = -(-TOTAL_BITS // 5)        # 21
GROUP = 5

# Not a secret. See the note above.
_KEY = b"chuck-save-code-v1"

MAX_CIGARETTES = (1 << 16) - 1
MAX_DEATHS = (1 << 10) - 1


class SaveCodeError(ValueError):
    """A code that cannot be read, with a line to show the player."""


def _check_bits(payload: int) -> int:
    raw = payload.to_bytes(-(-PAYLOAD_BITS // 8), "big")
    mac = hmac.new(_KEY, raw, hashlib.sha256).digest()
    return int.from_bytes(mac[:4], "big")


def encode(record: SaveRecord) -> str:
    """Pack a save into its code. Counters clamp rather than overflow.

    Clamping matters because cigarettes are farmable: loose ones respawn
    with the map, so a long enough session can push the total past what
    sixteen bits hold. Wrapping round to nothing would be worse than
    stopping.
    """
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

    number = payload << CHECK_BITS | _check_bits(payload)
    digits = []
    for _ in range(CODE_LENGTH):
        digits.append(ALPHABET[number & 31])
        number >>= 5
    text = "".join(reversed(digits))
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
    number = 0
    for char in cleaned:
        position = ALPHABET.find(char)
        if position < 0:
            raise SaveCodeError(f"'{char}' is not part of a save code.")
        number = number << 5 | position

    payload = number >> CHECK_BITS
    if payload >= 1 << PAYLOAD_BITS:
        raise SaveCodeError("That code is not one of ours.")
    if number & (1 << CHECK_BITS) - 1 != _check_bits(payload):
        raise SaveCodeError("That code has a character wrong in it.")

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
