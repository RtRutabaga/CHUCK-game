"""The save code: twelve characters, and what has to stay true of them.

The codec is pure -- a record in, a string out -- so it can be held to
the bit. The test that matters most is the golden one: a code written
down as a literal, with the save it has to decode to. Change the field
layout, the alphabet, the mask, or the order of either registry, and
that test fails instead of every code in the wild quietly meaning
something else.

After it come the parity tests. One check character buys two
guarantees and nothing else: a single wrong character and a single
transposition are always caught, and these tests try every one of
both across a spread of codes rather than sampling them. Anything
worse is a one-in-thirty-two coin, and there is a test that measures
that coin too, so the cost of a twelve-character code stays written
down where the next person will read it.
"""

import itertools
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.systems import save_code as codec
from src.systems import save_registry as registry
from src.systems.save import SaveRecord


# Written down, not computed. If this changes, codes people hold break.
GOLDEN_CODE = "KMW9-J6ZP-2T5D"
GOLDEN = SaveRecord(
    checkpoint_id="temple_9",
    # Not carried by a code. Written here as something other than
    # SANITY_START so the test below proves it is dropped.
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
    assert decoded.sanity == config.SANITY_START != GOLDEN.sanity
    assert set(decoded.progress_flags) == set(GOLDEN.progress_flags)
    assert decoded.cigarettes == GOLDEN.cigarettes
    assert decoded.deaths == GOLDEN.deaths


def test_a_code_is_twelve_characters() -> None:
    assert codec.CODE_LENGTH == 12
    assert len(codec.normalise(GOLDEN_CODE)) == 12
    # Grouped for reading, and the grouping is not part of the code.
    assert GOLDEN_CODE.count("-") == 2
    # Eleven characters of save and one of parity, with nothing
    # spare in the fifty-five bits.
    assert codec.PAYLOAD_BITS == 55
    assert codec.MESSAGE_SYMBOLS * codec.BITS_PER_SYMBOL == codec.PAYLOAD_BITS
    assert codec.PARITY_SYMBOLS == 1


def test_nothing_further_can_come_out_without_losing_a_field() -> None:
    """The floor, asserted, so a later shortening has to face it.

    A hundred and forty-seven doors need eight bits however they are
    written. The twenty-five progress flags are independent -- they
    gate the captain, the cabin and the cartons -- and not one of
    them follows from where Chuck is standing, so they cannot be
    packed against the entry. That is thirty-three bits before a
    single cigarette, a death, or a check character is written.
    """
    widths = dict(codec.LAYOUT)
    assert widths["entry"] == 8
    assert len([e for e in registry.SAVE_ENTRIES if e]) > 128
    assert widths["flags"] == len(registry.SAVE_FLAGS) == 25
    assert widths["entry"] + widths["flags"] == 33
    # And sanity is not among them at all.
    assert "sanity" not in widths


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
        assert back.sanity == config.SANITY_START
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


def _spread(count: int) -> list[SaveRecord]:
    """A seeded spread of saves, so parity is tried on more than one code."""
    rng = random.Random(1994)
    doors = [entry for entry in registry.SAVE_ENTRIES if entry]
    out = []
    for _ in range(count):
        flags = tuple(sorted(flag for flag in registry.SAVE_FLAGS
                             if rng.random() < 0.5))
        out.append(SaveRecord(rng.choice(doors), rng.randint(1, 100), flags,
                              rng.randint(0, codec.MAX_CIGARETTES),
                              rng.randint(0, codec.MAX_DEATHS)))
    return out


def test_no_single_wrong_character_gets_past_the_parity() -> None:
    """Every substitution at every position, across a spread of codes.

    Guaranteed rather than likely: one wrong symbol leaves the first
    syndrome equal to the error itself, which is non-zero by definition.
    """
    tried = 0
    for record in [GOLDEN] + _spread(24):
        clean = codec.normalise(codec.encode(record))
        for index, char in enumerate(clean):
            for other in codec.ALPHABET:
                if other == char:
                    continue
                tried += 1
                _raises(clean[:index] + other + clean[index + 1:])
    assert tried == 25 * codec.CODE_LENGTH * (len(codec.ALPHABET) - 1) == 9300


def test_two_wrong_characters_are_a_coin_and_that_is_the_deal() -> None:
    """One check character cannot promise what two could.

    Two wrong characters are caught about thirty-one times in
    thirty-two, and that last time loads a different save instead of
    refusing. It is the price of the character, measured here rather
    than assumed, so nobody has to rediscover it.
    """
    caught = tried = 0
    for record in _spread(2):
        clean = codec.normalise(codec.encode(record))
        for first, second in itertools.combinations(range(len(clean)), 2):
            for one in codec.ALPHABET:
                if one == clean[first]:
                    continue
                for two in codec.ALPHABET:
                    if two == clean[second]:
                        continue
                    tried += 1
                    try:
                        codec.decode(clean[:first] + one
                                     + clean[first + 1:second] + two
                                     + clean[second + 1:])
                    except codec.SaveCodeError:
                        caught += 1
    assert tried == 2 * 66 * 31 * 31 == 126_852
    assert 0.95 < caught / tried < 0.98, caught / tried


def test_two_characters_the_wrong_way_round_are_caught() -> None:
    """A transposition is two wrong characters, so it cannot slip by."""
    tried = 0
    for record in [GOLDEN] + _spread(40):
        clean = codec.normalise(codec.encode(record))
        for first, second in itertools.combinations(range(len(clean)), 2):
            if clean[first] == clean[second]:
                continue
            swapped = list(clean)
            swapped[first], swapped[second] = swapped[second], swapped[first]
            tried += 1
            _raises("".join(swapped))
    assert tried > 2000


def test_a_code_made_of_nothing_in_particular_is_almost_never_taken() -> None:
    """The one place parity is weaker than the hash it replaced.

    One chance in thirty-two to pass parity, and then the entry has to
    name one of the hundred and forty-seven doors that exist: about
    one string in fifty-six. A player who invents a code will
    occasionally be handed a real game, which is the acknowledged
    cost of twelve characters and not a defect.
    """
    rng = random.Random(4)
    taken = 0
    attempts = 20000
    for _ in range(attempts):
        try:
            codec.decode("".join(rng.choice(codec.ALPHABET)
                                 for _ in range(codec.CODE_LENGTH)))
        except codec.SaveCodeError:
            continue
        taken += 1
    assert attempts // 80 < taken < attempts // 30, (
        f"{taken} of {attempts} random strings")


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
    assert "12 characters" in _raises("ABC")
    assert "12 characters" in _raises(GOLDEN_CODE + "XXXX")
    # U is not in the alphabet, and is not an alias for anything...
    assert "not part of" in _raises("U" * 12)
    # ...and neither is punctuation.
    assert "not part of" in _raises("!" + codec.normalise(GOLDEN_CODE)[1:])


