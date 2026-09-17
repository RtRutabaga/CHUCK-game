"""The save code: twenty-one characters, and what has to stay true of them.

The codec is pure -- a record in, a string out -- so it can be held to
the bit. The test that matters most is the golden one: a code written
down as a literal, with the save it has to decode to. Change the field
layout, the alphabet, the key, or the order of either registry, and that
test fails instead of every code in the wild quietly meaning something
else.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.systems import save_code as codec
from src.systems import save_registry as registry
from src.systems.save import SaveRecord


# Written down, not computed. If this changes, codes people hold break.
GOLDEN_CODE = "08NAE-008G0-4T80Z-NY02X-F"
GOLDEN = SaveRecord(
    checkpoint_id="temple_9",
    sanity=41,
    progress_flags=("captain_chest_opened", "chult_reached",
                    "sewer_completed", "waterdeep_returned"),
    cigarettes=1234,
    deaths=7,
)


def _raises(text: str) -> str:
    try:
        codec.decode(text)
    except codec.SaveCodeError as exc:
        return str(exc)
    raise AssertionError(f"{text!r} should not have decoded")


def test_the_golden_code_still_means_what_it_meant() -> None:
    assert codec.encode(GOLDEN) == GOLDEN_CODE
    decoded = codec.decode(GOLDEN_CODE)
    assert decoded.checkpoint_id == GOLDEN.checkpoint_id
    assert decoded.sanity == GOLDEN.sanity
    assert set(decoded.progress_flags) == set(GOLDEN.progress_flags)
    assert decoded.cigarettes == GOLDEN.cigarettes
    assert decoded.deaths == GOLDEN.deaths


def test_a_code_is_twenty_one_characters() -> None:
    assert codec.CODE_LENGTH == 21
    assert len(codec.normalise(GOLDEN_CODE)) == 21
    # Grouped for reading, and the grouping is not part of the code.
    assert GOLDEN_CODE.count("-") == 4


def test_every_door_and_every_extreme_survives_a_round_trip() -> None:
    doors = [entry for entry in registry.SAVE_ENTRIES if entry]
    assert len(doors) >= 100
    for entry in doors:
        assert codec.decode(codec.encode(
            SaveRecord(entry, 60, (), 0, 0))).checkpoint_id == entry

    extremes = (
        SaveRecord(doors[0], 1, (), 0, 0),
        SaveRecord(doors[-1], 100, tuple(registry.SAVE_FLAGS),
                   codec.MAX_CIGARETTES, codec.MAX_DEATHS),
        SaveRecord(doors[len(doors) // 2], 50,
                   ("sewer_completed",), 1, 1),
    )
    for record in extremes:
        back = codec.decode(codec.encode(record))
        assert back.checkpoint_id == record.checkpoint_id
        assert back.sanity == record.sanity
        assert set(back.progress_flags) == set(record.progress_flags)
        assert back.cigarettes == record.cigarettes
        assert back.deaths == record.deaths


def test_counters_clamp_rather_than_wrap() -> None:
    """Cigarettes are farmable; a long run must not roll over to none.

    Loose cigarettes respawn with their map, so the total has no real
    ceiling. Sixteen bits is plenty for a played-through game, but a
    total that wrapped round to nothing would be worse than one that
    stopped counting.
    """
    huge = SaveRecord("temple_1", 60, (), codec.MAX_CIGARETTES + 5000,
                      codec.MAX_DEATHS + 99)
    back = codec.decode(codec.encode(huge))
    assert back.cigarettes == codec.MAX_CIGARETTES
    assert back.deaths == codec.MAX_DEATHS


def test_no_single_wrong_character_gets_past_the_checksum() -> None:
    """Every substitution at every position, not a sample of them."""
    clean = codec.normalise(GOLDEN_CODE)
    tried = 0
    for index, char in enumerate(clean):
        for other in codec.ALPHABET:
            if other == char:
                continue
            tried += 1
            _raises(clean[:index] + other + clean[index + 1:])
    assert tried == len(clean) * (len(codec.ALPHABET) - 1) == 651


def test_it_reads_a_code_however_it_comes_back() -> None:
    """Pasted, retyped, shouted, or with the dashes lost on the way."""
    wanted = codec.decode(GOLDEN_CODE)
    for variant in (GOLDEN_CODE.lower(),
                    GOLDEN_CODE.replace("-", ""),
                    GOLDEN_CODE.replace("-", " "),
                    f"  {GOLDEN_CODE}  ",
                    GOLDEN_CODE.replace("-", "_")):
        assert codec.decode(variant) == wanted, variant

    # Crockford's point: the characters that look like other characters
    # are read as the ones they look like, so a code read off a screen
    # still works. O is zero, I and L are one.
    swapped = codec.normalise(GOLDEN_CODE).replace("0", "O").replace("1", "I")
    assert codec.decode(swapped) == wanted


def test_a_code_that_is_not_one_says_so() -> None:
    assert "Enter" in _raises("")
    assert "21 characters" in _raises("ABC")
    assert "21 characters" in _raises(GOLDEN_CODE + "XXXX")
    # U is not in the alphabet, and is not an alias for anything...
    assert "not part of" in _raises("U" * 21)
    # ...and neither is punctuation.
    assert "not part of" in _raises("!" + codec.normalise(GOLDEN_CODE)[1:])


def test_a_code_from_another_version_is_refused_not_misread() -> None:
    """The version rides inside the checksum, so it cannot be faked in.

    Built the way a later build would build it, with this build's key,
    so the code checks out and is still refused on its version alone --
    which is the case that matters. A code from a build with a different
    key fails the checksum first.
    """
    payload = 0
    values = {"version": codec.CODE_VERSION + 1, "entry": 3, "sanity": 60,
              "flags": 0, "cigarettes": 0, "deaths": 0}
    for name, width in codec.LAYOUT:
        payload = payload << width | values[name]
    number = payload << codec.CHECK_BITS | codec._check_bits(payload)
    digits = []
    for _ in range(codec.CODE_LENGTH):
        digits.append(codec.ALPHABET[number & 31])
        number >>= 5
    assert "different version" in _raises("".join(reversed(digits)))


def test_a_code_never_carries_who_has_said_hello() -> None:
    """`spoken` is the one field a code drops, on purpose."""
    record = SaveRecord("temple_1", 60, (), 0, 0,
                        spoken=(("waterdeep_docks", 10, 20, "dock_worker"),))
    assert codec.for_display(record) == codec.encode(
        SaveRecord("temple_1", 60, (), 0, 0))
    assert codec.decode(codec.for_display(record)).spoken == ()


def test_an_unknown_door_is_refused_on_the_way_in_and_out() -> None:
    try:
        codec.encode(SaveRecord("no_such_door", 60, (), 0, 0))
    except codec.SaveCodeError as exc:
        assert "not a save entry" in str(exc)
    else:
        raise AssertionError("an unknown door should not encode")


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All save code tests passed.")


if __name__ == "__main__":
    _run_all()
