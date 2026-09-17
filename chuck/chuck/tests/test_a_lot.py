"""Counts that stop being counts.

The cigarette total and the death count both have a ceiling, because a
save code is twelve characters. Past it the game says "a lot" instead of
a number -- in the HUD, on the credits roll, and inside the code, all
three agreeing, which is the part worth testing. A player who farms past
the ceiling, saves, and pastes the code back should still have a lot.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.scenes.credits_scene import stats_lines
from src.systems import save_code as codec
from src.systems import tally
from src.systems.cigarettes import CigaretteLedger
from src.systems.deaths import DeathCounter
from src.systems.save import SaveRecord
from src.ui.bitmap_font import GLYPH_ORDER
from src.ui.hud import HUD


def test_a_number_stays_a_number_until_the_ceiling() -> None:
    assert tally.figure(0, tally.DEATH_LIMIT) == "0"
    assert tally.figure(7, tally.DEATH_LIMIT) == "7"
    assert tally.figure(tally.DEATH_LIMIT - 1, tally.DEATH_LIMIT) == "510"
    assert not tally.a_lot(tally.DEATH_LIMIT - 1, tally.DEATH_LIMIT)


def test_at_the_ceiling_and_past_it_the_answer_is_a_lot() -> None:
    for value in (tally.DEATH_LIMIT, tally.DEATH_LIMIT + 1, 99999):
        assert tally.a_lot(value, tally.DEATH_LIMIT)
        assert tally.figure(value, tally.DEATH_LIMIT) == "a lot"
    for value in (tally.CIGARETTE_LIMIT, tally.CIGARETTE_LIMIT + 5000):
        assert tally.figure(value, tally.CIGARETTE_LIMIT) == "a lot"


def test_the_huds_x_goes_with_the_number_and_not_with_the_phrase() -> None:
    """"x12" reads; "x a lot" does not."""
    assert tally.figure(12, tally.CIGARETTE_LIMIT, "x") == "x12"
    assert tally.figure(20000, tally.CIGARETTE_LIMIT, "x") == "a lot"


def test_the_phrase_is_something_the_pixel_font_can_draw() -> None:
    for char in tally.A_LOT:
        assert char in GLYPH_ORDER, char


def test_the_hud_draws_the_phrase_once_the_count_is_past_it() -> None:
    pygame.display.init()
    pygame.display.set_mode((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
    from src.core.assets import AssetManager

    font = AssetManager().bitmap_font()
    cigarettes, deaths = CigaretteLedger(), DeathCounter()
    cigarettes.replace(20000)
    deaths.replace(tally.DEATH_LIMIT + 3)

    class _Sanity:
        fraction = 1.0
        current = config.SANITY_MAX
        maximum = config.SANITY_MAX

    hud = HUD(_Sanity(), font=font, cigarettes=cigarettes, deaths=deaths)
    surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
    surface.fill((0, 0, 0))
    hud.draw(surface)

    # Both counters are up there, so the phrase is drawn twice and the
    # digits of neither total are anywhere on screen.
    wanted = font.render(tally.A_LOT)
    assert _appearances(surface, wanted) == 2
    assert _appearances(surface, font.render("20000")) == 0
    assert _appearances(surface, font.render("514")) == 0


def test_the_credits_say_it_too_and_change_their_remark() -> None:
    ordinary = stats_lines(9, 12, 3, 3)
    assert ordinary[0] == ("Deaths: 9", "Rats have short lives.")
    assert ordinary[1] == ("Cigarettes: 12", "Worth it.")

    plenty = stats_lines(tally.DEATH_LIMIT, tally.CIGARETTE_LIMIT + 1, 3, 3)
    assert plenty[0] == ("Deaths: a lot", "We stopped counting.")
    assert plenty[1] == ("Cigarettes: a lot", "Past counting. Worth it.")
    # The cartons are three of three and stay a number: they have no
    # ceiling to run into.
    assert plenty[2] == ("Premium cartons: 3/3", "Bobert is thrilled.")


def test_a_lot_survives_the_code_and_comes_back_a_lot() -> None:
    """The whole point: farm past the ceiling, save, paste it back.

    The code cannot hold twenty thousand, and does not have to. It holds
    "a lot", and what comes out the other side reads as "a lot" as well,
    so the player is never shown a number they did not earn.
    """
    farmed = SaveRecord("temple_1", 60, (), 20000, 900)
    back = codec.decode(codec.encode(farmed))
    assert back.cigarettes == tally.CIGARETTE_LIMIT
    assert back.deaths == tally.DEATH_LIMIT
    assert tally.figure(back.cigarettes, tally.CIGARETTE_LIMIT) == "a lot"
    assert tally.figure(back.deaths, tally.DEATH_LIMIT) == "a lot"
    assert stats_lines(back.deaths, back.cigarettes, 0, 3)[0][0] \
        == "Deaths: a lot"


def test_a_count_under_the_ceiling_is_carried_exactly() -> None:
    """No rounding on the way through: only the ceiling is fuzzy."""
    for cigarettes, deaths in ((0, 0), (1, 1), (193, 12),
                               (tally.CIGARETTE_LIMIT - 1,
                                tally.DEATH_LIMIT - 1)):
        back = codec.decode(codec.encode(
            SaveRecord("temple_1", 60, (), cigarettes, deaths)))
        assert (back.cigarettes, back.deaths) == (cigarettes, deaths)
        assert tally.figure(back.cigarettes, tally.CIGARETTE_LIMIT) \
            == str(cigarettes)


def test_the_code_fields_are_sized_to_the_ceilings() -> None:
    """One rule, in one place. Widen a field and the ceiling moves with it.

    If these ever came apart, a code would clamp somewhere the game was
    still happily showing a number, and a save would quietly lose count.
    """
    widths = dict(codec.LAYOUT)
    assert codec.MAX_CIGARETTES == tally.CIGARETTE_LIMIT
    assert codec.MAX_DEATHS == tally.DEATH_LIMIT
    assert tally.CIGARETTE_LIMIT == (1 << widths["cigarettes"]) - 1
    assert tally.DEATH_LIMIT == (1 << widths["deaths"]) - 1


def test_the_ceilings_are_out_of_reach_of_an_ordinary_game() -> None:
    """"A lot" is for farming, not for playing.

    There are about 193 cigarettes authored in the world. A player who
    finds every one of them, and dies far more than anybody should, is
    still nowhere near either ceiling -- which is what makes the phrase
    a joke about somebody's afternoon rather than a limitation.
    """
    assert tally.CIGARETTE_LIMIT > 193 * 40
    assert tally.DEATH_LIMIT > 500


def _appearances(surface, wanted) -> int:
    """How many times `wanted` is drawn on `surface`, by exact pixel shape.

    The surface is filled black first, so every lit pixel of the phrase
    has to be lit and every gap between them has to still be black --
    otherwise a run of other glyphs could cover the shape by accident.
    """
    width, height = wanted.get_size()
    lit, dark = [], []
    for y in range(height):
        for x in range(width):
            (lit if wanted.get_at((x, y))[3] > 0 else dark).append((x, y))
    assert lit, "the phrase should have pixels in it"
    found = 0
    for top in range(surface.get_height() - height):
        for left in range(surface.get_width() - width):
            if all(surface.get_at((left + x, top + y))[:3] != (0, 0, 0)
                   for x, y in lit) and all(
                       surface.get_at((left + x, top + y))[:3] == (0, 0, 0)
                       for x, y in dark):
                found += 1
    return found


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
    print("All a-lot tests passed.")


if __name__ == "__main__":
    _run_all()