def test_a_code_from_another_version_mostly_fails_the_check() -> None:
    """There is no version field left; the check constant carries it.

    A code built by a later format checks out against that format's
    seed and not against this one, so it is refused as mistyped rather
    than named. Thirty-one times in thirty-two -- the other time it
    decodes as some other save. That is the whole of the version
    handling a twelve-character code can afford, and it is why the seed
    must change whenever the layout does.
    """
    original = codec._SEED
    refused = 0
    try:
        for record in _spread(40):
            codec._SEED = original + 1
            later = codec.encode(record)
            codec._SEED = original
            try:
                codec.decode(later)
            except codec.SaveCodeError:
                refused += 1
    finally:
        codec._SEED = original
    assert refused >= 36, refused


def test_the_parity_is_the_arithmetic_it_claims_to_be() -> None:
    """The syndrome of a real code is zero, and GF(32) is a field."""
    for record in [GOLDEN] + _spread(8):
        word = codec._mask([codec.ALPHABET.index(char) for char
                            in codec.normalise(codec.encode(record))])
        assert codec._syndrome(word) == 0
    for value in range(1, 32):
        assert codec._divide(codec._multiply(value, 7), 7) == value
        assert codec._multiply(value, 1) == value
        assert codec._multiply(value, 0) == 0


def test_the_mask_hides_the_layout_without_hiding_an_error() -> None:
    """Symbol-wise, so one wrong character stays exactly one wrong.

    The mask is obscurity and nothing else -- it ships inside the game.
    What it must not do is cost the parity its guarantee, which it
    cannot, because it never moves a difference to another position.
    """
    word = list(range(codec.CODE_LENGTH))
    assert codec._mask(codec._mask(word)) == word
    assert codec._mask(word) != word
    changed = list(word)
    changed[5] ^= 9
    differing = [index for index, (before, after)
                 in enumerate(zip(codec._mask(word), codec._mask(changed)))
                 if before != after]
    assert differing == [5]


def test_a_code_carries_neither_hellos_nor_sanity() -> None:
    """The two fields a code drops, on purpose.

    `spoken` would need a positional key and is cosmetic. Sanity went
    with it to buy a character and a half: a code resumes at a door on a
    fresh sixty, the way walking in does. The local save keeps both.
    """
    assert codec.decode(codec.encode(
        SaveRecord("temple_1", 100, (), 0, 0))).sanity == config.SANITY_START
    assert codec.encode(SaveRecord("temple_1", 3, (), 0, 0)) == codec.encode(
        SaveRecord("temple_1", 99, (), 0, 0))
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
