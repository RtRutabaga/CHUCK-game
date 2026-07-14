"""NPCs.

Responsibilities:
    * Stand in the world (no wandering, no schedules — Phase One).
    * When interacted with, face Chuck and hand a dialogue id to the
      WorldScene, which starts the DialogueScene.

Writing/tone rules that shape implementation (Game Bible):
    * Dialogue is deadpan and grounded; strange things are stated as
      ordinary and never elaborated on.
    * Dialogue content lives in data/dialogue/, NEVER in code.
    * Special case: the sleeping vagrant by Chuck's barrel (Bobert) is
      scenery — present, never named, never interactable.

Deliberate non-behavior: NPCs are NOT solid. Chuck is one foot tall
and walks between people's boots. They don't move for him. Nobody
moves for a rat.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity

if TYPE_CHECKING:
    from src.core.assets import AssetManager


class NPC(Entity):
    """A character Chuck can talk to. Or rather: who talks at Chuck."""

    def __init__(
        self, center_x: float, center_y: float, npc_id: str, dialogue_id: str
    ) -> None:
        super().__init__(
            center_x - config.NPC_HITBOX_W / 2,
            center_y - config.NPC_HITBOX_H / 2,
            width=config.NPC_HITBOX_W,
            height=config.NPC_HITBOX_H,
        )
        self.npc_id = npc_id
        self.dialogue_id = dialogue_id
        self.facing = "down"
        self._frames: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Sprites
    # ------------------------------------------------------------------
    def load_sprites(self, assets: "AssetManager") -> None:
        """One frame per facing: down, up, left (+ mirrored right)."""
        import pygame

        row = assets.sheet(
            f"npcs/{self.npc_id}.png", config.NPC_FRAME_W, config.NPC_FRAME_H
        )[0]
        down, up, left = row
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """(x, y, w, h) of the interactable area: the WHOLE visible
        person (sprite extent), padded a little — not just the feet.

        NPCs aren't solid, so Chuck routinely stands overlapping them;
        pressing E anywhere on (or right beside) the person must work.
        Pure math, headless-testable; the WorldScene builds the Rect.
        """
        pad = 3
        w = config.NPC_FRAME_W + 2 * pad
        h = config.NPC_FRAME_H + 2 * pad
        x = int(self.x + self.width / 2 - w / 2)
        y = int(self.y + self.height - h + pad)
        return (x, y, w, h)

    def face_toward(self, other: Entity) -> None:
        """Turn to look at (down at, realistically) another entity."""
        dx = (other.x + other.width / 2) - (self.x + self.width / 2)
        dy = (other.y + other.height / 2) - (self.y + self.height / 2)
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

    def interact(self, by: Entity) -> str:
        """Face the interactor; return the dialogue id to play."""
        self.face_toward(by)
        return self.dialogue_id

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """Sprite anchored at the feet, like everyone."""
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is not None:
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (
                    int(self.x + self.width / 2 - fw / 2) - ox,
                    int(self.y + self.height - fh) - oy,
                ),
            )
        else:  # fallback: an olive rectangle of approximately a person
            pygame.draw.rect(
                surface,
                (110, 104, 66),
                pygame.Rect(int(self.x) - ox, int(self.y) - 22 - oy, 12, 30),
            )
