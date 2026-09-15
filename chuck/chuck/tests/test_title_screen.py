"""The title screen: Chuck, large, leaning on his name and smoking.

What has to stay true is mostly about the portrait being worth its
cost. It is drawn at twice the game's resolution, and the only reason
to pay for that is that he is big enough to have a face -- so the test
measures how big he is. He is leaning on the name, so the test checks
that his hand is actually on the stone. He smokes, so the test checks
that the smoke comes out of where the art says the ember and the mouth
are, rather than trusting a pair of numbers typed in twice.

And there is no subtitle.
"""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image

from src.core import config
from src.core.game import Game
from src.scenes.title_scene import (
    DRAG_TIME, LOWER_TIME, RAISE_TIME, REST_TIMES, TitleScene, chuck_pose,
    is_blinking,
)


TITLE = config.SPRITES_DIR / "title"


def _meta() -> dict:
    return json.loads((TITLE / "title.json").read_text(encoding="utf-8"))


def _title() -> tuple[tempfile.TemporaryDirectory, Game, TitleScene]:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    scene = TitleScene(game)
    game.scenes.replace(scene)
    return directory, game, scene


def _opaque_box(image: Image.Image) -> tuple[int, int, int, int]:
    return image.getchannel("A").getbbox()


def test_the_title_is_drawn_at_twice_the_game_resolution() -> None:
    """A 640x360 canvas, scaled up by two instead of by four."""
    directory, game, scene = _title()
    try:
        assert scene.canvas_size == (config.NATIVE_WIDTH * 2,
                                     config.NATIVE_HEIGHT * 2)
        game._draw()
        assert game._scene_canvas.get_size() == scene.canvas_size
        # ...and it still draws correctly onto anything else it is handed.
        native = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.draw(native)
        colours = {tuple(native.get_at((x, y)))
                   for x in range(0, config.NATIVE_WIDTH, 7)
                   for y in range(0, config.NATIVE_HEIGHT, 7)}
        assert len(colours) > 40, len(colours)
    finally:
        game._shutdown()
        directory.cleanup()


def test_chuck_is_big_enough_to_have_a_face() -> None:
    """Ten times the height of his twelve-by-fourteen sprite in play."""
    with Image.open(TITLE / "chuck_body.png") as body:
        left, top, right, bottom = _opaque_box(body)
    assert bottom - top >= 14 * 9, (top, bottom)
    assert right - left >= 12 * 9, (left, right)


def test_his_hand_is_on_the_stone() -> None:
    """He is leaning on the name, not standing next to it."""
    meta = _meta()
    lx, ly = meta["logo"]["origin"]
    cx, cy = meta["chuck_origin"]
    with Image.open(TITLE / "logo.png") as logo, \
            Image.open(TITLE / "chuck_body.png") as body:
        logo_alpha = logo.getchannel("A").load()
        body_alpha = body.getchannel("A").load()
        overlap = 0
        for y in range(body.height):
            for x in range(body.width):
                if not body_alpha[x, y]:
                    continue
                gx, gy = cx + x - lx, cy + y - ly
                if 0 <= gx < logo.width and 0 <= gy < logo.height \
                        and logo_alpha[gx, gy]:
                    overlap += 1
    assert overlap > 150, overlap


def test_every_layer_lines_up() -> None:
    """Tail, body and arm frames share one canvas, so they stack exactly."""
    meta = _meta()
    names = ["chuck_body.png", "chuck_body_blink.png"]
    names += [f"chuck_tail_{i}.png" for i in range(meta["tail_frames"])]
    names += [f"chuck_arm_{i}.png" for i in range(len(meta["arm_frames"]))]
    sizes = set()
    for name in names:
        with Image.open(TITLE / name) as image:
            sizes.add(image.size)
    assert len(sizes) == 1, sizes
    with Image.open(TITLE / "background.png") as sky:
        assert sky.size == tuple(meta["canvas"])


def test_the_ember_in_the_metadata_is_the_ember_in_the_art() -> None:
    """Smoke comes off the end of the cigarette in every arm frame.

    The positions are written by the same generator that draws the
    frames, but that is exactly the kind of pair that drifts: move the
    hand and forget the ember, and the smoke floats beside him.
    """
    meta = _meta()
    for index, frame in enumerate(meta["arm_frames"]):
        ex, ey = frame["ember"]
        with Image.open(TITLE / f"chuck_arm_{index}.png") as arm:
            pixels = arm.convert("RGBA").load()
            near = [pixels[round(ex) + ox, round(ey) + oy]
                    for ox in (-1, 0, 1) for oy in (-1, 0, 1)]
        assert any(p[3] and p[0] > 200 and p[1] < 190 for p in near), \
            (index, frame, near)


