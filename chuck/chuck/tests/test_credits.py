"""The end credits: the cast roll, the ending's last image, the cat."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.credits_scene import (
    CAST, FAST, MAX_CAST_H, MAX_CAST_W, SCROLL_SPEED, SPRITE_RIGHT, TEXT_X,
    CreditsScene, render_backdrop, stats_lines)
from src.scenes.title_scene import TitleScene


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    while game.scenes.current is not None:
        game.scenes.pop()
    return directory, game


def test_it_is_a_cast_and_nobody_who_made_it_is_named() -> None:
    words = " ".join(
        f"{section.title} {member.name} {member.line}"
        for section in CAST for member in section.members).lower()
    for credit in ("created", "directed", "designed", "producer", "programm",
                   "written by", "music by", "art by", "thanks", "sean",
                   "kerr", "claude", "anthropic"):
        assert credit not in words, credit
    # Chuck first, the tortle in Chult, and the cartons last of all.
    assert CAST[0].members[0].name == "Chuck"
    assert any(m.name == "The Tortle" for m in CAST[3].members)
    assert CAST[-1].members[-1].name == "Premium Buhetian Halfling Leaf"


def test_every_cast_member_has_a_sprite_that_fits_beside_its_name() -> None:
    directory, game = _game()
    try:
        credits = CreditsScene(game, good=False)
        for section in CAST:
            for member in section.members:
                image = credits._cast_image(member.sprite, member.name)
                assert image is not None, member.name
                width, height = image.get_size()
                assert height <= MAX_CAST_H and width <= MAX_CAST_W, \
                    (member.name, image.get_size())
                assert SPRITE_RIGHT - width >= 0 and SPRITE_RIGHT < TEXT_X
        # Every line is in the pixel font and fits on the screen.
        credits._build_roll()
        for _top, surface, x in credits._rows:
            assert x + surface.get_width() <= config.NATIVE_WIDTH, x
    finally:
        game._shutdown()
        directory.cleanup()


def test_every_section_has_a_backdrop_from_its_own_map() -> None:
    directory, game = _game()
    try:
        for section in CAST:
            image = render_backdrop(game, section.map_name, section.focus)
            assert image.get_height() == config.NATIVE_HEIGHT
            assert image.get_width() >= config.NATIVE_WIDTH
            # Not a black rectangle.
            colours = {image.get_at((x, y))[:3]
                       for x in range(0, image.get_width(), 23)
                       for y in range(0, image.get_height(), 17)}
            assert len(colours) > 4, section.map_name
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_numbers_have_something_to_say() -> None:
    assert stats_lines(0, 12, 3, 3) == [
        ("Deaths: 0", "Not once. Remarkable."),
        ("Cigarettes: 12", "Worth it."),
        ("Premium cartons: 3/3", "Bobert is thrilled."),
    ]
    lines = stats_lines(1, 0, 1, 3)
    assert lines[0][1] == "Just the once."
    assert lines[1][1] == "Not one."
    assert lines[2] == ("Premium cartons: 1/3", "Bobert noticed.")
    assert stats_lines(9, 1, 0, 3)[0][1] == "Rats have short lives."


def _run(game, credits, hold: bool = False) -> dict[str, float]:
    seen: dict[str, float] = {}
    surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
    for _ in range(20000):
        if game.scenes.current is not credits:
            break
        if hold:
            game.input._actions_down.add("interact")
        page = credits.page
        seen[page] = seen.get(page, 0.0) + 0.25
        if seen[page] == 0.25:
            credits.draw(surface)
        game.scenes.update(0.25)
    return seen


def test_the_roll_runs_its_course_then_the_title() -> None:
    directory, game = _game()
    try:
        credits = CreditsScene(game, good=True)
        game.scenes.push(credits)
        # Two to three minutes of cast at its own pace.
        assert 110 < credits._height / SCROLL_SPEED < 200
        seen = _run(game, credits)
        assert list(seen) == ["cast", "tableau", "stats", "the_end",
                              "stinger"]
        assert isinstance(game.scenes.current, TitleScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_holding_interact_hurries_it_but_does_not_skip_it() -> None:
    directory, game = _game()
    try:
        credits = CreditsScene(game, good=False)
        game.scenes.push(credits)
        seen = _run(game, credits, hold=True)
        assert list(seen) == ["cast", "tableau", "stats", "the_end",
                              "stinger"]
        roll = credits._height / SCROLL_SPEED
        assert seen["cast"] < roll / FAST + 1.0
        assert isinstance(game.scenes.current, TitleScene)
    finally:
        game.input._actions_down.discard("interact")
        game._shutdown()
        directory.cleanup()


def test_the_last_image_depends_on_the_smokes() -> None:
    directory, game = _game()
    try:
        good = CreditsScene(game, good=True)
        good.on_enter()
        bad = CreditsScene(game, good=False)
        bad.on_enter()
        awake = game.assets.image("objects/bobert_barrel_awake.png")
        asleep = game.assets.image("objects/bobert_barrel.png")
        assert good._tableau._barrel is awake and good._tableau.chuck
        assert bad._tableau._barrel is asleep and bad._tableau.chuck
        # The stinger: the cat, and no Chuck.
        assert good._stinger.cat and not good._stinger.chuck

        def render(credits):
            surface = pygame.Surface((config.NATIVE_WIDTH,
                                      config.NATIVE_HEIGHT))
            credits._close_up(credits._tableau)(surface)
            return pygame.image.tobytes(surface, "RGB")

        assert render(good) != render(bad)
    finally:
        game._shutdown()
        directory.cleanup()
