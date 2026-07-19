"""Pickups — starting with the cigarette, the game's signature collectible.

Responsibilities:
    * Sit in the world until Chuck's hitbox overlaps (WorldScene checks).
    * On pickup: restore sanity and remove itself (alive = False).
    * Draw as a tiny lit cigarette lying on the ground. No sparkle, no
      bobbing, no glow — the Game Bible trusts the player to notice it.

Phase One scope note: cigarettes are the ONLY collectible. Do not
generalize this into an item/inventory system yet — the Game Bible's
plan explicitly defers inventory.
"""

from __future__ import annotations

from src.core import config
from src.entities.entity import Entity

# A cigarette on the ground is 6x3 world pixels. Chuck is one foot
# tall; to him this is a find the size of a park bench.
CIG_W, CIG_H = 6, 3


class Cigarette(Entity):
    """Restores Chuck's sanity when collected."""

    def __init__(self, center_x: float, center_y: float) -> None:
        """Place a cigarette centered on (center_x, center_y)."""
        super().__init__(
            center_x - CIG_W / 2, center_y - CIG_H / 2, width=CIG_W, height=CIG_H
        )
        self.restore_amount = config.CIGARETTE_SANITY_RESTORE
        self._image = None  # set by load_sprite(); rects otherwise

    def load_sprite(self, assets) -> None:
        """Use the drawn sprite (smoke wisp included)."""
        self._image = assets.image("objects/cigarette.png")

    def on_collect(self, sanity_system, ledger=None) -> None:
        """Apply the pickup's effect and remove it from the world."""
        sanity_system.restore(self.restore_amount)
        if ledger is not None:
            ledger.add(1)
        self.alive = False
        # TODO (effects, later): a single small puff of smoke.

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        """The drawn sprite (bottom-aligned to the hitbox), or the old
        two-rect fallback if sprites aren't loaded (headless tests)."""
        import pygame

        ox, oy = camera_offset
        if self._image is not None:
            fw, fh = self._image.get_size()
            surface.blit(
                self._image,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
            return
        x, y = int(self.x) - ox, int(self.y) - oy
        pygame.draw.rect(
            surface, config.COLOR_CIG_PAPER, pygame.Rect(x, y, CIG_W - 1, CIG_H)
        )
        pygame.draw.rect(
            surface, config.COLOR_CIG_EMBER, pygame.Rect(x + CIG_W - 1, y, 1, CIG_H)
        )


# A carton on the ground is 12x8 world pixels — to Chuck, a crate.
CARTON_W, CARTON_H = 12, 8


class CigaretteCarton(Entity):
    """A full carton found in a temple urn: twenty cigarettes at once.

    Collecting it counts as consuming CARTON_CIGARETTE_COUNT cigarettes
    — sanity clamps at the maximum, while the overall-game ledger banks
    the exact number.
    """

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - CARTON_W / 2, center_y - CARTON_H / 2,
            width=CARTON_W, height=CARTON_H,
        )
        self.cigarette_count = config.CARTON_CIGARETTE_COUNT
        self.restore_amount = (
            self.cigarette_count * config.CIGARETTE_SANITY_RESTORE
        )
        self._image = None  # set by load_sprite(); rects otherwise

    def load_sprite(self, assets) -> None:
        self._image = assets.image("objects/cigarette_carton.png")

    def on_collect(self, sanity_system, ledger=None) -> None:
        """Twenty cigarettes at once; sanity simply clamps at full,
        while the ledger banks the exact carton count."""
        sanity_system.restore(self.restore_amount)
        if ledger is not None:
            ledger.add(self.cigarette_count)
        self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        if self._image is not None:
            fw, fh = self._image.get_size()
            surface.blit(
                self._image,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
            return
        pygame.draw.rect(
            surface, config.COLOR_CIG_PAPER,
            pygame.Rect(int(self.x) - ox, int(self.y) - oy,
                        CARTON_W, CARTON_H),
        )