def test_he_rests_lifts_drags_and_lowers() -> None:
    """The whole smoking cycle happens, in order, and loops."""
    rest = REST_TIMES[0]
    assert chuck_pose(0.1) == (0.0, "rest")
    amount, phase = chuck_pose(rest + RAISE_TIME / 2)
    assert phase == "raise" and 0.3 < amount < 0.7
    assert chuck_pose(rest + RAISE_TIME + DRAG_TIME / 2) == (1.0, "drag")
    amount, phase = chuck_pose(rest + RAISE_TIME + DRAG_TIME
                               + LOWER_TIME / 2)
    assert phase == "lower" and 0.3 < amount < 0.7
    loop = sum(r + RAISE_TIME + DRAG_TIME + LOWER_TIME for r in REST_TIMES)
    assert chuck_pose(0.1 + loop) == chuck_pose(0.1)
    # The rests are not all the same length, or it is a metronome.
    assert len(set(REST_TIMES)) == len(REST_TIMES)
    assert any(is_blinking(t / 100) for t in range(0, 800))
    assert not all(is_blinking(t / 100) for t in range(0, 800))


def test_the_smoke_comes_from_the_ember_and_the_exhale_from_the_mouth():
    directory, game, scene = _title()
    try:
        for _ in range(30):
            scene.update(1 / 30)
        ex, ey = scene.ember_position()
        assert scene._smoke
        assert min(abs(p.x - ex) + abs(p.y - ey) for p in scene._smoke) < 12

        # Run to the moment the arm starts down, and look for the breath.
        start = REST_TIMES[0] + RAISE_TIME + DRAG_TIME
        while scene._time < start + 0.05:
            scene.update(1 / 30)
        mx, my = scene.mouth_position()
        breath = [p for p in scene._smoke
                  if abs(p.x - mx) < 14 and abs(p.y - my) < 10]
        assert len(breath) >= 10, len(breath)
        # One breath per lowering, not one per frame of it.
        count = len(scene._smoke)
        scene.update(1 / 30)
        assert len(scene._smoke) <= count + 2
    finally:
        game._shutdown()
        directory.cleanup()


def test_he_moves() -> None:
    """Two moments in the cycle do not draw the same portrait."""
    directory, game, scene = _title()
    try:
        meta = _meta()
        cx, cy = meta["chuck_origin"]
        region = pygame.Rect(cx - 30, cy - 30, 180, 190)
        canvas = pygame.Surface(scene.canvas_size)

        def portrait() -> bytes:
            scene.draw(canvas)
            return pygame.image.tobytes(canvas.subsurface(region), "RGB")

        first = portrait()
        while scene._time < REST_TIMES[0] + RAISE_TIME + 0.2:
            scene.update(1 / 30)
        assert portrait() != first
    finally:
        game._shutdown()
        directory.cleanup()


def test_there_is_no_subtitle() -> None:
    """Every string the title draws is the menu or the controls."""
    directory, game, scene = _title()
    try:
        drawn = []
        real = scene._font.render

        def recording(text, *args, **kwargs):
            drawn.append(text)
            return real(text, *args, **kwargs)

        scene._font.render = recording
        scene.draw(pygame.Surface(scene.canvas_size))
        allowed = {f"{caret} {label}" for caret in (">", " ")
                   for label in scene.options}
        allowed.add("UP / DOWN   E / ENTER")
        # ...and the Fan Content Policy notice, which is not a subtitle.
        from src.scenes.title_scene import FAN_CONTENT_NOTICE
        allowed.update(FAN_CONTENT_NOTICE)
        assert set(drawn) <= allowed, set(drawn) - allowed
        assert not any("RAT" in text for text in drawn)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_fan_content_notice_is_on_the_title_and_fits() -> None:
    from src.scenes.title_scene import FAN_CONTENT_NOTICE

    text = " ".join(FAN_CONTENT_NOTICE)
    assert "unofficial Fan Content permitted under the Fan Content Policy" \
        in text
    assert "Not approved/endorsed by Wizards" in text
    assert "property of Wizards of the Coast" in text
    directory, game, scene = _title()
    try:
        drawn = []
        real = scene._font.render

        def recording(line, *args, **kwargs):
            image = real(line, *args, **kwargs)
            drawn.append((line, image.get_width()))
            return image

        scene._font.render = recording
        scene.draw(pygame.Surface(scene.canvas_size))
        widths = dict(drawn)
        for line in FAN_CONTENT_NOTICE:
            assert line in widths, line
            assert widths[line] <= scene.canvas_size[0] - 4, line
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All title screen tests passed.")


if __name__ == "__main__":
    _run_all()
