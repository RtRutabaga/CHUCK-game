"""Chuck descends into Zephyros' tower and meets its impossible owner.

This is Phase 10's quiet exposition scene, not a threat reveal.  The opening
uses a readable side view to compare one-foot Chuck with cloud-giant masonry,
rope, face, and hand.  Once Chuck reaches Zephyros' palm, the exact authored
dialogue advances with the same player-controlled typewriter rhythm as ordinary
conversation. The final line hands off to the following launch slice.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.scenes.scene import Scene
from src.systems.dialogue import DialogueSystem
from src.ui.dialogue_box import DialogueBox


ROPE_DESCENT_END = 7.0
FACE_ENTER_START = 6.2
FACE_ENTER_END = 10.8
SMILE_END = 13.0
HAND_RISE_START = 12.0
HAND_RISE_END = 16.0
HAND_SETTLE_END = 18.5
DIALOGUE_START = 19.5
CONVERSATION_FADE_START = 18.3
CONVERSATION_MUSIC_START = DIALOGUE_START

_SKY = (130, 190, 222)
_STONE = (190, 194, 203)
_STONE_LIGHT = (226, 222, 209)
_STONE_DARK = (111, 116, 139)
_MORTAR = (91, 94, 117)
_SHADOW = (34, 34, 51)
_SKIN = (128, 139, 160)
_SKIN_LIGHT = (171, 178, 190)
_SKIN_DARK = (82, 91, 115)
_EYE = (222, 225, 213)
_IRIS = (91, 117, 115)
_BEARD = (218, 212, 216)
_BEARD_SHADE = (163, 157, 174)
_PURPLE = (77, 55, 127)
_PURPLE_LIGHT = (112, 77, 162)
_GOLD = (218, 177, 72)
_ROPE = (181, 135, 71)
_ROPE_DARK = (99, 71, 43)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease(value: float) -> float:
    value = _clamp01(value)
    return value * value * (3.0 - 2.0 * value)


class ZephyrosIntroCutsceneScene(Scene):
    """Authored reveal followed by a normally advanced conversation."""

    def __init__(self, game, *, sanity: int) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self.sanity = sanity
        self._chuck: dict[str, pygame.Surface] = {}
        self.dialogue = DialogueSystem().get("zephyros_intro")
        self._dialogue_box = DialogueBox(game.assets)
        self._line_index = -1
        self._launch_started = False
        self._conversation_music_fading = False
        self._conversation_music_started = False

    def on_enter(self) -> None:
        grid = self.game.assets.sheet(
            config.CHUCK_SHEET, config.CHUCK_FRAME_W, config.CHUCK_FRAME_H
        )
        self._chuck = {
            "down": grid[0][0],
            "right": pygame.transform.flip(grid[2][0], True, False),
        }

    @property
    def phase(self) -> str:
        if self.elapsed < ROPE_DESCENT_END:
            return "rope_descent"
        if self.elapsed < HAND_RISE_START:
            return "face_reveal"
        if self.elapsed < HAND_SETTLE_END:
            return "hand_rise"
        return "conversation"

    @property
    def dialogue_index(self) -> int:
        return self._line_index

    @property
    def conversation_complete(self) -> bool:
        return (
            self._line_index == len(self.dialogue) - 1
            and self._dialogue_box.is_complete
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        # This cinematic is intentionally input-free.  ESC retains the
        # project's established application-level quit behavior.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        previous = self.elapsed
        self.elapsed += max(0.0, dt)
        if previous < CONVERSATION_FADE_START <= self.elapsed:
            self._conversation_music_fading = True
            self.game.audio.stop_music(fade_ms=900)
        # A second frame is deliberate: even a large dt cannot issue fade and
        # replacement playback simultaneously and turn the crossfade into a
        # hard cut.
        if (
            not self._conversation_music_started
            and self._conversation_music_fading
            and self.elapsed >= CONVERSATION_MUSIC_START
            and previous >= CONVERSATION_FADE_START
        ):
            self._conversation_music_started = True
            self.game.audio.play_music("zephyros_conversation.wav")
        if self.elapsed < DIALOGUE_START:
            return

        if self._line_index < 0:
            self._line_index = 0
            self.game.audio.play_sfx("interact")
            self._dialogue_box.show(self.dialogue[0])
        self._dialogue_box.update(dt)
        if not self.game.input.was_pressed("interact"):
            return
        if not self._dialogue_box.is_complete:
            self._dialogue_box.complete()
        elif self._line_index + 1 < len(self.dialogue):
            self._line_index += 1
            self.game.audio.play_sfx("interact")
            self._dialogue_box.show(self.dialogue[self._line_index])
        elif not self._launch_started:
            self._launch_started = True
            from src.scenes.zephyros_launch_cutscene_scene import (
                ZephyrosLaunchCutsceneScene,
            )
            self.game.scenes.replace(
                ZephyrosLaunchCutsceneScene(self.game, sanity=self.sanity)
            )

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_tower_interior(surface)

        face_progress = _ease(
            (self.elapsed - FACE_ENTER_START)
            / (FACE_ENTER_END - FACE_ENTER_START)
        )
        if face_progress > 0.0:
            face_x = round(334 + (80 - 334) * face_progress)
            self._draw_zephyros(surface, face_x, -8)

        hand_progress = _ease(
            (self.elapsed - HAND_RISE_START)
            / (HAND_RISE_END - HAND_RISE_START)
        )
        if hand_progress > 0.0:
            hand_x, hand_y = self.hand_position()
            # Zephyros reaches all the way to Chuck. Chuck does not cross the
            # room or fly toward a conveniently stationary palm.
            self._draw_hand(surface, hand_x, hand_y)

        self._draw_rope(surface)
        self._draw_chuck(surface)

        pygame.draw.rect(surface, (20, 25, 42), (0, 0, 320, 7))
        pygame.draw.rect(surface, (20, 25, 42), (0, 173, 320, 7))
        if self._line_index >= 0:
            self._dialogue_box.draw(surface)

    def hand_position(self) -> tuple[int, int]:
        progress = _ease(
            (self.elapsed - HAND_RISE_START)
            / (HAND_RISE_END - HAND_RISE_START)
        )
        return (
            round(330 + (75 - 330) * progress),
            round(181 + (111 - 181) * progress),
        )

    def _draw_tower_interior(self, surface: pygame.Surface) -> None:
        surface.fill(_STONE)
        pygame.draw.rect(surface, _STONE_LIGHT, (0, 0, 24, 180))
        pygame.draw.rect(surface, _STONE_DARK, (292, 0, 28, 180))
        for row, y in enumerate(range(7, 180, 34)):
            pygame.draw.line(surface, _MORTAR, (0, y), (320, y), 3)
            offset = 34 if row % 2 else 92
            for x in range(offset, 320, 112):
                pygame.draw.line(surface, _MORTAR, (x, y), (x - 3, y + 31), 2)
        # One tall opening supplies airy blue light without shrinking the
        # masonry into an ordinary human room.
        pygame.draw.rect(surface, _SHADOW, (252, 13, 30, 84))
        pygame.draw.rect(surface, _SKY, (256, 17, 22, 76))
        drift = int(self.elapsed * 4) % 34
        pygame.draw.ellipse(surface, (225, 237, 238),
                            (259 - drift, 44, 31, 9))

    def _draw_rope(self, surface: pygame.Surface) -> None:
        # The rope is giant-scale: nearly as thick as Chuck's torso.
        x = 78
        pygame.draw.line(surface, _ROPE_DARK, (x, 0), (x, 150), 7)
        pygame.draw.line(surface, _ROPE, (x - 1, 0), (x - 1, 150), 4)
        for y in range(4, 150, 8):
            pygame.draw.line(surface, (231, 191, 112),
                             (x - 3, y), (x + 2, y + 3), 1)

    def _draw_chuck(self, surface: pygame.Surface) -> None:
        if not self._chuck:
            return
        progress = _ease(self.elapsed / ROPE_DESCENT_END)
        x = 82
        y = round(18 + 91 * progress)
        bob = 1 if self.elapsed < ROPE_DESCENT_END and int(self.elapsed * 7) % 2 else 0
        facing = "down" if self.elapsed < HAND_RISE_START else "right"
        surface.blit(self._chuck[facing], (x, y + bob))

    def _blink_amount(self) -> float:
        # One clear introductory blink, then sparse calm blinks during speech.
        cycles = (9.55, 27.0, 43.5, 62.0, 82.0)
        return max(
            (1.0 - abs(self.elapsed - center) / 0.22 for center in cycles),
            default=0.0,
        )

    def _draw_zephyros(self, surface: pygame.Surface, x: int, y: int) -> None:
        # Purple shoulders and gold-trimmed collar establish the kindly cloud
        # giant before the face dominates the composition.
        # The robe continues below the frame. A closed shoulder ellipse made
        # Zephyros read as a floating portrait instead of a giant body.
        pygame.draw.polygon(
            surface, _PURPLE,
            ((x - 36, y + 105), (x + 180, y + 105),
             (x + 219, y + 236), (x - 69, y + 236)),
        )
        pygame.draw.ellipse(surface, _PURPLE, (x - 36, y + 94, 224, 68))
        pygame.draw.polygon(surface, _PURPLE_LIGHT,
                            ((x + 7, y + 110), (x + 72, y + 80),
                             (x + 133, y + 112), (x + 146, y + 236),
                             (x - 13, y + 236)))
        pygame.draw.line(surface, _GOLD,
                         (x - 17, y + 122), (x + 35, y + 102), 4)
        pygame.draw.line(surface, _GOLD,
                         (x + 139, y + 105), (x + 171, y + 130), 4)

        # Bald, weathered head: over ten times Chuck's sprite height.
        pygame.draw.ellipse(surface, _SKIN_DARK, (x - 8, y + 8, 166, 126))
        pygame.draw.ellipse(surface, _SKIN, (x, y, 148, 126))
        pygame.draw.ellipse(surface, _SKIN_LIGHT, (x + 16, y + 5, 76, 42))
        pygame.draw.ellipse(surface, _SKIN_DARK, (x - 14, y + 43, 28, 46))
        pygame.draw.ellipse(surface, _SKIN, (x - 10, y + 45, 22, 40))
        pygame.draw.ellipse(surface, _SKIN_DARK, (x + 137, y + 43, 28, 46))
        pygame.draw.ellipse(surface, _SKIN, (x + 138, y + 45, 22, 40))

        blink = _clamp01(self._blink_amount())
        eye_h = max(1, round(9 * (1.0 - blink)))
        eye_y = y + 49 + round(4 * blink)
        # Lightly raised brows keep the enormous face attentive and kindly;
        # filled downward brows made the first pass read as a boss encounter.
        pygame.draw.line(surface, _SKIN_DARK,
                         (x + 30, y + 43), (x + 56, y + 39), 2)
        pygame.draw.line(surface, _SKIN_DARK,
                         (x + 91, y + 39), (x + 117, y + 43), 2)
        for eye_x in (x + 37, x + 94):
            pygame.draw.ellipse(surface, _EYE, (eye_x, eye_y, 16, eye_h))
            if eye_h >= 5:
                pygame.draw.ellipse(surface, _IRIS,
                                    (eye_x + 6, eye_y + 2, 5, eye_h - 3))
                pygame.draw.rect(surface, _SHADOW,
                                 (eye_x + 8, eye_y + 3, 2, max(1, eye_h - 5)))

        pygame.draw.polygon(surface, _SKIN_DARK,
                            ((x + 70, y + 45), (x + 61, y + 82),
                             (x + 76, y + 89), (x + 87, y + 79)))
        pygame.draw.polygon(surface, _SKIN_LIGHT,
                            ((x + 70, y + 45), (x + 67, y + 78),
                             (x + 76, y + 81)))

        smile = _ease((self.elapsed - FACE_ENTER_END) / (SMILE_END - FACE_ENTER_END))
        mouth_y = y + 96
        lift = round(4 * smile)
        pygame.draw.lines(
            surface, _SKIN_DARK, False,
            ((x + 49, mouth_y - lift),
             (x + 61, mouth_y + 2),
             (x + 74, mouth_y + 4),
             (x + 87, mouth_y + 2),
             (x + 100, mouth_y - lift)),
            2,
        )

        # Long white beard and gold ear hoops soften rather than menace.
        pygame.draw.polygon(surface, _BEARD_SHADE,
                            ((x + 38, y + 103), (x + 110, y + 102),
                             (x + 94, y + 155), (x + 74, y + 166),
                             (x + 53, y + 155)))
        pygame.draw.polygon(surface, _BEARD,
                            ((x + 46, y + 104), (x + 102, y + 103),
                             (x + 88, y + 151), (x + 74, y + 160),
                             (x + 59, y + 151)))
        pygame.draw.line(surface, _BEARD_SHADE,
                         (x + 66, y + 110), (x + 71, y + 153), 2)
        pygame.draw.line(surface, _BEARD_SHADE,
                         (x + 85, y + 109), (x + 80, y + 156), 2)
        pygame.draw.arc(surface, _GOLD, (x - 10, y + 65, 20, 29),
                        math.radians(340), math.radians(200), 3)
        pygame.draw.arc(surface, _GOLD, (x + 140, y + 65, 20, 29),
                        math.radians(340), math.radians(200), 3)

    def _draw_hand(self, surface: pygame.Surface, x: int, y: int) -> None:
        pygame.draw.ellipse(surface, _SKIN_DARK, (x - 7, y + 8, 125, 35))
        pygame.draw.ellipse(surface, _SKIN, (x, y, 112, 34))
        pygame.draw.ellipse(surface, _SKIN_LIGHT, (x + 13, y + 3, 67, 13))
        for index in range(4):
            finger_x = x + 16 + index * 22
            pygame.draw.ellipse(surface, _SKIN,
                                (finger_x, y - 12 - index % 2 * 3, 18, 27))
            pygame.draw.line(surface, _SKIN_LIGHT,
                             (finger_x + 4, y - 6), (finger_x + 13, y - 5), 2)
